"""Cut a product off a flat studio background: flood-fill from the border, soft edge, trim."""
import sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

src, out, tol = sys.argv[1], sys.argv[2], float(sys.argv[3])
im = Image.open(src).convert("RGB"); a = np.asarray(im).astype(np.float32)
edge = np.concatenate([a[:6].reshape(-1, 3), a[-6:].reshape(-1, 3), a[:, :6].reshape(-1, 3), a[:, -6:].reshape(-1, 3)])
bg = np.median(edge, 0)
dist = np.abs(a - bg).max(-1)
near = dist <= tol
lab, _ = ndimage.label(near)
border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
bgmask = np.isin(lab, list(border))
alpha = (~bgmask).astype(np.float32)
alpha = ndimage.binary_opening(alpha > 0, iterations=1).astype(np.float32)
alpha = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255
rgba = np.dstack([a, alpha * 255]).astype(np.uint8)
o = Image.fromarray(rgba, "RGBA"); bb = o.getbbox(); o = o.crop(bb)
pad = int(max(o.size) * 0.04); c = Image.new("RGBA", (o.width + 2 * pad, o.height + 2 * pad), (0, 0, 0, 0)); c.paste(o, (pad, pad))
c.save(out); print(out, c.size, "bg", bg)
