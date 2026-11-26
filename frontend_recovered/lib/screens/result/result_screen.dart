import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../app/routes.dart';
import '../../app/theme.dart';
import '../../data/guide_catalog.dart';
import '../../data/guide_hindi.dart';
import '../../models/monument.dart';
import 'taj_story_screen.dart';
import 'reviews_panel.dart';
import 'guide_sections.dart';

/// Simple result screen showing Taj Mahal and nearby places.
class ResultScreen extends StatefulWidget {
  final String monumentId;
  final bool initialHindi;

  const ResultScreen(
      {super.key, required this.monumentId, this.initialHindi = false});

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  late bool _isHindi;
  late final Future<GuideCatalog> _catalogFuture = GuideCatalog.load();

  @override
  void initState() {
    super.initState();
    _isHindi = widget.initialHindi;
  }

  String _t(String english, String hindi) => _isHindi ? hindi : english;

  static const _tajMahal = Monument(
    id: 'taj-mahal',
    name: 'Taj Mahal',
    location: 'Agra, Uttar Pradesh',
    description:
        'Shah Jahan commissioned the Taj Mahal in memory of Mumtaz Mahal. '
        'Construction began in 1632 beside the Yamuna River in Agra. '
        'The white marble mausoleum was completed in 1648; other parts of '
        'the complex followed. Its dome, four minarets, stone inlay and '
        'symmetrical garden are highlights of Mughal architecture.',
    imageUrl: 'assets/images/taj_mahal.jpg',
    healthScore: 0.0,
    era: 'Mughal period',
    architecturalStyle: 'Indo-Islamic / Mughal',
  );

  static const _aboutHindi =
      'शाहजहाँ ने मुमताज़ महल की याद में ताज महल बनवाया। आगरा में यमुना नदी के किनारे इसका निर्माण 1632 में शुरू हुआ। सफेद संगमरमर का मुख्य मकबरा 1648 में पूरा हुआ; परिसर के अन्य हिस्से बाद में बने। इसका गुंबद, चार मीनारें, पत्थर की जड़ाई और सममित बाग मुगल वास्तुकला की विशेषताएँ हैं।';

  static const _historyEnglish =
      'Mumtaz Mahal died in 1631. Shah Jahan then commissioned the Taj Mahal in her memory. Construction began in 1632. The principal mausoleum was completed in 1648, while the mosque, guest house and other parts of the complex were completed later.';
  static const _historyHindi =
      'मुमताज़ महल का निधन 1631 में हुआ। उनकी याद में शाहजहाँ ने ताज महल बनवाने का आदेश दिया। निर्माण 1632 में शुरू हुआ। मुख्य मकबरा 1648 में पूरा हुआ, जबकि मस्जिद, अतिथि भवन और परिसर के अन्य हिस्से बाद में पूरे हुए।';
  static const _architectureEnglish =
      'The white marble mausoleum has a large central dome and four minarets. Floral stone inlay, marble lattice screens and Arabic calligraphy decorate it. A mosque to the west, guest house to the east and formal garden give the complex its balanced layout.';
  static const _architectureHindi =
      'सफेद संगमरमर के मकबरे में एक बड़ा केंद्रीय गुंबद और चार मीनारें हैं। फूलों की पत्थर-जड़ाई, संगमरमर की जालियाँ और अरबी सुलेख इसकी सजावट हैं। पश्चिम में मस्जिद, पूर्व में अतिथि भवन और औपचारिक बाग पूरे परिसर को संतुलित रूप देते हैं।';

  static const _gallery = [
    ('Front view', 'सामने का दृश्य', 'assets/images/taj_gallery/front.jpg'),
    (
      'Yamuna view',
      'यमुना का दृश्य',
      'assets/images/taj_gallery/yamuna_view.jpg'
    ),
    ('Main dome', 'मुख्य गुंबद', 'assets/images/taj_gallery/dome.jpg'),
    ('Garden', 'बाग', 'assets/images/taj_gallery/garden.jpg'),
    ('Minaret', 'मीनार', 'assets/images/taj_gallery/minaret.jpg'),
    ('Calligraphy', 'सुलेख', 'assets/images/taj_gallery/calligraphy.jpg'),
    ('Aerial view', 'हवाई दृश्य', 'assets/images/taj_gallery/aerial.jpg'),
    ('Marble lattice', 'संगमरमर की जाली', 'assets/images/taj_gallery/jali.jpg'),
  ];

  void _goBack(BuildContext context) {
    if (context.canPop()) {
      context.pop();
    } else {
      context.go(AppRoutes.home);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.primaryColor,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.arrow_back, color: Colors.white),
                    onPressed: () => _goBack(context),
                  ),
                  const Spacer(),
                  TextButton(
                    onPressed: () => setState(() => _isHindi = !_isHindi),
                    child: Text(
                      _isHindi ? 'English' : 'हिंदी',
                      style: const TextStyle(color: Colors.white),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child: AspectRatio(
                  aspectRatio: 16 / 9,
                  child: Image.asset(
                    _tajMahal.imageUrl,
                    width: double.infinity,
                    fit: BoxFit.cover,
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Text(
                _t(_tajMahal.name, 'ताज महल'),
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 24,
                  fontWeight: FontWeight.w600,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 4),
              Text(
                _t(_tajMahal.location, 'आगरा, उत्तर प्रदेश'),
                style: const TextStyle(
                  color: Colors.white70,
                  fontSize: 16,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              _buildAboutCard(),
              const SizedBox(height: 16),
              _buildQuickFactsCard(),
              const SizedBox(height: 16),
              _buildDetailCard(
                _t('History', 'इतिहास'),
                _t(_historyEnglish, _historyHindi),
              ),
              const SizedBox(height: 12),
              _buildDetailCard(
                _t('Architecture', 'वास्तुकला'),
                _t(_architectureEnglish, _architectureHindi),
              ),
              const SizedBox(height: 12),
              _buildStoryCard(context),
              const SizedBox(height: 20),
              _buildGallery(context),
              const SizedBox(height: 20),
              Text(
                _t('Places to visit near Taj Mahal',
                    'ताज महल के आसपास घूमने की जगहें'),
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 20,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                _t('Explore more heritage around Agra',
                    'आगरा की और धरोहरें देखें'),
                style: const TextStyle(color: Colors.white70, fontSize: 13),
              ),
              const SizedBox(height: 12),
              FutureBuilder<GuideCatalog>(
                future: _catalogFuture,
                builder: (context, snapshot) {
                  if (!snapshot.hasData) return const SizedBox.shrink();
                  return Column(children: [
                    for (final place in snapshot.data!.nearbyFor('taj_mahal'))
                      Card(
                          child: ListTile(
                        leading: place.photos.isEmpty
                            ? const Icon(Icons.place_outlined)
                            : Image.asset(place.photos.first,
                                width: 54, height: 54, fit: BoxFit.cover),
                        title: Text(
                            _isHindi ? guideNameHindi(place.name) : place.name),
                        trailing: const Icon(Icons.chevron_right),
                        onTap: () => context.push(
                            '/guide/${place.id}${_isHindi ? '?lang=hi' : ''}'),
                      )),
                  ]);
                },
              ),
              const SizedBox(height: 16),
              ReviewsPanel(placeId: 'taj_mahal', hindi: _isHindi),
              const SizedBox(height: 12),
              OutlinedButton.icon(
                onPressed: () => context
                    .push('/report/taj_mahal?lang=${_isHindi ? 'hi' : 'en'}'),
                icon: const Icon(Icons.report_outlined),
                label: Text(_t(
                    'Report an issue at this place', 'इस जगह की समस्या बताएँ')),
                style: OutlinedButton.styleFrom(
                    foregroundColor: Colors.white,
                    side: const BorderSide(color: Colors.white70)),
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAboutCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            _t('About', 'परिचय'),
            style: const TextStyle(
              color: AppTheme.accentColor,
              fontSize: 14,
              fontWeight: FontWeight.bold,
              letterSpacing: 0.5,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            _t(_tajMahal.description, _aboutHindi),
            style: const TextStyle(
              color: AppTheme.primaryTextColor,
              fontSize: 14,
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickFactsCard() {
    final facts = _isHindi
        ? <String, String>{
            'स्थान': 'आगरा, उत्तर प्रदेश',
            'नदी': 'यमुना',
            'बनवाया': 'शाहजहाँ ने',
            'स्मृति में': 'मुमताज़ महल',
            'निर्माण शुरू': '1632',
            'मुख्य मकबरा पूरा': '1648',
            'यूनेस्को सूची': '1983',
          }
        : <String, String>{
            'Location': _tajMahal.location,
            'River': 'Yamuna',
            'Commissioned by': 'Shah Jahan',
            'In memory of': 'Mumtaz Mahal',
            'Construction began': '1632',
            'Mausoleum ready': '1648',
            'UNESCO listed': '1983',
          };

    return GuideFactsCard(
        title: _t('Verified details', 'प्रमाणित तथ्य'), facts: facts);
  }

  Widget _buildDetailCard(String title, String body) =>
      GuideDetailCard(title: title, body: body);

  Widget _buildStoryCard(BuildContext context) {
    return Material(
      color: AppTheme.surfaceColor,
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: () => Navigator.of(context).push(
          MaterialPageRoute<void>(
            builder: (_) => TajStoryScreen(isHindi: _isHindi),
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              const Icon(Icons.menu_book_outlined, color: AppTheme.accentColor),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _t('Taj Mahal story', 'ताज महल की कहानी'),
                      style: const TextStyle(
                        color: AppTheme.primaryTextColor,
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Text(
                      _t('Opens in English', 'हिंदी में खुलेगी'),
                      style: const TextStyle(
                        color: AppTheme.secondaryTextColor,
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right, color: AppTheme.accentColor),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildGallery(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          _t('Taj Mahal gallery', 'ताज महल की तस्वीरें'),
          style: const TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          _t('Tap a photo to see it larger',
              'बड़ा देखने के लिए तस्वीर पर टैप करें'),
          style: const TextStyle(color: Colors.white70, fontSize: 13),
        ),
        const SizedBox(height: 12),
        SizedBox(
          height: 170,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: _gallery.length,
            separatorBuilder: (_, __) => const SizedBox(width: 12),
            itemBuilder: (context, index) {
              final (englishTitle, hindiTitle, path) = _gallery[index];
              final title = _t(englishTitle, hindiTitle);
              return Semantics(
                button: true,
                label: _t('Open $title photo', '$title तस्वीर खोलें'),
                child: InkWell(
                  borderRadius: BorderRadius.circular(16),
                  onTap: () => _showGalleryPhoto(context, title, path),
                  child: SizedBox(
                    width: 190,
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(16),
                      child: Stack(
                        fit: StackFit.expand,
                        children: [
                          Image.asset(path, fit: BoxFit.cover),
                          Align(
                            alignment: Alignment.bottomCenter,
                            child: Container(
                              width: double.infinity,
                              padding: const EdgeInsets.all(10),
                              color: Colors.black54,
                              child: Text(
                                title,
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  void _showGalleryPhoto(BuildContext context, String title, String path) {
    showDialog<void>(
      context: context,
      builder: (dialogContext) => Dialog(
        backgroundColor: AppTheme.surfaceColor,
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 760),
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        title,
                        style: const TextStyle(
                          color: AppTheme.primaryTextColor,
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    IconButton(
                      tooltip: _t('Close photo', 'तस्वीर बंद करें'),
                      onPressed: () => Navigator.of(dialogContext).pop(),
                      icon: const Icon(Icons.close, color: Colors.white),
                    ),
                  ],
                ),
                ConstrainedBox(
                  constraints: BoxConstraints(
                    maxHeight: MediaQuery.sizeOf(dialogContext).height * 0.7,
                  ),
                  child: InteractiveViewer(
                    child: Image.asset(path, fit: BoxFit.contain),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
