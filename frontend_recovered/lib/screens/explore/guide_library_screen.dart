import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../app/theme.dart';
import '../../app/routes.dart';
import '../../data/guide_catalog.dart';

/// Searchable display-content library; browsing does not claim AI detection.
class GuideLibraryScreen extends StatefulWidget {
  const GuideLibraryScreen({super.key});

  @override
  State<GuideLibraryScreen> createState() => _GuideLibraryScreenState();
}

class _GuideLibraryScreenState extends State<GuideLibraryScreen> {
  String _query = '';

  @override
  Widget build(BuildContext context) => PopScope(
        canPop: context.canPop(),
        onPopInvokedWithResult: (didPop, _) {
          if (!didPop) context.go(AppRoutes.home);
        },
        child: Scaffold(
          backgroundColor: AppTheme.primaryColor,
          appBar: AppBar(
            backgroundColor: AppTheme.primaryColor,
            foregroundColor: Colors.white,
            title: const Text('Explore heritage'),
            leading: IconButton(
              tooltip: 'Back',
              icon: const Icon(Icons.arrow_back),
              onPressed: () =>
                  context.canPop() ? context.pop() : context.go(AppRoutes.home),
            ),
          ),
          body: FutureBuilder<GuideCatalog>(
            future: GuideCatalog.load(),
            builder: (context, snapshot) {
              if (snapshot.hasError) {
                return const Center(
                  child: Text('The guide library could not be opened.',
                      style: TextStyle(color: Colors.white)),
                );
              }
              if (!snapshot.hasData) {
                return const Center(child: CircularProgressIndicator());
              }
              final catalog = snapshot.data!;
              final normalized = _query.trim().toLowerCase();
              final visible = normalized.isEmpty
                  ? catalog.mainGroups
                  : catalog.entries
                      .where((entry) =>
                          entry.name.toLowerCase().contains(normalized) ||
                          (entry.isMain &&
                              entry.location
                                  .toLowerCase()
                                  .contains(normalized)))
                      .toList();
              return Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 820),
                  child: ListView(
                    padding: const EdgeInsets.all(16),
                    children: [
                      const Text('Heritage guides',
                          style: TextStyle(
                              color: Colors.white,
                              fontSize: 26,
                              fontWeight: FontWeight.bold)),
                      const SizedBox(height: 4),
                      Text(
                        '${catalog.mainGroups.length} monument groups · ${catalog.entries.length - catalog.mainGroups.length} associated places',
                        style: const TextStyle(color: Colors.white70),
                      ),
                      const SizedBox(height: 14),
                      TextField(
                        onChanged: (value) => setState(() => _query = value),
                        decoration: InputDecoration(
                          hintText: 'Search monuments or places',
                          prefixIcon: const Icon(Icons.search),
                          filled: true,
                          fillColor: Colors.white,
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(14),
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      if (visible.isEmpty)
                        const Padding(
                          padding: EdgeInsets.all(20),
                          child: Text('No matching place found.',
                              style: TextStyle(color: Colors.white)),
                        ),
                      for (final entry in visible) ...[
                        _guideCard(entry, catalog),
                        const SizedBox(height: 10),
                      ],
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      );

  Widget _guideCard(GuideEntry entry, GuideCatalog catalog) {
    final group = catalog.byId[entry.groupId];
    return Material(
      color: AppTheme.surfaceColor,
      borderRadius: BorderRadius.circular(14),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: () => context.push(guidePathFor(entry.id)),
        child: Padding(
          padding: const EdgeInsets.all(10),
          child: Row(
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: SizedBox(
                  width: 76,
                  height: 76,
                  child: entry.photos.isEmpty
                      ? const ColoredBox(
                          color: Color(0xFFE7E8EC),
                          child: Icon(Icons.account_balance_outlined,
                              color: AppTheme.primaryColor),
                        )
                      : Image.asset(entry.photos.first, fit: BoxFit.cover),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(entry.name,
                        style: const TextStyle(
                            fontSize: 16, fontWeight: FontWeight.w600)),
                    const SizedBox(height: 4),
                    Text(
                      entry.isMain
                          ? (entry.location.isNotEmpty
                              ? entry.location
                              : 'Monument group')
                          : 'Part of ${group?.name ?? 'heritage collection'}',
                      style: const TextStyle(
                          color: AppTheme.secondaryTextColor, fontSize: 12),
                    ),
                    if (!entry.ready)
                      const Text('Identity needs confirmation',
                          style: TextStyle(
                              color: AppTheme.accentColor, fontSize: 12)),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right),
            ],
          ),
        ),
      ),
    );
  }
}
