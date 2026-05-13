#!/usr/bin/env python3
"""Batch content generation — automate the Dr. Math pipeline for multiple topics.

Usage:
    python3 scripts/batch_generate.py --topics "Integers,Fractions,Percentage" --prompt-id abc123
    python3 scripts/batch_generate.py --all-topics
    python3 scripts/batch_generate.py --topics-file topics.txt

The script runs the pipeline sequentially for each topic and produces
a summary report of successes and failures.
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


def batch_generate(
    topics: List[str],
    prompt_id: Optional[str] = None,
    skip_existing: bool = True,
) -> dict:
    """Run pipeline for multiple topics. Returns summary report."""
    print(f"\n{'='*60}")
    print(f"🚀 Dr. Math Batch Generation")
    print(f"   Topics: {len(topics)}")
    print(f"   Prompt: {prompt_id or 'Default'}")
    print(f"   Skip existing: {skip_existing}")
    print(f"{'='*60}\n")

    results = {
        "started_at": datetime.utcnow().isoformat(),
        "topics": topics,
        "prompt_id": prompt_id,
        "success": [],
        "failed": [],
        "skipped": [],
    }

    for i, topic in enumerate(topics, 1):
        slug = topic.lower().replace(" ", "_")
        output_path = OUTPUT_DIR / f"{slug}_output.json"

        print(f"\n[{i}/{len(topics)}] 📚 {topic}")
        print("-" * 40)

        if skip_existing and output_path.exists():
            print(f"   ⏭️  Skipping — output already exists: {output_path}")
            results["skipped"].append(topic)
            continue

        try:
            run_pipeline(topic, str(output_path), prompt_id=prompt_id)
            print(f"   ✅ Success")
            results["success"].append(topic)
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results["failed"].append({"topic": topic, "error": str(e)})

    results["completed_at"] = datetime.utcnow().isoformat()
    results["total"] = len(topics)
    results["success_count"] = len(results["success"])
    results["failed_count"] = len(results["failed"])
    results["skipped_count"] = len(results["skipped"])

    # Save report
    report_path = OUTPUT_DIR / f"batch_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n{'='*60}")
    print(f"📊 Batch Complete")
    print(f"   ✅ Success: {results['success_count']}")
    print(f"   ❌ Failed:  {results['failed_count']}")
    print(f"   ⏭️  Skipped: {results['skipped_count']}")
    print(f"   📁 Report:  {report_path}")
    print(f"{'='*60}\n")

    return results


def main():
    parser = argparse.ArgumentParser(description="Dr. Math Batch Content Generator")
    parser.add_argument("--topics", default=None, help="Comma-separated topic names")
    parser.add_argument("--topics-file", default=None, help="File with one topic per line")
    parser.add_argument("--all-topics", action="store_true", help="Use the default Class VII curriculum list")
    parser.add_argument("--prompt-id", default=None, help="Custom prompt ID to use")
    parser.add_argument("--no-skip", action="store_true", help="Re-generate even if output exists")
    args = parser.parse_args()

    if args.topics:
        topics = [t.strip() for t in args.topics.split(",") if t.strip()]
    elif args.topics_file:
        path = Path(args.topics_file)
        if not path.exists():
            print(f"❌ Topics file not found: {path}")
            sys.exit(1)
        topics = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    elif args.all_topics:
        topics = DEFAULT_TOPICS
    else:
        print("❌ No topics specified. Use --topics, --topics-file, or --all-topics")
        sys.exit(1)

    batch_generate(topics, prompt_id=args.prompt_id, skip_existing=not args.no_skip)


if __name__ == "__main__":
    main()
