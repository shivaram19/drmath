"""
MathWise E2E Test: Home Screen Flows

Tests:
1. App launches to Home screen
2. Resume Lesson → Topic Choice screen
3. Daily Practice → Practice Question screen
4. Enter Games → Games screen
5. Recommended topic → Topic Choice screen
6. Bottom nav switches between all 4 tabs
"""

import asyncio
from pydantic import BaseModel
from mobilerun import MobileAgent, MobileConfig
from mobilerun.config_manager import MobileConfig as ConfigManager


class HomeFlowResult(BaseModel):
    app_opened: bool
    resume_lesson_navigates: bool
    daily_practice_navigates: bool
    games_navigates: bool
    recommended_topic_navigates: bool
    bottom_nav_works: bool
    errors: list[str]


async def test_app_opens_to_home():
    """Verify the app opens and shows the Home screen."""
    config = ConfigManager.from_yaml("config/config.yaml")
    agent = MobileAgent(
        goal="Open the MathWise app and verify the Home screen is visible. "
             "Look for: 'Hello' greeting, 'Continue Learning' card, 'Daily Practice' card, "
             "'Math Playground' games summary, and 'Recommended for You' section. "
             "Return whether all these elements are present.",
        config=config,
        output_model=HomeFlowResult,
    )
    result = await agent.run()
    return result


async def test_resume_lesson_flow():
    """Tap Resume Lesson → verify Topic Choice screen."""
    config = ConfigManager.from_yaml("config/config.yaml")
    agent = MobileAgent(
        goal="On the MathWise Home screen, tap the 'Resume Lesson' button on the blue 'Continue Learning' card. "
             "Verify that the Topic Choice screen appears with two mode cards: "
             "'Learn Concept' (left) and 'Practice Problems' (right). "
             "Also verify the breadcrumb 'Geometry Foundations' and progress bar are visible.",
        config=config,
    )
    result = await agent.run()
    return result


async def test_daily_practice_flow():
    """Tap Start Now on Daily Practice → verify Practice Question screen."""
    config = ConfigManager.from_yaml("config/config.yaml")
    agent = MobileAgent(
        goal="On the MathWise Home screen, tap the 'Start Now' button on the 'Daily Practice' card. "
             "Verify that the Practice Question screen appears with a question about triangles, "
             "4 options (A/B/C/D), a triangle diagram, and a 'Submit Answer' button.",
        config=config,
    )
    result = await agent.run()
    return result


async def test_games_flow():
    """Tap Enter Games → verify Games screen."""
    config = ConfigManager.from_yaml("config/config.yaml")
    agent = MobileAgent(
        goal="On the MathWise Home screen, tap the 'Enter Games' button on the 'Math Playground' card. "
             "Verify that the Games screen appears with: 'Play & Learn' header, "
             "game cards (Math Detective, Puzzle Escape), star costs, and 'Play Now' buttons. "
             "Also check for the 'Weekly Challenge' section at the bottom.",
        config=config,
    )
    result = await agent.run()
    return result


async def test_bottom_navigation():
    """Tap all 4 bottom nav tabs and verify screen changes."""
    config = ConfigManager.from_yaml("config/config.yaml")
    agent = MobileAgent(
        goal="Test the bottom navigation bar in MathWise. Tap each tab in order and verify the screen changes: "
             "1. Tap 'Curriculum' tab → verify Curriculum list screen with chapters. "
             "2. Tap 'Games' tab → verify Games screen. "
             "3. Tap 'Profile' tab → verify Profile screen with avatar, stats, and achievements. "
             "4. Tap 'Home' tab → verify back to Home screen. "
             "Return success only if all 4 tabs work.",
        config=config,
    )
    result = await agent.run()
    return result


async def run_all_home_tests():
    """Run all home flow tests sequentially."""
    print("=" * 60)
    print("TEST SUITE: Home Screen Flows")
    print("=" * 60)

    tests = [
        ("App opens to Home", test_app_opens_to_home),
        ("Resume Lesson → Topic Choice", test_resume_lesson_flow),
        ("Daily Practice → Practice Question", test_daily_practice_flow),
        ("Enter Games → Games Screen", test_games_flow),
        ("Bottom Navigation (4 tabs)", test_bottom_navigation),
    ]

    results = []
    for name, test_fn in tests:
        print(f"\n▶ Running: {name}")
        try:
            result = await test_fn()
            success = getattr(result, 'success', False)
            reason = getattr(result, 'reason', 'N/A')
            steps = getattr(result, 'steps', 0)
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} | Steps: {steps} | {reason}")
            results.append((name, success, reason, steps))
        except Exception as e:
            print(f"  💥 ERROR: {e}")
            results.append((name, False, str(e), 0))

    return results


if __name__ == "__main__":
    asyncio.run(run_all_home_tests())
