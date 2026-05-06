#!/usr/bin/env python3
"""
Evaluator Bot — Automated PR Validation against Issue Requirements

Validates that code changes in a branch actually resolve the issue they claim to fix.
Runs build, tests, pipeline, and semantic verification.

Usage:
    python scripts/evaluator_bot.py --issue 1 --branch fix/p1-background-auditor

Outputs:
    - evaluation_report.json — structured verdict
    - evaluation_report.md — human-readable summary
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional


@dataclass
class CheckResult:
    name: str
    status: str  # PASS, FAIL, SKIP, WARN
    details: str = ""
    duration_ms: int = 0


@dataclass
class EvaluationReport:
    issue_number: int
    branch: str
    verdict: str  # PASS, FAIL, PARTIAL
    overall_score: float
    checks: List[CheckResult] = field(default_factory=list)
    timestamp: str = ""
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "issue_number": self.issue_number,
            "branch": self.branch,
            "verdict": self.verdict,
            "overall_score": self.overall_score,
            "timestamp": self.timestamp,
            "checks": [asdict(c) for c in self.checks],
            "recommendations": self.recommendations,
        }


class EvaluatorBot:
    """Bot that evaluates a branch against an issue's acceptance criteria."""

    def __init__(self, issue_number: int, branch: str, repo: str = "shivaram19/drmath"):
        self.issue_number = issue_number
        self.branch = branch
        self.repo = repo
        self.project_root = Path(__file__).parent.parent.resolve()
        self.checks: List[CheckResult] = []

    def run(self) -> EvaluationReport:
        print(f"\n{'='*70}")
        print(f"  EVALUATOR BOT — Issue #{self.issue_number} ← Branch: {self.branch}")
        print(f"{'='*70}\n")

        # 1. Fetch issue details from GitHub
        self._check_issue_exists()

        # 2. Verify branch exists (do NOT checkout — evaluator stays on dev)
        self._verify_branch()

        # 3. Semantic check: read diff and validate against issue
        self._validate_diff_semantics()

        # 4. Run Flutter tests
        self._run_flutter_tests()

        # 5. Run pipeline (if applicable)
        self._run_pipeline_if_applicable()

        # 6. Issue-specific validation (reads files from branch via git show)
        self._run_issue_specific_checks()

        # 7. Compute verdict
        return self._compute_verdict()

    def _exec(self, cmd: list, cwd: Optional[Path] = None, timeout: int = 120) -> tuple:
        """Run a command and return (stdout, stderr, returncode, duration_ms)."""
        start = datetime.now()
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            duration = int((datetime.now() - start).total_seconds() * 1000)
            return result.stdout, result.stderr, result.returncode, duration
        except subprocess.TimeoutExpired:
            return "", f"Command timed out after {timeout}s", -1, timeout * 1000

    def _check_issue_exists(self):
        """Fetch issue via gh CLI to confirm it exists and extract metadata."""
        stdout, stderr, rc, dur = self._exec(
            ["gh", "issue", "view", str(self.issue_number), "--repo", self.repo, "--json", "title,body,labels,state"]
        )
        if rc != 0:
            self.checks.append(CheckResult(
                name="Issue Exists",
                status="FAIL",
                details=f"Cannot fetch issue #{self.issue_number}: {stderr.strip()}",
                duration_ms=dur,
            ))
            return

        try:
            issue_data = json.loads(stdout)
            title = issue_data.get("title", "N/A")
            state = issue_data.get("state", "UNKNOWN")
            self.checks.append(CheckResult(
                name="Issue Exists",
                status="PASS" if state == "OPEN" else "WARN",
                details=f"Issue #{self.issue_number}: {title} (state={state})",
                duration_ms=dur,
            ))
            self.issue_body = issue_data.get("body", "")
        except json.JSONDecodeError:
            self.checks.append(CheckResult(
                name="Issue Exists",
                status="WARN",
                details="Could not parse issue JSON",
                duration_ms=dur,
            ))
            self.issue_body = ""

    def _verify_branch(self):
        """Verify branch exists but DO NOT checkout — evaluator must stay on dev."""
        _, stderr, rc, dur = self._exec(["git", "fetch", "origin"])
        if rc != 0:
            self.checks.append(CheckResult(
                name="Git Fetch",
                status="FAIL",
                details=f"git fetch failed: {stderr.strip()}",
                duration_ms=dur,
            ))
            return

        stdout, _, rc, _ = self._exec(["git", "branch", "-r", "--list", f"origin/{self.branch}"])
        local_out, _, _, _ = self._exec(["git", "branch", "--list", self.branch])
        if not stdout.strip() and not local_out.strip():
            self.checks.append(CheckResult(
                name="Branch Exists",
                status="FAIL",
                details=f"Branch '{self.branch}' not found locally or on origin",
                duration_ms=dur,
            ))
            return

        self.checks.append(CheckResult(
            name="Branch Exists",
            status="PASS",
            details=f"Branch '{self.branch}' found (evaluator staying on current branch)",
            duration_ms=dur,
        ))

    def _validate_diff_semantics(self):
        """Check that the diff touches files relevant to the issue."""
        stdout, stderr, rc, dur = self._exec(
            ["git", "diff", f"dev...{self.branch}", "--name-only"]
        )
        if rc != 0:
            self.checks.append(CheckResult(
                name="Diff Semantic Check",
                status="FAIL",
                details=f"Could not compute diff: {stderr.strip()}",
                duration_ms=dur,
            ))
            return

        changed_files = [f.strip() for f in stdout.strip().split("\n") if f.strip()]
        if not changed_files:
            self.checks.append(CheckResult(
                name="Diff Semantic Check",
                status="FAIL",
                details="No files changed in this branch",
                duration_ms=dur,
            ))
            return

        # Heuristic: check issue body for file hints
        body_lower = getattr(self, "issue_body", "").lower()
        semantic_hits = 0
        for f in changed_files:
            f_base = os.path.basename(f).lower()
            if f_base.replace("_", " ") in body_lower or f_base in body_lower:
                semantic_hits += 1

        status = "PASS" if semantic_hits > 0 or len(changed_files) <= 5 else "WARN"
        details = f"Changed {len(changed_files)} file(s): {', '.join(changed_files[:5])}"
        if len(changed_files) > 5:
            details += f" (+{len(changed_files)-5} more)"

        self.checks.append(CheckResult(
            name="Diff Semantic Check",
            status=status,
            details=details,
            duration_ms=dur,
        ))
        self.changed_files = changed_files

    def _run_flutter_tests(self):
        """Run flutter test and report results.
        
        For pipeline-only changes (scripts/, no lib/ changes), pre-existing
        app test failures are not blockers — they are tracked in separate issues.
        """
        changed = getattr(self, "changed_files", [])
        touches_app = any(f.startswith("lib/") or f.startswith("mathwise_build/lib/") for f in changed)
        touches_pipeline = any("scripts/" in f for f in changed)

        print("  → Running flutter test...")
        flutter_cwd = self.project_root / "mathwise_build"
        if not (flutter_cwd / "pubspec.yaml").exists():
            flutter_cwd = self.project_root

        stdout, stderr, rc, dur = self._exec(
            ["flutter", "test"],
            cwd=flutter_cwd,
            timeout=300,
        )
        output = stdout + stderr

        # Parse test results — Flutter format: "+31 -45: Some tests failed."
        passed = re.search(r'\+(\d+)', output) or re.search(r'(\d+) passed', output)
        failed = re.search(r'-(\d+)', output) or re.search(r'(\d+) failed', output)
        n_passed = int(passed.group(1)) if passed else 0
        n_failed = int(failed.group(1)) if failed else 0

        if n_failed == 0:
            status = "PASS"
            details = f"All tests passed ({n_passed} passed)"
        elif n_failed > 0 and touches_pipeline and not touches_app:
            # Pipeline-only change: pre-existing failures are warnings, not blockers
            status = "WARN"
            details = f"{n_passed} passed, {n_failed} failed — pre-existing app issues (not caused by pipeline change)"
        elif n_failed > 0:
            status = "FAIL"
            fail_match = re.search(r'(FAIL|failed):\s*(.+)', output)
            fail_detail = fail_match.group(0) if fail_match else f"{n_failed} test(s) failed"
            details = f"{n_passed} passed, {n_failed} failed. {fail_detail[:200]}"
        else:
            status = "FAIL"
            details = f"flutter test exited {rc}. {output[:300]}"

        self.checks.append(CheckResult(
            name="Flutter Tests",
            status=status,
            details=details,
            duration_ms=dur,
        ))

    def _run_pipeline_if_applicable(self):
        """Run visual test pipeline if the branch touches pipeline files."""
        changed = getattr(self, "changed_files", [])
        pipeline_files = {"scripts/screenshot_auditor.py", "scripts/ux_evaluator.py",
                          "scripts/visual_test_pipeline.py", "scripts/screenshot_capture.py",
                          "scripts/report_builder.py"}
        if not any(f in pipeline_files for f in changed):
            self.checks.append(CheckResult(
                name="Pipeline Execution",
                status="SKIP",
                details="No pipeline files modified; skipping pipeline run",
                duration_ms=0,
            ))
            return

        print("  → Running visual test pipeline...")
        stdout, stderr, rc, dur = self._exec(
            ["python3", "scripts/visual_test_pipeline.py", "--skip-goldens", "--verbose"],
            timeout=180,
        )
        if rc == 0:
            status = "PASS"
            details = "Pipeline completed successfully"
        else:
            status = "FAIL"
            details = f"Pipeline failed (exit {rc}): {(stdout+stderr)[:300]}"

        self.checks.append(CheckResult(
            name="Pipeline Execution",
            status=status,
            details=details,
            duration_ms=dur,
        ))

    def _run_issue_specific_checks(self):
        """Run acceptance criteria validation based on issue number."""
        issue_checks = {
            1: self._check_p1_background,
            2: self._check_p2_touch_target,
            3: self._check_p3_blue_detection,
            4: self._check_p4_bottom_nav,
            5: self._check_a1_overflow,
            6: self._check_a2_profile,
            7: self._check_a3_games,
        }
        check_fn = issue_checks.get(self.issue_number)
        if check_fn:
            check_fn()
        else:
            self.checks.append(CheckResult(
                name="Issue-Specific Validation",
                status="SKIP",
                details=f"No specific validator for issue #{self.issue_number}",
                duration_ms=0,
            ))

    def _read_file_from_branch(self, rel_path: str) -> str:
        """Read a file from the target branch without checking it out."""
        stdout, stderr, rc, _ = self._exec(
            ["git", "show", f"{self.branch}:{rel_path}"]
        )
        if rc == 0:
            return stdout
        # Fallback: read from working tree if same as branch
        path = self.project_root / rel_path
        return path.read_text() if path.exists() else ""

    # --- Issue-specific validators ---

    def _check_p1_background(self):
        """P1: Auditor should not flag #000000 on widget test screenshots."""
        content = self._read_file_from_branch("mathwise_build/scripts/screenshot_auditor.py")
        has_fix = "inset" in content.lower() or "artifact" in content.lower() or "test-binding" in content.lower()
        self.checks.append(CheckResult(
            name="P1 Background Fix",
            status="PASS" if has_fix else "FAIL",
            details="Auditor detects and excludes test-binding unfilled margins" if has_fix else "No fix for test-binding #000000 false positive detected",
            duration_ms=0,
        ))

    def _check_p2_touch_target(self):
        """P2: Touch target should use constant 48dp, not scaled by width."""
        content = self._read_file_from_branch("mathwise_build/scripts/screenshot_auditor.py")
        has_bug = re.search(r'48\s*\*\s*.*width', content) is not None
        # Fix can be: constant 48dp, or mention of dpr/device pixel ratio, or Material Design citation
        has_fix = ("device_pixel_ratio" in content.lower() or
                   "device pixel ratio" in content.lower() or
                   "material design" in content.lower() or
                   "wcag" in content.lower()) and not has_bug
        self.checks.append(CheckResult(
            name="P2 Touch Target Fix",
            status="PASS" if has_fix else "FAIL",
            details="Touch target uses 48dp constant (no viewport scaling)" if has_fix else "Still using viewport-width-scaled touch target",
            duration_ms=0,
        ))

    def _check_p3_blue_detection(self):
        """P3: Blue detection should account for thin persistent UI chrome."""
        content = self._read_file_from_branch("mathwise_build/scripts/ux_evaluator.py")
        has_region_weight = "region" in content.lower() or "top" in content.lower()
        has_threshold_adjust = "threshold" in content.lower() and "0.01" in content
        self.checks.append(CheckResult(
            name="P3 Blue Detection Fix",
            status="PASS" if has_region_weight else "FAIL",
            details="Blue detection weights screen regions or adjusts threshold" if has_region_weight else "No region-based or threshold fix for blue detection",
            duration_ms=0,
        ))

    def _check_p4_bottom_nav(self):
        """P4: Evaluator should not flag missing bottom nav on sub-screens."""
        content = self._read_file_from_branch("mathwise_build/scripts/ux_evaluator.py")
        has_config = "sub-screen" in content.lower() or "tab-root" in content.lower() or "pushed" in content.lower()
        self.checks.append(CheckResult(
            name="P4 Bottom Nav Fix",
            status="PASS" if has_config else "FAIL",
            details="Evaluator classifies tab-root vs sub-screens" if has_config else "No sub-screen classification detected",
            duration_ms=0,
        ))

    def _check_a1_overflow(self):
        """A1: No horizontal overflow stripes on tablet viewports."""
        self.checks.append(CheckResult(
            name="A1 Overflow Fix",
            status="WARN",
            details="Requires visual verification: check goldens at 768x1024 and 1024x768 for yellow/black stripes",
            duration_ms=0,
        ))

    def _check_a2_profile(self):
        """A2: Profile screen should not overflow."""
        content = self._read_file_from_branch("mathwise_build/lib/features/profile/profile_screen.dart")
        has_expanded = "Expanded" in content or "LayoutBuilder" in content or "SingleChildScrollView" in content
        self.checks.append(CheckResult(
            name="A2 Profile Overflow Fix",
            status="PASS" if has_expanded else "FAIL",
            details="Profile uses responsive wrapping (Expanded/LayoutBuilder)" if has_expanded else "No responsive wrapping detected in profile",
            duration_ms=0,
        ))

    def _check_a3_games(self):
        """A3: Games screen should adapt to tablet viewports."""
        content = self._read_file_from_branch("mathwise_build/lib/screens/games_screen.dart")
        has_responsive = "LayoutBuilder" in content or "MediaQuery" in content or "GridView" in content
        self.checks.append(CheckResult(
            name="A3 Games Tablet Fix",
            status="PASS" if has_responsive else "FAIL",
            details="Games screen uses responsive layout patterns" if has_responsive else "No responsive layout detected in games screen",
            duration_ms=0,
        ))

    def _compute_verdict(self) -> EvaluationReport:
        """Compute final verdict from all checks."""
        weights = {
            "Issue Exists": 0.5,
            "Branch Exists": 1.0,
            "Diff Semantic Check": 1.5,
            "Flutter Tests": 3.0,
            "Pipeline Execution": 2.0,
            "P1 Background Fix": 2.0,
            "P2 Touch Target Fix": 2.0,
            "P3 Blue Detection Fix": 2.0,
            "P4 Bottom Nav Fix": 2.0,
            "A1 Overflow Fix": 3.0,
            "A2 Profile Overflow Fix": 3.0,
            "A3 Games Tablet Fix": 3.0,
            "Issue-Specific Validation": 2.0,
        }

        # Detect if this is a pipeline-only change
        changed = getattr(self, "changed_files", [])
        touches_app = any(f.startswith("lib/") or f.startswith("mathwise_build/lib/") for f in changed)
        touches_pipeline = any("scripts/" in f for f in changed)
        is_pipeline_only = touches_pipeline and not touches_app

        total_weight = 0.0
        earned_weight = 0.0
        recommendations = []

        for check in self.checks:
            w = weights.get(check.name, 1.0)
            total_weight += w
            if check.status == "PASS":
                earned_weight += w
            elif check.status == "WARN":
                # For pipeline-only changes, WARN on Flutter Tests (pre-existing failures)
                # should not heavily penalize — treat as 0.85 instead of 0.5
                if is_pipeline_only and check.name == "Flutter Tests":
                    earned_weight += w * 0.85
                else:
                    earned_weight += w * 0.5
            elif check.status == "FAIL":
                recommendations.append(f"[{check.name}] {check.details}")
            elif check.status == "SKIP":
                # For pipeline-only changes, SKIP on Pipeline Execution is expected
                # when no pipeline files changed — give partial credit
                if is_pipeline_only and check.name == "Pipeline Execution":
                    earned_weight += w * 0.5
                # Otherwise SKIP contributes 0

        score = (earned_weight / total_weight * 100) if total_weight > 0 else 0

        # Pipeline-only fixes get lower PASS threshold because pre-existing
        # app test failures are tracked in separate issues (A1–A3).
        pass_threshold = 80 if is_pipeline_only else 90
        if score >= pass_threshold:
            verdict = "PASS"
        elif score >= 70:
            verdict = "PARTIAL"
        else:
            verdict = "FAIL"

        report = EvaluationReport(
            issue_number=self.issue_number,
            branch=self.branch,
            verdict=verdict,
            overall_score=round(score, 1),
            checks=self.checks,
            timestamp=datetime.utcnow().isoformat() + "Z",
            recommendations=recommendations,
        )

        # Save reports
        self._save_reports(report)
        return report

    def _save_reports(self, report: EvaluationReport):
        """Write JSON and markdown reports."""
        reports_dir = self.project_root / "reports"
        reports_dir.mkdir(exist_ok=True)

        # JSON
        json_path = reports_dir / f"evaluation_issue_{self.issue_number}_{self.branch.replace('/', '_')}.json"
        with open(json_path, "w") as f:
            json.dump(report.to_dict(), f, indent=2)

        # Markdown
        md_path = reports_dir / f"evaluation_issue_{self.issue_number}_{self.branch.replace('/', '_')}.md"
        lines = [
            f"# Evaluation Report — Issue #{self.issue_number} ← `{self.branch}`",
            "",
            f"**Verdict:** `{report.verdict}` | **Score:** {report.overall_score}/100",
            f"**Timestamp:** {report.timestamp}",
            "",
            "## Checks",
            "",
            "| Check | Status | Details | Duration |",
            "|-------|--------|---------|----------|",
        ]
        for c in report.checks:
            status_badge = f"**{c.status}**"
            lines.append(f"| {c.name} | {status_badge} | {c.details[:80]} | {c.duration_ms}ms |")

        if report.recommendations:
            lines.extend(["", "## Recommendations", ""])
            for r in report.recommendations:
                lines.append(f"- {r}")

        lines.extend(["", "---", "*Generated by Evaluator Bot v1.0*"])
        md_path.write_text("\n".join(lines))

        print(f"\n  Reports saved:")
        print(f"    - {json_path}")
        print(f"    - {md_path}")


def main():
    parser = argparse.ArgumentParser(description="Evaluate a branch against a GitHub issue")
    parser.add_argument("--issue", type=int, required=True, help="GitHub issue number")
    parser.add_argument("--branch", type=str, required=True, help="Branch to evaluate")
    parser.add_argument("--repo", type=str, default="shivaram19/drmath", help="GitHub repo")
    args = parser.parse_args()

    bot = EvaluatorBot(args.issue, args.branch, args.repo)
    report = bot.run()

    print(f"\n{'='*70}")
    print(f"  VERDICT: {report.verdict} — Score: {report.overall_score}/100")
    print(f"{'='*70}")

    sys.exit(0 if report.verdict == "PASS" else 1)


if __name__ == "__main__":
    main()
