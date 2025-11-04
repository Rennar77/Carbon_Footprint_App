// lib/services/log_service.dart
import '../services/api_service.dart';
import 'dart:convert';
import 'package:flutter/foundation.dart';

class LogService {
  /// ✅ Fetch available vehicles
  static Future<List<Map<String, dynamic>>?> getVehicles() async {
    final response = await ApiService.get("/vehicles", auth: true);
    if (response == null) return null;

    if (response["vehicles"] is List) {
      return List<Map<String, dynamic>>.from(response["vehicles"]);
    }
    return null;
  }

  /// ✅ Log car trip
  static Future<double?> logCar(String vehicleName, double distance,
      {String? category}) async {
    final data = await ApiService.post(
      "/log/car",
      {"vehicle_name": vehicleName, "distance": distance, "category": category},
      auth: true,
    );
    return data?["co2_kg"]?.toDouble();
  }
  /// ✅ Calculate CO₂ emission manually for a vehicle
static double calculateVehicleEmission(Map<String, dynamic> vehicle, double distanceKm) {
  final co2PerKm = (vehicle["comb_co2"] ?? 0).toDouble();
  return (co2PerKm * distanceKm) / 1000.0; // Convert g → kg
}


  /// ✅ Log electricity usage
  static Future<double?> logElectricity(double kwh, String region) async {
    final data = await ApiService.post(
      "/log/electricity",
      {"kwh": kwh, "region": region},
      auth: true,
    );
    return data?['co2_kg']?.toDouble();
  }

  /// ✅ Log flight
  static Future<double?> logFlight(double distanceKm, String classType) async {
    final data = await ApiService.post(
      "/log/flight",
      {"distance_km": distanceKm, "class_type": classType},
      auth: true,
    );
    return data?['co2_kg']?.toDouble();
  }

  /// ✅ Log cooking
  static Future<double?> logCooking(String type, double kgUsed) async {
    final data = await ApiService.post(
      "/log/cooking",
      {"type": type, "kg_used": kgUsed},
      auth: true,
    );
    return data?['co2_kg']?.toDouble();
  }

  /// ✅ Dashboard summary
  static Future<Map<String, dynamic>?> fetchSummary() async {
    return await ApiService.get("/dashboard/summary", auth: true);
  }
}
