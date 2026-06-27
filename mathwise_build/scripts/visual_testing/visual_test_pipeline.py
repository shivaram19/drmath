#!/usr/bin/env python3
"""
Visual Test Pipeline — Main Orchestrator

Runs the complete dual-persona visual testing pipeline:
  1. flutter test --update-goldens test/visual_screenshots_test.dart
  2. Copy golden files to screenshots/<timestamp>/
  3. Screenshot Auditor (pixel-level token validation)
  4. UI/UX Engineer (qualitative rubric evaluation)
  5. Report Builder (aggregation + summary)

Usage:
    cd mathwise_build
    python3 scripts/visual_testing/visual_test_pipeline.py

    # Skip golden generation (use existing test/goldens/)
    python3 scripts/visual_testing/visual_test_pipeline.py --skip-goldens

Output:
    reports/YYYY-MM-DD_HH-MM-SS/summary.md
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Add scripts directory to path for imports
SCRIPTS_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPTS_DIR))

from screenshot_auditor import ScreenshotAuditor, TokenManifest, generate_audit_report
from ux_evaluator import UXEvaluator, generate_ux_report
from report_builder import ReportBuilder


# ── Configuration ────────────────────────────────────────────────────────────

PROJECT_DIR = SCRIPTS_DIR.parent.parent
GOLDENS_DIR = PROJECT_DIR / "test" / "goldens"
REPORTS_DIR = PROJECT_DIR / "reports"


# ── Golden Generation ────────────────────────────────────────────────────────

def generate_goldens() -> bool:
    """Run `flutter test --update-goldens` and return success status."""
    print("=" * 60)
    print("🔨 STEP 1: Generating golden file screenshots...")
    print("=" * 60)

    start = time.time()
    try:
        result = subprocess.run(
            ["flutter", "test", "--update-goldens", "test/visual_screenshots_test.dart"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            check=False,  # Allow failures (overflow generates files anyway)
        )
        elapsed = time.time() - start
        # Check if files were generated regardless of test pass/fail
        if GOLDENS_DIR.exists() and any(GOLDENS_DIR.iterdir()):
            print(f"✅ Goldens generated in {elapsed:.1f}s")
            return True
        print(f"❌ No golden files found after {elapsed:.1f}s")
        print(f"STDERR:\n{result.stderr}")
        return False
    except FileNotFoundError:
        print("❌ `flutter` command not found. Ensure Flutter SDK is in PATH.")
        return False


# ── Copy Goldens ─────────────────────────────────────────────────────────────

def copy_goldens_to_screenshots(screenshots_dir: Path) -> dict:
    """Copy widget test golden files to the screenshots directory."""
    print("\n" + "=" * 60)
    print("📸 STEP 2: Copying golden files to screenshots directory...")
    print("=" * 60)

    screenshots_dir.mkdir(parents=True, exist_ok=True)
    screen_count = 0
    file_count = 0

    for screen_dir in sorted(GOLDENS_DIR.iterdir()):
        if not screen_dir.is_dir():
            continue
        dest_dir = screenshots_dir / screen_dir.name
        dest_dir.mkdir(parents=True, exist_ok=True)
        for png_file in sorted(screen_dir.glob("*.png")):
            shutil.copy2(png_file, dest_dir / png_file.name)
            file_count += 1
        screen_count += 1

    # Write metadata
    metadata = {
        "capture_method": "widget_test_goldens",
        "source": "test/visual_screenshots_test.dart",
        "timestamp": datetime.now().isoformat(),
        "screens_copied": screen_count,
        "files_copied": file_count,
        "note": "Uses system fallback fonts. Layout, color, and spacing evaluation remains accurate.",
    }
    with open(screenshots_dir / "capture_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"✅ Copied {file_count} screenshots from {screen_count} screens")
    return metadata


# ── Audit Step ───────────────────────────────────────────────────────────────

def run_audit(screenshots_dir: Path, reports_dir: Path) -> None:
    """Run Screenshot Auditor on all screenshots."""
    print("\n" + "=" * 60)
    print("🔍 STEP 3: Running Screenshot Auditor...")
    print("=" * 60)

    tokens_path = SCRIPTS_DIR / "design_tokens.json"
    tokens = TokenManifest(tokens_path)
    auditor = ScreenshotAuditor(tokens)

    start = time.time()
    screen_names = [d.name for d in screenshots_dir.iterdir() if d.is_dir()]
    all_results = {}

    for screen_name in screen_names:
        screen_dir = screenshots_dir / screen_name
        screen_results = []
        for screenshot_file in sorted(screen_dir.glob("*.png")):
            viewport = screenshot_file.stem
            print(f"   → {screen_name} @ {viewport}")
            result = auditor.audit(screenshot_file, screen_name, viewport)
            screen_results.append(result)

        if screen_results:
            all_results[screen_name] = screen_results
            report_dir = reports_dir / screen_name
            report_dir.mkdir(parents=True, exist_ok=True)
            generate_audit_report(screen_results, report_dir)

    total_violations = sum(
        len(v.violations) for results in all_results.values() for v in results
    )
    elapsed = time.time() - start
    print(f"\n✅ Audit completed in {elapsed:.1f}s ({total_violations} violations)")


# ── UX Evaluation Step ───────────────────────────────────────────────────────

def run_ux_eval(screenshots_dir: Path, reports_dir: Path) -> None:
    """Run UI/UX Engineer evaluation on all screenshots."""
    print("\n" + "=" * 60)
    print("🎨 STEP 4: Running UI/UX Engineer...")
    print("=" * 60)

    evaluator = UXEvaluator()
    start = time.time()
    screen_names = [d.name for d in screenshots_dir.iterdir() if d.is_dir()]
    all_results = {}

    for screen_name in screen_names:
        screen_dir = screenshots_dir / screen_name
        screen_results = []
        for screenshot_file in sorted(screen_dir.glob("*.png")):
            viewport = screenshot_file.stem
            print(f"   → {screen_name} @ {viewport}")
            result = evaluator.evaluate(screenshot_file, screen_name, viewport)
            screen_results.append(result)

        if screen_results:
            all_results[screen_name] = screen_results
            report_dir = reports_dir / screen_name
            report_dir.mkdir(parents=True, exist_ok=True)
            generate_ux_report(screen_results, report_dir)

    total_issues = sum(
        1 for results in all_results.values() for v in results
        for f in v.findings if f.verdict != "pass"
    )
    elapsed = time.time() - start
    print(f"\n✅ UX evaluation completed in {elapsed:.1f}s ({total_issues} issues)")


# ── Report Step ──────────────────────────────────────────────────────────────

def run_report_builder(reports_dir: Path) -> Path:
    """Aggregate all reports into summary."""
    print("\n" + "=" * 60)
    print("📊 STEP 5: Building summary report...")
    print("=" * 60)

    builder = ReportBuilder(reports_dir)
    summary_path = builder.build()
    print(f"✅ Summary report: {summary_path}")
    return summary_path


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Dr. Math Visual Testing Pipeline")
    parser.add_argument("--skip-goldens", action="store_true", help="Skip flutter test --update-goldens")
    parser.add_argument("--screenshots", default=None, help="Use existing screenshots directory")
    parser.add_argument("--output", default=None, help="Custom output directory for reports")
    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    screenshots_dir = Path(args.screenshots) if args.screenshots else PROJECT_DIR / "screenshots" / timestamp
    reports_dir = Path(args.output) if args.output else REPORTS_DIR / timestamp

    overall_start = time.time()
    trace = {"timestamp": timestamp, "steps": {}}

    # Step 1: Generate goldens
    if not args.skip_goldens:
        build_ok = generate_goldens()
        trace["steps"]["goldens"] = {"success": build_ok}
        if not build_ok:
            print("\n❌ Pipeline aborted: golden generation failed")
            return 1
    else:
        print("⏭️  Skipping golden generation")
        if not GOLDENS_DIR.exists():
            print(f"❌ Goldens directory not found: {GOLDENS_DIR}")
            return 1
        trace["steps"]["goldens"] = {"skipped": True}

    # Step 2: Copy to screenshots
    copy_start = time.time()
    metadata = copy_goldens_to_screenshots(screenshots_dir)
    trace["steps"]["copy"] = {
        "elapsed": time.time() - copy_start,
        "screens": metadata.get("screens_copied", 0),
        "files": metadata.get("files_copied", 0),
    }

    # Step 3: Audit
    audit_start = time.time()
    run_audit(screenshots_dir, reports_dir)
    trace["steps"]["audit"] = {"elapsed": time.time() - audit_start}

    # Step 4: UX Evaluation
    ux_start = time.time()
    run_ux_eval(screenshots_dir, reports_dir)
    trace["steps"]["ux_eval"] = {"elapsed": time.time() - ux_start}

    # Step 5: Report Builder
    report_start = time.time()
    summary_path = run_report_builder(reports_dir)
    trace["steps"]["report"] = {"elapsed": time.time() - report_start}

    # Final trace
    total_elapsed = time.time() - overall_start
    trace["total_elapsed"] = total_elapsed
    trace["reports_dir"] = str(reports_dir)
    trace["summary_path"] = str(summary_path)

    with open(reports_dir / "pipeline_trace.json", "w") as f:
        json.dump(trace, f, indent=2)

    print("\n" + "=" * 60)
    print("🎉 PIPELINE COMPLETE")
    print("=" * 60)
    print(f"⏱️  Total time: {total_elapsed:.1f}s")
    print(f"📁 Reports: {reports_dir}")
    print(f"📄 Summary: {summary_path}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
