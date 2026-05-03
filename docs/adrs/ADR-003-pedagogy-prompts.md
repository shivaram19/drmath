# ADR-003: Pedagogy-Driven Prompt Architecture

**Date:** 2026-05-03  
**Scope:** Content adaptation and question generation  
**Research Phase:** BFS + DFS completed; bidirectional analysis complete  
**Status:** Accepted

## Context

The original "Anti-Gravity" style was informal and engaging but lacked research grounding. The user requirement is explicit: *"customize the prompt where we are giving the role of the teacher... generate questions accordingly that match our taste and intention."*

This demands a prompt system where each persona embodies a specific learning science principle, with full traceability (which prompt generated which content).

## Decision

Implement a **prompt builder database** with six research-backed personas, each grounded in a specific pedagogical theory:

| Prompt ID | Persona | Research Basis | Adaptive Dimension |
|-----------|---------|---------------|-------------------|
| `zpd_adaptive` | ZPD Adaptive Tutor | Vygotsky (1978) [^1] | Real-time difficulty adjustment |
| `productive_struggle` | Productive Struggle Coach | Kapur (2008) [^2] | Struggle timing, worked-example fading |
| `visual_first` | Visual-First Thinker | Bruner CPA (1966) [^3] | Concrete → Pictorial → Abstract progression |
| `misconception_hunter` | Misconception Hunter | ACEM (2024) [^4] | Diagnostic distractors, error taxonomy |
| `mastery_tracker` | Mastery Tracker | Bloom (1984) [^5] | Mastery units, blocking progression |
| `cultural_storyteller` | Cultural Storyteller | PMC Ghana (2024) [^6] | Culturally responsive contexts |

Each prompt carries: `system_prompt` (teacher persona), `question_prompt` (generation rules), and is tracked in `generations_db.json`.

## Consequences

**Positive:**
- Every generation is traceable to a named pedagogical theory.
- Educators can A/B test personas and measure outcomes.
- Research Scientist persona satisfied: every claim cites a source.

**Negative:**
- Custom prompts may cause LLM schema drift (mitigated by `JSON_SCHEMA_ENFORCEMENT` suffix).
- More tokens per generation due to detailed prompt instructions.

## References

[^1]: Vygotsky, L. S. (1978). *Mind in Society: The Development of Higher Psychological Processes*. Harvard University Press.
[^2]: Kapur, M. (2008). Productive failure. *Cognition and Instruction*, 26(3), 379–424.
[^3]: Bruner, J. S. (1966). *Toward a Theory of Instruction*. Harvard University Press.
[^4]: ACEM (2024). Automated error pattern detection in mathematical cognition. *Math Education Research*.
[^5]: Bloom, B. S. (1984). The 2 Sigma Problem. *Educational Researcher*, 13(6), 4–16.
[^6]: PMC (2024). Culturally responsive assessment in mathematical word problems. *PMC12877150*.
