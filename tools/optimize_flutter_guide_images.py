"""Shrink packaged guide photos while retaining exact copies outside the APK.

Run after build_flutter_guide_assets.py or other guide asset generators.
Originals changed by this script are copied to local_asset_backups/guide_library.
"""

from __future__ import annotations

import io
import os
import shutil
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "frontend_recovered/assets/images/guide_library"
BACKUP = ROOT / "local_asset_backups/guide_library"


def main() -> None:
    before = after = changed = 0
    for path in sorted(ASSETS.glob("*.jpg")):
        original_size = path.stat().st_size
        before += original_size
        with Image.open(path) as source:
            image = ImageOps.exif_transpose(source)
            if image.mode != "RGB":
                image = image.convert("RGB")
            image.thumbnail((840, 840), Image.Resampling.LANCZOS)
            buffer = io.BytesIO()
            image.save(buffer, "JPEG", quality=72, optimize=True)
        encoded = buffer.getvalue()
        if len(encoded) >= original_size * 0.9:
            after += original_size
            continue
        backup = BACKUP / path.name
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists():
            shutil.copy2(path, backup)
        temp = path.with_suffix(".optimized.tmp")
        try:
            temp.write_bytes(encoded)
            with Image.open(temp) as check:
                check.verify()
            os.replace(temp, path)
        finally:
            temp.unlink(missing_ok=True)
        changed += 1
        after += len(encoded)
    print(
        f"Guide photos: {changed} smaller; "
        f"{before / 1048576:.1f} MiB -> {after / 1048576:.1f} MiB. "
        f"Originals: {BACKUP}"
    )


if __name__ == "__main__":
    main()
