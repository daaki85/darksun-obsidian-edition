"""Finish the human wrap and kilt folds in native pose coordinates."""
from dsloader import classoutfits as co

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
    # The hide flaps swing around the near thigh. Follow their painted
    # outlines rather than assuming a fixed horizontal waistband.
    facing = -1 if pose == 28 else 1
    texture = {}
    for py, row in enumerate(regions):
        for px, bits in enumerate(row):
            if bits and bits & co.LEGS and paint[py][px] is not None:
                color = paint[py][px]
                if (model == 2095 and (89 <= color <= 98 or color in (204, 207))
                        or model == 2099 and color in (129, 134, 135, 137, 139)):
                    texture[px, py] = color
    if not texture:
        return
    hem = max(y*facing for x, y in texture)

    def visible(x, y):
        color = paint[y][x] if 0 <= y < len(paint) and 0 <= x < len(paint[y]) else None
        if color is None and base is not None and 0 <= y < len(base) and 0 <= x < len(base[y]):
            color = base[y][x]
        if color is None and 0 <= y-top < len(rows) and 0 <= x-left < len(rows[y-top]):
            color = rows[y-top][x-left]
        return color not in (None, 255)

    for (x, y), color in texture.items():
        if y*facing < hem-4:
            continue
        if not visible(x+1, y) or not visible(x, y+facing):
            paint[y][x] = 204 if color in (89, 90, 91, 129, 134, 204, 207) else 205
        elif (x, y+facing) not in texture and (x-1, y) in texture:
            # The underside of the hanging flap turns away from the light.
            if color in (90, 91, 92, 93, 94, 129, 134, 135, 137):
                paint[y][x] = 204 if color in (90, 91, 129, 134) else 205
        elif (x-1, y) not in texture and (x+1, y) in texture and visible(x-1, y):
            if color in (94, 95, 96, 97, 98, 137, 139):
                paint[y][x] = 168 if color in (97, 98, 139) else 139
