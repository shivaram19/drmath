"""Quick test suite for the Dr. Math pipeline."""
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from pipeline.scraper import fetch_ixl_topics, search_mathisfun_topic
from pipeline.content_adapter import strip_html
from pipeline.question_generator import parse_json_array


def test_ixl_scraper():
    print("[TEST] IXL Topic Scraper")
    topics = fetch_ixl_topics()
    assert len(topics) > 100, f"Expected >100 topics, got {len(topics)}"
    assert any("integer" in t.lower() for t, _ in topics), "Integers not found"
    assert any("fraction" in t.lower() for t, _ in topics), "Fractions not found"
    print(f"  ✅ Found {len(topics)} topics")
    print(f"  ✅ Sample: {topics[0][0]}")


def test_obscura_fetch():
    print("[TEST] Obscura MathIsFun Fetch")
    html = search_mathisfun_topic("integers")
    assert len(html) > 5000, f"Expected >5000 chars, got {len(html)}"
    assert "integer" in html.lower() or "number" in html.lower(), "Content seems wrong"
    print(f"  ✅ Fetched {len(html)} chars")


def test_html_stripper():
    print("[TEST] HTML Stripper")
    raw = "<html><body><script>alert('x')</script><p>Hello 123</p></body></html>"
    clean = strip_html(raw)
    assert "alert" not in clean, "Script not removed"
    assert "Hello 123" in clean, "Text not extracted"
    print(f"  ✅ Clean text extracted")


def test_json_parser():
    print("[TEST] JSON Array Parser")
    # Normal case
    normal = '[{"id":1,"difficulty":1}]'
    assert parse_json_array(normal) == [{"id": 1, "difficulty": 1}]
    # Markdown fences
    fenced = '```json\n[{"id":1}]\n```'
    assert parse_json_array(fenced) == [{"id": 1}]
    # Extra text
    extra = 'Here is your JSON:\n[{"id":1}]\nHope that helps!'
    assert parse_json_array(extra) == [{"id": 1}]
    print("  ✅ All parser cases pass")


def test_output_structure():
    print("[TEST] Output JSON Structure")
    out_file = Path("output/integers_v2.json")
    if not out_file.exists():
        print("  ⚠️  No output file to test (run pipeline first)")
        return
    data = json.loads(out_file.read_text())
    assert data["topic"] == "Integers"
    assert len(data["source_ixl_skills"]) >= 10
    assert len(data["questions"]) == 40
    for q in data["questions"]:
        assert "id" in q
        assert "difficulty" in q and 1 <= q["difficulty"] <= 4
        assert "question" in q
        assert "options" in q and len(q["options"]) == 4
        assert "correct_answer" in q and q["correct_answer"] in "ABCD"
        assert "explanation" in q
    # Check distribution
    dist = data["meta"]["difficulty_distribution"]
    assert sum(dist.values()) == 40
    print(f"  ✅ 40 questions validated")
    print(f"  ✅ Difficulty distribution: {dist}")


def run_all():
    print("=" * 50)
    print("DR. MATH PIPELINE TEST SUITE")
    print("=" * 50)
    test_ixl_scraper()
    test_obscura_fetch()
    test_html_stripper()
    test_json_parser()
    test_output_structure()
    print("=" * 50)
    print("ALL TESTS PASSED ✅")
    print("=" * 50)


if __name__ == "__main__":
    run_all()
