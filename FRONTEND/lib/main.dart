import 'package:flutter/material.dart';
import 'package:carbon_footprint_app/screens/splash_screen.dart';
import 'package:carbon_footprint_app/screens/reset_password_screen.dart';
import 'package:carbon_footprint_app/utils/theme.dart';
import 'package:app_links/app_links.dart';
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
  StreamSubscription<Uri>? _appLinkSubscription;

  @override
  void initState() {
    super.initState();
    _initAppLinks();
  }

  Future<void> _initAppLinks() async {
    final appLinks = AppLinks();

    try {
      // Get the initial link if the app was opened with a link
      // Note: Use getInitialLink() instead of getInitialAppLink()
      final initialLink = await appLinks.getInitialLink();
      if (initialLink != null) {
        _handleAppLink(initialLink);
      }
    } catch (e) {
      debugPrint('Failed to get initial link: $e');
    }

    // Listen for app links while the app is running
    _appLinkSubscription = appLinks.uriLinkStream.listen(
      (Uri uri) {
        _handleAppLink(uri);
      },
      onError: (Object error, StackTrace stackTrace) {
        debugPrint('Error handling app link: $error');
      },
    );
  }

  void _handleAppLink(Uri uri) {
    debugPrint('Handling app link: $uri');
    
    if (uri.host == 'reset-password') {
      final token = uri.queryParameters['token'];
      final userIdStr = uri.queryParameters['user_id'];
      final int? userId = userIdStr != null ? int.tryParse(userIdStr) : null;
      
      if (token != null) {
        WidgetsBinding.instance.addPostFrameCallback((_) {
          _navigatorKey.currentState?.pushAndRemoveUntil(
            MaterialPageRoute(
              builder: (_) => ResetPasswordScreen(
                token: token,
                userId: userId,
              ),
            ),
            (route) => false,
          );
        });
      }
    }
  }

  @override
  void dispose() {
    _appLinkSubscription?.cancel();
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