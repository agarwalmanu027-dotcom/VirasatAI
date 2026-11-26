# VirasatAI local account and translation backend

This backend uses Node.js 24's built-in SQLite support. No database server or npm package is required. The database file is created at `backend/data/virasatai.sqlite` when the first account request is handled. Keep that file private and back it up before reinstalling or moving the server.

## What SQLite stores now

- `users`: random user ID, normalized email, display name, salted `scrypt` password hash, creation and update timestamps.
- `sessions`: SHA-256 hash of a random sign-in token, user ID, creation time and expiry (30 days).
- `reports`: report ID, owner user ID, place ID, category, optional description/location label, optional GPS coordinates and accuracy, status and timestamps. The `user_id` links each report to its account; a repeated `client_id` lets a phone safely retry without making a duplicate.
- `report_photos`: optional JPEG image (maximum 1 MB), linked to the report ID. The public report response only says whether a photo exists.
- `report_status_events`: a dated record of each report status. Right now only the initial `submitted` event is written; this means received by VirasatAI, not sent to any government authority.
- `reviews`: one rating and optional comment per signed-in user and heritage place. A later review from the same user updates the existing record.

Passwords and raw session tokens are never stored in the database. Heritage guide text, photos and Hindi/English stories remain packaged with the app. The app profile shows server-backed reports/reviews; there is no general browsing-history store. The Android app saves up to 10 report drafts (including compressed photo data and optional GPS coordinates) in private app storage. Once a real account and reachable backend are configured, the app tries to sync on sign-in, resume and every 30 seconds while open. Failed sends remain as drafts. This is foreground auto-sync, not guaranteed background delivery while the app is closed. The web build does not yet persist report drafts. GPS accuracy depends on the phone and surroundings; the app stores the reported accuracy in metres. No report is forwarded to an authority: verification rules and authority integration remain future work.

## Local run

From the project root, run `node backend/server.mjs`. The default URL is `http://127.0.0.1:8787`; the server is reachable only on this PC. Set `PORT` and, if needed, `VIRASATAI_DB_PATH` before starting. The database is not part of the Netlify static upload.

Account routes:

- `POST /auth/register` — JSON `{ "displayName": "Manu", "email": "manu@example.com", "password": "at least 10 characters" }`
- `POST /auth/login` — JSON `{ "email": "manu@example.com", "password": "..." }`
- `GET /auth/me` — `Authorization: Bearer <token>`
- `PATCH /auth/me` — Bearer token and JSON `{ "displayName": "New name" }`
- `POST /auth/logout` — Bearer token

Report routes (all require `Authorization: Bearer <token>`):

- `POST /reports` — JSON `{ "clientId": "a-device-generated-unique-id", "placeId": "taj-mahal", "category": "damage", "description": "A section of the railing appears broken.", "locationLabel": "Near the west gate", "latitude": 27.1751, "longitude": 78.0421, "accuracyM": 12.5, "photoBase64": "..." }`. Description is optional if a JPEG photo is present. GPS fields must be supplied together. Categories: `damage`, `litter`, `access`, `information`, `other`. The same `clientId` and content may be retried safely.
- `GET /reports` — the signed-in user's latest 100 reports.
- `GET /reports/<report-id>` — one report belonging to the signed-in user.

Review routes:

- `GET /places/<place-id>/reviews` — recent reviews and rating summary for a known heritage place.
- `POST /places/<place-id>/reviews` — Bearer token and JSON `{ "rating": 5, "comment": "Helpful guide" }`. The same account can update its review.

Registration and login return the token and public user fields. A Flutter build must specify the reachable API URL with `--dart-define=VIRASATAI_API_BASE_URL=https://your-server.example`. The current Android app defaults to its development Cloudflare API URL. Override it to use your own server. Real Android sessions are stored using the native Keystore encrypted channel and restored on restart until the backend token expires or the user signs out. Demo sessions remain temporary.

For a phone on a different network, the backend must be deployed at an HTTPS address with persistent disk/database storage. The project also has a Cloudflare Worker/D1 deployment; see `cloudflare/README.md`. Local Node/SQLite hosting is a separate option. Do not expose this local pilot directly to the public internet: it still needs production rate limiting, backups, monitoring and deployment hardening. For a browser frontend, set `VIRASATAI_ALLOWED_ORIGINS` to a comma-separated list of exact allowed origins; Android apps do not use browser CORS.

Run local tests with `node --test backend/*.test.mjs` from the project root.

## Bhashini pilot

`POST /translate` remains the earlier local Bhashini adapter. Real API access and language-pair support are unverified. It returns HTTP 503 `TRANSLATION_NOT_CONFIGURED` until private `BHASHINI_USER_ID`, `BHASHINI_API_KEY`, and `BHASHINI_PIPELINE_ID` values are configured. Do not put those credentials in Flutter source or public files.
