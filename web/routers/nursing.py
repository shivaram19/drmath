"""FastAPI router for the nursing practice module."""
from typing import Any, Dict, List, Optional

from pathlib import Path

from fastapi import APIRouter, Query, Request, Form
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel

from web.domain.constants import DEFAULT_PATTERN_KEY, CognitiveLevel, QuestionContext
from web.domain.models import Attempt, Question
from web.services.nursing_service import NursingService


router = APIRouter(prefix="/nursing", tags=["nursing"])
api_router = APIRouter(prefix="/api/nursing", tags=["nursing-api"])
service = NursingService()

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
def nursing_status() -> Dict[str, str]:
    meta = service.repository.get_meta()
    return {
        "status": "healthy",
        "module": "nursing",
        "questions": str(meta.get("total_questions", 0)),
    }


@api_router.get("/topics")
def nursing_topics() -> Dict[str, Any]:
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
def diagnostic_start(payload: DiagnosticStartRequest) -> DiagnosticStartResponse:
    questions = service.diagnostic.build(num_questions=payload.num_questions)
    return DiagnosticStartResponse(questions=[q.model_dump() for q in questions])


@api_router.post("/mock/start", response_model=MockStartResponse)
def mock_start(pattern_key: str = DEFAULT_PATTERN_KEY) -> MockStartResponse:
    questions = service.mock.build(pattern_key=pattern_key)
    return MockStartResponse(
        pattern_key=pattern_key,
        total_questions=len(questions),
        questions=[q.model_dump() for q in questions],
    )


@api_router.post("/report", response_model=ReportResponse)
def report_question(payload: ReportRequest) -> ReportResponse:
    record = service.report.report(
        question_id=payload.question_id,
        reason=payload.reason,
        user_id=payload.user_id,
    )
    return ReportResponse(status="recorded", report=record)


@api_router.post("/analyze")
def analyze_attempts(attempts: List[Attempt]) -> Dict[str, Any]:
    result = service.capability.analyze(attempts)
    return {
        "subject_capabilities": [s.model_dump() for s in result.subject_capabilities],
        "topic_capabilities": [t.model_dump() for t in result.topic_capabilities],
        "dimension_capabilities": [d.model_dump() for d in result.dimension_capabilities],
    }


@api_router.post("/pdf")
def weak_area_pdf(payload: PdfRequest) -> HTMLResponse:
    """Return a printable HTML practice sheet for weak areas."""
    html_bytes = service.pdf.export_weak_area(payload.attempts, top_n=payload.top_n)
    return HTMLResponse(
        content=html_bytes.decode("utf-8"),
        headers={"Content-Disposition": "attachment; filename=weak-area-practice.html"},
    )
