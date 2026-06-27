#!/usr/bin/env python3
"""
Screenshot Capture — Dual-Persona Visual Testing Pipeline

Captures Flutter web screens via Playwright. Some screens (reachable via
bottom nav or visible buttons) are captured here. Others (requiring scroll)
are captured via widget test golden files (test/visual_screenshots_test.dart).

Usage:
    cd mathwise_build
    python3 scripts/visual_testing/screenshot_capture.py [--output-dir screenshots/YYYY-MM-DD_HH-MM-SS]

Output:
    screenshots/YYYY-MM-DD_HH-MM-SS/<screen_name>/<viewport>.png
"""

from __future__ import annotations

import asyncio
import http.server
import json
import socketserver
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright, Page

# ── Configuration ────────────────────────────────────────────────────────────

BUILD_DIR = Path(__file__).parent.parent.parent / "build" / "web"
PORT = 9999
BASE_URL = f"http://localhost:{PORT}"

VIEWPORTS = [
    ("375x812", 375, 812),
    ("390x844", 390, 844),
    ("430x932", 430, 932),
    ("768x1024", 768, 1024),
    ("1024x768", 1024, 768),
]


@dataclass
class ScreenDef:
    name: str
    description: str
    navigate: callable  # async function(page) -> bool


# ── Navigation Helpers ───────────────────────────────────────────────────────

async def nav_home(page: Page) -> bool:
    await page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
    await asyncio.sleep(2.5)
    return True


async def nav_bottom_tab(page: Page, tab_x_ratio: float) -> bool:
    """Click a bottom nav tab using coordinate ratios."""
    await nav_home(page)
    vp = page.viewport_size
    x = int(vp["width"] * tab_x_ratio)
    y = int(vp["height"] * 0.93)
    await page.mouse.click(x, y)
    await asyncio.sleep(1.0)
    return True


async def nav_visible_button(page: Page, button_text: str, scroll_y_ratio: float = 0.0) -> bool:
    """Click a visible button by text. Optional scroll first."""
    await nav_home(page)
    if scroll_y_ratio > 0:
        # Attempt scroll via drag on canvas
        vp = page.viewport_size
        await page.mouse.move(vp["width"] // 2, int(vp["height"] * 0.7))
        await page.mouse.down()
        await page.mouse.move(vp["width"] // 2, int(vp["height"] * 0.3), steps=5)
        await page.mouse.up()
        await asyncio.sleep(0.5)
    try:
        await page.click(f"text='{button_text}'", timeout=5000)
        await asyncio.sleep(1.5)
        return True
    except Exception as e:
        print(f"      ⚠️  Could not click '{button_text}': {e}")
        return False


# Tab positions (normalized x coordinate for 4-tab bottom nav)
_TAB_HOME = 0.125
_TAB_LEARNING = 0.375
_TAB_GAMES = 0.625
_TAB_PROFILE = 0.875

SCREENS: list[ScreenDef] = [
    ScreenDef("home", "Home Screen", nav_home),
    ScreenDef("curriculum_list", "Curriculum List (Learning tab)", lambda p: nav_bottom_tab(p, _TAB_LEARNING)),
    ScreenDef("games", "Games Screen", lambda p: nav_bottom_tab(p, _TAB_GAMES)),
    ScreenDef("profile", "Profile Screen", lambda p: nav_bottom_tab(p, _TAB_PROFILE)),
    ScreenDef("practice_question", "Practice Question", lambda p: nav_visible_button(p, "Start Now")),
    ScreenDef("topic_choice", "Topic Choice", lambda p: nav_visible_button(p, "Resume Lesson")),
]


# ── HTTP Server ──────────────────────────────────────────────────────────────

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BUILD_DIR), **kwargs)

    def log_message(self, format, *args):
        pass


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def start_server() -> socketserver.TCPServer:
    handler = QuietHandler
    httpd = ReusableTCPServer(("", PORT), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    print(f"🌐 Serving Flutter web build at {BASE_URL}")
    return httpd


# ── Screenshot Capture ───────────────────────────────────────────────────────

async def capture_all_screens(output_dir: Path) -> dict:
    results = {
        "timestamp": datetime.now().isoformat(),
        "screens": {},
        "total_requested": len(SCREENS) * len(VIEWPORTS),
        "total_captured": 0,
        "failures": [],
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
        )
        page = await context.new_page()

        print(f"📸 Capturing {len(SCREENS)} screens × {len(VIEWPORTS)} viewports = {len(SCREENS) * len(VIEWPORTS)} screenshots")
        print(f"📁 Output: {output_dir}\n")

        for screen in SCREENS:
            screen_results = []
            for vp_name, vp_width, vp_height in VIEWPORTS:
                await page.set_viewport_size({"width": vp_width, "height": vp_height})
                await asyncio.sleep(0.3)

                print(f"   → {screen.description} @ {vp_name}")
                ok = await screen.navigate(page)
                if not ok:
                    results["failures"].append({"screen": screen.name, "viewport": vp_name})
                    continue

                screen_dir = output_dir / screen.name
                screen_dir.mkdir(parents=True, exist_ok=True)
                screenshot_path = screen_dir / f"{vp_name}.png"

                await page.screenshot(path=str(screenshot_path), full_page=False)
                print(f"      ✅ Saved: {screenshot_path}")
                screen_results.append({
                    "viewport": vp_name,
                    "width": vp_width,
                    "height": vp_height,
                    "path": str(screenshot_path.relative_to(output_dir)),
                })
                results["total_captured"] += 1

            results["screens"][screen.name] = {
                "description": screen.description,
                "viewports": screen_results,
            }

        await browser.close()

    return results


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None, help="Output directory for screenshots")
    args = parser.parse_args()

    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = Path(__file__).parent.parent.parent / "screenshots" / timestamp

    output_dir.mkdir(parents=True, exist_ok=True)

    server = start_server()
    time.sleep(1)

    try:
        results = asyncio.run(capture_all_screens(output_dir))

        meta_path = output_dir / "capture_metadata.json"
        with open(meta_path, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n📊 Summary:")
        print(f"   Captured: {results['total_captured']} / {results['total_requested']}")
        if results["failures"]:
            print(f"   Failures: {len(results['failures'])}")
            for f in results["failures"]:
                print(f"      - {f['screen']} @ {f['viewport']}")
        print(f"\n📁 Screenshots saved to: {output_dir}")
        print(f"📄 Metadata: {meta_path}")

    finally:
        server.shutdown()
        print("🛑 Server stopped")


if __name__ == "__main__":
    main()
