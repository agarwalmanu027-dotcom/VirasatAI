import 'package:flutter/material.dart';
import '../../app/theme.dart';

/// Shared guide presentation for the Taj, Qutub and catalogue pages.
class GuideSectionCard extends StatelessWidget {
  const GuideSectionCard(
      {super.key, required this.title, required this.content});
  final String title;
  final Widget content;

  @override
  Widget build(BuildContext context) => Container(
        width: double.infinity,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppTheme.surfaceColor,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(title,
              style: const TextStyle(
                  color: AppTheme.accentColor,
                  fontSize: 16,
                  fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          content,
        ]),
      );
}

class GuideFactLine extends StatelessWidget {
  const GuideFactLine({super.key, required this.label, required this.value});
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 8),
        child: LayoutBuilder(
            builder: (context, constraints) => Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(
                      width: constraints.maxWidth < 340
                          ? constraints.maxWidth * .35
                          : 130,
                      child: Text(label,
                          style: const TextStyle(
                              color: AppTheme.secondaryTextColor,
                              fontSize: 13,
                              fontWeight: FontWeight.w600)),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                        child: Text(value,
                            style: const TextStyle(
                                color: AppTheme.primaryTextColor,
                                fontSize: 13,
                                height: 1.4))),
                  ],
                )),
      );
}

class GuideFactsCard extends StatelessWidget {
  const GuideFactsCard({super.key, required this.title, required this.facts});
  final String title;
  final Map<String, String> facts;

  @override
  Widget build(BuildContext context) => GuideSectionCard(
        title: title,
        content:
            Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          for (final fact in facts.entries)
            GuideFactLine(label: fact.key, value: fact.value),
        ]),
      );
}

class GuideDetailCard extends StatelessWidget {
  const GuideDetailCard({super.key, required this.title, required this.body});
  final String title;
  final String body;

  @override
  Widget build(BuildContext context) => ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: ExpansionTile(
          backgroundColor: AppTheme.surfaceColor,
          collapsedBackgroundColor: AppTheme.surfaceColor,
          iconColor: AppTheme.accentColor,
          collapsedIconColor: AppTheme.accentColor,
          title: Text(title,
              style: const TextStyle(
                  color: AppTheme.primaryTextColor,
                  fontSize: 16,
                  fontWeight: FontWeight.w600)),
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
              child: SizedBox(
                  width: double.infinity,
                  child: Text(body,
                      style: const TextStyle(
                          color: AppTheme.primaryTextColor,
                          fontSize: 14,
                          height: 1.5))),
            )
          ],
        ),
      );
}
