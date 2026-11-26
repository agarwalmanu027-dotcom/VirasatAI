import 'dart:typed_data';

import 'package:image/image.dart' as img;

const dinoInputSide = 224;
const _mean = [0.485, 0.456, 0.406];
const _std = [0.229, 0.224, 0.225];

/// Shared by phone inference and the desktop regression diagnostic.
/// Keep orientation, cubic interpolation, padding and CHW layout identical.
Float32List? decodeDinoInput(Uint8List imageBytes) {
  final original = img.decodeImage(imageBytes);
  if (original == null) return null;
  final oriented = img.bakeOrientation(original);
  final resized = oriented.width >= oriented.height
      ? img.copyResize(oriented,
          width: dinoInputSide, interpolation: img.Interpolation.cubic)
      : img.copyResize(oriented,
          height: dinoInputSide, interpolation: img.Interpolation.cubic);
  final padded =
      img.Image(width: dinoInputSide, height: dinoInputSide, numChannels: 3);
  img.fill(padded, color: img.ColorRgb8(127, 127, 127));
  img.compositeImage(padded, resized,
      dstX: (dinoInputSide - resized.width) ~/ 2,
      dstY: (dinoInputSide - resized.height) ~/ 2);
  const plane = dinoInputSide * dinoInputSide;
  final input = Float32List(3 * plane);
  for (var y = 0; y < dinoInputSide; y++) {
    for (var x = 0; x < dinoInputSide; x++) {
      final pixel = padded.getPixel(x, y);
      final index = y * dinoInputSide + x;
      input[index] = (pixel.r / 255 - _mean[0]) / _std[0];
      input[plane + index] = (pixel.g / 255 - _mean[1]) / _std[1];
      input[2 * plane + index] = (pixel.b / 255 - _mean[2]) / _std[2];
    }
  }
  return input;
}
