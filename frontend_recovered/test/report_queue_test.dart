import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sih_test_1/data/report_queue.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('offline report queue survives a read and keeps one stable client ID', () async {
    const channel = MethodChannel('virasatai/reports');
    var stored = '[]';
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(channel, (call) async {
      if (call.method == 'read') return stored;
      if (call.method == 'write') {
        stored = call.arguments as String;
        return null;
      }
      throw MissingPluginException();
    });
    addTearDown(() => TestDefaultBinaryMessengerBinding.instance
        .defaultBinaryMessenger.setMockMethodCallHandler(channel, null));

    final id = ReportQueue.newClientId();
    await ReportQueue.add(PendingReport(
      clientId: id, ownerEmail: 'student@example.com', placeId: 'taj-mahal',
      category: 'litter', description: 'Plastic bottles near the entrance.',
      locationLabel: 'West gate', createdAt: '2026-10-12T00:00:00Z',
    ));
    final reloaded = await ReportQueue.read();
    expect(reloaded, hasLength(1));
    expect(reloaded.single.clientId, id);
    expect(reloaded.single.placeId, 'taj-mahal');
    expect(reloaded.single.description, 'Plastic bottles near the entrance.');
  });
}
