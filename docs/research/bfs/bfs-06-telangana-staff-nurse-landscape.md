# BFS-06: Telangana Staff Nurse Recruitment — Landscape Scan

**Date:** 2026-05-13  
**Scope:** Add a `/nursing` practice module to Dr. Math for a Telangana government staff-nurse recruitment candidate.  
**Research Phase:** BFS — breadth-first landscape mapping  
**Author:** Kimi Code CLI  

## 1. Problem Statement

The user's mother is preparing for a Telangana government nursing recruitment examination. We need to:

1. Identify the exact conducting body and exam mechanics.
2. Decompose the syllabus into subjects → topics → subtopics → concepts.
3. Source or generate verified MCQs in the Dr. Math JSON format.
4. Deploy a browser-based practice UI (`/nursing`) with diagnostic assessment, topic practice, and full-length mocks.

## 2. Candidate Requirements (validated)

| Dimension | User Choice |
|-----------|-------------|
| Exam type | Recruitment / Staff Nurse |
| State | Telangana |
| Content mix | Official previous-year style + syllabus-derived MCQs |
| Language | English + Telugu |
| Host | Add `/nursing` module to existing Dr. Math |
| Features | Topic-wise MCQ practice + full-length mock tests |
| Assessment philosophy | Multi-dimensional diagnostic: capabilities, weak areas, fast areas |

## 3. Conducting Bodies & Exam Patterns

### 3.1 MHSRB Telangana — Staff Nurse / Nursing Officer

- **Body:** Medical & Health Services Recruitment Board, Telangana (`mhsrb.telangana.gov.in`).
- **Post:** Staff Nurse / Nursing Officer.
- **Mode:** OMR-based or Computer-Based Test (CBT).
- **Pattern:** 80 MCQs, 80 marks, 1 hour, **English only**, no negative marking.
- **Selection:** 80 points written exam + 20 points for state-government hospital/institution contract/outsourced service.
- **Syllabus:** GNM-level nursing subjects.

Sources: freshersnow.com, careerpower.in, testbook.com [^1][^2][^3].

### 3.2 TSPSC — Staff Nurse

- **Body:** Telangana State Public Service Commission (`tspsc.gov.in`).
- **Pattern:** Two papers.
  - Paper I: General Studies — 50 questions, 50 marks, English & Telugu.
  - Paper II: Nursing (GNM level) — 100 questions, 100 marks, English.
  - Total: 150 marks, 2.5 hours.
- **Selection:** 70% written exam + 30% government-service experience.

Source: testbook.com [^4].

### 3.3 Decision

Primary target: **MHSRB Telangana Staff Nurse / Nursing Officer**, because it is the current, recurring recruitment and matches the user's "government exam" framing. The module will optionally include a TSPSC-style General Studies section for future expandability.

## 4. Syllabus Decomposition (MHSRB GNM-level)

Based on the INC GNM syllabus [^5] and coaching-aggregated MHSRB syllabi [^1][^3][^4]:

1. **Anatomy & Physiology**
2. **Fundamentals of Nursing**
3. **Microbiology**
4. **Pharmacology**
5. **Medical-Surgical Nursing**
6. **Community Health Nursing**
7. **Mental Health / Psychiatric Nursing**
8. **Child Health / Pediatric Nursing**
9. **Midwifery & Gynecological Nursing**
10. **Nutrition & Dietetics**
11. **Professional Trends / Nursing Administration & Ward Management**
12. **First Aid & Emergency Nursing**
13. **General Studies / GK** (optional, for TSPSC and breadth)

## 5. Content Strategy

- **Phase 1 (now):** Hand-curate a high-quality seed bank of ~200 MCQs covering the top subtopics. This avoids runtime LLM cost and guarantees accuracy for the user's mother.
- **Phase 2:** Use the existing Dr. Math LLM pipeline to generate additional questions per topic, with nursing-specific prompts and a medical-nurse reviewer persona.
- **Safety:** Medical content has higher stakes than math. Every seed question will include a cited source/concept tag; LLM-generated questions will require human review before promotion to "verified".

## 6. Product Design

### 6.1 Multi-dimensional diagnostic

The diagnostic will probe across:
- **Subject breadth** (which subjects are known vs unknown)
- **Accuracy** (correct/incorrect)
- **Speed** (time per question)
- **Confidence** (self-reported certainty)
- **Consistency** (performance across similar questions)

Output: a "capability map" stored in `localStorage` that drives the adaptive queue.

### 6.2 Practice modes

1. **Diagnostic Test** — 20 questions across all major subjects.
2. **Topic Practice** — pick a subject/topic, practice questions.
3. **Full-Length Mock** — 80 questions, 60 minutes, MHSRB pattern.
4. **Weak Area Drill** — automatically generated from lowest-accuracy topics.

### 6.3 Progress tracking

- Anonymous token in `localStorage` (same pattern as Dr. Math MVP).
- Per-topic accuracy, average time, streak.
- No server-side user accounts for v1.

## 7. References

[^1]: FreshersNow, "Telangana Staff Nurse Previous Question Papers PDF Download", 2024. https://www.freshersnow.com/mhsrb-telangana-staff-nurse-previous-questions-papers/
[^2]: CareerPower, "MHSRB Telangana Nursing Officer Recruitment 2024", 2024. https://www.careerpower.in/blog/mhsrb-telangana-nursing-officer-recruitment-2024
[^3]: Testbook, "MHSRB Staff Nurse Syllabus & Exam Pattern 2024". https://testbook.com/mhsrb-staff-nurse/syllabus-exam-pattern
[^4]: Testbook, "TSPSC Staff Nurse Syllabus - Download PDF, Exam Pattern & More". https://testbook.com/tspsc-staff-nurse/syllabus-exam-pattern
[^5]: Indian Nursing Council, "GNM Syllabus", 2015. https://www.iminursing.in/gnm-syllabus.pdf
