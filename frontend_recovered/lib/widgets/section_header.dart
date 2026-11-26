import 'package:flutter/material.dart';

/// A reusable section header with a title, optional subtitle and an
/// optional trailing action (text + callback).
class SectionHeader extends StatelessWidget {
  final String title;
  final String? subtitle;
  final String? actionText;
  final VoidCallback? onAction;

  const SectionHeader({
    super.key,
    required this.title,
    this.subtitle,
    this.actionText,
    this.onAction,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final hasAction = actionText != null && actionText!.isNotEmpty;

    return Row(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                title,
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              if (subtitle != null && subtitle!.isNotEmpty) ...[
                const SizedBox(height: 4),
                Text(
                  subtitle!,
                  style: theme.textTheme.bodySmall,
                ),
              ],
            ],
          ),
        ),
        if (hasAction)
          TextButton(
            onPressed: onAction,
            child: Text(
              actionText!,
              style: theme.textTheme.labelMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
      ],
    );
  }
}
