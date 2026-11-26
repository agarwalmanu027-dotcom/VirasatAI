"""Resize the approved VirasatAI icon for Android launcher densities."""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "frontend_recovered/assets/branding/virasatai_launcher_master.png"
RES = ROOT / "frontend_recovered/android/app/src/main/res"
BACKUP = ROOT / "local_asset_backups/launcher_flutter_default"
SIZES = {
    "mdpi": 48,
    "hdpi": 72,
    "xhdpi": 96,
    "xxhdpi": 144,
    "xxxhdpi": 192,
}


def main() -> None:
    BACKUP.mkdir(parents=True, exist_ok=True)
    with Image.open(SOURCE) as image:
        if image.width != image.height:
            raise ValueError("Launcher master must be square")
        image = image.convert("RGBA")
        for density, side in SIZES.items():
            target = RES / f"mipmap-{density}" / "ic_launcher.png"
            original = BACKUP / f"ic_launcher_{density}.png"
            if target.exists() and not original.exists():
                original.write_bytes(target.read_bytes())
            image.resize((side, side), Image.Resampling.LANCZOS).save(
                target, format="PNG", optimize=True
            )
            image.resize((side * 9 // 4, side * 9 // 4), Image.Resampling.LANCZOS).save(
                target.with_name("ic_launcher_foreground.png"), format="PNG", optimize=True
            )
            print(f"{density}: {side}x{side} -> {target}")


if __name__ == "__main__":
    main()
