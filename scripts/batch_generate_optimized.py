#!/usr/bin/env python3
"""Optimized multi-prompt batch generation with concurrency and full observability.

ENGINEERING PRINCIPLES:
1. Conscious parallelism: 3 workers max (respects API rate limits)
2. Idempotency: Skip already-generated files, resume on restart
3. Observability: Live status file updated after every job
4. Error resilience: Per-job error isolation, no cascade failures
5. PM clarity: Progress %, ETA, and per-dimension breakdown

Usage:
    python3 scripts/batch_generate_optimized.py --all-topics --workers 3
    python3 scripts/batch_generate_optimized.py --topics "Integers,Fractions" --prompts "storyteller,visual"
"""

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.config import OUTPUT_DIR
from pipeline.run import run_pipeline


# ── Configuration ───────────────────────────────────────────────────────────

DEFAULT_TOPICS = [
    "Integers", "Fractions", "Percentage", "Rational Numbers", "Exponents",
    "Triangles", "Simple Equations", "Lines and Angles", "Data Handling", "Perimeter and Area",
]

PROMPT_DIMENSIONS = {
    "default": {"id": "1624be66", "name": "Default (Anti-Gravity)", "slug": "default",
                "theory": "Scaffolded explanations", "icon": "🧮"},
    "storyteller": {"id": "cultural_storyteller", "name": "Cultural Storyteller", "slug": "storyteller",
                    "theory": "Indian context stories", "icon": "📖"},
    "visual": {"id": "visual_first", "name": "Visual-First Thinker", "slug": "visual",
               "theory": "CPA method (Concrete→Pictorial→Abstract)", "icon": "👁️"},
    "zpd": {"id": "zpd_adaptive", "name": "ZPD Adaptive Tutor", "slug": "zpd",
            "theory": "Vygotsky's Zone of Proximal Development", "icon": "🎯"},
}

STATUS_FILE = OUTPUT_DIR / "generation_status.json"


def _slugify(name: str) -> str:
    return name.lower().replace(" ", "_")


def load_status() -> Dict:
    if STATUS_FILE.exists():
        return json.loads(STATUS_FILE.read_text())
    return {"jobs": [], "started_at": None, "completed_at": None}


def save_status(status: Dict):
    STATUS_FILE.write_text(json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8")


def generate_one(job: Dict) -> Dict:
    """Run a single generation job. Isolated error handling."""
    topic = job["topic"]
    prompt_key = job["prompt_key"]
    cfg = PROMPT_DIMENSIONS[prompt_key]
    slug = _slugify(topic)
    output_filename = f"{slug}_{cfg['slug']}_output.json" if prompt_key != "default" else f"{slug}_output.json"
    output_path = OUTPUT_DIR / output_filename

    job["started_at"] = datetime.utcnow().isoformat()
    job["output_file"] = output_filename

    try:
        if output_path.exists():
            job["status"] = "skipped"
            job["message"] = f"Already exists: {output_filename}"
            job["completed_at"] = datetime.utcnow().isoformat()
            return job

        run_pipeline(topic, str(output_path), prompt_id=cfg["id"])
        job["status"] = "success"
        job["message"] = f"Generated {output_filename}"
    except Exception as e:
        job["status"] = "error"
        job["message"] = str(e)

    job["completed_at"] = datetime.utcnow().isoformat()
    return job


def build_job_list(topics: List[str], prompt_keys: List[str], skip_existing: bool = True) -> List[Dict]:
    """Build the complete job queue with pre-flight checks."""
    jobs = []
    for topic in topics:
        slug = _slugify(topic)
        for prompt_key in prompt_keys:
            cfg = PROMPT_DIMENSIONS[prompt_key]
            output_filename = f"{slug}_{cfg['slug']}_output.json" if prompt_key != "default" else f"{slug}_output.json"
            output_path = OUTPUT_DIR / output_filename

            # Pre-check if skipped
            pre_status = "pending"
            if skip_existing and output_path.exists():
                pre_status = "skipped"

            jobs.append({
                "topic": topic,
                "prompt_key": prompt_key,
                "prompt_name": cfg["name"],
                "prompt_icon": cfg["icon"],
                "theory": cfg["theory"],
                "output_file": output_filename,
                "status": pre_status,
                "message": "Queued" if pre_status == "pending" else f"Already exists: {output_filename}",
            })
    return jobs


def print_matrix(status: Dict):
    """Print a clean ASCII matrix of generation status."""
    jobs = status["jobs"]
    topics = sorted({j["topic"] for j in jobs})
    prompts = ["default", "storyteller", "visual", "zpd"]
    prompt_icons = {k: PROMPT_DIMENSIONS[k]["icon"] for k in prompts}

    # Header
    header = f"{'Topic':<22}"
    for pk in prompts:
        header += f" {prompt_icons[pk]:<3}"
    print(f"\n{'='*60}")
    print(header)
    print("-"*60)

    # Rows
    for topic in topics:
        row = f"{topic:<22}"
        for pk in prompts:
            job = next((j for j in jobs if j["topic"] == topic and j["prompt_key"] == pk), None)
            if not job:
                row += "  ? "
            elif job["status"] == "success":
                row += "  ✅ "
            elif job["status"] == "skipped":
                row += "  ⏭️  "
            elif job["status"] == "error":
                row += "  ❌ "
            elif job["status"] == "running":
                row += "  🔄 "
            else:
                row += "  ⏳ "
        print(row)
    print(f"{'='*60}\n")


def run_batch(topics: List[str], prompt_keys: List[str], workers: int = 3, skip_existing: bool = True):
    """Main orchestrator with ThreadPoolExecutor."""
    jobs = build_job_list(topics, prompt_keys, skip_existing)
    pending_jobs = [j for j in jobs if j["status"] == "pending"]
    skipped_jobs = [j for j in jobs if j["status"] == "skipped"]

    total = len(jobs)
    pending_count = len(pending_jobs)
    skipped_count = len(skipped_jobs)

    print(f"\n{'='*60}")
    print(f"🚀 Dr. Math Optimized Batch Generation")
    print(f"{'='*60}")
    print(f"   Topics:    {len(topics)}")
    print(f"   Prompts:   {len(prompt_keys)}")
    print(f"   Total:     {total}")
    print(f"   Pending:   {pending_count}")
    print(f"   Skipped:   {skipped_count}")
    print(f"   Workers:   {workers}")
    print(f"   Est. time: ~{pending_count * 90 // 60}m ({pending_count * 90}s @ 90s/gen)")
    print(f"{'='*60}\n")

    status = {
        "started_at": datetime.utcnow().isoformat(),
        "total_jobs": total,
        "pending_jobs": pending_count,
        "skipped_jobs": skipped_count,
        "workers": workers,
        "jobs": jobs,
    }
    save_status(status)

    if pending_count == 0:
        print("✅ Nothing to generate. All files exist.")
        print_matrix(status)
        return status

    # Run with ThreadPoolExecutor
    start_time = time.time()
    completed = 0
    success_count = 0
    error_count = 0

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_job = {executor.submit(generate_one, job): job for job in pending_jobs}

        for future in as_completed(future_to_job):
            job = future_to_job[future]
            try:
                result = future.result()
                # Update the job in status
                for j in status["jobs"]:
                    if j["topic"] == result["topic"] and j["prompt_key"] == result["prompt_key"]:
                        j.update(result)
                        break
            except Exception as e:
                job["status"] = "error"
                job["message"] = str(e)
                error_count += 1

            completed += 1
            if result.get("status") == "success":
                success_count += 1

            # Progress report every job
            elapsed = time.time() - start_time
            rate = elapsed / completed if completed > 0 else 0
            remaining = pending_count - completed
            eta_seconds = remaining * rate if rate > 0 else 0

            print(f"[{completed}/{pending_count}] {result.get('status','?').upper():<8} {result['topic']:<22} + {result['prompt_name']:<25} | ETA: {int(eta_seconds//60)}m {int(eta_seconds%60)}s")
            save_status(status)

    status["completed_at"] = datetime.utcnow().isoformat()
    status["elapsed_seconds"] = round(time.time() - start_time, 1)
    save_status(status)

    # Final summary
    print(f"\n{'='*60}")
    print(f"📊 Batch Complete in {status['elapsed_seconds']}s")
    print(f"   ✅ Success: {success_count}")
    print(f"   ❌ Failed:  {error_count}")
    print(f"   ⏭️  Skipped: {skipped_count}")
    print(f"{'='*60}\n")
    print_matrix(status)

    return status


def main():
    parser = argparse.ArgumentParser(description="Dr. Math Optimized Multi-Prompt Batch Generator")
    parser.add_argument("--topics", default=None, help="Comma-separated topic names")
    parser.add_argument("--all-topics", action="store_true", help="Use default Class VII curriculum")
    parser.add_argument("--prompts", default="default,storyteller,visual,zpd", help="Comma-separated prompt keys")
    parser.add_argument("--workers", type=int, default=3, help="Concurrent workers (max 5)")
    parser.add_argument("--no-skip", action="store_true", help="Re-generate existing files")
    parser.add_argument("--status", action="store_true", help="Print current status matrix and exit")
    args = parser.parse_args()

    if args.status:
        status = load_status()
        print_matrix(status)
        return

    if args.topics:
        topics = [t.strip() for t in args.topics.split(",") if t.strip()]
    elif args.all_topics:
        topics = DEFAULT_TOPICS
    else:
        print("❌ No topics specified. Use --topics or --all-topics")
        sys.exit(1)

    prompt_keys = [k.strip() for k in args.prompts.split(",") if k.strip()]
    workers = min(args.workers, 5)  # Cap at 5 for API courtesy

    run_batch(topics, prompt_keys, workers=workers, skip_existing=not args.no_skip)


if __name__ == "__main__":
    main()
