"""Import user-provided raw images that passed manual visual review."""

from __future__ import annotations

import json
from pathlib import Path
from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "frontend_recovered" / "assets" / "data" / "guide_catalog.json"
GALLERY = ROOT / "frontend_recovered" / "assets" / "images" / "guide_library"

APPROVED = {
    "mysore_palace__st_philomenas_church_crypt": {
        "folder": ROOT / "new images folder" / "raw" / "mysore_palace" / "sub_places" / "st_philomenas_church",
        "indices": [0, 2, 3, 5, 7, 9, 13, 17],
        "note": "Cathedral context views; the Drive batch contains no verified crypt interior.",
    },
}


def images(folder: Path) -> list[Path]:
    return [p for p in folder.rglob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}]


def main() -> None:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    entries = {row["id"]: row for row in data["entries"]}
    source_log = []
    added = 0
    for place_id, decision in APPROVED.items():
        files = images(decision["folder"])
        photos = entries[place_id].setdefault("photos", [])
        for sequence, index in enumerate(decision["indices"], 1):
            source = files[index]
            filename = f"{place_id}__drive_{sequence:02d}.jpg"
            relative = f"assets/images/guide_library/{filename}"
            if relative in photos:
                continue
            with Image.open(source) as image:
                image = ImageOps.exif_transpose(image).convert("RGB")
                image.thumbnail((1280, 1280), Image.Resampling.LANCZOS)
                image.save(GALLERY / filename, "JPEG", quality=84, optimize=True, progressive=True)
            photos.append(relative)
            source_log.append({"placeId": place_id, "source": str(source.relative_to(ROOT)).replace("\\", "/"), "appAsset": relative, "note": decision["note"]})
            added += 1
    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "tools" / "image_review" / "reviewed_raw_zero_manifest.json").write_text(json.dumps(source_log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"added": added}))


if __name__ == "__main__":
    main()
