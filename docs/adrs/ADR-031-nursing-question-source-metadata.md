# ADR-031: Source Metadata Schema for Nursing Questions

**Date:** 2026-05-05  
**Scope:** Provenance and verification fields for every nursing question.  
**Research Phase:** Implementation of ISSUE-004 / #56.  
**Status:** Accepted.  
**Tracked in:** #56

---

## Context

The nursing question bank needs auditability: every question must trace back to where it came from and when it was last verified. This is a prerequisite for the verification workflow (ISSUE-011) and for confidence in the adaptive engine.

## Decision

### 1. Three new fields on every nursing question

- `source_url` — URL or canonical reference to the source material (nullable until curated).
- `source_section` — Section, concept tag, or chapter identifier within the source.
- `verified_at` — ISO date the question was last verified.

These fields are added to the Pydantic `Question` model and to the JSON seed bank. Existing fields (`source`, `verification_status`, `verified_by`, `last_reviewed`) are retained for backward compatibility.

### 2. Backfill strategy

The existing 130 questions were backfilled using:

- `source_url = null` (flagged for future curation)
- `source_section = concept_tag or topic_id`
- `verified_at = last_reviewed`

A utility script (`scripts/backfill_nursing_metadata.py`) performs this idempotently and can be re-run after future generations.

### 3. API exposure

The fields are returned by the existing `/api/nursing/questions` endpoint because they are part of the `Question` model. No separate endpoint is required.

## Consequences

### Positive

- Managers can audit provenance before approving questions for daily quizzes.
- Verification workflow can read and write `verified_at` directly.
- Source metadata supports future DPDP and academic-citation requirements.

### Negative

- `source_url` is currently null for most existing questions until manual curation.
- New questions must be generated with these fields or backfilled before ingestion.

## References

[^1]: INC GNM Syllabus — Indian Nursing Council. https://www.indiannursingcouncil.org/
