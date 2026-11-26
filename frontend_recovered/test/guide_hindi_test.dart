import 'package:flutter_test/flutter_test.dart';
import 'package:sih_test_1/data/guide_catalog.dart';
import 'package:sih_test_1/data/guide_hindi.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  test('known nearby place and city display in Hindi', () {
    expect(guideNameHindi('Mehtab Bagh'), 'मेहताब बाग');
    expect(guideNameHindi('Taj Mahal, Agra'), 'ताज महल, आगरा');
    expect(guideLocationHindi('Agra, Uttar Pradesh, India'),
        'आगरा, उत्तर प्रदेश, भारत');
    expect(
      guideLocationHindi(
          'Across the Yamuna from the Taj Mahal, Agra, Uttar Pradesh'),
      'ताज महल के सामने यमुना नदी के पार, आगरा, उत्तर प्रदेश',
    );
  });

  test('every packaged guide name has a Hindi display spelling', () async {
    final catalog = await GuideCatalog.load();
    final untranslated = catalog.entries
        .where(
            (entry) => RegExp(r'[A-Za-z]').hasMatch(guideNameHindi(entry.name)))
        .map((entry) => entry.name)
        .toList();
    expect(untranslated, isEmpty);
  });

  test('every packaged guide location has a Hindi display spelling', () async {
    final catalog = await GuideCatalog.load();
    final untranslated = catalog.entries
        .where((entry) =>
            entry.location.isNotEmpty &&
            RegExp(r'[A-Za-z]').hasMatch(guideLocationHindi(entry.location)))
        .map((entry) => '${entry.name}: ${guideLocationHindi(entry.location)}')
        .toList();
    if (untranslated.isNotEmpty) {
      // ignore: avoid_print
      print(untranslated.join('\n'));
    }
    expect(untranslated, isEmpty);
  });
}
