// lib/screens/home/home_screen.dart

import 'package:flutter/material.dart';
import 'tabs/car_tab.dart';
import 'tabs/electricity_tab.dart';
import 'tabs/flight_tab.dart';
import 'tabs/summary_tab.dart';
import 'tabs/cooking_tab.dart';
import 'dashboard_screen.dart'; // ✅ Added import for dashboard

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int currentIndex = 0;

  final screens = const [
    CarTab(),
    ElectricityTab(),
    FlightTab(),
    CookingTab(),
    SummaryTab(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF2F2F2),

      // ✅ Soft Rounded Rectangle Top Header
      appBar: PreferredSize(
        preferredSize: const Size.fromHeight(130),
        child: AppBar(
          elevation: 0,
          toolbarHeight: 120,
          automaticallyImplyLeading: false,
          backgroundColor: Colors.transparent,

          flexibleSpace: ClipPath(
            clipper: SoftTopClipper(),
            child: Container(
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  colors: [Color(0xFF1B5E20), Color(0xFF4CAF50)],
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                ),
              ),
            ),
          ),

          title: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: const [
              Icon(Icons.eco, color: Colors.white, size: 34),
              SizedBox(width: 10),
              Text(
                "ECOTRACK",
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 27,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.3,
                ),
              ),
            ],
          ),

          centerTitle: true,

          // ✅ Dashboard button on the top-right corner
          actions: [
            IconButton(
              icon: const Icon(Icons.dashboard, color: Colors.white),
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const DashboardTab(userId: 1),
                  ),
                );
              },
            ),
          ],
        ),
      ),

      body: AnimatedSwitcher(
        duration: const Duration(milliseconds: 300),
        child: screens[currentIndex],
      ),

      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.only(
            topLeft: Radius.circular(26),
            topRight: Radius.circular(26),
          ),
          boxShadow: [
            BoxShadow(
              blurRadius: 24,
              color: Colors.black12,
              offset: Offset(0, -3),
            ),
          ],
        ),
        child: NavigationBar(
          height: 70,
          backgroundColor: Colors.transparent,
          elevation: 0,
          selectedIndex: currentIndex,
          indicatorColor: const Color(0xFF4CAF50),
          animationDuration: const Duration(milliseconds: 350),
          onDestinationSelected: (index) {
            setState(() => currentIndex = index);
          },
          destinations: const [
            NavigationDestination(
              icon: Icon(Icons.directions_car_outlined),
              selectedIcon: Icon(Icons.directions_car),
              label: "Car",
            ),
            NavigationDestination(
              icon: Icon(Icons.bolt_outlined),
              selectedIcon: Icon(Icons.bolt),
              label: "Power",
            ),
            NavigationDestination(
              icon: Icon(Icons.flight_outlined),
              selectedIcon: Icon(Icons.flight),
              label: "Flight",
            ),
            NavigationDestination(
              icon: Icon(Icons.local_fire_department_outlined),
              selectedIcon: Icon(Icons.local_fire_department),
              label: "Cooking",
            ),
            NavigationDestination(
              icon: Icon(Icons.summarize_outlined),
              selectedIcon: Icon(Icons.summarize),
              label: "Summary",
            ),
          ],
        ),
      ),
    );
  }
}

// ✅ Soft Rounded Rectangle Curve (like a soft card top)
class SoftTopClipper extends CustomClipper<Path> {
  @override
  Path getClip(Size size) {
    final double curveHeight = 40; // small, subtle roundness

    final path = Path();

    // Start bottom-left
    path.lineTo(0, size.height - curveHeight);

    // ✅ Soft curve from left → center → right
    path.quadraticBezierTo(
      size.width / 2, size.height, // gentle rise
      size.width, size.height - curveHeight,
    );

    // Right edge → top
    path.lineTo(size.width, 0);

    // Close shape
    path.lineTo(0, 0);
    path.close();

    return path;
  }

  @override
  bool shouldReclip(covariant CustomClipper<Path> oldClipper) => false;
}
