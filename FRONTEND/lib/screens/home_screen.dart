import 'package:flutter/material.dart';
import 'package:carbon_footprint_app/services/api_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ApiService _api = ApiService();
  String? _message;
  String? _error;
  Map<String, dynamic>? _estimate;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final msg = await _api.fetchRootMessage();
      if (!mounted) return;
      setState(() => _message = msg);
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Carbon Footprint')),
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (_error != null) Text('Error: $_error'),
            if (_message == null && _error == null)
              const CircularProgressIndicator()
            else if (_message != null)
              Text(_message!),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _runSampleTripEstimate,
              child: const Text('Run Sample Trip Estimate'),
            ),
            if (_estimate != null) ...[
              const SizedBox(height: 16),
              Text('Result: ${_estimate!['co2e']} ${_estimate!['co2e_unit']}'),
            ]
          ],
        ),
      ),
    );
  }

  Future<void> _runSampleTripEstimate() async {
    setState(() {
      _error = null;
      _estimate = null;
    });
    try {
      // Example: medium car, distance in km
      final res = await _api.estimateTrip(
        activityId: 'passenger_vehicle-vehicle_type_medium-fuel_source_na-distance_na-occupancy_na',
        parameters: {
          'distance': 10,
          'distance_unit': 'km',
        },
      );
      if (!mounted) return;
      setState(() => _estimate = res);
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e.toString());
    }
  }
}

