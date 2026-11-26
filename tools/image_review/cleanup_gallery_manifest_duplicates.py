"""Remove assets created more than once for the same reviewed candidate."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "frontend_recovered" / "assets" / "data" / "guide_catalog.json"
MANIFEST = ROOT / "frontend_recovered" / "assets" / "images" / "guide_library" / "REVIEWED_GALLERY_MANIFEST.json"


def main() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    kept = []
    duplicate_assets = set()
    seen = set()
    for item in payload.get("images", []):
        key = (item.get("placeId"), item.get("candidateId"))
        if key in seen:
            duplicate_assets.add(item["asset"])
        else:
            seen.add(key)
            kept.append(item)

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    for entry in catalog["entries"]:
        entry["photos"] = [photo for photo in entry.get("photos", []) if photo not in duplicate_assets]
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for asset in duplicate_assets:
        path = ROOT / "frontend_recovered" / asset
        if path.exists():
            path.unlink()
    MANIFEST.write_text(json.dumps({"totalRecorded": len(kept), "images": kept}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"removedDuplicateAssets": len(duplicate_assets), "remainingRecords": len(kept)}))


if __name__ == "__main__":
    main()
