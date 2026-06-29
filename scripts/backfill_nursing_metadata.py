#!/usr/bin/env python3
"""Backfill source metadata fields into the nursing question bank.

Adds source_url, source_section, and verified_at to each question where missing.
Existing values are preserved. Questions without a source_url are flagged for
future re-generation / manual curation.
"""
import json
from pathlib import Path

BANK_PATH = Path(__file__).resolve().parent.parent / "output" / "nursing_staff_nurse_output.json"


def backfill() -> dict:
    raw = json.loads(BANK_PATH.read_text(encoding="utf-8"))
    questions = raw.get("questions", [])
    updated = 0
    for q in questions:
        if "source_url" not in q:
            q["source_url"] = None
        if "source_section" not in q:
            q["source_section"] = q.get("concept_tag") or q.get("topic_id")
        if "verified_at" not in q:
            q["verified_at"] = q.get("last_reviewed")
        if q["source_url"] is None or q["verified_at"] is None:
            updated += 1
    return raw, len(questions), updated


def main() -> int:
    if not BANK_PATH.exists():
        print(f"Bank not found: {BANK_PATH}")
        return 1
    data, total, updated = backfill()
    BANK_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Backfilled {updated}/{total} questions in {BANK_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
