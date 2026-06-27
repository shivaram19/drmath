# Nursing App — Pages and Components Breakdown

**Target:** Extend the MathWise Flutter app with a nursing practice mode for Telangana Staff Nurse / ANM-GNM recruitment.  
**Approach:** Add a new top-level "Nursing" tab and a self-contained feature module under `lib/features/nursing/`.

---

## 1. Home / Dashboard Page

**Route:** `/nursing/home`  
**Purpose:** Entry point showing progress and quick actions.

### Components
- `NursingAppBar` — title "Nursing Practice", language toggle icon.
- `GreetingHeader` — "Welcome back" + last session summary.
- `QuickActionGrid` — 3 cards:
  - Start Diagnostic
  - Full Mock Test (80 Q)
  - Continue Practice
- `SubjectProgressList` — scrollable list of subjects with question count and progress bar.
- `RecentActivityCard` — last attempted topic/mock score.
- `NursingBottomNav` — Home / Subjects / Mock / Profile tabs.

---

## 2. Subject Explorer Page

**Route:** `/nursing/subjects`  
**Purpose:** Browse all nursing subjects.

### Components
- `NursingAppBar` — back button, title "Subjects".
- `SubjectGrid` — 2-column grid on phones, 3 on tablets.
- `SubjectCard` — icon, English name, Telugu name, question count, progress ring.
- `SearchBar` — filter subjects by name.

---

## 3. Topic List Page

**Route:** `/nursing/topics/:subjectId`  
**Purpose:** Show topics within a subject.

### Components
- `NursingAppBar` — subject name, back button.
- `TopicList` — vertical list of topics.
- `TopicCard` — topic name, question count, difficulty chip, "Practice" button.
- `TopicFilterChips` — filter by cognitive level / context.

---

## 4. Practice Page

**Route:** `/nursing/practice?subject_id=&topic_id=&cognitive_level=&context=`  
**Purpose:** Answer topic-wise or filtered questions with immediate feedback.

### Components
- `NursingAppBar` — topic/mode label, question counter.
- `ProgressIndicator` — linear progress of current session.
- `QuestionCard` — question stem with glossary tooltips.
- `OptionButton` — A/B/C/D selectable option.
- `ExplanationCard` — shown after answering.
- `ConfidenceSlider` — 1-5 confidence rating.
- `ActionFooter` — Next / Submit / Skip buttons.
- `ReportButton` — opens report dialog.

---

## 5. Diagnostic Page

**Route:** `/nursing/diagnostic`  
**Purpose:** 20-question adaptive diagnostic across subjects.

### Components
- `NursingAppBar` — "Diagnostic", close button.
- `TimerWidget` — elapsed time (not countdown).
- `ProgressIndicator` — 1/20, 2/20, etc.
- `QuestionCard` + `OptionButton` (no immediate feedback until end).
- `ConfidenceSlider` — per question or global.
- `SubmitDiagnosticButton` — appears on last question.
- `ExitConfirmationDialog` — warns on back press.

---

## 6. Mock Test Page

**Route:** `/nursing/mock`  
**Purpose:** 80-question full mock test, 60 minutes.

### Components
- `NursingAppBar` — countdown timer, question grid icon.
- `QuestionGridSheet` — bottom sheet showing all 80 questions with attempt status.
- `QuestionCard` + `OptionButton`.
- `FlagForReviewButton` — mark question for review.
- `FinishMockButton` — submit with confirmation.
- `TimeWarningDialog` — warns at 5 and 1 minutes remaining.
- `AutoSubmitHandler` — submits when timer hits zero.

---

## 7. Results / Capability Map Page

**Route:** `/nursing/results`  
**Purpose:** Show score, capabilities, and weak areas.

### Components
- `NursingAppBar` — title "Results".
- `ScoreSummaryCard` — correct/total, percentage, time.
- `SubjectCapabilityBars` — bar chart of accuracy per subject.
- `TopicCapabilityList` — sorted weak areas with priority scores.
- `DimensionBreakdown` — cognitive/context accuracy breakdown.
- `ActionButtons` — "Practice Weak Areas", "Retake Diagnostic", "New Mock".

---

## 8. Weak Area PDF Export Page

**Route:** `/nursing/pdf`  
**Purpose:** Generate and share a printable practice sheet.

### Components
- `NursingAppBar` — title "Practice PDF".
- `WeakAreaTopicList` — checkboxes for weak topics.
- `GeneratePdfButton` — calls `/api/nursing/pdf`.
- `PdfPreviewCard` — shows generated HTML or opens share sheet.
- `ShareButton` — native share intent.

---

## 9. Report Question Page

**Route:** `/nursing/report/:questionId` (modal or full page)  
**Purpose:** Report incorrect/ambiguous questions.

### Components
- `NursingAppBar` — title "Report Question".
- `QuestionPreviewCard` — read-only question view.
- `ReasonTextField` — multi-line input.
- `ReasonChips` — quick reasons: "Wrong answer", "Unclear wording", "Outdated", "Typo".
- `SubmitReportButton` — POST to `/api/nursing/report`.
- `SuccessSnackbar` — confirmation.

---

## 10. Settings / Language Page

**Route:** `/nursing/settings`  
**Purpose:** App preferences.

### Components
- `NursingAppBar` — title "Settings".
- `LanguageToggleTile` — English / Telugu switch.
- `ClearProgressButton` — clears local attempts with confirmation.
- `DisclaimerCard` — practice-only disclaimer.
- `AboutCard` — version, source attribution.

---

## Shared / Reusable Components

| Component | Purpose |
|-----------|---------|
| `NursingAppBar` | Consistent app bar with back, title, actions |
| `NursingBottomNav` | Bottom navigation for nursing tab |
| `QuestionCard` | Display question stem with glossary tooltips |
| `OptionButton` | A/B/C/D answer option |
| `ExplanationCard` | Post-answer explanation panel |
| `CapabilityBar` | Horizontal bar showing capability score |
| `TimerWidget` | Countdown or elapsed timer |
| `ConfidenceSlider` | 1-5 confidence rating |
| `GlossaryTooltip` | Telugu translation tooltip on medical terms |
| `LoadingSpinner` | Centered loading indicator |
| `EmptyState` | No questions / no results state |
| `ReportButton` | Opens report flow |
| `ErrorRetryWidget` | API error with retry button |

---

## Data Layer

- `NursingApiService` — HTTP client for `/api/nursing/*` endpoints.
- `NursingRepository` — local cache and persistence.
- `AttemptModel` — matches Pydantic `Attempt` schema.
- `CapabilityModel` — matches `Capability` response.
- `QuestionModel` — matches `NursingQuestion` schema.

---

## State Management

- Provider/Riverpod or simple `StatefulWidget` + service layer.
- Local progress stored in `SharedPreferences` (attempts, capability map, language).
- No server-side user accounts.
