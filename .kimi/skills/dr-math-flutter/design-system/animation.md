# Animation — Pedagogical Motion Design

**Single Responsibility:** Use motion to enhance learning, not distract from it.

## Problem

Animation for animation's sake increases cognitive load. For 12-13 year olds with ADHD, excessive motion is harmful [^1]. Motion must serve pedagogy.

## Pedagogical Animation Principles

### 1. Reduce Cognitive Load (Sweller 1988)

**Use motion to:**
- Direct attention (gentle pulse on new content)
- Show relationships (morphing shape into formula)
- Provide feedback (subtle scale on correct answer)

**Avoid:**
- Parallax scrolling
- Bouncing entrances
- Continuous spinning loaders

### 2. Progressive Disclosure (Bruner 1966)

```dart
// Concrete → Pictorial → Abstract with animated transitions
AnimatedSwitcher(
  duration: const Duration(milliseconds: 400),
  child: KeyedSubtree(
    key: ValueKey<String>(_currentSection),
    child: _buildSection(_currentSection),
  ),
);
```

### 3. Feedback Without Disruption

```dart
// Correct answer: subtle scale + green tint
AnimatedContainer(
  duration: const Duration(milliseconds: 200),
  curve: Curves.easeOut,
  transform: _isCorrect
      ? (Matrix4.identity()..scale(1.02))
      : Matrix4.identity(),
  decoration: BoxDecoration(
    color: _isCorrect
        ? Colors.green.withValues(alpha: 0.1)
        : Colors.transparent,
  ),
  child: const Text('Correct!'),
);
```

## Accessibility: Respect Reduced Motion

```dart
final reduceMotion = MediaQuery.of(context).disableAnimations;

AnimatedContainer(
  duration: reduceMotion ? Duration.zero : const Duration(milliseconds: 300),
  // ...
);
```

## Animation Types by Use Case

| Type | Use Case | Widget |
|------|----------|--------|
| Implicit | Layout changes, color transitions | `AnimatedContainer`, `AnimatedOpacity` |
| Explicit | Controlled playback, scrubbing | `AnimationController` + `AnimatedBuilder` |
| Hero | Screen-to-screen transitions | `Hero` widget |
| Staggered | Sequential element reveals | `StaggeredAnimation` |

## Anti-Patterns

| Anti-Pattern | Why It Fails |
|-------------|-------------|
| Auto-playing animations | Distracts from learning content |
| Long durations (>500ms) | Feels sluggish, wastes time |
| No reduced motion support | Violates WCAG 2.3.3 |
| Bounce/elastic curves for feedback | Feels unprofessional, juvenile |

## Expert Sources

[^1]: Sweller, J. (1988). "Cognitive Load Theory." *Learning and Instruction*, 1(4), 295-312.  
Flutter Team. "Animations tutorial." https://docs.flutter.dev/ui/animations/tutorial
