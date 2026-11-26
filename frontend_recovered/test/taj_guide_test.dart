import 'package:flutter/material.dart';

import 'package:flutter_test/flutter_test.dart';
import 'package:sih_test_1/app/app.dart';
import 'package:sih_test_1/app/routes.dart';
import 'package:sih_test_1/app/app_session.dart';
import 'package:sih_test_1/data/guide_catalog.dart';

Future<void> openTajGuide(WidgetTester tester) async {
  await tester.runAsync(() => GuideCatalog.load());
  AppSession.instance.signInForDemo('test@example.com');
  await tester.pumpWidget(const VirasatApp());
  AppRoutes.router.go('/result/taj-mahal');
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('Taj guide avoids a mismatched nearby-place photo',
      (tester) async {
    await openTajGuide(tester);

    expect(find.text("Akbar's Tomb"), findsNothing);
    expect(find.text('Agra Fort'), findsNothing);
    expect(find.text('View all 10 associated places'), findsNothing);
  });

  testWidgets('Taj gallery opens and closes a local photo', (tester) async {
    await openTajGuide(tester);

    final frontPhoto = find.text('Front view');
    await tester.ensureVisible(frontPhoto);
    await tester.tap(frontPhoto);
    await tester.pumpAndSettle();

    expect(find.byTooltip('Close photo'), findsOneWidget);
    await tester.tap(find.byTooltip('Close photo'));
    await tester.pumpAndSettle();
    expect(find.byTooltip('Close photo'), findsNothing);
  });

  testWidgets('Taj history expands to show prepared content', (tester) async {
    await openTajGuide(tester);

    final history = find.text('History');
    await tester.ensureVisible(history);
    await tester.tap(history);
    await tester.pumpAndSettle();

    expect(find.textContaining('Mumtaz Mahal died in 1631.'), findsOneWidget);
  });

  testWidgets('Taj guide switches between Hindi and English', (tester) async {
    tester.view.physicalSize = const Size(360, 800);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await openTajGuide(tester);

    await tester.tap(find.text('हिंदी'));
    await tester.pumpAndSettle();
    expect(find.text('प्रमाणित तथ्य'), findsOneWidget);
    expect(find.text('इतिहास'), findsOneWidget);
    expect(find.text('Verified details'), findsNothing);

    await tester.tap(find.text('English'));
    await tester.pumpAndSettle();
    expect(find.text('Verified details'), findsOneWidget);
    expect(find.text('प्रमाणित तथ्य'), findsNothing);
  });

  testWidgets('Prepared story opens in the selected language', (tester) async {
    await openTajGuide(tester);

    final storyButton = find.text('Taj Mahal story');
    await tester.ensureVisible(storyButton);
    await tester.tap(storyButton);
    await tester.pumpAndSettle();
    expect(find.text('Taj Mahal story'), findsOneWidget);
    expect(find.textContaining('Welcome to the Taj Mahal.'), findsOneWidget);
    expect(find.text('Listen'), findsOneWidget);

    await tester.tap(find.text('हिंदी'));
    await tester.pumpAndSettle();
    await tester.runAsync(() async =>
        await Future<void>.delayed(const Duration(milliseconds: 10)));
    await tester.pumpAndSettle();
    expect(find.textContaining('ताज महल में आपका स्वागत है।'), findsOneWidget);
    expect(find.text('सुनें'), findsOneWidget);

    await tester.pageBack();
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('हिंदी'));
    await tester.tap(find.text('हिंदी'));
    await tester.pumpAndSettle();
    final hindiStoryButton = find.text('ताज महल की कहानी');
    await tester.ensureVisible(hindiStoryButton);
    await tester.tap(hindiStoryButton);
    await tester.pumpAndSettle();
    expect(find.text('ताज महल की कहानी'), findsOneWidget);
    expect(find.textContaining('ताज महल में आपका स्वागत है।'), findsOneWidget);
  });

  testWidgets('Taj guide has no unrelated navigation shortcuts',
      (tester) async {
    tester.view.physicalSize = const Size(360, 800);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await openTajGuide(tester);

    expect(find.text('Choose a monument photo'), findsNothing);
    expect(find.text('Explore Qutub Minar guide'), findsNothing);
    expect(find.text('Browse all heritage guides'), findsNothing);
    expect(find.text('Taj Mahal'), findsOneWidget);
  });

  testWidgets('Mehtab Bagh opens prepared nearby details', (tester) async {
    tester.view.physicalSize = const Size(360, 800);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await openTajGuide(tester);

    final details = find.text('Mehtab Bagh');
    await tester.runAsync(() async =>
        await Future<void>.delayed(const Duration(milliseconds: 10)));
    await tester.pumpAndSettle();
    await tester.scrollUntilVisible(details, 400,
        scrollable: find
            .descendant(
                of: find.byType(SingleChildScrollView).first,
                matching: find.byType(Scrollable))
            .first);
    await tester.tap(details);
    await tester.pump();
    await tester.runAsync(() async =>
        await Future<void>.delayed(const Duration(milliseconds: 10)));
    await tester.pumpAndSettle();

    expect(find.text('Mehtab Bagh'), findsOneWidget);
    expect(find.text('Verified details'), findsOneWidget);
  });
}
