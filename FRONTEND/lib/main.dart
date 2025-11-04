import 'package:flutter/material.dart';
import 'package:carbon_footprint_app/screens/splash_screen.dart';
import 'package:carbon_footprint_app/utils/theme.dart';

void main() {
  runApp(const CarbonApp());
}

class CarbonApp extends StatelessWidget {
  const CarbonApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Carbon Footprint',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: AppTheme.primaryGreen),
        scaffoldBackgroundColor: AppTheme.background,
        useMaterial3: true,
      ),
      home: const SplashScreen(), // 👈 Start with the splash screen
    );
  }
}
