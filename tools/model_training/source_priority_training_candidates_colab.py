"""Collect traceable Commons image candidates for weak monument classes.

Run in Colab as manuagarwal885@gmail.com. This creates private review sheets,
not training files. Visually verify identity, source and duplication first.
"""

import csv
import hashlib
import io
import json
import random
import time
from pathlib import Path

import google.auth
import requests
from google.colab import auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from PIL import Image, ImageDraw, ImageOps

ROOT_ID = "1FL98KnE_e-BigfluYAGfFgLXdXtx9WWT"
MANIFEST_ID = "19BLdHeZLeq4YxLvB8OWLjwRZs_mgEWSv"
OUT = Path("/content/virasatai_priority_training_candidates")
OUT.mkdir(parents=True, exist_ok=True)
MAX_PER_CLASS = 20
QUERIES = {
    "badami_cave_temples": ["Badami Cave Temples Karnataka", "Badami cave temple entrance sculpture"],
    "sanchi_stupa": ["Great Stupa Sanchi Madhya Pradesh", "Sanchi Stupa torana"],
    "mysore_palace": ["Mysore Palace Amba Vilas exterior", "Mysore Palace interior"],
    "red_fort": ["Red Fort Delhi Lahori Gate", "Red Fort Delhi Diwan i Am"],
    "jaisalmer_fort": ["Jaisalmer Fort Rajasthan exterior", "Jaisalmer Fort Rajasthan entrance"],
    "hampi_monuments": ["Hampi Vittala Temple Karnataka", "Hampi Virupaksha Temple Karnataka"],
    "konark_sun_temple": ["Konark Sun Temple Odisha exterior", "Konark Sun Temple wheel sculpture"],
}

auth.authenticate_user()
creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/drive"])
drive = build("drive", "v3", credentials=creds, cache_discovery=False)
email = drive.about().get(fields="user(emailAddress)").execute()["user"]["emailAddress"].lower()
assert email == "manuagarwal885@gmail.com", email
manifest = list(csv.DictReader(io.StringIO(
    drive.files().get_media(fileId=MANIFEST_ID).execute().decode("utf-8-sig"))))
assert len(manifest) == 3141
old_hashes = [int(r["dhash"], 16) for r in manifest]

session = requests.Session()
session.headers.update({"User-Agent": "VirasatAI-student-image-review/1.0 (educational project)"})


def commons(params):
    for attempt in range(6):
        try:
            response = session.get("https://commons.wikimedia.org/w/api.php",
                                   params={"format": "json", **params}, timeout=40)
            if response.status_code in (429, 500, 502, 503, 504):
                time.sleep(min(60, 5 * (attempt + 1)))
                continue
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            if attempt == 5:
                raise
            time.sleep(min(60, 3 * (attempt + 1)))
    raise RuntimeError("Commons rate limit; rerun later")


def titles_for(query):
    data = commons({"action": "query", "list": "search", "srsearch": query,
                    "srnamespace": 6, "srlimit": 70})
    return [x["title"] for x in data["query"]["search"]]


def info_for(titles):
    for start in range(0, len(titles), 25):
        data = commons({"action": "query", "prop": "imageinfo",
                        "titles": "|".join(titles[start:start + 25]),
                        "iiprop": "url|size|sha1|extmetadata", "iiurlwidth": 700})
        for page in data["query"]["pages"].values():
            if page.get("imageinfo"):
                yield page["title"], page["imageinfo"][0]


def dhash(image):
    small = ImageOps.grayscale(image).resize((9, 8))
    pixels = list(small.getdata())
    result = 0
    for y in range(8):
        for x in range(8):
            result = (result << 1) | (pixels[y * 9 + x] > pixels[y * 9 + x + 1])
    return result


folder = drive.files().create(body={"name": "priority_training_image_review_2026-10-22",
                                    "mimeType": "application/vnd.google-apps.folder",
                                    "parents": [ROOT_ID]}, fields="id,webViewLink").execute()
all_rows = []
for label, queries in QUERIES.items():
    titles = []
    for query in queries:
        titles.extend(titles_for(query))
        time.sleep(0.5)
    titles = list(dict.fromkeys(titles))
    random.Random(20261022 + list(QUERIES).index(label)).shuffle(titles)
    selected = []
    new_hashes = []
    for title, info in info_for(titles[:100]):
        if len(selected) >= MAX_PER_CLASS:
            break
        name = title.lower()
        license_name = info.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "")
        if not license_name.startswith(("CC BY", "CC0", "PD", "Public domain")):
            continue
        if min(info.get("width", 0), info.get("height", 0)) < 900:
            continue
        if any(word in name for word in ("map", "diagram", "drawing", "painting", "collage", "logo")):
            continue
        if not info.get("thumburl"):
            continue
        try:
            response = session.get(info["thumburl"], timeout=45)
            response.raise_for_status()
            with Image.open(io.BytesIO(response.content)) as opened:
                photo = opened.convert("RGB")
            visual_hash = dhash(photo)
            if any((visual_hash ^ old).bit_count() <= 4 for old in old_hashes):
                continue
            if any((visual_hash ^ old).bit_count() <= 4 for old in new_hashes):
                continue
            token = hashlib.sha1(title.encode()).hexdigest()[:12]
            preview = OUT / f"{label}_{token}.jpg"
            photo.save(preview, quality=88)
            row = {"label": label, "index": len(selected), "title": title,
                   "source_page": "https://commons.wikimedia.org/wiki/" + title.replace(" ", "_"),
                   "license": license_name, "source_sha1": info.get("sha1", ""),
                   "width": info["width"], "height": info["height"],
                   "preview_dhash": hex(visual_hash), "preview_name": preview.name}
            selected.append(row)
            new_hashes.append(visual_hash)
            time.sleep(0.4)
        except Exception as error:
            print("SKIP", label, title, str(error)[:100], flush=True)
    if not selected:
        print("NO_CANDIDATES", label, flush=True)
        continue
    columns = 5
    rows_on_sheet = (len(selected) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * 240, rows_on_sheet * 230), "white")
    draw = ImageDraw.Draw(sheet)
    for row in selected:
        x = row["index"] % columns * 240
        y = row["index"] // columns * 230
        with Image.open(OUT / row["preview_name"]) as opened:
            tile = ImageOps.contain(opened, (230, 195))
        sheet.paste(tile, (x + (230 - tile.width) // 2, y))
        draw.text((x + 3, y + 197), f"{row['index']}: {row['title'][5:34]}", fill="black")
    sheet_path = OUT / f"{label}_candidate_sheet.jpg"
    sheet.save(sheet_path, quality=90)
    manifest_path = OUT / f"{label}_candidates.json"
    manifest_path.write_text(json.dumps(selected, indent=2), encoding="utf-8")
    for path in (sheet_path, manifest_path):
        drive.files().create(body={"name": path.name, "parents": [folder["id"]]},
                             media_body=MediaFileUpload(str(path), resumable=True),
                             fields="id").execute()
    all_rows.extend(selected)
    print("CANDIDATES", label, len(selected), flush=True)

print("PRIORITY_REVIEW_READY", {"candidates": len(all_rows), "classes": len(QUERIES),
                                "folder": folder}, flush=True)
