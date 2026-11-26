"""Collect licensed Wikimedia Commons previews for visual review."""

from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path


API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "VirasatAI/1.0 (student heritage app; contact via project owner)"


def request(params: dict) -> dict:
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=40) as response:
        return json.load(response)


def download(url: str, path: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as response:
        path.write_bytes(response.read())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("place_id")
    parser.add_argument("category")
    parser.add_argument("--limit", type=int, default=30)
    args = parser.parse_args()
    target = Path(__file__).resolve().parent / "expansion_candidates" / args.place_id
    target.mkdir(parents=True, exist_ok=True)
    members = request({
        "action": "query", "format": "json", "generator": "categorymembers",
        "gcmtitle": "Category:" + args.category, "gcmtype": "file",
        "gcmlimit": min(args.limit, 50), "prop": "imageinfo",
        "iiprop": "url|mime|extmetadata", "iiurlwidth": 1280,
    }).get("query", {}).get("pages", {})
    records = []
    for index, page in enumerate(members.values(), 1):
        info = (page.get("imageinfo") or [{}])[0]
        metadata = info.get("extmetadata") or {}
        url = info.get("thumburl")
        mime = info.get("mime", "")
        if not url or mime not in {"image/jpeg", "image/png"}:
            continue
        record = {
            "candidateId": len(records) + 1,
            "title": page.get("title", ""),
            "sourcePage": info.get("descriptionurl", ""),
            "previewUrl": url,
            "author": (metadata.get("Artist") or {}).get("value", ""),
            "license": (metadata.get("LicenseShortName") or {}).get("value", ""),
            "licenseUrl": (metadata.get("LicenseUrl") or {}).get("value", ""),
        }
        destination = target / f"candidate_{record['candidateId']:02d}.jpg"
        try:
            download(url, destination)
        except Exception as error:
            record["downloadError"] = str(error)
        records.append(record)
        time.sleep(0.12)
    (target / "candidates.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"placeId": args.place_id, "found": len(records), "downloaded": sum("downloadError" not in item for item in records)}))


if __name__ == "__main__":
    main()
