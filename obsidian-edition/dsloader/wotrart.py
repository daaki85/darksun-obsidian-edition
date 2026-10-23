"""Wake of the Ravager's spell icons in Shattered Lands, read from the player's own Wake of the
Ravager (its RESOURCE.GFF) when the Loader writes its copy of Shattered Lands' RESOURCE.GFF:
nothing from either game is in the repository.

Wake of the Ravager's icons (ICON 21000 + the spell, as Shattered Lands') are its own kind of
picture: the frame's header as Shattered Lands has it (16 by 16), then no rows but 0FFh, "PLNR",
the bits a pixel (4 or 5) and a colour map of that many bits' worth of palette numbers, then the
pixels as codes of those bits, the highest first. Code 0 is an escape: 0 then 0 is a pixel of
colour 0, 0 then k the last pixel k + 2 more times. (Worked out from the 101 spells both games
have: 38 come out the same as Shattered Lands' pixel for pixel, the rest within the colours its
fewer allow.) Its palette (RESOURCE.GFF's PAL 1000) isn't Shattered Lands', so each colour becomes
the nearest of Shattered Lands' that no region changes (the same in all its GPLDATA.GFF palettes).

ICONS: the 6th-level priest spells' icons, by name: its number in Wake of the Ravager (Whirlwind,
which it hasn't, takes its Sand Storm's, "a very large version of a dust devil"). Without Wake of
the Ravager (or for an icon it can't give), FALLBACKS: a Shattered Lands icon (its template's, or
the nearest in kind) tinted halfway toward the spell's colour, in the same stable colours."""

import os
import struct
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

from . import art, gff, icons

ICONS: Dict[str, int] = {
    "Blade Barrier": 21208, "Fire Seeds": 21209, "Heal": 21210, "Harm": 21211, "Heartseeker": 21212,
    "Sunstroke": 21213, "Wall of Thorns": 21214, "Water of Life": 21215, "Whirlwind": 21205,
}
# ... and without it: Shattered Lands' icon (ICON 21000 + its spell) and the tint, by name
FALLBACKS: Dict[str, Tuple[int, Tuple[int, int, int]]] = {
    "Heal": (21127, (255, 230, 140)), "Harm": (21128, (110, 0, 20)),  # Cure and Cause Critical Wounds'
    "Blade Barrier": (21137, (180, 190, 210)), "Wall of Thorns": (21073, (40, 110, 30)),  # Wall of Fire's, Entangle's
    "Sunstroke": (21131, (255, 210, 0)), "Fire Seeds": (21120, (255, 90, 0)),  # Flame Strike's, Produce Fire's
    "Heartseeker": (21136, (90, 140, 40)), "Water of Life": (21127, (40, 110, 255)),  # Slay Living's, Cure Critical's
    "Whirlwind": (21083, (215, 215, 230)),  # Dust Devil's
}
HEAL_SPIN = (211, b"HEAL:")  # (how a RESOURCE.GFF is told for Wake of the Ravager's)
PALETTE = ("PAL ", 1000)
PLNR = b"\xffPLNR"
GOG_NAMES = ("Dark Sun Wake of the Ravager", "Dark Sun - Wake of the Ravager", "Wake of the Ravager")


def _codes(data: bytes, bits: int) -> Iterator[int]:
    acc = n = 0
    for byte in data:
        acc, n = (acc << 8) | byte, n + 8
        while n >= bits:
            n -= bits
            yield (acc >> n) & ((1 << bits) - 1)


def decode_plnr(chunk: bytes) -> List[List[int]]:
    """A PLNR icon's rows of palette numbers (Wake of the Ravager's palette)."""
    offset, = struct.unpack_from("<I", chunk, 6)
    width, height = struct.unpack_from("<HH", chunk, offset)
    at = offset + 4
    if chunk[at:at + 5] != PLNR:
        raise ValueError("not a PLNR picture")
    bits = chunk[at + 5]
    colours = chunk[at + 6:at + 6 + (1 << bits)]
    codes, pixels, last = _codes(chunk[at + 6 + (1 << bits):], bits), [], 0
    for code in codes:
        if len(pixels) >= width * height:
            break
        if code:
            pixels.append(code)
            last = code
            continue
        count = next(codes, 0)
        if count:
            pixels += [last] * (count + 2)
        else:
            pixels.append(0)
            last = 0
    pixels = (pixels + [0] * (width * height))[:width * height]
    return [[colours[p] for p in pixels[y * width:(y + 1) * width]] for y in range(height)]


def is_wotr_resources(path: str) -> bool:
    try:
        with open(path, "rb") as f:
            spin = gff.read_gff(f.read()).get(("SPIN", HEAL_SPIN[0]), b"")
    except (OSError, gff.GffError, ValueError, struct.error):
        return False
    return spin.startswith(HEAL_SPIN[1])


def find_resources(sl_dir: Optional[str], given: Optional[str] = None) -> Optional[str]:
    """Wake of the Ravager's RESOURCE.GFF: in GIVEN (a folder), else in a folder beside Shattered
    Lands' SL_DIR with Ravager in its name, else None."""
    folders = [given] if given else []
    if sl_dir:
        parent = os.path.dirname(os.path.abspath(sl_dir))
        try:
            folders += [os.path.join(parent, d) for d in sorted(os.listdir(parent)) if "ravager" in d.lower()]
        except OSError:
            pass
    for folder in folders:
        path = art._find(folder, "RESOURCE.GFF") if folder and os.path.isdir(folder) else None
        if path and is_wotr_resources(path):
            return path
    return None


def stable_colours(gpl_data: bytes) -> List[Tuple[int, Tuple[int, int, int]]]:
    """Shattered Lands' palette numbers no region changes (alike in every GPLDATA.GFF palette)."""
    palettes = [art.palette_colours(v) for k, v in sorted(gff.read_gff(gpl_data).items())
                if k[0] == "PAL " and len(v) >= 768]
    return [(i, palettes[0][i]) for i in range(256) if all(p[i] == palettes[0][i] for p in palettes)]


def to_shattered_lands(rows: Sequence[Sequence[int]], wotr_palette, stable) -> List[List[int]]:
    """ROWS (Wake of the Ravager's palette) in the nearest of Shattered Lands' STABLE colours."""
    cache: Dict[int, int] = {}

    def nearest(p: int) -> int:
        if p not in cache:
            rgb = wotr_palette[p]
            cache[p] = min(stable, key=lambda e: sum((a - b) ** 2 for a, b in zip(e[1], rgb)))[0]
        return cache[p]
    return [[nearest(p) for p in row] for row in rows]


def spell_icons(wotr_resources: str, sl_gpldata: str) -> Dict[str, List[List[int]]]:
    """Each of ICONS as rows of Shattered Lands' palette numbers ({} if it can't be read)."""
    try:
        with open(wotr_resources, "rb") as f:
            chunks = gff.read_gff(f.read())
        with open(sl_gpldata, "rb") as f:
            stable = stable_colours(f.read())
        palette = art.palette_colours(chunks[PALETTE])
        return {name: to_shattered_lands(decode_plnr(chunks[("ICON", number)]), palette, stable)
                for name, number in ICONS.items()}
    except (OSError, KeyError, ValueError, IndexError, struct.error, gff.GffError):
        return {}


# Its pictures on the ground for two of them (OBJEX.GFF, beside its RESOURCE.GFF): its table of a
# spell's area picture gives Blade Barrier object 8432 (circling blades) and Wall of Thorns 8425
# (a tangle of thorns), neither in Shattered Lands. AREA_OBJECTS: each, by name, its object and
# picture (BMP) numbers in the Loader's copy of SEGOBJEX.GFF (the same objects; free pictures),
# made from Shattered Lands' fire wall's object (8419: its +2 and +4 the picture's anchor, from
# Wake of the Ravager's) and recoloured in the stable colours (DSCLOG's NS_SETUP puts them in the
# walls' own entries, AREA_NEW). Without Wake of the Ravager, AREA_FALLBACKS: the fire wall's own
# picture in a colour of the spell's, as bright as each pixel.
OBJECTS_FILE = "OBJEX.GFF"
FIRE_WALL_OBJECT = 8419
AREA_OBJECTS: Dict[str, Tuple[int, int]] = {"Blade Barrier": (8432, 2650), "Wall of Thorns": (8425, 2651)}
AREA_FALLBACKS: Dict[str, Tuple[int, int, int]] = {"Blade Barrier": (200, 210, 235), "Wall of Thorns": (120, 80, 35)}
OJFF_ANCHOR = 2  # (two words: x and y)


def _nearest_map(colours: Sequence[Tuple[int, int, int]], stable) -> Dict[int, int]:
    return {p: min(stable, key=lambda e: sum((a - b) ** 2 for a, b in zip(e[1], rgb)))[0]
            for p, rgb in enumerate(colours)}


def area_chunks(wotr_resources: Optional[str], sl_chunks: gff.Chunks, sl_gpldata: str) -> gff.Chunks:
    """AREA_OBJECTS' objects and pictures for the Loader's SEGOBJEX.GFF (SL_CHUNKS the game's):
    Wake of the Ravager's (beside WOTR_RESOURCES), else AREA_FALLBACKS' ({} if neither can be made)."""
    try:
        with open(sl_gpldata, "rb") as f:
            gpl = f.read()
        stable = stable_colours(gpl)
        sl_palette = next(art.palette_colours(v) for k, v in sorted(gff.read_gff(gpl).items())
                          if k[0] == "PAL " and len(v) >= 768)
        wall = sl_chunks[("OJFF", FIRE_WALL_OBJECT)]
        wall_picture = sl_chunks[("BMP ", struct.unpack_from("<H", wall, icons.OJFF_ICON)[0])]
    except (OSError, StopIteration, KeyError, ValueError, IndexError, struct.error, gff.GffError):
        return {}
    theirs: gff.Chunks = {}
    folder = os.path.dirname(wotr_resources) if wotr_resources else None
    objex = art._find(folder, OBJECTS_FILE) if folder else None
    try:
        if objex:
            with open(objex, "rb") as f:
                theirs = gff.read_gff(f.read())
            with open(wotr_resources, "rb") as f:
                wotr_map = _nearest_map(art.palette_colours(gff.read_gff(f.read())[PALETTE]), stable)
    except (OSError, KeyError, ValueError, IndexError, struct.error, gff.GffError):
        theirs = {}
    out: gff.Chunks = {}
    for name, (number, picture) in AREA_OBJECTS.items():
        record = bytearray(wall)
        struct.pack_into("<H", record, icons.OJFF_ICON, picture)
        try:
            own = theirs[("OJFF", number)]
            frames = icons.recolour_frames(theirs[("BMP ", struct.unpack_from("<H", own, icons.OJFF_ICON)[0])], wotr_map)
            record[OJFF_ANCHOR:OJFF_ANCHOR + 4] = own[OJFF_ANCHOR:OJFF_ANCHOR + 4]
        except (KeyError, ValueError, IndexError, struct.error):
            tint = AREA_FALLBACKS[name]
            shades = [tuple(c * (r * 3 + g * 6 + b) // 2550 for c in tint) for r, g, b in sl_palette]
            frames = icons.recolour_frames(wall_picture, _nearest_map(shades, stable))
        out[("OJFF", number)] = bytes(record)
        out[("BMP ", picture)] = frames
    return out


def tinted(rows: Sequence[Sequence[Optional[int]]], palette, stable, tint: Tuple[int, int, int]) -> List[List[Optional[int]]]:
    """ROWS (Shattered Lands' palette numbers) each halfway toward TINT, in the nearest STABLE colour."""
    cache: Dict[int, int] = {}

    def shade(p: int) -> int:
        if p not in cache:
            rgb = tuple((a + b) // 2 for a, b in zip(palette[p], tint))
            cache[p] = min(stable, key=lambda e: sum((a - b) ** 2 for a, b in zip(e[1], rgb)))[0]
        return cache[p]
    return [[shade(p) if p is not None else None for p in row] for row in rows]


def chunks(wotr_resources: Optional[str], sl_gpldata: str, numbers: Dict[str, int],
           sl_chunks: Optional[Dict[Tuple[str, int], bytes]] = None) -> Dict[Tuple[str, int], bytes]:
    """ICON chunks for Shattered Lands, NUMBERS each spell's icon number there: Wake of the
    Ravager's (WOTR_RESOURCES, if found), else FALLBACKS' from SL_CHUNKS (its RESOURCE.GFF's)."""
    found = spell_icons(wotr_resources, sl_gpldata) if wotr_resources else {}
    out = {("ICON", numbers[name]): icons.encode(rows) for name, rows in found.items() if name in numbers}
    if sl_chunks is None:
        return out
    try:
        with open(sl_gpldata, "rb") as f:
            gpl = f.read()
        stable = stable_colours(gpl)
        palette = next(art.palette_colours(v) for k, v in sorted(gff.read_gff(gpl).items())
                       if k[0] == "PAL " and len(v) >= 768)
    except (OSError, StopIteration, ValueError, IndexError, struct.error, gff.GffError):
        return out
    for name, number in numbers.items():
        if ("ICON", number) in out or name not in FALLBACKS:
            continue
        icon, tint = FALLBACKS[name]
        try:
            out[("ICON", number)] = icons.encode(tinted(icons.decode(sl_chunks[("ICON", icon)]), palette, stable, tint))
        except (KeyError, ValueError, IndexError, struct.error):
            pass  # (no icon: the game draws none)
    return out
