"""Adaptive queue — ranks questions and topics by demonstrated capability."""
import math
from typing import Dict, List

from web.domain.constants import ADAPTIVE_WEIGHTS, TARGET_SECONDS_PER_QUESTION
from web.domain.models import Attempt, TopicCapability, SubjectCapability


def _speed_score(median_seconds: float) -> float:
    if median_seconds <= 0:
        return 1.0
    ratio = median_seconds / TARGET_SECONDS_PER_QUESTION
    # Score 1.0 at target or below; falls off quadratically.
    return max(0.0, min(1.0, 1.0 - (ratio - 1.0) ** 2))


def _consistency_score(std_dev: float) -> float:
    # Lower std-dev across recent attempts => higher consistency.
    return max(0.0, min(1.0, 1.0 - std_dev))


def _compute_capability(attempts: List[Attempt]) -> Dict[str, float]:
    if not attempts:
        return {
            "accuracy": 0.0,
            "speed_score": 0.0,
            "confidence_gap": 1.0,
            "consistency_score": 0.0,
            "priority_score": 1.0,
        }

    correct = [a for a in attempts if a.is_correct]
    accuracy = len(correct) / len(attempts)

    times = [a.time_seconds for a in correct] or [a.time_seconds for a in attempts]
    median_seconds = sorted(times)[len(times) // 2] if times else TARGET_SECONDS_PER_QUESTION
    speed = _speed_score(median_seconds)

    mean_confidence = sum(a.confidence for a in attempts) / len(attempts)
    # Normalize confidence from 1-5 to 0-1.
    normalized_confidence = (mean_confidence - 1) / 4
    confidence_gap = abs(normalized_confidence - accuracy)

    # Consistency over last 5 attempts.
    recent = attempts[-5:]
    recent_correct = [1 if a.is_correct else 0 for a in recent]
    if len(recent_correct) > 1:
        mean = sum(recent_correct) / len(recent_correct)
        variance = sum((x - mean) ** 2 for x in recent_correct) / len(recent_correct)
        std_dev = math.sqrt(variance)
    else:
        std_dev = 0.5
    consistency = _consistency_score(std_dev)

    priority = (
        (1 - accuracy) * ADAPTIVE_WEIGHTS["accuracy"]
        + (1 - speed) * ADAPTIVE_WEIGHTS["speed"]
        + confidence_gap * ADAPTIVE_WEIGHTS["confidence_gap"]
        + (1 - consistency) * ADAPTIVE_WEIGHTS["consistency"]
    )

    return {
        "accuracy": accuracy,
        "speed_score": speed,
        "confidence_gap": confidence_gap,
        "consistency_score": consistency,
        "priority_score": priority,
    }


def compute_subject_capabilities(attempts: List[Attempt]) -> List[SubjectCapability]:
    by_subject: Dict[str, List[Attempt]] = {}
    for a in attempts:
        by_subject.setdefault(a.subject_id, []).append(a)

    result = []
    for subject_id, subj_attempts in by_subject.items():
        caps = _compute_capability(subj_attempts)
        result.append(SubjectCapability(subject_id=subject_id, **caps))
    return sorted(result, key=lambda x: x.priority_score, reverse=True)


def compute_topic_capabilities(attempts: List[Attempt]) -> List[TopicCapability]:
    by_topic: Dict[str, List[Attempt]] = {}
    for a in attempts:
        key = f"{a.subject_id}:{a.topic_id}"
        by_topic.setdefault(key, []).append(a)

    result = []
    for key, topic_attempts in by_topic.items():
        subject_id, topic_id = key.split(":", 1)
        caps = _compute_capability(topic_attempts)
        result.append(TopicCapability(subject_id=subject_id, topic_id=topic_id, **caps))
    return sorted(result, key=lambda x: x.priority_score, reverse=True)


def rank_topics_for_practice(attempts: List[Attempt]) -> List[TopicCapability]:
    """Return topics sorted by highest priority (most needing practice)."""
    return compute_topic_capabilities(attempts)


def rank_subjects_for_practice(attempts: List[Attempt]) -> List[SubjectCapability]:
    return compute_subject_capabilities(attempts)
