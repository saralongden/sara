"""Scale a 1-page vector PDF onto several trim sizes (fit + centre, gaps filled with bg colour) and combine."""
import io, sys
from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

src, out, prefix = sys.argv[1], sys.argv[2], sys.argv[3]
BG = (240/255, 236/255, 228/255)
SIZES = [("A4", 210*mm, 297*mm), ("A5", 148*mm, 210*mm), ("5x7in", 127*mm, 177.8*mm), ("8x10cm", 80*mm, 100*mm)]
combined = PdfWriter()
for name, W, H in SIZES:
    sp = PdfReader(src).pages[0]
    sw, sh = float(sp.mediabox.width), float(sp.mediabox.height)
    s = min(W / sw, H / sh)
    buf = io.BytesIO(); c = canvas.Canvas(buf, pagesize=(W, H)); c.setFillColorRGB(*BG); c.rect(0, 0, W, H, stroke=0, fill=1); c.save()
    page = PdfReader(buf).pages[0]
    page.merge_transformed_page(sp, Transformation().scale(s).translate((W - sw*s)/2, (H - sh*s)/2))
    w = PdfWriter(); w.add_page(page); w.write(f"{prefix}-{name}.pdf")
    combined.add_page(page)
    print(name, f"scale {s:.3f}", f"smallest-text factor vs A3 {s:.2f}")
combined.write(out)
