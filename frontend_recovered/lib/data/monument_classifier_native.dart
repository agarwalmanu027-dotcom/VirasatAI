import 'package:flutter/services.dart';
import 'package:image/image.dart' as img;
import 'package:tflite_flutter/tflite_flutter.dart';

import 'monument_guess.dart';

Future<Interpreter>? _interpreter;
Future<List<String>>? _labels;

Future<Interpreter> _loadInterpreter() => _interpreter ??=
    Interpreter.fromAsset('assets/models/monument_model.tflite');

Future<List<String>> _loadLabels() => _labels ??= rootBundle
    .loadString('assets/models/labels.txt')
    .then((value) => value.trim().split('\n'));

const _imageSide = 160;
List<List<List<List<double>>>> _makeInput(img.Image oriented) {
  final shortest =
      oriented.width < oriented.height ? oriented.width : oriented.height;
  final centre = img.copyCrop(
    oriented,
    x: (oriented.width - shortest) ~/ 2,
    y: (oriented.height - shortest) ~/ 2,
    width: shortest,
    height: shortest,
  );
  final resized = img.copyResize(
    centre,
    width: _imageSide,
    height: _imageSide,
    interpolation: img.Interpolation.cubic,
  );
  return [
    List.generate(
      _imageSide,
      (y) => List.generate(_imageSide, (x) {
        final pixel = resized.getPixel(x, y);
        return [pixel.r.toDouble(), pixel.g.toDouble(), pixel.b.toDouble()];
      }),
    ),
  ];
}

List<double> _run(
    Interpreter interpreter, List<List<List<List<double>>>> input) {
  final output = [List<double>.filled(20, 0)];
  interpreter.run(input, output);
  return output[0];
}

Future<MonumentGuess?> classifyMonument(Uint8List imageBytes) async {
  final decoded = img.decodeImage(imageBytes);
  if (decoded == null) return null;

  final interpreter = await _loadInterpreter();
  final labels = await _loadLabels();
  if (interpreter.getInputTensor(0).shape.join(',') != '1,160,160,3' ||
      interpreter.getOutputTensor(0).shape.join(',') != '1,20' ||
      labels.length != 20) {
    throw StateError('The bundled monument model and labels do not match.');
  }

  // Match the current Colab model: honour EXIF orientation and pass
  // unnormalised RGB float values (0–255).
  final oriented = img.bakeOrientation(decoded);
  // Use the evaluated centre framing. Taking the maximum score from several
  // crops inflated confidence and could turn one bad crop into a false match.
  final scores = _run(interpreter, _makeInput(oriented));

  var best = 0;
  for (var i = 1; i < scores.length; i++) {
    if (scores[i] > scores[best]) best = i;
  }
  return MonumentGuess(labels[best].trim(), scores[best]);
}
