"""NPCs and Old Hollow set pieces.

Every sheet is a horizontal strip of equal frames, base on the bottom row,
facing right. Run `python npcs.py`; a combined preview lands in
_preview/npcs_sheet.png next to the hero and Mossback for scale.
"""
import math

import hero
from deco import blob, totem_frames
from pix import (BONE, CLOAK, CRYSTAL, DEEP, FIRE, GLOW, GRASS, INK, PINK, RED, ROCK, SKY, STONE,
                 WOOD, CLEAR, dith, hexc, new, outline, paste, ramp_at, rng, save, save_preview,
                 sheet, sprite)

WAX = [hexc(c) for c in ("#3a2a2c", "#6b5048", "#a3836a", "#d4b78e", "#f0dfb6", "#fff6dc")]
BRASS = [hexc(c) for c in ("#3a2418", "#6e4a2a", "#a87a3c", "#d9ad5c", "#f4dc96")]
FUR = [hexc(c) for c in ("#1c1120", "#2f1d2c", "#47293b", "#603a4a", "#7d5460", "#9a7174")]
GLOWWORM = [hexc(c) for c in ("#3d5a2a", "#7fae47", "#c8f07a", "#f4ffc0")]
METAL = hero.METAL
PALM = [hexc("#b07f86"), hexc("#dcb0ad")]


def soft_blob(w, h, circles, ramp, light=(-0.45, -0.89)):
    """Like deco.blob but with flat bands of colour (dither only on band seams) - reads cleaner on characters."""
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
            t = 0.5 + 0.45 * lit - 0.25 * k * k
            v = max(0.0, min(0.999, t)) * (len(ramp) - 1)
            i = int(v)
            frac = v - i
            if 0.42 < frac < 0.58 and dith(x, y, 0.5):
                i += 1
            elif frac >= 0.58:
                i += 1
            p[x, y] = ramp[min(i, len(ramp) - 1)]
    return img


def rows_at(img, x0, y0, rows, key):
    """Paste ASCII rows at (x0, y0); '.' and unknown chars stay untouched."""
    p = img.load()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            c = key.get(ch)
            if c is not None and 0 <= x0 + x < img.width and 0 <= y0 + y < img.height:
                p[x0 + x, y0 + y] = c


# --------------------------------------------------------------- Nan Tallow --

TW, TH = 20, 34
TALLOW_FACE_KEY = {"g": BRASS[1], "G": WAX[5], "k": INK, "l": WAX[5], "c": hexc("#e39a86"),
                   "m": WAX[0], "n": RED[1], "b": WAX[2]}


def tallow_frame(bright, talk, flick):
    img = new(TW, TH)
    p = img.load()
    x0, x1 = 5, 14
    top = 11
    bottom = 30
    for x in range(x0 - 1, x1 + 2):
        for y in range(top, bottom + 1):
            inside = x0 <= x <= x1 and not (y == top and x in (x0, x1))
            if not inside and y >= 27:
                inside = y >= 27 + (1 if x in (x0 - 1, x1 + 1) else 0)  # wax pooling at the foot
            if not inside:
                continue
            u = (x - (x0 - 1) + 0.5) / (x1 - x0 + 3)
            t = 0.22 + 0.6 * math.sin(math.pi * u) - (0.16 if x >= 12 else 0)
            p[x, y] = ramp_at(WAX[1:5], t, x, y)
    # band of fresh melted wax across the top, dripping down in rounded runs
    drips = {5: 2, 6: 4, 7: 2, 8: 1, 9: 2, 10: 3, 11: 1, 12: 2, 13: 5, 14: 2}
    for x, ln in drips.items():
        for y in range(top, top + 1 + ln):
            if (x, y) in ((x0, top), (x1, top)):
                continue
            hi = x < 12
            p[x, y] = (WAX[5] if hi else WAX[4]) if y < top + ln else (WAX[4] if hi else WAX[3])
    if bright:  # the flame warms the top of her head
        for x in range(7, 13):
            p[x, top] = FIRE[5]
    # face (looking a little to the right): round spectacles, kind eyes, smile
    face = [
        ".gg..gg.",
        "gGkggGkg",
        ".gg..gg.",
        "c......c",
    ]
    rows_at(img, 6, 16, face, TALLOW_FACE_KEY)
    mouth = (["mnnm", ".mm."] if talk else ["m..m", ".mm."])
    rows_at(img, 8, 19, mouth, TALLOW_FACE_KEY)
    # knitted shawl over the shoulders, tied at the front
    shawl = [
        ".abbbbbbbbbba.",
        "abcbcbcbcbcbcba",
        "abcbcbcbcbcbcba",
        ".abcbcbcbcbcba.",
        "...abcbcbcbba..",
        ".....abddba....",
        ".....a.da.a....",
    ]
    key = {"a": PINK[0], "b": PINK[1], "c": PINK[2], "d": PINK[3]}
    rows_at(img, 2, 21, shawl, key)
    body = outline(img, INK)
    # brass saucer she stands in (drawn after the outline so it overlaps the foot)
    saucer = [
        "..bccccccccccccccb..",
        ".abbbbbbbbbbbbbbbba.",
        "..aaaaaaaaaaaaaaaa..",
    ]
    tray = new(TW, 4)
    rows_at(tray, 0, 0, saucer, {"a": BRASS[1], "b": BRASS[2], "c": BRASS[3]})
    paste(body, outline(tray, INK), 0, TH - 4)
    q = body.load()
    for (dx, dy) in ((4, 30), (15, 30), (16, 30)):  # wax spilling over the saucer rim
        q[dx, dy] = WAX[3]
    # wick and flame (no outline: flames glow)
    wick_x = 10
    for y in (8, 9, 10):
        q[wick_x, y] = INK
    q[wick_x + 1, 7] = INK
    q[wick_x - 1, 10] = CLEAR
    q[wick_x + 1, 10] = CLEAR
    if bright:
        flames = [
            ["...e..", "..ed..", "..dfe.", ".dffd.", ".dfgd.", ".cfgd.", "..dfc.", "..cd.."],
            ["..e...", "..de..", ".edf..", ".dffd.", ".dfgd.", ".cfgdc", "..fdc.", "..cd.."],
        ]
        fkey = {"c": FIRE[1], "d": FIRE[2], "e": FIRE[3], "f": FIRE[4], "g": FIRE[5]}
        rows_at(body, wick_x - 2, 0, flames[flick], fkey)
        q[wick_x + 1, 7] = FIRE[3]
    else:
        flames = [
            ["..c.", ".dc.", ".bb.", ".ba."],
            ["....", ".c..", ".dbc", ".ba."],
        ]
        fkey = {"a": CRYSTAL[1], "b": CRYSTAL[2], "c": FIRE[1], "d": FIRE[2]}
        rows_at(body, wick_x - 1, 3, flames[flick], fkey)
    return body


def tallow():
    frames = []
    for bright in (False, True):
        frames += [tallow_frame(bright, False, 0), tallow_frame(bright, False, 1),
                   tallow_frame(bright, True, 0), tallow_frame(bright, False, 1)]
    return frames


# --------------------------------------------------------------------- Pell --

def pell():
    """Fluffy cream moth seen from the front, 11x10, 4-frame flap (up, mid, down, mid)."""
    key = {"n": WOOD[3], "k": INK, "f": hexc("#fbf3dc"), "d": BONE[4], "c": BONE[3],
           "e": WOOD[3], "b": BONE[2], "a": WOOD[2]}
    frames = {
        "up": [
            "dn.....nd",
            "dd.n.n.dd",
            "cdekfkedc",
            ".cdcfcdc.",
            "...cfc...",
            "...beb...",
            "....b....",
        ],
        "mid": [
            ".n.....n.",
            "..n...n..",
            "dd.kfk.dd",
            "dedcfcded",
            "cddcfcddc",
            ".cdbebdc.",
            "..c.b.c..",
        ],
        "down": [
            ".n.....n.",
            "..n...n..",
            "...kfk...",
            ".ddcfcdd.",
            "deddfdded",
            "cdcbebcdc",
            ".cc.b.cc.",
        ],
    }
    out = []
    for name, bob in (("up", 0), ("mid", 1), ("down", 1), ("mid", 0)):
        img = new(11, 10)
        rows_at(img, 1, 1 + bob, frames[name], key)
        out.append(outline(img, INK))
    return out


# ------------------------------------------------------------------- Burrow --

BURROW_KEY = {"h": BRASS[2], "H": BRASS[3], "I": BRASS[4], "i": BRASS[1], "j": BRASS[0],
              "p": PINK[1], "q": PINK[2], "r": PINK[3], "s": PINK[4],
              "w": BONE[2], "W": BONE[3], "X": BONE[4], "k": INK, "m": FUR[0], "n": RED[1],
              "e": FUR[4], "E": FUR[5], "y": WOOD[1], "x": WOOD[2], "z": WOOD[3],
              "S": STONE[2], "T": STONE[3], "U": STONE[4], "R": STONE[1]}


def burrow_frame(breath, talk, nose):
    W, H = 26, 24
    img = new(W, H)
    # pickaxe he leans on like a walking stick: head up, handle to the ground
    pick = [
        "..RSTTU..",
        ".RSTTUUTS",
        "RS..xz..R",
        "R...xz...",
        "....xz...",
    ]
    rows_at(img, 16, 3, pick, BURROW_KEY)
    p = img.load()
    for y in range(8, H - 1):
        p[20, y] = WOOD[2]
        p[21, y] = WOOD[3] if y % 5 else WOOD[4]
    # round furry body + head, shaded like the rest of the props
    body = soft_blob(W, H, [(11, 11 + breath, 6.5), (11, 17, 7.5), (16, 11.5 + breath, 3.2)], FUR[1:6])
    paste(img, body, 0, 0)
    # lighter belly
    for y in range(14, 22):
        for x in range(11, 17):
            if math.hypot((x - 14.5) / 3.2, (y - 18) / 4.2) < 1 and p[x, y][3]:
                p[x, y] = FUR[4] if dith(x, y, 0.6) else FUR[3]
    # feet
    rows_at(img, 6, 22, ["qqWW..qqWW"], BURROW_KEY)
    # snout + big pink nose
    by = breath
    rows_at(img, 15, 10 + by - nose, ["eE.pq.", "eepqrsq", "eepqqrq", "e..ppq."], BURROW_KEY)
    p[15, 11 + by] = FUR[3]
    # whiskers
    p[22, 13 + by - nose] = BONE[2]
    p[23, 14 + by - nose] = BONE[2]
    # blind eye: a tiny closed crease
    p[12, 8 + by] = FUR[5]
    p[13, 8 + by] = FUR[5]
    p[12, 9 + by] = FUR[0]
    p[13, 9 + by] = FUR[0]
    p[14, 8 + by] = FUR[0]
    # mouth
    if talk:
        rows_at(img, 16, 14 + by, ["mm", "nm"], BURROW_KEY)
    else:
        p[16, 14 + by] = FUR[0]
        p[17, 14 + by] = FUR[0]
    # battered miner's cap with an empty lamp bracket
    cap = [
        "...hhhHH...",
        "..hHHIIHHh.",
        ".hhHHHHHjjh",
        ".ihhhhhhjkh",
        "iiiiiiiiiiiii",
    ]
    rows_at(img, 5, 1 + by, cap, BURROW_KEY)
    p[9, 2 + by] = BRASS[1]  # dent
    p[10, 3 + by] = BRASS[2]
    # huge pale digging claws wrapped round the handle
    arm = ["eeE", "deeE"]
    rows_at(img, 15, 16 + by, arm, {"d": FUR[3], "e": FUR[4], "E": FUR[5]})
    claws = [
        "rrX.X",
        "qrrXX",
        ".qqW.",
    ]
    rows_at(img, 17, 16 + by, claws, {**BURROW_KEY, "r": PALM[1], "q": PALM[0]})
    # tiny tail
    p[3, 20] = FUR[3]
    p[2, 21] = FUR[2]
    return outline(img, INK)


def burrow():
    return [burrow_frame(0, False, 0), burrow_frame(1, False, 0),
            burrow_frame(0, True, 1), burrow_frame(0, False, 0)]


# --------------------------------------------------------------------- Wisp --

def wisp():
    out = []
    for glowing in (False, True):
        if glowing:
            ramp = {"a": GLOWWORM[0], "b": GLOWWORM[1], "c": GLOWWORM[2], "d": GLOWWORM[3]}
        else:
            ramp = {"a": BONE[0], "b": hexc("#625a6a"), "c": BONE[1], "d": BONE[2]}
        ramp.update({"w": BONE[4], "k": INK, "o": BONE[3]})
        flat = [
            "......abb.",
            "dccbbabwwb",
            "dccbabbwkb",
            ".cc.aa.bb.",
        ]
        arch = [
            "...bb.abb.",
            "dcbbababwk",
            "dc..abbbwk",
            ".c...a.bb.",
        ]
        for shape in (flat, arch):
            img = new(12, 8)
            rows_at(img, 1, 3, shape, ramp)
            o = outline(img, INK)
            if glowing:  # the tail light glows past the outline
                q = o.load()
                q[1, 4] = GLOWWORM[3]
                q[1, 5] = GLOWWORM[3]
            out.append(o)
    return out


# ---------------------------------------------------------------------- Ash --

ASH_KEY = dict(hero.KEY)
ASH_KEY.update({
    "a": STONE[0], "b": STONE[1], "c": STONE[2], "d": STONE[3], "e": STONE[4],
    "q": hexc("#2f2b36"), "r": BONE[0], "s": BONE[1], "t": BONE[2],
    "F": FIRE[1], "G": FIRE[2], "H": FIRE[3],
})
COLD_LANTERN = [
    ".nnn.",
    ".n.n.",
    "mmnmm",
    "mSRSm",
    "mRZRm",
    "mRZRm",
    "mmmmm",
]
WEAK_LANTERN = [
    "..n..",
    ".mnm.",
    "mnnnm",
    "mZZZm",
    "mZGZm",
    "mFHFm",
    ".mnm.",
]
CLOAK_SIT = [  # knees drawn up under the cloak
    "...bbcddcc...",
    "..abccdddccc.",
    ".aabccdddcddc",
    ".aabbccddcddc",
    "aaabbccdddccc",
    "aaaabbbcccccb",
]
ASH_KEY.update({"R": STONE[3], "S": STONE[4], "Z": STONE[1], "o": METAL[2]})


def ash_sit(lift, breath):
    img = new(hero.F, hero.F)
    p = img.load()
    k = ASH_KEY
    feet = hero.F - 1
    body_top = feet - len(CLOAK_SIT) + 1
    paste(img, sprite(CLOAK_SIT, k), 7, body_top)
    # boots poking out under the hem in front
    for (bx, col) in ((18, hero.BOOT[0]), (20, hero.BOOT[1])):
        p[bx, feet] = col
        p[bx + 1, feet] = col
        p[bx + 1, feet - 1] = col
    # hood: slumped forward onto the knees unless lifted
    hood_dy = (2 if not lift else 0) + breath
    hood_dx = 2 if not lift else 0
    hood_top = body_top - 9 + hood_dy
    paste(img, sprite(hero.HOOD_TIP, k), 6 + hood_dx, hood_top + 1 + (1 if not lift else 0))
    hood = sprite(hero.HOOD, k)
    hp = hood.load()
    if lift:
        for (ex, ey) in hero.EYES_OPEN:
            hp[ex, ey] = BONE[2] if ey == 7 else BONE[1]
    else:  # looking down at the cold lantern
        hp[10, 9] = BONE[1]
        hp[11, 9] = BONE[0]
        hp[8, 9] = BONE[1]
    paste(img, hood, 8 + hood_dx, hood_top)
    # scarf hanging limp
    sx, sy = 10 + hood_dx // 2, hood_top + 10
    for i in range(7):
        if 0 <= sy + 1 < hero.F:
            p[sx + i, sy] = k["t"] if i in (4, 5) else k["s"]
            p[sx + i, sy + 1] = k["r"] if i < 6 else k["s"]
    for i in range(3):
        if sy + 2 + i < hero.F:
            p[sx, sy + 2 + i] = k["s"] if i < 2 else k["r"]
    # cold lantern set down beside them
    paste(img, sprite(COLD_LANTERN, k), 24, feet - 6)
    return outline(img, INK)


def ash_stand(variant):
    """Standing grey wanderer holding a weakly lit lantern (hero.frame with the ash palette)."""
    saved = dict(hero.KEY)
    saved_lantern = list(hero.LANTERN_DIM)
    hero.KEY.clear()
    hero.KEY.update(ASH_KEY)
    hero.LANTERN_DIM[:] = WEAK_LANTERN
    try:
        img = hero.frame(hero.CLOAK_IDLE, bob=variant, lantern=(0, variant), tip_dy=variant, dim=True)
    finally:
        hero.KEY.clear()
        hero.KEY.update(saved)
        hero.LANTERN_DIM[:] = saved_lantern
    # hero.frame paints a few fixed colours (glowing eyes, purple arm): drain them
    swap = {GLOW: BONE[3], hexc("#fffbe6"): BONE[2]}
    swap.update({CLOAK[i]: STONE[i] for i in range(5)})
    p = img.load()
    for y in range(img.height):
        for x in range(img.width):
            if p[x, y] in swap:
                p[x, y] = swap[p[x, y]]
    return img


def ash():
    return [ash_sit(False, 0), ash_sit(False, 1), ash_sit(True, 0), ash_sit(True, 1),
            ash_stand(0), ash_stand(1)]


# -------------------------------------------------------------------- Shade --

SHADE_BODY = [
    "....####....",
    "..########..",
    ".##########.",
    ".##########.",
    "############",
    "############",
    "############",
    ".##########.",
]
SHADE_TIPS = [  # a dark little flame licking backwards
    ["..#.........", "..##........", "..####......"],
    [".#..........", ".##.........", "..####......"],
    ["...#........", "..##........", "..####......"],
    ["..#.........", "...##.......", "..####......"],
]
SHADE_SQUASH = [
    "...####.....",
    ".#########..",
    "##########..",
    "##########..",
    "##########..",
]


def shade_hem(phase, width=12, lean=1):
    """Two rows of rippling ghost-hem points; `phase` slides them along."""
    row0 = "".join("#" if (x + phase) % 4 != 0 and 0 < x < width - 1 else "." for x in range(width))
    row1 = "".join("#" if (x + lean + phase) % 4 == 2 and 0 < x < width - 2 else "." for x in range(width))
    return [row0, row1]


def shade_frame(i, recoil=False):
    S = 16
    img = new(S, S)
    p = img.load()
    if recoil:
        rows = SHADE_SQUASH + shade_hem(i * 2, 11)[:1]
        ox, oy = 1, 8 + (i % 2)
        eye_row = oy + 2
    else:
        rows = SHADE_TIPS[i] + SHADE_BODY + shade_hem(i)
        ox, oy = 2, (1 if i in (0, 3) else 2)
        eye_row = oy + 3 + 3
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "#":
                X, Y = ox + x, oy + y
                if 0 <= X < S and 0 <= Y < S:
                    d = math.hypot(X - 5, Y - 5) / 10
                    p[X, Y] = DEEP[1] if dith(X, Y, max(0.0, 0.6 - d)) else INK
    o = outline(img, CLOAK[1])
    q = o.load()
    for y in range(S):  # faint violet sheen on the upper-left rim
        for x in range(S):
            if q[x, y] == CLOAK[1] and y < eye_row and x < ox + 6 and (x + y) % 2 == 0:
                q[x, y] = CLOAK[2]
    ex = ox + 7
    if recoil:  # squinting against the light
        for x in (ex - 2, ex - 1, ex + 1, ex + 2):
            q[x, eye_row] = BONE[2]
    else:
        for x in (ex, ex + 3):
            q[x, eye_row] = BONE[3]
            q[x, eye_row - 1] = INK if i == 3 else BONE[4]
    return o


def shade():
    return [shade_frame(i) for i in range(4)] + [shade_frame(0, True), shade_frame(1, True)]


# ------------------------------------------------------------ Little Hearth --

def hearth_frame(burn):
    W, H = 32, 28
    img = new(W, H)
    p = img.load()
    # bed of ash / coals inside the ring
    for x in range(6, 26):
        for y in (19, 20):
            p[x, y] = BONE[0] if not burn else (FIRE[1] if (x + y) % 3 else FIRE[2])
    # stacked logs (a little teepee and two cross logs)
    logs_cold = WOOD[1:4]
    logs = [
        (8, 18, 24, 18),
        (9, 17, 23, 17),
    ]
    for (xa, ya, xb, yb) in logs:
        for x in range(xa, xb + 1):
            p[x, ya] = logs_cold[1] if (x % 5) else logs_cold[0]
            p[x, ya - 1] = logs_cold[2] if x % 4 else logs_cold[1]
    # teepee of three logs leaning together
    for (xa, xb) in ((10, 15), (21, 16), (15, 15)):
        for k in range(8):
            y = 16 - k
            x = round(xa + (xb - xa) * k / 7)
            p[x, y] = logs_cold[0]
            p[x + 1, y] = logs_cold[2] if not burn else FIRE[0]
            if k == 7 and not burn:
                p[x, y] = WOOD[0]  # charred tips
    # log ends (cut rings)
    for (lx, ly) in ((7, 17), (25, 17)):
        rows_at(img, lx, ly - 1, ["ab", "ba"], {"a": WOOD[3], "b": WOOD[4]})
    # ring of stones, two staggered rows
    rr = rng(77)
    stones = [(x, 22, rr.uniform(2.6, 3.3)) for x in range(4, 30, 5)]
    stones += [(x, 25, rr.uniform(2.8, 3.4)) for x in range(2, 31, 5)]
    stones += [(3, 20, 2.4), (28, 20, 2.4)]
    for (sx, sy, sr) in stones:
        for y in range(H):
            for x in range(W):
                dx, dy = x + 0.5 - sx, (y + 0.5 - sy) * 1.2
                d = math.hypot(dx, dy)
                if d < sr:
                    lit = -(dx / sr * 0.45 + dy / sr * 0.89)
                    t = 0.45 + 0.4 * lit - 0.25 * (d / sr) ** 2
                    if burn and dy < 0:
                        t += 0.12
                    p[x, y] = ramp_at(STONE[1:5], t, x, y)
    for x in range(1, 31):  # flat base
        if p[x, H - 2][3]:
            p[x, H - 2] = STONE[1]
    for (x, y) in ((6, 21), (17, 23), (24, 20)):  # moss tufts on the stones
        p[x, y] = GRASS[3]
        p[x + 1, y] = GRASS[2]
    body = outline(img, INK)
    if burn:
        flames = [
            ["......e.........", ".....ed....e....", ".....dfe..ed....", "....dffe..dfd...",
             "...edffd.dffd...", "...dffgfddfgfd..", "..cdfggffffgfd..", "..cdfgggggffdc..",
             ".ccdffggggffdcc.", ".cddffggggfffdc.", "ccdddfffffffddcc", ".ccdddfffffdddc.",
             "..cccddddddccc.."],
            ["........e.......", "...e....de......", "...de..edf......", "...dfe.dffd.....",
             "..edffddffd..e..", "..dffgfffgfd.d..", ".cdffggffgffdd..", ".cdfgggggggffdc.",
             ".ccdffgggggfdcc.", "ccddffggggfffdc.", "ccdddfffffffdccc", ".ccdddffffdddcc.",
             "..cccddddddccc.."],
            [".......e........", "......de...e....", ".e....dfe.ed....", ".de..dffe.dfd...",
             "..dddffgd.dffd..", "..dffgggfddfgfd.", "..cdfggggfffgfd.", ".ccdfggggggffdc.",
             ".ccdffggggffddc.", ".cddffggggfffdcc", "ccdddfffffffddcc", ".ccdddfffffdddc.",
             "..cccddddddccc.."],
            ["....e...........", "....de....e.....", "...edf...de.....", "...dffe.edfd....",
             "..edffddffffd...", "..dffgffggffd...", "..cdfgggggfgfd..", ".ccdfgggggggfdc.",
             ".ccdffggggggfdc.", "ccddffgggggffdcc", "ccdddffffffffdcc", ".ccdddfffffdddc.",
             "..cccddddddccc.."],
        ]
        fkey = {"c": FIRE[1], "d": FIRE[2], "e": FIRE[3], "f": FIRE[4], "g": FIRE[5]}
        rows_at(body, 8, 6, flames[burn - 1], fkey)
        sparks = [((13, 2), (20, 4)), ((18, 1), (11, 4)), ((15, 0), (21, 3)), ((12, 1), (19, 2))]
        q = body.load()
        for (x, y) in sparks[burn - 1]:
            q[x, y] = FIRE[4]
    else:
        q = body.load()
        q[18, 18] = FIRE[1]  # one last red coal
        q[13, 19] = FIRE[0]
        for (x, y) in ((16, 7), (17, 5), (16, 3), (17, 1)):  # a thread of smoke: it only just went out
            q[x, y] = BONE[0]
    return body


def hearth_small():
    return [hearth_frame(0)] + [hearth_frame(i) for i in range(1, 5)]


# --------------------------------------------------------------- Hollow lamp --

def hollow_lamp():
    shape = [
        "...nn...",
        "..n..n..",
        "..mnnm..",
        ".mnnnnm.",
        ".mABBAm.",
        ".mBCCBm.",
        ".mBCCBm.",
        ".mABBAm.",
        ".mnnnnm.",
        "..mnnm..",
        "...mm...",
    ]
    out = []
    for lit in (False, True):
        if lit:
            glass = {"A": FIRE[3], "B": FIRE[4], "C": FIRE[5]}
        else:
            glass = {"A": STONE[0], "B": STONE[1], "C": STONE[2]}
        key = {"m": METAL[0], "n": METAL[1], **glass}
        img = new(8, 12)
        rows_at(img, 0, 0, shape, key)
        o = outline(img, INK)
        q = o.load()
        q[3, 0] = METAL[2]  # keep the hook's top pixel bright, not outlined
        q[4, 0] = METAL[2]
        out.append(o)
    return out


# ----------------------------------------------------------------- Hut door --

def hut_door(lit):
    W, H = 22, 26
    img = new(W, H)
    p = img.load()
    cx = 10.5
    # arch of fitted stones around the door
    for y in range(H):
        for x in range(W):
            d = math.hypot((x + 0.5 - cx) / 9.5, (y + 0.5 - 13) / 11.5)
            if y >= 13:
                d = abs(x + 0.5 - cx) / 9.5
            if d < 1.0:
                ang = math.atan2(y + 0.5 - 13, x + 0.5 - cx)
                block = int((ang + math.pi) / (math.pi / 7)) if y < 13 else (y - 13) // 3 + 20
                seam = (y >= 13 and (y - 13) % 3 == 2) or (y < 13 and abs(((ang + math.pi) / (math.pi / 7)) % 1 - 0.5) > 0.42)
                side = 0.62 if (x < cx) else 0.38
                c = ramp_at(STONE[1:5], side + (0.12 if block % 2 else -0.05) - 0.2 * d, x, y)
                p[x, y] = STONE[0] if seam else c
    # wooden round-topped door
    for y in range(H):
        for x in range(W):
            d = math.hypot((x + 0.5 - cx) / 6.5, (y + 0.5 - 13) / 8.0)
            if y >= 13:
                d = abs(x + 0.5 - cx) / 6.5
            if d < 1.0 and y < H - 1:
                plank = (x - 4) // 3
                seam = (x - 4) % 3 == 0
                c = WOOD[1] if seam else (WOOD[3] if plank % 2 else WOOD[2])
                if y in (12, 20) and not seam:
                    c = WOOD[4]  # cross braces
                if d > 0.86:
                    c = WOOD[0]
                p[x, y] = c
    # round window with a cross mullion
    win = [".aaa.", "abcba", "acccb", "abcba", ".aaa."]
    if lit:
        wkey = {"a": WOOD[0], "b": FIRE[4], "c": GLOW}
    else:
        wkey = {"a": WOOD[0], "b": SKY[1], "c": SKY[0]}
    rows_at(img, 8, 7, win, wkey)
    p[10, 9] = WOOD[1]  # mullion cross
    p[9, 9] = WOOD[1] if not lit else FIRE[3]
    p[11, 9] = WOOD[1] if not lit else FIRE[3]
    # brass knob
    p[14, 16] = BRASS[3]
    p[14, 17] = BRASS[1]
    # moss spilling over the top of the arch
    rr = rng(31)
    for x in range(2, 20):
        top = next((y for y in range(H) if p[x, y][3]), None)
        if top is None:
            continue
        p[x, top] = GRASS[4] if x % 3 else GRASS[5]
        p[x, top + 1] = GRASS[3]
        if rr.random() < 0.45:
            p[x, top + 2] = GRASS[2]
    for (rx, ry, ln) in ((2, 6, 4), (18, 5, 5)):  # a few trailing moss strands down the arch
        for k in range(ln):
            p[rx, ry + k] = GRASS[2] if k < ln - 1 else GRASS[3]
    # stepping stone
    for x in range(7, 15):
        p[x, H - 1] = STONE[2] if x % 4 else STONE[3]
    o = outline(img, INK)
    if lit:  # a little warm spill on the step
        q = o.load()
        for x in range(9, 13):
            if q[x, H - 1] != CLEAR:
                q[x, H - 1] = STONE[4]
    return o


# --------------------------------------------------------------------- build --

def build():
    sheets = {
        "sprites/tallow": tallow(),
        "sprites/pell": pell(),
        "sprites/burrow": burrow(),
        "sprites/wisp": wisp(),
        "sprites/ash": ash(),
        "sprites/shade": shade(),
        "sprites/hearth_small": hearth_small(),
        "sprites/hollow_lamp": hollow_lamp(),
    }
    for name, frames in sheets.items():
        save(sheet(frames), f"{name}.png")
    save(hut_door(False), "deco/hut_door.png")
    save(hut_door(True), "deco/hut_door_lit.png")
    preview(sheets)


def preview(sheets):
    """Every character in a row, standing on a ground line next to the hero and Mossback."""
    hero_idle = hero.frame(hero.CLOAK_IDLE)
    totem = totem_frames()[1]
    lineup = [hero_idle, totem]
    for name in ("tallow", "pell", "burrow", "wisp", "ash", "shade", "hearth_small", "hollow_lamp"):
        lineup += sheets[f"sprites/{name}"]
    lineup += [hut_door(False), hut_door(True)]
    pad = 3
    rows, row, wsum = [], [], 0
    for img in lineup:
        if wsum + img.width + pad > 300:
            rows.append(row)
            row, wsum = [], 0
        row.append(img)
        wsum += img.width + pad
    rows.append(row)
    rh = 48
    comp = new(304, rh * len(rows) + 4, hexc("#141a2c"))
    cp = comp.load()
    for r, items in enumerate(rows):
        x = 4
        base = rh * (r + 1)
        for xx in range(comp.width):
            cp[xx, base] = hexc("#2a3350")
        for img in items:
            comp.alpha_composite(img, (x, base - img.height))
            x += img.width + pad
    save_preview(comp, "npcs_sheet.png", 4, bg=hexc("#141a2c"))


if __name__ == "__main__":
    build()
