"""Add one visually verified, licensed local candidate to the offline gallery."""

import argparse
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "frontend_recovered/assets/data/guide_catalog.json"
LIBRARY = ROOT / "frontend_recovered/assets/images/guide_library"
MANIFEST = LIBRARY / "REVIEWED_GALLERY_MANIFEST.json"
CREDITS = LIBRARY / "NEW_GALLERY_CREDITS.md"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("place_id")
    parser.add_argument("candidate_id", type=int)
    args = parser.parse_args()
    source_dir = ROOT / "tools/image_review/candidates" / args.place_id
    candidates = json.loads((source_dir / "candidates.json").read_text(encoding="utf-8"))["candidates"]
    candidate = next(item for item in candidates if item["candidate_id"] == args.candidate_id)
    if not candidate["license"].lower().startswith(("cc ", "public domain", "cc0")):
        raise ValueError("License requires manual review")
    source = source_dir / f"candidate_{args.candidate_id:02d}.jpg"
    if not source.is_file():
        raise FileNotFoundError(source)
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    place = next(entry for entry in catalog["entries"] if entry["id"] == args.place_id)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if any(image.get("sourcePage") == candidate["source_page"] for image in manifest["images"]):
        raise ValueError("Source already imported")
    index = len(place["photos"]) + 1
    name = f"{args.place_id}_{index:02d}.jpg"
    destination = LIBRARY / name
    if destination.exists():
        raise FileExistsError(destination)
    shutil.copyfile(source, destination)
    asset = f"assets/images/guide_library/{name}"
    place["photos"].append(asset)
    manifest["images"].append({
        "placeId": args.place_id, "asset": asset, "candidateId": args.candidate_id,
        "title": candidate["title"], "sourcePage": candidate["source_page"],
        "author": candidate["author"], "license": candidate["license"],
        "licenseUrl": candidate["license_url"],
    })
    manifest["totalRecorded"] = len(manifest["images"])
    manifest["addedInLatestRun"] = 1
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with CREDITS.open("a", encoding="utf-8") as output:
        output.write(f"\n| {name} | {candidate['author']} | "
                     f"[{candidate['title']}]({candidate['source_page']}) | {candidate['license']} |\n")
    print(asset)


if __name__ == "__main__":
    main()
