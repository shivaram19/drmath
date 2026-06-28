"""Concrete survey-storage adapters for the web layer."""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from pipeline.config import DATA_DIR
from web.ports import SurveyStore


class JSONLSurveyStore(SurveyStore):
    """Append discovery-survey responses to a local JSONL file.

    Responses are written to `data/nursing_discovery_survey.jsonl` and retained
    for the duration of the Phase 10.9 research cycle. The path is configurable
    so tests can redirect output to a temp file.
    """

    def __init__(self, path: Optional[Path] = None):
        self.path = path or (DATA_DIR / "nursing_discovery_survey.jsonl")

    def save_response(self, response: Dict[str, Any]) -> None:
        record = {
            "received_at": datetime.utcnow().isoformat(),
            "response": response,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


class NoOpSurveyStore(SurveyStore):
    """Drop survey responses. Useful for tests and opt-out paths."""

    def save_response(self, response: Dict[str, Any]) -> None:
        return None
