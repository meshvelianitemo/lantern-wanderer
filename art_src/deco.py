"""Forest props, NPCs, interactables and light textures."""
import math

from bg import pine_shape
from pix import (BONE, FIRE, GLOW, GRASS, INK, PINE, PINK, RED, ROCK, STONE, WOOD, CLEAR,
                 dith, hexc, new, outline, paste, ramp_at, rng, save, save_preview, sheet, sprite)


def blob(w, h, circles, ramp, light=(-0.45, -0.89), rim_dark=True):
    """Union of circles shaded like a lumpy 3D shape."""
    img = new(w, h)
    p = img.load()
    for y in range(h):
        for x in range(w):
            best = None
            for (cx, cy, r) in circles:
                d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
                if d <= r:
                    k = d / r
                    if best is None or k < best[0]:
                        best = (k, (x + 0.5 - cx) / r, (y + 0.5 - cy) / r)
            if best is None:
                continue
            k, nx, ny = best
            lit = -(nx * light[0] + ny * light[1])
            t = 0.5 + 0.45 * lit - (0.25 * k * k if rim_dark else 0)
            p[x, y] = ramp_at(ramp, t, x, y)
    return img


def big_pine(seed, height, width):
    w, h = int(width) + 6, height + 4
    img = new(w, h)
    r = rng(seed)
    pine_shape(img.load(), w, h, w // 2, h - 1, height, width, PINE[2], PINE[3], PINE[1], r)
    p = img.load()
    for y in range(h):  # sparse bright needle tips on the lit side
        for x in range(w):
            if p[x, y] == PINE[3] and (x * 7 + y * 13) % 9 == 0:
                p[x, y] = PINE[4]
    return outline(img, PINE[0])


def bush(seed, w=30, h=16):
    r = rng(seed)
    circles = [(r.uniform(6, w - 6), r.uniform(h * 0.45, h - 4), r.uniform(4.5, 7)) for _ in range(5)]
    circles += [(w * 0.5, h - 5, 6.5)]
    img = blob(w, h, circles, GRASS[1:5])
    p = img.load()
    for _ in range(6):  # berries / tiny flowers
        x, y = r.randrange(3, w - 3), r.randrange(4, h - 3)
        if p[x, y][3]:
            p[x, y] = PINK[3] if r.random() < 0.5 else RED[3]
    return outline(img, GRASS[0])


def tufts():
    out = []
    shapes = [
        ["..b...b..", ".bc..bc..", ".cc.bcc.b", "bccbccbcc"],
        ["...c.....", ".b.cc..b.", "bc.cc.bc.", "bcccbccc."],
        [".....b...", "..b..c.b.", ".cc.cc.c.", "bccbcccbc"],
    ]
    for s in shapes:
        out.append(sprite(s, {"b": GRASS[3], "c": GRASS[4]}))
    return out


def flowers():
    tulip = [
        ".b.b.",
        ".bcb.",
        "bcdcb",
        ".bcb.",
        "..g..",
        ".gg..",
        "..g..",
        "..g..",
    ]
    tall = [
        "..d..",
        ".dcd.",
        "..d..",
        "..g..",
        "..gg.",
        ".gg..",
        "..g..",
        "..g..",
        "..g..",
    ]
    key = {"b": PINK[1], "c": PINK[2], "d": PINK[3], "g": GRASS[2]}
    key2 = {"b": RED[1], "c": RED[2], "d": BONE[3], "g": GRASS[2]}
    return [outline(sprite(tulip, key)), outline(sprite(tall, key)), outline(sprite(tulip, key2))]


def mushrooms():
    m = [
        "..rrrr........",
        ".rRwRRr.......",
        "rRRRRwRr.rrr..",
        "rrrrrrrrrRwRr.",
        "...ss...rrrrr.",
        "...ss.....s...",
        "..sss.....ss..",
    ]
    return outline(sprite(m, {"r": RED[1], "R": RED[2], "w": BONE[4], "s": BONE[3]}))


def fern():
    f = [
        "......c.......",
        "..c..cc...c...",
        ".cc.cc.c.cc.c.",
        "c.bcb..cbc..cc",
        ".bb.bb.bb..bb.",
        "b...bbbb...b..",
        ".....bb.......",
    ]
    return sprite(f, {"b": GRASS[2], "c": GRASS[3]})


def rock(seed, w=14, h=9):
    r = rng(seed)
    img = blob(w, h, [(w * 0.4, h * 0.7, h * 0.62), (w * 0.65, h * 0.75, h * 0.5)], STONE[1:5])
    p = img.load()
    for x in range(w):  # moss cap
        for y in range(h):
            if p[x, y][3]:
                if r.random() < 0.85:
                    p[x, y] = GRASS[3] if (x % 3) else GRASS[4]
                    if y + 1 < h and p[x, y + 1][3] and r.random() < 0.5:
                        p[x, y + 1] = GRASS[2]
                break
    return outline(img, INK)


def pillar(height=48):
    """Carved wooden pillar like the reference's beams (tileable vertically)."""
    w = 12
    img = new(w, height)
    p = img.load()
    for y in range(height):
        for x in range(w):
            t = 0.25 + 0.6 * math.sin(math.pi * (x + 0.5) / w) - (0.15 if x > w * 0.6 else 0)
            ring = (y % 16)
            if ring in (0, 1):
                t -= 0.3 if ring == 0 else -0.15
            c = ramp_at(WOOD[1:5], t - 0.05, x, y)
            if (x * 5 + y * 3) % 23 == 0 and 2 < x < w - 2:
                c = WOOD[2]
            p[x, y] = c
    for y in range(height):
        p[0, y] = INK
        p[w - 1, y] = INK
    return img


def knob():
    k = [
        "..aaaa..",
        ".abbcca.",
        "abcddcba",
        "abdeedca",
        "abcddcba",
        "abbcccba",
        ".abbbba.",
        "..aaaa..",
    ]
    return sprite(k, {"a": INK, "b": WOOD[2], "c": WOOD[3], "d": WOOD[4], "e": WOOD[5]})


def sign():
    s = [
        ".aaaaaaaaaaaaaa.",
        "abccccccccccccba",
        "acdddddddddddcba",
        "acdeeeeeeeeeedca",
        "acdffffffffffdca",
        "acddddddddddddca",
        "abbbbbbbbbbbbbba",
        ".aaaaaabbaaaaaa.",
        "......abca......",
        "......abca......",
        "......abca......",
        "......abca......",
        ".....aabcaa.....",
    ]
    return sprite(s, {"a": INK, "b": WOOD[1], "c": WOOD[2], "d": WOOD[3], "e": WOOD[4], "f": WOOD[2]})


def totem_frames():
    """Old Mossback, a carved totem spirit. Frames: sleep, awake, talk."""
    w, h = 20, 44
    base = new(w, h)
    p = base.load()
    for y in range(6, h):
        for x in range(2, w - 2):
            t = 0.2 + 0.65 * math.sin(math.pi * (x - 1.5) / (w - 4)) - (0.12 if x > 12 else 0)
            if y % 12 == 0:
                t -= 0.25
            p[x, y] = ramp_at(WOOD[1:6], t, x, y)
    # moss cap with sprout
    cap = [
        "......e.............",
        ".....ed.............",
        "....ddc..e..........",
        "..cccccc.dd.........",
        ".ccddddddddcc.......",
        "cbcccddddddccccc....",
        "bbbbccccccccccbbb...",
        "abbbbbbbbbbbbbbbba..",
        ".a.ab.abbb.ba.bba...",
        "......a.....a.......",
    ]
    paste(base, sprite(cap, {"a": GRASS[1], "b": GRASS[2], "c": GRASS[3], "d": GRASS[4], "e": GRASS[5]}), 1, 0)
    # carved brow + eye sockets + nose + mouth
    face = [
        "aaaaaaaaaaaa",
        "abbbbbbbbbba",
        "............",
        ".ooo....ooo.",
        "ooooo..ooooo",
        ".ooo.bb.ooo.",
        "......bb....",
        ".....bcb....",
        "....bbbbb...",
        "............",
        "..aaaaaaaa..",
        "..ammmmmma..",
        "..aaaaaaaa..",
    ]
    paste(base, sprite(face, {"a": WOOD[1], "b": WOOD[4], "c": WOOD[5], "o": INK, "m": INK}), 4, 12)
    # stubby branch arms
    for (ax, ay, d) in ((1, 28, -1), (18, 26, 1)):
        for i in range(3):
            p[ax + d * i if 0 <= ax + d * i < w else ax, ay - (1 if i == 2 else 0)] = WOOD[3]
    # carved bands lower down
    for y in (34, 35):
        for x in range(3, w - 3):
            if (x + y) % 2:
                p[x, y] = WOOD[2]
    for i in range(3):
        for x in range(4 + i * 4, 6 + i * 4):
            p[x, 39] = GRASS[3]
            p[x, 40] = GRASS[2]
    sleep = outline(base, INK)

    def eyes(img, lit, mouth_open):
        img = img.copy()
        q = img.load()
        for (ex, ey) in ((6, 16), (13, 16)):
            for dx in range(-1, 2):
                q[ex + dx, ey] = GLOW if lit else WOOD[0]
            q[ex, ey - 1] = FIRE[4] if lit else INK
            q[ex, ey + 1] = FIRE[3] if lit else INK
        if mouth_open:
            for x in range(7, 13):
                q[x, 24] = FIRE[2]
                q[x, 25] = INK
        return img
    return [eyes(sleep, False, False), eyes(sleep, True, False), eyes(sleep, True, True)]


def shrine_frames():
    """Ember shrine (checkpoint): unlit + 4 burning frames."""
    base = [
        "..aaaaaaaaaaaa..",
        ".abbccccccccbba.",
        "abccddddddddccba",
        ".aabbbbbbbbbbaa.",
        "...abbccddcba...",
        "....abccdcba....",
        "....abcddcba....",
        "....abccdcba....",
        "....abcddcba....",
        "....abccdcba....",
        "...aabbccccbaa..",
        "..abbccddddccba.",
        "..aaaaaaaaaaaaa.",
    ]
    key = {"a": INK, "b": STONE[1], "c": STONE[2], "d": STONE[3]}
    frames = []
    flames = [
        ["...e....", "..ede...", "..dfd.e.", ".ddfdd..", ".cdfdc..", "ccdddcc."],
        ["....e...", "...ed...", ".e.dfd..", "..ddfdd.", ".cdffdc.", ".ccddcc."],
        ["..e.....", "..de.e..", "..dfd...", ".ddffd..", ".cdfdcc.", "ccdddcc."],
        ["...e.e..", "...de...", "..dffd..", "..dfdd..", ".ccfdcc.", ".ccddcc."],
    ]
    fkey = {"c": FIRE[1], "d": FIRE[2], "e": FIRE[3], "f": FIRE[4]}
    for i in range(5):
        img = new(16, 22)
        paste(img, sprite(base, key), 0, 9)
        q = img.load()
        if i == 0:
            for x in (6, 7, 9):
                q[x, 9] = FIRE[0]
            q[8, 9] = FIRE[1]
        else:
            paste(img, sprite(flames[i - 1], fkey), 4, 3)
            for x in range(4, 12):
                q[x, 9] = FIRE[3] if x % 2 else FIRE[4]
        frames.append(img)
    return frames


def ember_frames():
    shapes = [
        ["...a...", "..aba..", ".abcba.", "abcdcba", ".abcba.", "..aba..", "...a..."],
        ["...a...", "..aba..", ".abcba.", "abcdcba", ".abcba.", "..aba..", "...a..."],
        ["..aaa..", ".abbba.", "abcccba", "abcdcba", "abcccba", ".abbba.", "..aaa.."],
        ["...a...", "..aba..", ".abcba.", "abcdcba", ".abcba.", "..aba..", "...a..."],
    ]
    key = {"a": FIRE[2], "b": FIRE[3], "c": FIRE[4], "d": FIRE[5]}
    out = []
    for i, s in enumerate(shapes):
        img = new(11, 11)
        paste(img, sprite(s, key), 2, 2 - (1 if i == 2 else 0))
        q = img.load()
        if i == 1:
            q[9, 1] = FIRE[5]
        if i == 3:
            q[1, 8] = FIRE[4]
        out.append(img)
    return out


def light_texture(radius, bands=((0.32, 1.0), (0.55, 0.72), (0.78, 0.45), (1.0, 0.2))):
    """Radial light with hard bands and a dithered seam between each band."""
    size = radius * 2
    img = new(size, size)
    p = img.load()
    for y in range(size):
        for x in range(size):
            d = math.hypot(x + 0.5 - radius, y + 0.5 - radius) / radius
            if d >= 1.0:
                continue
            a = 0
            for i, (edge, alpha) in enumerate(bands):
                if d <= edge:
                    a = alpha
                    prev = bands[i - 1][0] if i else 0
                    nxt = bands[i + 1][1] if i + 1 < len(bands) else 0
                    if d > edge - 0.035 and dith(x, y, 0.5):
                        a = nxt
                    break
            v = int(255 * a)
            p[x, y] = (255, 255, 255, v)
    return img


def firefly():
    f = [".a.", "aba", ".a."]
    return sprite(f, {"a": hexc("#c8f07a", 140), "b": hexc("#f4ffc0")})


def vine(seed, length):
    r = rng(seed)
    img = new(7, length)
    p = img.load()
    x = 3
    for y in range(length):
        if r.random() < 0.25:
            x = max(1, min(5, x + r.choice((-1, 1))))
        p[x, y] = GRASS[2]
        if r.random() < 0.3:
            side = r.choice((-1, 1))
            p[x + side, y] = GRASS[3] if r.random() < 0.6 else GRASS[4]
    p[x, length - 1] = GRASS[4]
    return img


def build():
    out = {
        "deco/pine_big": big_pine(1, 118, 46),
        "deco/pine_med": big_pine(2, 84, 36),
        "deco/pine_small": big_pine(3, 54, 26),
        "deco/bush_a": bush(4),
        "deco/bush_b": bush(5, 22, 13),
        "deco/mushrooms": mushrooms(),
        "deco/fern": fern(),
        "deco/rock_a": rock(6),
        "deco/rock_b": rock(7, 10, 7),
        "deco/pillar": pillar(48),
        "deco/knob": knob(),
        "deco/sign": sign(),
        "deco/vine_a": vine(8, 22),
        "deco/vine_b": vine(9, 14),
    }
    for i, t in enumerate(tufts()):
        out[f"deco/tuft_{i}"] = t
    for i, f in enumerate(flowers()):
        out[f"deco/flower_{i}"] = f
    for k, img in out.items():
        save(img, f"{k}.png")
    save(sheet(totem_frames()), "sprites/totem.png")
    save(sheet(shrine_frames()), "sprites/shrine.png")
    save(sheet(ember_frames()), "sprites/ember.png")
    save(light_texture(96), "fx/light_lantern.png")
    save(light_texture(40), "fx/light_small.png")
    save(firefly(), "fx/firefly.png")

    # contact sheet for review
    items = list(out.values()) + totem_frames() + shrine_frames() + ember_frames()
    cw = sum(i.width + 4 for i in items[:8])
    comp = new(330, 260, hexc("#2a3350"))
    x, y, rowh = 4, 4, 0
    for img in items:
        if x + img.width > 326:
            x, y = 4, y + rowh + 4
            rowh = 0
        comp.alpha_composite(img, (x, y))
        x += img.width + 4
        rowh = max(rowh, img.height)
    save_preview(comp, "deco_sheet.png", 3)


if __name__ == "__main__":
    build()
