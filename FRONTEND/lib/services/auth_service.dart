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
        Uri.parse("${ApiService.baseUrl}/auth/login"),
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
        Uri.parse("${ApiService.baseUrl}/auth/register"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"name": name, "email": email, "password": password}),
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

  /// 🔹 Forgot Password
  static Future<Map<String, dynamic>> forgotPassword(String email) async {
    try {
      final response = await http.post(
        Uri.parse('${ApiService.baseUrl}/auth/forgot-password'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email}),
      );

      final data = jsonDecode(response.body);
      return {
        'success': response.statusCode == 200,
        'message': data['message'] ?? 'An error occurred',
        'token': data['token'], // For testing only
      };
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: $e',
      };
    }
  }

  /// 🔹 Reset Password
  static Future<Map<String, dynamic>> resetPassword({
    required String token,
    required String newPassword,
    int? userId,
  }) async {
    try {
      final Map<String, dynamic> body = {
        'token': token,
        'new_password': newPassword,
      };

      if (userId != null) {
        body['user_id'] = userId;
      }

      final response = await http.post(
        Uri.parse('${ApiService.baseUrl}/auth/reset-password'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(body),
      );

      if (response.statusCode == 200) {
        return {
          'success': true,
          'message': 'Password reset successful',
        };
      } else {
        final data = jsonDecode(response.body);
        return {
          'success': false,
          'message': data['detail'] ?? 'Failed to reset password',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: $e',
      };
    }
  }

  /// 🔹 Verify Reset Token
  static Future<Map<String, dynamic>> verifyResetToken({
    required String token,
    int? userId,
  }) async {
    try {
      final Map<String, dynamic> body = {'token': token};

      if (userId != null) {
        body['user_id'] = userId;
      }

      final response = await http.post(
        Uri.parse('${ApiService.baseUrl}/auth/verify-reset-token'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(body),
      );

      final data = jsonDecode(response.body);
      return {
        'valid': data['valid'] ?? false,
        'message': data['message'],
        'user_id': data['user_id'],
      };
    } catch (e) {
      return {
        'valid': false,
        'message': 'Network error: $e',
      };
    }
  }
}
