"""Dr. Math Web UI — FastAPI backend with prompt builder, generation tracking, and manager lab."""
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).parent.parent))
from pipeline.config import OUTPUT_DIR, DATA_DIR
from pipeline.run import run_pipeline
from pipeline.db import list_prompts, get_prompt, save_prompt, delete_prompt, list_generations, _session
from db.crud import create_or_update_question_review, get_question_review, list_question_reviews, get_question_review_stats

# New SQLite database
from db.database import get_db as get_db_session
from db import crud
from db.models import Generation

app = FastAPI(title="Dr. Math", description="Class VII Math Content Generator with Prompt Lab")

BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.mount("/mathwise-web", StaticFiles(directory=BASE_DIR / "static" / "mathwise-web", html=True), name="mathwise-web")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def _slugify(name: str) -> str:
    return name.lower().replace(" ", "_")


def _unslugify(name: str) -> str:
    return name.replace("_", " ").title()


def _list_topics() -> List[Dict[str, Any]]:
    """List all topics, grouping multi-prompt versions under the same topic."""
    topic_map = {}
    for f in sorted(OUTPUT_DIR.glob("*_output.json")):
        if f.name.startswith("batch_report") or f.name.startswith("multi_prompt_report"):
            continue
        try:
            data = json.loads(f.read_text())
            # Parse filename: {slug}_{prompt}_output.json or {slug}_output.json
            parts = f.stem.replace("_output", "").split("_")
            
            # Detect if it's a multi-prompt file
            prompt_slug = None
            base_slug = "_".join(parts)
            if len(parts) >= 2 and parts[-1] in ("default", "storyteller", "visual", "zpd"):
                prompt_slug = parts[-1]
                base_slug = "_".join(parts[:-1])
            
            topic_name = data.get("topic", _unslugify(base_slug))
            prompt_name = data.get("prompt_name", "Default")
            
            if base_slug not in topic_map:
                topic_map[base_slug] = {
                    "slug": base_slug,
                    "name": topic_name,
                    "total_questions": data.get("meta", {}).get("total_questions", 0),
                    "difficulty": data.get("meta", {}).get("difficulty_distribution", {}),
                    "prompt_name": prompt_name,
                    "versions": [],
                }
            
            topic_map[base_slug]["versions"].append({
                "file": f.name,
                "prompt_slug": prompt_slug or "default",
                "prompt_name": prompt_name,
                "total_questions": data.get("meta", {}).get("total_questions", 0),
            })
        except Exception:
            continue
    
    # Return topics with version count
    result = []
    for slug, data in sorted(topic_map.items()):
        result.append({
            "slug": slug,
            "name": data["name"],
            "total_questions": data["total_questions"],
            "difficulty": data["difficulty"],
            "prompt_name": data["prompt_name"],
            "version_count": len(data["versions"]),
            "versions": data["versions"],
        })
    return result


# ------------------------------------------------------------------
# Public Pages
# ------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Marketing homepage for students, parents, and educators."""
    return templates.TemplateResponse(request, "index.html", {
        "topics": _list_topics(),
        "prompts": list_prompts(),
    })


@app.get("/manager", response_class=HTMLResponse)
def manager_page(request: Request):
    """Internal manager dashboard for content generation and review."""
    return templates.TemplateResponse(request, "manager.html", {
        "topics": _list_topics(),
        "prompts": list_prompts(),
    })


@app.get("/topic/{slug}", response_class=HTMLResponse)
def topic_page(request: Request, slug: str, prompt: Optional[str] = None, db: Session = Depends(get_db_session)):
    # Determine which file to load
    if prompt and prompt in ("default", "storyteller", "visual", "zpd"):
        json_path = OUTPUT_DIR / f"{slug}_{prompt}_output.json"
        md_path = DATA_DIR / f"{slug}_{prompt}_antigravity.md"
        if not json_path.exists():
            # Fallback to default
            json_path = OUTPUT_DIR / f"{slug}_output.json"
            md_path = DATA_DIR / f"{slug}_antigravity.md"
    else:
        json_path = OUTPUT_DIR / f"{slug}_output.json"
        md_path = DATA_DIR / f"{slug}_antigravity.md"

    # Load from file (fallback) or DB
    if json_path.exists():
        data = json.loads(json_path.read_text())
    else:
        # Try DB
        topic_obj = crud.get_topic_by_slug(db, slug)
        if not topic_obj:
            return templates.TemplateResponse(request, "404.html", {}, status_code=404)
        latest_gen = (
            db.query(Generation)
            .filter(Generation.topic_id == topic_obj.id)
            .order_by(Generation.created_at.desc())
            .first()
        )
        if not latest_gen or not latest_gen.questions_json:
            return templates.TemplateResponse(request, "404.html", {}, status_code=404)
        data = {
            "topic": topic_obj.name,
            "questions": json.loads(latest_gen.questions_json),
            "meta": {"total_questions": latest_gen.total_questions, "difficulty_distribution": latest_gen.difficulty_dict},
            "source_ixl_skills": [],
        }

    markdown_content = md_path.read_text() if md_path.exists() else (latest_gen.adapted_content if 'latest_gen' in dir() else "")

    # Get all generation versions for this topic
    topic_obj = crud.get_topic_by_slug(db, slug)
    versions = []
    if topic_obj:
        versions = [
            {
                "id": g.id,
                "created_at": g.created_at.isoformat() if g.created_at else "",
                "prompt_name": g.prompt.name if g.prompt else "Default",
                "total_questions": g.total_questions,
                "avg_rating": round(g.avg_rating, 1) if g.avg_rating else None,
                "status": g.status,
            }
            for g in topic_obj.generations
        ]

    # Discover available prompt dimensions from output files
    available_dimensions = []
    for dim in [("default", "Default"), ("storyteller", "Cultural Storyteller"), ("visual", "Visual-First"), ("zpd", "ZPD Adaptive")]:
        dim_slug, dim_name = dim
        dim_path = OUTPUT_DIR / f"{slug}_{dim_slug}_output.json"
        if dim_path.exists():
            available_dimensions.append({"slug": dim_slug, "name": dim_name})
    # Also check for default without suffix
    if (OUTPUT_DIR / f"{slug}_output.json").exists():
        if not any(d["slug"] == "default" for d in available_dimensions):
            available_dimensions.insert(0, {"slug": "default", "name": "Default"})

    return templates.TemplateResponse(request, "topic.html", {
        "topic": data,
        "markdown": markdown_content,
        "slug": slug,
        "versions": versions,
        "current_prompt": prompt or "default",
        "available_dimensions": available_dimensions,
    })


# ------------------------------------------------------------------
# Prompt Builder
# ------------------------------------------------------------------

@app.get("/prompts", response_class=HTMLResponse)
def prompts_page(request: Request, db: Session = Depends(get_db_session)):
    prompts = crud.list_prompts(db)
    # Group by family (root prompts and their versions)
    families = []
    seen = set()
    for p in prompts:
        if p.id in seen:
            continue
        family = crud.get_prompt_family(db, p.id)
        for f in family:
            seen.add(f.id)
        families.append({
            "root": family[0],
            "versions": family[1:],
            "all": family,
        })
    return templates.TemplateResponse(request, "prompts.html", {
        "families": families,
    })


@app.post("/prompts", response_class=RedirectResponse)
def create_prompt(
    name: str = Form(...),
    system_prompt: str = Form(...),
    question_prompt: str = Form(...),
    parent_id: Optional[str] = Form(None),
):
    save_prompt(name, system_prompt, question_prompt, parent_id=parent_id or None)
    return RedirectResponse(url="/prompts", status_code=303)


@app.post("/prompts/{prompt_id}/delete", response_class=RedirectResponse)
def remove_prompt(prompt_id: str):
    delete_prompt(prompt_id)
    return RedirectResponse(url="/prompts", status_code=303)


# ------------------------------------------------------------------
# Generation Tracking
# ------------------------------------------------------------------

@app.get("/history", response_class=HTMLResponse)
def history_page(request: Request):
    return templates.TemplateResponse(request, "history.html", {
        "generations": list_generations(),
        "prompts": {p["id"]: p for p in list_prompts()},
    })


# ------------------------------------------------------------------
# Generate
# ------------------------------------------------------------------

@app.post("/generate", response_class=RedirectResponse)
def web_generate(topic: str = Form(...), prompt_id: Optional[str] = Form(None)):
    slug = _slugify(topic)
    output_path = OUTPUT_DIR / f"{slug}_output.json"
    if not output_path.exists():
        try:
            run_pipeline(topic, str(output_path), prompt_id=prompt_id or None)
        except Exception:
            pass
    return RedirectResponse(url=f"/topic/{slug}", status_code=303)


# ------------------------------------------------------------------
# Manager Lab (Prompt Experimentation)
# ------------------------------------------------------------------

@app.get("/lab", response_class=HTMLResponse)
def lab_page(request: Request, db: Session = Depends(get_db_session)):
    """Manager lab: compare prompts, rate generations, see leaderboard."""
    generations = crud.list_generations(db)
    prompts = crud.list_prompts(db)
    leaderboard = crud.get_prompt_leaderboard(db)

    # Enrich generations with ratings
    gen_data = []
    for g in generations:
        gen_data.append({
            "id": g.id,
            "topic": g.topic.name if g.topic else "",
            "slug": g.topic.slug if g.topic else "",
            "prompt_name": g.prompt.name if g.prompt else "Default",
            "prompt_id": g.prompt_id,
            "status": g.status,
            "total_questions": g.total_questions,
            "difficulty": g.difficulty_dict,
            "avg_rating": round(g.avg_rating, 1) if g.avg_rating else None,
            "eval_count": len(g.evaluations),
            "created_at": g.created_at.isoformat() if g.created_at else "",
        })

    return templates.TemplateResponse(request, "lab.html", {
        "generations": gen_data,
        "prompts": prompts,
        "leaderboard": leaderboard,
    })


@app.get("/compare", response_class=HTMLResponse)
def compare_page(request: Request, a: int, b: int, db: Session = Depends(get_db_session)):
    """Side-by-side comparison of two generations."""
    gen_a = crud.get_generation_with_details(db, a)
    gen_b = crud.get_generation_with_details(db, b)
    if not gen_a or not gen_b:
        return templates.TemplateResponse(request, "404.html", {}, status_code=404)

    def _enrich(g):
        return {
            "id": g.id,
            "topic": g.topic.name if g.topic else "",
            "prompt_name": g.prompt.name if g.prompt else "Default",
            "status": g.status,
            "total_questions": g.total_questions,
            "difficulty": g.difficulty_dict,
            "avg_rating": round(g.avg_rating, 1) if g.avg_rating else None,
            "eval_count": len(g.evaluations),
            "created_at": g.created_at.isoformat() if g.created_at else "",
            "adapted_content": g.adapted_content or "",
            "questions": json.loads(g.questions_json) if g.questions_json else [],
            "grounding": [
                {"source_type": gl.source_type, "source_url": gl.source_url}
                for gl in g.grounding_logs
            ],
        }

    return templates.TemplateResponse(request, "compare.html", {
        "gen_a": _enrich(gen_a),
        "gen_b": _enrich(gen_b),
    })


# ------------------------------------------------------------------
# API
# ------------------------------------------------------------------

@app.get("/api/topics")
def api_list_topics() -> List[Dict[str, Any]]:
    return _list_topics()


@app.get("/api/topic/{slug}")
def api_get_topic(slug: str) -> Dict[str, Any]:
    json_path = OUTPUT_DIR / f"{slug}_output.json"
    if not json_path.exists():
        return JSONResponse({"error": "Not found"}, status_code=404)
    return json.loads(json_path.read_text())


@app.get("/api/prompts")
def api_list_prompts() -> List[Dict[str, Any]]:
    return list_prompts()


@app.post("/api/prompts")
def api_create_prompt(data: dict) -> Dict[str, Any]:
    p = save_prompt(data["name"], data["system_prompt"], data["question_prompt"])
    return p


@app.get("/api/history")
def api_list_history() -> List[Dict[str, Any]]:
    return list_generations()


@app.post("/api/generate")
def api_generate(topic: str = Form(...), prompt_id: Optional[str] = Form(None)):
    slug = _slugify(topic)
    output_path = OUTPUT_DIR / f"{slug}_output.json"

    if output_path.exists():
        return {"status": "exists", "slug": slug, "redirect": f"/topic/{slug}"}

    try:
        run_pipeline(topic, str(output_path), prompt_id=prompt_id or None)
        return {"status": "generated", "slug": slug, "redirect": f"/topic/{slug}"}
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


# ------------------------------------------------------------------
# Evaluations API
# ------------------------------------------------------------------

@app.post("/api/evaluations")
def api_create_evaluation(
    generation_id: int = Form(...),
    rating: int = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db_session),
):
    if not 1 <= rating <= 5:
        return JSONResponse({"error": "Rating must be 1-5"}, status_code=400)
    ev = crud.create_evaluation(db, generation_id, rating, notes)
    return {
        "id": ev.id,
        "generation_id": ev.generation_id,
        "rating": ev.rating,
        "notes": ev.notes,
        "created_at": ev.created_at.isoformat() if ev.created_at else None,
    }


@app.get("/api/evaluations")
def api_list_evaluations(generation_id: Optional[int] = None, db: Session = Depends(get_db_session)):
    evaluations = crud.list_evaluations(db, generation_id=generation_id)
    return [
        {
            "id": ev.id,
            "generation_id": ev.generation_id,
            "rating": ev.rating,
            "notes": ev.notes,
            "created_at": ev.created_at.isoformat() if ev.created_at else None,
        }
        for ev in evaluations
    ]


# ------------------------------------------------------------------
# Question Reviews (PM Review System)
# ------------------------------------------------------------------

@app.get("/review/{slug}", response_class=HTMLResponse)
def review_page(request: Request, slug: str, prompt: Optional[str] = None, db: Session = Depends(get_db_session)):
    """PM review page: see all questions for a topic and rate them."""
    topic_obj = crud.get_topic_by_slug(db, slug)
    if not topic_obj:
        return templates.TemplateResponse(request, "404.html", {}, status_code=404)
    
    # Load questions from the appropriate output file
    if prompt and prompt in ("default", "storyteller", "visual", "zpd"):
        json_path = OUTPUT_DIR / f"{slug}_{prompt}_output.json"
        if not json_path.exists():
            json_path = OUTPUT_DIR / f"{slug}_output.json"
    else:
        json_path = OUTPUT_DIR / f"{slug}_output.json"
    
    if json_path.exists():
        data = json.loads(json_path.read_text())
        questions = data.get("questions", [])
        prompt_name = data.get("prompt_name", "Default")
    else:
        # Fallback to DB
        latest_gen = (
            db.query(Generation)
            .filter(Generation.topic_id == topic_obj.id)
            .order_by(Generation.created_at.desc())
            .first()
        )
        if not latest_gen or not latest_gen.questions_json:
            return templates.TemplateResponse(request, "404.html", {"message": "No questions generated yet"}, status_code=404)
        questions = json.loads(latest_gen.questions_json)
        prompt_name = latest_gen.prompt.name if latest_gen.prompt else "Default"
    
    # Get generation ID for review storage (use latest DB generation for this topic)
    latest_gen = (
        db.query(Generation)
        .filter(Generation.topic_id == topic_obj.id)
        .order_by(Generation.created_at.desc())
        .first()
    )
    generation_id = latest_gen.id if latest_gen else 0
    
    # For now, reviews are tied to the latest generation regardless of prompt dimension
    # In future, we may want per-prompt-dimension review tables
    reviews = {r.question_index: r for r in (latest_gen.question_reviews if latest_gen else [])}
    stats = get_question_review_stats(db, generation_id) if generation_id else {"total_reviewed": 0}
    
    # Discover available dimensions
    available_dimensions = []
    for dim in [("default", "Default"), ("storyteller", "Cultural Storyteller"), ("visual", "Visual-First"), ("zpd", "ZPD Adaptive")]:
        dim_slug, dim_name = dim
        dim_path = OUTPUT_DIR / f"{slug}_{dim_slug}_output.json"
        if dim_path.exists():
            available_dimensions.append({"slug": dim_slug, "name": dim_name})
    if (OUTPUT_DIR / f"{slug}_output.json").exists():
        if not any(d["slug"] == "default" for d in available_dimensions):
            available_dimensions.insert(0, {"slug": "default", "name": "Default"})
    
    # Enrich questions with review data
    enriched = []
    for i, q in enumerate(questions):
        r = reviews.get(i)
        enriched.append({
            "index": i,
            "question": q.get("question", ""),
            "options": q.get("options", []),
            "correct_answer": q.get("correct_answer", ""),
            "explanation": q.get("explanation", ""),
            "difficulty": q.get("difficulty", 0),
            "review": {
                "thought_direction": r.thought_direction if r else None,
                "playfulness": r.playfulness if r else None,
                "guidance_quality": r.guidance_quality if r else None,
                "curiosity_building": r.curiosity_building if r else None,
                "notes": r.notes if r else None,
            } if r else None,
        })
    
    return templates.TemplateResponse(request, "review.html", {
        "topic": topic_obj,
        "slug": slug,
        "generation_id": generation_id,
        "questions": enriched,
        "stats": stats,
        "total_questions": len(questions),
        "current_prompt": prompt or "default",
        "prompt_name": prompt_name,
        "available_dimensions": available_dimensions,
    })


@app.post("/api/question-reviews")
def api_create_question_review(
    generation_id: int = Form(...),
    question_index: int = Form(...),
    thought_direction: Optional[int] = Form(None),
    playfulness: Optional[int] = Form(None),
    guidance_quality: Optional[int] = Form(None),
    curiosity_building: Optional[int] = Form(None),
    notes: Optional[str] = Form(None),
    reviewer_name: Optional[str] = Form("PM"),
    db: Session = Depends(get_db_session),
):
    """Submit or update a review for a specific question."""
    # Validate ratings are 1-5
    for field, val in [
        ("thought_direction", thought_direction),
        ("playfulness", playfulness),
        ("guidance_quality", guidance_quality),
        ("curiosity_building", curiosity_building),
    ]:
        if val is not None and not (1 <= val <= 5):
            return JSONResponse({"error": f"{field} must be 1-5"}, status_code=400)
    
    review = create_or_update_question_review(
        db, generation_id, question_index,
        thought_direction=thought_direction,
        playfulness=playfulness,
        guidance_quality=guidance_quality,
        curiosity_building=curiosity_building,
        notes=notes,
        reviewer_name=reviewer_name,
    )
    return {
        "id": review.id,
        "generation_id": review.generation_id,
        "question_index": review.question_index,
        "thought_direction": review.thought_direction,
        "playfulness": review.playfulness,
        "guidance_quality": review.guidance_quality,
        "curiosity_building": review.curiosity_building,
        "notes": review.notes,
        "reviewer_name": review.reviewer_name,
        "created_at": review.created_at.isoformat() if review.created_at else None,
        "updated_at": review.updated_at.isoformat() if review.updated_at else None,
    }


@app.get("/api/question-reviews")
def api_list_question_reviews(generation_id: int, db: Session = Depends(get_db_session)):
    """List all reviews for a generation."""
    reviews = list_question_reviews(db, generation_id=generation_id)
    return [
        {
            "id": r.id,
            "question_index": r.question_index,
            "thought_direction": r.thought_direction,
            "playfulness": r.playfulness,
            "guidance_quality": r.guidance_quality,
            "curiosity_building": r.curiosity_building,
            "notes": r.notes,
            "reviewer_name": r.reviewer_name,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reviews
    ]


@app.get("/api/question-reviews/stats/{generation_id}")
def api_question_review_stats(generation_id: int, db: Session = Depends(get_db_session)):
    """Get aggregate review stats for a generation."""
    return get_question_review_stats(db, generation_id)


@app.get("/instructions", response_class=HTMLResponse)
def instructions_page(request: Request):
    """PM Instructions page — how to review content and use the system."""
    return templates.TemplateResponse(request, "instructions.html", {})


@app.get("/status", response_class=HTMLResponse)
def status_page(request: Request):
    """Generation status dashboard — real-time view of all topic × dimension combinations."""
    from datetime import datetime

    status_file = OUTPUT_DIR / "generation_status.json"
    status_data = {"jobs": []}
    if status_file.exists():
        try:
            status_data = json.loads(status_file.read_text())
        except Exception:
            pass

    # Build matrix
    topics = sorted({j["topic"] for j in status_data.get("jobs", [])})
    prompts = ["default", "storyteller", "visual", "zpd"]
    prompt_icons = {"default": "🧮", "storyteller": "📖", "visual": "👁️", "zpd": "🎯"}

    matrix = []
    for topic in topics:
        row = {"topic": topic, "cells": []}
        for pk in prompts:
            job = next((j for j in status_data.get("jobs", []) if j["topic"] == topic and j["prompt_key"] == pk), None)
            if job:
                row["cells"].append({"status": job.get("status", "pending"), "message": job.get("message", "")})
            else:
                row["cells"].append({"status": "pending", "message": "Not queued"})
        matrix.append(row)

    # Summary counts
    jobs = status_data.get("jobs", [])
    total = len(jobs)
    success = len([j for j in jobs if j.get("status") == "success"])
    skipped = len([j for j in jobs if j.get("status") == "skipped"])
    errors = len([j for j in jobs if j.get("status") == "error"])
    pending = total - success - skipped - errors

    return templates.TemplateResponse(request, "status.html", {
        "matrix": matrix,
        "total": total,
        "success": success,
        "skipped": skipped,
        "errors": errors,
        "pending": pending,
        "now": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
    })


# ------------------------------------------------------------------
# APK Download
# ------------------------------------------------------------------

APK_PATH = Path(__file__).parent / "static" / "mathwise.apk"

@app.get("/mathwise.apk")
def download_apk():
    """Download the latest MathWise Android APK."""
    if not APK_PATH.exists():
        return JSONResponse(
            {"error": "APK not built yet. Please check back in a few minutes."},
            status_code=404
        )
    return FileResponse(
        path=str(APK_PATH),
        media_type="application/vnd.android.package-archive",
        filename="mathwise.apk"
    )


@app.get("/api/leaderboard")
def api_leaderboard(db: Session = Depends(get_db_session)):
    return crud.get_prompt_leaderboard(db)


@app.get("/api/generation/{generation_id}")
def api_get_generation(generation_id: int, db: Session = Depends(get_db_session)):
    g = crud.get_generation_with_details(db, generation_id)
    if not g:
        return JSONResponse({"error": "Not found"}, status_code=404)
    return {
        "id": g.id,
        "topic": g.topic.name if g.topic else None,
        "slug": g.topic.slug if g.topic else None,
        "prompt_id": g.prompt_id,
        "prompt_name": g.prompt.name if g.prompt else "Default",
        "status": g.status,
        "total_questions": g.total_questions,
        "difficulty": g.difficulty_dict,
        "avg_rating": round(g.avg_rating, 1) if g.avg_rating else None,
        "evaluations": [
            {"id": e.id, "rating": e.rating, "notes": e.notes}
            for e in g.evaluations
        ],
        "grounding_logs": [
            {"source_type": gl.source_type, "source_url": gl.source_url, "verification_status": gl.verification_status}
            for gl in g.grounding_logs
        ],
        "timeline": g.timeline,
        "created_at": g.created_at.isoformat() if g.created_at else None,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
