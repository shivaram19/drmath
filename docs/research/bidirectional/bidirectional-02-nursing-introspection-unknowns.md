# Bidirectional-02: Introspection of Unknowns — Nursing Module

**Date:** 2026-05-13  
**Scope:** Surface and validate assumptions before building the `/nursing` module.  
**Research Phase:** Bidirectional — cross-domain impact / meta-cognitive analysis  
**Author:** Kimi Code CLI  

## 1. Self-Interview: What am I assuming?

### Q1: Is MHSRB the right body?
**Assumption:** The user's mother is preparing for MHSRB Telangana Staff Nurse / Nursing Officer recruitment.  
**Why it might be wrong:** She might be preparing for TSPSC Staff Nurse, DMHO contract staff nurse, a specific hospital recruitment (NIMS/Osmania/Gandhi), or even ANM/GNM entrance.  
**Risk:** Building the wrong syllabus tree and exam pattern wastes effort.

### Q2: Is English-only the right content language?
**Assumption:** Because MHSRB paper is English-only, questions should be in English with Telugu UI only.  
**Why it might be wrong:** Many Telangana nursing candidates study in Telugu medium. Bilingual questions (English + Telugu) may improve comprehension and retention, even if the exam is English.  
**Risk:** The mother may struggle with English-only medical terms.

### Q3: Is my adaptive queue actually useful?
**Assumption:** A 4-dimensional heuristic (accuracy, speed, confidence, consistency) will prioritise study better than random practice.  
**Why it might be wrong:** No data yet. The confidence dimension may be noise. A simpler algorithm (e.g., SM-2 or even "lowest accuracy topic") might perform equally well with less complexity.  
**Risk:** Over-engineering before validation.

### Q4: Is the seed bank accurate?
**Assumption:** 104 hand-curated questions from standard GNM sources are correct.  
**Why it might be wrong:** I am not a nurse. Some answers may be outdated or context-dependent (e.g., WHO guideline changes, national programme names).  
**Risk:** Teaching wrong facts.

### Q5: Is a SOLID sub-package necessary?
**Assumption:** Separating `services/`, `repositories/`, `domain/` is the right structure.  
**Why it might be wrong:** The existing Dr. Math codebase is small and monolithic. Adding 7 new packages may be over-engineering for a prototype.  
**Risk:** Slower delivery and cognitive load.

### Q6: Does she need a web app right now?
**Assumption:** A browser-based `/nursing` module is the best delivery.  
**Why it might be wrong:** If she only uses a smartphone and has poor internet, a downloadable PDF question bank or a simple static HTML page might be more useful today.  
**Risk:** Building something she won't use.

### Q7: What is the real exam pattern right now?
**Assumption:** 80 MCQs, 60 min, English, no negative marking.  
**Why it might be wrong:** Exam patterns change. The latest MHSRB notification may have a different pattern.  
**Risk:** Mock tests train her for the wrong format.

## 2. What must I discover?

1. Latest official MHSRB / TSPSC notification for staff nurse.
2. Any freely available previous-year papers for Telangana staff nurse.
3. Research on adaptive learning / diagnostic testing for high-stakes exams.
4. Existing open nursing MCQ datasets.
5. Evidence on bilingual (English + regional language) MCQ effectiveness.
6. Best-practice folder structure for small FastAPI feature modules.

## 3. First-Principles Reframing

The deepest need is not "a web app." It is: **maximise the probability that the user's mother passes the exam.**

Everything else is a tactic. If a simpler tactic works better, we should use it.
