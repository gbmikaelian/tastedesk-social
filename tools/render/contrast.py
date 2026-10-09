from PIL import Image, ImageDraw, ImageFilter

from .common import COLORS, W, background, brand_pill, draw_block, draw_text, fit_font, headline, icon, save, text_width


def panel(img, box, part, good):
    x0, y0, x1, y1 = box
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rounded_rectangle([x0, y0 + 14, x1, y1 + 14], radius=36, fill=(0, 0, 0, 110))
    layer = layer.filter(ImageFilter.GaussianBlur(20))
    ld = ImageDraw.Draw(layer)
    fill = (255, 255, 255, 252) if good else (40, 44, 52, 245)
    ld.rounded_rectangle(box, radius=36, fill=fill)
    img.alpha_composite(layer)
    d = ImageDraw.Draw(img)
    color = COLORS["green"] if good else COLORS["red"]
    text = (17, 24, 39) if good else (235, 238, 242)
    label = part["label"]
    lf = fit_font(label, 800, 30, x1 - x0 - 140)
    d.rounded_rectangle([x0 + 40, y0 + 36, x0 + 100 + int(text_width(label, lf)), y0 + 92], radius=28, fill=color)
    draw_text(d, x0 + 70, y0 + 42, label, lf, (255, 255, 255))
    y = y0 + 140
    items = part["items"][:3]
    step = (y1 - y - 30) // max(len(items), 1)
    for it in items:
        cy = y + 26
        d.ellipse([x0 + 40, cy - 24, x0 + 88, cy + 24], fill=color)
        icon(d, "check" if good else "cross", x0 + 64, cy)
        draw_block(d, x0 + 112, cy - 26, it, 500 if not good else 800, 36, x1 - x0 - 150, text, max_lines=2)
        y += step


def render(spec, out):
    name = spec.get("theme", "dark")
    img = background(name)
    headline(ImageDraw.Draw(img), spec, name, y=60)
    panel(img, (50, 300, W - 50, 760), spec["before"], False)
    panel(img, (50, 800, W - 50, 1250), spec["after"], True)
    brand_pill(img, name)
    return [save(img, out)]
