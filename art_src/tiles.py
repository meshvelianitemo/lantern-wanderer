"""Ground tilesets.

Atlas layout (16px tiles, 16 columns):
  rows 0..15  : edge-mask variants. row = mask (U=1, R=2, D=4, L=8 set when that
                side is OPEN), col = texture phase ((ty % 4) * 4 + tx % 4) so the
                cobble pattern runs seamlessly across a 64x64 period.
  row 16      : decoration tiles drawn in EMPTY cells next to ground:
                cols 0-3  grass fringe (sits on top of a grass tile), by tx % 4
                cols 4-7  hanging roots (under a ceiling), by tx % 4
                col  8    grass curling over a right-facing ledge edge
                col  9    grass curling over a left-facing ledge edge
  row 17      : wooden one-way platform: 0 left, 1-2 middle, 3 right
"""
import math

from pix import (GRASS, PINE, ROCK, WOOD, CLEAR, hexc, new, rng, save, save_preview, ramp_at)

T = 16
PERIOD = 64
U, R, D, L = 1, 2, 4, 8


def wrapd(a, b):
    d = a - b
    return d - PERIOD * round(d / PERIOD)


def cobble(seed, ramp, mortar, cells=8, squash=1.18, light_bias=0):
    """Seamless Worley-noise cobblestone texture.

    Returns (image, mortar_mask) where mortar_mask[y][x] is True in the cracks.
    """
    r = rng(seed)
    cs = PERIOD / cells
    pts = []
    for cy in range(cells):
        for cx in range(cells):
            pts.append(((cx + 0.5) * cs + r.uniform(-2.7, 2.7),
                        (cy + 0.5) * cs + r.uniform(-2.2, 2.2),
                        r.random()))
    img = new(PERIOD, PERIOD)
    px = img.load()
    mort = [[False] * PERIOD for _ in range(PERIOD)]
    speck = rng(seed + 7)
    for y in range(PERIOD):
        for x in range(PERIOD):
            ds = []
            for (sx, sy, v) in pts:
                dx = wrapd(x + 0.5, sx)
                dy = wrapd(y + 0.5, sy)
                ds.append((math.hypot(dx, dy * squash), dx, dy, v))
            ds.sort(key=lambda t: t[0])
            d1, dx, dy, v = ds[0]
            edge = ds[1][0] - d1
            if edge < 1.05:
                mort[y][x] = True
                px[x, y] = mortar[1] if (x * 7 + y * 3) % 11 == 0 else mortar[0]
                continue
            b = (2 if v < 0.58 else 3) + light_bias
            n = max(d1, 0.01)
            lit = -(dx / n * 0.5 + dy / n * 0.86)
            c = b
            if edge < 2.3:
                if lit > 0.3:
                    c = b + 1
                elif lit < -0.25:
                    c = b - 1
            elif lit > 0.6 and d1 > 2.0 and speck.random() < 0.18:
                c = b + 1
            elif speck.random() < 0.025:
                c = b - 1
            px[x, y] = ramp[max(0, min(len(ramp) - 1, c))]
    return img, mort


def grass_profile(seed):
    """Per-column grass top offset and thickness, periodic over PERIOD."""
    r = rng(seed)
    top, th = [], []
    for x in range(PERIOD):
        top.append(1 if r.random() < 0.28 else 0)
        t = 4 if r.random() < 0.6 else 5
        if r.random() < 0.12:
            t += r.choice((2, 3, 4))  # little drips of moss
        th.append(t)
    # keep drips one or two pixels wide and smooth the profile a little
    for x in range(PERIOD):
        if th[x] > 6 and th[(x + 1) % PERIOD] > 6 and th[(x - 1) % PERIOD] > 6:
            th[x] = 5
    return top, th


def build_terrain(name, ramp, mortar, seed, grass=True, outline_col=None, light_bias=0,
                  moss=None, wood=None, profile=None, tex_post=None, fringe=None, hang=None,
                  texture=None, platform=None):
    """Build a terrain atlas (layout in the module docstring).

    Optional style hooks (defaults reproduce the forest look exactly):
      moss     6-colour ramp used for the grass/moss top (default GRASS)
      wood     6-colour ramp for the one-way platform planks (default WOOD)
      profile  (top, thickness) per-column lists of length PERIOD for the moss top
      tex_post callable(tex_image, mortar_mask) run on the cobble texture
      fringe   callable(rng, phase) -> 16x16 image for deco row cols 0-3
      hang     callable(rng, phase) -> 16x16 image for deco row cols 4-7
      texture  callable(seed, ramp, mortar, light_bias) -> (64x64 image, mortar_mask)
               replacing the cobble texture (e.g. masonry, earth)
      platform callable(i) -> 16x16 image for row 17 col i (0 left, 1-2 mid, 3 right);
               the walkable top must be on y=0 (collision is the top 5px)
    """
    GRASS_ = moss or GRASS
    WOOD_ = wood or WOOD
    tex, mort = (texture or cobble)(seed, ramp, mortar, light_bias=light_bias)
    if tex_post:
        tex_post(tex, mort)
    tex_px = tex.load()
    gtop, gth = profile if profile else grass_profile(seed + 100)
    out_rock = outline_col or ramp[0]
    atlas = new(16 * T, 18 * T)

    for mask in range(16):
        for phase in range(16):
            phx, phy = phase % 4, phase // 4
            ox, oy = phx * T, phy * T
            tile = new(T, T)
            tp = tile.load()
            kind = [[0] * T for _ in range(T)]  # 0 clear, 1 rock, 2 grass
            for y in range(T):
                for x in range(T):
                    tp[x, y] = tex_px[ox + x, oy + y]
                    kind[y][x] = 1

            def clear(x, y):
                if 0 <= x < T and 0 <= y < T:
                    tp[x, y] = CLEAR
                    kind[y][x] = 0

            # bumpy edges: cracks touching an open side become notches
            for i in range(T):
                if mask & L and mort[oy + i][ox]:
                    clear(0, i)
                if mask & R and mort[oy + i][ox + T - 1]:
                    clear(T - 1, i)
                if mask & D and mort[oy + T - 1][ox + i]:
                    clear(i, T - 1)
            # rounded convex corners
            if mask & U and mask & L:
                for p in ((0, 0), (1, 0), (0, 1)):
                    clear(*p)
            if mask & U and mask & R:
                for p in ((15, 0), (14, 0), (15, 1)):
                    clear(*p)
            if mask & D and mask & L:
                for p in ((0, 15), (1, 15), (0, 14), (0, 13), (2, 15)):
                    clear(*p)
            if mask & D and mask & R:
                for p in ((15, 15), (14, 15), (15, 14), (15, 13), (13, 15)):
                    clear(*p)

            # underside shading
            if mask & D:
                for x in range(T):
                    for y in (13, 14):
                        if kind[y][x] == 1:
                            c = tp[x, y]
                            idx = ramp.index(c) if c in ramp else 1
                            tp[x, y] = ramp[max(0, idx - (2 if y == 14 else 1))]
            if mask & R:
                for y in range(T):
                    for x in (13, 14):
                        if kind[y][x] == 1 and (x == 14 or y % 2 == 0):
                            c = tp[x, y]
                            idx = ramp.index(c) if c in ramp else 1
                            tp[x, y] = ramp[max(0, idx - 1)]

            if grass and mask & U:
                for x in range(T):
                    xw = ox + x
                    top, th = gtop[xw], gth[xw]
                    if kind[0][x] == 0 and x in (0, 15):
                        top = max(top, 1)
                    for y in range(0, top):
                        clear(x, y)
                    for y in range(top, min(T, top + th)):
                        if kind[y][x] == 0 and y > 1:
                            continue
                        k = y - top
                        if k == 0:
                            col = GRASS_[5] if (xw * 5) % 13 == 0 else GRASS_[4]
                        elif k == 1:
                            col = GRASS_[4] if (xw + y) % 3 == 0 else GRASS_[3]
                        elif k < th - 1:
                            col = GRASS_[3] if (xw * 3 + k) % 4 else GRASS_[2]
                        else:
                            col = GRASS_[2] if k < 4 else GRASS_[1]
                        tp[x, y] = col
                        kind[y][x] = 2
                    y = top + th
                    if y < T and kind[y][x] == 1:
                        tp[x, y] = ramp[0]
                # grass wraps over open side edges
                for side, xs in ((L, (0, 1)), (R, (15, 14))):
                    if mask & side:
                        drape = 4 + (ox // 16 + oy) % 3
                        for y in range(2, drape + 2):
                            x0 = xs[0]
                            if y < T and kind[y][x0] != 0:
                                tp[x0, y] = GRASS_[2] if y < drape else GRASS_[1]
                                kind[y][x0] = 2

            # outline pass on open sides
            res = tile.copy()
            rp = res.load()
            for y in range(T):
                for x in range(T):
                    if kind[y][x] == 0:
                        continue
                    edge_side = False
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < T and 0 <= ny < T:
                            if kind[ny][nx] == 0:
                                if kind[y][x] == 2 and dy == -1:
                                    continue  # grass tops stay bright
                                edge_side = True
                        else:
                            if (nx < 0 and mask & L) or (nx >= T and mask & R) or (ny >= T and mask & D):
                                edge_side = True
                    if edge_side:
                        rp[x, y] = GRASS_[0] if kind[y][x] == 2 else out_rock
            atlas.paste(res, (phase * T, mask * T))

    # --- decoration row ------------------------------------------------------
    r = rng(seed + 300)
    if grass and fringe:
        for ph in range(4):
            atlas.paste(fringe(r, ph), (ph * T, 16 * T))
    elif grass:
        for ph in range(4):
            f = new(T, T)
            fp = f.load()
            x = 0
            while x < T:
                h = r.choice((0, 0, 1, 1, 2, 2, 3, 4))
                if h:
                    for y in range(h):
                        yy = T - 1 - y
                        fp[x, yy] = GRASS_[5] if y == h - 1 and h > 2 else (GRASS_[4] if y > 0 else GRASS_[3])
                    if h >= 3 and x + 1 < T and r.random() < 0.5:
                        fp[x + 1, T - 1] = GRASS_[3]
                        fp[x + 1, T - 2] = GRASS_[4]
                        x += 1
                x += r.choice((1, 1, 2))
            atlas.paste(f, (ph * T, 16 * T))
    for ph in range(4):
        if hang:
            atlas.paste(hang(r, ph), ((4 + ph) * T, 16 * T))
            continue
        f = new(T, T)
        fp = f.load()
        for _ in range(r.randint(2, 4)):
            x = r.randint(1, 14)
            ln = r.randint(3, 11)
            for y in range(ln):
                xx = x + (1 if (y // 3) % 2 and r.random() < 0.6 else 0)
                xx = max(0, min(T - 1, xx))
                fp[xx, y] = ramp[1] if y < ln - 2 else ramp[2]
            if grass and r.random() < 0.7:
                fp[max(0, min(T - 1, x)), 0] = GRASS_[1]
                if ln > 5:
                    fp[max(0, min(T - 1, x)), 1] = GRASS_[2]
        atlas.paste(f, ((4 + ph) * T, 16 * T))
    if grass:
        for col, side in ((8, 1), (9, -1)):
            f = new(T, T)
            fp = f.load()
            edge = T - 1 if side == 1 else 0
            for y in range(1, 7):
                w = 1 if y > 2 else 2
                for k in range(w):
                    x = edge - k * side
                    fp[x, y] = GRASS_[3] if y < 3 else (GRASS_[2] if y < 5 else GRASS_[1])
            fp[edge, 7] = GRASS_[0]
            fp[edge - side, 3] = GRASS_[0]
            atlas.paste(f, (col * T, 16 * T))

    # --- wooden one-way platform ---------------------------------------------
    for i in range(4):
        if platform:
            atlas.paste(platform(i), (i * T, 17 * T))
            continue
        f = new(T, T)
        fp = f.load()
        for x in range(T):
            for y in range(0, 6):
                if y == 0:
                    c = WOOD_[4] if (x + i) % 5 else WOOD_[5]
                elif y == 1:
                    c = WOOD_[4]
                elif y in (2, 3):
                    c = WOOD_[3]
                elif y == 4:
                    c = WOOD_[2]
                else:
                    c = WOOD_[0]
                fp[x, y] = c
            if (x + i * 5) % 8 == 7:  # plank seams
                for y in range(1, 5):
                    fp[x, y] = WOOD_[1]
        # nails
        for x in range(T):
            if (x + i * 5) % 8 == 2:
                fp[x, 2] = WOOD_[5]
        if i == 0:
            for y in range(6):
                fp[0, y] = WOOD_[0]
            fp[1, 0] = CLEAR
            fp[0, 0] = CLEAR
        if i == 3:
            for y in range(6):
                fp[T - 1, y] = WOOD_[0]
            fp[T - 1, 0] = CLEAR
            fp[T - 2, 0] = CLEAR
        # little support bracket under the planks
        if i in (0, 3):
            bx = 3 if i == 0 else 11
            for y in range(6, 10):
                fp[bx, y] = WOOD_[2]
                fp[bx + 1, y] = WOOD_[1]
            for y in range(6, 9):
                fp[bx + (2 if i == 0 else -1), 6] = WOOD_[1]
        atlas.paste(f, (i * T, 17 * T))

    save(atlas, f"tiles/{name}.png")
    return atlas


def mask_at(grid, x, y):
    def solid(xx, yy):
        if yy < 0:
            return False
        if xx < 0 or xx >= len(grid[0]) or yy >= len(grid):
            return True
        return grid[yy][xx] == "#"
    m = 0
    if not solid(x, y - 1):
        m |= U
    if not solid(x + 1, y):
        m |= R
    if not solid(x, y + 1):
        m |= D
    if not solid(x - 1, y):
        m |= L
    return m


def preview_map(atlas, rows, name, bg=None):
    """Compose a test scene exactly the way the Godot level builder will."""
    from pix import SKY
    h, w = len(rows), len(rows[0])
    img = new(w * T, h * T, bg or SKY[3])
    def put(col, row, x, y):
        tile = atlas.crop((col * T, row * T, col * T + T, row * T + T))
        img.alpha_composite(tile, (x * T, y * T))
    for y in range(h):
        for x in range(w):
            c = rows[y][x]
            if c == "#":
                m = mask_at(rows, x, y)
                put((y % 4) * 4 + x % 4, m, x, y)
                if m & U and y > 0:
                    put(x % 4, 16, x, y - 1)
                    if m & L and x > 0:
                        put(8, 16, x - 1, y)
                    if m & R and x < w - 1:
                        put(9, 16, x + 1, y)
                if m & D and y < h - 1 and (x * 7 + y) % 3 == 0:
                    put(4 + x % 4, 16, x, y + 1)
            elif c == "=":
                left = x == 0 or rows[y][x - 1] != "="
                right = x == w - 1 or rows[y][x + 1] != "="
                put(0 if left else (3 if right else 1 + x % 2), 17, x, y)
    save_preview(img, name, 3)


if __name__ == "__main__":
    ground = build_terrain("forest_ground", ROCK, (ROCK[0], ROCK[1]), seed=11)
    wall_ramp = [hexc(c) for c in ("#0f0910", "#1a1018", "#26151e", "#341c24", "#43252b", "#532f33")]
    build_terrain("forest_wall", wall_ramp, (wall_ramp[0], wall_ramp[0]), seed=12, grass=False)
    save_preview(ground, "forest_ground_atlas.png", 3)
    test = [
        "..............................",
        "..............................",
        "...........######.............",
        "..........########.....===....",
        "...........#####..............",
        "..................#####.......",
        "#####............#######......",
        "######....===....########...##",
        "#######.........##########..##",
        "##############################",
        "##############################",
        "##############################",
    ]
    preview_map(ground, test, "forest_ground_test.png")
