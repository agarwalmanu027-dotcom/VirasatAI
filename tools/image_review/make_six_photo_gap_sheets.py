"""Build compact review sheets for nearby places that currently have six photos."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "frontend_recovered/assets/data/guide_catalog.json"
CANDIDATES = ROOT / "tools/image_review/candidates"
MANIFEST = ROOT / "frontend_recovered/assets/images/guide_library/REVIEWED_GALLERY_MANIFEST.json"
OUTPUT = ROOT / "tools/image_review/six_photo_gap_sheets"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=6)
    args = parser.parse_args()
    output = OUTPUT.parent / f"photo_gap_{args.count}_sheets"
    output.mkdir(parents=True, exist_ok=True)
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))["entries"]
    used = {
        row.get("sourcePage")
        for row in json.loads(MANIFEST.read_text(encoding="utf-8"))["images"]
    }
    places = [row for row in catalog if not row["isMain"] and len(row.get("photos", [])) == args.count]
    review_rows = []
    for place in places:
        path = CANDIDATES / place["id"] / "candidates.json"
        if not path.exists():
            continue
        candidates = json.loads(path.read_text(encoding="utf-8"))["candidates"]
        candidates = [row for row in candidates if row.get("source_page") not in used]
        candidates.sort(
            key=lambda row: (row.get("color_score", 0) + row.get("sharpness_score", 0) / 300),
            reverse=True,
        )
        for candidate in candidates[:3]:
            review_rows.append((place, candidate))

    font = ImageFont.load_default(size=18)
    cell_w, cell_h = 390, 300
    cols, rows_per_sheet = 3, 4
    for page, start in enumerate(range(0, len(review_rows), cols * rows_per_sheet), 1):
        subset = review_rows[start:start + cols * rows_per_sheet]
        canvas = Image.new("RGB", (cell_w * cols, cell_h * rows_per_sheet), "white")
        draw = ImageDraw.Draw(canvas)
        for offset, (place, candidate) in enumerate(subset):
            x = (offset % cols) * cell_w
            y = (offset // cols) * cell_h
            image_path = CANDIDATES / place["id"] / f"candidate_{candidate['candidate_id']:02d}.jpg"
            if image_path.exists():
                with Image.open(image_path) as source:
                    thumb = ImageOps.fit(source.convert("RGB"), (370, 220))
                canvas.paste(thumb, (x + 10, y + 10))
            label = f"{place['id']} | #{candidate['candidate_id']}"
            draw.text((x + 10, y + 238), label[:48], fill="black", font=font)
            draw.text((x + 10, y + 260), candidate["title"].replace("File:", "")[:48], fill="black", font=font)
        canvas.save(output / f"gap_{args.count}_{page:02d}.jpg", quality=88)
    print(json.dumps({"places": len(places), "reviewRows": len(review_rows), "sheets": page if review_rows else 0}))


if __name__ == "__main__":
    main()
