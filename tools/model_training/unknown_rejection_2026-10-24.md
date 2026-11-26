# Unsupported-photo rejection probe (24 October 2026)

The user supplied a phone screenshot in which a roadside local shrine was offered as Red Fort. The screenshot is not the original photo: its preview contains app labels, darkening and phone overlay controls. `tmp/unknown_scan/friend_photo_preview_proxy.jpg` is a crop of that screenshot solely for diagnosis.

## Why the old code guessed Red Fort

The DINOv2 retrieval encoder always ranks one of its 20 classes. The old app kept only the score difference between the first and second class. A large relative lead could pass even when the image was unlike every supported monument. The screenshot crop scored Red Fort with mean top-three cosine similarity 0.4183 and class margin 0.0322. The old app rule accepted margins at or above 0.0165, so this proxy reproduces the reported failure.

## Current prototype rule

The app now requires both mean top-three cosine similarity at least 0.65 and top-two class margin at least 0.03. Rejected images return no named result. The UI offers a clearer photo and manual selection. These numbers are provisional engineering cutoffs based on local exploratory probes, not calibrated probabilities or a validated unknown-place detector.

We used exact Dart phone preprocessing, the bundled ONNX model on local CPU, the bundled 2,155-image reference bank, and the same Dart retrieval function/policy to probe 40 existing gallery photos of supported monuments, 18 visually inspected gallery photos of other places and the screenshot crop. The gallery sets may share photo sources or sessions with model training; they are **not an independent test set**.

| Exploratory group | Images | Old accepted | New accepted | Correct top label |
| --- | ---: | ---: | ---: | ---: |
| Supported gallery | 40 | 36 | 26 | 37 |
| Other-place gallery | 18 | 14 | 4 | Not a supported label |
| User screenshot crop proxy | 1 | 1 | 0 | Red Fort ranked first, but now rejected |

All 26 newly accepted supported-gallery photos had the expected label; that is a property of this small, non-independent sample, not a measured phone accuracy. Four other places still passed as wrong monument suggestions: Chini Ka Rauza and Bibi Ka Maqbara as Taj Mahal, Aihole Durga Temple as Hampi, and Qutb Shahi Tombs as Taj Mahal. They look architecturally related, so an image-only embedding and one global cutoff cannot guarantee that every unsupported place is rejected. The policy also rejects 14/40 supported-gallery examples, including some correctly ranked photos; this is a real coverage tradeoff.

## What remains to verify

1. Obtain the original photo selected by the friend and test that photo on the new phone APK; the screenshot proxy cannot prove exact phone parity.
2. Assemble source-disjoint, real-phone known and unknown photographs. Include other red sandstone forts, similar Mughal tombs and local temples as hard unknowns. Do not reuse development-test photos to claim final performance.
3. Report known-photo recognition accuracy, accepted-known coverage and unknown false-accept rate separately, by place and by full/partial view. Select thresholds using validation, then freeze them before independent testing.
4. If near-lookalike unknown false accepts remain too high, train a separate supported-vs-unknown verifier with those negatives or add a human confirmation route. Never claim 100% or 90% unknown detection from this probe.

The local scripts `make_unknown_scan_probe.py`, `run_unknown_scan_probe.py` and Flutter `tool/dino_diagnostic.dart` can repeat this diagnosis without changing model weights or reference images. Their scratch files remain under `tmp/unknown_scan` and are not shipped in the app.
