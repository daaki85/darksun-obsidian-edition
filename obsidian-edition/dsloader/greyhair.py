"""Grey hair on the party's map figures as they age (with the Ages and magical aging rule): each
figure's hair (spriteparts' Parts.hair, found frame by frame) recoloured, shade for shade, by the
member's age category (aging.category): iron grey streaks when middle-aged, grey when old, white
when venerable. Done as the Loader dresses a member's pictures (sprites.Pictures.build), after
what they wear, and only on pixels still in the hair's own colours (a helm or a cloak over the hair
is left as it is).

MAPS: for each look (a model, or a half-elf's own figure: halfelf.MAN or halfelf.WOMAN), for each
age category, the hair's colours and the colour each becomes. SPECKLE: where a category greys only
some of the hair (streaks), which pixels: (period, count) by the pixel's place in the figure's own
frame, a pixel greyed where (x + 2 * y) % period < count. Races with no hair (Athasian dwarves and
muls are hairless; a thri-kreen has a carapace) have none."""

from typing import Dict, List, Optional, Sequence, Set, Tuple

MIDDLE, OLD, VENERABLE = 1, 2, 3  # (aging.category's)
Rows = List[List[Optional[int]]]
Point = Tuple[int, int]

MAPS: Dict[int, Dict[int, Dict[int, int]]] = {}
SPECKLE: Dict[int, Dict[int, Tuple[int, int]]] = {}


def look(model: int, figure: int) -> int:
    """What a figure's hair is drawn as: a half-elf's own figure (its object), else its model."""
    from . import halfelf
    return figure if figure in (halfelf.MAN, halfelf.WOMAN) else model


def aged(rows: Rows, hair: Set[Point], key: int, stage: int, pad: int) -> Rows:
    """ROWS (a dressed frame, padded by PAD) with the HAIR's pixels (in the frame's own places)
    greyed for age category STAGE, as MAPS has KEY's; the rest as it was."""
    colours = MAPS.get(key, {}).get(stage)
    if not colours or not hair:
        return rows
    period, count = SPECKLE.get(key, {}).get(stage, (1, 1))
    for x, y in hair:
        if (x + 2 * y) % period >= count:
            continue
        px, py = x + pad, y + pad
        if 0 <= py < len(rows) and 0 <= px < len(rows[py]):
            new = colours.get(rows[py][px])
            if new is not None:
                rows[py][px] = new
    return rows


def stage_of(gd, member: int) -> int:
    """A party member's age category (0 young, or none: the rule off, no age given yet)."""
    from . import aging, game
    if not getattr(gd, "rules", 0) & game.RULE_AGING:
        return 0
    try:
        sheet = gd.sheet(member)
        age = aging.age_of(sheet)
        return aging.category(sheet[game.SHEET_RACE], age) if age is not None else 0
    except (IndexError, ValueError, KeyError):
        return 0
