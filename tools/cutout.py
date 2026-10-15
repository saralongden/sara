"""Remove product photo backgrounds -> flat, single-layer transparent PNGs for Canva.

Usage: python3 tools/cutout.py <input image> [<input image> ...]
Writes products/canva/<name>.png (8-bit RGBA, sRGB, no layers, trimmed with even padding).
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from rembg import new_session, remove

OUT = Path(__file__).resolve().parent.parent / "products" / "canva"
PAD = 0.04          # transparent margin around the garment, as a fraction of its size
MAX_SIDE = 2400     # plenty for print, light enough for Canva

session = new_session("isnet-general-use")


def cut(path: Path) -> Path:
    src = Image.open(path).convert("RGB")
    alpha = np.asarray(remove(src, session=session, only_mask=True), dtype=np.float32) / 255

    # Tidy the matte: drop faint haze (e.g. soft floor shadows), keep anti-aliased edges
    alpha = np.clip((alpha - 0.08) / 0.84, 0, 1)

    # Decontaminate edge colour so no grey/white fringe shows on dark Canva backgrounds
    rgb = np.asarray(src, dtype=np.float32)
    bg = np.median(np.concatenate([rgb[:8].reshape(-1, 3), rgb[-8:].reshape(-1, 3),
                                   rgb[:, :8].reshape(-1, 3), rgb[:, -8:].reshape(-1, 3)]), axis=0)
    a = alpha[..., None]
    fg = np.where(a > 0.02, (rgb - (1 - a) * bg) / np.maximum(a, 0.02), rgb)
    fg = np.clip(fg, 0, 255)

    rgba = Image.fromarray(np.dstack([fg, alpha * 255]).astype(np.uint8), "RGBA")
    rgba = rgba.crop(rgba.getbbox())

    pad = int(max(rgba.size) * PAD)
    canvas = Image.new("RGBA", (rgba.width + 2 * pad, rgba.height + 2 * pad), (0, 0, 0, 0))
    canvas.paste(rgba, (pad, pad))
    if max(canvas.size) > MAX_SIDE:
        canvas.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)

    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / (path.stem + ".png")
    canvas.save(out, "PNG", optimize=True)  # single flat image, no layers
    return out


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(cut(Path(p)))
