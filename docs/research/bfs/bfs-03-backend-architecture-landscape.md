# BFS-03: Backend Architecture Landscape for Student-Facing Dr. Math

**Date:** 2026-05-13  
**Scope:** Backend architecture, data models, and runtime systems for transforming Dr. Math from a content-pipeline manager tool into an interactive adaptive learning platform for Indian Class VII students.  
**Research Phase:** BFS (Breadth-First Landscape Mapping)  
**Branch:** `backend-research`  

---

## 1. Context & Motivation

Dr. Math currently operates as a **content generation and curation pipeline**:
- Scrapes IXL skills and MathIsFun explanations.
- Adapts content via LLM using four research-backed pedagogical personas.
- Generates 40 MCQs per topic × 4 dimensions = ~1,680 questions.
- Provides PM/manager interfaces for review, comparison, and prompt experimentation.

The next phase requires a **student-facing runtime backend** where children can:
1. Start a learning session on a topic.
2. Receive questions selected adaptively from the generated pool.
3. Submit answers, request hints, and receive formative feedback.
4. Build a persistent "Mark" (multi-dimensional learner state) that evolves per topic.
5. Eventually engage with math mini-games whose outcomes feed back into the Mark system.

This document begins the breadth-first landscape mapping for that backend. It also records the first Council of Ten deliberation on the foundational decision: **what language/runtime and database stack should power this backend?**

---

## 2. Current State Snapshot

### 2.1 Existing Data Models (`db/models.py`)

| Entity | Purpose | Student-Relevant? |
|--------|---------|-------------------|
| `Prompt` | Teaching persona definitions (system + question prompt), versioned | Indirect — selects content style |
| `Topic` | Curriculum topic slug + name | Yes — student selects a topic |
| `Generation` | One batch of generated questions + adapted content per topic × prompt | Yes — source of questions |
| `Evaluation` | Manager 1–5⭐ rating of a generation | No — manager-only |
| `QuestionReview` | PM 4-dimension pedagogical rating per question | No — PM-only |
| `GroundingLog` | Source URL/content snippet used for generation | No — provenance only |

**Missing student-domain entities:** `Student`, `Session`, `Attempt`, `HintRequest`, `Mark`, `Achievement`, `GameSession`, `ConceptMastery`.

### 2.2 Existing User Flows (`web/main.py`)

| Route | Audience | Future Role |
|-------|----------|-------------|
| `/` Home | Manager/PM | Likely remains admin dashboard |
| `/topic/{slug}` | Manager/PM review | Read-only preview; student view may diverge |
| `/review/{slug}` | PM | Pedagogical quality review |
| `/lab`, `/compare`, `/history`, `/prompts` | Manager/PM | Admin tooling |
| `/instructions`, `/status` | PM/Internal | Operational visibility |
| `/api/*` | Internal/API | Needs student-facing API expansion |

**No current student authentication, session management, or adaptive runtime.**

### 2.3 Existing Adaptive Specification

`docs/architecture/adaptive-engine-design.md` and ADR-007 define the **"Mark" system**:
- Multi-dimensional state vector per student per topic.
- Dimensions: `difficulty_estimate`, `accuracy_streak`, `response_time_trend`, `hint_dependency_ratio`, `last_error_type`, `mastery_state`.
- Heuristic question selection; IRT/BKT deferred to Phase 2/3.
- Mastery states: `exploring` → `building` → `stretching` → `mastering` → `solid`.

This specification is **not yet persisted or executed** in the backend.

---

## 3. Proposal: Backend Language & Framework

**PROPOSAL:** Select the runtime language, web framework, and ORM for the student-facing backend.

**CANDIDATES:**

1. **Option A — Node.js + Express + Prisma + PostgreSQL + Redis**
   - Rationale: Ecosystem familiar to many full-stack developers; Prisma offers type-safe migrations; async-by-default; large middleware ecosystem.
   
2. **Option B — Python + FastAPI + SQLAlchemy 2.0 + PostgreSQL + Redis**
   - Rationale: Continues the existing stack (ADR-004); same language as the content pipeline; native async; SQLAlchemy already in use.
   
3. **Option C — Hybrid / Polyglot**
   - Rationale: Keep Python pipeline + FastAPI admin API; add a Node.js student-facing API that owns sessions/attempts/marks and consumes pipeline output.
   
4. **Option D — "Agentic Backend" (Language-agnostic, LLM-orchestrated)**
   - Rationale: Use LLM agents for hint generation, misconception diagnosis, and next-question selection; deterministic rails via structured generation.

**RISK LEVEL:** Critical — this decision constrains hiring, deployment, latency, cost, and integration with the existing pipeline for the lifetime of the product.

---

## 4. Council of Ten Deliberation

*Convened per the consensus-protocol skill. Each persona responds to the Proposal.*

### 4.1 Phase 1: Proposal Statement

See Section 3 above.

### 4.2 Phase 2: Asynchronous Deliberation

**PERSONA Research Scientist:** ENDORSE — The existing bibliography (Martin et al., 2020; Murray & Arroyo, 2002) supports the *pedagogical design* but is runtime-agnostic. No peer-reviewed evidence favors Node.js over Python for adaptive tutoring backends. The decision should therefore be driven by engineering constraints, not learning-science claims.

**PERSONA First-Principles Engineer:** CONCERN — The core axiom is "how children learn," not "what stack is popular." The critical atomic requirement is: *the backend must reliably map a child's action to an updated Mark and a selected next question*. Any stack that can model state transitions and serve JSON can satisfy this. We should derive from the state machine, not from ecosystem trends.

**PERSONA Distributed Systems Architect:** CONCERN — Option C (hybrid) introduces the most integration complexity: two runtimes, two deployment units, two ORMs, potential data-consistency boundaries. Option A or B keeps the system monolithic and simplifies transactional guarantees for session → attempt → mark updates.

**PERSONA Infrastructure-First SRE:** CONCERN — Option D ("agentic backend") lacks observability. If an LLM selects the next question, how do we prove it was pedagogically correct? Where is the audit trail? We need structured decision logs for every adaptation event before entrusting a child's learning path to a non-deterministic model.

**PERSONA Diagnostic Problem-Solver:** CONCERN — Options A and B both require a migration from SQLite to PostgreSQL. The symptom is "we need a real database"; the root cause is that SQLite is not suitable for concurrent student sessions. This decision is inseparable from the database decision. We should not choose a language without specifying the data model it must support.

**PERSONA Ethical Technologist:** CONCERN — Student data privacy must be a first-class constraint. Whichever stack we choose must support encrypted data at rest, minimal PII collection, and audit logging. The language matters less than the data-model discipline.

**PERSONA Resource Strategist:** BLOCK — We have not done TCO analysis for any option. Node.js vs. Python performance differs by workload; Prisma has licensing and team-learning costs; Redis adds infrastructure overhead. "Agentic" options have unbounded LLM token costs per student interaction. I cannot endorse any option without a TCO worksheet.

**PERSONA Curious Explorer:** ENDORSE — This is the right question to ask first. I propose we run a spike: implement the same minimal adaptive endpoint (start session → fetch question → submit answer → update Mark) in both Python/FastAPI and Node/Express against PostgreSQL, measure latency and developer ergonomics, and decide with data.

**PERSONA Clarity-Driven Communicator:** ENDORSE — The decision requires an ADR. This BFS document is the correct starting point. However, the final decision must be recorded in `docs/adrs/ADR-018-backend-language-framework.md` with explicit alternatives and rejection criteria.

**PERSONA Inner-Self Guided Builder:** ENDORSE — The right path is the one that lets us ship a safe, adaptive learning experience to children fastest, not the one that is most architecturally elegant. We should bias toward boring, well-understood technology (per AGENTS.md Decision Authority #1).

### 4.3 Phase 3: Blocking Check

**Blocking concern raised by Resource Strategist:** TCO analysis missing.

### 4.4 Phase 4: Consensus Round

The Council agrees that:
1. The language decision cannot be finalized without parallel research on data model, TCO, and deployment constraints.
2. The "agentic backend" (Option D) is too vague and must be decomposed into specific, bounded agent roles (e.g., hint-generation agent, misconception-tagging agent) before it can be evaluated.
3. A hybrid polyglot option should be rejected unless a clear service boundary justifies the operational overhead.
4. The best next step is to complete BFS landscape research (this document) and DFS deep-dives before reconvening on the final choice.

### 4.5 Phase 5: Final Decision

**DECISION:** Deferred pending BFS completion and TCO analysis.

**INTERIM POSITION:**
- **Retain Python/FastAPI/SQLAlchemy for the backend** as the default path (continuation of ADR-004), because it minimizes context switching with the existing pipeline and avoids polyglot complexity.
- **Explicitly evaluate Node.js/Express/Prisma** in a DFS deep-dive with TCO and team-velocity analysis.
- **Decompose "agentic backend"** into bounded agent roles (hint generation, misconception diagnosis, content regeneration triggers) and evaluate each separately.
- **Migrate from SQLite to PostgreSQL** regardless of language choice; SQLite cannot support concurrent student sessions.

**DISSENT RECORDED:** None — all personas accept the deferred decision.

**RATIONALE:** The current evidence is insufficient to overturn the existing FastAPI decision (ADR-004). However, the student's future may benefit from Node.js/Prisma if the Flutter client team or hiring pool favors it. We will decide with data, not momentum.

---

## 5. Initial Landscape Mapping

### 5.1 Backend Capability Areas

| Capability | Description | Why It Matters |
|------------|-------------|----------------|
| **Session Runtime** | Start, resume, timeout, end a student practice session | Core user loop |
| **Adaptive Selection** | Choose next question based on Mark | Pedagogical correctness |
| **Attempt Logging** | Record every answer, hint request, timeout | Analytics + adaptation |
| **Mark State Management** | Update and persist multi-dimensional learner state | Personalization |
| **Content Access** | Fetch questions from generated pools by topic/dimension/difficulty | Content pipeline integration |
| **Feedback Delivery** | Correctness + explanation + next-step hints | Learning effectiveness |
| **Progress & Mastery** | Topic-level and concept-level mastery dashboards | Motivation + parent visibility |
| **Game Integration Hook** | Receive game outcomes and translate into Mark updates | Future phase |
| **Auth & Identity** | Pseudonymous student identity + optional parent link | Privacy + persistence |
| **Observability** | Structured logs, metrics, adaptation audit trail | Safety + debugging |

### 5.2 Database Boundary Questions

- What belongs in PostgreSQL? (Students, sessions, attempts, marks, achievements, game sessions)
- What belongs in Redis? (Active session state, question-pool cache, rate-limit counters, real-time leaderboards)
- What stays in files/`output/*.json`? (Pre-generated question banks, until regenerated)
- What belongs in the content-pipeline DB? (Prompts, generations, grounding logs — manager domain)

### 5.3 Integration Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                     FLUTTER CLIENT                          │
│  (Student UI: questions, hints, games, progress)            │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS / WebSocket
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              STUDENT-FACING BACKEND                         │
│  • Session management                                       │
│  • Adaptive question selection                              │
│  • Attempt logging                                          │
│  • Mark updates                                             │
│  • Game result ingestion                                    │
└──────────┬──────────────────────────────┬───────────────────┘
           │                              │
           ▼                              ▼
┌─────────────────────┐      ┌──────────────────────────────┐
│   PostgreSQL        │      │   Redis                      │
│   (persistent state)│      │   (sessions, cache, realtime)│
└──────────┬──────────┘      └──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│              CONTENT PIPELINE (existing)                    │
│  • Prompts, Topics, Generations                             │
│  • Pre-generated question banks                             │
│  • Grounding & provenance                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Research Questions for DFS Phase

The following questions are deferred to DFS deep-dives:

1. What is the exact PostgreSQL schema for students, sessions, attempts, marks, and game sessions?
2. How should Redis key structure and TTL policies be designed for active sessions and question caches?
3. What is the TCO comparison between Python/FastAPI/SQLAlchemy and Node.js/Express/Prisma for 1,000 vs. 10,000 vs. 100,000 active students?
4. Which structured-generation library (Outlines, Guidance, JSON Schema) should enforce deterministic LLM outputs for hints/explanations?
5. Should the adaptive engine be synchronous request-response or event-driven?
6. What is the minimal PII-free identity model that supports parent dashboards and cross-device progress sync?
7. How do game results map to Mark dimensions without corrupting math-specific mastery signals?

---

## 7. References

[^1]: Bloom, B. S. (1984). The 2 Sigma Problem: The Search for Methods of Group Instruction as Effective as One-to-One Tutoring. *Educational Researcher*, 13(6), 4–16.

[^2]: Vygotsky, L. S. (1978). *Mind in Society: The Development of Higher Psychological Processes*. Harvard University Press.

[^3]: Martin, F., Chen, Y., Moore, R. L., & Westine, C. (2020). Systematic Review of Adaptive Learning Research Designs (2009–2018). *Educational Technology Research & Development*, 68, 1903–1929.

[^4]: Murray, T., & Arroyo, I. (2002). Toward Measuring and Maintaining the Zone of Proximal Development in Adaptive Instructional Systems. *Intelligent Tutoring Systems*.

[^5]: Sweller, J. (1988). Cognitive Load During Problem Solving: Effects on Learning. *Cognitive Science*, 12(2), 257–285.

[^6]: ADR-004: Web Framework Selection. `docs/adrs/ADR-004-web-framework.md`.

[^7]: ADR-007: Adaptive Engine Design — The "Mark" System. `docs/adrs/ADR-007-adaptive-engine.md`.

[^8]: Dr. Math Adaptive Engine Design. `docs/architecture/adaptive-engine-design.md`.
