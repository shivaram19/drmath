"""CRUD operations for Dr. Math database."""
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.dialects.sqlite import insert

from sqlalchemy.exc import IntegrityError

from db.models import Prompt, Topic, Generation, Evaluation, GroundingLog, QuestionReview, NursingAttempt


# ------------------------------------------------------------------
# Prompts
# ------------------------------------------------------------------

def create_prompt(db: Session, name: str, system_prompt: str, question_prompt: str, parent_id: Optional[str] = None) -> Prompt:
    """Create a prompt. If parent_id is given, it's a new version of an existing prompt.
    If name already exists without parent_id, auto-create as a new version.
    If the text is identical to the parent, returns the parent instead of a useless duplicate."""
    
    # If editing an existing prompt, check for no-op (identical text)
    if parent_id:
        parent = get_prompt(db, parent_id)
        if parent:
            if parent.system_prompt.strip() == system_prompt.strip() and parent.question_prompt.strip() == question_prompt.strip():
                # No actual change — return the existing prompt
                return parent
            # Count existing children + 1
            version = len(parent.children) + 1 if parent.children else 1
        else:
            version = 1
    else:
        # Check if a prompt with this exact name already exists (as a root)
        existing = db.query(Prompt).filter(Prompt.name == name).filter(Prompt.parent_id.is_(None)).first()
        if existing:
            # If text is identical to the latest root, return it (no-op)
            if existing.system_prompt.strip() == system_prompt.strip() and existing.question_prompt.strip() == question_prompt.strip():
                return existing
            parent_id = existing.id
            version = len(existing.children) + 1 if existing.children else 1
        else:
            version = 1
    
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
    try:
        db.commit()
        db.refresh(topic)
        return topic
    except IntegrityError:
        db.rollback()
        # Another thread created it; fetch the existing one
        topic = db.query(Topic).filter(Topic.slug == slug).first()
        if topic:
            return topic
        raise


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


# ------------------------------------------------------------------
# Question Reviews (PM Review System)
# ------------------------------------------------------------------

def create_or_update_question_review(
    db: Session,
    generation_id: int,
    question_index: int,
    thought_direction: Optional[int] = None,
    playfulness: Optional[int] = None,
    guidance_quality: Optional[int] = None,
    curiosity_building: Optional[int] = None,
    notes: Optional[str] = None,
    reviewer_name: Optional[str] = "PM",
) -> QuestionReview:
    """Create or update a review for a specific question."""
    existing = (
        db.query(QuestionReview)
        .filter(QuestionReview.generation_id == generation_id)
        .filter(QuestionReview.question_index == question_index)
        .first()
    )
    if existing:
        if thought_direction is not None:
            existing.thought_direction = thought_direction
        if playfulness is not None:
            existing.playfulness = playfulness
        if guidance_quality is not None:
            existing.guidance_quality = guidance_quality
        if curiosity_building is not None:
            existing.curiosity_building = curiosity_building
        if notes is not None:
            existing.notes = notes
        if reviewer_name is not None:
            existing.reviewer_name = reviewer_name
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing

    review = QuestionReview(
        generation_id=generation_id,
        question_index=question_index,
        thought_direction=thought_direction,
        playfulness=playfulness,
        guidance_quality=guidance_quality,
        curiosity_building=curiosity_building,
        notes=notes,
        reviewer_name=reviewer_name,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_question_review(db: Session, generation_id: int, question_index: int) -> Optional[QuestionReview]:
    return (
        db.query(QuestionReview)
        .filter(QuestionReview.generation_id == generation_id)
        .filter(QuestionReview.question_index == question_index)
        .first()
    )


def list_question_reviews(db: Session, generation_id: Optional[int] = None) -> List[QuestionReview]:
    q = db.query(QuestionReview)
    if generation_id:
        q = q.filter(QuestionReview.generation_id == generation_id)
    return q.order_by(QuestionReview.question_index.asc()).all()


# ------------------------------------------------------------------
# Nursing attempts (local-first sync)
# ------------------------------------------------------------------


def record_nursing_attempts(db: Session, attempts: List[Dict[str, Any]]) -> int:
    """Persist nursing attempts, ignoring duplicates by client_attempt_id.

    Returns the number of newly inserted rows.
    """
    inserted = 0
    for attempt in attempts:
        stmt = (
            insert(NursingAttempt)
            .values(**attempt)
            .on_conflict_do_nothing(index_elements=["client_attempt_id"])
        )
        result = db.execute(stmt)
        inserted += result.rowcount
    db.commit()
    return inserted


def list_nursing_attempts(
    db: Session,
    session_id: Optional[str] = None,
    question_id: Optional[int] = None,
    limit: Optional[int] = None,
) -> List[NursingAttempt]:
    q = db.query(NursingAttempt).order_by(NursingAttempt.answered_at.desc())
    if session_id:
        q = q.filter(NursingAttempt.session_id == session_id)
    if question_id is not None:
        q = q.filter(NursingAttempt.question_id == question_id)
    if limit:
        q = q.limit(limit)
    return q.all()


def count_nursing_attempts(db: Session, session_id: Optional[str] = None) -> int:
    q = db.query(NursingAttempt)
    if session_id:
        q = q.filter(NursingAttempt.session_id == session_id)
    return q.count()


# ------------------------------------------------------------------
# Question Reviews (PM Review System)
# ------------------------------------------------------------------


def get_question_review_stats(db: Session, generation_id: int) -> dict:
    """Return aggregate stats for all reviews on a generation."""
    reviews = list_question_reviews(db, generation_id)
    if not reviews:
        return {"total_reviewed": 0, "avg_thought_direction": None, "avg_playfulness": None}
    
    def avg(field):
        vals = [getattr(r, field) for r in reviews if getattr(r, field) is not None]
        return round(sum(vals) / len(vals), 2) if vals else None
    
    return {
        "total_reviewed": len(reviews),
        "avg_thought_direction": avg("thought_direction"),
        "avg_playfulness": avg("playfulness"),
        "avg_guidance_quality": avg("guidance_quality"),
        "avg_curiosity_building": avg("curiosity_building"),
    }
