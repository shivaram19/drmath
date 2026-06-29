"""Integration tests for the nursing API router."""
import json

import pytest
from fastapi.testclient import TestClient

from db import crud
from db.database import SessionLocal
from web.adapters.analytics import JSONLAnalyticsSink
from web.adapters.survey_store import JSONLSurveyStore
from web.dependencies import get_analytics_sink, get_survey_store
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
    assert 'property="og:title"' in response.text
    assert 'og:image' in response.text


def test_nursing_privacy_page_returns_200(client):
    response = client.get("/nursing/privacy")
    assert response.status_code == 200
    assert "Privacy Notice" in response.text
    assert "Digital Personal Data Protection Act" in response.text
    assert "Grievance Officer" in response.text
    assert "Server logs" in response.text
    assert "30 days" in response.text


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


def _override_analytics_sink(path):
    app.dependency_overrides[get_analytics_sink] = lambda: JSONLAnalyticsSink(path=path)


def test_record_analytics_event(client, tmp_path):
    path = tmp_path / "nursing_events.jsonl"
    _override_analytics_sink(path)
    try:
        response = client.post(
            "/api/nursing/analytics",
            json={
                "event": "landing_quiz_started",
                "timestamp": "2026-05-05T12:00:00Z",
                "consent_version": "2026-06-28",
                "metadata": {"source": "test"},
            },
        )
    finally:
        app.dependency_overrides.pop(get_analytics_sink, None)

    assert response.status_code == 200
    assert response.json()["status"] == "recorded"
    assert path.exists()
    lines = path.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["event"] == "landing_quiz_started"
    assert record["consent_version"] == "2026-06-28"
    assert record["metadata"]["source"] == "test"


def test_record_analytics_event_with_utm(client, tmp_path):
    path = tmp_path / "nursing_events.jsonl"
    _override_analytics_sink(path)
    try:
        response = client.post(
            "/api/nursing/analytics",
            json={
                "event": "apk_download_clicked",
                "timestamp": "2026-05-05T12:00:00Z",
                "consent_version": "2026-06-28",
                "metadata": {
                    "placement": "result_cta",
                    "utm_source": "web_nursing",
                    "utm_medium": "result_cta",
                    "utm_campaign": "nursing_full_app_install",
                    "utm_content": "after_quiz",
                },
            },
        )
    finally:
        app.dependency_overrides.pop(get_analytics_sink, None)

    assert response.status_code == 200
    assert response.json()["status"] == "recorded"
    lines = path.read_text(encoding="utf-8").strip().split("\n")
    record = json.loads(lines[0])
    assert record["metadata"]["utm_source"] == "web_nursing"
    assert record["metadata"]["utm_content"] == "after_quiz"


def test_record_analytics_event_rejects_long_utm(client, tmp_path):
    path = tmp_path / "nursing_events.jsonl"
    _override_analytics_sink(path)
    try:
        response = client.post(
            "/api/nursing/analytics",
            json={
                "event": "apk_download_clicked",
                "timestamp": "2026-05-05T12:00:00Z",
                "consent_version": "2026-06-28",
                "metadata": {
                    "utm_campaign": "x" * 129,
                },
            },
        )
    finally:
        app.dependency_overrides.pop(get_analytics_sink, None)

    assert response.status_code == 422
    assert not path.exists()


def test_existing_math_homepage_unaffected(client):
    response = client.get("/")
    assert response.status_code == 200


def test_discovery_survey_records_response(client, tmp_path):
    path = tmp_path / "nursing_discovery_survey.jsonl"
    app.dependency_overrides[get_survey_store] = lambda: JSONLSurveyStore(path=path)
    try:
        response = client.post(
            "/api/nursing/discovery-survey",
            json={
                "interested": "yes",
                "preferred_channel": "telegram",
                "cadence": "daily",
                "biggest_challenge": "time_management",
                "other_challenge": "Working night shifts",
                "language": "en",
            },
        )
    finally:
        app.dependency_overrides.pop(get_survey_store, None)

    assert response.status_code == 200
    assert response.json()["status"] == "recorded"
    assert path.exists()
    lines = path.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["response"]["interested"] == "yes"
    assert record["response"]["preferred_channel"] == "telegram"
    assert record["response"]["other_challenge"] == "Working night shifts"


def test_discovery_survey_rejects_invalid_interested(client):
    response = client.post(
        "/api/nursing/discovery-survey",
        json={
            "interested": "",
            "preferred_channel": "telegram",
            "cadence": "daily",
            "biggest_challenge": "time_management",
        },
    )
    assert response.status_code == 422


def _attempt_payload(client_attempt_id=None, question_id=1, session_id="test_sync"):
    import uuid
    return {
        "client_attempt_id": client_attempt_id or uuid.uuid4().hex,
        "session_id": session_id,
        "question_id": question_id,
        "selected_option": "A",
        "is_correct": True,
        "answered_at": "2026-05-05T12:00:00Z",
        "subject_id": "anatomy_physiology",
        "topic_id": "ap_cardiovascular",
        "cognitive_level": "remember",
    }


def test_sync_attempts_records_batch(client):
    response = client.post(
        "/api/nursing/attempts",
        json={"attempts": [_attempt_payload(question_id=1), _attempt_payload(question_id=2)]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["received"] == 2
    assert data["accepted"] == 2
    assert data["duplicates_ignored"] == 0


def test_sync_attempts_ignores_duplicates(client):
    import uuid
    session_id = f"test_dup_{uuid.uuid4().hex}"
    dup_id = f"dup-{uuid.uuid4().hex}"
    client.post(
        "/api/nursing/attempts",
        json={"attempts": [_attempt_payload(dup_id, 10, session_id)]},
    )
    response = client.post(
        "/api/nursing/attempts",
        json={"attempts": [_attempt_payload(dup_id, 10, session_id)]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["received"] == 1
    assert data["accepted"] == 0
    assert data["duplicates_ignored"] == 1
    db = SessionLocal()
    try:
        assert crud.count_nursing_attempts(db, session_id=session_id) == 1
    finally:
        db.close()


def test_sync_attempts_rejects_missing_required(client):
    response = client.post(
        "/api/nursing/attempts",
        json={"attempts": [{"question_id": 1}]},
    )
    assert response.status_code == 422


def test_get_concept_for_topic(client):
    response = client.get("/api/nursing/concept?topic_id=ap_cardiovascular")
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == "ap_cardiovascular"
    assert data["source_count"] > 0
    assert len(data["explanation"]) > 0


def test_get_concept_unknown_topic_returns_404(client):
    response = client.get("/api/nursing/concept?topic_id=nonexistent_topic_xyz")
    assert response.status_code == 404


def test_get_concept_rejects_empty_topic(client):
    response = client.get("/api/nursing/concept?topic_id=")
    assert response.status_code == 422


def test_discovery_survey_optional_other_challenge(client, tmp_path):
    path = tmp_path / "nursing_discovery_survey.jsonl"
    app.dependency_overrides[get_survey_store] = lambda: JSONLSurveyStore(path=path)
    try:
        response = client.post(
            "/api/nursing/discovery-survey",
            json={
                "interested": "maybe",
                "preferred_channel": "whatsapp",
                "cadence": "thrice_weekly",
                "biggest_challenge": "syllabus_coverage",
            },
        )
    finally:
        app.dependency_overrides.pop(get_survey_store, None)

    assert response.status_code == 200
    lines = path.read_text(encoding="utf-8").strip().split("\n")
    record = json.loads(lines[0])
    assert record["response"]["other_challenge"] is None
    assert record["response"]["language"] == "te"
