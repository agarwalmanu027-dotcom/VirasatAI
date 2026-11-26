import 'package:flutter/material.dart';

class AppTheme {
  static const primaryColor = Color(0xFF4E3528);
  static const accentColor = Color(0xFFB56A30);
  static const backgroundColor = Color(0xFFFBF5EA);
  static const surfaceColor = Color(0xFFFFFDF8);
  static const primaryTextColor = Color(0xFF2A211B);
  static const secondaryTextColor = Color(0xFF735F51);

  static ThemeData get light {
    return ThemeData(
      useMaterial3: true,
      colorScheme: const ColorScheme.light(
        primary: primaryColor,
        secondary: accentColor,
        surface: surfaceColor,
        onPrimary: Colors.white,
        onSecondary: Colors.white,
        onSurface: primaryTextColor,
      ),
      scaffoldBackgroundColor: backgroundColor,
      textTheme: const TextTheme(
        displayLarge: TextStyle(fontFamily: 'Inter', color: primaryTextColor),
        displayMedium: TextStyle(fontFamily: 'Inter', color: primaryTextColor),
        displaySmall: TextStyle(fontFamily: 'Inter', color: primaryTextColor),
        headlineLarge: TextStyle(fontFamily: 'Inter', color: primaryTextColor),
        headlineMedium: TextStyle(fontFamily: 'Inter', color: primaryTextColor),
        headlineSmall: TextStyle(fontFamily: 'Inter', color: primaryTextColor),
        titleLarge: TextStyle(fontFamily: 'Inter', color: primaryTextColor),
        titleMedium: TextStyle(fontFamily: 'Inter', color: primaryTextColor),
        titleSmall: TextStyle(fontFamily: 'Inter', color: primaryTextColor),
        bodyLarge: TextStyle(fontFamily: 'Inter', color: primaryTextColor),
        bodyMedium: TextStyle(fontFamily: 'Inter', color: primaryTextColor),
        bodySmall: TextStyle(fontFamily: 'Inter', color: secondaryTextColor),
        labelLarge: TextStyle(fontFamily: 'Inter', color: primaryTextColor),
        labelMedium: TextStyle(fontFamily: 'Inter', color: secondaryTextColor),
        labelSmall: TextStyle(fontFamily: 'Inter', color: secondaryTextColor),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: surfaceColor,
        foregroundColor: primaryTextColor,
        elevation: 0,
        centerTitle: false,
      ),
    );
  }
}
