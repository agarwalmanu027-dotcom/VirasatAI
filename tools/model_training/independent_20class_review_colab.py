"""Prepare review sheets for the 16 classes absent from the earlier 4-class test.

Run only in the authenticated 885 Colab notebook. Nothing is trained or scored
here. Each candidate must be visually verified before being called test data.
"""

import csv
import hashlib
import io
import json
import random
import time
from collections import Counter
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageOps
from google.colab import auth
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

auth.authenticate_user()
creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/drive"])
drive20 = build("drive", "v3", credentials=creds, cache_discovery=False)
account = drive20.about().get(fields="user(emailAddress)").execute()["user"]["emailAddress"].lower()
assert account == "manuagarwal885@gmail.com", account

ROOT_ID = "1FL98KnE_e-BigfluYAGfFgLXdXtx9WWT"
SPLIT_MANIFEST_ID = "1hd0mq6BPeJ1N0J_f7F_HOXsUnwmxHeVZ"
PRIOR_FOUR_MANIFEST_ID = "1zjRgf_bQsxoBLLzIfqF41ywsVJChZD8q"
EXTERIOR_MANIFEST_ID = "1YUh7lyn5q0Wn2EROdv83P24W59JEkbpz"
OUTPUT_NAME = "independent_20class_review_2026-10-16"
OUT = Path("/content/virasatai_20class_review")
OUT.mkdir(exist_ok=True)
MAX_PER_CLASS = 8

# Two categories of cave photographs remain one approved Ajanta/Ellora class.
QUERIES = {
    "ajanta_ellora_caves": ["Ajanta Caves Maharashtra", "Ellora Caves Maharashtra"],
    "charminar": ["Charminar Hyderabad"],
    "gateway_of_india": ["Gateway of India Mumbai"],
    "golden_temple": ["Golden Temple Amritsar Harmandir Sahib"],
    "hampi_monuments": ["Hampi Virupaksha Temple", "Hampi Vittala Temple"],
    "khajuraho_monuments": ["Khajuraho temples"],
    "konark_sun_temple": ["Konark Sun Temple"],
    "mahabalipuram": ["Mahabalipuram Shore Temple", "Mahabalipuram Five Rathas"],
    "meenakshi_temple": ["Meenakshi Amman Temple Madurai"],
    "mehrangarh_fort": ["Mehrangarh Fort Jodhpur"],
    "mysore_palace": ["Mysore Palace"],
    "qutub_minar": ["Qutub Minar Delhi"],
    "red_fort": ["Red Fort Delhi Lal Qila"],
    "sanchi_stupa": ["Sanchi Stupa Madhya Pradesh"],
    "taj_mahal": ["Taj Mahal Agra"],
    "victoria_memorial": ["Victoria Memorial Kolkata"],
}
assert len(QUERIES) == 16


def children(parent):
    files, token = [], None
    while True:
        response = drive20.files().list(q=f"'{parent}' in parents and trashed = false",
                                        fields="nextPageToken,files(id,name,mimeType)",
                                        pageSize=1000, pageToken=token).execute()
        files += response.get("files", [])
        token = response.get("nextPageToken")
        if not token:
            return files


existing = {f["name"]: f for f in children(ROOT_ID)}
if OUTPUT_NAME in existing:
    output_id = existing[OUTPUT_NAME]["id"]
else:
    output_id = drive20.files().create(body={"name": OUTPUT_NAME,
                                            "mimeType": "application/vnd.google-apps.folder",
                                            "parents": [ROOT_ID]}, fields="id").execute()["id"]
saved_files = {f["name"]: f for f in children(output_id)}

split_rows = list(csv.DictReader(io.StringIO(
    drive20.files().get_media(fileId=SPLIT_MANIFEST_ID).execute().decode("utf-8"))))
old_hashes = [int(r["dhash"], 16) for r in split_rows if r.get("dhash")]
old_sha1 = {r.get("source_sha1", "").lower() for r in split_rows} - {""}
prior_four = json.loads(drive20.files().get_media(fileId=PRIOR_FOUR_MANIFEST_ID).execute())
old_sha1.update(r.get("source_sha1", "").lower() for r in prior_four)
old_titles = {r.get("title", "") for r in prior_four}
exterior = json.loads(drive20.files().get_media(fileId=EXTERIOR_MANIFEST_ID).execute())
old_sha1.update(r.get("source_sha1", "").lower() for r in exterior)
old_titles.update(r.get("title", "") for r in exterior)

session = requests.Session()
session.headers.update({"User-Agent": "VirasatAI-student-evaluation/1.0 (educational visual review)"})


def wiki(params):
    for attempt in range(5):
        response = session.get("https://commons.wikimedia.org/w/api.php",
                               params={"format": "json", **params}, timeout=35)
        if response.status_code in (429, 500, 502, 503, 504):
            time.sleep(min(60, 5 * (attempt + 1)))
            continue
        response.raise_for_status()
        return response.json()
    raise RuntimeError("Wikimedia rate limit; already-saved sheets are preserved")


def titles_for(query):
    data = wiki({"action": "query", "list": "search", "srsearch": query,
                 "srnamespace": 6, "srlimit": 60})
    return [r["title"] for r in data["query"]["search"]]


def info_for(titles):
    for start in range(0, len(titles), 25):
        data = wiki({"action": "query", "prop": "imageinfo",
                     "titles": "|".join(titles[start:start + 25]),
                     "iiprop": "url|size|sha1|extmetadata", "iiurlwidth": 800})
        for page in data["query"]["pages"].values():
            if page.get("imageinfo"):
                yield page["title"], page["imageinfo"][0]


def dhash(image):
    grey = ImageOps.grayscale(image).resize((9, 8))
    pixels = list(grey.getdata())
    value = 0
    for row in range(8):
        for col in range(8):
            value = (value << 1) | (pixels[row * 9 + col] > pixels[row * 9 + col + 1])
    return value


all_rows = []
review_hashes = []
for label, queries in QUERIES.items():
    sheet_name = f"{label}_candidate_sheet.jpg"
    json_name = f"{label}_candidate_manifest.json"
    if sheet_name in saved_files and json_name in saved_files:
        rows = json.loads(drive20.files().get_media(fileId=saved_files[json_name]["id"]).execute())
        all_rows += rows
        review_hashes += [int(r["preview_dhash"], 16) for r in rows]
        print("RESUMED", label, len(rows), flush=True)
        continue
    pool = []
    for query in queries:
        pool.extend(titles_for(query))
        time.sleep(1)
    pool = list(dict.fromkeys(pool))
    random.Random(20261016 + list(QUERIES).index(label)).shuffle(pool)
    found = []
    for title, info in info_for(pool[:80]):
        if len(found) >= MAX_PER_CLASS:
            break
        if title in old_titles or info.get("sha1", "").lower() in old_sha1:
            continue
        license_name = info.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "")
        if not license_name.startswith(("CC BY", "CC0", "PD", "Public domain")):
            continue
        if min(info.get("width", 0), info.get("height", 0)) < 900:
            continue
        if any(word in title.lower() for word in
               ("map", "painting", "sketch", "drawing", "diagram", "collage", "poster", "logo")):
            continue
        if not info.get("thumburl"):
            continue
        try:
            response = session.get(info["thumburl"], timeout=40)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content)).convert("RGB")
            value = dhash(image)
            if any((value ^ old).bit_count() <= 6 for old in old_hashes + review_hashes):
                continue
            path = OUT / (label + "_" + hashlib.sha1(title.encode()).hexdigest()[:12] + ".jpg")
            image.save(path, quality=88)
            row = {"label": label, "index": len(found), "title": title,
                   "commons_page": "https://commons.wikimedia.org/wiki/" + title.replace(" ", "_"),
                   "license": license_name, "source_sha1": info.get("sha1", ""),
                   "original_url": info.get("url"), "source_width": info["width"],
                   "source_height": info["height"], "preview_dhash": f"{value:016x}",
                   "preview_file": path.name, "review_status": "needs_visual_review"}
            found.append(row)
            review_hashes.append(value)
            time.sleep(0.5)
        except (requests.RequestException, OSError) as exc:
            print("SKIP", label, title[:45], str(exc)[:90], flush=True)
    canvas = Image.new("RGB", (4 * 220, 2 * 220), "white")
    pen = ImageDraw.Draw(canvas)
    for row in found:
        pos = row["index"]
        x, y = (pos % 4) * 220, (pos // 4) * 220
        with Image.open(OUT / row["preview_file"]) as image:
            canvas.paste(ImageOps.fit(image, (210, 180)), (x, y))
        pen.text((x + 3, y + 183), f"{pos}: {row['title'][5:32]}", fill="black")
    sheet = OUT / sheet_name
    canvas.save(sheet, quality=88)
    manifest = OUT / json_name
    manifest.write_text(json.dumps(found, indent=2), encoding="utf-8")
    for path in (sheet, manifest):
        drive20.files().create(body={"name": path.name, "parents": [output_id]},
                               media_body=MediaFileUpload(str(path), resumable=True),
                               fields="id").execute()
    all_rows += found
    print("REVIEW_SHEET", label, len(found), flush=True)

print("20CLASS_REVIEW_READY", json.dumps({"folder_id": output_id,
    "new_classes": len(QUERIES), "candidate_count": len(all_rows),
    "per_class": dict(Counter(r["label"] for r in all_rows)),
    "status": "visual_review_required_before_scoring"}), flush=True)
