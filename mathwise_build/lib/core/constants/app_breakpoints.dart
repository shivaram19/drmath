/// Material 3 Window Size Classes & Content-Driven Breakpoints
///
/// Research basis:
/// - Material Design 3 (Google 2021–2026): Window size classes categorize
///   available screen space as compact, medium, expanded, large, extra-large [^1].
///   These are CONSTRAINT-based, not device-based. A phone in multi-window mode
///   can be "medium" even though the device is physically small.
///
/// - Flutter Docs (May 2026): "Use LayoutBuilder for constraint-based adaptation,
///   not MediaQuery for device size." [^2]
///
/// - freeCodeCamp / TechWithSam (2025–2026): Avoid hardcoded pixel values.
///   Use named constants or relative units (.sp, .w, .h via flutter_screenutil) [^3][^4].
///
/// Design decision: We use Material 3 standard breakpoints for layout CLASS
/// decisions (navigation rail vs. bottom bar, 1-col vs. 2-col grid). For
/// WIDGET-LEVEL thresholds ("can this Row fit two Text children side-by-side?"),
/// we define CONTENT-DERIVED minimums named after the content they protect,
/// not arbitrary device widths.
///
/// [^1]: https://m3.material.io/foundations/layout/applying-layout/window-size-classes
/// [^2]: https://docs.flutter.dev/ui/adaptive-responsive/best-practices
/// [^3]: https://www.freecodecamp.org/news/how-to-build-responsive-uis-in-flutter/
/// [^4]: https://dev.to/techwithsam/how-to-build-responsive-flutter-apps-for-phones-foldables-tablets-web-2026-140o
library;

/// Material 3 standard width breakpoints (in logical pixels / dp).
/// These define the five window size classes used for adaptive layout decisions.
abstract final class Breakpoints {
  /// Compact: phones in portrait, small foldables closed.
  /// Layout: single column, bottom navigation bar.
  static const double compact = 0;

  /// Medium: tablets in portrait, large phones in landscape, foldables open.
  /// Layout: two-column grid, navigation rail.
  static const double medium = 600;

  /// Expanded: small desktops, tablets in landscape.
  /// Layout: three-column grid, persistent navigation drawer.
  static const double expanded = 840;

  /// Large: standard desktops.
  /// Layout: spacious multi-column, sidebar navigation.
  static const double large = 1200;

  /// Extra-large: large desktops, ultrawide monitors.
  /// Layout: maximum content width with generous whitespace.
  static const double extraLarge = 1600;
}

/// Content-derived minimum widths for widget-level responsive decisions.
/// These answer the question: "How wide must THIS widget be to render
/// THIS content in THIS layout mode?"
///
/// Naming convention: kMinWidthFor<Content><LayoutMode>
/// Example: kMinWidthForHeaderTextsSideBySide = min width needed for
/// "Play & Learn" (displayMedium) + gap + "Unlocked by your effort" (bodyLarge).
abstract final class ContentMinWidths {
  /// Two stat cards side-by-side in a Row with Expanded.
  /// Each card needs ~160dp for icon (48) + gap (12) + text label + value.
  /// Two cards + 12dp gap = ~330dp. Below this, stack vertically.
  static const double twoStatCardsSideBySide = 330;

  /// Three stat boxes side-by-side in a Row with Expanded.
  /// Each box needs ~120dp for compact layout (icon above, text below).
  /// Three boxes + 2×12dp gaps = ~384dp.
  /// Below this, the boxes internally switch to vertical icon-over-text.
  static const double threeStatBoxesSideBySide = 384;

  /// Inside a single stat box: enough width for icon (48) + gap (12) + text.
  /// Below this threshold, the box switches to Column (icon above text).
  static const double statBoxRowLayout = 120;

  /// Two header text widgets side-by-side:
  /// "Play & Learn" at displayMedium (~180dp) + gap (12) +
  /// "Unlocked by your effort" at bodyLarge (~190dp) = ~382dp.
  /// Below this, stack vertically to prevent truncation.
  static const double headerTextsSideBySide = 382;

  /// Bento grid threshold: enough width for a two-column card layout
  /// with comfortable padding (24+24) and card min-width (~320 each).
  /// Matches Material 3 medium breakpoint (tablet landscape).
  static const double bentoTwoColumn = Breakpoints.medium;
}
