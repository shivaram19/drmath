"""Characterization tests for pipeline/run.py::run_pipeline().

These tests pin the observable behavior of the pipeline before structural
refactoring. All external dependencies (scraper, LLM) are mocked so the tests
are deterministic and do not cost API tokens.
"""
import json
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db import database as db_module
from db import crud


@pytest.fixture
def pipeline_test_env(tmp_path, monkeypatch):
    """Provide an isolated environment for a single pipeline run."""
    data_dir = tmp_path / "data"
    output_dir = tmp_path / "output"
    data_dir.mkdir()
    output_dir.mkdir()

    # Isolate file-system artifacts. run.py imports these values, so we must
    # patch the references it holds, not just pipeline.config.
    monkeypatch.setattr("pipeline.config.DATA_DIR", data_dir)
    monkeypatch.setattr("pipeline.config.OUTPUT_DIR", output_dir)

    # Isolate the database. Re-bind the engine and SessionLocal before any
    # pipeline module that imports them is loaded.
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    monkeypatch.setattr(db_module, "engine", test_engine)
    monkeypatch.setattr(db_module, "SessionLocal", TestingSessionLocal)

    # Create tables in the test database. Importing db.models registers them
    # with the shared Base metadata.
    from db import models  # noqa: F401

    db_module.Base.metadata.create_all(bind=test_engine)

    # Import the pipeline runner only after the database is patched.
    from pipeline import run as run_module

    monkeypatch.setattr(run_module, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(run_module, "DATA_DIR", data_dir)
    monkeypatch.setattr(run_module, "OUTPUT_DIR", output_dir)

    def get_prompt_from_test_db(prompt_id):
        if not prompt_id:
            return None
        db = TestingSessionLocal()
        try:
            prompt = crud.get_prompt(db, prompt_id)
            if prompt is None:
                return None
            return {
                "id": prompt.id,
                "name": prompt.name,
                "system_prompt": prompt.system_prompt,
                "question_prompt": prompt.question_prompt,
                "parent_id": prompt.parent_id,
                "version": prompt.version,
                "created_at": prompt.created_at.isoformat() if prompt.created_at else None,
            }
        finally:
            db.close()

    monkeypatch.setattr(run_module, "get_prompt", get_prompt_from_test_db)

    # Mock external dependencies.
    monkeypatch.setattr(
        run_module,
        "fetch_ixl_topics",
        lambda: [
            ("Integers", "https://in.ixl.com/maths/class-vii/integers"),
            ("Fractions", "https://in.ixl.com/maths/class-vii/fractions"),
        ],
    )
    monkeypatch.setattr(
        run_module,
        "search_mathisfun_topic",
        lambda topic: (
            "<html><body><p>Math is fun with numbers.</p></body></html>",
            "https://www.mathsisfun.com/numbers.html",
        ),
    )

    class FakeLLMClient:
        """Returns deterministic content based on prompt intent."""

        def generate(self, system_prompt: str, user_prompt: str, temperature=0.7, max_tokens=4000) -> str:
            if user_prompt.strip().startswith("TOPIC:"):
                return "# Adapted lesson\n\nMath is fun with numbers."

            questions = []
            for i in range(40):
                difficulty = (i % 4) + 1
                questions.append(
                    {
                        "id": i + 1,
                        "difficulty": difficulty,
                        "question": f"Question {i + 1}",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": "A",
                        "explanation": f"Explanation for question {i + 1}",
                    }
                )
            return json.dumps(questions)

    monkeypatch.setattr(run_module, "LLMClient", FakeLLMClient)

    yield run_module, data_dir, output_dir, TestingSessionLocal


@pytest.fixture
def broken_llm_env(pipeline_test_env, monkeypatch):
    """Return a pipeline environment where the LLM returns invalid JSON."""
    run_module, data_dir, output_dir, SessionLocal = pipeline_test_env

    class BrokenLLMClient:
        def generate(self, system_prompt: str, user_prompt: str, temperature=0.7, max_tokens=4000) -> str:
            if user_prompt.strip().startswith("TOPIC:"):
                return "# Adapted lesson"
            return "this is not json"

    monkeypatch.setattr(run_module, "LLMClient", BrokenLLMClient)
    return run_module, data_dir, output_dir, SessionLocal


def test_run_pipeline_creates_output_json(pipeline_test_env):
    run_module, data_dir, output_dir, _ = pipeline_test_env

    output_path = output_dir / "integers_test.json"
    result = run_module.run_pipeline("Integers", str(output_path))

    assert output_path.exists()
    written = json.loads(output_path.read_text(encoding="utf-8"))
    assert written["topic"] == "Integers"
    assert written["prompt_name"] == "Default (Anti-Gravity)"
    assert len(written["questions"]) == 40
    assert written["meta"]["total_questions"] == 40
    assert sum(written["meta"]["difficulty_distribution"].values()) == 40

    # The returned dict should match the written file.
    assert result["topic"] == written["topic"]
    assert result["meta"]["total_questions"] == written["meta"]["total_questions"]


def test_run_pipeline_creates_raw_and_adapted_files(pipeline_test_env):
    run_module, data_dir, output_dir, _ = pipeline_test_env

    output_path = output_dir / "integers_test.json"
    run_module.run_pipeline("Integers", str(output_path))

    assert (data_dir / "integers_raw.html").exists()
    assert (data_dir / "integers_antigravity.md").exists()
    assert "Math is fun" in (data_dir / "integers_raw.html").read_text()
    assert "Adapted lesson" in (data_dir / "integers_antigravity.md").read_text()


def test_run_pipeline_persists_generation_record(pipeline_test_env):
    run_module, data_dir, output_dir, SessionLocal = pipeline_test_env

    output_path = output_dir / "integers_test.json"
    run_module.run_pipeline("Integers", str(output_path))

    db = SessionLocal()
    try:
        topic = crud.get_topic_by_slug(db, "integers")
        assert topic is not None
        assert topic.name == "Integers"

        generations = crud.get_topic_generations(db, "integers")
        assert len(generations) == 1
        gen = generations[0]
        assert gen.status == "success"
        assert gen.total_questions == 40
        assert gen.output_path == str(output_path)
        assert gen.raw_html_path is not None
        assert gen.antigravity_path is not None
    finally:
        db.close()


def test_run_pipeline_creates_grounding_logs(pipeline_test_env):
    run_module, data_dir, output_dir, SessionLocal = pipeline_test_env

    output_path = output_dir / "integers_test.json"
    run_module.run_pipeline("Integers", str(output_path))

    db = SessionLocal()
    try:
        generations = crud.get_topic_generations(db, "integers")
        gen = generations[0]

        assert len(gen.grounding_logs) >= 2  # at least IXL + MathIsFun
        sources = {log.source_type for log in gen.grounding_logs}
        assert "ixl" in sources
        assert "mathisfun" in sources

        mathisfun_logs = [log for log in gen.grounding_logs if log.source_type == "mathisfun"]
        assert mathisfun_logs[0].source_url == "https://www.mathsisfun.com/numbers.html"
    finally:
        db.close()


def test_run_pipeline_with_custom_prompt(pipeline_test_env):
    run_module, data_dir, output_dir, SessionLocal = pipeline_test_env

    # Seed a custom prompt in the test database.
    db = SessionLocal()
    try:
        custom = crud.create_prompt(
            db,
            name="Storyteller",
            system_prompt="You are a storyteller.",
            question_prompt="Generate story questions.",
        )
    finally:
        db.close()

    output_path = output_dir / "integers_prompt_test.json"
    result = run_module.run_pipeline("Integers", str(output_path), prompt_id=custom.id)

    assert result["prompt_id"] == custom.id
    assert result["prompt_name"] == custom.name


def test_run_pipeline_failure_is_recorded(broken_llm_env):
    run_module, data_dir, output_dir, SessionLocal = broken_llm_env

    output_path = output_dir / "integers_broken.json"
    with pytest.raises(Exception):
        run_module.run_pipeline("Integers", str(output_path))

    db = SessionLocal()
    try:
        generations = crud.get_topic_generations(db, "integers")
        assert len(generations) == 1
        gen = generations[0]
        assert gen.status == "error"
        assert "error" in json.loads(gen.meta or "{}")
    finally:
        db.close()
