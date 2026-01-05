import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  
  static const String baseUrl = "https://carbon-footprint-app-41f7.onrender.com";
  static const Map<String, String> _headers = {
    "Content-Type": "application/json",
  };

  // -------------------------------------------------------
  // POST
  // -------------------------------------------------------
  static Future<Map<String, dynamic>?> post(
    String endpoint,
    Map<String, dynamic> body, {
    bool auth = false,
  }) async {
    final headers = await _prepareHeaders(auth);

    final response = await http.post(
      Uri.parse("$baseUrl$endpoint"),
      headers: headers,
      body: jsonEncode(body),
    );

    return _returnResponse(response);
  }

  // -------------------------------------------------------
  // GET
  // -------------------------------------------------------
  static Future<Map<String, dynamic>?> get(
    String endpoint, {
    bool auth = false,
  }) async {
    final headers = await _prepareHeaders(auth);

    final response = await http.get(
      Uri.parse("$baseUrl$endpoint"),
      headers: headers,
    );

    return _returnResponse(response);
  }

  // -------------------------------------------------------
  // PUT
  // -------------------------------------------------------
  static Future<Map<String, dynamic>?> put(
    String endpoint,
    Map<String, dynamic> body, {
    bool auth = false,
  }) async {
    final headers = await _prepareHeaders(auth);

    final response = await http.put(
      Uri.parse("$baseUrl$endpoint"),
      headers: headers,
      body: jsonEncode(body),
    );

    return _returnResponse(response);
  }

  // -------------------------------------------------------
  // DELETE
  // -------------------------------------------------------
  static Future<Map<String, dynamic>?> delete(
    String endpoint, {
    bool auth = false,
  }) async {
    final headers = await _prepareHeaders(auth);

    final response = await http.delete(
      Uri.parse("$baseUrl$endpoint"),
      headers: headers,
    );

    return _returnResponse(response);
  }

  // -------------------------------------------------------
  // FILE UPLOAD (multipart)
  // -------------------------------------------------------
  static Future<Map<String, dynamic>?> uploadFile(
    String endpoint,
    String filePath, {
    bool auth = true,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');

    var request = http.MultipartRequest(
      "POST",
      Uri.parse("$baseUrl$endpoint"),
    );

    if (auth && token != null) {
      request.headers["Authorization"] = "Bearer $token";
    }

    request.files.add(
      await http.MultipartFile.fromPath(
        "file",
        filePath,
      ),
    );

    final response = await request.send();
    final responseBody = await response.stream.bytesToString();

    try {
      return jsonDecode(responseBody);
    } catch (_) {
      return {"detail": "Upload failed with ${response.statusCode}"};
    }
  }

  // -------------------------------------------------------
  // HELPERS
  // -------------------------------------------------------
  static Future<Map<String, String>> _prepareHeaders(bool auth) async {
    final headers = Map<String, String>.from(_headers);

    if (auth) {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString("token");
      if (token != null) {
        headers["Authorization"] = "Bearer $token";
      }
    }
    return headers;
  }

  static Map<String, dynamic>? _returnResponse(http.Response response) {
    try {
      return jsonDecode(response.body);
    } catch (e) {
      return {
        "detail": "Request failed with status ${response.statusCode}",
      };
    }
  }
}
