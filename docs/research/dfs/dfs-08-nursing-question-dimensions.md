# DFS-08: Nursing Question Dimensions — MCQ-First, Cognitive-Level Tagging

**Date:** 2026-05-13  
**Scope:** Determine the minimal viable "different dimensions" framework for the nursing module.  
**Research Phase:** DFS — technology & pedagogy deep-dive  

## Executive Summary

After the user clarified that the nursing module is "topic-wise questions asked in different dimensions," I re-examined the plan. A four-dimensional framework (cognitive × format × context × difficulty) is comprehensive but introduces unnecessary UI and scoring complexity for v1. Research supports a simpler approach: **keep MCQ-only format, add lightweight cognitive-level and context tags**, and allow learners to practice by topic with optional difficulty/cognitive filters.

## Evidence

### 1. MCQs Can Assess Higher-Order Thinking

Well-designed MCQs are not limited to recall. They can assess application, analysis, and evaluation when stems and distractors are carefully constructed [^1]. In a pharmacy therapeutics sequence, students scored 73.1% on recall MCQs, 70.2% on application MCQs, and 60.1% on analysis MCQs, showing that higher-order MCQs do discriminate differently [^2].

### 2. Question Format Variety Does Not Clearly Outperform MCQs

A 2024 randomized controlled trial (n=45) compared very-short-answer questions (VSAQ) with MCQs for retrieval practice and found **no significant difference in final-test performance** between the two formats [^3]. This suggests that the *act* of retrieval matters more than the *format*. Adding true/false, fill-in-blank, or matching may increase UI complexity without clear learning gains.

### 3. MCQs Are More Reliable Than True/False

MCQs are less susceptible to guessing than true/false questions and offer faster, more objective scoring than constructed-response items [^4]. For a high-stakes exam like Telangana Staff Nurse, MCQ-first practice aligns with the actual test format and reduces scoring ambiguity.

### 4. Cognitive-Load Considerations

Cognitive Load Theory suggests that extraneous load (e.g., learning new question formats, complex UI) can impede learning [^5]. For an adult learner studying on a smartphone, a consistent MCQ interface reduces extraneous load and lets her focus on the medical content.

### 5. Bloom's Taxonomy Is Useful but Interpretive

Faculty-level Bloom assignments agree with student perceptions only ~70% of the time [^6]. Therefore, cognitive-level tags in the seed bank should be treated as **approximate instructional signals**, not rigid categories.

## Decision

**v1 dimensions (minimal):**
- **Format:** MCQ only.
- **Cognitive level:** `remember`, `understand`, `apply`, `analyze`.
- **Context:** `theory`, `scenario`, `calculation`.
- **Difficulty:** existing 1–3 scale.
- **Topic:** existing `topic_id`.

**Deferred to later phases:**
- True/False, fill-in-blank, matching, assertion-reason.
- Image-based questions.
- Audio/video questions.

## Rationale

1. Matches the actual Telangana Staff Nurse exam format (80 MCQs).
2. Minimizes UI and scoring complexity.
3. Still gives the user "different dimensions" through cognitive-level and context tags.
4. Reduces manual tagging burden (only two new tags per question).
5. Research shows retrieval practice, not format variety, drives retention.

## References

[^1]: Natural Sciences Publishing. (2024). MCQ research in medical, nursing, and health sciences education. *Journal of Applied Mathematics and Computation*.
[^2]: Cobb, M. A., et al. (2011). Using multiple choice questions written at various Bloom’s taxonomy levels to evaluate student performance across a therapeutics sequence. *American Journal of Pharmaceutical Education*.
[^3]: van Wijk, E. V., et al. (2024). The battle of question formats: a comparative study of retrieval practice using very short answer questions and multiple choice questions. *BMC Medical Education*.
[^4]: Jovanovska, J. (n.d.). Designing effective multiple-choice questions for assessing learning outcomes. *University of Glasgow*.
[^5]: Sweller, J. (1988). Cognitive load theory: Implications of cognitive load theory on the design of learning. *Learning and Instruction*.
[^6]: Stringer, J. K., et al. (2021). Examining Bloom's taxonomy in multiple choice questions. *BMC Medical Education*.
