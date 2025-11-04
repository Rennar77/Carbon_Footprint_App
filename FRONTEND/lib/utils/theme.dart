import 'package:flutter/material.dart';

class AppTheme {
  static const Color primaryGreen = Color(0xFF4CAF50);
  static const Color accentGreen = Color(0xFF81C784);
  static const Color background = Color(0xFFF5F5F5);
  static const Color lightGrey = Color(0xFFDDDDDD);
  static const Color textGrey = Color(0xFF888888);



  static ThemeData lightTheme = ThemeData(
    primaryColor: primaryGreen,
    colorScheme: ColorScheme.fromSeed(seedColor: primaryGreen),
    scaffoldBackgroundColor: Colors.white,
    textTheme: const TextTheme(
      bodyMedium: TextStyle(color: Colors.black87),
    ),
    useMaterial3: true,
  );
}
