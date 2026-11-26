"""Prepare traceable Commons candidates for weak monument classes in Colab.

Run only in the already authenticated 885-account notebook. This downloads
small previews to Colab for visual review; it does not modify raw_copy.
"""

import hashlib
import io
import json
import random
import time
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageOps
from googleapiclient.http import MediaFileUpload

API_URL = "https://commons.wikimedia.org/w/api.php"
REVIEW_DIR = Path("/content/virasatai_weak_review")
REVIEW_DIR.mkdir(exist_ok=True)
CATEGORIES = {
    "badami_cave_temples": "Category:Exterior of the Badami Cave Temples",
    "city_palace_udaipur": "Category:Lake views of City Palace (Udaipur)",
    "jaisalmer_fort": "Category:Remote views of Jaisalmer Fort",
    "amer_fort": "Category:Views of Amber Fort",
}
MAX_PER_CLASS = 18
session = requests.Session()
session.headers.update({"User-Agent": "VirasatAI-student-dataset/1.0 (educational image review)"})


def commons(params):
    for attempt in range(5):
        try:
            r = session.get(API_URL, params={"format": "json", **params}, timeout=35)
            r.raise_for_status()
            return r.json()
        except requests.RequestException:
            if attempt == 4:
                raise
            time.sleep(min(20, 2 ** attempt))


def category_titles(category):
    titles = []
    token = None
    while True:
        args = {"action": "query", "list": "categorymembers", "cmtitle": category,
                "cmtype": "file", "cmlimit": "max"}
        if token:
            args["cmcontinue"] = token
        data = commons(args)
        titles.extend(x["title"] for x in data["query"]["categorymembers"])
        token = data.get("continue", {}).get("cmcontinue")
        if not token:
            return titles


def image_info(titles):
    for start in range(0, len(titles), 40):
        data = commons({"action": "query", "prop": "imageinfo",
                        "titles": "|".join(titles[start:start + 40]),
                        "iiprop": "url|size|sha1|extmetadata", "iiurlwidth": 500})
        for page in data["query"]["pages"].values():
            if page.get("imageinfo"):
                yield page["title"], page["imageinfo"][0]


candidate_rows = []
for label, category in CATEGORIES.items():
    eligible = []
    for title, info in image_info(category_titles(category)):
        license_name = info.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "")
        lower = title.lower()
        if not license_name.startswith(("CC BY", "CC0", "PD", "Public domain")):
            continue
        if info.get("width", 0) < 1000 or info.get("height", 0) < 640:
            continue
        if any(word in lower for word in ("map", "drawing", "painting", "sketch", "collage", "diagram")):
            continue
        if not info.get("thumburl"):
            continue
        eligible.append((title, info, license_name))
    random.Random(74).shuffle(eligible)
    rows = []
    for title, info, license_name in eligible:
        if len(rows) >= MAX_PER_CLASS:
            break
        try:
            response = session.get(info["thumburl"], timeout=40)
            response.raise_for_status()
            photo = Image.open(io.BytesIO(response.content)).convert("RGB")
            token = hashlib.sha1(title.encode()).hexdigest()[:12]
            preview = REVIEW_DIR / f"{label}_{token}.jpg"
            photo.save(preview, quality=85)
            rows.append({"label": label, "index": len(rows), "title": title,
                         "category": category, "page": "https://commons.wikimedia.org/wiki/" + title.replace(" ", "_"),
                         "thumb_url": info["thumburl"], "license": license_name,
                         "sha1": info.get("sha1", ""), "width": info["width"], "height": info["height"],
                         "preview": str(preview)})
            time.sleep(0.6)
        except Exception as exc:
            print("SKIP", label, title, str(exc)[:100], flush=True)
    if not rows:
        continue
    canvas = Image.new("RGB", (6 * 190, 3 * 205), "white")
    draw = ImageDraw.Draw(canvas)
    for row in rows:
        index = row["index"]
        x, y = index % 6 * 190, index // 6 * 205
        with Image.open(row["preview"]) as image:
            canvas.paste(ImageOps.fit(image, (180, 170)), (x, y))
        draw.text((x + 3, y + 173), str(index) + ": " + row["title"][5:26], fill="black")
    sheet = REVIEW_DIR / f"{label}_commons_candidates.jpg"
    canvas.save(sheet, quality=86)
    uploaded = api().files().create(
        body={"name": sheet.name, "parents": [folder2["id"]]},
        media_body=MediaFileUpload(str(sheet), mimetype="image/jpeg"),
        fields="id,name").execute()
    print("CANDIDATES", label, "eligible", len(eligible), "review", len(rows),
          "sheet", uploaded["id"], flush=True)
    candidate_rows.extend(rows)

manifest_path = REVIEW_DIR / "commons_candidate_manifest.json"
manifest_path.write_text(json.dumps(candidate_rows, indent=2), encoding="utf-8")
created = api().files().create(
    body={"name": manifest_path.name, "parents": [folder2["id"]]},
    media_body=MediaFileUpload(str(manifest_path), mimetype="application/json"),
    fields="id,name").execute()
print("CANDIDATE MANIFEST", created["id"], len(candidate_rows), flush=True)
