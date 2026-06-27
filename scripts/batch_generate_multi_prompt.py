#!/usr/bin/env python3
"""Multi-prompt batch content generation — create multiple pedagogical versions of each topic.

Usage:
    # Generate all topics with 4 prompt dimensions
    python3 scripts/batch_generate_multi_prompt.py --all-topics

    # Generate specific topics
    python3 scripts/batch_generate_multi_prompt.py --topics "Integers,Fractions"

    # Custom prompt selection
    python3 scripts/batch_generate_multi_prompt.py --all-topics --prompts "default,storyteller,visual"

Each topic × prompt combination produces a unique output file:
    output/{slug}_{prompt_slug}_output.json

All generations are tracked in the SQLite database for PM comparison.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.config import OUTPUT_DIR
from pipeline.run import run_pipeline
from db.database import SessionLocal
from db import crud


DEFAULT_TOPICS = [
    "Integers",
    "Fractions",
    "Percentage",
    "Rational Numbers",
    "Exponents",
    "Triangles",
    "Simple Equations",
    "Lines and Angles",
    "Data Handling",
    "Perimeter and Area",
]

# Map of prompt aliases to database IDs
PROMPT_DIMENSIONS = {
    "default": {
        "id": "1624be66",
        "name": "Default (Anti-Gravity)",
        "slug": "default",
        "desc": "Standard adaptive content with clear explanations",
    },
    "storyteller": {
        "id": "cultural_storyteller",
        "name": "Cultural Storyteller",
        "slug": "storyteller",
        "desc": "Math woven into Indian stories — cricket, bazaar, festivals",
    },
    "visual": {
        "id": "visual_first",
        "name": "Visual-First Thinker",
        "slug": "visual",
        "desc": "Diagrams, visual intuition, CPA learning method",
    },
    "zpd": {
        "id": "zpd_adaptive",
        "name": "ZPD Adaptive Tutor",
        "slug": "zpd",
        "desc": "Just-right challenge, scaffolding, zone of proximal development",
    },
}


def _slugify(name: str) -> str:
    return name.lower().replace(" ", "_")


def batch_generate_multi_prompt(
    topics: List[str],
    prompt_keys: List[str],
    skip_existing: bool = True,
) -> dict:
    """Run pipeline for each topic × prompt combination."""
    
    # Validate prompts exist in DB
    db = SessionLocal()
    valid_prompts = {}
    for key in prompt_keys:
        cfg = PROMPT_DIMENSIONS.get(key)
        if not cfg:
            print(f"⚠️  Unknown prompt key: {key}. Skipping.")
            continue
        p = crud.get_prompt(db, cfg["id"])
        if p:
            valid_prompts[key] = cfg
        else:
            print(f"⚠️  Prompt not found in DB: {cfg['name']} ({cfg['id']}). Skipping.")
    db.close()

    if not valid_prompts:
        print("❌ No valid prompts found. Aborting.")
        return {"error": "No valid prompts"}

    total_jobs = len(topics) * len(valid_prompts)
    print(f"\n{'='*60}")
    print(f"🚀 Dr. Math Multi-Prompt Batch Generation")
    print(f"   Topics: {len(topics)}")
    print(f"   Prompts: {len(valid_prompts)}")
    print(f"   Total jobs: {total_jobs}")
    print(f"   Skip existing: {skip_existing}")
    for key, cfg in valid_prompts.items():
        print(f"   • {cfg['name']}: {cfg['desc']}")
    print(f"{'='*60}\n")

    results = {
        "started_at": datetime.utcnow().isoformat(),
        "topics": topics,
        "prompts": {k: v["name"] for k, v in valid_prompts.items()},
        "total_jobs": total_jobs,
        "success": [],
        "failed": [],
        "skipped": [],
    }

    job_num = 0
    for topic in topics:
        slug = _slugify(topic)
        for key, cfg in valid_prompts.items():
            job_num += 1
            output_filename = f"{slug}_{cfg['slug']}_output.json"
            output_path = OUTPUT_DIR / output_filename

            print(f"\n[{job_num}/{total_jobs}] 📚 {topic} + 🎨 {cfg['name']}")
            print("-" * 50)

            if skip_existing and output_path.exists():
                print(f"   ⏭️  Skipping — output exists: {output_filename}")
                results["skipped"].append({"topic": topic, "prompt": cfg["name"]})
                continue

            try:
                run_pipeline(topic, str(output_path), prompt_id=cfg["id"])
                print(f"   ✅ Success → {output_filename}")
                results["success"].append({"topic": topic, "prompt": cfg["name"]})
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                results["failed"].append({"topic": topic, "prompt": cfg["name"], "error": str(e)})

    results["completed_at"] = datetime.utcnow().isoformat()
    results["success_count"] = len(results["success"])
    results["failed_count"] = len(results["failed"])
    results["skipped_count"] = len(results["skipped"])

    report_path = OUTPUT_DIR / f"multi_prompt_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"📊 Multi-Prompt Batch Complete")
    print(f"   ✅ Success: {results['success_count']}")
    print(f"   ❌ Failed:  {results['failed_count']}")
    print(f"   ⏭️  Skipped: {results['skipped_count']}")
    print(f"   📁 Report:  {report_path}")
    print(f"{'='*60}\n")

    return results


def main():
    parser = argparse.ArgumentParser(description="Dr. Math Multi-Prompt Content Generator")
    parser.add_argument("--topics", default=None, help="Comma-separated topic names")
    parser.add_argument("--all-topics", action="store_true", help="Use the default Class VII curriculum list")
    parser.add_argument(
        "--prompts",
        default="default,storyteller,visual,zpd",
        help="Comma-separated prompt keys (default,storyteller,visual,zpd)",
    )
    parser.add_argument("--no-skip", action="store_true", help="Re-generate even if output exists")
    args = parser.parse_args()

    if args.topics:
        topics = [t.strip() for t in args.topics.split(",") if t.strip()]
    elif args.all_topics:
        topics = DEFAULT_TOPICS
    else:
        print("❌ No topics specified. Use --topics or --all-topics")
        sys.exit(1)

    prompt_keys = [k.strip() for k in args.prompts.split(",") if k.strip()]
    batch_generate_multi_prompt(topics, prompt_keys, skip_existing=not args.no_skip)


if __name__ == "__main__":
    main()
