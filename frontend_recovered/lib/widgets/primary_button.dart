import 'package:flutter/material.dart';

/// A reusable primary action button following the VirasatAI design system.
///
/// Supports a label, an optional leading icon, and a loading/disabled state.
class PrimaryButton extends StatelessWidget {
  final String label;
  final IconData? icon;
  final VoidCallback? onPressed;

  /// When true, a progress indicator replaces the icon and the button is
  /// disabled (onPressed is ignored).
  final bool loading;

  /// Whether the button should fill available width. Defaults to true.
  final bool expanded;

  const PrimaryButton({
    super.key,
    required this.label,
    this.icon,
    this.onPressed,
    this.loading = false,
    this.expanded = true,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final disabled = loading || onPressed == null;

    Widget content = Row(
      mainAxisSize: expanded ? MainAxisSize.max : MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        if (loading)
          const SizedBox(
            width: 18,
            height: 18,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
            ),
          )
        else if (icon != null)
          Icon(icon, size: 20),
        if ((loading || icon != null)) const SizedBox(width: 8),
        Flexible(
          child: Text(
            label,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: theme.textTheme.labelLarge?.copyWith(
              fontSize: 15,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ],
    );

    final button = FilledButton(
      onPressed: disabled ? null : onPressed,
      style: FilledButton.styleFrom(
        backgroundColor: theme.colorScheme.primary,
        foregroundColor: theme.colorScheme.onPrimary,
        disabledBackgroundColor: theme.colorScheme.primary.withAlpha(0x66),
        disabledForegroundColor: theme.colorScheme.onPrimary.withAlpha(0x99),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
        minimumSize: const Size(0, 48),
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(14)),
        ),
      ),
      child: content,
    );

    if (!expanded) return button;
    return SizedBox(width: double.infinity, child: button);
  }
}
