"""Candidate-only DINOv2 retrieval experiment for the reviewed 20-class split.

Run as a single Colab Python cell in the dataset owner's account. It never
changes the phone model. Validation selects the method; the development test
is used once for reporting. Crops are stress tests of those same test sources,
not an independent phone-photo holdout.
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
import torch
from google.colab import auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from PIL import Image, ImageOps
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from torch.utils.data import DataLoader, Dataset

ACCOUNT = "manuagarwal885@gmail.com"
MANIFEST_ID = "19BLdHeZLeq4YxLvB8OWLjwRZs_mgEWSv"
OUTPUT_PARENT_ID = "1FL98KnE_e-BigfluYAGfFgLXdXtx9WWT"
ROOT = Path("/content/virasatai_reviewed_v2")
OUT = ROOT / "dinov2_retrieval_2026-10-22"
SEED = 42
SIDE = 224
BATCH = 32
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
OUT.mkdir(parents=True, exist_ok=True)

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
rows = [r for r in all_rows if not r["raw_name"].lower().startswith("aug_")]
assert len(rows) == 3074
labels = sorted({r["label"] for r in rows})
assert len(labels) == 20
assert Counter(r["split"] for r in rows) == {"train": 2155, "val": 463, "test": 456}
groups = {}
for r in rows:
    key = (r["label"], r["source_group"])
    assert key not in groups or groups[key] == r["split"], "Source group crosses splits"
    groups[key] = r["split"]
    r["path"] = ROOT / "images" / r["split"] / r["label"] / (r["sha256"] + ".jpg")


def restore(row):
    if row["path"].exists():
        return
    data = fetch(row["file_id"])
    assert hashlib.sha256(data).hexdigest() == row["sha256"], "Source changed"
    with Image.open(io.BytesIO(data)) as source:
        photo = ImageOps.pad(ImageOps.exif_transpose(source).convert("RGB"),
                             (SIDE, SIDE), method=Image.Resampling.LANCZOS,
                             color=(127, 127, 127))
    row["path"].parent.mkdir(parents=True, exist_ok=True)
    photo.save(row["path"], quality=92)


for i, row in enumerate(rows, 1):
    restore(row)
    if i % 200 == 0 or i == len(rows):
        print("RESTORED", i, len(rows), flush=True)

device = "cuda" if torch.cuda.is_available() else "cpu"
assert device == "cuda", "Colab mein T4 GPU select karke dobara run karein"
print("GPU", torch.cuda.get_device_name(0), flush=True)
model = torch.hub.load("facebookresearch/dinov2", "dinov2_vits14").to(device).eval()
mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)


class Photos(Dataset):
    def __init__(self, selected, view):
        self.selected = selected
        self.view = view

    def __len__(self):
        return len(self.selected)

    def __getitem__(self, index):
        with Image.open(self.selected[index]["path"]) as source:
            image = source.convert("RGB")
        if self.view == "center_70":
            margin = int(SIDE * 0.15)
            image = image.crop((margin, margin, SIDE-margin, SIDE-margin))
            image = image.resize((SIDE, SIDE), Image.Resampling.BICUBIC)
        pixels = torch.from_numpy(np.asarray(image, dtype=np.float32).copy())
        pixels = pixels.permute(2, 0, 1) / 255.0
        return (pixels - mean) / std


def embeddings(selected, view):
    loader = DataLoader(Photos(selected, view), batch_size=BATCH, shuffle=False,
                        num_workers=2, pin_memory=True)
    chunks = []
    with torch.inference_mode():
        for batch in loader:
            feature = model(batch.to(device))
            feature = torch.nn.functional.normalize(feature.float(), dim=1)
            chunks.append(feature.cpu().numpy())
    return np.concatenate(chunks).astype(np.float32)


splits = {s: [r for r in rows if r["split"] == s] for s in ("train", "val", "test")}
y = {s: np.array([labels.index(r["label"]) for r in splits[s]]) for s in splits}
features = {}
for split in splits:
    for view in ("full", "center_70"):
        cache = OUT / f"{split}_{view}.npy"
        if cache.exists():
            data = np.load(cache)
            assert data.shape == (len(splits[split]), 384)
        else:
            data = embeddings(splits[split], view)
            np.save(cache, data)
        features[split, view] = data
        print("EMBEDDED", split, view, data.shape, flush=True)

# No class-balanced evaluation sampling: every held-out photo counts once.
# Retrieval scores are normalized within each class so large classes do not win
# only because they have more reference photos.
train_x = features["train", "full"]
train_y = y["train"]
train_by_class = [np.flatnonzero(train_y == c) for c in range(20)]


def retrieval_prob(query, k):
    similarity = query @ train_x.T
    scores = np.empty((len(query), 20), dtype=np.float32)
    for c, indices in enumerate(train_by_class):
        nearest = np.sort(similarity[:, indices], axis=1)[:, -min(k, len(indices)):]
        scores[:, c] = nearest.mean(axis=1)
    return scores


def softmax(scores, temperature):
    scaled = scores / temperature
    scaled -= scaled.max(axis=1, keepdims=True)
    exp = np.exp(scaled)
    return exp / exp.sum(axis=1, keepdims=True)


def candidate_predictions(name, split, view):
    x = features[split, view]
    if name.startswith("retrieval_"):
        k = int(name.split("_")[1])
        return retrieval_prob(x, k)
    return linear_models[name].predict_proba(x)


linear_models = {}
for strength in (0.1, 1.0, 10.0):
    name = f"linear_{strength}"
    clf = LogisticRegression(C=strength, max_iter=1000, class_weight="balanced")
    clf.fit(train_x, train_y)
    linear_models[name] = clf

candidates = ["retrieval_1", "retrieval_3", "retrieval_5"] + list(linear_models)
ranking = []
for name in candidates:
    full_pred = candidate_predictions(name, "val", "full").argmax(axis=1)
    crop_pred = candidate_predictions(name, "val", "center_70").argmax(axis=1)
    clean = accuracy_score(y["val"], full_pred)
    partial = accuracy_score(y["val"], crop_pred)
    ranking.append({"method": name, "val_full_accuracy": float(clean),
                    "val_center_crop_accuracy": float(partial),
                    "selection_score": float((clean + partial) / 2)})
ranking.sort(key=lambda item: (item["selection_score"], item["val_full_accuracy"]),
             reverse=True)
winner = ranking[0]["method"]
print("VALIDATION_SELECTION", json.dumps(ranking), flush=True)

val_scores = candidate_predictions(winner, "val", "full")
test_scores = candidate_predictions(winner, "test", "full")
test_partial_scores = candidate_predictions(winner, "test", "center_70")

# A threshold is selected only on validation. This is a coverage-vs-precision
# operating point, not evidence that unfamiliar monuments can be recognized.
best_threshold = None
for threshold in np.linspace(0, 1, 101):
    # Retrieval similarity is not calibrated probability; use top-two margin.
    if winner.startswith("retrieval_"):
        measure = lambda scores: np.sort(scores, axis=1)[:, -1] - np.sort(scores, axis=1)[:, -2]
        threshold_value = threshold * 0.30
    else:
        measure = lambda scores: scores.max(axis=1)
        threshold_value = threshold
    accepted = measure(val_scores) >= threshold_value
    if accepted.sum() >= 20:
        precision = (val_scores.argmax(axis=1)[accepted] == y["val"][accepted]).mean()
        if precision >= 0.90:
            best_threshold = float(threshold_value)
            break


def score_set(scores, truth):
    predicted = scores.argmax(axis=1)
    report = classification_report(truth, predicted, labels=list(range(20)),
                                   target_names=labels, output_dict=True, zero_division=0)
    result = {"count": len(truth), "accuracy": float(accuracy_score(truth, predicted)),
              "macro_precision": float(report["macro avg"]["precision"]),
              "macro_recall": float(report["macro avg"]["recall"]),
              "macro_f1": float(report["macro avg"]["f1-score"]),
              "per_class": report,
              "confusion_matrix": confusion_matrix(truth, predicted,
                                                    labels=list(range(20))).tolist()}
    if best_threshold is not None:
        if winner.startswith("retrieval_"):
            ordered = np.sort(scores, axis=1)
            confidence = ordered[:, -1] - ordered[:, -2]
        else:
            confidence = scores.max(axis=1)
        accepted = confidence >= best_threshold
        result["accepted_count"] = int(accepted.sum())
        result["accepted_coverage"] = float(accepted.mean())
        result["accepted_accuracy"] = (float((predicted[accepted] == truth[accepted]).mean())
                                       if accepted.any() else None)
    return result


metrics = {"status": "candidate_only_not_independent_phone_test",
           "method": winner, "validation_ranking": ranking,
           "validation_selected_threshold": best_threshold,
           "original_reviewed_source_photos": len(rows),
           "train_photos": len(splits["train"]), "validation_photos": len(splits["val"]),
           "development_test_photos": len(splits["test"]),
           "test_full": score_set(test_scores, y["test"]),
           "test_center_70": score_set(test_partial_scores, y["test"]),
           "warning": "The development test has informed model development. Crops reuse its source photos. A fresh independent phone-photo holdout and unknown-place negatives are needed before deployment or a 90% claim."}
(OUT / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
with (OUT / "test_predictions.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow(["file_id", "raw_name", "actual", "full_prediction", "partial_prediction"])
    for index, row in enumerate(splits["test"]):
        writer.writerow([row["file_id"], row["raw_name"], row["label"],
                         labels[test_scores[index].argmax()],
                         labels[test_partial_scores[index].argmax()]])
print("DINO_RESULT", json.dumps({"method": winner,
                                "full": metrics["test_full"]["accuracy"],
                                "partial": metrics["test_center_70"]["accuracy"],
                                "accepted_coverage": metrics["test_full"].get("accepted_coverage")}),
      flush=True)

folder = drive.files().create(body={"name": "dinov2_retrieval_candidate_2026-10-22",
                                    "mimeType": "application/vnd.google-apps.folder",
                                    "parents": [OUTPUT_PARENT_ID]},
                              fields="id,webViewLink").execute()
for filename in ("metrics.json", "test_predictions.csv"):
    drive.files().create(body={"name": filename, "parents": [folder["id"]]},
                         media_body=MediaFileUpload(str(OUT / filename), resumable=True),
                         fields="id").execute()
print("DINO_SAVED", folder, flush=True)
