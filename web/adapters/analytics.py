"""Concrete analytics adapters for the web layer."""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from pipeline.config import DATA_DIR
from web.ports import AnalyticsSink


class JSONLAnalyticsSink(AnalyticsSink):
    """Append anonymous events to a local JSONL file.

    This preserves the original nursing analytics behavior: events are written
    to `data/nursing_events.jsonl` and retained per the DPDPA privacy notice.
    The file path is configurable so tests can redirect output to a temp file.
    """

    def __init__(self, path: Optional[Path] = None):
        self.path = path or (DATA_DIR / "nursing_events.jsonl")

    def record_event(
        self,
        event: str,
        client_timestamp: str,
        consent_version: str,
        metadata: Dict[str, Any],
    ) -> None:
        record = {
            "received_at": datetime.utcnow().isoformat(),
            "event": event,
            "client_timestamp": client_timestamp,
            "consent_version": consent_version,
            "metadata": metadata,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


class NoOpAnalyticsSink(AnalyticsSink):
    """Drop analytics events. Useful for tests and opt-out paths."""

    def record_event(
        self,
        event: str,
        client_timestamp: str,
        consent_version: str,
        metadata: Dict[str, Any],
    ) -> None:
        return None
