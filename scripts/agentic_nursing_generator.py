#!/usr/bin/env python3
"""Agentic nursing question generator.

Fetches public-source content for a nursing topic, prompts an LLM to generate
multi-dimensionally labeled MCQs (cognitive level, context, difficulty), validates
them against the Question schema, and appends them to the nursing seed bank.

Example:
    python3 scripts/agentic_nursing_generator.py \
        --subject-id anatomy_physiology \
        --topic-id ap_cardiovascular \
        --source-url "https://en.wikipedia.org/wiki/Circulatory_system" \
        --count 10
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.llm_client import LLMClient
from pipeline.config import OUTPUT_DIR
from web.domain.models import Question


BANK_PATH = OUTPUT_DIR / "nursing_staff_nurse_output.json"
MAX_SOURCE_CHARS = 6000


SYSTEM_PROMPT = """You are an expert nursing educator and exam item writer.
Your task is to generate multiple-choice questions (MCQs) for Indian GNM-level
nursing students based on the provided source text.

For every question you must output a JSON object with these exact fields:
- id: integer (will be overwritten by the script, but include it)
- subject_id: string
- topic_id: string
- concept_tag: short snake_case tag for the specific concept
- difficulty: integer 1 (easy), 2 (medium), or 3 (hard)
- cognitive_level: one of remember, understand, apply, analyze
- context: one of theory, calculation, scenario
- format: always "mcq"
- question: the question text, 1-2 sentences
- options: array of exactly 4 strings, each starting with "A) ", "B) ", etc.
- correct_answer: single uppercase letter A-D
- explanation: 1-3 sentence explanation of the correct answer
- source: human-readable source name
- source_url: URL of the source (copy from input)
- source_section: concept_tag or topic subsection
- verified_at: today's date as YYYY-MM-DD
- verification_status: "reviewed"
- verified_by: "agentic-generator"
- last_reviewed: today's date as YYYY-MM-DD

Rules:
1. Questions must be factually grounded in the source text.
2. Each option must be plausible; only one is correct.
3. Vary difficulty, cognitive_level, and context across the batch.
4. Do not duplicate the example questions.
5. Return ONLY a JSON array of objects. No markdown, no commentary.
"""


def fetch_source_text(url: str) -> str:
    headers = {"User-Agent": "DrMathAgent/1.0 (educational content generation)"}
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    text = response.text
    # Very crude HTML-to-text: strip tags and collapse whitespace.
    text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.S)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:MAX_SOURCE_CHARS]


def load_bank(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {
            "topic": "Telangana Staff Nurse",
            "exam_pattern": "GNM",
            "meta": {
                "total_questions": 0,
                "language": "en",
                "source": "Agentic generator + INC GNM syllabus",
                "verification_status": "reviewed",
                "verified_by": "agentic-generator",
                "last_reviewed": str(date.today()),
                "generated_at": str(date.today()),
                "dimensions": {},
            },
            "questions": [],
        }
    return json.loads(path.read_text(encoding="utf-8"))


def save_bank(path: Path, bank: Dict[str, Any]) -> None:
    bank["meta"]["total_questions"] = len(bank["questions"])
    bank["meta"]["last_reviewed"] = str(date.today())
    bank["meta"]["generated_at"] = str(date.today())
    path.write_text(json.dumps(bank, indent=2, ensure_ascii=False), encoding="utf-8")


def parse_json_response(content: str) -> List[Dict[str, Any]]:
    # Some models wrap JSON in markdown fences.
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
    return json.loads(content)


def validate_question(raw: Dict[str, Any]) -> Optional[Question]:
    try:
        return Question.model_validate(raw)
    except Exception as exc:
        print(f"  validation failed: {exc}")
        return None


def generate_questions(
    client: LLMClient,
    subject_id: str,
    topic_id: str,
    source_url: str,
    source_text: str,
    existing_examples: List[Dict[str, Any]],
    count: int,
) -> List[Dict[str, Any]]:
    user_prompt = f"""Subject: {subject_id}
Topic: {topic_id}
Source URL: {source_url}

Source text:
{source_text}

Example questions already in the bank for this topic (do NOT duplicate):
{json.dumps(existing_examples[:3], indent=2)}

Generate {count} new, distinct MCQs for topic '{topic_id}'.
Return ONLY a JSON array.
"""
    content = client.generate(SYSTEM_PROMPT, user_prompt, temperature=0.8, max_tokens=4000)
    return parse_json_response(content)


def run(args: argparse.Namespace) -> int:
    if not args.source_url:
        print("--source-url is required")
        return 1

    print(f"Fetching source: {args.source_url}")
    try:
        source_text = fetch_source_text(args.source_url)
    except Exception as exc:
        print(f"Failed to fetch source: {exc}")
        return 1

    bank = load_bank(BANK_PATH)
    existing = [q for q in bank["questions"] if q.get("topic_id") == args.topic_id]
    existing_ids = {q["id"] for q in bank["questions"]}
    next_id = max(existing_ids, default=0) + 1

    client = LLMClient()
    print(f"Generating {args.count} questions for {args.topic_id}...")
    raw_questions = generate_questions(
        client,
        args.subject_id,
        args.topic_id,
        args.source_url,
        source_text,
        existing,
        args.count,
    )

    accepted = 0
    rejected = 0
    for raw in raw_questions:
        # Force required metadata fields regardless of model output.
        raw["id"] = next_id
        raw["subject_id"] = args.subject_id
        raw["topic_id"] = args.topic_id
        raw["format"] = "mcq"
        raw["source"] = raw.get("source") or "Public internet source"
        raw["source_url"] = args.source_url
        raw["verified_at"] = raw.get("verified_at") or str(date.today())
        raw["verification_status"] = raw.get("verification_status") or "reviewed"
        raw["verified_by"] = raw.get("verified_by") or "agentic-generator"
        raw["last_reviewed"] = raw.get("last_reviewed") or str(date.today())

        q = validate_question(raw)
        if q is None:
            rejected += 1
            continue
        bank["questions"].append(q.model_dump())
        next_id += 1
        accepted += 1

    save_bank(BANK_PATH, bank)
    print(f"Accepted: {accepted}, rejected: {rejected}, total bank: {len(bank['questions'])}")
    return 0 if accepted > 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Agentic nursing question generator")
    parser.add_argument("--subject-id", required=True)
    parser.add_argument("--topic-id", required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--count", type=int, default=10)
    return run(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
