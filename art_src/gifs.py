"""Turn recorded frames into a pixel-crisp GIF.

Record frames first (fixed 60 fps, so they're evenly spaced), e.g. every 3rd frame = 20 fps:
  Godot.exe --path . --fixed-fps 60 --resolution 480x270 -- --skip-intro --level=mossgrave
      --hold=move_right@30 --record=C:/tmp/walk --from=30 --every=3 --frames=330

Then:
  python gifs.py C:/tmp/walk ../media/gifs/walk.gif --fps 20 --scale 2

Options:
  --fps N           playback speed (match --every: 60 / every)
  --scale N         nearest-neighbour upscale (2 = 960x540)
  --crop x,y,w,h    cut a region out of the 480x270 frame first
  --skip N          drop the first N frames     --take N   keep only N frames after that
  --step N          keep every Nth of those (a time-lapse, N times faster)
  --hold S          linger on the last frame for S seconds
  --colors N        palette size (default 255)

One palette is shared by every frame (no flicker), with no dithering (keeps the pixel art clean).
Pixels that didn't change since the last frame are written as transparent, which GIF compresses
to almost nothing (the picture is identical; only the file is smaller).
"""
import argparse
import glob
import os

import numpy as np
from PIL import Image

CLEAR = 255  # palette index for "unchanged since the last frame"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("frames")
    ap.add_argument("out")
    ap.add_argument("--fps", type=float, default=20)
    ap.add_argument("--scale", type=int, default=2)
    ap.add_argument("--crop", default="")
    ap.add_argument("--skip", type=int, default=0)
    ap.add_argument("--take", type=int, default=0)
    ap.add_argument("--step", type=int, default=1, help="keep every Nth frame (N times faster)")
    ap.add_argument("--hold", type=float, default=0)
    ap.add_argument("--colors", type=int, default=255)
    ap.add_argument("--check", action="store_true", help="decode the GIF and compare it to the frames")
    a = ap.parse_args()

    paths = sorted(glob.glob(os.path.join(a.frames, "*.png")))[a.skip:]
    if a.take:
        paths = paths[:a.take]
    paths = paths[::a.step]
    if not paths:
        raise SystemExit("no frames in " + a.frames)
    frames = [Image.open(p).convert("RGB") for p in paths]
    if a.crop:
        x, y, w, h = (int(v) for v in a.crop.split(","))
        frames = [f.crop((x, y, x + w, y + h)) for f in frames]

    # one shared palette, from a strip of evenly spaced sample frames
    step = max(1, len(frames) // 16)
    samples = frames[::step]
    w, h = frames[0].size
    strip = Image.new("RGB", (w, h * len(samples)))
    for i, f in enumerate(samples):
        strip.paste(f, (0, h * i))
    palette = strip.quantize(colors=min(a.colors, CLEAR), method=Image.Quantize.MEDIANCUT)
    pal = palette.getpalette()[:CLEAR * 3]
    pal += [0, 0, 0] * (256 - len(pal) // 3)

    indexed = [np.array(f.quantize(palette=palette, dither=Image.Dither.NONE)) for f in frames]
    out = []
    prev = None
    for cur in indexed:
        d = cur.copy()
        same = cur == prev if prev is not None else None
        # only worth it when most of the picture holds still (not while the camera pans)
        if same is not None and same.mean() > 0.6:
            d[same] = CLEAR
        prev = cur
        if a.scale != 1:
            d = d.repeat(a.scale, axis=0).repeat(a.scale, axis=1)
        im = Image.fromarray(d, "P")
        im.putpalette(pal)
        out.append(im)

    ms = round(1000 / a.fps)
    durations = [ms] * len(out)
    if a.hold:
        durations[-1] += round(a.hold * 1000)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    out[0].save(a.out, save_all=True, append_images=out[1:], duration=durations, loop=0,
                optimize=False, disposal=1, transparency=CLEAR)
    kb = os.path.getsize(a.out) // 1024
    print("%s: %d frames, %.1f s, %dx%d, %d KB" % (a.out, len(out), sum(durations) / 1000,
                                                   w * a.scale, h * a.scale, kb))
    if a.check:
        check(a.out, indexed, pal, a.scale)


def check(path, indexed, pal, scale):
    """Decode the GIF frame by frame and count pixels that differ from what was meant."""
    lut = np.array(pal, dtype=np.uint8).reshape(-1, 3)
    gif = Image.open(path)
    bad = 0
    for i, want in enumerate(indexed):
        gif.seek(i)
        got = np.array(gif.convert("RGB"))[::scale, ::scale]
        bad += int((got != lut[want]).any(axis=2).sum())
    print("  check: %d wrong pixels across %d frames" % (bad, len(indexed)))


if __name__ == "__main__":
    main()
