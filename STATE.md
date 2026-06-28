# Dr. Math — Current State

**Last Updated:** 2026-05-05  
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
| https://drmath.trelolabs.com/mathwise.apk | ✅ Flutter release APK (15.5 MB) |
| https://drmath.trelolabs.com/api/nursing/analytics | ✅ Consent-gated analytics beacon |

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
| **Nursing Analytics** | ✅ | Anonymous `sendBeacon` events gated by `mw_privacy_consent`; JSONL retention 30 days |
| **Web-to-APK Conversion** | ✅ | UTM-tagged prompts on result, landing banner, share text; `apk_download_clicked` + `app_first_open` events |
| **Native App Analytics Consent** | ✅ | One-time in-app dialog; separate `mw_native_consent` record; DPDPA-aligned |
| **Native APK network permissions** | ✅ | `INTERNET` + `ACCESS_NETWORK_STATE` added to `AndroidManifest.xml`; fixes installed-APK "No internet connection" error |
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
| **Flutter release build** | ✅ Done | Jetifier ignore-list + ABI filter; `flutter build apk --release` succeeds |
| **Release APK size** | ✅ Done | 15.4 MB (target ≤ 20 MB) |
| **HomeScreen / app-wide narrow-screen overflow** | ✅ Done | 320–430 dp responsive pass; visual tests now use correct logical viewports |

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
| **ADR-020** | **DPDPA privacy notice & consent for Nursing** | **Accepted** |
| **ADR-021** | **Android release build toolchain** | **Accepted** |
| **ADR-022** | **Consent-gated analytics for Nursing** | **Accepted** |
| **ADR-023** | **Web-to-APK conversion measurement** | **Accepted** |
| **ADR-024** | **WhatsApp channel choice, consent model, and data retention** | **Proposed** |
| **ADR-025** | **Pragmatic SOLID refactor strategy** | **Proposed** |

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

1. **Phase 10.8+** — Monitor APK conversion funnel (`apk_prompt_shown` → `apk_download_clicked` → `app_first_open`) for at least 100 impressions; decide whether to spike a Play Console release based on click-to-open gap.
2. **~~Phase 10.8a~~ ✅** — Characterization tests for `pipeline/run.py` and core web routes committed.
3. **~~Phase 10.8b~~ ✅** — Math pipeline decoupled behind ports (`pipeline/interfaces.py`, `pipeline/adapters.py`, `pipeline/use_cases.py`); `run_pipeline()` is now a compatibility wrapper.
4. **~~Phase 10.8c~~ ✅** — Web composition root created (`web/dependencies.py`); `NursingService` and `AnalyticsSink` injected via FastAPI `Depends`. `web/main.py` left intact; router split deferred to incremental cleanup.
5. **🟡 Phase 10.9 — Backend** — WhatsApp daily quiz reminder experiment: explicit opt-in flow, BSP evaluation (Chat Mitra Starter / Meta Cloud API), Meta template approval, backend scheduler + STOP handling, cost/engagement reversal trigger. **Unblocked by Phase 10.8c. Tracked in #52.**
6. **Phase 10.10** — Expand nursing seed bank to 100 verified questions across INC GNM domains with `source_url`, `source_section`, and `verified_at` metadata.
7. **🟡 ADR-024** — Architecture Decision Record drafted (`docs/adrs/ADR-024-whatsapp-channel-choice-consent-retention.md`, status **Proposed**). Approval required before bot code is merged.
8. **ADR-025** — Write Architecture Decision Record for pragmatic SOLID refactor strategy (ports for volatile boundaries, Strangler Fig, delete `src/`).
9. **Structural cleanup** — Delete empty `src/` tree, update `AGENTS.md`, remove runtime artifacts from production Docker image.
10. **Manager requests features** — export ratings CSV, bulk generate, prompt templates from research personas.

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
| 2026-05-05 | ADR-024: WhatsApp channel, consent model, and data retention decision drafted (Proposed) | #52 / `1d15a74` |
| 2026-05-05 | Phase 10.8c: Web composition root + `NursingService`/`AnalyticsSink` injection; 57 tests passing | #51 |
| 2026-05-05 | Phase 10.8b: Pipeline ports/adapters/use-case refactor; `run_pipeline()` compatibility wrapper; 55 tests passing | #50 |
| 2026-05-05 | Phase 10.8a: Characterization tests for pipeline runner and web routes; 52 tests passing | `e403018` / #49 |
| 2026-06-28 | Phase 10.1: Nursing PWA landing live at /nursing/ | `cb71528` |
| 2026-06-28 | ADR-019: PWA-first distribution for Nursing | `8b199d5` |
| 2026-06-28 | Phase 10.6a: Consent-gated analytics endpoint and client events | — |
| 2026-06-28 | ADR-022: Consent-gated analytics for Nursing | — |
| 2026-06-28 | Phase 10.7: HomeScreen + shared widgets 320–430 dp responsive pass | — |
| 2026-06-28 | Full narrow-screen audit: fixed overflows in topic/subtopic/curriculum/concept screens; corrected visual-test viewport config | — |
| 2026-06-28 | Research: Phase 10.8 retrospective, WhatsApp/DPDPA/source-verification findings, refined plan in `docs/research/introspection-phase10_8-and-beyond-2026-06-28.md` | — |
| 2026-06-28 | Fixed installed APK "No internet connection": added `INTERNET`/`ACCESS_NETWORK_STATE` permissions; rebuilt + redeployed APK; local/remote SHA-256 verified | — |
| 2026-05-03 | Prompt versioning, expand/collapse, pipeline timestamps | `3ee765d` |
| 2026-05-03 | Web UI: prompt families, generation timeline, Lab updates | `0bd98aa` |
| 2026-05-03 | **LIVE: Deployed to production with HTTPS** | `e264acb` |
| 2026-05-03 | ADR-008: SQLite for prompt experimentation | `7c80386` |
| 2026-05-03 | SQLite DB layer (models, CRUD, migration) | `6e37c2e` |
| 2026-05-03 | Pipeline DB integration + grounding logs | `e75fa70` |
| 2026-05-03 | Manager Lab: A/B compare, ratings, leaderboard | `8f98520` |
| 2026-05-03 | Production deploy scripts + auto-SSL | `38f7a2e` |
| 2026-05-03 | Pre-commit hook + setup script | `7c81e4e` |
