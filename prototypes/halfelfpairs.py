"""Borrow a garment detail on the visible cloth of each half-elf single."""

from bisect import bisect_left
from statistics import median

import outfits
from dsloader import classoutfits as co, figures

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
    "Druid": (69, 188, 53, 54, 55, 56, 57),
    "Fighter": (88, 89, 91, 93, 95, 97, 98),
    "Preserver": (174, 175, 58, 74, 59, 239, 232),
    "Psionicist": (69, 70, 211, 71, 72, 73, 215),
    "Ranger": (69, 53, 189, 54, 226, 55, 56),
}
REEDS = (205, 94, 95, 97, 168, 169, 170)


def base_class(role):
    members = role.split("/")
    return next(name for name in BASE_ORDER if name in members)


def draw_pair(study, key, pose, role):
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
    hips = [x for level, panel in panels.items() if abs(level - belt) <= 1 for x in panel]
    hip = median(hips or [x for panel in panels.values() for x in panel])
    palette = study.game.palette

    def light(c):
        r, g, b = palette[c]
        return 3*r + 6*g + b

    values = sorted(light(single[pad + (height - 1 - level if pose == 28 else level)][x])
                    for level, panel in panels.items() for x in panel)
    for level, panel in panels.items():
        y = pad + (height - 1 - level if pose == 28 else level)
        depth = level - waist
        for x in panel:
            belt_depth = level - belt
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
                width = panel[-1] - panel[0] + 1
                inset = x - panel[0]
                if base == "Thief":
                    if level < shoulder + 1 or inset > max(2, width * .66):
                        continue
                    if accent == "Druid" and depth >= 0:
                        dye = REEDS
                elif inset > max(2, width * .39) or (inset == 0 and width > 4):
                    continue
            color = single[y][x]
            rank = min(6, bisect_left(values, light(color)) * 7 // len(values))
            if accent == "Fighter" and belt_depth == 0 and -1 <= dx <= 0:
                out[y][x] = 168  # Worn bone toggle at the top of the leather tab.
            else:
                out[y][x] = dye[rank]
    return out, pad
