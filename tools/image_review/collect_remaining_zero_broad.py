"""Collect broad Wikimedia Commons candidates for the final zero-photo places.

The queries are intentionally curated per place. Results remain review candidates;
nothing is added to the app until it has been visually checked.
"""

from __future__ import annotations

import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "tools" / "image_review"
API = "https://commons.wikimedia.org/w/api.php"
AGENT = "VirasatAI/1.0 (student heritage app; visual review)"

QUERIES = {
    "amer_fort__vidyadhar_garden": ["Vidyadhar Garden Jaipur", "Vidhyadhar garden Jaipur"],
    "amer_fort__sagar_lake": ["Sagar Lake Amer Jaipur", "Sagar Amer fort Jaipur"],
    "amer_fort__hathni_kund": ["Hathni Kund Jaipur", "Hathni Kund Amer Jaipur"],
    "red_fort__chunnamal_haveli": ["Chunnamal Haveli Delhi", "Chunna Mal Haveli Chandni Chowk"],
    "red_fort__naughara_kinari_bazaar": ["Naughara Delhi", "Nau Ghara Kinari Bazaar", "Naughara Jain temple Delhi"],
    "mysore_palace__kishkindha_moolika_bonsai_garden": ["Kishkindha Moolika Bonsai Garden", "Mysore bonsai garden"],
    "mysore_palace__gun_house": ["Gun House Mysore", "Gun House Mysuru"],
    "mysore_palace__karanji_lake_aviary": ["Karanji Lake aviary", "Karanji Lake Mysore"],
    "meenakshi_temple__vilachery_pottery_village": ["Vilachery pottery", "Vilacheri pottery Madurai"],
    "golden_temple__gurdwara_mata_kaulan": ["Gurdwara Mata Kaulan", "Kaulsar Sarovar Amritsar", "Gurdwara Kaulsar Sahib"],
    "khajuraho_monuments__ken_gharial_sanctuary": ["Ken Gharial Sanctuary", "Ken Ghariyal Sanctuary Panna"],
    "konark_sun_temple__kuruma_buddhist_site": ["Kuruma Buddhist site Odisha", "Kuruma Buddhism Odisha"],
    "konark_sun_temple__astaranga_beach": ["Astaranga beach Odisha", "Astranga beach Odisha"],
    "sanchi_stupa__sonari_stupas": ["Sonari stupas Madhya Pradesh", "Sonari Buddhist stupas"],
    "sanchi_stupa__andher_stupas": ["Andher stupas Madhya Pradesh", "Andher Buddhist site Sanchi"],
    "sanchi_stupa__halali_dam": ["Halali Dam Madhya Pradesh", "Halali reservoir Bhopal"],
    "mahabalipuram__poonjeri_village": ["Poonjeri village", "Poonjeri Mahabalipuram"],
    "jaisalmer_fort__akal_wood_fossil_park": ["Akal Wood Fossil Park", "Akal fossil park Jaisalmer"],
    "mehrangarh_fort__balsamand_lake": ["Balsamand Lake Jodhpur", "Bal Samand Lake"],
    "mehrangarh_fort__machia_biological_park": ["Machia Biological Park", "Machiya Safari Park Jodhpur"],
    "mehrangarh_fort__singhasni_village": ["Singhasni pottery Jodhpur", "Singhasni village Rajasthan"],
    "mehrangarh_fort__navchowkiya": ["Navchowkiya Jodhpur", "Navchokiya blue city Jodhpur"],
}


def clean(value: str) -> str:
    return re.sub(r"<[^>]+>", "", html.unescape(value or "")).strip()


def request(params: dict) -> dict:
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers={"User-Agent": AGENT})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=50) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == 4:
                raise
            time.sleep(3 * (attempt + 1))
    raise RuntimeError("Commons API request failed")


def fetch(url: str, path: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": AGENT})
    with urllib.request.urlopen(req, timeout=60) as response:
        path.write_bytes(response.read())


def main() -> None:
    root = REVIEW / "remaining_zero_broad"
    root.mkdir(exist_ok=True)
    for place_id, queries in QUERIES.items():
        target = root / place_id
        target.mkdir(exist_ok=True)
        if (target / "candidates.json").exists():
            continue
        records, seen = [], set()
        for query in queries:
            result = request({
                "action": "query", "format": "json", "formatversion": 2,
                "generator": "search", "gsrnamespace": 6, "gsrlimit": 30,
                "gsrsearch": query, "prop": "imageinfo",
                "iiprop": "url|mime|size|extmetadata", "iiurlwidth": 1280,
            })
            for page in result.get("query", {}).get("pages", []):
                info = (page.get("imageinfo") or [{}])[0]
                title = page.get("title", "")
                if title in seen or not info.get("thumburl") or info.get("mime") not in {"image/jpeg", "image/png"}:
                    continue
                seen.add(title)
                meta = info.get("extmetadata") or {}
                records.append({
                    "candidateId": len(records) + 1, "title": title, "query": query,
                    "sourcePage": info.get("descriptionurl", ""), "previewUrl": info["thumburl"],
                    "author": clean((meta.get("Artist") or {}).get("value", "")),
                    "license": clean((meta.get("LicenseShortName") or {}).get("value", "")),
                    "licenseUrl": (meta.get("LicenseUrl") or {}).get("value", ""),
                })
            time.sleep(.3)
        for row in records:
            path = target / f"candidate_{row['candidateId']:02d}.jpg"
            try:
                fetch(row["previewUrl"], path)
                row["previewPath"] = str(path.relative_to(ROOT)).replace("\\", "/")
            except Exception as error:
                row["error"] = str(error)
            time.sleep(.05)
        (target / "candidates.json").write_text(json.dumps({
            "placeId": place_id, "queries": queries, "candidates": records,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"placeId": place_id, "found": len(records)}))


if __name__ == "__main__":
    main()
