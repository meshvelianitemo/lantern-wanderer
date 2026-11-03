"""Side chapter - Under the Lake: the Starwell, a Keeper observatory sealed in
an air bubble at the bottom of the black lake.

Run `python starwell.py` to (re)generate:

  tiles/starwell_ground.png  256x288  tiles.py atlas layout; pale blue-grey dressed stone
                                      with a polished brass cap, weed sprigs and glass
                                      glints (row 16 cols 0-3), waterweed + drips hanging
                                      (cols 4-7), brass star-lattice catwalk (row 17)
  tiles/starwell_wall.png    256x288  dark blue glass mosaic panes, faint stars, brass ribs
  bg/starwell_base.png       480x270  lake-black gradient, caustics from far above (factor 0)
  bg/starwell_far.png        640x270  the great dome: pointed glass bays, the lake beyond, light shafts
  bg/starwell_mid.png        640x270  lantern-fish with glowing lures, kelp, bubble columns
  bg/starwell_near.png       640x270  brass pipes and brackets along the ceiling (top only)
  deco/telescope, star_chart, globe, book_stack, porthole, bubble_vent, orrery_ring (bottom-centre)
  deco/kelp                           (top-anchored, flush top row)
  sprites/caster_boat 40x12, caster_fish 32x10, caster_bird 36x10, caster_moon 28x10
                            tin shadow-play plates, one frame each, flat top edge, rivet at top centre
  sprites/starlamp.png      32x32   2 frames 16x32: 0 unlit, 1 lit (glass centre 24px above the bottom)
  sprites/orrery_sun.png    64x16   4 frames 16x16: 0 unlit, 1-3 lit flicker (centred)
  sprites/great_orrery.png  560x96  5 frames 112x96: 0 cold, 1-4 lit turning loop (bottom-centre)

Backdrop scene: scenes/backdrops/starwell.tscn. Previews: _preview/starwell_*.png
"""
import math
import os

from bg import periodic_noise
from drowned import masonry
from envkit import (Mask, compose_backdrop, compose_scene, deco_rows_preview, ingame, pad_rows,
                    props_sheet, rim_light, scene_backdrop, shade_mask, vgrad, H, W)
from pix import (BONE, FIRE, GLOW, INK, CLEAR, ROOT, STONE, WOOD, dith, hexc, new, outline, paste,
                 ramp_at, rng, save, save_preview, sheet)
from tiles import PERIOD, T, build_terrain

SW_STONE = [hexc(c) for c in ("#121826", "#1f293b", "#314058", "#475a76", "#677d99", "#90a6bf")]
SW_WALL = [hexc(c) for c in ("#060912", "#0b1120", "#111a30", "#182540", "#203152", "#2b4068")]
BRASS6 = [hexc(c) for c in ("#24160f", "#3a2418", "#6e4a2a", "#a87a3c", "#d9ad5c", "#f4dc96")]
TIN = [hexc(c) for c in ("#2a2219", "#4f4433", "#7c6a4a", "#a88f5c", "#d0b67c", "#efdfa8")]
WEED = [hexc(c) for c in ("#061412", "#0b2220", "#12332e", "#1b4840", "#2a6152", "#47806a")]
GLASS = [hexc(c) for c in ("#0d1424", "#16233c", "#22385a", "#36557e", "#5a80aa", "#a8c8e8")]
RIB = [hexc(c) for c in ("#1e1810", "#33291b", "#4d3f29")]
NAVY = [hexc(c) for c in ("#0b1226", "#14204a", "#22346e", "#34508f", "#5072b0")]
STAR_DIM = hexc("#7e98c8")
STAR = hexc("#d6e4ff")
STAR_GOLD = hexc("#f4e6a8")
DROP = hexc("#9fc4e0")
LAKE = [hexc(c) for c in ("#020409", "#040812", "#060e1c", "#091526", "#0c1d33", "#112742")]
CAUSTIC = (hexc("#14294a"), hexc("#1d3a5e"))

WALL_TINT = (0.5, 0.56, 0.68)


# ------------------------------------------------------------------ tiles ---

def stone_tex(seed, ramp, mortar, light_bias=0):
    """Dressed blue-grey blocks, a few carved four-point stars."""
    img, mort = masonry(seed, ramp, mortar, light_bias, course=8, min_w=12, max_w=22, glyphs=0.0)
    p = img.load()
    r = rng(seed + 5)
    placed = 0
    while placed < 6:
        x, y = r.randrange(PERIOD), r.randrange(PERIOD)
        near = [((x + dx) % PERIOD, (y + dy) % PERIOD) for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2)]
        if any(mort[yy][xx] for (xx, yy) in near):
            continue
        for dx, dy in ((0, -2), (0, -1), (0, 1), (0, 2), (-2, 0), (-1, 0), (1, 0), (2, 0)):
            p[(x + dx) % PERIOD, (y + dy) % PERIOD] = ramp[1] if abs(dx) + abs(dy) == 2 else ramp[2]
        p[x, y] = ramp[4]
        placed += 1
    return img, mort


def brass_profile():
    return [0] * PERIOD, [3] * PERIOD


def stone_fringe(r, ph):
    f = new(T, T)
    p = f.load()
    x = r.randint(0, 3)
    while x < T:
        roll = r.random()
        if roll < 0.2:  # a sprig of pale waterweed
            h = r.randint(2, 5)
            for y in range(h):
                xx = min(T - 1, x + (1 if y >= 3 else 0))
                p[xx, T - 1 - y] = WEED[3] if y < h - 1 else WEED[5]
        elif roll < 0.3:  # pebble
            p[x, T - 1] = SW_STONE[3]
            if x + 1 < T:
                p[x + 1, T - 1] = SW_STONE[2]
            p[x, T - 2] = SW_STONE[4]
        elif roll < 0.34:  # a chip of dome glass catching the light
            p[x, T - 1] = GLASS[4]
            p[x, T - 2] = GLASS[5]
        x += r.choice((2, 3, 4))
    return f


def weed_hang(r, ph):
    f = new(T, T)
    p = f.load()
    used = set()
    for _ in range(r.randint(1, 3)):
        x = r.randint(1, 14)
        if x in used:
            continue
        used.update((x - 1, x, x + 1))
        ln = r.randint(4, 14)
        for y in range(ln):
            xx = min(T - 1, x + (1 if (y // 4) % 2 and y > 2 else 0))
            p[xx, y] = WEED[2] if y < ln - 3 else (WEED[3] if y < ln - 1 else WEED[4])
        if ln + 2 < T and r.random() < 0.5:
            p[x, ln + 1] = DROP
    if r.random() < 0.45:
        x = r.randint(2, 13)
        if x not in used:
            p[x, 0] = SW_STONE[2]
            p[x, 2] = DROP
    return f


def catwalk(i):
    """Brass catwalk: two rails with a pierced star lattice between them."""
    f = new(T, T)
    p = f.load()
    for x in range(T):
        k = x % 8
        p[x, 0] = BRASS6[5] if k == 3 else BRASS6[4]
        p[x, 1] = BRASS6[5] if k == 6 else BRASS6[3]
        p[x, 4] = BRASS6[2]
        p[x, 5] = BRASS6[0]
        if k == 0:
            p[x, 2] = BRASS6[2]
            p[x, 3] = BRASS6[1]
        elif k == 4:
            p[x, 2] = BRASS6[3]
            p[x, 3] = BRASS6[2]
        elif k in (3, 5):
            p[x, 3] = BRASS6[2]
    if i in (0, 3):
        e = 0 if i == 0 else T - 1
        s = 1 if i == 0 else -1
        for y in range(6):
            p[e, y] = BRASS6[1]
        p[e, 0] = CLEAR
        for k in range(5):  # a strut down to the wall
            p[e + s * (2 + k), 6 + k] = BRASS6[3]
            p[e + s * (2 + k), 7 + k] = BRASS6[1]
        for y in range(6, 11):
            p[e + s, y] = BRASS6[2]
    return f


def glass_panes(seed, ramp, mortar, light_bias=0):
    """32px glass panes in brass ribs; each pane a faint mosaic sprinkled with stars."""
    r = rng(seed)
    img = new(PERIOD, PERIOD)
    p = img.load()
    mort = [[False] * PERIOD for _ in range(PERIOD)]
    shades = {}
    for y in range(PERIOD):
        for x in range(PERIOD):
            px_, py_ = x % 32, y % 32
            if px_ < 2 or py_ < 2:
                if px_ < 2 and py_ < 2:
                    c = RIB[2] if (px_, py_) == (0, 0) else RIB[1]
                elif px_ < 2:
                    c = RIB[1] if px_ == 0 else RIB[0]
                    if px_ == 0 and py_ % 8 == 5:
                        c = RIB[2]
                else:
                    c = RIB[1] if py_ == 0 else RIB[0]
                    if py_ == 0 and px_ % 8 == 5:
                        c = RIB[2]
                p[x, y] = c
                continue
            tx, ty = (px_ - 2) // 5, (py_ - 2) // 5
            ix, iy = (px_ - 2) % 5, (py_ - 2) % 5
            key = (x // 32, y // 32, tx, ty)
            if key not in shades:
                shades[key] = r.choice((2, 3, 3, 3, 4))
            if ix == 4 or iy == 4:
                p[x, y] = ramp[1] if dith(x, y, 0.7) else ramp[2]
                continue
            s = shades[key]
            if py_ < 12 and dith(x, y, (12 - py_) / 30.0):  # light from far above
                s += 1
            p[x, y] = ramp[min(5, s)]
    # faint stars set into the glass
    for _ in range(26):
        x, y = r.randrange(PERIOD), r.randrange(PERIOD)
        if x % 32 < 2 or y % 32 < 2:
            continue
        p[x, y] = STAR_DIM if r.random() < 0.75 else STAR
    for (x, y) in ((12, 44), (47, 15)):
        p[x, y] = STAR
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p[x + dx, y + dy] = STAR_DIM
    return img, mort


def build_tiles():
    ground = build_terrain("starwell_ground", SW_STONE, (SW_STONE[0], SW_STONE[1]), seed=71,
                           moss=BRASS6, profile=brass_profile(), fringe=stone_fringe, hang=weed_hang,
                           texture=stone_tex, platform=catwalk)
    wall = build_terrain("starwell_wall", SW_WALL, (SW_WALL[0], SW_WALL[0]), seed=72, grass=False,
                         texture=glass_panes)
    return ground, wall


# --------------------------------------------------------------- backdrop ---

def starwell_base():
    img = new(W, H)
    vgrad(img, LAKE, [(0, 0.95), (60, 0.72), (140, 0.42), (220, 0.18), (270, 0.06)])
    p = img.load()
    for y in range(0, 120):  # caustics: a wobbling net of light from the surface far above
        fade = 1 - y / 120
        for x in range(W):
            v = math.sin(x * 0.061 + math.sin(y * 0.13 + x * 0.011) * 2.2) + \
                math.sin(y * 0.093 - x * 0.023 + math.sin(x * 0.047) * 1.7)
            if abs(v) < 0.2 and dith(x, y, fade * 0.85):
                p[x, y] = CAUSTIC[1] if fade > 0.55 else CAUSTIC[0]
    r = rng(171)
    for _ in range(80):
        x, y = r.randrange(W), r.randrange(H)
        p[x, y] = hexc("#22406a") if r.random() < 0.3 else hexc("#132640")
    return img


def dome(seed, w=640):
    """Inside the great glass dome: tall pointed bays between brass-bound ribs."""
    img = new(w, H)
    p = img.load()
    r = rng(seed)
    body, rim, joint = hexc("#0a111f"), hexc("#16243c"), hexc("#060b15")
    brass, brass_hi = hexc("#2a2318"), hexc("#463a28")
    mull, shaft = hexc("#0c1628"), hexc("#14294a")
    n = 4
    gap = w / n
    rw = 14
    half = gap / 2 - rw / 2
    ys, sill = 104, 232
    R = half * 1.25
    m = Mask(w, H)
    for i in range(n):
        for off in (0, w, -w):
            cx = i * gap + off
            m.rect(cx - rw / 2, 0, cx + rw / 2, H - 1)
    arch_y = {}
    for x in range(w):
        k = round((x - gap / 2) / gap)
        acx = k * gap + gap / 2
        dx = x - acx
        if abs(dx) <= half:
            c = acx - (R - half) if dx >= 0 else acx + (R - half)
            y = ys - math.sqrt(max(0.0, R * R - (x - c) ** 2))
            arch_y[x % w] = y
            m.rect(x % w, 0, x % w, int(y))
    f = periodic_noise(seed + 3, w, ((3, 1.0), (7, 0.5), (13, 0.3)))
    for x in range(w):
        m.rect(x, sill, x, H - 1)
    # light shafts falling through the panes (drawn first, only where open)
    for _ in range(7):
        x0 = r.uniform(0, w)
        sw = r.uniform(8, 20)
        for y in range(H):
            xc = x0 + y * 0.22
            for x in range(int(xc - sw / 2), int(xc + sw / 2)):
                xx = x % w
                if not m.get(xx, y) and dith(x, y, (1 - y / H) * 0.32 * (1 - abs(x - xc) / (sw / 2))):
                    p[xx, y] = shaft
    # far lake floor seen through the glass
    for x in range(w):
        top = int(214 + 9 * f(x))
        for y in range(top, sill):
            if not m.get(x, y):
                p[x, y] = hexc("#070e1a")
    # pane leading: a mullion down each bay and transoms across
    for i in range(n):
        acx = int(i * gap + gap / 2)
        for y in range(int(arch_y.get(acx % w, 20)) + 1, sill):
            p[acx % w, y] = mull
        for x in range(int(acx - half), int(acx + half) + 1):
            for ty in (150, 196):
                if not m.get(x % w, ty):
                    p[x % w, ty] = mull
            for qx in (int(acx - half / 2), int(acx + half / 2)):
                if x == qx:
                    for y in range(int(arch_y.get(x % w, 40)) + 1, sill):
                        if (y // 2) % 2 == 0 or y > 150:
                            p[x % w, y] = mull
    for y in range(H):
        for x in range(w):
            if m.m[y][x]:
                p[x, y] = body
    rim_light(img, rim)
    # arch moulding and brass bands on the ribs
    for x, y in arch_y.items():
        yy = int(y)
        if 0 <= yy < H:
            p[x, yy] = rim
            if yy - 3 >= 0 and m.get(x, yy - 3):
                p[x, yy - 3] = joint
    for i in range(n):
        cx = i * gap
        for by in range(20, sill, 46):
            for x in range(int(cx - rw / 2), int(cx + rw / 2) + 1):
                for yy in (by, by + 1):
                    if m.get(x % w, yy):
                        p[x % w, yy] = brass_hi if yy == by else brass
            p[int(cx) % w, by + 3] = brass_hi  # rivet
        for y in range(0, sill):
            xx = int(cx - rw / 2 + 3) % w
            if m.get(xx, y) and p[xx, y] == body:
                p[xx, y] = joint
    for x in range(w):  # the sill
        p[x, sill] = rim
        p[x, sill + 1] = brass if x % 9 else brass_hi
    return img


def lantern_fish(p, w, x0, y0, ln, facing, r, lure_col):
    """A deep-water fish silhouette with a glowing lure on a stalk."""
    body, rim, eye = hexc("#040912"), hexc("#0c182a"), hexc("#29486a")
    m = Mask(w + 80, H)
    hgt = ln * 0.42
    cx = x0 + ln * 0.5
    m.ellipse(cx, y0, ln * 0.42, hgt * 0.5)
    tail = x0 + (0 if facing > 0 else ln)
    sgn = -facing
    m.poly([(tail + sgn * 1, y0), (tail + sgn * ln * 0.28, y0 - hgt * 0.5), (tail + sgn * ln * 0.22, y0),
            (tail + sgn * ln * 0.28, y0 + hgt * 0.5)])
    head = x0 + (ln if facing > 0 else 0)
    m.poly([(head - facing * ln * 0.25, y0), (head + facing * ln * 0.06, y0 + hgt * 0.15),
            (head - facing * ln * 0.1, y0 + hgt * 0.5)])  # underbite
    pts = []
    for yy in range(H):
        for xx in range(m.w):
            if m.m[yy][xx]:
                pts.append((xx, yy))
    for (xx, yy) in pts:
        up = not m.get(xx, yy - 1)
        p[xx % w, yy] = rim if up and dith(xx, yy, 0.7) else body
    ex = int(head - facing * ln * 0.18)
    p[ex % w, int(y0 - hgt * 0.12)] = eye
    # lure stalk curling forward from the forehead, and the light
    sx, sy = head - facing * ln * 0.2, y0 - hgt * 0.42
    lx, ly = sx, sy
    for k in range(int(ln * 0.45)):
        t = k / (ln * 0.45)
        lx = sx + facing * t * ln * 0.38
        ly = sy - math.sin(t * math.pi * 0.9) * ln * 0.22
        p[int(lx) % w, int(ly)] = rim
    for yy in range(int(ly) - 4, int(ly) + 5):
        for xx in range(int(lx) - 4, int(lx) + 5):
            d = math.hypot(xx - lx, yy - ly)
            if 0 <= yy < H and d < 4.2 and dith(xx, yy, (1 - d / 4.2) * 0.6):
                p[xx % w, yy] = hexc("#1a3050")
    p[int(lx) % w, int(ly)] = lure_col
    p[int(lx + 1) % w, int(ly)] = hexc("#6a88a8")


def deep_mid(seed, w=640):
    img = new(w, H)
    p = img.load()
    r = rng(seed)
    body, rim = hexc("#040910"), hexc("#0a1824")
    f = periodic_noise(seed + 1, w, ((3, 1.0), (7, 0.5), (13, 0.3)))
    # silt floor and kelp forest
    for x in range(w):
        top = int(254 + 6 * f(x))
        for y in range(top, H):
            p[x, y] = body
    for i in range(16):
        bx = r.uniform(0, w)
        hgt = r.uniform(40, 150)
        ph = r.uniform(0, math.tau)
        base = 256
        for k in range(int(hgt)):
            y = base - k
            sway = math.sin(k * 0.06 + ph) * (k / hgt) * 7
            x = int(bx + sway)
            p[x % w, y] = body
            p[(x + 1) % w, y] = rim if dith(x, y, 0.5) else body
            if k % 11 == 5 and k < hgt - 4:  # a blade
                side = 1 if (k // 11) % 2 else -1
                for b in range(1, 5):
                    p[(x + side * b) % w, y - b // 2] = body if b < 4 else rim
    # lantern-fish at different depths
    for i in range(6):
        ln = r.uniform(14, 30)
        x0 = (i + r.uniform(0.1, 0.7)) * w / 6
        y0 = r.uniform(50, 200)
        lure = hexc("#ffe7a3") if r.random() < 0.5 else hexc("#bfe8ff")
        lantern_fish(p, w, x0, y0, ln, 1 if r.random() < 0.6 else -1, r, lure)
    # bubble columns rising
    for i in range(5):
        bx = r.uniform(0, w)
        y = r.uniform(180, 250)
        while y > 10:
            rad = 1 if y < 120 else (1 if r.random() < 0.5 else 2)
            x = int(bx + math.sin(y * 0.08) * 3)
            for (dx, dy) in ((0, -rad), (0, rad), (-rad, 0), (rad, 0)):
                if 0 <= int(y) + dy < H:
                    p[(x + dx) % w, int(y) + dy] = hexc("#1c3656")
            if rad == 2:
                p[(x - 1) % w, int(y) - 1] = hexc("#2d5078")
            y -= r.uniform(9, 22)
    return img


def pipes_near(seed, w=640):
    img = new(w, H)
    p = img.load()
    r = rng(seed)
    body, rim, dark = hexc("#070910"), hexc("#2c2418"), hexc("#030407")
    weed = hexc("#081614")
    for x in range(w):
        for y in range(0, 3):
            p[x, y] = dark
        for (y0, th) in ((3, 5), (10, 4)):
            for k in range(th):
                p[x, y0 + k] = rim if k == 0 else (dark if k == th - 1 else body)
    for x in range(0, w, 32):  # pipe collars
        for y in range(2, 15):
            p[x % w, y] = rim if y in (3, 10) else body
            p[(x + 1) % w, y] = body
            p[(x + 2) % w, y] = dark
    for x in range(16, w, 64):  # brackets down from the ceiling
        for k in range(10):
            p[(x + k) % w, 14 + k // 2] = body
            p[(x - k) % w, 14 + k // 2] = body
        for y in range(14, 22):
            p[x % w, y] = body
            p[(x + 1) % w, y] = rim if y % 3 == 0 else body
    for i in range(4):  # vertical pipes dropping down, ending in a valve wheel
        x = int((i + r.uniform(0.2, 0.8)) * w / 4)
        ln = int(r.uniform(40, 120))
        for y in range(14, 14 + ln):
            p[x % w, y] = rim
            p[(x + 1) % w, y] = body
            p[(x + 2) % w, y] = body
            p[(x + 3) % w, y] = dark
            if (y - 14) % 24 == 20:
                for dx in range(-1, 5):
                    p[(x + dx) % w, y] = rim
                    p[(x + dx) % w, y + 1] = body
        cy = 14 + ln + 3
        for a in range(0, 360, 20):
            t = math.radians(a)
            p[int(x + 1.5 + math.cos(t) * 4) % w, int(cy + math.sin(t) * 4)] = rim if a < 180 else body
        for dx, dy in ((1, 0), (2, 0), (1, 1), (2, 1), (0, 0), (3, 1)):
            p[(x + dx) % w, cy + dy - 1] = body
    for _ in range(40):  # weed trailing off the pipes
        x0 = r.uniform(0, w)
        ln = int(r.uniform(4, 22))
        for y in range(14, 14 + ln):
            x = int(x0 + math.sin(y * 0.3 + x0) * 1.2)
            p[x % w, y] = weed
    return img


def build_backdrop():
    layers = {
        "base": starwell_base(),
        "far": dome(91),
        "mid": deep_mid(92),
        "near": pipes_near(93),
    }
    for name, img in layers.items():
        save(img, f"bg/starwell_{name}.png")
    scene = os.path.join(ROOT, "scenes", "backdrops", "starwell.tscn")
    with open(scene, "w", newline="\n") as fh:
        fh.write(TSCN)
    return layers


TSCN = """[gd_scene format=3]

[ext_resource type="Script" path="res://scripts/parallax_layer.gd" id="1_parallax"]
[ext_resource type="Texture2D" path="res://assets/bg/starwell_base.png" id="2_base"]
[ext_resource type="Texture2D" path="res://assets/bg/starwell_far.png" id="3_far"]
[ext_resource type="Texture2D" path="res://assets/bg/starwell_mid.png" id="4_mid"]
[ext_resource type="Texture2D" path="res://assets/bg/starwell_near.png" id="5_near"]

[node name="Backdrop" type="Node2D"]
z_index = -100

[node name="Base" type="Sprite2D" parent="."]
texture = ExtResource("2_base")
script = ExtResource("1_parallax")
factor = Vector2(0, 0)

[node name="Far" type="Sprite2D" parent="."]
texture = ExtResource("3_far")
script = ExtResource("1_parallax")
factor = Vector2(0.1, 0.05)
fill_below = Color(0.039, 0.067, 0.122, 1)

[node name="Mid" type="Sprite2D" parent="."]
texture = ExtResource("4_mid")
script = ExtResource("1_parallax")
factor = Vector2(0.25, 0.1)
screen_y = 6.0
fill_below = Color(0.016, 0.035, 0.063, 1)

[node name="Near" type="Sprite2D" parent="."]
texture = ExtResource("5_near")
script = ExtResource("1_parallax")
factor = Vector2(0.45, 0.18)
screen_y = -6.0
"""


# ------------------------------------------------------------------ props ---

def line(p, x0, y0, x1, y1, col):
    n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
    for i in range(n + 1):
        t = i / n
        p[int(round(x0 + (x1 - x0) * t)), int(round(y0 + (y1 - y0) * t))] = col


def telescope():
    w, h = 22, 30
    img = new(w, h)
    p = img.load()
    line(p, 11, 18, 12, 28, WOOD[1])           # back leg
    line(p, 11, 18, 3, 28, WOOD[3])
    line(p, 12, 18, 19, 28, WOOD[3])
    for (x, y) in ((4, 28), (18, 28)):
        p[x, y] = WOOD[2]
    for y in range(12, 19):                    # mount post
        p[11, y] = BRASS6[3]
        p[12, y] = BRASS6[2]
    m = Mask(w, h)
    m.line(4, 15, 17, 5, width=4)
    m.ellipse(17.5, 4.5, 2.6, 3.2)              # objective end
    m.rect(2, 15, 4, 17)                        # eyepiece
    tube = shade_mask(m, BRASS6[1:6], lo=0.15, hi=0.9)
    tp = tube.load()
    ax, ay = 13.0, -10.0                        # axis direction (normalised below)
    al = math.hypot(ax, ay)
    for y in range(h):
        for x in range(w):
            if not tp[x, y][3]:
                continue
            t = ((x - 4) * ax + (y - 15) * ay) / (al * al)
            if 0.28 < t < 0.33 or 0.62 < t < 0.67:
                tp[x, y] = BRASS6[1]
    tp[18, 3] = GLASS[5]
    tp[19, 4] = GLASS[4]
    paste(img, tube, 0, 0)
    p = img.load()
    p[11, 11] = BRASS6[5]
    p[12, 11] = BRASS6[3]
    return outline(img, INK)


def star_chart():
    w, h = 18, 24
    img = new(w, h)
    p = img.load()
    line(p, 9, 2, 13, 22, WOOD[1])
    line(p, 8, 2, 2, 22, WOOD[3])
    line(p, 10, 2, 15, 22, WOOD[3])
    for y in range(3, 16):
        for x in range(1, 17):
            edge = x in (1, 16) or y in (3, 15)
            p[x, y] = BONE[2] if edge else NAVY[1]
    pts = [(4, 6), (7, 5), (10, 7), (13, 6), (11, 11), (5, 12)]
    for a, b in ((0, 1), (1, 2), (2, 3), (2, 4), (4, 5)):
        (x0, y0), (x1, y1) = pts[a], pts[b]
        n = max(abs(x1 - x0), abs(y1 - y0))
        for i in range(n + 1):
            p[round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)] = NAVY[3]
    for (x, y) in pts:
        p[x, y] = STAR_GOLD
    for (x, y) in ((3, 9), (14, 9), (8, 13), (13, 13)):
        p[x, y] = STAR_DIM
    for x in range(1, 17):
        p[x, 16] = WOOD[4]
        p[x, 17] = WOOD[2]
    return outline(img, INK)


def globe():
    w, h = 16, 20
    m = Mask(w, h)
    m.ellipse(8, 8, 5.2, 5.2)
    img = shade_mask(m, NAVY, lo=0.1, hi=0.85)
    p = img.load()
    for x in range(3, 14):
        if p[x, 8][3]:
            p[x, 8] = BRASS6[2]
    for (x, y) in ((6, 5), (9, 4), (10, 10), (5, 11), (11, 6)):
        p[x, y] = STAR_GOLD
    for y in range(h):                          # brass meridian half-ring
        for x in range(w):
            d = math.hypot(x + 0.5 - 8, y + 0.5 - 8)
            if 6.0 <= d < 7.0 and x <= 8:
                p[x, y] = BRASS6[4] if y < 8 else BRASS6[3]
    for y in range(14, 17):
        p[7, y] = BRASS6[3]
        p[8, y] = BRASS6[2]
    for x in range(4, 12):
        p[x, 17] = BRASS6[4] if x < 7 else BRASS6[3]
        p[x, 18] = BRASS6[2]
    return outline(img, INK)


def book_stack():
    w, h = 16, 10
    img = new(w, h)
    p = img.load()
    books = [  # (x0, x1, y0, y1, cover, cover_hi)
        (1, 14, 6, 8, hexc("#2a3a6a"), hexc("#3c5288")),
        (2, 12, 3, 5, hexc("#6a2a32"), hexc("#8a3a40")),
        (3, 13, 1, 2, hexc("#2a4a3a"), hexc("#3a6a4c")),
    ]
    for (x0, x1, y0, y1, c, hi) in books:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if x >= x1 - 1:
                    p[x, y] = BONE[3] if (y + x) % 2 else BONE[2]  # page edges
                else:
                    p[x, y] = hi if y == y0 else c
        for x in (x0 + 2, x0 + 5):
            for y in range(y0, y1 + 1):
                if p[x, y] in (c, hi):
                    p[x, y] = BRASS6[3] if y == y0 else BRASS6[2]
    return outline(img, INK)


def porthole():
    img = new(32, 32)
    p = img.load()
    water = [hexc(c) for c in ("#04090f", "#071222", "#0b1b33", "#102848")]
    for y in range(32):
        for x in range(32):
            dx, dy = x + 0.5 - 16, y + 0.5 - 16
            d = math.hypot(dx, dy)
            if d <= 14.5:
                if d > 10.5:
                    a = math.atan2(dy, dx)
                    lit = -math.cos(a + math.pi / 4)
                    if d < 11.3:
                        p[x, y] = BRASS6[0]
                    else:
                        p[x, y] = ramp_at(BRASS6[1:6], 0.5 + 0.4 * lit, x, y)
                else:
                    p[x, y] = ramp_at(water, 1.0 - (y - 5) / 24.0, x, y)
            elif d <= 15.5:
                p[x, y] = INK
    for k in range(8):
        a = k * math.pi / 4 + math.pi / 8
        bx, by = int(16 + math.cos(a) * 12.8), int(16 + math.sin(a) * 12.8)
        p[bx, by] = BRASS6[5]
        p[bx + 1, by + 1] = BRASS6[1]
    fm = Mask(32, 32)                            # a faint fish passing outside
    fm.ellipse(14, 18, 4.5, 2.2)
    fm.poly([(9.5, 18), (7, 16), (7, 20)])
    for y in range(32):
        for x in range(32):
            if fm.m[y][x]:
                p[x, y] = hexc("#030710")
    p[17, 17] = hexc("#29486a")
    for (x, y) in ((20, 12), (21, 9), (20, 7)):
        p[x, y] = hexc("#2a5078")
    for (x, y, c) in ((9, 9, GLASS[4]), (10, 8, GLASS[4]), (8, 10, GLASS[3]), (11, 7, GLASS[3]),
                      (9, 12, GLASS[3]), (12, 9, GLASS[3])):
        p[x, y] = c
    p[10, 9] = GLASS[5]
    return img


def kelp():
    img = new(10, 29)
    p = img.load()
    for (x0, ln, ph) in ((2, 27, 0.0), (5, 20, 1.7), (7, 13, 3.1)):
        for y in range(ln):
            x = int(round(x0 + math.sin(y * 0.35 + ph) * 1.0))
            p[x, y] = WEED[2] if y < ln - 4 else (WEED[3] if y < ln - 1 else WEED[4])
            if y % 6 == 3 and y < ln - 3:
                side = 1 if (y // 6) % 2 else -1
                for b in (1, 2):
                    if 0 <= x + side * b < 10:
                        p[x + side * b, y + b - 1] = WEED[3] if b == 1 else WEED[4]
    img = outline(img, INK).crop((0, 0, 10, 28))
    q = img.load()
    for x in range(10):
        if q[x, 0] == INK:
            q[x, 0] = CLEAR
    return img


def bubble_vent():
    rows = [
        "...oooooo...",
        "..obdbdbdo..",
        ".obbdbdbdbbo",
        "obccccccccco",
        "obbbbbbbbbbo",
        "oooooooooooo",
    ]
    key = {"o": INK, "b": BRASS6[3], "c": BRASS6[4], "d": hexc("#0a0806")}
    img = new(12, 6)
    p = img.load()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in key:
                p[x, y] = key[ch]
    return img


def orrery_ring():
    w = h = 40
    cx, cy = 20, 19.5
    m = Mask(w, h)
    for y in range(h):
        for x in range(w):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            d = math.hypot(dx / 17.5, dy / 18.0)
            a = math.atan2(dy, dx)
            if 0.85 <= d <= 1.0 and not (-1.15 < a < -0.62):
                m.set(x, y)
    img = shade_mask(m, BRASS6[1:6], lo=0.2, hi=0.85)
    p = img.load()
    for k in range(24):  # engraved degree ticks
        a = k * math.tau / 24
        x, y = int(cx + math.cos(a) * 16.2), int(cy + math.sin(a) * 16.8)
        if p[x, y][3]:
            p[x, y] = BRASS6[1]
    # a little planet still riding its arm inside the ring
    a = 2.4
    sx, sy = cx + math.cos(a) * 15, cy + math.sin(a) * 15.5
    px_, py_ = cx + math.cos(a) * 8, cy + math.sin(a) * 8.5
    line(p, sx, sy, px_, py_, BRASS6[2])
    pm = Mask(w, h)
    pm.ellipse(px_, py_, 2.6, 2.6)
    planet = shade_mask(pm, [hexc(c) for c in ("#4a1018", "#8a2f26", "#c65a34", "#ef8a5f")], lo=0.1, hi=0.9)
    img.alpha_composite(planet)
    return outline(img, INK)


# --------------------------------------------------------------- mechanism ---

def tin_plate(m, w, h, holes=(), emboss=(), rivet=None):
    """A flat tin shadow-play cut-out: embossed top edge, darker rim, pierced holes."""
    inner = new(w, h)
    p = inner.load()
    for y in range(h):
        for x in range(w):
            if m.get(x, y):
                p[x, y] = TIN[3]
    q = inner.copy().load()
    for y in range(h):
        for x in range(w):
            if not q[x, y][3]:
                continue
            up = y == 0 or not q[x, y - 1][3]
            down = y == h - 1 or not q[x, y + 1][3]
            left = x == 0 or not q[x - 1, y][3]
            if up:
                p[x, y] = TIN[4] if x % 6 else TIN[5]
            elif down:
                p[x, y] = TIN[2]
            elif left:
                p[x, y] = TIN[4]
    for (x, y, c) in emboss:
        p[x, y] = c
    img = new(w + 2, h + 2)
    img.alpha_composite(inner, (1, 1))
    img = outline(img, TIN[1])
    q = img.load()
    for (x, y) in holes:
        q[x + 1, y + 1] = CLEAR
    if rivet is not None:
        q[rivet + 1, 1] = TIN[5]
        q[rivet + 1, 2] = TIN[1]
        q[rivet + 2, 2] = TIN[2]
    return img


def caster_boat():
    w, h = 38, 10
    m = Mask(w, h)
    m.rect(0, 0, 37, 1)
    for y in range(2, h):
        xl = int((y - 2) * 0.65)
        xr = 37 - int((y - 1) * 1.1)
        m.rect(xl, y, xr, y)
    holes = [(x, y) for x0 in (10, 18, 26) for (x, y) in ((x0, 4), (x0 + 1, 4), (x0, 5), (x0 + 1, 5))]
    emboss = [(x, 7, TIN[2]) for x in range(4, 30)] + [(x, 2, TIN[2]) for x in range(1, 36)]
    return tin_plate(m, w, h, holes, emboss, rivet=18)


def caster_fish():
    w, h = 30, 8
    m = Mask(w, h)
    m.poly([(0, 0), (7, 0), (7, 8), (0, 8), (3.2, 4)])        # forked tail
    for x in range(6, 30):
        bottom = 2.6 + 4.9 * math.sin(math.pi * min(1.0, (x - 5) / 23.0))
        top = 0 if x < 27 else (x - 26) * 0.9
        m.rect(x, int(top), x, int(min(7, bottom)))
    holes = [(25, 2)]
    emboss = [(22, y, TIN[2]) for y in range(2, 6)] + [(x, 4, TIN[4]) for x in (11, 14, 17)] + \
             [(x, 5, TIN[2]) for x in (12, 15, 18)]
    return tin_plate(m, w, h, holes, emboss, rivet=15)


def caster_bird():
    w, h = 34, 8
    m = Mask(w, h)
    m.rect(0, 0, 33, 1)                                        # wings, straight across
    for x in range(0, 34):
        if x < 12 or x > 21:
            if x % 3 != 2:
                m.set(x, 2)
            if x % 3 == 0 and 2 < x < 31:
                m.set(x, 3)
    m.ellipse(17, 3.5, 6, 3)                                   # body
    m.ellipse(24, 3, 2.2, 2.2)                                 # head
    m.rect(26, 3, 28, 3)                                       # beak
    m.poly([(12.5, 4), (6, 7.9), (11.5, 7.9)])                  # tail fan
    holes = [(24, 2)]
    emboss = [(x, 4, TIN[2]) for x in range(14, 21)] + [(15, 2, TIN[4]), (18, 2, TIN[4])]
    return tin_plate(m, w, h, holes, emboss, rivet=17)


def caster_moon():
    w, h = 26, 8
    m = Mask(w, h)
    m.rect(0, 0, 25, 0)                                        # the thin bar it hangs from
    for y in range(0, h):
        for x in range(w):
            fx, fy = x + 0.5, y + 0.5
            outer = ((fx - 13) / 13.0) ** 2 + (fy / 8.0) ** 2 <= 1.0
            inner = ((fx - 13) / 10.2) ** 2 + ((fy + 1.0) / 6.6) ** 2 <= 1.0
            if outer and not inner:
                m.set(x, y)
    # a sleepy closed eye on the moon's cheek
    emboss = [(5, 5, TIN[1]), (6, 6, TIN[1]), (7, 6, TIN[1]), (8, 6, TIN[1]), (9, 5, TIN[1]),
              (20, 5, TIN[4]), (21, 4, TIN[4])]
    return tin_plate(m, w, h, (), emboss, rivet=12)


def starlamp_frames():
    frames = []
    for lit in (False, True):
        img = new(16, 32)
        p = img.load()
        p[7, 1] = BRASS6[4]
        p[8, 1] = BRASS6[3]
        p[7, 2] = BRASS6[3]
        p[8, 2] = BRASS6[2]
        for x in range(5, 11):
            p[x, 3] = BRASS6[4] if x < 8 else BRASS6[3]
        for x in range(4, 12):
            p[x, 4] = (FIRE[3] if lit else BRASS6[2]) if 5 <= x <= 10 else BRASS6[2]
        for y in range(5, 13):
            for x in range(4, 12):
                if y in (5, 12) and x in (4, 11):
                    continue
                if x in (4, 11):
                    p[x, y] = BRASS6[2] if x == 4 else BRASS6[1]
                    continue
                if lit:
                    d = math.hypot(x + 0.5 - 8, (y + 0.5 - 8.5) * 0.9)
                    p[x, y] = hexc("#fff6d2") if d < 1.6 else (FIRE[5] if d < 2.6 else FIRE[4])
                else:
                    p[x, y] = ramp_at(GLASS[1:4], 0.65 - (y - 5) / 12.0, x, y)
        if not lit:
            p[5, 6] = GLASS[5]
            p[5, 7] = GLASS[4]
            p[7, 10] = BRASS6[1]
            p[8, 10] = BRASS6[1]
            p[7, 9] = BRASS6[2]
        else:
            p[6, 6] = hexc("#ffffff")
        for x in range(5, 11):
            p[x, 13] = BRASS6[3] if x < 9 else BRASS6[2]
            p[x, 14] = BRASS6[2]
        for y in range(15, 29):
            p[7, y] = BRASS6[3]
            p[8, y] = BRASS6[1]
        for x in range(6, 10):
            p[x, 21] = BRASS6[4] if x < 8 else BRASS6[2]
        for x in range(5, 11):
            p[x, 29] = SW_STONE[4] if x < 8 else SW_STONE[3]
        for x in range(4, 12):
            p[x, 30] = SW_STONE[2]
        frames.append(outline(img, INK))
    return frames


def orrery_sun_frames():
    frames = []
    for i in range(4):
        lit = i > 0
        img = new(16, 16)
        p = img.load()
        ramp = BRASS6[2:6] if lit else BRASS6[0:4]
        for y in range(16):
            for x in range(16):
                dx, dy = x + 0.5 - 8, y + 0.5 - 8
                d = math.hypot(dx, dy)
                if d <= 5.3:
                    lt = (dx * -0.55 + dy * -0.83) / 5.3
                    p[x, y] = ramp_at(ramp, 0.5 + 0.45 * lt - 0.15 * (d / 5.3) ** 2, x, y)
        for (x0, y0) in ((7, 1), (7, 13), (1, 7), (13, 7)):  # sun-ray fins
            for dx in range(2):
                for dy in range(2):
                    x, y = x0 + dx, y0 + dy
                    if math.hypot(x + 0.5 - 8, y + 0.5 - 8) > 5.3:
                        p[x, y] = ramp[2] if (dx + dy) == 0 else ramp[1]
        win = [(x, y) for y in (7, 8) for x in range(4, 12) if x not in (5, 8, 10)]
        win += [(7, 4), (8, 4), (7, 11), (8, 11)]
        flick = [None, (FIRE[5], FIRE[4]), (FIRE[4], FIRE[5]), (FIRE[5], FIRE[5])][i]
        for k, (x, y) in enumerate(win):
            if lit:
                p[x, y] = flick[k % 2] if y in (7, 8) else FIRE[4]
            else:
                p[x, y] = hexc("#1a1210")
        img = outline(img, INK)
        if lit:
            q = img.load()
            tips = [(7, 0), (8, 0), (7, 15), (8, 15), (0, 7), (0, 8), (15, 7), (15, 8)]
            for k, (x, y) in enumerate(tips):
                if (k + i) % 3 != 0:
                    q[x, y] = FIRE[3] if (k + i) % 2 else FIRE[4]
        frames.append(img)
    return frames


# -------------------------------------------------------------- great orrery ---

OW, OH = 112, 96
OCX, SUN_Y = 56, 38
# (rx, ry, count, step per frame in degrees, planet radius, ramp)
ORBITS = [
    (22, 7, 2, 45.0, 2.0, [hexc(c) for c in ("#3c4258", "#7e88a0", "#b2bccb", "#e8eef6")]),
    (34, 11, 3, -30.0, 2.8, [hexc(c) for c in ("#1a2152", "#29439a", "#3a7fcc", "#9fd8f2")]),
    (47, 15, 4, 22.5, 2.3, [hexc(c) for c in ("#4a1018", "#8a2f26", "#c65a34", "#f19a6a")]),
]


def _sphere(img, cx, cy, rad, ramp, light):
    p = img.load()
    for y in range(int(cy - rad) - 1, int(cy + rad) + 2):
        for x in range(int(cx - rad) - 1, int(cx + rad) + 2):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            d = math.hypot(dx, dy)
            if d <= rad and 0 <= x < img.width and 0 <= y < img.height:
                lt = (dx * light[0] + dy * light[1]) / max(rad, 0.1)  # light = direction to the light
                p[x, y] = ramp_at(ramp, 0.5 + 0.5 * lt - 0.1 * (d / rad), x, y)


def orrery_frame(k, lit):
    brass = BRASS6[1:6] if lit else BRASS6[0:4]
    back_thin = new(OW, OH)
    back_solid = new(OW, OH)
    hoop_layer = new(OW, OH)
    mid = new(OW, OH)
    front_thin = new(OW, OH)
    front_solid = new(OW, OH)
    # armillary hoop arching over everything
    hoop = new(OW, OH)
    hp = hoop.load()
    hcx, hcy, hrx, hry = OCX, 84, 42, 80
    for y in range(0, 85):
        for x in range(OW):
            d = math.hypot((x + 0.5 - hcx) / hrx, (y + 0.5 - hcy) / hry)
            if 0.955 <= d <= 1.0:
                a = math.atan2(y + 0.5 - hcy, x + 0.5 - hcx)
                lt = -math.cos(a + math.pi / 3)
                hp[x, y] = ramp_at(brass, 0.45 + 0.35 * lt, x, y)
    for deg in range(190, 351, 10):  # degree ticks inside the hoop
        a = math.radians(deg)
        x = int(hcx + math.cos(a) * (hrx - 4))
        y = int(hcy + math.sin(a) * (hry - 4))
        if 0 <= y < OH:
            hp[x, y] = brass[1]
    hoop_layer.alpha_composite(outline(hoop, INK))
    # rings and planets, split into the half behind the sun and the half in front
    bt, ft = back_thin.load(), front_thin.load()
    planets_back, planets_front = new(OW, OH), new(OW, OH)
    for (rx, ry, count, step, prad, ramp) in ORBITS:
        for deg10 in range(0, 3600, 4):
            a = math.radians(deg10 / 10)
            x, y = int(OCX + rx * math.cos(a)), int(SUN_Y + ry * math.sin(a))
            if math.sin(a) < 0:
                bt[x, y] = brass[1]
            else:
                ft[x, y] = brass[2] if lit else brass[1]
        pr = ramp if lit else [shade_c(c, 0.45) for c in ramp]
        for j in range(count):
            a = math.radians(j * 360.0 / count + step * k + 15)
            x, y = OCX + rx * math.cos(a), SUN_Y + ry * math.sin(a)
            if lit:  # the side facing the sun is the bright side
                lx, ly = OCX - x, SUN_Y - y
                ln = math.hypot(lx, ly) or 1.0
                light = (lx / ln, ly / ln)
            else:
                light = (-0.55, -0.83)
            target = planets_back if math.sin(a) < 0 else planets_front
            _sphere(target, x, y, prad, pr, light)
    back_solid.alpha_composite(outline(planets_back, INK))
    # base, column and the sun
    mp = mid.load()
    stone = SW_STONE if lit else [shade_c(c, 0.75) for c in SW_STONE]
    for (y0, y1, x0, x1, top, face) in ((80, 83, 32, 80, 4, 3), (84, 89, 18, 94, 3, 2), (90, 94, 12, 100, 2, 1)):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                c = stone[top] if y == y0 else stone[face]
                if x == x0:
                    c = stone[min(5, top + 1)]
                elif x == x1:
                    c = stone[max(0, face - 1)]
                mp[x, y] = c
    for x in range(32, 81):
        mp[x, 82] = brass[3] if x % 6 else brass[2]
    for cx_ in (34, 78):  # carved stars on the step
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            mp[cx_ + dx, 86 + dy] = stone[1] if (dx, dy) != (0, 0) else stone[4]
    for (fx, fy) in ((14, 79), (98, 79)):  # hoop feet
        for y in range(fy, 84):
            for x in range(fx - 3, fx + 4):
                mp[x, y] = brass[2] if x < fx else brass[1]
            mp[fx - 3, y] = brass[3]
    for y in range(46, 80):
        for x in range(53, 59):
            mp[x, y] = brass[3] if x == 54 else (brass[1] if x >= 57 else brass[2])
    for cy_ in (54, 65, 76):
        for x in range(52, 60):
            mp[x, cy_] = brass[3]
            mp[x, cy_ + 1] = brass[1]
    if lit:
        for y in range(SUN_Y - 10, SUN_Y + 11):
            for x in range(OCX - 10, OCX + 11):
                d = math.hypot(x + 0.5 - OCX, y + 0.5 - SUN_Y)
                if d <= 9.2:
                    mp[x, y] = hexc("#fff6d2") if d < 3.5 else (FIRE[5] if d < 5.8 else (FIRE[4] if d < 7.8 else FIRE[3]))
        mp[OCX - 3, SUN_Y - 4] = hexc("#ffffff")
    else:
        _sphere(mid, OCX, SUN_Y, 9.2, [hexc("#1a120e"), BRASS6[0], BRASS6[1], BRASS6[2]], (-0.55, -0.83))
        for x in range(OCX - 8, OCX + 9):
            if mp[x, SUN_Y][3]:
                mp[x, SUN_Y] = hexc("#140e0c")
    mid = outline(mid, INK)
    if lit:  # rays around the sun, alternating every frame
        q = mid.load()
        for ri in range(8):
            a = math.radians(ri * 45 + (22.5 if k % 2 else 0))
            for d in range(11, 14):
                x, y = int(round(OCX + math.cos(a) * d)), int(round(SUN_Y + math.sin(a) * d))
                if 0 <= x < OW and 0 <= y < OH and not q[x, y][3]:
                    q[x, y] = FIRE[4] if d < 13 else FIRE[3]
    front_solid.alpha_composite(outline(planets_front, INK))
    out = new(OW, OH)
    for layer in (hoop_layer, back_thin, back_solid, mid, front_thin, front_solid):
        out.alpha_composite(layer)
    return out


def shade_c(c, k):
    return (int(c[0] * k), int(c[1] * k), int(c[2] * k), c[3])


def great_orrery_frames():
    return [orrery_frame(0, False)] + [orrery_frame(k, True) for k in range(4)]


# ---------------------------------------------------------------- preview ---

TEST = [
    "##############################################",
    "##wwwwwwwwwwwwwwww......wwwwwwwwwwwwwwwwwww###",
    "#wwwwwwwwwwwwwwww........wwwwwwwwwwwwwwwwwww##",
    "#wwwwwwwwwwwwwwww........wwwwwwwwwwwwwwwwwww##",
    "#wwwwwwwwwwwwwwww........wwwwwwwwwwwwwwwwwww##",
    "#wwwwwwwwwwwwwwww........wwwwwwwwwwwwwwwwwww##",
    "#wwwwww======wwww........wwwwwwwwwwwwwwwwwww##",
    "#wwwwwwwwwwwwwwww........wwwwwwwwwwwwwww######",
    "#wwwwwwwwwwwwwwww........wwwwwwwwwwwwwww######",
    "#####wwwwwwwwwwww........wwwwwwwwwwwwwww######",
    "#####wwwwwwwwwwww........wwwwwwwwwwwwwww######",
    "##############################################",
    "##############################################",
]


def build():
    ground, wall = build_tiles()
    layers = build_backdrop()
    props = {
        "telescope": telescope(),
        "star_chart": star_chart(),
        "globe": globe(),
        "book_stack": book_stack(),
        "porthole": porthole(),
        "kelp": kelp(),
        "bubble_vent": bubble_vent(),
        "orrery_ring": orrery_ring(),
    }
    for k, img in props.items():
        save(img, f"deco/{k}.png")
    casters = {
        "caster_boat": caster_boat(),
        "caster_fish": caster_fish(),
        "caster_bird": caster_bird(),
        "caster_moon": caster_moon(),
    }
    for k, img in casters.items():
        save(img, f"sprites/{k}.png")
    lamps = starlamp_frames()
    save(sheet(lamps), "sprites/starlamp.png")
    suns = orrery_sun_frames()
    save(sheet(suns), "sprites/orrery_sun.png")
    orrery = great_orrery_frames()
    save(sheet(orrery), "sprites/great_orrery.png")

    save_preview(ground, "starwell_ground_atlas.png", 3)
    save_preview(wall, "starwell_wall_atlas.png", 3)
    deco_rows_preview(ground, "starwell_deco_rows.png")
    save_preview(compose_backdrop(layers, 40), "starwell_bg.png", 2)
    save_preview(sheet(orrery), "starwell_orrery.png", 2)

    rows = pad_rows(TEST)
    width = len(rows[0]) * T
    bd = scene_backdrop(layers, width)
    placed = [
        (props["telescope"], 6, 10, False), (props["globe"], 9, 10, False), (props["book_stack"], 11, 10, False),
        (props["star_chart"], 13, 10, False), (props["porthole"], 4, 4, False), (props["kelp"], 20, 1, True),
        (props["kelp"], 29, 1, True), (props["bubble_vent"], 22, 10, False), (props["orrery_ring"], 35, 10, False),
        (lamps[0], 26, 10, False), (lamps[1], 31, 10, False), (props["porthole"], 38, 5, False),
    ]
    scene = compose_scene(ground, wall, bd, rows, placed, wall_mod=WALL_TINT)
    # a hanging caster and its 2x shadow, as the game will draw them
    cast = casters["caster_fish"]
    scene.alpha_composite(cast, (30 * T - cast.width // 2, 6 * T))
    shadow = cast.resize((cast.width * 2, cast.height * 2))
    sp = shadow.load()
    for y in range(shadow.height):
        for x in range(shadow.width):
            if sp[x, y][3]:
                sp[x, y] = (6, 4, 12, 225)
    scene.alpha_composite(shadow, (34 * T - shadow.width // 2, 7 * T))
    scene.alpha_composite(suns[2], (18 * T, 4 * T))
    save_preview(scene, "starwell_test.png", 2)
    lit = ingame(scene, [(31 * T + 8, 8 * T + 8, 80, (1.0, 0.85, 0.6), 0.8),
                         (7 * T, 9 * T, 96, (1.0, 0.78, 0.5), 0.6),
                         (18 * T + 8, 4 * T + 8, 70, (1.0, 0.8, 0.45), 0.7)], ambient=(0.38, 0.44, 0.56))
    save_preview(lit, "starwell_test_ingame.png", 2)
    props_sheet(list(props.values()) + list(casters.values()) + lamps + suns, "starwell_props.png", height=44)


if __name__ == "__main__":
    build()
