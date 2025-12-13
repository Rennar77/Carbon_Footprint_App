import 'package:flutter/material.dart';
import 'package:carbon_footprint_app/screens/splash_screen.dart';
import 'package:carbon_footprint_app/screens/reset_password_screen.dart';
import 'package:carbon_footprint_app/utils/theme.dart';
import 'package:uni_links/uni_links.dart';
import 'dart:async';

void main() {
  runApp(const CarbonApp());
}

class CarbonApp extends StatefulWidget {
  const CarbonApp({super.key});

  @override
  State<CarbonApp> createState() => _CarbonAppState();
}

class _CarbonAppState extends State<CarbonApp> {
  final GlobalKey<NavigatorState> _navigatorKey = GlobalKey<NavigatorState>();
  StreamSubscription? _sub;

  @override
  void initState() {
    super.initState();
    _handleIncomingLinks();
  }

  void _handleIncomingLinks() {
    // Listen for app already opened via a link
    _sub = uriLinkStream.listen((Uri? uri) {
      if (uri != null && uri.host == 'reset-password') {
        final token = uri.queryParameters['token'];
        if (token != null) {
          _navigatorKey.currentState?.push(
            MaterialPageRoute(
              builder: (_) => ResetPasswordScreen(token: token),
            ),
          );
        }
      }
    }, onError: (err) {
      // Handle errors if needed
      debugPrint('Failed to handle link: $err');
    });
  }

  @override
  void dispose() {
    _sub?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      navigatorKey: _navigatorKey,
      debugShowCheckedModeBanner: false,
      title: 'Carbon Footprint',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: AppTheme.primaryGreen),
        scaffoldBackgroundColor: AppTheme.background,
        useMaterial3: true,
      ),
      home: const SplashScreen(),
    );
  }
}
