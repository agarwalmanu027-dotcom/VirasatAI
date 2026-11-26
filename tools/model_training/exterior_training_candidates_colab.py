"""Find NEW Badami/Amer exterior photos for manual training-data review.

Run in Colab only. This does not add images to training or alter any model.
It excludes every original training/validation/test hash and all previously
reviewed Commons candidate titles, including the independent test batch.
"""

import csv, hashlib, io, json, random, time
from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageOps
from google.colab import auth
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

auth.authenticate_user()
credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/drive"])
drive = build("drive", "v3", credentials=credentials, cache_discovery=False)
assert drive.about().get(fields="user(emailAddress)").execute()["user"]["emailAddress"].lower() == "manuagarwal885@gmail.com"
ROOT = "1FL98KnE_e-BigfluYAGfFgLXdXtx9WWT"
OLD_FOLDER = "1XmKmAhfVU48CY-yNgBAUOlafiU5Bz-Ey"
FIRST_REVIEW = "1ut_oVu1n9rI4_bzeQfkZ8pSaxJaRa07o"
INDEPENDENT_REVIEW = "1zjRgf_bQsxoBLLzIfqF41ywsVJChZD8q"
MIME_FOLDER = "application/vnd.google-apps.folder"
BASE = Path("/content/virasatai_exterior_training_review")
BASE.mkdir(exist_ok=True)

def children(folder):
    items, token = [], None
    while True:
        page = drive.files().list(q=f"'{folder}' in parents and trashed = false", pageSize=1000,
                                  pageToken=token, fields="nextPageToken,files(id,name,mimeType)").execute()
        items += page.get("files", [])
        token = page.get("nextPageToken")
        if not token: return items

def media(file_id): return drive.files().get_media(fileId=file_id).execute()

old_files = {x["name"]: x["id"] for x in children(OLD_FOLDER)}
old_hashes = []
with io.StringIO(media(old_files["manifest.csv"]).decode()) as f:
    for row in csv.DictReader(f): old_hashes.append(int(row["dhash"], 16))
old_candidates = json.loads(media(FIRST_REVIEW))
test_candidates = json.loads(media(INDEPENDENT_REVIEW))
seen_titles = {x["title"] for x in old_candidates + test_candidates}
seen_sha = {x.get("sha1") or x.get("source_sha1") for x in old_candidates + test_candidates}

session = requests.Session()
session.headers.update({"User-Agent": "VirasatAI-student-dataset/1.0 (educational visual review)"})

def query(params):
    for attempt in range(6):
        r = session.get("https://commons.wikimedia.org/w/api.php", params={"format":"json", **params}, timeout=40)
        if r.status_code in (429, 503):
            time.sleep(min(50, 5 * (attempt + 1)))
            continue
        r.raise_for_status(); return r.json()
    raise RuntimeError("Commons rate limit. Resume later without changing current data.")

def titles(category):
    result, token = [], None
    while True:
        params = {"action":"query", "list":"categorymembers", "cmtitle":category,
                  "cmtype":"file", "cmlimit":"max"}
        if token: params["cmcontinue"] = token
        data = query(params)
        result += [x["title"] for x in data["query"]["categorymembers"]]
        token = data.get("continue", {}).get("cmcontinue")
        if not token: return result

def info_batch(titles_list):
    for start in range(0, len(titles_list), 40):
        data = query({"action":"query", "prop":"imageinfo", "titles":"|".join(titles_list[start:start+40]),
                      "iiprop":"url|size|sha1|extmetadata", "iiurlwidth":800})
        for page in data["query"]["pages"].values():
            if page.get("imageinfo"): yield page["title"], page["imageinfo"][0]

def dhash(image):
    grey = ImageOps.grayscale(image).resize((9,8)); p = list(grey.getdata()); h = 0
    for r in range(8):
        for c in range(8): h = (h << 1) | (p[r*9+c] > p[r*9+c+1])
    return h

categories = {
  "badami_cave_temples": ["Category:Exterior of the Badami Cave Temples",
                          "Category:Exterior of the Badami cave temple 4"],
  "amer_fort": ["Category:Exterior of the Amber Fort"],
}
accepted = []
new_hashes = []
for label, cats in categories.items():
    pool = []
    for cat in cats:
        pool += [t for t in titles(cat) if t not in seen_titles]
        time.sleep(1)
    pool = list(dict.fromkeys(pool))
    random.Random(7805).shuffle(pool)
    for title, info in info_batch(pool):
        if sum(x["label"] == label for x in accepted) >= 24: break
        license_name = info.get("extmetadata",{}).get("LicenseShortName",{}).get("value","")
        if not license_name.startswith(("CC BY", "CC0", "PD", "Public domain")): continue
        if info.get("sha1") in seen_sha: continue
        if min(info.get("width",0), info.get("height",0)) < 640: continue
        if any(t in title.lower() for t in ("map", "layout", "drawing", "sketch", "poster", "painting", "collage")): continue
        if not info.get("thumburl"): continue
        try:
            r = session.get(info["thumburl"], timeout=40)
            r.raise_for_status()
            im = Image.open(io.BytesIO(r.content)).convert("RGB")
            h = dhash(im)
            if any((h ^ old).bit_count() < 8 for old in old_hashes + new_hashes): continue
            new_hashes.append(h)
            idx = sum(x["label"] == label for x in accepted)
            path = BASE / f"{label}_{idx:02d}.jpg"
            im.save(path, quality=86)
            accepted.append({"label":label,"index":idx,"title":title,"source_sha1":info.get("sha1"),
                             "source_page":"https://commons.wikimedia.org/wiki/"+title.replace(" ","_"),
                             "license":license_name,"preview":str(path),"dhash":f"{h:016x}",
                             "status":"needs_manual_review"})
            time.sleep(0.7)
        except (requests.RequestException, OSError) as exc:
            print("SKIP", label, title, str(exc)[:80], flush=True)
    subset = [x for x in accepted if x["label"] == label]
    sheet = Image.new("RGB", (6*190, 4*210), "white")
    pen = ImageDraw.Draw(sheet)
    for x in subset:
        col,row = x["index"]%6, x["index"]//6
        left,top = col*190,row*210
        with Image.open(x["preview"]) as im:
            sheet.paste(ImageOps.fit(im,(180,170)),(left,top))
        pen.text((left+3,top+174), f"{x['index']}: {x['title'][5:25]}", fill="black")
    sheet.save(BASE / f"{label}_exterior_training_candidates.jpg", quality=86)
    print("EXTERIOR_REVIEW", label, len(subset), flush=True)

manifest = BASE / "exterior_training_candidate_manifest.json"
manifest.write_text(json.dumps(accepted,indent=2), encoding="utf-8")
prior = [x for x in children(ROOT) if x["name"] == "exterior_training_review_2026-10-16" and x["mimeType"] == MIME_FOLDER]
folder = prior[0]["id"] if prior else drive.files().create(body={"name":"exterior_training_review_2026-10-16",
                       "mimeType":MIME_FOLDER,"parents":[ROOT]},fields="id").execute()["id"]
existing = {x["name"] for x in children(folder)}
for path in BASE.glob("*_exterior_training_candidates.jpg"):
    if path.name not in existing:
        drive.files().create(body={"name":path.name,"parents":[folder]},
                             media_body=MediaFileUpload(str(path)), fields="id").execute()
if manifest.name not in existing:
    drive.files().create(body={"name":manifest.name,"parents":[folder]},
                         media_body=MediaFileUpload(str(manifest)), fields="id").execute()
print("EXTERIOR_REVIEW_READY", json.dumps({"folder":folder,"counts":{k:sum(x["label"]==k for x in accepted) for k in categories}}),flush=True)
