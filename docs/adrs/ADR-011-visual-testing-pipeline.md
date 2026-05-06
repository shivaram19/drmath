# ADR-011: Dual-Persona Visual Testing Pipeline

**Date:** 2026-05-05  
**Scope:** All 11 Flutter screens, multi-viewport screenshot capture, and automated evaluation  
**Research Phase:** BFS-02, DFS-02, Bidirectional-02 completed  
**Status:** Accepted  
**Informed By:** ADR-010 (Mobile UI Pedagogy) — the rubric for evaluation  

---

## Context

ADR-010 defines 10 pedagogical design decisions (D1–D10) for every screen in the Dr. Math Flutter app. However, there is currently no automated mechanism to verify that implemented screens comply with these decisions. Manual code review catches syntax errors but misses visual hierarchy violations, color psychology errors, and cognitive load problems that only appear when a screen is rendered.

We need a pipeline that:
1. Captures every screen at multiple viewport sizes
2. Evaluates each screen against ADR-010's research-backed rubric
3. Validates layout correctness against our design token system
4. Produces actionable per-page reports with citations and remediation

This ADR records the architectural decision for such a pipeline.

---

## Decision

We will build a **dual-persona visual testing pipeline** with the following architecture:

### Capture Layer
- **Tool:** Playwright (Python) against Flutter web build
- **Output:** 55 PNG screenshots (11 screens × 5 viewports)
- **Viewports:** 375×812, 390×844, 430×932, 768×1024, 1024×768
- **Rationale:** Playwright provides arbitrary viewport sizing and interaction scripting at zero cost. The web build is already functional (see `scripts/web_screenshot.py`).

### Persona 1: Screenshot Auditor
- **Tool:** Python Pillow + design token manifest JSON
- **Function:** Pixel-level validation of colors, typography, spacing, touch target sizes
- **Determinism:** 100% deterministic, zero external dependencies
- **Rationale:** Rule-based auditing is fast (~3s for 55 shots), precise, and satisfies the Infrastructure-First SRE persona's observability mandate.

### Persona 2: UI/UX Engineer
- **Tool:** Structured rubric heuristics (Python) + optional Gemini Flash LLM
- **Function:** Qualitative evaluation of cognitive load, visual hierarchy, navigation clarity, accessibility, pedagogy compliance
- **Determinism:** Deterministic core; optional non-deterministic LLM enhancement
- **Rationale:** Semantic evaluation (e.g., "does this screen feel cluttered?") requires judgment. LLM vision provides this at ~$0.03/run, but the pipeline functions without it per Decision Authority #2 (open-source preference).

### Reporting Layer
- **Tool:** Python Jinja2 → Markdown + JSON
- **Output:** `reports/visual-test-YYYY-MM-DD/summary.md` + per-screen directories
- **Rationale:** Markdown is human-readable in any editor; JSON is machine-parseable for future CI integration.

---

## Consequences

### Positive
- Every screen is evaluated against ADR-010's research-backed criteria automatically.
- Per-page reports identify root cause (cognitive overload, touch target violation, color error) with citations.
- Zero-cost core pipeline satisfies Resource Strategist; optional LLM satisfies Curious Explorer.
- File-based, stateless architecture is CI-ready for future GitHub Actions integration.
- Design token manifest JSON creates a single source of truth for `AppColors`, `AppTheme`, and `PedagogyTokens`.

### Negative
- Flutter web build (CanvasKit) may render slightly differently from Android/iOS (Impeller/Skia). Screenshots are representative, not pixel-identical to native builds.
- Playwright interaction scripting (tapping buttons to navigate) can be brittle if widget text changes.
- Optional LLM evaluation is non-deterministic and may produce inconsistent results across model updates.
- 55 screenshots per run consume ~20MB disk space per execution (acceptable; reports are gitignored).

---

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|-----------------|
| **Applitools / Percy SaaS** | Proprietary lock-in, ~$0.50/run, no pedagogy-specific rules. Violates Resource Strategist and Decision Authority #2. |
| **Firebase Test Lab** | $2/run for 55 screenshots. Physical devices are overkill for layout audit. Violates Resource Strategist. |
| **Golden files (`matchesGoldenFile`)** | Platform-dependent, manages 55 references poorly, cannot evaluate "quality." Rejected for primary capture. |
| **integration_test screenshots** | One viewport per test invocation; 55 invocations impractical. Emulator overhead too slow. |
| **Mobilerun (physical device)** | ~$0.15/run, one device at a time, cannot test 5 viewports. Excellent for E2E but wrong tool for visual audit. |
| **No visual testing** | Manual review misses regressions. Violates Infrastructure-First SRE and all 10 personas. |

---

## References

[^1]: Sweller, J. (1988). Cognitive Load During Problem Solving: Effects on Learning. *Cognitive Science*, 12(2), 257–285. (Cognitive Load Theory — D1, D6)
[^2]: Miller, G. A. (1956). The Magical Number Seven, Plus or Minus Two. *Psychological Review*, 63(2), 81–97. (Working memory capacity — D1, cognitive load rubric)
[^3]: Elliot, A. J., & Maier, M. A. (2014). Color and Psychological Functioning: A Review. *Annual Review of Psychology*, 65, 95–120. (Color psychology — D4, color rubric)
[^4]: Parhi, P., et al. (2006). Target Size Study for One-Handed Thumb Use on Small Touchscreen Devices. *MobileHCI'06*. (Touch targets — D3, touch target rubric)
[^5]: Nielsen, J. (2016). *Hamburger Menus and Hidden Navigation Hurt UX Metrics*. Nielsen Norman Group. (Navigation — D5, navigation rubric)
[^6]: CAST (2018). *Universal Design for Learning Guidelines version 2.2*. http://udlguidelines.cast.org (UDL — D10, accessibility rubric)
[^7]: Microsoft. (2024). *Playwright Documentation*. https://playwright.dev/python/docs/screenshots (Screenshot capture)
[^8]: Pillow Contributors. (2024). *Pillow Documentation*. https://pillow.readthedocs.io (Pixel analysis)
[^9]: Google. (2024). *Gemini API Pricing*. https://ai.google.dev/pricing (LLM vision cost model)
[^10]: Beyer, B., et al. (2016). *Site Reliability Engineering: How Google Runs Production Systems*. O'Reilly. (Observability, toil reduction)
