"""Dr. Math Web UI — FastAPI backend with prompt builder & generation tracking."""
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

sys.path.insert(0, str(Path(__file__).parent.parent))
from pipeline.config import OUTPUT_DIR, DATA_DIR
from pipeline.run import run_pipeline
from pipeline.db import list_prompts, get_prompt, save_prompt, delete_prompt, list_generations

app = FastAPI(title="Dr. Math", description="Class VII Math Content Generator with Prompt Builder")

BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
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


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {
        "topics": _list_topics(),
        "prompts": list_prompts(),
    })


@app.get("/topic/{slug}", response_class=HTMLResponse)
def topic_page(request: Request, slug: str):
    json_path = OUTPUT_DIR / f"{slug}_output.json"
    md_path = DATA_DIR / f"{slug}_antigravity.md"
    if not json_path.exists():
        return templates.TemplateResponse(request, "404.html", {}, status_code=404)

    data = json.loads(json_path.read_text())
    markdown_content = md_path.read_text() if md_path.exists() else ""

    return templates.TemplateResponse(request, "topic.html", {
        "topic": data,
        "markdown": markdown_content,
        "slug": slug,
    })


# ------------------------------------------------------------------
# Prompt Builder
# ------------------------------------------------------------------

@app.get("/prompts", response_class=HTMLResponse)
def prompts_page(request: Request):
    return templates.TemplateResponse(request, "prompts.html", {
        "prompts": list_prompts(),
    })


@app.post("/prompts", response_class=RedirectResponse)
def create_prompt(
    name: str = Form(...),
    system_prompt: str = Form(...),
    question_prompt: str = Form(...),
):
    save_prompt(name, system_prompt, question_prompt)
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
