import 'dart:io';
import 'dart:math' as math;
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:sih_test_1/data/dinov2_matcher.dart';

DinoReferenceMatcher _fixture(List<List<double>> classScores) {
  final vectors = <double>[];
  final ids = <int>[];
  for (var id = 0; id < classScores.length; id++) {
    for (final score in classScores[id]) {
      vectors.addAll([score, math.sqrt(1 - score * score)]);
      ids.add(id);
    }
  }
  return DinoReferenceMatcher(
    embeddings: Float32List.fromList(vectors),
    classIds: Uint8List.fromList(ids),
    dimension: 2,
    classCount: classScores.length,
  );
}

void main() {
  group('DINO recognition policy', () {
    test('a large margin cannot rescue weak absolute support', () {
      const score = DinoRecognitionPolicy.minimumSimilarity - 0.01;
      const match = DinoMatch(0, score, score - 0.3);
      expect(match.margin, greaterThan(DinoRecognitionPolicy.minimumMargin));
      expect(DinoRecognitionPolicy.accepts(match), isFalse);
    });

    test('strong absolute support is rejected when classes are ambiguous', () {
      const score = DinoRecognitionPolicy.minimumSimilarity + 0.1;
      const match = DinoMatch(
        0,
        score,
        score - DinoRecognitionPolicy.minimumMargin / 2,
      );
      expect(DinoRecognitionPolicy.accepts(match), isFalse);
    });

    test('sufficient absolute support and class separation are accepted', () {
      const score = DinoRecognitionPolicy.minimumSimilarity + 0.01;
      const match = DinoMatch(
        0,
        score,
        score - DinoRecognitionPolicy.minimumMargin - 0.01,
      );
      expect(DinoRecognitionPolicy.accepts(match), isTrue);
    });

    test('invalid class IDs and impossible or non-finite scores are rejected',
        () {
      for (final match in [
        const DinoMatch(-1, 0.9, 0.3),
        const DinoMatch(0, double.nan, 0.3),
        const DinoMatch(0, double.infinity, 0.3),
        const DinoMatch(0, 0.9, double.nan),
        const DinoMatch(0, 0.9, double.negativeInfinity),
        const DinoMatch(0, 1.1, 0.3),
        const DinoMatch(0, 0.9, -1.1),
        const DinoMatch(0, 0.8, 0.9),
      ]) {
        expect(DinoRecognitionPolicy.accepts(match), isFalse);
      }
    });
  });

  group('DINO nearest-three retrieval', () {
    test('averages three neighbors per class instead of the single maximum',
        () {
      final matcher = _fixture([
        [0.9, 0.2, 0.8, 0.7],
        [0.1, 0.99, 0.1, 0.1],
      ]);
      final result = matcher.predict(Float32List.fromList([1, 0]));
      expect(result.classId, 0);
      expect(result.similarity, closeTo(0.8, 1e-7));
      expect(result.runnerUpSimilarity, closeTo(1.19 / 3, 1e-7));
    });

    test('normalizes query magnitude without changing rank or similarity', () {
      final matcher = _fixture([
        [0.9, 0.8, 0.7],
        [0.3, 0.2, 0.1],
      ]);
      final unit = matcher.predict(Float32List.fromList([1, 0]));
      final scaled = matcher.predict(Float32List.fromList([7, 0]));
      expect(scaled.classId, unit.classId);
      expect(scaled.similarity, closeTo(unit.similarity, 1e-10));
      expect(
          scaled.runnerUpSimilarity, closeTo(unit.runnerUpSimilarity, 1e-10));
    });

    test('rejects zero, wrong-size and non-finite query embeddings', () {
      final matcher = _fixture([
        [0.9, 0.8, 0.7],
        [0.3, 0.2, 0.1],
      ]);
      for (final values in [
        <double>[],
        [1.0],
        [1.0, 0.0, 0.0],
        [0.0, 0.0],
        [double.nan, 0.0],
        [double.infinity, 1.0],
      ]) {
        expect(() => matcher.predict(Float32List.fromList(values)),
            throwsStateError);
      }
    });

    test('rejects invalid bank shape, class IDs and insufficient references',
        () {
      final bank = _fixture([
        [0.9, 0.8, 0.7],
        [0.3, 0.2, 0.1],
      ]);
      expect(
        () => DinoReferenceMatcher(
          embeddings: bank.embeddings,
          classIds: bank.classIds,
          dimension: 0,
          classCount: 2,
        ),
        throwsStateError,
      );
      expect(
        () => DinoReferenceMatcher(
          embeddings: bank.embeddings,
          classIds: bank.classIds,
          dimension: 2,
          classCount: 1,
        ),
        throwsStateError,
      );
      expect(
        () => DinoReferenceMatcher(
          embeddings: Float32List(11),
          classIds: bank.classIds,
          dimension: 2,
          classCount: 2,
        ),
        throwsStateError,
      );
      expect(
        () => DinoReferenceMatcher(
          embeddings: bank.embeddings,
          classIds: Uint8List.fromList([0, 0, 0, 1, 1, 2]),
          dimension: 2,
          classCount: 2,
        ),
        throwsStateError,
      );
      expect(
        () => _fixture([
          [0.9, 0.8, 0.7],
          [0.3, 0.2],
        ]),
        throwsStateError,
      );
    });

    test('rejects non-unit and non-finite reference embeddings', () {
      final bank = _fixture([
        [0.9, 0.8, 0.7],
        [0.3, 0.2, 0.1],
      ]);
      for (final badValue in [0.0, 2.0, double.nan, double.infinity]) {
        final corrupted = Float32List.fromList(bank.embeddings);
        corrupted[0] = badValue;
        corrupted[1] = 0;
        expect(
          () => DinoReferenceMatcher(
            embeddings: corrupted,
            classIds: bank.classIds,
            dimension: 2,
            classCount: 2,
          ),
          throwsStateError,
        );
      }
    });

    test('bundled bank keeps the evaluated sorted nearest-three ranking', () {
      // This is a scoring regression, not an independent accuracy test:
      // query vectors deliberately come from the training-reference bank.
      final bytes =
          File('assets/models/dinov2_references.f32').readAsBytesSync();
      final data = ByteData.sublistView(bytes);
      final refs = Float32List(bytes.length ~/ 4);
      for (var i = 0; i < refs.length; i++) {
        refs[i] = data.getFloat32(i * 4, Endian.little);
      }
      final ids =
          File('assets/models/dinov2_reference_ids.u8').readAsBytesSync();
      final classCount = File('assets/models/dinov2_labels.txt')
          .readAsLinesSync()
          .where((line) => line.trim().isNotEmpty)
          .length;
      final dimension = refs.length ~/ ids.length;
      final matcher = DinoReferenceMatcher(
        embeddings: refs,
        classIds: ids,
        dimension: dimension,
        classCount: classCount,
      );
      for (final queryIndex in [0, ids.length ~/ 2, ids.length - 1]) {
        final query = Float32List.fromList(
          refs.sublist(queryIndex * dimension, (queryIndex + 1) * dimension),
        );
        final queryNorm =
            math.sqrt(query.fold<double>(0, (sum, x) => sum + x * x));
        final similarities = List.generate(classCount, (_) => <double>[]);
        for (var row = 0; row < ids.length; row++) {
          var dot = 0.0;
          for (var d = 0; d < dimension; d++) {
            dot += query[d] * refs[row * dimension + d];
          }
          similarities[ids[row]].add(dot / queryNorm);
        }
        final scores = similarities.map((values) {
          values.sort((a, b) => b.compareTo(a));
          return values.take(3).reduce((a, b) => a + b) / 3;
        }).toList();
        final ranking = List.generate(classCount, (id) => id)
          ..sort((a, b) => scores[b].compareTo(scores[a]));
        final actual = matcher.predict(query);
        expect(actual.classId, ranking[0]);
        expect(actual.similarity, closeTo(scores[ranking[0]], 1e-10));
        expect(actual.runnerUpSimilarity, closeTo(scores[ranking[1]], 1e-10));
      }
    });
  });
}
