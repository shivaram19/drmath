# Educational Question Generation — Evaluation Rubric Research

**Date:** 2026-05-13  
**Scope:** Research-backed dimensions for evaluating LLM-generated math questions  
**Research Phase:** DFS (Depth-First Synthesis)

---

## Research Synthesis

### Source 1: EQGBench (2025)
Multi-dimensional evaluation framework for educational question generation:
1. **Knowledge Point Alignment** — Does it cover the specified topic?
2. **Question Type Alignment** — Format correctness (MCQ structure, 4 options)
3. **Question Item Quality** — Clarity, unambiguous objective, solvability
4. **Solution Explanation Quality** — Correctness, rigor, completeness
5. **Competence-Oriented Guidance** — Contextually relevant, application-driven

### Source 2: Bloom's Taxonomy-Based Generation (2024)
Hierarchical expert evaluation rubric:
- **Understandable** → if NO, stop evaluation
- **Clear** → if NO, stop evaluation
- **Answerable** → if NO, stop evaluation
- **Central to topic** → if NO, stop evaluation
- **Would you use it?** → if NO, stop evaluation
- **Bloom's Level** → Apply/Analyze/Evaluate/Create

### Source 3: OpenLearnLM (2025)
LLM-as-Judge quality assurance (5 criteria, 25-point scale):
1. **Answer Accuracy** (critical) — Is the marked answer correct?
2. **Question Clarity** (critical) — Is the stem unambiguous?
3. **Distractor Quality** — Are wrong options plausible but distinguishable?
4. **Difficulty Match** — Does cognitive demand match intended level?
5. **Scenario Alignment** — Does it serve the educational context?

---

## Our Adapted Rubric

| Dimension | Research Source | PM Question | Scale |
|-----------|----------------|-------------|-------|
| **Thought Direction** | EQGBench Competence + Bloom's | Does it guide toward right thinking? | 1-5 |
| **Playfulness** | OpenLearnLM Scenario Alignment | Would MY child want to solve this? | 1-5 |
| **Guidance Quality** | EQGBench Solution Quality | Is the help helpful or just giving answers? | 1-5 |
| **Curiosity Building** | EQGBench Competence | Does it make them curious for more? | 1-5 |
| **Clarity** | OpenLearnLM Question Clarity | Is the question unambiguous? | Pass/Fail |
| **Accuracy** | OpenLearnLM Answer Accuracy | Is the correct answer actually correct? | Pass/Fail |

**Hierarchical Rule:** If Clarity or Accuracy fails, the question needs rewriting before other dimensions matter.

---

## Pedagogical Dimensions (Prompt Personas)

| Dimension | Theory | Child Experience | PM Feel-Test |
|-----------|--------|------------------|--------------|
| **Default** | Scaffolded instruction (Rosenshine) | "I understand step by step" | Progression logical? |
| **Storyteller** | Situated learning (Lave & Wenger) | "This is MY world" | Authentic context? |
| **Visual-First** | CPA method (Bruner) | "I can SEE it" | Intuitive diagrams? |
| **ZPD Adaptive** | Zone of Proximal Dev (Vygotsky) | "Challenging but doable" | Productive struggle? |

---

## Implementation Notes

1. **Batch Generation:** Use ThreadPoolExecutor with 3 workers (respects API rate limits)
2. **Idempotency:** Skip existing files, resume on restart
3. **Observability:** Live status JSON updated after every job
4. **Error Resilience:** Per-job isolation, no cascade failures
5. **PM Dashboard:** Real-time matrix showing all topic × dimension combinations

*Refs: EQGBench (2025), Bloom's AEQG (2024), OpenLearnLM (2025)*
