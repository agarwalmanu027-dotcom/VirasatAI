import 'package:flutter/material.dart';
import '../models/monument.dart';
import 'health_score_indicator.dart';

/// A compact, reusable card representing a single [Monument].
///
/// Designed to work in both lists and grids. Shows the monument image,
/// name, location and current health score with clear visual hierarchy.
class MonumentCard extends StatelessWidget {
  final Monument monument;
  final VoidCallback? onTap;

  const MonumentCard({super.key, required this.monument, this.onTap});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Material(
      color: theme.colorScheme.surface,
      borderRadius: BorderRadius.circular(20),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: LayoutBuilder(
          builder: (context, constraints) {
            final boundedHeight = constraints.maxHeight.isFinite;
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // When the card height is bounded (e.g. Home's fixed-height
                // horizontal list) the image flexes to consume the space left
                // after the content, so the card never overflows. In unbounded
                // contexts (Explore's grid, Home's featured card) the image
                // keeps its natural 16:10 ratio and the card sizes to it.
                if (boundedHeight)
                  Flexible(
                    child: SizedBox.expand(child: _buildImage(theme)),
                  )
                else
                  AspectRatio(
                    aspectRatio: 16 / 10,
                    child: _buildImage(theme),
                  ),
                _buildContent(theme),
              ],
            );
          },
        ),
      ),
    );
  }

  Widget _buildImage(ThemeData theme) {
    return Image.network(
      monument.imageUrl,
      fit: BoxFit.cover,
      loadingBuilder: (context, child, progress) {
        if (progress == null) return child;
        return Container(
          color: theme.colorScheme.surface,
          alignment: Alignment.center,
          child: const SizedBox(
            width: 24,
            height: 24,
            child: CircularProgressIndicator(strokeWidth: 2),
          ),
        );
      },
      errorBuilder: (context, error, stack) => Container(
        color: theme.colorScheme.surface,
        alignment: Alignment.center,
        child: Icon(
          Icons.image_outlined,
          size: 36,
          color: theme.colorScheme.onSurface.withAlpha(0x4D),
        ),
      ),
    );
  }

  Widget _buildContent(ThemeData theme) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 14),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  monument.name,
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    Icon(
                      Icons.location_on_outlined,
                      size: 14,
                      color: theme.colorScheme.onSurface.withAlpha(0x99),
                    ),
                    const SizedBox(width: 4),
                    Expanded(
                      child: Text(
                        monument.location,
                        style: theme.textTheme.bodySmall,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(width: 12),
          HealthScoreIndicator(
            score: monument.healthScore,
            radius: 24,
          ),
        ],
      ),
    );
  }
}
