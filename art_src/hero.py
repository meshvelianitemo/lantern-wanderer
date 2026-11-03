"""The hooded lantern wanderer.

Built from hand-placed ASCII parts which are posed per frame, then given an
automatic dark outline. Frames are 32x32, feet on the bottom row, facing right.
"""
from pix import (CLOAK, FIRE, GLOW, INK, SCARF, hexc, new, outline, paste, save,
                 save_preview, sheet, sprite)

F = 32
VOID = hexc("#0a0610")
BOOT = (hexc("#2a1c26"), hexc("#46303a"))
METAL = (hexc("#2a2330"), hexc("#4f4658"), hexc("#7b7286"))

KEY = {
    "a": CLOAK[0], "b": CLOAK[1], "c": CLOAK[2], "d": CLOAK[3], "e": CLOAK[4],
    "v": VOID, "y": GLOW, "w": hexc("#fffbe6"),
    "q": SCARF[0], "r": SCARF[1], "s": SCARF[2], "t": SCARF[3],
    "k": BOOT[0], "l": BOOT[1],
    "m": METAL[0], "n": METAL[1], "o": METAL[2],
    "F": FIRE[3], "G": FIRE[4], "H": FIRE[5],
}

HOOD = [
    "......cdd.....",
    "....ccddedd...",
    "...bcddeeedd..",
    "..bccddeeeddc.",
    ".bbccdddddddcc",
    ".bbcccddvvvvvc",
    "abbcccdvvvvvvc",
    "abbccdvvvvvvvc",
    "abbccdvvvvvvvc",
    ".abbccvvvvvvcb",
    "..abbbcccccbb.",
]
HOOD_TIP = [  # floppy point trailing behind the hood
    "...bb",
    "..bcc",
    ".bc..",
    "bb...",
]
EYES_OPEN = [(9, 7), (12, 7), (9, 8), (12, 8)]
EYES_BLINK = [(9, 8), (12, 8)]

CLOAK_IDLE = [
    "...bbcddc...",
    "..abccdddc..",
    "..abccdddcc.",
    ".aabbccdddc.",
    ".aabbccdddcc",
    "aaabbcccddcc",
    "aaabbbcccccb",
    "aa.abbb.bbb.",
]
CLOAK_RUN_A = [  # hem trailing behind (left)
    "....bbcddc..",
    "...abccdddc.",
    "..aabccdddc.",
    ".aabbccdddcc",
    "aaabbccdddcc",
    "aaabbbcccdcc",
    "a.aabbbcccb.",
    "..a..abb.b..",
]
CLOAK_RUN_B = [
    "....bbcddc..",
    "...abccdddc.",
    "..aabccdddcc",
    ".aabbccdddcc",
    ".aabbccddccc",
    "aaabbbcccccb",
    "aa.abbbbbbb.",
    "a....bb..b..",
]
CLOAK_JUMP = [
    "...bbcddc...",
    "..abccdddc..",
    "..abccdddc..",
    "..abbccddc..",
    ".aabbccdddc.",
    ".aabbbcccdc.",
    ".a.abbbbbb..",
    "...a..b.....",
]
CLOAK_FALL = [  # hem billows upward
    "...bbcddc...",
    "a.abccdddc.c",
    "aaabccdddccc",
    ".aabbccdddc.",
    ".aabbccdddc.",
    "aaabbbcccdcc",
    "aa.abbbbbcbb",
    "a.........b.",
]
CLOAK_LAND = [
    "..bbbcddcc..",
    ".aabccdddcc.",
    ".aabbccdddcc",
    "aaabbccdddcc",
    "aaabbbccddcc",
    "aaaabbbccccb",
    "aa.aabbbbbb.",
]

LANTERN = [
    "..n..",
    ".mnm.",
    "mnnnm",
    "mGHGm",
    "mGHGm",
    "mFGFm",
    ".mnm.",
]
LANTERN_DIM = [
    "..n..",
    ".mnm.",
    "mnnnm",
    "mFGFm",
    "mFGFm",
    "mFFFm",
    ".mnm.",
]


def leg(img, x, y_top, h, front):
    """Draw a 2px wide leg ending in a boot at (x, y_top)..(x, y_top+h-1)."""
    p = img.load()
    for yy in range(y_top, y_top + h):
        if 0 <= yy < F:
            p[x, yy] = BOOT[1] if front else BOOT[0]
            p[x + 1, yy] = BOOT[0]
    by = y_top + h - 1
    if 0 <= by < F and x + 2 < F:
        p[x + 2, by] = BOOT[1] if front else BOOT[0]


def scarf(img, x, y, phase, run):
    """Neck wrap plus a fluttering tail streaming backwards."""
    p = img.load()
    for i in range(7):
        p[x + i, y] = KEY["t"] if i in (4, 5) else KEY["s"]
        p[x + i, y + 1] = KEY["r"] if i < 6 else KEY["s"]
    length = 6 if run else 3
    for i in range(length):
        tx = x - 1 - i
        wave = [0, 0, 1, 1, 0, -1, -1, 0][(i + phase) % 8] if run else min(i, 2)
        ty = y + 1 + wave
        if 0 <= tx < F:
            p[tx, ty] = KEY["s"] if i < length - 2 else KEY["r"]
            if run and i < length - 1:
                p[tx, ty + 1] = KEY["r"] if i < length - 2 else KEY["q"]


def frame(cloak, bob=0, hood_dx=0, legs=((0, 0), (0, 0)), blink=False, scarf_phase=0,
          run=False, lantern=(0, 0), tip_dy=0, dim=False):
    img = new(F, F)
    cx = 10                               # left edge of the body art
    feet = F - 1
    body_top = 21 + bob
    hood_top = body_top - 9

    # back leg, body, front leg
    (bx, blift), (fx, flift) = legs
    leg(img, cx + 3 + bx, body_top + len(cloak) - 1 - blift, 3 + (feet - (body_top + len(cloak) + 1)), False)
    paste(img, sprite(cloak, KEY), cx, body_top)
    leg(img, cx + 6 + fx, body_top + len(cloak) - 1 - flift, 3 + (feet - (body_top + len(cloak) + 1)), True)

    # arm reaching forward to the lantern
    lx, ly = cx + 12 + lantern[0], body_top + 2 + lantern[1]
    p = img.load()
    for i, (ax, ay) in enumerate(((cx + 9, body_top + 3), (cx + 10, body_top + 3), (cx + 11, body_top + 3 + (1 if lantern[1] > 1 else 0)))):
        p[ax, ay] = CLOAK[2] if i < 2 else CLOAK[3]
    p[lx + 1, ly] = BOOT[1]               # hand on the handle

    paste(img, sprite(HOOD_TIP, KEY), cx - 3 + hood_dx, hood_top + 1 + tip_dy)
    hood = sprite(HOOD, KEY)
    hp = hood.load()
    for (ex, ey) in (EYES_BLINK if blink else EYES_OPEN):
        hp[ex, ey] = GLOW if ey == 7 or blink else hexc("#fffbe6")
    paste(img, hood, cx - 1 + hood_dx, hood_top)
    scarf(img, cx + 2 + hood_dx // 2, body_top + 1, scarf_phase, run)
    paste(img, sprite(LANTERN_DIM if dim else LANTERN, KEY), lx, ly)
    return outline(img, INK)


def build():
    idle = [
        frame(CLOAK_IDLE, bob=0),
        frame(CLOAK_IDLE, bob=0, lantern=(0, 1)),
        frame(CLOAK_IDLE, bob=1, lantern=(0, 1), tip_dy=1),
        frame(CLOAK_IDLE, bob=1, lantern=(0, 0), tip_dy=1),
        frame(CLOAK_IDLE, bob=0, blink=True),
        frame(CLOAK_IDLE, bob=0, lantern=(0, 1)),
    ]
    # Each run pose: (cloak, bob, back leg (dx, lift), front leg (dx, lift), lantern swing)
    run_poses = [
        (CLOAK_RUN_A, 0, (-2, 0), (2, 1), (1, 1)),
        (CLOAK_RUN_A, -1, (-1, 1), (2, 0), (1, 2)),
        (CLOAK_RUN_B, 0, (0, 2), (0, 0), (0, 2)),
        (CLOAK_RUN_B, 0, (2, 1), (-2, 0), (0, 1)),
        (CLOAK_RUN_A, -1, (2, 0), (-1, 1), (1, 1)),
        (CLOAK_RUN_B, 0, (0, 0), (0, 2), (1, 2)),
    ]
    run = [frame(c, bob=b, hood_dx=1, legs=(bl, fl), scarf_phase=i, run=True, lantern=ln,
                 tip_dy=(i % 2))
           for i, (c, b, bl, fl, ln) in enumerate(run_poses)]
    jump = [
        frame(CLOAK_JUMP, bob=-1, legs=((-1, 2), (1, 1)), run=True, scarf_phase=2, lantern=(0, 2), tip_dy=1),
        frame(CLOAK_JUMP, bob=-1, legs=((-1, 1), (1, 2)), run=True, scarf_phase=3, lantern=(0, 2), tip_dy=1),
    ]
    fall = [
        frame(CLOAK_FALL, bob=-1, legs=((-1, 0), (1, 1)), run=True, scarf_phase=5, lantern=(0, -1), tip_dy=-1),
        frame(CLOAK_FALL, bob=-1, legs=((-1, 1), (1, 0)), run=True, scarf_phase=6, lantern=(0, -1), tip_dy=-1),
    ]
    land = [
        frame(CLOAK_LAND, bob=2, lantern=(0, 2), tip_dy=2),
        frame(CLOAK_IDLE, bob=1, lantern=(0, 1), tip_dy=1),
    ]
    anims = {"idle": idle, "run": run, "jump": jump, "fall": fall, "land": land}
    for name, frames in anims.items():
        save(sheet(frames), f"sprites/hero_{name}.png")
    allf = idle + run + jump + fall + land
    save_preview(sheet(allf, 6), "hero_all.png", 6)
    return anims


if __name__ == "__main__":
    build()
