"""FastAPI router for the nursing practice module."""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from pathlib import Path

from fastapi import APIRouter, Query, Request, Form, Depends
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel, field_validator

from web.dependencies import get_analytics_sink, get_nursing_service, get_survey_store
from web.domain.constants import DEFAULT_PATTERN_KEY, CognitiveLevel, QuestionContext
from web.domain.models import Attempt, Question
from web.ports import AnalyticsSink, SurveyStore
from web.services.nursing_service import NursingService


router = APIRouter(prefix="/nursing", tags=["nursing"])
api_router = APIRouter(prefix="/api/nursing", tags=["nursing-api"])

NURSING_LANDING_PATH = Path(__file__).resolve().parent.parent / "static" / "nursing" / "index.html"
NURSING_PRIVACY_PATH = Path(__file__).resolve().parent.parent / "static" / "nursing" / "privacy.html"


# ---------------------------------------------------------------------------
# HTML landing page (PWA shell)
# ---------------------------------------------------------------------------

@router.get("", response_class=HTMLResponse)
def nursing_home():
    """Serve the PWA landing page as a fallback when nginx is not in front."""
    return FileResponse(NURSING_LANDING_PATH)


@router.get("/privacy", response_class=HTMLResponse)
def nursing_privacy():
    """Serve the DPDPA privacy notice as a fallback when nginx is not in front."""
    return FileResponse(NURSING_PRIVACY_PATH)


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

class DiagnosticStartRequest(BaseModel):
    num_questions: int = 20


class DiagnosticStartResponse(BaseModel):
    questions: List[Dict[str, Any]]


class MockStartResponse(BaseModel):
    pattern_key: str
    total_questions: int
    questions: List[Dict[str, Any]]


class ReportRequest(BaseModel):
    question_id: int
    reason: str
    user_id: Optional[str] = None


class ReportResponse(BaseModel):
    status: str
    report: Dict[str, Any]


class PdfRequest(BaseModel):
    attempts: List[Attempt]
    top_n: int = 3


@api_router.get("/status")
def nursing_status(service: NursingService = Depends(get_nursing_service)) -> Dict[str, str]:
    meta = service.repository.get_meta()
    return {
        "status": "healthy",
        "module": "nursing",
        "questions": str(meta.get("total_questions", 0)),
    }


@api_router.get("/topics")
def nursing_topics(service: NursingService = Depends(get_nursing_service)) -> Dict[str, Any]:
    subjects = service.repository.list_subjects()
    topics = {}
    for subject_id in subjects:
        topics[subject_id] = service.repository.list_topics(subject_id=subject_id)
    return {
        "subjects": subjects,
        "topics_by_subject": topics,
        "counts": service.repository.count_by_subject(),
    }


@api_router.get("/questions")
def nursing_questions(
    subject_id: Optional[str] = Query(None),
    topic_id: Optional[str] = Query(None),
    cognitive_level: Optional[CognitiveLevel] = Query(None),
    context: Optional[QuestionContext] = Query(None),
    difficulty: Optional[int] = Query(None),
    concept_tag: Optional[str] = Query(None),
    limit: Optional[int] = Query(None),
    service: NursingService = Depends(get_nursing_service),
) -> List[Dict[str, Any]]:
    questions = service.practice.by_topic(
        subject_id=subject_id,
        topic_id=topic_id,
        cognitive_level=cognitive_level,
        context=context,
        difficulty=difficulty,
        concept_tag=concept_tag,
        limit=limit,
    )
    return [q.model_dump() for q in questions]


@api_router.post("/diagnostic/start", response_model=DiagnosticStartResponse)
def diagnostic_start(
    payload: DiagnosticStartRequest,
    service: NursingService = Depends(get_nursing_service),
) -> DiagnosticStartResponse:
    questions = service.diagnostic.build(num_questions=payload.num_questions)
    return DiagnosticStartResponse(questions=[q.model_dump() for q in questions])


@api_router.post("/mock/start", response_model=MockStartResponse)
def mock_start(
    pattern_key: str = DEFAULT_PATTERN_KEY,
    service: NursingService = Depends(get_nursing_service),
) -> MockStartResponse:
    questions = service.mock.build(pattern_key=pattern_key)
    return MockStartResponse(
        pattern_key=pattern_key,
        total_questions=len(questions),
        questions=[q.model_dump() for q in questions],
    )


@api_router.post("/report", response_model=ReportResponse)
def report_question(
    payload: ReportRequest,
    service: NursingService = Depends(get_nursing_service),
) -> ReportResponse:
    record = service.report.report(
        question_id=payload.question_id,
        reason=payload.reason,
        user_id=payload.user_id,
    )
    return ReportResponse(status="recorded", report=record)


# ---------------------------------------------------------------------------
# Discovery survey (Phase 10.9a)
# ---------------------------------------------------------------------------

class DiscoverySurveyRequest(BaseModel):
    interested: str  # yes | maybe | no
    preferred_channel: str  # whatsapp | telegram | none
    cadence: str  # daily | thrice_weekly | weekends
    biggest_challenge: str
    other_challenge: Optional[str] = None
    language: str = "te"

    @field_validator("interested")
    @classmethod
    def _validate_interested(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in {"yes", "maybe", "no"}:
            raise ValueError("interested must be yes, maybe, or no")
        return value

    @field_validator("preferred_channel")
    @classmethod
    def _validate_channel(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in {"whatsapp", "telegram", "none"}:
            raise ValueError("preferred_channel must be whatsapp, telegram, or none")
        return value

    @field_validator("cadence")
    @classmethod
    def _validate_cadence(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in {"daily", "thrice_weekly", "weekends"}:
            raise ValueError("cadence must be daily, thrice_weekly, or weekends")
        return value

    @field_validator("biggest_challenge", "language")
    @classmethod
    def _strip_and_lower(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("must be a string")
        return value.strip().lower()


class DiscoverySurveyResponse(BaseModel):
    status: str


@api_router.post("/discovery-survey", response_model=DiscoverySurveyResponse)
def discovery_survey(
    payload: DiscoverySurveyRequest,
    store: SurveyStore = Depends(get_survey_store),
) -> DiscoverySurveyResponse:
    """Record a voluntary, non-PII discovery-survey response.

    The response is stored independently of analytics consent because it is an
    explicit user submission, not passive telemetry. No phone numbers or chat_ids
    are collected at this stage.
    """
    store.save_response(payload.model_dump())
    return DiscoverySurveyResponse(status="recorded")


@api_router.post("/analyze")
def analyze_attempts(
    attempts: List[Attempt],
    service: NursingService = Depends(get_nursing_service),
) -> Dict[str, Any]:
    result = service.capability.analyze(attempts)
    return {
        "subject_capabilities": [s.model_dump() for s in result.subject_capabilities],
        "topic_capabilities": [t.model_dump() for t in result.topic_capabilities],
        "dimension_capabilities": [d.model_dump() for d in result.dimension_capabilities],
    }


@api_router.post("/pdf")
def weak_area_pdf(
    payload: PdfRequest,
    service: NursingService = Depends(get_nursing_service),
) -> HTMLResponse:
    """Return a printable HTML practice sheet for weak areas."""
    html_bytes = service.pdf.export_weak_area(payload.attempts, top_n=payload.top_n)
    return HTMLResponse(
        content=html_bytes.decode("utf-8"),
        headers={"Content-Disposition": "attachment; filename=weak-area-practice.html"},
    )


# ---------------------------------------------------------------------------
# Analytics events (consent-gated)
# ---------------------------------------------------------------------------

class EventRequest(BaseModel):
    event: str
    timestamp: str
    consent_version: str
    metadata: Dict[str, Any] = {}

    @field_validator('metadata')
    @classmethod
    def _validate_utm_fields(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize campaign UTM fields to prevent log injection."""
        if not isinstance(value, dict):
            raise ValueError('metadata must be an object')
        for field in ('utm_source', 'utm_medium', 'utm_campaign', 'utm_content'):
            val = value.get(field)
            if val is not None and (not isinstance(val, str) or len(val) > 128):
                raise ValueError(f'{field} must be a string with max 128 characters')
        return value


@api_router.post("/analytics")
def record_event(
    payload: EventRequest,
    sink: AnalyticsSink = Depends(get_analytics_sink),
) -> JSONResponse:
    """Record an anonymous, consent-gated analytics event.

    No IP, device ID, or personal identifiers are stored. Events are appended
    to a local JSONL file and retained in line with the DPDPA privacy notice.
    """
    sink.record_event(
        event=payload.event,
        client_timestamp=payload.timestamp,
        consent_version=payload.consent_version,
        metadata=payload.metadata,
    )
    return JSONResponse({"status": "recorded"})
