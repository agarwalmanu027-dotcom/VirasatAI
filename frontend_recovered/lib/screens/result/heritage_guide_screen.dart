import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';

import '../../app/theme.dart';
import '../../data/guide_catalog.dart';
import '../../data/guide_hindi.dart';
import 'story_reader_screen.dart';
import 'reviews_panel.dart';
import 'guide_sections.dart';

/// A factual guide page for the prepared content library, not a scan result.
class HeritageGuideScreen extends StatefulWidget {
  const HeritageGuideScreen(
      {super.key, required this.placeId, this.initialHindi = false});

  final String placeId;
  final bool initialHindi;

  @override
  State<HeritageGuideScreen> createState() => _HeritageGuideScreenState();
}

class _HeritageGuideScreenState extends State<HeritageGuideScreen> {
  static const _maps = MethodChannel('virasatai/maps');
  late bool _isHindi;

  @override
  void initState() {
    super.initState();
    _isHindi = widget.initialHindi;
  }

  String _t(String en, String hi) => _isHindi ? hi : en;

  Future<void> _openMap(GuideEntry entry) async {
    try {
      await _maps.invokeMethod<void>('open', {
        'query': [entry.name, entry.location]
            .where((value) => value.trim().isNotEmpty)
            .join(', '),
      });
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text(_t('Maps could not be opened on this device.',
              'इस डिवाइस पर मैप नहीं खुल सका।'))));
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        backgroundColor: AppTheme.primaryColor,
        appBar: AppBar(
          backgroundColor: AppTheme.primaryColor,
          foregroundColor: Colors.white,
          title: Text(_t('VirasatAI guide', 'विरासतAI गाइड')),
          leading: IconButton(
            tooltip: 'Back',
            icon: const Icon(Icons.arrow_back),
            onPressed: () =>
                context.canPop() ? context.pop() : context.go('/guides'),
          ),
          actions: [
            TextButton(
              onPressed: () => setState(() => _isHindi = !_isHindi),
              child: Text(_isHindi ? 'English' : 'हिंदी',
                  style: const TextStyle(color: Colors.white)),
            ),
          ],
        ),
        body: FutureBuilder<GuideCatalog>(
          future: GuideCatalog.load(),
          builder: (context, snapshot) {
            if (snapshot.hasError) {
              return const Center(
                  child: Text('Guide could not be opened.',
                      style: TextStyle(color: Colors.white)));
            }
            if (!snapshot.hasData) {
              return const Center(child: CircularProgressIndicator());
            }
            final catalog = snapshot.data!;
            final entry = catalog.byId[widget.placeId];
            if (entry == null) {
              return const Center(
                  child: Text('Place not found.',
                      style: TextStyle(color: Colors.white)));
            }
            return _content(catalog, entry);
          },
        ),
      );

  Widget _content(GuideCatalog catalog, GuideEntry entry) {
    final nearby = entry.isMain ? catalog.nearbyFor(entry.id) : <GuideEntry>[];
    final parent = !entry.isMain ? catalog.byId[entry.groupId] : null;
    final story = _isHindi ? entry.storyHindi : entry.storyEnglish;
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 800),
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _hero(entry),
            const SizedBox(height: 14),
            Text(_isHindi ? guideNameHindi(entry.name) : entry.name,
                textAlign: TextAlign.center,
                style: const TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    fontWeight: FontWeight.bold)),
            if (entry.location.isNotEmpty)
              Text(
                  _isHindi
                      ? guideLocationHindi(entry.location)
                      : entry.location,
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.white70)),
            if (entry.location.isNotEmpty)
              Align(
                alignment: Alignment.center,
                child: TextButton.icon(
                  onPressed: () => _openMap(entry),
                  icon: const Icon(Icons.map_outlined),
                  label: Text(_t('Open in Maps', 'मैप में खोलें')),
                  style: TextButton.styleFrom(foregroundColor: Colors.white),
                ),
              ),
            const SizedBox(height: 14),
            if (parent != null) ...[
              TextButton.icon(
                onPressed: () => context.push(
                    '${guidePathFor(parent.id)}${_isHindi ? '?lang=hi' : ''}'),
                icon: const Icon(Icons.arrow_back),
                label: Text(_t('Part of ${parent.name}',
                    '${guideNameHindi(parent.name)} का हिस्सा')),
                style: TextButton.styleFrom(foregroundColor: Colors.white),
              ),
              const SizedBox(height: 10),
            ],
            if (!entry.ready)
              _section(
                _t('Details pending', 'जानकारी तैयार की जा रही है'),
                Text(_t(
                    entry.pendingReason ?? 'Site identity needs confirmation.',
                    'इस जगह की पहचान की पुष्टि अभी बाकी है।')),
              )
            else ...[
              _section(
                _t('About', 'परिचय'),
                Text(
                  _isHindi && entry.overviewHindi.isNotEmpty
                      ? entry.overviewHindi
                      : entry.overview,
                  style: const TextStyle(fontSize: 15, height: 1.5),
                ),
              ),
              if (entry.facts.isNotEmpty) ...[
                const SizedBox(height: 12),
                _factsCard(entry),
              ],
              const SizedBox(height: 12),
              _detail(
                _t('History', 'इतिहास'),
                _isHindi ? entry.historyHindi : entry.history,
                _t('Further historical details are not available in this guide yet.',
                    'इस गाइड में इतिहास का विस्तृत विवरण अभी उपलब्ध नहीं है।'),
              ),
              const SizedBox(height: 12),
              _detail(
                _t('Architecture', 'वास्तुकला'),
                _isHindi ? entry.architectureHindi : entry.architecture,
                _t('Further architectural details are not available in this guide yet.',
                    'इस गाइड में वास्तुकला का विस्तृत विवरण अभी उपलब्ध नहीं है।'),
              ),
              if (story.isNotEmpty) ...[
                const SizedBox(height: 12),
                _story(entry),
              ],
            ],
            const SizedBox(height: 20),
            if (entry.photos.isNotEmpty) ...[
              Text(_t('Photo gallery', 'तस्वीरें'),
                  style: const TextStyle(
                      color: Colors.white,
                      fontSize: 20,
                      fontWeight: FontWeight.w600)),
              const SizedBox(height: 10),
              SizedBox(
                height: 160,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  itemCount: entry.photos.length,
                  separatorBuilder: (_, __) => const SizedBox(width: 10),
                  itemBuilder: (context, index) => InkWell(
                    onTap: () => _openPhoto(entry, index),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(14),
                      child: Image.asset(entry.photos[index],
                          width: 190, fit: BoxFit.cover),
                    ),
                  ),
                ),
              ),
            ] else if (entry.ready)
              _section(
                _t('Photo gallery', 'तस्वीरें'),
                Text(_t('Reviewed photos are not available for this place yet.',
                    'इस जगह की जाँची हुई तस्वीरें अभी उपलब्ध नहीं हैं।')),
              ),
            if (nearby.isNotEmpty) ...[
              const SizedBox(height: 22),
              Text(
                  _t('Places to visit near ${entry.name}',
                      '${guideNameHindi(entry.name)} के आसपास घूमने की जगहें'),
                  style: const TextStyle(
                      color: Colors.white,
                      fontSize: 20,
                      fontWeight: FontWeight.w600)),
              const SizedBox(height: 4),
              Text(
                _t('These are selected associations, not a distance or travel-time guide.',
                    'ये चुनी हुई संबंधित जगहें हैं; दूरी या यात्रा समय की सूची नहीं।'),
                style: const TextStyle(color: Colors.white70, fontSize: 12),
              ),
              const SizedBox(height: 10),
              for (final place in nearby) ...[
                _nearbyCard(place),
                const SizedBox(height: 8),
              ],
            ],
            const SizedBox(height: 12),
            ReviewsPanel(placeId: entry.id, hindi: _isHindi),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: () => context
                  .push('/report/${entry.id}?lang=${_isHindi ? 'hi' : 'en'}'),
              icon: const Icon(Icons.report_outlined),
              label: Text(_t(
                  'Report an issue at this place', 'इस जगह की समस्या बताएँ')),
              style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.white,
                  side: const BorderSide(color: Colors.white70)),
            ),
            const SizedBox(height: 10),
            TextButton(
              onPressed: () => context.push('/guides'),
              child: Text(_t('Browse all guides', 'सभी गाइड देखें'),
                  style: const TextStyle(color: Colors.white)),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  Widget _hero(GuideEntry entry) => ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: AspectRatio(
          aspectRatio: 16 / 9,
          child: entry.photos.isEmpty
              ? const ColoredBox(
                  color: Color(0xFFE7E8EC),
                  child: Center(
                    child: Icon(Icons.account_balance_outlined,
                        size: 66, color: AppTheme.primaryColor),
                  ),
                )
              : Image.asset(entry.photos.first, fit: BoxFit.cover),
        ),
      );

  Widget _detail(String title, String content, String unavailable) =>
      GuideDetailCard(
        key: ValueKey('${widget.placeId}-$title'),
        title: title,
        body: content.isNotEmpty ? content : unavailable,
      );

  Widget _section(String title, Widget content) =>
      GuideSectionCard(title: title, content: content);

  Widget _factsCard(GuideEntry entry) {
    final values = _isHindi ? entry.factsHindi : entry.facts;
    final labels = _isHindi ? entry.factLabelsHindi : entry.factLabels;
    if (values.isNotEmpty && labels.length == values.length) {
      final locationLabel = _t('Location', 'स्थान');
      return GuideFactsCard(
          title: _t('Verified details', 'प्रमाणित तथ्य'),
          facts: {
            if (entry.location.isNotEmpty && !labels.contains(locationLabel))
              locationLabel: _isHindi
                  ? guideLocationHindi(entry.location)
                  : entry.location,
            for (var i = 0; i < values.length; i++) labels[i]: values[i],
          });
    }
    if (_isHindi) {
      return _section(
          'स्रोत-आधारित हिंदी विवरण',
          Text(
              entry.detailsSummaryHindi.isNotEmpty
                  ? entry.detailsSummaryHindi
                  : 'इस जगह के विस्तृत हिंदी तथ्य अभी उपलब्ध नहीं हैं।',
              style: const TextStyle(fontSize: 14, height: 1.5)));
    }
    return _section(
        'Verified details',
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            for (final fact in values)
              Padding(
                padding: const EdgeInsets.only(bottom: 9),
                child: Text('• $fact',
                    style: const TextStyle(fontSize: 14, height: 1.5)),
              )
          ],
        ));
  }

  Widget _story(GuideEntry entry) => Material(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(16),
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: () => Navigator.of(context).push(MaterialPageRoute<void>(
            builder: (_) => StoryReaderScreen(
              titleEnglish: '${entry.name} story',
              titleHindi: '${guideNameHindi(entry.name)} की कहानी',
              storyEnglish: Future.value(entry.storyEnglish),
              storyHindi: Future.value(entry.storyHindi.isNotEmpty
                  ? entry.storyHindi
                  : entry.storyEnglish),
              initialHindi: _isHindi && entry.storyHindi.isNotEmpty,
            ),
          )),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                const Icon(Icons.menu_book_outlined,
                    color: AppTheme.accentColor),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    _t('${entry.name} story',
                        '${guideNameHindi(entry.name)} की कहानी'),
                    style: const TextStyle(
                      color: AppTheme.primaryTextColor,
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                const Icon(Icons.chevron_right, color: AppTheme.accentColor),
              ],
            ),
          ),
        ),
      );

  Widget _nearbyCard(GuideEntry place) => Material(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(14),
        child: InkWell(
          borderRadius: BorderRadius.circular(14),
          onTap: () => context
              .push('${guidePathFor(place.id)}${_isHindi ? '?lang=hi' : ''}'),
          child: Padding(
            padding: const EdgeInsets.all(8),
            child: Row(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(9),
                  child: SizedBox(
                    width: 62,
                    height: 62,
                    child: place.photos.isEmpty
                        ? const ColoredBox(
                            color: Color(0xFFE7E8EC),
                            child: Icon(Icons.account_balance_outlined),
                          )
                        : Image.asset(place.photos.first, fit: BoxFit.cover),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                    child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(_isHindi ? guideNameHindi(place.name) : place.name,
                        style: const TextStyle(fontWeight: FontWeight.w600)),
                    if (!place.ready)
                      Text(_t('Details pending', 'जानकारी तैयार की जा रही है'),
                          style: const TextStyle(fontSize: 12)),
                  ],
                )),
                const Icon(Icons.chevron_right),
              ],
            ),
          ),
        ),
      );

  void _openPhoto(GuideEntry entry, int index) {
    showDialog<void>(
      context: context,
      builder: (dialogContext) => Dialog(
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(children: [
                Expanded(
                    child: Text(
                        '${_isHindi ? guideNameHindi(entry.name) : entry.name} · ${index + 1}')),
                IconButton(
                  tooltip: _t('Close photo', 'तस्वीर बंद करें'),
                  onPressed: () => Navigator.pop(dialogContext),
                  icon: const Icon(Icons.close),
                ),
              ]),
              ConstrainedBox(
                constraints: BoxConstraints(
                    maxHeight: MediaQuery.sizeOf(dialogContext).height * 0.7),
                child: InteractiveViewer(
                    child:
                        Image.asset(entry.photos[index], fit: BoxFit.contain)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
