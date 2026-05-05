"""
MathWise E2E Test: Practice Question Flows

Tests:
1. Answer a question correctly → see green feedback → Next Question
2. Answer a question incorrectly → see pink feedback with hint → Review Concept
3. Complete all 8 questions in the quiz
4. Verify progress dots update
5. Review Concept button navigates back to Concept Content
"""

import asyncio
from pydantic import BaseModel
from mobilerun import MobileAgent
from mobilerun.config_manager import MobileConfig


class QuizResult(BaseModel):
    total_questions: int
    correct_answers: int
    incorrect_answers: int
    hints_seen: int
    completed: bool


async def test_correct_answer_flow():
    """Select correct option → Submit → verify green feedback → Next Question."""
    config = MobileConfig.from_yaml("config/config.yaml")
    agent = MobileAgent(
        goal="On the MathWise Practice Question screen, read the question about triangles. "
             "Select the correct answer option (the one that makes sense mathematically). "
             "Tap 'Submit Answer'. "
             "Verify that a GREEN feedback card appears saying 'Correct!' or similar positive message. "
             "Then tap 'Next Question' and verify a new question appears (question 2 of 8).",
        config=config,
    )
    return await agent.run()


async def test_incorrect_answer_flow():
    """Select wrong option → Submit → verify pink feedback with hint → Review Concept."""
    config = MobileConfig.from_yaml("config/config.yaml")
    agent = MobileAgent(
        goal="On the MathWise Practice Question screen, deliberately select an INCORRECT answer. "
             "Tap 'Submit Answer'. "
             "Verify that a PINK/RED feedback card appears saying 'Not quite right' with a hint. "
             "Then tap 'Review Concept' and verify the Concept Content screen appears.",
        config=config,
    )
    return await agent.run()


async def test_complete_full_quiz():
    """Answer all 8 questions and verify completion."""
    config = MobileConfig.from_yaml("config/config.yaml")
    agent = MobileAgent(
        goal="Complete the entire MathWise triangle quiz (8 questions). "
             "For each question: read it, select the best answer, tap Submit, then tap Next Question. "
             "Keep going until all questions are done. "
             "Verify that after question 8, a completion message appears or the screen returns. "
             "Track how many you got correct vs incorrect.",
        config=config,
        output_model=QuizResult,
    )
    return await agent.run()


async def test_progress_dots_update():
    """Verify progress dots reflect current question index."""
    config = MobileConfig.from_yaml("config/config.yaml")
    agent = MobileAgent(
        goal="On the MathWise Practice Question screen, look at the progress dots at the bottom. "
             "Answer the first question and tap Next Question. "
             "Verify that the active dot (blue/larger) moves from position 1 to position 2. "
             "Do this for 3 questions total to confirm dot tracking works.",
        config=config,
    )
    return await agent.run()


async def test_review_concept_navigation():
    """From feedback card, Review Concept → Concept Content → Practice This Topic → back."""
    config = MobileConfig.from_yaml("config/config.yaml")
    agent = MobileAgent(
        goal="On the MathWise Practice Question screen, answer a question (any answer). "
             "On the feedback card, tap 'Review Concept'. "
             "Verify Concept Content screen opens. "
             "Scroll down and tap 'Practice This Topic'. "
             "Verify you return to Practice Question screen.",
        config=config,
    )
    return await agent.run()


async def run_all_practice_tests():
    """Run all practice flow tests."""
    print("=" * 60)
    print("TEST SUITE: Practice Question Flows")
    print("=" * 60)

    tests = [
        ("Correct answer → green feedback → next", test_correct_answer_flow),
        ("Incorrect answer → pink feedback → review concept", test_incorrect_answer_flow),
        ("Complete full 8-question quiz", test_complete_full_quiz),
        ("Progress dots update correctly", test_progress_dots_update),
        ("Review Concept circular navigation", test_review_concept_navigation),
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
    asyncio.run(run_all_practice_tests())
