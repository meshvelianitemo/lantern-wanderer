"""Small Keeper props drawn by hand: the lore tablet (assets/deco/tablet.png)."""
from pix import BONE, GLOW, GRASS, INK, STONE, save, save_preview, sprite


def tablet():
    """A worn Keeper tablet: rounded stone slab with faintly glowing carved lines."""
    rows = [
        "....aaaaaa....",
        "..aabcccccbaa.",
        ".abcccdddccba.",
        ".abcgghggcccba",
        "abccccccccccba",
        "abcghgggghccba",
        "abccccccccccba",
        "abcgggchggccba",
        "abccccccccccba",
        "abcghggcccccba",
        "abccccccccccba",
        "abcccgggghccba",
        "abbccccccccbba",
        "abbbcccccbbbba",
        "aabbbbbbbbbbaa",
        "mmaaaaaaaaaamm",
        "nmmnmmnmmnmmnm",
    ]
    key = {"a": INK, "b": STONE[1], "c": STONE[2], "d": STONE[3], "g": BONE[2], "h": GLOW,
           "m": GRASS[2], "n": GRASS[3]}
    return sprite(rows, key)


if __name__ == "__main__":
    img = tablet()
    save(img, "deco/tablet.png")
    save_preview(img, "tablet.png", 6)
