import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../app/theme.dart';

/// Reusable full-bleed background shell for the authentication / onboarding
/// screens (Welcome, Login, …).
///
/// Paints the Taj Mahal photograph edge-to-edge behind a transparent status bar
/// and veils it with the same cinematic dark-navy gradient used by
/// [AuthWelcomeScreen], then lays the supplied [child] on top inside a
/// [SafeArea].
///
/// It owns ONLY the presentation shell — the background image, the gradient
/// overlay, the system/status-bar treatment and the safe full-screen structure.
/// It deliberately contains no branding, buttons, fields, cards, navigation or
/// authentication logic.
class AuthBackground extends StatefulWidget {
  const AuthBackground({super.key, required this.child});

  /// Taj Mahal hero asset declared in `pubspec.yaml`.
  static const String heroAssetPath = 'assets/images/taj_mahal.jpg';

  /// Foreground content rendered on top of the background.
  final Widget child;

  @override
  State<AuthBackground> createState() => _AuthBackgroundState();
}

class _AuthBackgroundState extends State<AuthBackground> {
  /// Status bar appearance while the background is visible: kept visible and
  /// transparent so the photograph flows behind it, with light icons because
  /// the upper portion of the photograph is dark.
  static const SystemUiOverlayStyle _heroOverlayStyle = SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light,
    statusBarBrightness: Brightness.dark,
    systemStatusBarContrastEnforced: false,
  );

  /// Appearance restored on dispose so the rest of the app keeps its existing
  /// status bar styling.
  static const SystemUiOverlayStyle _defaultOverlayStyle = SystemUiOverlayStyle(
    statusBarColor: Colors.black,
    statusBarIconBrightness: Brightness.light,
    statusBarBrightness: Brightness.dark,
  );

  @override
  void initState() {
    super.initState();
    // Edge-to-edge rendering: the photograph paints behind the status bar while
    // both system overlays remain visible.
    SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);
    SystemChrome.setSystemUIOverlayStyle(_heroOverlayStyle);
  }

  @override
  void dispose() {
    SystemChrome.setSystemUIOverlayStyle(_defaultOverlayStyle);
    SystemChrome.setEnabledSystemUIMode(
      SystemUiMode.manual,
      overlays: SystemUiOverlay.values,
    );
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // Dark sous-surface so the photograph starts cleanly before it paints;
      // the full-bleed image covers the entire window on top of it.
      backgroundColor: AppTheme.primaryColor,
      body: Stack(
        fit: StackFit.expand,
        children: [
          const _TajMahalBackground(),
          const _CinematicGradient(),
          SafeArea(child: widget.child),
        ],
      ),
    );
  }
}

/// Full-window Taj Mahal photograph (BoxFit.cover) with a built-in fallback
/// so the screen always renders even if the asset cannot be read.
class _TajMahalBackground extends StatelessWidget {
  const _TajMahalBackground();

  @override
  Widget build(BuildContext context) {
    return Image.asset(
      AuthBackground.heroAssetPath,
      fit: BoxFit.cover,
      alignment: Alignment.center,
      errorBuilder: (context, error, stackTrace) => const _HeroFallback(),
    );
  }
}

/// Minimal private fallback for the hero photograph.
class _HeroFallback extends StatelessWidget {
  const _HeroFallback();

  @override
  Widget build(BuildContext context) {
    return const DecoratedBox(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [Color(0xFF79523A), AppTheme.primaryColor],
        ),
      ),
    );
  }
}

/// Cinematic transparent-to-navy veil. The sky and monument stay crisp at the
/// top, while the overlay deepens smoothly through mid-navy into a near-opaque,
/// dark-navy base so every foreground element is clearly readable against the
/// photograph — without crushing the upper half of the image.
class _CinematicGradient extends StatelessWidget {
  const _CinematicGradient();

  @override
  Widget build(BuildContext context) {
    return const DecoratedBox(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          stops: [0.0, 0.30, 0.55, 0.78, 1.0],
          colors: [
            Colors.transparent,
            Color(0x29422A1B),
            Color(0x66422A1B),
            Color(0xBF2A1B14),
            Color(0xFF2A1B14),
          ],
        ),
      ),
    );
  }
}
