import 'dart:math' as math;
import 'dart:typed_data';

/// Cosine similarities, not probabilities of a correct identification.
class DinoMatch {
  const DinoMatch(this.classId, this.similarity, this.runnerUpSimilarity);

  final int classId;
  final double similarity;
  final double runnerUpSimilarity;

  double get margin => similarity - runnerUpSimilarity;
}

/// Conservative prototype guard, not a calibrated unknown-place detector.
/// Both absolute support and separation matter: a large gap alone can occur
/// when every supported monument is a poor match. See the evaluation note in
/// tools/model_training/unknown_rejection_2026-10-24.md before changing these.
class DinoRecognitionPolicy {
  static const minimumSimilarity = 0.65;
  static const minimumMargin = 0.03;

  static bool accepts(DinoMatch match) =>
      match.classId >= 0 &&
      match.similarity.isFinite &&
      match.runnerUpSimilarity.isFinite &&
      match.similarity >= minimumSimilarity &&
      match.similarity <= 1.0001 &&
      match.runnerUpSimilarity >= -1.0001 &&
      match.margin >= minimumMargin;
}

/// The evaluated retrieval rule: average the three nearest references in each
/// class, then rank classes. Kept separate from ONNX so it can be tested.
class DinoReferenceMatcher {
  DinoReferenceMatcher({
    required this.embeddings,
    required this.classIds,
    required this.dimension,
    required this.classCount,
  }) {
    if (dimension < 1 ||
        classCount < 2 ||
        embeddings.length != classIds.length * dimension) {
      throw StateError('DINOv2 reference dimensions do not match.');
    }
    final counts = List<int>.filled(classCount, 0);
    for (var row = 0; row < classIds.length; row++) {
      final id = classIds[row];
      if (id >= classCount) throw StateError('Invalid reference class ID.');
      counts[id]++;
      var normSquared = 0.0;
      for (var i = 0; i < dimension; i++) {
        final value = embeddings[row * dimension + i];
        normSquared += value * value;
      }
      if (!normSquared.isFinite || (normSquared - 1).abs() > 0.001) {
        throw StateError('DINOv2 references must be finite unit vectors.');
      }
    }
    if (counts.any((count) => count < 3)) {
      throw StateError('Each class needs at least three DINOv2 references.');
    }
  }

  final Float32List embeddings;
  final Uint8List classIds;
  final int dimension;
  final int classCount;

  DinoMatch predict(Float32List query) {
    if (query.length != dimension) {
      throw StateError('Unexpected DINOv2 embedding size.');
    }
    var norm = 0.0;
    for (final value in query) {
      norm += value * value;
    }
    norm = math.sqrt(norm);
    if (norm == 0 || !norm.isFinite) {
      throw StateError('Invalid DINOv2 embedding.');
    }
    final top = List.generate(classCount, (_) => List<double>.filled(3, -2));
    for (var row = 0; row < classIds.length; row++) {
      var similarity = 0.0;
      final offset = row * dimension;
      for (var i = 0; i < dimension; i++) {
        similarity += query[i] * embeddings[offset + i];
      }
      similarity /= norm;
      final nearest = top[classIds[row]];
      if (similarity > nearest[2]) {
        nearest[0] = nearest[1];
        nearest[1] = nearest[2];
        nearest[2] = similarity;
      } else if (similarity > nearest[1]) {
        nearest[0] = nearest[1];
        nearest[1] = similarity;
      } else if (similarity > nearest[0]) {
        nearest[0] = similarity;
      }
    }
    var best = 0;
    var bestScore = -2.0;
    var secondScore = -2.0;
    for (var c = 0; c < classCount; c++) {
      final score = (top[c][0] + top[c][1] + top[c][2]) / 3;
      if (score > bestScore) {
        secondScore = bestScore;
        bestScore = score;
        best = c;
      } else if (score > secondScore) {
        secondScore = score;
      }
    }
    return DinoMatch(best, bestScore, secondScore);
  }
}
