"""Build the registered elf bodies, class outfits and review galleries from a Shattered Lands installation.

python prototypes/elfoutfits.py GAME_DIR OUTPUT_DIR
"""

import argparse
from pathlib import Path
from statistics import median

from PIL import Image, ImageDraw

import dwarfoutfits as dwarf
import outfits
from dsloader import classoutfits, figures, sprites

MODELS = ((figures.ELF_WOMAN, "Female"), (figures.ELF_MAN, "Male"))
STUDIES = ("Original", "Body base", "Gladiator", "Fighter", "Cleric")
FLESH = (129, 134, 132, 130, 145, 147)
GOLD = {44, 45, 64, 65, 179, 180, 181, 182, 183, 200, 201}
SHIRTS = {
    figures.ELF_MAN: {24, 29, 38, 39, 48, 49, 50, 158, 159, 160, 161, 162},
    figures.ELF_WOMAN: {36, 37, 58, 59, 60, 174, 175, 176, 177, 178},
}
# Native x bounds of the skirt near the knees, from side idle through side steps 1–4.
SIDE_HEMS = {
    figures.ELF_WOMAN: {2: (0, 8), 11: (1, 8), 12: (4, 13), 13: (0, 7), 14: (2, 11)},
    figures.ELF_MAN: {2: (-1, 7), 11: (-1, 6), 12: (1, 10), 13: (0, 7), 14: (2, 11)},
}
PAD = 4


# Centre of the lower face (or nape from behind), in native coordinates.
# The head finder follows the raised hand in several strikes. The mouth itself
# is below its brow rectangle and shares colours with both stock shirts.
# The final frame is traced with the fallen figure turned feet-down.
JAWS = {
    figures.ELF_WOMAN: (
        (8, 8),
        (9, 6),
        (7, 4),
        (7, 9),
        (8, 6),
        (8, 6),
        (7, 6),
        (6, 6),
        (4, 6),
        (7, 6),
        (8, 7),
        (8, 4),
        (13, 4),
        (8, 4),
        (10, 4),
        (10, 14),
        (11, 10),
        (16, 8),
        (12, 6),
        (7, 15),
        (16, 6),
        (12, 13),
        (13, 5),
        (13, 5),
        (10, 6),
        (6, 8),
        (8, 8),
        (6, 7),
        (7, 6),
    ),
    figures.ELF_MAN: (
        (8, 6),
        (9, 6),
        (7, 4),
        (7, 6),
        (8, 6),
        (8, 6),
        (7, 6),
        (6, 6),
        (4, 6),
        (7, 6),
        (8, 6),
        (6, 4),
        (10, 4),
        (8, 4),
        (10, 4),
        (10, 15),
        (11, 7),
        (14, 8),
        (6, 8),
        (7, 15),
        (15, 6),
        (16, 12),
        (13, 6),
        (12, 5),
        (10, 6),
        (6, 8),
        (8, 8),
        (8, 6),
        (9, 6),
    ),
}
BACK = {1, 7, 8, 9, 10, 18, 19, 20, 25, 28}
SIDE_FACE = {2, 11, 12, 13, 14, 22, 23}
RAMPS = {
    "Cleric": dwarf.CREAM,
    "Fighter": dwarf.LEATHER,
    "Preserver": dwarf.PLUM,
    "Ranger": dwarf.FOREST,
    "Thief": dwarf.HOOD,
    "Psionicist": dwarf.TEAL,
}


def face_pixels(rows, model, pose):
    """Native eyes, cheeks, mouth and jaw. Coordinates are upright for the fallen pose."""
    cx, cy = JAWS[model][pose]
    points = set()
    for y in range(max(0, cy - 7), min(len(rows), cy + 2)):
        # The jaw tapers inward on its last row. In profile it projects to the right.
        left, right = (-5, 3) if pose in SIDE_FACE else (-4, 4)
        if y == cy:
            left, right = (-3, 0) if pose in SIDE_FACE else (-2, 2)
        if y == cy + 1:
            left, right = (-3, -1) if pose in SIDE_FACE else (-1, 1)
        for x in range(max(0, cx + left), min(len(rows[y]), cx + right + 1)):
            c = rows[y][x]
            if (
                c in outfits.SKINC
                or c in GOLD
                or (
                    pose not in BACK
                    and (c in (77, 158, 159, 188, 254) or y >= cy and c in (174, 175))
                )
            ):
                points.add((x, y))
    return points


# Pin the garment under the long hair. Sampling the few uncovered shirt
# pixels in these poses instead follows the swinging arm.
BACK_SHOULDERS = {1: 9, 7: 6, 8: 4, 9: 7, 10: 8}
# Underfolds traced between the moving garment and the body. Each entry is
# (row, left, right) in the native picture. Leave the gap between feet open.
CAPE_SEAMS = {
    (2059, 11): ((16, 4, 4), (17, 4, 4)),
    (2061, 2): ((19, 1, 1),),
    (2061, 11): ((15, 2, 2), (16, 2, 2), (17, 2, 2), (18, 1, 1)),
    (2061, 12): ((18, 8, 8),),
    (2061, 15): ((18, 10, 10), (19, 10, 10), (20, 9, 9), (21, 9, 9)),
    (2059, 22): ((15, 7, 7), (16, 6, 7), (17, 6, 6), (18, 5, 6), (19, 5, 5)),
    (2059, 26): ((12, 11, 11), (13, 11, 11), (14, 11, 11)),
    (2061, 26): ((13, 11, 11), (14, 11, 11)),
}
# The longer Preserver panel reaches the thigh in these poses. The gap
# beside the lower arm in front walk 3 stays open above this underfold.
PLUM_UNDERFOLDS = {
    (2059, 0): ((22, 3, 3),),
    (2059, 3): ((23, 2, 2),),
    (2059, 4): ((18, 4, 4),),
    (2059, 6): ((19, 2, 2),),
    (2059, 15): ((27, 8, 8),),
    (2061, 3): ((20, 9, 9),),
    (2061, 5): tuple((y, 11, 11) for y in range(13, 19)),
    (2061, 26): ((22, 6, 6), (23, 6, 6)),
}
ROBE_SEAMS = {
    (2059, 0): ((19, 10, 10),),
    (2059, 24): ((16, 9, 9), (17, 8, 9), (18, 8, 8)),
    (2059, 26): ((19, 11, 11), (20, 11, 11)),
}


# The gold and brown inside a continuous lock belong to the same hood panel.
# Below the crown keep the native face opening in the front and side views.
def hood_hair(rows, model, pose, bow, face):
    cx, cy = JAWS[model][pose]
    cloth = set()
    for y, row in enumerate(rows[: cy + 7]):
        locks = [x for x, c in enumerate(row) if c in GOLD and (x, y) not in bow]
        if not locks:
            continue
        for x in range(min(locks), max(locks) + 1):
            if (x, y) in bow:
                continue
            crown = y <= cy - 4
            posterior = pose in BACK or pose in SIDE_FACE and x <= cx - 4
            visible_face = pose not in BACK and (x, y) in face
            if row[x] in GOLD or (
                row[x] in figures.HAIRS and (posterior or crown) and not visible_face
            ):
                cloth.add((x, y))
    return cloth


def render(game, model, pose, role, layers=None):
    combat, frame = divmod(pose, 15)
    fig = game.fig(model)
    source = fig.rows(combat, frame)
    height, width = len(source), len(source[0])
    if role == "Original":
        return [row[:] for row in source]
    fallen = pose == 28
    rows = source[::-1] if fallen else source
    parts = fig.parts(combat, frame)

    def point_up(point):
        x, y = point
        return (x, height - 1 - y if fallen else y)

    hair = {point_up(p) for p in parts.hair}
    bow = game.bow(fig, source, parts) if pose in (24, 25, 26) else set()
    bow = {point_up(p) for p in bow}
    face = face_pixels(rows, model, pose)
    locks = hood_hair(rows, model, pose, bow, face)
    protected = hair | bow | locks | face
    # Fingers extend past the waist in the recoil and the front follow-through.
    # Register them to the green retail wristbands, independently of the tunic.
    wrists = {point_up(p) for p in fig.bands(combat, frame)}
    fingers = {
        (x + dx, y + dy)
        for x, y in wrists
        for dx in range(-3, 4)
        for dy in range(-3, 4)
        if dx * dx + dy * dy <= 10
    }
    members = role.split("/")
    base = next(
        (
            key
            for key in (
                "Cleric",
                "Fighter",
                "Preserver",
                "Ranger",
                "Thief",
                "Psionicist",
                "Gladiator",
            )
            if key in members
        ),
        role,
    )
    hooded = "Thief" in members
    cape = next((key for key in ("Preserver", "Ranger", "Thief") if key in members), None)
    cloak_ramp = RAMPS[base] if cape == "Thief" else RAMPS.get(cape, dwarf.HOOD)
    cx, cy = JAWS[model][pose]
    # Feet on the overturned sprite are at the top of the native bitmap.
    feet = parts.feet
    if fallen and model == figures.ELF_WOMAN:
        feet = [(height - 1, 6, 7), (height - 1, 11, 13)]
    elif fallen:
        feet = [(height - 5, 4, 5), (height - 1, 12, 13)]
    if pose == 4:
        feet = [(19, 4, 6), (24, 9, 11)]
    elif pose == 6:
        feet = [(24, 2, 4), (19, 8, 9)]
    elif model == figures.ELF_WOMAN and pose == 27:
        # The run below the left wrist is her hand. Her lifted toe is at the right.
        feet = [(23, 13, 14), (16, 16, 18)]
    feet = sorted(feet, key=lambda foot: foot[1])
    if fallen:
        # Each death frame is a separate drawing. Read the torso feet-down.
        shoulder, waist = (8, 13) if model == figures.ELF_WOMAN else (7, 14)
    else:
        shoulder, waist = parts.shoulders[0], parts.waist
    if model == figures.ELF_WOMAN and pose == 16:
        shoulder, waist = 11, 16
    shirt = SHIRTS[model]
    # Shade these cells only in the matching garment. A shorter hem ends
    # above the extended thigh in the side thrust.
    cape_seams = CAPE_SEAMS.get((model, pose), ())
    if cape == "Preserver":
        cape_seams += PLUM_UNDERFOLDS.get((model, pose), ())
    if pose == 22 and cape == "Thief":
        cape_seams = ()
    cape_fill = {(x, y) for y, a, b in cape_seams for x in range(a, b + 1)}
    robe_fill = {(x, y) for y, a, b in ROBE_SEAMS.get((model, pose), ()) for x in range(a, b + 1)}

    def axis(y):
        points = [x for r in rows[max(0, y - 1) : y + 2] for x, c in enumerate(r) if c in shirt]
        return median(points) if points else (width - 1) / 2

    upper = axis(shoulder)
    if model == figures.ELF_WOMAN:
        upper = BACK_SHOULDERS.get(pose, upper)
    hip = axis(waist - 2)
    profile = pose in (2, 11, 12, 13, 14, 21, 22, 23, 24, 25)
    rear = pose in (1, 7, 8, 9, 10, 18, 19, 20, 25)
    lit = [sum(v * w for v, w in zip(rgb, (0.299, 0.587, 0.114))) for rgb in game.palette]
    out = [[None] * (width + 2 * PAD) for _ in range(height + 2 * PAD)]
    body = {(x, y) for y, row in enumerate(rows) for x, c in enumerate(row) if c is not None}
    for y, row in enumerate(rows):
        t = max(0, min(1, (y - shoulder) / max(1, waist - shoulder)))
        center = upper + (hip - upper) * t
        radius = (2.8 if profile else 4.3) - 0.7 * t
        depth = y - waist
        for x in range(-PAD, width + PAD):
            c = row[x] if 0 <= x < width else None
            dx = x - center
            u = dx / radius
            paint = c
            # The original chin and hair fall in front of the costume. The stock
            # cuffs are removed, but the hand crossing the chest stays in front.
            point = (x, y)
            foreground = point in protected or c in GOLD
            native = point_up(point)
            cloak_shade = None
            armour = 0
            arm = c is not None and (
                c in (249, 250)
                or (point in fingers and c in outfits.SKINC)
                or (
                    c in outfits.SKINC
                    and shoulder - 1 <= y <= waist + 2
                    and (
                        abs(u) > 0.8
                        or y < waist
                        and any(abs(x - hx) + abs(y - hy) <= 4 for hx, hy in parts.hands.values())
                    )
                )
            )
            if c is not None and not foreground:
                if y >= waist + 1:
                    # Shade the two limbs independently at their actual locations.
                    start = x
                    while (start - 1, y) in body:
                        start -= 1
                    end = x
                    while (end + 1, y) in body:
                        end += 1
                    pos = (x - start + 0.5) / (end - start + 1)
                    tone = 1 if pos > 0.72 else 4 if 0.18 < pos < 0.54 else 2
                    if (x, y + 1) not in body:
                        tone = max(0, tone - 1)
                else:
                    tone = 1 if u > 0.65 else 4 if -0.8 < u < -0.18 else 2
                    # Short light across the ribs, a recessed waist and a
                    # rounded hip; the arm swing retains the original lighting.
                    if 0.17 < t < 0.42 and -0.8 < u < 0.62:
                        tone = 3 if abs(u) < 0.18 else 5
                    elif 0.42 <= t < 0.58 and abs(u) < 0.76:
                        tone = 1 if u > 0.10 else 2
                    elif 0.75 < t < 0.99 and -0.66 < u < 0.18:
                        tone = 3
                if c not in outfits.SKINC or (not arm and y >= shoulder - 1):
                    paint = FLESH[tone]
            if role != "Body base" and not foreground and not arm:
                torso = c is not None and shoulder - 2 <= y <= waist and abs(dx) <= radius + 1
                rank = 0 if u > 0.85 else 1 if u > 0.25 else 3 if -0.9 < u < -0.22 else 2
                if c is not None and lit[c] > 125 and rank == 3:
                    rank = 4
                if base == "Gladiator":
                    if torso and abs(dx - (1.8 - 3.8 * t)) < 1.12:
                        paint = dwarf.LEATHER[0 if depth == -1 else rank]
                    if c is not None and 0 <= depth <= 3 and abs(dx) <= radius + 1:
                        paint = dwarf.LEATHER[rank]
                elif base == "Fighter":
                    if torso or (c is not None and 0 <= depth <= 3 and abs(dx) <= radius + 1):
                        paint = dwarf.LEATHER[rank]
                        if torso and abs(dx - (1.9 - 4 * t)) < 0.8:
                            paint = dwarf.HIDE[2]
                elif base == "Cleric" and shoulder - 1 <= y <= waist + 6:
                    fall = max(0, depth) / 6
                    hem_center = center - (1.7 * fall if profile else 0.5 * fall)
                    breadth = radius + 1.65 * fall
                    if depth > 0 and pose in SIDE_HEMS[model]:
                        left, right = SIDE_HEMS[model][pose]
                        hem_center = center * (1 - fall) + (left + right) / 2 * fall
                        breadth = radius * (1 - fall) + (right - left + 1) / 2 * fall
                    # Fill the narrow wedge behind her crossing wrist at the
                    # top of the skirt in the last profile step.
                    if model == figures.ELF_WOMAN and pose == 14 and depth == 1:
                        breadth += 0.5
                    fold = (x - hem_center) / breadth
                    if (
                        (abs(fold) <= 1 or point in robe_fill)
                        and (y > shoulder or c is not None)
                        and depth <= 6 - int(fold > 0.25)
                    ):
                        crease = 0.22 - 0.55 * fall + 0.12 * (1 - t)
                        shade = (
                            0
                            if fold > 0.87
                            else 1 if abs(fold - crease) < 0.16 or fold > 0.58 else 2
                        )
                        if -0.76 + 0.17 * fall < fold < -0.44 + 0.13 * fall:
                            shade = 4 if y > shoulder + 1 else 3
                        if 0.39 < fold < 0.60 and depth >= 2:
                            shade = 3
                        if depth == 6 or (depth == 5 and fold > 0.35):
                            shade = max(1, shade - 1)
                        paint = dwarf.CREAM[shade]
                        if c is None and (
                            (
                                model == figures.ELF_WOMAN
                                and pose == 21
                                and y >= 27
                                and x in (13, 14)
                            )
                            or (model == figures.ELF_MAN and pose == 23 and y >= 16 and 4 <= x <= 6)
                        ):
                            paint = None
                elif base in ("Preserver", "Ranger", "Thief", "Psionicist"):
                    if torso or (c is not None and 0 <= depth <= 4 and abs(dx) <= radius + 1):
                        tunic = RAMPS[base] if base == "Psionicist" else dwarf.LEATHER
                        paint = tunic[rank]
                if (
                    paint is not None
                    and paint not in outfits.SKINC
                    and shoulder - 2 <= y <= waist + 6
                ):
                    armour = classoutfits.CHEST if depth <= 0 else classoutfits.LEGS
                # A mantle opens over the chest in front and falls behind the
                # crossing wrist in profile. Offset its folds as the cloth flares.
                fall = max(0, depth) / 6
                breadth = radius + 0.8 + min(1, fall) * 1.6
                sweep = (-1.4 if profile else -0.7) * min(1, fall)
                fold = (dx - sweep) / breadth
                hem = (4 if cape == "Thief" else 6) - round(abs(fold + 0.2) * 1.8)
                if cape == "Ranger":
                    # One pinned corner lifts over the hip. The opposite panel
                    # is long enough to follow the striding leg.
                    hem -= round((fold + 1) * 1.55)
                drape = (
                    shoulder - 1 <= y <= waist + hem
                    and abs(fold) <= 1
                    and (c is not None or y > shoulder)
                    and (
                        rear
                        or fold < (-0.06 if profile else -0.49)
                        or not profile
                        and fold > 0.54
                        or y <= shoulder + 1
                    )
                )
                # The folded lining joins the outer panel to the jerkin behind
                # the wrist. It shares the equipped cloak's dye and shine mask.
                drape = drape or (point in cape_fill and c is None)
                if drape:
                    crease = -0.15 - fall * 0.24
                    shade = 2
                    if fold > 0.86:
                        shade = 0
                    elif abs(fold - crease) < 0.19 or fold > 0.46:
                        shade = 1
                    elif -0.86 + 0.15 * fall < fold < -0.54 + 0.12 * fall:
                        shade = 4
                    elif 0.17 < fold < 0.43:
                        shade = 3
                    cloak_shade = shade + 1
                    if cape:
                        paint = cloak_ramp[shade]
                        armour = 0
                        if cape == "Ranger" and torso and abs(dx - (2.1 - 4.8 * t)) < 0.85:
                            paint = dwarf.LEATHER[3 if dx < 2.1 - 4.8 * t else 1]
                # Keep a borrowed class detail visible on the lower torso or
                # hem while the shoulder is turned away or hidden by long hair.
                if "Ranger" in members and cape != "Ranger" and drape and depth == hem:
                    paint = dwarf.FOREST[3 if fold < 0 else 2]
                if "Preserver" in members and base == "Cleric" and depth in (3, 4) and armour:
                    paint = dwarf.PLUM[rank]
                if "Psionicist" in members and base != "Psionicist" and paint is not None:
                    if (
                        -2 <= depth <= 1
                        and abs(dx) <= radius + 0.5
                        and abs(depth + 0.35 * dx) < (1.65 if profile else 1.15)
                    ):
                        paint = dwarf.TEAL[4 if depth + 0.35 * dx < -0.15 else 2]
                if (
                    depth == 0
                    and abs(dx) <= radius
                    and paint is not None
                    and not (cape and drape)
                    and "Psionicist" not in members
                ):
                    paint = 169 if abs(dx) < 0.55 else 205
                # A small bone toggle fastens the Fighter's baldric over
                # the back of the mantle when the shoulder caps turn out of view.
                if rear and cape == "Preserver" and "Fighter" in members and drape:
                    if depth in (0, 1) and -0.85 <= fold <= -0.25:
                        paint = dwarf.BONE[2 if depth == 0 else 0]
                # Follow the actual sleeve pixels on the upper arm; the far
                # shoulder can disappear behind the braid or raised forearm.
                outside = (1 if rear else -1) * dx
                if (
                    ("Gladiator" in members or "Fighter" in members)
                    and c in shirt
                    and shoulder - 2 <= y <= shoulder + 1
                    and abs(u) > 0.55
                    and ("Fighter" in members or outside > 0)
                ):
                    ramp = dwarf.BONE if "Fighter" in members else dwarf.BRONZE
                    paint = ramp[3 if y == shoulder - 1 else 0 if y == shoulder + 1 else 2]
                    armour = classoutfits.ARMS
                if (
                    "Fighter" in members
                    and base == "Cleric"
                    and depth in (1, 2)
                    and abs(dx + 1.5) < 1.2
                    and paint is not None
                ):
                    paint = dwarf.LEATHER[rank]
            # At the nape the hood runs from the rear of the skull to the
            # shoulder seam. The face and the raised bow remain in front.
            nape = (
                profile
                and not rear
                and cy < y <= shoulder
                and c is not None
                and point not in face
                and not arm
                and abs(x - (upper - radius + 1)) <= 1
            )
            hood = hooded and point not in bow and (point in locks or nape)
            if hood:
                distance = (x - cx) / 5
                shade = 1 if distance > 0.48 else 3 if distance < -0.48 else 2
                if y < cy - 3 and -0.8 < distance < -0.1:
                    shade = 4
                if y > cy - 3 and (c in (128, 129, 179, 180) or y == cy + 2):
                    shade = max(1, shade - 1)
                paint = RAMPS[base][shade]
                cloak_shade = shade + 1
                armour = 0
            if layers is not None:
                if foreground and point not in bow:
                    layers["head"][native] = 1
                if cloak_shade is not None:
                    layers["cloak"][native] = cloak_shade
                if point in bow:
                    armour = classoutfits.BOW
                elif arm and not foreground:
                    armour = classoutfits.FOREARM
                    if c in outfits.SKINC and shoulder <= y < shoulder + 3 and abs(u) > 0.8:
                        armour |= classoutfits.ARMS
                elif paint is not None and not foreground and y > waist and paint in outfits.SKINC:
                    for foot_no, (sole, left, right) in enumerate(feet[:2]):
                        if sole - 3 <= y <= sole and left - 1 <= x <= right + 1:
                            armour = (classoutfits.LEFT_FOOT, classoutfits.RIGHT_FOOT)[foot_no]
                            break
                if armour:
                    layers["regions"][native] = armour
            if paint is not None:
                out[y + PAD][x + PAD] = paint
    if fallen:
        out.reverse()
    # Use the same foreground ear pass as the live elf renderer.
    return (
        out
        if layers is not None
        else figures.ears_over(out, source, model, frame, bool(combat), PAD)
    )


def tile(game, model, pose, role, terrain, scale):
    rows = render(game, model, pose, role)
    extra = 0 if role == "Original" else PAD
    return placed_tile(game, rows, terrain, scale, extra, extra, extra)


def placed_tile(game, rows, terrain, scale, left, top, bottom):
    h = len(rows) - top - bottom
    w = len(rows[0]) - 2 * left
    canvas = terrain.copy()
    ox = (canvas.width - w) // 2 - left
    oy = canvas.height - 2 - h - top
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            if c is not None:
                assert 0 <= x + ox < canvas.width and 0 <= y + oy < canvas.height
                canvas.putpixel((x + ox, y + oy), game.palette[c])
    return canvas.resize((canvas.width * scale, canvas.height * scale), Image.Resampling.NEAREST)


def reference_sheet(game, terrain):
    im = Image.new("RGB", (781, 467), dwarf.PAPER)
    pen = ImageDraw.Draw(im)
    pen.text((12, 8), "Elf and human outfits", font=dwarf.board_font(20), fill=dwarf.INK)
    columns = (
        "Original elf",
        "Elf Cleric",
        "Human Cleric",
        "Elf Fighter",
        "Human Fighter",
        "Elf Gladiator",
        "Human Gladiator",
    )
    for i, caption in enumerate(columns):
        pen.text(
            (113 + 101 * i, 46), caption, font=dwarf.board_font(12), fill=dwarf.INK, anchor="ma"
        )
    for j, (model, sex) in enumerate(MODELS):
        human = 2099 if model == figures.ELF_WOMAN else 2095
        for i, pose in enumerate((0, 13)):
            y = 68 + (2 * j + i) * 98
            pen.text((5, y + 18), sex, font=dwarf.board_font(12), fill=dwarf.INK)
            pen.text(
                (5, y + 38),
                "Front" if pose == 0 else "Side 3/4",
                font=dwarf.board_font(11),
                fill=dwarf.INK,
            )
            samples = [tile(game, model, pose, "Original", terrain, 2)]
            for role, alias in (
                ("Cleric", "Priest"),
                ("Fighter", "Warrior"),
                ("Gladiator", "Gladiator"),
            ):
                samples.append(tile(game, model, pose, role, terrain, 2))
                rows = classoutfits.frames(alias, False, human)[pose].canvas(
                    game.fr(human, pose), 10
                )
                samples.append(placed_tile(game, rows, terrain, 2, 10, 10, 0))
            for n, sample in enumerate(samples):
                im.paste(sample, (69 + 101 * n, y))
    return im


def gallery(game, output):
    terrain = (
        Image.open(
            Path(__file__).resolve().parents[1] / "playtest/logs/img/2026-11-18-alt-arena.png"
        )
        .convert("RGB")
        .crop((51, 154, 95, 194))
    )
    frames = []
    for k, name in enumerate(dwarf.NAMES):
        im = Image.new("RGB", (777, 438), dwarf.PAPER)
        pen = ImageDraw.Draw(im)
        pen.text((12, 10), "Elf outfit study", font=dwarf.board_font(21), fill=dwarf.INK)
        pen.text((765, 14), name, font=dwarf.board_font(15), fill=dwarf.INK, anchor="ra")
        for col, role in enumerate(STUDIES):
            cx = 136 + col * 143
            pen.text((cx, 48), role, font=dwarf.board_font(15), fill=dwarf.INK, anchor="ma")
        for j, (_, sex) in enumerate(MODELS):
            pen.text((8, 124 + j * 181), sex, font=dwarf.board_font(14), fill=dwarf.INK)
        im = im.quantize(32).convert("RGB")
        for j, (model, _) in enumerate(MODELS):
            for col, role in enumerate(STUDIES):
                cx = 136 + col * 143
                for scale, offset in ((3, 73), (1, 196)):
                    t = tile(game, model, k, role, terrain, scale)
                    im.paste(t, (cx - t.width // 2, offset + j * 181))
        q = im.quantize(256, dither=Image.Dither.NONE)
        assert q.convert("RGB").tobytes() == im.tobytes()
        frames.append(q)
    output.mkdir(exist_ok=True, parents=True)
    frames[0].save(output / "elf-first-pass.png")
    reference_sheet(game, terrain).save(output / "elf-human-reference.png")
    for row, (_, sex) in enumerate(MODELS):
        # Fixed-size tiles for stepping through the individual source poses.
        sheet = Image.new("RGB", (3 * 465, 10 * 118), dwarf.PAPER)
        for k, frame in enumerate(frames):
            x, y = (k % 3) * 465, (k // 3) * 118
            pen = ImageDraw.Draw(sheet)
            pen.text((x + 4, y), dwarf.NAMES[k], font=dwarf.board_font(12), fill=dwarf.INK)
            for i in range(len(STUDIES)):
                cx = 136 + 143 * i
                top = 196 + 181 * row
                t = frame.crop((cx - 22, top, cx + 22, top + 40)).resize(
                    (88, 80), Image.Resampling.NEAREST
                )
                sheet.paste(t, (x + 3 + 92 * i, y + 18))
                pen.text(
                    (x + 3 + 92 * i, y + 99), STUDIES[i], font=dwarf.board_font(10), fill=dwarf.INK
                )
        sheet.save(output / f"elf-{sex.lower()}-poses.png")
    keys = [0, 3, 4, 5, 6, 0, 1, 7, 8, 9, 10, 1, 2, 11, 12, 13, 14, 2, *range(15, 29)]
    frames[0].save(
        output / "elf-first-pass.gif",
        save_all=True,
        append_images=[frames[k] for k in keys[1:]],
        duration=[1000 if k < 3 or k >= 24 else 300 for k in keys],
        loop=0,
        disposal=1,
        optimize=False,
    )


def export_layers(game, output):
    from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

    with ZipFile(output / "elf_outfit_layers.zip", "w") as archive:
        for model, _ in MODELS:
            for role in classoutfits.ELF_ROLES.values():
                for combat, tag in enumerate(("walk", "combat")):
                    streams = {key: [] for key in ("image", "head", "cloak", "regions")}
                    for f in range(14 if combat else 15):
                        source = game.fr(model + combat, f)
                        layers = {key: {} for key in ("head", "cloak", "regions")}
                        drawing = render(game, model, f + 15 * combat, role, layers)
                        image = drawing[:-PAD]
                        for y, row in enumerate(image):
                            for x, pixel in enumerate(row):
                                stock = (
                                    source[y - PAD][x - PAD]
                                    if y >= PAD and PAD <= x < len(row) - PAD
                                    else None
                                )
                                row[x] = None if pixel == stock else 255 if pixel is None else pixel
                        streams["image"].append(image)
                        for key, points in layers.items():
                            mask = [[None] * len(row) for row in image]
                            for (x, y), value in points.items():
                                mask[y + PAD][x + PAD] = value
                            streams[key].append(mask)
                    for key, frames in streams.items():
                        suffix = "" if key == "image" else "-" + key
                        entry = ZipInfo(f"{model}/{role}/{tag}{suffix}")
                        archive.writestr(entry, sprites.encode_frames(frames), ZIP_DEFLATED)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir")
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--layers", action="store_true")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (export_layers if args.layers else gallery)(outfits.Game(args.game_dir), args.output_dir)
