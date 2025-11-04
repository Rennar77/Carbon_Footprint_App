import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String baseUrl = "http://192.168.1.6:8000"; // your backend IP
  static const Map<String, String> _headers = {
    "Content-Type": "application/json",
  };

  /// 🔹 POST request
  static Future<Map<String, dynamic>?> post(
    String endpoint,
    Map<String, dynamic> body, {
    bool auth = false,
  }) async {
    final headers = Map<String, String>.from(_headers);

    // Attach token if needed
    if (auth) {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }
    }

    final response = await http.post(
      Uri.parse("$baseUrl$endpoint"),
      headers: headers,
      body: jsonEncode(body),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      try {
        return jsonDecode(response.body);
      } catch (_) {
        return {"detail": "Request failed with ${response.statusCode}"};
      }
    }
  }

  /// 🔹 GET request
  static Future<Map<String, dynamic>?> get(
    String endpoint, {
    bool auth = false,
  }) async {
    final headers = Map<String, String>.from(_headers);

    if (auth) {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }
    }

    final response = await http.get(
      Uri.parse("$baseUrl$endpoint"),
      headers: headers,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      try {
        return jsonDecode(response.body);
      } catch (_) {
        return {"detail": "Request failed with ${response.statusCode}"};
      }
    }
  }
}
