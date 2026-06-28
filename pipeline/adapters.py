"""Concrete adapters for the math pipeline ports.

Each adapter wraps an existing implementation (scraper, LLM client, filesystem,
SQLite CRUD) so the use case does not depend on them directly. Optional
constructor injection lets tests substitute fakes or monkey-patched callables.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from pipeline import interfaces as pi
from pipeline.config import DATA_DIR, OUTPUT_DIR
from pipeline.content_adapter import build_adapter_prompt, strip_html
from pipeline.llm_client import LLMClient as _OpenAILLMClient
from pipeline.question_generator import build_question_prompt, parse_json_array
from pipeline.scraper import fetch_ixl_topics, search_mathisfun_topic
from db import crud
from db.database import SessionLocal


TopicSourceCallable = Callable[[], List[Tuple[str, str]]]
ContentSourceCallable = Callable[[str], Tuple[str, str]]
LLMClientClass = Callable[..., _OpenAILLMClient]


class IXLTopicSource(pi.TopicSource):
    """Fetch Class-VII topics from IXL via Obscura."""

    def __init__(self, fetch_topics: Optional[TopicSourceCallable] = None):
        self._fetch = fetch_topics or fetch_ixl_topics

    def fetch_topics(self) -> List[Tuple[str, str]]:
        return self._fetch()


class MathIsFunContentSource(pi.PedagogicalContentSource):
    """Fetch MathIsFun reference content for a topic."""

    def __init__(self, fetch_content: Optional[ContentSourceCallable] = None):
        self._fetch = fetch_content or search_mathisfun_topic

    def fetch_content(self, topic: str) -> pi.ScrapedContent:
        raw_html, source_url = self._fetch(topic)
        return pi.ScrapedContent(raw_html=raw_html, source_url=source_url)


class OpenAILLMClient(pi.LLMPort):
    """Adapt content and generate questions using the configured LLM provider."""

    def __init__(self, client: Optional[_OpenAILLMClient] = None):
        self._client = client

    def _get_client(self) -> _OpenAILLMClient:
        return self._client if self._client is not None else _OpenAILLMClient()

    def adapt_content(
        self,
        topic: str,
        raw_html: str,
        custom_system: Optional[str] = None,
        custom_user: Optional[str] = None,
    ) -> pi.AdaptedContent:
        sys_prompt, user_prompt = build_adapter_prompt(
            topic, raw_html, custom_system=custom_system, custom_user=custom_user
        )
        # Preserve the legacy custom-prompt behaviour: if a system prompt is
        # supplied, replace the adapter prompt with a minimal topic/raw-content
        # instruction.
        if custom_system:
            sys_prompt = custom_system
            user_prompt = (
                f"TOPIC: {topic}\nRAW CONTENT:\n{strip_html(raw_html)[:4000]}\n\n"
                "Adapt this into a lesson."
            )
        text = self._get_client().generate(
            sys_prompt, user_prompt, temperature=0.8, max_tokens=4000
        )
        return pi.AdaptedContent(text=text, generated_at=datetime.utcnow())

    def generate_questions(
        self,
        topic: str,
        adapted_content: str,
        custom_question_prompt: Optional[str] = None,
        count: int = 40,
    ) -> pi.QuestionSet:
        q_sys, q_user = build_question_prompt(
            topic, adapted_content, custom_prompt=custom_question_prompt
        )
        raw = self._get_client().generate(
            q_sys, q_user, temperature=0.7, max_tokens=12000
        )
        questions = parse_json_array(raw)
        diff_counts = {1: 0, 2: 0, 3: 0, 4: 0}
        for q in questions:
            d = q.get("difficulty", 0)
            if d in diff_counts:
                diff_counts[d] += 1
        return pi.QuestionSet(
            questions=questions,
            difficulty_distribution=diff_counts,
            generated_at=datetime.utcnow(),
        )


class FileSystemContentStore(pi.ContentStore):
    """Write pipeline artifacts to the local data/output directories."""

    def __init__(
        self, data_dir: Optional[Path] = None, output_dir: Optional[Path] = None
    ):
        self.data_dir = data_dir or DATA_DIR
        self.output_dir = output_dir or OUTPUT_DIR

    def save_raw_html(self, slug: str, raw_html: str) -> str:
        path = self.data_dir / f"{slug}_raw.html"
        path.write_text(raw_html, encoding="utf-8")
        return str(path)

    def save_adapted_content(self, slug: str, adapted_content: str) -> str:
        path = self.data_dir / f"{slug}_antigravity.md"
        path.write_text(adapted_content, encoding="utf-8")
        return str(path)

    def save_output(
        self, slug: str, output: Dict[str, Any], output_path: Optional[str] = None
    ) -> str:
        if output_path is None:
            path = self.output_dir / f"{slug}_output.json"
        else:
            path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
        return str(path)


class SQLGenerationTracker(pi.GenerationTracker):
    """Persist generation lifecycle and grounding logs to SQLite via CRUD."""

    def __init__(
        self, session_factory: Optional[Callable[[], Any]] = None
    ):
        self._session_factory = session_factory or SessionLocal

    def start(self, topic: str, slug: str, prompt_id: Optional[str]) -> int:
        db = self._session_factory()
        try:
            topic_obj = crud.get_or_create_topic(db, slug, topic)
            gen = crud.create_generation(
                db,
                topic_id=topic_obj.id,
                prompt_id=prompt_id,
                status="pending",
            )
            return gen.id
        finally:
            db.close()

    def record_success(self, generation_id: int, result: pi.PipelineResult) -> None:
        db = self._session_factory()
        try:
            crud.update_generation(
                db,
                generation_id=generation_id,
                status="success",
                output_path=result.output_path,
                total_questions=len(result.questions),
                difficulty_distribution=result.difficulty_distribution,
                adapted_content=result.antigravity_content,
                questions_json=result.questions,
                raw_html_path=result.raw_html_path,
                antigravity_path=result.antigravity_path,
                meta={
                    "total_questions": len(result.questions),
                    "difficulty": result.difficulty_distribution,
                    "prompt_name": result.prompt_name,
                },
                scraped_at=result.scraped_at,
                adapted_at=result.adapted_at,
                questions_generated_at=result.questions_generated_at,
                saved_at=result.saved_at,
            )
            for skill in result.source_ixl_skills[:5]:
                crud.create_grounding_log(
                    db,
                    generation_id=generation_id,
                    source_type="ixl",
                    source_url="https://in.ixl.com/maths/class-vii",
                    content_snippet=skill[:500],
                    verification_status="verified" if result.source_ixl_skills else "partial",
                )
            crud.create_grounding_log(
                db,
                generation_id=generation_id,
                source_type="mathisfun",
                source_url=result.mathisfun_url,
                content_snippet=strip_html(result.raw_html)[:500],
                verification_status="verified",
            )
        finally:
            db.close()

    def record_error(self, generation_id: int, error: Exception) -> None:
        db = self._session_factory()
        try:
            crud.update_generation(
                db,
                generation_id=generation_id,
                status="error",
                meta={"error": str(error)},
            )
        finally:
            db.close()
