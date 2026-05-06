# AI Rules for Flutter Code Generation

**Single Responsibility:** Constrain AI output to project-specific patterns.

## Rule File Location

`mathwise_build/.kimi/rules/flutter.md`

## Rules Content

```markdown
# Dr. Math Flutter Generation Rules

## Project Context
- Target: Indian Class VII students (ages 12-13)
- Offline demo app — no auth, no backend
- Material 3 design with purple (#6750A4) seed color

## Architecture (Hard Constraints)
1. Features live in `lib/features/{name}/screens/` and `lib/features/{name}/widgets/`
2. Models live in `lib/shared/models/` — PURE DART, no Flutter imports
3. Demo data lives in `lib/shared/data/`
4. Shared widgets live in `lib/shared/widgets/`
5. Theme lives in `lib/shared/theme/`
6. NO cross-feature imports. Use named routes for navigation.
7. NO business logic in `build()` methods.

## Code Style
- Use `const` constructors everywhere possible
- Use `final` for all variables unless mutation is required
- Prefer single quotes for strings
- Maximum 100 characters per line
- Trailing commas on multi-line collections

## State Management
- Local UI state: `StatefulWidget` + `setState`
- Shared app state: Riverpod `AsyncNotifier`
- NEVER use BLoC for simple toggle/checkbox state
- ALWAYS check `mounted` before `setState` after async

## Design System
- All colors from `Theme.of(context).colorScheme`
- All text styles from `Theme.of(context).textTheme`
- Minimum touch target: 48dp
- Card border radius: 16dp
- Button border radius: 12dp
- Body text minimum: 16sp

## Accessibility (Non-Negotiable)
- Every `IconButton` has `tooltip` or `semanticLabel`
- No color-only feedback — always pair with icon/text
- Test with 2.0x text scale factor
- All images have `semanticLabel` or `excludeFromSemantics: true`

## Performance
- `ListView.builder` for dynamic lists
- `const` widgets where possible
- Dispose all controllers and listeners
- No `Theme.of(context)` in `initState`

## Deprecated API Migration
- `withOpacity(x)` → `withValues(alpha: x)`
- `primaryColor` → `colorScheme.primary`
- `accentColor` → `colorScheme.secondary`
- `backgroundColor` → `colorScheme.surface`

## Testing
- Unit test all domain logic (pure Dart)
- Widget test all screens
- Use `tester.pumpAndSettle()` after navigation/animation
- Use `tester.pump()` after simple `setState`
- Mock repositories, never mock value objects
```

## Usage

When generating code, prepend these rules to the AI context:

```
You are generating Flutter code for the Dr. Math project.
Follow ALL rules in .kimi/rules/flutter.md.
Current task: [specific task]
```

## Validation

After AI generates code:

```bash
cd mathwise_build
flutter analyze          # Must pass zero errors
flutter test             # Must pass all tests
dart format --set-exit-if-changed .  # Must be formatted
```

## Anti-Patterns

| Anti-Pattern | Fix |
|-------------|-----|
| AI ignores rules file | Explicitly reference rules in every prompt |
| Rules are too vague | Specific constraints (file paths, sizes, colors) |
| Rules not versioned | Commit rules file to git |
| Rules conflict with each other | Regular review and consolidation |

## Expert Sources

Flutter Team. "AI rules for Flutter and Dart." https://docs.flutter.dev/ai/rules  
MCP Server. "Dart and Flutter MCP." https://pub.dev/packages/dart_mcp_server
