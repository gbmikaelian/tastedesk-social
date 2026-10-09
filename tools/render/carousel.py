from pathlib import Path

from PIL import ImageDraw

from .common import (
    COLORS, H, W, background, big_icon, brand_pill, draw_block, draw_text, font, phone, save, text_width, theme,
    fit_font,
)


def pager(d, i, n, t):
    label = f"{i}/{n}"
    f = font(800, 26)
    draw_text(d, W - 60 - text_width(label, f), 60, label, f, t["muted"])


def cover(img, d, s, t):
    lines = s["headline"][:3]
    size = min(fit_font(line, 800, 96, W - 140, 60)[0].size for line in lines)
    f = font(800, size)
    y = 300
    for i, line in enumerate(lines):
        draw_text(d, 70, y, line, f, t["accent"] if i == len(lines) - 1 else t["text"])
        y += int(size * 1.22)
    if s.get("subline"):
        draw_block(d, 70, y + 30, s["subline"], 500, 40, W - 140, t["muted"], max_lines=3)
    if s.get("icon"):
        big_icon(img, s["icon"], W - 230, H - 360, 140, COLORS.get(s.get("color", "green")), scale=4)
    label = s.get("swipe", "Սահեցրեք")
    sf = font(800, 34)
    draw_text(d, 70, H - 210, label, sf, t["accent"])
    ax = 70 + text_width(label, sf) + 24
    d.line([(ax, H - 188), (ax + 70, H - 188)], fill=t["accent"], width=6)
    d.polygon([(ax + 70, H - 202), (ax + 92, H - 188), (ax + 70, H - 174)], fill=t["accent"])


def point(img, d, s, t, n):
    has_shot = bool(s.get("screen"))
    draw_text(d, 60, 120, f"{n:02d}", font(800, 200), t["accent"])
    y = draw_block(d, 70, 400, s["title"], 800, 66, W - 140, t["text"], line_h=1.2, max_lines=3)
    y = draw_block(d, 70, y + 30, s.get("body", ""), 500, 42, W - 140, t["muted"], line_h=1.4,
                   max_lines=3 if has_shot else 5)
    if has_shot:
        shot = phone(s["screen"], 420, 700, -6, top=s.get("screen_top", 0))
        img.alpha_composite(shot, (W - shot.width + 60, max(y + 20, H - shot.height + 260)))
    elif s.get("icon"):
        big_icon(img, s["icon"], W - 210, 220, 110, COLORS.get(s.get("color", "green")), scale=3)


def cta(img, d, s, t):
    big_icon(img, s.get("icon", "bell"), W // 2, 400, 120, t["accent"], fill=t["bg"], scale=4)
    y = draw_block(d, W // 2, 600, s["title"], 800, 72, W - 160, t["text"], line_h=1.2, max_lines=3, center=True)
    draw_block(d, W // 2, y + 30, s.get("body", ""), 500, 42, W - 180, t["muted"], line_h=1.4, max_lines=4, center=True)


def render(spec, out):
    name = spec.get("theme", "dark")
    slides = spec["slides"]
    out = Path(out)
    files = []
    for i, s in enumerate(slides, 1):
        sname = s.get("theme", name)
        st = theme(sname)
        img = background(sname)
        d = ImageDraw.Draw(img)
        kind = s.get("type", "point")
        if kind == "cover":
            cover(img, d, s, st)
        elif kind == "cta":
            cta(img, d, s, st)
        else:
            point(img, d, s, st, sum(1 for x in slides[:i] if x.get("type", "point") == "point"))
        pager(ImageDraw.Draw(img), i, len(slides), st)
        brand_pill(img, sname)
        files.append(save(img, out.with_name(f"{out.stem}-{i}{out.suffix}")))
    return files
