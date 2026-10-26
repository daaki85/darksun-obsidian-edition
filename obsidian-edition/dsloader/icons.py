"""Inventory icons of the Loader's own for its items, made the way the game makes its magic
items' (the Bloodwrath's is the obsidian long sword's with a few pixels in the colours the game
cycles: 240-248, fire): from the plain item's icon.

- the Short Sword: the metal long sword's, its blade four steps shorter, centred;
- Inixhide (Legcrusher's Leather Chest Armor +1): the leather's brightest pixels in the fire colours;
- the Cloak of Protection +1: every other pixel of its lightest folds in the violet ones (232-239);
- the Rings of Protection +1: the gold band violet for Pehtucl's, in the fire colours for the
  arena's (the Tied-up Prisoner's), so the two can be told apart.

- the Bone Helm (bonescale.py): the leather Helm's, each shade of leather made the bone scale
  armour's of the same brightness (BONE).
- Kreenfang (arms.py, the arena's Gythka +1): the bone gythka's, its two blades in the fire colours;
- Shadowseeker (arms.py, Kurzak's Short Sword +1): the Short Sword's, its blade night steel (dark
  blue-greys).

Violet is 35-37 of the palette, which no region changes (232-239, violet in RESOURCE.GFF's
palette, are each region's own: red in the slave pens). The game cycles only 11-15 (water) and
224-255 (fire among them), so an icon tinted in colours it doesn't cycle (violet, night steel,
ice, gold) has every other column of its tint in the water's (`shining`) to shine as a magic
item does.

The game reads object pictures from SEGOBJEX.GFF. The game folder is never changed: the launcher
writes a copy of that file next to the patched game (the dos folder, D: in DOSBox) with an
object added for each of these icons, and DSCLOG has the game open the copy instead (its INT
21h hook, PROBE_DOS_OPEN).
An object (OJFF) is an item's picture number negated; its word +0Ch names its icon (a BMP chunk),
which is also how the item looks on the ground: a thing on the map of an item's object is drawn
with that icon (its map record's +0Fh), so each of these lies on the ground as its own icon.
"""

import os
import struct
from typing import Callable, Dict, List, Optional, Set, Tuple

from . import gff

OBJECTS_FILE = "SEGOBJEX.GFF"
OJFF_ICON = 0x0C  # an object's word naming its icon (BMP chunk)
FIRE = tuple(range(240, 249))  # the colours the game cycles: the Bloodwrath's glow
VIOLET = (37, 36, 35, 36)  # a violet no region changes
NIGHT_STEEL = (18, 20, 22, 24, 22, 20)  # dark blue-greys no region changes (17-31)
# the water's blues and lavenders, which the game cycles (as it does the fire's) and no region
# changes but for the step the cycle is at: the shine of a magic item whose tint isn't fire's
WATER = tuple(range(11, 16))

Rows = List[List[Optional[int]]]


def decode(chunk: bytes) -> Rows:
    from .art import decode_frame
    return [list(r) for r in decode_frame(chunk)[2]]


def _pack(pixels) -> bytes:
    """A run's pixels as the game packs them: a byte n (pixels n >> 1 plus one), then for n odd one
    pixel repeated, for n even that many pixels as they are; up to 128 a piece. A repeat for three
    alike or more (the game's own pictures are packed so: a window's marble and flat faces half
    their size or less, the game's memory for them the less)."""
    out, i, literal = bytearray(), 0, []

    def flush():
        for k in range(0, len(literal), 128):
            piece = literal[k:k + 128]
            out.extend(bytes([(len(piece) - 1) << 1]) + bytes(piece))
        literal.clear()
    while i < len(pixels):
        j = i
        while j < len(pixels) and pixels[j] == pixels[i] and j - i < 128:
            j += 1
        if j - i >= 3:
            flush()
            out.extend(bytes([((j - i - 1) << 1) | 1, pixels[i]]))
        else:
            literal.extend(pixels[i:j])
        i = j
    flush()
    return bytes(out)


def encode(rows: Rows) -> bytes:
    """A one-frame picture chunk, as the game's own: for each row with pixels its y, then its runs
    (x, a last-run flag, the count, the data's length, the data packed: _pack), then FFh."""
    height, width = len(rows), max((len(r) for r in rows), default=0)
    body = bytearray(struct.pack("<HH", width, height))
    for y, row in enumerate(rows):
        runs, x = [], 0
        while x < len(row):
            if row[x] is None:
                x += 1
                continue
            start = x
            while x < len(row) and row[x] is not None:
                x += 1
            runs.append((start, row[start:x]))
        if runs:
            body.append(y)
        for k, (start, pixels) in enumerate(runs):
            data = _pack(pixels)
            body += bytes([start, 0x80 if k == len(runs) - 1 else 0, len(pixels), len(data)]) + data
    body += b"\xff"
    head_size = 4 + 2 + 4
    return struct.pack("<IHI", head_size + len(body), 1, head_size) + bytes(body)


def shorter_blade(rows: Rows, steps: int = 4) -> Rows:
    """A sword drawn from top left to bottom right, its first STEPS diagonal steps of blade gone,
    the rest centred where the whole was."""
    size = len(rows)
    drawn = [(x, y) for y, r in enumerate(rows) for x, p in enumerate(r) if p is not None]
    x0, y0 = min(x for x, _ in drawn), min(y for _, y in drawn)
    cut = [[None if (y < y0 + steps or x < x0 + steps) else p for x, p in enumerate(r)] for y, r in enumerate(rows)]
    points = [(x, y) for y, r in enumerate(cut) for x, p in enumerate(r) if p is not None]
    left, top = min(x for x, _ in points), min(y for _, y in points)
    right, bottom = max(x for x, _ in points), max(y for _, y in points)
    dx, dy = (size - (right - left + 1)) // 2 - left, (size - (bottom - top + 1)) // 2 - top
    out: Rows = [[None] * len(rows[0]) for _ in range(size)]
    for x, y in points:
        out[y + dy][x + dx] = cut[y][x]
    return out


# The item box (right-click an item) puts its text below the picture, in room for one 22 pixels
# tall (the gythka's, the tallest but one). The Polearm's is 36: its text ran out of the box.
BOX_PICTURE = 22
POLEARM_OBJECT = 0x10000 - 0xFB5E


def fit_box(rows: Rows, size: int = BOX_PICTURE) -> Rows:
    """A picture taller or wider than SIZE drawn smaller, each pixel moved to its scaled place
    (a long thin line stays unbroken); one that fits, as it is."""
    height, width = len(rows), max((len(r) for r in rows), default=0)
    if height <= size and width <= size:
        return rows
    scale = size / max(height, width)
    out: Rows = [[None] * max(1, round(width * scale)) for _ in range(max(1, round(height * scale)))]
    for y, r in enumerate(rows):
        for x, p in enumerate(r):
            if p is not None:
                out[min(int(y * scale), len(out) - 1)][min(int(x * scale), len(out[0]) - 1)] = p
    return out


CHILL = (46, 220, 161, 220)  # (Magic Missile's white, cyan and blue)
SHOCK = (45, 64, 46, 65)  # (the purse's coin golds, and white)


def arrow_head(p: int, x: int, y: int) -> bool:
    """The Arrows icon's heads: its browns at the lower right."""
    return (p == 129 or 134 <= p <= 141) and x + y >= 15


def glow(rows: Rows, which: Callable[[int, int, int], bool], colours: Tuple[int, ...]) -> Rows:
    """Pixels chosen by WHICH(colour, x, y) in colours the game cycles, stepping along them."""
    return [[colours[(x + y) % len(colours)] if p is not None and which(p, x, y) else p
             for x, p in enumerate(r)] for y, r in enumerate(rows)]


def shining(rows: Rows, which: Callable[[int, int, int], bool], colours: Tuple[int, ...]) -> Rows:
    """As `glow`, every other column of its pixels in the WATER colours the game cycles: COLOURS
    (which the game doesn't cycle: violet, night steel, ice, gold) tint it, the water's make it
    shine as a magic item's does."""
    return [[(WATER[(x + y) % len(WATER)] if x % 2 == 0 else colours[(x + y) % len(colours)])
             if p is not None and which(p, x, y) else p for x, p in enumerate(r)] for y, r in enumerate(rows)]


# the leather Helm's shades -> the bone scale armour's (its icons' mauves) of the same brightness
BONE = {129: 207, 128: 205, 134: 58, 135: 194, 136: 206, 137: 59, 138: 60, 139: 61, 140: 61}


def recolour(rows: Rows, colours: Dict[int, int]) -> Rows:
    return [[colours.get(p, p) if p is not None else None for p in r] for r in rows]


def rim(rows: Rows, step: int, colours: Tuple[int, ...]) -> Rows:
    """The picture's edge (its pixels beside a clear one, or the picture's side), each STEP-th along
    the diagonals, in colours the game cycles."""
    def edge(x: int, y: int) -> bool:
        return any(not (0 <= x + dx < len(rows[0]) and 0 <= y + dy < len(rows)) or rows[y + dy][x + dx] is None
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
    return [[colours[(x + y) % len(colours)] if p is not None and (x + y) % step == 0 and edge(x, y) else p
             for x, p in enumerate(r)] for y, r in enumerate(rows)]


# the Shield's browns -> the metal long sword's greys, shade for shade (a step lighter than their brightness)
SHIELD_METAL = {129: 210, 128: 211, 134: 212, 179: 211, 135: 212, 136: 213, 137: 214, 138: 215, 139: 216}


GREAT_AXE_TYPE = 2
MAGIC_KINDS = {18: "Gutterknot", 112: "Deepbiter", 0: "Windlash"}  # (the game's types: none has a plus)
BLADE = range(0xD1, 0xDA)
# the Axe's metal head, shade for shade (by brightness), in the bone long sword's whites
AXE_BONE = {208: 129, 209: 132, 210: 132, 211: 200, 212: 146, 213: 146, 214: 148, 215: 152}
# ... and in the obsidian long sword's darker greys (it has 208-213, mostly 208-211)
AXE_OBSIDIAN = {210: 208, 211: 209, 212: 210, 213: 210, 214: 211, 215: 212}
MACE_OBSIDIAN = {210: 208, 211: 209, 212: 209, 213: 210, 214: 211, 215: 212, 217: 213}
OBSIDIAN_MACE_TYPE, MACE_NAME = 46, 0x13  # (the Mace's name: Blackmace has its own)  # a blade's greys, in the bone gythka's and the metal sword's icons

# Bracers of defense (bracers.py): drawn, a pair of steel cuffs (the Chameleon Gloves' blue-greys,
# which no region changes) with gold rims and a stud in the fire colours
STEEL = (22, 23, 24, 25, 26, 27, 28, 29, 30)  # dark to light
# metal, as the game's metal long sword: light greys (209-217) and its blade's blues (160, 161).
# Dark stone greys raised to them (the dagger's and pick's), light bone-white heads given the blues
# in their middle shades (the mace's, polearm's), the great axe's teal head too
STONE_TO_METAL = {208: 211, 209: 212, 210: 213, 211: 161, 212: 214, 213: 215, 214: 216, 215: 217}
LIGHT_TO_METAL = {210: 209, 211: 210, 212: 160, 213: 161, 214: 213, 215: 215}
TEAL_TO_METAL = {70: 160, 71: 161, 72: 215}
TEAL_TO_BONE = {70: 206, 71: 61, 72: 152}
TEAL_TO_OBSIDIAN = {70: 208, 71: 210, 72: 212}
DAGGER_BONE = {208: 60, 209: 61, 210: 152, 211: 146, 213: 152, 215: 152}
GOLD = (64, 65, 45)


def bracers_icon(_rows: Rows = None) -> Rows:
    out: Rows = [[None] * 16 for _ in range(14)]
    for left in (1, 8):  # two cuffs, each wider at the top (the forearm's thick end)
        for y in range(1, 13):
            taper = (y - 1) // 6  # 0 at the top, 1 below
            x0, x1 = left + taper, left + 6 - taper
            for x in range(x0, x1 + 1):
                shade = STEEL[min(len(STEEL) - 1, 1 + (x - x0) * 7 // max(1, x1 - x0))]
                if x == x0:
                    shade = STEEL[0]
                if y in (1, 12) or y in (2, 11) and x in (x0, x1):
                    shade = GOLD[1] if (x - x0) % 2 else GOLD[0]
                out[y][x] = shade
        out[6][left + 3] = FIRE[2]
        out[7][left + 3] = FIRE[4]
        out[6][left + 4] = FIRE[6]
        out[7][left + 2] = FIRE[0]
    return out


# plate (worldgear.py's Warden's Plate): the chain armour's greys polished, two steps lighter (the
# metal long sword's), a few of its brightest pixels in the fire colours (magic). The Helm's
# leather browns, by brightness, in the same greys
CHAIN_TO_PLATE = {208: 210, 209: 211, 210: 213, 211: 214, 212: 215, 213: 216, 214: 217, 215: 217, 216: 217}
LEATHER_TO_PLATE = {128: 210, 129: 211, 134: 212, 135: 213, 136: 214, 137: 215, 138: 216, 139: 217, 140: 217}


def plate_icon(colours: Dict[int, int], bright: Tuple[int, ...]) -> Callable[[Rows], Rows]:
    return lambda r: recolour(glow(r, lambda p, x, y: p in bright and (x + y) % 3 == 0, FIRE), colours)


# the Cloak and Boots of Elvenkind (worldgear.py): the Cloak's leather browns, by brightness, in a
# neutral grey cloth, a few of its lightest folds in a leaf green (no region changes 53-56); the
# Boots' browns in soft grey leather, their orange-browns in the greens
LEATHER_TO_GREY = {128: 208, 129: 209, 134: 210, 135: 211, 136: 212, 137: 213, 138: 214, 139: 215, 140: 216}
BOOTS_TO_ELVEN = {128: 209, 129: 210, 134: 211, 135: 212, 179: 53, 180: 54, 181: 55, 182: 56}
LEAF = (54, 55, 56, 55)


# the robes (robes.py), drawn: a hooded robe to the feet, wide sleeves with trimmed cuffs, a
# trimmed panel down the front (as Baldur's Gate's robes): O outline, b B the cloth, k the hood's
# shadow, G the trim, p the panel
ROBE = (".....OOOO.....",
        "....ObbbbO....",
        "...ObBkkBbO...",
        "...ObkkkkbO...",
        "..OOOGkkGOOO..",
        ".ObbbGppGbbbO.",
        "ObBbbGppGbbBbO",
        "ObBbOGppGObBbO",
        "ObBbOGppGObBbO",
        "OGGGOGppGOGGGO",
        "...ObGppGbO...",
        "...ObGppGbO...",
        "...ObGppGbO...",
        "..ObbGppGbbO..",
        "..ObBGppGBbO..",
        ".OOOOGGGGOOOO.")


def robe_icon(cloth: Tuple[int, int, int], trim: Tuple[int, int, int], sparks: Tuple[int, ...]) -> Rows:
    """A robe (ROBE) in CLOTH (outline, cloth, its light) and TRIM (dark, mid, light), every few
    pixels of its panel in SPARKS (the magic)."""
    out: Rows = []
    for y, line in enumerate(ROBE):
        row: List[Optional[int]] = []
        for x, c in enumerate(line):
            colour = {".": None, "O": cloth[0], "k": cloth[0], "b": cloth[1], "B": cloth[2], "G": trim[0],
                      "p": trim[2] if (x + y) % 2 else trim[1]}[c]
            if c == "p" and (x * 3 + y) % 5 == 0:
                colour = sparks[(x + y) % len(sparks)]
            row.append(colour)
        out.append(row)
    return out


def ashen_robe_icon(_rows: Rows = None) -> Rows:
    """The Ashen Robe (robes.py): ash greys, its panel pale ash, embers in the fire colours."""
    return robe_icon((208, 210, 212), (213, 215, 216), FIRE)


def veiled_robe_icon(_rows: Rows = None) -> Rows:
    """The Veiled Robe (robes.py): night blue, its panel and trim gold, violet glints."""
    return robe_icon((17, 20, 23), (64, 65, 45), (37, 12, 36, 14))  # (violet and the water's shine)


def elven_cloak_icon(rows: Rows) -> Rows:
    return recolour(shining(rows, lambda p, x, y: p in (138, 139, 140) and (x + y) % 3 == 0, LEAF), LEATHER_TO_GREY)


SILVER = (210, 212, 213, 214, 215, 216, 217)  # dark to light (the metal long sword's greys)


def circlet_icon(_rows: Rows = None) -> Rows:
    """Arrowbane: a thin silver band seen from a little above, a stone at its front in the fire
    colours."""
    out: Rows = [[None] * 18 for _ in range(12)]
    cx, cy, rx, ry = 8.5, 6.0, 7.5, 3.6
    import math
    for step in range(160):
        a = 2 * math.pi * step / 160
        x, y = int(round(cx + rx * math.cos(a))), int(round(cy + ry * math.sin(a)))
        front = math.sin(a) > 0  # (the near half: lit)
        shade = SILVER[min(len(SILVER) - 1, (4 if front else 1) + int(2 * math.cos(a - 0.8) + 0.5))]
        if 0 <= y < 12 and 0 <= x < 18 and (out[y][x] is None or front):
            out[y][x] = shade
    gem = int(round(cy + ry))
    out[gem][8], out[gem][9], out[gem - 1][8], out[gem - 1][9] = FIRE[2], FIRE[4], FIRE[6], FIRE[3]
    return out


# the Belt's leather -> red silk (the palette's own reds, darkest to brightest), flecked with gold
URNST_SILK = {128: 135, 129: 135, 134: 135, 135: 136, 136: 136, 137: 32, 138: 32}
URNST_GOLD = (183, 184)


def urnst_icon(rows: Rows) -> Rows:
    """The Golden Girdle of Urnst: the Belt in red silk, a fleck every fourth pixel, gold or the
    water's shine (`shining`) by turns."""
    rows = recolour(rows, URNST_SILK)
    return [[(URNST_GOLD[0] if x % 4 < 2 else WATER[(x + y) % len(WATER)]) if p is not None and (x + 2 * y) % 4 == 0
             else p for x, p in enumerate(r)] for y, r in enumerate(rows)]


def crown_icon(_rows: Rows = None) -> Rows:
    """The Sunking Crown: a gold band with five points, a jewel in the fire colours at its front."""
    out: Rows = [[None] * 18 for _ in range(14)]
    band_top, band_bottom = 8, 12
    for x in range(1, 17):
        for y in range(band_top, band_bottom + 1):
            out[y][x] = GOLD[0] if x in (1, 16) or y == band_bottom else GOLD[1] if y == band_top else GOLD[2]
    for peak in (2, 5, 8, 12, 15):  # the points, the middle one the tallest
        tall = 6 if peak == 8 else 4
        for k in range(1, tall + 1):
            out[band_top - k][peak] = GOLD[0] if k == tall else GOLD[2]
            if k < tall - 1:
                out[band_top - k][peak + 1] = GOLD[1]
        out[band_top - tall - 1][peak] = FIRE[5]
    out[10][8], out[10][9], out[11][8], out[11][9] = FIRE[2], FIRE[4], FIRE[6], FIRE[0]
    return out


# (name, the plain item's picture, the new object's number, its icon's number, the icon made from
# the plain one's)
ICONS: Tuple[Tuple[str, int, int, int, Callable[[Rows], Rows]], ...] = (
    ("Short Sword", 0xFC0A, 2427, 2432, shorter_blade),
    ("Inixhide", 0xFC02, 2428, 2433,
     lambda r: glow(r, lambda p, x, y: p in (0x89, 0x8A), FIRE)),
    ("Cloak of Protection +1", 0xFBE3, 2429, 2434,
     lambda r: shining(r, lambda p, x, y: p in (0x8A, 0x8B, 0x8C) and (x + y) % 2 == 0, VIOLET)),
    ("Pehtucl's Ring of Protection +1", 0xFA1C, 2430, 2435, lambda r: shining(r, lambda p, x, y: p == 0x3A, VIOLET)),
    ("Ring of Protection +1", 0xFA1C, 2431, 2436, lambda r: glow(r, lambda p, x, y: p == 0x3A, FIRE)),
    ("Bone Helm", 0xFC03, 2437, 2438, lambda r: recolour(r, BONE)),
    ("Kreenfang", 0xFC0D, 2446, 2447, lambda r: glow(r, lambda p, x, y: p in BLADE, FIRE)),
    ("Shadowseeker", 0xFC0A, 2448, 2449, lambda r: shining(shorter_blade(r), lambda p, x, y: p in BLADE, NIGHT_STEEL)),
    ("Bone Short Sword", 0xFC0C, 2419, 2420, shorter_blade),
    ("Bone Axe", 0xFB61, 2421, 2422, lambda r: recolour(r, AXE_BONE)),
    ("Obsidian Short Sword", 0xFC0B, 2488, 2489, shorter_blade),
    ("Obsidian Axe", 0xFB61, 2490, 2491, lambda r: recolour(r, AXE_OBSIDIAN)),
    # the game's only great axe is its Great Axe +3, its green gem (1, 2) the magic: a plain one's
    # has the handle's mauves there
    ("Great Axe", 0xFC06, 2492, 2493, lambda r: recolour(r, {1: 58, 2: 59})),
    # the game's obsidian maces are its Blackmace alone: a plain one, the Mace's head in obsidian
    ("Obsidian Mace", 0xFB5D, 2486, 2487, lambda r: recolour(r, MACE_OBSIDIAN)),
    # magic weapons of kinds the game has none of (worldgear.py): the game's magic look, its fire
    ("Gutterknot", 0xFB5F, 2494, 2495, lambda r: glow(r, lambda p, x, y: p >= 140 and p <= 143, FIRE)),
    ("Deepbiter", 0xFB46, 2496, 2497, lambda r: glow(r, lambda p, x, y: p in (209, 210) and (x + y) % 2 == 0, FIRE)),
    ("Windlash", 0xFC08, 2498, 2499, lambda r: glow(r, lambda p, x, y: p in (59, 60, 61), FIRE)),
    ("Greenbright", 0xFC0A, 2500, 2501, lambda r: glow(shorter_blade(r), lambda p, x, y: p in BLADE, FIRE)),
    ("Bracers of Defense", 0xFC01, 2502, 2503, bracers_icon),  # (on the map: the leather Arm Armor)
    # metal versions of the plain weapons the game has none of in metal: their heads and blades
    # in the metal long sword's colours
    ("Metal Dagger", 0xFB5A, 2504, 2505, lambda r: recolour(r, STONE_TO_METAL)),
    ("Metal Mace", 0xFB5D, 2506, 2507, lambda r: recolour(r, LIGHT_TO_METAL)),
    ("Metal Great Axe", 0xFC06, 2508, 2509, lambda r: recolour(r, {1: 58, 2: 59, **TEAL_TO_METAL})),
    ("Metal Pick", 0xFB46, 2510, 2511, lambda r: recolour(r, STONE_TO_METAL)),
    ("Metal Polearm", 0xFB5E, 2512, 2513, lambda r: recolour(r, LIGHT_TO_METAL)),
    # the circlet and the crown (worldgear.py), drawn; on the map, the Ring's
    ("Arrowbane", 0xFA1C, 2514, 2515, circlet_icon),
    ("Sunking Crown", 0xFA1C, 2516, 2517, crown_icon),
    # the Warden's Plate (worldgear.py): the Chain armour's pieces and the Helm, in plate
    ("Warden's Chest", 0xFBF4, 2538, 2539, plate_icon(CHAIN_TO_PLATE, (213, 214))),
    ("Warden's Arms", 0xFBF3, 2540, 2541, plate_icon(CHAIN_TO_PLATE, (213, 214, 215))),
    ("Warden's Legs", 0xFBF2, 2542, 2543, plate_icon(CHAIN_TO_PLATE, (213, 215, 216))),
    ("Warden's Helm", 0xFC03, 2544, 2545, plate_icon(LEATHER_TO_PLATE, (138, 139, 140))),
    # the Cloak and Boots of Elvenkind (worldgear.py): the Cloak's and the Boots'
    ("Cloak of Elvenkind", 0xFBE3, 2546, 2547, elven_cloak_icon),
    ("Boots of Elvenkind", 0xFBE5, 2548, 2549,
     lambda r: shining(recolour(r, BOOTS_TO_ELVEN), lambda p, x, y: 53 <= p <= 56, LEAF)),
    # the Flame Blade (worldgear.py): the obsidian long sword's, its blade in the fire colours
    ("Flame Blade", 0xFC0B, 2550, 2551, lambda r: glow(r, lambda p, x, y: p in BLADE or p in (208, 209, 210), FIRE)),
    # the magic axes (worldgear.py): the bone and obsidian Axes and the metal Great Axe, every other
    # pixel of their heads in the fire colours
    ("Drakejaw", 0xFB61, 2554, 2555,
     lambda r: glow(recolour(r, AXE_BONE), lambda p, x, y: p in AXE_BONE.values() and (x + y) % 2 == 0, FIRE)),
    ("Glasshewer", 0xFB61, 2556, 2557,
     lambda r: glow(recolour(r, AXE_OBSIDIAN), lambda p, x, y: 208 <= p <= 212 and (x + y) % 2 == 0, FIRE)),
    ("Headsman", 0xFC06, 2558, 2559,
     lambda r: glow(recolour(r, {1: 58, 2: 59, **TEAL_TO_METAL}), lambda p, x, y: 208 <= p <= 215 and (x + y) % 2 == 0, FIRE)),
    # the weapons for those who had too few (worldgear.py): the metal Dagger, the obsidian and bone
    # Short Swords and the metal Polearm, every other pixel of their blades in the fire colours
    ("Galefang", 0xFB5A, 2564, 2565,
     lambda r: glow(recolour(r, STONE_TO_METAL), lambda p, x, y: p in STONE_TO_METAL.values() and (x + y) % 2 == 0, FIRE)),
    ("Mindshard", 0xFC0B, 2566, 2567,
     lambda r: glow(shorter_blade(r), lambda p, x, y: (p in BLADE or p in (208, 209, 210)) and (x + y) % 2 == 0, FIRE)),
    ("Stillwater", 0xFC0C, 2568, 2569,
     lambda r: glow(shorter_blade(r), lambda p, x, y: p in (0x92, 0x94, 0x98, 0x9C) and (x + y) % 2 == 0, FIRE)),
    ("Linebreaker", 0xFB5E, 2570, 2571,
     lambda r: glow(recolour(r, LIGHT_TO_METAL), lambda p, x, y: p in LIGHT_TO_METAL.values() and (x + y) % 2 == 0, FIRE)),
    ("Thornwall", 0xFB5E, 2572, 2573, lambda r: glow(r, lambda p, x, y: 210 <= p <= 215 and (x + y) % 2 == 0, FIRE)),
    # the bone and obsidian Great Axes (weaponchoice.py): the Great Axe +3's, without its green gem,
    # its teal head in the bone long sword's whites and the obsidian long sword's greys
    ("Bone Great Axe", 0xFC06, 2574, 2575, lambda r: recolour(r, {1: 58, 2: 59, **TEAL_TO_BONE})),
    ("Obsidian Great Axe", 0xFC06, 2576, 2577, lambda r: recolour(r, {1: 58, 2: 59, **TEAL_TO_OBSIDIAN})),
    # the bone Dagger (weaponchoice.py): the obsidian Dagger's, its blade in the bone weapons' whites
    ("Bone Dagger", 0xFB60, 2578, 2579, lambda r: recolour(r, DAGGER_BONE)),
    # the robes (robes.py), drawn
    ("Ashen Robe", 0xFBE3, 2580, 2581, ashen_robe_icon),
    ("Veiled Robe", 0xFBE3, 2582, 2583, veiled_robe_icon),
    # the girdles, the bow and the amulet (worldgear.py): the Belt's, its brightest leather glowing
    # violet; the Belt in red silk with gold flecks; the Bow, its string in the fire colours; the
    # Necklace, every other pixel of its cord violet
    ("Girdle of Back Defense", 0xFBE6, 2606, 2607,
     lambda r: shining(r, lambda p, x, y: p in (137, 138) and (x + y) % 2 == 0, VIOLET)),
    ("Golden Girdle of Urnst", 0xFBE6, 2608, 2609, urnst_icon),
    ("Amulet of Magic Resistance", 0x86DD, 2612, 2613,
     lambda r: shining(r, lambda p, x, y: 17 <= p <= 20 and (x + y) % 2 == 0, VIOLET)),
    # the Spellarcher's spell arrows (spellarrows.py): the game's Arrows, their heads in the spell's
    # colours: Burning Hands' fire, Chill Touch's icy white and blue, Shocking Grasp's gold and white,
    # Vampiric Touch's violet
    ("Burning Arrows", 0xFBD2, 2614, 2615, lambda r: glow(r, arrow_head, FIRE)),
    ("Chill Arrows", 0xFBD2, 2616, 2617, lambda r: shining(r, arrow_head, CHILL)),
    ("Shocking Arrows", 0xFBD2, 2618, 2619, lambda r: shining(r, arrow_head, SHOCK)),
    ("Vampiric Arrows", 0xFBD2, 2620, 2621, lambda r: shining(r, arrow_head, VIOLET)),
    # the game's own Sling +1 (in a chest, object 1068) names a picture, object 2644, that its data
    # hasn't: blank in a shop or a pack. The Sling's, every other pixel of its strap in the fire colours
    ("Sling +1", 0xFC09, 2644, 2645, lambda r: glow(r, lambda p, x, y: 137 <= p <= 140 and (x + y) % 2 == 0, FIRE)),
    # the magic shields (worldgear.py): the game's wooden Shield, every other pixel of its rim in
    # the fire colours; its leather one in the metal long sword's greys, its whole rim burning
    ("Gutterward", 0xFB5B, 2586, 2587, lambda r: rim(r, 2, FIRE)),
    ("Ironbulwark", 0xFC04, 2588, 2589, lambda r: rim(recolour(r, SHIELD_METAL), 1, FIRE)),
    # the weapons for the kits with too few (worldgear.py): the bone and obsidian Daggers, every
    # other pixel of their blades in the fire colours; the Bow, its string; the Chatkcha, its blades
    ("Hayneedle", 0xFB60, 2590, 2591,
     lambda r: glow(recolour(r, DAGGER_BONE), lambda p, x, y: p in DAGGER_BONE.values() and (x + y) % 2 == 0, FIRE)),
    ("Nightsliver", 0xFB60, 2592, 2593, lambda r: glow(r, lambda p, x, y: 208 <= p <= 215 and (x + y) % 2 == 0, FIRE)),
    ("Dunesong", 0xFC07, 2594, 2595, lambda r: glow(r, lambda p, x, y: 210 <= p <= 214 and (x + y) % 2 == 0, FIRE)),
    ("Skycutter", 0xFC0E, 2596, 2597, lambda r: glow(r, lambda p, x, y: 158 <= p <= 162 and (x + y) % 2 == 0, FIRE)),
)
PICTURES: Dict[str, int] = {name: 0x10000 - number for name, _, number, _, _ in ICONS}  # an item's +0

# the game's own magic items whose icons have nothing in the colours it cycles, so they don't shine
# as its others do: (name, its object, the icon made from its own, a picture number of its own or
# None). With None the object's icon is its alone and changes in place; with a number the icon is
# shared (the Cahulaks +1's with the plain Cahulaks, the two rings' with each other and the plain
# Ring), and the object is given a picture of its own, the shining one. Weapons shine in the fire
# colours, as the game's own magic weapons and the Loader's do; the rest every other pixel in the
# water's (the leather helm's and the Drake Armor's in the fire's), tinted with their own colour
# where it is green (`shining`).
LEAF_GREEN = (53, 54, 55, 56, 55, 54)  # (the Silk Armor's and the Living Cloak's greens, which no region changes)
BLADE_METAL = range(208, 217)  # (the metal and obsidian greys of a blade or a head)
SHINE: Tuple[Tuple[str, int, Callable[[Rows], Rows], Optional[int]], ...] = (
    ("Parting Staff", 30044, lambda r: glow(r, lambda p, x, y: 158 <= p <= 161, WATER), None),
    ("Chameleon Gloves", 30020, lambda r: glow(r, lambda p, x, y: 24 <= p <= 30 and (x + y) % 2 == 0, WATER), None),
    # weapons: every other pixel of the blade or head in the fire colours
    ("Hornblade", 2270, lambda r: glow(r, lambda p, x, y: (60 <= p <= 65 or p in (194, 195)) and (x + y) % 2 == 0, FIRE), None),
    ("Cahulaks +1", 30003, lambda r: glow(r, lambda p, x, y: 210 <= p <= 213 and (x + y) % 2 == 0, FIRE), 2653),
    ("Dag's Dagger", 30005, lambda r: glow(r, lambda p, x, y: p in BLADE_METAL and (x + y) % 2 == 0, FIRE), None),
    ("Terror Blade", 2041, lambda r: glow(r, lambda p, x, y: 208 <= p <= 210 and (x + y) % 2 == 0, FIRE), None),
    ("Blackmace", 30006, lambda r: glow(r, lambda p, x, y: p in BLADE_METAL and (x + y) % 2 == 0, FIRE), None),
    # armour and worn things: every other pixel of their brightest shades in the water's
    ("Shimmer Armor", 30014, lambda r: glow(r, lambda p, x, y: 134 <= p <= 138 and (x + y) % 2 == 0, WATER), None),
    ("Drake Armor", 30013, lambda r: glow(r, lambda p, x, y: 134 <= p <= 138 and (x + y) % 2 == 0, FIRE), None),
    ("Silk Armor", 2008, lambda r: shining(r, lambda p, x, y: 51 <= p <= 56 and (x + y) % 2 == 0, LEAF_GREEN), None),
    ("Tanelyv's Arm Armor", 1362, lambda r: glow(r, lambda p, x, y: 209 <= p <= 213 and (x + y) % 2 == 0, WATER), None),
    ("Tanelyv's Leg Armor", 1363, lambda r: glow(r, lambda p, x, y: 209 <= p <= 213 and (x + y) % 2 == 0, WATER), None),
    ("Grey's Scale Arms", 2531, lambda r: glow(r, lambda p, x, y: 209 <= p <= 213 and (x + y) % 2 == 0, WATER), None),
    ("Grey's Scale Legs", 2518, lambda r: glow(r, lambda p, x, y: 209 <= p <= 213 and (x + y) % 2 == 0, WATER), None),
    ("Leather Helm +1", 1021, lambda r: glow(r, lambda p, x, y: 134 <= p <= 137 and (x + y) % 2 == 0, FIRE), None),
    ("Living Cloak", 30022, lambda r: shining(r, lambda p, x, y: 69 <= p <= 73 and (x + y) % 2 == 0, LEAF_GREEN), None),
    # jewellery and the orb: the gold or the gem
    ("Golden Torque", 30052, lambda r: glow(r, lambda p, x, y: 179 <= p <= 187 and (x + y) % 2 == 0, FIRE), None),
    ("Light of Dawn", 30008, lambda r: glow(r, lambda p, x, y: p in (58, 66, 200) and (x + y) % 2 == 0, FIRE), 2654),
    ("El's Ring", 30012, lambda r: glow(r, lambda p, x, y: p in (58, 66, 200) and (x + y) % 2 == 0, WATER), 2655),
    ("Orb of Knowledge", 31014, lambda r: glow(r, lambda p, x, y: 208 <= p <= 211, WATER), None),
)


def new_chunks(chunks: gff.Chunks) -> gff.Chunks:
    """The objects and pictures to add to the game's SEGOBJEX.GFF."""
    out: gff.Chunks = {}
    smaller: Dict[int, Rows] = {}
    if ("OJFF", POLEARM_OBJECT) in chunks:  # (the Polearm's picture, small enough for the item box)
        pole, = struct.unpack_from("<H", chunks[("OJFF", POLEARM_OBJECT)], OJFF_ICON)
        if ("BMP ", pole) in chunks:
            smaller[pole] = fit_box(decode(chunks[("BMP ", pole)]))
            out[("BMP ", pole)] = encode(smaller[pole])
    for _, plain, number, icon, make in ICONS:
        base = 0x10000 - plain
        record = bytearray(chunks[("OJFF", base)])
        old_icon, = struct.unpack_from("<H", record, OJFF_ICON)
        struct.pack_into("<H", record, OJFF_ICON, icon)
        out[("OJFF", number)] = bytes(record)
        if ("BMP ", base) in chunks:  # (the plain item's BMP of its own number, as the game's objects
            out[("BMP ", number)] = chunks[("BMP ", base)]  # have one; a necklace has none: kept so)
        rows = smaller.get(old_icon) or decode(chunks[("BMP ", old_icon)])
        out[("BMP ", icon)] = encode(make(rows))
    for _, obj, make, own in SHINE:
        if ("OJFF", obj) in chunks:
            icon, = struct.unpack_from("<H", chunks[("OJFF", obj)], OJFF_ICON)
            if ("BMP ", icon) in chunks:
                out[("BMP ", own or icon)] = encode(make(decode(chunks[("BMP ", icon)])))
                if own:  # (the object pointed at its own picture)
                    record = bytearray(chunks[("OJFF", obj)])
                    struct.pack_into("<H", record, OJFF_ICON, own)
                    out[("OJFF", obj)] = bytes(record)
    return out


def with_chunks(data: bytes, added: gff.Chunks, room: Optional[Dict[Tuple[str, int], int]] = None) -> bytes:
    """DATA (a GFF file, its table of contents last; types listing their ids as ranges have their
    offsets in GFFI index chunks, the others in the table itself) with ADDED appended: each added
    chunk (in place of one with its id, if there is one), the index chunks of their types grown
    by them, and a new table of contents, the header pointing to it. Everything already in the
    file stays where it was. ROOM: bytes kept free after a chunk (not in its length: for it to be
    written bigger in place later)."""
    room = room or {}
    toc_offset, toc_length = struct.unpack_from("<II", data, 12)
    pos = toc_offset + 8
    count, = struct.unpack_from("<H", data, pos)
    pos += 2
    types = []  # [type, ranged, info]
    for _ in range(count):
        kind, n = struct.unpack_from("<4sI", data, pos)
        pos += 8
        if n & 0x80000000:
            total, index, runs = struct.unpack_from("<III", data, pos)
            pos += 12
            ranges = [list(struct.unpack_from("<II", data, pos + 8 * i)) for i in range(runs)]
            pos += 8 * runs
            types.append([kind, True, [total, index, ranges]])
        else:
            entries = [list(struct.unpack_from("<III", data, pos + 12 * i)) for i in range(n)]
            pos += 12 * n
            types.append([kind, False, entries])
    out = bytearray(data)
    gffi = next(info for kind, ranged, info in types if kind == b"GFFI" and not ranged)
    for kind, ranged, info in types:
        ids = sorted(cid for (k, cid) in added if k.encode("latin1") == kind)
        if not ids:
            continue
        if not ranged:  # (listed one by one in the table of contents: each entry its place)
            for cid in ids:
                chunk = added[(kind.decode("latin1"), cid)]
                entry = next((e for e in info if e[0] == cid), None)
                if entry is None:
                    entry = [cid, 0, 0]
                    info.append(entry)
                    info.sort(key=lambda e: e[0])
                entry[1], entry[2] = len(out), len(chunk)
                out += chunk + bytes(room.get((kind.decode("latin1"), cid), 0))
            continue
        total, index, ranges = info
        entry = next(e for e in gffi if e[0] == index)
        table = data[entry[1]:entry[1] + entry[2]]
        listed, k = {}, 0  # id: (offset, length), in the order the runs give them
        for first, n in ranges:
            for cid in range(first, first + n):
                listed[cid] = struct.unpack_from("<II", table, 4 + 8 * k)
                k += 1
        for cid in ids:
            chunk = added[(kind.decode("latin1"), cid)]
            listed[cid] = (len(out), len(chunk))
            out += chunk + bytes(room.get((kind.decode("latin1"), cid), 0))
        # the game looks ids up in runs sorted by id (as the file's own are)
        ranges[:] = []
        new_table = bytearray(struct.pack("<I", len(listed)))
        for cid in sorted(listed):
            if ranges and ranges[-1][0] + ranges[-1][1] == cid:
                ranges[-1][1] += 1
            else:
                ranges.append([cid, 1])
            new_table += struct.pack("<II", *listed[cid])
        info[0] = len(listed)
        entry[1], entry[2] = len(out), len(new_table)
        out += new_table
    toc = bytearray(data[toc_offset:toc_offset + 4]) + bytes(4) + struct.pack("<H", len(types))
    for kind, ranged, info in types:
        if ranged:
            total, index, ranges = info
            toc += struct.pack("<4sIIII", kind, 0x80000000 | len(ranges), total, index, len(ranges))
            for first, n in ranges:
                toc += struct.pack("<II", first, n)
        else:
            toc += struct.pack("<4sI", kind, len(info))
            for cid, offset, length in info:
                toc += struct.pack("<III", cid, offset, length)
    struct.pack_into("<I", toc, 4, len(toc) - 2)  # (as the game's own: the length less 2)
    new_toc = len(out)
    out += toc
    struct.pack_into("<II", out, 12, new_toc, len(toc))
    return bytes(out)


# The new spells' icons (RESOURCE.GFF; game.NEW_SPELLS), ICON 21000 + the spell as the game's own,
# on the USE screen and the Effects screen. Cat's Grace: Strength's tile (ICON 21023: the spell Cat's
# Grace works as) in a tawny cat's golds, its glyph a cat's paw print in the game's dark line, with
# the light line below and right of it that its glyphs have. Erdlu Claw: Gaze Reflection's sandy
# tile, three claw scratches; Fogbolt: Armor's grey tile, its glyph taken off, a cloud with a bolt
# below; Reflected Image: Mirror Image's, one of its two figures left, the other hollow; Spook:
# Scare's purple tile, a ghost; Friends: Hold Person's warm tile, a heart.
RESOURCE_FILE = "RESOURCE.GFF"
STRENGTH_ICON, GAZE_ICON, CHARM_ICON, ARMOR_ICON = 21023, 21006, 21002, 21000
MIRROR_ICON, SCARE_ICON, HOLD_ICON = 21019, 21021, 21030
GRACE_ICON, CLAW_ICON, FOG_ICON, REFLECT_ICON, SPOOK_ICON, FRIENDS_ICON = range(21196, 21202)
GRACE_FILL = {163: 168, 76: 169, 77: 65, 75: 168, 78: 170, 134: 205}
GRACE_FRAME = {60: 170, 145: 169, 147: 170, 133: 205, 203: 207, 134: 205}
GLYPH, GLYPH_LIGHT = 204, 170
CAT_PAW = (  # (a paw print: four toes over the pad)
    ".....DD..DD.....",
    "....DDD..DDD....",
    "....DD....DD....",
    ".DD..........DD.",
    ".DDD........DDD.",
    "..DD..DDDD..DD..",
    ".....DDDDDD.....",
    "....DDDDDDDD....",
    "....DDDDDDDD....",
    ".....DDDDDD.....",
)
CAT_TOP = 3


def cat_icon(strength: Rows) -> Rows:
    """Cat's Grace's icon from Strength's."""
    n = len(strength)
    out = [list(r) for r in strength]
    for y in range(n):
        for x in range(n):
            p = out[y][x]
            if x in (0, n - 1) or y in (0, n - 1):
                out[y][x] = GRACE_FRAME.get(p, GRACE_FILL.get(p, 170))
            elif p in (204, 147):  # Strength's glyph and its light line: filled in from the left
                out[y][x] = out[y][x - 1] if x > 1 else 169
            else:
                out[y][x] = GRACE_FILL.get(p, 169)
    glyph = {(x, CAT_TOP + j) for j, line in enumerate(CAT_PAW) for x, ch in enumerate(line) if ch == "D"}
    for x, y in glyph:
        if (x + 1, y + 1) not in glyph and 0 < x + 1 < n - 1 and 0 < y + 1 < n - 1:
            out[y + 1][x + 1] = GLYPH_LIGHT
    for x, y in glyph:
        out[y][x] = GLYPH
    return out


CLAW_GLYPH = (  # (three claw scratches)
    ".....D....D....D",
    "....DD...DD...DD",
    "...DD...DD...DD.",
    "...DD...DD...DD.",
    "..DD...DD...DD..",
    "..DD...DD...DD..",
    ".DD...DD...DD...",
    ".DD...DD...DD...",
    ".D....D....D....",
)
FOG_GLYPH = (  # (a cloud with a bolt below)
    "......DDD.......",
    "...DDD...D......",
    "..D.......DDD...",
    ".D...........D..",
    ".DDDDDDDDDDDDD..",
    "......DD........",
    ".....DD.........",
    "....DDDDDD......",
    "........DD......",
    ".......DD.......",
    "......DD........",
    "......D.........",
)
CHARM_GLYPH = {174, 178, 74, 75}  # (Charm Person's and Scare's glyphs: their dark and light lines)
CHARM_FILL = (177, 176)  # (... filled in with its tile's own purples)
ARMOR_GLYPH, ARMOR_FILL = {208, 214}, (211, 212)  # (Armor's: its dome's lines, and its greys)
FOG_DARK, FOG_LIGHT = 208, 214
GHOST_GLYPH = (  # (a ghost: a hooded head, two eyes, a ragged hem)
    ".....DDDDDD.....",
    "....D......D....",
    "...D........D...",
    "...D..D..D..D...",
    "...D..D..D..D...",
    "...D........D...",
    "...D...DD...D...",
    "...D........D...",
    "...D........D...",
    "...D.D.DD.D.D...",
    "...DD.D..D.DD...",
)
HEART_GLYPH = (  # (a heart)
    "...DDD....DDD...",
    "..D...D..D...D..",
    ".D.....DD.....D.",
    ".D............D.",
    ".D............D.",
    "..D..........D..",
    "...D........D...",
    "....D......D....",
    ".....D....D.....",
    "......D..D......",
    ".......DD.......",
)
HOLD_GLYPH, HOLD_FILL = {134, 150}, (139, 140)  # (Hold Person's glyph lines, and its tile's tans)
HEART_DARK, HEART_LIGHT = 134, 150
MIRROR_GREEN = 42  # (Mirror Image's tile's green; its dark and pale teals below)
HAND_MIRROR = (  # (a hand mirror, a figure in its glass: D the frame, P the glass, F the figure)
    ".....DDDDDD.....",
    "....DPPPPPPD....",
    "...DPPPFFPPPD...",
    "...DPPPFFPPPD...",
    "...DPPFFFFPPD...",
    "...DPPPFFPPPD...",
    "...DPPPFFPPPD...",
    "...DPPFPPFPPD...",
    "....DPPPPPPD....",
    ".....DDDDDD.....",
    ".......DD.......",
    ".......DD.......",
    "......DDDD......",
)
HAND_MIRROR_COLOURS = {"D": 70, "P": 216, "F": 70}


def glyph_icon(base: Rows, old: Set[int], fill: int, glyph: Tuple[str, ...], top: int, dark: int,
               light: int) -> Rows:
    """BASE's tile with its glyph (colours OLD inside the frame) filled in with FILL and GLYPH drawn
    from row TOP in DARK, its light line LIGHT below and right of it."""
    n = len(base)
    out = [list(r) for r in base]
    for y in range(1, n - 1):
        for x in range(1, n - 1):
            if out[y][x] in old:
                out[y][x] = fill
    points = {(x, top + j) for j, line in enumerate(glyph) for x, ch in enumerate(line) if ch == "D"}
    for x, y in points:
        if (x + 1, y + 1) not in points and 0 < x + 1 < n - 1 and 0 < y + 1 < n - 1:
            out[y + 1][x + 1] = light
    for x, y in points:
        out[y][x] = dark
    return out


def claw_icon(gaze: Rows) -> Rows:
    """Erdlu Claw's icon from Gaze Reflection's."""
    return glyph_icon(gaze, {129, 60, 182, 183}, 180, CLAW_GLYPH, 3, 129, 183)


def untiled(base: Rows, old: Set[int], fills: Tuple[int, int]) -> Rows:
    """BASE's tile with its glyph (colours OLD inside the frame) taken off, each pixel of it one of
    FILLS, by turns."""
    n = len(base)
    out = [list(r) for r in base]
    for y in range(1, n - 1):
        for x in range(1, n - 1):
            if out[y][x] in old:
                out[y][x] = fills[(x + y) % 2]
    return out


def fog_icon(armor: Rows) -> Rows:
    """Fogbolt's icon from Armor's grey tile: its glyph taken off, then the cloud and bolt in its
    dark grey with its light line."""
    return glyph_icon(untiled(armor, ARMOR_GLYPH, ARMOR_FILL), set(), 0, FOG_GLYPH, 2, FOG_DARK, FOG_LIGHT)


def reflect_icon(mirror: Rows) -> Rows:
    """Reflected Image's icon from Mirror Image's tile: its two tall mirrors taken off (the tile's
    green within its border), and one hand mirror with one figure in its glass."""
    n = len(mirror)
    out = [list(r) for r in mirror]
    for y in range(1, n - 1):
        for x in range(1, n - 1):
            out[y][x] = MIRROR_GREEN
    for j, line in enumerate(HAND_MIRROR):
        for x, ch in enumerate(line):
            if ch in HAND_MIRROR_COLOURS:
                out[1 + j][x] = HAND_MIRROR_COLOURS[ch]
    return out


def spook_icon(scare: Rows) -> Rows:
    """Spook's icon from Scare's: its glyph taken off, a ghost in its dark line."""
    return glyph_icon(untiled(scare, CHARM_GLYPH, CHARM_FILL), set(), 0, GHOST_GLYPH, 3, 174, 178)


def friends_icon(hold: Rows) -> Rows:
    """Friends' icon from Hold Person's: its glyph taken off, a heart in its dark line."""
    return glyph_icon(untiled(hold, HOLD_GLYPH, HOLD_FILL), set(), 0, HEART_GLYPH, 3, HEART_DARK, HEART_LIGHT)


# A thief's Pick Pockets button (DSCLOG's PICK POCKETS: ICON 3048, where a priest's Turn Undead
# is, ICON 3044-3047 by element): Turn Undead's earth tile, its glyph taken off, a drawstring purse
# in its dark line with a gold coin in it.
TURN_EARTH_ICON, PICK_ICON = 3045, 3048
# The Spellarcher's arrows buttons (spellarrows.py; DSCLOG's PP_SHOW), ICON 3049-3052 after the
# purse's, one for each touch spell: its tile (ICON 21000 + the spell), the hand taken off, an arrow
# in the hand's dark line with its light line below and right: the touch spell, the hand's dark and
# light lines, and the tile's two fills.
ARROW_BUTTONS = {3049: (1, 202, 149, (164, 44)), 3050: (3, 49, 217, (73, 162)),
                 3051: (10, 254, 160, (159, 158)), 3052: (39, 254, 211, (209, 208))}
ARROW_GLYPH = (
    "..........DDDD..",
    "...........DDD..",
    "..........D.DD..",
    ".........D...D..",
    "........D.......",
    ".......D........",
    "......D.........",
    ".....D..........",
    "..D.D...........",
    "...D............",
    "..D.D...........",
)
TURN_GLYPH, TURN_FILL = {129, 141}, (136, 137)  # (the earth tile's glyph lines, and its browns)
PURSE_GLYPH = (  # (a purse: its tie and drawstring over the bag)
    "......D..D......",
    ".......DD.......",
    ".....DDDDDD.....",
    "......D..D......",
    ".....D....D.....",
    "....D......D....",
    "...D........D...",
    "..D..........D..",
    "..D..........D..",
    "..D..........D..",
    "...D........D...",
    "....DDDDDDDD....",
)
PURSE_COIN = {(7, 9): 45, (8, 9): 45, (7, 10): 64, (8, 10): 65, (6, 10): 65, (9, 10): 64, (7, 11): 65, (8, 11): 64}


def pick_icon(earth: Rows) -> Rows:
    """The Pick Pockets button's icon from Turn Undead's earth one."""
    out = glyph_icon(untiled(earth, TURN_GLYPH, TURN_FILL), set(), 0, PURSE_GLYPH, 2, 129, 141)
    for (x, y), colour in PURSE_COIN.items():
        out[y][x] = colour
    return out


def arrow_spell_icon(touch: Rows, dark: int, light: int, fills: Tuple[int, int]) -> Rows:
    """An arrows button's icon from its touch spell's: the hand (DARK, LIGHT) off, the arrow on."""
    return glyph_icon(untiled(touch, {dark, light}, fills), set(), 0, ARROW_GLYPH, 2, dark, light)


# Fogbolt's bolt (SEGOBJEX.GFF): a spell's record names its flight by a number (+10h, FFh none),
# a place in the game's table of 16 flights before the records (3 bytes each: the object flying,
# a byte); Magic Missile's, 4, is object 8109, BMP 2227 its picture (36 frames, one a direction)
# in a white core, cyan and a blue edge. Fogbolt's own: object 8118, Magic Missile's with picture
# 2584, the same frames in the greys 208-217 (alike in every region's palette), in place 15 of the
# table, which no spell's record names (DSCLOG's NS_SETUP).
MISSILE_OBJECT, MISSILE_PICTURE = 8109, 2227
FOG_BOLT_OBJECT, FOG_BOLT_PICTURE = 8118, 2584
FOG_BOLT_GREYS = {46: 214, 220: 211, 161: 209}  # white, cyan, blue: mid, dark and darkest grey


def recolour_frames(chunk: bytes, colours: Dict[int, int]) -> bytes:
    """A picture chunk with each frame's pixels changed by COLOURS (the runs' bytes in place)."""
    out = bytearray(chunk)
    count, = struct.unpack_from("<H", out, 4)
    for frame in range(count):
        pos = struct.unpack_from("<I", out, 6 + 4 * frame)[0] + 4
        while out[pos] != 0xFF:
            pos += 1
            while True:
                flags, length = out[pos + 1], out[pos + 3]
                pos += 4
                end = pos + length
                while pos < end:
                    c = out[pos]
                    n = 1 if c & 1 else (c >> 1) + 1
                    for at in range(pos + 1, pos + 1 + n):
                        out[at] = colours.get(out[at], out[at])
                    pos += 1 + n
                if flags & 0x80:
                    break
    return bytes(out)


def bolt_chunks(chunks: gff.Chunks) -> gff.Chunks:
    """Fogbolt's flight: its object (Magic Missile's, naming the grey picture) and picture."""
    record = bytearray(chunks[("OJFF", MISSILE_OBJECT)])
    struct.pack_into("<H", record, OJFF_ICON, FOG_BOLT_PICTURE)
    return {("OJFF", FOG_BOLT_OBJECT): bytes(record),
            ("BMP ", FOG_BOLT_PICTURE): recolour_frames(chunks[("BMP ", MISSILE_PICTURE)], FOG_BOLT_GREYS)}


def objects_beside(path: str) -> Optional[gff.Chunks]:
    """The game's SEGOBJEX.GFF in PATH's folder, with the Loader's own items' objects and
    icons (new_chunks), for their pictures (None if it can't be read)."""
    folder = os.path.dirname(path) or "."
    try:
        name = next(n for n in os.listdir(folder) if n.upper() == OBJECTS_FILE)
        with open(os.path.join(folder, name), "rb") as f:
            chunks = gff.read_gff(f.read())
        return {**chunks, **new_chunks(chunks)}
    except (OSError, StopIteration, gff.GffError, KeyError, ValueError, IndexError, struct.error):
        return None


def write_resources(source: str, dest: str, roll_store: bool = True) -> None:
    """The game's RESOURCE.GFF (SOURCE, only read) with the new spells' icons, the Pick Pockets
    button's, the descriptions of both and of the spell arrows (spelltexts.py), the save/load
    window's PAGE 1 to PAGE 4 buttons (savepages.py) and, with ROLL_STORE, the creation screen's
    STORE and RECALL (rollstore.py), to DEST."""
    with open(source, "rb") as f:
        data = f.read()
    chunks = gff.read_gff(data)
    added = {("ICON", GRACE_ICON): encode(cat_icon(decode(chunks[("ICON", STRENGTH_ICON)]))),
             ("ICON", CLAW_ICON): encode(claw_icon(decode(chunks[("ICON", GAZE_ICON)]))),
             ("ICON", FOG_ICON): encode(fog_icon(decode(chunks[("ICON", ARMOR_ICON)]))),
             ("ICON", REFLECT_ICON): encode(reflect_icon(decode(chunks[("ICON", MIRROR_ICON)]))),
             ("ICON", SPOOK_ICON): encode(spook_icon(decode(chunks[("ICON", SCARE_ICON)]))),
             ("ICON", FRIENDS_ICON): encode(friends_icon(decode(chunks[("ICON", HOLD_ICON)]))),
             ("ICON", PICK_ICON): encode(pick_icon(decode(chunks[("ICON", TURN_EARTH_ICON)]))),
             **{("ICON", icon): encode(arrow_spell_icon(decode(chunks[("ICON", 21000 + touch)]), *how))
                for icon, (touch, *how) in ARROW_BUTTONS.items()}}
    from . import spelltexts
    added.update(spelltexts.chunks())
    from . import art, game, wotrart  # the 6th-level priest spells' (Wake of the Ravager's, else tinted ones)
    folder = os.path.dirname(os.path.abspath(source))
    gpldata = art._find(folder, "GPLDATA.GFF")
    if gpldata:
        numbers = {name: 21000 + spell for spell, name in game.PRIEST6_SPELLS.items()}
        added.update(wotrart.chunks(wotrart.find_resources(folder), gpldata, numbers, chunks))
    from . import savepages
    try:
        added.update(savepages.chunks(chunks))
    except (KeyError, ValueError, IndexError, struct.error):
        pass  # (no buttons: PgUp and PgDn still change the page)
    from . import weaponpages
    try:
        added.update(weaponpages.chunks(chunks, objects_beside(source)))
    except (KeyError, ValueError, IndexError, StopIteration, struct.error):
        pass  # (no weapon pages: the panel as the game has it, the choice through the Loader)
    from . import kitpages
    try:
        added.update(kitpages.chunks(chunks))
    except (KeyError, ValueError, IndexError, StopIteration, struct.error):
        pass  # (no kit pages: no kits to choose)
    from . import rollstore
    try:
        if roll_store:
            added.update(rollstore.chunks(chunks))
    except (KeyError, ValueError, IndexError, struct.error):
        pass  # (no STORE and RECALL: the creation screen as the game has it)
    out = with_chunks(data, added)
    tmp = dest + ".tmp"
    with open(tmp, "wb") as f:
        f.write(out)
    os.replace(tmp, dest)


def _palette(source: str) -> None:
    """The game's palette (GPLDATA.GFF, beside SOURCE) for the party's pictures (spritegear: the
    half-elf man's colours are picked by their brightness). Without it, a half-elf is the human
    figure in the half-elf's colours (halfelf.py)."""
    from . import art, spritegear as sg
    gpl = art._find(os.path.dirname(os.path.abspath(source)), "GPLDATA.GFF")
    if not gpl:
        return
    try:
        with open(gpl, "rb") as f:
            sg.set_palette(art.palette_colours(gff.read_gff(f.read())[("PAL ", art.PORTRAIT_PALETTE)]))
    except (OSError, gff.GffError, KeyError, ValueError, struct.error):
        pass


def write_objects(source: str, dest: str, on: Optional[Dict[str, bool]] = None) -> Tuple[bool, Tuple[int, ...]]:
    """The game's SEGOBJEX.GFF (SOURCE, only read) with the Loader's icons, and its new items
    in their people's and chests' objects (the content switched ON: dataitems.py), to DEST.
    Whether Kalzith's object is in it (his scripts name it: without it they mustn't be
    written), and the objects added for items (the regions' copies and scripts naming them
    mustn't be written without them)."""
    with open(source, "rb") as f:
        data = f.read()
    from . import sprites
    chunks = gff.read_gff(data)
    added = new_chunks(chunks)
    room: Dict[Tuple[str, int], int] = {}
    _palette(source)
    try:  # (the party's own sprites, for what they wear: room after each to be dressed in place)
        looks = (on or {}).get("elf_looks", True) is not False  # (elves' ears, half-elves' figures)
        pictures = sprites.new_chunks(chunks, looks)
        room = sprites.new_room(chunks, pictures, looks)
        added.update(pictures)
    except (KeyError, ValueError, IndexError, struct.error):
        pass
    from . import kalzith
    try:
        his = kalzith.object_chunks(chunks)  # (the slave pens' defiler)
    except KeyError:  # (a number of his taken in this copy of the game: no Kalzith, the rest kept)
        his = {}
    added.update(his)
    try:
        added.update(bolt_chunks(chunks))
    except (KeyError, ValueError, IndexError, struct.error):
        pass  # (a game without Magic Missile's bolt: none to copy)
    from . import art, wotrart  # (Blade Barrier's and Wall of Thorns' walls: Wake of the Ravager's, else tinted)
    folder = os.path.dirname(os.path.abspath(source))
    gpldata = art._find(folder, "GPLDATA.GFF")
    if gpldata:
        added.update(wotrart.area_chunks(wotrart.find_resources(folder), chunks, gpldata))
        from . import whirlart  # (Whirlwind's funnel of dust)
        try:
            with open(gpldata, "rb") as f:
                added.update(whirlart.chunks(chunks, wotrart.stable_colours(f.read())))
        except (OSError, KeyError, ValueError, IndexError, struct.error, gff.GffError):
            pass
    from . import worldgear
    items = worldgear.data_chunks(chunks, on or {})
    added.update(items)
    from . import defaultparty
    if (on or {}).get("cilla_elf", True) is not False:  # (Cilla, an elf, drawn as one)
        added.update(defaultparty.figure_chunks(chunks, {**chunks, **added}))
    out = with_chunks(data, added, room)
    tmp = dest + ".tmp"
    with open(tmp, "wb") as f:
        f.write(out)
    os.replace(tmp, dest)
    return ("OJFF", kalzith.OBJECT) in his, tuple(sorted(n for (k, n) in items if k == "RDFF" and ("RDFF", n) not in chunks))


# The Loader's items, and the plain pictures they keep in a game that hasn't the copy
TSR_OBJECTS_ON = 218  # in DSCLOG's header: 1 once the game has opened the copy
PICTURE_CACHE = 0x0C  # an item's cache of the picture loaded for it (cleared to load anew)
LEATHER_CHEST_TYPE = 6
PLAIN: Dict[str, int] = {name: plain for name, plain, _, _, _ in ICONS}


def ready(gd, tsr_hdr) -> bool:
    """The game has opened the copy with the icons (DSCLOG says so)."""
    if tsr_hdr is None:
        return False
    return struct.unpack("<H", gd.guest.read(tsr_hdr + TSR_OBJECTS_ON, 2))[0] == 1


def _metal_types() -> Dict[int, str]:
    from . import game
    return {game.METAL_DAGGER_TYPE: "Metal Dagger", game.METAL_MACE_TYPE: "Metal Mace",
            game.METAL_GREAT_AXE_TYPE: "Metal Great Axe", game.METAL_PICK_TYPE: "Metal Pick",
            game.METAL_POLEARM_TYPE: "Metal Polearm"}


METAL_TYPES = _metal_types()


def _plate_types() -> Dict[int, str]:
    from . import game
    return {game.PLATE_CHEST_TYPE: "Warden's Chest", game.PLATE_ARMS_TYPE: "Warden's Arms",
            game.PLATE_LEGS_TYPE: "Warden's Legs"}


PLATE_TYPES = _plate_types()
OBSIDIAN_LONG_SWORD, FLAME_BLADE_NAME = 45, 0x156  # (the Flame Blade: worldgear.py)
METAL_HELM_TYPE, WARDENS_HELM = 89, 0x153  # (the game's metal helm, the Helm of Contemplation's; its name)
WOODEN_SHIELD_TYPE, GUTTERWARD = 16, 0x163  # (the game's wooden Shield; Gutterward's name: worldgear.py)


def which(rec: bytes) -> Optional[str]:
    """Which of the Loader's items an item record is, if one: the Short Sword (Shadowseeker once +1) and the
    Cloak by their types, the rings by their names and plus, Inixhide (Leather Chest Armor +1) and Kreenfang (the Gythka
    +1) by their types and plus (the game has no gythka with a plus)."""
    from . import game, npcitems, ring
    if len(rec) < game.ITEM_SIZE:
        return None
    kind, = struct.unpack_from("<H", rec, game.ITEM_TYPE)
    if kind == game.BONE_HELM_TYPE:
        return "Bone Helm"
    from . import spellarrows
    if kind == spellarrows.ARROWS_TYPE and struct.unpack_from("<H", rec, game.ITEM_NAME)[0] in spellarrows.NAMES:
        return spellarrows.NAMES[struct.unpack_from("<H", rec, game.ITEM_NAME)[0]].decode()
    plus = struct.unpack("b", rec[game.ITEM_PLUS:game.ITEM_PLUS + 1])[0]
    if kind == game.BONE_SHORT_SWORD_TYPE:
        return "Stillwater" if plus == 1 else "Bone Short Sword"
    if kind == game.BONE_AXE_TYPE:
        return "Drakejaw" if plus == 1 else "Bone Axe"
    if kind == game.OBSIDIAN_SHORT_SWORD_TYPE:
        return "Mindshard" if plus == 1 else "Obsidian Short Sword"
    if kind == game.AIR_DAGGER_TYPE:
        return "Galefang"
    if kind == game.OBSIDIAN_AXE_TYPE:
        return "Glasshewer" if plus == 2 else "Obsidian Axe"
    if kind == GREAT_AXE_TYPE and plus == 0:
        return "Great Axe"
    if kind == game.BONE_DAGGER_TYPE:
        return "Hayneedle" if plus == 1 else "Bone Dagger" if plus == 0 else None
    if kind == 17 and plus == 2:
        return "Nightsliver"
    if kind == 1 and plus == 1:
        return "Dunesong"
    if kind == game.BACK_GIRDLE_TYPE:
        return "Girdle of Back Defense"
    if kind == game.URNST_GIRDLE_TYPE:
        return "Golden Girdle of Urnst"
    if kind == game.MR_AMULET_TYPE:
        return "Amulet of Magic Resistance"
    if kind == 48 and plus == 2:
        return "Skycutter"
    if kind == game.BONE_GREAT_AXE_TYPE and plus == 0:
        return "Bone Great Axe"
    if kind == game.OBSIDIAN_GREAT_AXE_TYPE and plus == 0:
        return "Obsidian Great Axe"
    if kind == OBSIDIAN_MACE_TYPE and plus == 0 and struct.unpack_from("<H", rec, game.ITEM_NAME)[0] == MACE_NAME:
        return "Obsidian Mace"
    if kind == game.SHORT_SWORD_TYPE:
        return "Shadowseeker" if plus == 1 else "Short Sword"
    if kind == game.METAL_SHORT_SWORD_TYPE:
        return "Greenbright" if plus == 2 else "Short Sword" if plus == 0 else None
    if kind == game.BRACERS_TYPE:
        return "Bracers of Defense"
    if kind == game.ROBE_TYPE:
        return "Veiled Robe" if plus >= 2 else "Ashen Robe"
    if kind == game.METAL_SHIELD_TYPE:
        return "Ironbulwark"
    if kind == WOODEN_SHIELD_TYPE and plus == 1 and struct.unpack_from("<H", rec, game.ITEM_NAME)[0] == GUTTERWARD:
        return "Gutterward"
    if kind == game.CIRCLET_TYPE:
        return "Arrowbane"
    if kind == game.CROWN_TYPE:
        return "Sunking Crown"
    if kind == OBSIDIAN_LONG_SWORD and struct.unpack_from("<H", rec, game.ITEM_NAME)[0] == FLAME_BLADE_NAME:
        return "Flame Blade"
    if kind == game.ELVEN_CLOAK_TYPE:
        return "Cloak of Elvenkind"
    if kind == game.ELVEN_BOOTS_TYPE:
        return "Boots of Elvenkind"
    if kind in PLATE_TYPES:
        return PLATE_TYPES[kind]
    if kind == METAL_HELM_TYPE and struct.unpack_from("<H", rec, game.ITEM_NAME)[0] == WARDENS_HELM:
        return "Warden's Helm"
    if kind == game.METAL_GREAT_AXE_TYPE and plus == 2:
        return "Headsman"
    if kind == game.METAL_POLEARM_TYPE and plus == 2:
        return "Linebreaker"
    if kind == 19 and plus == 1 and struct.unpack_from("<H", rec, game.ITEM_NAME)[0] == 0x160:
        return "Thornwall"
    if kind in METAL_TYPES and plus == 0:
        return METAL_TYPES[kind]
    if plus == 1 and kind in MAGIC_KINDS:
        return MAGIC_KINDS[kind]
    if kind == game.GYTHKA_TYPE and plus == 1:
        return "Kreenfang"
    if kind == game.CLOAK_TYPE:
        return "Cloak of Protection +1"
    if ring.is_ring(rec) and plus == 1:
        name, = struct.unpack_from("<H", rec, game.ITEM_NAME)
        if name == ring.NAME_ENTRY:
            return "Ring of Protection +1"
        if name == npcitems.RING:
            return "Pehtucl's Ring of Protection +1"
    if kind == LEATHER_CHEST_TYPE and plus == 1:
        return "Inixhide"
    return None


def picture(name: str, on: bool) -> int:
    return PICTURES[name] if on else PLAIN[name]


def repaint(gd, on: bool) -> int:
    """The Loader's items anywhere in the region (carried, in a container, on the ground) with
    their own icons (ON: the game has the copy), or back to the plain ones (so a game without the
    copy never looks for a picture it hasn't). How many changed."""
    from . import game, ring
    it = ring.Items(gd)
    done = set()
    for thing in range(ring.THING_COUNT):
        for item, rec in it.chain(thing):
            name = which(rec)
            if name is None or item in done:
                continue
            want = picture(name, on)
            if struct.unpack_from("<H", rec, 0)[0] != want:
                at = it.items + item * game.ITEM_SIZE
                gd.guest.write(at, struct.pack("<H", want))
                gd.guest.write(at + PICTURE_CACHE, bytes(2))  # (a word: +0Eh and +0Fh are its spell)
                done.add(item)
    return len(done)
