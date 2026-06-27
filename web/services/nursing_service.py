"""Business logic for the nursing practice module.

This layer sits between the HTTP router and the question repository. It owns:
- Diagnostic set construction
- Topic-wise and dimension-filtered practice
- Full-length mock test construction
- Capability / weak-area analysis
- Printable weak-area export (HTML-for-PDF)
- Question reporting
"""
import json
import random
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from pipeline.config import OUTPUT_DIR, DATA_DIR
from web.domain.constants import (
    CognitiveLevel,
    QuestionContext,
    EXAM_PATTERNS,
    DEFAULT_PATTERN_KEY,
    DIAGNOSTIC_DEFAULT_LENGTH,
    DIAGNOSTIC_QUESTIONS_PER_SUBJECT,
)
from web.domain.models import Question, Attempt, DiagnosticResult
from web.repositories.question_repository import (
    JsonFileQuestionRepository,
    QuestionRepository,
)
from web.services.adaptive_queue import (
    compute_subject_capabilities,
    compute_topic_capabilities,
    rank_topics_for_practice,
)


REPORT_LOG_PATH = OUTPUT_DIR / "nursing_reports.json"


def _now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


class DiagnosticBuilder:
    """Builds a diagnostic question set that covers subjects and dimensions."""

    def __init__(self, repository: QuestionRepository):
        self.repository = repository

    def build(self, num_questions: int = DIAGNOSTIC_DEFAULT_LENGTH) -> List[Question]:
        """Return a diagnostic set spread across subjects, topics, and dimensions.

        Strategy: ask the repository for a per-subject spread, then fill any
        remaining slots with a balanced sample of remaining questions.
        """
        per_subject = max(1, num_questions // max(1, len(self.repository.list_subjects())))
        selected = self.repository.get_diagnostic_set(per_subject=per_subject)

        # Fill up to num_questions without duplication.
        if len(selected) < num_questions:
            remaining = [q for q in self.repository.get_all() if q not in selected]
            random.shuffle(remaining)
            selected.extend(remaining[: num_questions - len(selected)])

        random.shuffle(selected)
        return selected[:num_questions]


class PracticeBuilder:
    """Builds topic-wise, dimension-aware practice sessions."""

    def __init__(self, repository: QuestionRepository):
        self.repository = repository

    def by_topic(
        self,
        *,
        subject_id: Optional[str] = None,
        topic_id: Optional[str] = None,
        cognitive_level: Optional[CognitiveLevel] = None,
        context: Optional[QuestionContext] = None,
        difficulty: Optional[int] = None,
        concept_tag: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Question]:
        """Return questions filtered by all provided dimensions."""
        questions = self.repository.filter(
            subject_id=subject_id,
            topic_id=topic_id,
            cognitive_level=cognitive_level,
            context=context,
            difficulty=difficulty,
            concept_tag=concept_tag,
        )
        random.shuffle(questions)
        if limit is not None:
            return questions[:limit]
        return questions


class MockBuilder:
    """Builds a full-length mock test balanced by subject weights."""

    def __init__(self, repository: QuestionRepository):
        self.repository = repository

    def _subject_targets(self, pattern_key: str) -> Dict[str, int]:
        """Compute target question counts per subject from the topic tree."""
        topics_path = DATA_DIR / "nursing_topics.json"
        if not topics_path.exists():
            return {}

        raw = json.loads(topics_path.read_text(encoding="utf-8"))
        total = EXAM_PATTERNS[pattern_key].total_questions
        subjects = raw.get("subjects", [])

        # Sum estimated questions; fall back to equal distribution if missing.
        estimates = []
        for s in subjects:
            est = s.get("estimated_questions")
            if est is None:
                est = 1
            estimates.append((s["id"], est))

        total_est = sum(e for _, e in estimates) or 1
        targets = {}
        for subject_id, est in estimates:
            targets[subject_id] = round(est / total_est * total)

        # Distribute any rounding remainder to the largest subject.
        diff = total - sum(targets.values())
        if diff and targets:
            largest = max(targets, key=targets.get)
            targets[largest] += diff
        return targets

    def build(self, pattern_key: str = DEFAULT_PATTERN_KEY) -> List[Question]:
        """Return a mock test of the configured size with balanced subject coverage."""
        targets = self._subject_targets(pattern_key)
        by_subject: Dict[str, List[Question]] = {}
        for q in self.repository.get_all():
            by_subject.setdefault(q.subject_id, []).append(q)

        selected: List[Question] = []
        seen_ids = set()
        for subject_id, target in targets.items():
            pool = [q for q in by_subject.get(subject_id, []) if q.id not in seen_ids]
            random.shuffle(pool)
            for q in pool[:target]:
                selected.append(q)
                seen_ids.add(q.id)

        # If the bank is too small to meet every target, fill the remainder
        # from the full pool so the mock still has the expected length.
        total = EXAM_PATTERNS[pattern_key].total_questions
        if len(selected) < total:
            remaining = [q for q in self.repository.get_all() if q.id not in seen_ids]
            random.shuffle(remaining)
            selected.extend(remaining[: total - len(selected)])

        random.shuffle(selected)
        return selected


class CapabilityService:
    """Computes capability maps from attempt history."""

    def analyze(self, attempts: List[Attempt]) -> DiagnosticResult:
        return DiagnosticResult(
            attempts=attempts,
            subject_capabilities=compute_subject_capabilities(attempts),
            topic_capabilities=compute_topic_capabilities(attempts),
            dimension_capabilities=self._dimension_capabilities(attempts),
        )

    def _dimension_capabilities(self, attempts: List[Attempt]) -> List[Any]:
        """Compute capability per subject/topic/cognitive_level triplet."""
        from web.domain.models import DimensionCapability

        by_key: Dict[str, List[Attempt]] = {}
        for a in attempts:
            key = f"{a.subject_id}:{a.topic_id}:{a.cognitive_level}"
            by_key.setdefault(key, []).append(a)

        result = []
        for key, attempts_group in by_key.items():
            subject_id, topic_id, cognitive_level = key.split(":", 2)
            caps = self._compute_capability(attempts_group)
            result.append(
                DimensionCapability(
                    subject_id=subject_id,
                    topic_id=topic_id,
                    cognitive_level=cognitive_level,
                    **caps,
                )
            )
        return sorted(result, key=lambda x: x.priority_score, reverse=True)

    def _compute_capability(self, attempts: List[Attempt]) -> Dict[str, float]:
        """Thin wrapper so this service does not hard-depend on adaptive_queue internals."""
        from web.services.adaptive_queue import _compute_capability

        return _compute_capability(attempts)

    def weak_area_topics(self, attempts: List[Attempt], top_n: int = 3) -> List[str]:
        """Return the top N topic IDs most needing practice."""
        ranked = rank_topics_for_practice(attempts)
        return [r.topic_id for r in ranked[:top_n]]


class PdfExporter:
    """Generates a printable HTML practice sheet for weak areas.

    Returns HTML bytes so the browser can render and print-to-PDF without
    adding a PDF-generation dependency. A true binary PDF renderer can be
    swapped in later.
    """

    def __init__(self, repository: QuestionRepository):
        self.repository = repository

    def export_weak_area(
        self,
        attempts: List[Attempt],
        top_n: int = 3,
    ) -> bytes:
        """Return an HTML document with weak-area questions and answer key."""
        service = CapabilityService()
        ranked = rank_topics_for_practice(attempts)
        selected_questions: List[Question] = []
        seen_ids = set()
        for topic_cap in ranked[:top_n]:
            for q in self.repository.get_by_topic(topic_cap.topic_id):
                if q.id not in seen_ids:
                    selected_questions.append(q)
                    seen_ids.add(q.id)

        # If no attempts yet, fall back to a balanced sample.
        if not selected_questions:
            all_q = self.repository.get_all()
            random.shuffle(all_q)
            selected_questions = all_q[:10]

        html = self._render_html(selected_questions)
        return html.encode("utf-8")

    def _render_html(self, questions: List[Question]) -> str:
        lines = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "<meta charset='UTF-8'>",
            "<title>Dr. Math Nursing — Weak Area Practice</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 24px; line-height: 1.5; }",
            "h1 { font-size: 18px; }",
            ".question { margin-bottom: 20px; page-break-inside: avoid; }",
            ".options { margin-left: 20px; }",
            ".answer-key { margin-top: 30px; border-top: 1px solid #ccc; padding-top: 10px; }",
            "@media print { .no-print { display: none; } }",
            "</style>",
            "</head>",
            "<body>",
            "<h1>Dr. Math — Nursing Weak Area Practice</h1>",
            f"<p class='no-print'>Generated: {_now_iso()}</p>",
        ]
        for i, q in enumerate(questions, 1):
            lines.append(f"<div class='question'>")
            lines.append(f"<p><strong>Q{i}.</strong> {q.question}</p>")
            lines.append("<div class='options'>")
            for opt in q.options:
                lines.append(f"<p>{opt}</p>")
            lines.append("</div>")
            lines.append("</div>")

        lines.append("<div class='answer-key'>")
        lines.append("<h2>Answer Key</h2>")
        for i, q in enumerate(questions, 1):
            lines.append(f"<p>Q{i}: {q.correct_answer} — {q.explanation}</p>")
        lines.append("</div>")
        lines.append("</body></html>")
        return "\n".join(lines)


class ReportService:
    """Accepts and stores user reports about questionable content."""

    def __init__(self, log_path: Path = REPORT_LOG_PATH):
        self.log_path = log_path

    def report(self, question_id: int, reason: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Append a report to the JSON log and return the record."""
        entry = {
            "question_id": question_id,
            "reason": reason,
            "user_id": user_id,
            "reported_at": _now_iso(),
        }
        records = self._read()
        records.append(entry)
        self._write(records)
        return entry

    def _read(self) -> List[Dict[str, Any]]:
        if not self.log_path.exists():
            return []
        try:
            return json.loads(self.log_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []

    def _write(self, records: List[Dict[str, Any]]) -> None:
        self.log_path.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")

    def list_reports(self) -> List[Dict[str, Any]]:
        return self._read()


class NursingService:
    """Facade exposing all nursing business operations."""

    def __init__(self, repository: Optional[QuestionRepository] = None):
        self.repository = repository or JsonFileQuestionRepository()
        self.diagnostic = DiagnosticBuilder(self.repository)
        self.practice = PracticeBuilder(self.repository)
        self.mock = MockBuilder(self.repository)
        self.capability = CapabilityService()
        self.pdf = PdfExporter(self.repository)
        self.report = ReportService()
