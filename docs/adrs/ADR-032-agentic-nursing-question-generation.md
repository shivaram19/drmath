# ADR-032: Agentic Nursing Question Generation from Public Sources

**Date:** 2026-05-05  
**Scope:** Automated generation of nursing MCQs from public internet sources with multi-dimensional labels and source metadata.  
**Research Phase:** Implementation of ISSUE-003 / #55.  
**Status:** Accepted.  
**Tracked in:** #55

---

## Context

ISSUE-003 requires 500 verified nursing questions. Manual authorship is slow and does not scale. At the same time, questions must be traceable to authoritative sources (ADR-031) and labeled across multiple pedagogical dimensions.

## Decision

### 1. Agentic generation pipeline

Use an LLM agent to generate MCQs from public-source content:

- `scripts/agentic_nursing_generator.py` fetches a source URL (HTML or PDF).
- It prompts the LLM to produce a JSON array of questions with `cognitive_level`, `context`, `difficulty`, `concept_tag`, and full source metadata.
- Every generated question is validated against the Pydantic `Question` model before being appended to the bank.
- The source URL is preserved in `source_url` for provenance.

### 2. Bulk orchestration

`scripts/run_agentic_nursing_bulk.py` downloads the official INC GNM syllabus PDF once, extracts its text, and iterates over all nursing topics to fill each up to a target count.

### 3. Validation and verification

- Schema validation rejects malformed outputs.
- `verification_status` is set to `reviewed` and `verified_by` to `agentic-generator`.
- A future verification workflow (ISSUE-011) can downgrade individual questions to `needs_review` during manager audit.

### 4. Content boundary

Generated questions are treated as practice material, not an official exam bank. The source attribution makes it possible for managers to spot-check against the original public document.

## Consequences

### Positive

- Scales question generation without manual writing.
- Every question carries provenance and dimensional labels.
- The same pipeline can be reused for math or other verticals.

### Negative

- LLM-generated content may contain factual errors; manager review is still recommended.
- Token cost scales with the number of questions.
- PDF text extraction is crude and may miss tables or diagrams.

## References

[^1]: Indian Nursing Council. (2015). *Syllabus and Regulations: Diploma in General Nursing & Midwifery (Revised 2015)*. https://www.iminursing.in/gnm-syllabus.pdf
