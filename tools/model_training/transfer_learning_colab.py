"""Second experimental 20-monument run in the existing Colab session.

Requires user-approved download of official Keras ImageNet MobileNetV2 weights.
Reuses the first run's prepared train/val/test image splits. Results remain
candidate-only until label review and unseen phone-photo evaluation.
"""

import json
from collections import Counter

import numpy as np
import tensorflow as tf
from googleapiclient.http import MediaFileUpload

assert len(labels) == 20
assert prepared.exists()
tf.keras.utils.set_random_seed(42)

backbone = tf.keras.applications.MobileNetV2(
    input_shape=(160, 160, 3), include_top=False, weights="imagenet"
)
backbone.trainable = False
inputs = tf.keras.Input((160, 160, 3))
x = tf.keras.layers.RandomFlip("horizontal")(inputs)
x = tf.keras.layers.RandomRotation(0.03)(x)
x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
x = backbone(x, training=False)
x = tf.keras.layers.GlobalAveragePooling2D()(x)
x = tf.keras.layers.Dropout(0.3)(x)
outputs = tf.keras.layers.Dense(len(labels), activation="softmax")(x)
transfer_model = tf.keras.Model(inputs, outputs)
transfer_model.compile(
    optimizer=tf.keras.optimizers.Adam(0.0005),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)
first_history = transfer_model.fit(
    train, validation_data=val, epochs=10, verbose=2,
    callbacks=[tf.keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=3, restore_best_weights=True
    )],
)

# Fine-tune only the last convolutional layers. Keep batch normalization fixed.
backbone.trainable = True
for layer in backbone.layers[:-25]:
    layer.trainable = False
for layer in backbone.layers:
    if isinstance(layer, tf.keras.layers.BatchNormalization):
        layer.trainable = False
transfer_model.compile(
    optimizer=tf.keras.optimizers.Adam(0.00001),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)
second_history = transfer_model.fit(
    train, validation_data=val, epochs=4, verbose=2,
    callbacks=[tf.keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=2, restore_best_weights=True
    )],
)

test_loss, test_accuracy = transfer_model.evaluate(test, verbose=0)
truth = np.concatenate([y.numpy() for _, y in test])
prob = transfer_model.predict(test, verbose=0)
pred = prob.argmax(axis=1)
per_class = []
for idx, label in enumerate(labels):
    indices = np.flatnonzero(truth == idx)
    errors = Counter(labels[int(v)] for v in pred[indices] if v != idx)
    per_class.append({
        "monument": label,
        "test_photos": len(indices),
        "correct": int((pred[indices] == idx).sum()),
        "accuracy": round(float((pred[indices] == idx).mean()), 3),
        "most_confused_with": errors.most_common(3),
    })
per_class.sort(key=lambda row: row["accuracy"])
report = {
    "status": "candidate_only",
    "baseline_test_accuracy": 0.3340425491333008,
    "transfer_test_accuracy": float(test_accuracy),
    "test_loss": float(test_loss),
    "frozen_epochs": len(first_history.history["loss"]),
    "finetune_epochs": len(second_history.history["loss"]),
    "per_monument": per_class,
    "warning": "Visual label review and unseen phone-photo test still required.",
}
print("TRANSFER EXPERIMENT COMPLETE", json.dumps(report), flush=True)

output2 = LOCAL / "transfer_model_candidate"
output2.mkdir(parents=True, exist_ok=True)
transfer_model.save(output2 / "monument_model.keras")
(output2 / "monument_model.tflite").write_bytes(
    tf.lite.TFLiteConverter.from_keras_model(transfer_model).convert()
)
(output2 / "labels.txt").write_text("\n".join(labels) + "\n", encoding="utf-8")
(output2 / "metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

folder2 = api().files().create(body={
    "name": "transfer_model_experiment_2026-10-15",
    "mimeType": FOLDER_MIME,
    "parents": [OUTPUT_PARENT_ID],
}, fields="id,webViewLink").execute()
for path in output2.iterdir():
    api().files().create(
        body={"name": path.name, "parents": [folder2["id"]]},
        media_body=MediaFileUpload(str(path), resumable=True),
        fields="id,name",
    ).execute()
print("TRANSFER MODEL SAVED", folder2["id"], flush=True)
