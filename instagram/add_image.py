"""Add a photo to the Instagram set: flatten onto white, trim white margins, enlarge small
images (Lanczos + light sharpen) and record the photo's background colour so its tile matches.

Usage: python3 instagram/add_image.py <image> <name>    e.g. ... dress.webp 03-blue-dress
"""
import json
import sys
from pathlib import Path
from PIL import Image, ImageChops, ImageFilter

d = Path(__file__).resolve().parent / "images"
src, name = Path(sys.argv[1]), sys.argv[2]
im = Image.open(src).convert("RGBA")
white = Image.new("RGBA", im.size, (255, 255, 255, 255))
white.alpha_composite(im)
im = white.convert("RGB")
mask = ImageChops.difference(im, Image.new("RGB", im.size, "white")).convert("L").point(lambda v: 255 if v > 3 else 0)
im = im.crop(mask.getbbox())
if im.width < 1100:  # tile is ~1560px wide at export size
    k = -(-1100 // im.width)
    im = im.resize((im.width * k, im.height * k), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
im.save(d / f"{name}.jpg", quality=95)
bg = json.loads((d / "bg.json").read_text()) if (d / "bg.json").exists() else {}
bg[f"{name}.jpg"] = "#%02x%02x%02x" % im.getpixel((4, 4))
(d / "bg.json").write_text(json.dumps(bg, indent=1) + "\n")
print(name, im.size, bg[f"{name}.jpg"])
