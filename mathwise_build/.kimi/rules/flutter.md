# Dr. Math Flutter Rules

## Project Context
- Target: Indian Class VII students (ages 12–13)
- Offline demo app — no auth, no backend, no logging
- Material 3 design with custom ColorScheme
- Flutter 3.27.0 stable, Dart 3.6.0

## Architecture
- Features: `lib/features/{name}/screens/` + `lib/features/{name}/widgets/`
- Models: `lib/shared/models/` — pure Dart, NO Flutter imports
- Data: `lib/shared/data/` — demo repositories
- Widgets: `lib/shared/widgets/` — cross-cutting components
- Theme: `lib/shared/theme/` — ThemeData, extensions
- NO cross-feature imports. Use `MaterialPageRoute<void>()` for navigation.
- NO business logic in `build()` methods.

## Dependencies
- Current: `google_fonts`, `flutter_svg`, `cached_network_image`, `shimmer`
- DO NOT add: `flutter_bloc`, `get_it`, `dio`, `connectivity_plus`, `equatable`
  (unused, add bloat, require justification + ADR)

## State Management
- Local UI state: `StatefulWidget` + `setState`
- Shared app state: migrate to `Riverpod` when >3 screens share state
- NEVER use BLoC for simple toggle/checkbox state
- ALWAYS check `mounted` before `setState` after async

## Design System
- All colors: `Theme.of(context).colorScheme` or `AppColors`
- All text: `Theme.of(context).textTheme`
- Minimum touch target: 48dp
- Card radius: 16dp, Button radius: 12dp
- Body text minimum: 16sp, line height 1.5

## Accessibility
- Every `IconButton` has `tooltip`
- No color-only feedback — pair with icon + text
- Test with 2.0x text scale
- All images: `semanticLabel` or `excludeFromSemantics: true`

## Performance
- `const` constructors everywhere possible
- `ListView.builder` for lists >10 items
- Dispose all controllers and listeners
- No `Theme.of(context)` in `initState`

## Deprecated API Migration
- `withOpacity(x)` → `withValues(alpha: x)`
- `primaryColor` → `colorScheme.primary`
- `accentColor` → `colorScheme.secondary`
- `backgroundColor` → `colorScheme.surface`

## Testing
- Unit test: all domain logic in `test/models/`
- Widget test: all screens in `test/features/`
- Use `debugNetworkImageHttpClientProvider` for network image mocks
- Mock repositories, never mock value objects

## Analysis
- Run `flutter analyze --fatal-infos` before commit
- Run `dart format .` before commit
- Strict mode enabled: `strict-casts`, `strict-inference`, `strict-raw-types`
