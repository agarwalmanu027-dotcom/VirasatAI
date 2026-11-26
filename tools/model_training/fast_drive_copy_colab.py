"""Run this in Google Colab as manuagarwal885@gmail.com.

Server-side, resumable copy of the shared VirasatAI raw image tree. This does
not download image bytes to Colab or to the user's computer.
"""

from collections import Counter, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import random
import threading
import time

from google.colab import auth
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SOURCE_ID = "1Yv06Qg3Pnw94NUkek_oWKxlz83bt87oq"
DEST_ID = "1oIFKrlUqwO5tMoHbrtNesmJ8ix5FcNFE"
EXPECTED_EMAIL = "manuagarwal885@gmail.com"
FOLDER_MIME = "application/vnd.google-apps.folder"
MAX_WORKERS = 16
MAX_RETRIES = 8

auth.authenticate_user()
credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/drive"])
local = threading.local()


def drive():
    """Give each worker its own HTTP client; discovery clients are not thread-safe."""
    if not hasattr(local, "service"):
        local.service = build("drive", "v3", credentials=credentials,
                              cache_discovery=False)
    return local.service


def call(request_factory):
    for attempt in range(MAX_RETRIES):
        try:
            return request_factory().execute()
        except HttpError as exc:
            status = int(exc.resp.status)
            detail = exc.content.decode("utf-8", errors="replace")
            limited = status in (429, 500, 502, 503, 504) or (
                status == 403 and any(s in detail for s in (
                    "rateLimitExceeded", "userRateLimitExceeded", "backendError")))
            if not limited or attempt == MAX_RETRIES - 1:
                raise
            wait = min(60, 2 ** attempt + random.random())
            time.sleep(wait)


account = call(lambda: drive().about().get(fields="user(emailAddress)"))
email = account["user"]["emailAddress"].lower()
if email != EXPECTED_EMAIL:
    raise RuntimeError(f"Wrong Google account: {email}. Sign in as {EXPECTED_EMAIL}.")

for label, folder_id in (("Source", SOURCE_ID), ("Destination", DEST_ID)):
    meta = call(lambda fid=folder_id: drive().files().get(
        fileId=fid, fields="id,name,mimeType", supportsAllDrives=True))
    if meta["mimeType"] != FOLDER_MIME:
        raise RuntimeError(f"{label} is not a folder: {meta}")
    print(f"{label}: {meta['name']}")


def children(folder_id):
    result = []
    token = None
    while True:
        response = call(lambda: drive().files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            pageSize=1000,
            pageToken=token,
            fields="nextPageToken,files(id,name,mimeType,size)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True))
        result.extend(response.get("files", []))
        token = response.get("nextPageToken")
        if not token:
            return result


def make_folder(name, parent_id):
    response = call(lambda: drive().files().create(
        body={"name": name, "mimeType": FOLDER_MIME, "parents": [parent_id]},
        fields="id", supportsAllDrives=True))
    return response["id"]


# First build a plan. Existing same-name-and-size files are skipped so a
# disconnected Colab session can simply be run again.
pending = []
folder_queue = deque([(SOURCE_ID, DEST_ID)])
folder_count = 0
source_count = 0
existing_count = 0
while folder_queue:
    source_folder, dest_folder = folder_queue.popleft()
    source_children = children(source_folder)
    dest_children = children(dest_folder)
    folder_count += 1

    destination_folders = {
        item["name"]: item["id"] for item in dest_children
        if item["mimeType"] == FOLDER_MIME
    }
    existing_files = Counter(
        (item["name"], item.get("size", "")) for item in dest_children
        if item["mimeType"] != FOLDER_MIME
    )

    for item in source_children:
        if item["mimeType"] == FOLDER_MIME:
            target = destination_folders.get(item["name"])
            if target is None:
                target = make_folder(item["name"], dest_folder)
                destination_folders[item["name"]] = target
            folder_queue.append((item["id"], target))
        else:
            source_count += 1
            key = (item["name"], item.get("size", ""))
            if existing_files[key] > 0:
                existing_files[key] -= 1
                existing_count += 1
            else:
                pending.append((item["id"], item["name"], dest_folder))

print(f"Scanned {folder_count} folders. Source files: {source_count}.")
print(f"Already present: {existing_count}. Still to copy: {len(pending)}.")


def copy_one(task):
    file_id, name, parent_id = task
    call(lambda: drive().files().copy(
        fileId=file_id,
        body={"name": name, "parents": [parent_id]},
        fields="id", supportsAllDrives=True))
    return name


started = time.monotonic()
done = 0
failures = []
if pending:
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(copy_one, task): task for task in pending}
        for future in as_completed(futures):
            try:
                future.result()
                done += 1
            except Exception as exc:
                task = futures[future]
                failures.append((task[1], str(exc)[:300]))
            finished = done + len(failures)
            if finished % 100 == 0 or finished == len(pending):
                elapsed = max(1, time.monotonic() - started)
                rate = finished / elapsed
                remaining_hours = (len(pending) - finished) / max(rate, 0.001) / 3600
                print(f"Processed {finished:,}/{len(pending):,}; "
                      f"success {done:,}, errors {len(failures):,}; "
                      f"current ETA {remaining_hours:.1f} h", flush=True)

print(f"Finished this run: {done:,} copied; {len(failures):,} errors.")
if failures:
    print("First errors:", json.dumps(failures[:10], ensure_ascii=False, indent=2))
    print("After fixing the cause, run this cell again; existing files are skipped.")
else:
    print("COPY COMPLETE. Verify the folder count before curating images.")
