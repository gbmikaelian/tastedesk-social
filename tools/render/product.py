from PIL import ImageDraw

from .common import W, background, badge, brand_pill, card, draw_center, fit_font, headline, phone, save, theme


def phones(img, spec):
    front, back = spec.get("front"), spec.get("back")
    if front and back:
        img.alpha_composite(phone(back, 400, 860, 8), (30, 470))
        img.alpha_composite(phone(front, 470, 1080, -5), (455, 400))
        if spec.get("badge"):
            badge(img, spec["badge"], 20, 330)
        return [(600, 300, 430, 96), (40, 1150, 430, 104), (560, 1010, 460, 104)]
    if front:
        img.alpha_composite(phone(front, 500, 1080, -4), (300, 390))
        return [(40, 470, 430, 104), (620, 760, 420, 104), (40, 1110, 440, 104)]
    return [(70, 420, 900, 170), (110, 660, 900, 170), (70, 900, 900, 170)]


def spotlight(img, spec):
    shot = phone(spec["front"], 640, 1100, 0, top=spec.get("screen_top", 0))
    img.alpha_composite(shot, ((W - shot.width) // 2, 330))
    return [(610, 770, 440, 104), (30, 1090, 440, 104)]


def render(spec, out):
    name = spec.get("theme", "dark")
    variant = spec.get("variant") or ("phones" if spec.get("front") else "cards")
    img = background(name)
    if variant == "spotlight" and spec.get("front"):
        slots = spotlight(img, spec)
        d = ImageDraw.Draw(img)
        t = theme(name)
        lines = spec["headline"][:2]
        y = 60
        for i, line in enumerate(lines):
            f = fit_font(line, 800, 64, W - 120)
            draw_center(d, W / 2, y, line, f, t["text"] if i == 0 else t["accent"])
            y += 80
        if spec.get("subline"):
            draw_center(d, W / 2, y + 8, spec["subline"], fit_font(spec["subline"], 500, 32, W - 120), t["muted"])
        cards = spec.get("cards", [])[:2]
    else:
        slots = phones(img, dict(spec, front=None, back=None) if variant == "cards" else spec)
        headline(ImageDraw.Draw(img), spec, name)
        cards = spec.get("cards", [])[:3]
    for c, (x, y, w, h) in zip(cards, slots):
        card(img, x, y, w, h, c)
    brand_pill(img, name)
    return [save(img, out)]
