import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../shared/theme/pedagogy_tokens.dart';
import 'app_colors.dart';

class AppTheme {
  static ThemeData get lightTheme {
    final lexend = GoogleFonts.lexend();
    final jakarta = GoogleFonts.plusJakartaSans();

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      scaffoldBackgroundColor: AppColors.background,
      colorScheme: const ColorScheme(
        brightness: Brightness.light,
        primary: AppColors.primary,
        onPrimary: AppColors.onPrimary,
        primaryContainer: AppColors.primaryContainer,
        onPrimaryContainer: AppColors.onPrimaryContainer,
        secondary: AppColors.secondary,
        onSecondary: AppColors.onSecondary,
        secondaryContainer: AppColors.secondaryContainer,
        onSecondaryContainer: AppColors.onSecondaryContainer,
        tertiary: AppColors.tertiary,
        onTertiary: AppColors.onTertiary,
        tertiaryContainer: AppColors.tertiaryContainer,
        onTertiaryContainer: AppColors.onTertiaryContainer,
        error: AppColors.error,
        onError: AppColors.onPrimary,
        errorContainer: AppColors.errorContainer,
        onErrorContainer: AppColors.onErrorContainer,
        surface: AppColors.surface,
        onSurface: AppColors.onSurface,
        surfaceContainerHighest: AppColors.surfaceContainerHighest,
        surfaceContainerHigh: AppColors.surfaceContainerHigh,
        surfaceContainer: AppColors.surfaceContainer,
        surfaceContainerLow: AppColors.surfaceContainerLow,
        surfaceContainerLowest: AppColors.surfaceContainerLowest,
        outline: AppColors.outline,
        outlineVariant: AppColors.outlineVariant,
        inverseSurface: AppColors.inverseSurface,
        inversePrimary: AppColors.primaryFixedDim,
        shadow: Color(0x1F000000),
        scrim: Color(0x99000000),
      ),
      textTheme: TextTheme(
        displayLarge: lexend.copyWith(
          fontSize: 40,
          height: 1.2,
          letterSpacing: -0.02,
          fontWeight: FontWeight.w600,
          color: AppColors.onSurface,
        ),
        displayMedium: lexend.copyWith(
          fontSize: 32,
          height: 1.3,
          letterSpacing: -0.01,
          fontWeight: FontWeight.w600,
          color: AppColors.onSurface,
        ),
        displaySmall: lexend.copyWith(
          fontSize: 24,
          height: 1.4,
          fontWeight: FontWeight.w500,
          color: AppColors.onSurface,
        ),
        headlineMedium: jakarta.copyWith(
          fontSize: 18,
          height: 1.6,
          fontWeight: FontWeight.w400,
          color: AppColors.onSurface,
        ),
        bodyLarge: jakarta.copyWith(
          fontSize: 16,
          height: 1.6,
          fontWeight: FontWeight.w400,
          color: AppColors.onSurface,
        ),
        bodyMedium: jakarta.copyWith(
          fontSize: 14,
          height: 1.5,
          fontWeight: FontWeight.w400,
          color: AppColors.onSurfaceVariant,
        ),
        labelLarge: jakarta.copyWith(
          fontSize: 12,
          height: 1.0,
          letterSpacing: 0.05,
          fontWeight: FontWeight.w700,
          color: AppColors.onSurfaceVariant,
        ),
      ),
      appBarTheme: AppBarTheme(
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: false,
        backgroundColor: const Color(0xFFF8FAFC),
        foregroundColor: AppColors.onSurface,
        titleTextStyle: lexend.copyWith(
          fontSize: 20,
          fontWeight: FontWeight.w700,
          color: AppColors.primaryContainer,
        ),
      ),
      cardTheme: CardTheme(
        elevation: 0,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        color: AppColors.surfaceContainerLowest,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          elevation: 0,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          side: const BorderSide(color: AppColors.outlineVariant),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        ),
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: Colors.transparent,
        elevation: 0,
        type: BottomNavigationBarType.fixed,
        selectedItemColor: AppColors.primaryContainer,
        unselectedItemColor: AppColors.outline,
      ),
      extensions: const [PedagogyTokens.light],
    );
  }
}
