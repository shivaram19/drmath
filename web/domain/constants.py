"""Domain constants for the nursing practice module."""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class CognitiveLevel(str, Enum):
    """Bloom-derived cognitive demand levels used for dimension tagging."""

    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"


class QuestionContext(str, Enum):
    """Context dimension: how the question is framed."""

    THEORY = "theory"
    SCENARIO = "scenario"
    CALCULATION = "calculation"


class QuestionFormat(str, Enum):
    """Question format. v1 is MCQ-only; other formats are reserved for later phases."""

    MCQ = "mcq"


class VerificationStatus(str, Enum):
    """Content verification state."""

    REVIEWED = "reviewed"
    PENDING = "pending"
    FLAGGED = "flagged"


@dataclass(frozen=True)
class ExamPattern:
    key: str
    name: str
    body: str
    total_questions: int
    total_marks: int
    duration_minutes: int
    negative_marking: bool
    negative_mark_fraction: float
    language: str


EXAM_PATTERNS: Dict[str, ExamPattern] = {
    "mhsrb_staff_nurse": ExamPattern(
        key="mhsrb_staff_nurse",
        name="MHSRB Telangana Staff Nurse / Nursing Officer",
        body="Medical & Health Services Recruitment Board, Telangana",
        total_questions=80,
        total_marks=80,
        duration_minutes=60,
        negative_marking=False,
        negative_mark_fraction=0.0,
        language="English",
    ),
    "tspsc_staff_nurse": ExamPattern(
        key="tspsc_staff_nurse",
        name="TSPSC Staff Nurse",
        body="Telangana State Public Service Commission",
        total_questions=150,
        total_marks=150,
        duration_minutes=150,
        negative_marking=False,
        negative_mark_fraction=0.0,
        language="English & Telugu",
    ),
}

DEFAULT_PATTERN_KEY = "mhsrb_staff_nurse"
DEFAULT_SOURCE = "INC GNM Syllabus / Standard Nursing Textbooks"
DEFAULT_VERIFIED_BY = "GNM syllabus cross-check + INC textbook review"

TARGET_SECONDS_PER_QUESTION = 45  # 60 min / 80 questions

# Diagnostic config
DIAGNOSTIC_QUESTIONS_PER_SUBJECT = 2
DIAGNOSTIC_DEFAULT_LENGTH = 20

# Adaptive queue weights (must sum to 1.0)
ADAPTIVE_WEIGHTS = {
    "accuracy": 0.50,
    "speed": 0.25,
    "confidence_gap": 0.15,
    "consistency": 0.10,
}

# Subject display order
SUBJECT_ORDER: List[str] = [
    "anatomy_physiology",
    "fundamentals_nursing",
    "microbiology",
    "pharmacology",
    "medical_surgical",
    "community_health",
    "mental_health",
    "child_health",
    "midwifery",
    "nutrition",
    "first_aid",
]
