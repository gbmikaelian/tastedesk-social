import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
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

THEMES = {
    "dark": {
        "bg": (11, 18, 22), "glow": [(34, 197, 150, 150), (30, 138, 116, 120)], "dots": (255, 255, 255, 18),
        "text": (255, 255, 255), "accent": (52, 211, 153), "muted": (180, 200, 195),
        "pill": (52, 211, 153), "pill_text": (11, 18, 22),
    },
    "cream": {
        "bg": (246, 241, 232), "glow": [(167, 243, 208, 140), (253, 230, 138, 110)], "dots": (17, 24, 39, 22),
        "text": (17, 24, 39), "accent": (30, 138, 116), "muted": (90, 100, 110),
        "pill": (17, 24, 39), "pill_text": (255, 255, 255),
    },
    "green": {
        "bg": (22, 120, 100), "glow": [(52, 211, 153, 150), (11, 70, 58, 160)], "dots": (255, 255, 255, 26),
        "text": (255, 255, 255), "accent": (253, 224, 71), "muted": (209, 250, 229),
        "pill": (255, 255, 255), "pill_text": (22, 120, 100),
    },
}


def theme(name):
    return THEMES.get(name or "dark", THEMES["dark"])


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


def draw_center(d, cx, y, text, f, fill):
    draw_text(d, cx - text_width(text, f) / 2, y, text, f, fill)


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


def wrap(text, f, max_w):
    lines = []
    for para in text.split("\n"):
        line = ""
        for word in para.split(" "):
            test = f"{line} {word}".strip()
            if text_width(test, f) <= max_w or not line:
                line = test
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def draw_block(d, x, y, text, weight, size, max_w, fill, line_h=1.25, max_lines=None, center=False):
    f = font(weight, size)
    lines = wrap(text, f, max_w)
    while max_lines and len(lines) > max_lines and size > 24:
        size -= 2
        f = font(weight, size)
        lines = wrap(text, f, max_w)
    for line in lines:
        if center:
            draw_center(d, x, y, line, f, fill)
        else:
            draw_text(d, x, y, line, f, fill)
        y += int(size * line_h)
    return y


def background(name="dark", size=(W, H)):
    t = theme(name)
    w, h = size
    img = Image.new("RGBA", size, t["bg"] + (255,))
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([int(w * 0.35), int(h * 0.31), int(w * 1.2), int(h * 0.99)], fill=t["glow"][0])
    gd.ellipse([-int(w * 0.28), int(h * 0.52), int(w * 0.42), int(h * 1.1)], fill=t["glow"][1])
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(160)))
    d = ImageDraw.Draw(img)
    for x in range(30, w, 48):
        for y in range(30, h, 48):
            d.ellipse([x - 1.5, y - 1.5, x + 1.5, y + 1.5], fill=t["dots"])
    return img


def brand_pill(img, name="dark"):
    t = theme(name)
    w, h = img.size
    d = ImageDraw.Draw(img)
    bf = font(800, 28)
    label = "TasteDesk"
    lw = text_width(label, bf)
    d.rounded_rectangle([w - lw - 110, h - 86, w - 40, h - 36], radius=25, fill=t["pill"])
    draw_text(d, w - lw - 75, h - 80, label, bf, t["pill_text"])


def headline(d, spec, name="dark", y=70, x=60, size=62):
    t = theme(name)
    for i, line in enumerate(spec["headline"][:2]):
        f = fit_font(line, 800, size, W - 2 * x)
        draw_text(d, x, y, line, f, t["text"] if i == 0 else t["accent"])
        y += int(size * 1.26)
    if spec.get("subline"):
        draw_text(d, x, y + 12, spec["subline"], fit_font(spec["subline"], 500, 32, W - 2 * x), t["muted"])
        y += 56
    return y


def phone(src, width, crop_h, angle, top=0):
    shot = Image.open(ROOT / src).convert("RGB")
    shot = shot.resize((width, int(shot.height * width / shot.width)), Image.LANCZOS)
    shot = shot.crop((0, top, width, min(top + crop_h, shot.height)))
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
    return shadow.rotate(angle, resample=Image.BICUBIC, expand=True) if angle else shadow


def icon(d, kind, cx, cy, fill="white"):
    if kind == "check":
        d.line([(cx - 13, cy), (cx - 3, cy + 11), (cx + 14, cy - 11)], fill=fill, width=6, joint="curve")
    elif kind == "cross":
        d.line([(cx - 11, cy - 11), (cx + 11, cy + 11)], fill=fill, width=6)
        d.line([(cx - 11, cy + 11), (cx + 11, cy - 11)], fill=fill, width=6)
    elif kind == "bike":
        d.ellipse([cx - 17, cy + 2, cx - 5, cy + 14], outline=fill, width=4)
        d.ellipse([cx + 5, cy + 2, cx + 17, cy + 14], outline=fill, width=4)
        d.line([(cx - 11, cy + 8), (cx - 2, cy - 8), (cx + 11, cy + 8)], fill=fill, width=4)
        d.line([(cx - 2, cy - 8), (cx + 6, cy - 12)], fill=fill, width=4)
    elif kind == "bell":
        d.rounded_rectangle([cx - 12, cy - 14, cx + 12, cy + 8], radius=11, fill=fill)
        d.polygon([(cx - 17, cy + 8), (cx + 17, cy + 8), (cx + 12, cy + 2), (cx - 12, cy + 2)], fill=fill)
        d.ellipse([cx - 5, cy + 9, cx + 5, cy + 17], fill=fill)
    elif kind == "card":
        d.rounded_rectangle([cx - 17, cy - 12, cx + 17, cy + 12], radius=4, outline=fill, width=4)
        d.line([(cx - 17, cy - 3), (cx + 17, cy - 3)], fill=fill, width=4)
    elif kind == "star":
        pts = []
        for i in range(10):
            r = 17 if i % 2 == 0 else 7
            a = math.pi / 2 + i * math.pi / 5
            pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
        d.polygon(pts, fill=fill)
    elif kind == "clock":
        d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], outline=fill, width=4)
        d.line([(cx, cy), (cx, cy - 10)], fill=fill, width=4)
        d.line([(cx, cy), (cx + 8, cy + 4)], fill=fill, width=4)
    elif kind == "printer":
        d.rectangle([cx - 10, cy - 16, cx + 10, cy - 6], outline=fill, width=3)
        d.rounded_rectangle([cx - 17, cy - 6, cx + 17, cy + 8], radius=4, fill=fill)
        d.rectangle([cx - 10, cy + 4, cx + 10, cy + 16], fill=fill)
    elif kind == "qr":
        for ox, oy in ((-16, -16), (4, -16), (-16, 4)):
            d.rectangle([cx + ox, cy + oy, cx + ox + 12, cy + oy + 12], outline=fill, width=3)
        d.rectangle([cx + 6, cy + 6, cx + 10, cy + 10], fill=fill)
        d.rectangle([cx + 12, cy + 12, cx + 16, cy + 16], fill=fill)
    elif kind == "pin":
        d.ellipse([cx - 12, cy - 17, cx + 12, cy + 7], fill=fill)
        d.polygon([(cx - 10, cy), (cx + 10, cy), (cx, cy + 17)], fill=fill)
    elif kind == "chart":
        for i, h in enumerate((10, 20, 30)):
            d.rectangle([cx - 16 + i * 12, cy + 15 - h, cx - 8 + i * 12, cy + 15], fill=fill)
    elif kind == "phone":
        d.rounded_rectangle([cx - 10, cy - 17, cx + 10, cy + 17], radius=4, outline=fill, width=4)
        d.ellipse([cx - 2, cy + 9, cx + 2, cy + 13], fill=fill)
    else:
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=fill)


def big_icon(img, kind, cx, cy, r, color, fill="white", scale=3):
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    small = Image.new("RGBA", (60, 60), (0, 0, 0, 0))
    icon(ImageDraw.Draw(small), kind, 30, 30, fill=fill)
    big = small.resize((60 * scale, 60 * scale), Image.LANCZOS)
    img.alpha_composite(big, (int(cx - 30 * scale), int(cy - 30 * scale)))


def card(img, x, y, w, h, c):
    layer = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0))
    cd = ImageDraw.Draw(layer)
    cd.rounded_rectangle([40, 50, w + 40, h + 50], radius=26, fill=(0, 0, 0, 120))
    layer = layer.filter(ImageFilter.GaussianBlur(18))
    cd = ImageDraw.Draw(layer)
    cd.rounded_rectangle([40, 40, w + 40, h + 40], radius=26, fill=(255, 255, 255, 255))
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
    title, sub = trim(c["title"], tf, avail), trim(c.get("sub", ""), sf, avail)
    if sub:
        draw_text(cd, tx, mid - int(ts * 1.2), title, tf, (17, 24, 39))
        draw_text(cd, tx, mid + int(ss * 0.2), sub, sf, (100, 110, 120))
    else:
        draw_text(cd, tx, mid - int(ts * 0.7), title, tf, (17, 24, 39))
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


def save(img, out):
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, optimize=True)
    return str(out)
