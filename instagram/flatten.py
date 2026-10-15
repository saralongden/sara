"""Flatten the render to opaque sRGB PNG + JPG (no alpha, no layers) for Canva."""
import sys
from pathlib import Path
from PIL import Image
d = Path(__file__).resolve().parent
name = sys.argv[1] if len(sys.argv) > 1 else "Womens-On-Course-Instagram"
im = Image.open(d / "_raw.png").convert("RGB")
im.save(d / f"{name}.png", optimize=True, dpi=(300, 300))
im.save(d / f"{name}.jpg", quality=95, subsampling=0, dpi=(300, 300))
(d / "_raw.png").unlink()
print(im.size)
