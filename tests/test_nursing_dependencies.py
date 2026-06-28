"""Tests for the nursing composition-root dependencies.

These tests prove that `NursingService` and `AnalyticsSink` can be substituted
via `app.dependency_overrides`, which is the prerequisite for mocking nursing
behavior in higher-level tests and for wiring different adapters in production.
"""
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

from web.dependencies import get_analytics_sink, get_nursing_service
from web.main import app
from web.ports import AnalyticsSink
from web.services.nursing_service import NursingService


class FakeRepository:
    def get_meta(self) -> Dict[str, Any]:
        return {"total_questions": 42}


class FakeNursingService(NursingService):
    """A minimal service stand-in that only satisfies the status endpoint."""

    def __init__(self):
        self.repository = FakeRepository()


class FakeAnalyticsSink(AnalyticsSink):
    """Captures events instead of writing to disk."""

    def __init__(self):
        self.events: list = []

    def record_event(
        self,
        event: str,
        client_timestamp: str,
        consent_version: str,
        metadata: Dict[str, Any],
    ) -> None:
        self.events.append(
            {
                "event": event,
                "client_timestamp": client_timestamp,
                "consent_version": consent_version,
                "metadata": metadata,
            }
        )


@pytest.fixture
def client():
    return TestClient(app)


def test_nursing_service_can_be_overridden(client):
    app.dependency_overrides[get_nursing_service] = lambda: FakeNursingService()
    try:
        response = client.get("/api/nursing/status")
    finally:
        app.dependency_overrides.pop(get_nursing_service, None)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["questions"] == "42"


def test_analytics_sink_can_be_overridden(client):
    sink = FakeAnalyticsSink()
    app.dependency_overrides[get_analytics_sink] = lambda: sink
    try:
        response = client.post(
            "/api/nursing/analytics",
            json={
                "event": "test_event",
                "timestamp": "2026-05-05T12:00:00Z",
                "consent_version": "2026-06-28",
                "metadata": {"source": "dependency_test"},
            },
        )
    finally:
        app.dependency_overrides.pop(get_analytics_sink, None)

    assert response.status_code == 200
    assert response.json()["status"] == "recorded"
    assert len(sink.events) == 1
    assert sink.events[0]["event"] == "test_event"
    assert sink.events[0]["metadata"]["source"] == "dependency_test"
