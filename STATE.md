# Dr. Math — Current State

**Last Updated:** 2026-06-28  
**Branch:** `main`  
**Commits:** 35+ total (conventional format)  
**Environment:** Production VM `20.193.129.119`  
**Domain:** `drmath.trelolabs.com` ✅ Live with HTTPS

---

## 🌐 Live URLs

| URL | Status |
|---|---|
| https://drmath.trelolabs.com | ✅ Live |
| https://drmath.trelolabs.com/lab | ✅ Manager Lab |
| https://drmath.trelolabs.com/api/topics | ✅ API |
| **https://drmath.trelolabs.com/nursing/** | ✅ **Phase 10.1 PWA landing quiz** |
| https://drmath.trelolabs.com/api/nursing/status | ✅ Nursing API health |
| https://drmath.trelolabs.com/nursing/privacy | ✅ DPDPA privacy notice |
| https://drmath.trelolabs.com/mathwise.apk | ✅ Flutter APK download |

---

## ✅ What Works Right Now

| Component | Status | Detail |
|---|---|---|
| **Pipeline** | ✅ | Obscura → IXL + MathIsFun → LLM → 40 MCQs |
| **LLM** | ✅ | OpenAI `gpt-4o-mini` (primary). Azure authenticated but **no deployment** (404). Grok exhausted. |
| **Database** | ✅ | **SQLite** with SQLAlchemy (replaces JSON files). Tables: `prompts`, `topics`, `generations`, `evaluations`, `grounding_logs` |
| **Prompt Builder** | ✅ | Create custom teaching personas. **Auto-versioning** — edits create timestamped sub-versions. Full text expand/collapse. |
| **Manager Lab** | ✅ | `/lab` — rate generations 1–5⭐, see prompt leaderboard, A/B compare, view per-generation pipeline timeline |
| **Generation History** | ✅ | **All versions kept** (not just latest). Every generation records a 4-step timeline: scrape → adapt → generate → save. |
| **Grounding** | ✅ | Every generation logs IXL skills + MathIsFun URL used |
| **Web UI** | ✅ | FastAPI + Jinja2. Home, topic pages, prompt builder, history, lab, compare |
| **Nursing PWA** | ✅ | `/nursing/` daily 5-question quiz, offline fallback, share-to-WhatsApp, installable manifest + service worker |
| **Privacy & Consent** | ✅ | DPDPA notice at `/nursing/privacy`, consent banner, conditional share, withdrawal link |
| **Pre-commit** | ✅ | Blocks `.env`, runtime artifacts, `__pycache__`. Enforces conventional commits. |
| **Docker** | ✅ | `Dockerfile` + `docker-compose.yml` + nginx configs ready |
| **Deploy automation** | ✅ | `scripts/deploy.sh` installs nginx config, selects SSL, copies static assets, reloads nginx, health-checks endpoints |

---

## ❌ Blockers / Not Working

| Item | Why | Next Step |
|---|---|---|
| **Live deploy** | ✅ Done | System nginx proxies to Docker app on localhost:8000 |
| **Azure OpenAI** | No model deployment exists | Optional — OpenAI working fine |
| **HTTPS/SSL** | ✅ Done | Let's Encrypt ECDSA cert active; auto-renewal cron set |
| **Student session UI** | Not built yet | Phase after manager workflow stabilizes |
| **DPDPA privacy notice** | ✅ Done | `/nursing/privacy` live with consent banner |
| **Flutter release build** | `bcprov-jdk18on-1.80` major version 65 toolchain mismatch | Phase 10.3 (Issue #35) |
| **HomeScreen nursing card overflow** | Narrow-screen layout bug | Phase 10.5 (Issue #37) |

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
| **ADR-019** | **PWA-first distribution for Nursing** | **Accepted** |

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
| Nursing Staff Nurse | 1 | Default | — |

> Note: 6 topics exist as JSON files from earlier runs. DB migration captured 2 generations (Rational Numbers, Exponents). Re-generating any topic will create a fresh DB row.

---

## 🎯 Next Immediate Work

1. **Phase 10.3** — Fix Flutter release build toolchain (Issue #35)
3. **Phase 10.5** — Fix `HomeScreen` nursing card overflow on narrow screens (Issue #37)
4. **Manager requests features** — e.g., export ratings CSV, bulk generate, prompt templates from research personas

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
docker compose config

# Deploy to server (run ON the server)
./scripts/deploy.sh

# Enable SSL (run ON the server, after DNS works)
./scripts/init-ssl.sh

# Nursing smoke test
curl -s https://drmath.trelolabs.com/nursing/ | head -5
curl -s "https://drmath.trelolabs.com/api/nursing/questions?limit=5" | python3 -m json.tool | head -20
```

---

## 📝 Change Log

| Date | Change | Commit |
|---|---|---|
| 2026-06-28 | Phase 10.1: Nursing PWA landing live at /nursing/ | `cb71528` |
| 2026-06-28 | ADR-019: PWA-first distribution for Nursing | `8b199d5` |
| 2026-05-03 | Prompt versioning, expand/collapse, pipeline timestamps | `3ee765d` |
| 2026-05-03 | Web UI: prompt families, generation timeline, Lab updates | `0bd98aa` |
| 2026-05-03 | **LIVE: Deployed to production with HTTPS** | `e264acb` |
| 2026-05-03 | ADR-008: SQLite for prompt experimentation | `7c80386` |
| 2026-05-03 | SQLite DB layer (models, CRUD, migration) | `6e37c2e` |
| 2026-05-03 | Pipeline DB integration + grounding logs | `e75fa70` |
| 2026-05-03 | Manager Lab: A/B compare, ratings, leaderboard | `8f98520` |
| 2026-05-03 | Production deploy scripts + auto-SSL | `38f7a2e` |
| 2026-05-03 | Pre-commit hook + setup script | `7c81e4e` |
