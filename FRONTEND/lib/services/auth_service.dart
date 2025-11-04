import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'api_service.dart';

class AuthService {
  /// 🔹 Login user
  static Future<Map<String, dynamic>> login(
      String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse("${ApiService.baseUrl}/auth/login"), // ✅ Fixed endpoint
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"email": email, "password": password}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final token = data['token'];

        if (token != null) {
          final prefs = await SharedPreferences.getInstance();
          await prefs.setString('token', token);
        }

        return {"success": true, "data": data};
      } else {
        return {
          "success": false,
          "message":
              jsonDecode(response.body)['detail'] ?? 'Login failed. Try again.'
        };
      }
    } catch (e) {
      return {"success": false, "message": "Error: $e"};
    }
  }

  /// 🔹 Register user
  static Future<Map<String, dynamic>> register(
      String name, String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse("${ApiService.baseUrl}/auth/register"), // ✅ Fixed endpoint
        headers: {"Content-Type": "application/json"},
        body:
            jsonEncode({"name": name, "email": email, "password": password}),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return {
          "success": true,
          "message": "Registration successful! You can now log in."
        };
      } else {
        return {
          "success": false,
          "message":
              jsonDecode(response.body)['detail'] ?? 'Registration failed.'
        };
      }
    } catch (e) {
      return {"success": false, "message": "Error: $e"};
    }
  }

  /// 🔹 Logout user
  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('token');
  }

  /// 🔹 Check login status
  static Future<bool> isLoggedIn() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('token') != null;
  }

  /// 🔹 Get stored token
  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('token');
  }
}
