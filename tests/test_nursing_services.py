"""Unit tests for the nursing business service layer."""
import pytest

from web.domain.constants import CognitiveLevel, QuestionContext
from web.domain.models import Attempt
from web.repositories.question_repository import JsonFileQuestionRepository
from web.services.nursing_service import NursingService


@pytest.fixture
def service():
    return NursingService()


def test_diagnostic_set_length_and_coverage(service):
    questions = service.diagnostic.build(num_questions=20)
    assert len(questions) == 20
    assert len({q.subject_id for q in questions}) >= 2
    assert len({q.topic_id for q in questions}) >= 2


def test_diagnostic_no_duplicates(service):
    questions = service.diagnostic.build(num_questions=30)
    ids = [q.id for q in questions]
    assert len(ids) == len(set(ids))


def test_practice_filter_by_topic_and_cognitive(service):
    questions = service.practice.by_topic(
        topic_id="ap_cardiovascular",
        cognitive_level=CognitiveLevel.REMEMBER,
    )
    assert len(questions) > 0
    assert all(q.topic_id == "ap_cardiovascular" for q in questions)
    assert all(q.cognitive_level == CognitiveLevel.REMEMBER for q in questions)


def test_practice_filter_by_context(service):
    questions = service.practice.by_topic(context=QuestionContext.CALCULATION)
    assert len(questions) > 0
    assert all(q.context == QuestionContext.CALCULATION for q in questions)


def test_mock_returns_expected_count(service):
    questions = service.mock.build()
    assert len(questions) == 80


def test_mock_no_duplicates(service):
    questions = service.mock.build()
    ids = [q.id for q in questions]
    assert len(ids) == len(set(ids))


def test_mock_balanced_by_subject(service):
    questions = service.mock.build()
    counts = {}
    for q in questions:
        counts[q.subject_id] = counts.get(q.subject_id, 0) + 1
    assert len(counts) >= 2
    # Every subject with questions in the bank should appear.
    for subject_id in service.repository.list_subjects():
        assert subject_id in counts


def test_capability_analysis(service):
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
        ),
        Attempt(
            question_id=2,
            selected_option="B",
            is_correct=True,
            time_seconds=30.0,
            confidence=4,
            subject_id="fundamentals_nursing",
            topic_id="fn_vital_signs",
            cognitive_level="remember",
        ),
    ]
    result = service.capability.analyze(attempts)
    assert len(result.attempts) == 2
    assert len(result.subject_capabilities) == 2
    assert len(result.topic_capabilities) == 2
    assert len(result.dimension_capabilities) == 2


def test_weak_area_topics(service):
    attempts = [
        Attempt(
            question_id=1,
            selected_option="A",
            is_correct=False,
            time_seconds=90.0,
            confidence=1,
            subject_id="anatomy_physiology",
            topic_id="ap_cardiovascular",
            cognitive_level="remember",
        ),
        Attempt(
            question_id=2,
            selected_option="B",
            is_correct=True,
            time_seconds=30.0,
            confidence=4,
            subject_id="fundamentals_nursing",
            topic_id="fn_vital_signs",
            cognitive_level="remember",
        ),
    ]
    weak = service.capability.weak_area_topics(attempts, top_n=2)
    assert "ap_cardiovascular" in weak


def test_pdf_export_returns_html_bytes(service):
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
        ),
    ]
    pdf_bytes = service.pdf.export_weak_area(attempts, top_n=2)
    assert len(pdf_bytes) > 0
    assert b"<!DOCTYPE html>" in pdf_bytes
    assert b"Answer Key" in pdf_bytes


def test_pdf_export_fallback_when_no_attempts(service):
    pdf_bytes = service.pdf.export_weak_area([], top_n=2)
    assert len(pdf_bytes) > 0
    assert b"<!DOCTYPE html>" in pdf_bytes


def test_report_question(service, tmp_path):
    # Use a temporary log path so tests do not share state.
    from web.services.nursing_service import ReportService

    report_svc = ReportService(log_path=tmp_path / "reports.json")
    record = report_svc.report(question_id=5, reason="Option C is ambiguous")
    assert record["question_id"] == 5
    assert record["reason"] == "Option C is ambiguous"
    assert "reported_at" in record
    assert len(report_svc.list_reports()) == 1
