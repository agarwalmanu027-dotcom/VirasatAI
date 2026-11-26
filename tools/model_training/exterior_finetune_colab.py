"""Experimental exterior-photo fine tune in the existing Colab session only.

The manually reviewed images are train-only. The original model and test sets
remain unchanged. This run is diagnostic, not an APK release.
"""

import json
import numpy as np
import tensorflow as tf
from pathlib import Path
from googleapiclient.http import MediaFileUpload

selection = {
    'badami_cave_temples': {1, 2, 9, 15, 17, 22, 23},
    'amer_fort': {1, 3, 4, 5, 7, 8, 13, 15, 17, 18, 22, 23},
}
chosen = [x for x in accepted if x['index'] in selection.get(x['label'], set())]
assert len(chosen) == 19 and len(labels) == 20
for x in chosen:
    src = Path(x['preview'])
    assert src.exists()
    target = prepared / 'train' / x['label'] / f"exterior_{x['source_sha1']}.jpg"
    if not target.exists():
        target.write_bytes(src.read_bytes())
print('EXTERIOR_TRAIN_FILES', len(chosen), flush=True)

train_exterior = tf.keras.utils.image_dataset_from_directory(
    prepared / 'train', image_size=(160, 160), batch_size=32,
    label_mode='int', shuffle=True, seed=42)
assert train_exterior.class_names == labels
train_exterior = train_exterior.prefetch(tf.data.AUTOTUNE)
model_exterior = tf.keras.models.load_model(output2 / 'monument_model.keras')
model_exterior.compile(optimizer=tf.keras.optimizers.Adam(5e-6),
                       loss='sparse_categorical_crossentropy', metrics=['accuracy'])
history_exterior = model_exterior.fit(
    train_exterior, validation_data=val, epochs=3, verbose=2,
    callbacks=[tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=1,
                                                 restore_best_weights=True)])
truth = np.concatenate([y.numpy() for _, y in test])
old_pred = transfer_model.predict(test, verbose=0).argmax(1)
new_pred = model_exterior.predict(test, verbose=0).argmax(1)
report = {
    'status': 'candidate_only',
    'added_train_only': len(chosen),
    'original_test_total': len(truth),
    'original_model_correct': int((old_pred == truth).sum()),
    'exterior_candidate_correct': int((new_pred == truth).sum()),
    'original_model_accuracy': float((old_pred == truth).mean()),
    'exterior_candidate_accuracy': float((new_pred == truth).mean()),
    'per_focus_class': {
        label: {'total': int((truth == labels.index(label)).sum()),
                'original_correct': int(((truth == labels.index(label)) & (old_pred == truth)).sum()),
                'candidate_correct': int(((truth == labels.index(label)) & (new_pred == truth)).sum())}
        for label in selection
    },
    'val_loss': [float(v) for v in history_exterior.history['val_loss']],
    'limitation': 'Classes selected after prior error analysis. Independent photos and unseen phone photos still needed before app integration.',
}
print('EXTERIOR_FINETUNE_RESULT', json.dumps(report), flush=True)
out = Path('/content/virasatai_exterior_finetune_candidate')
out.mkdir(exist_ok=True)
(out / 'metrics.json').write_text(json.dumps(report, indent=2))
model_exterior.save(out / 'monument_model.keras')
(out / 'labels.txt').write_text('\n'.join(labels) + '\n')
folder = drive.files().create(body={'name': 'exterior_finetune_candidate_2026-10-16',
  'mimeType': 'application/vnd.google-apps.folder', 'parents': [ROOT]}, fields='id').execute()['id']
for path in out.iterdir():
    drive.files().create(body={'name': path.name, 'parents': [folder]},
        media_body=MediaFileUpload(str(path), resumable=True), fields='id').execute()
print('EXTERIOR_FINETUNE_SAVED', folder, flush=True)
