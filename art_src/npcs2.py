"""Characters for Chapters III-V (Drowned Halls, Rootdark, the Hearth) and the
hero's burning-scarf stages.

Run `python npcs2.py`; a combined preview lands in _preview/npcs2_sheet.png.
Shared helpers (rows_at, soft_blob, extra ramps) come from npcs.py.
"""
import math

import hero
from npcs import BRASS, WAX, rows_at, soft_blob
from pix import (AMETHYST, BONE, CLOAK, DEEP, FIRE, GRASS, INK, PINE, ROCK, SCARF, WOOD, CLEAR,
                 dith, hexc, new, outline, paste, ramp_at, rng, save, save_preview, sheet, sprite)

# Keeper ghosts: pale bone with a faint teal / cream glow
GHOST = [hexc(c) for c in ("#3e5a5e", "#6f948f", "#a6c7b9", "#d8ecdc", "#f7fbef")]
GHOST_LINE = hexc("#16242c")
GHOST_VOID = hexc("#0b1519")
EYE_LIGHT = hexc("#fff7d6")
EYE_HALO = hexc("#bfe8dc")
GREY_GHOST = [hexc(c) for c in ("#3a3d44", "#5c5f68", "#868892", "#adafb6", "#cfd0d4")]
WARM_GHOST = [hexc(c) for c in ("#6b5048", "#a3836a", "#d4b78e", "#f0dfb6", "#fff6dc")]
FISH = [hexc(c) for c in ("#3b2f3a", "#6c5a66", "#a28d93", "#cdb9b6", "#ece0d6", "#fff8ef")]
MILK = [hexc(c) for c in ("#7d8e96", "#b9cdd3", "#dce9ec", "#f4fafa")]
WILT = [hexc(c) for c in ("#2c302b", "#4b5148", "#6b7262", "#8c9282")]
LEAF_GLOW = hexc("#d8ff9a")
CHAR = hexc("#2e1714")
SINGED = hexc("#6b5a5e")


def band(ramp, t, x, y):
    """Flat bands of a ramp with ordered dither only on the seams between them."""
    v = max(0.0, min(0.999, t)) * (len(ramp) - 1)
    i = int(v)
    f = v - i
    if f >= 0.62 or (f > 0.38 and dith(x, y, 0.5)):
        i += 1
    return ramp[min(i, len(ramp) - 1)]


def set_alpha(img, alpha, keep=()):
    """Scale alpha of every opaque pixel except colours listed in `keep`."""
    p = img.load()
    for y in range(img.height):
        for x in range(img.width):
            c = p[x, y]
            if c[3] and c not in keep:
                p[x, y] = (c[0], c[1], c[2], int(c[3] * alpha / 255))


# ------------------------------------------------------------ Keeper ghosts --

def ghost(W, H, cx, hood_cy, hood_r, tip_h, tip_lean, shoulder_y, robe_bottom, w0, w1,
          phase, ramp=GHOST, lean=1.5, eye_gap=3, eye_h=1, tail_drift=3.0, void_col=GHOST_VOID):
    """Hooded, robed, floating Keeper silhouette with a wispy tail.

    Returns (img, eyes) - the image is not outlined yet; `eyes` lists eye pixels."""
    img = new(W, H)
    p = img.load()
    mask = set()
    for y in range(H - 1):
        for x in range(W):
            fx, fy = x + 0.5, y + 0.5
            inside = math.hypot(fx - cx, fy - hood_cy) < hood_r
            ty0 = hood_cy - hood_r - tip_h
            if not inside and ty0 <= fy < hood_cy - hood_r + 2:
                k = (fy - ty0) / (tip_h + 2)
                tc = cx - (1 - k) * tip_lean
                inside = abs(fx - tc) < 0.6 + k * hood_r * 0.65
            if not inside and shoulder_y <= fy < robe_bottom:
                k = (fy - shoulder_y) / (robe_bottom - shoulder_y)
                inside = abs(fx - (cx - lean * k)) < w0 + (w1 - w0) * k
            if not inside and fy >= robe_bottom:
                k = (fy - robe_bottom) / (H - 1 - robe_bottom)
                hw = w1 * (1 - k) ** 1.25
                c = cx - lean - k * tail_drift + math.sin(phase + k * 4.0) * 1.2
                inside = abs(fx - c) < max(hw, 0.7 if k < 0.92 else 0.0)
            if inside:
                mask.add((x, y))
    for (x, y) in mask:
        row = [xx for (xx, yy) in mask if yy == y]
        left, right = min(row), max(row)
        u = (x - left + 0.5) / (right - left + 1)
        t = 0.3 + 0.62 * math.sin(math.pi * u) - (0.18 if u > 0.66 else 0)
        if y > robe_bottom:
            t += 0.15 * (y - robe_bottom) / (H - robe_bottom)  # tail thins into light
        p[x, y] = band(ramp, t, x, y)
    # hem of the hood falling over the shoulders
    for (x, y) in mask:
        d = math.hypot(x + 0.5 - cx, y + 0.5 - hood_cy)
        if y + 0.5 > hood_cy + 1 and hood_r - 1.0 < d < hood_r + 0.6 and (x, y + 1) in mask:
            p[x, y] = ramp[0]
    # the face: a dark opening on the right side of the hood
    vcx, vcy = cx + hood_r * 0.5, hood_cy + 0.4
    rx, ry = hood_r * 0.62, hood_r * 0.56
    for (x, y) in mask:
        if ((x + 0.5 - vcx) / rx) ** 2 + ((y + 0.5 - vcy) / ry) ** 2 < 1:
            p[x, y] = void_col
    # rim of the hood opening catches the glow
    for (x, y) in list(mask):
        if p[x, y] != void_col:
            for dx, dy in ((1, 0), (0, 1), (0, -1)):
                if (x + dx, y + dy) in mask and p[x + dx, y + dy] == void_col and (x + y) % 2 == 0:
                    p[x, y] = ramp[-2]
                    break
    ex = int(math.floor(vcx - eye_gap / 2 - 0.5))
    ey = int(round(vcy - 0.5))
    eyes = []
    for ox in (0, eye_gap):
        for oy in range(eye_h):
            eyes.append((ex + ox, ey + oy))
    return img, mask, eyes


def finish_ghost(img, eyes, alpha, eye_col=EYE_LIGHT, halo=EYE_HALO, line=GHOST_LINE, keep_extra=()):
    o = outline(img, line)
    q = o.load()
    for (x, y) in eyes:
        q[x, y] = halo
    for (x, y) in eyes[: len(eyes)]:
        pass
    # eyes: brightest pixel on top of each eye, halo below
    for (x, y) in eyes:
        if (x, y - 1) not in eyes:
            q[x, y] = eye_col
    set_alpha(o, alpha, keep=(line, eye_col, halo, *keep_extra))
    return o


ARCH_BOOK = [
    ".pppp.pppp.",
    "pplllkllllp",
    "ppppqkqpppp",
    "pllllklllpp",
    "pppppkppppp",
    "LLLLLkLLLLL",
    ".LL.....LL.",
]
ARCH_BOOK_TURN = [
    ".....p.....",
    "....pp.....",
    ".pp.pq.ppp.",
    "pplllkllllp",
    "ppppqkqpppp",
    "pllllklllpp",
    "LLLLLkLLLLL",
    ".LL.....LL.",
]
BOOK_KEY = {"p": WAX[4], "q": WAX[3], "l": BONE[1], "k": WOOD[1], "L": hexc("#2f4a52")}


def archivist_frame(i):
    W, H = 22, 38
    bob = 1 if i == 1 else 0
    img, mask, eyes = ghost(W, H, cx=9.5, hood_cy=8.5 + bob, hood_r=5.2, tip_h=4, tip_lean=2.5,
                            shoulder_y=12 + bob, robe_bottom=29, w0=5.0, w1=6.5,
                            phase=i * 1.4, lean=1.0, eye_gap=3, eye_h=2)
    p = img.load()
    # embroidered hem and a front seam on the robe
    for (x, y) in mask:
        if y == 27 and (x % 2 == 0):
            p[x, y] = GHOST[4]
        if y in range(15 + bob, 27) and x == 12 and (x, y) in mask:
            p[x, y] = GHOST[1]
    # sleeve reaching to the book
    for k, (x, y) in enumerate(((13, 14), (14, 15), (15, 16), (12, 15), (13, 16), (14, 17))):
        p[x, y + bob] = GHOST[2] if k < 3 else GHOST[1]
    # the Book of Wicks, held open
    book = ARCH_BOOK_TURN if i == 3 else ARCH_BOOK
    by = 15 + bob - (1 if i == 3 else 0)
    bimg = new(W, H)
    rows_at(bimg, 10, by, book, BOOK_KEY)
    if i == 2:  # eyes brighten as it speaks
        eye_col, halo = hexc("#ffffff"), EYE_LIGHT
    else:
        eye_col, halo = EYE_LIGHT, EYE_HALO
    o = finish_ghost(img, eyes, 200, eye_col, halo)
    bo = outline(bimg, GHOST_LINE)
    o.alpha_composite(bo)
    q = o.load()
    for (hx, hy) in ((10, by + 4), (20, by + 4)):  # ghostly thumbs over the page edges
        q[hx, hy] = GHOST[3]
    return o


def archivist():
    return [archivist_frame(i) for i in range(4)]


def keeper_ghost():
    out = []
    for i in range(2):
        img, mask, eyes = ghost(14, 22, cx=6.5, hood_cy=5.5 + i, hood_r=3.8, tip_h=2, tip_lean=1.5,
                                shoulder_y=8 + i, robe_bottom=15, w0=3.4, w1=4.3,
                                phase=i * 2.0, lean=0.6, eye_gap=2, eye_h=1, tail_drift=2.0)
        out.append(finish_ghost(img, eyes, 185))
    return out


def bell_frame(i):
    warm = i >= 2
    ramp = WARM_GHOST if warm else GREY_GHOST
    shiver = 0 if warm else (i % 2)
    bob = (i % 2) if warm else 0
    img, mask, eyes = ghost(14, 20, cx=5.5 + shiver, hood_cy=5.5 + bob, hood_r=3.6, tip_h=1, tip_lean=1.0,
                            shoulder_y=8 + bob, robe_bottom=13, w0=3.0, w1=3.8,
                            phase=i * 1.7, ramp=ramp, lean=0.5, eye_gap=2, eye_h=2, tail_drift=1.5,
                            void_col=hexc("#140f12") if warm else GREY_GHOST[0])
    p = img.load()
    # tiny arm and the bell held out in front
    bx, by = 9 + shiver, 8 + bob
    p[bx - 1, by + 2] = ramp[2]
    bell = [".h.", "hHh", "hIh", "HHH", ".k."] if warm else [".h.", "hhh", "hHh", "hhh", ".k."]
    key = {"h": BRASS[2], "H": BRASS[3], "I": BRASS[4], "k": BRASS[0]} if warm else \
          {"h": BRASS[1], "H": BRASS[2], "k": BRASS[0]}
    rows_at(img, bx, by, bell, key)
    if warm:
        o = finish_ghost(img, eyes, 255, eye_col=EYE_LIGHT, halo=FIRE[4])
    else:
        o = finish_ghost(img, eyes, 150, eye_col=BONE[3], halo=BONE[2], line=hexc("#22252c"))
    return o


def bell():
    return [bell_frame(i) for i in range(4)]


# ------------------------------------------------------------- Old Gudgeon --

def _smooth_profile(points, W):
    out = []
    for x in range(W):
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            if x0 <= x <= x1:
                t = (x - x0) / max(1, x1 - x0)
                t = t * t * (3 - 2 * t)
                out.append(y0 + (y1 - y0) * t)
                break
        else:
            out.append(None)
    return out


def gudgeon_frame(bob, talk, sway):
    W, H = 48, 24
    img = new(W, H)
    p = img.load()
    # a broad flat catfish head surfacing at the front, a long low back behind it
    top = _smooth_profile([(1, 19), (8, 15), (16, 11), (24, 7), (31, 5), (36, 5), (40, 7), (43, 10), (44, 13)], W)
    mouth_y = 16 + bob
    for x in range(W):
        if top[x] is None:
            continue
        t0 = top[x] + bob
        for y in range(int(round(t0)), H):
            if y > mouth_y and x > 41 - (y - mouth_y - 1):
                continue  # chin recedes under the mouth, leaving room for the whiskers
            depth = (y - t0) / 9.0
            t = 0.88 - depth * 0.55
            if y > mouth_y and x > 33:
                t = 0.72  # pale belly / chin
            if x < 12:
                t -= 0.12
            p[x, y] = band(FISH[1:6], t, x, y)
    for x in (45, 46):  # blunt rounded snout
        for y in range(12 + bob + (x - 45), mouth_y + 1 - (x - 45)):
            if not p[x, y][3]:
                p[x, y] = FISH[4] if y < 14 + bob else FISH[3]
    # gill slit
    for k in range(10):
        x, y = 27 - (k // 4), 9 + bob + k
        if y < H:
            p[x, y] = FISH[1]
            p[x + 1, y] = FISH[4] if k < 7 else FISH[3]
    # spots, old scars and freckles
    r = rng(5)
    for _ in range(55):
        x, y = r.randrange(3, 44), r.randrange(4, 19)
        if p[x, y][3] and p[x, y] in FISH[3:]:
            p[x, y] = FISH[2]
            if r.random() < 0.45 and p[x + 1, y][3]:
                p[x + 1, y] = FISH[2]
    for (sx, sy) in ((30, 8), (31, 9), (32, 10), (33, 10)):
        p[sx, sy + bob] = FISH[5]
    # wide mouth with an upturned corner
    for x in range(33, 46):
        y = mouth_y - (1 if x < 35 else 0)
        if p[x, y][3]:
            p[x, y] = FISH[0]
            p[x, y - 1] = FISH[4]
    if talk:  # lower jaw drops
        for x in range(35, 42):
            for y in (mouth_y + 1, mouth_y + 2):
                if y < H and p[x, y][3]:
                    p[x, y] = INK if y == mouth_y + 1 else FISH[0]
    # nostrils
    p[43, 11 + bob] = FISH[1]
    p[41, 10 + bob] = FISH[1]
    # big milky blind eye under a heavy, sleepy lid
    ex, ey = 35, 10 + bob
    for y in range(ey - 3, ey + 4):
        for x in range(ex - 3, ex + 4):
            d = math.hypot(x - ex, y - ey)
            if d < 2.8:
                p[x, y] = MILK[0] if d > 2.0 else (MILK[3] if (x - ex, y - ey) in ((-1, -1), (0, -1), (-1, 0)) else MILK[1 if d > 1.2 else 2])
    for x in range(ex - 3, ex + 4):
        p[x, ey - 2] = FISH[1]
        p[x, ey - 3] = FISH[4]
    p[ex - 3, ey - 1] = FISH[1]
    p[ex + 3, ey - 1] = FISH[1]
    # long drooping whiskers: drawn before the outline so they read as solid feelers
    for (wx, wy, ln, ph, side) in ((45, mouth_y, 8, 0.0, 1), (42, mouth_y + 1, 7, 1.4, 0)):
        for k in range(ln):
            x = wx + int(round(math.sin(sway + ph + k * 0.55) * 1.2 + side * k * 0.15))
            y = wy + k
            if 0 <= x < W and 0 <= y < H:
                p[x, y] = FISH[2] if k < ln - 1 else FISH[3]
                if k < 3 and 0 <= x - side < W:
                    p[x - side, y] = FISH[3]
    o = outline(img, INK)
    # tattered translucent dorsal fin with dark spines
    fin = new(W, H)
    fp = fin.load()
    for x in range(7, 23):
        base = int(round(top[x] + bob))
        hgt = int(round(3 + 3.5 * math.sin((x - 7) / 16 * math.pi))) - (2 if x in (12, 18) else 0)
        for k in range(1, hgt + 1):
            y = base - k
            if y >= 0:
                fp[x, y] = FISH[1] if x % 3 == 0 else (FISH[4] if k == hgt else FISH[3])
    fin = outline(fin, FISH[0])
    set_alpha(fin, 175, keep=(FISH[0], FISH[1]))
    fin.alpha_composite(o)
    # small pectoral fin resting at the waterline, just behind the gill
    pec = new(W, H)
    rows_at(pec, 21, 15 + bob, ["...ab", "..abc", ".abcc", "abccb", ".bbb."],
            {"a": FISH[1], "b": FISH[3], "c": FISH[4]})
    pec = outline(pec, FISH[0])
    set_alpha(pec, 200, keep=(FISH[0], FISH[1]))
    fin.alpha_composite(pec)
    return fin


def gudgeon():
    return [gudgeon_frame(0, False, 0.0), gudgeon_frame(1, False, 1.0),
            gudgeon_frame(0, True, 2.0), gudgeon_frame(0, False, 3.0)]


# -------------------------------------------------------------- Root-Mother --

def rootmother_frame(awake, mouth_open):
    S = 64
    img = new(S, S)
    p = img.load()
    cx, cy = 32.0, 33.0
    L = (-0.5, -0.62, 0.6)

    def height(x, y):
        dx, dy = (x - cx) / 26.0, (y - cy) / 29.0
        r2 = dx * dx + dy * dy
        h = math.sqrt(max(0.0, 1 - r2)) * 7
        h += 2.6 * math.exp(-((y - 22) / 2.6) ** 2) * (1 if abs(x - cx) < 19 else 0.3)
        if 23 < y < 41:
            h += 4.5 * math.exp(-((x - cx) / 3.0) ** 2) * min(1.0, (y - 23) / 10)
        h += 2.0 * math.exp(-((x - cx) ** 2 + (y - 39) ** 2) / 10)  # nose tip
        for sx in (20, 44):
            h += 2.8 * math.exp(-((x - sx) ** 2 + (y - 37) ** 2) / 34)  # cheeks
            h -= 3.2 * math.exp(-((x - (sx + (2 if sx < 32 else -2))) ** 2 / 18 + (y - 28) ** 2 / 7))
        h -= (3.5 if mouth_open else 1.2) * math.exp(-((x - cx) ** 2 / 44 + (y - 47) ** 2 / (5 if mouth_open else 1.5)))
        h += 1.5 * math.exp(-((x - cx) ** 2 / 60 + (y - 54) ** 2 / 8))  # chin
        return h

    noise = rng(17)
    jag = [noise.uniform(-1.6, 1.6) for _ in range(64)]
    for y in range(S):
        for x in range(S):
            ang = math.atan2(y - cy, x - cx)
            edge = 1 + jag[int((ang + math.pi) / (2 * math.pi) * 63)] / 26
            dx, dy = (x + 0.5 - cx) / 27.5, (y + 0.5 - cy) / 30.5
            if dx * dx + dy * dy > edge * edge:
                continue
            hx = height(x + 1, y) - height(x - 1, y)
            hy = height(x, y + 1) - height(x, y - 1)
            n = (-hx / 2, -hy / 2, 1.0)
            nl = math.sqrt(n[0] ** 2 + n[1] ** 2 + 1)
            lit = (n[0] * L[0] + n[1] * L[1] + n[2] * L[2]) / nl
            t = 0.15 + 0.85 * (lit - 0.3) / 0.7
            # twisted root strands run down the face; grooves between them
            u = x + 2.4 * math.sin(y * 0.17 + x * 0.06) + 1.3 * math.sin(y * 0.43 + 1.0)
            groove = (u % 5.0) < 1.0
            if groove:
                t -= 0.28
            elif (u % 5.0) > 4.0:
                t += 0.08
            d = math.sqrt(dx * dx + dy * dy)
            t -= max(0.0, d - 0.8) * 1.2  # darker towards the rim so it sinks into the wall
            p[x, y] = ramp_at(WOOD[0:5], t, x, y)
    # roots reaching out of the face into the wall around it
    for (sx, sy, ex_, ey_, wdt) in ((20, 8, 14, -2, 2.4), (32, 4, 33, -2, 2.6), (44, 8, 51, -2, 2.2),
                                   (8, 26, -2, 22, 2.4), (8, 42, -2, 48, 2.2), (56, 26, 66, 20, 2.4),
                                   (56, 42, 66, 47, 2.0), (18, 58, 12, 66, 2.6), (32, 62, 33, 66, 2.4),
                                   (46, 58, 54, 66, 2.4)):
        for k in range(40):
            t = k / 39
            x = sx + (ex_ - sx) * t + math.sin(t * 6 + sx) * 1.2
            y = sy + (ey_ - sy) * t
            w = wdt * (1 - 0.35 * t)
            for yy in range(int(y - w), int(y + w) + 1):
                for xx in range(int(x - w), int(x + w) + 1):
                    if 0 <= xx < S and 0 <= yy < S and math.hypot(xx - x, yy - y) < w and not p[xx, yy][3]:
                        side = (xx - x) / max(w, 0.1)
                        c = ramp_at(WOOD[0:4], 0.45 - 0.35 * side - 0.3 * t, xx, yy)
                        p[xx, yy] = c
    # soft fade at the very edges of the canvas so it melts into the wall
    for y in range(S):
        for x in range(S):
            e = min(x, y, S - 1 - x, S - 1 - y)
            if e < 5 and p[x, y][3] and not dith(x, y, e / 5):
                p[x, y] = CLEAR
    # eyes
    for (ex, ey) in ((22, 28), (42, 28)):
        if awake:
            for y in range(ey - 3, ey + 4):
                for x in range(ex - 5, ex + 6):
                    d = ((x - ex) / 4.6) ** 2 + ((y - ey) / 2.6) ** 2
                    if d < 1:
                        p[x, y] = WOOD[0]
            for (x, y, c) in ((ex, ey, AMETHYST[3]), (ex + 1, ey, AMETHYST[3]), (ex, ey - 1, AMETHYST[4]),
                              (ex + 1, ey - 1, AMETHYST[2]), (ex - 1, ey, AMETHYST[1]), (ex + 2, ey, AMETHYST[1]),
                              (ex, ey + 1, AMETHYST[1]), (ex + 1, ey + 1, AMETHYST[2])):
                p[x, y] = c
        else:
            for x in range(ex - 5, ex + 6):  # closed lid: a soft downward arc
                y = ey + int(round(1.4 * (1 - ((x - ex) / 5.5) ** 2)))
                p[x, y] = WOOD[0]
                p[x, y - 1] = WOOD[3]
            for x in (ex - 3, ex, ex + 3):  # rootlet lashes
                p[x, ey + 3] = WOOD[1]
    # bushy moss eyebrows
    r = rng(23)
    for (bx0, bx1, slope) in ((14, 30, 0.12), (34, 50, -0.12)):
        for x in range(bx0, bx1):
            yb = 22 + slope * (x - (bx0 + bx1) / 2) + (1 if awake else 2) - 1
            th = 3 if bx0 + 2 < x < bx1 - 2 else 2
            for k in range(th):
                y = int(yb) + k
                p[x, y] = GRASS[4] if k == 0 else (GRASS[3] if k == 1 else GRASS[2])
            if r.random() < 0.35:
                p[x, int(yb) + th] = GRASS[1]
            if r.random() < 0.3:
                p[x, int(yb) - 1] = GRASS[5] if r.random() < 0.5 else GRASS[4]
    # mouth
    if mouth_open:
        for y in range(43, 52):
            for x in range(24, 41):
                d = ((x + 0.5 - cx) / 7.5) ** 2 + ((y + 0.5 - 47) / 3.4) ** 2
                if d < 1:
                    p[x, y] = INK if d < 0.6 else WOOD[0]
        for x in (28, 31, 35):  # rootlets hanging over the lip
            p[x, 44] = WOOD[2]
            p[x, 45] = WOOD[1]
    else:
        for x in range(24, 41):
            y = 47 - int(round(1.6 * ((x - cx) / 8.0) ** 2))
            p[x, y] = WOOD[0]
            p[x, y + 1] = WOOD[3] if 26 < x < 39 else WOOD[2]
    face = outline(img, INK)
    back = new(S, S)
    bp = back.load()
    for y in range(S):
        for x in range(S):
            u = x * 0.8 + y * 0.6 + 3 * math.sin(y * 0.21)
            v = x * 0.7 - y * 0.75 + 3 * math.sin(x * 0.19 + 1)
            a, b = u % 9.0, v % 11.0
            e = min(x, y, S - 1 - x, S - 1 - y)
            if (a < 3.2 or b < 3.0) and dith(x, y, min(1.0, e / 9.0)):
                k = (a / 3.2) if a < 3.2 else (b / 3.0)
                bp[x, y] = ramp_at(WOOD[0:3], 0.65 - k * 0.6, x, y)
    back = outline(back, INK)
    back.alpha_composite(face)
    o = back
    q = o.load()
    # glowing violet fungi
    for (fx, fy, n) in ((9, 40, 3), (51, 17, 2), (47, 53, 3), (14, 15, 2), (55, 36, 1)):
        for k in range(n):
            x, y = fx + k * 3 - (n - 1), fy + (k % 2)
            for (dx, dy, c) in ((-1, 0, AMETHYST[2]), (0, 0, AMETHYST[3]), (1, 0, AMETHYST[2]),
                                (0, -1, AMETHYST[4]), (0, 1, BONE[3]), (0, 2, BONE[2])):
                if 0 <= x + dx < S and 0 <= y + dy < S:
                    q[x + dx, y + dy] = c
    if awake:  # faint violet glow around the eyes
        for (ex, ey) in ((22, 28), (42, 28)):
            for (x, y) in ((ex - 6, ey), (ex + 6, ey), (ex, ey - 4), (ex + 1, ey + 4)):
                if q[x, y] in WOOD:
                    q[x, y] = AMETHYST[0]
    return o


def rootmother():
    return [rootmother_frame(False, False), rootmother_frame(True, False),
            rootmother_frame(True, True), rootmother_frame(True, False)]


# -------------------------------------------------------------------- Sprig --

def sprig_frame(i):
    W, H = 12, 16
    img = new(W, H)
    p = img.load()
    perky = i >= 2
    sway = (i % 2)
    g = GRASS if perky else None
    stem_c = GRASS[2] if perky else WILT[2]
    dark = GRASS[1] if perky else WILT[1]
    light = GRASS[4] if perky else WILT[3]
    mid = GRASS[3] if perky else WILT[2]
    # pinch of soil
    rows_at(img, 3, 13, [".abba.", "abbbba", ".aaaa."], {"a": ROCK[1], "b": ROCK[2]})
    # stem (bends over when wilted)
    if perky:
        stem = [(5, 12), (5, 11), (5, 10), (5, 9), (5 + sway, 8), (5 + sway, 7)]
        head = (5 + sway, 4)
    else:
        stem = [(5, 12), (5, 11), (5, 10), (6, 9), (6 + sway, 8), (7 + sway, 8)]
        head = (7 + sway, 7)
    for (x, y) in stem:
        p[x, y] = stem_c
    # leaf arms
    if perky:
        rows_at(img, 1, 7, ["ll.", ".lm", "..m"], {"l": light, "m": mid})
        rows_at(img, 6, 7, [".ll", "ml.", "m.."], {"l": light, "m": mid})
    else:
        rows_at(img, 2, 9, ["..m", ".m.", "ll."], {"l": light, "m": mid})
        rows_at(img, 6, 10, ["m..", ".m.", ".ll"], {"l": light, "m": mid})
    # round bud head with a tiny face and a sprout on top
    hx, hy = head
    rows_at(img, hx - 2, hy - 2, ["..s..", ".mlm.", "mlllm", "mlllm", ".mmm."],
            {"s": light, "m": mid, "l": light})
    face_y = hy + (0 if perky else 1)
    p[hx - 1 + (0 if perky else 1), face_y] = INK
    p[hx + 1, face_y] = INK
    if perky:
        p[hx, face_y + 1] = GRASS[1]
    o = outline(img, INK)
    if perky:  # faint glow along the leaf tips
        q = o.load()
        for (x, y) in ((1, 7), (2, 7), (8, 7), (9, 7), (hx, hy - 2)):
            if q[x, y][3]:
                q[x, y] = LEAF_GLOW
    return o


def sprig():
    return [sprig_frame(i) for i in range(4)]


def sapling_tree(i):
    W, H = 24, 40
    img = new(W, H)
    p = img.load()
    sway = i
    # roots and soil
    rows_at(img, 6, 36, ["..abbbbbba..", ".abbbbbbbba.", "aaaaaaaaaaaa"], {"a": ROCK[1], "b": ROCK[2]})
    for (x, y) in ((8, 35), (15, 35), (7, 36), (16, 36)):
        p[x, y] = WOOD[2]
    # slender trunk with a gentle lean
    for y in range(14, 36):
        x = 11 + (sway if y < 22 else 0)
        p[x, y] = WOOD[3]
        p[x + 1, y] = WOOD[2]
        if y > 30:
            p[x - 1, y] = WOOD[2]
    # one branch
    for k in range(4):
        p[13 + k, 22 - k] = WOOD[2]
    # leafy crown
    crown = soft_blob(W, 26, [(12 + sway, 10, 8.0), (7 + sway, 13, 5.5), (17 + sway, 13, 5.5), (12 + sway, 5, 5.0)],
                      GRASS[1:6])
    paste(img, crown, 0, 0)
    # little face of Sprig on the trunk, now grown
    p[11, 26] = INK
    p[13, 26] = INK
    p[12, 27] = WOOD[1]
    o = outline(img, INK)
    q = o.load()
    for (x, y) in ((6 + sway, 9), (17 + sway, 7), (12 + sway, 3), (9 + sway, 15), (19 + sway, 14)):
        if q[x, y][3]:
            q[x, y] = LEAF_GLOW  # a few leaves still keep the glow
    return o


# --------------------------------------------------------------- Hollow One --

def hollow_one_frame(i):
    W, H = 48, 56
    img = new(W, H)
    p = img.load()
    talk = i in (4, 5)
    recoil = i == 6
    ph = i * math.pi / 2
    lean = -3 if recoil else 0
    cx, hood_cy, hood_r = 22 + lean, 15 + (2 if recoil else 0), 10.5
    body_top, hem = 24 + (2 if recoil else 0), 47
    r = rng(100 + i)
    mask = set()
    for y in range(H):
        for x in range(W):
            fx, fy = x + 0.5, y + 0.5
            inside = math.hypot(fx - cx, (fy - hood_cy) * 1.05) < hood_r
            # hood point trailing back
            if not inside and hood_cy - hood_r - 7 <= fy < hood_cy - hood_r + 3:
                k = (fy - (hood_cy - hood_r - 7)) / 10
                tc = cx - 6 * (1 - k) - 2
                inside = abs(fx - tc) < 0.8 + k * 6
            if not inside and body_top <= fy < hem:
                k = (fy - body_top) / (hem - body_top)
                c = cx - 2 * k + (lean * 0.5 * (1 - k))
                inside = abs(fx - c) < 11 + 7 * k
            if not inside and fy >= hem:
                k = fy - hem
                for j in range(6):  # tattered hem that ripples
                    tx = cx - 17 + j * 6.2 + math.sin(ph + j * 1.9) * 1.5 - k * 0.4
                    ln = 4 + 3 * math.sin(ph * 0.5 + j * 2.3) - (2 if recoil else 0)
                    if k < ln and abs(fx - tx) < 2.4 - k * 0.45:
                        inside = True
            # arm reaching forward to where a lantern would hang
            if not inside and not recoil and 28 <= fy < 32 and cx + 6 < fx < cx + 16:
                inside = True
            if inside:
                mask.add((x, y))
    # ragged, flickering edge
    for (x, y) in list(mask):
        edge = any((x + dx, y + dy) not in mask for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if edge and r.random() < 0.22:
            mask.discard((x, y))
    for (x, y) in list(mask):
        if r.random() < 0.05:
            for dx, dy in ((1, 0), (-1, 0), (0, -1)):
                if 0 <= x + dx < W and 0 <= y + dy < H - 1:
                    mask.add((x + dx, y + dy))
    for (x, y) in mask:
        d = math.hypot(x - cx + 5, y - hood_cy + 4) / 40
        p[x, y] = DEEP[1] if dith(x, y, max(0.0, 0.55 - d)) else INK
    # the face: deeper black under the hood
    vcx, vcy = cx + hood_r * 0.38, hood_cy + 1
    for (x, y) in mask:
        if ((x + 0.5 - vcx) / (hood_r * 0.62)) ** 2 + ((y + 0.5 - vcy) / (hood_r * 0.55)) ** 2 < 1:
            p[x, y] = hexc("#05030a")
    # ragged scarf of shadow drifting behind
    for k in range(18):
        sx = int(cx - 6 - k)
        sy = int(body_top - 1 + k * 0.35 + math.sin(ph + k * 0.5) * 1.6)
        thick = 3 if k < 12 else 2
        if k > 14 and (k + i) % 2:
            continue
        for t in range(thick):
            if 0 <= sx < W and 0 <= sy + t < H:
                p[sx, sy + t] = CLOAK[1] if t == 0 else (CLOAK[0] if t == 1 else DEEP[2])
    for x in range(int(cx - 6), int(cx + 9)):  # wrap at the neck
        for t in range(3):
            y = body_top - 1 + t
            p[x, y] = CLOAK[1] if t == 0 else (CLOAK[0] if t == 1 else DEEP[2])
    o = outline(img, CLOAK[1])
    q = o.load()
    # violet sheen on the upper-left rim
    for y in range(H):
        for x in range(W):
            if q[x, y] == CLOAK[1] and y < hood_cy + 4 and x < cx and (x + y) % 2 == 0:
                q[x, y] = CLOAK[2]
    # the lantern-shaped hole where its light used to be
    if not recoil:
        lx, ly = int(cx + 15), 30
        hole = [
            "..xxx..",
            ".x...x.",
            "xxxxxxx",
            "x.....x",
            "x.....x",
            "x.....x",
            "x.....x",
            "x.....x",
            "xxxxxxx",
            ".x...x.",
        ]
        for yy, row in enumerate(hole):
            for xx, ch in enumerate(row):
                X, Y = lx - 3 + xx, ly + yy
                if 0 <= X < W and 0 <= Y < H:
                    if ch == "x":
                        q[X, Y] = CLOAK[2] if (X + Y) % 3 else CLOAK[3]
                    else:
                        q[X, Y] = CLEAR
    # eyes: two large pale lights
    ex, ey = int(vcx - 3), int(vcy - 1)
    if recoil:
        for x in (ex - 1, ex, ex + 1, ex + 4, ex + 5, ex + 6):
            q[x, ey + 1] = BONE[2]
    else:
        for (ox) in (0, 5):
            for (dx, dy) in ((0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)):
                q[ex + ox + dx, ey + dy] = BONE[4] if dy == 0 else BONE[3]
            if talk:  # eyes flare
                for (dx, dy) in ((-1, 1), (2, 1), (0, -1), (1, -1), (0, 3), (1, 3)):
                    q[ex + ox + dx, ey + dy] = CLOAK[3] if i == 4 else CLOAK[2]
                q[ex + ox, ey] = hexc("#ffffff")
                q[ex + ox + 1, ey] = hexc("#ffffff")
    return o


def hollow_one():
    return [hollow_one_frame(i) for i in range(7)]


# ------------------------------------------------------- Hero scarf stages --

def scarf_stage(stage):
    """Returns a replacement for hero.scarf: the wick burns shorter each stage."""
    K = hero.KEY

    def scarf(img, x, y, phase, run):
        p = img.load()
        wrap = 7 if stage == 1 else 6
        for i in range(wrap):
            p[x + i, y] = K["t"] if i in (4, 5) else K["s"]
            p[x + i, y + 1] = K["r"] if i < wrap - 1 else K["s"]
        if stage == 1:
            length = 3 if run else 2
            for i in range(length):
                tx = x - 1 - i
                wave = [0, 0, 1, 1, 0, -1, -1, 0][(i + phase) % 8] if run else min(i, 1)
                ty = y + 1 + wave
                last = i == length - 1
                if 0 <= tx < hero.F:
                    p[tx, ty] = SINGED if last else (K["s"] if i < length - 2 else K["q"])
                    if run and i == 0:
                        p[tx, ty + 1] = K["r"]
        else:
            # a burnt stub with one live ember at its tip
            wob = [0, 0, 1, 0][phase % 4] if run else 0
            p[x - 1, y + 1] = CHAR
            p[x - 2, y + 1 + wob] = FIRE[4]
    return scarf


def hero_stage_anims(stage):
    original = hero.scarf
    hero.scarf = scarf_stage(stage)
    try:
        F = hero.frame
        idle = [
            F(hero.CLOAK_IDLE, bob=0),
            F(hero.CLOAK_IDLE, bob=0, lantern=(0, 1)),
            F(hero.CLOAK_IDLE, bob=1, lantern=(0, 1), tip_dy=1),
            F(hero.CLOAK_IDLE, bob=1, lantern=(0, 0), tip_dy=1),
            F(hero.CLOAK_IDLE, bob=0, blink=True),
            F(hero.CLOAK_IDLE, bob=0, lantern=(0, 1)),
        ]
        run_poses = [
            (hero.CLOAK_RUN_A, 0, (-2, 0), (2, 1), (1, 1)),
            (hero.CLOAK_RUN_A, -1, (-1, 1), (2, 0), (1, 2)),
            (hero.CLOAK_RUN_B, 0, (0, 2), (0, 0), (0, 2)),
            (hero.CLOAK_RUN_B, 0, (2, 1), (-2, 0), (0, 1)),
            (hero.CLOAK_RUN_A, -1, (2, 0), (-1, 1), (1, 1)),
            (hero.CLOAK_RUN_B, 0, (0, 0), (0, 2), (1, 2)),
        ]
        run = [F(c, bob=b, hood_dx=1, legs=(bl, fl), scarf_phase=i, run=True, lantern=ln, tip_dy=(i % 2))
               for i, (c, b, bl, fl, ln) in enumerate(run_poses)]
        jump = [
            F(hero.CLOAK_JUMP, bob=-1, legs=((-1, 2), (1, 1)), run=True, scarf_phase=2, lantern=(0, 2), tip_dy=1),
            F(hero.CLOAK_JUMP, bob=-1, legs=((-1, 1), (1, 2)), run=True, scarf_phase=3, lantern=(0, 2), tip_dy=1),
        ]
        fall = [
            F(hero.CLOAK_FALL, bob=-1, legs=((-1, 0), (1, 1)), run=True, scarf_phase=5, lantern=(0, -1), tip_dy=-1),
            F(hero.CLOAK_FALL, bob=-1, legs=((-1, 1), (1, 0)), run=True, scarf_phase=6, lantern=(0, -1), tip_dy=-1),
        ]
        land = [
            F(hero.CLOAK_LAND, bob=2, lantern=(0, 2), tip_dy=2),
            F(hero.CLOAK_IDLE, bob=1, lantern=(0, 1), tip_dy=1),
        ]
    finally:
        hero.scarf = original
    return {"idle": idle, "run": run, "jump": jump, "fall": fall, "land": land}


# --------------------------------------------------------------------- build --

def build():
    sheets = {
        "archivist": archivist(),
        "bell": bell(),
        "gudgeon": gudgeon(),
        "rootmother": rootmother(),
        "sprig": sprig(),
        "hollow_one": hollow_one(),
        "keeper_ghost": keeper_ghost(),
        "sapling_tree": [sapling_tree(0), sapling_tree(1)],
    }
    for name, frames in sheets.items():
        save(sheet(frames), f"sprites/{name}.png")
    stages = {}
    for stage in (1, 2):
        anims = hero_stage_anims(stage)
        stages[stage] = anims
        for name, frames in anims.items():
            save(sheet(frames), f"sprites/hero_{name}_s{stage}.png")
    preview(sheets, stages)


def preview(sheets, stages):
    hero_idle = hero.frame(hero.CLOAK_IDLE)
    hero_run = hero.frame(hero.CLOAK_RUN_A, bob=0, hood_dx=1, legs=((-2, 0), (2, 1)), run=True, lantern=(1, 1))
    lineup = [hero_idle, hero_run, stages[1]["idle"][0], stages[1]["run"][0], stages[2]["idle"][0],
              stages[2]["run"][0]]
    for name in ("archivist", "keeper_ghost", "bell", "sprig", "sapling_tree", "gudgeon",
                 "hollow_one", "rootmother"):
        lineup += sheets[name]
    pad = 3
    rows, row, wsum = [], [], 0
    for img in lineup:
        if wsum + img.width + pad > 330:
            rows.append(row)
            row, wsum = [], 0
        row.append(img)
        wsum += img.width + pad
    rows.append(row)
    heights = [max(i.height for i in r) + 6 for r in rows]
    comp = new(336, sum(heights) + 4, hexc("#141a2c"))
    cp = comp.load()
    base = 0
    for r, items in enumerate(rows):
        base += heights[r]
        x = 4
        for xx in range(comp.width):
            cp[xx, base] = hexc("#2a3350")
        for img in items:
            comp.alpha_composite(img, (x, base - img.height))
            x += img.width + pad
    save_preview(comp, "npcs2_sheet.png", 3, bg=hexc("#141a2c"))


if __name__ == "__main__":
    build()
