# Dr. Math — Current State

**Last Updated:** 2026-05-03  
**Branch:** `main`  
**Commits:** 12 total (conventional format)  
**Environment:** Dev VM → Target VM `20.193.129.119`  
**Domain:** `drmath.trelolabs.com` (DNS **not yet** configured at Namecheap)

---

## ✅ What Works Right Now

| Component | Status | Detail |
|---|---|---|
| **Pipeline** | ✅ | Obscura → IXL + MathIsFun → LLM → 40 MCQs |
| **LLM** | ✅ | OpenAI `gpt-4o-mini` (primary). Azure authenticated but **no deployment** (404). Grok exhausted. |
| **Database** | ✅ | **SQLite** with SQLAlchemy (replaces JSON files). Tables: `prompts`, `topics`, `generations`, `evaluations`, `grounding_logs` |
| **Prompt Builder** | ✅ | Create custom teaching personas. Saved to DB. |
| **Manager Lab** | ✅ | `/lab` — rate generations 1–5⭐, see prompt leaderboard, A/B compare any two versions |
| **Generation History** | ✅ | **All versions kept** (not just latest). Every prompt experiment is preserved. |
| **Grounding** | ✅ | Every generation logs IXL skills + MathIsFun URL used |
| **Web UI** | ✅ | FastAPI + Jinja2. Home, topic pages, prompt builder, history, lab, compare |
| **Pre-commit** | ✅ | Blocks `.env`, runtime artifacts, `__pycache__`. Enforces conventional commits. |
| **Docker** | ✅ | `Dockerfile` + `docker-compose.yml` + `nginx.conf` ready |

---

## ❌ Blockers / Not Working

| Item | Why | Next Step |
|---|---|---|
| **Live deploy** | DNS A-record missing | You add `drmath.trelolabs.com → 20.193.129.119` at Namecheap, then run `scripts/deploy.sh` on server |
| **Azure OpenAI** | No model deployment exists | Create `gpt-4o-mini` deployment in Azure AI Foundry |
| **HTTPS/SSL** | Needs live server first | Run Certbot after DNS + deploy |
| **Student session UI** | Not built yet | Phase after manager workflow stabilizes |

---

## 🗄️ Database Schema (SQLite)

```
prompts              → id, name, system_prompt, question_prompt, created_at
topics               → id, slug, name, created_at
generations          → id, topic_id, prompt_id, status, total_questions,
                       difficulty_distribution, adapted_content, questions_json,
                       raw_html_path, antigravity_path, meta, created_at
evaluations          → id, generation_id, rating (1-5), notes, created_at
grounding_logs       → id, generation_id, source_type, source_url,
                       content_snippet, verification_status, created_at
```

**Key behavior:** Every `run_pipeline()` call creates a `generations` row. Re-generating the same topic appends a new row — old versions are never overwritten. This is intentional for manager A/B testing.

---

## 🧪 Manager Workflow (Current)

1. Go to **🎨 Prompts** → Create a teaching style
2. Go to **🏠 Home** → Generate topic with that prompt
3. Go to **🧪 Lab** → Rate output 1–5⭐, add notes
4. Generate **same topic again** with different prompt
5. Go to **⚖️ Compare** (`/compare?a=1&b=2`) → Side-by-side diff
6. Check **🏆 Leaderboard** → Which prompt has highest avg rating?

No passwords. Open access.

---

## 🏗️ Architecture Decisions

| ADR | Topic | Status |
|---|---|---|
| ADR-001 | Obscura headless browser | Accepted |
| ADR-002 | LLM provider strategy (OpenAI primary) | Accepted |
| ADR-003 | Pedagogy-backed prompt templates | Accepted |
| ADR-004 | FastAPI + Jinja2 SSR | Accepted |
| ADR-005 | Docker + nginx deployment | Accepted |
| ADR-006 | JSON file storage (original) | **Superseded by ADR-008** |
| ADR-007 | Adaptive engine design | Accepted |
| **ADR-008** | **SQLite for prompt experimentation** | **Accepted** |

---

## 📦 Generated Topics (DB)

| Topic | Versions | Prompts Used | Evaluations |
|---|---|---|---|
| Rational Numbers | 1 | Default | ⭐ 5.0 (1 eval) |
| Exponents | 1 | Default | ⭐ 4.0 (1 eval) |
| Integers | 1 | Default | — |
| Fractions | 1 | Default | — |
| Triangles | 1 | Default | — |
| Percentage | 1 | Default | — |

> Note: 6 topics exist as JSON files from earlier runs. DB migration captured 2 generations (Rational Numbers, Exponents). Re-generating any topic will create a fresh DB row.

---

## 🎯 Next Immediate Work

1. **Deploy to server** (waiting on you for DNS)
2. **Azure deployment** (waiting on you for AI Foundry config)
3. **Manager requests features** — e.g., export ratings CSV, bulk generate, prompt templates from research personas

---

## 🔧 One-Liner Diagnostics

```bash
# Check DB health
python3 -c "from db.database import SessionLocal; from db.models import Generation; db=SessionLocal(); print('Generations:', db.query(Generation).count())"

# Start web app locally
python3 web/main.py          # localhost:8000

# Test pipeline (costs API tokens)
python3 -m pipeline.run --topic "Integers" --prompt-id <id>

# Verify Docker Compose config
docker-compose config

# Deploy to server (run ON the server)
./scripts/deploy.sh

# Enable SSL (run ON the server, after DNS works)
./scripts/init-ssl.sh
```

---

## 📝 Change Log

| Date | Change | Commit |
|---|---|---|
| 2026-05-03 | ADR-008: SQLite for prompt experimentation | `7c80386` |
| 2026-05-03 | SQLite DB layer (models, CRUD, migration) | `6e37c2e` |
| 2026-05-03 | Pipeline DB integration + grounding logs | `e75fa70` |
| 2026-05-03 | Manager Lab: A/B compare, ratings, leaderboard | `8f98520` |
| 2026-05-03 | Production deploy scripts + auto-SSL | `38f7a2e` |
| 2026-05-03 | Pre-commit hook + setup script | `7c81e4e` |
