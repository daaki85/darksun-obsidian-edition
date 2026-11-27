"""Register equipment ownership on the approved half-elf class garments, one pose at a time."""
from functools import lru_cache

import halfelfstudy as he
from dsloader import classoutfits as co, figures, halfelfgarments, spritebelts
from outfitdetail import HALFTONES, RAMPS

REAR_WALK = (1, 7, 8, 9, 10)
REAR_CAPE = (*REAR_WALK, 18, 19, 20, 25)
ARMOR = co.CHEST | co.ARMS | co.LEGS
FEET = co.LEFT_FOOT | co.RIGHT_FOOT
LIMBS = FEET | co.FOREARM
GREEN = set(RAMPS["leaf"]) | set(HALFTONES.get("leaf", {}).values()) | {188, 189, 190, 226}
CLOTH = {
    "Druid": GREEN, "Ranger": GREEN, "Thief": set(he.OLD_SLATE) | set(he.SLATE),
    "Preserver": set(RAMPS["plum"]) | set(HALFTONES["plum"].values()) | {233, 238},
}


@lru_cache(maxsize=128)
def donor(study, obj, pose, garment):
    key = he.FIGURES[0 if obj == 307 else 1]
    fig = study.game.fig(key)
    cb, f = divmod(pose, 15)
    parent = ({"Fighter": "Warrior", "Preserver": "Mage", "Cleric": "Priest"}.get(garment, garment)
              if obj == 307 else ("Ranger" if garment == "Druid" else garment))
    data = co.frames(parent, cb, fig.model)[f]
    bits = {}
    for bit, points in data.regions.items():
        for point in points:
            bits[point] = bits.get(point, 0) | bit
    return bits, set(data.head), {(x, y): shade+1 for x, y, shade in data.cloak}, data.armor_trim


@lru_cache(maxsize=128)
def single_masks(study, obj, pose, garment):
    """Transfer donor ownership through the same per-row cuts as the garment art."""
    key = he.FIGURES[0 if obj == 307 else 1]
    fig = study.game.fig(key)
    combat, frame = divmod(pose, 15)
    body, pad = study.rows(key, pose, "Body base")
    outfit, _ = study.rows(key, pose, garment)
    bits, scalp, folds, original_trim = donor(study, obj, pose, garment)
    back = figures.mover_back(fig.maker.cuts[bool(combat), frame])
    parts = fig.parts(combat, frame)
    shoulder, neck = he.pairs.collar_position(study.registered, key, pose)
    waist = (12 if obj == 307 else 14) if pose == 28 else parts.waist
    height = len(outfit) - pad
    regions, head, cloak, trim = {}, set(), {}, set()
    for py, row in enumerate(outfit):
        y = py-pad
        level = height-1-y if pose == 28 else y
        for px, color in enumerate(row):
            if color is None:
                continue
            x = px-pad
            point, original = (x, y), (back(x, y), y)
            ownership = bits.get(original, 0)
            if ownership & co.BOW:
                regions[point] = co.BOW
                continue
            base = body[py][px]
            # 129 is native skin shadow as well as the oiled hide's rim.
            # Only the actual exposed body should retain skin ownership.
            hide_rim = garment == "Gladiator" and color == 129
            bare = color == base or (color in he.outfits.SKINC and not hide_rim)
            # The fitted hood has its own crown over the bun, including flying
            # tips outside the old human or elf hair silhouette.
            collar = shoulder+2 - min(4, abs(x-neck)//2)
            # In profile the pointed collar runs behind the upper arm. The
            # parent cape records exactly where that collar becomes shoulder
            # cloth, including the folds that cover his far arm on step four.
            shoulder_fold = (obj == 306 and pose in (2, 11, 12, 13, 14)
                             and y >= shoulder-1 and original in folds and original not in scalp)
            hood = (garment == "Thief" and not bare and color in CLOTH["Thief"]
                    and level <= collar and not shoulder_fold)
            if (bare and (original in scalp or point in parts.hair)) or hood:
                head.add(point)
                continue
            if bare:
                if ownership & LIMBS:
                    regions[point] = ownership & LIMBS
                continue
            clasp = garment == "Gladiator" and color in ((210, 214) if obj == 307 else (168, 186))
            if original in original_trim or clasp:
                trim.add(point)
            native_fold = folds.get(original)
            if garment in CLOTH and color in CLOTH[garment]:
                # The Druid's leaf panel is shorter than its Ranger donor.
                # Its refitted painted material also continues over old hair.
                if native_fold or garment == "Druid" or not ownership & (ARMOR | LIMBS):
                    red, green, blue = study.game.palette[color]
                    cloak[point] = native_fold or 1 + min(5, round((.30*red+.59*green+.11*blue)/32))
                    continue
            if ownership & co.FOREARM:
                # Separate moving wrist and cloth at the crossed arm.
                if color == he.at(fig.rows(combat, frame), x, y):
                    regions[point] = co.FOREARM
                    continue
            armor = ownership & ARMOR
            if not armor and not ownership & LIMBS:
                # The clipped hair exposes actual garment that was unassigned
                # in the parent art. Keep the new panel with the moving torso.
                armor = co.CHEST if level <= waist else co.LEGS
            if armor:
                regions[point] = armor
    if obj == 307 and garment == "Thief" and pose == 16:
        # Her head turns into the raised shoulder. The lower nape folds
        # onto the near shoulder here; the face and crown are above it.
        for point in ((13, 10), (14, 10), (15, 10), (13, 11), (14, 11), (13, 12), (14, 12)):
            x, y = point
            red, green, blue = study.game.palette[outfit[y+pad][x+pad]]
            cloak[point] = 1 + min(5, round((.30*red+.59*green+.11*blue)/32))
            head.discard(point)
            regions.pop(point, None)
    return regions, head, cloak, trim


@lru_cache(maxsize=64)
def outer_cape(study, obj, pose):
    """The Ranger silhouette, with the folds underneath its diagonal strap restored."""
    key = he.FIGURES[0 if obj == 307 else 1]
    ranger, pad = study.rows(key, pose, "Ranger")
    _, _, folds, _ = single_masks(study, obj, pose, "Ranger")
    fabric = {(x, y): (ranger[y+pad][x+pad], rank) for (x, y), rank in folds.items()}
    repairs = {}
    if pose in REAR_CAPE:
        # The fitted Thief back supplies a continuous woven panel in the same
        # pose. Its hood, hem and outer contour belong to the Thief alone.
        thief, _ = study.rows(key, pose, "Thief")
        _, hood, back, _ = single_masks(study, obj, pose, "Thief")
        parts = study.game.fig(key).parts(*divmod(pose, 15))
        shoulder = parts.shoulders[0]
        panel = set(back)
        if pose in REAR_WALK:
            panel.update(p for p in hood if shoulder <= p[1] <= shoulder + 2)
        # These two stitches are painted cloth in both approved drawings,
        # but both donors classified them as part of the tunic underneath.
        if obj == 307 and pose in (9, 10):
            panel.add((13, 11) if pose == 9 else (10, 12))
        for x, y in panel:
            p = x, y
            if p in fabric or p in parts.hair or not shoulder <= y <= parts.waist:
                continue
            if ranger[y+pad][x+pad] is None:
                continue
            color = thief[y+pad][x+pad]
            if color in CLOTH["Thief"]:
                r, g, b = study.game.palette[color]
                shade = 1 + min(5, round((.30*r+.59*g+.11*b)/32))
                repairs[p] = color, shade
    return fabric, repairs


def layers(study, obj, pose, role):
    """Return the padded archive masks, retaining secondary material and the fitted hood."""
    key = he.FIGURES[0 if obj == 307 else 1]
    base = halfelfgarments.garment(role)
    outfit, pad = study.rows(key, pose, role)
    single, _ = study.rows(key, pose, base)
    body, _ = study.rows(key, pose, "Body base")
    regions, head, cloak, trim = single_masks(study, obj, pose, base)
    regions, head, cloak, trim = dict(regions), set(head), dict(cloak), set(trim)
    if base != role:
        # Preserve the actual secondary materials: an ochre toggle, a teal
        # sash, an edge of plum or a dark baldric. No color-range inference
        # could tell all of these apart from their parent's garment.
        for py, row in enumerate(outfit):
            for px, current in enumerate(row):
                if current == single[py][px]:
                    continue
                p = px-pad, py-pad
                if current is None or current == body[py][px]:
                    regions.pop(p, None)
                    head.discard(p)
                    cloak.pop(p, None)
                    trim.discard(p)
                elif not regions.get(p, 0) & (co.BOW | co.FOREARM):
                    trim.add(p)
        if "Thief" in role and base != "Thief":
            shoulder, neck = he.pairs.collar_position(study.registered, key, pose)
            hood_regions, hood_head, hood_folds, _ = single_masks(study, obj, pose, "Thief")
            height = len(outfit)-pad
            for y in range(-pad, height):
                level = height-1-y if pose == 28 else y
                for x in range(-pad, len(outfit[0])-pad):
                    p = x, y
                    if level > shoulder + 2 - min(4, abs(x-neck)//2):
                        continue
                    regions.pop(p, None)
                    cloak.pop(p, None)
                    head.discard(p)
                    if p in hood_regions:
                        regions[p] = hood_regions[p]
                    if p in hood_head:
                        head.add(p)
                    elif base in halfelfgarments.CLOAKED and p in hood_folds and outfit[y+pad][x+pad] is not None:
                        # The borrowed hood brings the fold at its nape onto
                        # the underlying cape. A raised arm can hide the rest.
                        cloak[p] = hood_folds[p]
                        regions.pop(p, None)
    width, height = len(outfit[0]), len(outfit)
    channels = ("head", "regions", "trim", "cloak", "cape", "belt")
    out = {name: [[None]*width for _ in range(height)] for name in channels}

    def store(channel, p, value):
        x, y = p
        out[channel][y+pad][x+pad] = value

    for p, v in regions.items():
        store("regions", p, v)
    for p in head:
        store("head", p, 1)
    for p, shade in cloak.items():
        store("cloak", p, shade)
    for p in trim:
        store("trim", p, 1)

    foreground = {p for p, v in regions.items() if v & (LIMBS | co.BOW)}
    blocked = head | foreground
    if base not in halfelfgarments.CLOAKED:
        # Use the long cape actually fitted to this half-elf. Foreground
        # wrists, the native drawn bow, the head and feet retain precedence.
        fabric, repairs = outer_cape(study, obj, pose)
        # The parent figure's long locks used to cover the middle of this
        # panel. Only the actual hood can still hang over the repaired folds.
        if "Thief" in role and repairs:
            _, hood, _, _ = single_masks(study, obj, pose, "Thief")
            foreground.update(head & hood)
        visible = {p: fold for p, fold in fabric.items() if p not in blocked}
        visible.update((p, fold) for p, fold in repairs.items() if p not in foreground)
        for p, (source, shade) in visible.items():
            x, y = p
            if outfit[y+pad][x+pad] is None and not any(
                (x+dx, y+dy) in visible or he.at(outfit, x+dx+pad, y+dy+pad) is not None
                for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy
            ):
                continue  # A lone Ranger fold can lose its shoulder behind the foreground arm.
            store("cape", p, source)
            store("cloak", p, shade)
    combat, f = divmod(pose, 15)
    for p in spritebelts.waist(obj, combat, f):
        x, y = p
        color = he.at(outfit, x+pad, y+pad)
        if color not in (None, 254) and p not in blocked and p not in cloak:
            store("belt", p, 1)
    return out
