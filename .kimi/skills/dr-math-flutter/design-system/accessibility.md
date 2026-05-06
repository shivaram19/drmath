# Accessibility — WCAG 2.1 AA Compliance

**Single Responsibility:** Ensure the app is usable by all students, including those with disabilities.

## Problem

12-13 year olds include users with: low vision, color blindness, motor impairments, dyslexia, ADHD. Accessibility is not a feature — it is a constraint on every design decision.

## Required Compliance (Non-Negotiable)

### 1. Touch Targets (WCAG 2.5.5)

```dart
// Minimum 48×48 dp
IconButton(
  iconSize: 24,
  padding: const EdgeInsets.all(12), // 24 + 12 + 12 = 48
  onPressed: () {},
  icon: const Icon(Icons.close),
)

// Or use styleFrom:
ElevatedButton.styleFrom(
  minimumSize: const Size(48, 48),
)
```

### 2. Color Contrast (WCAG 1.4.3)

| Element | Ratio Required | Tool |
|---------|---------------|------|
| Normal text (<18sp) | 4.5:1 | `ColorScheme` ensures this |
| Large text (≥18sp bold / 24sp) | 3:1 | `ColorScheme` ensures this |
| UI components | 3:1 | Manual check with contrast checker |

```dart
// NEVER color-only feedback
// BAD:
Text('Correct!', style: TextStyle(color: Colors.green))

// GOOD:
Row(
  children: [
    Icon(Icons.check_circle, color: colorScheme.primary),
    const SizedBox(width: 8),
    Text('Correct!', style: textTheme.bodyLarge),
  ],
)
```

### 3. Screen Reader Support (TalkBack / VoiceOver)

```dart
// Every interactive element needs semantics
IconButton(
  onPressed: () => Navigator.pop(context),
  icon: const Icon(Icons.arrow_back),
  tooltip: 'Go back', // Announced by screen reader
)

// Complex widgets need grouping
Semantics(
  label: 'Question 3 of 8: What is the sum of angles in a triangle?',
  child: QuestionCard(/*...*/),
)

// Hide decorative images
Image.asset(
  'assets/decoration.png',
  excludeFromSemantics: true,
)
```

### 4. Text Scaling

```dart
// Test with:
// flutter run --dart-define=TEXT_SCALE=2.0
// Or in DevTools: set text scale to 2.0

// Ensure layout handles overflow:
Text(
  longText,
  style: textTheme.bodyLarge,
  overflow: TextOverflow.ellipsis, // Or wrap
  maxLines: 3,
)

// Use Flexible / Expanded in rows:
Row(
  children: [
    Flexible(child: Text('Long label that might overflow')),
    const SizedBox(width: 8),
    ElevatedButton(onPressed: () {}, child: Text('Action')),
  ],
)
```

### 5. Focus Management

```dart
// Ensure focus returns to logical place after dialog
FocusScope.of(context).requestFocus(_submitButtonFocus);

// Focus traversal order for forms
TextField(
  focusNode: _emailFocus,
  textInputAction: TextInputAction.next,
  onEditingComplete: () => FocusScope.of(context).requestFocus(_passwordFocus),
)
```

### 6. Reduce Motion

```dart
// Respect user preference:
final reduceMotion = MediaQuery.of(context).disableAnimations;

AnimatedContainer(
  duration: reduceMotion ? Duration.zero : const Duration(milliseconds: 300),
  // ...
)
```

## Accessibility Checklist Per Screen

- [ ] All interactive elements ≥48dp touch target
- [ ] No color-only information conveyance
- [ ] All `IconButton`s have `tooltip` or `semanticLabel`
- [ ] All images have `semanticLabel` or `excludeFromSemantics`
- [ ] Text handles 2.0x scale without truncation
- [ ] Screen reader can navigate full flow without visual reference
- [ ] Focus order is logical

## Testing Accessibility

```bash
# Enable TalkBack on device, navigate with volume keys
# Or use Flutter's accessibility inspector:
flutter run
# In DevTools: Inspect → Accessibility tree
```

## Expert Sources

Flutter Team. "Accessibility." https://docs.flutter.dev/ui/accessibility-and-internationalization/accessibility  
WCAG 2.1. "Web Content Accessibility Guidelines." https://www.w3.org/WAI/WCAG21/quickref
