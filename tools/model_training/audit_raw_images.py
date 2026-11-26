"""Inventory raw monument photos without modifying them."""

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from PIL import Image, UnidentifiedImageError


def audit(root: Path) -> dict:
    report = {"root": str(root), "monuments": {}, "exact_duplicates": [], "bad_files": []}
    hashes = defaultdict(list)
    for monument in sorted(p for p in root.iterdir() if p.is_dir()):
        stats = {"files": 0, "small_under_400px": 0, "formats": {}}
        for path in monument.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
                continue
            stats["files"] += 1
            try:
                with Image.open(path) as image:
                    image.verify()
                with Image.open(path) as image:
                    width, height = image.size
                    fmt = image.format or "unknown"
                if min(width, height) < 400:
                    stats["small_under_400px"] += 1
                stats["formats"][fmt] = stats["formats"].get(fmt, 0) + 1
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                hashes[digest].append(str(path.relative_to(root)))
            except (OSError, ValueError, UnidentifiedImageError) as exc:
                report["bad_files"].append({"path": str(path.relative_to(root)), "error": str(exc)})
        report["monuments"][monument.name] = stats
    report["exact_duplicates"] = [paths for paths in hashes.values() if len(paths) > 1]
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error(f"Folder not found: {args.root}")
    result = audit(args.root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"monuments": len(result["monuments"]), "files": sum(x["files"] for x in result["monuments"].values()), "duplicate_groups": len(result["exact_duplicates"]), "bad_files": len(result["bad_files"]) }))
