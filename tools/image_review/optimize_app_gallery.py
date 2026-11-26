"""Keep the large offline gallery within a practical APK size."""

from pathlib import Path
from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[2]
GALLERY = ROOT / "frontend_recovered" / "assets" / "images" / "guide_library"


def main() -> None:
    changed = 0
    before = 0
    after = 0
    for path in sorted(GALLERY.glob("*.jpg")):
        before += path.stat().st_size
        with Image.open(path) as opened:
            image = ImageOps.exif_transpose(opened).convert("RGB")
            if max(image.size) > 1024:
                image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                temporary = path.with_suffix(".optimized.jpg")
                image.save(temporary, "JPEG", quality=74, optimize=True, progressive=True)
                temporary.replace(path)
                changed += 1
        after += path.stat().st_size
    print({"changed": changed, "beforeMB": round(before / 1048576, 1), "afterMB": round(after / 1048576, 1)})


if __name__ == "__main__":
    main()
