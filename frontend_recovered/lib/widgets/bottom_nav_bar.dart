import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../app/routes.dart';
import '../app/theme.dart';

/// A reusable three-destination floating bottom navigation bar for VirasatAI.
///
/// Destinations: Featured (Home), Explore, Profile.
///
/// A separate floating Scan pill button sits to the RIGHT of the navbar dock,
/// aligned vertically with it on the same row.
///
/// Navigation is kept configurable via [currentIndex] and [onTap] so the
/// owning screen controls routing (e.g. go_router) — no screen logic is
/// hard-coded inside this widget.
class BottomNavBar extends StatelessWidget implements PreferredSizeWidget {
  final int currentIndex;
  final ValueChanged<int> onTap;

  const BottomNavBar({
    super.key,
    required this.currentIndex,
    required this.onTap,
  });

  @override
  // Preferred height: top padding (4) + navbar row (58) + bottom lift (14) = 76
  Size get preferredSize => const Size.fromHeight(76);

  static const _destinations = <_NavDestination>[
    _NavDestination(
      icon: Icons.home_outlined,
      activeIcon: Icons.home_rounded,
      label: 'Featured',
    ),
    _NavDestination(
      icon: Icons.explore_outlined,
      activeIcon: Icons.explore_rounded,
      label: 'Explore',
    ),
    _NavDestination(
      icon: Icons.person_outline_rounded,
      activeIcon: Icons.person_rounded,
      label: 'Profile',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return SafeArea(
      top: false,
      child: Padding(
        // Horizontal margins: 16px each side; bottom lift: 14px; top gap: 4px.
        padding: const EdgeInsets.fromLTRB(16, 4, 16, 14),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            // ── Floating navbar capsule (takes remaining space on left) ────
            Expanded(
              child: DecoratedBox(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(32),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withAlpha(0x0D),
                      blurRadius: 20,
                      offset: const Offset(0, 8),
                    ),
                    BoxShadow(
                      color: Colors.black.withAlpha(0x08),
                      blurRadius: 6,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: ConstrainedBox(
                  constraints: const BoxConstraints(minHeight: 58),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 6,
                      vertical: 4,
                    ),
                    child: Row(
                      children: [
                        for (int i = 0; i < _destinations.length; i++)
                          Expanded(
                            child: _NavBarItem(
                              destination: _destinations[i],
                              selected: i == currentIndex,
                              onTap: () => onTap(i),
                              theme: theme,
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
              ),
            ),

            // ── Gap between dock and Scan button ─────────────────────────────
            const SizedBox(width: 10),

            // ── Floating Scan pill button (positioned on the right side) ─────
            _FloatingScanButton(
              onTap: () => context.push(AppRoutes.scan),
            ),
          ],
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Floating Scan Button
// ---------------------------------------------------------------------------

/// A compact floating pill button positioned to the RIGHT of the navbar dock.
class _FloatingScanButton extends StatelessWidget {
  final VoidCallback onTap;

  const _FloatingScanButton({required this.onTap});

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        color: AppTheme.primaryColor,
        borderRadius: BorderRadius.circular(28),
        boxShadow: [
          BoxShadow(
            color: AppTheme.primaryColor.withAlpha(0x55),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
          BoxShadow(
            color: Colors.black.withAlpha(0x14),
            blurRadius: 6,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(28),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(28),
          splashColor: Colors.white.withAlpha(0x20),
          child: ConstrainedBox(
            constraints: const BoxConstraints(minHeight: 58),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(
                    Icons.camera_alt_rounded,
                    color: Colors.white,
                    size: 20,
                  ),
                  const SizedBox(width: 6),
                  Text(
                    'Scan',
                    style: Theme.of(context).textTheme.labelLarge?.copyWith(
                          color: Colors.white,
                          fontWeight: FontWeight.w700,
                          fontSize: 14,
                        ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}


class _NavBarItem extends StatelessWidget {
  final _NavDestination destination;
  final bool selected;
  final VoidCallback onTap;
  final ThemeData theme;

  const _NavBarItem({
    required this.destination,
    required this.selected,
    required this.onTap,
    required this.theme,
  });

  @override
  Widget build(BuildContext context) {
    const activeColor = AppTheme.primaryColor;
    const inactiveColor = AppTheme.secondaryTextColor;

    return Tooltip(
      message: destination.label,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 240),
        curve: Curves.easeOutCubic,
        margin: const EdgeInsets.symmetric(horizontal: 4),
        decoration: BoxDecoration(
          color: selected ? activeColor.withAlpha(0x12) : Colors.transparent,
          borderRadius: BorderRadius.circular(22),
        ),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: onTap,
            borderRadius: BorderRadius.circular(22),
            child: ConstrainedBox(
              constraints: const BoxConstraints(minHeight: 50),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 6),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    AnimatedSlide(
                      duration: const Duration(milliseconds: 240),
                      curve: Curves.easeOutCubic,
                      offset: selected ? Offset.zero : const Offset(0, 0.08),
                      child: AnimatedScale(
                        duration: const Duration(milliseconds: 240),
                        curve: Curves.easeOutBack,
                        scale: selected ? 1.08 : 1.0,
                        child: AnimatedSwitcher(
                           duration: const Duration(milliseconds: 180),
                           switchInCurve: Curves.easeOut,
                           switchOutCurve: Curves.easeIn,
                           transitionBuilder: (child, animation) {
                             return FadeTransition(
                               opacity: animation,
                               child: ScaleTransition(
                                 scale: Tween<double>(
                                   begin: 0.94,
                                   end: 1.0,
                                 ).animate(animation),
                                 child: child,
                               ),
                             );
                           },
                           child: Icon(
                             selected ? destination.activeIcon : destination.icon,
                             key: ValueKey<bool>(selected),
                             color: selected ? activeColor : inactiveColor,
                             size: 24,
                           ),
                         ),
                      ),
                    ),
                    const SizedBox(height: 4),
                    AnimatedDefaultTextStyle(
                      duration: const Duration(milliseconds: 220),
                      curve: Curves.easeOutCubic,
                      style: theme.textTheme.labelSmall!.copyWith(
                        color: selected ? activeColor : inactiveColor,
                        fontWeight:
                            selected ? FontWeight.w700 : FontWeight.w500,
                      ),
                      child: Text(
                        destination.label,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _NavDestination {
  final IconData icon;
  final IconData activeIcon;
  final String label;

  const _NavDestination({
    required this.icon,
    required this.activeIcon,
    required this.label,
  });
}

