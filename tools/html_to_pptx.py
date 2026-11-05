"""Build an editable single-slide PPTX (for Canva import) from tools/measure_html.js output.

Usage: python3 tools/html_to_pptx.py <boxes.json> <html_dir> <out.pptx>
Text becomes native text boxes, rects become shapes, images are pre-cropped to their box.
"""
import io, json, os, re, sys
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

PX = 9525
d = json.load(open(sys.argv[1])); base = sys.argv[2]
prs = Presentation(); prs.slide_width, prs.slide_height = Emu(int(d["w"] * PX)), Emu(int(d["h"] * PX))
slide = prs.slides.add_slide(prs.slide_layouts[6])


def px(v): return Emu(int(round(v * PX)))


def rgb(css):
    m = re.findall(r"[\d.]+", css)
    if not m: return None, 0
    r, g, b = (int(float(v)) for v in m[:3]); a = float(m[3]) if len(m) > 3 else 1
    return "%02X%02X%02X" % (r, g, b), a


def bare(shape):
    shape.shadow.inherit = False
    st = shape._element.find(qn("p:style"))
    if st is not None: shape._element.remove(st)


bg, _ = rgb(d["bg"]); f = slide.background.fill; f.solid(); f.fore_color.rgb = RGBColor.from_string(bg)

for e in d["els"]:
    if e["kind"] == "rect":
        fill, a = rgb(e["fill"]); border = e.get("border")
        if (not fill or a == 0) and not border: continue
        kind = MSO_SHAPE.ROUNDED_RECTANGLE if e["radius"] else MSO_SHAPE.RECTANGLE
        s = slide.shapes.add_shape(kind, px(e["x"]), px(e["y"]), px(e["w"]), px(max(e["h"], 1)))
        bare(s)
        if e["radius"]: s.adjustments[0] = min(0.5, e["radius"] / min(e["w"], e["h"]))
        if fill and a > 0: s.fill.solid(); s.fill.fore_color.rgb = RGBColor.from_string(fill)
        else: s.fill.background()
        if border:
            s.line.color.rgb = RGBColor.from_string(rgb(border["c"])[0]); s.line.width = Pt(border["w"] * 0.75)
        else: s.line.fill.background()
    elif e["kind"] == "image":
        im = Image.open(os.path.join(base, e["src"])).convert("RGB")
        bw, bh = e["w"], e["h"]
        if e["fit"] == "cover":
            ar = bw / bh
            if im.width / im.height > ar:
                nw = int(im.height * ar); l = (im.width - nw) // 2; im = im.crop((l, 0, l + nw, im.height))
            else:
                nh = int(im.width / ar); t = (im.height - nh) // 2; im = im.crop((0, t, im.width, t + nh))
            x, y, w, h = e["x"], e["y"], bw, bh
        else:
            sc = min(bw / im.width, bh / im.height); w, h = im.width * sc, im.height * sc
            x, y = e["x"] + (bw - w) / 2, e["y"] + (bh - h) / 2
        buf = io.BytesIO(); im.save(buf, "JPEG", quality=95); buf.seek(0)
        slide.shapes.add_picture(buf, px(x), px(y), px(w), px(h))
    else:
        pad = 40 if e["align"] != "center" else 0
        tb = slide.shapes.add_textbox(px(e["x"]), px(e["y"]), px(e["w"] + pad), px(e["h"]))
        tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        col, _ = rgb(e["color"])
        for i, line in enumerate(e["text"].split("\n")):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = PP_ALIGN.CENTER if e["align"] == "center" else PP_ALIGN.LEFT
            p.line_spacing = Pt(e["lineHeight"] * 0.75)
            r = p.add_run(); r.text = line
            ft = r.font; ft.name = e["font"]; ft.size = Pt(e["size"] * 0.75)
            ft.bold = e["weight"] >= 600; ft.italic = e["italic"]; ft.color.rgb = RGBColor.from_string(col)
            if e["spacing"]: r._r.get_or_add_rPr().set("spc", str(int(round(e["spacing"] * 0.75 * 100))))
prs.save(sys.argv[3])
