#!/usr/bin/env python3
"""Bulk agentic generation for the nursing question bank using government/INC sources.

Fetches the official INC GNM syllabus PDF once, extracts the text, and generates
multi-dimensionally labeled MCQs for every topic up to TARGET_PER_TOPIC.
"""
import argparse
import sys
import tempfile
from collections import Counter
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.agentic_nursing_generator import BANK_PATH, load_bank, save_bank

TARGET_PER_TOPIC = 12
INC_SYLLABUS_URL = "https://www.iminursing.in/gnm-syllabus.pdf"


def download_pdf_text(url: str) -> str:
    import io
    import pdfplumber

    print(f"Downloading source PDF: {url}")
    headers = {"User-Agent": "DrMathAgent/1.0 (educational content generation)"}
    response = requests.get(url, headers=headers, timeout=120)
    response.raise_for_status()
    text_parts = []
    with pdfplumber.open(io.BytesIO(response.content)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def topic_needs(bank: dict, target: int) -> dict:
    counts = Counter(q.get("topic_id") for q in bank.get("questions", []))
    topics = set()
    for q in bank.get("questions", []):
        topics.add((q.get("subject_id"), q.get("topic_id")))
    needs = {}
    for subject_id, topic_id in sorted(topics):
        need = max(0, target - counts.get(topic_id, 0))
        if need > 0:
            needs[(subject_id, topic_id)] = need
    return needs


def run_generator(subject_id: str, topic_id: str, source_url: str, text_file: Path, count: int) -> int:
    import subprocess

    cmd = [
        sys.executable,
        str(Path(__file__).resolve().parent / "agentic_nursing_generator.py"),
        "--subject-id", subject_id,
        "--topic-id", topic_id,
        "--source-url", source_url,
        "--source-text-file", str(text_file),
        "--count", str(count),
    ]
    result = subprocess.run(cmd)
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-per-topic", type=int, default=TARGET_PER_TOPIC)
    parser.add_argument("--source-url", default=INC_SYLLABUS_URL)
    args = parser.parse_args()

    source_text = download_pdf_text(args.source_url)
    if not source_text.strip():
        print("Failed to extract text from source PDF")
        return 1

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(source_text)
        text_file = Path(f.name)

    bank = load_bank(BANK_PATH)
    needs = topic_needs(bank, args.target_per_topic)
    total_needed = sum(needs.values())
    print(f"Topics needing questions: {len(needs)}; total needed: {total_needed}")

    failures = []
    for (subject_id, topic_id), need in needs.items():
        print(f"\n[{subject_id}/{topic_id}] generating {need} questions")
        rc = run_generator(subject_id, topic_id, args.source_url, text_file, need)
        if rc != 0:
            failures.append(topic_id)

    text_file.unlink(missing_ok=True)
    bank = load_bank(BANK_PATH)
    print(f"\nFinal bank size: {len(bank['questions'])}")
    if failures:
        print(f"Failures: {failures}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
