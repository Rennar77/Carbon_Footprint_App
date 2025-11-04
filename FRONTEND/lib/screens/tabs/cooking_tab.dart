// lib/screens/home/cooking_tab.dart

import 'package:flutter/material.dart';
import '../../services/log_service.dart';
import '../../utils/theme.dart';

class CookingTab extends StatefulWidget {
  const CookingTab({super.key});

  @override
  State<CookingTab> createState() => _CookingTabState();
}

class _CookingTabState extends State<CookingTab>
    with SingleTickerProviderStateMixin {
  String type = 'charcoal';
  final TextEditingController kgController = TextEditingController();

  late AnimationController _flameController;

  @override
  void initState() {
    super.initState();
    _flameController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
      lowerBound: 0.85,
      upperBound: 1.15,
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _flameController.dispose();
    super.dispose();
  }

  Future<void> logCooking() async {
    final kg = double.tryParse(kgController.text);
    if (kg == null || kg <= 0) return;

    final co2 = await LogService.logCooking(type, kg);
    if (!mounted || co2 == null) return;

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Logged $type: ${co2.toStringAsFixed(2)} kg CO₂'),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    IconData fuelIcon =
        type == 'charcoal' ? Icons.local_fire_department : Icons.local_gas_station;

    return SingleChildScrollView(
      child: Column(
        children: [
          // ✅ Fire Gradient Header
          Container(
            width: double.infinity,
            padding: const EdgeInsets.fromLTRB(20, 40, 20, 40),
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  Color(0xFFFF7A00), // bright flame orange
                  Color(0xFFB80000), // deep fire red
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
                ScaleTransition(
                  scale: _flameController,
                  child: Icon(
                    fuelIcon,
                    size: 80,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  type == "charcoal"
                      ? "Charcoal Cooking"
                      : "LPG Cooking",
                  style: theme.textTheme.headlineSmall?.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  "Track your cooking emissions",
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: Colors.white.withOpacity(0.9),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          // ✅ Main Card
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
                  const Text(
                    "Fuel Type",
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.primaryGreen,
                    ),
                  ),
                  const SizedBox(height: 8),

                  DropdownButtonFormField<String>(
                    value: type,
                    decoration: InputDecoration(
                      filled: true,
                      fillColor: Colors.grey.shade100,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    items: const [
                      DropdownMenuItem(
                          value: 'charcoal', child: Text("Charcoal")),
                      DropdownMenuItem(
                          value: 'lpg', child: Text("LPG (Gas)")),
                    ],
                    onChanged: (val) => setState(() => type = val!),
                  ),

                  const SizedBox(height: 22),

                  const Text(
                    "Amount Used (kg)",
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.primaryGreen,
                    ),
                  ),
                  const SizedBox(height: 8),

                  TextField(
                    controller: kgController,
                    keyboardType: TextInputType.number,
                    decoration: InputDecoration(
                      hintText: "Enter kg consumed",
                      filled: true,
                      fillColor: Colors.grey.shade100,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),

                  const SizedBox(height: 26),

                  // ✅ Button — Green and Full-Width
                  SizedBox(
                    width: double.infinity,
                    height: 50,
                    child: ElevatedButton(
                      onPressed: logCooking,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.primaryGreen,
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                      ),
                      child: const Text(
                        "Log Cooking",
                        style: TextStyle(
                            fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 40),
        ],
      ),
    );
  }
}
