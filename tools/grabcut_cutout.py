"""GrabCut cut-out for a garment on a plain studio background. Usage: grabcut.py in out"""
import sys
import cv2
import numpy as np
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
img = cv2.imread(src); h, w = img.shape[:2]
mask = np.zeros((h, w), np.uint8)
m = int(min(h, w) * 0.03)
rect = (m, m, w - 2 * m, h - 2 * m)
bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
cv2.grabCut(img, mask, rect, bgd, fgd, 8, cv2.GC_INIT_WITH_RECT)
fg = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
n, lab, stats, _ = cv2.connectedComponentsWithStats(fg)
if n > 1:
    k = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA]); fg = np.where(lab == k, 255, 0).astype(np.uint8)
fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
alpha = cv2.GaussianBlur(fg, (0, 0), 1.0)
rgba = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA); rgba[..., 3] = alpha
o = Image.fromarray(rgba); bb = Image.fromarray(fg).getbbox(); o = o.crop(bb)
pad = int(max(o.size) * 0.04); c = Image.new("RGBA", (o.width + 2 * pad, o.height + 2 * pad), (0, 0, 0, 0)); c.paste(o, (pad, pad))
c.save(out); print(out, c.size)
