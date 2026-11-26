"""Calibrate a safe confirmation threshold for the existing 20-class model.

Run only in the authenticated Colab notebook after the 3,141-image restore.
This reads the model from the owner's private Drive into temporary Colab storage.
It does not train on the validation or test split, and downloads nothing to the PC.
"""

import json
from pathlib import Path

import numpy as np
import tensorflow as tf

assert len(labels) == 20
assert len(manifest) == 3141
assert sum(x['split'] == 'val' for x in manifest) == 470
assert sum(x['split'] == 'test' for x in manifest) == 470

model_path = Path('/content/virasatai_exterior_restore/baseline_model.keras')
if not model_path.exists():
    model_path.write_bytes(fetch(MODEL_ID))
model = tf.keras.models.load_model(model_path)


def predictions(split):
    ds = tf.keras.utils.image_dataset_from_directory(
        PREPARED / split, class_names=labels, image_size=(160, 160),
        batch_size=32, label_mode='int', shuffle=False,
    ).prefetch(tf.data.AUTOTUNE)
    truth = np.concatenate([y.numpy() for _, y in ds])
    probability = model.predict(ds, verbose=0)
    return truth, probability.argmax(axis=1), probability.max(axis=1)


validation_truth, validation_prediction, validation_confidence = predictions('val')
test_truth, test_prediction, test_confidence = predictions('test')

possible_thresholds = np.round(np.arange(0.50, 0.96, 0.05), 2)
options = []
for threshold in possible_thresholds:
    kept = validation_confidence >= threshold
    if kept.sum() == 0:
        continue
    precision = float((validation_prediction[kept] == validation_truth[kept]).mean())
    coverage = float(kept.mean())
    options.append({'threshold': float(threshold), 'validation_precision': precision,
                    'validation_coverage': coverage, 'validation_kept': int(kept.sum())})

# Select only from validation data. Require a useful retained sample size.
eligible = [x for x in options if x['validation_precision'] >= 0.90
            and x['validation_kept'] >= 100]
chosen = min(eligible, key=lambda x: x['threshold']) if eligible else None

report = {
    'status': 'validation_calibration_only',
    'labels': labels,
    'validation_count': len(validation_truth),
    'validation_accuracy_all': float((validation_prediction == validation_truth).mean()),
    'threshold_options': options,
    'selected_threshold': chosen['threshold'] if chosen else None,
    'test_count': len(test_truth),
    'test_accuracy_all': float((test_prediction == test_truth).mean()),
    'note': 'Independent real-phone and unknown-monument tests are still required.',
}
if chosen:
    kept = test_confidence >= chosen['threshold']
    report['test_at_selected_threshold'] = {
        'kept': int(kept.sum()),
        'coverage': float(kept.mean()),
        'precision': float((test_prediction[kept] == test_truth[kept]).mean()),
    }

print('20CLASS_CONFIDENCE_CALIBRATION', json.dumps(report), flush=True)
