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

# New SQLite database
from db.database import get_db as get_db_session
from db import crud
from db.models import Generation

app = FastAPI(title="Dr. Math", description="Class VII Math Content Generator with Prompt Lab")

BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.mount("/mathwise-web", StaticFiles(directory=BASE_DIR / "static" / "mathwise-web"), name="mathwise-web")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def _slugify(name: str) -> str:
    return name.lower().replace(" ", "_")


def _unslugify(name: str) -> str:
    return name.replace("_", " ").title()


def _list_topics() -> List[Dict[str, Any]]:
    topics = []
    for f in sorted(OUTPUT_DIR.glob("*_output.json")):
        try:
            data = json.loads(f.read_text())
            topics.append({
                "slug": f.stem.replace("_output", ""),
                "name": data.get("topic", _unslugify(f.stem.replace("_output", ""))),
                "total_questions": data.get("meta", {}).get("total_questions", 0),
                "difficulty": data.get("meta", {}).get("difficulty_distribution", {}),
                "prompt_name": data.get("prompt_name", "Default"),
            })
        except Exception:
            continue
    return topics


# ------------------------------------------------------------------
# Public Pages
# ------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {
        "topics": _list_topics(),
        "prompts": list_prompts(),
    })


@app.get("/topic/{slug}", response_class=HTMLResponse)
def topic_page(request: Request, slug: str, db: Session = Depends(get_db_session)):
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

    return templates.TemplateResponse(request, "topic.html", {
        "topic": data,
        "markdown": markdown_content,
        "slug": slug,
        "versions": versions,
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
