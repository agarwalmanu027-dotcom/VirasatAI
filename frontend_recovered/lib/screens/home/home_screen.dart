import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_session.dart';
import '../../app/routes.dart';
import '../../app/theme.dart';
import '../../data/guide_catalog.dart';
import '../../widgets/bottom_nav_bar.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) => Scaffold(
        body: SafeArea(
          child: FutureBuilder<GuideCatalog>(
            future: GuideCatalog.load(),
            builder: (context, snapshot) {
              if (snapshot.hasError) {
                return const Center(
                    child: Text('Heritage guides could not be loaded.'));
              }
              if (!snapshot.hasData) {
                return const Center(child: CircularProgressIndicator());
              }
              final groups = snapshot.data!.mainGroups;
              return Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 900),
                  child: ListView(
                    padding: const EdgeInsets.fromLTRB(20, 20, 20, 32),
                    children: [
                      const Row(children: [
                        Icon(Icons.account_balance_outlined,
                            color: AppTheme.accentColor, size: 20),
                        SizedBox(width: 7),
                        Expanded(
                          child: Text('VIRASATAI  •  INDIAN HERITAGE',
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: TextStyle(
                                  color: AppTheme.accentColor,
                                  fontSize: 11,
                                  fontWeight: FontWeight.bold,
                                  letterSpacing: 1)),
                        ),
                      ]),
                      const SizedBox(height: 14),
                      AnimatedBuilder(
                        animation: AppSession.instance,
                        builder: (context, _) => Row(
                          children: [
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                      'Namaste, ${AppSession.instance.displayName}',
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                      style: const TextStyle(
                                          fontSize: 26,
                                          fontWeight: FontWeight.bold)),
                                  const Text('Where will you explore today?',
                                      style: TextStyle(
                                          color: AppTheme.secondaryTextColor)),
                                ],
                              ),
                            ),
                            IconButton.filledTonal(
                              tooltip: 'Profile',
                              onPressed: () => context.push(AppRoutes.profile),
                              icon: const Icon(Icons.person_outline),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 22),
                      InkWell(
                        onTap: () => context.push(AppRoutes.guideLibrary),
                        borderRadius: BorderRadius.circular(16),
                        child: const IgnorePointer(
                          child: TextField(
                            decoration: InputDecoration(
                              hintText: 'Search monuments and places',
                              prefixIcon: Icon(Icons.search),
                              filled: true,
                              border: OutlineInputBorder(
                                  borderSide: BorderSide.none),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 24),
                      _FeaturedGuide(entry: groups.first),
                      const SizedBox(height: 26),
                      Row(
                        children: [
                          const Expanded(
                            child: Text('Explore heritage',
                                style: TextStyle(
                                    fontSize: 21, fontWeight: FontWeight.bold)),
                          ),
                          TextButton(
                            onPressed: () =>
                                context.push(AppRoutes.guideLibrary),
                            child: const Text('See all'),
                          ),
                        ],
                      ),
                      const Text(
                          'Stories, photos and facts from selected Indian sites',
                          style: TextStyle(color: AppTheme.secondaryTextColor)),
                      const SizedBox(height: 12),
                      for (final entry in groups.skip(1).take(5))
                        Card(
                          margin: const EdgeInsets.only(bottom: 10),
                          clipBehavior: Clip.antiAlias,
                          child: ListTile(
                            contentPadding: const EdgeInsets.all(10),
                            leading: ClipRRect(
                              borderRadius: BorderRadius.circular(10),
                              child: SizedBox(
                                width: 58,
                                height: 58,
                                child: entry.photos.isEmpty
                                    ? const ColoredBox(
                                        color: Color(0xFFE9E5DB),
                                        child: Icon(
                                            Icons.account_balance_outlined),
                                      )
                                    : Image.asset(entry.photos.first,
                                        fit: BoxFit.cover),
                              ),
                            ),
                            title: Text(entry.name,
                                maxLines: 1, overflow: TextOverflow.ellipsis),
                            subtitle: Text(entry.location,
                                maxLines: 1, overflow: TextOverflow.ellipsis),
                            trailing: const Icon(Icons.chevron_right),
                            onTap: () => context.push(guidePathFor(entry.id)),
                          ),
                        ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
        bottomNavigationBar: BottomNavBar(
          currentIndex: 0,
          onTap: (index) {
            if (index == 1) context.push(AppRoutes.explore);
            if (index == 2) context.push(AppRoutes.profile);
            if (index == 3) context.push(AppRoutes.scan);
          },
        ),
      );
}

class _FeaturedGuide extends StatelessWidget {
  const _FeaturedGuide({required this.entry});
  final GuideEntry entry;

  @override
  Widget build(BuildContext context) => Container(
        height: 290,
        clipBehavior: Clip.antiAlias,
        decoration: BoxDecoration(
          color: AppTheme.primaryColor,
          borderRadius: BorderRadius.circular(22),
        ),
        child: Stack(
          fit: StackFit.expand,
          children: [
            if (entry.photos.isNotEmpty)
              Image.asset(entry.photos.first, fit: BoxFit.cover),
            const DecoratedBox(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [Colors.transparent, Color(0xE62A1B14)],
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  const Text('START YOUR JOURNEY',
                      style: TextStyle(
                          color: Color(0xFFF2C879),
                          fontWeight: FontWeight.bold,
                          letterSpacing: 1.2)),
                  const SizedBox(height: 5),
                  Text(entry.name,
                      style: const TextStyle(
                          color: Colors.white,
                          fontSize: 30,
                          fontWeight: FontWeight.bold)),
                  Text(entry.location,
                      style: const TextStyle(color: Colors.white70)),
                  const SizedBox(height: 16),
                  FilledButton.icon(
                    onPressed: () => context.push(guidePathFor(entry.id)),
                    icon: const Icon(Icons.auto_stories_outlined),
                    label: const Text('Open guide'),
                    style: FilledButton.styleFrom(
                        backgroundColor: Colors.white,
                        foregroundColor: AppTheme.primaryColor),
                  ),
                ],
              ),
            ),
          ],
        ),
      );
}
