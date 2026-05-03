"""Initialize SQLite DB and migrate existing JSON data."""
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import engine, Base
from db.models import Prompt, Topic, Generation, Evaluation
from db.database import SessionLocal


def _parse_iso(s: str) -> datetime:
    """Parse ISO datetime, handling Z suffix."""
    s = s.replace("Z", "+00:00")
    return datetime.fromisoformat(s)


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created.")


def migrate_json_data():
    """Migrate existing prompts_db.json and generations_db.json into SQLite."""
    data_dir = Path(__file__).parent.parent / "data"
    prompts_path = data_dir / "prompts_db.json"
    gens_path = data_dir / "generations_db.json"

    db = SessionLocal()
    migrated_prompts = 0
    migrated_gens = 0

    # Migrate prompts
    if prompts_path.exists():
        prompts = json.loads(prompts_path.read_text())
        for p in prompts:
            existing = db.query(Prompt).filter(Prompt.id == p["id"]).first()
            if existing:
                continue
            created = _parse_iso(p["created_at"]) if "created_at" in p else datetime.utcnow()
            prompt = Prompt(
                id=p["id"],
                name=p["name"],
                system_prompt=p.get("system_prompt", ""),
                question_prompt=p.get("question_prompt", ""),
                created_at=created,
            )
            db.add(prompt)
            migrated_prompts += 1
        db.commit()
        print(f"✅ Migrated {migrated_prompts} prompts.")

    # Migrate generations
    if gens_path.exists():
        gens = json.loads(gens_path.read_text())
        for g in gens:
            # Check if already migrated (by output_path + created_at combo)
            slug = g["topic"].lower().replace(" ", "_")
            topic = db.query(Topic).filter(Topic.slug == slug).first()
            if not topic:
                from db.crud import get_or_create_topic
                topic = get_or_create_topic(db, slug, g["topic"])

            existing = (
                db.query(Generation)
                .filter(Generation.topic_id == topic.id)
                .filter(Generation.output_path == g.get("output_path"))
                .first()
            )
            if existing:
                continue

            created = _parse_iso(g["created_at"]) if "created_at" in g else datetime.utcnow()
            # Validate prompt exists, else null it
            prompt_id = g.get("prompt_id")
            if prompt_id:
                prompt_exists = db.query(Prompt).filter(Prompt.id == prompt_id).first()
                if not prompt_exists:
                    prompt_id = None

            gen = Generation(
                topic_id=topic.id,
                prompt_id=prompt_id,
                status=g.get("status", "success"),
                output_path=g.get("output_path"),
                total_questions=g.get("meta", {}).get("total_questions"),
                difficulty_distribution=json.dumps(g.get("meta", {}).get("difficulty", {})),
                meta=json.dumps(g.get("meta", {})),
                created_at=created,
            )
            db.add(gen)
            migrated_gens += 1
        db.commit()
        print(f"✅ Migrated {migrated_gens} generations.")

    if migrated_prompts == 0 and migrated_gens == 0:
        print("ℹ️  No existing JSON data to migrate (or already migrated).")


if __name__ == "__main__":
    init_db()
    migrate_json_data()
