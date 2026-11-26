import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../app/theme.dart';

/// Nearby-place details prepared for the Taj Mahal pilot.
class MehtabBaghDetailScreen extends StatelessWidget {
  const MehtabBaghDetailScreen({super.key, required this.isHindi});

  final bool isHindi;

  String _t(String english, String hindi) => isHindi ? hindi : english;

  @override
  Widget build(BuildContext context) {
    final storyPath = isHindi
        ? 'assets/stories/mehtab_bagh_hi.txt'
        : 'assets/stories/mehtab_bagh_en.txt';

    return Scaffold(
      backgroundColor: AppTheme.primaryColor,
      appBar: AppBar(
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
        title: Text(_t('Mehtab Bagh', 'मेहताब बाग')),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 760),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  ClipRRect(
                    borderRadius: BorderRadius.circular(16),
                    child: AspectRatio(
                      aspectRatio: 16 / 9,
                      child: Image.asset(
                        'assets/images/mehtab_bagh_overview.jpg',
                        fit: BoxFit.cover,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  _card(
                    context,
                    title: _t('About', 'परिचय'),
                    child: Text(
                      _t(
                        'Mehtab Bagh is a Mughal garden across the Yamuna River from the Taj Mahal in Agra.',
                        'मेहताब बाग आगरा में यमुना नदी के पार ताज महल के सामने स्थित एक मुगल बाग है।',
                      ),
                      style: const TextStyle(fontSize: 16, height: 1.5),
                    ),
                  ),
                  const SizedBox(height: 12),
                  _card(
                    context,
                    title: _t('Verified details', 'प्रमाणित तथ्य'),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _fact(
                            _t('Location', 'स्थान'),
                            _t('Opposite bank of the Yamuna, Agra',
                                'यमुना के दूसरे किनारे, आगरा')),
                        const SizedBox(height: 8),
                        _fact(_t('Type', 'प्रकार'),
                            _t('Mughal garden', 'मुगल बाग')),
                        const SizedBox(height: 8),
                        _fact(_t('Layout', 'बनावट'),
                            _t('Charbagh tradition', 'चारबाग परंपरा')),
                      ],
                    ),
                  ),
                  const SizedBox(height: 12),
                  _card(
                    context,
                    title: _t('Story', 'कहानी'),
                    child: FutureBuilder<String>(
                      future: rootBundle.loadString(storyPath),
                      builder: (context, snapshot) {
                        if (snapshot.hasError) {
                          return Text(_t('The story could not be opened.',
                              'कहानी अभी नहीं खुल पा रही है।'));
                        }
                        if (!snapshot.hasData) {
                          return const Center(
                              child: CircularProgressIndicator());
                        }
                        return SelectableText(
                          snapshot.data!,
                          style: const TextStyle(fontSize: 16, height: 1.6),
                        );
                      },
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _card(BuildContext context,
      {required String title, required Widget child}) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: AppTheme.primaryTextColor,
                    fontWeight: FontWeight.w600,
                  )),
          const SizedBox(height: 8),
          child,
        ],
      ),
    );
  }

  Widget _fact(String label, String value) {
    return Text.rich(
      TextSpan(children: [
        TextSpan(
          text: '$label: ',
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        TextSpan(text: value),
      ]),
      style: const TextStyle(fontSize: 15, height: 1.4),
    );
  }
}
