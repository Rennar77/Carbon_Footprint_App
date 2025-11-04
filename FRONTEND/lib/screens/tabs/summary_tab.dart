// lib/screens/tabs/summary_tab.dart
import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../services/api_service.dart';

class SummaryTab extends StatefulWidget {
  const SummaryTab({super.key});

  @override
  State<SummaryTab> createState() => _SummaryTabState();
}

class _SummaryTabState extends State<SummaryTab> {
  double totalCo2 = 0.0;
  Map<String, double> breakdown = {
    "Car": 0,
    "Electricity": 0,
    "Flight": 0,
    "Cooking": 0
  };
  int lowEmissionStreak = 0;
  bool loading = false;

  final List<Color> pieColors = [
    Colors.green,
    Colors.orange,
    Colors.blue,
    Colors.brown,
  ];

  @override
  void initState() {
    super.initState();
    _loadSummary();
  }

  Future<void> _loadSummary() async {
    setState(() => loading = true);

    final data = await ApiService.get("/dashboard/summary", auth: true);
    if (!mounted) return;
    if (data == null) {
      setState(() => loading = false);
      return;
    }

    final rawSummary = (data['summary'] ?? {}) as Map<String, dynamic>;

    final Map<String, double> newBreakdown = {
      "Car": 0,
      "Electricity": 0,
      "Flight": 0,
      "Cooking": 0,
    };

    rawSummary.forEach((k, v) {
      final label = k[0].toUpperCase() + k.substring(1);
      newBreakdown[label] = (v as num).toDouble();
    });

    setState(() {
      breakdown = newBreakdown;
      totalCo2 = (data['total_co2'] ?? 0).toDouble();
      lowEmissionStreak = data['low_emission_streak_days'] ?? 0;
      loading = false;
    });
  }

  List<PieChartSectionData> _pieSections() {
    int i = 0;
    return breakdown.entries.map((entry) {
      final value = entry.value;
      final color = pieColors[i % pieColors.length];
      i++;

      return PieChartSectionData(
        color: color,
        value: value,
        title: '',
        radius: 60,
      );
    }).toList();
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Card(
      elevation: 0,
      color: color.withOpacity(0.12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            CircleAvatar(
              backgroundColor: color.withOpacity(0.2),
              child: Icon(icon, color: color),
            ),
            const SizedBox(width: 16),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: const TextStyle(
                        fontSize: 14, color: Colors.black54)),
                Text(
                  value,
                  style: const TextStyle(
                      fontSize: 22, fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: _loadSummary,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _buildStatCard(
              'Total CO₂ (kg)',
              totalCo2.toStringAsFixed(2),
              Icons.cloud,
              Colors.green,
            ),
            const SizedBox(height: 12),
            _buildStatCard(
              'Low-emission streak',
              '$lowEmissionStreak days',
              Icons.bolt,
              Colors.orange,
            ),
            const SizedBox(height: 20),

            // ---- PIE CHART + LABELS ----
            SizedBox(
              height: 260,
              child: loading
                  ? const Center(child: CircularProgressIndicator())
                  : Row(
                      children: [
                        Expanded(
                          flex: 2,
                          child: PieChart(
                            PieChartData(
                              sections: _pieSections(),
                              sectionsSpace: 2,
                              centerSpaceRadius: 38,
                            ),
                          ),
                        ),
                        Expanded(
                          flex: 3,
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: breakdown.entries.map((e) {
                              final index =
                                  breakdown.keys.toList().indexOf(e.key);
                              final color = pieColors[index];

                              return Padding(
                                padding:
                                    const EdgeInsets.symmetric(vertical: 6),
                                child: Row(
                                  children: [
                                    Container(
                                      width: 14,
                                      height: 14,
                                      decoration: BoxDecoration(
                                        color: color,
                                        shape: BoxShape.circle,
                                      ),
                                    ),
                                    const SizedBox(width: 8),
                                    Text(
                                      '${e.key}: ${e.value.toStringAsFixed(1)} kg',
                                      style: const TextStyle(fontSize: 15),
                                    ),
                                  ],
                                ),
                              );
                            }).toList(),
                          ),
                        )
                      ],
                    ),
            ),

            const SizedBox(height: 24),

            // ---- BREAKDOWN CARD ----
            Card(
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12)),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: breakdown.entries.map((e) {
                    return Padding(
                      padding: const EdgeInsets.symmetric(vertical: 6),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(e.key, style: const TextStyle(fontSize: 16)),
                          Text(
                            '${e.value.toStringAsFixed(2)} kg',
                            style: const TextStyle(
                                fontSize: 16, fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                    );
                  }).toList(),
                ),
              ),
            ),

            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _loadSummary,
              icon: const Icon(Icons.refresh),
              label: const Text('Refresh Summary'),
            ),
            const SizedBox(height: 20),
            const Text(
              'Tip: Pull down to refresh the summary.',
              style: TextStyle(color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }
}
