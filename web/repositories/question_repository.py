"""Question repository — abstracts question sources behind a clean interface.

Current implementation reads from the JSON seed bank. Future implementations
may read from the database or an LLM generation pipeline.
"""
import json
import random
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Dict, Any

from pipeline.config import OUTPUT_DIR
from web.domain.constants import CognitiveLevel, QuestionContext, VerificationStatus
from web.domain.models import Question, QuestionBank, QuestionBankMeta


DEFAULT_BANK_PATH = OUTPUT_DIR / "nursing_staff_nurse_output.json"


class QuestionRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Question]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, question_id: int) -> Optional[Question]:
        raise NotImplementedError

    @abstractmethod
    def get_by_subject(self, subject_id: str) -> List[Question]:
        raise NotImplementedError

    @abstractmethod
    def get_by_topic(self, topic_id: str) -> List[Question]:
        raise NotImplementedError

    @abstractmethod
    def get_diagnostic_set(self, per_subject: int = 2) -> List[Question]:
        raise NotImplementedError


class JsonFileQuestionRepository(QuestionRepository):
    """Reads questions from a Dr. Math-compatible JSON output file."""

    def __init__(self, path: Optional[Path] = None):
        self.path = path or DEFAULT_BANK_PATH
        self._bank: Optional[QuestionBank] = None
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            self._bank = QuestionBank(
                topic="",
                exam_pattern="",
                meta=QuestionBankMeta(
                    total_questions=0,
                    language="en",
                    source="",
                    verification_status=VerificationStatus.REVIEWED,
                ),
                questions=[],
            )
            return

        raw = json.loads(self.path.read_text(encoding="utf-8"))
        self._bank = QuestionBank.model_validate(raw)

    def reload(self) -> None:
        """Force re-read from disk (useful after seed regeneration)."""
        self._load()

    def get_meta(self) -> Dict[str, Any]:
        return self._bank.meta.model_dump()

    def get_all(self) -> List[Question]:
        return list(self._bank.questions)

    def get_by_id(self, question_id: int) -> Optional[Question]:
        for q in self._bank.questions:
            if q.id == question_id:
                return q
        return None

    def get_by_subject(self, subject_id: str) -> List[Question]:
        return [q for q in self._bank.questions if q.subject_id == subject_id]

    def get_by_topic(self, topic_id: str) -> List[Question]:
        return [q for q in self._bank.questions if q.topic_id == topic_id]

    def filter(
        self,
        *,
        subject_id: Optional[str] = None,
        topic_id: Optional[str] = None,
        cognitive_level: Optional[CognitiveLevel] = None,
        context: Optional[QuestionContext] = None,
        difficulty: Optional[int] = None,
        concept_tag: Optional[str] = None,
    ) -> List[Question]:
        """Return questions matching all provided filters.

        Filters are keyword-only to prevent positional confusion as the list grows.
        """
        result = self._bank.questions
        if subject_id is not None:
            result = [q for q in result if q.subject_id == subject_id]
        if topic_id is not None:
            result = [q for q in result if q.topic_id == topic_id]
        if cognitive_level is not None:
            result = [q for q in result if q.cognitive_level == cognitive_level]
        if context is not None:
            result = [q for q in result if q.context == context]
        if difficulty is not None:
            result = [q for q in result if q.difficulty == difficulty]
        if concept_tag is not None:
            result = [q for q in result if q.concept_tag == concept_tag]
        return result

    def count_by_subject(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for q in self._bank.questions:
            counts[q.subject_id] = counts.get(q.subject_id, 0) + 1
        return counts

    def list_subjects(self) -> List[str]:
        return sorted({q.subject_id for q in self._bank.questions})

    def list_topics(self, subject_id: Optional[str] = None) -> List[str]:
        questions = self._bank.questions
        if subject_id is not None:
            questions = [q for q in questions if q.subject_id == subject_id]
        return sorted({q.topic_id for q in questions})

    def get_by_exam_pattern(self, pattern: str) -> List[Question]:
        # For now, the seed bank supports all patterns; filter by verification later.
        return [
            q
            for q in self._bank.questions
            if q.verification_status in (VerificationStatus.REVIEWED,)
        ]

    def get_diagnostic_set(self, per_subject: int = 2) -> List[Question]:
        """Return up to `per_subject` questions per subject, spread across topics."""
        by_subject: Dict[str, List[Question]] = {}
        for q in self._bank.questions:
            by_subject.setdefault(q.subject_id, []).append(q)

        selected: List[Question] = []
        for subject_id, questions in by_subject.items():
            # Group by topic, pick one from each topic until we reach per_subject.
            by_topic: Dict[str, List[Question]] = {}
            for q in questions:
                by_topic.setdefault(q.topic_id, []).append(q)

            topics = list(by_topic.keys())
            random.shuffle(topics)
            count = 0
            for topic_id in topics:
                if count >= per_subject:
                    break
                q = random.choice(by_topic[topic_id])
                if q not in selected:
                    selected.append(q)
                    count += 1

        random.shuffle(selected)
        return selected


# Singleton instance wired to the seed bank.
_seed_repo: Optional[QuestionRepository] = None


def get_question_repository(path: Optional[Path] = None) -> QuestionRepository:
    global _seed_repo
    if _seed_repo is None:
        _seed_repo = JsonFileQuestionRepository(path)
    return _seed_repo
