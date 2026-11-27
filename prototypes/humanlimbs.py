"""Turn the exposed human limbs at their pose-specific elbows, knees and calves."""
from math import hypot


# Each pose traces two elbows, then two knees in native picture coordinates.
JOINTS = {
    2095: (
        ((2, 10), (18, 10), (6, 18), (14, 18)),
        ((4, 11), (17, 10), (7, 18), (14, 19)),
        ((3, 11), (8, 13), (4, 20), (8, 18)),
        ((1, 10), (17, 10), (6, 18), (11, 17)),
        ((2, 10), (16, 9), (7, 17), (11, 18)),
        ((1, 9), (16, 9), (6, 17), (12, 18)),
        ((2, 10), (16, 10), (6, 18), (12, 16)),
        ((1, 9), (13, 10), (5, 18), (9, 17)),
        ((1, 8), (14, 11), (5, 19), (10, 17)),
        ((1, 10), (13, 8), (6, 17), (10, 18)),
        ((1, 11), (13, 8), (7, 17), (10, 19)),
        ((5, 13), (10, 13), (4, 19), (7, 18)),
        ((6, 12), (13, 8), (4, 19), (11, 19)),
        ((3, 12), (8, 10), (2, 19), (5, 20)),
        ((6, 12), (14, 13), (4, 21), (11, 18)),
        ((4, 20), (14, 10), (5, 27), (12, 26)),
        ((5, 4), (18, 13), (8, 15), (15, 14)),
        ((12, 2), (12, 14), (14, 16), (21, 12)),
        ((2, 15), (10, 11), (4, 21), (11, 22)),
        ((2, 19), (9, 12), (4, 24), (12, 25)),
        ((11, 10), (20, 11), (14, 17), (22, 18)),
        ((7, 12), (22, 17), (15, 25), (20, 24)),
        ((8, 11), (19, 11), (4, 20), (10, 18)),
        ((5, 6), (15, 10), (3, 17), (9, 15)),
        ((6, 11), (10, 14), (6, 19), (10, 17)),
        ((6, 14), (11, 11), (7, 21), (13, 22)),
        ((3, 10), (16, 10), (9, 21), (15, 20)),
        ((1, 12), (15, 2), (4, 15), (14, 13)),
        ((3, 12), (14, 9), (5, 4), (12, 5)),
    ),
    2099: (
        ((1, 11), (15, 11), (4, 19), (12, 18)),
        ((4, 11), (15, 10), (7, 17), (13, 19)),
        ((4, 10), (7, 11), (4, 18), (6, 17)),
        ((1, 11), (14, 10), (4, 19), (10, 18)),
        ((3, 11), (15, 9), (6, 17), (11, 19)),
        ((1, 10), (15, 10), (6, 17), (11, 19)),
        ((2, 10), (14, 11), (5, 18), (11, 16)),
        ((4, 10), (15, 12), (7, 18), (11, 17)),
        ((4, 10), (15, 11), (8, 19), (12, 18)),
        ((5, 11), (16, 10), (8, 18), (13, 18)),
        ((4, 12), (16, 9), (8, 18), (11, 19)),
        ((7, 12), (11, 10), (8, 19), (10, 17)),
        ((6, 13), (14, 11), (7, 19), (13, 18)),
        ((10, 13), (16, 12), (10, 19), (13, 21)),
        ((7, 12), (14, 13), (6, 20), (11, 17)),
        ((6, 20), (15, 9), (7, 27), (12, 25)),
        ((4, 7), (17, 14), (8, 17), (14, 15)),
        ((12, 3), (13, 14), (14, 15), (19, 13)),
        ((4, 14), (11, 11), (4, 20), (9, 22)),
        ((3, 21), (11, 15), (5, 26), (12, 26)),
        ((11, 9), (19, 11), (14, 16), (22, 18)),
        ((7, 12), (21, 17), (15, 25), (19, 23)),
        ((10, 12), (22, 11), (8, 21), (13, 18)),
        ((8, 6), (19, 11), (8, 18), (12, 15)),
        ((6, 11), (9, 11), (4, 19), (9, 17)),
        ((4, 13), (8, 9), (5, 19), (11, 21)),
        ((3, 9), (15, 8), (9, 21), (13, 19)),
        ((1, 12), (12, 6), (6, 17), (14, 17)),
        ((4, 10), (14, 9), (7, 4), (12, 5)),
    ),
}


# Traces of the retail wristband and harness on the man's bare arm,
# and three pixels of warm leather on the woman's thigh plus one at the knee.
# Match the surrounding skin on the shaded edges and on the lit knee.
LEATHER = {
    2095: {3: ((19, 11, 137, 133),), 16: ((20, 12, 135, 134), (19, 18, 138, 144))},
    2099: {13: ((12, 17, 140, 146), (13, 17, 136, 132), (12, 18, 139, 145)),
           22: ((9, 17, 140, 147),)},
}


def joint_plane(edits, body, point, end, form, far, protected, skin):
    """Short lit upper plane, flexion crease and tapered forearm or calf."""
    x0, y0 = point
    dx, dy = end[0] - x0, end[1] - y0
    length = hypot(dx, dy)
    if length < 1:
        return
    dx, dy = dx / length, dy / length
    # Cross-axis points toward the arena light, including in a horizontal arm.
    lx, ly = -dy, dx
    if lx + ly * .75 > 0:
        lx, ly = -lx, -ly
    leg = form == "knee"
    for y in range(max(0, y0 - 7), min(len(body), y0 + 8)):
        for x in range(max(0, x0 - 7), min(len(body[y]), x0 + 8)):
            old = body[y][x]
            if old not in skin[1:] or (x, y) in protected:
                continue
            along = (x - x0) * dx + (y - y0) * dy
            across = (x - x0) * lx + (y - y0) * ly
            if not -2.8 < along < min(length - .8, 5) or abs(across) > 1.65:
                continue
            if along < -1.0:
                # Biceps or quadriceps, turning into the narrower joint.
                value = 8 if across > -.25 else 3
            elif along <= .65:
                value = (10 if leg else 9) if across > -.45 else 4
            elif along <= 1.85:
                value = 5 if across > .55 else 2
            elif along < 3.7:
                value = (8 if leg else 7) if across > -.15 else 3
            else:
                value = 6 if across > -.45 else 2
            if far:
                value -= 1
            prior = skin.index(old)
            # The darkest outlines and high retail accents retain their shape.
            tone = min(11, max(1, round(.74 * (value - 5.4) + .78 * (prior - 5.4) + 5.4)))
            if tone != prior:
                edits[x, y] = old, skin[tone]


def finish(body, model, pose, parts, foreground, sockets, skin):
    shoulder_x, shoulder_y, radius, belt_x, belt_y = sockets
    protected = set(foreground)
    if model == 2095:
        protected.update(parts.hair)
        if parts.head:
            protected.update((x, y) for x in range(parts.head.left, parts.head.right + 1)
                             for y in range(parts.head.top, round(shoulder_y)))
        elif pose == 28:
            protected.update((x, y) for y in range(14, len(body)) for x in range(3, 13))
    height = max(3, belt_y - shoulder_y)
    rear = parts.facing == "back" or pose == 28
    edits = {}
    # The light rolls off the outer upper ribs and returns on the near oblique.
    # In a back view the lit ridge ends earlier, at the shoulder blade.
    for y, row in enumerate(body):
        upright = len(body) - 1 - y if pose == 28 else y
        v = (upright - shoulder_y) / height
        if not .08 < v < .85:
            continue
        cx = shoulder_x + (belt_x - shoulder_x) * v
        for x, old in enumerate(row):
            if old not in skin[1:-1] or (x, y) in protected:
                continue
            u = (x - cx) / radius
            turn = (.41 if rear else .47) - .12 * u
            step = 0
            if -.73 < u < -.18 and turn - .22 < v < turn - .04:
                step = 2
            elif -.68 < u < .20 and turn <= v < turn + .18:
                step = -2
            elif .23 < u < .65 and .54 < v < .82:
                step = -2
            if step:
                tone = min(11, max(1, skin.index(old) + step))
                edits[x, y] = old, skin[tone]
    # Far limbs are smaller and usually have their own raised sole. Use each
    # pose's actual hand and sole to carry the stroke along the limb.
    soles = [((x1 + x2) / 2, y) for y, x1, x2 in parts.feet]
    elbows = JOINTS[model][pose][:2]
    knees = JOINTS[model][pose][2:]
    for form, joints, ends in (("elbow", elbows, list(parts.hands.values())), ("knee", knees, soles)):
        for i, point in enumerate(joints):
            x, y = point
            if form == "knee":
                candidates = [p for p in ends if abs(p[0] - x) <= 4.5 and 1 < p[1] - y <= 12]
            else:
                candidates = [p for p in ends if .5 < hypot(p[0] - x, p[1] - y) <= 8]
            if candidates:
                end = min(candidates, key=lambda p: hypot(p[0] - x, p[1] - y))
            else:
                end = x, y - 4 if pose == 28 else y + 5
            joint_plane(edits, body, point, end, form, i == 1, protected, skin)
    for x, y, old, new in LEATHER[model].get(pose, ()):
        if body[y][x] == old:
            edits[x, y] = old, new
    return {p: shade for p, shade in edits.items() if shade[0] != shade[1]}
