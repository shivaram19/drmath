"""
MathWise E2E Test: Profile & Games Flows

Tests:
1. Profile screen shows correct user data (Alex Johnson, Grade 8, Level 14)
2. Achievements grid displays 4 badges
3. Topic progress bars show Geometry 94%, Numbers 88%, Fractions 62%
4. Practice Fractions Now → Topic Choice
5. Games screen shows game cards and weekly challenge
6. Play Now shows SnackBar feedback
"""

import asyncio
from pydantic import BaseModel
from mobilerun import MobileAgent
from mobilerun.config_manager import MobileConfig


class ProfileValidation(BaseModel):
    username_visible: bool
    grade_visible: bool
    level_visible: bool
    streak_visible: bool
    badges_count: int
    strong_topics_count: int
    weak_topics_count: int


async def test_profile_data_display():
    """Verify all user profile data is rendered correctly."""
    config = MobileConfig.from_yaml("config/config.yaml")
    agent = MobileAgent(
        goal="On the MathWise Profile screen, verify the following data is visible: "
             "- Avatar image and name 'Alex Johnson' "
             "- 'Grade 8 • Math Enthusiast' subtitle "
             "- 'Level 14' badge and 'Top 5% Learner' badge "
             "- Stats: '24h' study hours, '12' topics completed, '85%' accuracy "
             "- 4 achievement badges: Fast Learner, Perfect Week, Math Wizard, 10 Day Streak "
             "- Strong Topics: Geometry 94%, Numbers 88% "
             "- Needs Focus: Fractions 62% "
             "Return a structured count of each element found.",
        config=config,
        output_model=ProfileValidation,
    )
    return await agent.run()


async def test_practice_fractions_button():
    """Tap Practice Fractions Now → verify Topic Choice screen."""
    config = MobileConfig.from_yaml("config/config.yaml")
    agent = MobileAgent(
        goal="On the MathWise Profile screen, scroll down to the 'Needs Focus' section. "
             "Tap the 'Practice Fractions Now' button. "
             "Verify the Topic Choice screen appears.",
        config=config,
    )
    return await agent.run()


async def test_games_screen_content():
    """Verify Games screen shows all expected content."""
    config = MobileConfig.from_yaml("config/config.yaml")
    agent = MobileAgent(
        goal="On the MathWise Games screen, verify the following are visible: "
             "- Stats row: 'Study Time Today' (1h 45m) and 'Lifelines' (3 Stars) "
             "- 'Play & Learn' header "
             "- 'Math Detective' game card with 1 star cost and 'Play Now' button "
             "- 'Puzzle Escape' game card with 2 stars cost and 'Play Now' button "
             "- 'Weekly Challenge' banner with trophy icon and 'Join Competition' button.",
        config=config,
    )
    return await agent.run()


async def test_play_now_snackbar():
    """Tap Play Now → verify SnackBar appears (demo behavior)."""
    config = MobileConfig.from_yaml("config/config.yaml")
    agent = MobileAgent(
        goal="On the MathWise Games screen, tap the 'Play Now' button on the 'Math Detective' card. "
             "Verify that a SnackBar or toast message appears saying 'Game starting...' or similar. "
             "The game does not actually launch (it's a demo).",
        config=config,
    )
    return await agent.run()


async def test_join_competition():
    """Tap Join Competition → verify Practice Question screen."""
    config = MobileConfig.from_yaml("config/config.yaml")
    agent = MobileAgent(
        goal="On the MathWise Games screen, scroll to the Weekly Challenge banner. "
             "Tap the 'Join Competition' button. "
             "Verify the Practice Question screen appears.",
        config=config,
    )
    return await agent.run()


async def run_all_profile_tests():
    """Run all profile and games tests."""
    print("=" * 60)
    print("TEST SUITE: Profile & Games Flows")
    print("=" * 60)

    tests = [
        ("Profile data display validation", test_profile_data_display),
        ("Practice Fractions Now → Topic Choice", test_practice_fractions_button),
        ("Games screen content", test_games_screen_content),
        ("Play Now → SnackBar (demo)", test_play_now_snackbar),
        ("Join Competition → Practice", test_join_competition),
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
    asyncio.run(run_all_profile_tests())
