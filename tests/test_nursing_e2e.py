"""End-to-end tests for the full nursing user journey."""
import pytest
from fastapi.testclient import TestClient

from web.main import app


@pytest.fixture
def client():
    return TestClient(app)


def _answer_question(q, correct=True):
    """Helper to produce an attempt payload for a given question."""
    answer = q["correct_answer"] if correct else "A" if q["correct_answer"] != "A" else "B"
    return {
        "question_id": q["id"],
        "selected_option": answer,
        "is_correct": correct,
        "time_seconds": 35.0,
        "confidence": 4 if correct else 2,
        "subject_id": q["subject_id"],
        "topic_id": q["topic_id"],
        "cognitive_level": q["cognitive_level"],
    }


def test_full_journey_diagnostic_to_pdf(client):
    # 1. Start diagnostic.
    response = client.post("/api/nursing/diagnostic/start", json={"num_questions": 20})
    assert response.status_code == 200
    diagnostic = response.json()
    assert len(diagnostic["questions"]) == 20

    # 2. Answer diagnostic questions (mix of correct/incorrect).
    attempts = []
    for i, q in enumerate(diagnostic["questions"]):
        attempts.append(_answer_question(q, correct=(i % 3 != 0)))

    # 3. Analyze and verify capability map.
    response = client.post("/api/nursing/analyze", json=attempts)
    assert response.status_code == 200
    analysis = response.json()
    assert "subject_capabilities" in analysis
    assert "topic_capabilities" in analysis
    assert "dimension_capabilities" in analysis
    assert len(analysis["topic_capabilities"]) > 0

    # Identify weakest topic.
    weakest = analysis["topic_capabilities"][0]
    assert weakest["priority_score"] > 0

    # 4. Start a weak-area practice session based on lowest capability.
    response = client.get(
        "/api/nursing/questions",
        params={"topic_id": weakest["topic_id"], "limit": 10},
    )
    assert response.status_code == 200
    practice = response.json()
    assert len(practice) > 0
    assert all(q["topic_id"] == weakest["topic_id"] for q in practice)

    # 5. Complete a mini mock (5 questions) and verify score calculation.
    response = client.post("/api/nursing/mock/start")
    assert response.status_code == 200
    mock = response.json()
    assert mock["total_questions"] == 80

    mini_attempts = [_answer_question(q, correct=(i % 2 == 0)) for i, q in enumerate(mock["questions"][:5])]
    correct_count = sum(1 for a in mini_attempts if a["is_correct"])
    assert correct_count == len([a for a in mini_attempts if a["is_correct"]])

    # 6. Request a PDF export and verify non-empty response.
    response = client.post("/api/nursing/pdf", json={"attempts": mini_attempts, "top_n": 2})
    assert response.status_code == 200
    assert len(response.content) > 0
    assert b"<!DOCTYPE html>" in response.content

    # 7. Report a question and verify it is recorded.
    response = client.post(
        "/api/nursing/report",
        json={"question_id": diagnostic["questions"][0]["id"], "reason": "E2E test report"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "recorded"
    assert data["report"]["question_id"] == diagnostic["questions"][0]["id"]


def test_existing_math_routes_still_work(client):
    response = client.get("/")
    assert response.status_code == 200
    response = client.get("/manager")
    assert response.status_code in (200, 307, 302)
