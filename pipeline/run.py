"""Main pipeline runner with custom prompt support."""
import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from pipeline.config import OUTPUT_DIR, DATA_DIR
from pipeline.scraper import fetch_ixl_topics, search_mathisfun_topic
from pipeline.content_adapter import build_adapter_prompt
from pipeline.question_generator import build_question_prompt, parse_json_array
from pipeline.llm_client import LLMClient
from pipeline.db import get_prompt, log_generation


def run_pipeline(topic: str, output_path: str, prompt_id: Optional[str] = None):
    print(f"\n🚀 Dr. Math Pipeline — Topic: {topic}\n")

    custom = get_prompt(prompt_id) if prompt_id else None
    prompt_name = custom["name"] if custom else "Default (Anti-Gravity)"
    print(f"🎨 Using prompt style: {prompt_name}\n")

    # Step 1: Scrape IXL topics
    print("[1/5] Fetching IXL topic list via Obscura...")
    ixl_topics = fetch_ixl_topics()
    matched = [t for t, _ in ixl_topics if topic.lower() in t.lower()]
    if matched:
        print(f"  ✅ Found {len(matched)} matching skills on IXL")
    else:
        print(f"  ⚠️  Topic not found in IXL. Proceeding anyway.")

    # Step 2: Fetch MathIsFun content
    print("[2/5] Fetching MathIsFun content via Obscura...")
    raw_html = search_mathisfun_topic(topic)
    print(f"  ✅ Fetched {len(raw_html)} chars of raw HTML")

    raw_path = DATA_DIR / f"{topic.lower().replace(' ', '_')}_raw.html"
    raw_path.write_text(raw_html, encoding="utf-8")
    print(f"  💾 Saved raw HTML to {raw_path}")

    # Step 3: Adapt content
    print("[3/5] Adapting content via LLM...")
    llm = LLMClient()
    sys_prompt, user_prompt = build_adapter_prompt(
        topic, raw_html,
        custom_system=custom.get("system_prompt") if custom else None,
        custom_user=custom.get("system_prompt") if custom else None  # Use system prompt as user template too if no separate user prompt
    )
    # If custom prompt has both system and question, use system for adapter too
    if custom and custom.get("system_prompt"):
        sys_prompt = custom["system_prompt"]
        user_prompt = f"TOPIC: {topic}\nRAW CONTENT:\n{strip_html(raw_html)[:4000]}\n\nAdapt this into a lesson."
    adapted_content = llm.generate(sys_prompt, user_prompt, temperature=0.8, max_tokens=4000)
    print(f"  ✅ Generated {len(adapted_content)} chars of adapted content")

    adapted_path = DATA_DIR / f"{topic.lower().replace(' ', '_')}_antigravity.md"
    adapted_path.write_text(adapted_content, encoding="utf-8")
    print(f"  💾 Saved adapted content to {adapted_path}")

    # Step 4: Generate 40 questions
    print("[4/5] Generating 40 structured questions via LLM...")
    q_sys, q_user = build_question_prompt(
        topic, adapted_content,
        custom_prompt=custom.get("question_prompt") if custom else None
    )
    raw_questions = llm.generate(q_sys, q_user, temperature=0.7, max_tokens=12000)
    questions = parse_json_array(raw_questions)
    print(f"  ✅ Parsed {len(questions)} questions")

    diff_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    for q in questions:
        d = q.get("difficulty", 0)
        if d in diff_counts:
            diff_counts[d] += 1
    print(f"  📊 Difficulty distribution: {diff_counts}")

    # Step 5: Assemble output
    print("[5/5] Saving output...")
    output = {
        "topic": topic,
        "prompt_id": prompt_id,
        "prompt_name": prompt_name,
        "source_ixl_skills": matched[:10],
        "antigravity_content": adapted_content,
        "questions": questions,
        "meta": {
            "total_questions": len(questions),
            "difficulty_distribution": diff_counts,
        },
    }

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")

    log_generation(
        topic=topic,
        prompt_id=prompt_id,
        output_path=str(out_path),
        status="success",
        meta={"total_questions": len(questions), "difficulty": diff_counts}
    )

    print(f"\n🎉 Done! Output saved to {out_path}\n")
    return output


def strip_html(raw_html: str) -> str:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(raw_html, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines[:2000])


def main():
    parser = argparse.ArgumentParser(description="Dr. Math Content Automation Pipeline")
    parser.add_argument("--topic", default="Integers", help="Math topic to process")
    parser.add_argument("--output", default=None, help="Output JSON file path")
    parser.add_argument("--prompt-id", default=None, help="Custom prompt ID to use")
    args = parser.parse_args()

    topic = args.topic
    output = args.output or str(OUTPUT_DIR / f"{topic.lower().replace(' ', '_')}_output.json")

    try:
        run_pipeline(topic, output, prompt_id=args.prompt_id)
    except Exception as e:
        log_generation(topic=args.topic, prompt_id=args.prompt_id, output_path=output, status="error", meta={"error": str(e)})
        print(f"\n❌ Pipeline failed: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
