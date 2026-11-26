import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../app/routes.dart';
import '../../app/theme.dart';
import '../../widgets/auth_background.dart';

/// Heritage palette tokens scoped to this screen so the shared [AppTheme] (and
/// every other screen) stays untouched by this visual polish pass.
///
/// [_heritageGold] is brighter than [AppTheme.accentColor] so the brand mark,
/// divider and "Log in" link stay crisp against the darkened photograph;
/// [_cream] is a warm off-white for the tagline.
const Color _heritageGold = Color(0xFFF2C879);
const Color _cream = Color(0xFFF6EDDC);

/// Welcome / authentication entry screen for VirasatAI.
///
/// Renders its foreground prompt on top of the shared [AuthBackground] — a
/// full-bleed Taj Mahal photograph with a soft cinematic bottom gradient and a
/// transparent light-icon status bar. All foreground content is laid out with
/// plain Flutter layout widgets (Column / Spacer / SliverFillRemaining) so it
/// scales gracefully on small to large Android screens without fixed screen
/// coordinates.
class AuthWelcomeScreen extends StatefulWidget {
  const AuthWelcomeScreen({super.key});

  @override
  State<AuthWelcomeScreen> createState() => _AuthWelcomeScreenState();
}

class _AuthWelcomeScreenState extends State<AuthWelcomeScreen> {
  @override
  Widget build(BuildContext context) {
    return const AuthBackground(
      child: _WelcomeForeground(),
    );
  }
}

/// Foreground prompt, shielded by [SafeArea] while the photograph below flows
/// edge-to-edge. Flexible spacers nudge the block towards the lower-middle of
/// the screen; when the content is taller than the viewport the spacers
/// collapse and the block scrolls instead of overflowing.
class _WelcomeForeground extends StatelessWidget {
  const _WelcomeForeground();

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: LayoutBuilder(
        builder: (context, constraints) {
          final bool compact =
              constraints.maxWidth < 360 || constraints.maxHeight < 600;
          final double horizontalPadding =
              constraints.maxWidth >= 600 ? 40.0 : 24.0;

          return CustomScrollView(
            slivers: [
              SliverPadding(
                padding: EdgeInsets.symmetric(horizontal: horizontalPadding),
                sliver: SliverFillRemaining(
                  hasScrollBody: false,
                  child: Center(
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 460),
                      child: _WelcomeContent(compact: compact),
                    ),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _WelcomeContent extends StatelessWidget {
  const _WelcomeContent({required this.compact});

  /// Narrow screens get proportionally smaller branding and spacing.
  final bool compact;

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // 6:1 flexible split places the block in the lower-middle without any
        // fixed pixel offsets.
        const Spacer(flex: 6),
        _BrandBlock(compact: compact),
        SizedBox(height: compact ? 18 : 26),
        _AuthActions(compact: compact),
        const Spacer(flex: 1),
      ],
    );
  }
}

class _BrandBlock extends StatelessWidget {
  const _BrandBlock({required this.compact});

  final bool compact;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    final TextStyle brandStyle =
        (textTheme.displaySmall ?? const TextStyle()).copyWith(
      color: _heritageGold,
      fontSize: compact ? 34.0 : 42.0,
      height: 1.1,
      fontWeight: FontWeight.w800,
      letterSpacing: 0.6,
      shadows: const [
        Shadow(color: Colors.black45, blurRadius: 16, offset: Offset(0, 2)),
      ],
    );

    final TextStyle taglineStyle =
        (textTheme.labelLarge ?? const TextStyle()).copyWith(
      color: _cream,
      fontSize: compact ? 11.5 : 13.0,
      fontWeight: FontWeight.w700,
      letterSpacing: 2.0,
      height: 1.7,
      shadows: const [
        Shadow(color: Colors.black45, blurRadius: 8, offset: Offset(0, 1)),
      ],
    );

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          'VirasatAI',
          textAlign: TextAlign.center,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: brandStyle,
        ),
        const SizedBox(height: 12),
        const _HeritageDivider(),
        const SizedBox(height: 16),
        Text(
          'HERITAGE, THOUGHTFULLY\nPRESERVED',
          textAlign: TextAlign.center,
          style: taglineStyle,
        ),
      ],
    );
  }
}

/// Decorative `──── • ────` divider in warm heritage gold.
class _HeritageDivider extends StatelessWidget {
  const _HeritageDivider();

  @override
  Widget build(BuildContext context) {
    const Color gold = _heritageGold;

    return Row(
      mainAxisSize: MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Container(width: 34, height: 1, color: gold.withValues(alpha: 0.7)),
        const SizedBox(width: 10),
        const Text('•', style: TextStyle(color: gold, fontSize: 13, height: 1)),
        const SizedBox(width: 10),
        Container(width: 34, height: 1, color: gold.withValues(alpha: 0.7)),
      ],
    );
  }
}

class _AuthActions extends StatelessWidget {
  const _AuthActions({required this.compact});

  /// Narrow or short viewports shrink button heights and gaps gracefully.
  final bool compact;

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _GuestContinueButton(compact: compact),
        SizedBox(height: compact ? 14 : 18),
        const _LoginPrompt(),
      ],
    );
  }
}

class _GuestContinueButton extends StatelessWidget {
  const _GuestContinueButton({required this.compact});

  /// Narrow or short viewports shrink the button height.
  final bool compact;

  @override
  Widget build(BuildContext context) {
    return _AuthOptionButton(
      label: 'Explore as guest',
      backgroundColor: AppTheme.primaryColor,
      foregroundColor: Colors.white,
      borderSide: BorderSide(
        color: _heritageGold.withValues(alpha: 0.6),
        width: 1,
      ),
      height: compact ? 48 : 52,
      leading: const Icon(Icons.explore_outlined, color: Colors.white),
      onPressed: () => context.go(AppRoutes.home),
    );
  }
}

/// Shared full-width action button: wide comfortable surface, rounded corners,
/// an optional leading icon and an optional warm-gold hairline border. Height
/// shrinks on very narrow viewports; the label is ellipsis-truncated so it can
/// never overflow on the smallest phones.
class _AuthOptionButton extends StatelessWidget {
  const _AuthOptionButton({
    required this.label,
    required this.backgroundColor,
    required this.foregroundColor,
    required this.onPressed,
    this.leading,
    this.borderSide,
    this.height = 52,
  });

  final String label;
  final Color backgroundColor;
  final Color foregroundColor;
  final VoidCallback onPressed;
  final Widget? leading;

  /// Optional subtle border for emphasised variants (Google primary).
  final BorderSide? borderSide;

  /// Comfortable button height; callers pass a smaller value on compact screens.
  final double height;

  static const double _cornerRadius = 16;

  @override
  Widget build(BuildContext context) {
    final TextStyle labelStyle =
        (Theme.of(context).textTheme.labelLarge ?? const TextStyle()).copyWith(
      color: foregroundColor,
      fontSize: 15,
      fontWeight: FontWeight.w700,
      letterSpacing: 0.2,
    );

    return Material(
      color: backgroundColor,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(_cornerRadius),
        side: borderSide ?? BorderSide.none,
      ),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onPressed,
        child: Container(
          width: double.infinity,
          height: height,
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              if (leading != null) ...[
                leading!,
                const SizedBox(width: 10),
              ],
              Flexible(
                child: Text(
                  label,
                  textAlign: TextAlign.center,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: labelStyle,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _LoginPrompt extends StatelessWidget {
  const _LoginPrompt();

  @override
  Widget build(BuildContext context) {
    final TextStyle? bodyStyle = Theme.of(context).textTheme.bodyMedium;

    final TextStyle regularStyle = (bodyStyle ?? const TextStyle()).copyWith(
      color: Colors.white,
      fontSize: 14,
      height: 1.35,
      shadows: const [
        Shadow(color: Colors.black45, blurRadius: 6, offset: Offset(0, 1)),
      ],
    );
    final TextStyle linkStyle = regularStyle.copyWith(
      color: _heritageGold,
      fontWeight: FontWeight.w800,
    );

    return Wrap(
      alignment: WrapAlignment.center,
      crossAxisAlignment: WrapCrossAlignment.center,
      children: [
        Text('Want to preview a profile? ', style: regularStyle),
        TextButton(
          onPressed: () => context.go(AppRoutes.login),
          style: TextButton.styleFrom(
            foregroundColor: _heritageGold,
            minimumSize: const Size(0, 40),
            padding: const EdgeInsets.symmetric(horizontal: 6),
            tapTargetSize: MaterialTapTargetSize.padded,
          ),
          child: Text('Demo sign in', style: linkStyle),
        ),
      ],
    );
  }
}
