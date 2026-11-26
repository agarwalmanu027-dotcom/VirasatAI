import 'package:flutter_test/flutter_test.dart';
import 'package:sih_test_1/screens/result/speech_chunks.dart';

void main() {
  test('long English and Hindi stories keep every word in short chunks', () {
    final story =
        '${List.filled(12, 'The monument has a long history.').join(' ')}\n\n'
        '${List.filled(12, 'यह स्मारक इतिहास का हिस्सा है।').join(' ')}';
    final chunks = splitSpeechChunks(story);

    expect(chunks.length, greaterThan(2));
    expect(chunks.every((chunk) => chunk.length <= 220), isTrue);
    expect(chunks.join(' '), story.replaceAll(RegExp(r'\s+'), ' ').trim());
  });
}
