"""Characterization tests for web/main.py routes.

These tests document the current HTTP behavior of the manager web interface
so that route-by-route refactoring can be verified without manual checks.
"""
import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db import crud
from db import database as db_module
from web.main import app


@pytest.fixture(scope="function")
def test_db(monkeypatch, tmp_path):
    """Create an isolated in-memory DB and patch filesystem-bound globals."""
    # Patch file-system paths that web.main holds at module import time.
    monkeypatch.setattr("web.main.OUTPUT_DIR", tmp_path / "output")
    monkeypatch.setattr("web.main.DATA_DIR", tmp_path / "data")

    # Patch legacy pipeline.db helpers so they do not touch the real DB.
    monkeypatch.setattr("web.main.list_prompts", lambda: [])
    monkeypatch.setattr("web.main.list_generations", lambda: [])
    monkeypatch.setattr(
        "web.main._list_topics",
        lambda: [
            {
                "slug": "integers",
                "name": "Integers",
                "total_questions": 40,
                "difficulty": {1: 10, 2: 10, 3: 10, 4: 10},
                "prompt_name": "Default",
                "version_count": 1,
                "versions": [],
            }
        ],
    )

    # Make the APK endpoint believe no APK is present so tests are deterministic.
    monkeypatch.setattr("web.main.APK_PATH", tmp_path / "mathwise.apk")

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    db_module.Base.metadata.create_all(bind=engine)
    return TestingSessionLocal


@pytest.fixture(scope="function")
def client(test_db):
    """Return a TestClient backed by the isolated in-memory database."""
    def get_test_db():
        db = test_db()
        try:
            yield db
        finally:
            db.close()

    original_override = app.dependency_overrides.get(db_module.get_db)
    app.dependency_overrides[db_module.get_db] = get_test_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        if original_override is not None:
            app.dependency_overrides[db_module.get_db] = original_override
        else:
            app.dependency_overrides.pop(db_module.get_db, None)


@pytest.fixture
def db_session(test_db):
    """Return the session factory used by the current test database."""
    return test_db


def test_home_page_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Integers" in response.text


def test_manager_page_returns_200(client):
    response = client.get("/manager")
    assert response.status_code == 200
    assert "Integers" in response.text


def test_topic_page_falls_back_to_db_when_no_file(client, db_session):
    # Seed a topic and generation in the test database.
    db = db_session()
    try:
        topic = crud.get_or_create_topic(db, "integers", "Integers")
        gen = crud.create_generation(
            db,
            topic_id=topic.id,
            prompt_id=None,
            status="success",
        )
        crud.update_generation(
            db,
            generation_id=gen.id,
            total_questions=1,
            questions_json=[{"id": 1, "question": "Q1"}],
            adapted_content="# Adapted content",
        )
    finally:
        db.close()

    response = client.get("/topic/integers")
    assert response.status_code == 200
    assert "Integers" in response.text
    assert "Q1" in response.text


def test_topic_page_returns_404_for_unknown_slug(client):
    response = client.get("/topic/unknown-topic")
    assert response.status_code == 404


def test_lab_page_returns_200(client, db_session):
    db = db_session()
    try:
        topic = crud.get_or_create_topic(db, "fractions", "Fractions")
        gen = crud.create_generation(
            db,
            topic_id=topic.id,
            prompt_id=None,
            status="success",
        )
        crud.update_generation(
            db,
            generation_id=gen.id,
            total_questions=40,
        )
    finally:
        db.close()

    response = client.get("/lab")
    assert response.status_code == 200
    assert "Fractions" in response.text


def test_api_leaderboard_returns_prompts_and_ratings(client, db_session):
    db = db_session()
    try:
        prompt = crud.create_prompt(
            db,
            name="Default",
            system_prompt="sys",
            question_prompt="q",
        )
        topic = crud.get_or_create_topic(db, "integers", "Integers")
        gen = crud.create_generation(
            db,
            topic_id=topic.id,
            prompt_id=prompt.id,
            status="success",
        )
        crud.create_evaluation(db, generation_id=gen.id, rating=5)
        expected_prompt_id = prompt.id
    finally:
        db.close()

    response = client.get("/api/leaderboard")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["prompt_id"] == expected_prompt_id
    assert data[0]["avg_rating"] == 5.0
    assert data[0]["eval_count"] == 1


def test_api_generation_detail_returns_generation(client, db_session):
    db = db_session()
    try:
        topic = crud.get_or_create_topic(db, "integers", "Integers")
        gen = crud.create_generation(
            db,
            topic_id=topic.id,
            prompt_id=None,
            status="success",
        )
        crud.update_generation(
            db,
            generation_id=gen.id,
            total_questions=40,
            difficulty_distribution={1: 10, 2: 10, 3: 10, 4: 10},
            questions_json=[{"id": 1, "question": "Q1"}],
        )
    finally:
        db.close()

    response = client.get(f"/api/generation/{gen.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == gen.id
    assert data["topic"] == "Integers"
    assert data["total_questions"] == 40
    assert data["difficulty"] == {"1": 10, "2": 10, "3": 10, "4": 10}
    assert data["timeline"] == []


def test_mathwise_apk_endpoint_returns_404_when_missing(client):
    response = client.get("/mathwise.apk")
    assert response.status_code == 404
    assert "APK not built yet" in response.json()["error"]
