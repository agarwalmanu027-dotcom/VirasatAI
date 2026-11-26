"""Make private contact sheets of EfficientNetV2-S development-test errors.

Run after the EfficientNetV2-S training cell in the same Colab runtime. The
generated sheets support visual label/quality review; no files are deleted.
"""

import csv
import io
import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image, ImageDraw, ImageFont
from googleapiclient.http import MediaFileUpload

assert "ROOT" in globals() and "drive" in globals() and "labels" in globals()
assert (ROOT / "images" / "test").exists(), "Run the training cell first"
if "model" not in globals() or "EfficientNetV2" not in model.name:
    saved = ROOT / "efficientnetv2s_candidate" / "monument_model.keras"
    if not saved.exists():
        saved.write_bytes(drive.files().get_media(
            fileId="1n8uZMvpflK6u6rybIMnC9VfCtpoXfAD1").execute())
    model = tf.keras.models.load_model(saved)

raw = tf.keras.utils.image_dataset_from_directory(
    ROOT / "images" / "test", class_names=labels, image_size=(224, 224),
    batch_size=16, label_mode="int", shuffle=False)
paths = [Path(p) for p in raw.file_paths]
truth = np.array([labels.index(path.parent.name) for path in paths])
prob = model.predict(raw, verbose=0)
pred = prob.argmax(axis=1)
assert len(paths) == len(pred) == 456
wrong = [dict(path=str(paths[i]), actual=labels[int(truth[i])],
              predicted=labels[int(pred[i])], confidence=float(prob[i, pred[i]]),
              actual_probability=float(prob[i, truth[i]]))
         for i in range(len(paths)) if pred[i] != truth[i]]
wrong.sort(key=lambda item: item["confidence"], reverse=True)

out = ROOT / "efficientnet_error_review"
out.mkdir(parents=True, exist_ok=True)
with (out / "errors.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=["path", "actual", "predicted",
                                                 "confidence", "actual_probability"])
    writer.writeheader()
    writer.writerows(wrong)

font = ImageFont.load_default()
tile_w, tile_h, cols, per_sheet = 310, 285, 4, 16
for start in range(0, len(wrong), per_sheet):
    selected = wrong[start:start + per_sheet]
    sheet = Image.new("RGB", (cols * tile_w, 4 * tile_h), "white")
    draw = ImageDraw.Draw(sheet)
    for position, item in enumerate(selected):
        x = (position % cols) * tile_w
        y = (position // cols) * tile_h
        with Image.open(item["path"]) as opened:
            image = opened.convert("RGB").resize((250, 250), Image.Resampling.LANCZOS)
        sheet.paste(image, (x + 30, y))
        draw.text((x + 5, y + 250), "Actual: " + item["actual"], fill="black", font=font)
        draw.text((x + 5, y + 265),
                  "Guess: " + item["predicted"] + f" {item['confidence']:.2f}",
                  fill="black", font=font)
    sheet.save(out / f"errors_{start // per_sheet + 1:02d}.jpg", quality=90)

summary = {"model": "EfficientNetV2-S", "development_test_photos": len(paths),
           "wrong": len(wrong), "sheets": (len(wrong) + per_sheet - 1) // per_sheet,
           "scope": "Visual review of labels, source quality, and monument ambiguity only"}
(out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
folder = drive.files().create(body={
    "name": "efficientnetv2s_error_review_2026-10-21",
    "mimeType": "application/vnd.google-apps.folder",
    "parents": ["1FL98KnE_e-BigfluYAGfFgLXdXtx9WWT"]},
    fields="id,webViewLink").execute()
for path in sorted(out.iterdir()):
    drive.files().create(body={"name": path.name, "parents": [folder["id"]]},
                         media_body=MediaFileUpload(str(path), resumable=True),
                         fields="id").execute()
print("ERROR_REVIEW_READY", summary, folder, flush=True)
