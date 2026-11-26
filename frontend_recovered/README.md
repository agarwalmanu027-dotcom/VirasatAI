# VirasatAI Flutter application

This folder contains the current Android app. See the repository root README for the full project description, setup and limitations.

## Current demo

- Version `1.0.1+8`, arm64 Android version code `2008`.
- On-device DINOv2/ONNX monument matching for 20 supported classes, with manual selection when a confident match is unavailable.
- Twenty main monument groups and 200 associated guide entries; two associated entries retain identity-pending notices.
- Packaged galleries, English/Hindi stories, shared facts/history/architecture cards, device text-to-speech and external Maps links.
- Real account sign-in, Android Keystore encrypted session persistence, reports with optional image/GPS and visitor reviews.

The root project context contains implementation history; older notes describe intermediate versions and should not override the latest verified state.

## Run and build

```powershell
flutter pub get
flutter run -d <device-id>
flutter build apk --release --split-per-abi --target-platform android-arm64
```

Set `--dart-define=VIRASATAI_API_BASE_URL=https://your-api.example` to use your own API. The code otherwise uses the development deployment configured in `lib/data/auth_api.dart`.

The demo release uses the project debug signing configuration. Supply your own private signing key before publishing. Local Android SDK paths and signing credentials are excluded from Git.

## Checks

```powershell
flutter analyze
flutter test
```

The latest guide change passed 11 targeted guide/catalog/widget checks and focused Dart analysis. Do not read this as a new benchmark of model accuracy.

## Platform and content boundaries

Android is the supported demo platform. Existing web launchers are development previews; browser support for the full native recognition, encrypted sessions, Maps and reporting behavior is not established by an Android build.

Packaged guides and recognition can run offline. Server account operations and submissions require connectivity; speech needs a suitable installed voice. Reports are stored by VirasatAI and are not automatically forwarded to a government authority. Additional BHASHINI translation languages and authority verification are future integration work.

The ready-to-build assets are in this folder. Rebuilding the gallery from the root content tools requires the original reviewed photos, which remain outside Git.
