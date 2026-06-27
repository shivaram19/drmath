# Bidirectional-04: Cross-Domain Impact Analysis — Nursing Module

**Date:** 2026-05-13  
**Scope:** How the `/nursing` module impacts and is impacted by other domains: Dr. Math math pipeline, infrastructure, content pipeline, future products, and user trust.  
**Research Phase:** Bidirectional — cross-domain impact analysis  
**Author:** Kimi Code CLI  

## 1. Impact on Dr. Math Math Pipeline

### Positive
- Nursing module brings adult learners to the platform, expanding user base.
- Reuses authentication/deployment infrastructure, improving ROI.

### Negative
- Risk of code leakage: nursing routes could accidentally affect math routes.
- UI/UX expectations may diverge (children vs. adults).
- Pre-commit hooks and tests must cover both modules.

### Mitigation
- Strict namespace isolation: all nursing code under `web/*nursing*` paths.
- Separate test files with clear naming.
- No shared mutable state between modules.

## 2. Impact on Content Pipeline

### Positive
- Nursing content provides a second use-case for the LLM generation pipeline.
- Validates the pipeline's ability to handle non-math domains.

### Negative
- Medical content requires higher verification standards than math.
- Current pipeline is tuned for Class VII math pedagogy; needs nursing persona.
- Risk of mixing math and nursing artifacts in `output/`.

### Mitigation
- Nursing outputs use `nursing_*.json` naming convention.
- Verification workflow requires human or textbook review.
- Separate prompt templates for nursing in `pipeline/prompts/`.

## 3. Impact on Infrastructure

### Positive
- No new servers, databases, or runtime dependencies (v1).
- Docker compose can serve both modules simultaneously.

### Negative
- `output/nursing_staff_nurse_output.json` increases repo size slightly.
- Future scale may require DB-backed question storage.
- PDF export may require a new Python dependency.

### Mitigation
- Keep JSON files in `output/` (already gitignored in pre-commit for runtime artifacts, but seed bank should be committed).
- Monitor container memory; nursing module is stateless.
- If PDF library is added, document TCO in ADR.

## 4. Impact on Brand & User Trust

### Positive
- Demonstrates platform can adapt to different exam needs.
- Helps a real person (user's mother), building emotional investment.

### Negative
- A wrong medical answer could damage trust more than a wrong math answer.
- If nursing module looks unprofessional, it hurts the whole Dr. Math brand.

### Mitigation
- Medical disclaimer on every page.
- Visible "Report question" and source tags.
- Polished, mobile-first UI.

## 5. Impact on Future Products

### Positive
- Module can be cloned for other state staff-nurse exams (AP, Karnataka, TN).
- Adaptive diagnostic model can be reused for other Dr. Math subjects.
- PDF export feature can be reused for math worksheets.

### Negative
- Maintaining multiple exam syllabi increases long-term maintenance.
- Telugu i18n infrastructure may be needed for other Indian languages.

### Mitigation
- Keep exam pattern config-driven from the start.
- Build i18n with a simple key-value JSON pattern that supports future languages.

## 6. Cross-Cutting Concerns

| Concern | Nursing Requirement |
|---------|---------------------|
| Accessibility | Telugu tooltips, large touch targets, screen-reader-friendly labels |
| Privacy | Anonymous; no account needed |
| Ethics | Medical disclaimer, verified content, report mechanism |
| Observability | Session logs, report logs, status endpoint |
| Cost | Zero API calls in v1; static JSON |
| Maintainability | Modular code, comprehensive tests |

## 7. Decision Implications

The nursing module should be treated as a **separate product** that happens to share infrastructure with Dr. Math. It needs its own:
- Content verification workflow.
- UI/UX language.
- Success metrics.
- Maintenance owner.

Failing to respect this separation will create coupling that hurts both products.
