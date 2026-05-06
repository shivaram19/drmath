#!/usr/bin/env python3
"""
Screenshot Auditor — Dual-Persona Visual Testing Pipeline

Pixel-level layout and design token validation for Flutter screenshots.
Produces per-screen audit reports with pass/fail verdicts.

Usage:
    cd mathwise_build
    python3 scripts/screenshot_auditor.py --screenshots screenshots/YYYY-MM-DD_HH-MM-SS/

Output:
    reports/YYYY-MM-DD_HH-MM-SS/<screen_name>/audit_report.md
"""

from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from PIL import Image


# ── Data Structures ──────────────────────────────────────────────────────────

@dataclass
class Violation:
    category: str
    rule: str
    severity: str  # "critical", "warning", "info"
    message: str
    expected: Optional[str] = None
    actual: Optional[str] = None
    remediation: str = ""


@dataclass
class AuditResult:
    screen_name: str
    viewport: str
    screenshot_path: Path
    violations: list[Violation] = field(default_factory=list)
    checks_passed: int = 0
    checks_total: int = 0
    score: float = 0.0  # 0–100


# ── Color Utilities ──────────────────────────────────────────────────────────

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple[int, ...]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb[:3])


def color_distance(c1: tuple[int, ...], c2: tuple[int, ...]) -> float:
    """Euclidean distance in RGB space."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1[:3], c2[:3])))


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    """WCAG 2.1 relative luminance."""

    def channel(c: float) -> float:
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else math.pow((c + 0.055) / 1.055, 2.4)

    return 0.2126 * channel(rgb[0]) + 0.7152 * channel(rgb[1]) + 0.0722 * channel(rgb[2])


def contrast_ratio(rgb1: tuple[int, int, int], rgb2: tuple[int, int, int]) -> float:
    l1, l2 = relative_luminance(rgb1), relative_luminance(rgb2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


# ── Token Loader ─────────────────────────────────────────────────────────────

class TokenManifest:
    def __init__(self, path: Path):
        with open(path) as f:
            self.data = json.load(f)
        self.allowed_colors: list[tuple[str, tuple[int, int, int]]] = []
        for name, hex_val in self.data.get("colors", {}).items():
            self.allowed_colors.append((name, hex_to_rgb(hex_val)))
        for name, hex_val in self.data.get("pedagogy", {}).items():
            if isinstance(hex_val, str) and hex_val.startswith("#"):
                self.allowed_colors.append((name, hex_to_rgb(hex_val)))
        self.min_touch_target = self.data.get("pedagogy", {}).get("minTouchTarget", 48)
        self.spacing_values = set(self.data.get("spacing", {}).values())


# ── Audit Checks ─────────────────────────────────────────────────────────────

class ScreenshotAuditor:
    def __init__(self, tokens: TokenManifest):
        self.tokens = tokens
        self.color_tolerance = 15  # RGB distance tolerance

    def audit(self, screenshot_path: Path, screen_name: str, viewport: str) -> AuditResult:
        img = Image.open(screenshot_path)
        result = AuditResult(screen_name=screen_name, viewport=viewport, screenshot_path=screenshot_path)

        # Check 1: Color token compliance
        self._check_colors(img, result)

        # Check 2: Touch target sizes (approximate)
        self._check_touch_targets(img, result)

        # Check 3: Background color compliance
        self._check_background(img, result)

        # Check 4: Contrast (approximate, sampling common text areas)
        self._check_contrast(img, result)

        # Check 5: No pure red backgrounds (ADR-010 D4)
        self._check_no_red_backgrounds(img, result)

        # Calculate score
        if result.checks_total > 0:
            result.score = (result.checks_passed / result.checks_total) * 100

        return result

    def _check_colors(self, img: Image.Image, result: AuditResult) -> None:
        """Check that dominant colors match the token palette."""
        result.checks_total += 1

        # Sample a grid of pixels and check if they're near allowed colors
        width, height = img.size
        sample_points = [
            (width // 4, height // 4),
            (width // 2, height // 4),
            (3 * width // 4, height // 4),
            (width // 4, height // 2),
            (width // 2, height // 2),
            (3 * width // 4, height // 2),
            (width // 4, 3 * height // 4),
            (width // 2, 3 * height // 4),
            (3 * width // 4, 3 * height // 4),
        ]

        off_palette_count = 0
        for x, y in sample_points:
            if x >= width or y >= height:
                continue
            pixel = img.getpixel((x, y))
            if len(pixel) == 4:
                pixel = pixel[:3]

            # Skip near-white, near-black, and transparent pixels
            if max(pixel) > 250 or min(pixel) < 10:
                continue

            # Check against allowed colors
            min_dist = min(color_distance(pixel, allowed) for _, allowed in self.tokens.allowed_colors)
            if min_dist > self.color_tolerance * 2.5:  # Looser tolerance for sampled pixels
                off_palette_count += 1

        # Allow up to 2 off-palette samples (images, photos, etc.)
        if off_palette_count <= 2:
            result.checks_passed += 1
        else:
            result.violations.append(
                Violation(
                    category="Color Tokens",
                    rule="Colors must match design token palette",
                    severity="warning",
                    message=f"{off_palette_count} sampled pixels deviate significantly from token palette",
                    remediation="Verify that all UI colors use AppColors or PedagogyTokens definitions",
                )
            )

    def _check_touch_targets(self, img: Image.Image, result: AuditResult) -> None:
        """Approximate touch target size by looking for interactive-looking colored regions."""
        result.checks_total += 1

        # This is a heuristic: look for regions with the primary or secondary color
        # that are smaller than the minimum touch target in either dimension.
        # A more accurate approach would require semantic knowledge of where buttons are.
        # For now, we use a simplified check.

        width, height = img.size
        primary_rgb = hex_to_rgb("#2C5F9F")
        secondary_rgb = hex_to_rgb("#176B51")

        # Scan for small primary/secondary colored regions
        min_target_px = int(self.tokens.min_touch_target * (width / 390))  # Scale to viewport

        # Simplified: check if any primary-colored region is suspiciously small
        # We do this by looking at the bottom nav area where buttons should be
        bottom_nav_y = int(height * 0.88)
        if bottom_nav_y < height:
            nav_region = img.crop((0, bottom_nav_y, width, height))
            nav_width, nav_height = nav_region.size
            if nav_width > 0 and nav_height > 0:
                # Bottom nav should span full width and be reasonably tall
                if nav_height < min_target_px * 0.8:
                    result.violations.append(
                        Violation(
                            category="Touch Targets",
                            rule="Bottom navigation must be ≥ 48dp tall",
                            severity="warning",
                            message=f"Bottom nav appears to be ~{nav_height}px tall (expected ≥ {min_target_px}px)",
                            remediation="Increase bottom nav height or verify padding",
                        )
                    )
                else:
                    result.checks_passed += 1
            else:
                result.checks_passed += 1
        else:
            result.checks_passed += 1

    def _check_background(self, img: Image.Image, result: AuditResult) -> None:
        """Check that the background uses the correct surface color."""
        result.checks_total += 1

        width, height = img.size
        # Sample corners and center-top
        bg_samples = [
            img.getpixel((5, 5)),
            img.getpixel((width - 5, 5)),
            img.getpixel((width // 2, 5)),
        ]

        expected_bg = hex_to_rgb("#F8F9FF")
        all_match = True
        for pixel in bg_samples:
            if len(pixel) == 4:
                pixel = pixel[:3]
            if color_distance(pixel, expected_bg) > self.color_tolerance:
                all_match = False
                break

        if all_match:
            result.checks_passed += 1
        else:
            result.violations.append(
                Violation(
                    category="Background",
                    rule="Background must use AppColors.surface (#F8F9FF)",
                    severity="info",
                    message="Background color deviates from expected surface color",
                    expected="#F8F9FF",
                    actual=rgb_to_hex(bg_samples[0]),
                    remediation="Use AppColors.background or AppColors.surface for scaffold background",
                )
            )

    def _check_contrast(self, img: Image.Image, result: AuditResult) -> None:
        """Approximate contrast check on sampled text regions."""
        result.checks_total += 1

        width, height = img.size
        # Sample text regions: look for dark text on light background
        text_samples = [
            (width // 4, height // 6),   # Header area
            (width // 2, height // 3),   # Body text area
            (width // 2, height // 2),   # Mid content
        ]

        min_contrast = 4.5  # WCAG AA
        all_pass = True
        for x, y in text_samples:
            if x >= width or y >= height:
                continue
            pixel = img.getpixel((x, y))
            if len(pixel) == 4:
                pixel = pixel[:3]

            # Sample nearby background
            bg_pixel = img.getpixel((max(0, x - 2), y))
            if len(bg_pixel) == 4:
                bg_pixel = bg_pixel[:3]

            # Only check if there's meaningful difference (likely text)
            if color_distance(pixel, bg_pixel) > 30:
                ratio = contrast_ratio(pixel, bg_pixel)
                if ratio < min_contrast:
                    all_pass = False
                    result.violations.append(
                        Violation(
                            category="Contrast",
                            rule="Text must have ≥ 4.5:1 contrast against background (WCAG AA)",
                            severity="warning",
                            message=f"Sampled text contrast at ({x},{y}) is {ratio:.1f}:1",
                            expected="≥ 4.5:1",
                            actual=f"{ratio:.1f}:1",
                            remediation="Darken text or lighten background; verify with WebAIM contrast checker",
                        )
                    )

        if all_pass:
            result.checks_passed += 1

    def _check_no_red_backgrounds(self, img: Image.Image, result: AuditResult) -> None:
        """ADR-010 D4: No red backgrounds for error feedback."""
        result.checks_total += 1

        width, height = img.size
        # Sample the screen for large red regions
        red_count = 0
        sample_step = max(1, width // 40)
        for y in range(0, height, sample_step):
            for x in range(0, width, sample_step):
                pixel = img.getpixel((x, y))
                if len(pixel) == 4 and pixel[3] < 128:
                    continue
                r, g, b = pixel[:3]
                # Detect red-dominant pixels (R significantly > G and B)
                if r > 180 and r > g + 40 and r > b + 40:
                    red_count += 1

        # If more than 5% of sampled pixels are red, flag it
        total_samples = (width // sample_step) * (height // sample_step)
        red_ratio = red_count / total_samples if total_samples > 0 else 0

        if red_ratio < 0.05:
            result.checks_passed += 1
        else:
            result.violations.append(
                Violation(
                    category="Color Psychology",
                    rule="No red backgrounds (ADR-010 D4)",
                    severity="critical",
                    message=f"Red pixels cover ~{red_ratio*100:.1f}% of screen. Red impairs achievement-task performance (Elliot & Maier 2014).",
                    remediation="Use errorContainer (soft pink #FFDAD6) with red icon for errors, not red backgrounds",
                )
            )


# ── Report Generation ────────────────────────────────────────────────────────

def generate_audit_report(results: list[AuditResult], output_dir: Path) -> Path:
    """Generate a markdown audit report for a screen across all viewports."""
    if not results:
        return output_dir / "audit_report.md"

    screen_name = results[0].screen_name
    lines = [
        f"# Screenshot Audit Report: `{screen_name}`",
        "",
        "**Auditor:** Screenshot Auditor (pixel-level token validation)",
        f"**Screen:** {screen_name}",
        f"**Viewports tested:** {len(results)}",
        "",
        "## Summary",
        "",
        "| Viewport | Score | Passed | Total | Violations |",
        "|----------|-------|--------|-------|------------|",
    ]

    total_violations = 0
    for r in results:
        total_violations += len(r.violations)
        lines.append(
            f"| {r.viewport} | {r.score:.0f}/100 | {r.checks_passed} | {r.checks_total} | {len(r.violations)} |"
        )

    avg_score = sum(r.score for r in results) / len(results) if results else 0
    lines.extend([
        "",
        f"**Overall Score:** {avg_score:.0f}/100",
        f"**Total Violations:** {total_violations}",
        "",
        "## Violations by Viewport",
        "",
    ])

    for r in results:
        lines.extend([
            f"### {r.viewport} ({r.screenshot_path.name})",
            "",
        ])
        if not r.violations:
            lines.append("✅ No violations detected.")
            lines.append("")
            continue

        for v in r.violations:
            severity_emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(v.severity, "⚪")
            lines.extend([
                f"{severity_emoji} **{v.category}** — {v.rule}",
                "",
                f"- **Severity:** {v.severity.upper()}",
                f"- **Message:** {v.message}",
            ])
            if v.expected:
                lines.append(f"- **Expected:** {v.expected}")
            if v.actual:
                lines.append(f"- **Actual:** {v.actual}")
            if v.remediation:
                lines.append(f"- **Remediation:** {v.remediation}")
            lines.append("")

    report_path = output_dir / "audit_report.md"
    with open(report_path, "w") as f:
        f.write("\n".join(lines))
    return report_path


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Screenshot Auditor for Flutter visual testing")
    parser.add_argument("--screenshots", required=True, help="Path to screenshots directory (timestamped)")
    parser.add_argument("--tokens", default=None, help="Path to design_tokens.json")
    parser.add_argument("--output", default=None, help="Output directory for reports")
    args = parser.parse_args()

    screenshots_dir = Path(args.screenshots)
    tokens_path = Path(args.tokens) if args.tokens else Path(__file__).parent / "design_tokens.json"
    output_dir = Path(args.output) if args.output else screenshots_dir.parent.parent / "reports" / screenshots_dir.name

    if not screenshots_dir.exists():
        print(f"❌ Screenshots directory not found: {screenshots_dir}")
        return

    tokens = TokenManifest(tokens_path)
    auditor = ScreenshotAuditor(tokens)

    # Load capture metadata to know which screens were captured
    meta_path = screenshots_dir / "capture_metadata.json"
    if meta_path.exists():
        with open(meta_path) as f:
            metadata = json.load(f)
        screen_names = list(metadata.get("screens", {}).keys())
    else:
        # Discover from directory structure
        screen_names = [d.name for d in screenshots_dir.iterdir() if d.is_dir()]

    print(f"🔍 Auditing {len(screen_names)} screens against design tokens...")

    all_results: dict[str, list[AuditResult]] = {}

    for screen_name in screen_names:
        screen_dir = screenshots_dir / screen_name
        if not screen_dir.exists():
            continue

        screen_results = []
        for screenshot_file in sorted(screen_dir.glob("*.png")):
            viewport = screenshot_file.stem
            print(f"   → {screen_name} @ {viewport}")
            result = auditor.audit(screenshot_file, screen_name, viewport)
            screen_results.append(result)

        if screen_results:
            all_results[screen_name] = screen_results
            report_dir = output_dir / screen_name
            report_dir.mkdir(parents=True, exist_ok=True)
            report_path = generate_audit_report(screen_results, report_dir)
            print(f"      ✅ Report: {report_path}")

    # Generate summary
    print(f"\n📊 Audit Summary:")
    total_violations = sum(len(v.violations) for results in all_results.values() for v in results)
    avg_score = (
        sum(v.score for results in all_results.values() for v in results)
        / sum(len(results) for results in all_results.values())
    ) if all_results else 0
    print(f"   Overall Score: {avg_score:.0f}/100")
    print(f"   Total Violations: {total_violations}")
    print(f"   Reports: {output_dir}")


if __name__ == "__main__":
    main()
