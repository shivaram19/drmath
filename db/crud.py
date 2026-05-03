"""CRUD operations for Dr. Math database."""
import json
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from db.models import Prompt, Topic, Generation, Evaluation, GroundingLog


# ------------------------------------------------------------------
# Prompts
# ------------------------------------------------------------------

def create_prompt(db: Session, name: str, system_prompt: str, question_prompt: str, parent_id: Optional[str] = None) -> Prompt:
    """Create a prompt. If parent_id is given, it's a new version of an existing prompt.
    If name already exists without parent_id, auto-create as a new version."""
    
    # Determine version number
    version = 1
    if parent_id:
        parent = get_prompt(db, parent_id)
        if parent:
            # Count existing children + 1
            version = len(parent.children) + 1 if parent.children else 1
    else:
        # Check if a prompt with this exact name already exists (as a root)
        existing = db.query(Prompt).filter(Prompt.name == name).filter(Prompt.parent_id.is_(None)).first()
        if existing:
            parent_id = existing.id
            version = len(existing.children) + 1 if existing.children else 1
    
    # Auto-name with timestamp if it's a version
    display_name = name
    if parent_id:
        display_name = f"{name} (v{version} — {datetime.utcnow().strftime('%b %d, %H:%M')})"
    
    prompt = Prompt(
        id=str(uuid.uuid4())[:8],
        name=display_name,
        system_prompt=system_prompt,
        question_prompt=question_prompt,
        parent_id=parent_id,
        version=version,
    )
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    return prompt


def get_prompt(db: Session, prompt_id: str) -> Optional[Prompt]:
    return db.query(Prompt).filter(Prompt.id == prompt_id).first()


def list_prompts(db: Session) -> List[Prompt]:
    return db.query(Prompt).order_by(Prompt.created_at.desc()).all()


def list_prompt_versions(db: Session, parent_id: str) -> List[Prompt]:
    """Return all versions (children) of a given prompt, oldest first."""
    return (
        db.query(Prompt)
        .filter(Prompt.parent_id == parent_id)
        .order_by(Prompt.version.asc())
        .all()
    )


def get_prompt_family(db: Session, prompt_id: str) -> List[Prompt]:
    """Return a prompt and all its versions (parent + children)."""
    prompt = get_prompt(db, prompt_id)
    if not prompt:
        return []
    
    # Find the root parent
    root = prompt
    while root.parent_id:
        root = get_prompt(db, root.parent_id)
        if not root:
            break
    
    # Get root + all descendants
    family = [root]
    family.extend(list_prompt_versions(db, root.id))
    return family


def delete_prompt(db: Session, prompt_id: str) -> bool:
    p = get_prompt(db, prompt_id)
    if not p:
        return False
    db.delete(p)
    db.commit()
    return True


# ------------------------------------------------------------------
# Topics
# ------------------------------------------------------------------

def get_or_create_topic(db: Session, slug: str, name: str) -> Topic:
    topic = db.query(Topic).filter(Topic.slug == slug).first()
    if topic:
        return topic
    topic = Topic(slug=slug, name=name)
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


def get_topic_by_slug(db: Session, slug: str) -> Optional[Topic]:
    return db.query(Topic).filter(Topic.slug == slug).first()


def list_topics(db: Session) -> List[Topic]:
    return db.query(Topic).order_by(Topic.name).all()


# ------------------------------------------------------------------
# Generations
# ------------------------------------------------------------------

def create_generation(
    db: Session,
    topic_id: int,
    prompt_id: Optional[str] = None,
    status: str = "pending",
) -> Generation:
    gen = Generation(topic_id=topic_id, prompt_id=prompt_id, status=status)
    db.add(gen)
    db.commit()
    db.refresh(gen)
    return gen


def get_generation(db: Session, generation_id: int) -> Optional[Generation]:
    return db.query(Generation).filter(Generation.id == generation_id).first()


def update_generation(
    db: Session,
    generation_id: int,
    status: Optional[str] = None,
    output_path: Optional[str] = None,
    total_questions: Optional[int] = None,
    difficulty_distribution: Optional[dict] = None,
    adapted_content: Optional[str] = None,
    questions_json: Optional[list] = None,
    raw_html_path: Optional[str] = None,
    antigravity_path: Optional[str] = None,
    meta: Optional[dict] = None,
    scraped_at: Optional[datetime] = None,
    adapted_at: Optional[datetime] = None,
    questions_generated_at: Optional[datetime] = None,
    saved_at: Optional[datetime] = None,
) -> Optional[Generation]:
    gen = get_generation(db, generation_id)
    if not gen:
        return None
    if status is not None:
        gen.status = status
    if output_path is not None:
        gen.output_path = output_path
    if total_questions is not None:
        gen.total_questions = total_questions
    if difficulty_distribution is not None:
        gen.difficulty_distribution = json.dumps(difficulty_distribution)
    if adapted_content is not None:
        gen.adapted_content = adapted_content
    if questions_json is not None:
        gen.questions_json = json.dumps(questions_json)
    if raw_html_path is not None:
        gen.raw_html_path = raw_html_path
    if antigravity_path is not None:
        gen.antigravity_path = antigravity_path
    if meta is not None:
        gen.meta = json.dumps(meta)
    if scraped_at is not None:
        gen.scraped_at = scraped_at
    if adapted_at is not None:
        gen.adapted_at = adapted_at
    if questions_generated_at is not None:
        gen.questions_generated_at = questions_generated_at
    if saved_at is not None:
        gen.saved_at = saved_at
    db.commit()
    db.refresh(gen)
    return gen


def list_generations(db: Session, topic_id: Optional[int] = None, prompt_id: Optional[str] = None) -> List[Generation]:
    q = db.query(Generation).order_by(Generation.created_at.desc())
    if topic_id:
        q = q.filter(Generation.topic_id == topic_id)
    if prompt_id:
        q = q.filter(Generation.prompt_id == prompt_id)
    return q.all()


def get_topic_generations(db: Session, topic_slug: str) -> List[Generation]:
    topic = get_topic_by_slug(db, topic_slug)
    if not topic:
        return []
    return db.query(Generation).filter(Generation.topic_id == topic.id).order_by(Generation.created_at.desc()).all()


# ------------------------------------------------------------------
# Evaluations
# ------------------------------------------------------------------

def create_evaluation(
    db: Session,
    generation_id: int,
    rating: int,
    notes: Optional[str] = None,
    evaluated_by: Optional[str] = None,
) -> Evaluation:
    ev = Evaluation(
        generation_id=generation_id,
        rating=rating,
        notes=notes,
        evaluated_by=evaluated_by,
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev


def get_evaluation(db: Session, evaluation_id: int) -> Optional[Evaluation]:
    return db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()


def list_evaluations(db: Session, generation_id: Optional[int] = None) -> List[Evaluation]:
    q = db.query(Evaluation)
    if generation_id:
        q = q.filter(Evaluation.generation_id == generation_id)
    return q.order_by(Evaluation.created_at.desc()).all()


def delete_evaluation(db: Session, evaluation_id: int) -> bool:
    ev = get_evaluation(db, evaluation_id)
    if not ev:
        return False
    db.delete(ev)
    db.commit()
    return True


# ------------------------------------------------------------------
# Grounding Logs
# ------------------------------------------------------------------

def create_grounding_log(
    db: Session,
    generation_id: int,
    source_type: str,
    source_url: Optional[str] = None,
    content_snippet: Optional[str] = None,
    verification_status: str = "verified",
) -> GroundingLog:
    log = GroundingLog(
        generation_id=generation_id,
        source_type=source_type,
        source_url=source_url,
        content_snippet=content_snippet,
        verification_status=verification_status,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def list_grounding_logs(db: Session, generation_id: Optional[int] = None) -> List[GroundingLog]:
    q = db.query(GroundingLog)
    if generation_id:
        q = q.filter(GroundingLog.generation_id == generation_id)
    return q.order_by(GroundingLog.created_at.desc()).all()


# ------------------------------------------------------------------
# Analytics / Leaderboard
# ------------------------------------------------------------------

def get_prompt_leaderboard(db: Session) -> List[dict]:
    """Return average rating per prompt, ranked best first."""
    results = (
        db.query(
            Prompt.id,
            Prompt.name,
            func.avg(Evaluation.rating).label("avg_rating"),
            func.count(Evaluation.id).label("eval_count"),
        )
        .join(Generation, Generation.prompt_id == Prompt.id)
        .join(Evaluation, Evaluation.generation_id == Generation.id)
        .group_by(Prompt.id)
        .order_by(func.avg(Evaluation.rating).desc())
        .all()
    )
    return [
        {
            "prompt_id": r.id,
            "prompt_name": r.name,
            "avg_rating": round(r.avg_rating, 2) if r.avg_rating else None,
            "eval_count": r.eval_count,
        }
        for r in results
    ]


def get_generation_with_details(db: Session, generation_id: int) -> Optional[Generation]:
    return (
        db.query(Generation)
        .filter(Generation.id == generation_id)
        .first()
    )
