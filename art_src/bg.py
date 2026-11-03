"""Parallax background layers for the forest (480x270 viewport).

Every layer except the sky tiles seamlessly horizontally (period = width), so
Godot's Parallax2D can repeat it forever.
"""
import math

from pix import (BONE, PINE, SKY, CLEAR, dith, hexc, new, ramp_at, rng, save, save_preview)

W, H = 480, 270


def periodic_noise(seed, width, octaves=((1, 1.0), (2, 0.5), (3, 0.35), (5, 0.2), (9, 0.1), (17, 0.05))):
    """Smooth 1D noise that wraps exactly at `width` (sum of integer-frequency sines)."""
    r = rng(seed)
    terms = [(f, a, r.uniform(0, math.tau)) for f, a in octaves]
    norm = sum(a for _, a, _ in terms)
    def f(x):
        return sum(a * math.sin(math.tau * fr * x / width + ph) for fr, a, ph in terms) / norm
    return f


def sky():
    img = new(W, H)
    p = img.load()
    stops = [(0, 0.0), (90, 0.28), (170, 0.55), (215, 0.78), (250, 0.92), (270, 1.0)]
    ramp = SKY[1:8]
    for y in range(H):
        for i in range(len(stops) - 1):
            if stops[i][0] <= y <= stops[i + 1][0]:
                y0, t0 = stops[i]
                y1, t1 = stops[i + 1]
                t = t0 + (t1 - t0) * (y - y0) / max(1, y1 - y0)
                break
        for x in range(W):
            p[x, y] = ramp_at(ramp, t, x, y)
    r = rng(5)
    for _ in range(170):  # stars, denser near the top
        x = r.randrange(W)
        y = int(r.random() ** 1.8 * 170)
        b = r.random()
        if b > 0.93:
            c = BONE[4]
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p[(x + dx) % W, max(0, y + dy)] = SKY[5]
        elif b > 0.6:
            c = BONE[3]
        else:
            c = SKY[5] if y > 60 else SKY[4]
        p[x, y] = c
    # moon with a dithered halo
    mx, my, mr = 366, 62, 13
    for y in range(my - 40, my + 41):
        for x in range(mx - 40, mx + 41):
            d = math.hypot(x - mx, y - my)
            if d <= mr:
                lx, ly = (x - mx + 4) / mr, (y - my + 4) / mr
                t = 1 - min(1, math.hypot(lx, ly) * 0.7)
                c = ramp_at(BONE[2:], 0.35 + 0.65 * t, x, y)
                p[x, y] = c
            elif d < mr + 18:
                t = 1 - (d - mr) / 18
                if dith(x, y, t * 0.55):
                    cur = p[x, y]
                    idx = SKY.index(cur) if cur in SKY else 3
                    p[x, y] = SKY[min(len(SKY) - 1, idx + 1)]
    for (cx, cy, cr) in ((362, 58, 3), (370, 67, 2), (359, 68, 1), (372, 55, 1)):
        for y in range(cy - cr, cy + cr + 1):
            for x in range(cx - cr, cx + cr + 1):
                if math.hypot(x - cx, y - cy) <= cr:
                    p[x, y] = BONE[2]
    return img


def clouds():
    """Puffy cumulus banks built from overlapping circles, lit from above."""
    w, h = 640, 150
    img = new(w, h)
    p = img.load()
    r = rng(21)
    bands = ((62, SKY[3], SKY[4], 14, (14, 30)), (92, SKY[4], SKY[5], 18, (10, 22)), (122, SKY[5], SKY[6], 22, (7, 16)))
    for base, body, lit, n, (rmin, rmax) in bands:
        puffs = [(r.uniform(0, w), base - r.uniform(0, 10), r.uniform(rmin, rmax)) for _ in range(n)]
        for x in range(w):
            topy = None
            for (cx, cy, cr) in puffs:
                for off in (-w, 0, w):
                    dx = x - (cx + off)
                    if abs(dx) < cr:
                        t = cy - math.sqrt(cr * cr - dx * dx) * 0.7
                        topy = t if topy is None else min(topy, t)
            if topy is None:
                continue
            bottom = base + 8
            for y in range(max(0, int(topy)), min(h, bottom)):
                d = y - topy
                if d < 2 or (d < 5 and dith(x, y, 1 - (d - 2) / 3)):
                    c = lit
                else:
                    c = body
                if y > bottom - 3 and dith(x, y, (y - (bottom - 3)) / 3):
                    continue
                p[x, y] = c
    return img


def mountains():
    w = 640
    img = new(w, H)
    p = img.load()
    for layer, (base, amp, seed, body, rim) in enumerate((
            (150, 55, 31, SKY[3], SKY[4]),
            (185, 40, 32, SKY[2], SKY[3]))):
        f = periodic_noise(seed, w, ((2, 1.0), (3, 0.7), (5, 0.4), (8, 0.25), (16, 0.12), (31, 0.05)))
        prev = None
        for x in range(w):
            ridge = base - amp * f(x)
            slope = f(x) - f((x + 1) % w)
            for y in range(max(0, int(ridge)), H):
                d = y - ridge
                c = body
                if d < 3 and slope < -0.002:
                    c = rim  # lit by the moon on the right
                elif d < 8 and slope < -0.004 and dith(x, y, 0.5 - d / 16):
                    c = rim
                p[x, y] = c
    return img


def pine_shape(p, w, h, x0, base, height, width, body, rim, dark, r, outline_col=None):
    """Stylised pine: overlapping drooping tiers with needle tufts, moon-lit right side."""
    top = base - height
    tiers = max(3, int(height / 10))
    trunk_h = max(3, height // 10)
    crown_bottom = base - trunk_h
    span = crown_bottom - top
    rows = []
    for i in range(tiers):
        yt = top + int(span * (i / tiers) ** 1.15) - (2 if i else 0)
        yb = top + int(span * ((i + 1) / tiers) ** 1.05)
        rows.append((yt, yb))
    for xx in (x0 - 1, x0):  # trunk
        for y in range(crown_bottom - 4, base):
            if 0 <= y < h:
                p[int(xx) % w, y] = dark
    for i in reversed(range(tiers)):
        yt, yb = rows[i]
        full = width / 2 * (0.3 + 0.7 * (i + 1) / tiers)
        tip = 1.2 + i * 0.3
        for y in range(yt, yb + 2):
            k = (y - yt) / max(1, yb - yt)
            half = tip + (full - tip) * min(1.0, k) ** 0.85
            for xx in range(int(x0 - half - 1), int(x0 + half) + 2):
                rel = (xx - x0) / max(1.0, half)
                if abs(rel) > 1.0:
                    continue
                droop = int(abs(rel) ** 2 * 2.2)  # outer tips hang lower
                if y > yb + droop - 1 or (y > yb and abs(rel) < 0.6):
                    continue
                if abs(rel) > 0.82 and (int(xx * 3 + y * 5) % 3 == 0):
                    continue  # ragged needle edge
                c = body
                if y >= yb + droop - 1 and k > 0.9:
                    c = dark
                elif rel > 0.35 and k < 0.92:
                    c = rim
                elif rel < -0.3:
                    c = dark
                if 0 <= y < h:
                    p[xx % w, y] = c
    if 0 <= top - 1 < h:
        p[int(x0) % w, top - 1] = body


def treeline(seed, base, count, hmin, hmax, body, rim, dark, fill_below=True, w=640):
    img = new(w, H)
    p = img.load()
    r = rng(seed)
    ground = periodic_noise(seed + 9, w, ((1, 1.0), (3, 0.5), (6, 0.2)))
    if fill_below:
        for x in range(w):
            g = int(base + 4 * ground(x))
            for y in range(g, H):
                p[x, y] = dark if y > g + 1 else body
    xs = sorted(r.uniform(0, w) for _ in range(count))
    for x0 in xs:
        hgt = r.randint(hmin, hmax)
        wid = hgt * r.uniform(0.32, 0.42)
        g = int(base + 4 * ground(x0)) + 2
        pine_shape(p, w, H, x0, g, hgt, wid, body, rim, dark, r)
    return img


def mist(seed, y0, thick, col, w=640, density=0.45):
    img = new(w, H)
    p = img.load()
    f = periodic_noise(seed, w)
    for x in range(w):
        c = y0 + 6 * f(x)
        for y in range(int(c - thick), int(c + thick)):
            t = 1 - abs(y - c) / thick
            if 0 <= y < H and dith(x, y, t * density):
                p[x, y] = col
    return img


def build():
    layers = {
        "sky": sky(),
        "clouds": clouds(),
        "mountains": mountains(),
        "pines_far": treeline(41, 205, 40, 44, 74, SKY[2], SKY[3], hexc("#1a2744")),
        "pines_mid": treeline(42, 236, 22, 70, 120, PINE[1], PINE[2], PINE[0]),
        "mist": mist(43, 212, 16, SKY[5], density=0.35),
    }
    for name, img in layers.items():
        save(img, f"bg/forest_{name}.png")
    comp = new(W, H)
    for name in ("sky", "clouds", "mountains", "mist", "pines_far", "pines_mid"):
        img = layers[name]
        comp.alpha_composite(img.crop((0, 0, W, H)) if img.height == H else img.crop((0, 0, W, img.height)),
                             (0, 0 if img.height == H else 40))
    save_preview(comp, "forest_bg.png", 2)


if __name__ == "__main__":
    build()
