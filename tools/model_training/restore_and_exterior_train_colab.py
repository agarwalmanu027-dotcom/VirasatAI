"""Resume the 20-class candidate experiment after a Colab runtime reset.

Run ONLY in Colab signed in as the 885 account. Downloads the original 3,141
prepared source images to transient Colab storage using the saved split manifest;
never downloads them to the laptop. The 19 reviewed exterior photos are added
to TRAIN only. Original validation/test images and the baseline model stay fixed.
"""

import csv, hashlib, io, json, random, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import google.auth
from google.colab import auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from PIL import Image, ImageOps
import numpy as np
import tensorflow as tf

ACCOUNT = 'manuagarwal885@gmail.com'
ROOT = '1FL98KnE_e-BigfluYAGfFgLXdXtx9WWT'
MANIFEST_ID = '1hd0mq6BPeJ1N0J_f7F_HOXsUnwmxHeVZ'
MODEL_ID = '1EL2Rv78lhgnDP-74AH5i8G51Pt-nO0Y1'
LABELS_ID = '1_z0LWgDroeVRHrm2bAz5IvrkZEWESW6-'
SELECTED_FOLDER = '1ojMtNoslOfWcQvRdxiklKHmo4sKRMwmr'
SELECTION_MANIFEST = '1YUh7lyn5q0Wn2EROdv83P24W59JEkbpz'
LOCAL = Path('/content/virasatai_exterior_restore')
PREPARED = LOCAL / 'prepared'
LOCAL.mkdir(exist_ok=True)
auth.authenticate_user()
creds, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/drive'])
local = threading.local()
def api():
    if not hasattr(local, 'service'):
        local.service = build('drive', 'v3', credentials=creds, cache_discovery=False)
    return local.service
who = api().about().get(fields='user(emailAddress)').execute()['user']['emailAddress'].lower()
assert who == ACCOUNT, f'Wrong Google account: {who}'
def fetch(file_id):
    for attempt in range(5):
        try:
            return api().files().get_media(fileId=file_id).execute()
        except Exception:
            if attempt == 4: raise
            time.sleep(min(30, 2 ** attempt + random.random()))
def children(folder):
    result, token = [], None
    while True:
        page = api().files().list(q=f"'{folder}' in parents and trashed = false",
            pageSize=1000, pageToken=token, fields='nextPageToken,files(id,name,mimeType)').execute()
        result += page.get('files', [])
        token = page.get('nextPageToken')
        if not token: return result

manifest = list(csv.DictReader(io.StringIO(fetch(MANIFEST_ID).decode('utf-8'))))
labels = fetch(LABELS_ID).decode('utf-8').splitlines()
assert len(manifest) == 3141 and len(labels) == 20
assert all(x['split'] in ('train','val','test') and x['label'] in labels for x in manifest)
print('RESTORE_START', {'photos':len(manifest),'labels':len(labels)}, flush=True)

def restore(row):
    path = PREPARED / row['split'] / row['label'] / (row['sha256'][:20] + '.jpg')
    if path.exists(): return 'present'
    raw = fetch(row['file_id'])
    if hashlib.sha256(raw).hexdigest() != row['sha256']:
        raise ValueError(f"Source changed: {row['file_id']}")
    with Image.open(io.BytesIO(raw)) as source:
        image = ImageOps.fit(ImageOps.exif_transpose(source).convert('RGB'),
                             (160,160), method=Image.Resampling.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, quality=88)
    return 'restored'

errors = []
with ThreadPoolExecutor(max_workers=12) as pool:
    jobs = {pool.submit(restore,row):row for row in manifest}
    restored = 0
    for n, job in enumerate(as_completed(jobs),1):
        try: restored += job.result() == 'restored'
        except Exception as exc: errors.append((jobs[job]['file_id'], str(exc)))
        if n % 200 == 0 or n == len(jobs):
            print('RESTORE_PROGRESS', n, len(jobs), 'restored', restored,
                  'errors', len(errors), flush=True)
if errors:
    raise RuntimeError(f'Restore incomplete; rerun this cell to resume: {errors[:5]}')

decisions = json.loads(fetch(SELECTION_MANIFEST))
approved = [x for x in decisions if x['status']=='visually_approved_for_training_preview']
files = {x['name']:x['id'] for x in children(SELECTED_FOLDER)}
assert len(approved) == 19 and len(files) == 19
for x in approved:
    name = f"{x['label']}_{x['index']:02d}.jpg"
    data = fetch(files[name])
    with Image.open(io.BytesIO(data)) as im:
        image = ImageOps.fit(im.convert('RGB'), (160,160))
    target = PREPARED/'train'/x['label']/f"exterior_{x['source_sha1']}.jpg"
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists(): image.save(target,quality=88)
print('TRAIN_ONLY_EXTERIORS', len(approved), flush=True)

def dataset(split, shuffle):
    ds = tf.keras.utils.image_dataset_from_directory(PREPARED/split,
        class_names=labels,image_size=(160,160),batch_size=32,
        label_mode='int',shuffle=shuffle,seed=42)
    return ds.prefetch(tf.data.AUTOTUNE)
train, val, test = dataset('train',True), dataset('val',False), dataset('test',False)
model_path = LOCAL/'baseline_model.keras'
if not model_path.exists(): model_path.write_bytes(fetch(MODEL_ID))
baseline = tf.keras.models.load_model(model_path)
candidate = tf.keras.models.load_model(model_path)
candidate.compile(optimizer=tf.keras.optimizers.Adam(5e-6),
                  loss='sparse_categorical_crossentropy',metrics=['accuracy'])
history = candidate.fit(train,validation_data=val,epochs=3,verbose=2,
    callbacks=[tf.keras.callbacks.EarlyStopping(monitor='val_loss',patience=1,
                                                  restore_best_weights=True)])
y = np.concatenate([batch.numpy() for _,batch in test])
old = baseline.predict(test,verbose=0).argmax(1)
new = candidate.predict(test,verbose=0).argmax(1)
report = {'status':'candidate_only','train_added':19,'test_count':len(y),
  'baseline_correct':int((old==y).sum()),'candidate_correct':int((new==y).sum()),
  'baseline_accuracy':float((old==y).mean()),
  'candidate_accuracy':float((new==y).mean()),
  'validation_loss':[float(v) for v in history.history['val_loss']],
  'per_focus_class':{
     label:{'total':int((y==labels.index(label)).sum()),
            'baseline_correct':int(((y==labels.index(label)) & (old==y)).sum()),
            'candidate_correct':int(((y==labels.index(label)) & (new==y)).sum())}
     for label in ('badami_cave_temples','amer_fort')},
  'limitation':'Original test influenced class selection. Separate independent photo and phone tests required before APK integration.'}
print('EXTERIOR_CANDIDATE_RESULT',json.dumps(report),flush=True)
output = LOCAL/'candidate'; output.mkdir(exist_ok=True)
(output/'metrics.json').write_text(json.dumps(report,indent=2))
(output/'labels.txt').write_text('\n'.join(labels)+'\n')
candidate.save(output/'monument_model.keras')
prior = [x for x in children(ROOT) if x['name']=='exterior_finetune_candidate_2026-10-16']
folder = prior[0]['id'] if prior else api().files().create(body={'name':'exterior_finetune_candidate_2026-10-16',
    'mimeType':'application/vnd.google-apps.folder','parents':[ROOT]},fields='id').execute()['id']
existing = {x['name'] for x in children(folder)}
for path in output.iterdir():
    if path.name not in existing:
        api().files().create(body={'name':path.name,'parents':[folder]},
            media_body=MediaFileUpload(str(path),resumable=True),fields='id').execute()
print('EXTERIOR_CANDIDATE_SAVED',folder,flush=True)
