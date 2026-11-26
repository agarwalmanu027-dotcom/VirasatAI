"""Create contact sheets for the exact-source zero-photo review batch."""

from __future__ import annotations

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "tools" / "image_review" / "exact_zero_candidates"
OUTPUT = ROOT / "tools" / "image_review" / "exact_zero_sheets"


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 16)
    for folder in sorted(SOURCE.iterdir()):
        metadata = folder / "candidates.json"
        if not metadata.exists():
            continue
        data = json.loads(metadata.read_text(encoding="utf-8"))
        candidates = [x for x in data["candidates"] if x.get("previewPath")]
        for page, start in enumerate(range(0, len(candidates), 9), 1):
            batch = candidates[start:start + 9]
            rows = (len(batch) + 2) // 3
            canvas = Image.new("RGB", (1650, 52 + rows * 420), "white")
            draw = ImageDraw.Draw(canvas)
            draw.text((12, 12), f"{data.get('displayName')} | exact licensed candidates", font=font, fill="black")
            for index, item in enumerate(batch):
                x, y = (index % 3) * 550, 52 + (index // 3) * 420
                image = Image.open(ROOT / item["previewPath"]).convert("RGB")
                image = ImageOps.contain(image, (530, 330))
                canvas.paste(image, (x + (550 - image.width) // 2, y + (330 - image.height) // 2))
                title = item["title"].removeprefix("File:")
                draw.text((x + 8, y + 337), f"#{item['candidateId']} | {item.get('license')}", font=font, fill="black")
                draw.text((x + 8, y + 361), title[:62], font=font, fill="black")
                draw.text((x + 8, y + 383), title[62:124], font=font, fill="black")
            output = OUTPUT / f"{folder.name}_{page:02d}.jpg"
            canvas.save(output, quality=92)
            print(output)


if __name__ == "__main__":
    main()
