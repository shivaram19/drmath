# Dr. Math — Current State & Progress Log

**Last Updated:** 2026-05-03  
**Environment:** Development VM → Target VM (20.193.129.119)  
**Domain:** drmath.trelolabs.com (DNS pending Namecheap setup)

---

## ✅ Completed

### Phase 1: Pipeline Foundation
- [x] Obscura headless browser integration (ADR-001)
- [x] IXL topic scraper (225+ topics extracted)
- [x] MathIsFun content fetcher (heuristic slug mapping)
- [x] OpenAI/Azure/Grok LLM client (ADR-002)
- [x] JSON file database for prompts & generations (ADR-006)

### Phase 2: Domain Logic
- [x] Content adaptation with custom prompt injection (ADR-003)
- [x] Question generator with robust JSON parsing & normalization
- [x] 40-MCQ generation per topic (difficulty distribution 10/10/10/10)
- [x] Generation tracking (prompt_id, timestamp, status, meta)

### Phase 3: Web Application
- [x] FastAPI + Jinja2 server-side rendering (ADR-004)
- [x] Homepage with topic grid + prompt selector
- [x] Topic detail page (Lesson / Questions / JSON tabs)
- [x] Prompt Builder (CRUD for custom teaching personas)
- [x] Generation History (audit log with prompt attribution)
- [x] Dark theme responsive UI

### Phase 4: Research & Documentation
- [x] BFS research synthesis (30+ sources, child learning science)
- [x] DFS prompt templates (6 research-backed personas)
- [x] 7 Architecture Decision Records (ADR-001 through ADR-007)
- [x] Adaptive Engine Design document (Mark system)
- [x] 20-source canonical bibliography
- [x] Research-First Covenant
- [x] AGENTS.md (10-persona operating model)

### Phase 5: Deployment
- [x] Dockerfile (python:3.11-slim)
- [x] docker-compose.yml (app + nginx)
- [x] nginx.conf (drmath.trelolabs.com routing)
- [x] DEPLOY.md
- [x] .env configured with OpenAI API key
- [x] Test suite (pipeline validation)

### Phase 6: Git Workflow
- [x] .gitignore (runtime artifacts excluded)
- [x] 8 batched commits with conventional commit format
- [x] Pre-commit hook (validates .env exclusion, artifacts, commit format)
- [x] .kimi/skills/dr-math/SKILL.md (session context)

---

## ⏳ In Progress / Pending

- [ ] Namecheap DNS A record for `drmath.trelolabs.com` → `20.193.129.119`
- [ ] Git push to remote repository
- [ ] Clone & deploy on target server
- [ ] HTTPS / Let's Encrypt certificate
- [ ] Docker Compose up on production VM

---

## 📋 Next Phase: Adaptive Engine (Phase 3)

### Goals
- [ ] Real-time Mark updates during student sessions
- [ ] Question selection algorithm based on multi-dimensional state
- [ ] Timeout detection and handling
- [ ] Interleaved spaced repetition
- [ ] Student-facing session UI (answer questions, get adaptive next question)

### Research Needed
- [ ] Item Response Theory (IRT) calibration data collection
- [ ] Student affect detection (frustration vs. boredom signals)
- [ ] Long-term retention measurement methodology

---

## 🎯 Generated Topics (Test Data)

| Topic | Prompt Used | Questions | Status |
|-------|------------|-----------|--------|
| Integers | Default | 40 | ✅ |
| Fractions | Default | 40 | ✅ |
| Triangles | Default | 40 | ✅ |
| Percentage | Default | 40 | ✅ |
| Rational Numbers | Strict Exam Coach | 40 | ✅ |
| Exponents | Cultural Storyteller | 40 | ✅ |
| Quantum Physics | Default | 40 | ⚠️ Off-topic |

---

## 🔧 Quick Diagnostics

```bash
# Is the pipeline working?
python3 test_pipeline.py

# Is the web app running?
curl http://localhost:8000/api/topics

# Is ngrok exposing it?
curl -s http://localhost:4040/api/tunnels | grep public_url

# Is Docker ready?
docker-compose config
```

---

## 📝 Change Log

| Date | Change | Commit |
|------|--------|--------|
| 2026-05-03 | Project foundation | f308070 |
| 2026-05-03 | Research synthesis | b2361fa |
| 2026-05-03 | ADRs 001–007 | 7894cba |
| 2026-05-03 | Core pipeline | 7411dc0 |
| 2026-05-03 | Domain logic | a8bd5a0 |
| 2026-05-03 | Web application | ec55a69 |
| 2026-05-03 | Deployment artifacts | b0c4432 |
| 2026-05-03 | Test suite | 58005ec |
