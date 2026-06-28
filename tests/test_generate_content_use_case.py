"""Unit tests for the port-based `GenerateContentUseCase`.

These tests verify that the use case can be exercised entirely with fake
adapters, proving the pipeline core no longer depends on concrete scrapers,
LLM clients, or the filesystem.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

import pytest

from pipeline.interfaces import (
    AdaptedContent,
    ContentStore,
    GenerationTracker,
    LLMPort,
    PedagogicalContentSource,
    PipelineResult,
    QuestionSet,
    ScrapedContent,
    TopicSource,
)
from pipeline.use_cases import GenerateContentUseCase


class FakeTopicSource(TopicSource):
    def __init__(self, topics: List[tuple]):
        self.topics = topics

    def fetch_topics(self) -> List[tuple]:
        return self.topics


class FakeContentSource(PedagogicalContentSource):
    def __init__(self, raw_html: str, url: str):
        self.raw_html = raw_html
        self.url = url

    def fetch_content(self, topic: str) -> ScrapedContent:
        return ScrapedContent(raw_html=self.raw_html, source_url=self.url)


class FakeLLM(LLMPort):
    def __init__(self, adapted: str, questions: List[Dict[str, Any]]):
        self.adapted = adapted
        self.questions = questions
        self.adapt_calls: List[dict] = []
        self.question_calls: List[dict] = []

    def adapt_content(
        self,
        topic: str,
        raw_html: str,
        custom_system: Optional[str] = None,
        custom_user: Optional[str] = None,
    ) -> AdaptedContent:
        self.adapt_calls.append(
            {"topic": topic, "custom_system": custom_system, "custom_user": custom_user}
        )
        return AdaptedContent(text=self.adapted, generated_at=datetime.utcnow())

    def generate_questions(
        self,
        topic: str,
        adapted_content: str,
        custom_question_prompt: Optional[str] = None,
        count: int = 40,
    ) -> QuestionSet:
        self.question_calls.append(
            {"topic": topic, "custom_question_prompt": custom_question_prompt, "count": count}
        )
        return QuestionSet(
            questions=self.questions,
            difficulty_distribution={1: len(self.questions), 2: 0, 3: 0, 4: 0},
            generated_at=datetime.utcnow(),
        )


class FakeContentStore(ContentStore):
    def __init__(self):
        self.raw_paths: List[str] = []
        self.adapted_paths: List[str] = []
        self.output_paths: List[str] = []

    def save_raw_html(self, slug: str, raw_html: str) -> str:
        path = f"{slug}_raw.html"
        self.raw_paths.append(path)
        return path

    def save_adapted_content(self, slug: str, adapted_content: str) -> str:
        path = f"{slug}_antigravity.md"
        self.adapted_paths.append(path)
        return path

    def save_output(
        self, slug: str, output: Dict[str, Any], output_path: Optional[str] = None
    ) -> str:
        path = output_path or f"{slug}_output.json"
        self.output_paths.append(path)
        return path


class FakeGenerationTracker(GenerationTracker):
    def __init__(self):
        self.start_calls: List[dict] = []
        self.success_calls: List[tuple] = []
        self.error_calls: List[tuple] = []
        self._next_id = 1

    def start(self, topic: str, slug: str, prompt_id: Optional[str]) -> int:
        self.start_calls.append({"topic": topic, "slug": slug, "prompt_id": prompt_id})
        gen_id = self._next_id
        self._next_id += 1
        return gen_id

    def record_success(self, generation_id: int, result: PipelineResult) -> None:
        self.success_calls.append((generation_id, result))

    def record_error(self, generation_id: int, error: Exception) -> None:
        self.error_calls.append((generation_id, error))


@pytest.fixture
def use_case():
    topic_source = FakeTopicSource([("Fractions", "Class VII Maths")])
    content_source = FakeContentSource(
        raw_html="<p>Fractions are parts of a whole.</p>",
        url="https://example.com/fractions",
    )
    llm = FakeLLM(
        adapted="# Fractions\n\nParts of a whole.",
        questions=[
            {
                "id": 1,
                "difficulty": 1,
                "question": "What is 1/2?",
                "options": ["A) half", "B) whole", "C) double", "D) zero"],
                "correct_answer": "A",
                "explanation": "One of two equal parts.",
            }
        ],
    )
    store = FakeContentStore()
    tracker = FakeGenerationTracker()
    return GenerateContentUseCase(
        topic_source=topic_source,
        content_source=content_source,
        llm=llm,
        content_store=store,
        generation_tracker=tracker,
    ), llm, store, tracker


def test_execute_returns_output_and_persists_via_ports(use_case):
    case, llm, store, tracker = use_case

    result = case.execute("Fractions", output_path="/tmp/fractions.json")

    assert result["topic"] == "Fractions"
    assert result["prompt_name"] == "Default (Anti-Gravity)"
    assert len(result["questions"]) == 1
    assert result["meta"]["total_questions"] == 1

    assert store.raw_paths == ["fractions_raw.html"]
    assert store.adapted_paths == ["fractions_antigravity.md"]
    assert store.output_paths == ["/tmp/fractions.json"]

    assert len(tracker.start_calls) == 1
    assert tracker.start_calls[0]["slug"] == "fractions"
    assert len(tracker.success_calls) == 1
    assert tracker.success_calls[0][0] == 1
    assert tracker.success_calls[0][1].mathisfun_url == "https://example.com/fractions"
    assert tracker.error_calls == []


def test_execute_uses_custom_prompt_when_provided():
    topic_source = FakeTopicSource([])
    content_source = FakeContentSource("<p>x</p>", "https://example.com/x")
    llm = FakeLLM("adapted", [])
    store = FakeContentStore()
    tracker = FakeGenerationTracker()

    def prompt_lookup(pid: str) -> Optional[Dict[str, Any]]:
        return {
            "id": pid,
            "name": "Visual-First",
            "system_prompt": "You are a visual tutor.",
            "question_prompt": "Draw questions.",
        }

    case = GenerateContentUseCase(
        topic_source=topic_source,
        content_source=content_source,
        llm=llm,
        content_store=store,
        generation_tracker=tracker,
        prompt_lookup=prompt_lookup,
    )

    result = case.execute("Algebra", prompt_id="abc123")

    assert result["prompt_name"] == "Visual-First"
    assert llm.adapt_calls[0]["custom_system"] == "You are a visual tutor."
    assert llm.question_calls[0]["custom_question_prompt"] == "Draw questions."


def test_execute_records_error_and_re_raises(use_case):
    case, llm, store, tracker = use_case
    llm.adapted = "# Broken"

    class BrokenLLM(LLMPort):
        def adapt_content(self, *args, **kwargs):
            raise RuntimeError("LLM refused")

        def generate_questions(self, *args, **kwargs):
            return QuestionSet(questions=[], difficulty_distribution={}, generated_at=datetime.utcnow())

    case.llm = BrokenLLM()

    with pytest.raises(RuntimeError, match="LLM refused"):
        case.execute("Fractions")

    assert len(tracker.error_calls) == 1
    assert tracker.error_calls[0][0] == 1
    assert isinstance(tracker.error_calls[0][1], RuntimeError)
    assert tracker.success_calls == []
