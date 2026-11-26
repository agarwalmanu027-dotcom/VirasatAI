
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sih_test_1/app/app.dart';
import 'package:sih_test_1/app/routes.dart';
import 'package:sih_test_1/app/app_session.dart';
import 'package:sih_test_1/data/guide_catalog.dart';

void main() {
  testWidgets('Library search opens a prepared Red Fort guide',
      (tester) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.runAsync(GuideCatalog.load);

    AppSession.instance.signInForDemo('test@example.com');
    await tester.pumpWidget(const VirasatApp());
    AppRoutes.router.go(AppRoutes.guideLibrary);
    await tester.pump();
    await tester.pump(const Duration(seconds: 1));
    await tester.runAsync(() async =>
        await Future<void>.delayed(const Duration(milliseconds: 10)));
    await tester.pump();

    expect(find.text('Heritage guides'), findsOneWidget);
    await tester.enterText(find.byType(EditableText), 'Red Fort');
    await tester.pumpAndSettle();
    await tester.tap(find.text('Red Fort, Delhi'));
    await tester.pump();
    await tester.pump(const Duration(seconds: 1));
    await tester.runAsync(() async =>
        await Future<void>.delayed(const Duration(milliseconds: 10)));
    await tester.pump();

    expect(find.text('Red Fort, Delhi'), findsOneWidget);
    await tester.scrollUntilVisible(find.text('Red Fort, Delhi story'), 150,
        scrollable: find.byType(Scrollable).first);
    await tester.tap(find.text('Red Fort, Delhi story'));
    await tester.pumpAndSettle();
    expect(find.text('Red Fort, Delhi story'), findsOneWidget);
    expect(find.byType(SelectableText), findsOneWidget);
  });
}
