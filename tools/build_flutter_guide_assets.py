"""Package the existing reviewed content library for the Flutter guide.

This uses only files already present in this workspace. It does not fetch media.
"""

from __future__ import annotations

import json
import re
from build_guide_details import detail_fields
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "06_Database/JSON/content_library_index.json"
ASSETS = ROOT / "frontend_recovered/assets"
IMAGE_DIR = ASSETS / "images/guide_library"
DATA_FILE = ASSETS / "data/guide_catalog.json"
REVIEWED_MANIFEST = IMAGE_DIR / "REVIEWED_GALLERY_MANIFEST.json"
RAW_ZERO_MANIFEST = ROOT / "tools/image_review/reviewed_raw_zero_manifest.json"
COVERAGE_AUDIT = ROOT / "tools/image_review/app_gallery_coverage_audit.json"


def reviewed_gallery_assets() -> tuple[dict[str, list[str]], dict[str, int]]:
    """Restore the gallery that was visually reviewed after the base catalog build."""
    grouped: dict[str, list[str]] = defaultdict(list)
    for manifest_path in (REVIEWED_MANIFEST, RAW_ZERO_MANIFEST):
        rows = json.loads(manifest_path.read_text(encoding="utf-8"))
        for row in rows["images"] if isinstance(rows, dict) else rows:
            asset = row.get("asset") or row.get("appAsset")
            if asset and (ASSETS.parent / asset).is_file():
                grouped[row["placeId"]].append(asset)
    audit = json.loads(COVERAGE_AUDIT.read_text(encoding="utf-8"))
    expected = {row["id"]: row["photoCount"] for row in audit["entries"]}
    return grouped, expected


def complete_gallery(place_id: str, base: list[str], reviewed: list[str],
                     expected_count: int) -> list[str]:
    candidates = base + reviewed
    if place_id == "taj_mahal":
        candidates += [f"assets/images/taj_gallery/{path.name}"
                       for path in sorted((ASSETS / "images/taj_gallery").glob("*.jpg"))]
    candidates += [
        f"assets/images/guide_library/{path.name}"
        for path in sorted(IMAGE_DIR.glob(f"{place_id}_*.jpg"))
        if re.fullmatch(re.escape(place_id) + r"_[0-9]+\.jpg", path.name)
    ]
    valid = [asset for asset in dict.fromkeys(candidates)
             if (ASSETS.parent / asset).is_file()]
    if len(valid) < expected_count:
        raise ValueError(f"{place_id}: only {len(valid)} photos; reviewed audit expects {expected_count}")
    return valid[:expected_count]


def overview_from_basic(path: Path) -> tuple[str, str]:
    if not path.is_file():
        return "", ""
    text = path.read_text(encoding="utf-8-sig")
    location = re.search(r"(?m)^Location:\s*(.+)$", text)
    overview = re.search(r"(?ms)^Overview\s*\n(.+?)(?:\n\s*\n|\Z)", text)
    return (
        location.group(1).strip() if location else "",
        overview.group(1).strip() if overview else "",
    )


def facts_from_file(path: Path) -> list[str]:
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8-sig")
    return [match.strip() for match in re.findall(r"(?m)^\d+\.\s+(.+)$", text)]


def image_asset(place_id: str, source: str, number: int) -> str | None:
    original = (ROOT / source).resolve()
    if not original.is_relative_to(ROOT) or not original.is_file():
        return None
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    output = IMAGE_DIR / f"{place_id}_{number:02d}.jpg"
    with Image.open(original) as image:
        image = ImageOps.exif_transpose(image)
        if image.mode != "RGB":
            image = image.convert("RGB")
        # The guide is viewed on a phone. Keep reviewed originals in 02_Images
        # and package smaller copies so the offline APK stays practical to share.
        image.thumbnail((840, 840), Image.Resampling.LANCZOS)
        image.save(output, "JPEG", quality=72, optimize=True)
    return output.relative_to(ASSETS.parent).as_posix()


def main() -> None:
    source = json.loads(INDEX.read_text(encoding="utf-8"))
    entries = source["entries"]
    reviewed, expected = reviewed_gallery_assets()
    main_by_order = {entry["group_order"]: entry["id"] for entry in entries if entry["is_main"]}
    compact = []
    photo_count = 0
    main_details = json.loads((ROOT / 'tools/guide_main_details.json').read_text(encoding='utf-8'))
    for entry in entries:
        place_id = entry["id"]
        paths = entry.get("files") or {}
        location, overview = overview_from_basic(ROOT / paths["basic"]) if paths.get("basic") else ("", "")
        facts = facts_from_file(ROOT / paths["facts"]) if paths.get("facts") else []
        narration = entry.get("narration") or {}
        ready = entry["content_status"] == "content_ready"
        # Later reviewed Basic_Info files use numbered facts instead of an
        # Overview heading. Their approved narration supplies a short About.
        if ready and not overview:
            overview = narration.get("english", "").split("\n\n", 1)[0].strip()
        overview_hindi = (narration.get("hindi", "").split("\n\n", 1)[0]
                          if ready else "")

        # The original Taj pilot files use a different, multi-line format.
        # A numbered-line parser would mistake section headings for facts.
        if place_id == "taj_mahal":
            overview = (
                "Shah Jahan commissioned the Taj Mahal in memory of Mumtaz Mahal. "
                "Construction began in 1632 beside the Yamuna River in Agra. "
                "The principal white marble mausoleum was completed in 1648."
            )
            overview_hindi = (
                "शाहजहाँ ने मुमताज़ महल की याद में ताज महल बनवाया। "
                "आगरा में यमुना नदी के किनारे इसका निर्माण 1632 में शुरू हुआ। "
                "मुख्य सफेद संगमरमर का मकबरा 1648 में पूरा हुआ।"
            )
            facts = [
                "Location: Agra, Uttar Pradesh, beside the Yamuna River.",
                "Commissioned by Shah Jahan in memory of Mumtaz Mahal.",
                "Construction began in 1632; the principal mausoleum was completed in 1648.",
                "The wider complex includes a mosque, guest house, gateway and formal garden.",
                "The white marble mausoleum has a central dome and four minarets.",
                "Marble jali, pietra dura stone inlay and Arabic calligraphy decorate the monument.",
                "The Taj Mahal was inscribed on the UNESCO World Heritage List in 1983.",
            ]

        # Use only the library's reviewed local display images. Keep the pilot
        # guides' existing images and do not create duplicate files for them.
        if place_id == "taj_mahal":
            photos = ["assets/images/taj_mahal.jpg"]
        elif place_id == "qutub_minar":
            photos = [
                "assets/images/qutub_gallery/overview.jpg",
                "assets/images/qutub_gallery/different_view.jpg",
                "assets/images/qutub_gallery/detail.jpg",
                "assets/images/qutub_gallery/complex.jpg",
            ]
        else:
            photos = []
            limit = 4 if entry["is_main"] else 2
            for image in entry.get("images", [])[:limit]:
                local_path = image.get("local_path")
                if not local_path:
                    continue
                asset = image_asset(place_id, local_path, len(photos) + 1)
                if asset:
                    photos.append(asset)
                    photo_count += 1

        photos = complete_gallery(place_id, photos, reviewed[place_id], expected[place_id])

        compact.append({
            "id": place_id,
            "name": entry["name"],
            "groupId": main_by_order[entry["group_order"]],
            "groupOrder": entry["group_order"],
            "isMain": entry["is_main"],
            "ready": ready,
            "pendingReason": entry.get("pending_reason") if not ready else None,
            "location": location,
            "overview": overview,
            "overviewHindi": overview_hindi,
            "facts": facts,
            "storyEnglish": narration.get("english", "") if ready else "",
            "storyHindi": narration.get("hindi", "") if ready else "",
            "photos": photos,
        })
        compact[-1].update(detail_fields(compact[-1], main_details))

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(
        json.dumps({"schemaVersion": 1, "entries": compact}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Packaged {len(compact)} entries, {sum(len(row['photos']) for row in compact)} gallery references and {photo_count} base photo copies")
    print(f"Catalog size: {DATA_FILE.stat().st_size:,} bytes")
    print(f"Photo size: {sum(p.stat().st_size for p in IMAGE_DIR.glob('*.jpg')):,} bytes")


if __name__ == "__main__":
    main()
