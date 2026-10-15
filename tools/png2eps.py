"""Convert transparent PNG cutouts to EPS (PostScript Level 3 masked image).

The background stays transparent via an image mask, so the garment drops onto
any colour. One flat image per file: no layers, no groups.

Usage: python3 tools/png2eps.py <in.png> [<in.png> ...]   -> writes <name>.eps beside each PNG
"""
import base64
import sys
import zlib
from pathlib import Path

import numpy as np
from PIL import Image

DPI = 300  # physical size = pixels / 300 inches


def convert(src: Path) -> Path:
    im = Image.open(src).convert("RGBA")
    w, h = im.size
    px = np.asarray(im)
    # InterleaveType 1: per pixel [mask, R, G, B]; mask 0 = paint, 255 = transparent
    mask = np.where(px[..., 3] >= 128, 0, 255).astype(np.uint8)
    data = np.dstack([mask, px[..., :3]]).tobytes()
    payload = base64.a85encode(zlib.compress(data, 9), wrapcol=76).decode() + "~>"

    wpt, hpt = w * 72 / DPI, h * 72 / DPI
    eps = f"""%!PS-Adobe-3.0 EPSF-3.0
%%Creator: Golf Hub flyer cutout tool
%%Title: {src.stem}
%%BoundingBox: 0 0 {int(round(wpt))} {int(round(hpt))}
%%HiResBoundingBox: 0 0 {wpt:.3f} {hpt:.3f}
%%LanguageLevel: 3
%%Pages: 1
%%EndComments
%%Page: 1 1
gsave
{wpt:.3f} {hpt:.3f} scale
/DeviceRGB setcolorspace
/src currentfile /ASCII85Decode filter /FlateDecode filter def
<<
  /ImageType 3
  /InterleaveType 1
  /DataDict << /ImageType 1 /Width {w} /Height {h} /BitsPerComponent 8
               /Decode [0 1 0 1 0 1] /ImageMatrix [{w} 0 0 -{h} 0 {h}] /DataSource src >>
  /MaskDict << /ImageType 1 /Width {w} /Height {h} /BitsPerComponent 8
               /Decode [0 1] /ImageMatrix [{w} 0 0 -{h} 0 {h}] >>
>> image
{payload}
grestore
showpage
%%EOF
"""
    out = src.with_suffix(".eps")
    out.write_text(eps)
    return out


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(convert(Path(p)))
