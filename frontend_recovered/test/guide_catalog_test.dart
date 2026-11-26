import 'package:flutter_test/flutter_test.dart';
import 'package:sih_test_1/data/guide_catalog.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('approved library has 20 groups and 10 places per group', () async {
    final catalog = await GuideCatalog.load();
    expect(catalog.entries.length, 220);
    expect(catalog.mainGroups.length, 20);
    for (final group in catalog.mainGroups) {
      expect(catalog.nearbyFor(group.id).length, 10);
      expect(group.photos.length, greaterThanOrEqualTo(8), reason: group.id);
    }
    expect(catalog.entries.every((entry) => entry.photos.isNotEmpty), isTrue);
    expect(
        catalog.entries
            .fold<int>(0, (count, entry) => count + entry.photos.length),
        1001);
    expect(
        catalog
            .nearbyFor('qutub_minar')
            .every((entry) => entry.photos.isNotEmpty),
        isTrue);
    expect(catalog.entries.where((entry) => entry.ready).length, 218);
    expect(catalog.byId['amer_fort__hathni_kund']!.ready, isFalse);
    final taj = catalog.byId['taj_mahal']!;
    expect(taj.overview, contains('Shah Jahan'));
    expect(taj.facts, hasLength(7));
    expect(taj.facts, isNot(contains('BASIC FACTS')));
    for (final entry in catalog.mainGroups.where(
        (entry) => entry.id != 'taj_mahal' && entry.id != 'qutub_minar')) {
      expect(entry.factsHindi.length, entry.facts.length, reason: entry.id);
      expect(entry.factLabels.length, entry.facts.length, reason: entry.id);
      expect(entry.factLabelsHindi.length, entry.facts.length,
          reason: entry.id);
      expect(entry.history, isNot(entry.facts.join(' ')), reason: entry.id);
      expect(entry.architecture, isNot(entry.facts.join(' ')),
          reason: entry.id);
      for (final text in [
        ...entry.factsHindi,
        entry.historyHindi,
        entry.architectureHindi,
      ]) {
        expect(RegExp(r'[\u0900-\u097F]').hasMatch(text) ||
            RegExp(r'^[0-9\s–.,\[\]]+$').hasMatch(text), isTrue,
            reason: entry.id);
      }
      expect(entry.history, isNotEmpty, reason: entry.id);
      expect(entry.architecture, isNotEmpty, reason: entry.id);
    }
    for (final entry in catalog.entries.where(
      (entry) => entry.groupOrder >= 15 && entry.ready,
    )) {
      expect(entry.overview.trim(), isNotEmpty, reason: entry.id);
      expect(entry.overviewHindi.trim(), isNotEmpty, reason: entry.id);
    }
  });
}
