import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"
W, H = 1080, 1350
COLORS = {
    "green": (30, 138, 116),
    "amber": (245, 158, 11),
    "blue": (59, 130, 246),
    "red": (239, 68, 68),
    "purple": (139, 92, 246),
    "dark": (17, 24, 39),
}


def font(weight, size):
    return (
        ImageFont.truetype(str(FONTS / f"noto-sans-armenian-armenian-{weight}-normal.woff"), size),
        ImageFont.truetype(str(FONTS / f"manrope-latin-{weight}-normal.woff"), size),
    )


def runs(text):
    out = []
    for ch in text:
        arm = 0x0530 <= ord(ch) <= 0x058F or (ch == " " and out and out[-1][0])
        if out and out[-1][0] == arm:
            out[-1][1] += ch
        else:
            out.append([arm, ch])
    return out


def text_width(text, f):
    return sum((f[0] if arm else f[1]).getlength(s) for arm, s in runs(text))


def draw_text(d, x, y, text, f, fill):
    for arm, s in runs(text):
        ff = f[0] if arm else f[1]
        d.text((x, y), s, font=ff, fill=fill)
        x += ff.getlength(s)


def trim(text, f, max_w):
    if text_width(text, f) <= max_w:
        return text
    while text and text_width(text + "…", f) > max_w:
        text = text[:-1]
    return text.rstrip() + "…"


def fit_font(text, weight, size, max_w, min_size=None):
    min_size = min_size or int(size * 0.8)
    while size > min_size:
        f = font(weight, size)
        if text_width(text, f) <= max_w:
            return f
        size -= 2
    return font(weight, size)


def background():
    img = Image.new("RGBA", (W, H), (11, 18, 22, 255))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([380, 420, 1300, 1340], fill=(34, 197, 150, 150))
    gd.ellipse([-300, 700, 450, 1500], fill=(30, 138, 116, 120))
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(160)))
    d = ImageDraw.Draw(img)
    for x in range(30, W, 48):
        for y in range(30, H, 48):
            d.ellipse([x - 1.5, y - 1.5, x + 1.5, y + 1.5], fill=(255, 255, 255, 18))
    return img


def phone(src, width, crop_h, angle):
    shot = Image.open(ROOT / src).convert("RGB")
    shot = shot.resize((width, int(shot.height * width / shot.width)), Image.LANCZOS)
    shot = shot.crop((0, 0, width, min(crop_h, shot.height)))
    bezel = 14
    fw, fh = width + 2 * bezel, shot.height + 2 * bezel
    frame = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
    ImageDraw.Draw(frame).rounded_rectangle(
        [0, 0, fw - 1, fh - 1], radius=58, fill=(20, 24, 30, 255), outline=(70, 80, 90, 255), width=2
    )
    mask = Image.new("L", shot.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, width - 1, shot.height - 1], radius=46, fill=255)
    frame.paste(shot, (bezel, bezel), mask)
    shadow = Image.new("RGBA", (fw + 160, fh + 160), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([80, 100, fw + 80, fh + 100], radius=58, fill=(0, 0, 0, 170))
    shadow = shadow.filter(ImageFilter.GaussianBlur(35))
    shadow.paste(frame, (80, 80), frame)
    return shadow.rotate(angle, resample=Image.BICUBIC, expand=True)


def icon(d, kind, cx, cy):
    white = "white"
    if kind == "check":
        d.line([(cx - 13, cy), (cx - 3, cy + 11), (cx + 14, cy - 11)], fill=white, width=6, joint="curve")
    elif kind == "bike":
        d.ellipse([cx - 17, cy + 2, cx - 5, cy + 14], outline=white, width=4)
        d.ellipse([cx + 5, cy + 2, cx + 17, cy + 14], outline=white, width=4)
        d.line([(cx - 11, cy + 8), (cx - 2, cy - 8), (cx + 11, cy + 8)], fill=white, width=4)
        d.line([(cx - 2, cy - 8), (cx + 6, cy - 12)], fill=white, width=4)
    elif kind == "bell":
        d.rounded_rectangle([cx - 12, cy - 14, cx + 12, cy + 8], radius=11, fill=white)
        d.polygon([(cx - 17, cy + 8), (cx + 17, cy + 8), (cx + 12, cy + 2), (cx - 12, cy + 2)], fill=white)
        d.ellipse([cx - 5, cy + 9, cx + 5, cy + 17], fill=white)
    elif kind == "card":
        d.rounded_rectangle([cx - 17, cy - 12, cx + 17, cy + 12], radius=4, outline=white, width=4)
        d.line([(cx - 17, cy - 3), (cx + 17, cy - 3)], fill=white, width=4)
    elif kind == "star":
        pts = []
        for i in range(10):
            r = 17 if i % 2 == 0 else 7
            import math
            a = math.pi / 2 + i * math.pi / 5
            pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
        d.polygon(pts, fill=white)
    elif kind == "clock":
        d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], outline=white, width=4)
        d.line([(cx, cy), (cx, cy - 10)], fill=white, width=4)
        d.line([(cx, cy), (cx + 8, cy + 4)], fill=white, width=4)
    elif kind == "printer":
        d.rectangle([cx - 10, cy - 16, cx + 10, cy - 6], outline=white, width=3)
        d.rounded_rectangle([cx - 17, cy - 6, cx + 17, cy + 8], radius=4, fill=white)
        d.rectangle([cx - 10, cy + 4, cx + 10, cy + 16], fill=white, outline=(0, 0, 0, 0))
    elif kind == "qr":
        for ox, oy in ((-16, -16), (4, -16), (-16, 4)):
            d.rectangle([cx + ox, cy + oy, cx + ox + 12, cy + oy + 12], outline=white, width=3)
        d.rectangle([cx + 6, cy + 6, cx + 10, cy + 10], fill=white)
        d.rectangle([cx + 12, cy + 12, cx + 16, cy + 16], fill=white)
    elif kind == "pin":
        d.ellipse([cx - 12, cy - 17, cx + 12, cy + 7], fill=white)
        d.polygon([(cx - 10, cy), (cx + 10, cy), (cx, cy + 17)], fill=white)
    elif kind == "chart":
        for i, h in enumerate((10, 20, 30)):
            d.rectangle([cx - 16 + i * 12, cy + 15 - h, cx - 8 + i * 12, cy + 15], fill=white)
    else:
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=white)


def card(img, x, y, w, h, c):
    layer = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0))
    cd = ImageDraw.Draw(layer)
    cd.rounded_rectangle([40, 50, w + 40, h + 50], radius=26, fill=(0, 0, 0, 120))
    layer = layer.filter(ImageFilter.GaussianBlur(18))
    cd = ImageDraw.Draw(layer)
    cd.rounded_rectangle([40, 40, w + 40, h + 40], radius=26, fill=(255, 255, 255, 250))
    mid = 40 + h // 2
    big = h >= 140
    r, cx = (44, 110) if big else (30, 90)
    cd.ellipse([cx - r, mid - r, cx + r, mid + r], fill=COLORS.get(c.get("color", "green"), COLORS["green"]))
    icon(cd, c.get("icon", "check"), cx, mid)
    tx = cx + r + 22
    avail = w + 40 - tx - 24
    ts, ss = (44, 32) if big else (30, 24)
    tf = fit_font(c["title"], 800, ts, avail)
    sf = fit_font(c.get("sub", ""), 500, ss, avail)
    c = dict(c, title=trim(c["title"], tf, avail), sub=trim(c.get("sub", ""), sf, avail))
    if c.get("sub"):
        draw_text(cd, tx, mid - int(ts * 1.2), c["title"], tf, (17, 24, 39))
        draw_text(cd, tx, mid + int(ss * 0.2), c["sub"], sf, (100, 110, 120))
    else:
        draw_text(cd, tx, mid - int(ts * 0.7), c["title"], tf, (17, 24, 39))
    img.alpha_composite(layer, (x - 40, y - 40))


def badge(img, src, x, y):
    p = Image.open(ROOT / src["file"]).convert("RGB").crop(tuple(src["crop"])).resize((230, 230), Image.LANCZOS)
    b = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
    ImageDraw.Draw(b).ellipse([20, 30, 290, 300], fill=(0, 0, 0, 110))
    b = b.filter(ImageFilter.GaussianBlur(14))
    ImageDraw.Draw(b).ellipse([25, 25, 275, 275], fill=(255, 255, 255, 255))
    mask = Image.new("L", (230, 230), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, 229, 229], fill=255)
    b.paste(p, (35, 35), mask)
    img.alpha_composite(b.rotate(-8, resample=Image.BICUBIC), (x, y))


def render(spec, out):
    img = background()
    front, back = spec.get("front"), spec.get("back")
    cards = spec.get("cards", [])[:3]

    if front and back:
        img.alpha_composite(phone(back, 400, 860, 8), (30, 470))
        img.alpha_composite(phone(front, 470, 1080, -5), (455, 400))
        slots = [(600, 300, 430, 96), (40, 1150, 430, 104), (560, 1010, 460, 104)]
    elif front:
        img.alpha_composite(phone(front, 500, 1080, -4), (300, 390))
        slots = [(40, 470, 430, 104), (620, 760, 420, 104), (40, 1110, 440, 104)]
    else:
        slots = [(70, 420, 900, 170), (110, 660, 900, 170), (70, 900, 900, 170)]

    if spec.get("badge") and (front and back):
        badge(img, spec["badge"], 20, 330)

    for c, (x, y, w, h) in zip(cards, slots):
        card(img, x, y, w, h, c)

    d = ImageDraw.Draw(img)
    lines = spec["headline"]
    y = 70
    for i, line in enumerate(lines[:2]):
        f = fit_font(line, 800, 62, W - 120)
        draw_text(d, 60, y, line, f, (255, 255, 255) if i == 0 else (52, 211, 153))
        y += 78
    if spec.get("subline"):
        draw_text(d, 60, y + 12, spec["subline"], fit_font(spec["subline"], 500, 32, W - 120), (180, 200, 195))

    bf = font(800, 28)
    label = "TasteDesk"
    lw = text_width(label, bf)
    d.rounded_rectangle([W - lw - 110, H - 86, W - 40, H - 36], radius=25, fill=(52, 211, 153))
    draw_text(d, W - lw - 75, H - 80, label, bf, (11, 18, 22))

    img.convert("RGB").save(out, optimize=True)
    return out


if __name__ == "__main__":
    spec_path, out_path = sys.argv[1], sys.argv[2]
    print(render(json.loads(Path(spec_path).read_text(encoding="utf-8")), out_path))
