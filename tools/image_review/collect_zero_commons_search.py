"""Collect Wikimedia Commons search previews for still-empty nearby places."""

from __future__ import annotations

import html
import json
import re
import time
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "tools" / "image_review"
CATALOG = ROOT / "frontend_recovered" / "assets" / "data" / "guide_catalog.json"
API = "https://commons.wikimedia.org/w/api.php"
AGENT = "VirasatAI/1.0 (student heritage app; visual review)"


def clean(value: str) -> str:
    return re.sub(r"<[^>]+>", "", html.unescape(value or "")).strip()


def request(params: dict) -> dict:
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers={"User-Agent": AGENT})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=45) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == 4:
                raise
            time.sleep(4 * (attempt + 1))
    raise RuntimeError("Commons API request failed")


def fetch(url: str, path: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": AGENT})
    with urllib.request.urlopen(req, timeout=60) as response:
        path.write_bytes(response.read())


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))["entries"]
    groups = {x["id"]: x for x in catalog}
    empty = [x for x in catalog if x["id"] != x["groupId"] and not x.get("photos")]
    root = REVIEW / "zero_search_candidates"
    root.mkdir(exist_ok=True)
    for entry in empty:
        place_id = entry["id"]
        target = root / place_id
        target.mkdir(exist_ok=True)
        if (target / "candidates.json").exists():
            continue
        location = entry.get("location", "")
        group = groups[entry["groupId"]]["name"]
        query = f'"{entry["name"]}" {location or group} filetype:bitmap'
        result = request({
            "action": "query", "format": "json", "formatversion": 2,
            "generator": "search", "gsrnamespace": 6, "gsrlimit": 15,
            "gsrsearch": query, "prop": "imageinfo",
            "iiprop": "url|mime|size|extmetadata", "iiurlwidth": 1280,
        })
        records = []
        for page in result.get("query", {}).get("pages", []):
            info = (page.get("imageinfo") or [{}])[0]
            if not info.get("thumburl") or info.get("mime") not in {"image/jpeg", "image/png"}:
                continue
            meta = info.get("extmetadata") or {}
            row = {
                "candidateId": len(records) + 1, "title": page.get("title", ""),
                "sourcePage": info.get("descriptionurl", ""), "previewUrl": info["thumburl"],
                "author": clean((meta.get("Artist") or {}).get("value", "")),
                "license": clean((meta.get("LicenseShortName") or {}).get("value", "")),
                "licenseUrl": (meta.get("LicenseUrl") or {}).get("value", ""),
            }
            path = target / f"candidate_{row['candidateId']:02d}.jpg"
            try:
                fetch(row["previewUrl"], path)
                row["previewPath"] = str(path.relative_to(ROOT)).replace("\\", "/")
            except Exception as error:
                row["error"] = str(error)
            records.append(row)
            time.sleep(0.08)
        (target / "candidates.json").write_text(json.dumps({
            "placeId": place_id, "displayName": entry["name"], "query": query, "candidates": records,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"placeId": place_id, "found": len(records)}))
        time.sleep(1.0)


if __name__ == "__main__":
    main()
