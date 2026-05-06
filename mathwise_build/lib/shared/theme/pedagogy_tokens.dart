import 'dart:ui';

import 'package:flutter/material.dart';

/// Pedagogy-specific design tokens for the MathWise app.
///
/// These tokens extend Material 3's ColorScheme with colors and metrics
/// specifically chosen for math education accessibility.
///
/// Usage:
/// ```dart
/// final tokens = Theme.of(context).extension<PedagogyTokens>()!;
/// Container(color: tokens.successGreen.withValues(alpha: 0.1));
/// ```
@immutable
class PedagogyTokens extends ThemeExtension<PedagogyTokens> {
  const PedagogyTokens({
    required this.successGreen,
    required this.hintAmber,
    required this.errorRose,
    required this.minTouchTarget,
    required this.cardRadius,
    required this.buttonRadius,
    required this.spacingXs,
    required this.spacingSm,
    required this.spacingMd,
    required this.spacingLg,
    required this.spacingXl,
  });

  /// Feedback color for correct answers.
  /// Rationale: Green signals competence (Deci & Ryan 2000) [^23].
  final Color successGreen;

  /// Feedback color for scaffolded hints.
  /// Rationale: Amber signals "attention, not alarm" (Elliot & Maier 2014) [^14].
  final Color hintAmber;

  /// Feedback color for incorrect answers.
  /// Rationale: Soft rose reduces math anxiety vs pure red [^14].
  final Color errorRose;

  /// Minimum touch target size.
  /// Rationale: WCAG 2.5.5; Parhi et al. (2006) [^11].
  final double minTouchTarget;

  /// Card border radius.
  final double cardRadius;

  /// Button border radius.
  final double buttonRadius;

  /// Extra-small spacing (4dp).
  final double spacingXs;

  /// Small spacing (8dp).
  final double spacingSm;

  /// Medium spacing (16dp).
  final double spacingMd;

  /// Large spacing (24dp).
  final double spacingLg;

  /// Extra-large spacing (32dp).
  final double spacingXl;

  /// Default token set for light theme.
  static const light = PedagogyTokens(
    successGreen: Color(0xFF4CAF50),
    hintAmber: Color(0xFFFF9800),
    errorRose: Color(0xFFE91E63),
    minTouchTarget: 48.0,
    cardRadius: 16.0,
    buttonRadius: 12.0,
    spacingXs: 4.0,
    spacingSm: 8.0,
    spacingMd: 16.0,
    spacingLg: 24.0,
    spacingXl: 32.0,
  );

  @override
  PedagogyTokens copyWith({
    Color? successGreen,
    Color? hintAmber,
    Color? errorRose,
    double? minTouchTarget,
    double? cardRadius,
    double? buttonRadius,
    double? spacingXs,
    double? spacingSm,
    double? spacingMd,
    double? spacingLg,
    double? spacingXl,
  }) {
    return PedagogyTokens(
      successGreen: successGreen ?? this.successGreen,
      hintAmber: hintAmber ?? this.hintAmber,
      errorRose: errorRose ?? this.errorRose,
      minTouchTarget: minTouchTarget ?? this.minTouchTarget,
      cardRadius: cardRadius ?? this.cardRadius,
      buttonRadius: buttonRadius ?? this.buttonRadius,
      spacingXs: spacingXs ?? this.spacingXs,
      spacingSm: spacingSm ?? this.spacingSm,
      spacingMd: spacingMd ?? this.spacingMd,
      spacingLg: spacingLg ?? this.spacingLg,
      spacingXl: spacingXl ?? this.spacingXl,
    );
  }

  @override
  PedagogyTokens lerp(ThemeExtension<PedagogyTokens>? other, double t) {
    if (other is! PedagogyTokens) return this;
    return PedagogyTokens(
      successGreen: Color.lerp(successGreen, other.successGreen, t)!,
      hintAmber: Color.lerp(hintAmber, other.hintAmber, t)!,
      errorRose: Color.lerp(errorRose, other.errorRose, t)!,
      minTouchTarget: lerpDouble(minTouchTarget, other.minTouchTarget, t)!,
      cardRadius: lerpDouble(cardRadius, other.cardRadius, t)!,
      buttonRadius: lerpDouble(buttonRadius, other.buttonRadius, t)!,
      spacingXs: lerpDouble(spacingXs, other.spacingXs, t)!,
      spacingSm: lerpDouble(spacingSm, other.spacingSm, t)!,
      spacingMd: lerpDouble(spacingMd, other.spacingMd, t)!,
      spacingLg: lerpDouble(spacingLg, other.spacingLg, t)!,
      spacingXl: lerpDouble(spacingXl, other.spacingXl, t)!,
    );
  }
}
