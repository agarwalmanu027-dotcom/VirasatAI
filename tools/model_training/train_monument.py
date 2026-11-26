"""Train the first offline monument-recognition CNN from a prepared dataset.

TensorFlow must be installed separately. This script never downloads model weights.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path,
                        default=PROJECT / "05_AI_Dataset" / "prepared_monuments")
    parser.add_argument("--output", type=Path,
                        default=PROJECT / "05_AI_Dataset" / "trained_monuments")
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.epochs < 1 or args.batch_size < 1:
        parser.error("Epochs and batch size must be positive")
    labels_file = args.data / "labels.txt"
    if not labels_file.exists() or any(not (args.data / split).is_dir()
                                       for split in ("train", "val", "test")):
        parser.error("Prepared dataset is missing. Run prepare_dataset.py --write first.")
    if args.output.exists() and any(args.output.iterdir()):
        parser.error(f"Output folder is not empty: {args.output}")
    labels = labels_file.read_text(encoding="utf-8").splitlines()
    if len(labels) < 2:
        parser.error("At least two monument classes are required")
    try:
        import tensorflow as tf
    except ImportError:
        print("TensorFlow is not installed. No packages were downloaded or installed.", file=sys.stderr)
        return 2

    tf.keras.utils.set_random_seed(args.seed)
    def load(split: str, shuffle: bool):
        return tf.keras.utils.image_dataset_from_directory(
            args.data / split, labels="inferred", label_mode="int", class_names=labels,
            image_size=(224, 224), batch_size=args.batch_size, shuffle=shuffle,
            seed=args.seed,
        ).prefetch(tf.data.AUTOTUNE)

    train = load("train", True)
    val = load("val", False)
    test = load("test", False)
    # A small CNN baseline: no hidden download of ImageNet or other weights.
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(224, 224, 3)),
        tf.keras.layers.Rescaling(1.0 / 255),
        tf.keras.layers.RandomRotation(0.03),
        tf.keras.layers.RandomZoom(0.08),
        tf.keras.layers.Conv2D(32, 3, activation="relu", padding="same"),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(64, 3, activation="relu", padding="same"),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(128, 3, activation="relu", padding="same"),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(192, 3, activation="relu", padding="same"),
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(len(labels), activation="softmax"),
    ])
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                  loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    history = model.fit(
        train, validation_data=val, epochs=args.epochs,
        callbacks=[tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=5, restore_best_weights=True
        )], verbose=2,
    )
    test_loss, test_accuracy = model.evaluate(test, verbose=0)
    # Count each test class separately, so a high overall score cannot hide weak classes.
    confusion = [[0 for _ in labels] for _ in labels]
    for images, targets in test:
        predictions = tf.argmax(model(images, training=False), axis=1).numpy()
        for actual, predicted in zip(targets.numpy(), predictions):
            confusion[int(actual)][int(predicted)] += 1
    per_class = {label: {"correct": confusion[i][i], "total": sum(confusion[i])}
                 for i, label in enumerate(labels)}

    args.output.mkdir(parents=True, exist_ok=True)
    model.save(args.output / "monument_model.keras")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    (args.output / "monument_model.tflite").write_bytes(converter.convert())
    (args.output / "labels.txt").write_text("\n".join(labels) + "\n", encoding="utf-8")
    metrics = {"architecture": "small_cnn_baseline", "input_size": [224, 224],
               "input_type": "float32_rgb_0_to_255", "test_loss": float(test_loss),
               "test_accuracy": float(test_accuracy), "per_class": per_class,
               "confusion_matrix": confusion, "labels": labels,
               "training_epochs": len(history.history["loss"])}
    (args.output / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    print("Model is only a candidate until it passes unseen phone-photo tests.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
