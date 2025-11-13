import 'package:flutter/material.dart';
import '../services/api_service.dart';

class DashboardTab extends StatefulWidget {
  final int userId;

  const DashboardTab({super.key, required this.userId});

  @override
  State<DashboardTab> createState() => _DashboardTabState();
}

class _DashboardTabState extends State<DashboardTab> {
  String? recommendation;
  List<Map<String, String>> badges = [];
  bool loading = true;

  // Keep track of badges we've already shown popups for
  final Set<String> _shownBadgeNames = {};

  @override
  void initState() {
    super.initState();
    _fetchRecommendation();
  }

  Future<void> _fetchRecommendation() async {
    setState(() => loading = true);

    final data = await ApiService.get("/api/recommendation/${widget.userId}");

    if (data != null) {
      final rec = data['recommendation']?.toString();
      final List<dynamic> badgeData = data['badges'] ?? [];

      // Convert badges to proper string map
      final List<Map<String, String>> badgeList = badgeData
          .map<Map<String, String>>((b) => {
                "name": b['name'].toString(),
                "description": b['description'].toString()
              })
          .toList();

      setState(() {
        recommendation = rec;
        badges = badgeList;
        loading = false;
      });

      // Show badge popups for any new badges
      for (var badge in badgeList) {
        if (!_shownBadgeNames.contains(badge['name'])) {
          _shownBadgeNames.add(badge['name']!);
          _showBadgePopup(badge['name']!, badge['description']!);
        }
      }
    } else {
      setState(() => loading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Failed to load dashboard data')),
      );
    }
  }

  void _showBadgePopup(String title, String description) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: Text("🏅 $title"),
        content: Text(description),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("Close"),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Recommendation Card
                  if (recommendation != null) ...[
                    Card(
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                      color: Colors.green.shade50,
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Text(
                          recommendation!,
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),
                  ],

                  // Badges List
                  if (badges.isNotEmpty) ...[
                    const Text(
                      "New Badges Earned",
                      style:
                          TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 12),
                    Column(
                      children: badges
                          .map((b) => Card(
                                shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(12)),
                                color: Colors.amber.shade50,
                                child: ListTile(
                                  leading: const Icon(Icons.emoji_events,
                                      color: Colors.amber),
                                  title: Text(b['name']!),
                                  subtitle: Text(b['description']!),
                                ),
                              ))
                          .toList(),
                    ),
                    const SizedBox(height: 24),
                  ],

                  if (badges.isEmpty)
                    const Text(
                      "No new badges earned yet. Keep logging activities!",
                      style: TextStyle(fontSize: 16),
                    ),
                ],
              ),
            ),
    );
  }
}
