"""Build the Loader garments and equipment surfaces on the two half-giants.

python prototypes/halfgiantequipment.py GAME_DIR ARCHIVE
"""
import argparse
from pathlib import Path

import halfgiantstudy as hg
from fittedraceequipment import make_layers, write_archive
from studyarmordetail import Atlas, co, landmarks, study_surface
from dsloader import spritebracers

LEFT = 5


def pose_layers(atlas, swatch, model, pose):
    game = atlas.game
    cb, f = divmod(pose, 15)
    fig = game.fig(model)
    source = fig.rows(cb, f)
    width, height = len(source[0]), len(source)
    obj = 309 if model == 2074 else 308
    parts = fig.parts(cb, f)
    visible = {}
    outfits = hg.study_rows(game, model, pose, swatch, pairs=True, panels=visible)
    body = outfits["Body base"]
    dx, dy = hg.FEMALE_OFFSETS[pose] if model == 2074 else (0, 0)

    def native(x, y):
        x, y = x+dx, y+dy
        return (width-1-x, height-1-y) if pose == 28 else (x, y)

    def points(cut):
        return {native(x, y) for x, y in cut}

    def sample(rows, p):
        x, y = p
        return rows[y][x+LEFT]

    def inside(p):
        x, y = p
        return 0 <= y < height and -LEFT <= x < width+LEFT

    top, _, _, _, crossing, locks, _, waist = hg.fitted_panels(pose, model == 2074)
    cloaked = points(visible["cloak"])
    sleeve = points(visible["sleeve"])
    guard = points(visible["guard"])
    hem = set()
    # The center keeper and each end ride the turning pelvis separately.
    for (x0, y0), (x1, y1) in zip(waist, waist[1:]):
        for x in range(x0, x1+1):
            t = (x-x0)/max(1, x1-x0)
            hem.add(native(x, round(hg.mix(y0, y1, t))))
    crown = points(locks)
    shoulder = hg.CUTS[pose][0]
    for y in range(height):
        for x in range(width):
            px, py = native(x, y)
            if not inside((px, py)):
                continue
            if pose in hg.LOW_HEAD:
                cx, cy, rx, ry = hg.LOW_HEAD[pose]
                on_head = ((x-cx)/rx)**2+((y-cy)/ry)**2 <= 1
            else:
                on_head = min(shoulder[0], shoulder[2])+1 <= x <= max(shoulder[0], shoulder[2])-1 and y <= min(shoulder[1], shoulder[3])
            if on_head:
                crown.add((px, py))
    crown.update(parts.hair)
    if model == 2074 and pose in hg.PROFILE_LOCKS:
        sy, spans = hg.PROFILE_LOCKS[pose]
        crown.update((x, sy+i) for i, (l, r) in enumerate(spans) for x in range(l, r+1))
    bow = game.bow(fig, source, parts) if 24 <= pose <= 26 else set()
    cuffs = set(spritebracers.visible(source, model, f, bool(cb), None, None, source, 0))
    arm = points(crossing) | cuffs
    arm.update((hx+a, hy+b) for hx, hy in parts.hands.values() for a in (-1, 0, 1) for b in (-1, 0, 1))
    soles = list(hg.SOLES[pose])
    if model == 2074 and pose == 27:
        soles[0] = (16, 34)
    boots = ({}, {})
    for n, (toe, sole) in enumerate(soles):
        for y in range(sole-5, sole+1):
            for x in range(toe-4, toe+5):
                pt = native(x, y)
                if inside(pt):
                    boots[n][pt] = abs(x-toe)+.5*(sole-y)
    for pt in set(boots[0]) & set(boots[1]):
        del boots[1 if boots[0][pt] <= boots[1][pt] else 0][pt]

    ranger = outfits["Ranger"]
    fold = {p: round(5*hg.RAMPS["leaf"].index(sample(ranger, p))/(len(hg.RAMPS["leaf"])-1))
            for p in cloaked}
    result = {}
    cuts = landmarks(obj, pose, game)
    for role, outfit in outfits.items():
        if role in ("Original", "Body base"):
            continue
        _, surface, _, _, _ = study_surface(game, obj, pose, outfits, role, cuts)
        surface = {(u-LEFT, y) for u, y in surface}
        def skin_or_base(p):
            return inside(p) and sample(outfit, p) is not None and sample(outfit, p) == sample(body, p)
        forearm = {p for p in arm-bow if skin_or_base(p)}
        head = {p for p in crown-bow-forearm if skin_or_base(p)}
        foot = tuple({p for p in boot if skin_or_base(p) or (
                     sample(outfit, p) in (88, 90, 95) and sample(outfit, p) == sample(outfits["Gladiator"], p))}
                     for boot in boots)
        hidden = head | forearm | bow | foot[0] | foot[1]
        # On bare-backed classes the separate worn cape uses the Ranger's
        # moving fall. Hair, forearms, toes and the bow remain in front.
        folds = {p: r for p, r in fold.items() if p not in hidden}
        chest = surface & points(top)
        arms = surface & sleeve if "Cleric" in role else set()
        if role == "Fighter":
            arms.update(p for p in guard if inside(p) and sample(outfit, p) is not None)
        regions = {co.CHEST: chest-arms-hidden, co.ARMS: arms-hidden, co.LEGS: surface-chest-arms-hidden,
                   co.FOREARM: forearm, co.LEFT_FOOT: foot[0], co.RIGHT_FOOT: foot[1],
                   co.BOW: {p for p in bow if inside(p) and sample(outfit, p) is not None}}
        native_cloak = "Ranger" in role
        belt = {p for p in hem-hidden if inside(p) and sample(outfit, p) is not None
                and not (native_cloak and p in folds)}
        cape = None if native_cloak else {p: sample(ranger, p) for p in folds}
        result[role] = make_layers(source, outfit, LEFT, 0, regions, folds, head, belt, cape)
    return result


def export(game_dir, archive):
    atlas = Atlas(game_dir)
    swatch = hg.reference_folds(atlas.game)["linen"]
    write_archive(archive, hg.MODELS, lambda model, pose: pose_layers(atlas, swatch, model, pose))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    export(args.game_dir, args.archive)
