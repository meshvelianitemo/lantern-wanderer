"""The scarf GIF: the wanderer runs through the night, and their scarf (their wick) burns
shorter, stage by stage. The pieces that burn away drift up as sparks.

  python scarf_gif.py ../media/gifs/00_the_scarf.gif
"""
import os
import random
import sys

import numpy as np
from PIL import Image

SPRITES = os.path.join(os.path.dirname(__file__), "..", "assets", "sprites")
W, H = 96, 56
SCALE = 6
GROUND = 46          # top of the ground
HERO_X = 32          # left edge of the 32x32 hero
HOLD = 28            # frames on each scarf stage
SPARK_FRAMES = 10
SKY_TOP = np.array([18, 14, 34])
SKY_LOW = np.array([44, 30, 52])


def sheet(name):
    im = Image.open(os.path.join(SPRITES, name)).convert("RGBA")
    return [im.crop((i * 32, 0, i * 32 + 32, 32)) for i in range(im.width // 32)]


def background(rng):
    sky = np.zeros((H, W, 3), dtype=np.uint8)
    for y in range(H):
        t = y / H
        sky[y, :] = (SKY_TOP * (1 - t) + SKY_LOW * t).astype(np.uint8)
    for _ in range(26):
        x, y = rng.randrange(W), rng.randrange(GROUND - 6)
        sky[y, x] = (200, 196, 230) if rng.random() < 0.4 else (120, 112, 160)
    return Image.fromarray(sky)


def ground_strip(rng, length):
    """A long strip of earth, grass and pebbles that scrolls under the runner."""
    strip = Image.new("RGB", (length, H - GROUND), (58, 34, 36))
    px = strip.load()
    for x in range(length):
        px[x, 0] = (96, 150, 64)
        px[x, 1] = (70, 112, 52) if x % 3 else (96, 150, 64)
        for y in range(2, H - GROUND):
            if rng.random() < 0.08:
                px[x, y] = (84, 52, 50)
            elif rng.random() < 0.04:
                px[x, y] = (40, 24, 28)
    tufts = Image.new("RGBA", (length, 4), (0, 0, 0, 0))
    tp = tufts.load()
    for x in range(0, length, 1):
        if rng.random() < 0.18:
            h = rng.choice([1, 2, 2, 3])
            for y in range(4 - h, 4):
                tp[x, y] = (110, 168, 72, 255)
    return strip, tufts


def glow(cx, cy, radius, strength):
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / radius
    a = np.clip(1 - d, 0, 1) ** 2 * strength
    return a[..., None] * np.array([255, 170, 90])


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "scarf.gif"
    rng = random.Random(7)
    stages = [sheet("hero_run.png"), sheet("hero_run_s1.png"), sheet("hero_run_s2.png")]
    sky = background(rng)
    strip, tufts = ground_strip(rng, 4000)
    timeline = []  # (stage, sparks_from_stage or None, spark_age)
    for s in range(3):
        timeline += [(s, None, 0)] * HOLD
        if s < 2:
            timeline += [(s + 1, s, age) for age in range(SPARK_FRAMES)]
    timeline += [(2, None, 0)] * 10

    sparks = []
    frames = []
    for n, (stage, burnt_from, age) in enumerate(timeline):
        f = sky.copy().convert("RGB")
        scroll = n * 3
        f.paste(strip.crop((scroll, 0, scroll + W, H - GROUND)), (0, GROUND))
        f.paste(tufts.crop((scroll, 0, scroll + W, 4)), (0, GROUND - 3), tufts.crop((scroll, 0, scroll + W, 4)))
        flicker = 0.5 + 0.06 * np.sin(n * 1.7) + 0.04 * np.sin(n * 2.9)
        lit = np.array(f).astype(float) + glow(HERO_X + 22, GROUND - 14, 30, flicker)
        f = Image.fromarray(np.clip(lit, 0, 255).astype(np.uint8))
        hero = stages[stage][n % 6]
        f.paste(hero, (HERO_X, GROUND - 32), hero)
        # the bit of scarf that just burned away, as sparks
        if burnt_from is not None and age == 0:
            before = np.array(stages[burnt_from][n % 6])[..., 3] > 0
            after = np.array(stages[stage][n % 6])[..., 3] > 0
            for y, x in zip(*np.nonzero(before & ~after)):
                sparks.append([HERO_X + x, GROUND - 32 + y, rng.uniform(-0.6, 0.2), rng.uniform(-1.4, -0.5), 0])
        px = f.load()
        for s in sparks:
            s[0] += s[2] - 1.5  # the wind of running carries them back
            s[1] += s[3]
            s[4] += 1
            x, y = int(s[0]), int(s[1])
            if 0 <= x < W and 0 <= y < H:
                px[x, y] = (255, 230, 140) if s[4] < 4 else ((240, 120, 40) if s[4] < 9 else (130, 60, 40))
        sparks = [s for s in sparks if s[4] < 14]
        frames.append(f.resize((W * SCALE, H * SCALE), Image.NEAREST))

    pal = frames[0].quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    q = [fr.quantize(palette=pal, dither=Image.Dither.NONE) for fr in frames]
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    durations = [83] * len(q)
    durations[-1] = 900
    q[0].save(out_path, save_all=True, append_images=q[1:], duration=durations, loop=0, disposal=1)
    print("%s: %d frames, %d KB" % (out_path, len(q), os.path.getsize(out_path) // 1024))


if __name__ == "__main__":
    main()
