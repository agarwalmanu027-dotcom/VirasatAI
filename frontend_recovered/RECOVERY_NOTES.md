# Recovered VirasatAI Flutter frontend

These files were assembled from the individually supplied temporary files on 9 October 2026. The source Dart files, two tests, `pubspec.yaml`, `pubspec.lock`, and eleven image assets were copied without changing their contents. This is a separate copy for inspection; it has not been merged into the main VirasatAI content folders.

## What is included

- `lib/main.dart` starts the Flutter app.
- `lib/app/` contains the app, theme, and routes.
- `lib/screens/` contains welcome/login, home, explore, scan, analysis, and result screens. Some route destinations lead to `PlaceholderScreen`.
- `lib/widgets/` contains reusable UI widgets.
- `lib/models/` and `lib/data/mock_data.dart` contain prototype data structures and sample records.
- `assets/images/` contains eleven files declared in `pubspec.yaml`, but five files with `.jpg` names are actually small "File not found" text responses, so only six are real image assets.
- `test/` contains two supplied widget tests.

## Important current behavior

- The scan screen can request a camera or gallery image through `image_picker`, but its Analyze action goes directly to `/result/taj-mahal`. It does not run a trained monument model.
- The analysis screen waits two seconds, then shows the same fixed Taj Mahal result.
- Several places, damage types, health scores, and dated health histories in `mock_data.dart` are demonstration data. They are not verified AI predictions or real conservation records.
- The result screen labels one card "Akbar's Tomb" while displaying a Chini Ka Rauza image. Do not present that pairing as correct. Other inherited asset labels and credits need review before public use.
- `agra_fort.jpg`, `chini_ka_rauza.jpg`, `itimad_ud_daulah.jpg`, `jama_masjid.jpg`, and `mehtab_bagh.jpg` are invalid image files. Their contents begin with "File not found". Replace or remove their references before claiming the app displays them.
- The supplied `PROJECT.md` was not copied. It presents broad features such as automated government filing and structural health monitoring as if they were established; those claims conflict with the current approved student-project scope and have not been verified in this code.
- No app audio, model inference, database, or working issue-report submission is established by these retrieved files.

## Why some supplied files were left out

Generic Flutter launcher icons, duplicate images, generated desktop/iOS/Linux build files, scattered Gradle/XML/Swift files, and files named `download` were not needed to recover the Flutter UI source. The standalone root `README.md` was the default Flutter template rather than an explanation of this app. The PDF and unrelated project documents remain in the supplied temporary location; they were not treated as code.

## Verification and next step

Static checks found 24 Dart source files and all relative imports resolved. All eleven declared asset paths exist, but only six contain real image data. Flutter was not available as a shell command in this environment, so `flutter analyze`, `flutter test`, and app launch were not run. To make this a full runnable Flutter project, install or locate Flutter, run `flutter create .` in this folder to generate platform scaffolding, then `flutter pub get`, `flutter analyze`, and `flutter test`. Review any generated platform configuration before using a device. Preserve the existing `lib/`, `assets/`, `test/`, and `pubspec.yaml` files.

The main project decisions remain in `../VirasatAI_Project_Context.txt`. Use this frontend as the starting interface only after deciding which prototype features to retain and replacing mock claims with real behavior.
