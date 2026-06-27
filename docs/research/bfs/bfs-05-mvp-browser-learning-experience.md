# BFS-05: MVP Browser Learning Experience — Feature Set & Low-Level Design

**Date:** 2026-06-12  
**Scope:** Define the minimum viable product (MVP) for an end-to-end in-browser adaptive math learning experience for Indian Class VII students, pass it through the Council of Ten, and produce low-level designs for approved features.  
**Research Phase:** BFS (Breadth-First Landscape Mapping) + Consensus  
**Branch:** `backend-research`  

---

## 1. Research Summary

Real-time searches on adaptive learning MVPs, intelligent tutoring systems, and math pedagogy converged on a consistent pattern: the most effective learning loop is **narrow, closed, and fast** [^1][^2][^3].

Key findings from the landscape:
- **MVP ed-tech products** should prioritize user registration, content delivery, and basic assessment before adding gamification or advanced analytics [^4][^5].
- **Effective math tutoring** relies on immediate feedback, scaffolded hints, and step-level adaptation rather than end-of-problem evaluation [^6][^7].
- **Adaptive sequencing** should re-measure mastery continuously and select the next item based on current state [^8][^9].
- **Hint ladders** (vague → concrete → worked example) are a well-established ITS pattern [^10][^11].
- **Anonymous/pseudonymous identity** minimizes friction and supports child privacy by default [^12][^13].
- **Spaced repetition** and **active recall** improve long-term retention [^14][^15].

---

## 2. High-Level MVP Feature Candidates

| # | Feature | User Story | Why It Matters |
|---|---------|------------|----------------|
| F1 | **Anonymous Session Identity** | "I open the browser and start learning without signing up." | Removes friction; protects child privacy; fits MVP validation. |
| F2 | **Topic Selection** | "I pick Integers, Fractions, or another Class VII topic." | Connects to the 10 generated content areas. |
| F3 | **Adaptive Practice Loop** | "The next question matches how I'm doing right now." | Core differentiator; implements the Mark system. |
| F4 | **Immediate Feedback** | "I know right away if I'm right and why." | Research shows immediate feedback accelerates learning [^6]. |
| F5 | **Progressive Hints** | "If I'm stuck, I get a hint that nudges me, not the answer." | Supports productive struggle without giving up. |
| F6 | **Session Summary** | "At the end I see what I practiced and how I did." | Closes the loop and motivates return. |
| F7 | **Spaced Repetition Queue** | "Questions I got wrong come back later." | Converts practice into long-term memory. |
| F8 | **Dimension Selector** | "I learn through stories, visuals, or step-by-step examples." | Uses the 4 pedagogical dimensions already built. |

**Deferred (post-MVP):** full user accounts, parent dashboard, gamification, LLM-generated dynamic hints, multiplayer leaderboards, emotion/affect detection.

---

## 3. Proposal: MVP Feature Set

**PROPOSAL:** Build an in-browser MVP consisting of F1–F8 above, with the explicit constraint that **no user account is required** and **all hints/explanations come from pre-generated content**, not LLM calls at runtime.

**RISK LEVEL:** High — this is the first student-facing product experience.

---

## 4. Council of Ten Deliberation

### 4.1 Persona Responses

**PERSONA Research Scientist:** ENDORSE — The feature set aligns with evidence: immediate feedback (Kulhavy, 1989; Black & Wiliam, 1998), scaffolded hints (Koedinger & Aleven, 2007), continuous mastery updates (Murray & Arroyo, 2002), and spaced repetition (Settles & Meeder, 2016). Deferring gamification is correct; motivation mechanics should follow core learning efficacy.

**PERSONA First-Principles Engineer:** ENDORSE — The atomic loop is: student sees question → optionally requests hints → submits answer → receives feedback → system updates state → selects next question. F1–F8 cover this loop completely.

**PERSONA Distributed Systems Architect:** CONCERN — F7 (spaced repetition) introduces state that must persist across sessions. If we use anonymous sessions, how do we identify a returning student? Browser localStorage? IP fingerprint? Cookie? Each has tradeoffs.

**PERSONA Infrastructure-First SRE:** CONCERN — F5 hints and F4 feedback must be pre-generated and validated. No runtime LLM calls in MVP means we must ensure every question in the pool has hint text. What percentage of the ~1,680 questions currently have usable hints?

**PERSONA Diagnostic Problem-Solver:** CONCERN — F3 adaptive selection is heuristic-only in Phase 1 (per ADR-007). We must define exactly how `difficulty_estimate` updates after each response. Without a precise rule, "adaptive" becomes arbitrary.

**PERSONA Ethical Technologist:** ENDORSE — Anonymous-first design is the right default for children. But we must be transparent: what data persists, where, and for how long? Browser localStorage can be cleared by the user; server-side anonymous sessions need a retention policy.

**PERSONA Resource Strategist:** CONCERN — We must cap MVP cost. No runtime LLM calls is good. But we need to estimate: storage for attempts, server compute for adaptive selection, and caching. The MVP should run within the existing Docker box.

**PERSONA Curious Explorer:** ENDORSE — Propose an MVP experiment: A/B test the 4 pedagogical dimensions (F8) by randomly assigning first-time students to a default dimension and measuring completion rate and accuracy.

**PERSONA Clarity-Driven Communicator:** BLOCK — This is a major product decision. It requires an ADR documenting the MVP scope, rejected features, and success metrics before any code is written.

**PERSONA Inner-Self Guided Builder:** ENDORSE — The proposal serves the child first: low friction, immediate feedback, privacy by default, no dark patterns. It is the right thing to build.

### 4.2 Blocking Check

**Blocking concern raised by Clarity-Driven Communicator:** ADR required.

**Blocking concern raised by Distributed Systems Architect:** Returning anonymous student identity strategy undefined.

### 4.3 Consensus Round

The Council agrees:
1. The MVP scope (F1–F8) is pedagogically sound and technically feasible.
2. Returning anonymous identity will be solved with a **browser-stored anonymous token** (`localStorage` + optional cookie backup), not server-side accounts.
3. Spaced repetition is simplified to **same-session wrong-answer retry** plus a **"Review Queue"** stored in `localStorage` for cross-session persistence in MVP.
4. Adaptive selection rule will be explicitly defined (see Section 6).
5. No runtime LLM calls. All hints/explanations must come from generated JSON.
6. ADR-020 will document the MVP scope before implementation.

### 4.4 Final Decision

**DECISION:** Approved.

**FINAL PROPOSAL:**
- Build F1–F8 as the in-browser MVP.
- Use anonymous browser-token identity.
- Store cross-session state in `localStorage` with optional server backup.
- Implement heuristic adaptive selection with explicit rules.
- Use only pre-generated hints/explanations.
- Write ADR-020 before code.

**DISSENT RECORDED:** None.

---

## 5. Low-Level Design — Approved MVP Features

### F1: Anonymous Session Identity

**Approach:**
- On first visit, generate `student_token = uuid4()` in browser.
- Store in `localStorage` under key `drmath_student_token`.
- Send token with every API request as `X-Student-Token` header.
- Server creates a `students` row with this token if not exists.
- Optional: cookie fallback if `localStorage` is unavailable.
- No email, name, or password required. Optional display name defaults to "Math Explorer".

**Privacy:**
- Token is random and unlinkable to PII.
- Data retention: 90 days of inactivity → anonymize attempt logs, keep aggregate stats.

### F2: Topic Selection

**Approach:**
- `/learn` page lists 10 topics as cards.
- Each topic shows: name, question count, short description, "Start Practice" CTA.
- Clicking starts a new `Session` with `session_type='adaptive'`.
- Also supports a "Review" session type from the spaced-repetition queue.

### F3: Adaptive Practice Loop

**State per session (in-memory + persisted after each attempt):**
```json
{
  "session_id": "uuid",
  "topic_slug": "integers",
  "dimension": "default",
  "difficulty_estimate": 1.5,
  "streak_correct": 0,
  "streak_wrong": 0,
  "recent_question_ids": [],
  "last_error_type": null,
  "questions_asked": 0,
  "questions_correct": 0
}
```

**Question selection algorithm (heuristic):**
```python
def select_next_question(mark, pool):
    scores = []
    for q in pool:
        score = 0
        # Difficulty match (closer is better)
        score += 10 - abs(q.difficulty - mark.difficulty_estimate)
        # Penalize recently seen
        if q.id in mark.recent_question_ids:
            score -= 25
        # Boost if targeting last error
        if q.misconception_tag == mark.last_error_type:
            score += 15
        # Slight randomness to avoid repetition
        score += random.uniform(-1, 1)
        scores.append((q, score))
    return max(scores, key=lambda x: x[1])[0]
```

**Mark update rules:**
- Correct answer: `streak_correct += 1`, `streak_wrong = 0`, `difficulty_estimate += min(0.3, 0.1 + streak_correct * 0.05)`.
- Wrong answer: `streak_wrong += 1`, `streak_correct = 0`, `difficulty_estimate -= min(0.3, 0.1 + streak_wrong * 0.05)`.
- Timeout: treat as wrong, but smaller decrease (`-0.05`).
- Clamp `difficulty_estimate` to `[0.5, 4.5]`.

### F4: Immediate Feedback

**UI flow:**
- Student selects option → clicks "Submit".
- API responds with: `is_correct`, `correct_answer`, `explanation`, `misconception_note` (if applicable).
- Show green check or red cross.
- Display explanation below. Use MathJax or plain text for formulas.
- "Next Question" button becomes active.

**Backend:**
- Record `Attempt` row with timing, correctness, selected answer, mark snapshot.
- Update `student_marks` for the topic.

### F5: Progressive Hints

**Levels:**
1. **Level 1 — Prompt:** Vague nudge (e.g., "Think about what happens to the sign when you subtract a negative.").
2. **Level 2 — Scaffold:** More specific guidance (e.g., "Rewrite the expression as: 5 + (+3).").
3. **Level 3 — Worked Example:** Full step-by-step solution shown.

**Data source:**
- Each generated question must include `hints: [level1, level2, level3]`.
- If missing, show generic topic-level hint.
- Track `hint_requests` with level and whether it was before/after answer.

### F6: Session Summary

**Display after 10 questions or when student clicks "End Session":**
- Questions attempted
- Accuracy %
- Longest correct streak
- Time spent
- Topics/concepts practiced
- Suggested next topic or review items

**Persistence:**
- Session summary stored in DB and returned to browser.
- Stored in `localStorage` as `last_session_summary` for instant replay.

### F7: Spaced Repetition Queue

**Simplified MVP approach:**
- Maintain a `review_queue` array in `localStorage`.
- When a question is answered incorrectly, add `{question_id, due_at}` with `due_at = now + 10 minutes`.
- During a new session, if any review items are due, offer "Review Due Questions" option.
- Cross-session persistence via `localStorage`; server-side backup optional.

**Scheduling:**
- 1st wrong: due in 10 minutes
- 2nd wrong: due in 1 day
- 3rd wrong: due in 3 days

### F8: Pedagogical Dimension Selector

**Approach:**
- On topic selection, show 4 dimension cards.
- Default selection: "Step-by-Step Clarity" (Anti-Gravity).
- Student can switch dimensions between sessions; within a session, dimension is fixed.
- Filter question pool by selected dimension's `prompt_dimension` field.

---

## 6. API Contract (MVP)

```
POST /api/learn/start
  Body: { topic_slug, dimension }
  Returns: { session_id, student_token, first_question }

POST /api/learn/answer
  Header: X-Student-Token
  Body: { session_id, question_id, selected_answer, time_ms }
  Returns: { is_correct, correct_answer, explanation, next_question, mark }

POST /api/learn/hint
  Header: X-Student-Token
  Body: { session_id, question_id, level }
  Returns: { hint_text }

POST /api/learn/end
  Header: X-Student-Token
  Body: { session_id }
  Returns: { summary }

GET  /api/learn/review-due
  Header: X-Student-Token
  Returns: { due_count, due_questions }
```

---

## 7. Data Model Additions for MVP

Based on `dfs-04-adaptive-database-schema.md`, the MVP requires only these tables to be implemented first:

1. `students` — token-based identity
2. `topics` — already exists; needs `description` and `display_order`
3. `questions` — pointer to generated content
4. `student_marks` — per-topic Mark state
5. `sessions` — practice session metadata
6. `attempts` — immutable answer events
7. `hint_requests` — hint usage events

**Deferred post-MVP:** `concepts`, `misconceptions`, `spaced_repetition_items`, `game_sessions`, `achievements`.

---

## 8. Success Metrics for MVP

| Metric | Target | Why |
|--------|--------|-----|
| Session completion rate (≥5 questions) | >60% | Validates engagement |
| Hint usage rate | 20–40% | Validates scaffolding usefulness |
| Accuracy trend over session | Flat or rising | Validates adaptive selection |
| Return within 24h | >15% | Validates motivation |
| Page load time | <2s | Validates performance |
| Runtime LLM cost | ₹0 | Validates cost constraint |

---

## 9. Open Questions for Next DFS

1. What percentage of generated questions have usable `hints` arrays?
2. Should the adaptive engine update marks synchronously or asynchronously?
3. How do we handle `localStorage` clearing / cross-device sessions?
4. What is the exact UI for switching dimensions mid-session vs. between sessions?
5. Do we need a simple "diagnostic" placement session before adaptive practice?

---

## 10. References

[^1]: FasterCapital. (n.d.). *Defining Your MVP Goals And Objectives*. https://fastercapital.com/topics/defining-your-mvp-goals-and-objectives.html

[^2]: Financial Model Excel. (2025). *What Are the Startup Costs for an AI Tutoring Platform?* https://financialmodelexcel.com/blogs/cost-open/ai-tutoring-platform-education

[^3]: Knack. (2026). *How to Build a Language Learning App: A Comprehensive Guide*. https://www.knack.com/blog/how-to-build-language-learning-app/

[^4]: FasterCapital. (n.d.). *How to calculate MVP cost for a education product*. https://fastercapital.com/content/How-to-calculate-MVP-cost-for-a-education-product--A-framework-and-checklist.html

[^5]: Qrolic Technologies. (2026). *Language Learning Platform Features*. https://qrolic.com/blog/language-learning-website-essential-features/

[^6]: Sessink, O. (2007). *An Adaptive Feedback Framework to Support Reflection, Guiding and Tutoring*. Journal of Interactive Learning Research.

[^7]: Aleven, V., McLaren, B., Roll, I., & Koedinger, K. (2016). *Instruction Based on Adaptive Learning Technologies*. In Handbook of Research on Learning and Instruction (2nd ed.).

[^8]: WiFi Talents. (2026). *Best Adaptive Math Software | 2026 Edition*. https://wifitalents.com/best/adaptive-math-software/

[^9]: Astra AI. (2025). *What Is AI Tutoring? Benefits, Examples, Math Focus*. https://astra-ai.co/blog/what-is-ai-tutoring/

[^10]: Narciss, S., & Huth, K. (2004). *How to design informative tutoring feedback for multimedia learning*. In Instructional Design for Multimedia Learning.

[^11]: Mitrovic, A., & Martin, B. (2000). *SQL Tutor*. https://doi.org/10.1007/3-540-45108-0_28

[^12]: IEEE. (2023). *Using Differential Privacy to Define Personal, Anonymous, and Pseudonymous Data*. https://ieeexplore.ieee.org/document/10268936

[^13]: U.S. Federal Trade Commission. *Children's Online Privacy Protection Rule (COPPA)*. https://www.ftc.gov/business-guidance/privacy-security/childrens-privacy

[^14]: Settles, B., & Meeder, B. (2016). *A Trainable Spaced Repetition Model for Language Learning*. ACL 2016.

[^15]: Third Space Learning. (2025). *Voice-Based AI Math Tutoring vs. Text-Based*. https://thirdspacelearning.com/us/blog/voice-based-ai-maths-tutoring-vs-text-based/
