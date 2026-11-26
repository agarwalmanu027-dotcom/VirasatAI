"""Paste in a new cell after evaluate_dinov2_retrieval_colab.py finishes.

Scores 11 previously held-out Commons photos. This is a small web-image check,
not a real phone-photo acceptance test or a 20-class accuracy estimate.
"""

from collections import Counter

HOLDOUT_FOLDERS = {
    "amer_fort": "1xWzqGjNQngSEuGFOMdHE0hcNiTTgvqNi",
    "jaisalmer_fort": "1rMtoCdzjv8ECJAPxsIfSZ4j90iIOXpQE",
    "city_palace_udaipur": "1WzX7-TSezxyhfX6eoIJ9hOAzTuQdAYKi",
    "badami_cave_temples": "19nk5VKLpvhXLlFeobkN6fiX51zKG5w8i",
}
assert winner == "retrieval_3", "Same DINO run required"
assert len(train_x) == 2155 and train_x.shape[1] == 384
assert who == ACCOUNT == "manuagarwal885@gmail.com"

holdout = []
seen_training_hashes = {r["sha256"] for r in rows}
for label, folder_id in HOLDOUT_FOLDERS.items():
    listing = drive.files().list(q=f"'{folder_id}' in parents and trashed = false",
                                 fields="nextPageToken,files(id,name,mimeType)",
                                 pageSize=100).execute()
    assert not listing.get("nextPageToken")
    for item in listing["files"]:
        assert item["mimeType"].startswith("image/")
        data = fetch(item["id"])
        assert hashlib.sha256(data).hexdigest() not in seen_training_hashes
        with Image.open(io.BytesIO(data)) as source:
            photo = ImageOps.pad(ImageOps.exif_transpose(source).convert("RGB"),
                                 (SIDE, SIDE), method=Image.Resampling.LANCZOS,
                                 color=(127, 127, 127))
        path = OUT / "external_11" / label / item["name"]
        path.parent.mkdir(parents=True, exist_ok=True)
        photo.save(path, quality=92)
        holdout.append({"label": label, "name": item["name"], "path": path})
assert len(holdout) == 11, len(holdout)

summary = {"status": "small_external_web_image_check_only", "count": 11,
           "same_runtime_retrieval_method": winner, "results": []}
for view in ("full", "center_70"):
    external_x = embeddings(holdout, view)
    scores = retrieval_prob(external_x, 3)
    for i, item in enumerate(holdout):
        predicted = labels[int(scores[i].argmax())]
        top2 = np.sort(scores[i])[-2:]
        result = {"view": view, "name": item["name"], "actual": item["label"],
                  "predicted": predicted, "correct": predicted == item["label"],
                  "top_two_similarity_margin": float(top2[1] - top2[0])}
        summary["results"].append(result)
        print("EXTERNAL", view, item["label"], "=>", predicted,
              "margin", round(result["top_two_similarity_margin"], 3), flush=True)
    checked = summary["results"][-11:]
    print("EXTERNAL_SUMMARY", view, sum(r["correct"] for r in checked), "/11", flush=True)

(OUT / "external_11_metrics.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
