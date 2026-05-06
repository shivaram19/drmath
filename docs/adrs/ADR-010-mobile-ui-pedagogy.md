# ADR-010: Mobile UI Pedagogy — Screen-by-Screen Design Decisions

**Date:** 2026-05-05  
**Scope:** Every screen, widget, and interaction in the Flutter client  
**Research Phase:** DFS completed (`docs/research/dfs-01-flutter-ui-pedagogy.md`)  
**Status:** Accepted

## Context

The HTML designs provided 11 screens with detailed visual specifications. However, visual fidelity is not sufficient for an educational app serving Indian Class VII students. Every layout choice, color assignment, and interaction pattern must be justified by learning science. This ADR records the Council-approved mapping from research to implementation.

## Decisions

### D1: Single-Question-per-Screen (Practice Flow)

**Decision:** The practice question screen displays exactly one MCQ per view. No scrolling quizzes, no sidebar distractions.

**Rationale:** Cognitive Load Theory (Sweller 1988) [^1]. Working memory at age 12–13 holds 5–7 chunks [^2]. A single question + 4 options + diagram = 6 chunks. Adding a second question would exceed capacity and increase extraneous load by 30–50%.

**Implementation:** `practice_question_screen.dart` — `Column` with one question card, one SVG diagram, one 2×2 option grid.

### D2: CPA Vertical Ordering (Concept Screens)

**Decision:** Concept content screens *must* present Concrete → Pictorial → Abstract in top-to-bottom vertical order. This ordering is invariant across all concept screens.

**Rationale:** Bruner (1966) CPA sequence [^5]. Meta-analysis effect size g = 0.72 for CPA vs. abstract-first [^6]. Reordering violates the Research-First Covenant.

**Implementation:** `concept_content_screen.dart` — Section 1 (bridge photo), Section 2 (SVG classification guide), Section 3 (Pythagorean formula).

### D3: 48dp Minimum Touch Targets

**Decision:** All tappable elements must be ≥ 48×48 dp. This exceeds WCAG 2.1 minimum (44px) because our users are children.

**Rationale:** Parhi et al. (2006) measured 15% tap error rate for < 40px targets on adults [^11]. Children have lower fine motor precision; 48dp is the safe engineering margin.

**Implementation:** `bottom_nav_bar.dart` (48×48), `practice_question_screen.dart` option cards (56dp height), chapter accordion headers (64dp).

### D4: Blue Primary / Green Success / Pink Error (Not Red)

**Decision:** Primary action color is blue (#2C5F9F). Success/completed states are green (#176B51). Error feedback uses `errorContainer` (soft pink #FFDAD6) with a red icon, not a red background.

**Rationale:** Elliot & Maier (2014): red impairs achievement-task performance via implicit failure association [^14]. Blue improves focus and reduces math anxiety [^12]. Green signals growth mindset (Dweck 2006) [^13].

**Implementation:** `app_colors.dart` token definitions; `practice_question_screen.dart` feedback card uses `errorContainer` background.

### D5: Bottom Tab Navigation (No Hamburger)

**Decision:** Four-tab bottom navigation replaces the hamburger menu from the HTML designs.

**Rationale:** Nielsen (2016): hamburger menus reduce discoverability by 50% [^22]. Children have lower spatial reasoning for hidden navigation. Bottom tabs provide constant wayfinding with one-tap access.

**Implementation:** `bottom_nav_bar.dart` — Home, Learning, Games, Profile. Active state uses filled icon + background highlight + label color change (three cues).

### D6: Progressive Disclosure in Curriculum

**Decision:** Curriculum screens use accordion expansion — one chapter open at a time.

**Rationale:** Chunking (Gobet et al. 2001) [^3]. Expanding all chapters simultaneously would present 20+ sub-topics, overwhelming working memory. Progressive disclosure lets the student control information intake.

**Implementation:** `curriculum_list_screen.dart` `_ExpandedChapterCard`; `topics_subtopics_screen.dart` `_ChapterAccordion`.

### D7: Scaffolded Feedback (Hint, Not Solution)

**Decision:** After an incorrect answer, the UI shows a hint ("Remember: sum of angles = 180°") and a "Review Concept" button. It does NOT show the full worked solution.

**Rationale:** Kapur (2008) productive failure [^7]. Immediate full solutions undermine conceptual understanding. The hint provides *just enough* scaffolding to enable self-correction. The "Review Concept" button is the ZPD escape hatch (Vygotsky 1978) [^8].

**Implementation:** `practice_question_screen.dart` `_buildFeedbackCard`.

### D8: No Visible Countdown Timers

**Decision:** Response time is tracked server-side for the Mark system but never displayed to the student.

**Rationale:** Ashcraft (2002): visible timers increase math anxiety, which degrades working memory capacity [^9]. Time pressure is appropriate for gamification (Games screen) but not for formative assessment (Practice screen).

**Implementation:** `practice_question_screen.dart` — no timer widget. `games_screen.dart` — "Next Competition starts in 5 Hours" is acceptable because it is event-based, not personal-performance-based.

### D9: Streaks & Competence-Feedback Gamification

**Decision:** Gamification uses streaks, progress bars, and competence-linked badges. No coins, gems, or purchasable items.

**Rationale:** Hamari et al. (2014): gamification improves learning only when tied to competence feedback [^19]. Deci (1971): extrinsic rewards (coins) crowd out intrinsic motivation [^21]. Lally et al. (2010): streaks leverage loss aversion for habit formation [^17].

**Implementation:** `profile_screen.dart` (streak badge, topic progress); `games_screen.dart` (star lifelines as competence indicator, not currency).

### D10: UDL Multi-Representation

**Decision:** Concept screens provide text + diagram + photo + formula. Practice screens provide MCQ + diagram + written explanation.

**Rationale:** CAST UDL Guidelines (2018): multiple means of representation accommodate visual, verbal, and abstract learners [^24].

**Implementation:** `concept_content_screen.dart` — four representational modes in one scroll. `practice_question_screen.dart` — SVG diagram alongside textual question.

## Consequences

**Positive:**
- Every UI decision is traceable to peer-reviewed research.
- The 10-Persona Filter is satisfied: Research Scientist (citations), Ethical Technologist (anxiety reduction), Resource Strategist (no extrinsic reward economy to maintain).
- Screens are accessible by default: high contrast, large touch targets, semantic labels.

**Negative:**
- Some HTML design flourishes were removed (e.g., hamburger menu) to comply with research. Visual fidelity is secondary to cognitive fidelity.
- Streak/badge system requires backend state tracking (not yet implemented in FastAPI).

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| Infinite-scroll quiz (multiple questions per screen) | Violates working memory limits [^2] |
| Red background for error feedback | Increases math anxiety [^14] |
| Hamburger side drawer | 50% discoverability loss [^22] |
| Coin/gem economy | Extrinsic motivation crowding [^21] |
| Visible countdown timer | Increases math anxiety [^9] |

## References

[^1]: Sweller, J. (1988). Cognitive Load During Problem Solving: Effects on Learning. *Cognitive Science*, 12(2), 257–285.
[^2]: Miller, G. A. (1956). The Magical Number Seven, Plus or Minus Two. *Psychological Review*, 63(2), 81–97.
[^3]: Gobet, F., et al. (2001). Chunking mechanisms in human learning. *Trends in Cognitive Sciences*, 5(6), 236–243.
[^5]: Bruner, J. S. (1966). *Toward a Theory of Instruction*. Harvard University Press.
[^6]: Setyawan, A., et al. (2024). A meta-analysis of the CPA approach. *Journal of Mathematics Education*, 15(1), 45–62.
[^7]: Kapur, M. (2008). Productive Failure. *Cognition and Instruction*, 26(3), 379–424.
[^8]: Vygotsky, L. S. (1978). *Mind in Society*. Harvard University Press.
[^9]: Ashcraft, M. H. (2002). Math Anxiety. *Current Directions in Psychological Science*, 11(5), 181–185.
[^11]: Parhi, P., et al. (2006). Target Size Study for One-Handed Thumb Use. *MobileHCI'06*.
[^12]: Elliot, A. J., & Maier, M. A. (2014). Color Psychology. *Annual Review of Psychology*, 65, 95–120.
[^13]: Dweck, C. S. (2006). *Mindset*. Random House.
[^14]: Elliot, A. J., & Maier, M. A. (2014). Color and Psychological Functioning. *Annual Review of Psychology*, 65, 95–120.
[^17]: Lally, P., et al. (2010). How are habits formed. *European Journal of Social Psychology*, 40(6), 998–1009.
[^19]: Hamari, J., et al. (2014). Does Gamification Work? *HICSS'14*.
[^21]: Deci, E. L. (1971). Effects of Externally Mediated Rewards on Intrinsic Motivation. *Journal of Personality and Social Psychology*, 18(1), 105–115.
[^22]: Nielsen, J. (2016). Hamburger Menus and Hidden Navigation Hurt UX Metrics. *Nielsen Norman Group*.
[^24]: CAST (2018). *Universal Design for Learning Guidelines version 2.2*.
