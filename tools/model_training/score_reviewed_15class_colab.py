"""Exploratory Colab-only score for visually reviewed Commons images.

This set covers 15 newly reviewed monument groups. Red Fort had no usable
candidate in this batch. Four earlier groups are reported separately; this is
not a complete 20-class or phone-camera acceptance test.
"""

import io
import json
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import requests
import tensorflow as tf
from PIL import Image, ImageOps
from google.colab import auth
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

auth.authenticate_user()
creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/drive"])
drive = build("drive", "v3", credentials=creds, cache_discovery=False)
assert drive.about().get(fields="user(emailAddress)").execute()["user"]["emailAddress"].lower() == "manuagarwal885@gmail.com"

REVIEW_FOLDER = "1U5FuPI_0YiCIxUaWwZuWjNiMiDms3vO7"
MODEL_ID = "1pwlOBiD3gmbU_4KRcLKse1M7TVgZT9-n"
LABELS_ID = "1_z0LWgDroeVRHrm2bAz5IvrkZEWESW6-"
ACCEPTED = {
    "ajanta_ellora_caves": [0, 1, 3, 4, 5, 6, 7],
    "charminar": [1, 2, 3, 4, 5, 7],
    "gateway_of_india": [1, 2, 4],
    "golden_temple": [0, 4],
    "hampi_monuments": [1, 4, 5],
    "khajuraho_monuments": [1, 3, 4, 5, 6, 7],
    "konark_sun_temple": [2, 3, 5, 7],
    "mahabalipuram": [0, 1, 4, 5, 6],
    "meenakshi_temple": [1, 3, 4, 5, 6],
    "mehrangarh_fort": [0, 6, 7],
    "mysore_palace": [0, 7],
    "qutub_minar": [1, 2, 3, 4, 6, 7],
    "red_fort": [],
    "sanchi_stupa": [4, 5, 6],
    "taj_mahal": [0, 7],
    "victoria_memorial": [1, 4, 5, 7],
}

def media(fid):
    return drive.files().get_media(fileId=fid).execute()

def children(fid):
    files, token = [], None
    while True:
        result = drive.files().list(q=f"'{fid}' in parents and trashed = false",
                                    fields="nextPageToken,files(id,name)", pageSize=1000,
                                    pageToken=token).execute()
        files += result.get("files", [])
        token = result.get("nextPageToken")
        if not token:
            return {f["name"]: f["id"] for f in files}

files = children(REVIEW_FOLDER)
labels = media(LABELS_ID).decode().splitlines()
model_path = Path("/content/virasatai_baseline.tflite")
if not model_path.exists():
    model_path.write_bytes(media(MODEL_ID))
interpreter = tf.lite.Interpreter(model_path=str(model_path))
interpreter.allocate_tensors()
inp, out = interpreter.get_input_details()[0], interpreter.get_output_details()[0]
assert list(inp["shape"]) == [1, 160, 160, 3]

session = requests.Session()
session.headers.update({"User-Agent": "VirasatAI-student-evaluation/1.0 (educational image check)"})
results = []
for label, selected in ACCEPTED.items():
    if not selected:
        continue
    rows = json.loads(media(files[f"{label}_candidate_manifest.json"]))
    lookup = {r["index"]: r for r in rows}
    for number in selected:
        row = lookup[number]
        # Original source is preferred. Commons may rate-limit it; the already
        # downloaded 800px preview from this same Colab review is a fallback.
        image, resolution = None, "original"
        try:
            response = session.get(row["original_url"], timeout=35)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content)).convert("RGB")
        except (requests.RequestException, OSError) as exc:
            preview = Path("/content/virasatai_20class_review") / row["preview_file"]
            if preview.exists():
                image = Image.open(preview).convert("RGB")
                resolution = "800px_preview_fallback"
            else:
                results.append({"actual": label, "index": number,
                                "status": "unavailable", "error": str(exc)[:180]})
                continue
        pixels = np.asarray(ImageOps.fit(image, (160, 160)), dtype=np.float32)[None]
        interpreter.set_tensor(inp["index"], pixels)
        interpreter.invoke()
        probs = interpreter.get_tensor(out["index"])[0]
        prediction = labels[int(np.argmax(probs))]
        results.append({"actual": label, "index": number,
                        "prediction": prediction, "correct": prediction == label,
                        "confidence": round(float(np.max(probs)), 4),
                        "resolution": resolution, "image_size": list(image.size),
                        "commons_page": row["commons_page"], "license": row["license"],
                        "source_sha1": row["source_sha1"], "status": "scored"})
        print("SCORED", label, number, prediction, resolution, flush=True)
        time.sleep(0.25)

scored = [r for r in results if r["status"] == "scored"]
per_class = defaultdict(lambda: {"tested": 0, "correct": 0})
for row in scored:
    per_class[row["actual"]]["tested"] += 1
    per_class[row["actual"]]["correct"] += int(row["correct"])
report = {"status": "exploratory_independent_commons_test_only",
          "coverage": "15 of 20 classes; Red Fort and prior 4-class set not included",
          "tested": len(scored), "correct": sum(r["correct"] for r in scored),
          "unavailable": len(results) - len(scored),
          "originals": sum(r["resolution"] == "original" for r in scored),
          "preview_fallbacks": sum(r["resolution"] != "original" for r in scored),
          "per_class": dict(per_class), "rows": results,
          "not_a_phone_camera_test": True,
          "red_fort_rejected": "All eight candidates were signs, plaques, an unrelated detail, or unclear facade"}
payload = json.dumps(report, indent=2).encode()
existing = files.get("reviewed_15class_baseline_results.json")
if existing:
    drive.files().update(fileId=existing, media_body=MediaInMemoryUpload(payload, mimetype="application/json"), fields="id").execute()
else:
    drive.files().create(body={"name": "reviewed_15class_baseline_results.json", "parents": [REVIEW_FOLDER]},
                         media_body=MediaInMemoryUpload(payload, mimetype="application/json"), fields="id").execute()
print("REVIEWED_15CLASS_RESULT", json.dumps({k: v for k, v in report.items() if k != "rows"}), flush=True)
