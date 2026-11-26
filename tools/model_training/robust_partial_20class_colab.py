"""Train a robust 20-monument candidate in Google Colab.

This run is intentionally aimed at real phone photos: partial monuments,
crowds/foreground occlusion, off-centre framing, blur and compression.  It
restores the existing fixed train/validation/test split from Drive, keeps
validation and test images out of training, evaluates both clean and hard
views, and only marks the result eligible when it beats the currently bundled
MobileNetV2 benchmark on both sets.

Run in Colab while signed in as manuagarwal885@gmail.com.  Pretrained Keras
weights are downloaded inside Colab only (already approved by the user).
"""

import csv
import hashlib
import io
import json
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import google.auth
import numpy as np
import tensorflow as tf
from google.colab import auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from PIL import Image, ImageOps

ACCOUNT = "manuagarwal885@gmail.com"
OUTPUT_PARENT_ID = "1FL98KnE_e-BigfluYAGfFgLXdXtx9WWT"
MANIFEST_ID = "1hd0mq6BPeJ1N0J_f7F_HOXsUnwmxHeVZ"
LABELS_ID = "1_z0LWgDroeVRHrm2bAz5IvrkZEWESW6-"
IMAGE_SIDE = 192
BATCH_SIZE = 32
SEED = 47
LOCAL = Path("/content/virasatai_robust_partial_20class")
PREPARED = LOCAL / "prepared"
OUTPUT = LOCAL / "output"

tf.keras.utils.set_random_seed(SEED)
LOCAL.mkdir(parents=True, exist_ok=True)
OUTPUT.mkdir(parents=True, exist_ok=True)

auth.authenticate_user()
creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/drive"])
thread_local = threading.local()


def api():
    if not hasattr(thread_local, "service"):
        thread_local.service = build(
            "drive", "v3", credentials=creds, cache_discovery=False
        )
    return thread_local.service


def fetch(file_id):
    for attempt in range(6):
        try:
            return api().files().get_media(fileId=file_id).execute()
        except Exception:
            if attempt == 5:
                raise
            time.sleep(min(30, 2**attempt + random.random()))


def children(folder_id):
    rows, token = [], None
    while True:
        page = api().files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            pageSize=1000,
            pageToken=token,
            fields="nextPageToken,files(id,name,mimeType)",
        ).execute()
        rows += page.get("files", [])
        token = page.get("nextPageToken")
        if not token:
            return rows


who = api().about().get(fields="user(emailAddress)").execute()["user"]["emailAddress"].lower()
assert who == ACCOUNT, f"Wrong Google account: {who}"
manifest = list(csv.DictReader(io.StringIO(fetch(MANIFEST_ID).decode("utf-8"))))
labels = fetch(LABELS_ID).decode("utf-8").splitlines()
assert len(manifest) == 3141 and len(labels) == 20
assert all(row["label"] in labels for row in manifest)
assert all(row["split"] in ("train", "val", "test") for row in manifest)
print("RESTORE_START", {"photos": len(manifest), "classes": len(labels)}, flush=True)


def restore(row):
    destination = PREPARED / row["split"] / row["label"] / f"{row['sha256'][:20]}.jpg"
    if destination.exists():
        return "present"
    raw = fetch(row["file_id"])
    if hashlib.sha256(raw).hexdigest() != row["sha256"]:
        raise ValueError(f"Source changed: {row['file_id']}")
    with Image.open(io.BytesIO(raw)) as opened:
        # Pad instead of centre-cropping so edge details and the complete scene
        # remain available to the augmentation pipeline.
        image = ImageOps.pad(
            ImageOps.exif_transpose(opened).convert("RGB"),
            (IMAGE_SIDE, IMAGE_SIDE),
            method=Image.Resampling.LANCZOS,
            color=(127, 127, 127),
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, quality=90)
    return "restored"


errors = []
with ThreadPoolExecutor(max_workers=12) as pool:
    jobs = {pool.submit(restore, row): row for row in manifest}
    restored = 0
    for number, job in enumerate(as_completed(jobs), 1):
        try:
            restored += job.result() == "restored"
        except Exception as exc:
            errors.append((jobs[job]["file_id"], str(exc)))
        if number % 200 == 0 or number == len(jobs):
            print("RESTORE_PROGRESS", number, len(jobs), "errors", len(errors), flush=True)
if errors:
    raise RuntimeError(f"Restore incomplete; rerun to resume: {errors[:5]}")


def load(split, shuffle):
    ds = tf.keras.utils.image_dataset_from_directory(
        PREPARED / split,
        class_names=labels,
        image_size=(IMAGE_SIDE, IMAGE_SIDE),
        batch_size=BATCH_SIZE,
        label_mode="int",
        shuffle=shuffle,
        seed=SEED,
    )
    return ds.prefetch(tf.data.AUTOTUNE)


train = load("train", True)
val = load("val", False)
test = load("test", False)


class RandomOcclusion(tf.keras.layers.Layer):
    """Cover a random foreground-like rectangle on some training images."""

    def call(self, images, training=None):
        if not training:
            return images

        def obscure(image):
            apply = tf.random.uniform(()) < 0.60

            def changed():
                height = tf.shape(image)[0]
                width = tf.shape(image)[1]
                box_h = tf.random.uniform((), height // 7, height // 2, dtype=tf.int32)
                box_w = tf.random.uniform((), width // 7, width // 2, dtype=tf.int32)
                # Bias the obstruction toward the lower half, where people and
                # vehicles commonly cover monument photographs.
                top = tf.random.uniform((), height // 3, height - box_h + 1, dtype=tf.int32)
                left = tf.random.uniform((), 0, width - box_w + 1, dtype=tf.int32)
                mask = tf.pad(
                    tf.ones((box_h, box_w, 3), image.dtype),
                    [[top, height - top - box_h], [left, width - left - box_w], [0, 0]],
                )
                fill = tf.random.uniform((1, 1, 3), 35.0, 220.0, dtype=image.dtype)
                return image * (1.0 - mask) + fill * mask

            return tf.cond(apply, changed, lambda: image)

        return tf.map_fn(obscure, images)


augment = tf.keras.Sequential(
    [
        tf.keras.layers.RandomFlip("horizontal"),
        tf.keras.layers.RandomRotation(0.06, fill_mode="reflect"),
        tf.keras.layers.RandomTranslation(0.14, 0.14, fill_mode="reflect"),
        # Includes zoomed details and wider views.
        tf.keras.layers.RandomZoom((-0.25, 0.35), (-0.25, 0.35), fill_mode="reflect"),
        tf.keras.layers.RandomContrast(0.25),
        RandomOcclusion(),
    ],
    name="phone_photo_augmentation",
)

backbone = tf.keras.applications.MobileNetV3Small(
    input_shape=(IMAGE_SIDE, IMAGE_SIDE, 3),
    include_top=False,
    weights="imagenet",
    include_preprocessing=True,
)
backbone.trainable = False
inputs = tf.keras.Input((IMAGE_SIDE, IMAGE_SIDE, 3), name="image")
x = augment(inputs)
x = backbone(x, training=False)
x = tf.keras.layers.GlobalAveragePooling2D()(x)
x = tf.keras.layers.Dropout(0.35)(x)
outputs = tf.keras.layers.Dense(20, activation="softmax", name="monument")(x)
model = tf.keras.Model(inputs, outputs)
model.compile(
    optimizer=tf.keras.optimizers.Adam(4e-4),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)

callbacks = [
    tf.keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=3, restore_best_weights=True
    ),
    tf.keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss", patience=2, factor=0.35, min_lr=1e-6
    ),
]
frozen = model.fit(train, validation_data=val, epochs=14, callbacks=callbacks, verbose=2)

backbone.trainable = True
for layer in backbone.layers[:-35]:
    layer.trainable = False
for layer in backbone.layers:
    if isinstance(layer, tf.keras.layers.BatchNormalization):
        layer.trainable = False
model.compile(
    optimizer=tf.keras.optimizers.Adam(8e-6),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)
fine = model.fit(train, validation_data=val, epochs=7, callbacks=callbacks, verbose=2)


def harden(images):
    """Deterministic difficult-view test; never used for optimization."""
    images = tf.image.resize_with_crop_or_pad(images, 154, 154)
    images = tf.image.resize(images, (IMAGE_SIDE, IMAGE_SIDE), antialias=True)
    images = tf.image.adjust_contrast(images, 0.72)
    # A fixed lower-centre obstruction makes run-to-run comparison stable.
    batch = tf.shape(images)[0]
    cover = tf.ones((batch, 48, 64, 3), images.dtype) * 105.0
    return tf.tensor_scatter_nd_update(
        images,
        indices=tf.reshape(
            tf.stack(tf.meshgrid(tf.range(batch), tf.range(128, 176), tf.range(64, 128), indexing="ij"), axis=-1),
            (-1, 3),
        ),
        updates=tf.reshape(cover, (-1, 3)),
    )


clean_loss, clean_accuracy = model.evaluate(test, verbose=0)
truth, clean_probs, hard_probs = [], [], []
for images, target in test:
    truth.append(target.numpy())
    clean_probs.append(model(images, training=False).numpy())
    hard_probs.append(model(harden(images), training=False).numpy())
truth = np.concatenate(truth)
clean_probs = np.concatenate(clean_probs)
hard_probs = np.concatenate(hard_probs)
clean_pred = clean_probs.argmax(1)
hard_pred = hard_probs.argmax(1)

per_class = []
for index, label in enumerate(labels):
    selected = truth == index
    per_class.append(
        {
            "monument": label,
            "count": int(selected.sum()),
            "clean_accuracy": float((clean_pred[selected] == truth[selected]).mean()),
            "hard_accuracy": float((hard_pred[selected] == truth[selected]).mean()),
        }
    )

hard_accuracy = float((hard_pred == truth).mean())
report = {
    "status": "candidate_only",
    "classes": 20,
    "source_photos": len(manifest),
    "clean_test_accuracy": float(clean_accuracy),
    "hard_partial_occluded_test_accuracy": hard_accuracy,
    "current_app_clean_benchmark": 0.785106,
    "eligible_for_phone_evaluation": bool(clean_accuracy >= 0.785106 and hard_accuracy >= 0.60),
    "frozen_epochs": len(frozen.history["loss"]),
    "fine_tune_epochs": len(fine.history["loss"]),
    "per_monument": per_class,
    "warning": "Final replacement still requires independent full-size and phone-photo evaluation.",
}
print("ROBUST_RESULT", json.dumps(report), flush=True)

model.save(OUTPUT / "monument_model.keras")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
(OUTPUT / "monument_model.tflite").write_bytes(converter.convert())
(OUTPUT / "labels.txt").write_text("\n".join(labels) + "\n", encoding="utf-8")
(OUTPUT / "metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

folder = api().files().create(
    body={
        "name": "robust_partial_20class_candidate_2026-10-19",
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [OUTPUT_PARENT_ID],
    },
    fields="id,webViewLink",
).execute()
for path in OUTPUT.iterdir():
    api().files().create(
        body={"name": path.name, "parents": [folder["id"]]},
        media_body=MediaFileUpload(str(path), resumable=True),
        fields="id,name",
    ).execute()
print("ROBUST_MODEL_SAVED", folder, flush=True)
