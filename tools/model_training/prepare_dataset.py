"""Build a reproducible monument-classification dataset from reviewed photos.

Only files placed under 05_AI_Dataset/Monument_Recognition/<class>/ are used.
The original photos are never changed. Nearby_Heritage is deliberately excluded.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import sys
from pathlib import Path

from PIL import Image, UnidentifiedImageError


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
EXCLUDED_PARTS = {"nearby_heritage", "nearby_places", "gallery", "display", "rejected"}
PROJECT = Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect(source: Path, minimum: int) -> tuple[dict[str, list[dict]], list[dict], list[dict]]:
    classes: dict[str, list[dict]] = {}
    rejected: list[dict] = []
    duplicates: list[dict] = []
    seen_hashes: dict[str, tuple[str, str]] = {}

    for class_dir in sorted(p for p in source.iterdir() if p.is_dir()):
        label = class_dir.name
        entries: list[dict] = []
        for path in sorted(class_dir.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            relative = path.relative_to(class_dir)
            if any(part.lower() in EXCLUDED_PARTS for part in relative.parts[:-1]):
                rejected.append({"path": str(path), "reason": "excluded display/nearby folder"})
                continue
            try:
                with Image.open(path) as image:
                    image.verify()
                with Image.open(path) as image:
                    width, height = image.size
                if min(width, height) < minimum:
                    rejected.append({"path": str(path), "reason": f"too small: {width}x{height}"})
                    continue
            except (UnidentifiedImageError, OSError, ValueError) as error:
                rejected.append({"path": str(path), "reason": f"unreadable: {error}"})
                continue
            digest = sha256(path)
            if digest in seen_hashes:
                first_label, first_path = seen_hashes[digest]
                duplicates.append({"path": str(path), "first_path": first_path,
                                   "first_class": first_label, "class": label})
                continue
            seen_hashes[digest] = (label, str(path))
            entries.append({"path": str(path), "sha256": digest, "width": width,
                            "height": height, "label": label})
        if entries:
            classes[label] = entries
    return classes, rejected, duplicates


def assign_splits(classes: dict[str, list[dict]], seed: int) -> list[dict]:
    rng = random.Random(seed)
    rows: list[dict] = []
    for label, entries in sorted(classes.items()):
        items = entries.copy()
        rng.shuffle(items)
        n = len(items)
        test_count = max(1, round(n * 0.15))
        val_count = max(1, round(n * 0.15))
        for index, entry in enumerate(items):
            split = "test" if index < test_count else "val" if index < test_count + val_count else "train"
            rows.append({**entry, "split": split})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=PROJECT / "05_AI_Dataset" / "Monument_Recognition")
    parser.add_argument("--output", type=Path,
                        default=PROJECT / "05_AI_Dataset" / "prepared_monuments")
    parser.add_argument("--minimum-side", type=int, default=224)
    parser.add_argument("--minimum-per-class", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--write", action="store_true",
                        help="Create a resized JPEG dataset; default only audits and prints a report")
    args = parser.parse_args()
    if not args.source.is_dir():
        parser.error(f"Source folder does not exist: {args.source}")
    if args.minimum_side < 1 or args.minimum_per_class < 3:
        parser.error("Minimum side must be positive and minimum per class at least 3")

    classes, rejected, duplicates = inspect(args.source, args.minimum_side)
    cross_class = [item for item in duplicates if item["class"] != item["first_class"]]
    report = {"source": str(args.source), "classes": {k: len(v) for k, v in classes.items()},
              "rejected": rejected, "exact_duplicates": duplicates,
              "ready": len(classes) >= 2 and all(len(v) >= args.minimum_per_class for v in classes.values())
              and not cross_class}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not args.write:
        return 0
    if not report["ready"]:
        print("Dataset is not ready: need at least two classes, enough reviewed images per class,"
              " and no exact image shared across classes.", file=sys.stderr)
        return 2
    if args.output.exists() and any(args.output.iterdir()):
        print(f"Output is not empty; refusing to overwrite: {args.output}", file=sys.stderr)
        return 2

    rows = assign_splits(classes, args.seed)
    args.output.mkdir(parents=True, exist_ok=True)
    for row in rows:
        destination = args.output / row["split"] / row["label"] / f'{row["sha256"][:20]}.jpg'
        destination.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(row["path"]) as image:
            image = image.convert("RGB")
            image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            image.save(destination, format="JPEG", quality=90, optimize=True)
        row["prepared_path"] = str(destination)
    with (args.output / "manifest.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with (args.output / "audit.json").open("w", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False)
    (args.output / "labels.txt").write_text("\n".join(sorted(classes)) + "\n", encoding="utf-8")
    print(f"Prepared {len(rows)} images in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
