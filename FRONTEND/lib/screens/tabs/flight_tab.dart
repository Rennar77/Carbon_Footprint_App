import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

class FlightTab extends StatefulWidget {
  const FlightTab({super.key});

  @override
  State<FlightTab> createState() => _FlightTabState();
}

class _FlightTabState extends State<FlightTab>
    with SingleTickerProviderStateMixin {

  final TextEditingController _distanceController = TextEditingController();
  String _selectedClass = 'Economy';
  double? _calculatedCO2;
  bool _isLoading = false;

  late AnimationController _planeController;
  late Animation<Offset> _planeOffset;

  @override
  void initState() {
    super.initState();

    _planeController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    )..repeat(reverse: true);

    _planeOffset = Tween<Offset>(
      begin: const Offset(-0.25, 0.15),
      end: const Offset(0.25, -0.1),
    ).animate(
      CurvedAnimation(
        parent: _planeController,
        curve: Curves.easeInOut,
      ),
    );
  }

  @override
  void dispose() {
    _distanceController.dispose();
    _planeController.dispose();
    super.dispose();
  }

  Future<void> _calculateFlightEmission() async {
    final distance = double.tryParse(_distanceController.text);

    if (distance == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Please enter a valid distance")),
      );
      return;
    }

    setState(() => _isLoading = true);

    try {
      final response = await http.post(
        Uri.parse("http://10.0.2.2:8000/api/calculate_flight_emission"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "distance": distance,
          "travel_class": _selectedClass,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);

        setState(() {
          _calculatedCO2 = data["emission"];
          _isLoading = false;
        });
      } else {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Error: ${response.body}")),
        );
      }
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return SingleChildScrollView(
      child: Column(
        children: [
          // ✅ Uniform Gradient Header (like Cooking/Electricity)
          Container(
            width: double.infinity,
            padding: const EdgeInsets.fromLTRB(20, 40, 20, 40),
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  Color(0xFF00C6FF),
                  Color(0xFF0072FF),
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
                SlideTransition(
                  position: _planeOffset,
                  child: const Icon(
                    Icons.flight_takeoff_rounded,
                    size: 90,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  "Flight Emissions",
                  style: theme.textTheme.headlineSmall?.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  "Calculate CO₂ from your trip",
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: Colors.white.withOpacity(0.9),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          // ✅ Main Card (exactly matches the pattern)
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
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    "Flight Distance (km)",
                    style: TextStyle(
                        fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 10),

                  TextField(
                    controller: _distanceController,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      hintText: "Enter distance in km",
                      border: OutlineInputBorder(),
                    ),
                  ),

                  const SizedBox(height: 22),

                  const Text(
                    "Travel Class",
                    style: TextStyle(
                        fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 6),

                  DropdownButtonFormField<String>(
                    value: _selectedClass,
                    decoration: const InputDecoration(
                      border: OutlineInputBorder(),
                    ),
                    items: const [
                      DropdownMenuItem(
                          value: "Economy", child: Text("Economy Class")),
                      DropdownMenuItem(
                          value: "Business", child: Text("Business Class")),
                      DropdownMenuItem(
                          value: "First", child: Text("First Class")),
                    ],
                    onChanged: (value) =>
                        setState(() => _selectedClass = value!),
                  ),

                  const SizedBox(height: 28),

                  // ✅ Same Green Button as Car/Electricity/Cooking
                  SizedBox(
                    width: double.infinity,
                    height: 50,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green.shade600,
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                      ),
                      onPressed: _calculateFlightEmission,
                      child: const Text(
                        "Calculate CO₂ Emission",
                        style: TextStyle(
                          fontSize: 17,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          if (_calculatedCO2 != null) ...[
            const SizedBox(height: 24),

            // ✅ Result card styled like other tabs
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: theme.colorScheme.primary.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Column(
                  children: [
                    const Text(
                      "Estimated CO₂ Emission",
                      style:
                          TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      "${_calculatedCO2!.toStringAsFixed(2)} kg",
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: theme.colorScheme.primary,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],

          const SizedBox(height: 40), // ✅ No awkward bottom space
        ],
      ),
    );
  }
}
