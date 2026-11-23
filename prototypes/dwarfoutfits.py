"""Render a dwarf outfit study from the player's own Shattered Lands figures.

    python3 prototypes/dwarfoutfits.py GAME_DIR OUTPUT_DIR

Use --proposals for the playable class and multiclass galleries.
The default renders the exploratory eight-outfit lineup for each dwarf figure. Coordinates below are in its
native frame. The fallen pose is drawn feet-down, then turned back for display.
"""

import argparse
from pathlib import Path
from typing import NamedTuple

from PIL import Image, ImageDraw, ImageFont

import outfits
from dsloader import classoutfits as co, sprites


class Pose(NamedTuple):
    crown_x: int
    crown_y: int
    shoulder_x: int
    shoulder_y: int
    hip_x: int
    hip_y: int


# The collar travels with the rib cage. In profile the head leads the hip.
POSES = [
    (10, 0, 10, 5, 10, 12),
    (10, 0, 10, 5, 9, 12),
    (8, 0, 5, 6, 4, 12),
    (9, 0, 9, 5, 9, 12),
    (9, 0, 9, 5, 9, 11),
    (9, 0, 9, 5, 9, 11),
    (10, 0, 10, 5, 10, 11),
    (7, 0, 7, 5, 7, 12),
    (6, 0, 6, 5, 6, 12),
    (7, 0, 7, 5, 7, 12),
    (7, 0, 7, 5, 7, 12),
    (7, 0, 4, 6, 3, 11),
    (12, 0, 9, 5, 7, 12),
    (8, 0, 5, 6, 4, 12),
    (11, 0, 8, 5, 7, 12),
    (7, 2, 7, 7, 5, 14),
    (11, 0, 11, 5, 10, 10),
    (8, 4, 10, 9, 10, 12),
    (6, 0, 6, 5, 6, 12),
    (5, 0, 7, 5, 7, 11),
    (6, 0, 8, 5, 9, 11),
    (8, 0, 8, 5, 9, 11),
    (14, 0, 11, 5, 8, 11),
    (13, 0, 10, 5, 7, 10),
    (8, 0, 7, 5, 6, 12),
    (5, 3, 6, 8, 6, 14),
    (7, 3, 8, 8, 9, 14),
    (3, 4, 6, 8, 8, 11),
    (6, 1, 6, 5, 7, 11),
]
ROLES = ("Warrior", "Thief", "Priest", "Mage", "Druid", "Ranger", "Gladiator", "Psionicist")
LEATHER = (208, 88, 207, 92, 96)
BONE = (205, 206, 199, 155)
HIDE = (88, 92, 95, 168)  # turned edge, shadow, face and worn leather
HOOD = (208, 17, 20, 24, 28)
LIT_HOOD = (*HOOD[:3], 25, HOOD[4])
CREAM = (207, 194, 61, 199, 155)
PLUM = (17, 174, 175, 58, 119)
LEAF = (207, 188, 54, 55, 56)
OCHRE = (204, 95, 168, 169, 170)
FOREST = (17, 69, 53, 54, 56)
BRONZE = (204, 94, 168, 186)
TEAL = (17, 69, 70, 71, 73)
FLESH = (134, 132, 130, 145, 147)
CLOAK_LENGTHS = {"Thief": 4, "Mage": 3, "Druid": 3, "Ranger": 4, "Priest": 5}
RAMPS = (LEATHER, HOOD, CREAM, PLUM, LEAF, FOREST, LEATHER, TEAL)
NAMES = (
    ["Front idle", "Rear idle", "Side idle"]
    + [f"{side} walk {i}/4" for side in ("Front", "Rear", "Side") for i in range(1, 5)]
    + [f"{side} strike {i}/3" for side in ("Front", "Rear", "Side") for i in range(1, 4)]
    + ["Front bow", "Rear bow", "Side bow", "Hit", "Fallen"]
)


class Design(NamedTuple):
    name: str
    base: str
    shoulders: bool = False
    hood: bool = False
    sash: bool = False


SINGLES = (
    Design("Cleric", "Priest"),
    Design("Fighter", "Warrior"),
    Design("Gladiator", "Gladiator"),
    Design("Psionicist", "Psionicist"),
    Design("Thief", "Thief"),
)
PAIRS = (
    Design("Cleric/Fighter", "Priest", shoulders=True),
    Design("Cleric/Psionicist", "Priest", sash=True),
    Design("Fighter/Psionicist", "Warrior", sash=True),
    Design("Fighter/Thief", "Warrior", hood=True),
    Design("Psionicist/Thief", "Thief", sash=True),
)
TRIPLES = (
    Design("Cleric/Fighter/Psionicist", "Priest", shoulders=True, sash=True),
    Design("Fighter/Psionicist/Thief", "Warrior", hood=True, sash=True),
)


# Toe centres in the native picture, with the fallen figure turned upright.
# A raised foot often ends several rows above the planted foot.
TOES = (
    ((6, 20), (14, 17)),
    ((5, 18), (14, 20)),
    ((2, 20), (8, 16)),
    ((5, 20), (11, 18)),
    ((6, 15), (12, 19)),
    ((5, 18), (11, 20)),
    ((6, 19), (13, 15)),
    ((4, 20), (9, 17)),
    ((4, 21), (8, 16)),
    ((4, 18), (10, 20)),
    ((5, 17), (8, 22)),
    ((3, 18), None),
    ((2, 17), (10, 19)),
    ((4, 20), (1, 16)),
    ((1, 19), (10, 17)),
    ((1, 22), (9, 20)),
    ((6, 18), (14, 14)),
    ((5, 19), (14, 15)),
    ((1, 17), (10, 20)),
    ((3, 19), (12, 20)),
    ((4, 19), (13, 20)),
    ((7, 20), (13, 16)),
    ((1, 19), (8, 16)),
    ((2, 18), (9, 14)),
    ((1, 20), (9, 18)),
    ((2, 20), (11, 23)),
    ((8, 24), (15, 20)),
    ((9, 19), (14, 14)),
    ((3, 16), (11, 16)),
)


# Native deltoid crests, listed from screen left to right. A hidden
# shoulder has no cap. The offsets follow the arm swing, including the
# high elbow in the third front strike and the woman's separate wind-up.
SHOULDERS = (
    ((5, 5), (15, 5)),
    ((5, 6), (14, 6)),
    ((4, 5), None),
    ((4, 4), (14, 5)),
    ((4, 5), (15, 3)),
    ((4, 4), (14, 4)),
    ((5, 3), (15, 6)),
    ((2, 6), (11, 6)),
    ((2, 5), (11, 7)),
    ((3, 6), (12, 6)),
    ((3, 5), (12, 6)),
    ((4, 6), None),
    ((8, 5), None),
    ((4, 5), None),
    ((6, 4), None),
    ((3, 8), None),
    ((7, 3), (16, 5)),
    (None, (12, 8)),
    ((3, 4), None),
    ((5, 6), None),
    ((7, 6), None),
    ((5, 5), (12, 6)),
    ((8, 4), None),
    ((8, 4), None),
    ((4, 4), None),
    ((4, 9), (9, 8)),
    ((3, 8), (12, 8)),
    (None, (8, 4)),
    ((2, 6), (10, 6)),
)

# Inclusive cheek and jaw spans relative to the crown. The front chin
# overlaps the torso by two native rows. In profile the nose leads it.
FRONT_HEAD = ((-1, 1), (-2, 2), (-3, 3), (-3, 3), (-3, 2), (-2, 2), (-1, 1))
SIDE_HEAD = ((-1, 1), (-2, 2), (-3, 2), (-2, 3), (-2, 3), (-1, 2))
REAR_HEAD = ((-1, 1), (-2, 2), (-2, 3), (-2, 3), (-2, 2))
FALLEN_HEAD = ((-2, 2), (-3, 2), (-3, 2), (-3, 1), (-2, 0))
HIT_HEAD = ((-1, 1), (-2, 2), (-2, 3), (-2, 2), (-1, 1))


# Front edge of the Cleric's folded robe in the side and oblique views.
# Each landmark runs from the collar (x, y) to the belt (x). The elbow can
# cross this line; the foreground arm and bow are painted afterwards.
ROBE_FRONTS = {
    2: (8, 6, 7),
    11: (6, 6, 6), 12: (10, 6, 9), 13: (7, 6, 7), 14: (10, 6, 9),
    21: (10, 7, 11), 22: (13, 6, 10), 23: (12, 6, 9),
    24: (8, 6, 8), 25: (7, 8, 8), 26: (10, 9, 11),
}


# One run per row from the hood's back fold to the garment on the shoulder.
# Coordinates follow the actual lean in each side view. At the side bow
# the bow hand masks the near edge, leaving the opposite fold visible.
HOOD_SHOULDERS = {
    # First row, then inclusive (left, right) bounds down the fold.
    2:  (3, ((4, 6), (3, 6), (2, 6), (2, 6), (1, 6), (1, 4))),
    11: (3, ((3, 5), (2, 5), (2, 5), (1, 4), (1, 3), (0, 2))),
    12: (3, ((8, 10), (7, 10), (6, 10), (5, 10), (5, 9))),
    13: (3, ((4, 6), (3, 6), (2, 6), (2, 6), (2, 6), (1, 4))),
    14: (3, ((7, 9), (6, 9), (5, 9), (4, 8), (4, 7))),
    21: (3, ((11, 12), (10, 12), (11, 12), (10, 12), (10, 12), (10, 11))),
    22: (3, ((10, 12), (9, 12), (8, 12), (7, 11), (6, 9))),
    23: (3, ((9, 11), (8, 11), (7, 11), (7, 10), (6, 8))),
    24: (3, ((4, 6), (3, 6), (3, 6), (3, 6), (3, 5))),
    25: (6, ((3, 4), (3, 5), (2, 5), (2, 4), (2, 4))),
    26: (6, ((10, 11), (10, 12), (10, 13), (10, 12), (10, 11))),
}


def hood_shade(x, row, head_rows, turned):
    """Value on the crown, outer fold or lining of the open hood."""
    if not 0 <= row < len(head_rows):
        return None
    lo, hi = head_rows[row]
    if row == 0 and -2 <= x <= (0 if turned else 2):
        return 4 if x == -1 else 3 if x < 1 else 2
    if row == 1 and -3 <= x <= (2 if turned else 3):
        return 3 if x <= -1 else 2 if x < 2 else 1
    if row >= 2:
        # The thicker trailing fold descends behind the profile ear. Taper
        # both edges toward the collar and preserve the eyes and cheek.
        outer = lo - (2 if turned and row in (3, 4) else 1)
        if outer <= x <= lo + int(turned and row <= 3):
            return 2 if x == outer else 3 if x <= lo else 1
        if not turned and hi <= x <= hi + 1:
            return 2 if x == hi else 1
    return None


def shoulder_guard(rows, point, side, ramp, crest=2):
    """Fit a domed plate to the lit upper arm and stitch its lower edge."""
    if point is None:
        return {}
    ax, ay = point
    # Run the light over the shoulder, then turn the outer lip down
    # the arm. The inside rivet and dark welt sit against the harness.
    shape = (
        (0, -1, crest),
        (-1, 0, 3),
        (0, 0, 2),
        (1, 0, 1),
        (-1, 1, 1),
        (0, 1, 0),
        (-2, 1, 1),
        (-2, 2, 0),
        (1, 1, 0),
    )
    result = {}
    for u, v, shade in shape:
        x, y = ax + side * u, ay + v
        if 0 <= y < len(rows) and 0 <= x < len(rows[y]) and rows[y][x] is not None:
            result[x, y] = ramp[shade]
    return result


def draw(game, model, k, role, design=None, layers=None):
    """Draw one registered pose. Optional layer maps use native, unpadded coordinates."""
    combat, f = divmod(k, 15)
    figure = game.fig(model)
    rows = figure.rows(combat, f)
    dead = k == 28
    if dead:
        rows = rows[::-1]
    height, width = len(rows), len(rows[0])
    # The female dwarf uses a standing wind-up in her first strike.
    registration = 0 if model == 2053 and k == 15 else k
    pose = Pose(*POSES[registration])
    toes = TOES[registration]
    cx, cy, sx, sy, hx, hy = pose
    profile = k in (2, 11, 12, 13, 14, 21, 22, 23, 24, 25)
    rear = k in (1, 7, 8, 9, 10, 18, 19, 20, 25)
    if dead:
        head_rows = FALLEN_HEAD
    elif k == 27:
        head_rows = HIT_HEAD
    elif rear:
        head_rows = REAR_HEAD
    elif profile and k != 21:
        head_rows = SIDE_HEAD
    else:
        head_rows = FRONT_HEAD
    hooded = role == "Thief" or (design and design.hood)
    # The open hood and side cloak catch one more step of slate on the ridge.
    slate = HOOD if rear else LIT_HOOD
    hood_ramp = slate
    if design and design.hood:
        hood_ramp = LEATHER
    elif hooded and design and design.sash:
        hood_ramp = TEAL
    trimmed_hood = design and design.hood and design.sash
    turned_hood = profile and k != 21
    # Front flaps stop above the two lower jaw rows. The short recoil
    # and fallen heads keep a fourth row of cloth at the temples.
    hood_end = len(head_rows) if turned_hood else max(4, len(head_rows) - 2)
    shoulder_fold = HOOD_SHOULDERS.get(k) if hooded else None
    fighter = role == "Warrior"
    # The jerkin and the robe follow the same rib cage in a side view.
    side_jerkin = fighter and k in (2, 11, 12, 13, 14)
    garment_front = ROBE_FRONTS.get(k) if role == "Priest" or side_jerkin else None
    left, right = SHOULDERS[registration]
    guards = {}
    if fighter or (design and design.shoulders):
        guards.update(shoulder_guard(rows, left, 1, BONE))
        guards.update(shoulder_guard(rows, right, -1, BONE))
    elif role == "Gladiator":
        # The same anatomical arm is on screen left in a rear view.
        # Only its leather strap is visible when the arm turns away.
        point, side = (left, 1) if rear or profile else (right, -1)
        guards.update(shoulder_guard(rows, point, side, BRONZE, crest=3))
    bow = game.bow(figure, rows, figure.parts(combat, f)) if k in (24, 25, 26) else set()
    palette = RAMPS[ROLES.index(role)] if role else FLESH
    cloak_ramp = slate if role == "Thief" else palette
    lower = OCHRE if role == "Druid" else LEATHER if role == "Ranger" else palette
    hue = [sum(c * v for c, v in zip(rgb, (0.30, 0.59, 0.11))) for rgb in game.palette]
    pad = 4
    pixels = Image.new("P", (width + 2 * pad, height + 2 * pad), 255)
    pixels.putpalette([c for rgb in game.palette for c in rgb])
    hands = set(bow)
    if dead:
        wrists = [
            (x, y) for y, row in enumerate(rows) for x, c in enumerate(row) if c in (249, 250)
        ]
    else:
        wrists = figure.bands(combat, f)
    for x, y in wrists:
        for yy in range(max(0, y - 2), min(height, y + 3)):
            for xx in range(max(0, x - 2), min(width, x + 3)):
                if (x - xx) ** 2 + (y - yy) ** 2 <= 5:
                    hands.add((xx, yy))
    if k == 13:
        # In side step three the wrist crosses the abdomen. The top of the
        # usual wrist radius catches the stock harness above the knuckles.
        hands.difference_update(((5, 7), (6, 7), (5, 8), (6, 8), (7, 8), (7, 9)))
    bare_rows = game.fig(2055).rows(combat, f) if model == 2053 else rows
    if dead and model == 2053:
        bare_rows = bare_rows[::-1]
    for y in range(height):
        t = min(1, max(0, (y - sy) / max(1, hy - sy)))
        mid = sx * (1 - t) + hx * t
        radius = (3 if profile else 4.3) - 0.55 * t
        front_edge = None
        if garment_front:
            collar_x, collar_y, belt_x = garment_front
            if collar_y <= y <= hy + 5:
                travel = min(1, (y - collar_y) / (hy - collar_y))
                front_edge = round(collar_x + (belt_x - collar_x) * travel)
        fold_bounds = None
        if shoulder_fold:
            first_y, runs = shoulder_fold
            if first_y <= y < first_y + len(runs):
                fold_bounds = runs[y - first_y]
        for x in range(-pad, width + pad):
            c = rows[y][x] if 0 <= x < width else None
            dx = x - mid
            d = y - hy
            depth = y - sy
            row = y - cy
            on_head = 0 <= row < len(head_rows) and head_rows[row][0] <= x - cx <= head_rows[row][1]
            head = c is not None and on_head
            # Leave the skin and occlusion shadow directly under the jaw open.
            neck = (
                not rear
                and len(head_rows) <= row < len(head_rows) + 2
                and abs(x - cx) <= (2 if row == len(head_rows) else 1)
            )

            hand = c is not None and (x, y) in hands
            body = c is not None and not (head or hand)
            paint = c
            # A broad light plane on the near shoulder and a narrow shadow
            # under it read at the dwarves' native height of about 20 pixels.
            shade = 0 if dx > radius - 0.6 else 1 if dx > 1 else 3 if dx > -2.8 else 2
            if c is not None and hue[c] > 145 and dx < 1:
                shade = min(4, shade + 1)
            if c is not None and c not in outfits.SKINC and not (head or hand):
                paint = FLESH[shade if abs(dx) < radius else 1 + int(hue[c] > 65)]
            # The woman's grey boots and the man's skin have the same stride
            # except in their opening attack. Borrow shading only inside her outline.
            if body and d > 1 and c not in outfits.SKINC:
                ref = rows if model == 2053 and k == 15 else bare_rows
                sample = ref[y][x] if y < len(ref) and x < len(ref[y]) else None
                paint = sample if sample in outfits.SKINC else FLESH[min(4, int(hue[c] // 38))]
            skin = paint
            surface = 0
            fold_rank = None
            cape = False
            torso = body and 0 <= depth and d <= 1 and abs(dx) <= radius + 0.5
            if torso:
                surface = co.CHEST
                paint = palette[shade]
                if role == "Gladiator":
                    if abs(dx - (2 - 4 * t)) > 1.1:
                        paint = skin
                        surface = 0
                    elif d == -1:
                        paint = LEATHER[0]  # shadow where the strap tucks under the belt
                if fighter:
                    # Warm side shadow above the belt, with a lighter baldric
                    # crossing the jerkin from the shoulder to the far hip.
                    paint = HIDE[0] if shade == 0 else palette[shade]
                    if abs(dx - (2.5 - 5 * t)) < 1:
                        paint = HIDE[2 if dx < 2.5 - 5 * t else 0]
                if role == "Priest" and -0.7 < dx + 1.6 - 0.4 * t < 0.7:
                    paint = CREAM[4 if depth % 4 else 1]
                if role == "Mage" and not rear and depth in (2, 3) and abs(dx + 1.1) < 1:
                    paint = PLUM[4 if depth == 2 else 1]
            # Outer cloth rests on the shoulders. Its trailing side swings
            # with the weight transfer and clears the forearm in front views.
            length = CLOAK_LENGTHS.get(role, 4)
            if (role in CLOAK_LENGTHS or layers is not None) and depth >= 0 and d <= length:
                progress = depth / (hy - sy + length + 1)
                sway = (-1, 0, 1, 0)[f % 4] if k not in (0, 1, 2, 28) else 0
                center = mid - (2.6 if profile else 0.4) * progress + sway * progress
                breadth = (3.7 if profile else 4.4) + 1.3 * progress
                u = (x - center) / breadth
                if abs(u) < 1 and d <= length - max(0, round((u + 0.2) * 1.6)):
                    face = rear or (profile and u < -0.28) or c is None or depth <= 2 and torso
                    if face:
                        crease = u + 0.55 * progress - 0.12 * (1 - progress) ** 2
                        fold = (
                            0
                            if u > 0.85
                            else (
                                1
                                if -0.15 < crease < 0.17 or u > 0.64
                                else 3 if -0.76 < crease < -0.35 else 2
                            )
                        )
                        if -0.63 < crease < -0.48 and depth >= 2:
                            fold = 4
                        fold_rank = (0, 1, 2, 4, 5)[fold]
                        if role in CLOAK_LENGTHS:
                            paint = cloak_ramp[fold]
                            cape = True
                            surface = 0
                        if role == "Druid" and d == CLOAK_LENGTHS[role] - max(
                            0, round((u + 0.2) * 1.6)
                        ):
                            paint = OCHRE[min(3, fold)]
            if role == "Priest" and 0 <= d <= min(height - 3 - hy, 6):
                u = dx / (radius + 0.45 * d)
                if abs(u) <= 1 and (d < 6 or abs(u) < 0.8):
                    surface = co.LEGS
                    cape = False
                    paint = CREAM[
                        1 if u > 0.55 else 4 if -0.55 < u < -0.25 else 0 if 0.05 < u < 0.26 else 2
                    ]
            # The raised leg in recoil leaves a one-pixel channel under the short hem.
            trim_hem = k == 27 and (x, y) == (12, 13) and role in ("Gladiator", "Psionicist")
            if fighter and body and 1 <= d <= 3 and abs(dx) <= radius + 0.4:
                # Two hip flaps hang from the belt. The outer corners turn
                # inward on the final row and leave the space between legs open.
                if d < 3 or 0.8 <= abs(dx) < radius - 0.5:
                    paint = HIDE[0 if abs(dx) < 0.8 else 2 if -2.8 < dx < -0.8 else 1]
                    if d == 1 and 1 < dx < 3.2:
                        paint = 205
                    surface = co.LEGS
                    cape = False
            elif role not in ("Priest", "Warrior") and 0 <= d <= (4 if role in ("Thief", "Druid") else 3):
                if not trim_hem and abs(dx) <= radius + 0.22 * d and (body or role != "Thief" and d <= 2):
                    if (
                        not rear
                        or role not in CLOAK_LENGTHS
                        or role == "Druid"
                        and dx > 1.8
                        or d > CLOAK_LENGTHS[role]
                    ):
                        rank = (
                            0
                            if dx > 2.4
                            else 3 if -2.9 < dx < -0.6 else 1 if abs(dx - 0.7) < 1 else 2
                        )
                        paint = lower[rank]
                        surface = co.LEGS
                        cape = False
            if d == 0 and abs(dx) <= radius and not (rear and role in CLOAK_LENGTHS):
                surface = co.LEGS
                paint = 169 if abs(dx) < 0.5 else 205
            if fighter and front_edge is not None and body and d < 0:
                # The near arm can cover most of the abdomen. Let the lit
                # edge of the overlapping leather panels show above the wrist.
                if front_edge - 6 <= x <= front_edge:
                    seam = (hy - y + (front_edge - x) // 2) % 4
                    tone = 0 if x == front_edge or seam == 0 else 3 if seam == 1 else 1
                    paint = HIDE[tone]
                    stitch_start = 1 if 11 <= k <= 14 else 2
                    if seam == 1 and stitch_start <= front_edge - x <= 3:
                        paint = BONE[2]  # pale stitching along the near panel
                    elif k == 13 and (x, y) in ((5, 7), (6, 8)):
                        paint = LEATHER[0]  # panel shadow just behind the crossing wrist
                    surface = co.CHEST
            if role == "Priest" and front_edge is not None and front_edge - 2 <= x <= front_edge:
                # The return fold wraps around the rib cage, then drops
                # from the belt. A thin dark seam defines the leading edge.
                if c is not None or paint is not None or d >= 1:
                    edge = x - front_edge
                    if edge == 0:
                        tone = 1 if d >= 2 else 2
                    elif edge == -1:
                        tone = 4 if d < -1 or d in (2, 3) else 3
                    else:
                        tone = 2 if d >= 3 else 3
                    paint = CREAM[tone]
                    if y == hy:
                        paint = 205
                    cape = False
                    fold_rank = None
                    surface = co.CHEST if d < 0 else co.LEGS
            if (
                role == "Ranger"
                and -1 <= depth < hy - sy
                and abs(dx - (-3.6 + 0.32 * depth)) < 1.25
                and paint is not None
            ):
                paint = 155 if depth == -1 else 168 if depth == 1 else 205 if dx < -1.8 else 207
            if role == "Psionicist" and torso and abs(dx - (2.5 - 5 * t)) < 0.8:
                paint = 72 if depth > 1 else 169
            if design:
                # A short cowl leaves the fighter's shoulder caps and legs visible.
                if design.hood and body and 0 <= depth <= 2 and abs(dx) <= 2.5 - 0.55 * depth:
                    paint = hood_ramp[1 if dx > 1 else 3 if dx < -0.5 else 2]
                # Carry the baldric across the back as well as the front. The
                # short woven end falls over the belt and remains visible in profile.
                # The raised profile jerkin fills the neckline below the jaw;
                # the sash still starts at its original shoulder seam.
                if design.sash and paint is not None and 0 <= depth and d <= 3 and not (side_jerkin and neck):
                    strap_x = (1.8 - 3.9 * t) * (-1 if rear else 1)
                    delta = dx - strap_x
                    if abs(delta) <= (1.05 if d <= 0 else 0.78):
                        paint = 169 if d == 0 else TEAL[4 if delta < -0.12 else 3 if d < 0 else 2]
            if (x, y) in guards:
                paint = guards[x, y]
                surface = co.ARMS
                fold_rank = None
                cape = False
            if role is None:
                paint = skin
            # The exposed neckline ends at the collar in a profile robe.
            open_neck = neck and (front_edge is None or x > front_edge or (x, y) in guards)
            if head or open_neck:
                surface = 0
                fold_rank = None
                paint = c if head else skin
            if hooded:
                if rear:
                    shade = min(3, int(hue[c] // 48)) if head else None
                else:
                    shade = hood_shade(x - cx, row, head_rows, turned_hood) if row < hood_end else None
                    # Let the stock jaw and the clean base beside it show
                    # between the two ends of the hood, even above a cowl.
                    if hood_end <= row < len(head_rows) and abs(x - cx) <= 2 and (x, y) not in guards:
                        paint = c if head else skin
                        fold_rank = None
                        surface = 0
                on_shoulder = (
                    fold_bounds is not None and fold_bounds[0] <= x <= fold_bounds[1]
                    and (x, y) not in guards
                )
                if on_shoulder:
                    # The light ridge continues down the nape, with the
                    # darker turn toward the neck. Hands pass in front.
                    lo, hi = fold_bounds
                    shade = 2 if x == lo else 1 if x == hi else 3
                if shade is not None:
                    paint = hood_ramp[shade]
                    # A single seam picks up the triple-class sash, including
                    # on the back where the front opening is out of view.
                    if trimmed_hood and x == cx - 1 and row <= (3 if rear else 1):
                        paint = TEAL[4 if row == 0 else 3]
                    fold_rank = (0, 1, 2, 4, 5)[shade] if on_shoulder and y >= sy else None
                    surface = 0
            if hand:
                # The stock cuff ends here. Keep the hand outline and the bow.
                paint = (
                    c if (x, y) in bow or c in outfits.SKINC else FLESH[min(4, int(hue[c] // 38))]
                )
            if layers is not None:
                point = (x, height - 1 - y if dead else y)
                if head and not hand:
                    layers["head"][point] = 1
                if hand or head or open_neck:
                    fold_rank = None
                    surface = co.BOW if (x, y) in bow else co.FOREARM if hand else 0
                elif paint == skin and body:
                    for toe, foot in zip(toes, (co.LEFT_FOOT, co.RIGHT_FOOT)):
                        if toe and 0 <= toe[1] - y < 3 and abs(x - toe[0]) <= 3:
                            surface = foot
                            break
                if fold_rank is not None:
                    layers["cloak"][point] = fold_rank + 1
                if surface and not (cape and not hand):
                    layers["regions"][point] = surface
            if paint is not None:
                pixels.putpixel((x + pad, y + pad), paint)
    if dead:
        pixels = pixels.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    pixels.info["transparency"] = 255
    return pixels if layers is not None else pixels.convert("RGBA")


def gallery(game, model, name):
    # Keep all cells at the same integer scale and on the native foot anchor.
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 14)
    except OSError:
        font = ImageFont.load_default()
    frames = []
    for k, label in enumerate(NAMES):
        gallery = Image.new("RGB", (476, 280), "#322e2b")
        pen = ImageDraw.Draw(gallery)
        pen.text((8, 5), name, fill="#f1e6d4", font=font)
        pen.text((468, 5), label, fill="#f1e6d4", font=font, anchor="ra")
        for i, role in enumerate(ROLES):
            actor = draw(game, model, k, role)
            panel = Image.new("RGB", (38, 32), "#b4a694")
            panel.paste(actor, ((38 - actor.width) // 2, 32 - actor.height + 2), actor)
            x = 4 + (i % 4) * 118
            y = 23 + (i // 4) * 127
            gallery.paste(panel.resize((114, 96), Image.Resampling.NEAREST), (x, y))
            pen.text((x + 57, y + 99), role, anchor="ma", fill="#f1e6d4", font=font)
        frames.append(gallery)
    return frames


FIGURES = ((2053, "Female"), (2055, "Male"))
PAPER = "#302d2a"
INK = "#f2e8d8"
SAND = "#b8a996"
MUTED = "#c8b9a6"


def board_font(size):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def figure_tile(game, model, pose, design, scale):
    actor = draw(game, model, pose, design.base, design)
    tile = Image.new("RGB", (38, 32), SAND)
    origin = ((tile.width - actor.width) // 2, tile.height - actor.height + 2)
    tile.paste(actor, origin, actor)
    return tile.resize((38 * scale, 32 * scale), Image.Resampling.NEAREST)


def caption(pen, x, y, design, font):
    # Two lines keep the triple-class names readable even on a narrow screen.
    parts = design.name.split("/")
    if len(parts) == 3:
        pen.text((x, y), "/".join(parts[:2]) + "/", font=font, fill=INK, anchor="mt")
        pen.text((x, y + 17), parts[2], font=font, fill=INK, anchor="mt")
    else:
        pen.text((x, y), design.name, font=font, fill=INK, anchor="mt")


def proposal_board(game, title, designs, pose):
    column = 151
    width = 64 + column * len(designs)
    board = Image.new("RGB", (width, 310), PAPER)
    pen = ImageDraw.Draw(board)
    font, small = board_font(17), board_font(14)
    pen.text((10, 8), title, font=font, fill=INK)
    pen.text((width - 10, 10), NAMES[pose], font=small, fill=MUTED, anchor="ra")
    centers = [64 + column * col + column // 2 for col in range(len(designs))]
    for center, design in zip(centers, designs):
        caption(pen, center, 258, design, small)
    for row, (_, gender) in enumerate(FIGURES):
        pen.text((8, 92 + row * 106), gender, font=small, fill=INK, anchor="lm")
    # Reserve the rest of the GIF palette for the game's original sprite shades.
    board = board.quantize(colors=48).convert("RGB")
    for row, (model, _) in enumerate(FIGURES):
        for center, design in zip(centers, designs):
            tile = figure_tile(game, model, pose, design, 3)
            board.paste(tile, (center - tile.width // 2, 46 + row * 106))
    return board


def proposal_sheet(game):
    groups = (("Single classes", SINGLES), ("Two classes", PAIRS), ("Three classes", TRIPLES))
    cell = 158
    sheet = Image.new("RGB", (5 * cell + 20, 448), PAPER)
    pen = ImageDraw.Draw(sheet)
    pen.text((10, 7), "Dwarf outfits", font=board_font(21), fill=INK)
    pen.text(
        (sheet.width - 10, 12),
        "Female front  /  Male rear",
        font=board_font(15),
        fill=MUTED,
        anchor="ra",
    )
    font = board_font(14)
    for row, (title, designs) in enumerate(groups):
        y = 44 + row * 132
        pen.text((10, y), title, font=font, fill=INK)
        for col, design in enumerate(designs):
            x = 10 + col * cell
            for side, (model, _) in enumerate(FIGURES):
                tile = figure_tile(game, model, side, design, 2)
                sheet.paste(tile, (x + side * tile.width, y + 23))
            caption(pen, x + 76, y + 94, design, font)
    return sheet


def render_proposals(game, output):
    proposal_sheet(game).save(output / "dwarf-proposals.png")
    thieves = tuple(d for d in SINGLES + PAIRS + TRIPLES if d.hood or d.base == "Thief")
    for key, title, designs in (
        ("single", "Dwarf single classes", SINGLES),
        ("double", "Dwarf two-class outfits", PAIRS),
        ("triple", "Dwarf three-class outfits", TRIPLES),
        ("thief-hoods", "Dwarf Thief hoods", thieves),
    ):
        frames = [proposal_board(game, title, designs, k) for k in range(len(NAMES))]
        frames[0].save(
            output / f"dwarf-{key}.gif",
            save_all=True,
            append_images=frames[1:],
            duration=[1050 if k < 3 or k >= 24 else 290 for k in range(len(frames))],
            loop=0,
            disposal=1,
        )


def export_layers(game, output):
    """Pack only edits to the player's bitmap and authored equipment masks."""
    from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

    with ZipFile(output / "dwarf_outfit_layers.zip", "w") as archive:
        for model, _ in FIGURES:
            for design in SINGLES + PAIRS + TRIPLES:
                for combat, tag in ((0, "walk"), (1, "combat")):
                    streams = {key: [] for key in ("image", "regions", "head", "cloak")}
                    for f in range(14 if combat else 15):
                        source = game.fig(model).rows(combat, f)
                        layers = {key: {} for key in ("regions", "cloak", "head")}
                        art = draw(game, model, f + 15 * combat, design.base, design, layers)
                        width, height = len(source[0]), len(source)
                        frames = {
                            key: [[None] * (width + 8) for _ in range(height + 4)]
                            for key in streams
                        }
                        for y in range(height):
                            for x in range(-4, width + 4):
                                c = art.getpixel((x + 4, y + 4))
                                stock = source[y][x] if 0 <= x < width else None
                                if (None if c == 255 else c) != stock:
                                    frames["image"][y + 4][x + 4] = c
                        for key, points in layers.items():
                            for (x, y), value in points.items():
                                frames[key][y + 4][x + 4] = value
                        for key, rows in frames.items():
                            streams[key].append(rows)
                    for key, frames in streams.items():
                        suffix = "" if key == "image" else "-" + key
                        entry = ZipInfo(f"{model}/{design.name}/{tag}{suffix}")
                        archive.writestr(entry, sprites.encode_frames(frames), ZIP_DEFLATED)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir")
    parser.add_argument("output_dir", type=Path)
    parser.add_argument(
        "--proposals",
        action="store_true",
        help="render the playable single and multiclass review boards",
    )
    parser.add_argument(
        "--layers", action="store_true", help="export the registered dwarf loader layers"
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    game = outfits.Game(args.game_dir)
    if args.layers:
        export_layers(game, args.output_dir)
        return
    if args.proposals:
        render_proposals(game, args.output_dir)
        return
    for model, gender in ((2053, "female"), (2055, "male")):
        frames = gallery(game, model, "Dwarf " + gender)
        frames[0].save(
            args.output_dir / f"dwarf-{gender}.gif",
            save_all=True,
            append_images=frames[1:],
            duration=[
                950 if k in (0, 1, 2, 24, 25, 26, 27, 28) else 300 for k in range(len(NAMES))
            ],
            loop=0,
            disposal=1,
        )


if __name__ == "__main__":
    main()
