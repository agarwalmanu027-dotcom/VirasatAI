"""Import visually approved exact-source images into the Flutter guide gallery."""

from __future__ import annotations

import json
from pathlib import Path
from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "tools" / "image_review"
CATALOG = ROOT / "frontend_recovered" / "assets" / "data" / "guide_catalog.json"
GALLERY = ROOT / "frontend_recovered" / "assets" / "images" / "guide_library"
MANIFEST = GALLERY / "REVIEWED_GALLERY_MANIFEST.json"


def save_optimized(source: Path, destination: Path) -> None:
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        image.thumbnail((1280, 1280), Image.Resampling.LANCZOS)
        image.save(destination, "JPEG", quality=84, optimize=True, progressive=True)


def main() -> None:
    approved = json.loads((REVIEW / "reviewed_exact_zero.json").read_text(encoding="utf-8"))
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    entries = {row["id"]: row for row in catalog["entries"]}
    manifest_data = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {"images": []}
    manifest = manifest_data["images"]
    added = 0
    for decision in approved:
        place_id = decision["place_id"]
        source_dir = REVIEW / decision.get("source", "exact_zero_candidates") / place_id
        data = json.loads((source_dir / "candidates.json").read_text(encoding="utf-8"))
        source_rows = data["candidates"] if isinstance(data, dict) else data
        candidates = {row["candidateId"]: row for row in source_rows}
        entry = entries[place_id]
        photos = entry.setdefault("photos", [])
        for candidate_id in decision["selected"]:
            item = candidates[candidate_id]
            filename = f"{place_id}__exact_{candidate_id:02d}.jpg"
            relative = f"assets/images/guide_library/{filename}"
            if relative in photos:
                continue
            preview_path = item.get("previewPath") or str(source_dir / f"candidate_{candidate_id:02d}.jpg")
            preview_path = Path(preview_path)
            if not preview_path.is_absolute():
                preview_path = ROOT / preview_path
            save_optimized(preview_path, GALLERY / filename)
            photos.append(relative)
            manifest.append({
                "placeId": place_id,
                "appAsset": relative,
                "sourceTitle": item["title"],
                "sourcePage": item["sourcePage"],
                "author": item["author"],
                "license": item["license"],
                "licenseUrl": item["licenseUrl"],
                "reviewStatus": "visually_reviewed_exact_identity",
            })
            added += 1
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest_data["addedInLatestRun"] = added
    manifest_data["totalRecorded"] = len(manifest)
    MANIFEST.write_text(json.dumps(manifest_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"added": added, "places": len(approved)}))


if __name__ == "__main__":
    main()
