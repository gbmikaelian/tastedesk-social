from PIL import Image, ImageDraw, ImageFilter

from .common import H, W, background, brand_pill, draw_block, draw_text, font, save, text_width, theme, wrap


def bubble(img, y, msg, max_w=820):
    me = msg.get("from") == "me"
    f = font(500, 40)
    lines = wrap(msg["text"], f, max_w - 60)
    bw = int(max(text_width(line, f) for line in lines)) + 60
    bh = len(lines) * 54 + 40
    x = W - 80 - bw if me else 80
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rounded_rectangle([x, y + 8, x + bw, y + bh + 8], radius=30, fill=(0, 0, 0, 80))
    layer = layer.filter(ImageFilter.GaussianBlur(12))
    ld = ImageDraw.Draw(layer)
    fill = (30, 138, 116, 255) if me else (255, 255, 255, 255)
    ld.rounded_rectangle([x, y, x + bw, y + bh], radius=30, fill=fill)
    img.alpha_composite(layer)
    d = ImageDraw.Draw(img)
    color = (255, 255, 255) if me else (17, 24, 39)
    ty = y + 18
    for line in lines:
        draw_text(d, x + 30, ty, line, f, color)
        ty += 54
    if msg.get("time"):
        tf = font(500, 22)
        tx = x + bw - 30 - text_width(msg["time"], tf)
        draw_text(d, tx, y + bh + 8, msg["time"], tf, (150, 160, 170))
        bh += 24
    return y + bh + 26


def render(spec, out):
    name = spec.get("theme", "cream")
    t = theme(name)
    img = background(name)
    d = ImageDraw.Draw(img)
    y = draw_block(d, 70, 70, spec["setup"], 800, 58, W - 140, t["text"], line_h=1.22, max_lines=3)
    y += 40
    for msg in spec.get("chat", [])[:5]:
        y = bubble(img, y, msg)
    if spec.get("punch"):
        d = ImageDraw.Draw(img)
        py = max(y + 30, H - 330)
        draw_block(d, 70, py, spec["punch"], 800, 50, W - 140, t["accent"], line_h=1.25, max_lines=3)
    brand_pill(img, name)
    return [save(img, out)]
