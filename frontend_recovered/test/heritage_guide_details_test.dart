import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sih_test_1/data/guide_catalog.dart';
import 'package:sih_test_1/screens/result/heritage_guide_screen.dart';
import 'package:sih_test_1/screens/result/guide_sections.dart';

void main() {
  testWidgets(
      'common guide opens both sections and switches their content to Hindi',
      (tester) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    late GuideCatalog catalog;
    await tester.runAsync(() async {
      catalog = await GuideCatalog.load();
    });
    final entry = catalog.byId['red_fort']!;
    Future<void> tapSection(String title) async {
      await Scrollable.ensureVisible(tester.element(find.text(title)),
          alignment: 0.5);
      await tester.pump(const Duration(milliseconds: 350));
      await tester.tap(find.text(title));
    }
    await tester.pumpWidget(
        const MaterialApp(home: HeritageGuideScreen(placeId: 'red_fort')));
    await tester.pump(const Duration(milliseconds: 350));
    await tester
        .runAsync(() => Future<void>.delayed(const Duration(milliseconds: 30)));
    await tester.pump(const Duration(milliseconds: 350));
    final scrollable = find.byType(Scrollable).first;
    await tester.scrollUntilVisible(find.text('History'), 200,
        scrollable: scrollable);
    await tapSection('History');
    await tester.pump(const Duration(milliseconds: 350));
    await tester
        .runAsync(() => Future<void>.delayed(const Duration(milliseconds: 30)));
    await tester.pump(const Duration(milliseconds: 350));
    expect(find.text(entry.history), findsOneWidget);
    await tester.scrollUntilVisible(find.text('Architecture'), 200,
        scrollable: scrollable);
    await tapSection('Architecture');
    await tester.pump(const Duration(milliseconds: 350));
    await tester
        .runAsync(() => Future<void>.delayed(const Duration(milliseconds: 30)));
    await tester.pump(const Duration(milliseconds: 350));
    expect(find.text(entry.architecture), findsOneWidget);
    await tester.tap(find.text('हिंदी'));
    await tester.pump(const Duration(milliseconds: 350));
    await tester
        .runAsync(() => Future<void>.delayed(const Duration(milliseconds: 30)));
    await tester.pump(const Duration(milliseconds: 350));
    await tester.scrollUntilVisible(find.text('प्रमाणित तथ्य'), -200,
        scrollable: scrollable);
    expect(find.byType(GuideFactsCard), findsOneWidget);
    expect(find.text(entry.factLabelsHindi.first), findsOneWidget);
    expect(find.text(entry.factsHindi.first), findsOneWidget);
    expect(find.text(entry.facts.first), findsNothing);
    await tester.scrollUntilVisible(find.text('इतिहास'), 200,
        scrollable: scrollable);
    await tapSection('इतिहास');
    await tester.pump(const Duration(milliseconds: 350));
    await tester
        .runAsync(() => Future<void>.delayed(const Duration(milliseconds: 30)));
    await tester.pump(const Duration(milliseconds: 350));
    expect(find.text(entry.historyHindi), findsOneWidget);
    await tester.scrollUntilVisible(find.text('वास्तुकला'), 200,
        scrollable: scrollable);
    await tapSection('वास्तुकला');
    await tester.pump(const Duration(milliseconds: 350));
    await tester
        .runAsync(() => Future<void>.delayed(const Duration(milliseconds: 30)));
    await tester.pump(const Duration(milliseconds: 350));
    expect(find.text(entry.architectureHindi), findsOneWidget);
  });
}
