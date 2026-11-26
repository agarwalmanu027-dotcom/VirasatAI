"""Colab: add a first, traceable Badami Cave Temples photo batch to private Drive.

Uses Wikimedia Commons images only. Does not install packages. These photos are
candidate training inputs; gallery publication still needs visual/license review.
"""

import csv
import hashlib
import io
import json
import time
from collections import defaultdict

import google.auth
from google.colab import auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from PIL import Image
import requests

BADAMI_IMAGES_ID = "1tFBstE22DngU0MMPT8F8r9pi2gbV-HJf"
BADAMI_FOLDER_ID = "1D4Wf2Eyihp_VjAXPL825xJkVWSq5fx8U"
ACCOUNT = "manuagarwal885@gmail.com"
API = "https://commons.wikimedia.org/w/api.php"
CATEGORIES = {
    "exterior": "Category:Exterior of the Badami Cave Temples",
    "cave_1": "Category:Badami cave temples (cave 1)",
    "cave_2": "Category:Badami cave temples (cave 2)",
    "cave_3": "Category:Badami cave temples (cave 3)",
    "cave_4": "Category:Badami cave temples (cave 4)",
}
MAX_PER_GROUP = 12
ALLOWED_LICENSES = ("CC BY", "CC0", "PD", "Public domain")

auth.authenticate_user()
creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/drive"])
drive = build("drive", "v3", credentials=creds, cache_discovery=False)
who = drive.about().get(fields="user(emailAddress)").execute()["user"]["emailAddress"]
if who.lower() != ACCOUNT:
    raise RuntimeError(f"Wrong Drive account: {who}")
session = requests.Session()
session.headers.update({"User-Agent": "VirasatAI-student-dataset/1.0 (educational image review)"})


def commons(params):
    for attempt in range(5):
        try:
            response = session.get(API, params={"format": "json", **params}, timeout=35)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            if attempt == 4:
                raise
            time.sleep(2 ** attempt)


def category_files(category):
    result, token = [], None
    while True:
        params = {"action": "query", "list": "categorymembers", "cmtitle": category,
                  "cmtype": "file", "cmlimit": "max"}
        if token:
            params["cmcontinue"] = token
        data = commons(params)
        result.extend(item["title"] for item in data["query"]["categorymembers"])
        token = data.get("continue", {}).get("cmcontinue")
        if not token:
            return result


def info_batch(titles):
    for start in range(0, len(titles), 40):
        data = commons({"action": "query", "prop": "imageinfo", "titles": "|".join(titles[start:start+40]),
                        "iiprop": "url|size|sha1|extmetadata", "iiurlwidth": 1280})
        for page in data["query"]["pages"].values():
            if page.get("imageinfo"):
                yield page["title"], page["imageinfo"][0]


existing = set()
token = None
while True:
    data = drive.files().list(q=f"'{BADAMI_IMAGES_ID}' in parents and trashed = false",
                              fields="nextPageToken,files(name)", pageSize=1000,
                              pageToken=token).execute()
    existing.update(item["name"] for item in data.get("files", []))
    token = data.get("nextPageToken")
    if not token:
        break

selected, seen_sha = [], set()
for group, category in CATEGORIES.items():
    candidates = []
    for title, info in info_batch(category_files(category)):
        metadata = info.get("extmetadata", {})
        license_name = metadata.get("LicenseShortName", {}).get("value", "")
        if not license_name.startswith(ALLOWED_LICENSES):
            continue
        if info.get("width", 0) < 1000 or info.get("height", 0) < 640:
            continue
        if not info.get("thumburl") or info.get("sha1") in seen_sha:
            continue
        lower = title.lower()
        if any(word in lower for word in ("map", "drawing", "painting", "sketch", "panorama", "collage")):
            continue
        candidates.append((title, info, license_name))
    # Stable ordering makes repeat runs idempotent and auditable.
    for title, info, license_name in sorted(candidates, key=lambda item: item[0])[:MAX_PER_GROUP]:
        seen_sha.add(info["sha1"])
        selected.append((group, title, info, license_name))
    print(group, "eligible:", len(candidates), "selected:", min(len(candidates), MAX_PER_GROUP))

rows = []
for index, (group, title, info, license_name) in enumerate(selected, 1):
    name = "badami_commons_" + group + "_" + hashlib.sha1(title.encode()).hexdigest()[:12] + ".jpg"
    if name in existing:
        print(index, "skip existing", name)
        continue
    try:
        response = session.get(info["thumburl"], timeout=60)
        response.raise_for_status()
        photo = Image.open(io.BytesIO(response.content))
        photo.verify()
        photo = Image.open(io.BytesIO(response.content)).convert("RGB")
        if min(photo.size) < 640:
            continue
        output = io.BytesIO()
        photo.save(output, "JPEG", quality=88, optimize=True)
        output.seek(0)
        created = drive.files().create(
            body={"name": name, "parents": [BADAMI_IMAGES_ID], "description": title},
            media_body=MediaIoBaseUpload(output, mimetype="image/jpeg", resumable=False),
            fields="id,name").execute()
        rows.append({"drive_id": created["id"], "name": name, "group": group,
                     "commons_title": title, "commons_page": "https://commons.wikimedia.org/wiki/" + title.replace(" ", "_"),
                     "license": license_name, "source_sha1": info["sha1"],
                     "source_width": info["width"], "source_height": info["height"]})
        print(index, "added", name)
    except Exception as exc:
        print(index, "ERROR", title, str(exc)[:200])

if rows:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    data = io.BytesIO(buffer.getvalue().encode("utf-8"))
    drive.files().create(body={"name": "badami_commons_batch_sources.csv", "parents": [BADAMI_FOLDER_ID]},
                         media_body=MediaIoBaseUpload(data, mimetype="text/csv"), fields="id").execute()
print(json.dumps({"selected": len(selected), "added": len(rows), "existing_before": len(existing)}))
