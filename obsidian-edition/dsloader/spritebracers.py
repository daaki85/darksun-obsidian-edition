"""The wristbands visible in the retail map drawings, in native frame coordinates."""

from . import classoutfits as co, spriteparts as sp


# The half-giants' cuffs share metal colors with their harness, knees and boots.
# Sample the short middle band across each visible cuff in these 29 drawings.
GIANT_WRISTS = (
    ((2, 17), (28, 17)), ((4, 15),), ((13, 19),),
    ((2, 17), (26, 17)), ((2, 19), (24, 15)), ((2, 17), (24, 16)), ((2, 16), (24, 19)),
    ((3, 17), (18, 17)), ((21, 18),), ((2, 17), (19, 16)), ((2, 20),),
    ((14, 20),), ((19, 12), (9, 16)), ((13, 15), (5, 18)), ((19, 18),),
    ((5, 20), (18, 5)), ((7, 6), (29, 23)), ((7, 2), (10, 21)),
    ((14, 15),), ((5, 18), (13, 9)), ((13, 17),),
    ((4, 9), (28, 18)), ((27, 15),), ((8, 5), (23, 17)),
    ((14, 18),), ((14, 18),), ((3, 14), (28, 14)),
    ((3, 20), (21, 2)), ((21, 14), (3, 17)),
)
# The woman's rear arm overlaps the torso differently, and her raised and
# fallen poses sit on different native scan lines from the man's.
GIANT_WOMAN = {
    0: ((2, 17), (26, 17)), 2: ((12, 20),), 3: ((2, 18), (26, 18)),
    4: ((2, 20), (24, 16)), 5: ((2, 18), (24, 17)), 6: ((2, 17), (24, 20)),
    11: ((14, 21),), 12: ((19, 13), (9, 17)), 13: ((13, 16), (5, 19)),
    14: ((19, 19),), 16: ((7, 10), (29, 27)), 17: ((7, 2), (10, 23)),
    21: ((4, 10), (28, 19)), 24: ((14, 19),), 27: ((3, 21), (21, 3)),
    28: ((23, 15), (4, 17)),
}
GIANT_METAL = frozenset((*range(17, 32), *range(48, 53), *range(208, 216)))

# Some wrists are bare or shaded brown rather than painted with the retail
# green marker. These short runs follow the band above the knuckles.
BARE = {
    (2068, 1): ((2, 8), (3, 9), (16, 7), (17, 7)),
    (2068, 2): ((9, 10), (10, 10), (9, 11)),
    (2068, 7): ((0, 8), (1, 8), (12, 8), (13, 8)),
    (2068, 8): ((13, 8), (13, 9), (14, 9)),
    (2095, 7): ((0, 9), (1, 9), (12, 9), (13, 8)),
    (2095, 9): ((1, 9), (2, 8), (13, 9), (14, 8)),
}
BARE[2093, 7] = BARE[2095, 7]
BARE[2093, 9] = BARE[2095, 9]

# Class outfits reconstruct both arms behind the human woman's original cloak.
# The half-elf's maker later narrows these same source coordinates.
RESTORED_WRISTS = {
    1: ((3, 12), (4, 12), (15, 13), (16, 13)),
    7: ((3, 9), (4, 9), (13, 13), (14, 13)),
    8: ((3, 9), (4, 9), (15, 12), (16, 12)),
    9: ((4, 13), (5, 13), (16, 10), (17, 10)),
    10: ((4, 12), (5, 12), (14, 11), (15, 11)),
}


def visible(rows, model, frame, combat, own, costume, canvas, pad):
    """Visible cuff pixels, clipped to the authored foreground arm and drawn figure."""
    pose = frame + combat * sp.WALK_FRAMES
    source = own.source if own is not None else rows
    if model in (2072, 2074):
        centers = GIANT_WRISTS[pose]
        if model == 2074:
            centers = GIANT_WOMAN.get(pose, centers)
        points = {(x, y) for cx, cy in centers for y in range(cy - 1, cy + 2)
                  for x in range(cx - 1, cx + 2) if 0 <= y < len(source) and 0 <= x < len(source[y])
                  and source[y][x] in GIANT_METAL}
    elif model == 2099 and costume and pose in RESTORED_WRISTS:
        points = RESTORED_WRISTS[pose]
    else:
        bands = sp.MODELS[model][1]
        points = {(x, y) for y, row in enumerate(source) for x, c in enumerate(row) if c in bands}
        points.update(BARE.get((model, pose), ()))
    if own:
        points = {(nx, y) for x, y in points for nx in range(own.at(x, y), own.at(x + 1, y))}

    forearm = set(costume.regions[co.FOREARM]) if costume else set()
    if costume and model == 2099 and pose not in RESTORED_WRISTS:
        # The fitted woman marks her ochre/leather wristbands as arm material.
        forearm.update(costume.regions[co.ARMS])
    blocked = set(costume.regions[co.BOW]) | set(costume.head) if costume else set()
    result = []
    for x, y in sorted(points):
        if not (0 <= y < len(rows) and 0 <= x < len(rows[y])):
            continue
        c = canvas[y + pad][x + pad]
        if c is None or c == 254 or (x, y) in blocked:
            continue
        # A fitted mantle or hood can cross a donor wrist. Skin, the source's
        # unchanged wristband and the foreground arm mask establish visibility.
        if costume and (x, y) not in forearm and c != rows[y][x] and not 128 <= c <= 154:
            continue
        result.append((x, y))
    return result
