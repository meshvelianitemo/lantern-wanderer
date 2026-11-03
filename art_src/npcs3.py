"""Characters and small sprites for Under the Lake (the Starwell).

Run `python npcs3.py` to (re)generate:

  sprites/orrin.png       192x28  8 frames 24x28, feet on the bottom row, facing right:
                                  0-1 idle, 2-3 talk, 4-5 idle_lit, 6-7 talk_lit
                                  (lit: a little lantern hangs from his orrery key and
                                  his spectacles glint warm)
  sprites/name_stone.png   40x10  4 frames 10x10: a carved pebble whose glyph pulses gold
  fx/star.png              21x7   3 frames 7x7: small dot, medium dot, four-point twinkle
                                  (white / pale gold, meant to be tinted)
  ui/icon_ember.png         7x7   journal ember icon (same colours as sprites/ember.png)

A combined preview lands in _preview/npcs3_sheet.png, next to the hero for scale.
"""
import math

from envkit import Mask
from npcs import BRASS, WAX, rows_at
from pix import (BONE, FIRE, GLOW, INK, CLEAR, STONE, hexc, new, outline, paste, ramp_at, save,
                 save_preview, sheet, sprite)
import hero

CAP = [hexc(c) for c in ("#0e1230", "#19225a", "#27357e", "#3a4ea4", "#566cc4")]
ROBE = [hexc(c) for c in ("#1c1a2a", "#2c2940", "#403b58", "#585274", "#767092")]
BEARD = [BONE[1], BONE[2], BONE[3], BONE[4]]
STAR_DOT = hexc("#e8dc9a")
VOID = hero.VOID
LENS_COLD = (hexc("#bfe0f4"), hexc("#4a6a8a"))
LENS_WARM = (GLOW, FIRE[3])
METAL = hero.METAL

# Pointed star-dotted hood; the tip flops back. Placed at (4, bob).
HOOD = [
    ".bb............",
    "abcb...........",
    ".abcb..........",
    "..bccb.........",
    "..bccdb........",
    "..bcsddb.......",
    ".abccddeb......",
    ".abcdsddde.....",
    "abbccddddded...",
    "abccddvvvvvdd..",
    "abccdvvvvvvvdc.",
    "abccvvvvvvvvvc.",
    ".abcvvvvvvvvvc.",
    ".abbvvvvvvvvc..",
]
HOOD_KEY = {"a": CAP[0], "b": CAP[1], "c": CAP[2], "d": CAP[3], "e": CAP[4], "s": STAR_DOT, "v": VOID}

# beard spans per row (relative to the beard's top row): (x0, x1) in frame coordinates
BEARD_ROWS = [(10, 15), (9, 16), (9, 16), (9, 16), (9, 15), (10, 15), (10, 15), (10, 14), (11, 14),
              (11, 13), (12, 13), (13, 13)]


def orrin_frame(talk, mouth_open, bob, lit, sway):
    W, H = 24, 28
    img = new(W, H)
    p = img.load()
    cx = 11.0
    # robe: a round little bell
    top = 13 + bob
    for y in range(top, 26):
        hw = 4.6 + (y - top) * 0.33
        if y >= 24:
            hw -= (y - 23) * 0.6
        x0, x1 = int(round(cx - hw)), int(round(cx + hw))
        for x in range(x0, x1 + 1):
            u = (x - x0 + 0.5) / (x1 - x0 + 1)
            t = 0.15 + 0.85 * min(1.0, u * 1.2) - (0.22 if u > 0.88 else 0.0)
            p[x, y] = ramp_at(ROBE[1:5], t, x, y)
    for x in range(int(cx - 6), int(cx + 7)):  # belt
        if p[x, 20][3]:
            p[x, 20] = BRASS[2] if x < 14 else BRASS[1]
    p[14, 20] = BRASS[4]
    for (x0, x1) in ((7, 9), (12, 14)):  # boots
        for x in range(x0, x1 + 1):
            p[x, 26] = hero.BOOT[1] if x < x1 else hero.BOOT[0]
            p[x, 27] = hero.BOOT[0]
    # the orrery key: a long brass shaft with a ring bow on top and a bit at the foot
    for y in range(6, 28):
        p[18, y] = BRASS[3] if y % 6 else BRASS[4]
        p[19, y] = BRASS[1]
    for a in range(0, 360, 15):
        t = math.radians(a)
        x, y = int(round(18.5 + math.cos(t) * 2.2)), int(round(3.5 + math.sin(t) * 2.2))
        p[x, y] = BRASS[3] if a > 180 or a < 20 else BRASS[2]
    for (x, y) in ((20, 24), (21, 24), (21, 25), (20, 26), (21, 26)):
        p[x, y] = BRASS[2]
    # sleeve and mitten on the key
    for (x, y) in ((14, 15), (15, 15), (16, 16), (15, 16), (17, 16)):
        p[x, y + bob] = ROBE[3]
    p[17, 16 + bob] = hero.BOOT[1]
    p[17, 17 + bob] = hero.BOOT[0]
    # hood
    rows_at(img, 4, bob, HOOD, HOOD_KEY)
    # spectacles: two big round lenses in brass rims
    lens = LENS_WARM if lit else LENS_COLD
    sy = 10 + bob
    for x in range(10, 17):
        for dy in (0, 1):
            p[x, sy + dy] = BRASS[3] if x in (10, 13, 16) else lens[1]
    p[11, sy] = lens[0]
    p[14, sy] = lens[0]
    for x in (11, 12, 14, 15):
        p[x, sy - 1] = BRASS[2]
    # beard
    by = 12 + bob
    for i, (x0, x1) in enumerate(BEARD_ROWS):
        y = by + i
        if i >= 6:
            x0, x1 = x0 + sway, x1 + sway
        for x in range(x0, x1 + 1):
            u = (x - x0 + 0.5) / (x1 - x0 + 1)
            c = BEARD[1] if u < 0.3 else (BEARD[2] if u < 0.75 else BEARD[3])
            if (x + i) % 3 == 0 and i > 1 and 0 < u < 1:
                c = BEARD[max(0, BEARD.index(c) - 1)]  # strands
            p[x, y] = c
    for x in range(10, 16):  # moustache
        p[x, by] = BEARD[2] if x < 13 else BEARD[3]
    if talk and mouth_open:
        p[12, by + 1] = hexc("#3a2a2c")
        p[13, by + 1] = hexc("#3a2a2c")
        p[12, by + 2] = hexc("#5a3a3c")
    elif talk:
        p[12, by + 1] = BEARD[0]
        p[13, by + 1] = BEARD[0]
    # little lantern hanging off the key's bow
    if lit:
        p[21, 5] = METAL[1]
        lan = [".m.", "mnm", "GHG", "FGF", "mmm"]
        rows_at(img, 20, 6, lan, {"m": METAL[0], "n": METAL[1], "F": FIRE[3], "G": FIRE[4], "H": FIRE[5]})
    out = outline(img, INK)
    q = out.load()
    if lit:  # warm light on the near side of the hood and beard
        for (x, y) in ((17, 10 + bob), (17, 11 + bob), (16, 13 + bob), (17, 14 + bob)):
            if q[x, y][3] and q[x, y] != INK:
                q[x, y] = WAX[4]
        q[22, 7] = FIRE[3]
    return out


def orrin():
    frames = []
    for lit in (False, True):
        frames += [
            orrin_frame(False, False, 0, lit, 0),
            orrin_frame(False, False, 1, lit, 0),
            orrin_frame(True, True, 0, lit, 0),
            orrin_frame(True, False, 0, lit, 1),
        ]
    return frames


def name_stone():
    glyph_cols = [BRASS[2], BRASS[3], GLOW, BRASS[3]]
    frames = []
    for i in range(4):
        m = Mask(10, 10)
        m.ellipse(5, 5.5, 3.7, 3.0)
        img = new(10, 10)
        p = img.load()
        for y in range(10):
            for x in range(10):
                if m.get(x, y):
                    dx, dy = (x + 0.5 - 5) / 3.7, (y + 0.5 - 5.5) / 3.0
                    lt = -0.55 * dx - 0.83 * dy
                    p[x, y] = ramp_at(STONE[1:6], 0.45 + 0.4 * lt, x, y)
        g = glyph_cols[i]
        for (x, y) in ((5, 4), (4, 5), (5, 5), (6, 5), (5, 6), (4, 7), (6, 7)):
            p[x, y] = g if (x, y) != (5, 5) else (hexc("#fff6d2") if i == 2 else g)
        if i == 2:  # the brightest beat warms the stone around the rune
            for (x, y) in ((3, 4), (7, 4), (3, 6), (7, 6)):
                if p[x, y][3]:
                    p[x, y] = BRASS[1]
        frames.append(outline(img, INK))
    return frames


def star_frames():
    white = (255, 255, 255, 255)

    def gold(a):
        return (255, 243, 200, a)

    frames = []
    for i in range(3):
        img = new(7, 7)
        p = img.load()
        p[3, 3] = white
        if i == 0:
            for (x, y) in ((2, 3), (4, 3), (3, 2), (3, 4)):
                p[x, y] = gold(100)
        elif i == 1:
            for (x, y) in ((2, 3), (4, 3), (3, 2), (3, 4)):
                p[x, y] = gold(230)
            for (x, y) in ((2, 2), (4, 2), (2, 4), (4, 4)):
                p[x, y] = gold(70)
        else:
            for d, a in ((1, 235), (2, 150), (3, 70)):
                for (x, y) in ((3 - d, 3), (3 + d, 3), (3, 3 - d), (3, 3 + d)):
                    p[x, y] = gold(a)
            for (x, y) in ((2, 2), (4, 2), (2, 4), (4, 4)):
                p[x, y] = gold(60)
        frames.append(img)
    return frames


def icon_ember():
    s = ["...a...", "..aba..", ".abcba.", "abcdcba", ".abcba.", "..aba..", "...a..."]
    return sprite(s, {"a": FIRE[2], "b": FIRE[3], "c": FIRE[4], "d": FIRE[5]})


def build():
    o = orrin()
    save(sheet(o), "sprites/orrin.png")
    ns = name_stone()
    save(sheet(ns), "sprites/name_stone.png")
    st = star_frames()
    save(sheet(st), "fx/star.png")
    ic = icon_ember()
    save(ic, "ui/icon_ember.png")
    preview(o, ns, st, ic)


def preview(o, ns, st, ic):
    from PIL import Image
    import os
    from pix import ASSETS
    hero_idle = Image.open(os.path.join(ASSETS, "sprites", "hero_idle.png")).convert("RGBA").crop((0, 0, 32, 32))
    keeper = Image.open(os.path.join(ASSETS, "sprites", "keeper_ghost.png")).convert("RGBA")
    items = [hero_idle, keeper.crop((0, 0, keeper.width // 2, keeper.height))] + o + ns + st + [ic]
    wsum = sum(i.width + 4 for i in items) + 4
    comp = new(wsum, 40, hexc("#2a3350"))
    x = 4
    for i in items:
        comp.alpha_composite(i, (x, 36 - i.height))
        x += i.width + 4
    save_preview(comp, "npcs3_sheet.png", 6)


if __name__ == "__main__":
    build()
