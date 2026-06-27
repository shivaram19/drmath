#!/usr/bin/env python3
"""
Report Builder — Dual-Persona Visual Testing Pipeline

Aggregates per-screen audit and UX reports into a single summary markdown file
with overall quality score, priority-ranked remediation backlog, and cross-viewport
comparison matrix.

Usage:
    cd mathwise_build
    python3 scripts/report_builder.py --reports reports/YYYY-MM-DD_HH-MM-SS/

Output:
    reports/YYYY-MM-DD_HH-MM-SS/summary.md
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ── Data Structures ──────────────────────────────────────────────────────────

@dataclass
class ScreenSummary:
    name: str
    ux_score: float = 0.0
    audit_score: float = 0.0
    combined_score: float = 0.0
    viewport_count: int = 0
    critical_issues: int = 0
    high_issues: int = 0
    medium_issues: int = 0
    top_remediation: list[str] = field(default_factory=list)


@dataclass
class BacklogItem:
    screen: str
    viewport: str
    category: str
    severity: str
    issue: str
    remediation: str
    citation: str = ""


# ── Parser ───────────────────────────────────────────────────────────────────

class ReportParser:
    """Parse markdown reports to extract scores and findings."""

    @staticmethod
    def parse_ux_report(path: Path) -> tuple[float, list[dict]]:
        """Extract overall score and findings from a UX report."""
        text = path.read_text()
        findings = []

        # Extract score
        score_match = re.search(r"\*\*Overall Score:\*\*\s*(\d+(?:\.\d+)?)/100", text)
        score = float(score_match.group(1)) if score_match else 0.0

        # Extract issues (verdict != pass)
        issue_blocks = re.findall(
            r"([🔴🟠🟡🔵ℹ️⚪])\s*\*\*(.+?)\*\*\s*—\s*(.+?)\n"
            r"\n?\s*-\s*\*\*Verdict:\*\*\s*(\w+)\n"
            r"\s*-\s*\*\*Severity:\*\*\s*(\w+)\n"
            r"\s*-\s*\*\*Message:\*\*\s*(.+?)\n"
            r"\s*-\s*\*\*Citation:\*\*\s*(.+?)\n"
            r"\s*-\s*\*\*Remediation:\*\*\s*(.+?)(?=\n\n|\Z)",
            text,
            re.DOTALL,
        )

        for match in issue_blocks:
            emoji, category, rule, verdict, severity, message, citation, remediation = match
            findings.append({
                "category": category.strip(),
                "rule": rule.strip(),
                "severity": severity.strip().lower(),
                "message": message.strip(),
                "citation": citation.strip(),
                "remediation": remediation.strip(),
            })

        return score, findings

    @staticmethod
    def parse_audit_report(path: Path) -> tuple[float, list[dict]]:
        """Extract overall score and violations from an audit report."""
        text = path.read_text()
        violations = []

        # Extract score
        score_match = re.search(r"\*\*Overall Score:\*\*\s*(\d+(?:\.\d+)?)/100", text)
        score = float(score_match.group(1)) if score_match else 0.0

        # Extract violations
        violation_blocks = re.findall(
            r"([🔴🟡🔵⚪])\s*\*\*(.+?)\*\*\s*—\s*(.+?)\n"
            r"\n?\s*-\s*\*\*Severity:\*\*\s*(\w+)\n"
            r"\s*-\s*\*\*Message:\*\*\s*(.+?)(?=\n\s*-\s*\*\*Expected|\n\s*-\s*\*\*Remediation|\n\n|\Z)"
            r"(?:\n\s*-\s*\*\*Expected:\*\*\s*(.+?))?"
            r"(?:\n\s*-\s*\*\*Actual:\*\*\s*(.+?))?"
            r"(?:\n\s*-\s*\*\*Remediation:\*\*\s*(.+?))?",
            text,
            re.DOTALL,
        )

        for match in violation_blocks:
            emoji, category, rule, severity, message = match[0], match[1], match[2], match[3], match[4]
            remediation = match[7] if len(match) > 7 and match[7] else ""
            violations.append({
                "category": category.strip(),
                "severity": severity.strip().lower(),
                "message": message.strip(),
                "remediation": remediation.strip(),
            })

        return score, violations


# ── Builder ──────────────────────────────────────────────────────────────────

class ReportBuilder:
    def __init__(self, reports_dir: Path):
        self.reports_dir = reports_dir
        self.parser = ReportParser()
        self.screen_summaries: dict[str, ScreenSummary] = {}
        self.backlog: list[BacklogItem] = []

    def build(self) -> Path:
        """Aggregate all reports and generate summary.md."""
        self._collect_screen_data()
        self._build_backlog()
        return self._write_summary()

    def _collect_screen_data(self) -> None:
        """Walk the reports directory and parse all per-screen reports."""
        for screen_dir in sorted(self.reports_dir.iterdir()):
            if not screen_dir.is_dir():
                continue

            screen_name = screen_dir.name
            summary = ScreenSummary(name=screen_name)

            ux_path = screen_dir / "ux_report.md"
            audit_path = screen_dir / "audit_report.md"

            if ux_path.exists():
                score, findings = self.parser.parse_ux_report(ux_path)
                summary.ux_score = score
                summary.viewport_count = max(summary.viewport_count, self._count_viewports(findings))
                for f in findings:
                    self._tally_issue(summary, f["severity"])
                    self.backlog.append(BacklogItem(
                        screen=screen_name,
                        viewport="all",
                        category=f"UX: {f['category']}",
                        severity=f["severity"],
                        issue=f["message"],
                        remediation=f["remediation"],
                        citation=f.get("citation", ""),
                    ))

            if audit_path.exists():
                score, violations = self.parser.parse_audit_report(audit_path)
                summary.audit_score = score
                summary.viewport_count = max(summary.viewport_count, self._count_viewports(violations))
                for v in violations:
                    self._tally_issue(summary, v["severity"])
                    self.backlog.append(BacklogItem(
                        screen=screen_name,
                        viewport="all",
                        category=f"Audit: {v['category']}",
                        severity=v["severity"],
                        issue=v["message"],
                        remediation=v.get("remediation", ""),
                    ))

            summary.combined_score = (summary.ux_score + summary.audit_score) / 2
            self.screen_summaries[screen_name] = summary

    def _count_viewports(self, items: list[dict]) -> int:
        """Estimate viewport count from report content."""
        # Reports are aggregated per screen, so we can't directly count viewports from findings.
        # Use a heuristic: if the report exists, assume 5 viewports were tested.
        return 5

    def _tally_issue(self, summary: ScreenSummary, severity: str) -> None:
        if severity == "critical":
            summary.critical_issues += 1
        elif severity == "high":
            summary.high_issues += 1
        elif severity == "medium":
            summary.medium_issues += 1

    def _build_backlog(self) -> None:
        """Sort backlog by severity and deduplicate."""
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        self.backlog.sort(key=lambda x: severity_order.get(x.severity, 99))

        # Deduplicate by (screen, category, issue)
        seen = set()
        deduped = []
        for item in self.backlog:
            key = (item.screen, item.category, item.issue[:60])
            if key not in seen:
                seen.add(key)
                deduped.append(item)
        self.backlog = deduped[:50]  # Cap at 50 items

    def _write_summary(self) -> Path:
        """Generate the summary markdown report."""
        screens = sorted(self.screen_summaries.values(), key=lambda s: s.combined_score)
        overall_score = sum(s.combined_score for s in screens) / len(screens) if screens else 0
        total_critical = sum(s.critical_issues for s in screens)
        total_high = sum(s.high_issues for s in screens)
        total_medium = sum(s.medium_issues for s in screens)

        lines = [
            "# Visual Testing Pipeline — Executive Summary",
            "",
            f"**Date:** {self.reports_dir.name}",
            f"**Screens tested:** {len(screens)}",
            f"**Viewports per screen:** 5 (375×812, 390×844, 430×932, 768×1024, 1024×768)",
            f"**Total screenshots:** {len(screens) * 5}",
            "",
            "## Overall Quality Score",
            "",
            f"### {overall_score:.0f}/100",
            "",
            "| Metric | Count |",
            "|--------|-------|",
            f"| Critical Issues | {total_critical} |",
            f"| High Issues | {total_high} |",
            f"| Medium Issues | {total_medium} |",
            f"| Total Backlog Items | {len(self.backlog)} |",
            "",
            "---",
            "",
            "## Per-Screen Quality Matrix",
            "",
            "| Screen | UX Score | Audit Score | Combined | Critical | High | Medium |",
            "|--------|----------|-------------|----------|----------|------|--------|",
        ]

        for s in screens:
            lines.append(
                f"| `{s.name}` | {s.ux_score:.0f} | {s.audit_score:.0f} | **{s.combined_score:.0f}** | {s.critical_issues} | {s.high_issues} | {s.medium_issues} |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## Priority Remediation Backlog",
            "",
        ])

        if not self.backlog:
            lines.append("✅ No issues detected. All screens pass visual quality checks.")
        else:
            for i, item in enumerate(self.backlog, 1):
                severity_emoji = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🔵",
                    "info": "ℹ️",
                }.get(item.severity, "⚪")
                lines.extend([
                    f"{i}. {severity_emoji} **`{item.screen}`** — {item.category}",
                    f"   - **Issue:** {item.issue}",
                    f"   - **Remediation:** {item.remediation}",
                ])
                if item.citation:
                    lines.append(f"   - **Citation:** {item.citation}")
                lines.append("")

        lines.extend([
            "",
            "---",
            "",
            "## Methodology",
            "",
            "### Persona 1: Screenshot Auditor",
            "- Pixel-level validation of colors, spacing, and touch target sizes against `design_tokens.json`",
            "- Automated contrast ratio sampling (WCAG 2.1 AA)",
            "- Design token compliance: `AppColors` + `PedagogyTokens`",
            "",
            "### Persona 2: UI/UX Engineer",
            "- Cognitive load estimation via visual region counting (Miller 1956)",
            "- Color psychology validation: blue primary, no red backgrounds (Elliot & Maier 2014)",
            "- Navigation discoverability: bottom tab detection (Nielsen 2016)",
            "- Pedagogy compliance: ADR-010 D1–D10 screen-specific rules",
            "",
            "### Tools",
            "- **Capture:** Playwright + Flutter web build",
            "- **Analysis:** Python Pillow (pixel audit) + structured rubric (UX evaluation)",
            "- **Reporting:** Jinja2-inspired Markdown generation",
            "",
            "## References",
            "",
            "- ADR-010: Mobile UI Pedagogy",
            "- ADR-011: Visual Testing Pipeline",
            "- BFS-02: Visual Testing Landscape",
            "- DFS-02: Visual Testing Deep-Dive",
            "- Bidirectional-02: Cross-Domain Impact Analysis",
        ])

        summary_path = self.reports_dir / "summary.md"
        with open(summary_path, "w") as f:
            f.write("\n".join(lines))
        return summary_path


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Report Builder for visual testing pipeline")
    parser.add_argument("--reports", required=True, help="Path to reports directory (timestamped)")
    args = parser.parse_args()

    reports_dir = Path(args.reports)
    if not reports_dir.exists():
        print(f"❌ Reports directory not found: {reports_dir}")
        return

    builder = ReportBuilder(reports_dir)
    summary_path = builder.build()
    print(f"📊 Summary report generated: {summary_path}")

    # Print quick stats
    screens = builder.screen_summaries
    overall = sum(s.combined_score for s in screens.values()) / len(screens) if screens else 0
    print(f"\n   Overall Score: {overall:.0f}/100")
    print(f"   Screens: {len(screens)}")
    print(f"   Backlog Items: {len(builder.backlog)}")


if __name__ == "__main__":
    main()
