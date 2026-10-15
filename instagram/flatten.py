"""Flatten the render to opaque sRGB PNG + JPG (no alpha, no layers) for Canva."""
from pathlib import Path
from PIL import Image
d = Path(__file__).resolve().parent
im = Image.open(d / "_raw.png").convert("RGB")
im.save(d / "Womens-On-Course-Instagram.png", optimize=True, dpi=(300, 300))
im.save(d / "Womens-On-Course-Instagram.jpg", quality=95, subsampling=0, dpi=(300, 300))
(d / "_raw.png").unlink()
print(im.size)
