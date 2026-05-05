"""
MathWise E2E Test: Curriculum & Topics Flows

Tests:
1. Curriculum List → expand chapter → tap subtopic → Topic Choice
2. Curriculum Grid → tap topic tile → Topic Choice
3. Curriculum Stepper → tap Resume Journey → Topic Choice
4. Topics & Subtopics → tap subtopic → Topic Choice
5. Topic Choice → Learn Concept → Concept Content
6. Topic Choice → Practice Problems → Practice Question
7. Concept Content → Practice This Topic → Practice Question
"""

import asyncio
from mobilerun import MobileAgent
from mobilerun.config_manager import MobileConfig


async def test_curriculum_list_subtopic():
    """Expand Chapter 2 in list view, tap Triangles subtopic."""
    config = MobileConfig.from_yaml("config/config.yaml")
    agent = MobileAgent(
        goal="On the MathWise Curriculum List screen, find Chapter 2 'Geometry'. "
             "If it is collapsed, tap it to expand. Then tap the 'Triangles' subtopic row. "
             "Verify the Topic Choice screen appears with 'Learn Concept' and 'Practice Problems' cards.",
        config=config,
    )
    return await agent.run()


async def test_curriculum_grid_tile():
    """Tap Triangles tile in 2×2 grid → Topic Choice."""
    config = MobileConfig.from_yaml("config/config.yaml")
    agent = MobileAgent(
        goal="On the MathWise Curriculum Grid screen, find the expanded Chapter 2 grid. "
             "Tap the 'Triangles' tile (should show 'In Progress'). "
             "Verify the Topic Choice screen appears.",
        config=config,
    )
    return await agent.run()


async def test_curriculum_stepper_resume():
    """Tap Resume Journey on current step → Topic Choice."""
    config = MobileConfig.from_yaml("config/config.yaml")
    agent = MobileAgent(
        goal="On the MathWise Curriculum Stepper screen, find the current step (blue circle with play icon). "
             "Tap the 'Resume Journey' button in that step's card. "
             "Verify the Topic Choice screen appears.",
        config=config,
    )
    return await agent.run()


async def test_topics_subtopics():
    """Tap subtopic in Topics & Subtopics accordion → Topic Choice."""
    config = MobileConfig.from_yaml("config/config.yaml")
    agent = MobileAgent(
        goal="On the MathWise Topics & Subtopics screen, find Chapter 2 'Geometry'. "
             "If collapsed, tap to expand. Then tap the 'Triangles' subtopic. "
             "Verify the Topic Choice screen appears.",
        config=config,
    )
    return await agent.run()


async def test_topic_choice_learn():
    """Tap Learn Concept → verify Concept Content with CPA sections."""
    config = MobileConfig.from_yaml("config/config.yaml")
    agent = MobileAgent(
        goal="On the MathWise Topic Choice screen, tap the 'Learn Concept' card (left side, book icon). "
             "Verify the Concept Content screen appears with: "
             "1. 'Why do we care?' section with bridge image, "
             "2. 'Classification Guide' with 3 triangle type cards, "
             "3. 'The Pythagorean Connection' with formula a² + b² = c². "
             "Scroll down to confirm all sections are visible.",
        config=config,
    )
    return await agent.run()


async def test_topic_choice_practice():
    """Tap Practice Problems → verify Practice Question screen."""
    config = MobileConfig.from_yaml("config/config.yaml")
    agent = MobileAgent(
        goal="On the MathWise Topic Choice screen, tap the 'Practice Problems' card (right side, pencil icon). "
             "Verify the Practice Question screen appears with a question, 4 options, and Submit button.",
        config=config,
    )
    return await agent.run()


async def test_concept_to_practice():
    """Concept Content → scroll down → Practice This Topic → Practice Question."""
    config = MobileConfig.from_yaml("config/config.yaml")
    agent = MobileAgent(
        goal="On the MathWise Concept Content screen, scroll to the bottom. "
             "Tap the large blue 'Practice This Topic' button. "
             "Verify the Practice Question screen appears with a triangle question.",
        config=config,
    )
    return await agent.run()


async def run_all_curriculum_tests():
    """Run all curriculum flow tests."""
    print("=" * 60)
    print("TEST SUITE: Curriculum & Topics Flows")
    print("=" * 60)

    tests = [
        ("Curriculum List → Subtopic → Topic Choice", test_curriculum_list_subtopic),
        ("Curriculum Grid → Tile → Topic Choice", test_curriculum_grid_tile),
        ("Curriculum Stepper → Resume Journey", test_curriculum_stepper_resume),
        ("Topics & Subtopics → Subtopic", test_topics_subtopics),
        ("Topic Choice → Learn Concept", test_topic_choice_learn),
        ("Topic Choice → Practice Problems", test_topic_choice_practice),
        ("Concept Content → Practice This Topic", test_concept_to_practice),
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
    asyncio.run(run_all_curriculum_tests())
