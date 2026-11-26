import 'package:flutter/material.dart';

/// A reusable, presentation-only overlay shown during AI processing / loading.
///
/// It does NOT perform any real AI work. The caller is responsible for
/// showing/hiding it (e.g. by placing it in a [Stack]) and for driving any
/// progress value via [progress].
class LoadingOverlay extends StatelessWidget {
  /// Optional title, e.g. "Analyzing monument".
  final String? title;

  /// Current processing message shown beneath the indicator.
  final String message;

  /// Optional deterministic progress in the range 0.0 - 1.0.
  /// When null (default) an indeterminate indicator is shown.
  final double? progress;

  const LoadingOverlay({
    super.key,
    this.title,
    required this.message,
    this.progress,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final hasProgress = progress != null;

    return Positioned.fill(
      child: ColoredBox(
        color: Colors.black.withAlpha(0x78),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 320),
            child: Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: theme.colorScheme.surface,
                borderRadius: BorderRadius.circular(20),
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (hasProgress)
                    SizedBox(
                      width: 48,
                      height: 48,
                      child: CircularProgressIndicator(
                        value: progress,
                        strokeWidth: 4,
                        valueColor: AlwaysStoppedAnimation<Color>(
                          theme.colorScheme.primary,
                        ),
                      ),
                    )
                  else
                    const SizedBox(
                      width: 36,
                      height: 36,
                      child: CircularProgressIndicator(strokeWidth: 3),
                    ),
                  if (title != null) ...[
                    const SizedBox(height: 20),
                    Text(
                      title!,
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                  const SizedBox(height: 8),
                  Text(
                    message,
                    style: theme.textTheme.bodySmall,
                    textAlign: TextAlign.center,
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
