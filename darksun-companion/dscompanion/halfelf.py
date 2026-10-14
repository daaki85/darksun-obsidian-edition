"""Half-elves' own colours on the map: the game draws a half-elf with the human's pictures (objects
306 and 307 name the same as 300 and 301), so the Loader's copy of SEGOBJEX (sprites.py) recolours
them, in colours the party's pictures already have.

A half-elf man: fair-haired (the human man's dark hair, the top rows of his head, in golden
browns), a green tunic (the sheen on his black one), brown boots and bronze wristbands. A
half-elf woman: golden hair (hers is brown), a purple cloak for her green one, purple wristbands and
red boots for her blue ones.

Worn gear is drawn over these (spritegear.armed): armour, a cloak or boots in their own colours; so `over` keeps what the gear changed and recolours only what it left alone.
"""

from typing import Dict, List, Optional, Set, Tuple

Rows = List[List[Optional[int]]]

MAN, WOMAN = 306, 307  # (the party objects: 300 + the figure picked at creation)

# The man's hair (his head's top rows: below them these browns and greys are his face and clothes)
MAN_HAIR_ROWS = 6
MAN_HAIR = {69: 179, 70: 180, 210: 180, 212: 64, 50: 200, 213: 65, 48: 179, 23: 180, 29: 65}
# ... below them: the tunic's greys green, and from MAN_BOOT_ROWS above his feet the boots' brown
MAN_TUNIC = {48: 188, 20: 188, 23: 189, 50: 190, 29: 191, 213: 191, 210: 189, 212: 190}
MAN_BOOT_ROWS = 7
MAN_BOOTS = {69: 204, 70: 207, 50: 205, 29: 168, 23: 207, 48: 204, 20: 204, 210: 207, 213: 168}
MAN_BANDS = {250: 180, 249: 182}  # (green wristbands bronze)
BANDS = {250: 176, 249: 176}  # (hers purple)

# The woman's hair: the browns of her hair, as one patch from the top of her head
HAIR_COLOURS = frozenset((128, 129, 134, 135, 136, 137, 138, 179, 180))
HAIR = {129: 180, 128: 181, 134: 181, 136: 182, 135: 181, 137: 182, 179: 200, 180: 182, 138: 65}
HAIR_LEAST = 15  # (fewer, and something is over her head: her darkest browns in its top half)
# ... and the rest of her: the cloak's greens purple, the wristbands too, the boots' blues red
CLOAK = {188: 174, 189: 175, 190: 176, 191: 176, 53: 175, 54: 176, 55: 176, 56: 176, 69: 174,
         70: 175, 42: 176}
BOOTS = {158: 195, 159: 202, 160: 76, 38: 77, 48: 16}
BODY = {**CLOAK, **BANDS, **BOOTS}


def _fill(rows: Rows, seeds) -> Set[Tuple[int, int]]:
    """The pixels of the hair's colours joined to SEEDS."""
    h, w = len(rows), len(rows[0]) if rows else 0
    seen: Set[Tuple[int, int]] = set()
    stack = list(seeds)
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or not (0 <= x < w and 0 <= y < h) or rows[y][x] not in HAIR_COLOURS:
            continue
        seen.add((x, y))
        stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return seen


def _hair(rows: Rows) -> Set[Tuple[int, int]]:
    """The woman's hair in one frame: from the hair's colours in its top two rows."""
    filled = [y for y, r in enumerate(rows) if any(p is not None for p in r)]
    if not filled:
        return set()
    top, bottom = filled[0], filled[-1]
    w = len(rows[0])
    hair = _fill(rows, [(x, y) for y in range(top, top + 2) for x in range(w) if rows[y][x] in HAIR_COLOURS])
    if len(hair) < HAIR_LEAST:  # (an arm or a weapon above her head)
        hair = _fill(rows, [(x, y) for y in range(top, top + (bottom - top) // 2) for x in range(w)
                            if rows[y][x] in (128, 129)])
    return hair


def recolour(rows: Rows, figure: int) -> Rows:
    """One frame of the human's picture as FIGURE's (unchanged, but a half-elf)."""
    if figure == MAN:
        filled = [y for y, r in enumerate(rows) if any(p is not None for p in r)]
        if not filled:
            return rows
        top, bottom = filled[0], filled[-1]

        def colours(y: int) -> Dict[int, int]:
            if y < top + MAN_HAIR_ROWS:
                return MAN_HAIR
            return {**(MAN_BOOTS if y > bottom - MAN_BOOT_ROWS else MAN_TUNIC), **MAN_BANDS}
        return [[p if p is None else colours(y).get(p, p) for p in r] for y, r in enumerate(rows)]
    if figure == WOMAN:
        hair = _hair(rows)
        return [[p if p is None else (HAIR if (x, y) in hair else BODY).get(p, p) for x, p in enumerate(r)]
                for y, r in enumerate(rows)]
    return rows


def over(dressed: Rows, rows: Rows, figure: int, pad: int) -> Rows:
    """DRESSED (ROWS with gear, padded by PAD) in FIGURE's colours where the gear left ROWS as
    they were."""
    if figure not in (MAN, WOMAN):
        return dressed
    own = recolour(rows, figure)
    for y, r in enumerate(rows):
        out = dressed[y + pad]
        for x, p in enumerate(r):
            if p is not None and out[x + pad] == p:
                out[x + pad] = own[y][x]
    return dressed
