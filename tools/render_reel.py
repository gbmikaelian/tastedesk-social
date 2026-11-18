"""Render the TasteDesk "order journey" reel: 1080x1920, 30 fps, 120 BPM cuts.

python3 -I tools/render_reel.py <out_dir> [--still t1,t2,...]
"""
import math
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_post as rp  # noqa: E402

ROOT = rp.ROOT
W, H, FPS = 1080, 1920, 30
BG = ROOT / "bg" / "reel-2026-11-18"
TEAL = rp.BRAND
TEAL_L = rp.BRAND_LIGHT


# ---------- easing ----------
def clamp(x):
    return max(0.0, min(1.0, x))


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_back(x):
    x = clamp(x)
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def prog(t, start, dur):
    return clamp((t - start) / dur)


# ---------- layers ----------
def with_alpha(layer, a):
    if a >= 0.999:
        return layer
    l = layer.copy()
    l.putalpha(l.getchannel("A").point(lambda v: int(v * a)))
    return l


def paste(img, layer, x, y, a=1.0, scale=1.0):
    if a <= 0.001:
        return
    if abs(scale - 1) > 0.002:
        w, h = layer.size
        nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
        layer = layer.resize((nw, nh), Image.BILINEAR)
        x, y = x + (w - nw) // 2, y + (h - nh) // 2
    img.alpha_composite(with_alpha(layer, a), (int(x), int(y)))


def text_layer(text, weight, size, fill, shadow=True):
    f = rp.font(weight, size)
    w = int(rp.text_width(text, f)) + 40
    h = int(size * 1.6) + 30
    l = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if shadow:
        s = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        rp.draw_text(ImageDraw.Draw(s), 20, 18, text, f, (0, 0, 0, 170))
        l = s.filter(ImageFilter.GaussianBlur(9))
    rp.draw_text(ImageDraw.Draw(l), 20, 12, text, f, fill)
    return l


def chip_layer(text, fill=TEAL, fg=(255, 255, 255), size=30):
    f = rp.font(800, size)
    tw = int(rp.text_width(text, f))
    w, h = tw + 56, int(size * 2.0)
    l = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(l)
    d.rounded_rectangle([10, 10, 10 + w, 10 + h], radius=h // 2, fill=fill)
    rp.draw_text(d, 10 + 28, 10 + int(h / 2 - size * 0.72), text, f, fg)
    return l


def card_layer(title, sub, color, icon, w=880, h=150):
    l = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0))
    rp.card(l, 40, 40, w, h, {"title": title, "sub": sub, "color": color, "icon": icon})
    return l


def logo_layer(scale, light=True):
    l = Image.new("RGBA", (1200, 500), (0, 0, 0, 0))
    rp.logo(l, 1200, 500, scale=scale, light=light)
    return l.crop(l.getbbox())


def phone_layer(src, width=600):
    shot = Image.open(ROOT / src).convert("RGB")
    shot = shot.resize((width, int(shot.height * width / shot.width)), Image.LANCZOS)
    bezel = 16
    fw, fh = width + 2 * bezel, shot.height + 2 * bezel
    frame = Image.new("RGBA", (fw + 120, fh + 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle([60, 80, fw + 60, fh + 80], radius=70, fill=(0, 0, 0, 160))
    frame = frame.filter(ImageFilter.GaussianBlur(30))
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle([60, 60, fw + 59, fh + 59], radius=70, fill=(18, 22, 28, 255), outline=(80, 90, 100, 255), width=3)
    mask = Image.new("L", shot.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, shot.width - 1, shot.height - 1], radius=54, fill=255)
    frame.paste(shot, (60 + bezel, 60 + bezel), mask)
    return frame, (60 + bezel, 60 + bezel, shot.width, shot.height)


def grad(top_h, top_a, bottom_h, bottom_a):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    for y in range(top_h):
        d.line([(0, y), (W, y)], fill=(0, 0, 0, int(top_a * (1 - y / top_h) ** 1.4)))
    for y in range(bottom_h):
        d.line([(0, H - 1 - y), (W, H - 1 - y)], fill=(0, 0, 0, int(bottom_a * (1 - y / bottom_h) ** 1.4)))
    return g


class Photo:
    def __init__(self, name, z0=1.0, z1=1.1, fx=0.5, fy=0.5, dx=0.0, blur=0, dim=0):
        im = Image.open(BG / name).convert("RGB")
        k = max(W / im.width, H / im.height)
        self.im = im.resize((round(im.width * k * 1.0), round(im.height * k * 1.0)), Image.LANCZOS)
        if blur:
            self.im = self.im.filter(ImageFilter.GaussianBlur(blur))
        if dim:
            self.im = Image.blend(self.im, Image.new("RGB", self.im.size, (0, 0, 0)), dim)
        self.z0, self.z1, self.fx, self.fy, self.dx = z0, z1, fx, fy, dx

    def frame(self, p, punch=0.0):
        z = self.z0 + (self.z1 - self.z0) * p + punch
        cw, ch = W / z, H / z
        cx = self.im.width * (self.fx + self.dx * (p - 0.5))
        cy = self.im.height * self.fy
        x0 = min(max(cx - cw / 2, 0), self.im.width - cw)
        y0 = min(max(cy - ch / 2, 0), self.im.height - ch)
        return self.im.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch)).convert("RGBA")


def cut_in(img, lt):
    """Flash + punch at the start of a scene (lt = local time)."""
    a = 1 - prog(lt, 0, 0.22)
    if a > 0:
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(150 * a))))


def punch(lt):
    return 0.10 * (1 - ease_out(prog(lt, 0, 0.35)))


def headline(img, lt, lines, y, start=0.1, sizes=(84, 84)):
    for i, (txt, col) in enumerate(lines):
        l = HL_CACHE.setdefault((txt, col, sizes[i]), text_layer(txt, 800, sizes[i], col))
        p = ease_out(prog(lt, start + i * 0.12, 0.35))
        paste(img, l, 48, y + i * int(sizes[0] * 1.18) + 50 * (1 - p), p)


HL_CACHE = {}


# ---------- scenes ----------
def scene1():
    ph = Photo("1-home.png", 1.0, 1.12, fx=0.42, fy=0.55)
    g = grad(760, 210, 500, 150)

    def draw(lt, dur):
        img = ph.frame(lt / dur, punch(lt) * 0.5)
        img.alpha_composite(g)
        paste(img, CH["s1"], 52, 190 + 30 * (1 - ease_out(prog(lt, 0.2, 0.3))), ease_out(prog(lt, 0.2, 0.3)))
        headline(img, lt, [("Մեկ պատվերի", (255, 255, 255)), ("ճանապարհը", TEAL_L)], 290, start=0.45, sizes=(96, 96))
        p = ease_out(prog(lt, 1.3, 0.4))
        paste(img, CH["s1sub"], 48, 540 + 30 * (1 - p), p)
        paste(img, LOGO_S, W - LOGO_S.width - 30, 60, ease_out(prog(lt, 0.1, 0.4)))
        cut_in(img, lt + 1)  # no flash on the very first frame
        return img

    return draw


def scene2():
    ph = Photo("1-home.png", 1.18, 1.25, fx=0.45, fy=0.5, blur=18, dim=0.45)
    screens = [PH["menu"], PH["cart"], PH["checkout"]]
    t_sw = [0.0, 1.0, 2.0]  # local times screens become current

    def draw(lt, dur):
        img = ph.frame(lt / dur, punch(lt))
        p_in = ease_back(prog(lt, 0.0, 0.45))
        base_y = 470 + int(900 * (1 - p_in))
        fr, _ = screens[0]
        x0 = (W - fr.width) // 2
        # swipe between screens
        idx = 0
        for i, ts in enumerate(t_sw):
            if lt >= ts:
                idx = i
        cur, (sx, sy, sw, sh) = screens[idx]
        sp = ease_out(prog(lt, t_sw[idx], 0.28)) if idx > 0 else 1.0
        if idx > 0 and sp < 1:
            prev = screens[idx - 1][0]
            paste(img, prev, x0 - int(W * sp), base_y)
            paste(img, cur, x0 + int(W * (1 - sp)), base_y)
        else:
            paste(img, cur, x0, base_y, scale=1.0)
        # tap ripple on "Place order" (checkout screen, button near bottom)
        if idx == 2:
            tp = prog(lt, 2.45, 0.45)
            if 0 < tp < 1:
                r = int(30 + 110 * ease_out(tp))
                cx, cy = x0 + sx + sw // 2, base_y + sy + int(sh * 0.947)
                rl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(rl).ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, int(150 * (1 - tp))))
                img.alpha_composite(rl)
            tq = ease_back(prog(lt, 2.75, 0.35))
            paste(img, CH["sent"], (W - CH["sent"].width) // 2, 1330 + int(60 * (1 - tq)), clamp(tq * 1.5), scale=0.6 + 0.4 * tq)
        paste(img, CH["s2"], 52, 150 + 30 * (1 - ease_out(prog(lt, 0.15, 0.3))), ease_out(prog(lt, 0.15, 0.3)))
        headline(img, lt, [("Պատվիրում է", (255, 255, 255)), ("հավելվածից", TEAL_L)], 230, start=0.25, sizes=(78, 78))
        paste(img, LOGO_S, W - LOGO_S.width - 30, 60)
        cut_in(img, lt)
        return img

    return draw


def scene3():
    ph = Photo("2-printer.png", 1.04, 1.16, fx=0.42, fy=0.5)
    g = grad(700, 220, 760, 230)

    def draw(lt, dur):
        img = ph.frame(lt / dur, punch(lt))
        img.alpha_composite(g)
        paste(img, CH["s3"], 52, 150 + 30 * (1 - ease_out(prog(lt, 0.1, 0.3))), ease_out(prog(lt, 0.1, 0.3)))
        headline(img, lt, [("Չեկն ինքն է", (255, 255, 255)), ("տպվում", TEAL_L)], 230, start=0.2, sizes=(84, 84))
        for i, (key, t0) in enumerate((("c3a", 0.55), ("c3b", 1.2))):
            p = ease_back(prog(lt, t0, 0.4))
            paste(img, CD[key], 60 - 40 + int(W * (1 - p)), 1290 + i * 190, clamp(p * 2))
        paste(img, LOGO_S, W - LOGO_S.width - 30, 60)
        cut_in(img, lt)
        return img

    return draw


def scene4():
    ph = Photo("3-cook.png", 1.12, 1.02, fx=0.5, fy=0.52)
    g = grad(640, 220, 720, 230)
    pills = [("p1", 0.5), ("p2", 1.0), ("p3", 1.5)]

    def draw(lt, dur):
        img = ph.frame(lt / dur, punch(lt))
        img.alpha_composite(g)
        paste(img, CH["s4"], 52, 150 + 30 * (1 - ease_out(prog(lt, 0.1, 0.3))), ease_out(prog(lt, 0.1, 0.3)))
        headline(img, lt, [("Մեկ հպում", (255, 255, 255)), ("հաճախորդը տեսնում է", TEAL_L)], 230, start=0.2, sizes=(84, 72))
        y = 1390
        for i, (key, t0) in enumerate(pills):
            p = ease_back(prog(lt, t0, 0.3))
            on = lt >= t0
            lay = PL[key + "on"] if on else PL[key]
            paste(img, lay, 60, y + i * 128, 0.35 + 0.65 * clamp(p) if on else 0.35, scale=1.0 + 0.08 * math.sin(math.pi * clamp(p)) if on else 1.0)
        paste(img, LOGO_S, W - LOGO_S.width - 30, 60)
        cut_in(img, lt)
        return img

    return draw


def scene5():
    ph = Photo("4-door.png", 1.0, 1.1, fx=0.55, fy=0.48, dx=-0.04)
    g = grad(640, 220, 760, 230)

    def draw(lt, dur):
        img = ph.frame(lt / dur, punch(lt))
        img.alpha_composite(g)
        paste(img, CH["s5"], 52, 150 + 30 * (1 - ease_out(prog(lt, 0.1, 0.3))), ease_out(prog(lt, 0.1, 0.3)))
        headline(img, lt, [("Իսկ հաճախորդը", (255, 255, 255)), ("ամեն քայլը live", TEAL_L)], 230, start=0.2, sizes=(84, 84))
        p1 = ease_back(prog(lt, 0.5, 0.4))
        paste(img, CD["c5a"], 20 + int(W * (1 - p1)), 1290, clamp(p1 * 2))
        p2 = ease_back(prog(lt, 1.25, 0.4))
        paste(img, CD["c5b"], 20 + int(W * (1 - p2)), 1480, clamp(p2 * 2))
        paste(img, LOGO_S, W - LOGO_S.width - 30, 60)
        cut_in(img, lt)
        return img

    return draw


def scene6():
    bg = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        k = y / (H - 1)
        d.line([(0, y), (W, y)], fill=(int(8 + 6 * k), int(40 + 40 * (1 - abs(k - 0.45) * 2)), int(36 + 34 * (1 - abs(k - 0.45) * 2)), 255))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([90, 520, 990, 1420], fill=(19, 134, 117, 170))
    bg.alpha_composite(glow.filter(ImageFilter.GaussianBlur(170)))
    big = LOGO_B

    def draw(lt, dur):
        img = bg.copy()
        # expanding rings on the logo hit
        for k, t0 in enumerate((0.05, 0.3)):
            rp_ = prog(lt, t0, 1.0)
            if 0 < rp_ < 1:
                r = int(200 + 700 * ease_out(rp_))
                rl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(rl).ellipse([W // 2 - r, 900 - r, W // 2 + r, 900 + r], outline=(94, 224, 200, int(120 * (1 - rp_))), width=6)
                img.alpha_composite(rl)
        p = ease_back(prog(lt, 0.0, 0.5))
        paste(img, big, (W - big.width) // 2, 900 - big.height // 2, clamp(p * 2), scale=0.6 + 0.4 * p)
        for i, (key, t0, y) in enumerate((("e1", 0.6, 1070), ("e2", 0.85, 1170))):
            q = ease_out(prog(lt, t0, 0.4))
            l = CH[key]
            paste(img, l, (W - l.width) // 2, y + 30 * (1 - q), q)
        q = ease_back(prog(lt, 1.2, 0.4))
        paste(img, CH["cta"], (W - CH["cta"].width) // 2, 1330, clamp(q * 2), scale=0.7 + 0.3 * q)
        cut_in(img, lt)
        return img

    return draw


# ---------- assets ----------
CH, CD, PL, PH = {}, {}, {}, {}
LOGO_S = LOGO_B = None


def build_assets():
    global LOGO_S, LOGO_B
    CH["s1"] = chip_layer("Burgery · երեկոյան 19:40", fill=(255, 255, 255, 235), fg=(17, 24, 39))
    CH["s1sub"] = text_layer("հավելվածից մինչև դուռ", 500, 50, (235, 240, 240))
    CH["s2"] = chip_layer("01  Հաճախորդ")
    CH["s3"] = chip_layer("02  Խոհանոց")
    CH["s4"] = chip_layer("03  Խոհարար")
    CH["s5"] = chip_layer("04  Առաքիչ")
    CH["sent"] = chip_layer("Պատվերն ուղարկված է", fill=TEAL, size=40)
    CH["e1"] = text_layer("Պատվերից մինչև դուռ", 800, 64, (255, 255, 255))
    CH["e2"] = text_layer("մեկ համակարգում", 800, 64, TEAL_L)
    CH["cta"] = chip_layer("tastedesk.am  ·  անվճար դեմո", fill=(255, 255, 255), fg=(17, 24, 39), size=38)
    CD["c3a"] = card_layer("Նոր պատվեր #236", "Կայքից՝ ուղիղ live board", "green", "bell", w=900, h=150)
    CD["c3b"] = card_layer("Չեկը տպվեց խոհանոցում", "Ավտոմատ, ճիշտ կայանում", "amber", "printer", w=900, h=150)
    CD["c5a"] = card_layer("Առաքիչ · Ճանապարհին", "Պատվեր #236 · 6 000 ֏", "blue", "bike", w=940, h=150)
    CD["c5b"] = card_layer("Առաքված", "Հաճախորդը տեսավ ամեն քայլ", "green", "check", w=940, h=150)
    for key, txt in (("p1", "Ընդունված"), ("p2", "Պատրաստվում է"), ("p3", "Պատրաստ է")):
        PL[key] = card_layer(txt, "", "dark", "clock", w=700, h=118)
        PL[key + "on"] = card_layer(txt, "", "green", "check", w=700, h=118)
    PH["menu"] = phone_layer("screens/01-menu.png")
    PH["cart"] = phone_layer("screens/03-cart.png")
    PH["checkout"] = phone_layer("screens/05-checkout-delivery.png")
    LOGO_S = logo_layer(0.62)
    LOGO_B = logo_layer(2.0)


# Beat grid: 120 BPM -> 0.5 s per beat.
SCENES = [(scene1, 3.0), (scene2, 3.5), (scene3, 2.5), (scene4, 2.5), (scene5, 2.5), (scene6, 3.0)]


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    build_assets()
    stills = None
    if "--still" in sys.argv:
        stills = [float(x) for x in sys.argv[sys.argv.index("--still") + 1].split(",")]
    starts, t = [], 0.0
    for _, dur in SCENES:
        starts.append(t)
        t += dur
    if stills is not None:
        for T in stills:
            for (fn, dur), s in zip(SCENES, starts):
                if s <= T < s + dur:
                    fn()(T - s, dur).convert("RGB").save(out / f"still-{T:05.2f}.jpg", quality=90)
        return
    files = []
    for i, ((fn, dur), s) in enumerate(zip(SCENES, starts)):
        draw = fn()
        n = round(dur * FPS)
        tmp, final = out / f"scene{i}.tmp.mp4", out / f"scene{i}.mp4"
        p = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
             "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(FPS), str(tmp)],
            stdin=subprocess.PIPE,
        )
        for f in range(n):
            p.stdin.write(draw(f / FPS, dur).convert("RGB").tobytes())
        p.stdin.close()
        if p.wait() != 0:
            raise SystemExit(f"ffmpeg failed on scene {i}")
        tmp.rename(final)
        files.append(final)
        print("scene", i, "done", flush=True)
    (out / "list.txt").write_text("".join(f"file '{f.name}'\n" for f in files))


if __name__ == "__main__":
    main()
