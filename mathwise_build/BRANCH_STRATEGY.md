# Dr. Math Branch Strategy — Dual-Track Development

## Overview

Two parallel tracks that must never disrupt each other. Each track lives on its own long-running branch with feature branches sprouting from it.

```
main (production)
├── content-pipeline/      ← Track 1: Content Generation Automation
│   ├── feat/content-...   ← Feature branches
│   └── research/...       ← Research spikes
│
└── games-integration/     ← Track 2: Games Research + Integration
    ├── feat/game-...      ← Game feature branches
    ├── research/...       ← Integration research
    └── spike/...          ← Technical experiments
```

---

## Track 1: Content Generation Automation (`content-pipeline`)

**Goal:** Automate the adaptive math content generation pipeline that produces curriculum-aligned assessment items for Indian Class VII students.

**What this branch owns:**
- `pipeline/` — scraper, LLM client, question generator, content adapter
- `db/` — models, CRUD, migrations
- `web/` — FastAPI serving layer (content API endpoints only)
- `docs/research/` — pedagogy research, BFS/DFS studies
- `data/`, `output/` — generated artifacts (gitignored)

**Forbidden to touch:**
- `lib/` — Flutter app code
- `test/features/` — Flutter widget tests
- `scripts/visual_testing/` — visual regression framework
- Any game-related code

**Branch naming:**
- `feat/content-{topic-slug}` — new content features
- `research/{bfs|dfs|bidirectional}-##-{name}` — research documents
- `fix/content-{bug-description}` — bug fixes

---

## Track 2: Games Integration (`games-integration`)

**Goal:** Research, design, and integrate low-latency educational games into the Flutter app that build mathematical curiosity through play.

**What this branch owns:**
- `lib/features/games/` — game screens, widgets, state management
- `lib/games/` — reusable game engines/components (if shared)
- `test/features/games/` — game widget tests
- `docs/research/games/` — game design research, integration studies
- `scripts/games/` — game-specific tooling (if any)

**Forbidden to touch:**
- `pipeline/` — content generation code
- `db/` — database models (read-only via API)
- `web/` main.py — except adding `/games/*` endpoints if needed
- Content generation configuration

**Branch naming:**
- `feat/game-{name}` — new game implementation
- `research/game-{topic}` — integration/architecture research
- `spike/{tech}-latency` — performance experiments
- `fix/game-{bug-description}` — game bug fixes

---

## Cross-Track Integration Rules

1. **No direct commits to `main`**. All work goes through PRs from track branches.
2. **Track branches are long-running**. They are rebased on `main` periodically, not deleted.
3. **Feature branches are short-lived**. Created from track branch, merged back, then deleted.
4. **Shared interfaces only**. If Track 2 needs content data, it uses the existing API — never imports from `pipeline/`.
5. **ADR required for cross-track changes**. Any modification affecting both tracks needs an Architecture Decision Record.

---

## MCP Real-Time Search Automation (Future)

**Goal:** Automate research fetching using MCP real-time search capabilities.

**Implementation plan:**
1. Create `.kimi/mcp/search_tools.yaml` defining search personas
2. Each track branch runs scheduled research jobs:
   - Track 1: "What are latest adaptive learning algorithms?"
   - Track 2: "How are educational games built in Flutter with low latency?"
3. Results auto-commit to `docs/research/` on the respective track branch
4. Human review before merging research into mainline docs

---

## Current State & Next Steps

| Track | Branch | Status | Next Action |
|-------|--------|--------|-------------|
| Content | `content-pipeline` | ✅ Exists as `dev` | Stabilize, rename to `content-pipeline` |
| Games | `games-integration` | ❌ Does not exist | Create from `main`, begin research |

**Immediate actions needed:**
1. Create `games-integration` branch from `main`
2. Write `docs/research/games/FLUTTER_GAMES_INTEGRATION_RESEARCH.md`
3. Identify 3-5 reference apps/games for study
4. Document latency requirements (< 16ms frame budget for 60fps)
5. Define curiosity-building game mechanics for math concepts
