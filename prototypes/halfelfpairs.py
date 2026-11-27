"""Borrow a garment detail on the visible cloth of each half-elf single."""

from bisect import bisect_left
from itertools import combinations
from statistics import median

import outfits
from dsloader import classoutfits as co, figures
from outfitdetail import RAMPS, HALFTONES
from thiefhood import OLD_SLATE
from multiclasscolor import TEAL_SCALE, HOOD_DYES, hood_class

# Order the gallery by the single whose silhouette carries the second detail.
BASE_ORDER = ("Thief", "Cleric", "Druid", "Preserver", "Ranger", "Fighter")
ROSTER = tuple(role for combo, role in co.ELF_ROLES.items() if len(combo) == 2) + (
    "Druid/Fighter", "Druid/Preserver", "Druid/Psionicist", "Druid/Thief",
)
TRIPLES = tuple(role for combo, role in co.ELF_ROLES.items() if len(combo) == 3) + tuple(
    "Druid/" + "/".join(pair) for pair in combinations(("Fighter", "Preserver", "Psionicist", "Thief"), 2)
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


# The woman's free arm turns the pointed nape out over the near shoulder
# in rear strike 2. The lower rows are outside the usual short collar cut.
STRIKE_NAPE = ((2, 7), (2, 7), (3, 7), (5, 7), (5, 6), (6, 6))


def base_class(role):
    members = role.split("/")
    return next(name for name in BASE_ORDER if name in members)


def collar_position(study, key, pose):
    if pose == 28:
        return 7, (7 if key == outfits.HALF_ELF_WOMAN else 9)
    parts = study.game.fig(key).parts(*divmod(pose, 15))
    return parts.shoulders[0], (parts.head.left + parts.head.right) // 2


def dye_hood(study, key, pose, role, rows, pad):
    hood, _ = study.rows(key, pose, "Thief")
    body, _ = study.rows(key, pose, "Body base")
    dye = HOOD_DYES[hood_class(role)]
    shoulder, neck = collar_position(study, key, pose)
    out = [r[:] for r in rows]
    for y, row in enumerate(out):
        level = len(out) - 1 - y if pose == 28 else y - pad
        if level > shoulder + 2:
            continue
        for x, color in enumerate(row):
            if level <= shoulder + 2 - min(4, abs(x - pad - neck) // 2):
                if color in dye and color == hood[y][x] and color != body[y][x]:
                    row[x] = dye[color]
    return out


def hooded_outfit(study, key, pose, garment):
    hood, pad = study.rows(key, pose, "Thief")
    fitted, _ = study.rows(key, pose, garment)
    out = [row[:] for row in fitted]
    cb, frame = divmod(pose, 15)
    fig = study.game.fig(key)
    shoulder, neck = collar_position(study, key, pose)

    # Fit the tip of the hood over the registered garment at the nape.
    height = len(out) - pad
    for y, row in enumerate(out):
        level = height - 1 - (y - pad) if pose == 28 else y - pad
        for x in range(len(row)):
            collar = shoulder + 2 - min(4, abs(x - pad - neck) // 2)
            if level <= collar:
                row[x] = hood[y][x]

    if "Druid" in garment and key == outfits.HALF_ELF_MAN and pose in (1, 7, 8, 9, 10):
        # With his hood up the two leaf panels meet across his back. Continue
        # the Thief's own folds through the join, above the lifted corner.
        fields = co.frames("Thief", cb, fig.model)[frame]
        arm = set(fields.regions[co.FOREARM])
        back = figures.mover_back(fig.maker.cuts[bool(cb), frame])
        slate = RAMPS["slate"]
        leaf = (69, 69, 188, 53, 53, 54, 54, 54, 55, 55, 55, 56, 56, 56, 57, 57)
        for y in range(shoulder + 1, fig.parts(cb, frame).waist + 1):
            row = out[y + pad]
            edges = [x for x, c in enumerate(row) if c in (53, 54, 55, 56, 57, 188)]
            if not edges:
                continue
            for x in range(edges[0] + 1, edges[-1]):
                fold = hood[y + pad][x]
                if row[x] in outfits.SKINC and fold in slate and (back(x-pad, y), y) not in arm:
                    row[x] = leaf[slate.index(fold)]
    return out, pad


def draw_pair(study, key, pose, role, *, baldric=False, far_lining=False, above_belt=False):
    # Review tools also call this entry point directly with a finished study.
    # Compose on the registered fabrics before applying the exposed skin.
    if hasattr(study, "registered"):
        rows, pad = draw_pair(study.registered, key, pose, role, baldric=baldric,
                              far_lining=far_lining, above_belt=above_belt)
        return study.finish(key, pose, role, rows, pad)
    if role == "Druid/Thief":
        return hooded_outfit(study, key, pose, "Druid")
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
    if base == "Fighter" and accent == "Psionicist":
        cap = set(fields.regions[co.ARMS]) - blocked - set(fields.head)
        for y, row in enumerate(out):
            for x, color in enumerate(row):
                if (color in TEAL_SCALE and color != body[y][x]
                        and (back(x-pad, y-pad), y-pad) in cap):
                    row[x] = TEAL_SCALE[color]
    height = len(out) - pad
    if pose == 28:
        shoulder, waist = (7, 12) if female else (7, 14)
    else:
        parts = fig.parts(cb, frame)
        shoulder, waist = parts.shoulders[0], parts.waist

    # Read the fallen figure feet-down. Visible fabric can extend behind the
    # body in profile. Only its painted pixels may take a lining or a belt.
    chest = set()
    if baldric:
        jerkin = co.frames("Warrior" if female else "Fighter", cb, fig.model)[frame]
        chest = set(jerkin.regions[co.CHEST]) - set(jerkin.head) - set(jerkin.regions[co.FOREARM])
    panels = {}
    for y, row in enumerate(single):
        native_y = y - pad
        level = height - 1 - native_y if pose == 28 else native_y
        if level < shoulder or level > waist + 8:
            continue
        panel = []
        for x, c in enumerate(row):
            point = back(x - pad, native_y), native_y
            # The leather crosses the exposed torso where the Druid cape
            # opens. Follow the Fighter's chest mask under the crossing arm.
            exposed_chest = point in chest and level > shoulder and c in outfits.SKINC
            if c is None or point in blocked or ((c == body[y][x] or c in outfits.SKINC) and not exposed_chest):
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
        for level in range(min(shoulder, belt - 6), belt + 6):
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
    if above_belt:
        # The teal wrap sits above the Thief’s leather sword belt. Both
        # tuck against the same hip as the cloak swings behind the legs.
        belt -= 2
    palette = study.game.palette

    def light(c):
        r, g, b = palette[c]
        return 3*r + 6*g + b

    values = sorted(light(single[pad + (height - 1 - level if pose == 28 else level)][x])
                    for level, panel in panels.items() for x in panel)
    dye = DYES[accent]
    green_pleat = role == "Ranger/Thief" and not female and pose in (2, 11, 12, 13, 14)
    falling_nape = role == "Cleric/Thief" and female and pose == 19
    if not female and base == "Cleric" and accent == "Preserver":
        # The narrower turned edge on his robe needs plum through the mids.
        dye = (174, 174, 175, 175, 58, 74, 59)
    elif female and base == "Cleric" and accent == "Fighter" and not baldric:
        dye = (88, 88, 89, 89, 90, 91, 93)
    for level, panel in panels.items():
        y = pad + (height - 1 - level if pose == 28 else level)
        nape_left, nape_right = STRIKE_NAPE[level-16] if falling_nape and 16 <= level <= 21 else (0, -1)
        for x in panel:
            belt_depth = level - belt
            if waist_detail:
                # Allow one pixel for the thickness of the fabric at the hip.
                support = footprint.get(level, ())
                if not any(xx in support for xx in (x - 1, x, x + 1)):
                    continue
                dx = x - hip
            if baldric:
                # Run the sword strap from the near shoulder to the other hip.
                # The separate teal waist wrap crosses it in front.
                drop = (level - shoulder) / max(1, belt - shoulder)
                edge = -2.5 + 4 * drop
                if not female and pose == 24 and base == "Druid":
                    # He turns under the bow. The visible strap crosses the
                    # narrow shoulder at x=5 before disappearing at the wrist.
                    edge = pad + 5 + drop - hip
                if level > belt + 2 or not edge - 1.3 <= dx <= edge + 1.4:
                    continue
            elif accent == "Fighter":
                # A dark sword belt crosses the waist and turns down at the hip.
                seam = belt_depth + max(-1, min(1, round(dx / 4)))
                if seam not in (-1, 0, 1) and not (1 <= belt_depth <= 3 and -3 <= dx <= -1):
                    continue
            elif accent == "Psionicist":
                # The broader teal sash slopes to a tucked end on the near side.
                seam = belt_depth + max(-3, min(3, round(dx * 0.45)))
                if pose in (1, 7, 8, 9, 10, 18, 19, 20, 25):
                    # A folded sash is two pixels deep at the back. The tucked
                    # end is on the front, out of sight behind the waist.
                    if seam not in (-1, 0) or abs(dx) > 5:
                        continue
                elif abs(seam + 1) > 1 and not (0 <= belt_depth <= 3 and -2 <= dx <= 0):
                    continue
            else:
                # A turned panel follows the swept edge from shoulder to hem.
                # Keep a strip of the original outer fabric along its lit side.
                if base in LINING and single[y][x] not in LINING[base]:
                    continue
                width = panel[-1] - panel[0] + 1
                inset = panel[-1] - x if far_lining else x - panel[0]
                if base == "Thief":
                    if level < shoulder + 1 or inset > max(2, width * .66):
                        continue
                elif inset > max(2, width * (.25 if far_lining else .39)) or (inset == 0 and width > 4):
                    continue
            color = single[y][x]
            rank = min(6, bisect_left(values, light(color)) * 7 // len(values))
            if accent == "Fighter" and belt_depth == 0 and -1 <= dx <= 0:
                if female and base == "Cleric" and not baldric:
                    out[y][x] = 155 if dx < -0.25 else 199
                else:
                    out[y][x] = 168  # Worn bone toggle at the top of the leather tab.
            elif green_pleat or nape_left <= x-pad <= nape_right:
                # Keep the source fold shades continuous with the hood.
                # Re-ranking them by the other garments collapsed the shadow.
                out[y][x] = HOOD_DYES[accent].get(color, dye[rank])
            else:
                out[y][x] = dye[rank]
    return out, pad


def draw_triple(study, key, pose, role):
    if hasattr(study, "registered"):
        return study.rows(key, pose, role)
    members = role.split("/")
    if "Thief" in members and role != "Fighter/Psionicist/Thief":
        return hooded_outfit(study, key, pose, "/".join(name for name in members if name != "Thief"))

    base = base_class(role)
    # Carry the lining first so the waist detail passes in front. Where two
    # linings meet, put the Ranger green along the opposite turned edge.
    accents = [name for name in ("Preserver", "Ranger", "Fighter", "Psionicist")
               if name in members and name != base]
    first, second = ("/".join(name for name in members if name in (base, accent)) for accent in accents)
    if accents == ["Fighter", "Psionicist"] and base != "Thief":
        under, pad = draw_pair(study, key, pose, first, baldric=True)
    else:
        under, pad = study.rows(key, pose, first)
    if accents == ["Preserver", "Ranger"]:
        over, _ = draw_pair(study, key, pose, second, far_lining=True)
    elif base == "Thief":
        over, _ = draw_pair(study, key, pose, second, above_belt=True)
    else:
        over, _ = study.rows(key, pose, second)
    plain, _ = study.rows(key, pose, base)
    out = [row[:] for row in under]
    for row, accent_row, base_row in zip(out, over, plain):
        for x, (accent_pixel, base_pixel) in enumerate(zip(accent_row, base_row)):
            if accent_pixel != base_pixel:
                row[x] = accent_pixel
    return out, pad
