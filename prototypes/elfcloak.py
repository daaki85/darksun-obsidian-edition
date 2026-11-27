"""Paint the trailing male elf cloak from the matching retail Mage pose."""

# Trailing cloth outside the male elf's silhouette, from row 6 down.
# Narrowing the last runs opens the space beneath the lifted corner.
SWING_EDGES = {
    11: ((0, 0), (-1, -1), (-2, -1), (-3, -1), (-4, 0), (-5, 1), (-5, 1),
         (-6, 1), (-6, 1), (-6, 2), (-5, 2), (-5, 2), (-5, 1), (-4, -3)),
    12: ((4, 4), (2, 4), (0, 3), (-1, 2), (-2, 1), (-3, 1), (-4, 1),
         (-4, 1), (-5, 1), (-5, 1), (-6, -2), (-6, -4)),
    13: ((2, 2), (1, 2), (0, 2), (0, 2), (-1, 1), (-2, 1), (-2, 1),
         (-3, 2), (-3, 2), (-4, 2), (-5, 2), (-6, 2), (-6, -3)),
    14: ((3, 3), (2, 2), (1, 1), (0, 2), (-1, 3), (-1, 4), (-2, 4),
         (-2, 3), (-3, 3), (-3, 3), (-4, 3), (-4, 3), (-4, 3), (-4, 0), (-4, -2)),
}

# Pigments from the outer fold of retail Mage 724. Each maps to a plum
# pigment for the class mantle and a relief rank for the six-color worn dye.
MAGE_FOLD = {
    158: (17, 0), 159: (174, 1), 38: (112, 2), 160: (175, 2),
    71: (58, 3), 39: (239, 4), 161: (232, 5), 40: (233, 5),
    49: (115, 3), 50: (119, 4), 212: (118, 4),
}

# Path of the inner pleat, from the shoulder attachment towards the free
# corner. The third step is still opening; the fourth folds back on itself.
SWING_PLEAT = {
    11: (11, (-3, -3, -4, -4, -4, -5)),
    12: (11, (-1, -2, -2, -3, -4, -5)),
    13: (11, (0, 0, -1, -1, -2, -2, -3, -4)),
    14: (11, (2, 1, 1, 0, 0, -1, -1, -2, -3)),
}

HIP_DIAGONAL = {11: 15, 12: 18, 13: 16, 14: 18}


def lifted_hem(model, pose, x, y, body_left):
    """Pixels that must show the underlying leg, garment, or open ground."""
    if model == 2059:
        return pose == 14 and (x, y) == (7, 16)
    return model == 2061 and pose in HIP_DIAGONAL and y >= 11 and x >= body_left and x + y > HIP_DIAGONAL[pose]


def paint_swing(game, pose, body, paint, folds, regions, family, ramp):
    # The archive retains the original equipment registration. The swinging
    # tip needs two more columns on either side for paint and cloak dye.
    extra = 2
    top = len(paint) - len(body)
    left = (len(paint[0]) - len(body[0])) // 2
    image = [[None] * extra + row[:] + [None] * extra for row in paint]
    dye = [[None] * extra + row[:] + [None] * extra for row in folds]
    edge = [next((x for x, c in enumerate(row) if c is not None), len(row)) for row in body]
    mage = game.fr(724, pose)
    for y, body_left in enumerate(edge):
        for px in range(left + body_left):
            py = y + top
            if folds[py][px] is not None:
                dye[py][px + extra] = None
                if family and not regions[py][px]:
                    image[py][px + extra] = None
    pleat_y, pleat = SWING_PLEAT[pose]
    for y, (start, end) in enumerate(SWING_EDGES[pose], 6):
        outer = next(i for i, c in enumerate(mage[y]) if c in MAGE_FOLD)
        strip = []
        for c in mage[y][outer:]:
            if c not in MAGE_FOLD:
                break
            strip.append(MAGE_FOLD[c])
        width = end - start + 1
        py = y + top
        for x in range(start, min(end + 1, edge[y])):
            px = x + left + extra
            if image[py][px] not in (None, 255):
                continue
            src = x + left
            if x >= edge[y] - 2 and src >= 0 and folds[py][src]:
                image[py][px] = paint[py][src]
                dye[py][px] = folds[py][src]
                continue
            plum, rank = strip[(2 * (x - start) + 1) * len(strip) // (2 * width)]
            along = y - pleat_y
            if 0 <= along < len(pleat):
                crease = pleat[along]
                if x == crease:
                    rank = 1 if along < len(pleat) - 1 else 2
                    plum = 175 if along % 3 == 1 else 174
                elif x == crease - 1 and along not in (0, len(pleat) - 1):
                    rank = 3 if along % 3 == 2 else 4
                    plum = 115 if rank == 3 else 239
            dye[py][px] = rank + 1
            if family:
                image[py][px] = plum if family == "plum" else ramp[round(rank * (len(ramp) - 1) / 5)]
    if pose == 12 and folds[7 + top][6 + left] and not regions[6 + top][5 + left]:
        # A two-panel shoulder passes above the raised wrist in this pose.
        dye[6 + top][5 + left + extra] = folds[7 + top][6 + left]
        if family:
            image[6 + top][5 + left + extra] = paint[7 + top][6 + left]
    return image, dye
