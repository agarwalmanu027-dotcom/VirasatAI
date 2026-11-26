import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';

import '../../app/theme.dart';
import '../../data/guide_catalog.dart';
import '../../data/guide_hindi.dart';
import 'story_reader_screen.dart';
import 'reviews_panel.dart';
import 'guide_sections.dart';

/// Prepared display guide. This route is reached by browsing, not by AI scan.
class QutubMinarGuideScreen extends StatefulWidget {
  const QutubMinarGuideScreen({super.key, this.initialHindi = false});

  final bool initialHindi;

  @override
  State<QutubMinarGuideScreen> createState() => _QutubMinarGuideScreenState();
}

class _QutubMinarGuideScreenState extends State<QutubMinarGuideScreen> {
  late bool _isHindi;
  late final Future<GuideCatalog> _catalog;

  @override
  void initState() {
    super.initState();
    _isHindi = widget.initialHindi;
    _catalog = GuideCatalog.load();
  }

  String _t(String en, String hi) => _isHindi ? hi : en;

  static const _photos = <(String, String, String)>[
    (
      'Tower view',
      'मीनार का दृश्य',
      'assets/images/qutub_gallery/overview.jpg'
    ),
    (
      'Another angle',
      'दूसरा दृश्य',
      'assets/images/qutub_gallery/different_view.jpg'
    ),
    (
      'Stone details',
      'पत्थर की बारीकियाँ',
      'assets/images/qutub_gallery/detail.jpg'
    ),
    ('Complex', 'परिसर', 'assets/images/qutub_gallery/complex.jpg'),
    (
      'Historic view',
      'ऐतिहासिक दृश्य',
      'assets/images/guide_library/qutub_minar_05.jpg'
    ),
    (
      'Carved facade',
      'नक्काशीदार भाग',
      'assets/images/guide_library/qutub_minar_06.jpg'
    ),
    (
      'Complex detail',
      'परिसर का विवरण',
      'assets/images/guide_library/qutub_minar_07.jpg'
    ),
    (
      'Different perspective',
      'अलग दृष्टिकोण',
      'assets/images/guide_library/qutub_minar_08.jpg'
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.primaryColor,
      appBar: AppBar(
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
        title: Text(_t('Qutub Minar guide', 'क़ुतुब मीनार गाइड')),
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
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 800),
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: AspectRatio(
                    aspectRatio: 16 / 9,
                    child: Image.asset(_photos.first.$3, fit: BoxFit.cover),
                  ),
                ),
                const SizedBox(height: 14),
                Text(
                  _t('Qutub Minar', 'क़ुतुब मीनार'),
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                      color: Colors.white,
                      fontSize: 25,
                      fontWeight: FontWeight.bold),
                ),
                Text(
                  _t('Mehrauli, Delhi', 'महरौली, दिल्ली'),
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.white70, fontSize: 16),
                ),
                const SizedBox(height: 18),
                _card(
                  _t('About', 'परिचय'),
                  Text(
                    _t(
                      'Qutub Minar is the landmark tower of a larger historic complex in Mehrauli. The complex preserves buildings from different periods of Delhi history.',
                      'क़ुतुब मीनार महरौली के एक बड़े ऐतिहासिक परिसर की प्रसिद्ध मीनार है। इस परिसर में दिल्ली के इतिहास के अलग-अलग समय की इमारतें हैं।',
                    ),
                    style: const TextStyle(fontSize: 15, height: 1.5),
                  ),
                ),
                const SizedBox(height: 12),
                _card(
                  _t('Verified details', 'प्रमाणित तथ्य'),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _fact(_t('Location', 'स्थान'),
                          _t('Mehrauli, Delhi', 'महरौली, दिल्ली')),
                      _fact(_t('Height', 'ऊँचाई'),
                          _t('About 72.5 metres', 'लगभग 72.5 मीटर')),
                      _fact(
                          _t('Construction', 'निर्माण'),
                          _t('Began under Qutb-ud-din Aibak; continued under later rulers including Iltutmish',
                              'क़ुतुबुद्दीन ऐबक के समय शुरू हुआ; इल्तुतमिश सहित बाद के शासकों ने आगे बढ़ाया')),
                      _fact(_t('UNESCO listing', 'यूनेस्को सूची'), '1993'),
                      _fact(
                        _t('Complex includes', 'परिसर में शामिल'),
                        _t(
                          'Quwwat-ul-Islam Mosque, Iltutmish\'s Tomb, Alai Darwaza, the Iron Pillar and the unfinished Alai Minar',
                          'कुव्वत-उल-इस्लाम मस्जिद, इल्तुतमिश का मकबरा, अलाई दरवाज़ा, लौह स्तंभ और अधूरी अलाई मीनार',
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 12),
                _detail(
                  _t('History', 'इतिहास'),
                  _t(
                    'Construction of the minaret began under Qutb-ud-din Aibak and continued under later rulers, including Iltutmish. The surrounding buildings record different phases of the Delhi Sultanate. The Qutb complex joined the UNESCO World Heritage List in 1993.',
                    'मीनार का निर्माण क़ुतुबुद्दीन ऐबक के समय शुरू हुआ और इल्तुतमिश सहित बाद के शासकों ने इसे आगे बढ़ाया। आसपास की इमारतें दिल्ली सल्तनत के अलग-अलग समय को दिखाती हैं। क़ुतुब परिसर 1993 में यूनेस्को की विश्व धरोहर सूची में शामिल हुआ।',
                  ),
                ),
                const SizedBox(height: 12),
                _detail(
                  _t('Architecture', 'वास्तुकला'),
                  _t(
                    'The tower rises about 72.5 metres and narrows towards the top. Its carved sandstone surfaces and projecting balconies are prominent features. The complex also includes Quwwat-ul-Islam Mosque, Iltutmish\'s Tomb, Alai Darwaza, the Iron Pillar and the unfinished Alai Minar.',
                    'मीनार लगभग 72.5 मीटर ऊँची है और ऊपर की ओर पतली होती जाती है। नक्काशीदार बलुआ पत्थर और बाहर निकली बालकनियाँ इसकी विशेषताएँ हैं। परिसर में कुव्वत-उल-इस्लाम मस्जिद, इल्तुतमिश का मकबरा, अलाई दरवाज़ा, लौह स्तंभ और अधूरी अलाई मीनार भी हैं।',
                  ),
                ),
                const SizedBox(height: 12),
                Material(
                  color: AppTheme.surfaceColor,
                  borderRadius: BorderRadius.circular(16),
                  child: InkWell(
                    borderRadius: BorderRadius.circular(16),
                    onTap: () =>
                        Navigator.of(context).push(MaterialPageRoute<void>(
                      builder: (_) => StoryReaderScreen(
                        titleEnglish: 'Qutub Minar story',
                        titleHindi: 'क़ुतुब मीनार की कहानी',
                        initialHindi: _isHindi,
                        storyEnglish: rootBundle
                            .loadString('assets/stories/qutub_minar_en.txt'),
                        storyHindi: rootBundle
                            .loadString('assets/stories/qutub_minar_hi.txt'),
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
                              _t('Qutub Minar story', 'क़ुतुब मीनार की कहानी'),
                              style: const TextStyle(
                                color: AppTheme.primaryTextColor,
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                          const Icon(Icons.chevron_right,
                              color: AppTheme.accentColor),
                        ],
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 20),
                Text(_t('Qutub Minar gallery', 'क़ुतुब मीनार की तस्वीरें'),
                    style: const TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.w600)),
                const SizedBox(height: 10),
                SizedBox(
                  height: 165,
                  child: ListView.separated(
                    scrollDirection: Axis.horizontal,
                    itemCount: _photos.length,
                    separatorBuilder: (_, __) => const SizedBox(width: 10),
                    itemBuilder: (context, index) {
                      final (en, hi, path) = _photos[index];
                      return InkWell(
                        onTap: () => _openPhoto(_t(en, hi), path),
                        child: SizedBox(
                          width: 185,
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(14),
                            child: Stack(
                              fit: StackFit.expand,
                              children: [
                                Image.asset(path, fit: BoxFit.cover),
                                Align(
                                  alignment: Alignment.bottomCenter,
                                  child: Container(
                                    color: Colors.black54,
                                    padding: const EdgeInsets.all(8),
                                    width: double.infinity,
                                    child: Text(_t(en, hi),
                                        style: const TextStyle(
                                            color: Colors.white)),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                ),
                const SizedBox(height: 20),
                Text(
                    _t('Places to visit near Qutub Minar',
                        'क़ुतुब मीनार के आसपास घूमने की जगहें'),
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
                FutureBuilder<GuideCatalog>(
                  future: _catalog,
                  builder: (context, snapshot) {
                    if (snapshot.hasError) {
                      return Text(
                          _t('Nearby places could not be loaded.',
                              'आसपास की जगहें अभी नहीं खुल सकीं।'),
                          style: const TextStyle(color: Colors.white));
                    }
                    if (!snapshot.hasData) {
                      return Text(
                          _t('Loading nearby places…',
                              'आसपास की जगहें खुल रही हैं…'),
                          style: const TextStyle(color: Colors.white70));
                    }
                    final nearby = snapshot.data!.nearbyFor('qutub_minar');
                    return Column(
                      children: [
                        for (final place in nearby) ...[
                          _nearbyCard(place),
                          const SizedBox(height: 8),
                        ],
                      ],
                    );
                  },
                ),
                const SizedBox(height: 16),
                ReviewsPanel(placeId: 'qutub_minar', hindi: _isHindi),
                const SizedBox(height: 12),
                OutlinedButton.icon(
                  onPressed: () => context.push(
                      '/report/qutub_minar?lang=${_isHindi ? 'hi' : 'en'}'),
                  icon: const Icon(Icons.report_outlined),
                  label: Text(_t('Report an issue at this place',
                      'इस जगह की समस्या बताएँ')),
                  style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.white,
                      side: const BorderSide(color: Colors.white70)),
                ),
                const SizedBox(height: 20),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _card(String title, Widget content) =>
      GuideSectionCard(title: title, content: content);

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
                  child: Text(
                      _isHindi ? guideNameHindi(place.name) : place.name,
                      style: const TextStyle(fontWeight: FontWeight.w600)),
                ),
                const Icon(Icons.chevron_right),
              ],
            ),
          ),
        ),
      );

  Widget _fact(String label, String value) =>
      GuideFactLine(label: label, value: value);

  Widget _detail(String title, String body) =>
      GuideDetailCard(title: title, body: body);

  void _openPhoto(String title, String path) {
    showDialog<void>(
      context: context,
      builder: (dialogContext) => Dialog(
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(children: [
                Expanded(child: Text(title)),
                IconButton(
                    tooltip: 'Close photo',
                    onPressed: () => Navigator.pop(dialogContext),
                    icon: const Icon(Icons.close)),
              ]),
              ConstrainedBox(
                constraints: BoxConstraints(
                    maxHeight: MediaQuery.sizeOf(dialogContext).height * 0.7),
                child: InteractiveViewer(
                  child: Image.asset(path, fit: BoxFit.contain),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
