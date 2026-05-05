#!/usr/bin/env python3
"""
MathWise Mobilerun E2E Test Runner

Orchestrates all end-to-end test suites for the MathWise Flutter app.
Requires: Android device connected with Portal APK installed, LLM API key set.

Usage:
    export GOOGLE_API_KEY=your-key
    source ../mobilerun-venv/bin/activate
    python runner.py

Or run individual suites:
    python tests/test_home_flow.py
    python tests/test_curriculum_flow.py
    python tests/test_practice_flow.py
    python tests/test_profile_flow.py
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

from tests.test_home_flow import run_all_home_tests
from tests.test_curriculum_flow import run_all_curriculum_tests
from tests.test_practice_flow import run_all_practice_tests
from tests.test_profile_flow import run_all_profile_tests


async def run_all_suites():
    """Run all test suites and generate a combined report."""
    start_time = datetime.now()

    all_results = {
        "timestamp": start_time.isoformat(),
        "suites": {},
        "summary": {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "total_steps": 0,
        },
    }

    suites = [
        ("home", run_all_home_tests),
        ("curriculum", run_all_curriculum_tests),
        ("practice", run_all_practice_tests),
        ("profile", run_all_profile_tests),
    ]

    for suite_name, suite_fn in suites:
        print(f"\n{'#' * 70}")
        print(f"# SUITE: {suite_name.upper()}")
        print(f"{'#' * 70}")

        try:
            results = await suite_fn()
            all_results["suites"][suite_name] = [
                {
                    "test": name,
                    "passed": success,
                    "reason": reason,
                    "steps": steps,
                }
                for name, success, reason, steps in results
            ]

            for name, success, reason, steps in results:
                all_results["summary"]["total_tests"] += 1
                all_results["summary"]["total_steps"] += steps
                if success:
                    all_results["summary"]["passed"] += 1
                else:
                    all_results["summary"]["failed"] += 1
        except Exception as e:
            print(f"\n💥 SUITE ERROR: {e}")
            all_results["suites"][suite_name] = [{"error": str(e)}]
            all_results["summary"]["errors"] += 1

    # Calculate duration
    duration = (datetime.now() - start_time).total_seconds()
    all_results["summary"]["duration_seconds"] = round(duration, 2)

    # Print summary
    print("\n" + "=" * 70)
    print("FINAL REPORT")
    print("=" * 70)

    total = all_results["summary"]["total_tests"]
    passed = all_results["summary"]["passed"]
    failed = all_results["summary"]["failed"]
    errors = all_results["summary"]["errors"]
    steps = all_results["summary"]["total_steps"]

    pass_rate = (passed / total * 100) if total > 0 else 0

    print(f"\nTotal Tests:    {total}")
    print(f"Passed:         {passed} ({pass_rate:.1f}%)")
    print(f"Failed:         {failed}")
    print(f"Suite Errors:   {errors}")
    print(f"Total Steps:    {steps}")
    print(f"Duration:       {duration:.1f}s")

    # Save report
    report_path = Path("report.json")
    report_path.write_text(json.dumps(all_results, indent=2))
    print(f"\n📄 Full report saved to: {report_path.absolute()}")

    # Exit with error code if any failures
    if failed > 0 or errors > 0:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)
    else:
        print("\n✅ ALL TESTS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    # Verify config exists
    if not Path("config/config.yaml").exists():
        print("ERROR: config/config.yaml not found. Run from mobilerun-tests/ directory.")
        sys.exit(1)

    # Check for API key
    import os
    if not any(os.getenv(k) for k in ["GOOGLE_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]):
        print("WARNING: No LLM API key found. Set GOOGLE_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY.")
        print("Mobilerun will fail without an LLM provider.")

    asyncio.run(run_all_suites())
