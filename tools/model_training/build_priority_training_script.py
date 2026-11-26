"""Build the one-cell Colab experiment from the already audited V2 recipe."""

from pathlib import Path

here = Path(__file__).resolve().parent
base = (here / "train_reviewed_mobilenetv2_colab.py").read_text(encoding="utf-8")
addition = (here / "priority_training_injection.py").read_text(encoding="utf-8")
assert base.count("\n\ndef dataset(split, shuffle):") == 1
base = base.replace("\n\ndef dataset(split, shuffle):", "\n\n" + addition + "\n\ndef dataset(split, shuffle):")
# Reuse any already restored Colab images to avoid another 3,074-file download.
base = base.replace('out = ROOT / "candidate"', 'out = ROOT / "priority_candidate"')
base = base.replace('rows = [r for r in all_rows if not r["raw_name"].lower().startswith("aug_")]',
                    'rows = [r for r in all_rows if not r["raw_name"].lower().startswith("aug_")]\noriginal_photo_count = len(rows)')
base = base.replace('"excluded_augmented": len(all_rows)-len(rows)',
                    '"excluded_augmented": len(all_rows)-original_photo_count')
base = base.replace('          "photos": len(rows), "excluded_augmented":',
                    '          "photos": len(rows), "priority_added": len(accepted), "excluded_augmented":')
base = base.replace('print("REVIEWED_V2_RESULT", json.dumps(report), flush=True)',
                    'print("PRIORITY_V2_RESULT", json.dumps(report), flush=True)')
base = base.replace('"reviewed_v2_candidate_2026-10-21"',
                    '"reviewed_v2_priority_candidate_2026-10-22"')
base = base.replace('for name in ("metrics.json", "labels.txt", "monument_model.keras"):',
                    'for name in ("metrics.json", "labels.txt", "monument_model.keras", "priority_candidate_audit.json"):')
base = base.replace('MediaFileUpload(str(out / name), resumable=True)',
                    'MediaFileUpload(str(audit_path if name == "priority_candidate_audit.json" else out / name), resumable=True)')
base = base.replace('print("CANDIDATE_SAVED", folder, flush=True)',
                    'print("PRIORITY_CANDIDATE_SAVED", folder, flush=True)')
target = here / "train_reviewed_v2_with_priority_colab.py"
target.write_text(base, encoding="utf-8")
print(target)
