"""Tiny pixel-art toolkit shared by every asset generator.

Everything is drawn pixel-by-pixel into RGBA PIL images using one shared
palette so all assets in the game feel like they belong together.
"""
import math
import os
import random

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
PREVIEW = os.path.join(ROOT, "art_src", "_preview")


def hexc(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


CLEAR = (0, 0, 0, 0)

# ---------------------------------------------------------------- palette ---
# Ramps go dark -> light.
INK = hexc("#120d18")

ROCK = [hexc(c) for c in ("#1c0f17", "#341b23", "#542a29", "#77402f", "#9c5b39", "#c4834f")]
DEEP = [hexc(c) for c in ("#140b12", "#21121a", "#2e1920", "#3f2226")]
GRASS = [hexc(c) for c in ("#132820", "#1f4430", "#2f6634", "#4a8a3a", "#76b443", "#b5e061")]
PINE = [hexc(c) for c in ("#0d1a1f", "#132a2c", "#1b3b39", "#285246", "#3a6e57")]
SKY = [hexc(c) for c in ("#10142a", "#18203d", "#212f52", "#2c4467", "#3d5e7c", "#5a8191",
                         "#86ab9f", "#bcd4b4", "#f1e2b8")]
WOOD = [hexc(c) for c in ("#22121a", "#3d2023", "#5e3229", "#844b33", "#aa6b42", "#cf9259")]
STONE = [hexc(c) for c in ("#191a28", "#282b3e", "#3c4258", "#575f78", "#7e88a0", "#b2bccb")]
CRYSTAL = [hexc(c) for c in ("#1a2152", "#29439a", "#3a7fcc", "#5fc1e6", "#b1f0f2")]
AMETHYST = [hexc(c) for c in ("#2a1846", "#4c2a7e", "#7d48b8", "#b67ee0", "#e9c4f7")]
FIRE = [hexc(c) for c in ("#4d1712", "#93341a", "#d8662a", "#f3a744", "#ffda7a", "#fff6d2")]
CLOAK = [hexc(c) for c in ("#1f1230", "#38204f", "#56337a", "#7c4fa0", "#a77cc4")]
SCARF = [hexc(c) for c in ("#5e2416", "#a2441f", "#d9742e", "#f2ad4f")]
PINK = [hexc(c) for c in ("#5a1834", "#9c2a55", "#d9487a", "#ff86ad", "#ffc4d6")]
RED = [hexc(c) for c in ("#4a1018", "#8a1f26", "#c63a34", "#ef6a4f")]
BONE = [hexc(c) for c in ("#4b4552", "#7d7586", "#b2a9b4", "#e4ddd8", "#fffaf0")]
GLOW = hexc("#ffe7a3")


def new(w, h, fill=CLEAR):
    return Image.new("RGBA", (w, h), fill)


def sprite(rows, key, w=None):
    """Build an image from ASCII rows. key maps char -> rgba; '.' is clear."""
    h = len(rows)
    w = w or max(len(r) for r in rows)
    img = new(w, h)
    px = img.load()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in key and key[ch] is not None:
                px[x, y] = key[ch]
    return img


def paste(dst, src, x, y):
    """Alpha-respecting paste that keeps hard pixel edges."""
    dst.alpha_composite(src, (int(x), int(y)))


def flip(img):
    return img.transpose(Image.FLIP_LEFT_RIGHT)


N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
N8 = N4 + ((1, 1), (-1, -1), (1, -1), (-1, 1))


def outline(img, color=INK, diagonal=False):
    """Add a 1px outline around every opaque region (drawn outside it)."""
    w, h = img.size
    src = img.load()
    out = img.copy()
    o = out.load()
    nb = N8 if diagonal else N4
    for y in range(h):
        for x in range(w):
            if src[x, y][3]:
                continue
            for dx, dy in nb:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and src[nx, ny][3]:
                    o[x, y] = color
                    break
    return out


def pad(img, n):
    out = new(img.width + 2 * n, img.height + 2 * n)
    out.paste(img, (n, n))
    return out


BAYER4 = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))


def dith(x, y, t):
    """True if pixel should take the 'next' colour for blend factor t (0..1)."""
    return t * 16 > BAYER4[y % 4][x % 4] + 0.5


def ramp_at(ramp, t, x, y):
    """Pick a colour from a ramp at position t (0..1) with ordered dithering."""
    t = max(0.0, min(1.0, t)) * (len(ramp) - 1)
    i = int(t)
    if i >= len(ramp) - 1:
        return ramp[-1]
    return ramp[i + 1] if dith(x, y, t - i) else ramp[i]


def save(img, rel, preview=0):
    path = os.path.join(ASSETS, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    if preview:
        save_preview(img, os.path.basename(rel), preview)
    return path


def save_preview(img, name, scale=4, bg=(40, 44, 60, 255)):
    os.makedirs(PREVIEW, exist_ok=True)
    base = new(img.width, img.height, bg)
    base.alpha_composite(img)
    base = base.resize((img.width * scale, img.height * scale), Image.NEAREST)
    base.save(os.path.join(PREVIEW, name))


def sheet(frames, cols=None):
    """Pack equally sized frames into a horizontal (or gridded) strip."""
    fw, fh = frames[0].size
    cols = cols or len(frames)
    rows = math.ceil(len(frames) / cols)
    out = new(fw * cols, fh * rows)
    for i, f in enumerate(frames):
        out.paste(f, ((i % cols) * fw, (i // cols) * fh))
    return out


def rng(seed):
    return random.Random(seed)


def shade(c, k):
    """Multiply rgb by k (keeps alpha). Only for derived/glow effects."""
    return (min(255, int(c[0] * k)), min(255, int(c[1] * k)), min(255, int(c[2] * k)), c[3])
