import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sih_test_1/app/app.dart';
import 'package:sih_test_1/app/app_session.dart';
import 'package:sih_test_1/app/routes.dart';
import 'package:sih_test_1/data/guide_catalog.dart';
import 'package:sih_test_1/screens/home/home_screen.dart';

void main() {
  testWidgets('login opens before the heritage home', (tester) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    AppSession.instance.signOut();
    await tester.pumpWidget(const VirasatApp());
    AppRoutes.router.go('/');
    await tester.pumpAndSettle();

    expect(find.text('Sign in to explore'), findsOneWidget);
    await tester.runAsync(() => GuideCatalog.load());
    await tester.enterText(
        find.byType(TextFormField).first, 'manu@example.com');
    await tester.ensureVisible(find.text('Continue in demo mode'));
    await tester.tap(find.text('Continue in demo mode'));
    for (var i = 0; i < 5; i++) {
      await tester.pump(const Duration(milliseconds: 250));
    }
    await tester.runAsync(() async =>
        await Future<void>.delayed(const Duration(milliseconds: 10)));
    await tester.pump();
    expect(find.byType(HomeScreen), findsOneWidget);
    expect(find.text('Where will you explore today?'), findsOneWidget);
    expect(find.text('Open guide'), findsOneWidget);
  });

  testWidgets('demo sign in shows a profile and can sign out', (tester) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    AppSession.instance.signInForDemo('manu@example.com');
    await tester.runAsync(GuideCatalog.load);
    await tester.pumpWidget(const VirasatApp());
    AppRoutes.router.go(AppRoutes.profile);
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 400));
    expect(find.text('manu@example.com'), findsOneWidget);
    await tester.scrollUntilVisible(find.text('Leave demo session'), 160,
        scrollable: find.byType(Scrollable).first);
    await tester.pump(const Duration(milliseconds: 300));
    expect(find.text('Leave demo session'), findsOneWidget);

    await tester.tap(find.text('Leave demo session'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 400));
    expect(find.text('Sign in to explore'), findsOneWidget);
  });
}
