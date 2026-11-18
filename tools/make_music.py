"""Synthesize a royalty-free 120 BPM promo track for the reel. python3 -I tools/make_music.py out.wav"""
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 44100
DUR = 17.0
BEAT = 0.5
N = int(SR * DUR)
L = np.zeros(N)
R = np.zeros(N)
rng = np.random.default_rng(7)


def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N:
        return
    sig = sig[: N - i] * gain
    L[i:i + len(sig)] += sig * (1 - max(pan, 0))
    R[i:i + len(sig)] += sig * (1 + min(pan, 0))


def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR
    e = np.exp(-t / d)
    na = max(1, int(a * SR))
    e[:na] *= np.linspace(0, 1, na)
    return e


def filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, btype=kind, fs=SR, output="sos"), x)


def kick():
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t / 0.04)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(n, 0.001, 0.16) * 1.1 + filt(rng.normal(size=n), "high", 3000) * env(n, 0.0005, 0.004) * 0.3


def clap():
    n = int(0.3 * SR)
    x = filt(rng.normal(size=n), "band", [900, 4000])
    e = env(n, 0.001, 0.09)
    for k in (0.01, 0.02):
        e[int(k * SR):] += env(n - int(k * SR), 0.001, 0.01) * 0.6
    return x * e * 0.5


def hat(open_=False):
    n = int((0.25 if open_ else 0.06) * SR)
    return filt(rng.normal(size=n), "high", 7000) * env(n, 0.0005, 0.08 if open_ else 0.015) * 0.25


def saw(freq, dur, detune=0.006):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = 0
    for d in (-detune, 0, detune):
        s = s + 2 * ((t * freq * (1 + d)) % 1) - 1
    return s / 3


def note(m):
    return 440 * 2 ** ((m - 69) / 12)


def bass(m, dur):
    s = saw(note(m), dur, 0.002) + 0.6 * np.sin(2 * np.pi * note(m - 12) * np.arange(int(dur * SR)) / SR)
    return filt(s, "low", 700) * env(len(s), 0.003, dur * 0.6) * 0.38


def stab(ms, dur=0.22):
    s = sum(saw(note(m), dur) for m in ms) / len(ms)
    return filt(s, "low", 2600) * env(len(s), 0.003, 0.09) * 0.32


def whoosh(dur=0.5):
    n = int(dur * SR)
    x = rng.normal(size=n)
    out = np.zeros(n)
    seg = n // 12
    for k in range(12):
        f = 400 + 7000 * (k / 11) ** 2
        out[k * seg:(k + 1) * seg] = filt(x, "band", [f * 0.7, f * 1.3])[k * seg:(k + 1) * seg]
    return out * np.linspace(0, 1, n) ** 2 * 0.35


def impact():
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * np.cumsum(38 + 60 * np.exp(-t / 0.08)) / SR) * env(n, 0.001, 0.35)
    noise = filt(rng.normal(size=n), "low", 5000) * env(n, 0.001, 0.25) * 0.35
    return (boom + noise) * 0.9


def blip(f=1400, dur=0.08):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t) * env(n, 0.001, 0.03) * 0.25


def printer(dur=0.55):
    n = int(dur * SR)
    t = np.arange(n) / SR
    buzz = filt(np.sign(np.sin(2 * np.pi * 95 * t)) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 22 * t))), "band", [300, 3000])
    return buzz * np.minimum(1, np.minimum(t / 0.02, (dur - t) / 0.05)) * 0.18


# chords per 2 s bar: Am F C G (root midi for bass, stab voicing)
PROG = [(45, [69, 72, 76]), (41, [65, 69, 72]), (48, [67, 72, 76]), (43, [67, 71, 74])]

END = 14.0
for b in range(int(END / BEAT)):
    t = b * BEAT
    intro = t < 3.0
    add(kick(), t, 0.55 if intro and t < 1.0 else 1.0)
    if not intro and b % 2 == 1:
        add(clap(), t, 1.0)
    for k in range(2 if intro else 4):
        step = BEAT / (2 if intro else 4)
        add(hat(open_=(not intro and k == 2)), t + k * step, 0.8 if k % 2 else 1.0, pan=0.3 if k % 2 else -0.2)
    bar = int(t // 2) % 4
    root, chord = PROG[bar]
    if t >= 1.0:
        add(bass(root + (12 if b % 2 else 0), 0.24), t, 1.0)
        add(bass(root, 0.24), t + 0.25, 0.9)
    if not intro:
        add(stab(chord), t + 0.25, 1.0, pan=-0.25)
        if b % 4 == 3:
            add(stab([c + 12 for c in chord], 0.15), t + 0.375, 0.6, pan=0.3)

# transitions
for c in (3.0, 6.5, 9.0, 11.5):
    add(whoosh(0.5), c - 0.5, 1.0)
    add(impact(), c, 0.45)
add(whoosh(1.0), END - 1.0, 1.4)

# UI sound effects matching the picture
for t in (3.0 + 2.45,):  # tap on "Place order"
    add(blip(1800, 0.06), t, 1.2)
add(blip(1200, 0.12), 3.0 + 2.75, 1.0)
add(blip(1500, 0.1), 6.5 + 0.55, 0.9)  # new order card
add(printer(), 6.5 + 1.15, 1.0)  # ticket prints
for k, t in enumerate((9.5, 10.0, 10.5)):  # status pills
    add(blip(1100 + 250 * k, 0.09), t, 1.0)
add(blip(1500, 0.1), 11.5 + 0.5, 0.9)
add(blip(2000, 0.14), 11.5 + 1.25, 1.0)

# logo ending: big hit + Am pad
add(impact(), END, 1.0)
padn = int(3.0 * SR)
tt = np.arange(padn) / SR
pad = sum(saw(note(m), 3.0, 0.01) for m in (57, 64, 69, 72, 76)) / 5
pad = filt(pad, "low", 1800) * np.minimum(1, tt / 0.03) * np.exp(-tt / 1.2) * 0.35
add(pad, END, 1.0, pan=0.0)
add(kick(), END, 1.0)

mix = np.stack([L, R], axis=1)
fade = int(0.6 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix /= np.max(np.abs(mix)) / 0.89
mix = np.tanh(mix * 1.3) / np.tanh(1.3)
wavfile.write(sys.argv[1], SR, (mix * 32767).astype(np.int16))
