"""The magic items' shine in Wake of the Ravager (icons.SHINE's, for the sequel's own items).

The sequel cycles colours 1-31 of its palette in five runs: 1-5 a bright blue (BLUE), 6-10 pink and
violet (VIOLET), 11-15 green (GREEN), 16-23 the fire (FIRE) and 24-31 the water's blue-greys (WATER).
Its magic items' icons have a few pixels in one of them, so they shine in the inventory, a shop and on
the ground; twelve have none or one or two (a survey of its OBJEX.GFF's item records with a plus or a
power, 2026-11-26), so they lie still beside the others. The Loader gives them the shine (SHINE): every
other pixel of their blade, metal, gem or brightest shades in a cycled run, as icons.SHINE does for
Shattered Lands' twenty. Each is its object's own icon (no other object shows it), changed in place in
the Loader's copy of OBJEX.GFF (ravager.objects_fixed): so saved games shine too. Read from the player's
own OBJEX.GFF: nothing from the sequel is in the repository.
"""

import struct
from typing import Callable, FrozenSet, Tuple

from . import gff, icons

BLUE = tuple(range(1, 6))
VIOLET = tuple(range(6, 11))
GREEN = tuple(range(11, 16))
FIRE = tuple(range(16, 24))
WATER = tuple(range(24, 32))
CYCLED = frozenset(range(1, 32))
OJFF_ICON = icons.OJFF_ICON


class Shine:
    """Item NAME's object, the palette numbers of its icon to shine (every other one, by x + y, unless
    ALL), and the cycled run they step along."""

    def __init__(self, name: str, obj: int, colours: FrozenSet[int], run: Tuple[int, ...], every_other: bool = True):
        self.name, self.obj, self.colours, self.run, self.every_other = name, obj, colours, run, every_other

    def which(self) -> Callable[[int, int, int], bool]:
        return lambda p, x, y: p in self.colours and (not self.every_other or (x + y) % 2 == 0)


# weapons in the fire, as Shattered Lands' magic weapons; armour, worn things and stones in the water's
# blue-greys; the Chatchka's violet and the Boots' green in their own colour's run
SHINE: Tuple[Shine, ...] = (
    Shine("Dragonsbane +4", 675, frozenset((232, 241, 242, 244, 245, 246, 247)), FIRE),  # (the blade's greys)
    Shine("Toothed Club +2", 30014, frozenset((201, 202, 203, 192)), FIRE),  # (the bone)
    Shine("Chatchka +1", 733, frozenset((144, 145, 146, 147)), VIOLET),  # (its blue-violet blades)
    Shine("Gloves +3", 680, frozenset((234, 235, 236)), WATER),  # (the steel's blue-greys)
    Shine("Armor +1 (leather, 833)", 833, frozenset((198, 199, 180)), WATER),  # (its brightest browns, the red)
    Shine("Armor +3 (leather, 834)", 834, frozenset((198, 199, 180)), WATER),
    Shine("Armor +3 (scale, 853)", 853, frozenset((136, 137, 138, 140)), WATER),  # (the scales' cyans)
    Shine("Boots", 1603, frozenset((115, 116, 117)), GREEN),  # (the greens)
    Shine("Amulet", 30010, frozenset((99, 100, 101, 107)), FIRE),  # (the gold)
    Shine("Ioun Stone", 30012, frozenset((233, 234)), WATER),
    Shine("Necklace", 31209, frozenset((198, 199, 233, 247)), WATER),  # (the pendant)
    Shine("Rod", 31202, frozenset((213, 214, 215, 216)), WATER),  # (the wood's lighter browns)
)


def icon_of(chunks: gff.Chunks, obj: int):
    """Object OBJ's icon number, None if the object or its picture isn't there."""
    rec = chunks.get(("OJFF", obj))
    if rec is None:
        return None
    icon, = struct.unpack_from("<H", rec, OJFF_ICON)
    return icon if ("BMP ", icon) in chunks else None


def shone(rows, shine: Shine):
    """ROWS (the sequel's palette numbers, None none) with SHINE's pixels in its run."""
    return icons.glow(rows, shine.which(), shine.run)


def chunks(objects: gff.Chunks) -> gff.Chunks:
    """The icons of SHINE's objects, shining, for the copy of OBJEX.GFF; one without SHINE's colours
    (another release's picture), or not there, is left as it is."""
    from . import sequelicons
    out: gff.Chunks = {}
    for s in SHINE:
        icon = icon_of(objects, s.obj)
        if icon is None:
            continue
        rows = sequelicons.decode(objects[("BMP ", icon)])
        if not any(p in s.colours for r in rows for p in r):
            continue
        out[("BMP ", icon)] = icons.encode(shone(rows, s))
    return out
