# Research-First Covenant

**Date:** 2026-05-03  
**Scope:** All engineering and pedagogical decisions in the Dr. Math project  
**Status:** Mandatory

## The Covenant

Every architectural decision, prompt design, and UI choice in this project must be grounded in peer-reviewed research or canonical industry sources. Intuition is not sufficient.

## The Workflow

```
Decompose → BFS → DFS → Bidirectional → ADR → Code → Test → Commit
```

No code is written before the preceding steps are complete.

## Requirements

1. **Research before code.** For every feature, document the research phase in `docs/research/`.
2. **Citations for every claim.** Use numbered references to T1–T3 sources.
3. **ADRs for every architectural decision.** File at `docs/adrs/ADR-###-{topic}.md`.
4. **10-Persona Filter on every change.** Each change must satisfy all ten personas.
5. **No anti-patterns.** "Everyone does it" / "We'll fix it later" are violations.

## Persona Checklist

Before committing, verify:

- [ ] **Research Scientist:** Are all claims cited?
- [ ] **First-Principles Engineer:** Is this derived from axioms, not trends?
- [ ] **Distributed Systems Architect:** Will this scale or bottleneck?
- [ ] **Infrastructure-First SRE:** Is observability included?
- [ ] **Ethical Technologist:** Are privacy and accessibility considered?
- [ ] **Resource Strategist:** Is the TCO justified?
- [ ] **Diagnostic Problem-Solver:** Are root causes addressed, not symptoms?
- [ ] **Curious Explorer:** Is this documented in the lab notebook?
- [ ] **Clarity-Driven Communicator:** Is the commit message and ADR clear?
- [ ] **Inner-Self Guided Builder:** Is this the right thing to build?

## Violations

Violations of this covenant must be documented as technical debt in `docs/decisions/` with a remediation plan.
