"""Fill app galleries from already visually reviewed candidate images.

This script never selects a new image. It only consumes candidate IDs recorded
as selected in reviewed*.json files, avoids byte-identical duplicates, creates
size-conscious JPEG app assets, and updates guide_catalog.json plus a manifest.
"""

from __future__ import annotations

import glob
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[2]
REVIEW_ROOT = ROOT / "tools" / "image_review"
CANDIDATES = REVIEW_ROOT / "candidates"
EXPANSION_CANDIDATES = REVIEW_ROOT / "expansion_candidates"
APP_IMAGES = ROOT / "frontend_recovered" / "assets" / "images" / "guide_library"
CATALOG = ROOT / "frontend_recovered" / "assets" / "data" / "guide_catalog.json"
MANIFEST = APP_IMAGES / "REVIEWED_GALLERY_MANIFEST.json"
COVERAGE_AUDIT = REVIEW_ROOT / "app_gallery_coverage_audit.json"
TARGET_COUNT = 8


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def selected_candidates() -> dict[str, set[int]]:
    selected: dict[str, set[int]] = defaultdict(set)
    for name in glob.glob(str(REVIEW_ROOT / "reviewed*.json")):
        try:
            records = json.loads(Path(name).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(records, list):
            continue
        for record in records:
            if not isinstance(record, dict) or not record.get("place_id"):
                continue
            for item in record.get("selected", []):
                candidate_id = item.get("candidate_id") if isinstance(item, dict) else None
                if isinstance(candidate_id, int) and candidate_id > 0:
                    selected[record["place_id"]].add(candidate_id)
    return selected


def metadata_for(place_id: str) -> list[dict]:
    path = CANDIDATES / place_id / "candidates.json"
    if not path.exists() or not any((CANDIDATES / place_id).glob("candidate_*.jpg")):
        path = EXPANSION_CANDIDATES / place_id / "candidates.json"
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("candidates", []) if isinstance(payload, dict) else []


def save_optimized(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB")
        image.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
        image.save(destination, "JPEG", quality=84, optimize=True, progressive=True)


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    selected = selected_candidates()
    manifest: list[dict] = []
    if MANIFEST.exists():
        previous = json.loads(MANIFEST.read_text(encoding="utf-8"))
        if isinstance(previous, dict) and isinstance(previous.get("images"), list):
            manifest.extend(previous["images"])
    recorded_candidates = {
        (item.get("placeId"), item.get("candidateId"))
        for item in manifest if isinstance(item, dict)
    }
    added = 0

    for entry in catalog["entries"]:
        place_id = entry["id"]
        photos: list[str] = list(entry.get("photos", []))
        known_hashes = set()
        for asset in photos:
            local = ROOT / "frontend_recovered" / asset
            if local.exists():
                known_hashes.add(sha256(local))

        metadata = metadata_for(place_id)
        for candidate_id in sorted(selected.get(place_id, set())):
            if len(photos) >= TARGET_COUNT:
                break
            if (place_id, candidate_id) in recorded_candidates:
                continue
            source = CANDIDATES / place_id / f"candidate_{candidate_id:02d}.jpg"
            if not source.exists():
                source = EXPANSION_CANDIDATES / place_id / f"candidate_{candidate_id:02d}.jpg"
            if not source.exists():
                continue
            source_hash = sha256(source)
            if source_hash in known_hashes:
                continue
            next_number = len(photos) + 1
            destination = APP_IMAGES / f"{place_id}_{next_number:02d}.jpg"
            while destination.exists():
                next_number += 1
                destination = APP_IMAGES / f"{place_id}_{next_number:02d}.jpg"
            save_optimized(source, destination)
            asset_path = "assets/images/guide_library/" + destination.name
            photos.append(asset_path)
            known_hashes.add(source_hash)
            info = metadata[candidate_id - 1] if candidate_id <= len(metadata) else {}
            manifest.append({
                "placeId": place_id,
                "asset": asset_path,
                "candidateId": candidate_id,
                "title": info.get("title", ""),
                "sourcePage": info.get("source_page", ""),
                "author": info.get("author", ""),
                "license": info.get("license", ""),
                "licenseUrl": info.get("license_url", ""),
            })
            recorded_candidates.add((place_id, candidate_id))
            added += 1
        entry["photos"] = photos

    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({"addedInLatestRun": added, "totalRecorded": len(manifest), "images": manifest}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts = [len(entry.get("photos", [])) for entry in catalog["entries"]]
    coverage = [{
        "id": entry["id"], "name": entry["name"], "groupId": entry["groupId"],
        "isMain": entry["isMain"], "photoCount": len(entry.get("photos", [])),
        "neededForMinimumSeven": max(0, 7 - len(entry.get("photos", []))),
    } for entry in catalog["entries"]]
    COVERAGE_AUDIT.write_text(json.dumps({
        "target": "minimum 7 photos per entry; 8 for main monuments",
        "entries": coverage,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "added": added,
        "entries": len(counts),
        "atLeastEight": sum(count >= TARGET_COUNT for count in counts),
        "zero": sum(count == 0 for count in counts),
        "remainingToEight": sum(max(0, TARGET_COUNT - count) for count in counts),
    }))


if __name__ == "__main__":
    main()
