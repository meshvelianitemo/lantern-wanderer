"""The game icon: the wanderer and their lantern on a night-sky tile.

Writes icon.png (256px, the window/taskbar icon) and icon.ico (16-256px, the .exe icon)
to the project root. Drawn at 32x32 and scaled up by whole numbers so it stays crisp.
"""
import os

from PIL import Image

from pix import BONE, FIRE, GLOW, GRASS, INK, ROOT, SKY, new, paste, save_preview

S = 32


def tile():
    """Rounded night-sky square, lighter toward the horizon, with a few stars."""
    img = new(S, S)
    p = img.load()
    for y in range(S):
        c = SKY[0] if y < 12 else SKY[1] if y < 22 else SKY[2]
        for x in range(S):
            p[x, y] = c
    for x, y in ((0, 0), (1, 0), (0, 1), (S - 1, 0), (S - 2, 0), (S - 1, 1),
                 (0, S - 1), (1, S - 1), (0, S - 2), (S - 1, S - 1), (S - 2, S - 1), (S - 1, S - 2)):
        p[x, y] = (0, 0, 0, 0)
    for x, y, c in ((5, 4, BONE[3]), (24, 3, GLOW), (28, 9, BONE[2]), (3, 12, BONE[2]), (14, 2, BONE[2])):
        p[x, y] = c
    return img


def glow(img, cx, cy):
    """Warm rings of lantern light, dithered at the edge like the in-game light."""
    p = img.load()
    warm = FIRE[3]
    for y in range(S):
        for x in range(S):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if d < 5.5:
                a = 0.38
            elif d < 8.5:
                a = 0.22
            elif d < 11.5 and (x + y) % 2 == 0:
                a = 0.12
            else:
                continue
            r, g, b, alpha = p[x, y]
            if alpha:
                p[x, y] = (round(r + (warm[0] - r) * a), round(g + (warm[1] - g) * a),
                           round(b + (warm[2] - b) * a), alpha)


def build():
    hero = Image.open(os.path.join(ROOT, "assets", "sprites", "hero_idle.png")).convert("RGBA").crop((0, 0, 32, 32))
    left, top, right, bottom = hero.getbbox()
    # the light comes from the middle of the lantern's flame pixels
    hp = hero.load()
    fire = [(x, y) for y in range(32) for x in range(32) if hp[x, y] in (FIRE[4], FIRE[5])]
    flame = (sum(x for x, _ in fire) // len(fire), sum(y for _, y in fire) // len(fire))
    dx = (S - (right - left)) // 2 - left
    dy = (S - 3) - bottom
    img = tile()
    glow(img, flame[0] + dx, flame[1] + dy)
    p = img.load()
    for x in range(2, S - 2):  # mossy ground under their feet
        p[x, S - 3] = GRASS[1]
        p[x, S - 2] = INK if x % 5 else GRASS[0]
    paste(img, hero, dx, dy)

    big = img.resize((256, 256), Image.NEAREST)
    big.save(os.path.join(ROOT, "icon.png"))
    sizes = {16: img.resize((16, 16), Image.BOX), 32: img, 48: img.resize((48, 48), Image.NEAREST),
             64: img.resize((64, 64), Image.NEAREST), 128: img.resize((128, 128), Image.NEAREST), 256: big}
    big.save(os.path.join(ROOT, "icon.ico"), format="ICO", sizes=[(s, s) for s in sizes],
             append_images=[sizes[s] for s in sizes if s != 256])
    save_preview(img, "icon.png", 8)
    strip = new(16 + 32 + 48 + 64 + 40, 64, SKY[0])
    x = 4
    for s in (16, 32, 48, 64):
        paste(strip, sizes[s], x, 0)
        x += s + 8
    save_preview(strip, "icon_sizes.png", 3)
    print("icon.png, icon.ico")


if __name__ == "__main__":
    build()
