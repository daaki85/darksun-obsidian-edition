"""Fit leg armor between each boot opening and the moving knee."""

from . import classoutfits as co, halfelf

# Exposed calf on the stock pictures when no lower garment can take the dye.
# These slivers belong to the retail figure and stay at its native coordinates
# even when the independently painted class bodies are reshaded.
RETAIL_CALVES = {
    (2095, 2): ((7, 13), (8, 14), (8, 15), (9, 15), (9, 16), (8, 17)),
    (2095, 15): ((11, 25), (12, 25), (11, 26), (12, 26)),
    (2095, 16): ((7, 16), (8, 16)),
    (2095, 21): ((20, 21), (21, 22), (21, 23)),
    (2095, 23): ((11, 12), (12, 13)),
    (2095, 27): ((13, 10), (14, 10), (13, 11), (14, 11), (15, 11), (16, 11),
                 (14, 12), (15, 12), (16, 12)),
    (2099, 21): ((13, 26), (14, 26)),
    (2055, 17): ((14, 12), (15, 12)),
    (2070, 2): ((11, 13), (12, 13), (3, 15), (3, 16), (4, 16), (5, 16)),
    (2070, 4): ((10, 16), (11, 16), (12, 16)),
    (2070, 12): ((3, 12), (2, 13), (2, 14), (11, 14), (11, 15)),
    (2070, 14): ((3, 14), (2, 15)),
    (2070, 17): ((7, 16), (7, 17)),
}


def visible(rows, model, frame, combat, own, costume, source, pad):
    """Follow exposed calf skin on the short-hem drawing, under the wearer's hem."""
    layer = (halfelf.MAN if model == 2061 else halfelf.WOMAN) if own else model
    if costume is None:
        points = RETAIL_CALVES.get((layer, frame + 15 * combat), ())
        return [(x, y) for x, y in points if y < len(rows) and x < len(rows[y])
                and rows[y][x] in range(128, 154)]
    reference = co.frames("Fighter" if own else "Gladiator", combat, layer)[frame]
    bare = reference.canvas(rows, pad)
    feet = (co.LEFT_FOOT, co.RIGHT_FOOT)
    blocked = set(costume.head) | set(costume.armor_trim)
    for bit in (co.CHEST, co.ARMS, co.LEGS, co.BOW, co.FOREARM, *feet):
        blocked.update(costume.regions[bit])
    if costume.native_cloak:
        blocked.update((x, y) for x, y, _ in costume.cloak)
    for bit in (*feet, co.BOW, co.FOREARM, co.LEGS):
        blocked.update(reference.regions[bit])
    # The fallen drawings put the feet above the knees. Fit each calf from
    # its own foot so the raised leg can be much higher than the planted one.
    toward_knee = 1 if combat and frame == 13 else -1
    depth = 7 if model in (2072, 2074) else 3 if model in (2068, 2070, 2053, 2055) else 5
    radius = 3 if model in (2072, 2074) else 2
    visible = set()
    for bit in feet:
        foot = reference.regions[bit]
        if not foot:
            continue
        ankle = max(y*toward_knee for x, y in foot)
        previous = {x for x, y in foot if y*toward_knee >= ankle-1}
        for rise in range(1, depth+1):
            y = (ankle + rise)*toward_knee
            if not 0 <= y < len(rows) or not previous:
                break
            center = (min(previous) + max(previous))/2
            columns = {x+dx for x in previous for dx in (-1, 0, 1)}
            previous = {x for x in columns if 0 <= x < len(rows[y]) and abs(x-center) <= radius+1
                        and bare[y+pad][x+pad] in range(128, 154)}
            for x in previous:
                if ((x, y) not in blocked and source[y+pad][x+pad] == bare[y+pad][x+pad]):
                    visible.add((x, y))
    return sorted(visible, key=lambda p: (p[1], p[0]))
