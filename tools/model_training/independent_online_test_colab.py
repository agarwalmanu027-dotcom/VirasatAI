"""Build a NEW, reviewable online-photo test set in the existing Colab session.

Run in a FRESH Colab runtime. It loads the prior source manifests from the
user's private Drive; no model training needs to be repeated. This cell only
creates candidate contact sheets and a manifest. It never adds photos to
training, changes a model, or claims accuracy before visual label review.
"""

import csv
import hashlib
import io
import json
import random
import time
from collections import defaultdict
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageOps
from googleapiclient.http import MediaFileUpload
from google.colab import auth
import google.auth
from googleapiclient.discovery import build

auth.authenticate_user()
credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/drive"])
service = build("drive", "v3", credentials=credentials, cache_discovery=False)
api = lambda: service
OUTPUT_PARENT_ID = "1FL98KnE_e-BigfluYAGfFgLXdXtx9WWT"
FIRST_MODEL_FOLDER_ID = "1XmKmAhfVU48CY-yNgBAUOlafiU5Bz-Ey"
REVIEW_MANIFEST_ID = "1ut_oVu1n9rI4_bzeQfkZ8pSaxJaRa07o"
FOLDER_MIME = "application/vnd.google-apps.folder"


def children(parent_id):
    result, token = [], None
    while True:
        response = api().files().list(
            q=f"'{parent_id}' in parents and trashed = false",
            pageSize=1000, pageToken=token,
            fields="nextPageToken,files(id,name,mimeType)"
        ).execute()
        result.extend(response.get("files", []))
        token = response.get("nextPageToken")
        if not token:
            return result


def dhash(image):
    grey = ImageOps.grayscale(image).resize((9, 8))
    pixels = list(grey.getdata())
    value = 0
    for row in range(8):
        for col in range(8):
            value = (value << 1) | (pixels[row * 9 + col] > pixels[row * 9 + col + 1])
    return value


original_files = {item["name"]: item["id"] for item in children(FIRST_MODEL_FOLDER_ID)}
labels = api().files().get_media(fileId=original_files["labels.txt"]).execute().decode().splitlines()
manifest_bytes = api().files().get_media(fileId=original_files["manifest.csv"]).execute()
candidate_rows = json.loads(api().files().get_media(fileId=REVIEW_MANIFEST_ID).execute())
source_files = {item["name"]: item["id"] for item in children(OUTPUT_PARENT_ID)}
focus_source_id = source_files.get("focus_sources_and_selection.json")
rows = json.loads(api().files().get_media(fileId=focus_source_id).execute()) if focus_source_id else []

TEST_CATEGORIES = {
    "badami_cave_temples": [
        "Category:Exterior of the Badami cave temple 1",
        "Category:Exterior of the Badami cave temple 2",
        "Category:Exterior of the Badami cave temple 3",
    ],
    "city_palace_udaipur": ["Category:City Palace, Udaipur"],
    "jaisalmer_fort": ["Category:Jaisalmer Fort"],
    "amer_fort": ["Category:Amber Fort"],
}
MAX_CANDIDATES_PER_CLASS = 12
TEST_DIR = Path("/content/virasatai_independent_test_review")
TEST_DIR.mkdir(exist_ok=True)

assert len(labels) == 20
account = api().about().get(fields="user(emailAddress)").execute()["user"]["emailAddress"]
assert account.lower() == "manuagarwal885@gmail.com", account

# Exclude every photo in the original train/validation/test splits and the
# focused additions. Also exclude every photo in the previous Commons review,
# including its external holdout. This keeps selection sources independent.
known_hashes = defaultdict(list)
with io.StringIO(manifest_bytes.decode("utf-8")) as stream:
    for row in csv.DictReader(stream):
        known_hashes[row["label"]].append(int(row["dhash"], 16))
known_titles = {r["title"] for r in candidate_rows}
known_sha1 = {r.get("sha1", "") for r in candidate_rows} - {""}
# The previous reviewed Commons titles and SHA-1 values are excluded below,
# regardless of whether they were used as training or holdout photos.

session = requests.Session()
session.headers.update({"User-Agent": "VirasatAI-student-dataset/1.0 (educational evaluation review)"})


def wiki_query(params):
    for attempt in range(5):
        response = session.get(
            "https://commons.wikimedia.org/w/api.php",
            params={"format": "json", **params}, timeout=35,
        )
        if response.status_code in (429, 503):
            time.sleep(min(45, 4 * (attempt + 1)))
            continue
        response.raise_for_status()
        return response.json()
    raise RuntimeError("Wikimedia rate limit; stop and resume later")


def file_titles(category):
    found = []
    token = None
    while len(found) < 150:
        query = {"action": "query", "list": "categorymembers",
                 "cmtitle": category, "cmtype": "file", "cmlimit": 150}
        if token:
            query["cmcontinue"] = token
        data = wiki_query(query)
        found.extend(item["title"] for item in data["query"]["categorymembers"])
        token = data.get("continue", {}).get("cmcontinue")
        if not token:
            break
    return found[:150]


def infos(titles):
    for start in range(0, len(titles), 35):
        data = wiki_query({"action": "query", "prop": "imageinfo",
                           "titles": "|".join(titles[start:start + 35]),
                           "iiprop": "url|size|sha1|extmetadata", "iiurlwidth": 500})
        for page in data["query"]["pages"].values():
            if page.get("imageinfo"):
                yield page["title"], page["imageinfo"][0]


def near_existing(value, hashes, threshold=6):
    return any((value ^ old).bit_count() <= threshold for old in hashes)


test_review_rows = []
all_old_hashes = [h for group in known_hashes.values() for h in group]
all_new_test_hashes = []
for label, categories in TEST_CATEGORIES.items():
    pool = []
    seen_titles = set()
    for category in categories:
        for title in file_titles(category):
            if title not in seen_titles and title not in known_titles:
                seen_titles.add(title)
                pool.append((title, category))
        time.sleep(1)
    random.Random(2917 + labels.index(label)).shuffle(pool)
    category_by_title = dict(pool)
    accepted = []
    for title, info in infos([item[0] for item in pool[:120]]):
        if len(accepted) >= MAX_CANDIDATES_PER_CLASS:
            break
        license_name = info.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "")
        if not license_name.startswith(("CC BY", "CC0", "PD", "Public domain")):
            continue
        if info.get("sha1") in known_sha1:
            continue
        if min(info.get("width", 0), info.get("height", 0)) < 640:
            continue
        if any(word in title.lower() for word in (
            "map", "painting", "sketch", "drawing", "diagram", "collage", "poster"
        )):
            continue
        if not info.get("thumburl"):
            continue
        try:
            response = session.get(info["thumburl"], timeout=40)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content)).convert("RGB")
            value = dhash(image)
            if near_existing(value, all_old_hashes) or near_existing(value, all_new_test_hashes):
                continue
            all_new_test_hashes.append(value)
            token = hashlib.sha1(title.encode()).hexdigest()[:12]
            preview = TEST_DIR / f"{label}_{token}.jpg"
            image.save(preview, quality=85)
            accepted.append({
                "label": label, "index": len(accepted), "title": title,
                "category": category_by_title[title],
                "page": "https://commons.wikimedia.org/wiki/" + title.replace(" ", "_"),
                "license": license_name, "source_sha1": info.get("sha1", ""),
                "preview": str(preview), "preview_dhash": f"{value:016x}",
                "width": info["width"], "height": info["height"],
                "review_status": "needs_visual_label_review",
            })
            time.sleep(0.8)
        except (requests.RequestException, OSError) as exc:
            print("SKIP", label, title, str(exc)[:90], flush=True)
    if not accepted:
        print("NO_NEW_CANDIDATES", label, flush=True)
        continue
    canvas = Image.new("RGB", (4 * 220, 3 * 220), "white")
    draw = ImageDraw.Draw(canvas)
    for item in accepted:
        x, y = (item["index"] % 4) * 220, (item["index"] // 4) * 220
        with Image.open(item["preview"]) as image:
            canvas.paste(ImageOps.fit(image, (210, 180)), (x, y))
        draw.text((x + 3, y + 183), f"{item['index']}: {item['title'][5:31]}", fill="black")
    sheet = TEST_DIR / f"{label}_independent_candidates.jpg"
    canvas.save(sheet, quality=86)
    test_review_rows.extend(accepted)
    print("REVIEW_SHEET", label, len(accepted), str(sheet), flush=True)

manifest = TEST_DIR / "independent_candidate_manifest.json"
manifest.write_text(json.dumps(test_review_rows, indent=2), encoding="utf-8")

# Upload only review artifacts to a dedicated private folder. Do not label them
# as test data until an actual person confirms every monument in the sheet.
existing = [item for item in children(OUTPUT_PARENT_ID)
            if item["mimeType"] == FOLDER_MIME
            and item["name"] == "independent_test_review_2026-10-16"]
review_folder_id = existing[0]["id"] if existing else api().files().create(
    body={"name": "independent_test_review_2026-10-16", "mimeType": FOLDER_MIME,
          "parents": [OUTPUT_PARENT_ID]}, fields="id").execute()["id"]
existing_names = {item["name"] for item in children(review_folder_id)}
for path in list(TEST_DIR.glob("*_independent_candidates.jpg")) + [manifest]:
    if path.name not in existing_names:
        api().files().create(
            body={"name": path.name, "parents": [review_folder_id]},
            media_body=MediaFileUpload(str(path), resumable=True), fields="id"
        ).execute()
print("INDEPENDENT_REVIEW_READY", json.dumps({
    "folder_id": review_folder_id,
    "candidate_counts": {label: sum(r["label"] == label for r in test_review_rows)
                         for label in TEST_CATEGORIES},
    "status": "visual_review_required_before_scoring",
}), flush=True)
