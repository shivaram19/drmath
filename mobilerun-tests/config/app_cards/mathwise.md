# MathWise App Guide

MathWise is an adaptive mathematics learning app for Indian Class VII-VIII students. It uses a bottom-tab navigation with four tabs: Home, Curriculum, Games, and Profile.

## Navigation Structure

### Bottom Tabs (always visible)
- **Home** (index 0): Dashboard with resume card, daily practice, games summary, recommended topics
- **Curriculum** (index 1): Chapter list with expandable accordion chapters
- **Games** (index 2): Math games catalog and weekly challenges
- **Profile** (index 3): User stats, achievements, topic progress

### Screen Flows

**Home → Continue Learning**
- Tap "Resume Lesson" button on the blue continue card
- Navigates to Topic Choice screen

**Home → Daily Practice**
- Tap "Start Now" on the Daily Practice card (secondary color)
- Navigates directly to Practice Question screen

**Home → Games**
- Tap "Enter Games" button on the games summary card
- Or tap the Games bottom tab

**Class Selection → Topics**
- Tap any class card (Class 5 through Class 10)
- Navigates to Topics & Subtopics screen

**Curriculum List → Subtopic**
- Tap a chapter header to expand it
- Tap any non-locked subtopic row
- Navigates to Topic Choice screen

**Curriculum Grid → Topic Tile**
- Tap any non-locked 2×2 topic tile
- Navigates to Topic Choice screen

**Curriculum Stepper → Actions**
- Completed steps: "Review Lesson" → Concept Content
- Current step: "Resume Journey" → Topic Choice
- Current step: "Quick Quiz" → Practice Question

**Topic Choice → Modes**
- "Learn Concept" card (left, blue) → Concept Content screen
- "Practice Problems" card (right, pink/orange) → Practice Question screen

**Concept Content → Practice**
- Scroll to bottom
- Tap "Practice This Topic" large blue button
- Navigates to Practice Question screen

**Practice Question → Flow**
- Tap one of 4 MCQ options (A/B/C/D)
- Tap "Submit Answer"
- Feedback appears: green for correct, pink for incorrect with hint
- "Review Concept" → goes back to Concept Content
- "Next Question" → advances to next question (8 total)

**Games → Play**
- Tap "Play Now" on any game card
- Shows SnackBar (demo only, no real games yet)
- "Join Competition" → Practice Question screen

**Profile → Actions**
- "View All" achievements → SnackBar
- "Practice Fractions Now" → Topic Choice screen

## UI Patterns

### Cards & Containers
- White rounded cards with subtle shadow: primary content containers
- Blue (`#3B6DE7`) primary actions: Resume, Start Learning, Practice
- Pink/Orange (`#FF6B4A`) secondary actions: Start Practice
- Green (`#4CAF50`) success states: completed topics, correct answers
- Gray outlines: locked/inactive states

### Touch Targets
- All buttons minimum 48dp height
- Option buttons in quizzes are full-width rows with A/B/C/D labels

### Text Elements
- Headlines: large bold text (topic titles)
- Body: regular weight, slightly muted color
- Labels: uppercase small text for section headers

## Common Actions
- **Back**: Top-left chevron or system back button
- **Scroll**: Most screens scroll vertically; content is below fold
- **Tap card**: Many cards are tappable (class cards, topic tiles, subtopic rows)

## Tips
- The app has NO login screen; it opens directly to Home
- Demo data shows Alex Johnson, Grade 8, 12-day streak
- Locked chapters show a lock icon and cannot be tapped
- The Quick Check in Concept Content is interactive: tap options then Submit
