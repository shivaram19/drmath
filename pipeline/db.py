"""SQLite-backed database layer (replaces JSON files).

All legacy functions keep the same signatures for backward compatibility.
New CRUD functions are exposed for the manager lab and evaluations.
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

# Ensure models are registered
from db.database import SessionLocal, Base, engine
from db import models
from db import crud

# Create tables on first import if they don't exist
Base.metadata.create_all(bind=engine)


def _session():
    """Get a new DB session."""
    return SessionLocal()


# ------------------------------------------------------------------
# Legacy-compatible prompt API
# ------------------------------------------------------------------

def list_prompts() -> List[Dict[str, Any]]:
    db = _session()
    try:
        prompts = crud.list_prompts(db)
        return [
            {
                "id": p.id,
                "name": p.name,
                "system_prompt": p.system_prompt,
                "question_prompt": p.question_prompt,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in prompts
        ]
    finally:
        db.close()


def get_prompt(prompt_id: str) -> Optional[Dict[str, Any]]:
    if not prompt_id:
        return None
    db = _session()
    try:
        p = crud.get_prompt(db, prompt_id)
        if not p:
            return None
        return {
            "id": p.id,
            "name": p.name,
            "system_prompt": p.system_prompt,
            "question_prompt": p.question_prompt,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
    finally:
        db.close()


def save_prompt(name: str, system_prompt: str, question_prompt: str) -> Dict[str, Any]:
    db = _session()
    try:
        p = crud.create_prompt(db, name, system_prompt, question_prompt)
        return {
            "id": p.id,
            "name": p.name,
            "system_prompt": p.system_prompt,
            "question_prompt": p.question_prompt,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
    finally:
        db.close()


def delete_prompt(prompt_id: str) -> bool:
    db = _session()
    try:
        return crud.delete_prompt(db, prompt_id)
    finally:
        db.close()


# ------------------------------------------------------------------
# Legacy-compatible generation API
# ------------------------------------------------------------------

def list_generations() -> List[Dict[str, Any]]:
    db = _session()
    try:
        gens = crud.list_generations(db)
        return [_gen_to_dict(g) for g in gens]
    finally:
        db.close()


def log_generation(topic: str, prompt_id: Optional[str], output_path: str, status: str, meta: Dict[str, Any]):
    """Legacy log — creates or updates a generation record."""
    db = _session()
    try:
        slug = topic.lower().replace(" ", "_")
        topic_obj = crud.get_or_create_topic(db, slug, topic)
        crud.create_generation(
            db,
            topic_id=topic_obj.id,
            prompt_id=prompt_id,
            status=status,
        )
    finally:
        db.close()


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------

def _gen_to_dict(g: models.Generation) -> Dict[str, Any]:
    return {
        "id": g.id,
        "topic": g.topic.name if g.topic else "",
        "prompt_id": g.prompt_id,
        "output_path": g.output_path,
        "status": g.status,
        "meta": json.loads(g.meta) if g.meta else {},
        "created_at": g.created_at.isoformat() if g.created_at else None,
    }
