"""Pydantic domain models for the nursing practice module."""
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from web.domain.constants import (
    CognitiveLevel,
    QuestionContext,
    QuestionFormat,
    VerificationStatus,
)


class Question(BaseModel):
    """A single nursing practice question. v1 is MCQ-only."""

    id: int
    subject_id: str
    topic_id: str
    concept_tag: str
    difficulty: int = Field(ge=1, le=3)
    cognitive_level: CognitiveLevel
    context: QuestionContext
    format: QuestionFormat = QuestionFormat.MCQ
    question: str
    options: List[str]
    correct_answer: str = Field(pattern=r"^[A-D]$")
    explanation: str
    source: str
    source_url: Optional[str] = None
    source_section: Optional[str] = None
    verified_at: Optional[str] = None
    verification_status: VerificationStatus
    verified_by: Optional[str] = None
    last_reviewed: Optional[str] = None
    telugu_hint: Optional[str] = None

    @field_validator("options")
    @classmethod
    def _exactly_four_options(cls, v: List[str]) -> List[str]:
        if len(v) != 4:
            raise ValueError("MCQ must have exactly 4 options")
        return v


class QuestionBankMeta(BaseModel):
    """Metadata block from a nursing question bank JSON file."""

    total_questions: int
    language: str
    source: str
    verification_status: VerificationStatus
    verified_by: Optional[str] = None
    last_reviewed: Optional[str] = None
    generated_at: Optional[str] = None
    dimensions: Optional[dict] = None


class QuestionBank(BaseModel):
    """Root model for a nursing question bank JSON file."""

    topic: str
    exam_pattern: str
    meta: QuestionBankMeta
    questions: List[Question]


class TopicSummary(BaseModel):
    subject_id: str
    topic_id: str
    name_en: str
    name_te: str
    question_count: int


class Capability(BaseModel):
    accuracy: float = Field(ge=0.0, le=1.0)
    speed_score: float = Field(ge=0.0, le=1.0)
    confidence_gap: float = Field(ge=0.0, le=1.0)
    consistency_score: float = Field(ge=0.0, le=1.0)
    priority_score: float = Field(ge=0.0, le=1.0)


class SubjectCapability(Capability):
    subject_id: str


class TopicCapability(Capability):
    subject_id: str
    topic_id: str


class DimensionCapability(Capability):
    subject_id: str
    topic_id: str
    cognitive_level: str


class Attempt(BaseModel):
    question_id: int
    selected_option: str
    is_correct: bool
    time_seconds: float
    confidence: int = Field(ge=1, le=5)
    subject_id: str
    topic_id: str
    cognitive_level: str


class DiagnosticResult(BaseModel):
    attempts: List[Attempt]
    subject_capabilities: List[SubjectCapability]
    topic_capabilities: List[TopicCapability]
    dimension_capabilities: List[DimensionCapability]


class PracticeSession(BaseModel):
    mode: str  # "diagnostic", "topic", "mock", "weak-area", "dimension-drill"
    subject_id: Optional[str] = None
    topic_id: Optional[str] = None
    cognitive_level: Optional[str] = None
    context: Optional[str] = None
    questions: List[Question]
