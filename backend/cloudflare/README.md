# VirasatAI Cloudflare deployment

This folder contains the production-shaped Cloudflare Worker and D1 schema for
accounts, sessions, issue reports with optional JPEG/GPS, status history and
visitor reviews. It does not include BHASHINI credentials or translation.

Live deployment (18 October 2026):

- Worker: `https://virasatai-api.agarwalmanu027.workers.dev`
- D1 database: `virasatai` in APAC, bound as `DB`
- `/health` confirms `status: ok` and `database: connected`
- Registration, login, profile lookup, GPS report submission and review
  submission/read were exercised against the live service. Temporary test data
  was removed afterward.

Build the connected Flutter APK from the project root with:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\build_connected_apk.ps1 -ApiUrl "https://virasatai-api.agarwalmanu027.workers.dev"
```

The real `wrangler.toml` contains the non-secret D1 binding ID. OAuth tokens and
account credentials remain in Wrangler's user configuration and are not stored
in this project.
