"""Build isolated local review sheets from saved previews; never alters candidate metadata."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "tools" / "image_review"

def make(place_id):
    record = json.loads((REVIEW / "candidates" / place_id / "candidates.json").read_text(encoding="utf-8-sig"))
    rescue = json.loads((REVIEW / "targeted_source_rescue.json").read_text(encoding="utf-8-sig"))
    exact = next((p for p in rescue["places"] if p["place_id"] == place_id), None)
    titles = {f["filename"] for f in exact["recommended_files"] + exact.get("category_file_hints", [])} if exact else None
    niche_path = REVIEW / "additional_niche_rescue_plan.json"
    if exact is None and niche_path.exists():
        niche = json.loads(niche_path.read_text(encoding="utf-8-sig"))
        extra = next((p for p in niche if p["place_id"] == place_id), None)
        if extra:
            titles = set(extra["exact_files"])
    candidates = [c for c in record.get("candidates", []) if titles is None or c["title"] in titles]
    if not candidates:
        print(f"{place_id}: exact-source candidates not yet present")
        return
    out = REVIEW / "targeted_sheets"
    out.mkdir(exist_ok=True)
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 17)
    for start in range(0, len(candidates), 9):
        batch = candidates[start:start+9]
        rows = (len(batch)+2)//3
        canvas = Image.new("RGB", (1680, 55+rows*440), "white")
        draw = ImageDraw.Draw(canvas)
        draw.text((12, 12), f'{record["display_name"]} | exact rescue candidates', font=font, fill="black")
        for i,c in enumerate(batch):
            x,y = (i%3)*560,55+(i//3)*440
            p = Path(c["preview_path"])
            p = p if p.is_absolute() else ROOT/p
            photo = ImageOps.contain(Image.open(p).convert("RGB"), (540,350))
            canvas.paste(photo,(x+(560-photo.width)//2,y+(350-photo.height)//2))
            draw.text((x+8,y+355),f'#{c["candidate_id"]} | {c["original_width"]} x {c["original_height"]}',font=font,fill="black")
            title = c["title"].removeprefix("File:")
            for k in range(3):
                draw.text((x+8,y+379+k*19),title[k*58:(k+1)*58],font=font,fill="black")
        sheet = out / f'{place_id}_{start//9+1:02}.jpg'
        canvas.save(sheet,quality=95)
        print(sheet)

if __name__ == "__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--place",action="append",required=True)
    args=ap.parse_args()
    for p in args.place:
        make(p)

