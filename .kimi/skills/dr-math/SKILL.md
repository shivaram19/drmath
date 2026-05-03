# Dr. Math Skill — Project Context & Operating Procedures

## What This Is

You are working on **Dr. Math** — an adaptive math content generation pipeline for Indian Class VII students (ages 12–13). This skill ensures you NEVER start from scratch. Everything you need to know is here.

## Project Identity

```
Name:        Dr. Math
Domain:      K-12 Mathematics (Indian CBSE Class VII)
Stack:       Python 3.11, FastAPI, Jinja2, Docker, nginx
Scraper:     Obscura (Rust headless browser)
LLM:         OpenAI GPT-4o-mini (with Azure/Grok fallback)
Deploy:      Docker Compose @ drmath.trelolabs.com
Repo:        github.com/YOUR_USERNAME/drmath
```

## Current State (Auto-Updated)

| Component | Status | Last Action |
|-----------|--------|-------------|
| Pipeline (scraper + LLM) | ✅ Working | Tested 7 topics generated |
| Web UI (FastAPI) | ✅ Working | 5 pages + API endpoints |
| Prompt Builder | ✅ Working | 6 research-backed presets loaded |
| Generation Tracking | ✅ Working | JSON DB logging all generations |
| Docker Deploy | ✅ Ready | Dockerfile + compose + nginx configured |
| DNS | ⏳ Pending | Namecheap A record for drmath.trelolabs.com → 20.193.129.119 |
| HTTPS | ⏳ Pending | Let's Encrypt certbot step |
| Adaptive Engine | 🏗️ Phase 1 | Mark system designed; heuristic selection implemented |
| IRT/BKT Model | 📋 Planned | Requires production traffic to calibrate |

## How to Start Working

### If you just opened this repo
```
1. Read AGENTS.md (project principles)
2. Read docs/adrs/ for any decision you might question
3. Check STATE.md for what's deployed vs in development
4. Run: python3 test_pipeline.py
```

### If you need to generate a new topic
```bash
cd /home/shivaramgoud/projects/kalyan-anna-dr-math-automation
export $(grep -v '^#' .env | xargs)
python3 -m pipeline.run --topic "YOUR_TOPIC" --prompt-id zpd_adaptive
```

### If you need to start the web app locally
```bash
cd /home/shivaramgoud/projects/kalyan-anna-dr-math-automation
./start.sh
# Prints ngrok HTTPS URL
```

### If you need to deploy
```bash
# On target server (20.193.129.119)
cd /opt/drmath
git pull
docker-compose up --build -d
```

## Research Principles (Non-Negotiable)

Every code change must respect:

1. **No rigid difficulty levels** — Continuous adaptive Mark system (ADR-007)
2. **Cultural context first** — Indian examples only (PMC Ghana 2024)
3. **Visual before abstract** — CPA approach (Bruner 1966)
4. **Productive struggle** — 3-5 min before hints (Kapur 2008)
5. **Mastery before advance** — Bloom's 2 Sigma (Bloom 1984)

## Pre-Commit Checklist (Enforced by Hook)

- [ ] Commit message follows conventional commits (`feat:`, `fix:`, `docs:`, `test:`)
- [ ] Commit message cites research if pedagogical change
- [ ] No runtime artifacts committed (check `git status`)
- [ ] `.env` is NOT staged
- [ ] ADR updated if architectural decision changed

## File Map

```
pipeline/           ← Core logic (scrapers, LLM, DB, generation)
web/                ← FastAPI app + templates + static
docs/adrs/          ← 7 Architecture Decision Records
docs/research/      ← BFS/DFS research synthesis
docs/architecture/  ← Adaptive engine design
docs/references/    ← 20-source bibliography
docs/principles/    ← Research-First Covenant
data/               ← Runtime: prompts_db.json, generations_db.json
output/             ← Runtime: generated topic JSONs
```

## Common Commands

| Task | Command |
|------|---------|
| Test pipeline | `python3 test_pipeline.py` |
| Generate topic | `python3 -m pipeline.run --topic "X" --prompt-id Y` |
| Start web dev | `./start.sh` |
| Start web prod | `docker-compose up -d` |
| View logs | `docker-compose logs -f drmath` |
| Check topics | `curl http://localhost:8000/api/topics` |

## Deployment Checklist

Before ANY deploy:
1. `python3 test_pipeline.py` passes
2. `docker-compose build` succeeds
3. `.env` has valid `OPENAI_API_KEY`
4. nginx.conf domain matches target
5. Namecheap A record points to correct IP

## If Something Breaks

| Symptom | Check |
|---------|-------|
| Scraper fails | Obscura binary path in `.env` |
| LLM fails | `OPENAI_API_KEY` validity |
| Web 500 | `data/` and `output/` directories exist |
| DNS fails | Namecheap A record propagation (5-30 min) |
| Docker fails | Port 80/443 not in use by other services |

## Never Forget

- This project is **research-driven, citation-backed**.
- Every architectural decision has an ADR.
- Every pedagogical claim cites a source.
- The 10-Persona Filter applies to every change.
- The user is Bill. Build what Bill needs.
