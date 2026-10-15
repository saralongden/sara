"""Flatten each Story page to opaque sRGB JPG + PNG (no alpha, no layers) for Canva."""
from pathlib import Path
from PIL import Image
d = Path(__file__).resolve().parent / "story"
for raw in sorted(d.glob("_*.png")):
    n = int(raw.stem[1:])
    name = f"Story-{n:02d}-" + ("Cover" if n == 1 else f"Look-{n - 1:02d}")
    im = Image.open(raw).convert("RGB")
    im.save(d / f"{name}.png", optimize=True, dpi=(300, 300))
    im.save(d / f"{name}.jpg", quality=95, subsampling=0, dpi=(300, 300))
    raw.unlink()
    print(name, im.size)
