"""Score visually reviewed, previously unseen Commons previews in Colab only.

The four contact sheets and both candidate models stay in the user's Drive or
Colab runtime. A sheet tile is only 210x180 px, so this is an exploratory
independent web-image check, not a phone-camera acceptance test.
"""

import io
import json
from collections import defaultdict

import numpy as np
import tensorflow as tf
from PIL import Image, ImageOps
from google.colab import auth
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

auth.authenticate_user()
credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/drive"])
drive = build("drive", "v3", credentials=credentials, cache_discovery=False)
assert drive.about().get(fields="user(emailAddress)").execute()["user"]["emailAddress"].lower() == "manuagarwal885@gmail.com"

REVIEW_FOLDER = "1HYRw4IoU2uF2nVaYnKLY-k6dBplddkVj"
TRANSFER_MODEL = "1pwlOBiD3gmbU_4KRcLKse1M7TVgZT9-n"
FOCUS_MODEL = "1ba3VfPq97OYWYfHGGG3c_ezPEDiue5RC"
LABELS_FILE = "1_z0LWgDroeVRHrm2bAz5IvrkZEWESW6-"
MANIFEST_FILE = "1zjRgf_bQsxoBLLzIfqF41ywsVJChZD8q"
SHEETS = {
    "badami_cave_temples": "1T5MPYO-TrHpWsT-BHvP_yhlSRrLfw1Pm",
    "city_palace_udaipur": "1uQmmOpyt-QWeyJvLthz-lgotJkT4JfpG",
    "jaisalmer_fort": "1_dJh0ygeE68tE7bXg5wBI991Dy6sOR-7",
    "amer_fort": "1H09cLyEML3C-eCdlOURN6n4lbQW_Xd50",
}
# Each of these is visibly a monument or its distinctive fort/palace facade.
# Avoid inscriptions, ordinary market streets, generic sculptures and very
# ambiguous details. Jaisalmer has few usable candidates in this batch.
ACCEPTED = {
    "badami_cave_temples": [2, 3, 4, 7, 8, 9, 10, 11],
    "city_palace_udaipur": [0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11],
    "jaisalmer_fort": [3, 11],
    "amer_fort": [0, 2, 3, 4, 5, 7, 10, 11],
}


def media(file_id):
    return drive.files().get_media(fileId=file_id).execute()


labels = media(LABELS_FILE).decode("utf-8").splitlines()
manifest = json.loads(media(MANIFEST_FILE))
index = {(row["label"], row["index"]): row for row in manifest}
images, truth, selected = [], [], []
for label, chosen in ACCEPTED.items():
    sheet = Image.open(io.BytesIO(media(SHEETS[label]))).convert("RGB")
    assert sheet.size == (880, 660), (label, sheet.size)
    for n in chosen:
        row = index[(label, n)]
        x, y = (n % 4) * 220, (n // 4) * 220
        tile = sheet.crop((x, y, x + 210, y + 180))
        images.append(np.asarray(ImageOps.fit(tile, (160, 160)), dtype=np.float32))
        truth.append(labels.index(label))
        selected.append({"actual": label, "sheet_index": n, "commons_page": row["page"],
                         "license": row["license"], "source_sha1": row["source_sha1"]})
x = np.stack(images)
truth = np.asarray(truth)
print("VISUALLY_REVIEWED_SAMPLES", len(x), {k: len(v) for k, v in ACCEPTED.items()}, flush=True)

open("/content/virasatai_transfer.tflite", "wb").write(media(TRANSFER_MODEL))
interpreter = tf.lite.Interpreter(model_path="/content/virasatai_transfer.tflite")
interpreter.allocate_tensors()
inp = interpreter.get_input_details()[0]
out = interpreter.get_output_details()[0]
assert list(inp["shape"]) == [1, 160, 160, 3]
transfer_prob = []
for image in x:
    interpreter.set_tensor(inp["index"], image[None, ...])
    interpreter.invoke()
    transfer_prob.append(interpreter.get_tensor(out["index"])[0])
transfer_prob = np.asarray(transfer_prob)

open("/content/virasatai_focus.keras", "wb").write(media(FOCUS_MODEL))
focus_model = tf.keras.models.load_model("/content/virasatai_focus.keras", compile=False)
focus_prob = focus_model.predict(x, verbose=0)


def report(probs):
    prediction = probs.argmax(axis=1)
    per_class = {}
    for label in ACCEPTED:
        positions = np.flatnonzero(truth == labels.index(label))
        per_class[label] = {"tested": len(positions),
                            "correct": int((prediction[positions] == truth[positions]).sum())}
    return {"tested": len(truth), "correct": int((prediction == truth).sum()),
            "per_class": per_class}


for n, row in enumerate(selected):
    for name, probs in (("transfer", transfer_prob), ("focus", focus_prob)):
        row[name + "_prediction"] = labels[int(probs[n].argmax())]
        row[name + "_confidence"] = float(probs[n].max())

result = {
    "status": "exploratory_independent_preview_test_only",
    "limitation": "Only 4 of 20 classes, selected after visual review. Inputs are 210x180 contact-sheet crops, not full-resolution or real phone photos; Jaisalmer has only 2 unambiguous images. Do not treat this as deployment approval.",
    "transfer": report(transfer_prob),
    "focus": report(focus_prob),
    "selection": ACCEPTED,
    "results": selected,
}
print("INDEPENDENT_PREVIEW_RESULT", json.dumps({k: v for k, v in result.items() if k != "results"}), flush=True)
print("PER_IMAGE", json.dumps(selected), flush=True)
payload = json.dumps(result, indent=2).encode("utf-8")
existing = drive.files().list(q=f"'{REVIEW_FOLDER}' in parents and name = 'independent_preview_metrics.json' and trashed = false",
                              fields="files(id)").execute().get("files", [])
if existing:
    saved = drive.files().update(fileId=existing[0]["id"],
                                media_body=MediaInMemoryUpload(payload, mimetype="application/json"),
                                fields="id,name").execute()
else:
    saved = drive.files().create(body={"name": "independent_preview_metrics.json", "parents": [REVIEW_FOLDER]},
                                media_body=MediaInMemoryUpload(payload, mimetype="application/json"),
                                fields="id,name").execute()
print("SAVED_REVIEW_METRICS", saved["id"], flush=True)
