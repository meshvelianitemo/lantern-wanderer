"""Chapter III - the Drowned Halls: flooded ruins of the Keepers.

Run `python drowned.py` to (re)generate:

  tiles/drowned_ground.png  256x288  forest atlas layout; carved wet Keeper masonry,
                                     dark algae tops, algae strands / broken chain ends
                                     hanging (row 16 cols 4-7), verdigris copper
                                     grating as the one-way platform (row 17)
  tiles/drowned_wall.png    256x288  dark teal-grey masonry (rows 0-15 used)
  bg/drowned_base.png       480x270  teal-black gradient, drifting motes (factor 0)
  bg/drowned_far.png        640x270  colossal arcade with faint drowned-window lights
  bg/drowned_mid.png        640x270  broken columns + hanging chains
  bg/drowned_near.png       640x270  ragged ceiling lip with algae + chains (top only)
  sprites/water.png          64x16   4 frames 16x16: animated surface (ripple rows 0-3)
  sprites/water_body.png     16x16   translucent body, identical to surface rows 4-15
  sprites/hook.png           32x40   2 frames 16x40: 0 empty crook, 1 hero lantern hung
  sprites/eye_gate.png       32x48   2 frames 16x48: 0 eye dark, 1 eye drinking light
  deco/keeper_statue, broken_column, urn, drowned_lamp, lily (bottom-centre)
  deco/chain_hang (top-anchored, flush top row)

Backdrop scene: scenes/backdrops/drowned.tscn. Previews: _preview/drowned_*.png
"""
import math

from bg import periodic_noise
from envkit import (Mask, compose_scene, deco_rows_preview, flush_top, ingame, pad_rows,
                    props_sheet, rim_light, scene_backdrop, shade_mask, vgrad, H, W)
from pix import BONE, FIRE, GLOW, INK, CLEAR, dith, hexc, new, outline, paste, ramp_at, rng, save, save_preview, sheet, sprite
from tiles import PERIOD, T, build_terrain

MASONRY = [hexc(c) for c in ("#0f1618", "#1a2427", "#26363a", "#354a4c", "#4a6362", "#678480")]
WALL = [hexc(c) for c in ("#070b0c", "#0c1314", "#121b1d", "#182427", "#1f2e31", "#283a3d")]
ALGAE = [hexc(c) for c in ("#07110e", "#0c1d18", "#122a21", "#1a3a2b", "#255037", "#3a6c48")]
VERDIGRIS = [hexc(c) for c in ("#0d1c1b", "#173431", "#235048", "#33705f", "#4f9479", "#86c2a0")]
IRON = [hexc(c) for c in ("#151a1c", "#283033", "#3e4a4c", "#5f6e6c")]
METAL = (hexc("#2a2330"), hexc("#4f4658"), hexc("#7b7286"))  # the hero's lantern (hero.py)
DROP = hexc("#9fd6cc")
PALE = hexc("#9cc9b8")
FACE = hexc("#0a1012")

WATER_BODY = hexc("#0b2a2c", 185)
WATER_FLECK = hexc("#123735", 185)

WALL_TINT = (0.48, 0.56, 0.58)


# ------------------------------------------------------------------ tiles ---

def masonry(seed, ramp, mortar, light_bias=0, course=8, min_w=9, max_w=20, glyphs=0.04):
    """Seamless carved block courses (period 64). Mortar = bottom + right edge of each block."""
    r = rng(seed)
    img = new(PERIOD, PERIOD)
    p = img.load()
    mort = [[False] * PERIOD for _ in range(PERIOD)]
    top = len(ramp) - 1
    for ci in range(PERIOD // course):
        y0 = ci * course
        widths, total = [], 0
        while total < PERIOD:
            wd = r.randint(min_w, max_w)
            if PERIOD - (total + wd) < min_w:
                wd = PERIOD - total
            widths.append(wd)
            total += wd
        x = r.randint(0, PERIOD - 1)
        for wd in widths:
            shade = 2 + light_bias + (1 if r.random() < 0.4 else 0)
            worn = r.random() < 0.3
            for yy in range(course):
                for xx in range(wd):
                    X, Y = (x + xx) % PERIOD, y0 + yy
                    if yy == course - 1 or xx == wd - 1:
                        mort[Y][X] = True
                        p[X, Y] = mortar[1] if (X * 7 + Y * 3) % 11 == 0 else mortar[0]
                        continue
                    c = shade
                    if yy == 0 or (xx == 0 and yy < course - 2):
                        c = shade + 1  # top/left bevel catches the light
                    elif yy == course - 2 or xx == wd - 2:
                        c = shade - 1
                    elif worn and (X * 5 + Y * 11) % 13 == 0:
                        c = shade - 1  # pitting
                    p[X, Y] = ramp[max(0, min(top, c))]
            # carved Keeper eye on some long blocks
            if wd >= 14 and r.random() < glyphs:
                gx, gy = x + wd // 2 - 2, y0 + 2
                for (ex, ey) in ((1, 0), (2, 0), (3, 0), (0, 1), (4, 1), (1, 2), (2, 2), (3, 2)):
                    p[(gx + ex) % PERIOD, gy + ey] = ramp[max(0, shade - 1)]
                p[(gx + 2) % PERIOD, gy + 1] = ramp[0]
            x += wd
    return img, mort


def wet_streaks(tex, mort):
    p = tex.load()
    r = rng(91)
    for _ in range(22):
        x, y = r.randrange(PERIOD), r.randrange(PERIOD)
        for k in range(r.randint(3, 10)):
            yy = (y + k) % PERIOD
            if mort[yy][x] or not dith(x, yy, 0.6):
                continue
            c = p[x, yy]
            i = MASONRY.index(c) if c in MASONRY else 2
            p[x, yy] = MASONRY[max(1, i - 1)]
    for y in range(PERIOD):  # algae creeping along the joints
        for x in range(PERIOD):
            if mort[y][x] and r.random() < 0.07:
                p[x, y] = ALGAE[2] if r.random() < 0.7 else ALGAE[3]


def algae_profile(seed):
    r = rng(seed)
    top, th = [], []
    for x in range(PERIOD):
        top.append(1 if r.random() < 0.25 else 0)
        t = 2 if r.random() < 0.5 else 3
        if r.random() < 0.14:
            t += r.choice((2, 3, 5))  # wet algae sliding down the face
        th.append(t)
    return top, th


def algae_fringe(r, ph):
    f = new(T, T)
    p = f.load()
    x = 0
    while x < T:
        h = r.choice((0, 0, 1, 1, 1, 2, 2, 3))
        for y in range(h):
            p[x, T - 1 - y] = ALGAE[3] if y < h - 1 else ALGAE[4]
        if h >= 2 and r.random() < 0.18:
            p[x, T - 1 - h] = DROP
        x += r.choice((1, 1, 2))
    return f


def chain_end(p, x, links, broken=True):
    y = 0
    for li in range(links):
        last = li == links - 1
        if li % 2 == 0:  # face-on ring
            for (dx, dy, c) in ((1, 0, IRON[3]), (0, 1, IRON[2]), (2, 1, IRON[1]), (0, 2, IRON[2]),
                                (2, 2, IRON[1]), (1, 3, IRON[1])):
                if last and broken and dx == 2 and dy >= 1:
                    continue  # snapped open
                if y + dy < T:
                    p[x + dx, y + dy] = c
            y += 3
        else:  # edge-on link
            for dy in range(3):
                if y + dy < T:
                    p[x + 1, y + dy] = IRON[2] if dy == 0 else IRON[1]
            y += 2


def algae_hang(r, ph):
    f = new(T, T)
    p = f.load()
    used = set()
    if r.random() < 0.55:
        x = r.randint(1, 12)
        chain_end(p, x, r.randint(2, 4))
        used.update(range(x - 1, x + 4))
    for _ in range(r.randint(1, 3)):
        x = r.randint(1, 14)
        if x in used:
            continue
        used.update((x - 1, x, x + 1))
        ln = r.randint(4, 13)
        for y in range(ln):
            xx = x + (1 if (y // 3) % 2 and y > 2 else 0)
            p[min(T - 1, xx), y] = ALGAE[2] if y < ln - 2 else ALGAE[4]
        if ln + 2 < T and r.random() < 0.5:
            p[x, ln + 1] = DROP
    return f


def grating(i):
    """Verdigris Keeper grating: rails with see-through lattice."""
    f = new(T, T)
    p = f.load()
    for x in range(T):
        p[x, 0] = VERDIGRIS[4] if (x + i * 3) % 7 else VERDIGRIS[5]
        p[x, 1] = VERDIGRIS[3]
        p[x, 4] = VERDIGRIS[2]
        p[x, 5] = VERDIGRIS[0]
        for y in (2, 3):
            if (x + y) % 4 in (0, 1):
                p[x, y] = VERDIGRIS[2] if y == 2 else VERDIGRIS[1]
    for x in range(T):
        if (x + i * 5) % 8 == 3:
            p[x, 1] = VERDIGRIS[5]  # rivets
    if i in (0, 3):
        e = 0 if i == 0 else T - 1
        s = 1 if i == 0 else -1
        for y in range(6):
            p[e, y] = VERDIGRIS[0]
            p[e + s, y] = VERDIGRIS[2] if y < 5 else VERDIGRIS[0]
        p[e, 0] = CLEAR
        # diagonal strut down to the wall
        for k in range(5):
            p[e + s * (2 + k), 6 + k] = VERDIGRIS[2]
            p[e + s * (2 + k), 7 + k] = VERDIGRIS[0]
        for y in range(6, 11):
            p[e + s, y] = VERDIGRIS[1]
    return f


def build_tiles():
    ground = build_terrain("drowned_ground", MASONRY, (MASONRY[0], MASONRY[1]), seed=41,
                           moss=ALGAE, profile=algae_profile(141), tex_post=wet_streaks,
                           fringe=algae_fringe, hang=algae_hang, texture=masonry, platform=grating)
    wall = build_terrain("drowned_wall", WALL, (WALL[0], WALL[0]), seed=42, grass=False,
                         texture=lambda s, rp, m, light_bias=0: masonry(s, rp, m, light_bias, course=8,
                                                                        min_w=12, max_w=24, glyphs=0.0))
    return ground, wall


# ------------------------------------------------------------------ water ---

def water_frames():
    body = new(T, T)
    bp = body.load()
    for y in range(T):
        for x in range(T):
            bp[x, y] = WATER_FLECK if (x * 5 + y * 3) % 17 == 0 else WATER_BODY
    frames = []
    for i in range(4):
        f = body.copy()
        p = f.load()
        ph = i * math.pi / 2
        for x in range(T):
            s1 = math.sin(math.tau * x / T + ph) * 0.7 + math.sin(math.tau * 2 * x / T - ph) * 0.3
            s2 = math.sin(math.tau * 2 * x / T + ph * 2 + 1.3)
            p[x, 0] = hexc("#bfe8dc", 230) if s1 > 0.55 else CLEAR
            p[x, 1] = hexc("#7fbcb0", 220) if s1 > 0.05 else hexc("#1d4a48", 205)
            p[x, 2] = hexc("#2f6a64", 200) if s2 > 0.55 else hexc("#164040", 195)
            p[x, 3] = hexc("#225452", 192) if (s2 < -0.7 and dith(x, 3, 0.5)) else hexc("#103434", 190)
        frames.append(f)
    return frames, body


# --------------------------------------------------------------- backdrop ---

BASE_RAMP = [hexc(c) for c in ("#030707", "#051010", "#081617", "#0b1d1f", "#0f2628")]


def drowned_base():
    img = new(W, H)
    vgrad(img, BASE_RAMP, [(0, 0.0), (80, 0.35), (170, 0.8), (215, 1.0), (240, 0.55), (270, 0.25)])
    p = img.load()
    for (cx, cy, rad) in ((150, 150, 80), (390, 130, 70)):
        for y in range(cy - rad, cy + rad):
            for x in range(cx - rad, cx + rad):
                if 0 <= x < W and 0 <= y < H:
                    d = math.hypot(x - cx, (y - cy) * 1.4) / rad
                    if d < 1 and dith(x, y, (1 - d) * 0.5):
                        p[x, y] = hexc("#10292a")
    r = rng(71)
    for _ in range(90):  # drifting motes
        x, y = r.randrange(W), r.randrange(H)
        p[x, y] = hexc("#4e7a70") if r.random() < 0.25 else hexc("#22403c")
    return img


def arcade(seed, w=640):
    img = new(w, H)
    p = img.load()
    r = rng(seed)
    body, rim, joint = hexc("#0c181a"), hexc("#152628"), hexc("#081214")
    n, ys, floor_y, pw = 4, 132, 226, 26
    gap = w / n
    half = gap / 2 - pw / 2
    m = Mask(w, H)
    for i in range(n):
        for off in (0, w, -w):
            cx = i * gap + off
            m.rect(cx - pw / 2, 0, cx + pw / 2, H - 1)
            m.rect(cx - pw / 2 - 4, ys - 7, cx + pw / 2 + 4, ys)          # capital
            m.rect(cx - pw / 2 - 3, floor_y - 12, cx + pw / 2 + 3, H - 1)  # plinth
    crowns = {}
    for x in range(w):
        k = round((x - gap / 2) / gap)
        acx = k * gap + gap / 2
        dx = x - acx
        if abs(dx) <= half:
            crown = ys - math.sqrt(max(0.0, half * half - dx * dx)) * 0.95
            crowns[x] = crown
            m.rect(x, 0, x, int(crown))
    f = periodic_noise(seed + 3, w, ((3, 1.0), (7, 0.6), (17, 0.3)))
    for x in range(w):
        m.rect(x, int(floor_y + 4 * f(x)), x, H - 1)
    for y in range(H):
        for x in range(w):
            if m.m[y][x]:
                p[x, y] = body
    rim_light(img, rim)
    # voussoir joints around each arch
    for i in range(n):
        acx = i * gap + gap / 2
        for a in range(0, 181, 13):
            t = math.radians(a)
            for rr in range(int(half) + 1, int(half) + 8):
                x = int(acx + math.cos(t) * rr)
                y = int(ys - math.sin(t) * rr * 0.95)
                if 0 <= y < H and p[x % w, y] == body:
                    p[x % w, y] = joint
        for x in range(int(acx - 3), int(acx + 4)):  # keystone
            for y in range(int(ys - half * 0.95) - 9, int(ys - half * 0.95)):
                if 0 <= y < H:
                    p[x % w, y] = rim if x == int(acx - 3) or y == int(ys - half * 0.95) - 9 else body
    # cornice line at the spring
    for x in range(w):
        if p[x, ys - 7] == body:
            p[x, ys - 7] = rim
    # drowned windows: small arched lights high in the wall and low on the pillars
    spots = [(i * gap / 2 + gap / 4 + r.uniform(-6, 6), 30 + r.randint(0, 10), 2, 13) for i in range(n * 2)]
    spots += [(i * gap + r.uniform(-3, 3), 150 + r.randint(0, 25), 2, 11) for i in range(n) if r.random() < 0.75]
    for (wx, wy0, ww, wh) in spots:
        lit = r.random() < 0.7
        wy1 = wy0 + wh
        if lit:  # soft dithered halo on the stone first
            for y in range(wy0 - 5, wy1 + 5):
                for x in range(int(wx - 8), int(wx + 9)):
                    xx = x % w
                    if 0 <= y < H and p[xx, y] == body:
                        d = math.hypot((x - wx) / 8, (y - (wy0 + wy1) / 2) / (wh / 2 + 5))
                        if d < 1 and dith(x, y, (1 - d) * 0.4):
                            p[xx, y] = rim
        for y in range(wy0, wy1):
            for x in range(int(round(wx - ww)), int(round(wx + ww)) + 1):
                rr = x - wx
                if y - wy0 < ww and math.hypot(rr, ww - (y - wy0)) > ww + 0.4:
                    continue
                if not m.get(x % w, y):
                    continue
                if not lit:
                    c = hexc("#040a0b")
                elif abs(rr) < 0.6:
                    c = hexc("#0e1d1e") if y > wy0 + 3 else hexc("#3a625a")  # mullion
                else:
                    c = hexc("#4f8075") if y < wy0 + wh * 0.6 else hexc("#335a52")
                p[x % w, y] = c
        sill = wy1
        for x in range(int(round(wx - ww)) - 1, int(round(wx + ww)) + 2):
            if 0 <= sill < H and m.get(x % w, sill):
                p[x % w, sill] = rim
    return img


def ruins_mid(seed, w=640):
    img = new(w, H)
    p = img.load()
    r = rng(seed)
    body, rim, flute = hexc("#071012"), hexc("#0f1d1f"), hexc("#0b1618")
    m = Mask(w, H)
    f = periodic_noise(seed + 1, w, ((3, 1.0), (7, 0.5), (13, 0.3)))
    for x in range(w):
        m.rect(x, int(250 + 5 * f(x)), x, H - 1)
    cols = []
    for i in range(5):
        cx = (i + r.uniform(0.15, 0.85)) * w / 5
        cw = r.uniform(16, 26)
        top = r.uniform(70, 185)
        slope = r.choice((-0.7, -0.4, 0.4, 0.7))
        cols.append((cx, cw))
        for x in range(int(cx - cw / 2), int(cx + cw / 2) + 1):
            t = top + (x - cx) * slope + r.choice((0, 0, 1, 2, 3))
            m.rect(x % w, int(t), x % w, H - 1)
        for x in range(int(cx - cw / 2 - 4), int(cx + cw / 2 + 5)):
            m.rect(x % w, 238, x % w, H - 1)
    # a fallen drum lying on the rubble
    fx = r.uniform(0, w)
    m.ellipse(fx, 244, 22, 7)
    for y in range(H):
        for x in range(w):
            if m.m[y][x]:
                p[x, y] = body
    rim_light(img, rim)
    for (cx, cw) in cols:  # fluting
        for x in range(int(cx - cw / 2) + 3, int(cx + cw / 2) - 1, 5):
            for y in range(H):
                if p[x % w, y] == body and y < 236:
                    p[x % w, y] = flute
    # hanging chains, some with a cold cage lantern
    for i in range(6):
        x = int(r.uniform(0, w))
        ln = int(r.uniform(40, 150))
        for y in range(ln):
            k = y % 6
            if k in (1, 2):
                p[x % w, y] = rim
                p[(x + 2) % w, y] = body
            elif k in (0, 3):
                p[(x + 1) % w, y] = rim
            else:
                p[(x + 1) % w, y] = body
        if r.random() < 0.5:
            for y in range(ln, ln + 8):
                for xx in range(x - 2, x + 5):
                    edge = xx in (x - 2, x + 4) or y in (ln, ln + 7)
                    if edge or xx == x + 1:
                        p[xx % w, y] = rim if edge else body
    return img


def ruins_near(seed, w=640):
    img = new(w, H)
    p = img.load()
    r = rng(seed)
    body, tip = hexc("#040909"), hexc("#0c2019")
    f = periodic_noise(seed + 1, w, ((2, 1.0), (5, 0.6), (11, 0.3)))
    for x in range(w):
        d = int(10 + 7 * f(x))
        for y in range(d):
            p[x, y] = body
    for _ in range(70):
        x0 = r.uniform(0, w)
        ln = int(r.uniform(6, 46))
        start = int(10 + 7 * f(int(x0) % w))
        for y in range(start, start + ln):
            x = int(x0 + math.sin(y * 0.25 + x0) * 1.2)
            p[x % w, y] = tip if y > start + ln - 3 and dith(x, y, 0.6) else body
    for i in range(3):  # near chains
        x = int(r.uniform(0, w))
        for y in range(0, int(r.uniform(50, 110))):
            k = y % 8
            if k in (1, 2, 3):
                p[x % w, y] = body
                p[(x + 3) % w, y] = body
            elif k in (0, 4):
                for dx in (1, 2):
                    p[(x + dx) % w, y] = body
            else:
                p[(x + 1) % w, y] = body
                p[(x + 2) % w, y] = body
    return img


def build_backdrop():
    layers = {
        "base": drowned_base(),
        "far": arcade(81),
        "mid": ruins_mid(82),
        "near": ruins_near(83),
    }
    for name, img in layers.items():
        save(img, f"bg/drowned_{name}.png")
    return layers


# ------------------------------------------------------------------ props ---

def moss_tops(img, chance=0.7, drip=0.35, seed=5):
    """Algae on every upward-facing surface of a stone prop."""
    p = img.load()
    r = rng(seed)
    w, h = img.size
    src = img.copy().load()
    for x in range(w):
        for y in range(h):
            if src[x, y][3] and src[x, y] != INK and (y == 0 or src[x, y - 1][3] == 0 or src[x, y - 1] == INK):
                if r.random() < chance:
                    p[x, y] = ALGAE[4] if r.random() < 0.6 else ALGAE[3]
                    if y + 1 < h and src[x, y + 1][3] and src[x, y + 1] != INK and r.random() < drip:
                        p[x, y + 1] = ALGAE[2]
    return img


STATUE = [
    "..................1...",
    "................4444..",
    "................4ww43.",
    "................4wg43.",
    "................4wh43.",
    "................4ww43.",
    ".................333..",
    "..................3...",
    ".................45...",
    ".................44...",
    "...22...3dd......43...",
    "..233.33dd5dd....43...",
    "..23.223dd555dd..43...",
    ".22..2333dd555dd343...",
    "....22333ddddddd343...",
    "....22333ddvvvvv343...",
    "....122333dvvvvvv43...",
    "....122333vvvvvvv43...",
    "....12233dvvvvvvv43...",
    ".....1223333vvvvd343..",
    "......12223333322.43..",
    "......22333ddd3...43..",
    "......122333ddd3.443..",
    ".....1122333dddd3433..",
    ".....11222333ddd333...",
    "....111222333dddd3....",
    "....111222333dddd3....",
    "....1112222333ddd3....",
    "...11112222333ddd33...",
    "...11112222333dddd3...",
    "...111122222333ddd3...",
    "..1111122222333dddd3..",
    "..11111222223333ddd3..",
    "..111112222222333333..",
    ".44444444444444444443.",
    ".33333333333333333332.",
    ".22222222222222222221.",
    ".33333333333333333332.",
    ".22222222222222222221.",
    ".11111111111111111111.",
]


def keeper_statue():
    """A small hooded Keeper - same hood as the wanderer - lifting a lantern.
    Lit from its own lantern, upper right, like the hero."""
    key = {"1": MASONRY[1], "2": MASONRY[2], "3": MASONRY[3], "d": MASONRY[4], "4": MASONRY[4],
           "5": MASONRY[5], "v": FACE, "w": hexc("#1b3330"), "g": PALE, "h": hexc("#5f8f84")}
    img = outline(sprite(STATUE, key), INK)
    return moss_tops(img, chance=0.55, seed=11)


def broken_column():
    w, h = 16, 30
    m = Mask(w, h)
    tops = [9, 8, 7, 9, 6, 5, 7, 10, 11, 9]
    for i, t in enumerate(tops):
        m.rect(3 + i, t, 3 + i, 25)
    m.rect(2, 5 + 4, 2, 9)
    m.rect(1, 26, 14, 27)
    m.rect(0, 28, 15, 29)
    img = shade_mask(m, MASONRY[1:6], lo=0.1, hi=0.85)
    p = img.load()
    for x in (5, 8, 11):
        for y in range(11, 26):
            if p[x, y][3]:
                p[x, y] = MASONRY[1] if y % 4 else MASONRY[2]
    p[7, 15] = MASONRY[0]
    p[8, 16] = MASONRY[0]
    img = outline(img, INK)
    return moss_tops(img, seed=12)


def chain_hang():
    """Hanging chain, 5x40; row 0 is a link, so it sits flush against the ceiling."""
    img = new(5, 41)
    p = img.load()
    for y in range(41):
        li, k = y // 4, y % 4
        if li % 2 == 0:
            if k in (0, 3):
                p[2, y] = IRON[3] if k == 0 else IRON[1]
            else:
                p[1, y] = IRON[3]
                p[3, y] = IRON[1]
        else:
            p[2, y] = IRON[2] if k < 2 else IRON[1]
    img = outline(img, INK).crop((0, 0, 5, 40))
    q = img.load()
    for x in range(5):  # no outline cap along the ceiling
        if q[x, 0] == INK:
            q[x, 0] = CLEAR
    q[2, 0] = IRON[2]
    return img


def lily():
    s = [
        "....aba.....",
        "...abcba....",
        "..bbcdcbb...",
        ".eeffbbbffe.",
        "effgfffgffee",
        ".eeeffffeee.",
    ]
    key = {"a": hexc("#a8dcc8"), "b": hexc("#dff5ea"), "c": hexc("#ffffff"), "d": hexc("#f6f0b0"),
           "e": ALGAE[2], "f": ALGAE[3], "g": ALGAE[5]}
    img = sprite(s, key)
    p = img.load()
    p[6, 4] = CLEAR  # the notch in the pad
    p[6, 5] = CLEAR
    return img


def urn():
    w, h = 10, 12
    m = Mask(w, h)
    m.ellipse(5, 7.5, 4.2, 4.2)
    m.rect(3, 1, 6, 3)
    m.rect(2, 0, 7, 0)
    img = shade_mask(m, [hexc("#2c3a3a"), hexc("#3e5250"), hexc("#566e69"), hexc("#7a908a"), hexc("#a6b9b0")],
                     lo=0.1, hi=0.85)
    p = img.load()
    for x in range(1, 9):  # painted Keeper band
        if p[x, 7][3]:
            p[x, 7] = VERDIGRIS[2] if x % 3 else hexc("#8a6a3a")
    p[6, 9] = hexc("#1f2a2a")
    p[7, 10] = hexc("#1f2a2a")
    img = outline(img, INK)
    q = img.load()
    for x in (0, 9):  # tiny handles
        q[x, 3] = INK
        q[x, 4] = hexc("#3e5250")
    return moss_tops(img, chance=0.3, seed=13)


def drowned_lamp():
    s = [
        "..aaaa..",
        ".abccba.",
        "abddddba",
        "adeffeda",
        "adeffeda",
        "abddddba",
        ".abccba.",
        "..abba..",
        "...bb...",
        ".aabbaa.",
        "abccccba",
        ".aaaaaa.",
    ]
    key = {"a": INK, "b": VERDIGRIS[1], "c": VERDIGRIS[3], "d": VERDIGRIS[2],
           "e": hexc("#16302c"), "f": hexc("#2a4c45")}
    img = sprite(s, key)
    img.load()[4, 3] = hexc("#5f8f84")  # a cold glint on the glass
    return img


# ---------------------------------------------------------------- mechanic ---

HERO_LANTERN = [
    "..m..",
    ".mmm.",
    "mnnnm",
    "mFGFm",
    "mGHGm",
    "mFGFm",
    "mnnnm",
    ".mmm.",
]


def hook_frames():
    base = new(16, 40)
    p = base.load()
    # stone foot
    foot = [
        "...aaaaaaaa.....",
        "..abccccccba....",
        "..abcddddcba....",
        ".aabbbbbbbbaa...",
        ".aaaaaaaaaaaa...",
    ]
    paste(base, sprite(foot, {"a": INK, "b": MASONRY[2], "c": MASONRY[3], "d": MASONRY[4]}), 1, 35)
    # iron post
    for y in range(5, 36):
        p[7, y] = IRON[3] if y % 7 else IRON[2]
        p[8, y] = IRON[1]
    # crook: arc over the top opening down to the right
    cx, cy, rad = 10.5, 5.0, 3.0
    for a in range(0, 181, 6):
        t = math.radians(a)
        x = int(round(cx - math.cos(t) * rad))
        y = int(round(cy - math.sin(t) * rad))
        p[x, y] = IRON[3] if a < 100 else IRON[2]
        p[x, y + 1] = IRON[1] if p[x, y + 1][3] == 0 else p[x, y + 1]
    for y in range(5, 8):
        p[13, y] = IRON[2]
        p[14, y] = IRON[1]
    p[12, 8] = IRON[2]  # curl at the tip
    p[12, 9] = IRON[1]
    for y in (12, 22):  # binding rings
        p[6, y] = IRON[2]
        p[9, y] = IRON[1]
    empty = outline(base, INK)
    hung = empty.copy()
    lan = sprite(HERO_LANTERN, {"m": METAL[0], "n": METAL[1], "F": FIRE[3], "G": FIRE[4], "H": FIRE[5]})
    paste(hung, lan, 11, 8)
    hp = hung.load()
    hp[13, 8] = METAL[2]  # ring over the crook tip
    return [empty, hung]


def eye_gate_frames():
    w, h = 16, 48
    m = Mask(w, h)
    m.rect(0, 0, 15, 44)
    for x in range(16):  # portcullis teeth
        if x % 4 in (1, 2):
            m.rect(x, 45, x, 47)
    base = shade_mask(m, MASONRY[1:6], lo=0.25, hi=0.7)
    p = base.load()
    for y in range(h):  # block joints
        for x in range(w):
            if not p[x, y][3]:
                continue
            if y in (16, 30) or (x == 8 and 16 < y < 30) or (x == 5 and 30 < y < 44):
                p[x, y] = MASONRY[1]
            if x == 0 or y == 0:
                p[x, y] = MASONRY[4]
            if x == 15:
                p[x, y] = MASONRY[1]
    for y in (20, 21, 37, 38):  # verdigris bands
        for x in range(16):
            p[x, y] = VERDIGRIS[3] if y in (20, 37) else VERDIGRIS[1]
        for x in (2, 13):
            p[x, y] = VERDIGRIS[5] if y in (20, 37) else VERDIGRIS[2]
    for x in range(16):
        for y in range(44, 48):
            if p[x, y][3]:
                p[x, y] = IRON[2] if x % 4 == 1 else IRON[1]
    # carved medallion with an almond eye
    mx, my = 7.5, 8.5
    for y in range(2, 16):
        for x in range(1, 15):
            d = math.hypot(x + 0.5 - mx - 0.5, y + 0.5 - my - 0.5)
            if 5.4 < d < 6.5:
                p[x, y] = MASONRY[1]
            elif 4.6 < d <= 5.4:
                p[x, y] = MASONRY[4] if y < my else MASONRY[3]
    eye_ring = [(5, 8), (6, 7), (7, 7), (8, 7), (9, 7), (10, 8), (9, 10), (8, 10), (7, 10), (6, 10), (5, 9), (10, 9)]
    iris = [(7, 8), (8, 8), (7, 9), (8, 9)]
    rays = [(8, 4), (8, 13), (3, 9), (12, 8)]
    frames = []
    for lit in (False, True):
        img = base.copy()
        q = img.load()
        for (x, y) in eye_ring:
            q[x, y] = hexc("#d9c58f") if lit else MASONRY[0]
        for (x, y) in ((6, 8), (9, 8), (6, 9), (9, 9)):
            q[x, y] = hexc("#7a5f30") if lit else MASONRY[1]
        for (x, y) in iris:
            q[x, y] = (GLOW if (x, y) != (8, 8) else hexc("#ffffff")) if lit else INK
        for (x, y) in rays:
            q[x, y] = FIRE[3] if lit else MASONRY[1]
        if lit:  # runes along the joints drink the light too
            for (x, y) in ((3, 24), (4, 24), (11, 26), (12, 26), (7, 33), (8, 33)):
                q[x, y] = hexc("#b89a5a")
        frames.append(img)
    return frames


# ---------------------------------------------------------------- preview ---

TEST = [
    "##################################",
    "###wwwww.......######.....wwwww###",
    "##wwwww...........................#",
    "#wwwww............................#",
    "#wwww.............................#",
    "#www...........................####",
    "#ww....======..................####",
    "#w...........................######",
    "#............................######",
    "####.....................#########",
    "#####~~~~~~~~~~~~~~~~~~~~#########",
    "#####ooooooo####ooooooooo#########",
    "######oooooo#####oooooooo#########",
    "#######ooooo######ooooooo#########",
    "##################################",
    "##################################",
]


def build():
    ground, wall = build_tiles()
    layers = build_backdrop()
    water, body = water_frames()
    save(sheet(water), "sprites/water.png")
    save(body, "sprites/water_body.png")
    hooks = hook_frames()
    save(sheet(hooks), "sprites/hook.png")
    gates = eye_gate_frames()
    save(sheet(gates), "sprites/eye_gate.png")
    props = {
        "keeper_statue": keeper_statue(),
        "broken_column": broken_column(),
        "chain_hang": chain_hang(),
        "lily": lily(),
        "urn": urn(),
        "drowned_lamp": drowned_lamp(),
    }
    for k, img in props.items():
        save(img, f"deco/{k}.png")

    save_preview(ground, "drowned_ground_atlas.png", 3)
    deco_rows_preview(ground, "drowned_deco_rows.png")
    from envkit import compose_backdrop
    save_preview(compose_backdrop(layers, 40), "drowned_bg.png", 2)
    rows = pad_rows(TEST)
    grid = [r.replace("~", ".").replace("o", ".") for r in rows]
    width = len(rows[0]) * T
    bd = scene_backdrop(layers, width)
    placed = [
        (props["keeper_statue"], 6, 8, False), (props["broken_column"], 21, 8, False),
        (props["urn"], 18, 8, False), (props["chain_hang"], 13, 1, True), (props["chain_hang"], 23, 1, True),
        (props["drowned_lamp"], 28, 3, False), (hooks[1], 10, 8, False), (hooks[0], 15, 8, False),
        (gates[1], 25, 8, False), (gates[0], 2, 8, False),
    ]
    scene = compose_scene(ground, wall, bd, grid, placed, wall_mod=WALL_TINT)
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            if c == "~":
                scene.alpha_composite(water[x % 4], (x * T, y * T))
            elif c == "o":
                scene.alpha_composite(body, (x * T, y * T))
    for x in (8, 14, 19):
        scene.alpha_composite(props["lily"], (x * T + 2, 10 * T - 3))
    save_preview(scene, "drowned_test.png", 2)
    lit = ingame(scene, [(10 * T + 13, 8 * T + 12, 70, (1.0, 0.7, 0.4), 0.8),
                         (12 * T, 9 * T, 96, (1.0, 0.78, 0.5), 0.6)], ambient=(0.4, 0.5, 0.52))
    save_preview(lit, "drowned_test_ingame.png", 2)
    props_sheet(list(props.values()) + water + [body] + hooks + gates, "drowned_props.png", height=52)


if __name__ == "__main__":
    build()
