import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../app/routes.dart';
import '../widgets/bottom_nav_bar.dart';

class PlaceholderScreen extends StatelessWidget {
  final String title;
  final int? navbarIndex;

  const PlaceholderScreen({
    super.key,
    required this.title,
    this.navbarIndex,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(title)),
      body: navbarIndex != null
          ? SafeArea(
              child: Stack(
                children: [
                  // Content - scrolls behind the floating navigation
                  Center(child: Text('Welcome to $title')),
                  // Floating bottom navigation - positioned at bottom of SafeArea
                  Positioned(
                    left: 0,
                    right: 0,
                    bottom: 0,
                    child: BottomNavBar(
                      currentIndex: navbarIndex!,
                      onTap: (index) {
                        final route = const [
                          AppRoutes.home,
                          AppRoutes.explore,
                          AppRoutes.profile,
                        ][index];
                        context.go(route);
                      },
                    ),
                  ),
                ],
              ),
            )
          : Center(child: Text('Welcome to $title')),
    );
  }
}
