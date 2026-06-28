"""Hexagonal ports for the web layer.

These abstract volatile boundaries so that routers depend on capabilities, not
concrete implementations. Concrete adapters live in `web/adapters/`.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class AnalyticsSink(ABC):
    """Persist anonymous, consent-gated analytics events.

    Implementations may write to JSONL, a queue, an external telemetry service,
    or drop events entirely (e.g. in tests).
    """

    @abstractmethod
    def record_event(
        self,
        event: str,
        client_timestamp: str,
        consent_version: str,
        metadata: Dict[str, Any],
    ) -> None:
        """Record a single analytics event."""
        ...


class SurveyStore(ABC):
    """Persist voluntary, non-PII discovery-survey responses.

    Responses are written to durable storage for analysis and then erased once
    the research purpose is complete. No raw phone numbers, chat_ids, or other
    personal identifiers are stored.
    """

    @abstractmethod
    def save_response(self, response: Dict[str, Any]) -> None:
        """Save a single survey response."""
        ...
