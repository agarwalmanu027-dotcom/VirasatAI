"""Download exact Wikimedia Commons files from saved source plans for visual review."""

from __future__ import annotations

import argparse
import html
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "tools" / "image_review"
API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "VirasatAI/1.0 (student heritage app; visual source review)"


def clean(value: str) -> str:
    return re.sub(r"<[^>]+>", "", html.unescape(value or "")).strip()


def api(params: dict) -> dict:
    request = urllib.request.Request(
        API + "?" + urllib.parse.urlencode(params),
        headers={"User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.load(response)


def download(url: str, path: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=75) as response:
        path.write_bytes(response.read())


def plans() -> dict[str, dict]:
    merged: dict[str, dict] = {}
    for name in (
        "additional_niche_rescue_plan.json",
        "all_exact_rescue_collect_plan.json",
        "zero_rescue_source_plan.json",
    ):
        data = json.loads((REVIEW / name).read_text(encoding="utf-8-sig"))
        for row in data:
            if row.get("exact_files"):
                merged[row["place_id"]] = row
    return merged


def collect(place_id: str, row: dict) -> None:
    titles = list(dict.fromkeys(row["exact_files"]))
    target = REVIEW / "exact_zero_candidates" / place_id
    target.mkdir(parents=True, exist_ok=True)
    records = []
    for start in range(0, len(titles), 50):
        result = api({
            "action": "query", "format": "json", "formatversion": 2,
            "titles": "|".join(titles[start:start + 50]), "prop": "imageinfo",
            "iiprop": "url|mime|size|extmetadata", "iiurlwidth": 1280,
        })
        for page in result.get("query", {}).get("pages", []):
            info = (page.get("imageinfo") or [{}])[0]
            metadata = info.get("extmetadata") or {}
            url = info.get("thumburl")
            if page.get("missing") or not url:
                records.append({"title": page.get("title", ""), "error": "missing"})
                continue
            record = {
                "candidateId": len(records) + 1,
                "title": page.get("title", ""),
                "sourcePage": info.get("descriptionurl", ""),
                "previewUrl": url,
                "originalWidth": info.get("width"),
                "originalHeight": info.get("height"),
                "author": clean((metadata.get("Artist") or {}).get("value", "")),
                "license": clean((metadata.get("LicenseShortName") or {}).get("value", "")),
                "licenseUrl": (metadata.get("LicenseUrl") or {}).get("value", ""),
            }
            destination = target / f"candidate_{record['candidateId']:02d}.jpg"
            try:
                download(url, destination)
                record["previewPath"] = str(destination.relative_to(ROOT)).replace("\\", "/")
            except Exception as error:
                record["error"] = str(error)
            records.append(record)
            time.sleep(0.15)
    (target / "candidates.json").write_text(
        json.dumps({"placeId": place_id, "displayName": row.get("display_name"), "candidates": records}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"placeId": place_id, "requested": len(titles), "downloaded": sum("previewPath" in x for x in records)}))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--place", action="append", required=True)
    args = parser.parse_args()
    known = plans()
    for place_id in args.place:
        collect(place_id, known[place_id])


if __name__ == "__main__":
    main()
