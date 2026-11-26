import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sih_test_1/screens/result/qutub_minar_guide_screen.dart';

void main() {
  testWidgets('Qutub guide shows prepared facts and both story languages',
      (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: QutubMinarGuideScreen()),
    );
    await tester.pumpAndSettle();

    expect(find.text('Qutub Minar'), findsOneWidget);
    await tester.scrollUntilVisible(find.text('Verified details'), 150);
    expect(find.text('Verified details'), findsOneWidget);
    await tester.scrollUntilVisible(find.text('Qutub Minar story'), 150);
    await tester.tap(find.text('Qutub Minar story'));
    await tester.pumpAndSettle();
    expect(find.textContaining('Welcome to the Qutub Minar complex'),
        findsOneWidget);

    await tester.pageBack();
    await tester.pumpAndSettle();
    await tester.tap(find.text('हिंदी'));
    await tester.pumpAndSettle();
    await tester.scrollUntilVisible(find.text('क़ुतुब मीनार की कहानी'), 150,
        scrollable: find.byType(Scrollable).first);
    await Scrollable.ensureVisible(
        tester.element(find.text('क़ुतुब मीनार की कहानी')),
        alignment: 0.5);
    await tester.pumpAndSettle();
    await tester.tap(find.text('क़ुतुब मीनार की कहानी'));
    await tester.pumpAndSettle();
    expect(find.textContaining('महरौली के क़ुतुब मीनार परिसर'), findsOneWidget);
  });
}
