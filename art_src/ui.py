"""Hand-made proportional pixel font (BMFont .fnt for Godot) and UI frames."""
import os

from pix import (ASSETS, BONE, CRYSTAL, FIRE, GLOW, GRASS, INK, RED, SKY, WOOD, CLEAR, hexc, new,
                 outline, paste, save, save_preview, sprite)

# 7px cap height; lowercase glyphs carry 2 extra descender rows.
GLYPHS = {
    "A": ".###.|#...#|#...#|#####|#...#|#...#|#...#",
    "B": "####.|#...#|#...#|####.|#...#|#...#|####.",
    "C": ".###.|#...#|#....|#....|#....|#...#|.###.",
    "D": "####.|#...#|#...#|#...#|#...#|#...#|####.",
    "E": "#####|#....|#....|####.|#....|#....|#####",
    "F": "#####|#....|#....|####.|#....|#....|#....",
    "G": ".###.|#...#|#....|#.###|#...#|#...#|.####",
    "H": "#...#|#...#|#...#|#####|#...#|#...#|#...#",
    "I": "###|.#.|.#.|.#.|.#.|.#.|###",
    "J": "..###|...#.|...#.|...#.|#..#.|#..#.|.##..",
    "K": "#...#|#..#.|#.#..|##...|#.#..|#..#.|#...#",
    "L": "#....|#....|#....|#....|#....|#....|#####",
    "M": "#...#|##.##|#.#.#|#.#.#|#...#|#...#|#...#",
    "N": "#...#|##..#|#.#.#|#..##|#...#|#...#|#...#",
    "O": ".###.|#...#|#...#|#...#|#...#|#...#|.###.",
    "P": "####.|#...#|#...#|####.|#....|#....|#....",
    "Q": ".###.|#...#|#...#|#...#|#.#.#|#..#.|.##.#",
    "R": "####.|#...#|#...#|####.|#.#..|#..#.|#...#",
    "S": ".####|#....|#....|.###.|....#|....#|####.",
    "T": "#####|..#..|..#..|..#..|..#..|..#..|..#..",
    "U": "#...#|#...#|#...#|#...#|#...#|#...#|.###.",
    "V": "#...#|#...#|#...#|#...#|.#.#.|.#.#.|..#..",
    "W": "#...#|#...#|#...#|#.#.#|#.#.#|##.##|#...#",
    "X": "#...#|#...#|.#.#.|..#..|.#.#.|#...#|#...#",
    "Y": "#...#|#...#|.#.#.|..#..|..#..|..#..|..#..",
    "Z": "#####|....#|...#.|..#..|.#...|#....|#####",
    "a": ".....|.....|.###.|....#|.####|#...#|.####",
    "b": "#....|#....|####.|#...#|#...#|#...#|####.",
    "c": "....|....|.###|#...|#...|#...|.###",
    "d": "....#|....#|.####|#...#|#...#|#...#|.####",
    "e": ".....|.....|.###.|#...#|#####|#....|.###.",
    "f": "..##|.#..|.#..|###.|.#..|.#..|.#..",
    "g": ".....|.....|.####|#...#|#...#|#...#|.####|....#|.###.",
    "h": "#....|#....|####.|#...#|#...#|#...#|#...#",
    "i": "#|.|#|#|#|#|#",
    "j": "..#|...|..#|..#|..#|..#|..#|#.#|.#.",
    "k": "#...|#...|#..#|#.#.|##..|#.#.|#..#",
    "l": "#.|#.|#.|#.|#.|#.|.#",
    "m": ".....|.....|##.#.|#.#.#|#.#.#|#.#.#|#.#.#",
    "n": ".....|.....|####.|#...#|#...#|#...#|#...#",
    "o": ".....|.....|.###.|#...#|#...#|#...#|.###.",
    "p": ".....|.....|####.|#...#|#...#|#...#|####.|#....|#....",
    "q": ".....|.....|.####|#...#|#...#|#...#|.####|....#|....#",
    "r": "....|....|#.##|##..|#...|#...|#...",
    "s": ".....|.....|.####|#....|.###.|....#|####.",
    "t": ".#..|.#..|###.|.#..|.#..|.#..|..##",
    "u": ".....|.....|#...#|#...#|#...#|#...#|.####",
    "v": ".....|.....|#...#|#...#|#...#|.#.#.|..#..",
    "w": ".....|.....|#...#|#...#|#.#.#|#.#.#|.#.#.",
    "x": ".....|.....|#...#|.#.#.|..#..|.#.#.|#...#",
    "y": ".....|.....|#...#|#...#|#...#|#...#|.####|....#|.###.",
    "z": ".....|.....|#####|...#.|..#..|.#...|#####",
    "0": ".###.|#...#|#..##|#.#.#|##..#|#...#|.###.",
    "1": ".#.|##.|.#.|.#.|.#.|.#.|###",
    "2": ".###.|#...#|....#|...#.|..#..|.#...|#####",
    "3": "####.|....#|....#|.###.|....#|....#|####.",
    "4": "...#.|..##.|.#.#.|#..#.|#####|...#.|...#.",
    "5": "#####|#....|####.|....#|....#|#...#|.###.",
    "6": ".###.|#....|#....|####.|#...#|#...#|.###.",
    "7": "#####|....#|...#.|..#..|..#..|..#..|..#..",
    "8": ".###.|#...#|#...#|.###.|#...#|#...#|.###.",
    "9": ".###.|#...#|#...#|.####|....#|....#|.###.",
    "!": "#|#|#|#|#|.|#",
    "?": ".###.|#...#|....#|...#.|..#..|.....|..#..",
    ".": ".|.|.|.|.|.|#",
    ",": "..|..|..|..|..|..|.#|#.",
    ":": ".|.|#|.|.|.|#",
    ";": "..|..|.#|..|..|..|.#|#.",
    "'": "#|#|.|.|.|.|.",
    '"': "#.#|#.#|...|...|...|...|...",
    "-": "....|....|....|####|....|....|....",
    "+": "...|...|.#.|###|.#.|...|...",
    "=": "....|....|####|....|####|....|....",
    "_": ".....|.....|.....|.....|.....|.....|#####",
    "(": ".#|#.|#.|#.|#.|#.|.#",
    ")": "#.|.#|.#|.#|.#|.#|#.",
    "[": "##|#.|#.|#.|#.|#.|##",
    "]": "##|.#|.#|.#|.#|.#|##",
    "{": "..#|.#.|.#.|#..|.#.|.#.|..#",
    "}": "#..|.#.|.#.|..#|.#.|.#.|#..",
    "/": "....#|...#.|...#.|..#..|.#...|.#...|#....",
    "\\": "#....|.#...|.#...|..#..|...#.|...#.|....#",
    "<": "...|..#|.#.|#..|.#.|..#|...",
    ">": "...|#..|.#.|..#|.#.|#..|...",
    "*": "...|#.#|.#.|#.#|...|...|...",
    "#": ".#.#.|.#.#.|#####|.#.#.|#####|.#.#.|.#.#.",
    "%": "#...#|#..#.|...#.|..#..|.#...|.#..#|#...#",
    "&": ".##..|#..#.|#.#..|.#...|#.#.#|#..#.|.##.#",
    "$": "..#..|.####|#.#..|.###.|..#.#|####.|..#..",
    "@": ".###.|#...#|#.###|#.#.#|#.###|#....|.###.",
    "|": "#|#|#|#|#|#|#",
    "~": ".....|.....|.....|.#..#|#.##.|.....|.....",
    "^": ".#.|#.#|...|...|...|...|...",
    "`": "#.|.#|..|..|..|..|..",
}
CELL_H = 9
BASE = 7
LINE_H = 11


def build_font():
    chars = sorted(GLYPHS.items(), key=lambda kv: ord(kv[0]))
    cols, cw = 16, 7
    rows = (len(chars) + cols - 1) // cols
    img = new(cols * cw, rows * (CELL_H + 1))
    p = img.load()
    lines = []
    for i, (ch, g) in enumerate(chars):
        gr = g.split("|")
        w = max(len(r) for r in gr)
        ox, oy = (i % cols) * cw, (i // cols) * (CELL_H + 1)
        for y, row in enumerate(gr):
            for x, c in enumerate(row):
                if c == "#":
                    p[ox + x, oy + y] = (255, 255, 255, 255)
        lines.append(f"char id={ord(ch)} x={ox} y={oy} width={w} height={CELL_H} "
                     f"xoffset=0 yoffset=0 xadvance={w + 1} page=0 chnl=15")
    lines.append(f"char id=32 x=0 y=0 width=0 height=0 xoffset=0 yoffset=0 xadvance=3 page=0 chnl=15")
    save(img, "ui/pixel_font.png")
    head = [
        'info face="Ember" size=9 bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=0 aa=1 padding=0,0,0,0 spacing=1,1 outline=0',
        f"common lineHeight={LINE_H} base={BASE} scaleW={img.width} scaleH={img.height} pages=1 packed=0 alphaChnl=0 redChnl=4 greenChnl=4 blueChnl=4",
        'page id=0 file="pixel_font.png"',
        f"chars count={len(lines)}",
    ]
    with open(os.path.join(ASSETS, "ui", "pixel_font.fnt"), "w", newline="\n") as f:
        f.write("\n".join(head + lines) + "\n")
    return img


def text_img(s, color=(255, 255, 255, 255)):
    """Render text with the font (used to bake a few UI images)."""
    w = sum(max(len(r) for r in GLYPHS[c].split("|")) + 1 if c != " " else 3 for c in s)
    img = new(w, CELL_H)
    p = img.load()
    x = 0
    for c in s:
        if c == " ":
            x += 3
            continue
        gr = GLYPHS[c].split("|")
        for y, row in enumerate(gr):
            for xx, ch in enumerate(row):
                if ch == "#":
                    p[x + xx, y] = color
        x += max(len(r) for r in gr) + 1
    return img


def panel():
    """9-slice dialogue frame (margins 7)."""
    s = [
        "..aaaaaaaaaaaaaaaaaaaa..",
        ".abbbbbbbbbbbbbbbbbbbba.",
        "abccbbbbbbbbbbbbbbbbccba",
        "abceaaaaaaaaaaaaaaaaecba",
        "abbaffffffffffffffffabba",
        "abbaffffffffffffffffabba",
    ]
    mid = "abbaffffffffffffffffabba"
    rows = s + [mid] * 12 + list(reversed(s))
    key = {"a": INK, "b": WOOD[3], "c": WOOD[5], "e": GLOW, "f": hexc("#141a30", 238)}
    img = sprite(rows, key)
    p = img.load()
    for y in range(4, img.height - 4):  # subtle inner bevel
        p[4, y] = hexc("#1d2642", 238)
    for x in range(4, img.width - 4):
        p[x, 4] = hexc("#1d2642", 238)
    return img


def nameplate():
    s = [
        ".aaaaaaaaaaaa.",
        "abbbbbbbbbbbba",
        "abccccccccccba",
        "abccccccccccba",
        "abccccccccccba",
        "abccccccccccba",
        "abddddddddddba",
        ".aaaaaaaaaaaa.",
    ]
    rows = s[:2] + [s[2]] * 3 + s[2:]
    return sprite(rows, {"a": INK, "b": WOOD[4], "c": WOOD[2], "d": WOOD[1]})


def keycap(letter=""):
    """A key prompt. With no letter it is the blank cap the game stretches to fit any key name."""
    cap = [
        ".aaaaaaaaa.",
        "abbbbbbbbba",
        "abbbbbbbbba",
        "abbbbbbbbba",
        "abbbbbbbbba",
        "abbbbbbbbba",
        "abbbbbbbbba",
        "abbbbbbbbba",
        "abbbbbbbbba",
        "accccccccca",
        "addddddddda",
        ".aaaaaaaaa.",
    ]
    img = sprite(cap, {"a": INK, "b": BONE[3], "c": BONE[2], "d": BONE[1]})
    if letter:
        t = text_img(letter, INK)
        paste(img, t, (11 - t.width + 1) // 2, 1)
    return img


PAD_COLORS = {  # face button -> (face, lip, letter), Xbox-style colours
    "A": (GRASS[3], GRASS[2], BONE[4]),
    "B": (RED[2], RED[1], BONE[4]),
    "X": (CRYSTAL[2], CRYSTAL[1], BONE[4]),
    "Y": (FIRE[3], FIRE[2], INK),
}


def pad_button(letter):
    """A round gamepad face button, the same height as a keycap."""
    face, lip, ink = PAD_COLORS[letter]
    rows = [
        "...aaaaa...",
        ".aabbbbbaa.",
        ".abbbbbbba.",
        "abbbbbbbbba",
        "abbbbbbbbba",
        "abbbbbbbbba",
        "abbbbbbbbba",
        "abbbbbbbbba",
        "acbbbbbbbca",
        ".accccccca.",
        ".aacccccaa.",
        "...aaaaa...",
    ]
    img = sprite(rows, {"a": INK, "b": face, "c": lip})
    t = text_img(letter, ink)
    paste(img, t, (11 - t.width + 1) // 2, 2)
    return img


def arrow():
    return sprite(["#####", ".###.", "..#.."], {"#": GLOW})


def build():
    font = build_font()
    save(panel(), "ui/panel.png")
    save(nameplate(), "ui/nameplate.png")
    save(keycap("E"), "ui/key_e.png")
    save(keycap(), "ui/key_blank.png")
    for letter in PAD_COLORS:
        save(pad_button(letter), f"ui/pad_{letter.lower()}.png")
    save(arrow(), "ui/arrow.png")
    demo = new(220, 40, hexc("#141a30"))
    paste(demo, text_img("The Hollow Light - Ember & Moss", GLOW), 4, 4)
    paste(demo, text_img("quick brown fox jumps; lazy dog? 0123456789!", BONE[3]), 4, 16)
    paste(demo, keycap("E"), 4, 27)
    for i, letter in enumerate(PAD_COLORS):
        paste(demo, pad_button(letter), 30 + i * 14, 27)
    paste(demo, arrow(), 20, 30)
    save_preview(demo, "ui_demo.png", 4)
    save_preview(panel(), "ui_panel.png", 6)


if __name__ == "__main__":
    build()
