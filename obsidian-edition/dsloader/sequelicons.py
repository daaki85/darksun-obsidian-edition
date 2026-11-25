"""Wake of the Ravager's own inventory icons for the weapons the Loader brings from it (the great
sword, lotulis, double spear, trikal and darts: not the javelin, PICTURES) and for the great axes,
whose icon the sequel drew anew (a two-bladed head on a long haft; Shattered Lands' is a hand
axe's size): the user's choice, 2026-11-25. Read from the player's own Wake of the Ravager (its OBJEX.GFF beside
the RESOURCE.GFF wotrart.find_resources finds) when the Loader writes its copy of SEGOBJEX.GFF:
nothing from the sequel is in the repository. Without it, the icons stay icons.ICONS' own.

The sequel's icons are its own kinds of picture (wotrart's PLNR, and PLAN: the same header and
colour map, the pixels as plain codes of that many bits, code 0 none), in its palette (RESOURCE.GFF's
PAL 1000). Each is brought into Shattered Lands' colours by kind of pixel, in its brightness order:
- wood (a brown or tan) into the game's staves' red-browns (WOOD: the Quarterstaff's);
- steel (a grey, a lavender grey) into the item's own material (MATERIALS: its blade's or head's
  greys in the game's icons: the obsidian, metal, stone or bone long sword's, gythka's or pick's);
- a gem (a magic item's: green, magenta) into the greens the game cycles (icons.GREEN): it shines;
- any other (a dart's gold point, an outline's black) into the nearest colour no region changes.
A magic one then burns as the Loader's others do (icons.glow): every other pixel of its head or
blade (its steel, a dart's gold) in the fire colours (the water's for the Bone Great Sword +1, as Hayneedle's), or every
pixel for the stronger of a kind (a +2 beside a +1, a +3 beside a +2)."""

import os
import struct
from typing import Dict, List, Optional, Sequence, Tuple

from . import art, gff, icons, wotrart

Rows = List[List[Optional[int]]]
PALETTE = ("PAL ", 1000)
PLAN = b"\xffPLAN"

# the sequel's icons (OBJEX.GFF's BMP chunks): its plain Twohand Sword's (object 604), Lotulis'
# (600), Double Spear's (602), Trikal's (601), its fast Darts' (790: its plain darts' objects, 703
# and 732, have no icon of their own), Great Axe's (608) and its magic Great Axe's, with a gem
# (661). Not its Javelin's (702): all black steel, shaft and head, a black stick in the game's
# colours; the Loader's (the Quarterstaff thinned to a shaft, a flint head) is of its shape.
PICTURES = {"great sword": 3531, "lotulis": 2390, "double spear": 3898, "trikal": 3899,
            "darts": 2165, "great axe": 2321, "magic great axe": 2239}

# Shattered Lands' colours, darkest first: the staves' wood, and each material's blade or head
WOOD = (129, 135, 136, 137, 138, 139, 140, 141)
MATERIALS = {
    "metal": (208, 209, 210, 211, 212, 213, 214, 215, 216, 217),
    "obsidian": (208, 209, 210, 211, 212, 213),
    "flint": (208, 209, 210, 211, 212, 213, 214),  # (icons.FLINT_HEAD's: the wooden kinds' heads)
    "stone": (48, 49, 24, 50, 51),
    "bone": (132, 146, 148, 152, 156),
}

# ICONS' names (and the game's Great Axe +3) drawn from the sequel's: (its picture, the material,
# the glow: None, or (colours, every other pixel))
HALF, ALL = True, False
SEQUEL: Dict[str, Tuple[str, str, Optional[Tuple[Tuple[int, ...], bool]]]] = {
    "Great Sword": ("great sword", "obsidian", None),
    "Metal Great Sword": ("great sword", "metal", None),
    "Bone Great Sword": ("great sword", "bone", None),
    "Great Sword +2": ("great sword", "metal", (icons.FIRE, HALF)),
    "Great Sword +3": ("great sword", "metal", (icons.FIRE, ALL)),
    "Bone Great Sword +1": ("great sword", "bone", (icons.WATER, HALF)),
    "Lotulis": ("lotulis", "stone", None),
    "Metal Lotulis": ("lotulis", "metal", None),
    "Obsidian Lotulis": ("lotulis", "obsidian", None),
    "Lotulis +1": ("lotulis", "stone", (icons.FIRE, HALF)),
    "Lotulis +2": ("lotulis", "metal", (icons.FIRE, ALL)),
    "Obsidian Lotulis +1": ("lotulis", "obsidian", (icons.FIRE, HALF)),
    "Double Spear": ("double spear", "flint", None),
    "Double Spear +1": ("double spear", "flint", (icons.FIRE, HALF)),
    "Double Spear +2": ("double spear", "flint", (icons.FIRE, ALL)),
    "Trikal": ("trikal", "flint", None),
    "Trikal +1": ("trikal", "flint", (icons.FIRE, HALF)),
    "Trikal +2": ("trikal", "flint", (icons.FIRE, ALL)),
    "Darts": ("darts", "flint", None),
    "Darts +1": ("darts", "flint", (icons.FIRE, ALL)),
    "Great Axe": ("great axe", "metal", None),
    "Metal Great Axe": ("great axe", "metal", None),
    "Bone Great Axe": ("great axe", "bone", None),
    "Obsidian Great Axe": ("great axe", "obsidian", None),
    "Headsman": ("great axe", "metal", (icons.FIRE, HALF)),
}
# the game's own Great Axe +3 (its object, 1018): the sequel's magic one, its gem shining green,
# as a picture of its own (the game's, 2084, is Soulcrusher's too: a hand axe, kept), the object
# pointed at it, as icons.SHINE's Cahulaks +1
GAME_GREAT_AXE = 1018
GAME_GREAT_AXE_PICTURE = 2727
GAME_GREAT_AXE_LOOK = ("magic great axe", "metal", None)


def decode(chunk: bytes) -> Rows:
    """One of the sequel's pictures as rows of its palette numbers (None: none): a PLNR or PLAN
    picture, or one of Shattered Lands' kind."""
    offset, = struct.unpack_from("<I", chunk, 6)
    width, height = struct.unpack_from("<HH", chunk, offset)
    at = offset + 4
    tag = chunk[at:at + 5]
    if tag == wotrart.PLNR:
        return [[p or None for p in row] for row in wotrart.decode_plnr(chunk)]
    if tag != PLAN:
        return icons.decode(chunk)
    bits = chunk[at + 5]
    colours = chunk[at + 6:at + 6 + (1 << bits)]
    pixels: List[int] = []
    for code in wotrart._codes(chunk[at + 6 + (1 << bits):], bits):
        if len(pixels) >= width * height:
            break
        pixels.append(code)
    pixels = (pixels + [0] * (width * height))[:width * height]
    return [[colours[p] or None for p in pixels[y * width:(y + 1) * width]] for y in range(height)]


def kind_of(rgb: Tuple[int, int, int]) -> str:
    """A colour of the sequel's palette as wood, steel, gold, a gem or other (see the module's text)."""
    r, g, b = rgb
    top, low = max(rgb), min(rgb)
    if top < 40:
        return "other"  # (an outline's black)
    if (top - low) / top < 0.3 or b > r and b >= g:
        return "steel"  # (a grey, a lavender grey; a blade's blue edge)
    if r > 200 and g > 130 and g - b > 60:
        return "gold"  # (a dart's point)
    if r > g >= b and r - b > 50:
        return "wood"
    return "gem"


def _brightness(rgb: Tuple[int, int, int]) -> float:
    return 0.3 * rgb[0] + 0.59 * rgb[1] + 0.11 * rgb[2]


def in_shattered_lands(rows: Rows, palette: Sequence[Tuple[int, int, int]], material: str,
                       stable: Sequence[Tuple[int, Tuple[int, int, int]]]) -> Tuple[Rows, Tuple[int, ...]]:
    """ROWS (the sequel's colours) in Shattered Lands' (see the module's text), and the colours its
    head or blade (the steel) came out in."""
    used = sorted({p for row in rows for p in row if p is not None})
    by_kind: Dict[str, List[int]] = {}
    for p in used:
        by_kind.setdefault(kind_of(palette[p]), []).append(p)
    ramps = {"wood": WOOD, "steel": MATERIALS[material], "gem": icons.GREEN}
    colour: Dict[int, int] = {}
    for kind, ps in by_kind.items():
        if kind not in ramps:
            for p in ps:
                colour[p] = min(stable, key=lambda e: sum((a - c) ** 2 for a, c in zip(e[1], palette[p])))[0]
            continue
        ramp = ramps[kind]
        lights = [_brightness(palette[p]) for p in ps]
        low, high = min(lights), max(lights)
        for p, light in zip(ps, lights):
            where = (light - low) / (high - low) if high > low else 0.75
            colour[p] = ramp[round(where * (len(ramp) - 1))]
    head = tuple(sorted({colour[p] for p in by_kind.get("steel", []) + by_kind.get("gold", [])}))
    return [[colour[p] if p is not None else None for p in row] for row in rows], head


# the sequel draws its Twohand Sword its long sword's size: its blade made three steps longer, as the
# Loader's own great swords' (icons.longer_blade; cut above its guard, which starts at row 7), so it
# stands bigger than the long sword (the user's ask, 2026-11-25)
SHAPES = {"great sword": lambda rows: icons.longer_blade(rows, cut=7)}


def look(rows: Rows, palette, material: str, glow, stable, kind: str = "") -> Rows:
    """The sequel's ROWS (of KIND) as an icon of Shattered Lands: its shape (SHAPES), in its
    colours, and burning as GLOW says."""
    out, head = in_shattered_lands(SHAPES.get(kind, lambda r: r)(rows), palette, material, stable)
    if glow is None:
        return out
    colours, half = glow
    return icons.glow(out, lambda p, x, y: p in head and (not half or (x + y) % 2 == 0), colours)


def read(wotr_resources: Optional[str]) -> Tuple[Dict[str, Rows], Sequence[Tuple[int, int, int]]]:
    """The sequel's PICTURES (by kind) and its palette, from the OBJEX.GFF beside WOTR_RESOURCES
    ({} and [] if it can't be read)."""
    if not wotr_resources:
        return {}, []
    objex = art._find(os.path.dirname(wotr_resources), wotrart.OBJECTS_FILE)
    try:
        with open(objex or "", "rb") as f:
            theirs = gff.read_gff(f.read())
        with open(wotr_resources, "rb") as f:
            palette = art.palette_colours(gff.read_gff(f.read())[PALETTE])
        return {kind: decode(theirs[("BMP ", number)]) for kind, number in PICTURES.items()}, palette
    except (OSError, KeyError, ValueError, IndexError, struct.error, gff.GffError):
        return {}, []


def chunks(wotr_resources: Optional[str], sl_chunks: gff.Chunks, added: gff.Chunks, sl_gpldata: str) -> gff.Chunks:
    """For the Loader's SEGOBJEX.GFF (SL_CHUNKS the game's, ADDED icons.new_chunks'): the pictures
    of SEQUEL's items and of the game's Great Axe +3 (GAME_GREAT_AXE_PICTURE, its object pointed
    at it) drawn from the sequel's, and the item box's
    copies of those among icons.BOX_TALL; {} without the sequel."""
    theirs, palette = read(wotr_resources)
    if not theirs:
        return {}
    try:
        with open(sl_gpldata, "rb") as f:
            stable = wotrart.stable_colours(f.read())
    except (OSError, ValueError, IndexError, struct.error, gff.GffError):
        return {}
    if not stable:
        return {}
    out: gff.Chunks = {}
    for name, _, _, icon, _ in icons.ICONS:
        if name in SEQUEL:
            kind, material, glow = SEQUEL[name]
            out[("BMP ", icon)] = icons.encode(look(theirs[kind], palette, material, glow, stable, kind))
    record = added.get(("OJFF", GAME_GREAT_AXE)) or sl_chunks.get(("OJFF", GAME_GREAT_AXE))
    if record is not None:
        record = bytearray(record)
        struct.pack_into("<H", record, icons.OJFF_ICON, GAME_GREAT_AXE_PICTURE)
        out[("OJFF", GAME_GREAT_AXE)] = bytes(record)
        kind, material, glow = GAME_GREAT_AXE_LOOK
        out[("BMP ", GAME_GREAT_AXE_PICTURE)] = icons.encode(look(theirs[kind], palette, material, glow, stable))
    for i, icon in enumerate(icons.BOX_TALL):
        if ("BMP ", icon) in out:
            out[("BMP ", icons.BOX_SMALL + i)] = icons.encode(icons.fit_box(icons.decode(out[("BMP ", icon)])))
    return out
