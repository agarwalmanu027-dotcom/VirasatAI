import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter_onnxruntime/flutter_onnxruntime.dart';

import 'dinov2_input.dart';
import 'dinov2_matcher.dart';
import 'monument_guess.dart';

const _dimension = 384;
const _references = 2155;
const _classes = 20;

Future<OrtSession>? _session;
Future<_ReferenceBank>? _bank;

Future<OrtSession> _loadSession() => _session ??= OnnxRuntime()
    .createSessionFromAsset(
      'assets/models/dinov2_vits14_encoder.onnx',
      options: OrtSessionOptions(
        // Bound native memory used for CPU workers and tensor caching on phones.
        intraOpNumThreads: 2,
        interOpNumThreads: 1,
        useArena: false,
      ),
    );

Future<_ReferenceBank> _loadBank() => _bank ??= _ReferenceBank.load();

class _ReferenceBank {
  const _ReferenceBank(this.matcher, this.labels);

  final DinoReferenceMatcher matcher;
  final List<String> labels;

  static Future<_ReferenceBank> load() async {
    final data = await rootBundle.load('assets/models/dinov2_references.f32');
    final ids = await rootBundle.load('assets/models/dinov2_reference_ids.u8');
    final labels =
        (await rootBundle.loadString('assets/models/dinov2_labels.txt'))
            .trim()
            .split('\n');
    if (data.lengthInBytes != _references * _dimension * 4 ||
        ids.lengthInBytes != _references ||
        labels.length != _classes) {
      throw StateError('DINOv2 model and reference bank do not match.');
    }
    return _ReferenceBank(
      DinoReferenceMatcher(
        embeddings: Float32List.view(
            data.buffer, data.offsetInBytes, _references * _dimension),
        classIds: Uint8List.view(ids.buffer, ids.offsetInBytes, _references),
        dimension: _dimension,
        classCount: _classes,
      ),
      labels,
    );
  }
}

Future<MonumentGuess?> classifyMonument(Uint8List imageBytes) async {
  final pixels = await compute(decodeDinoInput, imageBytes);
  if (pixels == null) return null;
  final session = await _loadSession();
  final bank = await _loadBank();
  if (session.inputNames.single != 'image' ||
      session.outputNames.single != 'embedding') {
    throw StateError('Unexpected DINOv2 ONNX inputs or outputs.');
  }

  final input =
      await OrtValue.fromList(pixels, [1, 3, dinoInputSide, dinoInputSide]);
  Map<String, OrtValue>? outputs;
  try {
    outputs = await session.run({'image': input});
    final values = await outputs['embedding']!.asFlattenedList();
    final embedding = Float32List.fromList(
        values.cast<num>().map((v) => v.toDouble()).toList());
    final match = bank.matcher.predict(embedding);
    if (!DinoRecognitionPolicy.accepts(match)) return null;
    // Return absolute similarity only after the recognition gate has passed.
    // This is still not a calibrated probability; the UI never shows a %.
    return MonumentGuess(
        bank.labels[match.classId], match.similarity.clamp(0.0, 1.0));
  } finally {
    await input.dispose();
    if (outputs != null) {
      for (final value in outputs.values) {
        await value.dispose();
      }
    }
  }
}
