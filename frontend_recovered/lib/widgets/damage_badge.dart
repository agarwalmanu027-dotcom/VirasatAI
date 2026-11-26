import 'package:flutter/material.dart';

/// Damage categories recognized by VirasatAI, used by [DamageBadge].
///
/// The widget accepts this type instead of being tied to one specific issue,
/// so any supported damage type can be rendered as a reusable badge.
enum DamageType {
  cracks,
  surfaceStaining,
  vegetation,
  graffiti,
  spalling;

  /// Human-readable label matching the mock data strings.
  String get label {
    switch (this) {
      case DamageType.cracks:
        return 'Cracks';
      case DamageType.surfaceStaining:
        return 'Surface staining';
      case DamageType.vegetation:
        return 'Vegetation';
      case DamageType.graffiti:
        return 'Graffiti';
      case DamageType.spalling:
        return 'Spalling';
    }
  }

  /// Representative Material icon for the damage category.
  IconData get icon {
    switch (this) {
      case DamageType.cracks:
        return Icons.show_chart;
      case DamageType.surfaceStaining:
        return Icons.water_drop_outlined;
      case DamageType.vegetation:
        return Icons.grass_outlined;
      case DamageType.graffiti:
        return Icons.brush_outlined;
      case DamageType.spalling:
        return Icons.broken_image_outlined;
    }
  }

  /// Resolves a damage type from its human-readable [label]
  /// (as stored in mock data such as `MockData.damageTypes`).
  static DamageType fromString(String label) {
    switch (label.toLowerCase()) {
      case 'cracks':
        return DamageType.cracks;
      case 'surface staining':
        return DamageType.surfaceStaining;
      case 'vegetation':
        return DamageType.vegetation;
      case 'graffiti':
        return DamageType.graffiti;
      case 'spalling':
        return DamageType.spalling;
      default:
        return DamageType.cracks;
    }
  }
}

/// A reusable chip/badge representing a single detected damage type.
class DamageBadge extends StatelessWidget {
  final DamageType type;

  const DamageBadge({super.key, required this.type});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    // VirasatAI warning color — used for detected damage (cline.md).
    const color = Color(0xFFC05621);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withAlpha(0x1F),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withAlpha(0x59)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(type.icon, size: 14, color: color),
          const SizedBox(width: 6),
          Text(
            type.label,
            style: theme.textTheme.labelSmall?.copyWith(
              color: color,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}
