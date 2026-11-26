// Uses the exact app preprocessing and match policy for local CPU diagnostics.
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:sih_test_1/data/dinov2_input.dart';
import 'package:sih_test_1/data/dinov2_matcher.dart';

void main(List<String> args) {
  if (args.length != 2) {
    throw ArgumentError(
        'Usage: dino_diagnostic.dart prepare|score manifest.json');
  }
  final items =
      (jsonDecode(File(args[1]).readAsStringSync()) as List).cast<Map>();
  if (args[0] == 'prepare') {
    for (final row in items) {
      final input =
          decodeDinoInput(File(row['image'] as String).readAsBytesSync());
      if (input == null) throw StateError('Cannot decode diagnostic image');
      File(row['tensor'] as String)
          .writeAsBytesSync(input.buffer.asUint8List());
    }
    stdout.writeln('Prepared ${items.length} tensors using app preprocessing.');
  } else if (args[0] == 'score') {
    final refs = File('assets/models/dinov2_references.f32').readAsBytesSync();
    final matcher = DinoReferenceMatcher(
      embeddings: Float32List.view(refs.buffer, refs.offsetInBytes),
      classIds: File('assets/models/dinov2_reference_ids.u8').readAsBytesSync(),
      dimension: 384,
      classCount: 20,
    );
    final labels = File('assets/models/dinov2_labels.txt').readAsLinesSync();
    final result = <Map<String, Object?>>[];
    for (final row in items) {
      final bytes = File(row['embedding'] as String).readAsBytesSync();
      final match =
          matcher.predict(Float32List.view(bytes.buffer, bytes.offsetInBytes));
      result.add({
        'image': row['image'],
        'expected': row['expected'],
        'role': row['role'],
        'predicted': labels[match.classId],
        'similarity': match.similarity,
        'margin': match.margin,
        'oldAccepted': match.margin >= 0.0165,
        'accepted': DinoRecognitionPolicy.accepts(match),
      });
    }
    stdout.writeln(jsonEncode(result));
  } else {
    throw ArgumentError('Unknown operation');
  }
}
