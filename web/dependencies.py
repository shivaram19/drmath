"""Composition root for FastAPI dependencies.

All concrete wiring lives here so routers stay portable and testable. Tests can
override any provider via `app.dependency_overrides[provider]`.
"""
from db.database import get_db  # noqa: F401
from web.adapters.analytics import JSONLAnalyticsSink
from web.adapters.survey_store import JSONLSurveyStore
from web.ports import AnalyticsSink, SurveyStore
from web.services.nursing_service import NursingService


def get_nursing_service() -> NursingService:
    """Return the default nursing service facade."""
    return NursingService()


def get_analytics_sink() -> AnalyticsSink:
    """Return the default analytics sink (local JSONL)."""
    return JSONLAnalyticsSink()


def get_survey_store() -> SurveyStore:
    """Return the default survey store (local JSONL)."""
    return JSONLSurveyStore()
