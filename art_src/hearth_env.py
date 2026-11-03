"""Chapter V - the Hearth: the cold heart of the mountain.

Run `python hearth_env.py` to (re)generate:

  tiles/hearth_ground.png  256x288  forest atlas layout; basalt with faint ember-crack
                                    veins, ash/cinder tops, obsidian drips hanging
                                    (row 16 cols 4-7), Keeper bronze bridge (row 17)
  tiles/hearth_wall.png    256x288  charcoal / red-black basalt (rows 0-15 used)
  bg/hearth_base.png       480x270  near-black, dim red glow from far below (factor 0)
  bg/hearth_far.png        640x270  giant Keeper statues holding up the roof
  bg/hearth_mid.png        640x270  basalt columns
  sprites/hearth_great.png 576x80   6 frames of 96x80:
                                    0 cold, 1 faint pulse, 2-5 roaring flame cycle.
                                    The Cradle (hood-shaped niche) interior spans
                                    x 40..55, y 36..59 of each frame; its floor is
                                    y = 60 (stand a 14x22 figure with feet on y 60,
                                    centred on x 48 -> 20px above the frame bottom).
  deco/keeper_giant, brazier_cold, obsidian, cinder_pile (bottom-centre)

Backdrop scene: scenes/backdrops/hearth.tscn. Previews: _preview/hearth_*.png
"""
import math

from bg import periodic_noise
from cave import prism
from envkit import (Mask, compose_backdrop, compose_scene, deco_rows_preview, ingame, pad_rows,
                    pnoise2, props_sheet, rim_light, scene_backdrop, shade_mask, vgrad, H, W)
from pix import FIRE, GLOW, INK, CLEAR, dith, hexc, new, outline, paste, ramp_at, rng, save, save_preview, sheet, sprite
from tiles import PERIOD, T, build_terrain, cobble

BASALT = [hexc(c) for c in ("#0d0b0e", "#1a161a", "#272126", "#352d33", "#463c42", "#5c5056")]
WALL = [hexc(c) for c in ("#070506", "#0d0809", "#140b0c", "#1b0f10", "#231315", "#2c1819")]
ASHR = [hexc(c) for c in ("#141113", "#2a2628", "#3d383a", "#55504f", "#706a67", "#8f8884")]
BRONZE = [hexc(c) for c in ("#2a1a12", "#4a2e1c", "#704626", "#9a6634", "#c48d4a", "#e0b46a")]
OBSIDIAN = [hexc(c) for c in ("#050407", "#0e0b12", "#1b1622", "#2e2838", "#6f6680")]
STATUE = [hexc(c) for c in ("#1a1619", "#2a2328", "#3a3137", "#4c4148", "#62555c", "#7c6d72")]
VOID = hexc("#07050a")

WALL_TINT = (0.62, 0.48, 0.5)


# ------------------------------------------------------------------ tiles ---

def basalt(seed, ramp, mortar, light_bias=0):
    return cobble(seed, ramp, mortar, cells=6, squash=1.0, light_bias=light_bias)


def make_veins(strength):
    def veins(tex, mort):
        p = tex.load()
        n = pnoise2(77, PERIOD, 4, 2)
        for y in range(PERIOD):
            for x in range(PERIOD):
                if not mort[y][x]:
                    continue
                v = n(x, y)
                if v > 0.62 - strength:
                    p[x, y] = FIRE[1] if v > 0.74 - strength and (x + y) % 3 == 0 else FIRE[0]
    return veins


def ash_profile(seed):
    r = rng(seed)
    top, th = [], []
    for x in range(PERIOD):
        top.append(1 if r.random() < 0.3 else 0)
        t = 1 if r.random() < 0.5 else 2
        if r.random() < 0.08:
            t += r.choice((1, 2))
        th.append(t)
    return top, th


def cinder_fringe(r, ph):
    f = new(T, T)
    p = f.load()
    x = 0
    while x < T:
        h = r.choice((0, 0, 1, 1, 1, 2))
        for y in range(h):
            p[x, T - 1 - y] = ASHR[3] if y == h - 1 else ASHR[2]
        if h and r.random() < 0.08:
            p[x, T - h] = FIRE[3]  # a speck that is still warm
        elif h == 1 and r.random() < 0.2:
            p[x, T - 1] = ASHR[1]  # dark cinder
        x += r.choice((1, 1, 2))
    return f


def obsidian_drips(r, ph):
    f = new(T, T)
    p = f.load()
    used = set()
    for _ in range(r.randint(1, 3)):
        x = r.randint(1, 13)
        if x in used or x + 1 in used:
            continue
        used.update((x - 1, x, x + 1, x + 2))
        ln = r.randint(3, 9)
        for y in range(ln):
            wide = y < ln * 0.6
            p[x, y] = OBSIDIAN[3] if y < ln - 1 else OBSIDIAN[2]
            if wide:
                p[x + 1, y] = OBSIDIAN[1]
        p[x, 1] = OBSIDIAN[4]  # glassy highlight
        if r.random() < 0.4:
            p[x, ln - 1] = FIRE[1]
    return f


def bronze_bridge(i):
    f = new(T, T)
    p = f.load()
    for x in range(T):
        p[x, 0] = BRONZE[5] if (x + i * 3) % 8 == 2 else BRONZE[4]
        p[x, 1] = BRONZE[3]
        p[x, 5] = BRONZE[2]
        p[x, 6] = BRONZE[0]
        for y in (2, 3, 4):
            p[x, y] = BRONZE[2]
    # pierced roundels along the side
    for cx in (3.5, 11.5):
        for y in (2, 3, 4):
            for x in range(int(cx) - 1, int(cx) + 2):
                d = math.hypot(x + 0.5 - (cx + 0.5), y + 0.5 - 3.5)
                if d < 0.8:
                    p[x, y] = CLEAR
                elif d < 1.6:
                    p[x, y] = BRONZE[1] if y > 3 else BRONZE[3]
    if i in (0, 3):
        e = 0 if i == 0 else T - 1
        s = 1 if i == 0 else -1
        p[e, 0] = CLEAR
        for y in range(1, 7):
            p[e, y] = BRONZE[1]
        p[e + s, 7] = BRONZE[2]  # finial bracket
        p[e + s, 8] = BRONZE[3]
        p[e + 2 * s, 8] = BRONZE[2]
        p[e + s, 9] = BRONZE[1]
    return f


def build_tiles():
    ground = build_terrain("hearth_ground", BASALT, (BASALT[0], BASALT[0]), seed=61,
                           moss=ASHR, profile=ash_profile(161), tex_post=make_veins(0.0),
                           fringe=cinder_fringe, hang=obsidian_drips, texture=basalt, platform=bronze_bridge)
    wall = build_terrain("hearth_wall", WALL, (WALL[0], WALL[0]), seed=62, grass=False,
                         texture=basalt, tex_post=make_veins(-0.06))
    return ground, wall


# --------------------------------------------------------------- backdrop ---

BASE_RAMP = [hexc(c) for c in ("#050304", "#0a0506", "#120708", "#1c0a0a", "#2a0e0b", "#3a140d")]


def hearth_base():
    img = new(W, H)
    vgrad(img, BASE_RAMP, [(0, 0.0), (140, 0.12), (210, 0.45), (250, 0.8), (270, 1.0)])
    p = img.load()
    cx, cy, rad = 240, 300, 200
    for y in range(120, H):
        for x in range(W):
            d = math.hypot(x - cx, (y - cy) * 1.6) / rad
            if d < 1 and dith(x, y, (1 - d) * 0.5):
                p[x, y] = hexc("#3a140d") if d < 0.55 else hexc("#2a0e0b")
    r = rng(57)
    for _ in range(90):  # embers rising, ash falling
        x, y = r.randrange(W), int(H - r.random() ** 1.6 * H)
        b = r.random()
        p[x, y] = FIRE[2] if b > 0.85 else (FIRE[1] if b > 0.5 else hexc("#3a3436"))
    return img


def statue_mask(m, cx, base, roof):
    """Front-facing hooded Keeper pressing the roof up with both hands."""
    s = (base - roof) / 190.0
    m.rect(cx - 26 * s, base - 14 * s, cx + 26 * s, base)                       # plinth
    m.poly([(cx - 21 * s, base - 14 * s), (cx + 21 * s, base - 14 * s),
            (cx + 13 * s, base - 112 * s), (cx - 13 * s, base - 112 * s)])     # robe
    m.ellipse(cx, base - 112 * s, 18 * s, 7 * s)                               # shoulders
    m.ellipse(cx, base - 128 * s, 13 * s, 15 * s)                              # hood
    m.poly([(cx - 9 * s, base - 136 * s), (cx, base - 154 * s), (cx + 9 * s, base - 136 * s)])
    for sx in (-1, 1):
        ex, ey = cx + sx * 31 * s, base - 140 * s                               # elbow
        m.line(cx + sx * 14 * s, base - 114 * s, ex, ey, width=max(3, int(8 * s)))
        m.line(ex, ey, cx + sx * 27 * s, roof + 8, width=max(3, int(7 * s)))
        m.rect(cx + sx * 27 * s - 8 * s, roof, cx + sx * 27 * s + 8 * s, roof + 8)


def statue_face(p, w, cx, base, roof, void):
    s = (base - roof) / 190.0
    fy = base - 124 * s
    for y in range(int(fy - 9 * s), int(fy + 9 * s) + 1):
        for x in range(int(cx - 8 * s), int(cx + 8 * s) + 1):
            if ((x - cx) / (7 * s)) ** 2 + ((y - fy) / (8.5 * s)) ** 2 <= 1 and 0 <= y < H:
                p[x % w, y] = void


def atlantes(seed, w=640):
    img = new(w, H)
    p = img.load()
    r = rng(seed)
    body, rim, red, void = hexc("#0f090a"), hexc("#1a1011"), hexc("#34120e"), hexc("#060304")
    m = Mask(w, H)
    roof, base = 34, 244
    f = periodic_noise(seed + 1, w, ((3, 1.0), (7, 0.5)))
    for x in range(w):
        m.rect(x, 0, x, int(roof + 3 * f(x)))
    statues = []
    for i in range(4):
        cx = (i + 0.5) * w / 4 + r.uniform(-8, 8)
        statues.append(cx)
        for off in (0, w, -w):
            statue_mask(m, cx + off, base, roof)
    for x in range(w):
        m.rect(x, int(base + 3 * f(x * 3 % w)), x, H - 1)
    for y in range(H):
        for x in range(w):
            if m.m[y][x]:
                p[x, y] = body
    rim_light(img, rim, below=red)
    s = (base - roof) / 190.0
    for cx in statues:
        statue_face(p, w, cx, base, roof, void)
        for k in (-1, 1):  # robe folds
            fx = int(cx + k * 6 * s)
            for y in range(int(base - 100 * s), int(base - 16 * s)):
                if p[fx % w, y] == body and y % 4:
                    p[fx % w, y] = rim
    for x in range(w):  # cornice under the roof, lit from far below
        y = int(roof + 3 * f(x)) + 1
        if 0 <= y < H and p[x, y][3] == 0:
            p[x, y] = red if dith(x, y, 0.5) else rim
    return img


def basalt_columns(seed, w=640):
    img = new(w, H)
    p = img.load()
    r = rng(seed)
    body, rim, top, joint = hexc("#0b0708"), hexc("#1a0d0c"), hexc("#2a120e"), hexc("#060405")
    x = 0
    tops = []
    while x < w:
        cw = r.randint(9, 17)
        group = r.random() < 0.6
        t = r.uniform(130, 235) if group else H + 1
        tops.append((x, cw, t))
        x += cw
    # make it wrap: last column ends exactly at w
    for (x0, cw, t) in tops:
        for x in range(x0, min(w, x0 + cw)):
            for y in range(int(t), H):
                p[x, y] = body
            if t < H:
                for y in range(int(t), min(H, int(t) + 2)):
                    p[x, y] = top
        if t < H:
            for y in range(int(t), H):
                p[x0 % w, y] = joint
                p[(x0 + cw - 1) % w, y] = rim
            for y in range(int(t) + 6, H, r.randint(14, 26)):  # cross joints
                for x in range(x0, min(w, x0 + cw)):
                    p[x, y] = joint
    f = periodic_noise(seed + 1, w, ((4, 1.0), (9, 0.5)))
    for x in range(w):  # broken columns heaped at the foot, so fill_below joins up
        y0 = int(258 + 4 * f(x))
        for y in range(y0, H):
            p[x, y] = rim if y == y0 else body
    return img


def build_backdrop():
    layers = {
        "base": hearth_base(),
        "far": atlantes(101),
        "mid": basalt_columns(102),
    }
    for name, img in layers.items():
        save(img, f"bg/hearth_{name}.png")
    return layers


# ------------------------------------------------------------------ props ---

def keeper_giant():
    """Huge front-facing Keeper statue, palms raised to hold up the dark."""
    w, h = 32, 64
    m = Mask(w, h)
    m.rect(2, 57, 29, 63)
    m.rect(1, 56, 30, 56)
    m.poly([(7, 56), (25, 56), (20.5, 32), (11.5, 32)])        # robe
    m.ellipse(16, 32, 8.5, 3.2)                                # shoulders
    m.ellipse(16, 24.5, 6.4, 7.6)                              # hood
    m.poly([(11.5, 20), (16, 12.5), (20.5, 20)])               # hood peak
    for sx in (-1, 1):
        ex = 16 + sx * 12
        m.line(16 + sx * 7, 31, ex, 21, width=3)               # upper arm
        m.line(ex, 21, 16 + sx * 11, 8, width=3)               # forearm
        m.rect(16 + sx * 11 - 3, 5, 16 + sx * 11 + 3, 7)       # open palm
    img = shade_mask(m, STATUE[1:6], lo=0.1, hi=0.9, vertical=0.1)
    p = img.load()
    for y in range(20, 33):                                    # face opening
        for x in range(11, 22):
            if ((x + 0.5 - 16) / 3.8) ** 2 + ((y + 0.5 - 27) / 4.6) ** 2 <= 1:
                p[x, y] = VOID
    for (x, y) in ((14, 27), (17, 27)):                        # two cold embers for eyes
        p[x, y] = FIRE[0]
    for x in range(10, 23):                                    # bronze girdle
        if p[x, 40][3]:
            p[x, 40] = BRONZE[3] if x < 16 else BRONZE[2]
            p[x, 41] = BRONZE[1]
    for (x, y) in ((15, 47), (16, 47), (17, 47), (14, 48), (18, 48), (15, 49), (16, 49), (17, 49)):
        p[x, y] = STATUE[1]                                    # Keeper eye carved on the robe
    p[16, 48] = FIRE[0]
    for y in range(43, 56):                                    # folds
        if y % 3:
            p[12 + (y - 43) // 6, y] = STATUE[1]
            p[20 - (y - 43) // 6, y] = STATUE[1]
    for x in range(2, 30):                                     # plinth groove + ember cracks
        p[x, 59] = STATUE[1]
    for (x, y) in ((9, 60), (10, 61), (10, 62), (22, 58), (23, 60)):
        p[x, y] = FIRE[0]
    for x in list(range(2, 9)) + list(range(24, 31)):          # palms catch the light
        if p[x, 5][3]:
            p[x, 5] = STATUE[4]
    return outline(img, INK)


def brazier_cold():
    s = [
        "abbbbbbbbbbbbbba",
        "acddeeeeeeeeddca",
        ".acdffgffhffdca.",
        ".abccddddddccba.",
        "..abccddddccba..",
        "...aabbccbbaa...",
        ".....abccba.....",
        "......acba......",
        "......acba......",
        ".....abccba.....",
        "......acba......",
        "......acba......",
        "......acba......",
        ".....abccba.....",
        "....abbccbba....",
        "...ab.acba.ba...",
        "..ab..acba..ba..",
        ".ab...acba...ba.",
        "ab....abba....ba",
        "aa....aaaa....aa",
    ]
    key = {"a": INK, "b": BRONZE[1], "c": BRONZE[2], "d": BRONZE[3], "e": BRONZE[4],
           "f": ASHR[2], "g": ASHR[3], "h": FIRE[1]}
    img = sprite(s, key)
    p = img.load()
    for x in range(2, 14):  # cold ash heaped in the bowl
        p[x, 1] = ASHR[3] if x % 3 else ASHR[4]
    p[9, 1] = FIRE[0]
    return img


def obsidian():
    img = new(12, 16)
    for (x0, height, width, lean) in ((3, 9, 3, -0.3), (6, 15, 4, 0.05), (9, 7, 3, 0.35)):
        prism(img, x0, 15, height, width, OBSIDIAN, lean)
    img = outline(img, INK)
    p = img.load()
    for (x, y) in ((6, 6), (5, 11), (9, 12)):
        if p[x, y][3] and p[x, y] != INK:
            p[x, y] = FIRE[1]
    p[6, 9] = FIRE[2]
    return img


def cinder_pile():
    s = [
        ".....cdc......",
        "...bccddcb....",
        "..bccdcdccbb..",
        ".abbcccbccbba.",
        "aabbbbbbbbbbaa",
    ]
    img = sprite(s, {"a": ASHR[1], "b": ASHR[2], "c": ASHR[3], "d": ASHR[4]})
    p = img.load()
    for (x, y, c) in ((6, 1, FIRE[3]), (8, 3, FIRE[2]), (4, 3, INK), (10, 2, INK), (3, 4, FIRE[1])):
        p[x, y] = c
    return img


# ----------------------------------------------------------- great hearth ---

GW, GH = 96, 80
GCX = 47.5


def arch_r(x, y, cx, cy, rx, ry):
    """Normalised 'radius' for a round-topped arch: <=1 inside."""
    if y >= cy:
        return abs(x + 0.5 - cx) / rx
    return math.hypot((x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry)


def in_outer(x, y):
    return arch_r(x, y, GCX, 38, 44, 32) <= 1 and y < 72


def in_inner(x, y):
    return arch_r(x, y, GCX, 32, 31.5, 22) <= 1 and y < 72


def in_heart(x, y):
    return ((x + 0.5 - GCX) / 17) ** 2 + ((y + 0.5 - 45) / 20) ** 2 <= 1 or (40 <= x <= 55 and 60 <= y < 72)


def in_cradle(x, y):
    """Hood-shaped niche: 16 wide x 24 tall (x 40..55, y 36..59)."""
    if not (36 <= y <= 59 and 40 <= x <= 55):
        return False
    if y < 44:  # rounded hood top, tip leaning back to the left
        return ((x + 0.5 - 48.5) / 7.2) ** 2 + ((y + 0.5 - 44) / 8.2) ** 2 <= 1 or (x, y) in ((41, 38), (42, 38), (41, 39), (40, 37))
    half = 6.6 + (y - 44) / 15 * 1.4
    return abs(x + 0.5 - 48) <= half


def heart_cracks():
    """Veins radiating from the Cradle across the heart-stone."""
    r = rng(23)
    pts = set()
    for k in range(9):
        a = math.tau * k / 9 + r.uniform(-0.15, 0.15)
        x, y = GCX + math.cos(a) * 9, 48 + math.sin(a) * 11
        for step in range(14):
            a += r.uniform(-0.5, 0.5)
            x += math.cos(a)
            y += math.sin(a) * 1.15
            xi, yi = int(x), int(y)
            if in_heart(xi, yi) and not in_cradle(xi, yi):
                pts.add((xi, yi))
                if step % 5 == 4:  # small branch
                    pts.add((xi + 1, yi + 1))
    return pts


CRACKS = heart_cracks()


def flame_level(x, k):
    ph = k * math.tau / 4
    base = 0.55 + 0.22 * math.sin(x * 0.31 + ph) + 0.12 * math.sin(x * 0.73 - 2 * ph + 1.0) \
        + 0.1 * abs(math.sin(x * 0.17 + 3 * ph))
    return max(0.15, base)


def hearth_frames():
    frames = []
    for state in range(6):
        cold, pulse, roar = state == 0, state == 1, state >= 2
        k = state - 2
        img = new(GW, GH)
        p = img.load()
        for y in range(GH):
            for x in range(GW):
                # steps
                if y >= 76:
                    p[x, y] = STATUE[2] if y == 76 else (STATUE[1] if y < 79 else STATUE[0])
                    continue
                if y >= 72 and 6 <= x <= 89:
                    p[x, y] = STATUE[3] if y == 72 else (STATUE[2] if y < 75 else STATUE[1])
                    if roar and y == 72:
                        p[x, y] = FIRE[2] if 18 <= x <= 77 else STATUE[4]
                    continue
                if not in_outer(x, y):
                    continue
                if in_inner(x, y):
                    # firebox interior
                    if roar:
                        lvl = flame_level(x, k)
                        v = (72 - y) / (52 * lvl)
                        if v < 1:
                            idx = 5 - int(v * 5)
                            c = FIRE[max(1, min(5, idx))]
                            if dith(x, y, (v * 5) % 1) and idx - 1 >= 1:
                                c = FIRE[idx - 1]
                        else:
                            c = FIRE[0] if dith(x, y, 0.55) else hexc("#2a0c08")
                    elif pulse:
                        c = hexc("#0c0607")
                        if y > 64:
                            c = FIRE[0] if dith(x, y, (y - 64) / 10) else hexc("#140807")
                    else:
                        c = hexc("#0a0607")
                        if y > 68 and dith(x * 3, y, 0.15):
                            c = hexc("#1f1416")  # cold ash bed
                    p[x, y] = c
                    continue
                # carved frame: lighter near the opening, darker outward
                ri = arch_r(x, y, GCX, 32, 31.5, 22)
                ro = arch_r(x, y, GCX, 38, 44, 32)
                t = 0.75 - (ri - 1) * 2.2 - 0.15 * (y / GH)
                c = ramp_at(STATUE[1:5], t, x, y)
                if ro > 0.95:
                    c = STATUE[1]
                if 1.0 < ri < 1.06:
                    c = BRONZE[3] if y < 40 or x < GCX else BRONZE[2]  # bronze trim on the opening
                    if roar:
                        c = BRONZE[5]
                    elif pulse:
                        c = BRONZE[3]
                p[x, y] = c
        # voussoir joints + runes on the arch band
        for a in range(8, 180, 12):
            t = math.radians(a)
            for rr in range(0, 9):
                x = int(GCX + math.cos(t) * (32.5 + rr * 1.3))
                y = int(32 - math.sin(t) * (22.5 + rr * 1.0))
                if 0 <= x < GW and 0 <= y < GH and in_outer(x, y) and not in_inner(x, y) and \
                        arch_r(x, y, GCX, 32, 31.5, 22) > 1.08:
                    p[x, y] = STATUE[1]
        for (x, y) in ((10, 50), (11, 51), (10, 55), (12, 60), (84, 50), (85, 52), (84, 57), (83, 62)):
            p[x, y] = FIRE[1] if roar else (FIRE[0] if pulse else STATUE[1])
        # keystone with the Keeper eye
        for y in range(5, 14):
            for x in range(42, 54):
                if in_outer(x, y):
                    p[x, y] = STATUE[4] if y == 5 or x == 42 else (STATUE[2] if x == 53 or y == 13 else STATUE[3])
        eye = [(45, 9), (46, 8), (47, 8), (48, 8), (49, 8), (50, 9), (49, 10), (48, 10), (47, 10), (46, 10)]
        for (x, y) in eye:
            p[x, y] = STATUE[1]
        for (x, y) in ((47, 9), (48, 9)):
            p[x, y] = GLOW if roar else (FIRE[1] if pulse else INK)
        # the heart-stone
        for y in range(GH):
            for x in range(GW):
                if not in_heart(x, y):
                    continue
                if 60 <= y and not (((x + 0.5 - GCX) / 17) ** 2 + ((y + 0.5 - 45) / 20) ** 2 <= 1):
                    c = STATUE[2] if x < 48 else STATUE[1]  # pedestal
                    p[x, y] = c
                    continue
                nx, ny = (x + 0.5 - GCX) / 17, (y + 0.5 - 45) / 20
                lit = -(nx * 0.55 + ny * 0.8)
                t = 0.45 + 0.4 * lit - 0.25 * (nx * nx + ny * ny)
                p[x, y] = ramp_at(BASALT[1:6], t, x, y)
        for (x, y) in CRACKS:
            p[x, y] = FIRE[4] if roar and (x + y + k) % 3 else (FIRE[3] if roar else (FIRE[1] if pulse else FIRE[0]))
        # rim of the heart catches the fire
        if roar:
            for y in range(GH):
                for x in range(GW):
                    if in_heart(x, y) and y < 62 and not in_heart(x + 1, y) or (in_heart(x, y) and y < 62 and not in_heart(x - 1, y)):
                        p[x, y] = FIRE[3]
                    elif in_heart(x, y) and not in_heart(x, y - 1) and y < 50:
                        p[x, y] = FIRE[2]
        # the Cradle
        for y in range(GH):
            for x in range(GW):
                if not in_cradle(x, y):
                    continue
                if roar:
                    d = math.hypot(x + 0.5 - 48, (y + 0.5 - 50) * 0.8) / 11
                    c = hexc("#ffffff") if d < 0.35 else (GLOW if d < 0.6 else (FIRE[5] if d < 0.85 else FIRE[4]))
                    if dith(x + k, y, 0.15) and d > 0.5:
                        c = FIRE[4]
                elif pulse:
                    c = FIRE[0] if dith(x, y, max(0.0, 0.5 - abs(y - 52) / 16)) else VOID
                else:
                    c = VOID
                p[x, y] = c
        for y in range(36, 61):  # niche lip: lit edge on the left, shadow on the right
            for x in range(39, 57):
                if in_cradle(x, y) or not in_heart(x, y):
                    continue
                if in_cradle(x + 1, y):
                    p[x, y] = BASALT[4] if not roar else FIRE[4]
                elif in_cradle(x - 1, y) or in_cradle(x, y - 1):
                    p[x, y] = BASALT[1] if not roar else FIRE[2]
        for x in range(40, 56):  # niche floor
            if in_heart(x, 60):
                p[x, 60] = BASALT[4] if not roar else FIRE[3]
        if roar:  # loose tongues and sparks above the flames
            r = rng(300 + k)
            for _ in range(10):
                x, y = r.randint(20, 75), r.randint(12, 40)
                if in_inner(x, y) and not in_heart(x, y):
                    p[x, y] = FIRE[3] if r.random() < 0.6 else FIRE[4]
                    if in_inner(x, y + 1) and not in_heart(x, y + 1):
                        p[x, y + 1] = FIRE[2]
        frames.append(outline(img, INK))
    return frames


# ---------------------------------------------------------------- preview ---

TEST = [
    "##################################",
    "###wwwwwwww......########wwwwwwww#",
    "##wwwwww..........................#",
    "#wwww.............................#",
    "#ww...............................#",
    "#w................................#",
    "#.....====...................====.#",
    "#.................................#",
    "#.................................#",
    "##................................#",
    "###.............................###",
    "#####........................######",
    "##################################",
    "##################################",
    "##################################",
    "##################################",
]


def build():
    ground, wall = build_tiles()
    layers = build_backdrop()
    hearth = hearth_frames()
    save(sheet(hearth), "sprites/hearth_great.png")
    props = {
        "keeper_giant": keeper_giant(),
        "brazier_cold": brazier_cold(),
        "obsidian": obsidian(),
        "cinder_pile": cinder_pile(),
    }
    for k, img in props.items():
        save(img, f"deco/{k}.png")

    save_preview(ground, "hearth_ground_atlas.png", 3)
    deco_rows_preview(ground, "hearth_deco_rows.png")
    order = (("far", 0.25), ("mid", 0.5))
    save_preview(compose_backdrop(layers, 40, order), "hearth_bg.png", 2)
    rows = pad_rows(TEST)
    width = len(rows[0]) * T
    for name, frame in (("hearth_test.png", hearth[0]), ("hearth_test_roar.png", hearth[3])):
        bd = scene_backdrop(layers, width, order)
        placed = [
            (props["keeper_giant"], 6, 10, False), (props["keeper_giant"], 27, 10, False),
            (props["brazier_cold"], 10, 10, False), (props["brazier_cold"], 23, 10, False),
            (props["obsidian"], 4, 9, False), (props["cinder_pile"], 13, 10, False),
            (props["cinder_pile"], 21, 10, False),
        ]
        scene = compose_scene(ground, wall, bd, rows, placed, wall_mod=WALL_TINT)
        scene.alpha_composite(frame, (17 * T - GW // 2, 11 * T - GH))
        save_preview(scene, name, 2)
        if name == "hearth_test_roar.png":
            lit = ingame(scene, [(17 * T, 11 * T - 30, 150, (1.0, 0.62, 0.32), 1.0)], ambient=(0.5, 0.36, 0.36))
        else:
            lit = ingame(scene, [(15 * T, 10 * T + 8, 96, (1.0, 0.78, 0.5), 0.7)], ambient=(0.5, 0.36, 0.36))
        save_preview(lit, name.replace(".png", "_ingame.png"), 2)
    save_preview(sheet(hearth), "hearth_great_frames.png", 3)
    big = new(GW + 4, GH + 4, (40, 44, 60, 255))
    big.alpha_composite(hearth[0], (2, 2))
    save_preview(big, "hearth_great_cold.png", 5)
    props_sheet(list(props.values()), "hearth_props.png")


if __name__ == "__main__":
    build()
