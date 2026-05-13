#!/usr/bin/env python3
"""Capture screenshots of the Flutter web app via Playwright browser automation."""

import asyncio
import os
import subprocess
from pathlib import Path

from playwright.async_api import async_playwright

BASE_DIR = Path(__file__).parent.parent.parent
WEB_BUILD_DIR = BASE_DIR / "build" / "web"
OUTPUT_DIR = BASE_DIR / "screenshots" / "current_app"

VIEWPORTS = {
    "mobile": {"width": 390, "height": 844, "nav_y": 810},
    "tablet": {"width": 1024, "height": 768, "nav_y": 740},
}

# Bottom nav x positions for each viewport
NAV_POSITIONS = {
    "mobile": {"home": 50, "learning": 150, "games": 250, "profile": 340},
    "tablet": {"home": 200, "learning": 450, "games": 650, "profile": 900},
}


async def start_flutter_server():
    proc = subprocess.Popen(
        ["python3", "-m", "http.server", "8766"],
        cwd=WEB_BUILD_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    await asyncio.sleep(2)
    return proc


async def capture_screen(page, name: str, viewport_name: str):
    await asyncio.sleep(1.5)
    path = OUTPUT_DIR / f"{name}_{viewport_name}.png"
    await page.screenshot(path=str(path), full_page=False)
    print(f"  ✓ {name} @ {viewport_name}")
    return path


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not WEB_BUILD_DIR.exists():
        print(f"ERROR: Flutter web build not found at {WEB_BUILD_DIR}")
        return

    server = await start_flutter_server()
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()

            for vp_name, dims in VIEWPORTS.items():
                print(f"Capturing @ {vp_name} ({dims['width']}×{dims['height']})...")
                page = await browser.new_page(viewport={"width": dims["width"], "height": dims["height"]})

                await page.goto("http://localhost:8766/index.html", wait_until="networkidle")
                await asyncio.sleep(4)  # Wait for Flutter

                # Home
                await capture_screen(page, "home", vp_name)

                # Learning
                pos = NAV_POSITIONS[vp_name]["learning"]
                await page.mouse.click(pos, dims["nav_y"])
                await capture_screen(page, "learning", vp_name)

                # Games
                pos = NAV_POSITIONS[vp_name]["games"]
                await page.mouse.click(pos, dims["nav_y"])
                await capture_screen(page, "games", vp_name)

                # Profile
                pos = NAV_POSITIONS[vp_name]["profile"]
                await page.mouse.click(pos, dims["nav_y"])
                await capture_screen(page, "profile", vp_name)

                await page.close()

            await browser.close()
    finally:
        server.terminate()
        server.wait()

    print(f"\nAll screenshots saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
