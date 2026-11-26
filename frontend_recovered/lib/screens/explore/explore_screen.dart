import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../app/routes.dart';
import '../../app/theme.dart';
import '../../data/mock_data.dart';
import '../../models/monument.dart';
import '../../widgets/bottom_nav_bar.dart';
import '../../widgets/monument_card.dart';
import '../../widgets/section_header.dart';

/// VirasatAI Explore screen (Phase 4B).
///
/// A heritage-discovery hub that feels distinct from Home: search,
/// category chips, hidden gems and the full monument catalogue.
///
/// Search and category filtering are deliberately UI-only in this phase.
class ExploreScreen extends StatefulWidget {
  const ExploreScreen({super.key});

  @override
  State<ExploreScreen> createState() => _ExploreScreenState();
}

class _ExploreScreenState extends State<ExploreScreen> {
  // Bottom navigation destinations in display order. Explore is active.
  static const _navRoutes = <String>[
    AppRoutes.home,
    AppRoutes.explore,
    AppRoutes.scan,
    AppRoutes.profile,
  ];

  // Discovery categories. Filtering is not implemented yet, so the chips
  // only track a visual selection.
  static const _categories = <String>[
    'All',
    'Forts',
    'Tombs',
    'Temples',
    'Other',
  ];

  String _selectedCategory = 'All';

  @override
  Widget build(BuildContext context) {
    final monuments = MockData.monuments;

    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildHeader(context),
              const SizedBox(height: 20),
              _buildSearch(context),
              const SizedBox(height: 20),
              _buildCategories(context),
              const SizedBox(height: 24),
              _buildHiddenGems(context, monuments),
              const SizedBox(height: 32),
              _buildAllMonuments(context, monuments),
            ],
          ),
        ),
      ),
      bottomNavigationBar: BottomNavBar(
        currentIndex: 1,
        onTap: _handleNavigation,
      ),
    );
  }

  /// Routes via the bottom navigation bar. Scan is a full-screen capture
  /// flow, so it is pushed to keep a previous screen on the stack (the system
  /// Back button then returns there instead of exiting the app). The other
  /// destinations replace the current location, which is standard bottom-nav
  /// behaviour.
  void _handleNavigation(int index) {
    final route = _navRoutes[index];
    if (route == AppRoutes.scan) {
      context.push(route);
    } else {
      context.go(route);
    }
  }

  // ---------------------------------------------------------------------------
  // Header
  // ---------------------------------------------------------------------------
  Widget _buildHeader(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Explore Heritage',
          style: theme.textTheme.headlineSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 6),
        Text(
          "Discover India's stories",
          style: theme.textTheme.bodyMedium?.copyWith(
            color: AppTheme.secondaryTextColor,
          ),
        ),
      ],
    );
  }

  // ---------------------------------------------------------------------------
  // Search (UI only)
  // ---------------------------------------------------------------------------
  Widget _buildSearch(BuildContext context) {
    final theme = Theme.of(context);
    return TextField(
      readOnly: true, // Search is UI-only in this phase.
      decoration: InputDecoration(
        hintText: 'Search monuments',
        hintStyle: theme.textTheme.bodyMedium?.copyWith(
          color: AppTheme.secondaryTextColor,
        ),
        prefixIcon: const Icon(Icons.search_rounded, size: 22),
        filled: true,
        fillColor: theme.colorScheme.surface,
        contentPadding: const EdgeInsets.symmetric(vertical: 14),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide.none,
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(
            color: AppTheme.primaryColor.withAlpha(0x4D),
            width: 1.5,
          ),
        ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // Categories (visual selection only)
  // ---------------------------------------------------------------------------
  Widget _buildCategories(BuildContext context) {
    return SizedBox(
      height: 44,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: _categories.length,
        separatorBuilder: (context, index) => const SizedBox(width: 8),
        itemBuilder: (context, index) {
          final category = _categories[index];
          return _CategoryChip(
            label: category,
            selected: category == _selectedCategory,
            onTap: () => setState(() => _selectedCategory = category),
          );
        },
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // Hidden Gems
  // ---------------------------------------------------------------------------
  Widget _buildHiddenGems(BuildContext context, List<Monument> monuments) {
    final gem = _hiddenGem(monuments);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SectionHeader(
          title: 'Hidden Gems',
          subtitle: 'Uncover lesser-known heritage wonders',
        ),
        const SizedBox(height: 16),
        MonumentCard(
          monument: gem,
          onTap: () => context.go('/monument/${gem.id}'),
        ),
      ],
    );
  }

  /// Picks a single "hidden gem" from the mock catalogue: the most
  /// preserved site. Keeps the screen data-driven rather than hardcoded.
  Monument _hiddenGem(List<Monument> monuments) {
    return monuments.reduce(
      (current, next) =>
          next.healthScore > current.healthScore ? next : current,
    );
  }

  // ---------------------------------------------------------------------------
  // All Monuments
  // ---------------------------------------------------------------------------
  Widget _buildAllMonuments(BuildContext context, List<Monument> monuments) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SectionHeader(
          title: 'All Monuments',
          subtitle: 'Explore the full collection',
        ),
        const SizedBox(height: 16),
        // Clean two-column grid. Cards auto-size their height from the
        // available width, mirroring the Home screen's unbounded-height list.
        for (int i = 0; i < monuments.length; i += 2) ...[
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(child: _monumentCard(monuments[i])),
              const SizedBox(width: 12),
              Expanded(
                child: i + 1 < monuments.length
                    ? _monumentCard(monuments[i + 1])
                    : const SizedBox.shrink(),
              ),
            ],
          ),
          if (i + 2 < monuments.length) const SizedBox(height: 12),
        ],
      ],
    );
  }

  Widget _monumentCard(Monument monument) {
    return MonumentCard(
      monument: monument,
      onTap: () => context.go('/monument/${monument.id}'),
    );
  }
}

/// A screen-local category chip with a distinct selected state.
class _CategoryChip extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback onTap;

  const _CategoryChip({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final foregroundColor =
        selected ? Colors.white : AppTheme.secondaryTextColor;

    return Material(
      color: selected ? AppTheme.primaryColor : AppTheme.surfaceColor,
      borderRadius: BorderRadius.circular(14),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Container(
          alignment: Alignment.center,
          padding: const EdgeInsets.symmetric(horizontal: 16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(14),
            border: selected
                ? null
                : Border.all(color: theme.colorScheme.primary.withAlpha(0x1F)),
          ),
          child: Text(
            label,
            style: theme.textTheme.labelLarge?.copyWith(
              fontSize: 15,
              fontWeight: FontWeight.w600,
              color: foregroundColor,
            ),
          ),
        ),
      ),
    );
  }
}