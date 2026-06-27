"""Unit tests for the nursing question repository."""
import pytest

from web.domain.constants import CognitiveLevel, QuestionContext
from web.domain.models import QuestionBank
from web.repositories.question_repository import JsonFileQuestionRepository


@pytest.fixture
def repo():
    return JsonFileQuestionRepository()


def test_seed_bank_validates(repo):
    bank = repo._bank
    assert isinstance(bank, QuestionBank)
    assert bank.meta.total_questions == len(bank.questions)


def test_all_questions_have_dimensions(repo):
    for q in repo.get_all():
        assert isinstance(q.cognitive_level, CognitiveLevel)
        assert isinstance(q.context, QuestionContext)
        assert q.format.value == "mcq"
        assert q.verified_by
        assert q.last_reviewed
        assert len(q.options) == 4


def test_filter_by_subject(repo):
    qs = repo.get_by_subject("anatomy_physiology")
    assert len(qs) > 0
    assert all(q.subject_id == "anatomy_physiology" for q in qs)


def test_filter_by_topic_and_cognitive(repo):
    qs = repo.filter(
        topic_id="ap_cardiovascular",
        cognitive_level=CognitiveLevel.REMEMBER,
    )
    assert len(qs) > 0
    assert all(q.topic_id == "ap_cardiovascular" for q in qs)
    assert all(q.cognitive_level == CognitiveLevel.REMEMBER for q in qs)


def test_filter_by_context_calculation(repo):
    qs = repo.filter(context=QuestionContext.CALCULATION)
    assert len(qs) > 0
    assert all(q.context == QuestionContext.CALCULATION for q in qs)


def test_get_question_by_id(repo):
    q = repo.get_by_id(1)
    assert q is not None
    assert q.id == 1


def test_count_by_subject(repo):
    counts = repo.count_by_subject()
    assert "anatomy_physiology" in counts
    assert sum(counts.values()) == repo.get_meta()["total_questions"]


def test_list_topics(repo):
    topics = repo.list_topics(subject_id="anatomy_physiology")
    assert "ap_cardiovascular" in topics
    assert len(topics) == len(set(topics))


def test_empty_filter_combination(repo):
    qs = repo.filter(subject_id="nonexistent_subject")
    assert qs == []
