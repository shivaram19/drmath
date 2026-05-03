"""Generate structured MCQs via LLM with custom prompts."""
import json
import re
from typing import List, Dict, Any, Optional

DEFAULT_QUESTION_SYSTEM = """You are a CBSE Class-VII math teacher."""

JSON_SCHEMA_ENFORCEMENT = """

STRICT OUTPUT REQUIREMENTS:
You MUST return a valid JSON array with EXACTLY this structure for each question:

[
  {
    "id": 1,
    "difficulty": 1,
    "question": "Question text here?",
    "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
    "correct_answer": "B",
    "explanation": "Step-by-step explanation here"
  }
]

RULES:
1. EXACTLY 40 questions total
2. difficulty 1: 10 questions, difficulty 2: 10 questions, difficulty 3: 10 questions, difficulty 4: 10 questions
3. Options MUST be labeled A), B), C), D)
4. correct_answer MUST be exactly one of: A, B, C, D
5. Every question MUST have an id (1-40), difficulty (1-4), question, options, correct_answer, and explanation
6. Return ONLY the JSON array. No markdown fences. No text before or after.
"""


def _normalize_question(q: dict, idx: int) -> dict:
    """Fix common LLM output variations to match our schema."""
    normalized = {}
    normalized["id"] = q.get("id", idx + 1)
    normalized["difficulty"] = q.get("difficulty", (idx // 10) + 1 if idx < 40 else 4)
    normalized["question"] = q.get("question", q.get("q", ""))

    # Handle options
    opts = q.get("options", q.get("choices", []))
    if len(opts) == 4 and not any(str(opt).startswith("A)") for opt in opts):
        opts = [f"A) {opts[0]}", f"B) {opts[1]}", f"C) {opts[2]}", f"D) {opts[3]}"]
    normalized["options"] = opts

    # Handle correct answer
    ans = q.get("correct_answer", q.get("answer", q.get("correct", "")))
    if ans and ans not in "ABCD":
        # Try to find which option matches
        for i, opt in enumerate(opts):
            if str(ans).lower() in str(opt).lower():
                ans = "ABCD"[i]
                break
    if not ans:
        ans = "A"
    normalized["correct_answer"] = ans

    normalized["explanation"] = q.get("explanation", q.get("reason", "Think through the steps carefully."))
    return normalized


def parse_json_array(text: str) -> List[Dict[str, Any]]:
    """Robustly extract and normalize JSON array from LLM response."""
    text = text.strip()
    # Remove markdown fences
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    # Find array bounds
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("No JSON array found in response")

    data = json.loads(text[start:end + 1])
    # Normalize each question
    normalized = [_normalize_question(q, i) for i, q in enumerate(data)]
    return normalized


def build_question_prompt(topic: str, adapted_content: str, custom_prompt: Optional[str] = None) -> tuple:
    """Returns (system_prompt, user_prompt)."""
    system = DEFAULT_QUESTION_SYSTEM
    if custom_prompt:
        user = custom_prompt.format(topic=topic, adapted_content=adapted_content[:3000])
        user += JSON_SCHEMA_ENFORCEMENT
    else:
        user = f"""Create exactly 40 multiple-choice questions on the topic: {topic}

Use this content as reference:
{adapted_content[:3000]}

{JSON_SCHEMA_ENFORCEMENT}
"""
    return system, user
