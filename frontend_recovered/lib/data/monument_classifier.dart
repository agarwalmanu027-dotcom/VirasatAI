import 'dart:typed_data';

import 'monument_classifier_stub.dart'
    if (dart.library.io) 'monument_classifier_dinov2.dart' as platform;
import 'monument_guess.dart';

Future<MonumentGuess?> classifyMonument(Uint8List imageBytes) =>
    platform.classifyMonument(imageBytes);
