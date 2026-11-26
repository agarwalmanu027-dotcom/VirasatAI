import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import 'package:sih_test_1/data/monument_guess.dart';
import 'package:sih_test_1/data/guide_catalog.dart';
import 'package:sih_test_1/screens/scan/scan_screen.dart';

class _FakeImagePicker extends ImagePicker {
  final sources = <ImageSource>[];

  @override
  Future<XFile?> pickImage({
    required ImageSource source,
    double? maxWidth,
    double? maxHeight,
    int? imageQuality,
    CameraDevice preferredCameraDevice = CameraDevice.rear,
    bool requestFullMetadata = true,
  }) async {
    sources.add(source);
    return XFile.fromData(
      Uint8List.fromList(base64Decode(
          'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/lZkAAAAASUVORK5CYII=')),
      name: 'photo.png',
      mimeType: 'image/png',
    );
  }
}

void main() {
  testWidgets('Camera choice screen explains the empty area on a small phone',
      (tester) async {
    tester.view.physicalSize = const Size(320, 568);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(MaterialApp(
      home: ScanScreen(imagePicker: _FakeImagePicker()),
    ));
    expect(find.text('Ready to scan a monument'), findsOneWidget);
    expect(find.textContaining('The camera opens separately'), findsOneWidget);
    expect(find.text('Open camera'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('Opening scan launches camera without tapping another button',
      (tester) async {
    final picker = _FakeImagePicker();
    await tester.pumpWidget(MaterialApp(
      home: ScanScreen(
        imagePicker: picker,
        autoOpenCamera: true,
        classifier: (_) async => null,
      ),
    ));
    await tester.pump();
    expect(picker.sources, [ImageSource.camera]);
  });

  testWidgets('Unsupported photo has no named suggestion and can be retaken',
      (tester) async {
    tester.view.physicalSize = const Size(360, 800);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      MaterialApp(
        home: ScanScreen(
          imagePicker: _FakeImagePicker(),
          classifier: (_) async => null,
        ),
      ),
    );
    expect(
        find.text(
            'Recognizes 20 supported monuments. Other places may not be recognized.'),
        findsOneWidget);
    await tester.tap(find.text('Choose from gallery'));
    await tester.pumpAndSettle();

    expect(find.text('Photo ready'), findsOneWidget);
    expect(find.textContaining('Monument could not be confidently recognized'),
        findsOneWidget);
    expect(find.text('Taj Mahal'), findsNothing);
    expect(find.text('Mehtab Bagh'), findsNothing);
    expect(find.textContaining('Possible match:'), findsNothing);
    expect(find.textContaining('Yes, open'), findsNothing);
    expect(find.text('Choose monument manually'), findsOneWidget);

    await tester.tap(find.text('Choose again'));
    await tester.pumpAndSettle();
    expect(find.text('Choose from gallery'), findsOneWidget);
    expect(find.text('Photo ready'), findsNothing);
  });

  testWidgets('Accepted tentative match is offered for confirmation',
      (tester) async {
    await tester.runAsync(() => GuideCatalog.load());
    tester.view.physicalSize = const Size(360, 800);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(MaterialApp(
      home: ScanScreen(
        imagePicker: _FakeImagePicker(),
        classifier: (_) async => const MonumentGuess('taj_mahal', 0.60),
      ),
    ));
    await tester.tap(find.text('Choose from gallery'));
    await tester.runAsync(
        () => Future<void>.delayed(const Duration(milliseconds: 100)));
    for (var i = 0;
        i < 20 &&
            find.textContaining('Possible match: Taj Mahal').evaluate().isEmpty;
        i++) {
      await tester.pump(const Duration(milliseconds: 250));
    }

    expect(find.textContaining('Possible match: Taj Mahal'), findsOneWidget);
    expect(find.textContaining('Yes, open Taj Mahal'), findsOneWidget);
    expect(find.text('Choose monument manually'), findsOneWidget);
  });

  testWidgets('Unsupported photo still allows manual monument selection',
      (tester) async {
    tester.view.physicalSize = const Size(360, 800);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    final router = GoRouter(routes: [
      GoRoute(
        path: '/',
        builder: (_, state) => ScanScreen(
          imagePicker: _FakeImagePicker(),
          classifier: (_) async => null,
        ),
      ),
      GoRoute(
        path: '/guides',
        builder: (_, state) => const Scaffold(body: Text('Manual guide list')),
      ),
    ]);
    addTearDown(router.dispose);
    await tester.pumpWidget(MaterialApp.router(routerConfig: router));
    await tester.tap(find.text('Choose from gallery'));
    await tester.pumpAndSettle();
    expect(find.textContaining('Yes, open'), findsNothing);
    await tester.tap(find.text('Choose monument manually'));
    await tester.pumpAndSettle();
    expect(find.text('Manual guide list'), findsOneWidget);
  });

  for (final score in [double.nan, double.infinity, 1.01]) {
    testWidgets('Invalid confidence $score cannot show a named suggestion',
        (tester) async {
      tester.view.physicalSize = const Size(360, 800);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      await tester.runAsync(GuideCatalog.load);
      await tester.pumpWidget(MaterialApp(
        home: ScanScreen(
          imagePicker: _FakeImagePicker(),
          classifier: (_) async => MonumentGuess('red_fort', score),
        ),
      ));
      await tester.tap(find.text('Choose from gallery'));
      await tester.runAsync(
          () => Future<void>.delayed(const Duration(milliseconds: 100)));
      await tester.pump(const Duration(milliseconds: 250));
      expect(
          find.textContaining('Monument could not be confidently recognized'),
          findsOneWidget);
      expect(find.textContaining('Red Fort'), findsNothing);
      expect(find.textContaining('Yes, open'), findsNothing);
      expect(find.text('Choose monument manually'), findsOneWidget);
    });
  }

  testWidgets('Low-confidence guess is hidden without an open-guide button',
      (tester) async {
    tester.view.physicalSize = const Size(360, 800);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.runAsync(() => GuideCatalog.load());
    await tester.pumpWidget(MaterialApp(
      home: ScanScreen(
        imagePicker: _FakeImagePicker(),
        classifier: (_) async => const MonumentGuess('taj_mahal', 0.42),
      ),
    ));
    await tester.tap(find.text('Choose from gallery'));
    await tester.runAsync(
        () => Future<void>.delayed(const Duration(milliseconds: 100)));
    await tester.pump(const Duration(milliseconds: 250));
    expect(find.textContaining('Monument could not be confidently recognized'),
        findsOneWidget);
    expect(find.textContaining('Taj Mahal'), findsNothing);
    expect(find.textContaining('42%'), findsNothing);
    expect(find.textContaining('Yes, open Taj Mahal'), findsNothing);
  });

  testWidgets('Long match remains usable on a compact phone', (tester) async {
    tester.view.physicalSize = const Size(320, 568);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.runAsync(GuideCatalog.load);
    await tester.pumpWidget(MaterialApp(
      home: ScanScreen(
        imagePicker: _FakeImagePicker(),
        classifier: (_) async =>
            const MonumentGuess('ajanta_ellora_caves', 0.80),
      ),
    ));
    await tester.tap(find.text('Choose from gallery'));
    await tester.runAsync(
        () => Future<void>.delayed(const Duration(milliseconds: 100)));
    await tester.pump(const Duration(milliseconds: 300));
    expect(find.textContaining('Yes, open Ajanta'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
