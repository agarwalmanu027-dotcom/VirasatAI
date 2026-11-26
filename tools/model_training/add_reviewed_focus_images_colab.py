"""Add visually reviewed exterior photos; keep a separate untouched holdout.

Requires prior notebook cells including review_weak_classes_colab.py. All new
photos stay in the user's private Drive. Source raw files are not deleted.
"""

import csv
import hashlib
import io
import json
import time
from collections import defaultdict
from pathlib import Path

import requests
from PIL import Image, ImageOps
from googleapiclient.http import MediaIoBaseUpload, MediaFileUpload

# Indices refer to the numbered, visually inspected Commons contact sheets.
TRAIN_PICK = {
    "badami_cave_temples": [0, 1, 7, 9, 15, 17],
    "city_palace_udaipur": [0, 1, 2, 4, 5, 6, 11, 12],
    "jaisalmer_fort": [0, 1, 3, 6, 7, 8, 13, 15],
    "amer_fort": [0, 2, 4, 5, 6, 7, 8, 9],
}
HOLDOUT_PICK = {
    "badami_cave_temples": [3, 8, 10, 12],
    "city_palace_udaipur": [8, 10, 16, 17],
    "jaisalmer_fort": [2, 5, 10, 14, 17],
    "amer_fort": [10, 12, 14, 16],
}

account = api().about().get(fields="user(emailAddress)").execute()["user"]["emailAddress"]
if account.lower() != "manuagarwal885@gmail.com":
    raise RuntimeError("Wrong Drive account: " + account)

folder_by_label = {}
for monument in children(ROOT_ID):
    if monument["mimeType"] == FOLDER_MIME:
        image_folders = [x for x in children(monument["id"])
                         if x["mimeType"] == FOLDER_MIME and x["name"] == "images"]
        if len(image_folders) == 1:
            folder_by_label[monument["name"]] = image_folders[0]["id"]

existing_hashes = defaultdict(list)
with (prepared / "manifest.csv").open(newline="", encoding="utf-8") as stream:
    for row in csv.DictReader(stream):
        existing_hashes[row["label"]].append(int(row["dhash"], 16))

all_rows = {(r["label"], r["index"]): r for r in candidate_rows}
out_dir = Path("/content/virasatai_reviewed_focus")
out_dir.mkdir(exist_ok=True)
holdout_root = api().files().create(
    body={"name": "focus_external_holdout_2026-10-15", "mimeType": FOLDER_MIME,
          "parents": [OUTPUT_PARENT_ID]}, fields="id,webViewLink").execute()
holdout_folders = {}
for label in HOLDOUT_PICK:
    holdout_folders[label] = api().files().create(
        body={"name": label, "mimeType": FOLDER_MIME,
              "parents": [holdout_root["id"]]}, fields="id").execute()["id"]

rows = []
seen_new = defaultdict(list)
for label in TRAIN_PICK:
    existing_names = {x["name"] for x in children(folder_by_label[label])}
    requests_for_class = [("train", i) for i in TRAIN_PICK[label]] + [
        ("external_holdout", i) for i in HOLDOUT_PICK[label]]
    for role, index in requests_for_class:
        item = all_rows[(label, index)]
        name = "commons_focus_" + label + "_" + hashlib.sha1(item["title"].encode()).hexdigest()[:12] + ".jpg"
        status = "added"
        if role == "train" and name in existing_names:
            status = "already_present"
        try:
            data = commons({"action": "query", "prop": "imageinfo", "titles": item["title"],
                            "iiprop": "url|size|sha1|extmetadata", "iiurlwidth": 1280})
            page = next(iter(data["query"]["pages"].values()))
            info = page["imageinfo"][0]
            license_name = info.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "")
            if not license_name.startswith(("CC BY", "CC0", "PD", "Public domain")):
                raise ValueError("license changed or missing")
            url = info.get("thumburl") or info["url"]
            response = session.get(url, timeout=60)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content)).convert("RGB")
            if min(image.size) < 500:
                raise ValueError("downloaded image too small")
            visual_hash = dhash(image)
            # Holdout must not overlap the pre-existing model's source imagery.
            if role == "train" and any(
                (visual_hash ^ h).bit_count() <= 4
                for hashes in existing_hashes.values() for h in hashes
            ):
                status = "skip_near_existing"
            elif role == "external_holdout" and any(
                (visual_hash ^ h).bit_count() <= 6
                for hashes in existing_hashes.values() for h in hashes
            ):
                status = "skip_near_existing"
            elif any((visual_hash ^ h).bit_count() <= 4 for h in seen_new[label]):
                status = "skip_near_new"
            if status == "added":
                seen_new[label].append(visual_hash)
                buf = io.BytesIO()
                image.save(buf, format="JPEG", quality=88, optimize=True)
                buf.seek(0)
                parent = folder_by_label[label] if role == "train" else holdout_folders[label]
                created = api().files().create(
                    body={"name": name, "parents": [parent],
                          "description": item["page"] + " | " + license_name},
                    media_body=MediaIoBaseUpload(buf, mimetype="image/jpeg", resumable=False),
                    fields="id,name").execute()
                item["new_drive_id"] = created["id"]
                if role == "train":
                    existing_names.add(name)
                status = "added"
            rows.append({"label": label, "role": role, "candidate_index": index,
                         "name": name, "status": status, "source_page": item["page"],
                         "source_title": item["title"], "license": license_name,
                         "source_sha1": info.get("sha1", ""),
                         "source_width": info.get("width"), "source_height": info.get("height"),
                         "drive_id": item.get("new_drive_id", "")})
            print(label, role, index, status, flush=True)
        except Exception as exc:
            rows.append({"label": label, "role": role, "candidate_index": index,
                         "name": name, "status": "error:" + str(exc)[:150],
                         "source_page": item["page"], "source_title": item["title"]})
            print(label, role, index, "ERROR", str(exc)[:150], flush=True)
        time.sleep(0.5)

record = out_dir / "focus_sources_and_selection.json"
record.write_text(json.dumps(rows, indent=2), encoding="utf-8")
api().files().create(body={"name": record.name, "parents": [OUTPUT_PARENT_ID]},
                     media_body=MediaFileUpload(str(record), mimetype="application/json"),
                     fields="id,name").execute()
print("FOCUS_ADDITION_COMPLETE", json.dumps({
    "added_train": sum(r["status"] == "added" and r["role"] == "train" for r in rows),
    "added_holdout": sum(r["status"] == "added" and r["role"] == "external_holdout" for r in rows),
    "skipped_or_error": sum(r["status"] != "added" for r in rows),
    "holdout_folder": holdout_root["id"]
}), flush=True)
