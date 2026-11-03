"""Historical one-off generator for the very first Mossgrave map.

levels/mossgrave.txt is now the source of truth (it has since gained a header, a
west exit to Old Hollow and a door into the Glimmerdeep), so this script only
writes a copy of the original layout into art_src/_preview/ for reference.
New maps live in make_maps.py."""
import os

W, H = 116, 26
g = [["."] * W for _ in range(H)]


def fill(x0, y0, x1, y1, c="#"):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            g[y][x] = c


def wall(x0, y0, x1, y1):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if g[y][x] == ".":
                g[y][x] = "w"


def put(x, y, c):
    g[y][x] = c


# --- A: the clearing where Mossback stands ---------------------------------
fill(0, 5, 2, 25)
fill(3, 10, 3, 25)
fill(0, 19, 31, 25)
for x, c in ((5, "i"), (7, "P"), (9, "n"), (11, "g"), (13, "b"), (17, "T"), (21, "t"), (25, "y")):
    put(x, 18, c)
fill(22, 17, 24, 17, "=")
fill(26, 15, 30, 16)
put(28, 14, "e")
put(29, 14, "B")
put(27, 18, "m")
put(31, 18, "f")
# --- B: rising ground and the shrine nook ----------------------------------
fill(32, 17, 37, 25)
fill(38, 15, 58, 25)
put(34, 16, "n")
put(36, 16, "y")
fill(40, 13, 42, 13, "=")
put(41, 14, "|")
fill(44, 11, 53, 12)
wall(43, 13, 54, 14)
put(48, 14, "S")
put(45, 13, "v")
put(51, 13, "v")
put(46, 10, "y")
put(52, 10, "e")
put(39, 14, "t")
put(55, 14, "r")
put(57, 14, "i")
# --- C: the broken bridge ---------------------------------------------------
fill(59, 18, 63, 25)
put(60, 17, "b")
fill(64, 18, 68, 18, "=")
fill(71, 18, 75, 18, "=")
fill(64, 19, 64, 25, "|")
fill(68, 19, 68, 21, "|")
fill(71, 19, 71, 21, "|")
fill(75, 19, 75, 25, "|")
put(70, 16, "e")
fill(76, 18, 84, 25)
put(78, 17, "t")
put(80, 17, "n")
put(83, 17, "r")
# --- D: down toward the cave mouth -----------------------------------------
fill(85, 20, 115, 25)
fill(86, 18, 87, 18, "=")
fill(89, 16, 91, 16)
put(90, 15, "e")
put(88, 19, "R")
put(92, 19, "i")
put(94, 19, "m")
fill(97, 4, 115, 12)
fill(99, 13, 115, 15)
fill(96, 7, 96, 10)
wall(98, 13, 115, 19)
fill(114, 16, 115, 19)
for x in (101, 106, 110):
    put(x, 16, "v")
put(97, 19, "r")
put(104, 19, "m")
put(108, 19, "C")

header = """; Mossgrave Woods - see scripts/level.gd for the legend.
; Lines starting with ';' are comments. Every map row should be the same width.
"""
out = os.path.join(os.path.dirname(__file__), "_preview", "forest_01_original.txt")
with open(out, "w", newline="\n") as f:
    f.write(header + "\n".join("".join(r) for r in g) + "\n")
print(open(out).read())
