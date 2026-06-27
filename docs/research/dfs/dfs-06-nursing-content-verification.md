# DFS-06: Content Verification Strategy for Medical/Nursing MCQs

**Date:** 2026-05-13  
**Scope:** How to source, generate, and verify MCQs for a high-stakes nursing recruitment exam.  
**Research Phase:** DFS — depth-first quality/safety deep-dive  
**Author:** Kimi Code CLI  

## 1. Why Medical Content Is Different from Math Content

A wrong math question is embarrassing. A wrong medical question can:
- Teach dangerous patient-care practices.
- Mislead a candidate in a high-stakes recruitment exam.
- Erode trust in the practice tool.

Therefore verification is not optional — it is a safety requirement.

## 2. Content Sources (Hierarchy of Trust)

| Tier | Source | Examples | Use |
|------|--------|----------|-----|
| **T1** | Official / statutory | INC GNM syllabus, MHSRB notification, standard nursing textbooks | Seed bank, canonical answers |
| **T2** | Peer-reviewed / canonical | Nursing journals, WHO/ICMR guidelines, standard texts (Brunner & Suddarth, Lewis) | Reference verification |
| **T3** | Coaching / PYQ aggregators | Testbook, Adda247, FreshersNow | Pattern reference, not primary source |
| **T4** | LLM-generated | GPT-4o-mini output | Raw material only; must be reviewed |

## 3. Verification Pipeline

Every MCQ carries a `verification_status`:

```
unverified → reviewed → verified → deprecated
```

### Stage 1: Source tagging
- Each question is tagged with its source(s) and concept reference.

### Stage 2: Dual review
- **Clinical review:** Does the answer align with T1/T2 sources?
- **Exam-pattern review:** Does the wording/style match MHSRB/TSPSC MCQs?

### Stage 3: Crowd flag
- UI includes "Report question" button.
- Flagged questions move to `review_pending`.

### Stage 4: Periodic audit
- Re-run a sample of verified questions against updated textbooks/guidelines annually.

## 4. Seed Bank v1 Approach

For the initial launch, we avoid LLM-generated clinical questions. We:
1. Derive questions directly from the INC GNM syllabus topics.
2. Reference standard nursing facts (vital sign ranges, normal values, infection-control steps).
3. Mark every question as `reviewed` with source tag `INC-GNM-syllabus`.
4. Avoid controversial or region-specific protocols where guidelines differ.

## 5. LLM Generation v2 Approach

When expanding the bank:
1. Prompt the LLM with a specific syllabus subtopic and a reference fact.
2. Require the LLM to cite the fact it used.
3. A nurse reviewer (human or verified textbook) approves each generated question.
4. Do not auto-promote LLM output to `verified`.

## 6. Safety UX

- Disclaimer: "This is a practice aid based on publicly available syllabi. Always cross-check with official notifications and textbooks."
- Report button on every question.
- No questions on emergency procedures that could be acted upon in real life without professional training.

## 7. References

[^1]: Indian Nursing Council. (2015). *Syllabus for General Nursing and Midwifery*. https://www.iminursing.in/gnm-syllabus.pdf
[^2]: World Health Organization. (2020). *Guidelines on Core Components of Infection Prevention and Control Programmes at the National and Acute Health Care Facility Level*. WHO.
[^3]: Brunner & Suddarth's *Textbook of Medical-Surgical Nursing* (15th ed.). Wolters Kluwer.
