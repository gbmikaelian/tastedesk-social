import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

from .common import background, card, draw_block, draw_center, fit_font, font, phone, save, text_width, theme

RW, RH, FPS = 1080, 1920, 30


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def scene_layers(s, name, last):
    t = theme(s.get("theme", name))
    bg = background(s.get("theme", name), (RW, RH))
    text = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
    d = ImageDraw.Draw(text)
    lines = s["headline"][:3]
    y = 260 if s.get("screen") else 640
    for i, line in enumerate(lines):
        f = fit_font(line, 800, 84, RW - 140, 60)
        draw_center(d, RW / 2, y, line, f, t["text"] if i < len(lines) - 1 or len(lines) == 1 else t["accent"])
        y += 104
    if s.get("sub"):
        y = draw_block(d, RW // 2, y + 20, s["sub"], 500, 40, RW - 180, t["muted"], max_lines=3, center=True)
    if last:
        bf = font(800, 44)
        label = "TasteDesk"
        lw = text_width(label, bf)
        d.rounded_rectangle([(RW - lw) / 2 - 50, y + 80, (RW + lw) / 2 + 50, y + 170], radius=45, fill=t["pill"])
        draw_center(d, RW / 2, y + 96, label, bf, t["pill_text"])
    front = None
    if s.get("screen"):
        front = phone(s["screen"], 660, 1200, 0, top=s.get("screen_top", 0))
        if s.get("card"):
            card(front, 40, front.height - 420, front.width - 80, 110, s["card"])
    return bg, text, front, y


def frame(layers, k, n):
    bg, text, front, ty = layers
    sec = k / FPS
    img = bg.copy()
    a = ease(sec / 0.5)
    tl = text.copy()
    tl.putalpha(tl.getchannel("A").point(lambda v: int(v * a)))
    img.alpha_composite(tl, (0, int(40 * (1 - a))))
    if front is not None:
        p = ease((sec - 0.2) / 0.8)
        drift = int(40 * k / n)
        y = int(ty + 40 + 500 * (1 - p)) - drift
        img.alpha_composite(front, ((RW - front.width) // 2, min(y, RH)))
    return img


def render(spec, out):
    name = spec.get("theme", "dark")
    scenes = spec["scenes"]
    per = spec.get("seconds_per_scene", 3)
    n = int(per * FPS)
    fade = int(0.3 * FPS)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{RW}x{RH}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium",
           "-crf", "20", "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    all_layers = [scene_layers(s, name, i == len(scenes) - 1) for i, s in enumerate(scenes)]
    cover = None
    for i, layers in enumerate(all_layers):
        extra = 2 * FPS if i == len(scenes) - 1 else 0
        for k in range(n + extra):
            img = frame(layers, k, n + extra)
            if i + 1 < len(all_layers) and k >= n - fade:
                nxt = frame(all_layers[i + 1], 0, n)
                img = Image.blend(img, nxt, (k - (n - fade) + 1) / (fade + 1))
            if i == 0 and k == int(1.2 * FPS):
                cover = img.copy()
            proc.stdin.write(img.convert("RGB").tobytes())
    proc.stdin.close()
    if proc.wait():
        raise SystemExit("ffmpeg failed")
    return [str(out), save(cover, out.with_suffix(".jpg"))]
