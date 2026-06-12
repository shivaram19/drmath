# Dr. Math — Engineering Case Study

**An adaptive, AI-powered math learning platform for Indian Class VII students.**

---

## At a Glance

| | |
|---|---|
| **Role** | Founder / Lead Engineer / Product Architect |
| **Domain** | K-12 Education Technology (EdTech), Generative AI, Adaptive Learning |
| **Target Users** | Indian students aged 12–13 (CBSE Class VII) |
| **Live URL** | https://drmath.trelolabs.com |
| **Stack** | Python, FastAPI, SQLAlchemy, PostgreSQL (planned), Docker, nginx, OpenAI GPT-4o-mini, Flutter |
| **Status** | Content pipeline live; student-facing backend in research |
| **Key Differentiator** | Every pedagogical and architectural decision is backed by peer-reviewed learning science |

---

## The Problem

Most math apps for Indian middle-schoolers fall into one of two traps:

1. **Rigid difficulty levels** — force kids into fixed "easy/medium/hard" buckets that ignore their actual thinking.
2. **Generic worksheets** — generate endless practice problems without understanding *why* a child struggles.

The result? Children either get bored (too easy) or anxious (too hard), and never develop the cognitive flexibility and reasoning ability that real math learning requires.

## The Product Vision

> Build an adaptive math companion that reads how a child's brain is evolving — not just whether they got the answer right — and continuously selects the next question, hint, or explanation to move them into their Zone of Proximal Development.

---

## What I Built

### Phase 1: Research-Backed Content Pipeline (Live)

A fully automated pipeline that produces curriculum-aligned, pedagogically diverse assessment content:

| Component | What It Does |
|-----------|--------------|
| **Scraper** | Headless browser (Obscura) extracts IXL skills and MathIsFun explanations |
| **LLM Adapter** | OpenAI GPT-4o-mini rewrites content through research-backed personas |
| **Question Generator** | Produces 40 MCQs per topic with explanations, distractors, and difficulty metadata |
| **Batch Orchestrator** | Concurrent generation across 10 topics × 4 pedagogical dimensions |
| **PM Review System** | Four-dimension rating interface for pedagogical quality review |

**Generated corpus:** ~1,680 questions across 10 Class VII topics (Integers, Fractions, Percentage, Rational Numbers, Exponents, Triangles, Simple Equations, Lines and Angles, Data Handling, Perimeter and Area) × 4 pedagogical dimensions.

### Phase 2: Adaptive Runtime Backend (In Research)

Designing a student-facing backend around the **"Mark" system** — a multi-dimensional learner state vector that tracks:

- Accuracy streaks and response-time trends
- Hint dependency and confidence patterns
- Misconception history
- Continuous difficulty estimate (no rigid levels)
- Spaced-repetition scheduling per concept

### Phase 3: Games Integration (Planned)

Mini-games whose outcomes feed back into the Mark system, so play and practice share one unified model of the child's understanding.

---

## The Pedagogical Dimensions

Dr. Math does not generate one-size-fits-all questions. It generates through four lenses, each grounded in research:

| Dimension | Research Basis | Approach |
|-----------|----------------|----------|
| **Default (Anti-Gravity)** | Rosenshine's Principles of Instruction | Clear scaffolding, progressive difficulty, direct instruction |
| **Cultural Storyteller** | Situated Learning / Lave & Wenger | Math embedded in Indian cultural contexts |
| **Visual-First Thinker** | Bruner's Concrete-Pictorial-Abstract (1966) | Diagrams, number lines, spatial reasoning |
| **ZPD Adaptive Tutor** | Vygotsky's Zone of Proximal Development (1978) | Just-harder-than-comfortable problems with fading support |

---

## Architecture Highlights

```
┌─────────────────────────────────────────────────────────────┐
│  Flutter Client / Web UI                                    │
│  (Student practice, PM review, Manager lab)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  FastAPI Backend                                            │
│  • Adaptive question selection                              │
│  • Session / attempt / hint logging                         │
│  • Mark state updates                                       │
│  • Content pipeline API                                     │
└──────────┬──────────────────────────────┬───────────────────┘
           │                              │
           ▼                              ▼
┌─────────────────────┐      ┌──────────────────────────────┐
│   PostgreSQL        │      │   Redis                      │
│   (students, marks, │      │   (active sessions,          │
│    attempts, games) │      │    question cache, SR queue) │
└──────────┬──────────┘      └──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│  Content Pipeline (Python)                                  │
│  • IXL + MathIsFun scraping                                 │
│  • LLM adaptation & question generation                     │
│  • Versioned prompt management                              │
│  • Grounding & provenance logs                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Engineering Rigor

### Research-First Covenant

Every architectural decision requires:
1. Decomposition → BFS landscape mapping → DFS deep-dive → ADR → Code.
2. Citations from T1–T3 sources.
3. Council of Ten deliberation for non-trivial decisions.
4. No rigid difficulty levels (research supports continuous adaptation).

### Architecture Decision Records (ADRs)

19+ ADRs document decisions on scraping, LLM providers, adaptive engine, SQLite→PostgreSQL migration, prompt experimentation, PM review system, batch generation, and more.

### Quality Gates

- Git pre-commit hook enforces conventional commits, blocks `.env` and runtime artifacts.
- Every generation records a 4-step pipeline timeline: scrape → adapt → generate → save.
- Grounding logs link every question back to IXL/MathIsFun sources.

---

## Outcomes & Metrics

| Metric | Value |
|--------|-------|
| Topics generated | 10 (CBSE Class VII) |
| Pedagogical dimensions | 4 |
| Total questions generated | ~1,680 |
| Invalid questions | 0 |
| Pipeline batch jobs | 40 (10 topics × 4 dimensions) |
| ADRs written | 17+ |
| Research documents | 10+ (BFS/DFS/bidirectional) |
| Deployment | Live with Docker + nginx + HTTPS |

---

## Skills Demonstrated

- **Product Architecture:** Translated a vague vision ("adapt to the kid's brain") into a concrete state-machine and data model.
- **AI/LLM Engineering:** Built a deterministic pipeline around a non-deterministic model using structured generation, prompt versioning, and grounding.
- **Backend Engineering:** Designed PostgreSQL schemas for adaptive learning, session management, and spaced repetition.
- **Research Synthesis:** Converted learning-science papers into engineering specifications and evaluation rubrics.
- **DevOps & Deployment:** Dockerized the stack, deployed behind nginx, and automated SSL.
- **Ethical Technology:** Designed for child privacy by default (pseudonymous IDs, minimal PII, encrypted state at rest).

---

## Live Links

| URL | Purpose |
|-----|---------|
| https://drmath.trelolabs.com | Main application |
| https://drmath.trelolabs.com/review/integers | PM question review interface |
| https://drmath.trelolabs.com/status | Generation status dashboard |
| https://drmath.trelolabs.com/instructions | PM guide to pedagogical dimensions |

---

## What I Learned

1. **AI is not the product; pedagogy is.** The most impressive technical demo fails if it does not serve how children actually learn.
2. **Deterministic rails matter for kids.** LLMs are powerful but must be constrained by structured output, explicit misconception taxonomies, and human-in-the-loop review.
3. **Data models outlive code.** Investing in the schema early — especially separating events from derived state — pays off across every future feature.
4. **Research-first engineering is slower but safer.** Writing ADRs before code prevented several expensive architectural pivots.

---

## Roadmap

- [x] Research-backed content pipeline
- [x] PM review system
- [x] Multi-prompt batch generation
- [ ] Student authentication & pseudonymous identity
- [ ] Adaptive question runtime
- [ ] Spaced repetition engine
- [ ] Parent/teacher progress dashboard
- [ ] Math mini-games integrated with Mark system

---

## Contact

Built by **Shivaram Goud**.  
GitHub: https://github.com/shivaram19/drmath  
Live Demo: https://drmath.trelolabs.com
