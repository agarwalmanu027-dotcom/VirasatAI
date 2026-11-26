from __future__ import annotations

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "tools" / "image_review" / "remaining_zero_broad"
OUT = ROOT / "tools" / "image_review" / "remaining_zero_sheets"
OUT.mkdir(exist_ok=True)
FONT = ImageFont.load_default()

for folder in SOURCE.iterdir():
    metadata = folder / "candidates.json"
    if not metadata.exists():
        continue
    data = json.loads(metadata.read_text(encoding="utf-8"))
    rows = data.get("candidates", [])
    if not rows:
        continue
    cells = []
    for row in rows:
        path = folder / f"candidate_{row['candidateId']:02d}.jpg"
        if not path.exists():
            continue
        try:
            with Image.open(path) as image:
                image = ImageOps.exif_transpose(image).convert("RGB")
                image.thumbnail((300, 210))
                cell = Image.new("RGB", (320, 270), "white")
                cell.paste(image, ((320-image.width)//2, 5))
                draw = ImageDraw.Draw(cell)
                title = row.get("title", "").replace("File:", "")
                draw.text((8, 220), f"#{row['candidateId']} {title[:45]}", fill="black", font=FONT)
                cells.append(cell)
        except Exception:
            pass
    if not cells:
        continue
    cols = 4
    rows_n = (len(cells) + cols - 1) // cols
    sheet = Image.new("RGB", (cols*320, rows_n*270), "#dddddd")
    for index, cell in enumerate(cells):
        sheet.paste(cell, ((index % cols)*320, (index // cols)*270))
    sheet.save(OUT / f"{folder.name}.jpg", quality=88)
    print(folder.name, len(cells))
