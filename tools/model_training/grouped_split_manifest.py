"""Propose a source-grouped split from the existing VirasatAI Drive manifest.

This is a metadata-only preparation step. It does not copy photos, train a
model, or claim the resulting test set is independent of unseen phone photos.
Visually review the generated near-pair list before freezing a new dataset.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import random
from collections import defaultdict
from pathlib import Path


SPLITS = ("train", "val", "test")


class UnionFind:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))

    def find(self, n: int) -> int:
        while self.parent[n] != n:
            self.parent[n] = self.parent[self.parent[n]]
            n = self.parent[n]
        return n

    def join(self, a: int, b: int) -> None:
        self.parent[self.find(a)] = self.find(b)


def hamming(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def group_rows(rows: list[dict], max_distance: int = 4,
               reviewed: dict | None = None) -> tuple[dict, list[dict]]:
    """Group same-class exact hashes and conservative dHash neighbours.

    dHash groups are deliberately review candidates, not verified same sources.
    Grouping false positives costs split balance but cannot leak an edited copy.
    """
    if not 0 <= max_distance <= 64:
        raise ValueError("max_distance must be between 0 and 64")
    by_label: dict[str, list[int]] = defaultdict(list)
    for i, row in enumerate(rows):
        if not all(row.get(key) for key in ("label", "file_id", "raw_name", "sha256", "dhash")):
            raise ValueError(f"Incomplete manifest row {i + 1}")
        by_label[row["label"]].append(i)
    union = UnionFind(len(rows))
    pairs: list[dict] = []
    reviewed = reviewed or {}
    lookup = {(row["label"], row["raw_name"]): i for i, row in enumerate(rows)}
    exclusions = {frozenset(pair) for pair in reviewed.get("reviewed_dhash_false_positive", [])}
    for first, second in reviewed.get("reviewed_same_source_or_session", []):
        matches = [(label, lookup.get((label, first)), lookup.get((label, second)))
                   for label in by_label]
        matches = [(label, a, b) for label, a, b in matches if a is not None and b is not None]
        if len(matches) != 1:
            raise ValueError(f"Reviewed same-source pair missing or ambiguous: {first}, {second}")
        union.join(matches[0][1], matches[0][2])
    for label, indices in sorted(by_label.items()):
        hashes = [(i, int(rows[i]["dhash"], 16)) for i in indices]
        for pos, (a, hash_a) in enumerate(hashes):
            for b, hash_b in hashes[pos + 1:]:
                distance = hamming(hash_a, hash_b)
                exact = rows[a]["sha256"] == rows[b]["sha256"]
                if frozenset((rows[a]["raw_name"], rows[b]["raw_name"])) in exclusions:
                    continue
                if exact or distance <= max_distance:
                    union.join(a, b)
                    pairs.append({"label": label, "file_a": rows[a]["raw_name"],
                                  "old_split_a": rows[a].get("split", ""),
                                  "file_b": rows[b]["raw_name"],
                                  "old_split_b": rows[b].get("split", ""),
                                  "dhash_distance": distance, "exact_sha": exact})
    for excluded in exclusions:
        if len(excluded) != 2:
            raise ValueError(f"Invalid reviewed false-positive pair: {sorted(excluded)}")
        first, second = sorted(excluded)
        matches = [(lookup[(label, first)], lookup[(label, second)])
                   for label in by_label
                   if (label, first) in lookup and (label, second) in lookup]
        if len(matches) != 1:
            raise ValueError(f"Reviewed false-positive pair missing or ambiguous: {first}, {second}")
        if union.find(matches[0][0]) == union.find(matches[0][1]):
            raise ValueError(f"Conflicting review decisions group a false-positive pair: {first}, {second}")
    groups: dict[tuple[str, int], list[int]] = defaultdict(list)
    for label, indices in by_label.items():
        for i in indices:
            groups[(label, union.find(i))].append(i)
    return groups, pairs


def assign(rows: list[dict], groups: dict, seed: int = 42) -> list[dict]:
    """Assign entire groups, aiming for 70/15/15 photo counts per class."""
    rng = random.Random(seed)
    by_label: dict[str, list[list[int]]] = defaultdict(list)
    for (label, _), indices in groups.items():
        by_label[label].append(indices)
    output = [dict(row) for row in rows]
    for label, class_groups in sorted(by_label.items()):
        if len(class_groups) < 3:
            raise ValueError(f"{label}: fewer than three independent candidate groups")
        rng.shuffle(class_groups)
        class_groups.sort(key=len, reverse=True)
        total = sum(map(len, class_groups))
        targets = {"train": total * .70, "val": total * .15, "test": total * .15}
        counts = dict.fromkeys(SPLITS, 0)
        # Seed the smallest holdouts first so every class is represented.
        first = {"test": class_groups.pop(), "val": class_groups.pop(),
                 "train": class_groups.pop()}
        for split, indices in first.items():
            for i in indices:
                output[i]["split"] = split
            counts[split] += len(indices)
        for indices in class_groups:
            split = max(SPLITS, key=lambda name: (targets[name] - counts[name],
                                                  -SPLITS.index(name)))
            for i in indices:
                output[i]["split"] = split
            counts[split] += len(indices)
    for (_, _), indices in groups.items():
        digest = hashlib.sha256("|".join(sorted(rows[i]["file_id"] for i in indices)).encode()).hexdigest()[:16]
        for i in indices:
            output[i]["source_group"] = digest
            output[i]["old_split"] = rows[i].get("split", "")
    return output


def propose(rows: list[dict], seed: int = 42, max_distance: int = 4,
            reviewed: dict | None = None) -> tuple[list[dict], dict, list[dict]]:
    groups, pairs = group_rows(rows, max_distance, reviewed)
    output = assign(rows, groups, seed)
    counts: dict[str, dict[str, int]] = defaultdict(lambda: dict.fromkeys(SPLITS, 0))
    for row in output:
        counts[row["label"]][row["split"]] += 1
    old_cross = [pair for pair in pairs if pair["old_split_a"] != pair["old_split_b"]]
    summary = {"status": "proposed_requires_visual_review", "photos": len(rows),
               "candidate_source_groups": len(groups), "distance_threshold": max_distance,
               "near_pairs": len(pairs), "old_cross_split_near_pairs": len(old_cross),
               "counts": dict(sorted(counts.items())),
               "warning": "dHash misses some edits and has false positives. Review source provenance and pairs before training."}
    return output, summary, pairs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, nargs="?", help="local metadata CSV")
    parser.add_argument("--drive-manifest-id", help="read metadata CSV directly from Drive in Colab")
    parser.add_argument("--output", type=Path, required=True,
                        help="new directory, never an existing dataset")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-distance", type=int, default=4)
    parser.add_argument("--review-file", type=Path,
                        help="JSON file of visually verified same-source and false-positive pairs")
    args = parser.parse_args()
    if bool(args.manifest) == bool(args.drive_manifest_id):
        parser.error("Specify either a local manifest or --drive-manifest-id")
    if args.output.exists():
        parser.error("Output already exists; refusing to overwrite")
    if args.drive_manifest_id:
        import google.auth
        from google.colab import auth
        from googleapiclient.discovery import build

        auth.authenticate_user()
        credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/drive.readonly"])
        service = build("drive", "v3", credentials=credentials, cache_discovery=False)
        metadata = service.files().get(fileId=args.drive_manifest_id,
                                       fields="id,name,mimeType").execute()
        if metadata["name"] != "manifest.csv" or metadata["mimeType"] != "text/csv":
            parser.error("Drive ID does not point to the expected manifest.csv")
        payload = service.files().get_media(fileId=args.drive_manifest_id).execute()
        rows = list(csv.DictReader(io.StringIO(payload.decode("utf-8-sig"))))
    else:
        with args.manifest.open(newline="", encoding="utf-8-sig") as stream:
            rows = list(csv.DictReader(stream))
    if not rows:
        parser.error("Empty manifest")
    reviewed = json.loads(args.review_file.read_text(encoding="utf-8")) if args.review_file else None
    proposed, summary, pairs = propose(rows, args.seed, args.max_distance, reviewed)
    args.output.mkdir(parents=True)
    with (args.output / "proposed_manifest.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(proposed[0]))
        writer.writeheader()
        writer.writerows(proposed)
    with (args.output / "review_pairs.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=("label", "file_a", "old_split_a", "file_b",
                                                      "old_split_b", "dhash_distance", "exact_sha"))
        writer.writeheader()
        writer.writerows(pairs)
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
