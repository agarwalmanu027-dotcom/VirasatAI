"""First *experimental* 20-class VirasatAI model run in Google Colab.

No package install or pretrained-weight download. Reads only main monument
image folders; nearby photos and gallery content are excluded. It preserves
the private raw copy and writes candidate model artifacts to a separate folder.
Visual label review and unseen phone-photo testing are still required.
"""

import csv
import hashlib
import io
import json
import random
import threading
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import google.auth
from google.colab import auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from PIL import Image, ImageOps, UnidentifiedImageError

ROOT_ID = "1oIFKrlUqwO5tMoHbrtNesmJ8ix5FcNFE"
OUTPUT_PARENT_ID = "1FL98KnE_e-BigfluYAGfFgLXdXtx9WWT"
EXPECTED_ACCOUNT = "manuagarwal885@gmail.com"
MAX_PER_CLASS = 180  # fast first experiment; not a final 300-photo target
MIN_SIDE = 300
IMAGE_SIDE = 160
SEED = 42
WORKERS = 10
LOCAL = Path("/content/virasatai_first_model")
IMAGE_EXT = (".jpg", ".jpeg", ".png", ".webp")
FOLDER_MIME = "application/vnd.google-apps.folder"

auth.authenticate_user()
credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/drive"])
thread_local = threading.local()


def api():
    if not hasattr(thread_local, "service"):
        thread_local.service = build("drive", "v3", credentials=credentials,
                                     cache_discovery=False)
    return thread_local.service


who = api().about().get(fields="user(emailAddress)").execute()["user"]["emailAddress"]
if who.lower() != EXPECTED_ACCOUNT:
    raise RuntimeError(f"Wrong Drive account: {who}")


def children(parent_id):
    items, token = [], None
    while True:
        response = api().files().list(
            q=f"'{parent_id}' in parents and trashed = false",
            pageSize=1000, pageToken=token,
            fields="nextPageToken,files(id,name,mimeType,size,md5Checksum)").execute()
        items.extend(response.get("files", []))
        token = response.get("nextPageToken")
        if not token:
            return items


classes = {}
for monument in children(ROOT_ID):
    if monument["mimeType"] != FOLDER_MIME:
        continue
    image_folders = [item for item in children(monument["id"])
                     if item["mimeType"] == FOLDER_MIME and item["name"] == "images"]
    if len(image_folders) != 1:
        raise RuntimeError(f"Missing/ambiguous main images folder: {monument['name']}")
    photos = [item for item in children(image_folders[0]["id"])
              if item["mimeType"].startswith("image/") and
              item["name"].lower().endswith(IMAGE_EXT)]
    classes[monument["name"]] = photos
print("Main classes and raw counts:", json.dumps({k: len(v) for k, v in sorted(classes.items())}))
if len(classes) != 20 or any(len(files) < 20 for files in classes.values()):
    raise RuntimeError("Need all 20 main classes with at least 20 photos each")


def dhash(image):
    grey = ImageOps.grayscale(image).resize((9, 8))
    pixels = list(grey.getdata())
    value = 0
    for row in range(8):
        for col in range(8):
            value = (value << 1) | (pixels[row * 9 + col] > pixels[row * 9 + col + 1])
    return value


def fetch(label, item):
    for attempt in range(4):
        try:
            data = api().files().get_media(fileId=item["id"]).execute()
            with Image.open(io.BytesIO(data)) as source:
                source.load()
                if min(source.size) < MIN_SIDE:
                    return None, (label, item["name"], "too_small")
                image = ImageOps.exif_transpose(source).convert("RGB")
                visual_hash = dhash(image)
                image = ImageOps.fit(image, (IMAGE_SIDE, IMAGE_SIDE), method=Image.Resampling.LANCZOS)
                buffer = io.BytesIO()
                image.save(buffer, format="JPEG", quality=88)
                return (label, item["id"], item["name"], hashlib.sha256(data).hexdigest(),
                        visual_hash, buffer.getvalue()), None
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            return None, (label, item["name"], f"bad_image:{exc}")
        except Exception as exc:
            if attempt == 3:
                return None, (label, item["name"], f"download_error:{exc}")
    return None, (label, item["name"], "unknown")


rng = random.Random(SEED)
tasks = []
for label, files in sorted(classes.items()):
    ordered = sorted(files, key=lambda item: item["name"])
    rng.shuffle(ordered)
    tasks.extend((label, item) for item in ordered[:min(len(ordered), MAX_PER_CLASS + 25)])
print("Checking main photos:", len(tasks), flush=True)
accepted, rejected = [], []
with ThreadPoolExecutor(max_workers=WORKERS) as pool:
    futures = {pool.submit(fetch, label, item): (label, item["name"]) for label, item in tasks}
    for index, future in enumerate(as_completed(futures), 1):
        photo, reason = future.result()
        if photo:
            accepted.append(photo)
        if reason:
            rejected.append(reason)
        if index % 200 == 0 or index == len(tasks):
            print(f"Checked {index}/{len(tasks)}, readable {len(accepted)}, rejected {len(rejected)}", flush=True)

seen_exact, seen_visual = {}, defaultdict(list)
selected = defaultdict(list)
for photo in sorted(accepted, key=lambda p: (p[0], p[2])):
    label, file_id, name, sha, perceptual, jpeg = photo
    if sha in seen_exact:
        rejected.append((label, name, "exact_duplicate_of:" + seen_exact[sha]))
        continue
    if any((perceptual ^ prior).bit_count() <= 2 for prior in seen_visual[label]):
        rejected.append((label, name, "near_duplicate"))
        continue
    if len(selected[label]) >= MAX_PER_CLASS:
        continue
    seen_exact[sha] = label + "/" + name
    seen_visual[label].append(perceptual)
    selected[label].append(photo)

counts = {label: len(selected[label]) for label in sorted(classes)}
print("Filtered class counts:", json.dumps(counts), flush=True)
if any(n < 20 for n in counts.values()):
    raise RuntimeError("After filtering, at least one class has fewer than 20 usable images")

prepared = LOCAL / "prepared_monuments"
if prepared.exists() and any(prepared.rglob("*.jpg")):
    raise RuntimeError("Prepared output already exists; refusing to mix runs")
manifest = []
for label in sorted(selected):
    photos = selected[label][:]
    rng.shuffle(photos)
    n = len(photos)
    test_n = max(3, round(n * .15))
    val_n = max(3, round(n * .15))
    for index, photo in enumerate(photos):
        _, file_id, name, sha, perceptual, jpeg = photo
        split = "test" if index < test_n else "val" if index < test_n + val_n else "train"
        target = prepared / split / label / (sha[:20] + ".jpg")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(jpeg)
        manifest.append({"label": label, "split": split, "file_id": file_id,
                         "raw_name": name, "sha256": sha, "dhash": hex(perceptual)})
(prepared / "labels.txt").write_text("\n".join(sorted(selected)) + "\n", encoding="utf-8")
with (prepared / "manifest.csv").open("w", newline="", encoding="utf-8") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(manifest[0]))
    writer.writeheader()
    writer.writerows(manifest)
audit = {"status": "candidate_unreviewed", "raw_counts": {k: len(v) for k, v in classes.items()},
         "selected_counts": counts, "rejected_count": len(rejected), "rejected": rejected,
         "notes": "Main monuments only; no nearby images. Automated filtering does not verify place identity."}
(prepared / "audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
print("PREPARATION COMPLETE", len(manifest), "candidate images", flush=True)

import tensorflow as tf
tf.keras.utils.set_random_seed(SEED)
labels = sorted(selected)
def load(split, shuffle):
    return tf.keras.utils.image_dataset_from_directory(
        prepared / split, class_names=labels, image_size=(IMAGE_SIDE, IMAGE_SIDE),
        batch_size=32, shuffle=shuffle, seed=SEED).prefetch(tf.data.AUTOTUNE)
train, val, test = load("train", True), load("val", False), load("test", False)
model = tf.keras.Sequential([
    tf.keras.layers.Input((IMAGE_SIDE, IMAGE_SIDE, 3)),
    tf.keras.layers.Rescaling(1 / 255),
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomRotation(.04),
    tf.keras.layers.Conv2D(32, 3, activation="relu"), tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Conv2D(64, 3, activation="relu"), tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Conv2D(128, 3, activation="relu"), tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Conv2D(192, 3, activation="relu"), tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dropout(.3), tf.keras.layers.Dense(20, activation="softmax")])
model.compile(optimizer=tf.keras.optimizers.Adam(.001),
              loss="sparse_categorical_crossentropy", metrics=["accuracy"])
history = model.fit(train, validation_data=val, epochs=12, verbose=2,
                    callbacks=[tf.keras.callbacks.EarlyStopping(
                        monitor="val_loss", patience=3, restore_best_weights=True)])
loss, accuracy = model.evaluate(test, verbose=0)
output = LOCAL / "candidate_model"
output.mkdir(parents=True, exist_ok=True)
model.save(output / "monument_model.keras")
(output / "monument_model.tflite").write_bytes(tf.lite.TFLiteConverter.from_keras_model(model).convert())
(output / "labels.txt").write_text("\n".join(labels) + "\n", encoding="utf-8")
metrics = {"status": "candidate_only", "test_accuracy": float(accuracy), "test_loss": float(loss),
           "epochs": len(history.history["loss"]), "class_counts": counts,
           "warning": "Labels need visual review and unseen phone-photo testing before app integration."}
(output / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print("EXPERIMENT COMPLETE", json.dumps(metrics), flush=True)

dest = api().files().create(body={"name": "first_model_experiment_2026-10-15",
                                  "mimeType": FOLDER_MIME, "parents": [OUTPUT_PARENT_ID]},
                            fields="id,webViewLink").execute()
for path in [output / "monument_model.keras", output / "monument_model.tflite",
             output / "labels.txt", output / "metrics.json", prepared / "manifest.csv",
             prepared / "audit.json"]:
    api().files().create(body={"name": path.name, "parents": [dest["id"]]},
                         media_body=MediaFileUpload(str(path), resumable=True),
                         fields="id,name").execute()
print("SAVED MODEL TO DRIVE", dest["id"], flush=True)
