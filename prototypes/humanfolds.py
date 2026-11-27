"""Finish the human wrap and kilt folds in native pose coordinates."""
from dsloader import classoutfits as co

# One clasp where the diagonal strap meets the moving hip.
CLASPS = {
    2095: ((6, 14), (13, 14), (4, 15), (6, 13), (7, 13), (7, 13), (7, 13),
           (8, 14), (9, 15), (10, 14), (10, 15), (5, 15), (7, 15), (4, 14), (7, 15),
           (6, 23), (10, 12), (17, 13), (7, 18), (8, 21), (19, 14), (14, 21),
           (7, 15), (6, 12), (6, 15), (10, 18), (7, 17), (8, 12), (7, 7)),
    2099: ((6, 14), (12, 14), (5, 14), (5, 14), (7, 13), (7, 13), (6, 13),
           (11, 14), (12, 14), (13, 14), (12, 14), (8, 13), (11, 14), (13, 15), (9, 14),
           (7, 23), (9, 14), (16, 13), (8, 17), (11, 22), (19, 13), (15, 21),
           (13, 15), (13, 13), (5, 14), (9, 16), (7, 16), (7, 15), (10, 6)),
}

# Fixed game pigments. Several ochres become skin pink on the regional palettes.
OILED = {88: 208, 89: 129, 90: 129, 91: 204, 92: 204, 93: 207, 94: 195,
         95: 203, 96: 205, 97: 205, 98: 194, 99: 194, 129: 208, 134: 204,
         135: 207, 137: 195, 139: 205, 168: 205, 169: 194, 185: 195, 203: 204,
         204: 129, 205: 207, 207: 204}


# The near end of the gathered fold below the arm, or beside the spine
# in a rear view. The woman's long hair hides the top of the rear folds.
WRAP = {
    2095: (
        (4, 6), (13, 8), (1, 8),
        (4, 6), (5, 6), (4, 6), (5, 6),
        (8, 8), (9, 8), (9, 8), (9, 8),
        (3, 8), (6, 8), (3, 7), (5, 8),
        (4, 16), (9, 8), None, (7, 11), None, None,
        (10, 13), (7, 8), (4, 6), (5, 7), None, (5, 10),
        None, (8, 12),
    ),
    2099: (
        (5, 9), (9, 13), (2, 8),
        (4, 9), (7, 9), (5, 9), (5, 9),
        (9, 13), (10, 13), (10, 13), (9, 13),
        (7, 9), (9, 9), (11, 8), (8, 11),
        (7, 18), (9, 12), (15, 10), (4, 15), (7, 19), (16, 12),
        (12, 17), (11, 10), None, None, (6, 14), (6, 12),
        None, (7, 10),
    ),
}


def finish(rows, paint, regions, base, model, role, pose):
    if role not in ("Psionicist", "Gladiator"):
        return
    top = len(paint) - len(rows)
    left = (len(paint[0]) - len(rows[0])) // 2
    if role == "Psionicist":
        start = WRAP[model][pose]
        if start is None:
            return
        x, y = start
        rise = -1 if pose == 28 else 1
        # The lit lip sits directly above a short, stepped cast shadow. Leave
        # the existing belt, deep shadow, original highlights and arm intact.
        for dx, dy, light in ((0, 0, 1), (1, 0, 1), (0, 1, -1), (1, 1, -1),
                              (2, 1, 1), (2, 2, -1), (3, 2, 1), (3, 3, -1),
                              (4, 3, -1)):
            px, py = x+dx+left, y+dy*rise+top
            color = paint[py][px]
            if color in (70, 71):
                paint[py][px] = color+light
        if model == 2095 and pose == 10:
            # The bent arm shades the far rib on the last rear step.
            for dx, dy, tone in ((0, 0, 71), (1, 1, 71), (2, 1, 69), (1, 2, 69)):
                px, py = left+10+dx, top+7+dy
                if paint[py][px] == 70:
                    paint[py][px] = tone
            # Reflected light tapers off where the fold tucks behind the belt.
            for px, py in ((9, 11), (9, 12)):
                if paint[top+py][left+px] == 69:
                    paint[top+py][left+px] = 70
        return
    leather = {}
    for y, row in enumerate(regions):
        for x, bits in enumerate(row):
            if not bits or not bits & (co.CHEST | co.ARMS | co.LEGS):
                continue
            ink = paint[y][x]
            # The male layers also own the skin beneath the harness.
            if ink in OILED and (model == 2099 or ink not in (129, 134)):
                leather[x, y] = ink
    rise = -1 if pose == 28 else 1

    def touching_skin(x, y):
        if not 0 <= x < len(paint[0]) or not 0 <= y < len(paint):
            return False
        if (x, y) in leather:
            return False
        value = paint[y][x]
        if value is None and base is not None:
            value = base[y][x]
        if value is None and 0 <= y-top < len(rows) and 0 <= x-left < len(rows[y-top]):
            value = rows[y-top][x-left]
        return value in range(128, 154)

    cx, cy = CLASPS[model][pose]
    cx, cy = cx+left, cy+top
    for (x, y), ink in leather.items():
        tone = OILED[ink]
        # One receding edge, with a warm fold still visible on the stepped
        # narrow strap. Deepen the underside where the panel crosses the thigh.
        if touching_skin(x, y+rise):
            tone = 208 if (x, y-rise) in leather else 129
        elif touching_skin(x+1, y) and (x-1, y) in leather:
            tone = 129 if tone in (208, 129, 204, 207) else 204
        # The upper-left lip of the strap remains lit above the contact shadow.
        if regions[y][x] & co.CHEST and touching_skin(x-1, y) and (x+1, y) in leather:
            tone = 207 if ink in (88, 89, 129, 134, 204) else 205
        if model == 2099:
            # On her kilt the lip rolls into a narrow oiled hide flap.
            depth = (y-cy)*rise
            if (regions[y][x] & co.LEGS and 1 <= depth <= 3 and abs(x-cx-(1-depth*.3)) <= .6
                    and (x, y+rise) in leather and ink not in (88, 129, 204)):
                tone = 205
        paint[y][x] = tone
    if (cx, cy) in leather:
        x, y = cx, cy
        # A single dull steel focal point. Its cheek is on the same fastening.
        paint[y][x] = 214
        if (x+1, y) in leather:
            paint[y][x+1] = 210
