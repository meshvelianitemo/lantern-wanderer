"""Chapter IV - the Rootdark: the forest's roots reaching down to the Hearth.

Run `python rootdark.py` to (re)generate:

  tiles/rootdark_ground.png  256x288  forest atlas layout; packed violet-brown earth
                                      threaded with roots, glowing hyphae mat on top,
                                      root tendrils hanging (row 16 cols 4-7), a thick
                                      root branch as the one-way platform (row 17)
  tiles/rootdark_wall.png    256x288  very dark violet-brown earth (rows 0-15 used)
  bg/rootdark_base.png       480x270  violet-black gradient with spore glints (factor 0)
  bg/rootdark_far.png        640x270  colossal roots descending like pillars + spores
  bg/rootdark_mid.png        640x270  tangled root arches
  bg/rootdark_near.png       640x270  hanging tendrils (top only)
  sprites/thorn.png           64x16   4 frames 16x16, tiles both ways: 0 intact thorn
                                      knot, 1 glowing cracks, 2 burning apart, 3 ash
  deco/fungus_tall, fungus_cluster, spore_pod, root_knot (bottom-centre)
  deco/root_hang (top-anchored, flush top row)

Backdrop scene: scenes/backdrops/rootdark.tscn. Previews: _preview/rootdark_*.png
"""
import math

from bg import periodic_noise
from envkit import (Mask, compose_backdrop, compose_scene, deco_rows_preview, ingame, pad_rows,
                    pnoise2, props_sheet, rim_light, scene_backdrop, vgrad, H, W)
from pix import AMETHYST, FIRE, INK, CLEAR, dith, hexc, new, outline, ramp_at, rng, save, save_preview, sheet, sprite
from tiles import PERIOD, T, build_terrain

EARTH = [hexc(c) for c in ("#0b060b", "#150c14", "#1f111c", "#2a1624", "#371d2e", "#47253a")]
WALL = [hexc(c) for c in ("#070407", "#0c070c", "#120a11", "#180e17", "#1f121d", "#271724")]
ROOT = [hexc(c) for c in ("#170c10", "#2a161a", "#422224", "#5c3229", "#7a4632", "#9a6040")]
ROOT_MID = [hexc(c) for c in ("#140a0e", "#221216", "#331b1d", "#462523", "#5a3129", "#6e3e30")]
ROOT_DIM = [hexc(c) for c in ("#0a0609", "#130b0e", "#1c1013", "#261518", "#311b1c", "#3d2221")]
HYPHAE = [hexc(c) for c in ("#120a1c", "#2a1846", "#3d2266", "#5a3492", "#7d48b8", "#b67ee0")]
SPORE = hexc("#e9c4f7")
THORN = [hexc(c) for c in ("#09040b", "#160a1a", "#26122c", "#3a1d42", "#56305e")]
THORN_TIP = hexc("#9a7aa6")
ASH = [hexc(c) for c in ("#1e1a1c", "#2e2729", "#453e3f", "#615a59", "#857d7a")]

WALL_TINT = (0.62, 0.5, 0.62)


# ------------------------------------------------------------------ tiles ---

def make_earth(roots_ramp, n_roots=3):
    def earth(seed, ramp, mortar, light_bias=0):
        n = pnoise2(seed, PERIOD, 8, 3)
        r = rng(seed + 1)
        img = new(PERIOD, PERIOD)
        p = img.load()
        mort = [[False] * PERIOD for _ in range(PERIOD)]
        for y in range(PERIOD):
            for x in range(PERIOD):
                v = n(x, y)
                if v < 0.3:
                    mort[y][x] = True
                    p[x, y] = mortar[0]
                else:
                    p[x, y] = ramp_at(ramp[1:5], 0.1 + (v - 0.3) * 1.25 + 0.1 * light_bias, x, y)
        for _ in range(14):  # pebbles
            x, y = r.randrange(PERIOD), r.randrange(PERIOD)
            for (dx, dy, c) in ((0, 0, ramp[4]), (1, 0, ramp[3]), (0, 1, ramp[3]), (1, 1, ramp[2])):
                p[(x + dx) % PERIOD, (y + dy) % PERIOD] = c
            p[(x + 1) % PERIOD, (y + 2) % PERIOD] = ramp[0]

        def put_root(points, thick):
            for (x, y) in points:
                for t in range(-1, thick + 1):
                    yy = (y + t) % PERIOD
                    xx = x % PERIOD
                    if t == -1 or t == thick:
                        if p[xx, yy] not in roots_ramp:
                            p[xx, yy] = ramp[0]  # shadow groove along the root
                        continue
                    c = roots_ramp[4] if t == 0 else (roots_ramp[1] if t == thick - 1 else roots_ramp[3])
                    if t > 0 and (x * 3 + t) % 7 == 0:
                        c = roots_ramp[2]  # bark
                    p[xx, yy] = c
                    mort[yy][xx] = False

        for k in range(n_roots):
            y0 = r.uniform(0, PERIOD)
            a1, a2 = r.uniform(3, 8), r.uniform(1, 3)
            f2 = r.choice((3, 4, 5))
            ph1, ph2 = r.uniform(0, math.tau), r.uniform(0, math.tau)
            thick = r.choice((2, 3))
            dive = r.uniform(0, PERIOD)  # where the root sinks out of sight
            pts = []
            for x in range(PERIOD):
                y = y0 + a1 * math.sin(math.tau * x / PERIOD + ph1) + a2 * math.sin(math.tau * f2 * x / PERIOD + ph2)
                gap = (x - dive) % PERIOD
                if gap < 9:
                    continue
                pts.append((x, int(round(y))))
            put_root(pts, thick)
            pts = {x: y for (x, y) in pts}
            pts = [(x, pts.get(x, int(y0))) for x in range(PERIOD)]
            for _ in range(3):  # rootlets
                x = r.randrange(PERIOD)
                y = pts[x][1] + thick
                d = r.choice((-1, 1))
                for i in range(r.randint(3, 6)):
                    xx, yy = (x + d * (i // 2)) % PERIOD, (y + i) % PERIOD
                    p[xx, yy] = roots_ramp[2]
        # one root diving vertically
        x0, amp, ph = r.uniform(0, PERIOD), r.uniform(2, 5), r.uniform(0, math.tau)
        for y in range(PERIOD):
            xc = int(round(x0 + amp * math.sin(math.tau * y / PERIOD + ph)))
            for t in range(-1, 3):
                xx = (xc + t) % PERIOD
                if t in (-1, 2):
                    if p[xx, y] not in roots_ramp:
                        p[xx, y] = ramp[0]
                    continue
                p[xx, y] = roots_ramp[4] if t == 0 else roots_ramp[2]
                mort[y][xx] = False
        return img, mort
    return earth


def hyphae_profile(seed):
    r = rng(seed)
    top, th = [], []
    for x in range(PERIOD):
        top.append(1 if r.random() < 0.35 else 0)
        t = 1 if r.random() < 0.4 else 2
        if r.random() < 0.12:
            t += r.choice((2, 3, 4))  # threads trailing over the lip
        th.append(t)
    return top, th


def hyphae_fringe(r, ph):
    f = new(T, T)
    p = f.load()
    x = 0
    while x < T:
        h = r.choice((0, 0, 0, 1, 2, 2, 3, 4))
        lean = r.choice((-1, 0, 0, 1))
        for y in range(h):
            xx = max(0, min(T - 1, x + (lean if y >= 2 else 0)))
            p[xx, T - 1 - y] = HYPHAE[2] if y < h - 1 else HYPHAE[4]
        if h >= 3 and r.random() < 0.35:
            p[max(0, min(T - 1, x + lean)), T - 1 - h] = SPORE
        x += r.choice((1, 2, 2))
    return f


def tendrils(r, ph):
    f = new(T, T)
    p = f.load()
    used = set()
    for _ in range(r.randint(2, 3)):
        x = r.randint(1, 14)
        if x in used:
            continue
        used.update((x - 1, x, x + 1))
        ln = r.randint(5, 14)
        thick = 2 if ln > 9 and x < 14 else 1
        for y in range(ln):
            xx = max(0, min(T - 1, x + int(round(math.sin(y * 0.6 + x) * 0.8))))
            p[xx, y] = ROOT[2] if y < ln - 2 else ROOT[3]
            if thick == 2 and y < ln * 0.5:
                p[min(T - 1, xx + 1), y] = ROOT[1]
        if r.random() < 0.3 and ln + 1 < T:
            p[x, ln] = HYPHAE[4]
        if ln > 7 and r.random() < 0.6:  # a rootlet forking off
            y = ln // 2
            d = r.choice((-1, 1))
            for i in range(1, 4):
                xx = x + d * i
                if 0 <= xx < T and y + i < T:
                    p[xx, y + i] = ROOT[1]
    return f


def root_branch(i):
    """Thick root lying across a gap; walkable top at y=0."""
    f = new(T, T)
    p = f.load()
    for x in range(T):
        p[x, 0] = ROOT[4] if (x + i * 3) % 6 else ROOT[5]
        p[x, 1] = ROOT[3]
        p[x, 2] = ROOT[3] if (x + i) % 5 else ROOT[2]
        p[x, 3] = ROOT[2] if (x * 2 + i) % 7 else ROOT[1]  # bark grooves
        p[x, 4] = ROOT[2]
        p[x, 5] = ROOT[1]
        p[x, 6] = ROOT[0]
    for x in range(T):
        if (x * 5 + i * 3) % 11 == 0:
            p[x, 0] = HYPHAE[4]  # a few glowing hyphae on the bark
    if i == 2:  # knot
        for (x, y, c) in ((7, 2, ROOT[1]), (8, 2, ROOT[1]), (6, 3, ROOT[1]), (9, 3, ROOT[4]), (7, 4, ROOT[4]),
                          (8, 4, ROOT[4]), (7, 3, ROOT[0]), (8, 3, ROOT[0])):
            p[x, y] = c
    if i in (1, 2):  # rootlets dangling underneath
        x = 4 if i == 1 else 11
        for y in range(7, 11 + i):
            p[x + (1 if y > 9 else 0), y] = ROOT[1]
    if i in (0, 3):  # broken-off ends taper and fray
        e = 0 if i == 0 else T - 1
        s = 1 if i == 0 else -1
        for y in (0, 6):
            p[e, y] = CLEAR
        p[e, 1] = ROOT[2]
        p[e + s, 0] = ROOT[3]
        for (dx, y) in ((0, 7), (0, 8), (1, 9), (2, 7), (2, 8), (3, 9), (3, 10)):
            p[e + s * dx, y] = ROOT[1]
    return f


def build_tiles():
    ground = build_terrain("rootdark_ground", EARTH, (EARTH[0], EARTH[1]), seed=51,
                           moss=HYPHAE, profile=hyphae_profile(151), fringe=hyphae_fringe,
                           hang=tendrils, texture=make_earth(ROOT_MID, n_roots=2), platform=root_branch)
    wall = build_terrain("rootdark_wall", WALL, (WALL[0], WALL[0]), seed=52, grass=False,
                         texture=make_earth(ROOT_DIM, n_roots=1))
    return ground, wall


# ------------------------------------------------------------------ thorn ---

def thorn_frames():
    """Thorn-root knot, periodic 16 in x and y so a wall of them tiles seamlessly."""
    def wrap(v):
        return v % T

    # two woven diagonal vines + one horizontal binder
    def bend(x):
        return round(math.sin(math.tau * x / T) * 1.2)

    def vine_a(x, y):
        return wrap(y - x + bend(x)) in (0, 1, 2, 3)

    def vine_b(x, y):
        return wrap(y + x - 8 - bend(x + 4)) in (0, 1, 2, 3)

    def vine_c(x, y):
        return wrap(y - 4 + round(math.sin(math.tau * x / T) * 1.5)) in (0, 1)

    def solid(x, y):
        return vine_a(x, y) or vine_b(x, y) or vine_c(x, y)

    intact = new(T, T)
    p = intact.load()
    for y in range(T):
        for x in range(T):
            a, b = vine_a(x, y), vine_b(x, y)
            top = None
            if a and b:  # woven: the vines take turns passing over each other
                top = "b" if (x // 4) % 2 == 0 else "a"
            elif a:
                top = "a"
            elif b:
                top = "b"
            if top == "a":
                k = wrap(y - x + bend(x))
                c = THORN[4] if k == 0 else (THORN[3] if k == 1 else (THORN[2] if k == 2 else THORN[1]))
            elif top == "b":
                k = wrap(y + x - 8 - bend(x + 4))
                c = THORN[3] if k == 0 else (THORN[2] if k < 3 else THORN[1])
            elif vine_c(x, y):
                c = THORN[3] if wrap(y - 4 + round(math.sin(math.tau * x / T) * 1.5)) == 0 else THORN[1]
            else:
                c = THORN[0]
            p[x, y] = c
    # thorns poking out of the vines into the gaps
    # thorns: spikes grow straight out of the vines into the gaps, tipped pale
    src_px = intact.copy().load()
    for y in range(T):
        for x in range(T):
            if src_px[x, y] != THORN[0] or (x * 7 + y * 5) % 6:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if src_px[wrap(x - dx), wrap(y - dy)] == THORN[0]:
                    continue  # (dx, dy) must point away from a vine pixel
                tip = (wrap(x + dx), wrap(y + dy))
                if src_px[tip] == THORN[0]:
                    p[x, y] = THORN[3]
                    p[tip] = THORN_TIP if (x + y) % 2 else THORN[4]
                break
    frames = [intact]

    # frame 1: glowing cracks along the vine cores
    f1 = intact.copy()
    q = f1.load()
    for y in range(T):
        for x in range(T):
            if wrap(y - x + bend(x)) in (1, 2) and (x + y) % 3 != 0:
                q[x, y] = FIRE[3] if (x + y) % 4 else FIRE[4]
            elif wrap(y + x - 8 - bend(x + 4)) == 1 and (x * 3 + y) % 4 != 0:
                q[x, y] = FIRE[2]
            elif vine_c(x, y) and x % 3 == 0:
                q[x, y] = FIRE[2]
            elif q[x, y] == THORN[0]:
                q[x, y] = FIRE[0] if dith(x, y, 0.25) else THORN[0]
    frames.append(f1)

    # frame 2: burning apart - charred, holes, bright cracks
    f2 = new(T, T)
    q = f2.load()
    for y in range(T):
        for x in range(T):
            if not solid(x, y):
                if dith(x, y, 0.12):
                    q[x, y] = FIRE[1]
                continue
            if dith(x + 1, y + 2, 0.35):
                continue  # crumbled away
            if wrap(y - x + bend(x)) == 1 or wrap(y + x - 8 - bend(x + 4)) == 1:
                q[x, y] = FIRE[4] if (x + y) % 3 == 0 else FIRE[3]
            else:
                q[x, y] = ASH[1] if (x + y) % 2 else ASH[0]
    frames.append(f2)

    # frame 3: ash sifting down, last embers
    f3 = new(T, T)
    q = f3.load()
    for y in range(T):
        for x in range(T):
            if solid(x, y) and dith(x + 3, y + 1, 0.2):
                q[x, y] = ASH[3] if y > 9 else ASH[2]
    for (x, y) in ((4, 11), (12, 5), (9, 14)):
        q[x, y] = FIRE[3]
    frames.append(f3)
    return frames


# --------------------------------------------------------------- backdrop ---

BASE_RAMP = [hexc(c) for c in ("#060307", "#0a050c", "#0f0812", "#140b18", "#1a0f1f")]


def root_base():
    img = new(W, H)
    vgrad(img, BASE_RAMP, [(0, 0.1), (90, 0.45), (180, 0.9), (230, 1.0), (270, 0.6)])
    p = img.load()
    for (cx, cy, rad) in ((100, 190, 70), (330, 160, 90)):
        for y in range(cy - rad, cy + rad):
            for x in range(cx - rad, cx + rad):
                if 0 <= x < W and 0 <= y < H:
                    d = math.hypot(x - cx, (y - cy) * 1.3) / rad
                    if d < 1 and dith(x, y, (1 - d) * 0.45):
                        p[x, y] = hexc("#1d1028")
    r = rng(53)
    for _ in range(110):
        x, y = r.randrange(W), r.randrange(H)
        b = r.random()
        p[x, y] = SPORE if b > 0.93 else (AMETHYST[2] if b > 0.6 else AMETHYST[1])
    return img


def giant_roots(seed, w=640):
    img = new(w, H)
    p = img.load()
    r = rng(seed)
    body, rim, groove = hexc("#140a14"), hexc("#241322"), hexc("#0e070e")
    m = Mask(w, H)
    roots = []
    for i in range(5):
        x0 = (i + r.uniform(0.2, 0.8)) * w / 5
        wt = r.uniform(26, 44)
        sway, freq, ph, drift = r.uniform(6, 16), r.uniform(0.012, 0.025), r.uniform(0, math.tau), r.uniform(-0.12, 0.12)
        fork = r.uniform(120, 220) if r.random() < 0.6 else None
        roots.append((x0, wt, sway, freq, ph, drift, fork))
        for y in range(H):
            xc = x0 + sway * math.sin(y * freq + ph) + drift * y
            half = wt / 2 * (1 - 0.35 * y / H) + 2 * math.sin(y * 0.07 + ph)
            if fork and y > fork:
                spread = (y - fork) * 0.35
                for sx in (-1, 1):
                    c = xc + sx * spread
                    hw = half * 0.55
                    for x in range(int(c - hw), int(c + hw) + 1):
                        m.set(x % w, y)
            else:
                for x in range(int(xc - half), int(xc + half) + 1):
                    m.set(x % w, y)
    # floor of tangled earth
    f = periodic_noise(seed + 2, w, ((2, 1.0), (5, 0.5), (11, 0.25)))
    for x in range(w):
        m.rect(x, int(236 + 6 * f(x)), x, H - 1)
    for y in range(H):
        for x in range(w):
            if m.m[y][x]:
                p[x, y] = body
    rim_light(img, rim)
    for (x0, wt, sway, freq, ph, drift, fork) in roots:  # bark grooves follow the sway
        for k in (-0.25, 0.1, 0.32):
            for y in range(0, int(fork or H)):
                xc = x0 + sway * math.sin(y * freq + ph) + drift * y + k * wt * (1 - 0.35 * y / H)
                xx = int(xc) % w
                if p[xx, y] == body and (y // 3) % 5:
                    p[xx, y] = groove
    for _ in range(60):  # spores drifting near the roots
        x, y = r.randrange(w), r.randrange(H - 40)
        if p[x, y][3] == 0 and any(p[(x + d) % w, y][3] for d in (-4, 4)):
            p[x, y] = AMETHYST[3] if r.random() < 0.6 else SPORE
    return img


def root_arches(seed, w=640):
    img = new(w, H)
    p = img.load()
    r = rng(seed)
    body, rim = hexc("#0c060c"), hexc("#1b0e1a")
    m = Mask(w, H)
    for i in range(7):  # arcs from the floor up and back down
        cx, cy = r.uniform(0, w), r.uniform(200, 290)
        R = r.uniform(50, 120)
        thick = r.uniform(6, 13)
        a0, a1 = r.uniform(0.05, 0.4), r.uniform(0.6, 0.95)
        for a in [a0 + (a1 - a0) * k / 400 for k in range(401)]:
            t = math.pi * a
            for d in range(int(thick)):
                rr = R + d - thick / 2 + math.sin(t * 7 + i) * 2
                x, y = cx + math.cos(t) * rr, cy - math.sin(t) * rr * 0.9
                m.set(int(x) % w, int(y))
    for i in range(4):  # roots falling from the ceiling, bending
        x0 = r.uniform(0, w)
        for y in range(0, int(r.uniform(90, 200))):
            xc = x0 + math.sin(y * 0.03 + i) * 14
            hw = max(2.0, 7 - y * 0.03)
            for x in range(int(xc - hw), int(xc + hw) + 1):
                m.set(x % w, y)
    f = periodic_noise(seed + 1, w, ((3, 1.0), (7, 0.4)))
    for x in range(w):
        m.rect(x, int(252 + 5 * f(x)), x, H - 1)
    for y in range(H):
        for x in range(w):
            if m.m[y][x]:
                p[x, y] = body
    rim_light(img, rim)
    return img


def hanging_tendrils(seed, w=640):
    img = new(w, H)
    p = img.load()
    r = rng(seed)
    body = hexc("#050306")
    f = periodic_noise(seed + 1, w, ((2, 1.0), (6, 0.5)))
    for x in range(w):
        for y in range(int(6 + 5 * f(x))):
            p[x, y] = body
    for _ in range(55):
        x0 = r.uniform(0, w)
        ln = int(r.uniform(15, 120))
        thick = 2 if r.random() < 0.3 else 1
        for y in range(ln):
            x = int(x0 + math.sin(y * 0.08 + x0) * 3)
            for t in range(thick):
                p[(x + t) % w, y] = body
        if r.random() < 0.3:
            x = int(x0 + math.sin(ln * 0.08 + x0) * 3)
            p[x % w, ln] = AMETHYST[2]
            p[x % w, ln + 1] = AMETHYST[3]
    return img


def build_backdrop():
    layers = {
        "base": root_base(),
        "far": giant_roots(91),
        "mid": root_arches(92),
        "near": hanging_tendrils(93),
    }
    for name, img in layers.items():
        save(img, f"bg/rootdark_{name}.png")
    return layers


# ------------------------------------------------------------------ props ---

FKEY = {"a": HYPHAE[1], "b": HYPHAE[2], "c": HYPHAE[3], "d": HYPHAE[4], "e": HYPHAE[5], "f": SPORE,
        "s": hexc("#4a3a52"), "t": hexc("#6d5a74"), "g": hexc("#24132e")}


def fungus_tall():
    s = [
        "...cdd....",
        "..cddee...",
        ".bcddeef..",
        "bbccdddee.",
        "abbccdddd.",
        ".ggggggg..",
        "....st....",
        "....st....",
        "...st.....",
        "...st.....",
        ".bcdd.....",
        "bccdde....",
        "agggg.....",
        "...st.....",
        "...st.....",
        "....st....",
        "....st....",
        "...sstt...",
    ]
    return outline(sprite(s, FKEY), INK)


def fungus_cluster():
    s = [
        "...cdd........",
        "..bcdde...cd..",
        ".abcdddfbccde.",
        ".gggggg.agggg.",
        "...st.cd..st..",
        "...st.ggg.st..",
        "..sst..st.st..",
        ".sssttsstsstt.",
    ]
    return outline(sprite(s, FKEY), INK)


def spore_pod():
    m = Mask(10, 10)
    m.ellipse(5, 4.5, 4, 4.2)
    m.rect(4, 8, 5, 9)
    img = new(10, 10)
    p = img.load()
    for y in range(10):
        for x in range(10):
            if m.get(x, y):
                d = math.hypot(x + 0.5 - 4.2, y + 0.5 - 3.6) / 4.2
                p[x, y] = ramp_at(HYPHAE[1:5], 1 - d * 0.9, x, y)
    for (x, y) in ((3, 2), (6, 4), (4, 6), (6, 2)):
        p[x, y] = SPORE if (x, y) == (3, 2) else HYPHAE[5]
    p[4, 8] = ROOT[2]
    p[5, 8] = ROOT[1]
    p[4, 9] = ROOT[2]
    p[5, 9] = ROOT[1]
    return outline(img, INK)


def root_knot():
    m = Mask(16, 10)
    img = new(16, 10)
    p = img.load()
    loops = [(4, 9, 4, 5), (10, 9, 5, 7), (7, 9, 3, 3), (13, 9, 3, 4)]
    for (cx, cy, rx, ry) in loops:
        for a in range(0, 181, 4):
            t = math.radians(a)
            x, y = int(round(cx + math.cos(t) * rx)), int(round(cy - math.sin(t) * ry))
            if 0 <= x < 16 and 0 <= y < 10:
                p[x, y] = ROOT[4] if a > 90 else ROOT[3]
                if y + 1 < 10:
                    q = p[x, y + 1]
                    if q[3] == 0:
                        p[x, y + 1] = ROOT[1]
    for x in range(1, 15):
        p[x, 9] = ROOT[2] if x % 3 else ROOT[1]
    p[10, 2] = HYPHAE[4]
    return outline(img, INK)


def root_hang():
    w, h = 8, 30
    img = new(w, h)
    p = img.load()
    for y in range(h):
        k = 1 - y / (h - 1)
        half = 0.6 + 2.6 * k ** 0.8
        cx = 3.5 + math.sin(y * 0.22) * 1.2
        for x in range(w):
            rel = (x + 0.5 - cx) / half
            if abs(rel) <= 1:
                c = ROOT_MID[4] if rel < -0.4 else (ROOT_MID[3] if rel < 0.2 else ROOT_MID[1])
                if (y * 3 + x) % 9 == 0:
                    c = ROOT_MID[2]
                p[x, y] = c
    for i in range(6):  # side rootlet
        x, y = 5 + i // 2, 9 + i
        if x < w:
            p[x, y] = ROOT_MID[2]
    p[int(3.5 + math.sin((h - 1) * 0.22) * 1.2), h - 1] = HYPHAE[4]
    img = outline(img, INK)
    q = img.load()
    for x in range(w):  # sits flush against the ceiling
        if q[x, 0] == INK:
            q[x, 0] = CLEAR
    return img


# ---------------------------------------------------------------- preview ---

TEST = [
    "##################################",
    "###wwwww......######......wwwww###",
    "##wwwww...........................#",
    "#wwww.............................#",
    "#www..............................#",
    "#ww............................####",
    "#w.....=====...........TT......####",
    "#......................TT....######",
    "#......................TT....######",
    "####...........######..TT...#######",
    "#####.......########...TT....######",
    "######.....#########...TT....######",
    "#######...##########=====.....#####",
    "##########################....#####",
    "##################################",
    "##################################",
]


def build():
    ground, wall = build_tiles()
    layers = build_backdrop()
    thorns = thorn_frames()
    save(sheet(thorns), "sprites/thorn.png")
    props = {
        "fungus_tall": fungus_tall(),
        "fungus_cluster": fungus_cluster(),
        "root_hang": root_hang(),
        "spore_pod": spore_pod(),
        "root_knot": root_knot(),
    }
    for k, img in props.items():
        save(img, f"deco/{k}.png")

    save_preview(ground, "rootdark_ground_atlas.png", 3)
    deco_rows_preview(ground, "rootdark_deco_rows.png")
    save_preview(compose_backdrop(layers, 40), "rootdark_bg.png", 2)
    rows = pad_rows(TEST)
    grid = [r.replace("T", ".") for r in rows]
    width = len(rows[0]) * T
    bd = scene_backdrop(layers, width)
    placed = [
        (props["fungus_tall"], 5, 12, False), (props["fungus_cluster"], 13, 8, False),
        (props["spore_pod"], 16, 8, False), (props["root_knot"], 19, 8, False),
        (props["root_hang"], 10, 1, True), (props["root_hang"], 19, 1, True),
        (props["fungus_cluster"], 27, 12, False), (props["fungus_tall"], 3, 8, False),
    ]
    scene = compose_scene(ground, wall, bd, grid, placed, wall_mod=WALL_TINT)
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            if c == "T":
                frame = 0 if y < 9 else (1 if y < 10 else (2 if y < 11 else 3))
                scene.alpha_composite(thorns[frame], (x * T, y * T))
    save_preview(scene, "rootdark_test.png", 2)
    lit = ingame(scene, [(20 * T, 8 * T + 6, 96, (1.0, 0.78, 0.5), 0.7)], ambient=(0.36, 0.3, 0.42))
    save_preview(lit, "rootdark_test_ingame.png", 2)
    props_sheet(list(props.values()) + thorns, "rootdark_props.png")


if __name__ == "__main__":
    build()
