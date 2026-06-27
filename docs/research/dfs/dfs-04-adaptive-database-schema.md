# DFS-04: Adaptive Database Schema Design for Student-Facing Dr. Math

**Date:** 2026-05-13  
**Scope:** PostgreSQL data model for student identity, sessions, attempts, hints, adaptive "Mark" state, spaced repetition, achievements, and game-result integration.  
**Research Phase:** DFS (Depth-First Technology Deep-Dive)  
**Branch:** `backend-research`  

---

## 1. Research Question

How should Dr. Math persist student learning state in PostgreSQL so that the system can:
1. Serve adaptive question selection in <200ms,
2. Track every student action with full auditability,
3. Support the "Mark" state vector from ADR-007 [^7],
4. Enable spaced repetition and mastery progression,
5. Leave a clean integration point for future games,
6. Minimize collection of child PII under Indian DPDP Act 2023 and COPPA/GDPR-K principles?

---

## 2. How Great Platforms Built This

### 2.1 Open edX — Course-Centric Progress Model

Open edX stores learner progress in two core patterns [^1]:

**`courseware_studentmodule`** — one row per (student, course_module) tuple:
```
(student_id, module_id, module_type, state, grade, max_grade, done, created, modified)
```
This table is the largest and most queried in the Open edX data package. It holds the *most recent* state of each content item a learner touched. The `state` column is a JSON blob containing problem-specific data (e.g., last answer, position). Grades are normalized (`grade / max_grade`).

**`BlockCompletion` / `AggregateCompletion`** — introduced later to fix performance and correctness problems:
- `BlockCompletion`: `(user, course_key, usage_key, block_type, completed [0.0–1.0])`
- `AggregateCompletion`: `(user, course_key, usage_key, aggregation_name, earned, possible)`

The Robust Grades project added `PersistentCourseGrade` and `PersistentSubsectionGrade` because grades were previously recalculated on demand, which was too slow at scale and lost historical truth when content changed [^2].

**Lessons for Dr. Math:**
- Separate *event/interaction* data from *aggregated state* data.
- Do not recalculate mastery on demand; persist it incrementally.
- Use immutable event history to protect against content changes.
- Index the hot path: `(student_id, topic_id, concept_id)`.

### 2.2 ASSISTments — Transaction-Level Interaction Model

ASSISTments logs each student action as a transaction [^3][^4]:
```
(order_id, user_id, problem_id, skill_id/skill_name, correct, attempt_count,
 ms_first_response, hint_count, first_action, opportunity, ...)
```

Key design choices:
- **First-action coding:** Every interaction is classified as `attempt`, `hint`, or `correct` on first action. This is the primary signal for knowledge tracing.
- **Skill tags (Knowledge Components):** Problems are tagged with one or more skills. Multi-skill problems are duplicated in analysis datasets.
- **Hints:** `hint_count` and `first_action=hint` model help-seeking behavior.
- **Opportunity counter:** Tracks how many times a student has encountered a skill, critical for BKT [^5].

**Lessons for Dr. Math:**
- Store *first action* distinctly from subsequent attempts.
- Tag every question with knowledge components (sub-skills within a topic).
- Count opportunities per concept for future BKT calibration.
- Distinguish "hint before answer" from "answer then hint" — they mean different things cognitively.

### 2.3 Duolingo — Student-Word Decay Model

Duolingo's student model tracks per-word recall probability using **Half-Life Regression (HLR)** [^6]:
```
p = 2^(-Δ/h)
```
where `p` = recall probability, `Δ` = days since last practice, `h` = memory half-life.

Data stored per student-word pair:
- `x_n`: total times seen
- `x_+`: correct recalls
- `x_-`: incorrect recalls
- lexeme tag features

This powers:
- **Strength meters:** visual decay of skill freshness.
- **Practice prioritization:** weakest words selected first.
- **Spaced repetition schedule:** next review computed from predicted half-life.

**Lessons for Dr. Math:**
- Track per-concept counters (seen, correct, incorrect) for spaced repetition.
- Model forgetting as continuous decay, not binary "mastered / not mastered."
- Use strength meters as a parent-facing visualization, not as the internal adaptive signal.

### 2.4 Khan Academy — Mastery Percentage Model

Khan Academy represents mastery as a percentage per exercise/skill, updated from practice sessions. The backend uses:
- **UserExercise** table: `(user, exercise, longest_streak, progress, total_done, last_done, ...)`
- **ProblemLog** table: one row per problem attempt with timing and answer.
- **Mastery percentage** is derived from recent performance and streaks.

**Lessons for Dr. Math:**
- Streaks are motivating and computationally cheap.
- A summary table prevents expensive aggregation at read time.
- Keep raw attempt logs for research and debugging.

---

## 3. Extracted Data Model Principles

From the platforms above, we derive these principles:

| # | Principle | Rationale |
|---|-----------|-----------|
| P1 | **Events are immutable; state is derived.** | Never mutate history. Marks and mastery are computed from events. |
| P2 | **One row per atomic interaction.** | An attempt, a hint request, a timeout, and a game action are separate events. |
| P3 | **First action is primary signal.** | Subsequent retries on the same question contaminate knowledge-tracing signals. |
| P4 | **Separate content from interaction.** | Question text lives in content pipeline; backend references `question_id`. |
| P5 | **Mastery is continuous, not boolean.** | Avoid "Level 1/2/3/4" buckets per ADR-007 and AGENTS.md. |
| P6 | **Minimize PII; prefer pseudonymous IDs.** | Child data protection requires default-privacy design. |
| P7 | **Index the hot paths before scale.** | `(student_id, topic_id)` and `(student_id, concept_id)` will be queried constantly. |

---

## 4. Proposed PostgreSQL Schema v1

### 4.1 Entity Overview

```
students
  └── student_marks (one per student-topic)
        └── derived from: attempts, hint_requests, timeouts, game_actions

sessions
  └── session_events (attempts, hints, timeouts, navigations)

questions (imported from pipeline output)
  └── question_concepts (many-to-many to concepts)
  └── question_misconceptions (many-to-many to misconceptions)

concepts (knowledge components within a topic)
misconceptions (catalog of known error patterns)

spaced_repetition_items (per student-concept review schedule)
achievements
game_sessions
game_actions
```

### 4.2 DDL

```sql
-- ----------------------------------------------------------------------
-- Students: pseudonymous, minimal PII
-- ----------------------------------------------------------------------
CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    public_id TEXT UNIQUE NOT NULL,          -- shareable with client, no sequence leak
    display_name TEXT,                        -- optional, can be avatar name
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_active_at TIMESTAMPTZ
);
CREATE INDEX idx_students_last_active ON students(last_active_at);

-- ----------------------------------------------------------------------
-- Topics: mirrors pipeline topics, but canonical for backend
-- ----------------------------------------------------------------------
CREATE TABLE topics (
    id SERIAL PRIMARY KEY,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    display_order INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------------------
-- Concepts: fine-grained knowledge components (e.g., "integer_addition",
-- "sign_confusion", "number_line_positioning")
-- ----------------------------------------------------------------------
CREATE TABLE concepts (
    id SERIAL PRIMARY KEY,
    topic_id INT NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    slug TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    prerequisite_concept_id INT REFERENCES concepts(id),
    UNIQUE(topic_id, slug)
);
CREATE INDEX idx_concepts_topic ON concepts(topic_id);

-- ----------------------------------------------------------------------
-- Misconceptions: catalog of known error patterns
-- ----------------------------------------------------------------------
CREATE TABLE misconceptions (
    id SERIAL PRIMARY KEY,
    topic_id INT NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    slug TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    example_wrong_answer TEXT,
    remediation_strategy TEXT,
    UNIQUE(topic_id, slug)
);

-- ----------------------------------------------------------------------
-- Questions: pointer to pipeline-generated content
-- ----------------------------------------------------------------------
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generation_id INT,                       -- links to pipeline.generations
    topic_id INT NOT NULL REFERENCES topics(id),
    prompt_dimension TEXT,                   -- default | storyteller | visual | zpd
    external_ref TEXT,                       -- e.g., "integers_output.json#12"
    difficulty_estimate DECIMAL(4,2) NOT NULL DEFAULT 1.0,  -- continuous 0.5–4.5
    estimated_time_ms INT,                   -- expected solve time
    correct_answer TEXT NOT NULL,
    question_hash TEXT UNIQUE,               -- deterministic hash of canonical content
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_questions_topic ON questions(topic_id);
CREATE INDEX idx_questions_difficulty ON questions(topic_id, difficulty_estimate);

CREATE TABLE question_concepts (
    question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    concept_id INT NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    weight DECIMAL(3,2) NOT NULL DEFAULT 1.0,  -- how strongly this concept is tested
    PRIMARY KEY (question_id, concept_id)
);

CREATE TABLE question_misconceptions (
    question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    misconception_id INT NOT NULL REFERENCES misconceptions(id) ON DELETE CASCADE,
    distractor_index INT,                    -- which wrong option signals this misconception
    PRIMARY KEY (question_id, misconception_id)
);

-- ----------------------------------------------------------------------
-- Student Marks: per-topic adaptive state vector (the "Mark")
-- ----------------------------------------------------------------------
CREATE TABLE student_marks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    topic_id INT NOT NULL REFERENCES topics(id) ON DELETE CASCADE,

    -- continuous mastery spectrum (ADR-007)
    mastery_state TEXT NOT NULL DEFAULT 'exploring'
        CHECK (mastery_state IN ('exploring', 'building', 'stretching', 'mastering', 'solid')),

    -- adaptive dimensions
    difficulty_estimate DECIMAL(4,2) NOT NULL DEFAULT 1.5,
    accuracy_rate DECIMAL(4,3) NOT NULL DEFAULT 0.0,
    streak_correct INT NOT NULL DEFAULT 0,
    streak_wrong INT NOT NULL DEFAULT 0,
    avg_response_time_ms INT,
    hint_dependency_ratio DECIMAL(4,3) NOT NULL DEFAULT 0.0,
    last_error_type TEXT,                    -- misconception slug or NULL
    confidence_trend TEXT CHECK (confidence_trend IN ('rising', 'falling', 'anxious', 'overconfident', 'stable')),

    -- spaced repetition counters
    total_attempts INT NOT NULL DEFAULT 0,
    total_correct INT NOT NULL DEFAULT 0,
    last_session_at TIMESTAMPTZ,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(student_id, topic_id)
);
CREATE INDEX idx_marks_student ON student_marks(student_id);
CREATE INDEX idx_marks_topic ON student_marks(topic_id);

-- ----------------------------------------------------------------------
-- Sessions: a single student practice episode
-- ----------------------------------------------------------------------
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    topic_id INT NOT NULL REFERENCES topics(id),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    session_type TEXT NOT NULL DEFAULT 'adaptive' CHECK (session_type IN ('adaptive', 'review', 'game', 'assignment')),
    final_mastery_state TEXT,
    questions_asked INT NOT NULL DEFAULT 0,
    questions_correct INT NOT NULL DEFAULT 0,
    client_info JSONB
);
CREATE INDEX idx_sessions_student ON sessions(student_id, started_at DESC);
CREATE INDEX idx_sessions_active ON sessions(student_id) WHERE ended_at IS NULL;

-- ----------------------------------------------------------------------
-- Attempts: immutable record of every answer submission
-- ----------------------------------------------------------------------
CREATE TABLE attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES questions(id),

    -- timing
    presented_at TIMESTAMPTZ NOT NULL,
    answered_at TIMESTAMPTZ,
    response_time_ms INT,

    -- outcome
    is_correct BOOLEAN,
    selected_answer TEXT,
    is_timeout BOOLEAN NOT NULL DEFAULT FALSE,
    is_first_action BOOLEAN NOT NULL DEFAULT TRUE,

    -- adaptive signals
    difficulty_at_time DECIMAL(4,2) NOT NULL,
    mark_state_before JSONB NOT NULL,         -- snapshot of student_marks before
    mark_state_after JSONB,                   -- snapshot after (computed async or sync)

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_attempts_session ON attempts(session_id, presented_at);
CREATE INDEX idx_attempts_student_question ON attempts(student_id, question_id, presented_at DESC);

-- ----------------------------------------------------------------------
-- Hint Requests: separate from attempts because hints are help-seeking signals
-- ----------------------------------------------------------------------
CREATE TABLE hint_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attempt_id UUID NOT NULL REFERENCES attempts(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    hint_level INT NOT NULL DEFAULT 1,        -- progressive hint: 1 = vague, 3 = worked example
    hint_type TEXT NOT NULL DEFAULT 'scaffold' CHECK (hint_type IN ('scaffold', 'visual', 'worked_example', 'definition')),
    was_before_answer BOOLEAN NOT NULL,       -- true if hint preceded any answer attempt
    llm_generated BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX idx_hints_attempt ON hint_requests(attempt_id);
CREATE INDEX idx_hints_session ON hint_requests(session_id, requested_at);

-- ----------------------------------------------------------------------
-- Spaced Repetition Queue: per student-concept next-review schedule
-- ----------------------------------------------------------------------
CREATE TABLE spaced_repetition_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    concept_id INT NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,

    strength_score DECIMAL(4,3) NOT NULL DEFAULT 0.5,  -- 0 = forgotten, 1 = solid
    half_life_days DECIMAL(6,3) NOT NULL DEFAULT 1.0,
    last_reviewed_at TIMESTAMPTZ,
    next_review_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    consecutive_correct INT NOT NULL DEFAULT 0,
    consecutive_incorrect INT NOT NULL DEFAULT 0,

    UNIQUE(student_id, concept_id)
);
CREATE INDEX idx_sr_due ON spaced_repetition_items(next_review_at) WHERE next_review_at <= NOW() + INTERVAL '1 day';

-- ----------------------------------------------------------------------
-- Game Sessions: integration point for future mini-games
-- ----------------------------------------------------------------------
CREATE TABLE game_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions(id),  -- may be standalone or linked
    game_type TEXT NOT NULL,                  -- e.g., 'fraction_puzzle', 'integer_race'
    topic_id INT REFERENCES topics(id),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    score INT,
    meta JSONB
);
CREATE INDEX idx_game_sessions_student ON game_sessions(student_id, started_at DESC);

CREATE TABLE game_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    game_session_id UUID NOT NULL REFERENCES game_sessions(id) ON DELETE CASCADE,
    action_type TEXT NOT NULL,                -- 'move', 'hint', 'fail', 'success', 'timeout'
    concept_slug TEXT,
    difficulty_at_time DECIMAL(4,2),
    response_time_ms INT,
    is_correct BOOLEAN,
    payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_game_actions_session ON game_actions(game_session_id, created_at);

-- ----------------------------------------------------------------------
-- Achievements: motivational badges / milestones
-- ----------------------------------------------------------------------
CREATE TABLE achievements (
    id SERIAL PRIMARY KEY,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    criteria_type TEXT NOT NULL CHECK (criteria_type IN ('streak', 'mastery', 'persistence', 'explorer', 'social')),
    criteria JSONB NOT NULL
);

CREATE TABLE student_achievements (
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    achievement_id INT NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
    awarded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    context JSONB,
    PRIMARY KEY (student_id, achievement_id)
);
```

### 4.3 Design Notes

| Choice | Reason |
|--------|--------|
| **UUID primary keys for student-facing tables** | Prevents sequence enumeration attacks; supports pseudonymous identities. |
| **`attempts.mark_state_before` / `mark_state_after` as JSONB** | Immutable snapshots allow debugging and research without reconstructing history. |
| **Separate `hint_requests` table** | Distinguishes help-seeking from answering, which is critical for BKT and dependency-ratio metrics [^3]. |
| **Continuous `difficulty_estimate` decimal** | Honors ADR-007: no rigid difficulty buckets. |
| **`spaced_repetition_items` table** | Enables future Duolingo-style HLR or Leitner scheduling without schema changes. |
| **Game tables isolated but linked** | Future games can be built independently, then mapped to concepts via `game_actions.concept_slug`. |
| **No PII in `students`** | `display_name` is optional and can be an avatar name. No email/phone required. |

---

## 5. Hot Query Patterns & Indexes

| Query | Index |
|-------|-------|
| "Load student's Mark for topic" | `student_marks(student_id, topic_id)` (UNIQUE covers this) |
| "Pick next question for topic at difficulty ~X" | `questions(topic_id, difficulty_estimate)` |
| "Fetch student's recent sessions" | `sessions(student_id, started_at DESC)` |
| "Load active session" | `sessions(student_id) WHERE ended_at IS NULL` |
| "Find concepts due for review" | `spaced_repetition_items(next_review_at)` partial index |
| "Aggregate attempts by concept" | `attempts(student_id, question_id, presented_at)` + join to `question_concepts` |
| "Game results for a student" | `game_sessions(student_id, started_at DESC)` |

---

## 6. Council of Ten Deliberation

### 6.1 Proposal

Adopt the PostgreSQL schema in Section 4 as the v1 data model for the student-facing backend.

### 6.2 Deliberation

**PERSONA Research Scientist:** ENDORSE — The schema maps cleanly onto ASSISTments transaction logs, Duolingo's student-word model, and the Mark vector from ADR-007. Continuous difficulty and immutable events are research-backed [^3][^5][^6].

**PERSONA First-Principles Engineer:** ENDORSE — The model is derived from the atomic student action: a child sees a question, may request hints, answers (or times out), and the system updates state. Every table traces to that action.

**PERSONA Distributed Systems Architect:** CONCERN — At scale, `attempts` and `hint_requests` will grow very large. We need a retention/cold-storage strategy from day one, not as an afterthought. Also, `mark_state_after` JSONB snapshots will bloat the table.

**PERSONA Infrastructure-First SRE:** CONCERN — We need observability metrics: `attempt_insert_latency_p99`, `mark_update_latency_p99`, `adaptive_selection_latency_p99`. Without these, we cannot prove the schema performs.

**PERSONA Diagnostic Problem-Solver:** CONCERN — The schema assumes questions can be tagged with concepts and misconceptions. The current pipeline output does not reliably include these tags. We need a content-tagging strategy (manual, LLM-assisted, or hybrid) before this schema is usable.

**PERSONA Ethical Technologist:** ENDORSE — Default-privacy design is excellent: UUID pseudonyms, no required PII, optional display name. But we must also encrypt `mark_state_before`/`mark_state_after` JSONB at rest if it contains inferred cognitive state about a child.

**PERSONA Resource Strategist:** CONCERN — PostgreSQL + Redis + potentially LLM calls per interaction will cost real money. We need a per-student-per-month cost model before building.

**PERSONA Curious Explorer:** ENDORSE — The schema supports multiple future research directions: BKT calibration, HLR scheduling, game-to-mark mapping. I propose we also add an `experiments` table for A/B testing pedagogical variants.

**PERSONA Clarity-Driven Communicator:** BLOCK — This schema represents a major architectural decision. It requires ADR-018 (or ADR-019) before any migration code is written. No code before ADR.

**PERSONA Inner-Self Guided Builder:** ENDORSE — The schema serves the child first: fast question selection, privacy by default, clear progress signals. It is the right thing, not the easy thing.

### 6.3 Final Decision

**DECISION:** Approved in principle, **blocked from code implementation** until ADR is written.

**FINAL PROPOSAL:**
- Adopt the schema in Section 4 as the v1 student-facing data model.
- Add a migration path from SQLite pipeline DB to PostgreSQL backend DB.
- Address content-tagging gap by creating a separate research task: `docs/research/dfs/dfs-08-question-concept-tagging.md`.
- Add observability requirements to ADR-019.
- Add data-retention and cost-model requirements to ADR-019.

**DISSENT RECORDED:** None.

**RATIONALE:** The schema is research-aligned, privacy-respecting, and extensible. The blocking concern (ADR) is procedural, not technical, and will be satisfied before any migration or code is written.

---

## 7. Open Questions for Next DFS

1. How are questions imported from `output/*.json` into the `questions` table? One-time bulk import or continuous sync?
2. What is the algorithm for updating `student_marks.difficulty_estimate` after each attempt? (Deferred to adaptive engine DFS.)
3. How are concepts and misconceptions initially populated for each Class VII topic?
4. What is the retention policy for `attempts` and `hint_requests`? Hot for 90 days, cold storage (Parquet/S3) thereafter?
5. Should `student_marks` be updated synchronously on every attempt or asynchronously via an event queue?

---

## 8. References

[^1]: edX Research Guide. (2021). *User Info and Learner Progress Data — SQL Schema*. https://docs.openedx.org/en/ulmo/developers/references/internal_data_formats/data_references/sql_schema.html

[^2]: edX Engineering Blog. (2018). *XBlock Lessons: Plugin Performance and Grading*. https://engineering.edx.org/xblock-lessons-plugin-performance-and-grading-2f85a1d6fb2a

[^3]: IEEE DataPort. (2026). *ASSISTments Dataset 2009-2010*. https://ieee-dataport.org/documents/assistments-dataset-2009-2010

[^4]: Chaudhry, R., et al. (2018). Modeling Hint-Taking Behavior and Knowledge State of Students. *Proceedings of the 11th International Conference on Educational Data Mining (EDM 2018)*. https://educationaldatamining.org/files/conferences/EDM2018/papers/EDM2018_paper_100.pdf

[^5]: Gowda, S. M., et al. (2011). Ensembling Student Knowledge Models in ASSISTments. *Proceedings of KDD 2011*. https://pslcdatashop.web.cmu.edu/KDD2011/papers/C-kddined2011.pdf

[^6]: Settles, B., & Meeder, B. (2016). A Trainable Spaced Repetition Model for Language Learning. *Proceedings of ACL 2016*. https://www.cs.cmu.edu/~bsr/SettlesMeeder_ACL_2016.pdf

[^7]: ADR-007: Adaptive Engine Design — The "Mark" System. `docs/adrs/ADR-007-adaptive-engine.md`.

[^8]: Dr. Math Adaptive Engine Design. `docs/architecture/adaptive-engine-design.md`.
