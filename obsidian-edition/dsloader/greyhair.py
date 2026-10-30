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
muls are hairless; a thri-kreen has a carapace) keep their looks."""

from typing import Dict, List, Optional, Set, Tuple

from . import spriteparts as sp

MIDDLE, OLD, VENERABLE = 1, 2, 3  # (aging.category's)
Rows = List[List[Optional[int]]]
Point = Tuple[int, int]

# (each to stable greys, 208-217, dark to light as the hair's own shades: iron grey streaks, grey, white)
MAPS: Dict[int, Dict[int, Dict[int, int]]] = {
    2095: {  # human man
        1: {23: 212, 29: 214, 48: 211, 50: 213, 69: 211, 70: 212},
        2: {23: 213, 29: 215, 48: 212, 50: 214, 69: 212, 70: 213},
        3: {23: 215, 29: 217, 48: 214, 50: 216, 69: 214, 70: 215},
    },
    2099: {  # human woman
        1: {128: 212, 133: 213, 136: 213, 179: 213, 180: 214},
        2: {128: 212, 129: 211, 133: 213, 134: 212, 135: 213, 136: 213, 179: 213, 180: 214},
        3: {128: 215, 129: 214, 133: 216, 134: 215, 135: 216, 136: 216, 179: 216, 180: 217},
    },
    2061: {  # elf man
        1: {44: 213, 45: 214, 64: 211, 65: 214, 128: 209, 135: 210, 136: 210, 137: 211, 138: 211, 139: 212, 140: 212, 179: 210, 180: 210, 181: 212, 182: 213, 200: 212},
        2: {44: 214, 45: 215, 64: 212, 65: 214, 128: 210, 135: 210, 136: 211, 137: 211, 138: 212, 139: 212, 140: 213, 179: 210, 180: 211, 181: 212, 182: 213, 200: 213},
        3: {44: 216, 45: 217, 64: 214, 65: 216, 128: 212, 135: 212, 136: 213, 137: 213, 138: 214, 139: 214, 140: 215, 179: 212, 180: 213, 181: 214, 182: 215, 200: 215},
    },
    2059: {  # elf woman
        1: {44: 213, 45: 214, 64: 211, 65: 214, 128: 209, 135: 210, 136: 210, 137: 211, 138: 211, 139: 212, 140: 212, 179: 210, 180: 210, 181: 212, 182: 213, 200: 212, 201: 211},
        2: {44: 214, 45: 215, 64: 212, 65: 214, 128: 210, 135: 210, 136: 211, 137: 211, 138: 212, 139: 212, 140: 213, 179: 210, 180: 211, 181: 212, 182: 213, 200: 213, 201: 212},
        3: {44: 216, 45: 217, 64: 214, 65: 216, 128: 212, 135: 212, 136: 213, 137: 213, 138: 214, 139: 214, 140: 215, 179: 212, 180: 213, 181: 214, 182: 215, 200: 215, 201: 214},
    },
    306: {  # half-elf man (his own figure)
        1: {65: 215, 182: 214, 200: 213},
        2: {64: 212, 65: 215, 179: 210, 180: 211, 181: 212, 182: 214, 200: 213},
        3: {64: 214, 65: 217, 179: 212, 180: 213, 181: 214, 182: 216, 200: 215},
    },
    307: {  # half-elf woman (her own figure)
        1: {65: 215, 182: 214, 200: 213},
        2: {64: 212, 65: 215, 179: 210, 180: 211, 181: 212, 182: 214, 200: 213},
        3: {64: 214, 65: 217, 179: 212, 180: 213, 181: 214, 182: 216, 200: 215},
    },
    2072: {  # half-giant man
        1: {128: 211, 129: 210, 133: 212, 179: 211, 180: 212},
        2: {128: 212, 129: 211, 133: 213, 179: 212, 180: 214},
        3: {128: 215, 129: 213, 133: 216, 179: 215, 180: 216},
    },
    2074: {  # half-giant woman
        1: {128: 211, 129: 210, 133: 212, 134: 211, 179: 211, 180: 212, 181: 213},
        2: {128: 211, 129: 210, 133: 212, 134: 211, 179: 211, 180: 213, 181: 214},
        3: {128: 213, 129: 211, 133: 214, 134: 213, 179: 213, 180: 215, 181: 216},
    },
    2068: {  # halfling man
        1: {180: 213, 201: 214},
        2: {128: 211, 129: 210, 179: 212, 180: 213, 201: 214, 254: 209},
        3: {128: 213, 129: 212, 179: 214, 180: 216, 201: 217, 254: 211},
    },
    2070: {  # halfling woman
        1: {181: 213, 182: 214, 183: 215, 184: 216, 200: 213, 201: 212},
        2: {128: 209, 179: 210, 180: 211, 181: 213, 182: 214, 183: 215, 184: 216, 200: 213, 201: 212},
        3: {128: 211, 179: 212, 180: 213, 181: 215, 182: 216, 183: 217, 184: 46, 200: 215, 201: 214},
    },
}
SPECKLE: Dict[int, Dict[int, Tuple[int, int]]] = {2095: {1: (7, 3)}, 2061: {1: (5, 2)}, 2059: {1: (5, 2)}, 2072: {1: (6, 2)}, 2074: {1: (6, 2)}}

# Finding the hair to grey (hair()), apart from what spriteparts finds for the gear (which is left
# as it is): the hair's colours where spriteparts' list leaves some out (the elf woman's crown
# highlights, the halfling man's lit half...), each model's own
COLOURS: Dict[int, frozenset] = {
    2061: frozenset((44, 45, 64, 65, 179, 180, 181, 182, 200)),
    2059: frozenset((44, 45, 64, 65, 179, 180, 181, 182, 200, 201)),
    2099: frozenset((128, 129, 133, 134, 135, 136, 179, 180)),
    2068: frozenset((128, 129, 179, 180, 201)),
    2070: frozenset((179, 180, 181, 182, 183, 184, 200, 201)),
    2074: frozenset((128, 129, 133, 134, 179, 180, 181)),
}
# the hair kept inside its zone as it is followed (where the face has the hair's colours: not
# the halfling woman, whose fringe falls below the brow)
STRICT = frozenset((2095, 2099, 2072, 2074))
# the head placed by hand where finding it takes the bow's tip for the crown (the bow frames):
# (top, left, right, the row the shoulders start on), as spriteparts.HEADS
HEADS: Dict[Tuple[int, bool, int], Tuple[int, int, int, int]] = {
    (2095, True, 10): (3, 5, 12, 9), (2095, True, 11): (3, 5, 11, 8),
    (2099, True, 10): (3, 2, 9, 9), (2099, True, 11): (3, 4, 10, 8),
    (2061, True, 10): (3, 2, 9, 9), (2061, True, 11): (3, 4, 10, 7),
    (2059, True, 10): (3, 2, 9, 9), (2059, True, 11): (3, 4, 10, 7),
    (2068, True, 10): (3, 1, 9, 9), (2068, True, 11): (3, 4, 11, 6),
    (2070, True, 10): (3, 0, 11, 10), (2070, True, 11): (2, 3, 12, 6),
    (2072, True, 10): (4, 7, 15, 13), (2072, True, 11): (4, 9, 19, 11),
    (2074, True, 10): (4, 6, 15, 14), (2074, True, 11): (3, 8, 21, 11),
}
# the half-giants: only the face's middle kept out facing the viewer (their hair is wide), the
# face kept out from the side too, a frame's head facing otherwise than the frame (the bow drawn
# facing the viewer; the woman hit, her head thrown back), and the bow's light colours not hair
CENTRED_FACE = frozenset((2072, 2074))
HAIR_FACING = {(2072, True, 11): "front", (2074, True, 11): "front", (2074, True, 12): "side"}
BOW_LIGHT = frozenset((181, 182, 183))
# the halfling man, whose brows and face shadows are his hair's dark browns: no hair from a row
# down in the head's middle facing the viewer (FACE_FROM), short hair (HAIR_ROWS: front, back,
# side; not where his head is bowed); and the darkest shade the face or the clothes have too,
# taken only where the hair surrounds it (INNER: at least INNER_MIN of its 8 neighbours)
FACE_FROM: Dict[Tuple[int, bool, int], int] = {
    (2068, False, 0): 3, (2068, False, 3): 3, (2068, False, 4): 3, (2068, False, 5): 3,
    (2068, False, 6): 3, (2068, True, 0): 5, (2068, True, 1): 3, (2068, True, 9): 3}
HAIR_ROWS: Dict[int, Tuple[int, int, int]] = {2068: (5, 6, 5)}
HAIR_BOWED = frozenset(((2068, True, 2), (2068, True, 12)))
INNER: Dict[int, frozenset] = {2068: frozenset((254,)), 2070: frozenset((128,))}
INNER_MIN = 5
# the elves' hair shaded with the skin's browns (taken where joined to the hair): from behind,
# above the shoulders, the darker ones too; facing the viewer or the side, within the hair's zone
BROWNS: Dict[int, Tuple[frozenset, frozenset]] = {
    m: (frozenset((128, 135, 136, 138, 140)), frozenset((135, 136, 137, 138, 139, 140))) for m in (2059, 2061)}
LONG_BACK = frozenset((2059,))


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


def _clusters(rows: Rows, colours: frozenset, within: Optional[Set[Point]], strict: bool) -> List[List[Point]]:
    """Groups of touching pixels in COLOURS (diagonals too) starting WITHIN; STRICT, kept in it."""
    seen: Set[Point] = set()
    groups = []
    for y, row in enumerate(rows):
        for x, p in enumerate(row):
            if p not in colours or (x, y) in seen or (within is not None and (x, y) not in within):
                continue
            group, stack = [], [(x, y)]
            seen.add((x, y))
            while stack:
                a, b = stack.pop()
                group.append((a, b))
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        n = (a + dx, b + dy)
                        if 0 <= n[1] < len(rows) and 0 <= n[0] < len(rows[n[1]]) and n not in seen \
                                and rows[n[1]][n[0]] in colours and (not strict or within is None or n in within):
                            seen.add(n)
                            stack.append(n)
            groups.append(group)
    return groups


def hair(rows: Rows, model: int, frame: int, combat: bool) -> Set[Point]:
    """The hair to grey in one frame of MODEL (the game's own frames; spriteparts.find's way, with
    the corrections above)."""
    colours = COLOURS.get(model, sp.MODELS[model][2])
    if not colours or (combat and frame == sp.DEAD_FRAME):
        return set()
    facing = (sp.COMBAT_FACING if combat else sp.WALK_FACING)[frame]
    filled = [y for y, r in enumerate(rows) if any(p is not None for p in r)]
    bottom = filled[-1] if filled else 0
    heights = sp.HEAD_ROWS.get(model)
    head, neck = sp._head(rows, heights[(sp.FRONT, sp.BACK, sp.SIDE).index(facing)] if heights and facing else None)
    placed = HEADS.get((model, combat, frame)) or sp.HEADS.get((model, combat, frame))
    if placed:
        top, left, right, neck = placed
        head = sp.Head(top, left, right, top + max(1, (neck - top) * 2 // 5))
    if not head:
        return set()
    waist = neck + round((bottom - neck) * 0.42)
    zone = {(x, y) for y in range(head.top, min(waist, bottom) + 1) for x in range(head.left - 3, head.right + 4)}
    seen_as = HAIR_FACING.get((model, combat, frame), facing)
    if model in CENTRED_FACE:
        if seen_as == sp.FRONT:
            middle, half = (head.left + head.right) // 2, (head.right - head.left) // 4
            zone -= {(x, y) for y in range(head.brow + 1, waist + 1) for x in range(middle - half, middle + half + 1)}
        elif seen_as == sp.SIDE:
            zone -= {(x, y) for y in range(head.brow, waist + 1) for x in range(head.right - 3, head.right + 4)}
    elif facing == sp.FRONT:
        zone -= {(x, y) for y in range(head.brow + 1, waist + 1) for x in range(head.left + 2, head.right - 1)}
    out: Set[Point] = set()
    for group in _clusters(rows, colours, zone, model in STRICT):
        if any(y <= head.brow for _, y in group):
            out.update(group)
    if model in BROWNS and out:
        behind, beside = BROWNS[model]
        down = waist if model in LONG_BACK else neck  # (her long hair over her back)
        extra, within = (behind, {(x, y) for x, y in zone if y < down}) if facing == sp.BACK else (beside, zone)
        for group in _clusters(rows, colours | extra, within, True):
            if any(pt in out for pt in group):
                out.update(group)
    if model in CENTRED_FACE and combat and frame in sp.BOW_FRAMES:
        bow = BOW_LIGHT - colours
        out = {(x, y) for x, y in out if not any(
            0 <= y + dy < len(rows) and 0 <= x + dx < len(rows[y + dy]) and rows[y + dy][x + dx] in bow
            for dx in (-1, 0, 1) for dy in (-1, 0, 1))}
    face = FACE_FROM.get((model, combat, frame))
    if face is not None:
        out = {(x, y) for x, y in out if y < face or not head.left + 2 <= x <= head.right - 2}
    if model in HAIR_ROWS and facing and (model, combat, frame) not in HAIR_BOWED:
        reach = head.top + HAIR_ROWS[model][(sp.FRONT, sp.BACK, sp.SIDE).index(facing)]
        out = {(x, y) for x, y in out if y < reach}
    inner = INNER.get(model)
    if inner and out:
        out |= {(x, y) for y, r in enumerate(rows) for x, p in enumerate(r) if p in inner
                and sum((x + dx, y + dy) in out for dx in (-1, 0, 1) for dy in (-1, 0, 1)) >= INNER_MIN}
    return out


def own_hair(points: Set[Point], rows: Rows, shoulders: Optional[int]) -> Set[Point]:
    """A half-elf's own figure's hair (figures.own's points: those still golden) grown to all the
    golden hair joined to it above the shoulders (her bun, his temple drawn anew)."""
    from . import figures
    limit = min(len(rows), shoulders if shoulders is not None else len(rows))
    out, stack = set(points), list(points)
    while stack:
        x, y = stack.pop()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                n = (x + dx, y + dy)
                if n not in out and 0 <= n[1] < limit and 0 <= n[0] < len(rows[n[1]]) \
                        and rows[n[1]][n[0]] in figures.GOLDEN_HAIR:
                    out.add(n)
                    stack.append(n)
    return out
