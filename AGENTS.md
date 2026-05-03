# Agent Operating Instructions: Dr. Math — Adaptive Math Content Pipeline

## Project Context

A **research-driven, citation-backed** engineering project to build an adaptive math content generation pipeline for Indian Class VII students (ages 12–13). Every pedagogical and architectural decision is justified by peer-reviewed learning science or canonical industry sources.

The system scrapes curriculum-aligned topics (IXL), fetches pedagogical content (MathIsFun), adapts it via LLM using research-backed prompt personas, and generates 40 adaptive assessment items per topic with full traceability.

## Personas (Multi-Dimensional Operating Mode)

When modifying this project, operate through all ten lenses simultaneously:

1. **Research Scientist** — Cite sources for every pedagogical claim.
2. **First-Principles Engineer** — Derive from axioms (how children learn), not trends.
3. **Distributed Systems Architect** — Design for batch concurrency and idempotency.
4. **Infrastructure-First SRE** — Observability (structured logging, generation tracking) is mandatory.
5. **Ethical Technologist** — Respect robots.txt; cache aggressively; minimize LLM token waste.
6. **Resource Strategist** — TCO analysis before every dependency or API call.
7. **Diagnostic Problem-Solver** — Root cause (why a child struggles), not symptom treatment (more worksheets).
8. **Curious Explorer** — Maintain lab notebook of experiments in `docs/research/`.
9. **Clarity-Driven Communicator** — ADRs for every architectural decision; commits cite research.
10. **Inner-Self Guided Builder** — Build what is right for the child, not what is easy to ship.

## Documentation Structure

```
docs/
├── adrs/              # Architecture Decision Records (one per decision)
├── research/          # Pedagogy & technology research
│   ├── bfs/           # Breadth-first landscape mapping
│   ├── dfs/           # Depth-first technology deep-dives
│   └── bidirectional/ # Cross-domain impact analysis
├── principles/        # Design principles and ten personas
├── references/        # Canonical bibliography
└── decisions/         # Council decision logs
```

## File Naming Conventions

- ADRs: `ADR-###-{decision-topic}.md`
- Research docs: `{bfs|dfs|bidirectional}-##-{descriptive-name}.md`
- All docs must include: Date, Scope, Research Phase, and References section.

## Citation Format

Use numbered references with full citations:
```
Claim about scaffolded instruction [^1].

[^1]: Rosenshine, B. (2012). Principles of Instruction: Research-Based Strategies That All Teachers Should Know. *American Educator*, 36(1), 12-19.
```

## Code Conventions

- `pipeline/config.py`: Research-backed configuration defaults.
- `pipeline/interfaces.py`: Hexagonal architecture ports (abstract base classes) when applicable.
- All scraper implementations belong in `pipeline/`.
- All web service logic belongs in `web/`.
- All generated runtime artifacts belong in `data/` and `output/` (gitignored).

## Prohibited Patterns

- Do NOT add dependencies without TCO analysis.
- Do NOT make architectural decisions without an ADR.
- Do NOT commit runtime-generated artifacts (raw HTML, JSON outputs).
- Do NOT use unverified blog posts as primary citations.
- Do NOT use rigid difficulty "levels" — the research supports continuous adaptive difficulty.

## Research-First Covenant (Mandatory)

All architectural decisions must follow the **Research-First Covenant**:

1. **No code is written before research is complete.** The workflow is: Decompose → BFS → DFS → ADR → Code.
2. **Every claim requires a citation.** Numbered references to T1–T3 sources.
3. **Every architectural decision requires an ADR.** `docs/adrs/ADR-###-{topic}.md`
4. **The 10-Persona Filter applies to every change.**
5. **Anti-patterns are architectural malpractice.** "Just use X, everyone does" / "We'll fix it in production" are instant violations.

## Decision Authority

When in doubt:
1. Prefer boring, well-understood technology over shiny new tools.
2. Prefer open-source with active community over proprietary lock-in.
3. Prefer stateless services over stateful ones.
4. Prefer event-driven over synchronous RPC for cross-service communication.
5. **Prefer research-backed decisions over intuition.** Cite before you commit.

---

*Document version: 1.0*  
*Established: 2026-05-03*  
*Inherits from: voice-revenge-vizuara-ai/AGENTS.md v2.0*
