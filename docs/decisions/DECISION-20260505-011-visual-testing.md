# DECISION-20260505-011: Dual-Persona Visual Testing Pipeline

**Date:** 2026-05-05  
**Topic:** Architecture for visual testing of the Dr. Math Flutter client  
**Scope:** All 11 screens, 5 viewport sizes, 2 evaluation personas  
**Informed By:** BFS-02, DFS-02, Bidirectional-02  
**ADR:** ADR-011 (companion document)  

---

## Council of Ten Deliberation

### Question
Should we build a dual-persona visual testing pipeline (UI/UX Engineer + Screenshot Auditor) using Playwright screenshot capture, Pillow pixel audit, and optional Gemini Flash LLM evaluation?

### Deliberation Process

All 10 personas reviewed BFS-02, DFS-02, and Bidirectional-02. Each persona provided a stance with a key concern or endorsement point. No persona blocked the proposal after concerns were addressed.

---

### Persona Stances

| # | Persona | Stance | Key Point | Concern Addressed |
|---|---------|--------|-----------|-------------------|
| 1 | Research Scientist | ✅ Endorse | Every rubric item cites ADR-010 or T1/T2 source. LLM evaluation is constrained by structured rubric, not open-ended generation. | — |
| 2 | First-Principles Engineer | ✅ Endorse | Evaluation criteria derived from cognitive axioms (Miller 5±2, Elliot & Maier color psychology, Parhi touch targets), not "what looks good." | — |
| 3 | Distributed Systems Architect | ✅ Endorse | Stateless pipeline: screenshots are immutable inputs; persona outputs are pure functions of (screenshot + rubric + tokens). Parallelizable. Idempotent. | Initial concern: LLM calls are non-deterministic. Addressed: LLM is optional; deterministic rubric is the core. |
| 4 | Infrastructure-First SRE | ✅ Endorse | Structured JSON trace + markdown report per run. Trace ID → commit SHA. Exit codes for future CI gate. | Initial concern: Report storage and retention. Addressed: File-based outputs in `reports/`, gitignored, with timestamp. |
| 5 | Ethical Technologist | ✅ Endorse | Demo data only (no PII in screenshots). Accessibility is a scored rubric item, not afterthought. LLM token waste minimized via hash-based caching. | — |
| 6 | Resource Strategist | ✅ Endorse | Core pipeline: $0 (Playwright + Pillow + Jinja2). Optional LLM: ~$0.03/run. No SaaS lock-in. Rejected Applitools ($0.50/run) and Firebase Test Lab ($2/run). | — |
| 7 | Diagnostic Problem-Solver | ✅ Endorse | Every failure includes root cause (e.g., "9 chunks visible exceeds Miller's 7±2 limit") and remediation, not just "looks wrong." | — |
| 8 | Curious Explorer | ✅ Endorse | Lab notebook in `docs/research/`. Experiment track: compare LLM vs. rubric accuracy, cost per run, false positive rate over time. | — |
| 9 | Clarity-Driven Communicator | ✅ Endorse | ADR-011 documents architecture. Per-screen markdown reports. Priority-ranked remediation backlog. Conventional commits cite research. | — |
| 10 | Inner-Self Guided Builder | ✅ Endorse | Pipeline prioritizes cognitive fidelity over pixel perfection. Catches pedagogy violations (red backgrounds, visible timers, hamburger menus) even if they "look good." | — |

### Unanimous Approval

**All 10 personas endorse the proposal.** No blocking concerns remain.

---

## Decision

**APPROVED:** Build the dual-persona visual testing pipeline as specified in ADR-011.

**Implementation order:**
1. Export design tokens to JSON
2. Build `screenshot_capture.py` (11 screens × 5 viewports)
3. Build `screenshot_auditor.py` (Pillow-based token validation)
4. Build `ux_evaluator.py` (structured rubric + optional LLM)
5. Build `report_builder.py` (aggregation + summary)
6. Build `visual_test_pipeline.py` (orchestrator)
7. Write skill file `testing/visual-testing.md`
8. Dogfood: run on current app, document findings

**Quality gate (future):** When CI integration is added (Phase 2), pipeline must:
- Run in < 3 minutes
- Cost <$0.10/run
- Produce exit code 0 (pass) or 1 (fail)
- Block PR on accessibility or pedagogy violations only (not pixel shifts)

---

## References

- BFS-02: Visual Testing Landscape
- DFS-02: Visual Testing Deep-Dive
- Bidirectional-02: Cross-Domain Impact Analysis
- ADR-011: Visual Testing Pipeline (companion)
