"""Hand registration for the map figures, in the retail drawing's own coordinates."""

from . import classoutfits as co, spritegiantgrips, spriteparts as sp


# Swinging fist, supporting fist: three strikes per direction, then recoil.
# Fingers may cross the head or the opposite arm. The giant's knee and the
# kreen's lower arms carry the same band colours as their upper wrists.
_GIANT = (
    ((19, 2), (4, 22)), ((2, 7), (30, 27)), ((4, 21), (1, 2)),
    ((17, 12), (4, 18)), ((13, 6), (2, 20)), ((10, 18), (2, 13)),
    ((5, 5), (28, 20)), ((31, 15), (9, 14)), ((24, 20), (5, 7)),
    ((6, 22), (27, 3)),
)
_MUL = (
    ((14, 1), (5, 17)), ((2, 3), (20, 18)), ((3, 17), (3, 1)),
    ((11, 8), (2, 10)), ((10, 5), (1, 13)), ((7, 12), (1, 8)),
    ((2, 4), (19, 13)), ((23, 10), (6, 12)), ((18, 12), (2, 4)),
    ((3, 15), (19, 1)),
)
_HALFLING_WOMAN = (
    ((16, 2), (7, 16)), ((2, 8), (16, 16)), ((3, 15), (3, 1)),
    ((14, 7), (5, 11)), ((11, 2), (1, 12)), ((7, 12), (1, 7)),
    ((4, 5), (18, 13)), ((21, 9), (6, 11)), ((17, 13), (3, 7)),
    ((3, 15), (17, 4)),
)
_KREEN = (
    ((2, 4), (5, 14)), ((2, 10), (28, 14)), ((23, 7), (18, 19)),
    ((16, 11), (13, 18)), ((18, 6), (2, 12)), ((8, 18), (1, 12)),
    ((7, 5), (25, 25)), ((38, 13), (23, 14)), ((31, 18), (16, 8)),
    ((6, 18), (23, 8)),
)

_WALK_RIGHT = {
    2053: {13: (8, 11)}, 2055: {13: (8, 11)}, 2059: {12: (10, 13)},
    2068: {2: (13, 12), 13: (8, 10)}, 2070: {13: (8, 11)},
    2099: co.HALF_ELF_WOMAN_REAR_HAND,
}


# Follow the same upper claws through a stride. Their lower wrists carry
# identical bands, which otherwise makes the weapon jump between arms.
_KREEN_WALK = (
    ((1, 9), (27, 12)), ((22, 13), (2, 9)), ((32, 17), (18, 7)),
    ((2, 8), (25, 10)), ((1, 12), (27, 14)), ((1, 11), (27, 13)), ((2, 7), (26, 10)),
    ((21, 12), (2, 9)), ((23, 17), (2, 14)), ((21, 14), (1, 10)), ((22, 12), (2, 9)),
    ((32, 17), (18, 7)), ((26, 21), (17, 8)), ((30, 18), (17, 7)), ((30, 16), (18, 6)),
)


def combat_hands(model, f):
    if not (f < 9 or f == 12):
        return
    if model in co.ELVES:
        return co.ELF_MELEE_HANDS[model][f]
    if model in (2095, 2099):
        grips, wrists = ((co.FIGHT_GRIPS, co.FIGHT_SHIELDS) if model == 2095
                         else (co.WOMAN_FIGHT_GRIPS, co.WOMAN_FIGHT_SHIELDS))
        return grips[f], wrists[f]
    if model in (*co.DWARVES, 2068):
        if model == 2053 and f == 0:
            return (1, 11), (18, 11)
        return co.DWARF_FIGHT_GRIPS[f], co.DWARF_FIGHT_SHIELDS[f]
    sets = {2072: _GIANT, 2074: _GIANT, 2093: _MUL, 2070: _HALFLING_WOMAN, sp.KREEN: _KREEN}
    if model in sets:
        return sets[model][9 if f == 12 else f]


def _on_hand(rows, point, model):
    """Bring the wristband finder's offset back onto the skin or claw drawing."""
    x, y = point
    cells = [(xx, yy) for yy in range(max(0, y-2), min(len(rows), y+3))
             for xx in range(max(0, x-2), min(len(rows[yy]), x+3))
             if rows[yy][xx] is not None]
    def priority(p):
        xx, yy = p
        c = rows[yy][xx]
        skin = 130 <= c <= 154 or model == sp.KREEN and (179 <= c <= 183 or c == 201)
        return (not skin, (xx-x)**2 + (yy-y)**2, abs(xx-x), yy, xx)
    return min(cells, key=priority) if cells else point


def positioned(rows, model, f, combat, own, found):
    source = own.source if own else rows
    if combat:
        pair = combat_hands(model, f)
        if pair is None:
            return found
        native = dict(zip(("right", "left"), pair))
    else:
        native = dict(own.source_parts.hands if own else found)
        right = _WALK_RIGHT.get(model, {}).get(f)
        if right:
            native["right"] = right
        if model == 2099 and f in co.HALF_ELF_WOMAN_REAR_HAND:
            native["left"] = co.WOMAN_WALK_SHIELDS[f]
        if model in spritegiantgrips.WALK:
            return dict(zip(("right", "left"), spritegiantgrips.WALK[model][f]))
        if model == sp.KREEN:
            native = dict(zip(("right", "left"), _KREEN_WALK[f]))
    adjusted = {}
    for hand, point in native.items():
        x, y = _on_hand(source, point, model)
        adjusted[hand] = (own.at(x, y) if own else x, y)
    return adjusted


def supporting_wrist(source, palm, model):
    """The visible cuff closest to the supporting fist, even when the wrist is raised."""
    x, y = palm
    colors = sp.MODELS[model][1]
    cells = [(xx, yy) for yy in range(max(0, y-5), min(len(source), y+6))
             for xx in range(max(0, x-5), min(len(source[yy]), x+6))
             if source[yy][xx] in colors and (xx-x)**2 + (yy-y)**2 <= 25]
    if not cells:
        return palm
    xx, yy = min(cells, key=lambda p: ((p[0]-x)**2 + (p[1]-y)**2, abs(p[0]-x), p))
    return xx, yy
