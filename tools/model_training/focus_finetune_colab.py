"""Experimental focus-image fine-tune, using the existing Colab session.

Never mixes the external holdout into training. Leaves the original model intact.
"""

import io
import json
from collections import Counter

import numpy as np
import tensorflow as tf
from PIL import Image, ImageOps
from googleapiclient.http import MediaFileUpload

assert len(labels) == 20
assert folder2["id"] == "1QMtQcTDq4DFYru2uUYO2ei2WFU-BcKZ7"
added = [r for r in rows if r["role"] == "train" and r["status"] == "added"]
assert len(added) == 21, f"Unexpected new training count: {len(added)}"
for row in added:
    target = prepared / "train" / row["label"] / row["name"]
    if not target.exists():
        data = api().files().get_media(fileId=row["drive_id"]).execute()
        with Image.open(io.BytesIO(data)) as im:
            ImageOps.fit(im.convert("RGB"), (160, 160)).save(target, quality=90)
print("FOCUS_TRAIN_FILES", len(added), flush=True)

train_focus = tf.keras.utils.image_dataset_from_directory(
    prepared / "train", image_size=(160, 160), batch_size=32,
    label_mode="int", shuffle=True, seed=42,
)
assert train_focus.class_names == labels
train_focus = train_focus.prefetch(tf.data.AUTOTUNE)

# Load a second copy so that the 78.5% baseline remains untouched.
candidate = tf.keras.models.load_model(output2 / "monument_model.keras")
candidate.compile(
    optimizer=tf.keras.optimizers.Adam(5e-6),
    loss="sparse_categorical_crossentropy", metrics=["accuracy"],
)
history = candidate.fit(
    train_focus, validation_data=val, epochs=3, verbose=2,
    callbacks=[tf.keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=1, restore_best_weights=True
    )],
)
old_test_prob = transfer_model.predict(test, verbose=0)
new_test_prob = candidate.predict(test, verbose=0)
truth = np.concatenate([y.numpy() for _, y in test])
old_test_accuracy = float((old_test_prob.argmax(1) == truth).mean())
new_test_accuracy = float((new_test_prob.argmax(1) == truth).mean())

holdout_x = []
holdout_y = []
for label, folder_id in holdout_folders.items():
    for file in children(folder_id):
        data = api().files().get_media(fileId=file["id"]).execute()
        with Image.open(io.BytesIO(data)) as im:
            holdout_x.append(np.asarray(
                ImageOps.fit(im.convert("RGB"), (160, 160)), dtype=np.float32
            ))
        holdout_y.append(labels.index(label))
assert len(holdout_x) == 11
holdout_x = np.stack(holdout_x)
holdout_y = np.asarray(holdout_y)
old_holdout_prob = transfer_model.predict(holdout_x, verbose=0)
new_holdout_prob = candidate.predict(holdout_x, verbose=0)
old_holdout_accuracy = float((old_holdout_prob.argmax(1) == holdout_y).mean())
new_holdout_accuracy = float((new_holdout_prob.argmax(1) == holdout_y).mean())

per_class = []
for label in ["badami_cave_temples", "city_palace_udaipur", "jaisalmer_fort", "amer_fort"]:
    k = labels.index(label)
    test_idx = np.flatnonzero(truth == k)
    ext_idx = np.flatnonzero(holdout_y == k)
    per_class.append({
        "monument": label,
        "old_test_correct": int((old_test_prob.argmax(1)[test_idx] == k).sum()),
        "new_test_correct": int((new_test_prob.argmax(1)[test_idx] == k).sum()),
        "test_total": len(test_idx),
        "old_external_correct": int((old_holdout_prob.argmax(1)[ext_idx] == k).sum()),
        "new_external_correct": int((new_holdout_prob.argmax(1)[ext_idx] == k).sum()),
        "external_total": len(ext_idx),
    })
report = {
    "status": "candidate_only",
    "added_train": len(added),
    "epochs": len(history.history["loss"]),
    "old_original_test_accuracy": old_test_accuracy,
    "new_original_test_accuracy": new_test_accuracy,
    "old_external_holdout_accuracy": old_holdout_accuracy,
    "new_external_holdout_accuracy": new_holdout_accuracy,
    "external_count": len(holdout_y),
    "per_focus_class": per_class,
    "val_loss": [float(v) for v in history.history["val_loss"]],
    "limitations": "Focused class selection used prior test error analysis. External sample is only 11 images. Unseen phone-photo testing remains necessary.",
}
print("FOCUS_FINETUNE_RESULT", json.dumps(report), flush=True)

focus_out = LOCAL / "focus_finetune_candidate"
focus_out.mkdir(exist_ok=True)
(focus_out / "metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
candidate.save(focus_out / "monument_model.keras")
(focus_out / "labels.txt").write_text("\n".join(labels) + "\n", encoding="utf-8")
focus_folder = api().files().create(body={
    "name": "focus_finetune_candidate_2026-10-15", "mimeType": FOLDER_MIME,
    "parents": [OUTPUT_PARENT_ID]
}, fields="id,webViewLink").execute()
for path in focus_out.iterdir():
    api().files().create(
        body={"name": path.name, "parents": [focus_folder["id"]]},
        media_body=MediaFileUpload(str(path), resumable=True), fields="id,name"
    ).execute()
print("FOCUS_FINETUNE_SAVED", focus_folder["id"], flush=True)
