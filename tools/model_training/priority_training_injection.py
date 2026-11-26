# Reviewed source-sheet indices are only candidate selections. This block
# rechecks the Commons identity, license, source hash and near-duplicates
# before accepting images into TRAIN ONLY.
import requests

PRIORITY_FOLDER_ID = "1tYtgfjwCfcbz1ZtQgZRmlnJRyoQHU8zU"
SHORTLIST_ID = "1QROT8lAPHnRXO2CACKx73Gs-TlzrK1If"
CANDIDATE_MANIFEST_IDS = {
    "badami_cave_temples": "1-XBfSOePnPEoo2nS9gZ7F_wx7m8EUfG8",
    "sanchi_stupa": "1IZIO9uQmfRsN1bKudFE3DHGK5KpUfax6",
    "mysore_palace": "1X2-oWa3SHLMkr9og4MgcvaY7szDTX4f9",
    "red_fort": "1vUBJA9Gc0Q38Q-t8HsFio7lvH-sDrnDl",
    "jaisalmer_fort": "1sRaU9KQPLGx8XcaEVuKRJlmOFfFfhdwL",
    "hampi_monuments": "1Tg8U90coHMxFxjt-OS21eOOPM9mf0dDc",
    "konark_sun_temple": "19Ie3IjSF2T4rfFMixC0aOd_dYHjtPLhJ",
}

shortlist = list(csv.DictReader(io.StringIO(fetch(SHORTLIST_ID).decode("utf-8-sig"))))
assert len(shortlist) == 60 and all(r["decision"] == "shortlist" for r in shortlist)
candidate_manifests = {
    label: {str(row["index"]): row for row in json.loads(fetch(file_id))}
    for label, file_id in CANDIDATE_MANIFEST_IDS.items()
}
session = requests.Session()
session.headers.update({"User-Agent": "VirasatAI-student-image-review/1.0 (educational project)"})


def candidate_hash(photo):
    gray = ImageOps.grayscale(photo).resize((9, 8))
    pixels = list(gray.getdata())
    result = 0
    for yy in range(8):
        for xx in range(8):
            result = (result << 1) | (pixels[yy * 9 + xx] > pixels[yy * 9 + xx + 1])
    return result


def get_commons_image(title):
    for attempt in range(6):
        try:
            res = session.get("https://commons.wikimedia.org/w/api.php", params={
                "action": "query", "format": "json", "prop": "imageinfo",
                "titles": title, "iiprop": "url|sha1|size|extmetadata",
                "iiurlwidth": 900}, timeout=45)
            if res.status_code in (429, 500, 502, 503, 504):
                time.sleep(min(60, 5 * (attempt + 1)))
                continue
            res.raise_for_status()
            page = next(iter(res.json()["query"]["pages"].values()))
            return page["imageinfo"][0]
        except (requests.RequestException, KeyError, StopIteration):
            if attempt == 5:
                raise
            time.sleep(min(60, 3 * (attempt + 1)))
    raise RuntimeError("Commons image metadata unavailable")


existing_hashes = [int(r["dhash"], 16) for r in all_rows]
accepted_hashes = []
accepted = []
rejected = []
for item in shortlist:
    label = item["label"]
    source = candidate_manifests[label][item["index"]]
    try:
        assert source["label"] == label
        assert source["license"].startswith(("CC BY", "CC0", "PD", "Public domain"))
        info = get_commons_image(source["title"])
        assert info["sha1"] == source["source_sha1"], "Commons source changed"
        assert min(info["width"], info["height"]) >= 900
        current_license = info.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "")
        assert current_license.startswith(("CC BY", "CC0", "PD", "Public domain"))
        preview_url = info.get("thumburl") or info.get("url")
        response = session.get(preview_url, timeout=60)
        response.raise_for_status()
        with Image.open(io.BytesIO(response.content)) as opened:
            photo = ImageOps.exif_transpose(opened).convert("RGB")
        visual_hash = candidate_hash(photo)
        assert all((visual_hash ^ old).bit_count() > 8 for old in existing_hashes), "near old dataset photo"
        assert all((visual_hash ^ old).bit_count() > 8 for old in accepted_hashes), "near another candidate"
        normalized = ImageOps.pad(photo, (SIDE, SIDE), method=Image.Resampling.LANCZOS,
                                  color=(127, 127, 127))
        dest = ROOT / "images" / "train" / label / ("priority_" + info["sha1"] + ".jpg")
        dest.parent.mkdir(parents=True, exist_ok=True)
        normalized.save(dest, quality=92)
        accepted_hashes.append(visual_hash)
        counts[label, "train"] += 1
        rows.append({"label": label, "split": "train"})
        accepted.append({**source, "reason": item["reason"], "train_path": str(dest),
                         "current_license": current_license})
    except Exception as error:
        rejected.append({"label": label, "index": source["index"],
                         "title": source["title"], "reason": str(error)})
    if (len(accepted) + len(rejected)) % 10 == 0:
        print("PRIORITY_RECHECK", len(accepted), "accepted", len(rejected), "rejected", flush=True)

assert len(accepted) >= 20, "Too few verified additions; inspect rejection list before training"
priority_audit = {"shortlisted": len(shortlist), "accepted": accepted, "rejected": rejected,
                  "warning": "Source-title review and dHash screening are imperfect; do not treat as an independent test."}
audit_path = ROOT / "priority_candidate_audit.json"
audit_path.write_text(json.dumps(priority_audit, indent=2), encoding="utf-8")
print("PRIORITY_DATASET_READY", {"shortlisted": len(shortlist),
                                 "accepted": len(accepted), "rejected": len(rejected),
                                 "train_total": sum(counts[label, "train"] for label in labels)}, flush=True)
