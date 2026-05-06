# Design System Skill — Token Architecture

**Single Responsibility:** Define how visual design is expressed as code.

## Problem

Hardcoded `Color(0xFF6750A4)` in 47 files. When the brand color changes, 47 files must change. When dark mode is requested, it's a rewrite. When accessibility audit fails, colors are scattered and untraceable.

## Solution: Token Hierarchy

```
Design Tokens (brand decisions)
    │
    ▼
ThemeData / ColorScheme (Flutter mapping)
    │
    ▼
Component Themes (CardTheme, ButtonTheme)
    │
    ▼
Widgets (Theme.of(context).colorScheme.primary)
```

**Rule:** No widget references a raw color, size, or font. All values flow through `Theme.of(context)`.

## Dr. Math Token Map

| Token | Value | Semantics |
|-------|-------|-----------|
| `seedColor` | `#6750A4` | Purple — focus, learning, calm |
| `surface` | `#F8F9FA` | Calm off-white background |
| `success` | `#4CAF50` | Correct answer feedback |
| `hintAmber` | `#FF9800` | Hint card, gentle attention |
| `errorRose` | `#E91E63` | Incorrect answer |
| `minTouchTarget` | `48.0` | WCAG 2.5.5 minimum |
| `cardRadius` | `16.0` | Friendly, non-threatening |
| `buttonRadius` | `12.0` | Actionable, inviting |
| `bodyLarge` | `18.0` | Body text for children |
| `titleLarge` | `24.0` | Section headers |

## File Structure

```
lib/shared/theme/
├── app_theme.dart          # ThemeData.light() / ThemeData.dark()
├── color_scheme.dart       # ColorScheme.fromSeed + custom tokens
├── text_theme.dart         # Typography scale for readability
├── component_themes.dart   # CardTheme, ButtonTheme, InputTheme
└── extensions.dart         # ThemeExtension for custom tokens
```

## Anti-Patterns

| Anti-Pattern | Symptom | Fix |
|-------------|---------|-----|
| `Color(0xFF...)` in widget | 47 replacements for one change | `Theme.of(context).colorScheme.primary` |
| `TextStyle(fontSize: 16)` | Inconsistent typography | `Theme.of(context).textTheme.bodyLarge` |
| `EdgeInsets.all(16)` everywhere | Inconsistent spacing | `AppSpacing.of(context).medium` via extension |
| No dark mode | User complaints, battery drain | Build `ColorScheme` with `brightness` parameter |
| Color-only feedback | Fails WCAG 1.4.1 | Pair color with icon + text |

## Expert Sources

Material Design 3. "Design Tokens." https://m3.material.io/styles/color/the-color-system/tokens  
Felker, R. (Solido). Awesome Flutter — Design System packages. https://github.com/Solido/awesome-flutter#ui
