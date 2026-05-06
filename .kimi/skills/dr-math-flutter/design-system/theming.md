# Theming — ColorScheme, ThemeExtension, Material 3

**Single Responsibility:** Implement a complete, accessible theme in Flutter.

## Material 3 Foundation

```dart
// shared/theme/app_theme.dart
import 'package:flutter/material.dart';

class AppTheme {
  static const _seedColor = Color(0xFF6750A4);

  static ThemeData light() {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: _seedColor,
      brightness: Brightness.light,
    );
    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: const Color(0xFFF8F9FA),
      textTheme: _buildTextTheme(colorScheme),
      cardTheme: _cardTheme,
      elevatedButtonTheme: _elevatedButtonTheme,
      extensions: const [AppSpacing.small()],
    );
  }

  static ThemeData dark() {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: _seedColor,
      brightness: Brightness.dark,
    );
    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: const Color(0xFF1C1B1F),
      textTheme: _buildTextTheme(colorScheme),
      cardTheme: _cardTheme,
      elevatedButtonTheme: _elevatedButtonTheme,
      extensions: const [AppSpacing.small()],
    );
  }
}
```

## ThemeExtension for Custom Tokens

```dart
// shared/theme/extensions.dart
@immutable
class AppSpacing extends ThemeExtension<AppSpacing> {
  final double xs;
  final double sm;
  final double md;
  final double lg;
  final double xl;

  const AppSpacing.small()
      : xs = 4, sm = 8, md = 12, lg = 16, xl = 24;

  const AppSpacing.large()
      : xs = 8, sm = 12, md = 16, lg = 24, xl = 32;

  @override
  AppSpacing copyWith({/*...*/}) => /*...*/;

  @override
  AppSpacing lerp(ThemeExtension<AppSpacing>? other, double t) => /*...*/;
}

// Access:
final spacing = Theme.of(context).extension<AppSpacing>()!;
Padding(padding: EdgeInsets.all(spacing.md))
```

## Typography for Children (12-13 y/o)

```dart
TextTheme _buildTextTheme(ColorScheme scheme) {
  return TextTheme(
    displayLarge: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: scheme.onSurface),
    titleLarge: TextStyle(fontSize: 24, fontWeight: FontWeight.w600, color: scheme.onSurface),
    bodyLarge: TextStyle(fontSize: 18, height: 1.5, color: scheme.onSurface), // Readable
    bodyMedium: TextStyle(fontSize: 16, height: 1.4, color: scheme.onSurfaceVariant),
    labelLarge: TextStyle(fontSize: 14, fontWeight: FontWeight.w500, color: scheme.primary),
  );
}
```

**Rule:** Minimum body text 16sp. Line height 1.4-1.5 for dyslexia accessibility.

## Component Theme Overrides

```dart
static final _cardTheme = CardTheme(
  elevation: 2,
  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
  margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
);

static final _elevatedButtonTheme = ElevatedButtonThemeData(
  style: ElevatedButton.styleFrom(
    minimumSize: const Size(48, 48), // Touch target
    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
  ),
);
```

## Anti-Patterns

| Anti-Pattern | Fix |
|-------------|-----|
| `primaryColor` / `accentColor` | Use `colorScheme.primary` / `colorScheme.secondary` |
| `backgroundColor` | Use `colorScheme.surface` |
| Hardcoded `withOpacity` | Use `colorScheme.primary.withValues(alpha: 0.1)` |
| `Theme.of(context)` in `initState` | Move to `didChangeDependencies` |
| Not handling text scale | Test with `MediaQuery.textScaleFactorOf(context) > 1.0` |

## Expert Sources

Material Design 3. "Color system." https://m3.material.io/styles/color  
FreeCodeCamp. "Theming and Customization in Flutter." https://www.freecodecamp.org/news/theming-and-customization-in-flutter
