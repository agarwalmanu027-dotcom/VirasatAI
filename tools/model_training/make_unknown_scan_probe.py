"""Build a local diagnostic probe from already reviewed gallery assets.

These examples are exploratory only. Gallery photos may overlap training source
sessions, and one user screenshot contains UI overlays. Do not publish these as
an independent accuracy or unknown-detection result.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "tmp" / "unknown_scan"
ASSETS = ROOT / "frontend_recovered" / "assets"
MANIFEST = ASSETS / "images" / "guide_library" / "REVIEWED_GALLERY_MANIFEST.json"
LABELS = (ASSETS / "models" / "dinov2_labels.txt").read_text().splitlines()
UNSUPPORTED = [
    "taj_mahal__chini_ka_rauza",
    "ajanta_ellora_caves__bibi_ka_maqbara",
    "amer_fort__garh_ganesh_temple",
    "badami_cave_temples__aihole_durga_temple",
    "charminar__qutb_shahi_tombs",
    "city_palace_udaipur__vintage_car_museum",
    "gateway_of_india__afghan_church",
    "golden_temple__partition_museum",
    "hampi_monuments__sanapur_lake",
    "jaisalmer_fort__tanot_mata_temple",
    "khajuraho_monuments__raneh_falls",
    "konark_sun_temple__chandrabhaga_beach",
    "mahabalipuram__alamparai_fort",
    "meenakshi_temple__gandhi_memorial_museum",
    "mehrangarh_fort__jaswant_thada",
    "mysore_palace__railway_museum_mysore",
    "qutub_minar__jamali_kamali_mosque",
    "red_fort__st_james_church",
    "sanchi_stupa__udayagiri_caves",
    "victoria_memorial__armenian_church",
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tensors").mkdir(exist_ok=True)
    (OUT / "embeddings").mkdir(exist_ok=True)
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in json.loads(MANIFEST.read_text(encoding="utf-8"))["images"]:
        if not row.get("asset") or not row.get("placeId"):
            continue
        photo = ROOT / "frontend_recovered" / row["asset"]
        if photo.is_file():
            grouped[row["placeId"]].append({"path": photo, "sourcePage": row["sourcePage"]})

    candidates = []
    for label in LABELS:
        found = grouped[label][:2]
        if label == "taj_mahal":
            found = [
                {"path": ASSETS / "images" / "taj_mahal.jpg", "sourcePage": "bundled gallery"},
                {"path": ASSETS / "images" / "taj_gallery" / "front.jpg", "sourcePage": "bundled gallery"},
            ]
        for row in found:
            candidates.append((row["path"], label, "known_gallery_probe", row["sourcePage"]))
    for place in UNSUPPORTED:
        for row in grouped[place][:1]:
            candidates.append((row["path"], "unknown", "unknown_gallery_probe", row["sourcePage"]))

    # Screenshot crop is a proxy for the image selected by the friend. It has
    # overlay graphics and must never be called the original phone photo.
    user_image = Path(r"C:\Users\MANU AGARWAL\Downloads\WhatsApp Image 2026-10-24 at 5.17.50 PM.jpeg")
    if user_image.exists():
        with Image.open(user_image) as image:
            image.crop((27, 177, 693, 1077)).save(OUT / "friend_photo_preview_proxy.jpg", quality=95)
        candidates.append((OUT / "friend_photo_preview_proxy.jpg", "unknown", "screenshot_proxy", "user screenshot"))

    rows = []
    for i, (image, expected, role, source_page) in enumerate(candidates):
        rows.append({
            "image": str(image.resolve()),
            "tensor": str((OUT / "tensors" / f"{i:03d}.f32").resolve()),
            "embedding": str((OUT / "embeddings" / f"{i:03d}.f32").resolve()),
            "expected": expected,
            "role": role,
            "sourcePage": source_page,
        })
    (OUT / "fixture_manifest.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    # A quick human check for identity ambiguity before treating any image as
    # an unsupported example. Only probes, never training or test labels.
    unknown_rows = [r for r in rows if r["role"] != "known_gallery_probe"]
    sheet = Image.new("RGB", (1200, ((len(unknown_rows) + 3) // 4) * 225), "white")
    draw = ImageDraw.Draw(sheet)
    for i, row in enumerate(unknown_rows):
        with Image.open(row["image"]) as source:
            thumb = source.convert("RGB")
            thumb.thumbnail((280, 180))
        x, y = (i % 4) * 300 + 10, (i // 4) * 225 + 10
        sheet.paste(thumb, (x, y))
        draw.text((x, y + 185), Path(row["image"]).stem[:34], fill="black")
    sheet.save(OUT / "unknown_contact_sheet.jpg", quality=90)
    print({"known_gallery": sum(r["role"] == "known_gallery_probe" for r in rows),
           "unknown_gallery": sum(r["role"] == "unknown_gallery_probe" for r in rows),
           "screenshot_proxy": sum(r["role"] == "screenshot_proxy" for r in rows)})


if __name__ == "__main__":
    main()
