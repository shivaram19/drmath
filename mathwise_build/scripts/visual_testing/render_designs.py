#!/usr/bin/env python3
"""Render Stitch design HTML files to screenshots at multiple viewports."""

import asyncio
import os
import subprocess
from pathlib import Path

from playwright.async_api import async_playwright

BASE_DIR = Path(__file__).parent.parent.parent
HTML_DIR = BASE_DIR / "screenshots" / "design_html"
OUTPUT_DIR = BASE_DIR / "screenshots" / "designs"

VIEWPORTS = {
    "mobile": {"width": 390, "height": 844},
    "tablet": {"width": 1024, "height": 768},
}

SCREENS = [
    "home_page",
    "curriculum_list",
    "profile_screen",
    "games_screen",
    "concept_content",
    "class_selection",
    "topic_choice",
    "practice_question",
]


async def start_server():
    """Start a simple HTTP server for the HTML files."""
    proc = subprocess.Popen(
        ["python3", "-m", "http.server", "8765"],
        cwd=HTML_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    await asyncio.sleep(1)
    return proc


async def render_screen(page, screen_name: str, viewport_name: str, width: int, height: int):
    """Render a single screen at a given viewport."""
    await page.set_viewport_size({"width": width, "height": height})
    url = f"http://localhost:8765/{screen_name}.html"
    await page.goto(url, wait_until="networkidle")
    # Wait for fonts to load
    await asyncio.sleep(2)

    # Take full page screenshot
    output_path = OUTPUT_DIR / f"{screen_name}_{viewport_name}.png"
    await page.screenshot(path=str(output_path), full_page=True)
    print(f"  ✓ {screen_name} @ {viewport_name} ({width}×{height})")
    return output_path


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    server = await start_server()
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            for screen in SCREENS:
                print(f"Rendering {screen}...")
                for vp_name, dims in VIEWPORTS.items():
                    await render_screen(page, screen, vp_name, dims["width"], dims["height"])

            await browser.close()
    finally:
        server.terminate()
        server.wait()

    print(f"\nAll screenshots saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
