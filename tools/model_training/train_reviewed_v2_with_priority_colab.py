"""Run in the owner's Google Colab account after uploading the reviewed manifest.

Candidate-only MobileNetV2 experiment. The reviewed split is source-grouped
for visually checked dHash<=8 pairs, but is not an independent phone test.
All pre-generated aug_ files are excluded because most parent IDs are unknown.
"""

import csv
import hashlib
import io
import json
import random
import time
from collections import Counter
from pathlib import Path

import google.auth
import numpy as np
import tensorflow as tf
from google.colab import auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from PIL import Image, ImageOps
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

ACCOUNT = "manuagarwal885@gmail.com"
MANIFEST_ID = "19BLdHeZLeq4YxLvB8OWLjwRZs_mgEWSv"
OUTPUT_PARENT_ID = "1FL98KnE_e-BigfluYAGfFgLXdXtx9WWT"
ROOT = Path("/content/virasatai_reviewed_v2")
SIDE = 224
SEED = 42
BATCH = 32

tf.keras.utils.set_random_seed(SEED)
auth.authenticate_user()
creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/drive"])
drive = build("drive", "v3", credentials=creds, cache_discovery=False)
who = drive.about().get(fields="user(emailAddress)").execute()["user"]["emailAddress"].lower()
assert who == ACCOUNT, f"Wrong Google account: {who}"


def fetch(file_id):
    for attempt in range(6):
        try:
            return drive.files().get_media(fileId=file_id).execute()
        except Exception:
            if attempt == 5:
                raise
            time.sleep(min(30, 2 ** attempt + random.random()))


all_rows = list(csv.DictReader(io.StringIO(fetch(MANIFEST_ID).decode("utf-8-sig"))))
assert len(all_rows) == 3141
assert all(r["split"] in ("train", "val", "test") for r in all_rows)
assert all(r["file_id"] and r["sha256"] and r["source_group"] for r in all_rows)
labels = sorted({r["label"] for r in all_rows})
assert len(labels) == 20
rows = [r for r in all_rows if not r["raw_name"].lower().startswith("aug_")]
original_photo_count = len(rows)
assert len(rows) == 3074
groups = {}
for r in rows:
    key = (r["label"], r["source_group"])
    assert key not in groups or groups[key] == r["split"], "Source group crosses splits"
    groups[key] = r["split"]
counts = Counter((r["label"], r["split"]) for r in rows)
assert all(counts[label, split] >= 5 for label in labels for split in ("train", "val", "test"))
print("DATASET", {"photos": len(rows), "excluded_augmented": len(all_rows)-original_photo_count,
                  "split_counts": dict(Counter(r["split"] for r in rows))}, flush=True)


def restore(row):
    path = ROOT / "images" / row["split"] / row["label"] / (row["sha256"] + ".jpg")
    if path.exists():
        return
    data = fetch(row["file_id"])
    if hashlib.sha256(data).hexdigest() != row["sha256"]:
        raise ValueError("Drive source changed: " + row["file_id"])
    with Image.open(io.BytesIO(data)) as source:
        photo = ImageOps.pad(ImageOps.exif_transpose(source).convert("RGB"),
                             (SIDE, SIDE), method=Image.Resampling.LANCZOS,
                             color=(127, 127, 127))
    path.parent.mkdir(parents=True, exist_ok=True)
    photo.save(path, quality=92)


for n, row in enumerate(rows, 1):
    restore(row)
    if n % 200 == 0 or n == len(rows):
        print("RESTORED", n, len(rows), flush=True)


# Reviewed source-sheet indices are only candidate selections. This block
# rechecks the Commons identity, license, source hash and near-duplicates
# before accepting images into TRAIN ONLY.
import requests

PRIORITY_FOLDER_ID = "1tYtgfjwCfcbz1ZtQgZRmlnJRyoQHU8zU"
SHORTLIST_ID = "1QROT8lAPHnRXO2CACKx73Gs-TlzrK1If"
CANDIDATE_MANIFEST_IDS = {
    "badami_cave_temples": "1-XBfSOePnPEoo2nS9gZ7F_wx7m8EUfG8",
    "sanchi_stupa": "1IZIO9uQmfRsN1bKudFE3DHGK5KpUfax6",
    "mysore_palace": "1X2-oWa3SHLMkr9og4MgcvaY7szDTX4f9",
    "red_fort": "1vUBJA9Gc0Q38Q-t8HsFio7lvH-sDrnDl",
    "jaisalmer_fort": "1sRaU9KQPLGx8XcaEVuKRJlmOFfFfhdwL",
    "hampi_monuments": "1Tg8U90coHMxFxjt-OS21eOOPM9mf0dDc",
    "konark_sun_temple": "19Ie3IjSF2T4rfFMixC0aOd_dYHjtPLhJ",
}

shortlist = list(csv.DictReader(io.StringIO(fetch(SHORTLIST_ID).decode("utf-8-sig"))))
assert len(shortlist) == 60 and all(r["decision"] == "shortlist" for r in shortlist)
candidate_manifests = {
    label: {str(row["index"]): row for row in json.loads(fetch(file_id))}
    for label, file_id in CANDIDATE_MANIFEST_IDS.items()
}
session = requests.Session()
session.headers.update({"User-Agent": "VirasatAI-student-image-review/1.0 (educational project)"})


def candidate_hash(photo):
    gray = ImageOps.grayscale(photo).resize((9, 8))
    pixels = list(gray.getdata())
    result = 0
    for yy in range(8):
        for xx in range(8):
            result = (result << 1) | (pixels[yy * 9 + xx] > pixels[yy * 9 + xx + 1])
    return result


def get_commons_image(title):
    for attempt in range(6):
        try:
            res = session.get("https://commons.wikimedia.org/w/api.php", params={
                "action": "query", "format": "json", "prop": "imageinfo",
                "titles": title, "iiprop": "url|sha1|size|extmetadata",
                "iiurlwidth": 900}, timeout=45)
            if res.status_code in (429, 500, 502, 503, 504):
                time.sleep(min(60, 5 * (attempt + 1)))
                continue
            res.raise_for_status()
            page = next(iter(res.json()["query"]["pages"].values()))
            return page["imageinfo"][0]
        except (requests.RequestException, KeyError, StopIteration):
            if attempt == 5:
                raise
            time.sleep(min(60, 3 * (attempt + 1)))
    raise RuntimeError("Commons image metadata unavailable")


existing_hashes = [int(r["dhash"], 16) for r in all_rows]
accepted_hashes = []
accepted = []
rejected = []
for item in shortlist:
    label = item["label"]
    source = candidate_manifests[label][item["index"]]
    try:
        assert source["label"] == label
        assert source["license"].startswith(("CC BY", "CC0", "PD", "Public domain"))
        info = get_commons_image(source["title"])
        assert info["sha1"] == source["source_sha1"], "Commons source changed"
        assert min(info["width"], info["height"]) >= 900
        current_license = info.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "")
        assert current_license.startswith(("CC BY", "CC0", "PD", "Public domain"))
        preview_url = info.get("thumburl") or info.get("url")
        response = session.get(preview_url, timeout=60)
        response.raise_for_status()
        with Image.open(io.BytesIO(response.content)) as opened:
            photo = ImageOps.exif_transpose(opened).convert("RGB")
        visual_hash = candidate_hash(photo)
        assert all((visual_hash ^ old).bit_count() > 8 for old in existing_hashes), "near old dataset photo"
        assert all((visual_hash ^ old).bit_count() > 8 for old in accepted_hashes), "near another candidate"
        normalized = ImageOps.pad(photo, (SIDE, SIDE), method=Image.Resampling.LANCZOS,
                                  color=(127, 127, 127))
        dest = ROOT / "images" / "train" / label / ("priority_" + info["sha1"] + ".jpg")
        dest.parent.mkdir(parents=True, exist_ok=True)
        normalized.save(dest, quality=92)
        accepted_hashes.append(visual_hash)
        counts[label, "train"] += 1
        rows.append({"label": label, "split": "train"})
        accepted.append({**source, "reason": item["reason"], "train_path": str(dest),
                         "current_license": current_license})
    except Exception as error:
        rejected.append({"label": label, "index": source["index"],
                         "title": source["title"], "reason": str(error)})
    if (len(accepted) + len(rejected)) % 10 == 0:
        print("PRIORITY_RECHECK", len(accepted), "accepted", len(rejected), "rejected", flush=True)

assert len(accepted) >= 20, "Too few verified additions; inspect rejection list before training"
priority_audit = {"shortlisted": len(shortlist), "accepted": accepted, "rejected": rejected,
                  "warning": "Source-title review and dHash screening are imperfect; do not treat as an independent test."}
audit_path = ROOT / "priority_candidate_audit.json"
audit_path.write_text(json.dumps(priority_audit, indent=2), encoding="utf-8")
print("PRIORITY_DATASET_READY", {"shortlisted": len(shortlist),
                                 "accepted": len(accepted), "rejected": len(rejected),
                                 "train_total": sum(counts[label, "train"] for label in labels)}, flush=True)


def dataset(split, shuffle):
    ds = tf.keras.utils.image_dataset_from_directory(
        ROOT / "images" / split, class_names=labels, image_size=(SIDE, SIDE),
        batch_size=BATCH, label_mode="int", shuffle=shuffle, seed=SEED)
    return ds.prefetch(tf.data.AUTOTUNE)


train = dataset("train", True)
val = dataset("val", False)
test = dataset("test", False)
augmentation = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomRotation(0.04, fill_mode="reflect"),
    tf.keras.layers.RandomTranslation(0.08, 0.08, fill_mode="reflect"),
    tf.keras.layers.RandomZoom((-0.16, 0.08), fill_mode="reflect"),
    tf.keras.layers.RandomContrast(0.12),
])
backbone = tf.keras.applications.MobileNetV2(
    input_shape=(SIDE, SIDE, 3), include_top=False, weights="imagenet")
backbone.trainable = False
inputs = tf.keras.Input((SIDE, SIDE, 3))
x = augmentation(inputs)
x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
x = backbone(x, training=False)
x = tf.keras.layers.GlobalAveragePooling2D()(x)
x = tf.keras.layers.Dropout(0.3)(x)
outputs = tf.keras.layers.Dense(20, activation="softmax")(x)
model = tf.keras.Model(inputs, outputs)

train_counts = np.array([counts[label, "train"] for label in labels], dtype=np.float32)
class_weight = {i: float(train_counts.sum() / (20 * count))
                for i, count in enumerate(train_counts)}
out = ROOT / "priority_candidate"
out.mkdir(parents=True, exist_ok=True)
checkpoint = out / "best.keras"


def callbacks(initial_value_threshold=None):
    return [tf.keras.callbacks.ModelCheckpoint(str(checkpoint), monitor="val_loss",
                                               save_best_only=True,
                                               initial_value_threshold=initial_value_threshold),
            tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=4,
                                             restore_best_weights=True),
            tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5,
                                                 patience=2, min_lr=1e-7)]


model.compile(optimizer=tf.keras.optimizers.AdamW(learning_rate=3e-4, weight_decay=1e-4),
              loss="sparse_categorical_crossentropy", metrics=["accuracy"])
frozen = model.fit(train, validation_data=val, epochs=15, callbacks=callbacks(),
                   class_weight=class_weight, verbose=2)
model = tf.keras.models.load_model(checkpoint)
frozen_val_loss = float(model.evaluate(val, verbose=0)[0])
backbone = next(layer for layer in model.layers if isinstance(layer, tf.keras.Model))
backbone.trainable = True
for layer in backbone.layers:
    if isinstance(layer, tf.keras.layers.BatchNormalization):
        layer.trainable = False
model.compile(optimizer=tf.keras.optimizers.AdamW(learning_rate=5e-6, weight_decay=1e-5),
              loss="sparse_categorical_crossentropy", metrics=["accuracy"])
fine = model.fit(train, validation_data=val, epochs=15,
                 callbacks=callbacks(initial_value_threshold=frozen_val_loss),
                 class_weight=class_weight, verbose=2)
model = tf.keras.models.load_model(checkpoint)

truth = np.concatenate([y.numpy() for _, y in test])
prob = model.predict(test, verbose=0)
pred = prob.argmax(axis=1)
report = {"status": "candidate_only_not_independent_phone_test", "classes": labels,
          "photos": len(rows), "priority_added": len(accepted), "excluded_augmented": len(all_rows)-original_photo_count,
          "frozen_epochs": len(frozen.history["loss"]),
          "fine_tune_epochs": len(fine.history["loss"]),
          "candidate_test_accuracy": float(accuracy_score(truth, pred)),
          "per_class": classification_report(truth, pred, target_names=labels,
                                               output_dict=True, zero_division=0),
          "confusion_matrix": confusion_matrix(truth, pred).tolist(),
          "warning": "Reviewed split is candidate-only. Independent real phone photos and remaining source provenance are required before a 90% claim or app replacement."}
(out / "metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
(out / "labels.txt").write_text("\n".join(labels) + "\n", encoding="utf-8")
model.save(out / "monument_model.keras")
print("PRIORITY_V2_RESULT", json.dumps(report), flush=True)

folder = drive.files().create(body={"name": "reviewed_v2_priority_candidate_2026-10-22",
                                    "mimeType": "application/vnd.google-apps.folder",
                                    "parents": [OUTPUT_PARENT_ID]}, fields="id,webViewLink").execute()
for name in ("metrics.json", "labels.txt", "monument_model.keras", "priority_candidate_audit.json"):
    drive.files().create(body={"name": name, "parents": [folder["id"]]},
                         media_body=MediaFileUpload(str(audit_path if name == "priority_candidate_audit.json" else out / name), resumable=True),
                         fields="id").execute()
print("PRIORITY_CANDIDATE_SAVED", folder, flush=True)
