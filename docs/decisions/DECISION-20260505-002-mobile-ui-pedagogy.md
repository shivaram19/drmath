## DECISION-20260505-002: Mobile UI Pedagogy Implementation

**Date:** 2026-05-05  
**Proposal:** Apply research-backed UI/UX principles (Cognitive Load Theory, CPA, UDL, SDT) to all 11 Flutter screens.  
**Risk Level:** Medium — Affects every user interaction; requires tradeoffs between visual polish and cognitive fidelity.  
**Final Decision:** Approved  

### Council Deliberation

| Persona | Stance | Key Point |
|---|---|---|
| Research Scientist | Endorse | DFS-01 cites 24 peer-reviewed sources; all claims traceable to T1–T2 evidence. |
| First-Principles Engineer | Endorse | Derives from axioms: children have limited working memory → one question per screen. |
| Distributed Systems Architect | Endorse | No architecture change; pure UI layer. No blocking concern. |
| Infrastructure-First SRE | Endorse | Accessibility-first design reduces support burden (WCAG compliance out-of-box). |
| Diagnostic Problem-Solver | Endorse | Root cause of poor retention is cognitive overload, not "more worksheets." D1–D10 address this. |
| Ethical Technologist | Endorse | D4 (pink not red error) and D8 (no timers) directly reduce math anxiety. COPPA-safe anonymous auth maintained. |
| Resource Strategist | Endorse | No new dependencies required. Research is free; implementation uses existing Flutter primitives. |
| Curious Explorer | Endorse | Proposed A/B test: measure session duration with vs. without visible timers (hypothesis: no-timer wins). |
| Clarity-Driven Communicator | Endorse | ADR-010 written. DFS-01 research doc written. Code comments cite research at point of use. |
| Inner-Self Guided Builder | Endorse | Removing hamburger menu and coins serves the child's deeper need (wayfinding, intrinsic motivation). |

### Rationale

Unanimous approval. The Council confirmed that visual fidelity must be subordinate to cognitive fidelity for an educational product serving 12–13 year olds. Every screen now carries research-backed inline comments and architectural justification.

### Dissent Recorded

None.

### Action Items

- [x] ADR written: `docs/adrs/ADR-010-mobile-ui-pedagogy.md`
- [x] Research doc written: `docs/research/dfs-01-flutter-ui-pedagogy.md`
- [x] Decision log written: `docs/decisions/DECISION-20260505-002-mobile-ui-pedagogy.md`
- [x] Code annotated with research citations
- [ ] Run A/B test on timer visibility (deferred to post-MVP)
