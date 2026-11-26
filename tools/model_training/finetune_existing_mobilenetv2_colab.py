"""Colab-only controlled fine-tuning of the existing 78.5% MobileNetV2.

Uses the original fixed splits. Selects weights using validation only and
compares both models on identical clean and synthetic difficult test images.
No new pretrained backbone is downloaded. No model is installed in the APK.
"""
import json
from pathlib import Path
import numpy as np
import tensorflow as tf
from google.colab import auth
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

auth.authenticate_user()
credentials, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/drive'])
service = build('drive', 'v3', credentials=credentials, cache_discovery=False)
# Reuse the verified original restore procedure, stopping before its old
# experiment adds images or trains anything.
source = service.files().get_media(fileId='1AMSZIdokOFz_5NL7upw0ArLVEE3b_ZbJ').execute().decode('utf-8')
exec(compile(source[:source.index('decisions =')], 'restore_original_split.py', 'exec'))
tf.keras.utils.set_random_seed(73)
baseline_path = LOCAL / 'baseline_model.keras'
if not baseline_path.exists():
    baseline_path.write_bytes(fetch(MODEL_ID))
baseline = tf.keras.models.load_model(baseline_path)
candidate = tf.keras.models.load_model(baseline_path)
assert candidate.input_shape == (None, 160, 160, 3)
assert candidate.output_shape[-1] == 20
backbones = [layer for layer in candidate.layers if isinstance(layer, tf.keras.Model)]
assert len(backbones) == 1, 'Inspect model architecture before continuing'
backbone = backbones[0]
backbone.trainable = True
for layer in backbone.layers:
    layer.trainable = False
for layer in backbone.layers[-35:]:
    if not isinstance(layer, tf.keras.layers.BatchNormalization):
        layer.trainable = True

augmentation = tf.keras.Sequential([
    tf.keras.layers.RandomRotation(0.035, fill_mode='reflect'),
    tf.keras.layers.RandomTranslation(0.08, 0.08, fill_mode='reflect'),
    tf.keras.layers.RandomZoom((-0.18, 0.10), fill_mode='reflect'),
    tf.keras.layers.RandomContrast(0.15),
])

def augment_image(image, target):
    image = augmentation(image, training=True)
    # Mild lower-frame foreground cover; keep most monument evidence visible.
    batch = tf.shape(image)[0]
    yy = tf.range(160)[None, :, None, None]
    xx = tf.range(160)[None, None, :, None]
    top = tf.random.uniform((batch, 1, 1, 1), 90, 130, dtype=tf.int32)
    left = tf.random.uniform((batch, 1, 1, 1), 10, 110, dtype=tf.int32)
    apply = tf.random.uniform((batch, 1, 1, 1)) < 0.3
    mask = apply & (yy >= top) & (yy < top + 28) & (xx >= left) & (xx < left + 30)
    return tf.clip_by_value(tf.where(mask, 110.0, image), 0.0, 255.0), target

def dataset(split, shuffle=False):
    return tf.keras.utils.image_dataset_from_directory(
        PREPARED / split, class_names=labels, image_size=(160,160),
        batch_size=32, label_mode='int', shuffle=shuffle, seed=73)

train = dataset('train', True).map(augment_image, num_parallel_calls=tf.data.AUTOTUNE).prefetch(tf.data.AUTOTUNE)
val = dataset('val').prefetch(tf.data.AUTOTUNE)
test = dataset('test').prefetch(tf.data.AUTOTUNE)
out = LOCAL / 'existing_v2_augmented_candidate'
out.mkdir(exist_ok=True)
# Save the baseline as a fallback. A candidate must improve validation loss
# before ModelCheckpoint is allowed to overwrite it.
baseline.save(out / 'best.keras')
baseline_val_loss = float(baseline.evaluate(val, verbose=0)[0])
candidate.compile(optimizer=tf.keras.optimizers.Adam(3e-6),
                  loss='sparse_categorical_crossentropy', metrics=['accuracy'])
history = candidate.fit(train, validation_data=val, epochs=12, verbose=2,
    callbacks=[tf.keras.callbacks.ModelCheckpoint(str(out/'best.keras'),
        monitor='val_loss', save_best_only=True, initial_value_threshold=baseline_val_loss),
        tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=3),
        tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', patience=2, factor=0.5)])
candidate = tf.keras.models.load_model(out/'best.keras')

def difficult(images):
    cropped = tf.image.central_crop(images, 0.8)
    cropped = tf.image.resize(cropped, (160,160))
    yy = tf.range(160)[None,:,None,None]
    xx = tf.range(160)[None,None,:,None]
    mask = (yy >= 108) & (yy < 144) & (xx >= 55) & (xx < 100)
    return tf.where(mask, 110.0, cropped)

truth, old, new, old_hard, new_hard = [], [], [], [], []
for images, target in test:
    truth.extend(target.numpy())
    old.extend(baseline(images, training=False).numpy())
    new.extend(candidate(images, training=False).numpy())
    hard = difficult(images)
    old_hard.extend(baseline(hard, training=False).numpy())
    new_hard.extend(candidate(hard, training=False).numpy())
truth = np.asarray(truth)
def accuracy(prob):
    return float((np.asarray(prob).argmax(1) == truth).mean())
report = {'status':'candidate_only', 'baseline_clean':accuracy(old),
    'candidate_clean':accuracy(new), 'baseline_partial':accuracy(old_hard),
    'candidate_partial':accuracy(new_hard), 'test_count':len(truth),
    'epochs':len(history.history['loss']),
    'limitation':'Synthetic partial tests are diagnostic; independent crowded/off-centre phone tests remain required.',
    'per_class':{label:{'count':int((truth==i).sum()),
        'candidate_clean':float((np.asarray(new).argmax(1)[truth==i]==i).mean())}
        for i,label in enumerate(labels)}}
print('EXISTING_V2_FINETUNE_RESULT', json.dumps(report), flush=True)
candidate.save(out/'monument_model.keras')
(out/'monument_model.tflite').write_bytes(tf.lite.TFLiteConverter.from_keras_model(candidate).convert())
(out/'labels.txt').write_text('\n'.join(labels)+'\n')
(out/'metrics.json').write_text(json.dumps(report,indent=2))
folder = api().files().create(body={'name':'existing_MobileNetV2_augmented_finetune',
    'mimeType':'application/vnd.google-apps.folder','parents':[ROOT]},fields='id,webViewLink').execute()
for name in ['monument_model.keras','monument_model.tflite','labels.txt','metrics.json']:
    api().files().create(body={'name':name,'parents':[folder['id']]},
        media_body=MediaFileUpload(str(out/name),resumable=True),fields='id').execute()
print('FINETUNE_SAVED',folder,flush=True)
