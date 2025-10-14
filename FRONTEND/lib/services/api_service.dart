import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:carbon_footprint_app/utils/constants.dart';

class ApiService {
  final http.Client _client;

  ApiService({http.Client? client}) : _client = client ?? http.Client();

  Future<String> fetchRootMessage() async {
    final uri = Uri.parse('${AppConstants.backendBaseUrl}/');
    final resp = await _client.get(uri);
    if (resp.statusCode != 200) {
      throw Exception('Failed to reach backend: ${resp.statusCode}');
    }
    final data = jsonDecode(resp.body) as Map<String, dynamic>;
    return data['message']?.toString() ?? 'OK';
  }

  Future<Map<String, dynamic>> estimateTrip({
    required String activityId,
    required Map<String, dynamic> parameters,
    String dataVersion = '25.25',
  }) async {
    final uri = Uri.parse('${AppConstants.backendBaseUrl}/v1/trips/estimate');
    final resp = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'activity_id': activityId,
        'data_version': dataVersion,
        'parameters': parameters,
      }),
    );
    if (resp.statusCode != 200) {
      throw Exception('Trip estimate failed: ${resp.statusCode} ${resp.body}');
    }
    return jsonDecode(resp.body) as Map<String, dynamic>;
  }
}

