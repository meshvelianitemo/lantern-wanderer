"""Generator for the chapter maps (levels/<id>.txt).

After generation each .txt file is the source of truth - edit it by hand, or edit
this script and regenerate ONLY the map you changed:  python make_maps.py old_hollow
(Mossgrave Woods predates this script; see make_level.py.)
"""
import os
import sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "levels")


class Map:
    def __init__(self, w, h, fill="#"):
        self.w, self.h = w, h
        self.g = [[fill] * w for _ in range(h)]

    def rect(self, x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(self.h, y1 + 1)):
            for x in range(max(0, x0), min(self.w, x1 + 1)):
                self.g[y][x] = c

    def carve(self, x0, y0, x1, y1, c="w"):
        self.rect(x0, y0, x1, y1, c)

    def fill(self, x0, y0, x1, y1, c="#"):
        self.rect(x0, y0, x1, y1, c)

    def put(self, x, y, c):
        self.g[y][x] = c

    def row(self, x0, x1, y, c):
        self.rect(x0, y, x1, y, c)

    def save(self, name, header):
        path = os.path.join(OUT, name + ".txt")
        body = "\n".join("".join(r) for r in self.g)
        with open(path, "w", newline="\n") as f:
            f.write(header.strip("\n") + "\n" + body + "\n")
        print(f"wrote {path} ({self.w}x{self.h})")


STALACTITE_A, STALACTITE_B = "^", "'"


# ---------------------------------------------------------------- Old Hollow --
def old_hollow():
    m = Map(80, 24, ".")
    m.fill(0, 20, 79, 23)                 # floor
    m.fill(0, 0, 2, 23)                   # west wall
    m.fill(0, 0, 62, 4)                   # the great fallen trunk / root roof
    m.carve(3, 5, 62, 19)                 # the sheltered hollow, wall behind
    for x in range(3, 63):                # ragged underside of the roof
        if (x * 7) % 5 == 0 or x in (20, 21, 41, 42):
            m.put(x, 5, "#")
    m.fill(59, 5, 62, 6)
    # west ledge with the three Wickways
    m.fill(3, 16, 13, 19)
    m.fill(14, 18, 15, 19)
    m.put(5, 15, "V")
    m.put(8, 15, "U")
    m.put(11, 15, "R")
    m.put(13, 15, "Q")
    # walkways and embers
    m.row(20, 23, 18, "=")
    m.row(25, 29, 16, "=")
    m.row(31, 34, 14, "=")
    m.put(33, 13, "e")
    m.row(47, 50, 18, "=")
    m.row(51, 54, 16, "=")
    m.put(53, 15, "e")
    # huts in the back wall
    m.put(17, 19, "h")
    m.put(27, 19, "j")
    m.put(49, 19, "k")
    # the Little Hearth and its people
    m.put(34, 19, "A")
    m.put(38, 19, "E")
    m.put(39, 19, "F")
    m.put(42, 19, "p")
    m.put(44, 19, "Y")
    m.put(19, 19, "W")
    m.put(30, 19, "D")
    m.put(24, 19, "J")
    m.put(61, 19, "O")
    # Echoes & Home: Glim beside Wisp, Vesper by the fire (First Page), where Echoes
    # bring you back, and the Hollow filling up (table, bunting, Maud's bell post)
    m.put(21, 19, "C")
    m.put(22, 19, "c")
    m.put(41, 19, "M")
    m.put(36, 19, "r")
    m.put(46, 19, "T")
    m.put(32, 19, "B")
    for x in (25, 46):
        m.put(x, 6, "u")
    # the well: shallow enough to wade in, deep enough for a very old fish
    m.carve(54, 20, 58, 20)
    m.row(54, 58, 21, "_")
    m.put(56, 20, "G")
    # hanging lamps
    for i, x in enumerate((14, 19, 24, 29, 46, 51, 56, 60)):
        m.put(x, 7 + i % 2, "L")
    m.put(10, 6, "v")
    m.put(36, 6, "v")
    m.put(54, 6, "v")
    # outside: the edge of the woods, and a thorny barrow with a secret
    m.fill(66, 16, 73, 19)
    m.carve(67, 17, 72, 19)
    m.put(66, 18, "&")
    m.put(66, 19, "&")
    m.row(63, 64, 18, "=")                # steps up and over the barrow
    m.row(74, 75, 18, "=")
    m.put(69, 19, "K")
    m.put(71, 19, "e")
    m.put(70, 19, "N")                    # Fitch, late as ever
    m.put(69, 15, "H")                    # Orrin's telescope, under the open sky
    m.put(70, 15, "I")
    m.put(67, 15, "y")
    m.put(72, 15, "n")
    for x, c in ((63, "i"), (64, "b"), (65, "f"), (75, "Z"), (76, "t"), (78, "y"), (74, "n")):
        m.put(x, 19, c)
    m.put(79, 19, "1")
    m.save("old_hollow", """
; Old Hollow - the hub village under the roots of a fallen giant tree.
; NPCs you share an ember with move in here (see Story.NPCS "where").
@name Old Hollow
@subtitle The Last Warm Place
@theme forest
@light 0.78,0.78,0.94 0.42,0.38,0.58 66 56
@warm 0.95,0.78,0.62
@music hollow_cold gave_tallow hollow home>=6 hollow_full
@ambience hollow
@seed 21
@char 1 door 1 mossgrave 1
@char V wickway 2 glimmerdeep 2 glimmerdeep
@char U wickway 3 drowned 3 drowned
@char R wickway 4 rootdark 4 rootdark
@char Q sign sign_wickway_hollow stone
@char Z sign sign_hollow
@char A npc tallow
@char F hearth
@char p npc pell
@char W npc wisp
@char Y npc ash
@char D npc bell
@char J npc sprig_tree
@char G npc gudgeon
@char O npc hollow_one
@char E spot epilogue epilogue_wake ending_many
@char L lamp
@char h hut wisp
@char j hut bell
@char k hut ash
@char K sign tablet_hollow_secret stone
@char N name fitch
@char I npc orrin
@char H prop telescope -2
@char C npc glim
@char c hut glim
@char M npc vesper
@char r spot echo_return
@char T propif home>=3 supper_table -3
@char B propif echo_maud,gave_bell bell_post -3
@char u propif home>=4 bunting -3 top
""")


# --------------------------------------------------------------- Glimmerdeep --
def glimmerdeep():
    m = Map(140, 58)
    # A: entry tunnel from the Mossgrave cave mouth
    m.carve(0, 5, 17, 9)
    m.put(1, 9, "1")
    m.put(6, 5, STALACTITE_A)
    m.put(12, 5, STALACTITE_B)
    m.put(9, 9, "G")
    m.put(14, 9, "k")
    # B: steps down to the shrine and Burrow's dig
    m.carve(18, 5, 34, 13)
    m.fill(18, 10, 20, 13)
    m.fill(21, 12, 23, 13)
    m.put(22, 9, "e")
    m.put(24, 13, "a")
    m.put(26, 13, "S")
    m.put(28, 13, "j")
    m.put(31, 13, "M")
    m.put(33, 13, "K")
    m.put(25, 5, STALACTITE_A)
    m.put(30, 5, STALACTITE_B)
    # C: the first glimmer bridge, over a deep pit (bottomless: it runs off the map)
    m.carve(35, 6, 44, 13)
    m.carve(35, 14, 38, m.h - 1)
    m.row(35, 38, 14, "*")
    m.put(42, 13, "H")
    m.put(44, 13, "T")
    # D: the Glimmer Gallery - a great open chasm
    m.carve(45, 3, 65, m.h - 1, ".")
    m.row(47, 49, 16, "*")
    m.row(52, 54, 19, "*")
    m.row(57, 59, 22, "*")
    m.row(62, 64, 25, "*")
    m.put(60, 20, "x")
    # optional violet route to an ember cache
    m.row(46, 47, 12, "%")
    m.row(50, 51, 10, "%")
    m.row(54, 55, 8, "%")
    m.fill(57, 8, 63, 9)
    m.put(59, 7, "e")
    m.put(61, 7, "e")
    m.put(60, 7, "N")                     # Pim, up the violet way
    m.put(63, 7, "q")
    m.put(58, 7, "j")
    for x in (48, 53, 58, 63):
        m.put(x, 3, STALACTITE_A if x % 2 else STALACTITE_B)
    # E: landing and the long dark corridor
    m.carve(66, 22, 112, 26)
    m.put(68, 26, "k")
    m.put(72, 26, "u")
    m.put(78, 24, "x")
    m.put(83, 24, "e")
    m.put(88, 24, "x")
    m.put(90, 26, "K")
    m.put(75, 22, STALACTITE_A)
    m.put(84, 22, STALACTITE_B)
    m.put(92, 22, STALACTITE_A)
    # the shaft down, with glimmer ledges to climb back up
    m.carve(94, 27, 96, 40)
    for i, y in enumerate((39, 37, 35, 33, 31, 29)):
        x0 = 94 if i % 2 == 0 else 95
        m.row(x0, x0 + 1, y, "*")
    # Wisp's nook beyond the shaft
    m.put(102, 26, "u")
    m.put(106, 26, "a")
    m.put(108, 26, "u")
    m.put(110, 26, "Y")
    m.put(112, 26, "k")
    # F: the lower tunnel
    m.carve(60, 36, 139, 40)
    m.put(64, 40, "e")
    m.put(70, 38, "X")
    m.put(76, 40, "e")
    m.put(80, 40, "j")
    m.put(62, 40, "q")
    m.put(86, 40, "K")
    m.put(89, 40, "I")                    # Tobin
    m.put(101, 40, "S")
    m.put(104, 40, "k")
    # the Wickway chamber, Ash, and the black water
    m.carve(112, 29, 139, 40)
    m.put(116, 40, "J")
    m.put(120, 40, "A")
    m.put(124, 40, "K")
    m.put(127, 40, "W")
    m.put(129, 40, "u")
    m.fill(132, 41, 139, 42, "~")
    m.put(134, 40, "O")
    for x in (115, 121, 126, 133, 137):
        m.put(x, 29, STALACTITE_A if x % 2 else STALACTITE_B)
    # Lark's lantern, where it went out: a nook above the chamber, up violet glimmer
    # (a strong flame only: three embers), through a gap in the chamber roof
    m.carve(116, 25, 127, 27)
    m.carve(116, 28, 118, 28)
    for i, y in enumerate((39, 37, 35, 33, 31, 29)):
        x0 = 114 if i % 2 == 0 else 117
        m.row(x0, x0 + 1, y, "%")
    m.put(115, 29, "w")
    m.put(124, 27, "Z")
    m.put(126, 27, "e")
    m.put(120, 27, "q")
    # the old seam: down a crack between the shrine and Ash's chamber, to where Glim went
    m.carve(107, 41, 108, 47)
    for y in (53, 51, 49, 47, 45, 43):
        m.row(107, 108, y, "=")
    m.carve(96, 48, 122, 54)
    m.put(118, 54, "C")                   # Glim (once you have seen Lark's Song)
    m.put(100, 54, "e")
    m.put(102, 51, "X")                   # guarding the ember, away from Glim
    m.put(98, 54, "k")
    m.put(121, 54, "K")
    m.put(114, 54, "u")
    for x in (101, 105, 113, 119):
        m.put(x, 48, STALACTITE_A if x % 2 else STALACTITE_B)
    m.save("glimmerdeep", """
; The Glimmerdeep - Chapter II. Crystal caves under the mountain.
@name The Glimmerdeep
@subtitle Chapter II
@theme cave
@light 0.5,0.54,0.72 0.2,0.2,0.34 8 40 y
@seed 31
@char 1 door 1 mossgrave 2
@char W wickway 2 old_hollow 2 glimmerdeep
@char M npc burrow
@char Y npc wisp
@char A npc ash
@char O npc gudgeon
@char G sign tablet_glimmer_1 stone
@char H sign tablet_glimmer_3 stone
@char J sign tablet_glimmer_2 stone
@char T trigger glimmer_violet_hint !embers>=3
@char N name pim
@char I name tobin
@char Z keepsake lantern
@char C npc glim
""")


# ----------------------------------------------------------- Drowned Halls --
def drowned():
    m = Map(150, 30)
    # A: the landing by the black lake, where Old Gudgeon leaves you
    m.carve(0, 10, 19, 19)
    m.fill(0, 20, 3, 29, "~")
    m.put(5, 19, "1")
    m.put(7, 19, "T")
    m.put(10, 19, "K")
    m.put(13, 19, "G")
    m.put(16, 19, "S")
    m.put(8, 10, "c")
    m.put(15, 10, "c")
    m.put(4, 15, "l")
    # B: the flooded corridor, and Bell
    m.carve(20, 10, 49, 19)
    for x0 in (22, 29, 36, 43):
        m.fill(x0, 20, x0 + 1, 22, "~")
        m.put(x0, 19, "Y")
    m.put(26, 16, "e")
    m.put(33, 16, "e")
    m.put(40, 19, "B")
    m.put(34, 19, "M")                    # Maud, who called everyone home
    m.put(47, 14, "x")
    m.put(25, 14, "l")
    m.put(39, 14, "l")
    m.put(31, 10, "c")
    m.put(45, 10, "c")
    # C: the half-drowned library and the Archivist
    m.carve(50, 4, 79, 19)
    for x in (52, 62, 77):
        m.put(x, 19, "C")
    m.put(59, 19, "K")
    m.put(54, 19, "U")
    m.put(70, 19, "U")
    m.put(56, 19, "H")
    m.put(66, 19, "A")
    m.row(74, 76, 18, "=")
    m.row(69, 72, 16, "=")
    m.put(70, 15, "e")
    m.put(75, 17, "N")                    # Wren
    for x in (55, 64, 72):
        m.put(x, 4, "c")
    m.put(79, 19, "J")
    # the sunk supper hall, under the library: a crack down, an eye-gate in the dark,
    # and its eye-stone far off by a hook (hang your flame there, then go down with a spark)
    m.carve(57, 20, 58, 22)
    m.row(57, 58, 24, "=")
    m.row(57, 58, 22, "=")
    m.carve(55, 23, 61, 25)
    m.put(61, 23, "g")                    # the gate
    m.carve(62, 22, 78, 26)
    m.put(77, 19, "y")                    # its eye-stone
    m.put(78, 19, "h")
    m.put(65, 26, "t")
    m.put(71, 26, "t")
    m.put(68, 26, "C")
    m.put(75, 26, "z")                    # Maud's handbell
    m.put(70, 24, "x")
    m.put(64, 22, "c")
    m.put(76, 22, "c")
    # D: the first hook - an eye-stone, a glimmer bridge, and a gate in the dark
    m.carve(80, 10, 100, 19)
    m.put(80, 17, "i")
    m.put(81, 19, "h")
    m.fill(82, 21, 85, 23, "~")
    m.row(82, 85, 20, "*")
    m.fill(86, 10, 97, 16)
    m.put(90, 19, "U")
    m.put(94, 17, "Q")
    m.put(99, 19, "S")
    # E: the cistern, and Old Gudgeon shivering in it
    m.carve(101, 4, 125, 19)
    m.fill(102, 20, 124, 29, "~")
    m.row(103, 105, 18, "=")
    m.row(107, 109, 16, "=")
    m.row(112, 114, 19, "=")
    m.row(110, 111, 18, "=")             # so the cistern can be crossed both ways
    m.row(116, 118, 17, "=")
    m.row(121, 123, 18, "=")
    m.put(111, 19, "O")
    m.put(113, 18, "4")                   # where Gudgeon brings you back from the Starwell
    m.put(108, 14, "e")
    m.put(118, 12, "x")
    for x in (106, 115, 122):
        m.put(x, 4, "c")
    # F: the Wickway, and the last gate down to the roots
    m.carve(126, 8, 149, 19)
    m.put(129, 19, "W")
    m.put(134, 19, "L")
    m.put(137, 19, "K")
    m.fill(139, 8, 149, 16)
    m.put(141, 17, "q")
    m.put(148, 19, "2")
    m.save("drowned", """
; The Drowned Halls - Chapter III. The flooded ruins of the Keepers.
@name The Drowned Halls
@subtitle Chapter III
@theme drowned
@light 0.46,0.56,0.6 0.3,0.38,0.42 20 120
@seed 41
@char 1 spot 1
@char 4 spot 4
@char 2 door 2 rootdark 1 rootdark_enter
@char W wickway 3 old_hollow 3 drowned
@char T trigger drowned_arrive
@char A npc archivist
@char B npc bell
@char O npc gudgeon
@char G sign tablet_drowned_1 stone
@char H sign tablet_drowned_2 stone
@char J sign tablet_drowned_3 stone
@char L sign tablet_drowned_4 stone
@char h hook
@char i eye hall
@char Q gate hall
@char q gate deep
@char K prop keeper_statue -4
@char C prop broken_column -4
@char U prop urn -2
@char Y prop lily 6
@char l prop drowned_lamp -3
@char c prop chain_hang -3 top
@char M name maud
@char N name wren
@char g gate supper
@char y eye supper
@char t prop supper_table -3
@char z keepsake bell
""")


# --------------------------------------------------------------- Rootdark --
def rootdark():
    m = Map(150, 44)
    # A: the root stair
    m.carve(0, 4, 24, 9)
    m.put(1, 9, "1")
    m.put(10, 9, "G")
    m.put(16, 9, "S")
    m.put(6, 9, "N")
    m.put(20, 9, "U")
    for x in (6, 14, 21):
        m.put(x, 4, "r")
    m.carve(25, 4, 40, 15)
    m.fill(25, 10, 27, 15)
    m.fill(28, 12, 30, 15)
    m.put(29, 9, "e")
    # B: Sprig, under a crack where the sun once fell
    m.carve(34, 0, 35, 3, ".")
    m.put(35, 15, "Y")
    m.put(32, 15, "U")
    m.put(38, 15, "F")
    # C: the Root-Mother's chamber
    m.carve(41, 6, 62, 21)
    m.fill(41, 18, 43, 21)
    m.fill(44, 20, 46, 21)
    m.put(54, 21, "M")
    for x, c in ((48, "F"), (50, "U"), (58, "U"), (61, "F"), (45, "Z")):
        m.put(x, 21 if c != "Z" else 19, c)
    for x in (47, 52, 57):
        m.put(x, 6, "r")
    # D: the thorn passage, the hole down, and a hidden first page
    m.carve(63, 18, 84, 21)
    m.fill(65, 18, 65, 21, "&")
    m.carve(74, 22, 75, 27)
    m.fill(79, 18, 79, 21, "&")
    m.put(82, 21, "H")
    m.put(83, 21, "I")                    # Edda, beside the page she carved
    m.put(84, 21, "e")
    m.put(70, 21, "N")
    # E: the long dark - where every shade wakes at once
    m.carve(74, 28, 130, 32)
    m.put(76, 32, "S")
    m.put(78, 32, "T")
    for x, y, c in ((84, 30, "x"), (92, 31, "x"), (100, 30, "x"), (108, 30, "X"), (116, 31, "x"), (122, 30, "x")):
        m.put(x, y, c)
    m.fill(104, 28, 104, 32, "&")
    m.put(88, 31, "e")
    m.put(112, 31, "e")
    for x in (82, 95, 110, 124):
        m.put(x, 28, "r")
    m.put(97, 32, "U")
    m.put(119, 32, "F")
    # F: the Hollow One, the Wickway, and the stair to the Hearth
    m.carve(131, 22, 149, 32)
    m.put(136, 32, "V")
    m.put(142, 32, "W")
    m.put(148, 32, "2")
    m.row(139, 140, 31, "%")
    m.row(136, 137, 29, "%")
    m.row(139, 140, 27, "%")
    m.fill(142, 25, 147, 25)
    m.put(144, 24, "e")
    m.put(146, 24, "e")
    m.put(133, 32, "Z")
    m.save("rootdark", """
; The Rootdark - Chapter IV. The roots of the forest, and the deepest dark.
@name The Rootdark
@subtitle Chapter IV
@theme rootdark
@light 0.42,0.36,0.52 0.18,0.13,0.24 8 32 y
@music rootdark seen_chase_start chase hollow_one_gone rootdark
@seed 51
@char 1 door 1 drowned 2
@char 2 door 2 hearth 1 hearth_enter
@char W wickway 4 old_hollow 4 rootdark
@char T trigger chase_start
@char Y npc sprig
@char M npc rootmother
@char V npc hollow_one
@char G sign tablet_root_1 stone
@char H sign tablet_root_2 stone
@char F prop fungus_tall -2
@char U prop fungus_cluster 3
@char Z prop spore_pod -2
@char N prop root_knot -2
@char r prop root_hang -3 top
@char I name edda
""")


# ------------------------------------------------------------------ Hearth --
def hearth():
    m = Map(90, 30)
    m.carve(0, 4, 89, 21)
    # the great bridge, between the stone Keepers, over nothing at all
    m.carve(21, 22, 65, 29, ".")
    m.row(21, 65, 22, "=")
    m.put(1, 21, "1")
    m.put(4, 21, "T")
    m.put(8, 21, "G")
    m.put(14, 21, "S")
    m.put(18, 21, "B")
    for x in (26, 38, 50, 62):
        m.put(x, 21, "K")
    m.put(68, 21, "B")
    m.put(67, 21, "H")
    m.put(70, 21, "c")
    m.put(72, 21, "O")
    m.put(84, 21, "c")
    m.put(87, 21, "O")
    m.put(78, 21, "Q")
    m.save("hearth", """
; The Hearth - Chapter V. The cold heart at the root of the mountain.
@name The Hearth
@subtitle Chapter V
@theme hearth
@light 0.52,0.4,0.4 0.42,0.3,0.32 10 70
@music hearth ending_light ending ending_dark -
@seed 61
@char 1 door 1 rootdark 2
@char T trigger hearth_arrive
@char G sign tablet_hearth_1 stone
@char H sign tablet_hearth_2 stone
@char Q great_hearth
@char K prop keeper_giant -6
@char B prop brazier_cold -2
@char O prop obsidian -2
@char c prop cinder_pile 3
""")


# ---------------------------------------------------------------- Starwell --
# Shadow geometry (see scripts/caster.gd): a still light at L throws a plate's
# shadow to S = 2C - L (the plate's centre C mirrored away from the light),
# twice the plate's size. Its top edge is what you stand on.
T = 16
PLATES = {"boat": (40, 12), "fish": (32, 10), "bird": (36, 10), "moon": (28, 10)}


def hook_light(x, y):           # a hook standing in tile (x, y)
    return (x * T + 8 + 5, (y + 1) * T - 28)


def lamp_light(x, y):           # a star-lamp standing in tile (x, y)
    return (x * T + 8, (y + 1) * T - 24)


def sun_at(x, y):               # an orrery sun starting in tile (x, y)
    return (x * T + 8, y * T + 8)


def plate_for(light, shadow_centre_x, shadow_top, shape):
    """Where to hang a plate so `light` throws its shadow centred on
    shadow_centre_x with its top edge at shadow_top. Returns the pixel centre."""
    w, h = PLATES[shape]
    sx, sy = shadow_centre_x, shadow_top + h
    return ((sx + light[0]) / 2.0, (sy + light[1]) / 2.0)


def caster_char(m, header, ch, shape, centre):
    """Places a plate at a pixel centre: its tile, plus a pixel nudge."""
    cx, cy = int(centre[0] // T), int(centre[1] // T)
    dx, dy = round(centre[0] - (cx * T + 8)), round(centre[1] - (cy * T + 8))
    m.put(cx, cy, ch)
    header.append(f"@char {ch} caster {shape} {dx} {dy}")


def shadow_of(light, centre, shape):
    w, h = PLATES[shape]
    sx, sy = 2 * centre[0] - light[0], 2 * centre[1] - light[1]
    return (sx - w, sx + w, sy - h)   # left, right, top


def starwell():
    m = Map(97, 51)
    hdr = []
    # A: the lock where Old Gudgeon surfaces, at the bottom of the lake
    m.carve(0, 38, 13, 45)
    m.fill(0, 46, 3, 50, "~")
    m.put(2, 45, "O")
    m.put(6, 45, "1")
    m.put(8, 45, "T")
    m.put(10, 45, "G")
    m.put(12, 45, "S")
    m.put(7, 38, "k")
    m.put(1, 38, "k")
    m.put(9, 45, "v")
    # B: Orrin's lesson room - the first plate, and a star-lamp to throw it
    m.carve(14, 38, 30, 45)
    m.put(16, 45, "Z")                          # telescope
    m.put(18, 45, "R")                          # Orrin
    m.put(21, 45, "2")                          # spot: orrin
    m.put(22, 45, "C")                          # star chart
    m.put(23, 45, "H")
    m.put(15, 45, "N")                          # Agathe's name, by her old blackboard
    lamp1 = (25, 45)
    m.put(*lamp1, "L")
    m.fill(31, 43, 37, 50)                      # the ledge: three tiles up, no way to jump it
    L1 = lamp_light(*lamp1)
    c1 = plate_for(L1, 480, 714, "boat")
    caster_char(m, hdr, "a", "boat", c1)
    # C: the hook bridge over black water, and a lamp on the far side to come back by
    m.carve(31, 35, 52, 42)
    m.carve(38, 43, 43, 46)
    m.fill(38, 47, 43, 50, "~")
    m.put(33, 42, "J")                          # tablet: shadow-play
    hook = (36, 42)
    m.put(*hook, "h")
    HL = hook_light(*hook)
    c2 = plate_for(HL, 656, 690, "boat")        # a wide one, the first time you walk the dark
    caster_char(m, hdr, "b", "boat", c2)
    lamp2 = (46, 42)
    m.put(*lamp2, "L")
    L2 = lamp_light(*lamp2)
    c3 = plate_for(L2, 656, 690, "fish")
    caster_char(m, hdr, "r", "fish", c3)
    m.put(63, 37, "x")                          # a shade over the orrery pit
    m.put(52, 42, "S")
    m.fill(44, 43, 55, 50)
    # D: the Orrery Hall - an orrery sun on a rail sweeps a bridge of shadows over the pit
    m.carve(53, 33, 75, 42)
    m.carve(56, 43, 70, 46)
    m.fill(56, 47, 70, 50, "~")
    m.fill(71, 43, 96, 50)
    sun = (56, 44)
    m.put(*sun, "Q")
    S0 = sun_at(*sun)
    right_end = 69                              # the rail ends under tile 69
    LR = (right_end * T + 8, S0[1])
    hdr.append(f"@char Q orrery {right_end - sun[0]} 0 24")
    for ch, sx in (("d", 940), ("f", 1036), ("i", 1132)):
        caster_char(m, hdr, ch, "boat", plate_for(LR, sx, 686, "boat"))
    m.put(67, 40, "e")                          # jump for it from the moving bridge
    m.put(54, 42, "U")
    m.put(73, 42, "U")
    m.put(60, 33, "k")
    m.put(66, 33, "k")
    # E: the Well - two orrery suns on upright rails; their shadows are lifts
    m.carve(76, 9, 93, 42)
    m.fill(94, 0, 96, 50)
    # A plate 16px beside the rail and 90px below the sun's top stays within the
    # sun's reach (92) the whole way: the shadow rides from 16px above the floor
    # (sun at the top, resting) up to level with the landing (sun at the bottom).
    sun1 = (79, 42)
    m.put(*sun1, "V")
    hdr.append("@char V orrery 0 -11 22 2.6")
    s1 = sun_at(*sun1)
    lift1 = (s1[0] + 16, s1[1] - 11 * T + 90)
    caster_char(m, hdr, "l", "boat", lift1)
    m.fill(85, 31, 93, 32)                      # the first landing
    m.fill(76, 31, 77, 32)                      # a little alcove across the well
    m.put(76, 30, "M")                          # Corran's name
    sun2 = (90, 30)
    m.put(*sun2, "W")
    hdr.append("@char W orrery 0 -11 22 2.6")
    s2 = sun_at(*sun2)
    lift2 = (s2[0] - 16, s2[1] - 11 * T + 90)
    caster_char(m, hdr, "n", "boat", lift2)
    for name, sun_, plate in (("lift 1", s1, lift1), ("lift 2", s2, lift2)):
        lo = shadow_of((sun_[0], sun_[1] - 11 * T), plate, "boat")
        hi = shadow_of(sun_, plate, "boat")
        print(f"  {name}: x {lo[0]:.0f}..{lo[1]:.0f}, top {lo[2]:.0f} -> {hi[2]:.0f}")
    m.put(88, 42, "e")
    for x in (78, 84, 90):
        m.put(x, 9, "k")
    # F: the top gallery and the dome of the Great Orrery
    m.carve(38, 2, 62, 18)
    m.carve(60, 10, 84, 18)
    m.fill(38, 19, 84, 20)
    m.put(80, 18, "L")
    m.put(66, 18, "L")
    m.put(72, 17, "x")
    m.put(58, 15, "x")
    m.put(70, 18, "e")
    m.put(56, 18, "K")                          # tablet: the sky
    m.put(48, 18, "Y")                          # the Great Orrery
    m.put(41, 18, "X")                          # Orrin's own name
    m.put(61, 18, "U")
    m.put(40, 18, "Z")
    for x in (44, 52):
        m.put(x, 2, "k")
    # windows onto the lake all the way round
    for x, y in ((9, 41), (27, 41), (47, 38), (64, 37), (84, 38), (88, 24), (44, 9), (56, 13)):
        if m.g[y][x] == "w":
            m.put(x, y, "o")
    for line in hdr:
        print("  ", line)
    for name, light, centre, shape in (
            ("lesson", L1, c1, "boat"), ("hook", HL, c2, "boat"), ("return", L2, c3, "fish")):
        print(f"  {name}: shadow x {shadow_of(light, centre, shape)[0]:.0f}..{shadow_of(light, centre, shape)[1]:.0f}"
              f" top {shadow_of(light, centre, shape)[2]:.0f}")
    m.save("starwell", """
; Under the Lake: the Starwell - a sunken Keeper observatory (side chapter, after Ch III).
; Reached by riding Old Gudgeon from the Drowned Halls' cistern. Shadow geometry is
; computed in art_src/make_maps.py - regenerate rather than moving plates by hand.
@name The Starwell
@subtitle Under the Lake
@theme starwell
@light 0.5,0.56,0.7 0.2,0.22,0.36 44 18 y
@glow 0.56,0.6,0.82 orrery_lit
@music starwell orrery_lit stars
@seed 71
@char 1 spot 1
@char 2 spot orrin
@char T trigger starwell_arrive
@char O npc gudgeon
@char R npc orrin
@char G sign tablet_starwell_1 stone
@char J sign tablet_starwell_2 stone
@char K sign tablet_starwell_3 stone
@char H prop globe -2
@char C prop star_chart -2
@char Z prop telescope -2
@char U prop orrery_ring -4
@char o prop porthole -6
@char k prop kelp -3 top
@char v prop bubble_vent -2
@char L starlamp
@char h hook
@char Y great_orrery
@char N name agathe
@char M name corran
@char X name orrin
""" + "\n".join(hdr) + "\n")


# ----------------------------------------------------------------- Echoes --
# Playable memories (see DESIGN.md section 7). Rows given are tile rows; something
# placed in row y stands on the ground in row y + 1.

def shaft(m, x0, x1, top_floor, bottom_floor, exit="left"):
    """Open a drop between two floors with one-way steps every 2 rows, so it can be
    climbed back up as well as dropped down (Vesper runs back up these). The top step
    sits on the `exit` side, next to where the upper floor carries on."""
    m.carve(x0, top_floor, x1, bottom_floor - 1)
    left = exit == "left"
    for y in range(top_floor + 2, bottom_floor - 1, 2):
        if left:
            m.row(x0, x0 + 2, y, "=")
        else:
            m.row(x1 - 2, x1, y, "=")
        left = not left


def echo_lark():
    """I. Lark's Song: one age ago, the Glimmerdeep. Sharing lights the way."""
    m = Map(100, 28)
    # A: where Lark comes down, lantern full
    m.carve(0, 11, 18, 17)
    m.put(3, 17, "L")
    m.put(1, 17, "P")
    m.put(9, 17, "K")
    m.put(14, 17, "k")
    for x in (5, 11, 16):
        m.put(x, 11, STALACTITE_A if x % 2 else STALACTITE_B)
    # B: young Burrow up on the ledge by the eye-stone; the gate it opens is far below
    m.carve(19, 5, 36, 17)
    m.fill(19, 10, 27, 11)                # the high ledge
    m.row(29, 31, 16, "=")
    m.row(26, 28, 14, "=")
    m.row(29, 31, 12, "=")
    m.put(20, 9, "i")                     # eye-stone
    m.put(23, 9, "b")                     # Burrow, a pup
    m.put(26, 9, "k")
    m.put(33, 17, "L")
    m.put(35, 17, "h")                    # "somebody would have to stay by it"
    m.carve(37, 15, 44, 17)               # low corridor through the gate
    m.put(38, 15, "Q")
    for x in (22, 28, 34):
        m.put(x, 5, STALACTITE_A if x % 2 else STALACTITE_B)
    # C: the shade nest over a frozen pool, and young Gudgeon in it
    m.carve(45, 12, 72, 17)
    m.carve(56, 18, 60, 18)
    m.row(56, 60, 19, "_")
    m.put(58, 18, "G")
    m.put(46, 17, "L")
    m.put(48, 17, "s")                    # "a light that stayed put would keep them off"
    for x, y, c in ((54, 14, "X"), (56, 15, "X"), (61, 14, "X"), (63, 15, "x")):
        m.put(x, y, c)
    m.put(51, 17, "a")
    m.put(66, 17, "u")
    for x in (50, 59, 68):
        m.put(x, 12, STALACTITE_A if x % 2 else STALACTITE_B)
    # D: Glim on a ledge above the pit, and glimmer stepping stones over the cold water
    m.carve(73, 9, 84, 25)
    m.row(73, 75, 16, "=")
    m.row(76, 77, 14, "=")
    m.fill(78, 12, 83, 12)
    m.put(81, 11, "c")                    # Glim and her egg-to-be
    m.put(79, 11, "k")
    m.put(71, 17, "L")
    m.row(74, 75, 20, "*")
    m.row(77, 78, 21, "*")
    m.row(80, 81, 22, "*")
    m.fill(73, 26, 84, 27, "~")
    m.fill(83, 24, 84, 25)
    # E: the last cave, darker and darker, and an egg nobody came back for
    m.carve(85, 18, 99, 23)
    m.put(86, 23, "L")
    m.put(88, 23, "d")                    # the lantern is lighter than it was
    m.put(92, 20, "x")
    m.put(97, 23, "E")
    m.put(94, 23, "j")
    m.put(99, 23, "u")
    m.save("echo_lark", """
; Echo I - Lark's Song. One age ago, in the Glimmerdeep. Played as Lark (see DESIGN.md 7b).
@name Lark's Song
@subtitle An Echo
@theme cave
@echo lark
@hero lark
@embers 6
@light 0.52,0.56,0.74 0.15,0.15,0.27 60 96
@music echo_lark
@seed 71
@char b npc lark_burrow
@char G npc lark_gudgeon
@char c npc lark_glim
@char E npc lark_egg
@char i eye lark
@char Q gate lark
@char h trigger lark_gate_hint
@char s trigger lark_shades_hint
@char d trigger lark_dim_hint
@char L landing
""")


def echo_maud():
    """II. The Last Winter: the night of the flood, up the Long Stair as the water rises."""
    m = Map(44, 74)
    m.carve(4, 2, 39, 69)                 # the stairwell, from the supper hall to the upper door
    m.fill(0, 70, 43, 73)
    m.put(0, 73, "r")                     # the flood, starting under the hall floor
    # the supper hall
    m.put(6, 69, "P")
    m.put(8, 69, "L")
    m.put(13, 69, "t")
    m.put(26, 69, "t")
    m.put(20, 69, "H")                    # Hollis, asleep at the table
    m.put(16, 69, "h")
    m.put(10, 66, "k")
    m.put(32, 66, "k")

    def stair(rows, starts, w=4):
        for y, x in zip(rows, starts):
            m.row(x, x + w - 1, y, "=")

    # each flight climbs 12 rows to a landing, with a Keeper asleep beside it
    stair((68, 66, 64, 62, 60), (9, 13, 17, 21, 25))
    m.fill(30, 58, 39, 59)
    m.put(31, 57, "L")
    m.put(34, 57, "s")
    m.put(37, 57, "F")                    # Fitch
    m.put(34, 54, "k")
    stair((56, 54, 52, 50, 48), (26, 22, 18, 14, 10))
    m.fill(4, 46, 9, 47)
    m.put(8, 45, "L")
    m.put(5, 45, "B")                     # Tobin
    m.put(7, 42, "k")
    stair((44, 42, 40, 38, 36), (10, 14, 18, 22, 26))
    m.fill(31, 34, 39, 35)
    m.put(32, 33, "L")
    m.put(37, 33, "M")                    # Pim
    m.put(35, 30, "k")
    stair((32, 30, 28, 26, 24), (27, 23, 19, 15, 11))
    m.fill(4, 22, 9, 23)
    m.put(8, 21, "L")
    m.put(5, 21, "W")                     # Wren
    m.put(7, 18, "k")
    stair((20, 18, 16, 14, 12), (10, 14, 18, 22, 26))
    m.fill(31, 10, 39, 11)
    m.put(32, 9, "L")
    m.put(38, 9, "D")                     # the upper door: not without all five
    m.put(35, 6, "k")
    m.save("echo_maud", """
; Echo II - The Last Winter. The Drowned Halls the night the water rose. Played as Maud.
@name The Last Winter
@subtitle An Echo
@theme drowned
@echo maud
@hero maud
@lantern 0.45
@ability bell
@light 0.26,0.27,0.36 0.15,0.15,0.23 64 8 y
@music echo_maud
@ambience flood
@seed 72
@char r rising water 7
@char H sleeper hollis
@char F sleeper fitch
@char B sleeper tobin
@char M sleeper pim
@char W sleeper wren
@char L landing
@char D headcount 5 maud_door maud_not_yet
@char h trigger maud_hollis_hint
@char s trigger maud_stair
@char t prop supper_table -2
@char k prop keeper_lamp -3
""")


def echo_vesper():
    """III. Vesper: the first wick's walk down a warm mountain, and the run back up."""
    m = Map(70, 58)
    # the halls first, then the shafts between them (so their steps survive)
    m.carve(1, 4, 40, 9)
    m.carve(20, 14, 62, 19)
    m.carve(6, 24, 61, 29)
    m.carve(6, 36, 50, 41)
    m.carve(40, 46, 68, 53)
    shaft(m, 36, 41, 10, 20)
    shaft(m, 56, 61, 20, 30)
    shaft(m, 6, 11, 30, 42, exit="right")
    shaft(m, 43, 49, 42, 54)
    # H1: the Keepers' gate, where Edda meets you
    m.put(3, 9, "P")
    m.put(2, 9, "L")
    m.put(5, 9, "E")                      # Edda walks with you
    m.put(15, 9, "a")                     # Hollis
    m.put(10, 9, "k")
    m.put(28, 9, "k")
    for x in (8, 20, 32):
        m.put(x, 4, "n")
    m.put(24, 4, "o")
    # H2: the bee-galleries and workshops
    m.put(38, 19, "L")
    m.put(30, 19, "b")                    # Tobin
    m.put(47, 19, "c")                    # Wren
    m.put(26, 19, "k")
    m.put(52, 19, "k")
    m.put(34, 14, "o")
    m.put(44, 14, "n")
    # H3: the supper rooms, and the last gate
    m.put(58, 29, "L")
    m.put(40, 29, "d")                    # Pim
    m.put(30, 29, "f")                    # Maud, with Bell's supper for after
    m.put(48, 29, "k")
    m.put(22, 29, "k")
    m.put(36, 24, "o")
    m.put(18, 29, "z")                    # the way back up ends here, with Edda
    m.put(14, 29, "g")                    # the last gate: Edda stops
    m.put(16, 24, "n")
    # H4: alone now, the deep road
    m.put(40, 41, "L")
    m.put(14, 41, "L")
    m.put(24, 41, "k")
    # the Hearth, as it was
    m.put(46, 53, "L")
    m.put(56, 53, "h")
    m.put(63, 53, "O")
    m.put(0, 56, "r")                     # the cold, waiting under the Hearth
    m.save("echo_vesper", """
; Echo III - Vesper. The Rootway before the first cold, down to the Hearth and back. Played as Vesper.
@name Vesper
@subtitle An Echo
@theme rootdark
@echo vesper
@hero vesper
@embers 4
@fear 12 50
@light 1.0,0.84,0.66 0.74,0.54,0.46 10 50 y
@music echo_vesper vesper:fear_off echo_vesper_dark
@ambience rootway
@seed 73
@char E follower edda
@char a npc v_hollis
@char b npc v_tobin
@char c npc v_wren
@char d npc v_pim
@char f npc v_maud
@char g trigger vesper_gate !vesper:fear_off
@char z trigger vesper_end vesper:fear_off
@char h trigger vesper_hearth
@char O old_hearth
@char r rising dark 13
@char L landing
@char n prop banner -3 top
@char o prop lamp_string -3 top
@char k prop keeper_lamp -3
""")


MAPS = {"old_hollow": old_hollow, "glimmerdeep": glimmerdeep, "drowned": drowned,
        "rootdark": rootdark, "hearth": hearth, "starwell": starwell,
        "echo_lark": echo_lark, "echo_maud": echo_maud, "echo_vesper": echo_vesper}

if __name__ == "__main__":
    for name in (sys.argv[1:] or MAPS):
        MAPS[name]()
