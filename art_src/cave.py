"""Chapter II - the Glimmerdeep: crystal caves under the mountain.

Run `python cave.py` to (re)generate every cave asset:

  tiles/cave_ground.png   256x288  same atlas layout as forest_ground (see tiles.py):
                                   blue-grey cobble with faint crystal flecks, dark teal
                                   lichen tops, dripping stalactites + lichen strands in
                                   deco row cols 4-7, grey Keeper scaffolding in row 17
  tiles/cave_wall.png     256x288  dark indigo background rock (rows 0-15 used)
  bg/cave_base.png        480x270  static gradient with glow-worm specks (factor 0)
  bg/cave_far.png         640x270  far cavern: columns, ceiling + floor, crystal glints
  bg/cave_mid.png         640x270  mid stalagmites / stalactites
  bg/cave_near.png        640x270  near ceiling of big hanging rock (top only)
  deco/crystal_big.png, crystal_small.png, crystal_violet.png, stalagmite.png,
  deco/cave_shroom.png, bones.png        floor props, anchored bottom-centre
  deco/stalactite_a.png, stalactite_b.png ceiling props, anchored top-centre
  sprites/glimmer.png     64x16    4 frames of 16x16: 0 dormant, 1 lit, 2-3 lit shimmer
  sprites/wickway.png     96x48    4 frames of 24x48: 0 cold, 1-3 lit flicker

The backdrop is assembled in scenes/backdrops/cave.tscn. Previews go to
art_src/_preview/cave_*.png.
"""
import math

from bg import periodic_noise
from pix import (AMETHYST, BONE, CRYSTAL, FIRE, INK, STONE, CLEAR, dith, hexc, new, outline,
                 paste, ramp_at, rng, save, save_preview, sheet, sprite)
from tiles import PERIOD, T, build_terrain
from envkit import compose_backdrop, compose_scene, ingame, vgrad

W, H = 480, 270

CAVE_ROCK = [hexc(c) for c in ("#12131f", "#1e2133", "#2c3249", "#3e4762", "#57637f", "#7c8aa6")]
CAVE_WALL = [hexc(c) for c in ("#08080f", "#0e0f1a", "#151726", "#1c1f33", "#252a42", "#2f3551")]
LICHEN = [hexc(c) for c in ("#0b1a1f", "#11303a", "#184545", "#215c55", "#2e7868", "#4fa48a")]
KEEPER_WOOD = [hexc(c) for c in ("#17121a", "#2a2129", "#3e3239", "#56464a", "#6f5d5c", "#8c7870")]
BRASS = [hexc(c) for c in ("#2a1c18", "#4f3424", "#7a5530", "#a8803e", "#d3b25e")]
GLOWWORM = hexc("#8ff0e0")


# ------------------------------------------------------------------ tiles ---

def crystal_flecks(tex, mort):
    """Sparse glimmer flecks embedded in a few cobbles."""
    p = tex.load()
    r = rng(77)
    for y in range(PERIOD):
        for x in range(PERIOD):
            if mort[y][x] or r.random() > 0.0022:
                continue
            p[x, y] = CRYSTAL[3] if r.random() < 0.45 else CRYSTAL[2]
            nx, ny = (x + 1) % PERIOD, (y + 1) % PERIOD
            if not mort[ny][nx]:
                p[nx, ny] = CRYSTAL[1]


def lichen_profile(seed):
    r = rng(seed)
    top, th = [], []
    for x in range(PERIOD):
        top.append(1 if r.random() < 0.3 else 0)
        t = 2 if r.random() < 0.45 else 3
        if r.random() < 0.09:
            t += r.choice((2, 3))  # lichen drips over the lip
        th.append(t)
    return top, th


def lichen_fringe(r, ph):
    """Low moss cushions with the odd glowing spore."""
    f = new(T, T)
    p = f.load()
    x = 0
    while x < T:
        h = r.choice((0, 0, 0, 1, 1, 1, 2, 2))
        for y in range(h):
            p[x, T - 1 - y] = LICHEN[3] if y == 0 else LICHEN[4]
        if h == 2 and r.random() < 0.3:
            p[x, T - 3] = GLOWWORM if r.random() < 0.5 else LICHEN[5]
        x += r.choice((1, 1, 2))
    return f


def drips(r, ph):
    """Stalactite drips and pale lichen strands hanging from a ceiling."""
    f = new(T, T)
    p = f.load()
    used = set()
    for _ in range(r.randint(1, 3)):
        x = r.randint(1, 13)
        if x in used or x + 1 in used:
            continue
        used.update((x - 1, x, x + 1, x + 2))
        ln = r.randint(3, 8)
        for y in range(ln):
            wid = 2 if y < ln * 0.55 else 1
            for k in range(wid):
                c = CAVE_ROCK[2] if k == 0 else CAVE_ROCK[1]
                if y == 0:
                    c = CAVE_ROCK[1]
                p[x + k, y] = c
        p[x, ln - 1] = CAVE_ROCK[3]
        if r.random() < 0.5 and ln + 2 < T:
            p[x, ln + 1] = CRYSTAL[3]  # a single falling drop
    for _ in range(r.randint(1, 2)):
        x = r.randint(1, 14)
        if x in used:
            continue
        ln = r.randint(4, 10)
        for y in range(ln):
            p[x, y] = LICHEN[2] if y < ln - 2 else LICHEN[3]
        p[x, ln - 1] = LICHEN[5]
    return f


def build_tiles():
    ground = build_terrain("cave_ground", CAVE_ROCK, (CAVE_ROCK[0], CAVE_ROCK[1]), seed=31,
                           moss=LICHEN, wood=KEEPER_WOOD, profile=lichen_profile(131),
                           tex_post=crystal_flecks, fringe=lichen_fringe, hang=drips)
    wall = build_terrain("cave_wall", CAVE_WALL, (CAVE_WALL[0], CAVE_WALL[0]), seed=32, grass=False)
    return ground, wall


# -------------------------------------------------------------- backdrops ---

BASE_RAMP = [hexc(c) for c in ("#06060d", "#0a0b16", "#0e1120", "#13182b", "#182037")]


def cave_base():
    img = new(W, H)
    vgrad(img, BASE_RAMP, [(0, 0.0), (70, 0.3), (150, 0.85), (200, 1.0), (240, 0.6), (270, 0.3)])
    p = img.load()
    r = rng(51)
    # faint far crystal glow, a couple of dithered blooms
    for (cx, cy, rad) in ((120, 170, 60), (360, 150, 75)):
        for y in range(cy - rad, cy + rad):
            for x in range(cx - rad, cx + rad):
                if not (0 <= x < W and 0 <= y < H):
                    continue
                d = math.hypot(x - cx, (y - cy) * 1.6) / rad
                if d < 1 and dith(x, y, (1 - d) * 0.55):
                    p[x, y] = hexc("#14223a") if d > 0.45 else hexc("#182a45")
    # glow-worms on the far ceiling, thinning out downward
    for _ in range(140):
        x = r.randrange(W)
        y = int(r.random() ** 2.2 * 120)
        b = r.random()
        p[x, y] = GLOWWORM if b > 0.9 else (CRYSTAL[2] if b > 0.55 else CRYSTAL[1])
    return img


def silhouette(seed, w, ceil_base, ceil_amp, floor_base, floor_amp, n_cols, spikes, body, rim,
               glints=0, col_width=(10, 24)):
    """Cavern slice: ragged ceiling + floor, joined by a few columns, with stalactites/-mites."""
    img = new(w, H)
    p = img.load()
    r = rng(seed)
    fc = periodic_noise(seed + 1, w, ((2, 1.0), (3, 0.6), (7, 0.3), (13, 0.15)))
    ff = periodic_noise(seed + 2, w, ((1, 1.0), (3, 0.5), (5, 0.3), (11, 0.15)))
    ceil = [ceil_base + ceil_amp * fc(x) for x in range(w)]
    floor = [floor_base + floor_amp * ff(x) for x in range(w)]
    # stalactites (down from ceiling) and stalagmites (up from floor)
    for _ in range(spikes):
        x0 = r.uniform(0, w)
        ln = r.uniform(10, 46)
        half = r.uniform(2.5, 6.5)
        down = r.random() < 0.55
        for xx in range(int(x0 - half) - 1, int(x0 + half) + 2):
            rel = abs(xx - x0) / half
            if rel > 1:
                continue
            reach = ln * (1 - rel) ** 1.4
            xi = xx % w
            if down:
                ceil[xi] = max(ceil[xi], ceil_base + ceil_amp * fc(xi) + reach)
            else:
                floor[xi] = min(floor[xi], floor_base + floor_amp * ff(xi) - reach)
    # columns that join floor and ceiling
    cols = []
    for _ in range(n_cols):
        x0 = r.uniform(0, w)
        cw = r.uniform(*col_width)
        wob = r.uniform(0, math.tau)
        cols.append((x0, cw, wob))
    for x in range(w):
        for y in range(H):
            solid = y < ceil[x] or y >= floor[x]
            if not solid:
                for (x0, cw, wob) in cols:
                    # hourglass column: wide at both ends, pinched in the middle
                    t = y / H
                    half = cw * (0.42 + 0.5 * (abs(t - 0.5) * 2) ** 2) + 1.5 * math.sin(y * 0.09 + wob)
                    dx = (x - x0 + w / 2) % w - w / 2
                    if abs(dx) < half:
                        solid = True
                        break
            if solid:
                p[x, y] = body
    # rim light: pixels whose right neighbour (or below) is open
    q = img.copy().load()
    for x in range(w):
        for y in range(H):
            if q[x, y][3] == 0:
                continue
            right_open = q[(x + 1) % w, y][3] == 0
            below_open = y + 1 < H and q[x, y + 1][3] == 0
            above_open = y > 0 and q[x, y - 1][3] == 0
            if right_open or (below_open and dith(x, y, 0.5)) or (above_open and dith(x, y, 0.35)):
                p[x, y] = rim
    # tiny crystal glints embedded near open edges
    placed = 0
    tries = 0
    while placed < glints and tries < glints * 40:
        tries += 1
        x, y = r.randrange(w), r.randrange(H)
        if q[x, y][3] == 0:
            continue
        near_open = any(q[(x + dx) % w, min(H - 1, max(0, y + dy))][3] == 0
                        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)))
        if not near_open:
            continue
        p[x, y] = CRYSTAL[3] if r.random() < 0.6 else CRYSTAL[4]
        if r.random() < 0.6:
            p[(x + 1) % w, y] = CRYSTAL[2]
        if r.random() < 0.4 and y + 1 < H:
            p[x, y + 1] = CRYSTAL[1]
        placed += 1
    return img


def near_ceiling(seed, w=640):
    img = new(w, H)
    p = img.load()
    r = rng(seed)
    fc = periodic_noise(seed + 1, w, ((2, 1.0), (5, 0.5), (9, 0.3)))
    depth = [26 + 10 * fc(x) for x in range(w)]
    for _ in range(11):
        x0 = r.uniform(0, w)
        ln = r.uniform(25, 70)
        half = r.uniform(6, 13)
        for xx in range(int(x0 - half) - 1, int(x0 + half) + 2):
            rel = abs(xx - x0) / half
            if rel <= 1:
                xi = xx % w
                depth[xi] = max(depth[xi], 26 + 10 * fc(xi) + ln * (1 - rel) ** 1.6)
    body, rim = hexc("#07080f"), hexc("#0f1220")
    for x in range(w):
        for y in range(int(depth[x])):
            p[x, y] = body
        y = int(depth[x])
        if 0 < y < H:
            p[x, y - 1] = rim
            if dith(x, y, 0.5):
                p[x, y - 2] = rim
        if (x * 13) % 41 == 0 and y + 1 < H:  # drops hanging from the tips
            p[x, y] = CRYSTAL[1]
    return img


def build_backdrop():
    layers = {
        "base": cave_base(),
        "far": silhouette(61, 640, 34, 16, 206, 10, 4, 34, hexc("#121a2e"), hexc("#1b2741"), glints=26,
                          col_width=(10, 22)),
        "mid": silhouette(62, 640, 14, 12, 232, 8, 2, 22, hexc("#0b0f1d"), hexc("#141c31"), glints=10,
                          col_width=(16, 30)),
        "near": near_ceiling(63),
    }
    for name, img in layers.items():
        save(img, f"bg/cave_{name}.png")
    return layers


# ------------------------------------------------------------------ props ---

def prism(img, x0, base, height, width, ramp, lean=0.0, outline_col=None):
    """One faceted crystal prism: pointed tip, lit left face, darker right face."""
    p = img.load()
    tip_h = max(2, int(width * 0.9))
    for y in range(height):
        yy = base - y
        if yy < 0:
            continue
        cx = x0 + lean * y
        if y < height - tip_h:
            half = width / 2
        else:
            half = width / 2 * (height - y) / tip_h
        lo, hi = int(round(cx - half)), int(round(cx + half))
        for x in range(lo, hi + 1):
            if not (0 <= x < img.width):
                continue
            rel = (x - cx) / max(0.5, half)
            if rel < -0.25:
                c = ramp[3]
            elif rel < 0.2:
                c = ramp[2]
            else:
                c = ramp[1]
            if x == lo:
                c = ramp[4] if y > 1 else ramp[3]
            p[x, yy] = c
        top_x = int(round(cx))
        if y == height - 1 and 0 <= top_x < img.width:
            p[top_x, yy] = ramp[4]


def crystal_cluster(seed, w, h, ramp, specs):
    img = new(w, h)
    for (x0, height, width, lean) in specs:
        prism(img, x0, h - 1, height, width, ramp, lean)
    img = outline(img, ramp[0])
    p = img.load()
    r = rng(seed)
    for _ in range(3):  # sparkle
        x, y = r.randrange(w), r.randrange(h)
        if p[x, y][3] and p[x, y] != ramp[0]:
            p[x, y] = ramp[4]
    return img


def crystal_big():
    ramp = CRYSTAL
    specs = [(6, 14, 4, -0.18), (16, 16, 4, 0.16), (11, 23, 5, -0.02), (8, 9, 3, -0.35), (15, 8, 3, 0.4)]
    return crystal_cluster(1, 22, 26, ramp, specs)


def crystal_small():
    specs = [(4, 8, 3, -0.25), (7, 12, 3, 0.05), (10, 6, 3, 0.35)]
    return crystal_cluster(2, 13, 14, CRYSTAL, specs)


def crystal_violet():
    specs = [(5, 10, 4, -0.22), (9, 15, 4, 0.04), (13, 7, 3, 0.3)]
    return crystal_cluster(3, 17, 17, AMETHYST, specs)


def stalagmite():
    w, h = 14, 22
    img = new(w, h)
    p = img.load()
    for y in range(h):
        k = y / (h - 1)  # 0 at tip
        half = 0.6 + 5.6 * k ** 1.15
        cx = w / 2 - 0.5 + math.sin(y * 0.35) * 0.4
        for x in range(w):
            rel = (x - cx) / half
            if abs(rel) > 1:
                continue
            if rel < -0.45:
                c = STONE[4] if y > 2 else STONE[3]
            elif rel < 0.15:
                c = STONE[3]
            elif rel < 0.6:
                c = STONE[2]
            else:
                c = STONE[1]
            if y % 6 == 3 and -0.5 < rel < 0.5 and x % 2:
                c = STONE[2]  # growth rings
            if y > h - 4 and rel > 0:
                c = STONE[1]
            p[x, y] = c
    p[int(w / 2), 0] = CRYSTAL[3]  # wet tip
    return outline(img, INK)


def cave_shroom():
    m = [
        "...cccc.......",
        "..cdddec......",
        ".cddddddc.ccc.",
        ".bbbbbbbbcdeec",
        "....ss..bbbbbb",
        "....ss....s...",
        "...sss...ss...",
    ]
    key = {"b": CRYSTAL[2], "c": CRYSTAL[3], "d": CRYSTAL[4], "e": hexc("#ffffff"), "s": BONE[2]}
    return outline(sprite(m, key), INK)


def bones():
    b = [
        "..aaa.........",
        ".abbba....c...",
        ".bdbdb...cc.c.",
        ".abbba.cbbbbcc",
        "cc.ba..c....c.",
        ".ccbbbbbbc....",
    ]
    return outline(sprite(b, {"a": BONE[3], "b": BONE[2], "c": BONE[1], "d": INK}), INK)


def stalactite(w, h, seed):
    img = new(w, h)
    p = img.load()
    for y in range(h):
        k = 1 - y / (h - 1)  # 1 at the ceiling, 0 at the tip
        half = 0.5 + (w / 2 - 1) * k ** 1.2
        cx = w / 2 - 0.5
        for x in range(w):
            rel = (x - cx) / half
            if abs(rel) <= 1:
                t = 0.5 - 0.45 * rel - 0.2 * (1 - k)
                p[x, y] = ramp_at(CAVE_ROCK[1:5], t, x, y)
    img = outline(img, INK)
    q = img.load()
    for x in range(w):  # no outline along the ceiling it hangs from
        if q[x, 0] == INK:
            q[x, 0] = CAVE_ROCK[1]
    q[int(w / 2 - 0.5), h - 1] = CRYSTAL[3]
    return img


# ---------------------------------------------------------------- glimmer ---

def glimmer_frames():
    """Light-drinking crystal block: dormant ghost + lit solid (+2 shimmer).

    Facets form a diamond lattice with period 16, so lit blocks placed side by
    side (or stacked) join without a seam.
    """
    def facet(x, y):
        """-> (shade 0..3 with 3 = brightest, on_edge) for the lattice cell."""
        u, v = x + 0.5 - 8, y + 0.5 - 8
        if abs(u) + abs(v) >= 8:  # belongs to a corner diamond
            u = u - 8 if u > 0 else u + 8
            v = v - 8 if v > 0 else v + 8
        edge = abs(u) + abs(v) > 6.6
        if u < 0 and v < 0:
            s = 3
        elif u >= 0 and v < 0:
            s = 2
        elif u < 0:
            s = 1
        else:
            s = 0
        return s, edge

    frames = []
    # frame 0: dormant ghost - dotted rim + a whisper of the lattice
    f = new(T, T)
    p = f.load()
    for y in range(T):
        for x in range(T):
            border = y == 0 or y == T - 1 or x == 0 or x == T - 1
            _, edge = facet(x, y)
            if border and dith(x, y, 0.5):
                p[x, y] = CRYSTAL[1][:3] + (190,)
            elif edge and dith(x, y, 0.3):
                p[x, y] = CRYSTAL[1][:3] + (100,)
    p[4, 0] = CRYSTAL[2][:3] + (210,)
    p[12, 0] = CRYSTAL[2][:3] + (210,)
    frames.append(f)

    shades = (CRYSTAL[1], CRYSTAL[2], CRYSTAL[2], CRYSTAL[3])

    def lit(sparks):
        f = new(T, T)
        p = f.load()
        for y in range(T):
            for x in range(T):
                s, edge = facet(x, y)
                c = shades[s]
                if s == 1 and dith(x, y, 0.5):
                    c = CRYSTAL[1]  # lower-left facet: half-tone between dark and mid
                if edge:
                    c = CRYSTAL[4] if s >= 2 else CRYSTAL[1]
                p[x, y] = c
        for x in range(T):
            p[x, 0] = CRYSTAL[4]
            p[x, 1] = CRYSTAL[4] if p[x, 1] in (CRYSTAL[3], CRYSTAL[4]) else CRYSTAL[3]
            p[x, T - 1] = CRYSTAL[0]
        for (sx, sy) in sparks:
            p[sx, sy] = hexc("#ffffff")
            for dx, dy in ((1, 0), (-1, 0), (0, 1)):
                if 0 <= sx + dx < T and 0 <= sy + dy < T and dy >= 0:
                    p[sx + dx, sy + dy] = CRYSTAL[4]
        return f

    frames.append(lit([(5, 0)]))
    frames.append(lit([(11, 0), (3, 4)]))
    frames.append(lit([(14, 0), (10, 9)]))
    return frames


# ---------------------------------------------------------------- wickway ---

def wickway_frames():
    """Keeper lantern-lift post: stone plinth, brass post, caged lantern, chain up."""
    fw, fh = 24, 48
    base = new(fw, fh)
    p = base.load()
    cx = 12  # post occupies x 11..12

    # chain from the top of the frame down to the cage
    for y in range(0, 5):
        p[cx - 1 + (y % 2), y] = STONE[3] if y % 2 else STONE[2]
        p[cx - (y % 2), y] = STONE[1]
    # cage: 10 wide x 13 tall (y 5..17), x 7..16
    for y in range(5, 18):
        for x in range(7, 17):
            edge = x in (7, 16) or y in (5, 6, 16, 17)
            bar = x in (10, 13)
            if y == 5 and x in (7, 16):
                continue
            if edge or bar:
                if y in (5, 6):
                    c = BRASS[3] if y == 5 else BRASS[2]
                elif y in (16, 17):
                    c = BRASS[2] if y == 16 else BRASS[1]
                else:
                    c = BRASS[2] if x < 12 else BRASS[1]
                p[x, y] = c
            else:
                p[x, y] = hexc("#0c0a12")
    # roof ring + top loop
    for x in range(9, 15):
        p[x, 4] = BRASS[2]
    p[11, 3] = BRASS[3]
    p[12, 3] = BRASS[2]
    # post
    for y in range(18, 40):
        p[cx - 1, y] = BRASS[2] if (y % 6) else BRASS[3]
        p[cx, y] = BRASS[1]
    for y in (24, 32):  # collar bands
        for x in range(cx - 2, cx + 2):
            p[x, y] = BRASS[3] if x < cx else BRASS[2]
    # lift wheel on the post
    wx, wy, wr = cx + 4, 27, 3
    for y in range(wy - wr - 1, wy + wr + 2):
        for x in range(wx - wr - 1, wx + wr + 2):
            d = math.hypot(x - wx, y - wy)
            if wr - 0.8 <= d <= wr + 0.4:
                p[x, y] = BRASS[3] if y < wy else BRASS[2]
            elif d < 0.8:
                p[x, y] = BRASS[4]
            elif d < wr - 0.8 and (x == wx or y == wy):
                p[x, y] = BRASS[1]
    for x in range(cx + 1, wx):
        p[x, wy] = BRASS[1]
    # stone plinth (y 40..47)
    plinth = [
        "......aaaaaaaaaaaa......",
        ".....abbccccccccbba.....",
        ".....abcdddddddccba.....",
        "....aaaaaaaaaaaaaaaa....",
        "...abbcccccddddccccba...",
        "...abccdddddddddccbba...",
        "..aabbbccccccccccbbbaa..",
        "..aaaaaaaaaaaaaaaaaaaa..",
    ]
    paste(base, sprite(plinth, {"a": INK, "b": STONE[1], "c": STONE[2], "d": STONE[3]}), 0, 40)
    q = base.load()
    for (x, y) in ((8, 45), (15, 44), (11, 46)):  # Keeper runes, faintly carved
        q[x, y] = STONE[0]
    base = outline(base, INK)

    flames = [
        ["..c...", ".cdc..", ".cedc.", "cdefdc", ".cddc."],
        ["...c..", "..cdc.", ".cdedc", "cdefdc", ".cddc."],
        [".c..c.", ".cdc..", "cdedc.", "cdefdc", ".cddc."],
    ]
    fkey = {"c": FIRE[2], "d": FIRE[3], "e": FIRE[4], "f": FIRE[5]}
    frames = []
    cold = base.copy()
    cq = cold.load()
    cq[12, 15] = FIRE[0]  # dead wick
    cq[12, 14] = INK
    frames.append(cold)
    for i, fl in enumerate(flames):
        img = base.copy()
        iq = img.load()
        for y in range(7, 16):  # warm glass glow behind the bars
            for x in range(8, 16):
                if iq[x, y] == hexc("#0c0a12"):
                    iq[x, y] = FIRE[1] if dith(x, y, 0.35 + 0.1 * i) else FIRE[0]
        paste(img, sprite(fl, fkey), 9, 10)
        iq = img.load()
        for y in range(7, 16):  # bars catch the light on their inner edge
            for x in (10, 13):
                if iq[x, y] in (BRASS[1], BRASS[2]):
                    iq[x, y] = BRASS[4] if (y + i) % 3 else BRASS[3]
        for x in range(9, 15):
            iq[x, 4] = BRASS[3]
        frames.append(img)
    return frames


# ---------------------------------------------------------------- preview ---

TEST = [
    "##################################",
    "####www......####....######wwww##",
    "###wwww..........................#",
    "##wwwww..........................#",
    "#wwwwww..........................#",
    "#wwwwww..........................#",
    "#wwwww.....................=====.#",
    "#wwww............................#",
    "#www.........######..............#",
    "#ww..........######...........####",
    "###.....................GGGG..####",
    "####.........................#####",
    "#####.....===.......#####....#####",
    "######.............######....#####",
    "########.....###..#######....#####",
    "##################################",
    "##################################",
]


def build():
    ground, wall = build_tiles()
    layers = build_backdrop()
    props = {
        "crystal_big": crystal_big(),
        "crystal_small": crystal_small(),
        "crystal_violet": crystal_violet(),
        "stalagmite": stalagmite(),
        "cave_shroom": cave_shroom(),
        "bones": bones(),
        "stalactite_a": stalactite(10, 22, 1),
        "stalactite_b": stalactite(7, 14, 2),
    }
    for k, img in props.items():
        save(img, f"deco/{k}.png")
    glim = glimmer_frames()
    save(sheet(glim), "sprites/glimmer.png")
    wick = wickway_frames()
    save(sheet(wick), "sprites/wickway.png")

    # ---- previews
    save_preview(ground, "cave_ground_atlas.png", 3)
    backdrop = compose_backdrop(layers, scroll=40)
    save_preview(backdrop, "cave_bg.png", 2)
    tw = max(len(r) for r in TEST)
    rows = [r.replace("G", ".").ljust(tw, "#") for r in TEST]
    w = len(rows[0]) * T
    bd = new(w, len(rows) * T, (0, 0, 0, 255))
    bd.alpha_composite(compose_backdrop(layers, 40), (0, 0))
    bd.alpha_composite(compose_backdrop(layers, 520).crop((0, 0, w - W, H)), (W, 0))
    placed = [
        (props["crystal_big"], 22, 11, False), (props["crystal_small"], 7, 13, False),
        (props["stalagmite"], 4, 13, False), (props["cave_shroom"], 25, 11, False),
        (props["bones"], 18, 11, False), (props["crystal_violet"], 11, 7, False),
        (props["stalactite_a"], 16, 1, True), (props["stalactite_b"], 10, 1, True),
        (props["stalactite_a"], 26, 1, True), (wick[1], 31, 8, False),
    ]
    scene = compose_scene(ground, wall, bd, rows, placed)
    for i, x in enumerate(range(24, 28)):
        scene.alpha_composite(glim[1 + i % 3] if x < 26 else glim[0], (x * T, 10 * T))
    save_preview(scene, "cave_test.png", 2)
    lit = ingame(scene, [(8 * T + 10, 13 * T + 10, 96, (1.0, 0.78, 0.5), 0.75),
                         (31 * T + 8, 9 * T + 2, 80, (1.0, 0.66, 0.35), 0.8)])
    save_preview(lit, "cave_test_ingame.png", 2)

    items = list(props.values()) + glim
    sheet_img = new(sum(i.width + 4 for i in items) + sum(f.width + 2 for f in wick) + 4, 60)
    x = 2
    for img in items:
        sheet_img.alpha_composite(img, (x, 58 - img.height))
        x += img.width + 4
    for f in wick:
        sheet_img.alpha_composite(f, (x, 10))
        x += f.width + 2
    save_preview(sheet_img, "cave_props.png", 4)


if __name__ == "__main__":
    build()
