"""Art for "Echoes & Home" (DESIGN.md section 7f).

Run `python echoes.py` to (re)generate, all under assets/:

  sprites/hero_{idle,run,jump,fall,land}_{lark,vesper,maud}.png
                         hero skins, same sheets as hero_*.png (32x32 frames: idle 6, run 6,
                         jump 2, fall 2, land 2; feet on the bottom row; facing right).
                         Lark: slate-blue cloak, rose scarf. Vesper: bone-white cloak, long gold
                         scarf. Maud: a Keeper woman with a brass handbell where the lantern
                         would be (bell body x 23-27, y 25-28, centre ~25,26.5 at rest).
  sprites/glim.png       80x12   4 frames 20x12: 0-1 cold idle, 2-3 lit idle (Wisp's mama)
  sprites/edda.png      160x28   8 frames 20x28: 0-1 idle, 2-3 talk, 4-7 walk (the carver)
  sprites/keeper_{hollis,fitch,tobin,pim,wren}.png
                        128x20   8 frames 16x20: 0-1 asleep, 2-3 awake idle, 4-7 walk
  sprites/keepsake.png   48x16   3 frames 16x16: Lark's cold lantern, Maud's handbell, the first page
  sprites/sapling_tree_2.png  80x56   2 frames 40x56 (Sprig, taller)
  sprites/sapling_tree_3.png 112x76   2 frames 56x76 (Sprig, tall)
  fx/ring.png            96x96   soft white ring (the bell's sound wave)
  deco/supper_table.png  deco/bunting.png (hangs)  deco/bell_post.png
  deco/keeper_lamp.png   deco/lamp_string.png (hangs)  deco/banner.png (hangs)

Previews: _preview/echoes_heroes.png, echoes_npcs.png, echoes_props.png, echoes_scale.png.
"""
import math

from PIL import Image

import hero
from npcs import BRASS, WAX, rows_at, soft_blob
from npcs2 import LEAF_GLOW
from pix import (BONE, CRYSTAL, FIRE, GLOW, GRASS, INK, PINK, RED, ROCK, SCARF, STONE, WOOD, hexc,
                 new, outline, paste, ramp_at, save, save_preview, sheet, sprite)

F = 32
BOOT = hero.BOOT
METAL = hero.METAL
VOID = hero.VOID
EYE = hexc("#fffbe6")

ANIMS = ("idle", "run", "jump", "fall", "land")


def ellipse(img, cx, cy, rx, ry, ramp, light=(0.55, -0.83), rim=0.22):
    """Filled ellipse shaded in flat bands (lit from the upper right, the way we face)."""
    p = img.load()
    for y in range(int(cy - ry - 1), int(cy + ry + 2)):
        for x in range(int(cx - rx - 1), int(cx + rx + 2)):
            if not (0 <= x < img.width and 0 <= y < img.height):
                continue
            nx, ny = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            k = nx * nx + ny * ny
            if k > 1.0:
                continue
            t = 0.5 + 0.42 * (nx * light[0] + ny * light[1]) - rim * k
            p[x, y] = ramp_at(ramp, t, x, y)


# ================================================================ hero skins ==

LARK = {
    "cloak": [hexc(c) for c in ("#1a1d2c", "#2a3146", "#3d4a64", "#566887", "#7a8ea9")],
    "scarf": [hexc(c) for c in ("#4a1424", "#8c2a40", "#c54a5f", "#ec8590")],
    "tail": None,
}
VESPER = {
    "cloak": [hexc(c) for c in ("#3b3443", "#6a6176", "#a399a7", "#d9d0cb", "#f6efe3")],
    "scarf": [hexc(c) for c in ("#5b360c", "#a46c18", "#dea42c", "#ffd965")],
    "tail": (5, 9),                      # longer scarf: (idle, running) tail length
}


def _long_scarf(lengths):
    """hero.scarf with a longer tail; the shape and wave are the same."""
    def scarf(img, x, y, phase, run):
        p = img.load()
        K = hero.KEY
        for i in range(7):
            p[x + i, y] = K["t"] if i in (4, 5) else K["s"]
            p[x + i, y + 1] = K["r"] if i < 6 else K["s"]
        length = lengths[1] if run else lengths[0]
        for i in range(length):
            tx = x - 1 - i
            wave = [0, 0, 1, 1, 0, -1, -1, 0][(i + phase) % 8] if run else min(i, 3)
            ty = y + 1 + wave
            if 0 <= tx < F and 0 <= ty < F:
                p[tx, ty] = K["s"] if i < length - 2 else K["r"]
                if run and i < length - 1 and ty + 1 < F:
                    p[tx, ty + 1] = K["r"] if i < length - 2 else K["q"]
    return scarf


def wick_skin(skin):
    """Re-run hero.build() with another cloak and scarf (and maybe a longer scarf)."""
    saved = (hero.KEY, hero.CLOAK, hero.scarf, hero.save, hero.save_preview)
    key = dict(hero.KEY)
    for ch, c in zip("abcde", skin["cloak"]):
        key[ch] = c
    for ch, c in zip("qrst", skin["scarf"]):
        key[ch] = c
    hero.KEY = key
    hero.CLOAK = skin["cloak"]
    if skin["tail"]:
        hero.scarf = _long_scarf(skin["tail"])
    hero.save = lambda *a, **k: None
    hero.save_preview = lambda *a, **k: None
    try:
        anims = hero.build()
    finally:
        hero.KEY, hero.CLOAK, hero.scarf, hero.save, hero.save_preview = saved
    return anims


def lark_stage(stage):
    """Lark's scarf burning down as Lark gives embers away: npcs2's own hero stages
    (singed shorter at 1, a glowing stub at 2), drawn with Lark's cloak and scarf."""
    import npcs2
    saved = (hero.KEY, hero.CLOAK)
    key = dict(hero.KEY)
    for ch, c in zip("abcde", LARK["cloak"]):
        key[ch] = c
    for ch, c in zip("qrst", LARK["scarf"]):
        key[ch] = c
    hero.KEY = key
    hero.CLOAK = LARK["cloak"]
    try:
        return npcs2.hero_stage_anims(stage)   # its scarf_stage() picks up hero.KEY
    finally:
        hero.KEY, hero.CLOAK = saved


# --- Maud ---------------------------------------------------------------------

DRESS = [hexc(c) for c in ("#22101c", "#3c1b2b", "#5a2b3a", "#7c3f47", "#9f5a57")]
SHAWL = [hexc(c) for c in ("#4a2e12", "#7a5220", "#a97b33", "#d4a64f")]
KERCHIEF = [hexc(c) for c in ("#12241d", "#1f3c2e", "#2f5a41", "#457a56", "#62996c")]
DOT = WAX[4]
HANDBELL_KEY = {"h": BRASS[2], "H": BRASS[3], "I": BRASS[4], "k": BRASS[1], "W": WOOD[3],
                "w": WOOD[2], "c": BRASS[0]}
# a brass handbell on a short wooden handle (row 0 is the handle top, under Maud's mitten)
HANDBELL = [
    "..W..",
    ".kwk.",
    ".hHI.",
    "hHHIh",
    "hHHHh",
    "kkhkk",
    "..c..",
]
# Maud reuses the hero's animated cloak silhouettes as her dress (same poses, same timing),
# with a dotted kerchief instead of a hood, a shawl instead of a scarf, and the bell instead
# of the lantern. Kerchief: a round headscarf, face opening at the front, eyes like the hero's.
KERCHIEF_ROWS = [
    "....bbcccd...",
    "..bbccdedcd..",
    ".bbcedccdddd.",
    "abbcccdcdedd.",
    "abccddvvvvvdc",
    "abcedvvvvvvvc",
    "abccvvvvvvvvc",
    ".abcvvvvvvvvc",
    ".aabcvvvvvvc.",
    "...abbccccb..",
]
KERCHIEF_KEY = {"a": KERCHIEF[0], "b": KERCHIEF[1], "c": KERCHIEF[2], "d": KERCHIEF[3], "e": DOT,
                "v": VOID}
MAUD_EYES = ((7, 6), (10, 6), (7, 7), (10, 7))
MAUD_BLINK = ((7, 7), (10, 7))
KNOT = [  # the kerchief's knot and two tails, behind the head
    "..t",
    ".tt",
    "tt.",
    ".t.",
]
DRESS_KEY = {"a": DRESS[0], "b": DRESS[1], "c": DRESS[2], "d": DRESS[3], "e": DRESS[4]}
APRON_KEY = {"a": WAX[1], "A": WAX[3], "L": WAX[4]}


def maud_frame(cloak, bob=0, hood_dx=0, legs=((0, 0), (0, 0)), blink=False, scarf_phase=0,
               run=False, lantern=(0, 0), tip_dy=0):
    """Same signature and pose maths as hero.frame, so Maud moves exactly like the wick."""
    img = new(F, F)
    cx = 10
    feet = F - 1
    body_top = 21 + bob
    hood_top = body_top - 9

    (bx, blift), (fx, flift) = legs
    hero.leg(img, cx + 3 + bx, body_top + len(cloak) - 1 - blift, 3 + (feet - (body_top + len(cloak) + 1)), False)
    dress = sprite(cloak, DRESS_KEY)
    dp = dress.load()
    # apron: a cream panel down the front half of the dress, where there is dress to cover
    for y in range(2, len(cloak) - 1):
        for x in range(6, 10):
            if dp[x, y][3]:
                dp[x, y] = APRON_KEY["L"] if x == 9 else (APRON_KEY["a"] if x == 6 else APRON_KEY["A"])
    if dp[8, len(cloak) - 2][3]:
        dp[8, len(cloak) - 2] = APRON_KEY["a"]      # a little pocket seam
    paste(img, dress, cx, body_top)
    hero.leg(img, cx + 6 + fx, body_top + len(cloak) - 1 - flift, 3 + (feet - (body_top + len(cloak) + 1)), True)

    p = img.load()
    # apron strings tied at the back of the waist
    p[cx + 1, body_top + 2] = WAX[3]
    p[cx, body_top + 3] = WAX[2]
    # arm out to the bell
    lx, ly = cx + 12 + lantern[0], body_top + 2 + lantern[1]
    for i, (ax, ay) in enumerate(((cx + 9, body_top + 3), (cx + 10, body_top + 3),
                                  (cx + 11, body_top + 3 + (1 if lantern[1] > 1 else 0)))):
        p[ax, ay] = DRESS[2] if i < 2 else DRESS[3]
    # the shawl: over both shoulders (just under the kerchief), its point and fringe trailing behind
    sx, sy = cx + hood_dx // 2, body_top + 1
    for i in range(11):
        p[sx + i, sy] = SHAWL[3] if i in (6, 7, 8) else SHAWL[2]
    for i in range(10):
        p[sx + i, sy + 1] = SHAWL[2] if 2 < i < 8 else SHAWL[1]
    for i in range(1, 5):
        p[sx + i, sy + 2] = SHAWL[1]
    p[sx + 2, sy + 3] = SHAWL[1]
    length = 5 if run else 2
    for i in range(length):
        tx = sx - 1 - i
        wave = [0, 0, 1, 1, 0, -1, -1, 0][(i + scarf_phase) % 8] if run else min(i, 2)
        ty = sy + wave
        if 0 <= tx < F:
            p[tx, ty] = SHAWL[2] if i < length - 1 else SHAWL[0]
            if run and i < length - 2:
                p[tx, ty + 1] = SHAWL[1]
    # head
    paste(img, sprite(KNOT, {"t": KERCHIEF[2]}), cx - 3 + hood_dx, hood_top + 4 + tip_dy)
    head = sprite(KERCHIEF_ROWS, KERCHIEF_KEY)
    hp = head.load()
    for (ex, ey) in (MAUD_BLINK if blink else MAUD_EYES):
        hp[ex, ey] = GLOW if ey == 6 or blink else EYE
    paste(img, head, cx - 1 + hood_dx, hood_top)
    # the bell, its handle in her mitten, a sleeve reaching out to it
    rows_at(img, lx + 1, ly, HANDBELL, HANDBELL_KEY)
    p[lx, ly + (1 if ly < body_top + 3 else 0)] = DRESS[3]
    p[lx + 1, ly] = BOOT[1]
    p[lx + 2, ly] = BOOT[0]
    return outline(img, INK)


def maud_anims():
    """hero.build()'s poses, frame for frame."""
    C = hero
    idle = [
        maud_frame(C.CLOAK_IDLE, bob=0),
        maud_frame(C.CLOAK_IDLE, bob=0, lantern=(0, 1)),
        maud_frame(C.CLOAK_IDLE, bob=1, lantern=(0, 1), tip_dy=1),
        maud_frame(C.CLOAK_IDLE, bob=1, lantern=(0, 0), tip_dy=1),
        maud_frame(C.CLOAK_IDLE, bob=0, blink=True),
        maud_frame(C.CLOAK_IDLE, bob=0, lantern=(0, 1)),
    ]
    run_poses = [
        (C.CLOAK_RUN_A, 0, (-2, 0), (2, 1), (1, 1)),
        (C.CLOAK_RUN_A, -1, (-1, 1), (2, 0), (1, 2)),
        (C.CLOAK_RUN_B, 0, (0, 2), (0, 0), (0, 2)),
        (C.CLOAK_RUN_B, 0, (2, 1), (-2, 0), (0, 1)),
        (C.CLOAK_RUN_A, -1, (2, 0), (-1, 1), (1, 1)),
        (C.CLOAK_RUN_B, 0, (0, 0), (0, 2), (1, 2)),
    ]
    run = [maud_frame(c, bob=b, hood_dx=1, legs=(bl, fl), scarf_phase=i, run=True, lantern=ln,
                      tip_dy=(i % 2))
           for i, (c, b, bl, fl, ln) in enumerate(run_poses)]
    jump = [
        maud_frame(C.CLOAK_JUMP, bob=-1, legs=((-1, 2), (1, 1)), run=True, scarf_phase=2, lantern=(0, 2), tip_dy=1),
        maud_frame(C.CLOAK_JUMP, bob=-1, legs=((-1, 1), (1, 2)), run=True, scarf_phase=3, lantern=(0, 2), tip_dy=1),
    ]
    fall = [
        maud_frame(C.CLOAK_FALL, bob=-1, legs=((-1, 0), (1, 1)), run=True, scarf_phase=5, lantern=(0, -1), tip_dy=-1),
        maud_frame(C.CLOAK_FALL, bob=-1, legs=((-1, 1), (1, 0)), run=True, scarf_phase=6, lantern=(0, -1), tip_dy=-1),
    ]
    land = [
        maud_frame(C.CLOAK_LAND, bob=2, lantern=(0, 2), tip_dy=2),
        maud_frame(C.CLOAK_IDLE, bob=1, lantern=(0, 1), tip_dy=1),
    ]
    return {"idle": idle, "run": run, "jump": jump, "fall": fall, "land": land}


# ===================================================================== Glim ==

GLIM_COLD = [BONE[0], hexc("#625a6a"), BONE[1], BONE[2]]
GLIM_LIT = [hexc("#3d5a2a"), hexc("#7fae47"), hexc("#c8f07a"), hexc("#f4ffc0")]


def glim_frame(lit, arch):
    """Wisp's mama: Wisp's flat, crisp style, bigger and plumper, with a kind face."""
    W, H = 20, 12
    img = new(W, H)
    p = img.load()
    a, b, c, d = GLIM_LIT if lit else GLIM_COLD
    # tail glow, two plump body segments, a big round head; the body lifts when she breathes
    segs = [(3.4, 7.6, 2.1), (6.6, 7.1, 2.9), (10.2, 6.7, 3.2), (14.4, 6.3, 3.6)]
    for i, (sx, sy, r) in enumerate(segs):
        sy -= 1 if arch and i in (1, 2) else 0
        for y in range(H):
            for x in range(W):
                nx, ny = (x + 0.5 - sx) / r, (y + 0.5 - sy) / r
                if nx * nx + ny * ny > 1.0:
                    continue
                if i == 0:
                    col = d if ny < 0.3 else c       # the tail light
                elif ny > 0.5:
                    col = a
                elif ny < -0.25 and nx > -0.3:
                    col = c
                else:
                    col = b
                p[x, y] = col
        if 0 < i:                                    # seam where this segment meets the last
            x0 = int(sx - r + 0.6)
            for y in range(int(sy - r * 0.55), int(sy + r * 0.7)):
                if 0 <= y < H and p[x0, y][3]:
                    p[x0, y] = a
    for x in (6, 9, 12, 15):                         # little feet
        p[x, 10] = a
    # the face: a big kind eye (sleepy when cold), a smile, a blush when warm
    if lit:
        p[15, 4] = BONE[4]
        p[16, 4] = BONE[4]
        p[15, 5] = BONE[4]
        p[16, 5] = INK
        p[14, 7] = PINK[3]
    else:
        p[15, 5] = INK
        p[16, 5] = INK
        p[15, 4] = a
        p[16, 4] = a
    p[17, 7] = a
    p[16, 8] = a
    # antennae curling up and back
    for (x, y) in ((13, 2), (12, 1), (16, 2), (17, 1)):
        p[x, y] = c
    p[12, 0] = d if lit else c
    p[17, 0] = d if lit else c
    o = outline(img, INK)
    if lit:  # the tail light glows past the outline
        q = o.load()
        q[0, 7] = d
        q[0, 8] = d
    return o


def glim():
    return [glim_frame(False, False), glim_frame(False, True), glim_frame(True, False), glim_frame(True, True)]


# ===================================================================== Edda ==

EDDA_HOOD = [hexc(c) for c in ("#1d1d26", "#2e2f3c", "#454757", "#626576", "#858999")]
EDDA_ROBE = [hexc(c) for c in ("#1f1712", "#33261c", "#4c3828", "#694e36", "#866849")]
LEATHER = [hexc(c) for c in ("#3a2216", "#5e3a24", "#865634", "#a87448")]


def edda_frame(bob=0, talk=False, raise_tool=0, legs=((0, 0), (0, 0)), blink=False, step=0):
    W, H = 20, 28
    img = new(W, H)
    p = img.load()
    cx = 9
    top = 14 + bob
    (bx_, blift), (fx_, flift) = legs
    hero.leg(img, cx - 3 + bx_, 24 - blift, 4, False)
    hero.leg(img, cx + 1 + fx_, 24 - flift, 4, True)
    # robe
    for y in range(top, 26):
        hw = 4.0 + (y - top) * 0.3
        x0, x1 = int(round(cx - hw)) + (step if y > 23 else 0), int(round(cx + hw)) + (step if y > 23 else 0)
        for x in range(x0, x1 + 1):
            u = (x - x0 + 0.5) / (x1 - x0 + 1)
            p[x, y] = ramp_at(EDDA_ROBE[1:5], 0.12 + 0.8 * min(1.0, u * 1.15) - (0.22 if u > 0.9 else 0), x, y)
    # leather apron with loops of tools
    for y in range(top + 2, 25):
        for x in range(cx, cx + 4):
            p[x, y] = LEATHER[2] if x < cx + 3 else LEATHER[1]
    for x in range(cx - 4, cx + 5):
        p[x, top + 2] = LEATHER[3] if x >= cx else LEATHER[1]
    p[cx + 1, top + 5] = METAL[2]          # a spare chisel in a loop
    p[cx + 1, top + 6] = METAL[1]
    p[cx + 1, top + 7] = WOOD[2]
    # hood: rounded with a heavy tip slumped behind, dust-grey
    hx, hy = cx + 1, top - 6
    ellipse(img, hx, hy, 5.2, 5.0, EDDA_HOOD[1:5])
    for (x, y) in ((hx - 5, hy - 3), (hx - 6, hy - 2), (hx - 6, hy - 1), (hx - 7, hy)):
        p[int(x), int(y)] = EDDA_HOOD[2]
    for y in range(int(hy) - 1, int(hy) + 4):  # the dark face
        for x in range(int(hx), int(hx) + 5 - (1 if y == int(hy) + 3 else 0)):
            p[x, y] = VOID
    ex, ey = int(hx) + 1, int(hy) + 1
    # an old carver's squint under one long pale brow
    for x in range(ex - 1, ex + 4):
        p[x, ey - 1] = BONE[3] if x != ex + 1 else BONE[2]
    if blink:
        p[ex, ey + 1] = BONE[1]
        p[ex + 3, ey + 1] = BONE[1]
    else:
        p[ex, ey + 1] = GLOW
        p[ex + 3, ey + 1] = GLOW
    if talk:
        p[ex + 1, ey + 3] = hexc("#5a3a3c")
        p[ex + 2, ey + 3] = hexc("#5a3a3c")
    # arm and chisel: the chisel lifts when Edda talks
    ay = top + 2 - raise_tool
    for (x, y) in ((cx + 4, top + 2), (cx + 5, top + 2), (cx + 6, ay + 1)):
        p[x, y] = EDDA_ROBE[3]
    p[cx + 7, ay] = BOOT[1]
    for k in range(4):                     # wooden handle, then the steel blade upward
        p[cx + 7, ay - 1 - k] = METAL[2] if k >= 2 else WOOD[2]
    p[cx + 7, ay - 5] = METAL[1]
    return outline(img, INK)


def edda():
    walk = [((-1, 0), (1, 1), 0, 0), ((0, 1), (0, 0), -1, 1), ((1, 0), (-1, 1), 0, 0), ((0, 0), (0, 1), -1, -1)]
    return [
        edda_frame(0),
        edda_frame(1),
        edda_frame(0, talk=True, raise_tool=2),
        edda_frame(0, talk=False, raise_tool=1),
    ] + [edda_frame(-bb if bb else 0, legs=(bl, fl), step=st) for (bl, fl, bb, st) in walk]


# ================================================================== Keepers ==

KEEPERS = {
    "hollis": {"hood": [hexc(c) for c in ("#2e2010", "#4e3818", "#76562a", "#a07c40", "#c8a45a")],
               "robe": [hexc(c) for c in ("#2a1c12", "#4a311c", "#6e4c28", "#946b38", "#b88d4c")]},
    "fitch": {"hood": [hexc(c) for c in ("#1a2420", "#2a3b33", "#3e574a", "#587666", "#7a9784")],
              "robe": [hexc(c) for c in ("#1c2420", "#2c3a33", "#425648", "#5e7462", "#7e937e")]},
    "tobin": {"hood": [hexc(c) for c in ("#141a30", "#202c4e", "#304270", "#465c92", "#6a7eb0")],
              "robe": [hexc(c) for c in ("#161a2a", "#242a44", "#363f62", "#4e5880", "#6c769c")]},
    "pim": {"hood": [hexc(c) for c in ("#2e1610", "#4e2618", "#783c22", "#a05a30", "#c47c44")],
            "robe": [hexc(c) for c in ("#2a1812", "#46281c", "#6a3e28", "#8e5838", "#b07850")]},
    "wren": {"hood": [hexc(c) for c in ("#22182e", "#38284c", "#52406c", "#6e5a8c", "#9080ac")],
             "robe": [hexc(c) for c in ("#1e182a", "#322842", "#4a3c5e", "#64567a", "#82769a")]},
}


def keeper_body(img, k, pose, bob=0, legs=((0, 0), (0, 0)), blink=False, step=0):
    """A small Keeper. pose: 'sleep' (curled up, sitting) or 'stand'. Returns the head centre."""
    p = img.load()
    cx = 7
    hood, robe = k["hood"], k["robe"]
    if pose == "sleep":
        # a sitting mound of robe, head slumped forward on the knees
        ellipse(img, cx, 16.5 - bob * 0.5, 5.6, 3.6 + bob * 0.4, robe[1:5])
        for x in range(cx + 3, cx + 6):    # toes peeking out
            p[x, 19] = BOOT[1] if x < cx + 5 else BOOT[0]
        hx, hy = cx + 2, 12 - bob
        ellipse(img, hx, hy, 3.8, 3.5, hood[1:5])
        p[int(hx) - 4, int(hy) - 2] = hood[2]   # hood tip flopped back
        p[int(hx) - 5, int(hy) - 1] = hood[2]
        for y in range(int(hy), int(hy) + 3):
            for x in range(int(hx), int(hx) + 4):
                p[x, y] = VOID
        p[int(hx) + 1, int(hy) + 2] = hexc("#5c5866")   # shut eyes: dim and low
        p[int(hx) + 3, int(hy) + 2] = hexc("#5c5866")
        return hx, hy
    (bx_, blift), (fx_, flift) = legs
    hero.leg(img, cx - 3 + bx_, 17 - blift, 3, False)
    hero.leg(img, cx + 1 + fx_, 17 - flift, 3, True)
    top = 10 + bob
    for y in range(top, 18):
        hw = 3.2 + (y - top) * 0.32
        sh = step if y > 15 else 0
        x0, x1 = int(round(cx - hw)) + sh, int(round(cx + hw)) + sh
        for x in range(x0, x1 + 1):
            u = (x - x0 + 0.5) / (x1 - x0 + 1)
            p[x, y] = ramp_at(robe[1:5], 0.12 + 0.8 * min(1.0, u * 1.15) - (0.22 if u > 0.9 else 0), x, y)
    hx, hy = cx + 1, top - 4
    ellipse(img, hx, hy, 4.0, 3.8, hood[1:5])
    p[int(hx) - 4, int(hy) - 3] = hood[2]
    p[int(hx) - 5, int(hy) - 2] = hood[2]
    for y in range(int(hy) - 1, int(hy) + 3):
        for x in range(int(hx), int(hx) + 4 - (1 if y == int(hy) + 2 else 0)):
            p[x, y] = VOID
    ex, ey = int(hx) + 1, int(hy)
    if blink:
        p[ex, ey + 1] = GLOW
        p[ex + 2, ey + 1] = GLOW
    else:
        p[ex, ey] = EYE
        p[ex + 2, ey] = EYE
    p[cx + 3, top + 3] = robe[3]             # a little mitten
    p[cx + 4, top + 3] = BOOT[1]
    return hx, hy


def keeper_extra(img, kid, pose, hx, hy, frame_i):
    """Each Keeper's tell: hat, scarf, apron, broom or bird."""
    p = img.load()
    hx, hy = int(hx), int(hy)
    if kid == "hollis":                   # straw bee-hat with a veil
        straw = [WAX[2], WAX[3], WAX[4]]
        for x in range(hx - 5, hx + 5):
            p[x, hy - 3] = straw[1] if x < hx + 3 else straw[2]
        for x in range(hx - 2, hx + 2):
            p[x, hy - 4] = straw[0]
            p[x, hy - 5] = straw[1]
        for y in range(hy - 2, hy + 2):    # the veil: a fine mesh over the face
            for x in range(hx, hx + 5):
                if (x + y) % 2 == 0 and p[x, y][3]:
                    p[x, y] = hexc("#8a8c78")
        if pose != "sleep" and frame_i % 2 == 0:   # a bee
            p[hx + 6, hy - 5] = FIRE[4]
            p[hx + 7, hy - 5] = INK
    elif kid == "fitch":                  # a long scarf, trailing to the ground
        sc = [RED[1], RED[2], RED[3]]
        ny = hy + 3 if pose != "sleep" else hy + 3
        for x in range(hx - 3, hx + 3):
            p[x, ny] = sc[2] if x % 2 else sc[1]
        if pose == "sleep":
            for i in range(5):
                p[hx - 4 - i, ny + 1 + i // 2] = sc[1] if i % 2 else sc[2]
        else:
            wave = frame_i % 2
            for i in range(7):
                x = hx - 4 - i // 2
                y = ny + 1 + i
                if y < 20 and x >= 0:
                    p[x - (wave if i > 3 else 0), y] = sc[1] if (i // 2) % 2 else sc[2]
    elif kid == "tobin":                  # mender's apron and a hammer at the belt
        if pose == "sleep":
            for x in range(hx - 1, hx + 3):
                p[x, 15] = LEATHER[2]
                p[x, 16] = LEATHER[1]
        else:
            for y in range(hy + 5, hy + 11):
                for x in range(hx - 1, hx + 3):
                    if p[x, y][3]:
                        p[x, y] = LEATHER[2] if x < hx + 2 else LEATHER[1]
            for (x, y) in ((hx - 3, hy + 7), (hx - 3, hy + 8), (hx - 3, hy + 9)):
                p[x, y] = WOOD[2]
            p[hx - 4, hy + 7] = METAL[2]
            p[hx - 2, hy + 7] = METAL[1]
    elif kid == "pim":                    # a broom
        if pose == "sleep":
            for i in range(9):            # leaning against them
                p[1 + i, 19 - i // 2] = WOOD[2] if i > 2 else WAX[3]
        else:
            bx = hx + 5
            for y in range(hy - 2, 16):
                p[bx, y] = WOOD[3] if y % 3 else WOOD[2]
            for y in range(16, 20):
                for x in range(bx - 1, bx + 2):
                    p[x, y] = WAX[3] if (x + y) % 2 else WAX[2]
    elif kid == "wren":                   # a little songbird on the shoulder
        by = hy + 3 if pose != "sleep" else hy - 4
        bxx = hx - 4 if pose != "sleep" else hx - 1
        bird = [".bb.", "bBBk", ".bb."] if not (pose != "sleep" and frame_i % 2) else [".bb.", "bBBk", "bbb."]
        rows_at(img, bxx, by - 2, bird, {"b": hexc("#8a4a2a"), "B": hexc("#c87a44"), "k": FIRE[3]})


def keeper(kid):
    k = KEEPERS[kid]
    frames = []
    for i in range(8):
        img = new(16, 20)
        if i < 2:
            hx, hy = keeper_body(img, k, "sleep", bob=i)
            keeper_extra(img, kid, "sleep", hx, hy, i)
            o = outline(img, INK)
            if i == 1:                     # a little 'z' drifting up
                rows_at(o, 11, 1, ["zzz", "..z", ".z.", "zzz"][:0] + ["zz", ".z", "zz"],
                        {"z": BONE[3]})
            else:
                rows_at(o, 12, 4, ["z"], {"z": BONE[2]})
            frames.append(o)
            continue
        if i < 4:
            hx, hy = keeper_body(img, k, "stand", bob=i - 2, blink=False)
        else:
            j = i - 4
            legs = [((-1, 0), (1, 1)), ((0, 1), (0, 0)), ((1, 0), (-1, 1)), ((0, 0), (0, 1))][j]
            hx, hy = keeper_body(img, k, "stand", bob=-1 if j % 2 else 0, legs=legs,
                                 step=[0, -1, 0, 1][j])
        keeper_extra(img, kid, "stand", hx, hy, i)
        frames.append(outline(img, INK))
    return frames


# ================================================================ keepsakes ==

def keepsake_lantern():
    img = new(16, 16)
    cold = {"m": METAL[0], "n": METAL[1], "o": METAL[2], "g": hexc("#22283a"), "G": hexc("#3a4258"),
            "s": hexc("#58606e")}
    rows_at(img, 4, 1, [
        "..mmm..",
        ".m...m.",
        "..non..",
        ".nnnnn.",
        "mgGsGgm",
        "mgGgGgm",
        "mgsgGgm",
        "mgGgGgm",
        "mgggggm",
        ".nnnnn.",
        "mmmmmmm",
    ], cold)
    p = img.load()
    p[7, 7] = hexc("#7a7480")             # a cold, curled-up wick
    p[7, 8] = hexc("#4b4552")
    return outline(img, INK)


def keepsake_bell():
    img = new(16, 16)
    rows_at(img, 4, 1, [
        "...W...",
        "...W...",
        "...w...",
        "..kwk..",
        "..hHI..",
        ".hHHIh.",
        ".hHHIh.",
        "hHHHHIh",
        "hHHHHHh",
        "kkkhkkk",
        "...c...",
    ], HANDBELL_KEY)
    p = img.load()
    p[6, 6] = BRASS[4]                    # a glint
    p[5, 8] = BRASS[4]
    return outline(img, INK)


def keepsake_page():
    img = new(16, 16)
    slate = [hexc(c) for c in ("#26283a", "#3a3e52", "#555b70", "#737a8e")]
    p = img.load()
    for y in range(2, 14):
        for x in range(2, 14):
            if (x in (2, 13) and y in (2, 13)):
                continue
            t = 0.45 + 0.35 * ((x - 2) / 11) - 0.3 * ((y - 2) / 11)
            p[x, y] = ramp_at(slate[1:4], t, x, y)
    # a chipped corner, carved lines, and a little flame glyph
    p[13, 3] = (0, 0, 0, 0)
    p[12, 2] = (0, 0, 0, 0)
    for y in (5, 7, 9, 11):
        for x in range(4, 12 - (2 if y == 11 else 0)):
            if (x * 3 + y) % 5:
                p[x, y] = slate[0]
    rows_at(img, 10, 3, [".F", "FG", "F."], {"F": FIRE[3], "G": FIRE[4]})
    return outline(img, INK)


# ============================================================ Sprig, taller ==

def sapling_big(W, H, trunk_h, crown, sway, branches, face_y, glows, roots_w):
    img = new(W, H)
    p = img.load()
    mid = W // 2
    # soil and roots
    rw = roots_w
    rows_at(img, mid - rw // 2, H - 4, ["." + "b" * (rw - 2) + ".", "b" * rw, "a" * rw],
            {"a": ROCK[1], "b": ROCK[2]})
    for k in range(4):
        p[mid - 3 - k, H - 5 + (k // 2)] = WOOD[2]
        p[mid + 3 + k, H - 5 + (k // 2)] = WOOD[2]
    # trunk: thicker at the base, leaning with the sway up top
    base = H - 5
    for y in range(base - trunk_h, base + 1):
        k = (base - y) / trunk_h
        w = 3 if k < 0.5 else 2
        x = mid - 1 + (sway if k > 0.55 else 0)
        for dx in range(w + (1 if k < 0.2 else 0)):
            p[x + dx, y] = WOOD[3] if dx == 0 else WOOD[2]
        if k < 0.15:
            p[x - 1, y] = WOOD[2]
    for (bx, by, length, d) in branches:
        for k in range(length):
            p[bx + d * k + (sway if by < base - trunk_h * 0.5 else 0), by - k] = WOOD[2]
    circles = [(cx + sway, cy, r) for (cx, cy, r) in crown]
    paste(img, soft_blob(W, H, circles, GRASS[1:6]), 0, 0)
    # Sprig's face on the trunk, smiling
    p[mid - 1, face_y] = INK
    p[mid + 1, face_y] = INK
    p[mid, face_y + 1] = WOOD[1]
    o = outline(img, INK)
    q = o.load()
    for (x, y) in glows:
        if 0 <= x + sway < W and q[x + sway, y][3] and q[x + sway, y] != INK:
            q[x + sway, y] = LEAF_GLOW
    return o


def sapling_2(i):
    W, H = 40, 56
    crown = [(20, 15, 11.0), (12, 19, 7.5), (28, 19, 7.5), (20, 8, 7.0), (15, 11, 6.0), (26, 11, 6.0)]
    return sapling_big(W, H, 30, crown, i, [(21, 32, 6, 1), (18, 36, 5, -1)], 41,
                       [(10, 16), (29, 13), (20, 4), (14, 23), (31, 21), (23, 18)], 16)


def sapling_3(i):
    W, H = 56, 76
    crown = [(28, 20, 15.0), (16, 26, 10.0), (40, 26, 10.0), (28, 9, 9.0), (20, 13, 8.5), (37, 13, 8.5),
             (10, 31, 6.0), (46, 31, 6.0)]
    return sapling_big(W, H, 42, crown, i, [(29, 44, 8, 1), (26, 48, 7, -1), (29, 38, 6, 1)], 58,
                       [(12, 21), (42, 17), (28, 4), (19, 31), (44, 29), (33, 22), (8, 30), (24, 12), (47, 33)],
                       22)


# ======================================================================= fx ==

def ring():
    S = 96
    img = new(S, S)
    p = img.load()
    c = S / 2
    for y in range(S):
        for x in range(S):
            d = math.hypot(x + 0.5 - c, y + 0.5 - c)
            # a bright band at r=42 that fades out both ways, a faint wash inside
            a = math.exp(-((d - 42.0) / 3.2) ** 2) + 0.12 * max(0.0, min(1.0, (42.0 - d) / 42.0)) ** 1.5
            if d > 47.5:
                a = 0.0
            a = max(0.0, min(1.0, a))
            if a > 0.01:
                p[x, y] = (255, 255, 255, int(a * 255))
    return img


# ===================================================================== deco ==

def supper_table():
    W, H = 80, 18
    img = new(W, H)
    p = img.load()
    # the top, with a lighter front edge
    for x in range(2, W - 2):
        p[x, 9] = WOOD[4]
        p[x, 10] = WOOD[3]
        p[x, 11] = WOOD[2]
        if x % 13 == 0:
            p[x, 10] = WOOD[2]           # board seams
    for lx in (5, 6, W - 7, W - 6, 38, 39):  # legs
        for y in range(12, 18):
            p[lx, y] = WOOD[2] if lx % 2 else WOOD[1]
    for x in range(7, W - 7):           # a stretcher between the legs
        p[x, 15] = WOOD[1]
    # bowls, a loaf, a jug and a candle
    for bx in (10, 24, 50, 64):            # wide shallow bowls of soup
        rows_at(img, bx, 6, ["rssssr", "bBBBBb", ".bbbb."],
                {"r": BONE[3], "s": hexc("#c8843c"), "B": STONE[3], "b": STONE[2]})
    rows_at(img, 34, 3, [".llll.", "lLLLLl", "lLLLLl", "dddddd"],
            {"l": BRASS[2], "L": BRASS[3], "d": BRASS[1]})        # the loaf
    rows_at(img, 43, 1, [".jj.", "jJJj", "jJJj", "jJJj", ".jj.", "jjjj"],
            {"j": hexc("#5a6a8a"), "J": hexc("#7a8eaa")})          # a jug
    rows_at(img, 58, 2, [".F.", ".G.", ".w.", ".w.", ".w.", "kkk"],
            {"F": FIRE[4], "G": FIRE[5], "w": WAX[4], "k": BRASS[1]})  # a candle
    o = outline(img, INK)
    q = o.load()
    for (x, y) in ((12, 4), (13, 3), (26, 4), (27, 3), (52, 3), (53, 4), (66, 4)):   # steam, unoutlined
        q[x, y] = (230, 230, 240, 140)
    return o


def bunting():
    W, H = 96, 14
    img = new(W, H)
    p = img.load()
    cols = [SCARF[2], GRASS[3], PINK[3], BONE[3], CRYSTAL[2], FIRE[3]]
    sag = lambda x: int(round(5 * math.sin(math.pi * x / (W - 1))))
    for x in range(W):
        p[x, sag(x)] = WOOD[1]
    for i, x0 in enumerate(range(4, W - 6, 9)):
        c = cols[i % len(cols)]
        dark = (int(c[0] * 0.7), int(c[1] * 0.7), int(c[2] * 0.7), 255)
        top = sag(x0 + 3) + 1
        for r in range(6):
            for x in range(x0 + r // 2, x0 + 7 - r // 2):
                if top + r < H:
                    p[x, top + r] = c if x < x0 + 5 - r // 3 else dark
    return outline(img, INK)


def bell_post():
    W, H = 14, 34
    img = new(W, H)
    p = img.load()
    for y in range(4, 31):               # the post
        p[4, y] = WOOD[3]
        p[5, y] = WOOD[2]
    for x in range(4, 12):               # the arm
        p[x, 4] = WOOD[3]
        p[x, 5] = WOOD[2]
    p[6, 6] = WOOD[2]                    # brace
    p[7, 7] = WOOD[2]
    p[10, 6] = METAL[1]                  # hook
    rows_at(img, 8, 7, ["..W..", ".kwk.", ".hHI.", "hHHIh", "hHHHh", "kkhkk", "..c.."], HANDBELL_KEY)
    rows_at(img, 1, 30, ["aabbbbbaa", "abbbbbbba", "aaaaaaaaa"][:3], {"a": STONE[1], "b": STONE[2]})
    p[11, 9] = BRASS[4]
    return outline(img, INK)


def keeper_lamp():
    W, H = 12, 16
    img = new(W, H)
    rows_at(img, 1, 0, [
        "mmmmm.....",
        "....n.....",
        "...mnm....",
        "..mmmmm...",
        "..mFGFm...",
        "..mGHGm...",
        "..mGHGm...",
        "..mFGFm...",
        "..mmmmm...",
        "...mnm....",
        "....m.....",
    ], {"m": METAL[0], "n": METAL[1], "F": FIRE[3], "G": FIRE[4], "H": FIRE[5]})
    p = img.load()
    for y in range(0, 13):               # the wall bracket
        p[1, y] = METAL[1]
    o = outline(img, INK)
    q = o.load()
    q[4, 5] = FIRE[2]                     # warm light spilling on the frame
    return o


def lamp_string():
    W, H = 96, 16
    img = new(W, H)
    p = img.load()
    sag = lambda x: int(round(6 * math.sin(math.pi * x / (W - 1))))
    for x in range(W):
        p[x, sag(x)] = WOOD[1]
    for i, x0 in enumerate(range(8, W - 6, 14)):
        y0 = sag(x0 + 1) + 1
        p[x0 + 1, y0] = METAL[1]
        rows_at(img, x0, y0 + 1, ["mmm", "FHF", "GHG", "mmm"],
                {"m": METAL[0], "F": FIRE[3], "G": FIRE[4], "H": FIRE[5]})
    return outline(img, INK)


def banner():
    W, H = 18, 34
    img = new(W, H)
    p = img.load()
    cloth = [hexc(c) for c in ("#3a1220", "#5e1c30", "#842a40", "#a84050")]
    for x in range(1, W - 1):            # the rod
        p[x, 1] = WOOD[3]
        p[x, 2] = WOOD[2]
    p[0, 1] = BRASS[3]
    p[W - 1, 1] = BRASS[3]
    for y in range(3, 31):
        for x in range(3, W - 3):
            # swallowtail at the bottom
            if y > 26 and abs(x - W / 2 + 0.5) < (y - 26) * 0.9:
                continue
            u = (x - 3) / (W - 7)
            p[x, y] = cloth[1] if u < 0.2 else (cloth[3] if u > 0.75 else cloth[2])
    for x in range(3, W - 3):            # gold borders
        p[x, 4] = BRASS[3]
    for y in range(4, 27):
        p[4, y] = BRASS[2]
        p[W - 5, y] = BRASS[2]
    # the Keepers' flame on it
    rows_at(img, 6, 11, ["..G..", ".GHG.", ".GHG.", "GHHHG", "GHHHG", ".GGG.", "..k.."],
            {"G": FIRE[3], "H": FIRE[4], "k": BRASS[2]})
    return outline(img, INK)


# ==================================================================== build ==

def build():
    out = {}
    # hero skins
    heroes = {"lark": wick_skin(LARK), "vesper": wick_skin(VESPER), "maud": maud_anims()}
    for skin, anims in heroes.items():
        for a in ANIMS:
            save(sheet(anims[a]), f"sprites/hero_{a}_{skin}.png")
    out["heroes"] = heroes
    # Lark's scarf burns down too: hero_<anim>_lark_s1 / _s2
    lark_stages = {1: lark_stage(1), 2: lark_stage(2)}
    for stage, anims in lark_stages.items():
        for a in ANIMS:
            save(sheet(anims[a]), f"sprites/hero_{a}_lark_s{stage}.png")
    strips = [sheet(sum((a[n] for n in ANIMS), [])) for a in (heroes["lark"], lark_stages[1], lark_stages[2])]
    save_preview(_stack(strips), "echoes_lark_stages.png", 4)
    # characters
    sheets = {
        "glim": sheet(glim()),
        "edda": sheet(edda()),
    }
    for kid in KEEPERS:
        sheets[f"keeper_{kid}"] = sheet(keeper(kid))
    for name, img in sheets.items():
        save(img, f"sprites/{name}.png")
    save(sheet([keepsake_lantern(), keepsake_bell(), keepsake_page()]), "sprites/keepsake.png")
    save(sheet([sapling_2(0), sapling_2(1)]), "sprites/sapling_tree_2.png")
    save(sheet([sapling_3(0), sapling_3(1)]), "sprites/sapling_tree_3.png")
    save(ring(), "fx/ring.png")
    deco = {"supper_table": supper_table(), "bunting": bunting(), "bell_post": bell_post(),
            "keeper_lamp": keeper_lamp(), "lamp_string": lamp_string(), "banner": banner()}
    for name, img in deco.items():
        save(img, f"deco/{name}.png")
    previews(heroes, sheets, deco)


def _stack(rows, gap=4, bg=(40, 44, 60, 255)):
    w = max(r.width for r in rows) + gap * 2
    h = sum(r.height for r in rows) + gap * (len(rows) + 1)
    out = new(w, h, bg)
    y = gap
    for r in rows:
        out.alpha_composite(r, (gap, y))
        y += r.height + gap
    return out


def _row(imgs, gap=4):
    w = sum(i.width for i in imgs) + gap * (len(imgs) - 1)
    h = max(i.height for i in imgs)
    out = new(w, h)
    x = 0
    for i in imgs:
        out.alpha_composite(i, (x, h - i.height))
        x += i.width + gap
    return out


def previews(heroes, sheets, deco):
    import os
    from pix import ASSETS
    load = lambda rel: Image.open(os.path.join(ASSETS, rel)).convert("RGBA")
    rows = []
    for skin in ("lark", "vesper", "maud"):
        a = heroes[skin]
        rows.append(sheet(a["idle"] + a["run"] + a["jump"] + a["fall"] + a["land"]))
    base = [load(f"sprites/hero_{a}.png") for a in ANIMS]
    rows.insert(0, _row(base, 0))
    save_preview(_stack(rows), "echoes_heroes.png", 4)
    npc_rows = [sheets["glim"], sheets["edda"]] + [sheets[f"keeper_{k}"] for k in KEEPERS]
    npc_rows.append(load("sprites/keepsake.png"))
    save_preview(_stack(npc_rows), "echoes_npcs.png", 5)
    props = _row([load("sprites/sapling_tree.png"), load("sprites/sapling_tree_2.png"),
                  load("sprites/sapling_tree_3.png")], 8)
    deco_row = _row([deco["supper_table"], deco["bell_post"], deco["keeper_lamp"], deco["banner"]], 8)
    hang_row = _row([deco["bunting"], deco["lamp_string"]], 8)
    save_preview(_stack([props, deco_row, hang_row, load("fx/ring.png")]), "echoes_props.png", 4)
    # everyone side by side at game scale, on a dark ground line
    lineup = _row([heroes["lark"]["idle"][0], heroes["vesper"]["idle"][0], heroes["maud"]["idle"][0],
                   load("sprites/hero_idle.png").crop((0, 0, 32, 32)),
                   load("sprites/orrin.png").crop((0, 0, 24, 28)),
                   load("sprites/bell.png").crop((28, 0, 42, 20)),
                   sheets["edda"].crop((0, 0, 20, 28))]
                  + [sheets[f"keeper_{k}"].crop((32, 0, 48, 20)) for k in KEEPERS]
                  + [sheets["glim"].crop((40, 0, 60, 12)), load("sprites/wisp.png").crop((24, 0, 36, 8))], 2)
    save_preview(_stack([lineup], bg=(22, 26, 42, 255)), "echoes_scale.png", 5)


if __name__ == "__main__":
    build()
    print("echoes art written")
