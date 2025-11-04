import 'package:flutter/material.dart';
import '../../services/log_service.dart';

class CarTab extends StatefulWidget {
  const CarTab({super.key});

  @override
  State<CarTab> createState() => _CarTabState();
}

class _CarTabState extends State<CarTab> {

  final TextEditingController _distanceController = TextEditingController();
  final TextEditingController _makeController = TextEditingController();
  final TextEditingController _modelController = TextEditingController();
  final TextEditingController _mpgController = TextEditingController();

  List<Map<String, dynamic>> vehicles = [];
  Map<String, dynamic>? selectedVehicle;
  bool isCustomVehicle = false;
  double? estimatedEmission;

  @override
  void initState() {
    super.initState();
    _loadVehicles();
  }

  @override
  void dispose() {
    super.dispose();
  }

  Future<void> _loadVehicles() async {
    try {
      final data = await LogService.getVehicles();
      if (mounted) {
        setState(() => vehicles = data ?? []);
      }
    } catch (_) {}
  }

  Future<void> _previewEmission() async {
    final distance = double.tryParse(_distanceController.text);
    if (distance == null) return;

    Map<String, dynamic> vehicleData;

    if (isCustomVehicle) {
      vehicleData = {
        "make": _makeController.text,
        "model": _modelController.text,
        "comb_co2": double.tryParse(_mpgController.text) ?? 250.0,
      };
    } else if (selectedVehicle != null) {
      vehicleData = selectedVehicle!;
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Please select a vehicle first.")),
      );
      return;
    }

    final emission =
        LogService.calculateVehicleEmission(vehicleData, distance);

    setState(() {
      estimatedEmission = emission;
    });
  }

  Future<void> _logCar() async {
    final distance = double.tryParse(_distanceController.text);
    if (distance == null) return;

    final vehicleName = isCustomVehicle
        ? "${_makeController.text} ${_modelController.text}"
        : "${selectedVehicle?['make'] ?? ''} ${selectedVehicle?['model'] ?? ''}";

    final co2 = await LogService.logCar(vehicleName, distance);
    if (!mounted || co2 == null) return;

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          "Logged: ${co2.toStringAsFixed(2)} kg CO₂",
        ),
      ),
    );

    setState(() => estimatedEmission = null);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return SingleChildScrollView(
      child: Column(
        children: [
          // ✅ Full-width Gradient Header
          Container(
            width: double.infinity,
            padding: const EdgeInsets.fromLTRB(20, 40, 20, 40),
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  Color(0xFF2ECC71),
                  Color(0xFF27AE60),
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.only(
                bottomLeft: Radius.circular(28),
                bottomRight: Radius.circular(28),
              ),
            ),
            child: Column(
              children: [
                const Icon(
                  Icons.directions_car_rounded,
                  size: 80,
                  color: Colors.white,
                ),
                const SizedBox(height: 12),
                Text(
                  "Vehicle Emissions",
                  style: theme.textTheme.headlineSmall?.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  "Estimate & log your car's carbon output",
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: Colors.white.withOpacity(0.9),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          // ✅ Main Card (matching ElectricityTab)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: theme.cardColor,
                borderRadius: BorderRadius.circular(18),
                boxShadow: [
                  BoxShadow(
                    blurRadius: 14,
                    spreadRadius: 2,
                    color: Colors.black.withOpacity(0.06),
                    offset: const Offset(0, 6),
                  )
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // ✅ Switch
                  Row(
                    children: [
                      const Text(
                        "Use Custom Vehicle",
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                      const Spacer(),
                      Switch(
                        activeColor: Colors.green,
                        value: isCustomVehicle,
                        onChanged: (v) {
                          setState(() {
                            isCustomVehicle = v;
                            estimatedEmission = null;
                          });
                        },
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // ✅ Dropdown or Custom inputs
                  AnimatedSwitcher(
                    duration: const Duration(milliseconds: 300),
                    child: isCustomVehicle
                        ? Column(
                            key: const ValueKey("custom"),
                            children: [
                              _input(_makeController, "Make"),
                              const SizedBox(height: 12),
                              _input(_modelController, "Model"),
                              const SizedBox(height: 12),
                              _input(_mpgController, "CO₂ (g/km)",
                                  keyboard: TextInputType.number),
                            ],
                          )
                        : DropdownButtonFormField<Map<String, dynamic>>(
                            key: const ValueKey("dropdown"),
                            value: selectedVehicle,
                            items: vehicles
                                .map((v) => DropdownMenuItem(
                                      value: v,
                                      child: Text(
                                          "${v['make']} ${v['model']} (${v['year']})"),
                                    ))
                                .toList(),
                            onChanged: (v) =>
                                setState(() => selectedVehicle = v),
                            decoration: const InputDecoration(
                              labelText: "Select Vehicle",
                              border: OutlineInputBorder(),
                            ),
                          ),
                  ),

                  const SizedBox(height: 20),

                  // ✅ Distance input
                  _input(_distanceController, "Distance (km)",
                      keyboard: TextInputType.number),

                  const SizedBox(height: 28),

                  // ✅ Buttons
                  Row(
                    children: [
                      Expanded(
                        child: _greenButton(
                          icon: Icons.calculate,
                          text: "Estimate",
                          action: _previewEmission,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _greenButton(
                          icon: Icons.check_circle,
                          text: "Log Trip",
                          action: _logCar,
                        ),
                      ),
                    ],
                  ),

                  if (estimatedEmission != null) ...[
                    const SizedBox(height: 26),
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.green.shade100,
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: Text(
                        "Estimated Emission: ${estimatedEmission!.toStringAsFixed(2)} kg CO₂",
                        style: const TextStyle(
                          fontSize: 17,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),

          const SizedBox(height: 40),
        ],
      ),
    );
  }

  // ✅ Input field
  Widget _input(TextEditingController c, String label,
      {TextInputType keyboard = TextInputType.text}) {
    return TextField(
      controller: c,
      keyboardType: keyboard,
      decoration: InputDecoration(
        labelText: label,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
  }

  // ✅ Unified green button
  Widget _greenButton(
      {required IconData icon,
      required String text,
      required VoidCallback action}) {
    return ElevatedButton.icon(
      onPressed: action,
      icon: Icon(icon, color: Colors.white),
      label: Text(text, style: const TextStyle(color: Colors.white)),
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.green.shade600,
        padding: const EdgeInsets.symmetric(vertical: 14),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      ),
    );
  }
}
