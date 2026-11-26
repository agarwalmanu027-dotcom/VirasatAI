# VirasatAI

An Android heritage guide and monument recognition project developed by **Manu Agarwal**.

VirasatAI helps visitors explore selected Indian monuments, read or listen to their stories, find associated places, and submit reviews or heritage concerns.

## Current application

- Photo recognition for 20 supported monument classes, using a DINOv2 ViT-S/14 ONNX image encoder and local reference embeddings.
- A guide catalogue with 20 main monument groups and 200 associated places. This content coverage is separate from the model's recognition scope.
- English and Hindi guide content, stories, history and architecture sections. Two associated places retain explicit identity-pending notices.
- 1,001 packaged gallery references, local search, associated-place cards and an external Maps action.
- Device text-to-speech where a suitable language voice is available.
- Real account sign-in, encrypted Android session storage, visitor reviews, and issue reports with optional photos and location.
- Packaged guides and recognition work on the phone without an inference server. Account operations and server submissions need connectivity; offline report drafts can be retained locally.

The checked Android demo is `1.0.1+8`, arm64 version code `2008`. The guide layout update passed 11 targeted tests and focused Dart analysis, and was installed on the development Realme phone. The owner confirmed that the corrected guides work. This is not a claim of universal device compatibility or a new recognition accuracy measurement.

## Technology

- Flutter and Dart: mobile interface and local app logic.
- ONNX Runtime and DINOv2: on-device visual embeddings and monument matching.
- Cloudflare Workers and D1: deployed accounts, reports and reviews API.
- Node.js and SQLite: alternative local backend.
- Python: content packaging, image preparation and model experiment utilities.

## Repository structure

- `frontend_recovered/`: current Flutter application, Android project, tests and packaged model/image/story assets. The folder name is historical; this is the app source.
- `backend/cloudflare/`: Worker, database schema and example deployment configuration.
- `backend/`: local Node.js API and tests. Live SQLite files are excluded.
- `01_Data/`, `03_Scripts/`, `04_Audio/`, `06_Database/`: heritage text, narration resources, catalogue indexes and related source records.
- `02_Images/`: source/license metadata. Original large photo collections remain local; app-ready images are included under the Flutter assets.
- `tools/`: content builders, image review records and model training/evaluation scripts.
- `output/presentation/`, `output/pdf/`: final presentation and code/viva guide.
- `VirasatAI_Final_Project_Report_Revised_v10.docx`: final college report.

## Run the Android app

Install Flutter with a Dart SDK compatible with `frontend_recovered/pubspec.yaml`, Android SDK/build tools and a compatible JDK. Enable USB debugging on an Android phone.

```powershell
cd frontend_recovered
flutter pub get
flutter devices
flutter run -d <device-id>
```

The app currently defaults to the development deployment configured in `lib/data/auth_api.dart`. To use your own backend, supply its HTTPS address:

```powershell
flutter run -d <device-id> --dart-define=VIRASATAI_API_BASE_URL=https://your-api.example
```

Build a demo arm64 APK:

```powershell
flutter build apk --release --split-per-abi --target-platform android-arm64
```

Output: `frontend_recovered/build/app/outputs/flutter-apk/app-arm64-v8a-release.apk`.

The current demo release configuration uses the Android debug signing key. Configure a private release keystore before publishing to an app store. Never commit signing keys.

## Backend and database

For a local backend, use Node.js 24 or a compatible version with built-in SQLite support:

```powershell
node backend/server.mjs
```

The default local URL is `http://127.0.0.1:8787`. A physical phone needs a reachable address; its own `127.0.0.1` is not the laptop. See `backend/README.md` for API routes.

For Cloudflare, copy `backend/cloudflare/wrangler.toml.example` to `wrangler.toml`, create your own D1 database, enter its binding ID, apply `schema.sql`, and deploy with Wrangler. Authenticate using your own Cloudflare account. Account credentials and local Wrangler state are excluded from Git.

## Checks

```powershell
cd frontend_recovered
flutter analyze
flutter test
```

Local backend checks from the repository root:

```powershell
node --test backend/*.test.mjs
```

## Content and model utilities

The packaged catalogue and images are ready to build from a fresh checkout. Do not regenerate image assets unless the original reviewed photo collection is available locally; `tools/build_flutter_guide_assets.py` reads those original paths. `tools/build_guide_details.py` refreshes bilingual detail sections from the existing packaged catalogue and `tools/guide_main_details.json`.

Model experiment scripts are under `tools/model_training/`. Raw datasets and training runs are not included. Read the evaluation notes before quoting results; development-set results are not independent phone-photo accuracy.

## Limitations and future work

Recognition supports selected classes and can reject images or suggest an incorrect match. Associated places are curated relationships, not a guaranteed distance or travel-time ranking. Offline speech depends on installed device voices.

Reports are received by VirasatAI. Automated verification at a 500-report threshold and forwarding to ASI or another authority are planned, not verified operational integrations. The BHASHINI adapter is a pilot; live translation credentials and access are not configured in this repository. Bundled English/Hindi content should not be described as live multilingual translation.

## Assets and private information

Heritage photos and pretrained model assets retain their original licenses. Source/license records are included with the content and gallery metadata; inclusion here does not grant blanket ownership or relicensing rights.

API secrets, passwords, personal account databases, signing keys, machine configuration, build caches, raw datasets and downloaded demo utilities are excluded. Add your own private credentials through environment variables or the relevant provider's secret settings.
