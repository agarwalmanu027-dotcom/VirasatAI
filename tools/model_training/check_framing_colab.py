"""Standalone Colab diagnostic for the fixed 470-photo validation split."""

import csv
import hashlib
import io
from collections import defaultdict

import numpy as np
import tensorflow as tf
import google.auth
from google.colab import auth
from googleapiclient.discovery import build
from PIL import Image, ImageOps

auth.authenticate_user()
credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/drive.readonly"])
service = build("drive", "v3", credentials=credentials, cache_discovery=False)
email = service.about().get(fields="user(emailAddress)").execute()["user"]["emailAddress"].lower()
assert email == "manuagarwal885@gmail.com", f"Wrong Google account: {email}"

def fetch(file_id):
    return service.files().get_media(fileId=file_id).execute()

manifest = list(csv.DictReader(io.StringIO(fetch("1hd0mq6BPeJ1N0J_f7F_HOXsUnwmxHeVZ").decode())))
labels = fetch("1_z0LWgDroeVRHrm2bAz5IvrkZEWESW6-").decode().splitlines()
model_path = "/content/virasatai_baseline_for_framing.keras"
with open(model_path, "wb") as stream:
    stream.write(fetch("1EL2Rv78lhgnDP-74AH5i8G51Pt-nO0Y1"))
baseline = tf.keras.models.load_model(model_path)

FOCUS = {
    "badami_cave_temples", "city_palace_udaipur",
    "jaisalmer_fort", "amer_fort",
}
rows = [row for row in manifest if row["split"] == "val"]
assert len(rows) == 470, f"Unexpected validation size: {len(rows)}"
assert len(labels) == 20 and baseline.input_shape == (None, 160, 160, 3)

def image_array(image):
    return np.asarray(image, dtype=np.float32)

variants = defaultdict(list)
targets = []
for number, row in enumerate(rows, 1):
    raw = fetch(row["file_id"])
    if hashlib.sha256(raw).hexdigest() != row["sha256"]:
        raise ValueError("Raw file changed: " + row["file_id"])
    with Image.open(io.BytesIO(raw)) as source:
        oriented = ImageOps.exif_transpose(source).convert("RGB")
        centre = ImageOps.fit(oriented, (160, 160), method=Image.Resampling.LANCZOS)
        full = ImageOps.pad(oriented, (160, 160), method=Image.Resampling.LANCZOS,
                            color=(128, 128, 128))
        stretch = oriented.resize((160, 160), Image.Resampling.LANCZOS)
    variants["centre_crop"].append(image_array(centre))
    variants["whole_image_pad"].append(image_array(full))
    variants["whole_image_stretch"].append(image_array(stretch))
    targets.append(labels.index(row["label"]))
    if number % 100 == 0 or number == len(rows):
        print("FRAMING_PROGRESS", number, len(rows), flush=True)

targets = np.asarray(targets)
predictions = {}
for name, images in variants.items():
    probability = baseline.predict(np.stack(images), batch_size=32, verbose=0)
    predictions[name] = probability.argmax(axis=1)

for name, predicted in predictions.items():
    print("FRAMING_RESULT", name,
          f"overall={(predicted == targets).mean():.2%}",
          "focus=" + ", ".join(
              f"{label}:{(predicted[targets == labels.index(label)] == labels.index(label)).mean():.1%}"
              for label in sorted(FOCUS)), flush=True)

centre_ok = predictions["centre_crop"] == targets
for name in ("whole_image_pad", "whole_image_stretch"):
    other_ok = predictions[name] == targets
    print("FRAMING_CHANGED", name,
          "fixed", int((~centre_ok & other_ok).sum()),
          "broken", int((centre_ok & ~other_ok).sum()), flush=True)

print("Validation diagnostic only. Keep the 470-photo test split out of this decision.")
