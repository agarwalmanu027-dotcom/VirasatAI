import 'package:flutter/material.dart';

/// Health condition tiers for a monument, derived from its numeric health score.
///
/// Color mapping follows the VirasatAI health colors defined in `cline.md`:
/// - Good     -> Success  #2F855A  (80-100)
/// - Fair     -> Warning  #C05621  (60-79)
/// - Poor     -> Danger   #B91C1C  (40-59)
/// - Critical -> deep danger #7F1D1D (< 40)
class HealthCondition {
  final String label;
  final Color color;

  const HealthCondition._(this.label, this.color);

  static const good = HealthCondition._('Good', Color(0xFF2F855A));
  static const fair = HealthCondition._('Fair', Color(0xFFC05621));
  static const poor = HealthCondition._('Poor', Color(0xFFB91C1C));
  static const critical = HealthCondition._('Critical', Color(0xFF7F1D1D));

  /// Returns the condition tier for the given [score] (expected 0-100).
  static HealthCondition fromScore(double score) {
    if (score >= 80) return good;
    if (score >= 60) return fair;
    if (score >= 40) return poor;
    return critical;
  }
}

/// A reusable circular health score indicator.
///
/// Displays the numeric score and an appropriate condition label, colored
/// according to the VirasatAI health color system. Does not assume any
/// specific monument's score.
class HealthScoreIndicator extends StatelessWidget {
  final double score;

  /// Radius of the circular indicator.
  final double radius;

  /// Thickness of the progress ring.
  final double strokeWidth;

  /// Whether to show the condition label below the score.
  final bool showLabel;

  const HealthScoreIndicator({
    super.key,
    required this.score,
    this.radius = 28,
    this.strokeWidth = 5,
    this.showLabel = true,
  });

  @override
  Widget build(BuildContext context) {
    final condition = HealthCondition.fromScore(score);
    final clamped = score.clamp(0.0, 100.0).toDouble();
    final theme = Theme.of(context);
    final isWhole = clamped == clamped.truncateToDouble();

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          width: radius * 2,
          height: radius * 2,
          child: Stack(
            alignment: Alignment.center,
            children: [
              CircularProgressIndicator(
                value: clamped / 100,
                strokeWidth: strokeWidth,
                backgroundColor: condition.color.withAlpha(0x1F),
                valueColor: AlwaysStoppedAnimation<Color>(condition.color),
              ),
              Text(
                isWhole
                    ? clamped.toStringAsFixed(0)
                    : clamped.toStringAsFixed(1),
                style: theme.textTheme.labelLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: condition.color,
                  fontSize: radius * 0.5,
                  height: 1,
                ),
              ),
            ],
          ),
        ),
        if (showLabel) ...[
          const SizedBox(height: 4),
          Text(
            condition.label,
            style: theme.textTheme.labelSmall?.copyWith(
              color: condition.color,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ],
    );
  }
}
