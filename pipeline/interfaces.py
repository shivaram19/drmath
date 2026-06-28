"""Hexagonal ports for the math content pipeline.

These abstract boundaries are volatile or likely to gain multiple implementations
(LLM provider, scraper, content store, generation repository). The orchestrator
in `pipeline/use_cases.py` depends only on these ports; concrete adapters live in
`pipeline/adapters.py`.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass
class ScrapedContent:
    raw_html: str
    source_url: str


@dataclass
class AdaptedContent:
    text: str
    generated_at: datetime


@dataclass
class QuestionSet:
    questions: List[Dict[str, Any]]
    difficulty_distribution: Dict[int, int]
    generated_at: datetime


@dataclass
class PipelineResult:
    topic: str
    prompt_id: Optional[str]
    prompt_name: str
    source_ixl_skills: List[str]
    mathisfun_url: str
    raw_html: str
    antigravity_content: str
    questions: List[Dict[str, Any]]
    difficulty_distribution: Dict[int, int]
    output_path: str
    raw_html_path: str
    antigravity_path: str
    scraped_at: datetime
    adapted_at: datetime
    questions_generated_at: datetime
    saved_at: datetime
    meta: Dict[str, Any] = field(default_factory=dict)


class TopicSource(ABC):
    """Fetch a list of curriculum topics/skills for matching."""

    @abstractmethod
    def fetch_topics(self) -> List[Tuple[str, str]]:
        """Return [(topic_name, category), ...]."""
        ...


class PedagogicalContentSource(ABC):
    """Fetch reference content for a given topic."""

    @abstractmethod
    def fetch_content(self, topic: str) -> ScrapedContent:
        """Return raw HTML + canonical source URL for the topic."""
        ...


class LLMPort(ABC):
    """Generate adapted lessons and question sets via an LLM."""

    @abstractmethod
    def adapt_content(
        self,
        topic: str,
        raw_html: str,
        custom_system: Optional[str] = None,
        custom_user: Optional[str] = None,
    ) -> AdaptedContent:
        ...

    @abstractmethod
    def generate_questions(
        self,
        topic: str,
        adapted_content: str,
        custom_question_prompt: Optional[str] = None,
        count: int = 40,
    ) -> QuestionSet:
        ...


class ContentStore(ABC):
    """Persist raw HTML, adapted markdown, and final output JSON."""

    @abstractmethod
    def save_raw_html(self, slug: str, raw_html: str) -> str:
        """Return the path where the raw HTML was saved."""
        ...

    @abstractmethod
    def save_adapted_content(self, slug: str, adapted_content: str) -> str:
        """Return the path where the adapted content was saved."""
        ...

    @abstractmethod
    def save_output(
        self, slug: str, output: Dict[str, Any], output_path: Optional[str] = None
    ) -> str:
        """Return the path where the output JSON was saved."""
        ...


class GenerationTracker(ABC):
    """Create and update generation records plus grounding logs."""

    @abstractmethod
    def start(self, topic: str, slug: str, prompt_id: Optional[str]) -> int:
        """Create a pending generation and return its id."""
        ...

    @abstractmethod
    def record_success(self, generation_id: int, result: PipelineResult) -> None:
        ...

    @abstractmethod
    def record_error(self, generation_id: int, error: Exception) -> None:
        ...


PromptLookup = Callable[[str], Optional[Dict[str, Any]]]
