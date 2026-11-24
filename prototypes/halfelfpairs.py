"""Borrow a garment detail on the visible cloth of each half-elf single."""

from bisect import bisect_left
from statistics import median

import outfits
from dsloader import classoutfits as co, figures
from outfitdetail import RAMPS, HALFTONES
from thiefhood import OLD_SLATE

# Order the gallery by the single whose silhouette carries the second detail.
BASE_ORDER = ("Thief", "Cleric", "Druid", "Preserver", "Ranger", "Fighter")
ROSTER = tuple(role for combo, role in co.ELF_ROLES.items() if len(combo) == 2) + (
    "Druid/Fighter", "Druid/Preserver", "Druid/Psionicist", "Druid/Thief",
)
GROUPS = (
    ("robes", ("Cleric",)),
    ("leaf", ("Druid",)),
    ("mantles", ("Preserver", "Ranger", "Fighter")),
    ("hoods", ("Thief",)),
)
DYES = {
    "Cleric": (205, 206, 121, 123, 199, 125, 62),
    "Fighter": (88, 89, 91, 93, 95, 97, 98),
    "Preserver": (174, 175, 58, 74, 59, 239, 232),
    "Psionicist": (69, 70, 211, 71, 72, 73, 215),
    "Ranger": (69, 53, 189, 54, 226, 55, 56),
}

# The colored lining turns with the mantle. Leather shorts and straps below
# the moving hem must keep their own shade, particularly in front views.
LINING = {
    "Thief": OLD_SLATE,
    "Preserver": frozenset(RAMPS["plum"]) | set(HALFTONES["plum"].values()) | {233, 238},
}


def base_class(role):
    members = role.split("/")
    return next(name for name in BASE_ORDER if name in members)


def short_hooded_cape(study, key, pose):
    hood, pad = study.rows(key, pose, "Thief")
    druid, _ = study.rows(key, pose, "Druid")
    out = [row[:] for row in druid]
    cb, frame = divmod(pose, 15)
    fig = study.game.fig(key)
    if pose == 28:
        shoulder, neck = 7, (7 if key == outfits.HALF_ELF_WOMAN else 9)
    else:
        parts = fig.parts(cb, frame)
        shoulder = parts.shoulders[0]
        neck = (parts.head.left + parts.head.right) // 2

    # Lay the shaped tail of the hood over the Druid's registered leaf cape.
    # Using the whole kilt below it keeps the hip wrap attached during recoil.
    height = len(out) - pad
    for y, row in enumerate(out):
        level = height - 1 - (y - pad) if pose == 28 else y - pad
        for x in range(len(row)):
            collar = shoulder + 2 - min(4, abs(x - pad - neck) // 2)
            if level <= collar:
                row[x] = hood[y][x]

    if key == outfits.HALF_ELF_MAN and pose in (1, 7, 8, 9, 10):
        # With his hood up the two leaf panels meet across his back. Continue
        # the Thief's own folds through the join, above the lifted corner.
        fields = co.frames("Thief", cb, fig.model)[frame]
        arm = set(fields.regions[co.FOREARM])
        back = figures.mover_back(fig.maker.cuts[bool(cb), frame])
        slate = RAMPS["slate"]
        leaf = (69, 69, 188, 53, 53, 54, 54, 54, 55, 55, 55, 56, 56, 56, 57, 57)
        for y in range(shoulder + 1, parts.waist + 1):
            row = out[y + pad]
            edges = [x for x, c in enumerate(row) if c in (53, 54, 55, 56, 57, 188)]
            if not edges:
                continue
            for x in range(edges[0] + 1, edges[-1]):
                fold = hood[y + pad][x]
                if row[x] in outfits.SKINC and fold in slate and (back(x-pad, y), y) not in arm:
                    row[x] = leaf[slate.index(fold)]
    return out, pad


def draw_pair(study, key, pose, role):
    if role == "Druid/Thief":
        return short_hooded_cape(study, key, pose)
    base = base_class(role)
    accent, = (name for name in role.split("/") if name != base)
    single, pad = study.rows(key, pose, base)
    body, _ = study.rows(key, pose, "Body base")
    out = [row[:] for row in single]
    cb, frame = divmod(pose, 15)
    fig = study.game.fig(key)
    female = key == outfits.HALF_ELF_WOMAN
    parent = {"Fighter": "Warrior", "Cleric": "Priest", "Preserver": "Mage"}.get(base, base) if female else base
    # The male Druid's short cape is cut from the registered Ranger panel.
    fields = co.frames("Ranger" if base == "Druid" and not female else parent, cb, fig.model)[frame]
    blocked = set(fields.regions[co.FOREARM] + fields.regions[co.BOW]
                  + fields.regions[co.LEFT_FOOT] + fields.regions[co.RIGHT_FOOT])
    back = figures.mover_back(fig.maker.cuts[bool(cb), frame])
    height = len(out) - pad
    if pose == 28:
        shoulder, waist = (7, 12) if female else (7, 14)
    else:
        parts = fig.parts(cb, frame)
        shoulder, waist = parts.shoulders[0], parts.waist

    # Read the fallen figure feet-down. Visible fabric can extend behind the
    # body in profile. Only its painted pixels may take a lining or a belt.
    panels = {}
    for y, row in enumerate(single):
        native_y = y - pad
        level = height - 1 - native_y if pose == 28 else native_y
        if level < shoulder or level > waist + 8:
            continue
        panel = []
        for x, c in enumerate(row):
            if (c is None or c == body[y][x] or c in outfits.SKINC
                    or (back(x - pad, native_y), native_y) in blocked):
                continue
            panel.append(x)
        if panel:
            panels[level] = panel

    # Anchor the sash to the worn waist. A flaring lower hem must not drag
    # the buckle sideways when the near arm crosses the belt.
    belt = waist + (2 if base == "Druid" else 0)
    waist_detail = accent in ("Fighter", "Psionicist")
    if waist_detail:
        # The Gladiator's close-fitting kilt follows the hips even where the
        # clean body's legs part or the outer cloak swings past the calf.
        fitted, _ = study.rows(key, pose, "Gladiator")
        footprint = {}
        for level in range(belt - 6, belt + 6):
            y = pad + (height - 1 - level if pose == 28 else level)
            if not 0 <= y < len(fitted):
                continue
            footprint[level] = {x for x, c in enumerate(fitted[y])
                                if c is not None and (back(x - pad, y - pad), y - pad) not in blocked}
        hips = [x for level in range(belt - 1, belt + 2) for x in footprint.get(level, ())]
        hip = median(hips)

        # His profile wrist crosses the belt. Trace the top of the kilt
        # just below it in the two extended steps, then let the end tuck in.
        if not female and pose == 13 and base != "Druid":
            hip, belt = pad + 8, 16
        elif not female and pose == 12 and base == "Druid":
            hip, belt = pad + 9, 18
    palette = study.game.palette

    def light(c):
        r, g, b = palette[c]
        return 3*r + 6*g + b

    values = sorted(light(single[pad + (height - 1 - level if pose == 28 else level)][x])
                    for level, panel in panels.items() for x in panel)
    for level, panel in panels.items():
        y = pad + (height - 1 - level if pose == 28 else level)
        for x in panel:
            belt_depth = level - belt
            if waist_detail:
                # Allow one pixel for the thickness of the fabric at the hip.
                support = footprint.get(level, ())
                if not any(xx in support for xx in (x - 1, x, x + 1)):
                    continue
                dx = x - hip
            dye = DYES[accent]
            if accent == "Fighter":
                # A dark sword belt crosses the waist and turns down at the hip.
                seam = belt_depth + max(-1, min(1, round(dx / 4)))
                if seam not in (-1, 0, 1) and not (1 <= belt_depth <= 3 and -3 <= dx <= -1):
                    continue
            elif accent == "Psionicist":
                # The broader teal sash slopes to a tucked end on the near side.
                seam = belt_depth + max(-3, min(3, round(dx * 0.45)))
                if abs(seam + 1) > 1 and not (0 <= belt_depth <= 3 and -2 <= dx <= 0):
                    continue
            else:
                # A turned panel follows the swept edge from shoulder to hem.
                # Keep a strip of the original outer fabric along its lit side.
                if base in LINING and single[y][x] not in LINING[base]:
                    continue
                width = panel[-1] - panel[0] + 1
                inset = x - panel[0]
                if base == "Thief":
                    if level < shoulder + 1 or inset > max(2, width * .66):
                        continue
                elif inset > max(2, width * .39) or (inset == 0 and width > 4):
                    continue
            color = single[y][x]
            rank = min(6, bisect_left(values, light(color)) * 7 // len(values))
            if accent == "Fighter" and belt_depth == 0 and -1 <= dx <= 0:
                out[y][x] = 168  # Worn bone toggle at the top of the leather tab.
            else:
                out[y][x] = dye[rank]
    return out, pad
