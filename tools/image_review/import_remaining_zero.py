from __future__ import annotations

import io
import json
import time
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "tools" / "image_review"
CATALOG = ROOT / "frontend_recovered" / "assets" / "data" / "guide_catalog.json"
GALLERY = ROOT / "frontend_recovered" / "assets" / "images" / "guide_library"
MANIFEST = GALLERY / "REVIEWED_GALLERY_MANIFEST.json"
AGENT = "Mozilla/5.0 VirasatAI student heritage app"

BROAD = {
    "amer_fort__sagar_lake": [3, 12],
    "red_fort__chunnamal_haveli": [1, 2],
    "red_fort__naughara_kinari_bazaar": [1, 2, 3],
    "mysore_palace__kishkindha_moolika_bonsai_garden": [1, 2, 5, 22],
    "mysore_palace__karanji_lake_aviary": [4, 5, 6, 8, 9, 13, 14, 18],
    "golden_temple__gurdwara_mata_kaulan": [1, 2, 3],
    "khajuraho_monuments__ken_gharial_sanctuary": [1, 2],
    "konark_sun_temple__kuruma_buddhist_site": [1],
    "sanchi_stupa__sonari_stupas": [2, 3, 7, 8],
}

EXPANSION = {
    "sanchi_stupa__andher_stupas": [8],
    "badami_cave_temples__galaganatha_temples": [1, 2, 3, 4, 5, 6, 7, 8],
}


def save_image(raw: bytes, destination: Path) -> None:
    with Image.open(io.BytesIO(raw)) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        image.thumbnail((1280, 1280), Image.Resampling.LANCZOS)
        image.save(destination, "JPEG", quality=84, optimize=True, progressive=True)


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    entries = {row["id"]: row for row in catalog["entries"]}
    manifest_data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest = manifest_data["images"]
    added = 0

    for source_name, decisions in [("remaining_zero_broad", BROAD), ("expansion_candidates", EXPANSION)]:
        for place_id, selected in decisions.items():
            folder = REVIEW / source_name / place_id
            data = json.loads((folder / "candidates.json").read_text(encoding="utf-8"))
            rows = data.get("candidates", data) if isinstance(data, dict) else data
            candidates = {row["candidateId"]: row for row in rows}
            for candidate_id in selected:
                source = folder / f"candidate_{candidate_id:02d}.jpg"
                if not source.exists():
                    continue
                filename = f"{place_id}__verified_{source_name}_{candidate_id:02d}.jpg"
                relative = f"assets/images/guide_library/{filename}"
                if relative in entries[place_id].setdefault("photos", []):
                    continue
                save_image(source.read_bytes(), GALLERY / filename)
                entries[place_id]["photos"].append(relative)
                item = candidates[candidate_id]
                manifest.append({"placeId": place_id, "appAsset": relative, "sourceTitle": item.get("title", ""), "sourcePage": item.get("sourcePage", ""), "author": item.get("author", ""), "license": item.get("license", ""), "licenseUrl": item.get("licenseUrl", ""), "reviewStatus": "visually_reviewed_place_identity"})
                added += 1

    external = json.loads((REVIEW / "remaining_external_sources.json").read_text(encoding="utf-8"))
    for group in external:
        place_id = group["placeId"]
        for index, url in enumerate(group["urls"], 1):
            filename = f"{place_id}__verified_external_{index:02d}.jpg"
            relative = f"assets/images/guide_library/{filename}"
            if relative in entries[place_id].setdefault("photos", []):
                continue
            try:
                req = Request(url, headers={"User-Agent": AGENT, "Referer": group["sourcePage"]})
                with urlopen(req, timeout=60) as response:
                    save_image(response.read(), GALLERY / filename)
            except Exception as error:
                print(json.dumps({"placeId": place_id, "index": index, "error": str(error)}))
                continue
            entries[place_id]["photos"].append(relative)
            manifest.append({"placeId": place_id, "appAsset": relative, "sourceTitle": f"{entries[place_id]['name']} photo {index}", "sourcePage": group["sourcePage"], "author": "Source page contributor", "license": group.get("license", "Source-site reuse terms; verify before public release"), "licenseUrl": group.get("licenseUrl", group["sourcePage"]), "reviewStatus": "visually_matched_external_source"})
            added += 1
            time.sleep(.15)

    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest_data["addedInLatestRun"] = added
    manifest_data["totalRecorded"] = len(manifest)
    MANIFEST.write_text(json.dumps(manifest_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"added": added}))


if __name__ == "__main__":
    main()
