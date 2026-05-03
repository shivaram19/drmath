"""Simple JSON file database for prompts and generation tracking."""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from pipeline.config import DATA_DIR

PROMPTS_DB = DATA_DIR / "prompts_db.json"
GENERATIONS_DB = DATA_DIR / "generations_db.json"


def _load_json(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except Exception:
        return []


def _save_json(path: Path, data: List[Dict[str, Any]]):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


# ------------------------------------------------------------------
# Prompts
# ------------------------------------------------------------------

def list_prompts() -> List[Dict[str, Any]]:
    return _load_json(PROMPTS_DB)


def get_prompt(prompt_id: str) -> Optional[Dict[str, Any]]:
    for p in list_prompts():
        if p.get("id") == prompt_id:
            return p
    return None


def save_prompt(name: str, system_prompt: str, question_prompt: str) -> Dict[str, Any]:
    prompts = list_prompts()
    prompt = {
        "id": str(uuid.uuid4())[:8],
        "name": name,
        "system_prompt": system_prompt,
        "question_prompt": question_prompt,
        "created_at": datetime.utcnow().isoformat(),
    }
    prompts.append(prompt)
    _save_json(PROMPTS_DB, prompts)
    return prompt


def delete_prompt(prompt_id: str) -> bool:
    prompts = list_prompts()
    filtered = [p for p in prompts if p.get("id") != prompt_id]
    if len(filtered) == len(prompts):
        return False
    _save_json(PROMPTS_DB, filtered)
    return True


# ------------------------------------------------------------------
# Generation tracking
# ------------------------------------------------------------------

def list_generations() -> List[Dict[str, Any]]:
    return _load_json(GENERATIONS_DB)


def log_generation(topic: str, prompt_id: Optional[str], output_path: str, status: str, meta: Dict[str, Any]):
    gens = list_generations()
    gens.append({
        "id": str(uuid.uuid4())[:8],
        "topic": topic,
        "prompt_id": prompt_id,
        "output_path": output_path,
        "status": status,
        "meta": meta,
        "created_at": datetime.utcnow().isoformat(),
    })
    _save_json(GENERATIONS_DB, gens)
