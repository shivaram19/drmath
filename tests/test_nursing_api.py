"""Integration tests for the nursing API router."""
import pytest
from fastapi.testclient import TestClient

from web.domain.constants import CognitiveLevel, QuestionContext
from web.domain.models import Attempt
from web.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_status_endpoint(client):
    response = client.get("/api/nursing/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["module"] == "nursing"
    assert int(data["questions"]) > 0


def test_topics_endpoint(client):
    response = client.get("/api/nursing/topics")
    assert response.status_code == 200
    data = response.json()
    assert "subjects" in data
    assert "topics_by_subject" in data
    assert "counts" in data
    assert "anatomy_physiology" in data["subjects"]


def test_questions_filter_by_topic(client):
    response = client.get("/api/nursing/questions?topic_id=ap_cardiovascular")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(q["topic_id"] == "ap_cardiovascular" for q in data)


def test_questions_filter_by_cognitive_and_context(client):
    response = client.get(
        "/api/nursing/questions",
        params={
            "cognitive_level": CognitiveLevel.REMEMBER.value,
            "context": QuestionContext.THEORY.value,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(q["cognitive_level"] == CognitiveLevel.REMEMBER.value for q in data)
    assert all(q["context"] == QuestionContext.THEORY.value for q in data)


def test_diagnostic_start(client):
    response = client.post("/api/nursing/diagnostic/start", json={"num_questions": 20})
    assert response.status_code == 200
    data = response.json()
    assert len(data["questions"]) == 20


def test_mock_start(client):
    response = client.post("/api/nursing/mock/start")
    assert response.status_code == 200
    data = response.json()
    assert data["total_questions"] == 80
    assert len(data["questions"]) == 80


def test_report_question(client):
    response = client.post(
        "/api/nursing/report",
        json={"question_id": 5, "reason": "Option C looks wrong"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "recorded"
    assert data["report"]["question_id"] == 5


def test_analyze_attempts(client):
    attempts = [
        Attempt(
            question_id=1,
            selected_option="A",
            is_correct=False,
            time_seconds=60.0,
            confidence=2,
            subject_id="anatomy_physiology",
            topic_id="ap_cardiovascular",
            cognitive_level="remember",
        ).model_dump(),
    ]
    response = client.post("/api/nursing/analyze", json=attempts)
    assert response.status_code == 200
    data = response.json()
    assert "subject_capabilities" in data
    assert "topic_capabilities" in data
    assert "dimension_capabilities" in data


def test_nursing_landing_page_returns_200(client):
    response = client.get("/nursing")
    assert response.status_code == 200
    assert "MathWise Nursing" in response.text


def test_nursing_privacy_page_returns_200(client):
    response = client.get("/nursing/privacy")
    assert response.status_code == 200
    assert "Privacy Notice" in response.text
    assert "Digital Personal Data Protection Act" in response.text


def test_pdf_export_post(client):
    attempts = [
        Attempt(
            question_id=1,
            selected_option="A",
            is_correct=False,
            time_seconds=60.0,
            confidence=2,
            subject_id="anatomy_physiology",
            topic_id="ap_cardiovascular",
            cognitive_level="remember",
        ).model_dump(),
    ]
    response = client.post("/api/nursing/pdf", json={"attempts": attempts, "top_n": 2})
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text
    assert "Answer Key" in response.text


def test_existing_math_homepage_unaffected(client):
    response = client.get("/")
    assert response.status_code == 200
