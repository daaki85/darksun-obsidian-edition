"""Export the approved halfling outfits with their fitted equipment surfaces.

python prototypes/halflingequipment.py GAME_DIR OUTPUT_ZIP
"""
import argparse
from pathlib import Path

import halflingmultis as art
import halflingstudy as fit
from dsloader import classoutfits as co, spritebracers
from outfitdetail import RAMPS, reference_folds
from studyarmordetail import landmarks, study_surface
from wornreview import Atlas

# A lifted foot can end above the automatically detected floor run; in the
# third front strike the other little run is part of the supporting shin.
# Native male soles, with the woman's per-pose registration applied below.
SOLE_CORRECTIONS = {
    8: ((21, 4, 5), (16, 7, 9)),
    10: ((17, 4, 6), (22, 8, 9)),
    13: ((16, 1, 2), (20, 2, 6)),
    17: ((19, 4, 5), (15, 14, 15)),
    27: ((19, 9, 9), (14, 13, 16)),
}


def appendage_masks(game, model, pose, source, body, outfit):
    cb, frame = divmod(pose, 15)
    figure = game.fig(model)
    parts = figure.parts(cb, frame)
    dx, dy = fit.CUT[pose][-1] if model == 2070 else (0, 0)
    w, h = len(source[0]), len(source)

    def native(point):
        x, y = point[0]+dx, point[1]+dy
        return (w-1-x, h-1-y) if pose == 28 else (x, y)

    # Register the actual drawn face. A hood can extend up to the face opening.
    head = {native(p) for p in fit.head_pixels(pose)} | set(parts.hair)
    bow = {native((x, y)) for y, lo, hi in fit.BOW_ARCS.get(pose, ()) for x in range(lo, hi+1)}
    if model == 2070 and pose == 24:
        bow.add((6, 16))
    bow = {(x, y) for x, y in bow if 0 <= y < h and 0 <= x < w and source[y][x] is not None}
    head = {(x, y) for x, y in head - bow if 0 <= y < h and 0 <= x < w and outfit[y][x+4] is not None}
    # The original colored cuffs also identify wrists when the hand itself
    # is obscured. Let genuinely crossing cloth occlude a cuff or knuckle.
    wrist = figure.bands(cb, frame) | set(spritebracers.BARE.get((model, pose), ()))
    grips = set(parts.hands.values())
    arm = {(x+i, y+j) for x, y in wrist | grips for i, j in
           ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1))}
    skin = {(x, y) for y in range(h) for x in range(w) if outfit[y][x+4] is not None
            and outfit[y][x+4] == body[y][x+4]}
    arm &= skin - head - bow
    feet = [set(), set()]
    if pose == 28:
        soles = [(0, 3, 5), (0, 9, 12)]
    elif pose in SOLE_CORRECTIONS:
        soles = [(sole+dy, a+dx, b+dx) for sole, a, b in SOLE_CORRECTIONS[pose]]
    else:
        soles = sorted(parts.feet, key=lambda entry: entry[1])
    for x, y in skin - arm - head - bow:
        if (body[y][x+4] not in range(128, 155) and body[y][x+4] not in (208, 209, 210, 254)):
            continue
        choices = [(max(a-x, x-b, 0), abs(y-sole), i) for i, (sole, a, b) in enumerate(soles)
                   if a-1 <= x <= b+1 and (0 <= y <= 2 if pose == 28 else 0 <= sole-y <= 2)]
        if choices:
            feet[min(choices)[2]].add((x, y))
    shoulder = {native(p) for p in fit.shoulder_paint(model, pose)}
    ax, ay = fit.SHOULDER[pose]
    sleeve = {native((ax+i, ay+j)) for i in range(-2, 3) for j in (0, 1, 2)}
    return head, bow, arm, feet, sleeve, shoulder, native


def cloak_folds(rows, role, pose, native, blocked):
    members = role.split("/")
    # Hooded Clerics retain a cream robe underneath a separate cloak.
    family = next((r for r in ("Druid", "Ranger", "Thief") if r in members), None)
    if family == "Thief" and "Cleric" in members:
        family = None
    donor = family or "Ranger"
    ramp = art.singles.MOSS if donor == "Druid" else RAMPS["leaf" if donor == "Ranger" else "slate"]
    layer = rows[donor]
    base, outfit = rows["Body base"], rows[role]
    hood = {native(p) for p in art.singles.hood(pose)[0]} if "Thief" in members else set()
    folds = {}
    for y, row in enumerate(layer):
        for u, color in enumerate(row):
            p = u-4, y
            if p in blocked or p in hood or color not in ramp or color == base[y][u]:
                continue
            if family and outfit[y][u] != color:
                continue  # The corner lies behind another class's sash or weapon strap.
            if color in (17, 208, 69) and not any(
                    0 <= y+j < len(layer) and 0 <= u+i < len(row) and
                    layer[y+j][u+i] in ramp[3:] and layer[y+j][u+i] != base[y+j][u+i]
                    for i, j in ((-1, 0), (1, 0), (0, -1), (0, 1))):
                continue
            folds[p] = round(5*ramp.index(color)/(len(ramp)-1))
    return folds, family is not None


def rear_equipped_cape(rows, role, pose, native, head, bow, forearm):
    """A full outer garment covers the short mantle, belt and crossed sashes."""
    hood = set()
    if "Thief" in role:
        hood = {native(p) for p in art.singles.hood(pose)[0]}
    slate = "Thief" in role and "Ranger" not in role and not role.startswith(("Cleric", "Druid"))
    donor = rows["Thief" if slate else "Ranger"]
    ramp = RAMPS["slate" if slate else "leaf"]
    body = rows["Body base"]
    actual_head = {native(p) for p in fit.head_pixels(pose)}
    foreground = bow | hood | actual_head | forearm
    cape = {}
    for y, row in enumerate(donor):
        for u, c in enumerate(row):
            point = u-4, y
            if c not in ramp or c == body[y][u] or point in foreground:
                continue
            # The Ranger painting already places the locks, fingers and feet
            # ahead of the cloth. A wrist or shoe mask for the *undressed*
            # hip can otherwise punch little holes in a fully covered fold.
            cape[point] = c

    # The rear strike and raised bow pull the neckline up under the nape.
    # Native coordinates follow the exposed back between the passing elbow
    # and the collar. Continue the adjacent crease beneath the actual hair.
    # A few individual holes below those shoulders expose the underlying
    # jersey at the elbow or through a fold on the hip in the long back panel.
    seams = {
        18: ((4, 6, 7), (4, 7, 8), (4, 4, 10), (7, 7, 10)),
        19: ((4, 7, 6), (5, 7, 7), (10, 10, 10), (3, 3, 14)),
        20: ((5, 7, 6), (6, 8, 7), (11, 11, 10)),
        25: ((4, 6, 9), (5, 7, 10)),
        28: ((6, 7, 10),),
    }
    foreground.update(head)
    for lo, hi, row in seams.get(pose, ()):
        for col in range(lo, hi+1):
            x, y = native((col, row))
            if ((x, y) in cape or (x, y) in foreground
                    or body[y][x+4] is None):
                continue
            for point in ((x, y+1), (x-1, y+1), (x+1, y+1), (x-1, y), (x+1, y)):
                if point in cape:
                    cape[x, y] = cape[point]
                    break
    return cape

def export(game_dir, archive):
    from fittedraceequipment import make_layers, write_archive

    atlas = Atlas(game_dir)
    game = atlas.game
    swatches = reference_folds(game)
    cache = {}

    def pose_layers(model, pose):
        if pose not in cache:
            cache[pose] = art.draw(game, pose, swatches)
        rows = cache[pose][model]
        source = game.fr(model+(pose >= 15), pose % 15)
        result = {}
        cuts = landmarks(310 + (model == 2070), pose, game)
        for role, outfit in rows.items():
            if role in ("Original", "Body base"):
                continue
            head, bow, arm, feet, sleeve, cap, native = appendage_masks(
                game, model, pose, source, rows["Body base"], outfit)
            blocked = head | bow | arm | feet[0] | feet[1]
            folds, native_cloak = cloak_folds(rows, role, pose, native, blocked)
            if model == 2070 and pose == 20 and role == "Cleric/Thief":
                # The borrowed corner would project beyond her raised arm
                # after the robe and hood cover the Ranger's shoulder seam.
                folds.pop((13, 8), None)
            cloth, surface, additions, covered, _ = study_surface(
                game, 310 + (model == 2070), pose, rows, role, cuts)
            dye = {(u-4, v) for u, v in surface} - blocked - cap
            waist = len(source)-1-cuts[1] if pose == 28 else cuts[1]
            chest = {(x, y) for x, y in dye if (y >= waist if pose == 28 else y <= waist)}
            arms = dye & sleeve
            # Through a crossing arm the small torso can project directly
            # under the sleeve's candidate box. The centre of the painted
            # jerkin, bounded by the actual shoulder and hip, is chest cloth.
            sx, sy = native(fit.CUT[pose][0])
            hx, hy = native(fit.CUT[pose][1])
            for u, y in cloth - additions - covered:
                x = u-4
                depth = (y-sy)/(hy-sy)
                if (.15 <= depth < 1 and abs(x-(sx+depth*(hx-sx))) <= 2 and
                        rows["Body base"][y][u] is not None and (x, y) not in blocked | cap):
                    chest.add((x, y))
                    arms.discard((x, y))
            region = {co.CHEST: chest - arms, co.ARMS: arms, co.LEGS: dye - chest - arms,
                      co.LEFT_FOOT: feet[0], co.RIGHT_FOOT: feet[1], co.FOREARM: arm, co.BOW: bow}
            # A girdle fastens across the existing waist wrap; the portion
            # of a multiclass sash outside this row keeps its native dye.
            belt = {(u-4, v) for u, v in cloth if v == waist}
            belt.difference_update(blocked)
            if native_cloak:
                belt.difference_update(folds)
            # A bare-backed class borrows its own race's swinging Ranger cloth.
            # Sample the original palette values before reducing to six fold ranks.
            cape = None if native_cloak else {(x, y): rows["Ranger"][y][x+4] for x, y in folds}
            if pose in fit.REAR:
                cape = rear_equipped_cape(rows, role, pose, native, head, bow, arm)
            result[role] = make_layers(source, outfit, 4, 0, region, folds, head, belt, cape or {})
        return result

    write_archive(archive, fit.MODELS, pose_layers)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    export(args.game_dir, args.archive)
