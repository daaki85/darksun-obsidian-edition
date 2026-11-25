"""Druid, Psionicist, Ranger and Thief studies on the fitted halfling bodies."""
import argparse
import math
from pathlib import Path

from PIL import Image

import halflingstudy as fit
from elfreview import TERRAIN, dwarf, elf, label, loop
from outfitdetail import RAMPS, reference_folds
from wornreview import Atlas

SINGLES = ("Druid", "Psionicist", "Ranger", "Thief")
TEAL = (69, 69, 70, 70, 71, 71, 40, 72, 73)
MOSS = (208, 69, 188, 53, 189, 54, 226, 55, 227, 56)
# Back corner of the long cloak in the profile walk, strikes, bow and recoil.
# It lags the shoulder in step two, then drops as the forward knee straightens.
TRAIL = {2: (-2, 16), 11: (-3, 15), 12: (-3, 14), 13: (-3, 17), 14: (0, 16),
         15: (-2, 16), 16: (4, 13), 17: (1, 13), 21: (2, 12), 22: (0, 13),
         23: (-1, 11), 24: (-2, 16), 27: (-1, 13)}
# Left edge of the exposed brow, relative to the head origin. On the
# turning front strikes the face moves towards the opposite edge of the hood.
BROW = {15: 2, 16: 3, 17: 1, 21: 2, 24: 3, 26: 2, 27: 2}


def cloak_outline(pose, short):
    (sx, sy), (hx, hy), left, right, _ = fit.CUT[pose]
    if pose in TRAIL:
        tx, ty = TRAIL[pose]
        if short:
            tx = (tx + hx-3)//2
            ty = min(ty, hy+2)
        hem = ((tx, ty), (tx+2, ty), (hx-1, hy+(1 if short else 3)),
               (hx+2, hy+(0 if short else 2)))
        corners = ((sx-2, sy), (sx-4, sy+3), *hem, (sx+2, sy+1))
    else:
        lx, ly = left
        rx, ry = right
        if short:
            lx, ly, rx, ry = hx-4, hy+1, hx+4, hy+2
        corners = ((sx-2, sy), (sx-4, sy+2), (lx-1, ly-1), (lx, ly),
                   (hx-2, ly-1), (hx, (ly+ry)//2+1), (rx-1, ry-1),
                   (rx+1, ry), (sx+4, sy+2), (sx+2, sy))
    if pose in (17, 27):
        # The head dips towards the left hand. The far shoulder stays high
        # on the right, lifting the cloth clear of the forward knee.
        reach = 5 if short else 7
        drop = 2 if short else 4
        corners = ((sx+1, sy-1), (sx+4, sy), (hx+reach, hy+drop-1),
                   (hx+reach-1, hy+drop), (hx+1, hy+drop-1), (hx-1, hy))
    if pose == 28:
        # The folded legs rise above the fallen torso. Stack the cloth at
        # the hip, with the left fold fanning onto the ground.
        tip = hy+1 if short else hy+3
        corners = ((sx-3, sy), (sx-4, sy+2), (hx-5, tip-1), (hx-3, tip),
                   (hx, tip-1), (hx+3, tip), (hx+4, hy), (sx+2, sy+1))
    panel = fit.pixels(corners)
    # Leave the floor visible inside the bent elbow. On the back swing
    # the cloth instead reaches the arm; carry its fold into that corner.
    if pose == 0:
        panel -= {(x, y) for x, y in panel if x <= 6 and 8 <= y <= 12}
    if pose == 6:
        panel -= {(x, y) for x, y in panel if x >= 14 and 8 <= y <= 13}
    arm_folds = {1: ((5, 9), (15, 9), (15, 10)), 7: ((11, 10),),
                 8: ((11, 9), (11, 10)), 9: ((2, 10), (12, 9)), 10: ((2, 11),)}
    panel.update(arm_folds.get(pose, ()))
    if not short:
        hem_turns = {4: (13, 17), 11: (0, 15), 24: (1, 16), 26: (9, 21)}
        if pose in hem_turns:
            panel.add(hem_turns[pose])
    return panel


def hood(pose):
    """Cut the opening from the fitted cowl and leave the turning jaw exposed."""
    left, top, spans = fit.HEADS[pose]
    head = fit.head_pixels(pose)
    shell, opening = set(), set()
    for i, (lo, hi) in enumerate(spans):
        brow = BROW.get(pose, 4 if pose in fit.PROFILE else 2)
        for xx in range(lo, hi+1):
            p = left+xx, top+i
            if pose not in fit.REAR and i >= (6 if pose == 27 else 2) and xx >= brow and (
                    pose in fit.PROFILE or i >= 3 or xx < hi):
                opening.add(p)
            else:
                shell.add(p)
    # Extend the back seam below the crown independently of the hair.
    for i in range(2, len(spans)+2):
        y = top+i
        x = left+spans[min(i, len(spans)-1)][0]
        shell.add((x-1, y))
        if i >= len(spans):
            shell.add((x, y))
    return shell - opening, opening, head


# Inclusive scanline spans in the retail man's cel. The woman uses the
# registration in CUT. The upper rows track the two armholes from shoulders
# to waist (y=5..11). Each hem starts on the row below the waist.
# Short cloth follows the pelvis; the long cloth lags the advancing leg.
REAR_FIT = {
    1: (((7,13),(6,13),(6,13),(7,13),(7,13),(7,12),(7,12)),
        ((6,13),(6,13),(6,12)), ((6,13),(5,14),(5,14),(5,14),(6,14))),
    7: (((3,9),(3,10),(3,10),(3,10),(4,9),(4,8),(4,8)),
        ((3,9),(3,9),(4,9)), ((3,10),(2,10),(2,10),(2,10),(2,8))),
    8: (((3,9),(2,10),(3,10),(3,9),(3,9),(3,8),(3,8)),
        ((3,9),(3,9),(3,8)), ((2,10),(2,10),(1,10),(1,9),(1,7))),
    9: (((4,10),(3,11),(4,11),(4,11),(4,9),(5,10),(5,10)),
        ((4,10),(4,10),(5,10)), ((4,11),(4,11),(4,12),(5,12),(7,12))),
    10: (((4,10),(4,11),(4,11),(4,9),(4,9),(5,10),(5,10)),
         ((4,10),(4,10),(5,10)), ((4,11),(4,11),(4,12),(5,12),(7,12))),
}
# Position of the dominant fold at the shoulder, waist and hem. The hem
# turns a little later than the waist at each change of support.
REAR_FOLD = {1: (9, 9, 10), 7: (6, 6, 5), 8: (6, 5, 3),
             9: (7, 7, 8), 10: (8, 8, 10)}


def rear_single_rows(fitted, model, pose, swatches):
    body = fitted["Body base"]
    out = {k: [row[:] for row in body] for k in SINGLES}
    upper, skirt, train = REAR_FIT[pose]
    shoulder, waist, hem = REAR_FOLD[pose]
    dx, dy = fit.CUT[pose][-1] if model == 2070 else (0, 0)
    head = fit.head_pixels(pose)
    # Carry her shaded lower locks across the cloth. At the tips the hair
    # separates again and the material between the strands shows through.
    hair = set()
    if model == 2070:
        for y in range(5, 11):
            row = fitted["Original"][y+dy]
            locks = [u-4-dx for u, c in enumerate(row) if c in (179, 180, 181, 182)]
            if locks:
                hair.update((x, y) for x in locks)
                if y <= 7:
                    hair.update((x, y) for x in range(min(locks), max(locks)+1))
                if y == 7:
                    hair.update((x, y+1) for x in locks[1:])

    for role, ramp in (("Druid", MOSS), ("Psionicist", TEAL), ("Ranger", RAMPS["leaf"]),
                       ("Thief", RAMPS["slate"])):
        long = role in ("Ranger", "Thief")
        rows = upper + (train if long else skirt)
        for i, (lo, hi) in enumerate(rows):
            y = 5+i
            v = y+dy
            pivot = (shoulder+(waist-shoulder)*i/6 if i <= 6 else
                     waist+(hem-waist)*(i-6)/5)
            if long and (5 if pose == 8 else 4) <= i <= 6:
                # Cloth falls past the waist at the back. Ease it towards
                # the hem while keeping the swinging arm in front of it.
                hem_left, hem_right = train[0]
                lo -= int(lo > hem_left)
                hi += int(hi < hem_right)
            for x in range(lo, hi+1):
                u = x+4+dx
                if (x, y) in head or role != "Thief" and (x, y) in hair:
                    continue
                # Armholes are cut into the native shoulder silhouette.
                if long and i < 7 and not upper[i][0] <= x <= upper[i][1] and body[v][u] is not None:
                    continue
                if i < 4 and body[v][u] is None:
                    continue
                grain = swatches["slate"][(i+2)%8][(x-waist-i//3)%8]
                distance = x-pivot
                # The upper fold passes over the shoulder blade and opens
                # into a wider crease below the belt.
                fold = math.cos(distance*(1.05 if i < 6 else 1.45)+.75*math.sin(i*.65))
                shade = .56+.17*fold+.062*grain
                if i < 3:
                    shade += .08 if x < shoulder else -.07
                if x == hi or (i > 5 and x == lo):
                    shade -= .19
                color = fit.dye(ramp, shade*(len(ramp)-1))
                if role == "Psionicist":
                    # The vest is fitted to the ribcage, with leather below
                    # a tie that tips down onto the weight-bearing hip.
                    if i >= 7:
                        if i == 9 and (x <= lo or x >= hi or abs(distance) > 2):
                            continue
                        color = fit.dye(RAMPS["hide"], 5.4+.7*grain+1.1*math.cos(distance))
                        # A short overlapping teal panel turns down from the
                        # tie at one hip instead of splitting over both legs.
                        if -2.5 < x-waist+.5*(i-7) < 1:
                            color = fit.dye(TEAL, 4.1+.54*grain-.7*(i-7))
                    if i == 6 or i == 5 and x > waist+1:
                        color = fit.dye(TEAL, 2+.3*grain)
                elif role == "Druid":
                    # A short leaf cape folds over the ochre skirt. Leave
                    # one longer fold above the hip swinging away.
                    if i >= 7+(abs(distance) < 1.5):
                        if i == 9 and abs(distance) > 2.7:
                            continue
                        color = fit.dye(RAMPS["ochre"], 5.9+.65*grain-1.2*(x == hi))
                elif i == len(rows)-1:
                    if abs(distance) > 2.2:
                        continue
                    color = fit.dye(ramp, (shade-.13)*(len(ramp)-1))
                if role == "Thief" and i < 3 and abs(x-shoulder) <= 3-i:
                    color = fit.dye(ramp, 4.8+.5*grain-.4*i)
                out[role][v][u] = color
    return out


def draw(game, model, pose, swatches):
    fitted = fit.rows_for(game, model, pose, swatches["linen"])
    fit.check_uncovered_head(game, model, pose, fitted)
    if pose == 28:
        fitted = {k: fit.flip(v) for k, v in fitted.items()}
    body, fighter = fitted["Body base"], fitted["Fighter"]
    rear_walk = pose in REAR_FIT
    out = rear_single_rows(fitted, model, pose, swatches) if rear_walk else {
        k: [r[:] for r in body] for k in SINGLES}
    (sx, sy), (hx, hy), _, _, offset = fit.CUT[pose]
    dx, dy = offset if model == 2070 else (0, 0)
    shell, opening, head = hood(pose)
    neck = {(x, y+1) for x, y in head} - head
    long, short = cloak_outline(pose, False), cloak_outline(pose, True)
    bow = {(x, y) for y, lo, hi in fit.BOW_ARCS.get(pose, ()) for x in range(lo, hi+1)}
    if model == 2070 and pose == 24:
        bow.add((6-dx, 16-dy))
    cb, frame = divmod(pose, 15)
    hands = game.fig(model).parts(cb, frame).hands.values() if pose != 28 else ()
    grip = {(x-dx+i, y-dy+j) for x, y in hands for i in (-1, 0, 1) for j in (-1, 0, 1)}
    head_x, head_y, spans = fit.HEADS[pose]
    face_and_neck = head | neck
    for v, row in enumerate(body):
        y = v-dy
        depth = (y-sy)/max(1, hy-sy)
        axis = sx+(hx-sx)*min(1, max(0, depth))
        for u, skin in enumerate(row):
            x = u-4-dx
            pt = x, y
            if pt in bow:
                continue
            tailored = fighter[v][u] != skin
            grain = swatches["slate"][(y-sy)%8][(x-hx)%8]
            turn = 1.6*math.cos((x-axis)*1.24-.65*depth)
            shade = 5.2+turn+.65*grain-.36*abs(x-axis)
            if not rear_walk and pt not in face_and_neck and tailored:
                # Cross the fitted teal vest with a narrow leather tie. The
                # back flap hangs from the belt and clears the forward thigh.
                if y == hy or (y == hy+1 and x == hx-2):
                    out["Psionicist"][v][u] = fit.dye(RAMPS["hide"], shade-.6)
                else:
                    out["Psionicist"][v][u] = fit.dye(TEAL, shade+.3 if y < hy else shade-1.3)
                for role in ("Ranger", "Thief", "Druid"):
                    ramp = RAMPS["ochre"] if role == "Druid" else RAMPS["hide"]
                    lift = 1.8 if role == "Druid" and y > hy else 0
                    out[role][v][u] = fit.dye(ramp, shade+lift+(2 if y < hy else 0))
            if not rear_walk and pt not in face_and_neck and (skin is None or pt not in grip):
                for role, panel, ramp in (("Druid", short, MOSS), ("Ranger", long, RAMPS["leaf"]),
                                          ("Thief", long, RAMPS["slate"])):
                    if pt not in panel:
                        continue
                    # At the front, separate the two falls of cloth to expose
                    # the tunic. In profile the near arm crosses the drape.
                    rim = x-axis
                    gap = 2.4
                    if role == "Druid":
                        # The short cape pins over the breastbone and parts
                        # below it, with the near shoulder carrying the fold.
                        gap = max(0, 2.3*depth-.65)
                    near_side = rim < .6 if pose in (17, 27) else rim > -.6
                    if pose not in fit.REAR and skin is not None and (
                            not tailored or (pose in TRAIL and near_side) or
                            (pose not in TRAIL and abs(rim) < gap)):
                        continue
                    if pose in fit.REAR and skin is not None and not tailored and (
                            y < hy or abs(x-axis) > 4 and y < hy+2):
                        continue
                    edge = (x+1, y) not in panel or (x, y+1) not in panel
                    swing = (axis-TRAIL[pose][0])*.54 if pose in TRAIL else (hx-sx)*.4
                    if pose in (17, 27):
                        swing = -2.8
                    fold = math.cos(1.42*(x-axis+swing*depth)+.4*depth*depth)
                    light = .48+.20*fold+.038*grain-.16*edge-.055*min(depth, 2)
                    out[role][v][u] = fit.dye(ramp, light*(len(ramp)-1))
            if pt in shell and (pt not in grip or pt in head):
                i = y-head_y
                lo, hi = spans[min(max(i, 0), len(spans)-1)]
                across = (x-head_x-lo)/max(1, hi-lo)
                rim = any((x+i, y+j) in opening for i, j in ((0, 1), (1, 0)))
                light = 8.8-5*abs(across-.3)-.50*i+.43*grain-3.5*rim
                out["Thief"][v][u] = fit.dye(RAMPS["slate"], light)
    if model == 2070:
        tuck_hair(game, pose, swatches, out["Thief"], fitted["Original"], dx, dy, bow, shell, opening)
    return {k: fit.flip(v) if pose == 28 else v for k, v in (fitted | out).items()}


def tuck_hair(game, pose, swatches, thief, native, dx, dy, bow, shell, opening):
    # Both retail bodies use the same registered movement. Where a lock of
    # hair tucks into the hood it exposes either air, skin, or the cloak fold
    # underneath. Sample that particular layer from the short-haired twin.
    twin = draw(game, 2068, pose, swatches)
    donor, original = twin["Thief"], twin["Original"]
    if pose == 28:
        donor, original = fit.flip(donor), fit.flip(original)
    _, top, spans = fit.HEADS[pose]
    end = max(fit.CUT[pose][1][1]+1, top+len(spans)+1)
    hair_tones = {157, 179, 180, 181, 182, 183, 184, 200, 201}
    locks = {(u, v) for v, row in enumerate(native) for u, c in enumerate(row)
             if c in hair_tones and v-dy <= end and (u-4-dx, v-dy) not in bow}
    fringe = {(u+i, v+j) for u, v in locks
              for i, j in ((-1, 0), (1, 0), (0, -1), (0, 1))}
    for v, row in enumerate(native):
        for u, c in enumerate(row):
            x, y = u-4-dx, v-dy
            if (x, y) in bow or (x, y) in shell or (x, y) in opening:
                continue
            if (u, v) not in locks and not (c in fit.DARK | {255} and
                                            ((u, v) in fringe or y < top+len(spans)+2)):
                continue
            col = x+4
            inside = 0 <= y < len(donor) and 0 <= col < len(donor[0])
            if not inside or original[y][col] != c or y <= top+len(spans):
                thief[v][u] = donor[y][col] if inside else None


def verify_face(outfits, model, pose):
    dx, dy = fit.CUT[pose][-1] if model == 2070 else (0, 0)
    _, opening, head = hood(pose)
    for role in SINGLES:
        rows, original = outfits[role], outfits["Original"]
        points = opening if role == "Thief" else head
        for x, y in points:
            u, v = x+dx+4, y+dy
            if pose == 28:
                u, v = len(rows[0])-1-u, len(rows)-1-v
            if rows[v][u] != original[v][u]:
                raise ValueError(f"{model} {role}, pose {pose}: changed face pixel at {(x, y)}")


def render(game_dir, output):
    atlas = Atlas(game_dir)
    game = atlas.game
    swatches = reference_folds(game)
    sand = Image.open(TERRAIN).convert("RGB").crop((39, 130, 93, 181))
    stone = Image.open(TERRAIN.with_name("2026-11-09-figures-all-gone.png")).convert("RGB").crop(
        (164, 21, 218, 72))
    columns = ("Original", *SINGLES)
    frames = []
    # Every still sheet includes the three earlier singles for comparison.
    all_roles = ("Original", "Gladiator", "Fighter", "Cleric", *SINGLES)
    sheets = {m: Image.new("RGB", (175+8*83, 42+29*66), dwarf.PAPER) for m in fit.MODELS}
    for sheet in sheets.values():
        for j, role in enumerate(all_roles):
            label(sheet, (175+j*83+40, 14), role, 14, "ma")
    for pose, name in enumerate(dwarf.NAMES):
        page = Image.new("RGB", (688, 591), dwarf.PAPER)
        label(page, (12, 7), "Halfling single classes", 20)
        label(page, (12, 560), "Above at 2× on arena sand. Below at game size on sand and paving.", 14)
        label(page, (677, 12), f"{pose:02}  {name}", 15, "ra")
        for i, model in enumerate(fit.MODELS):
            outfits = draw(game, model, pose, swatches)
            verify_face(outfits, model, pose)
            label(page, (10, 82+i*153), ("Man", "Woman")[i], 14)
            for j, role in enumerate(columns):
                x, y = 78+j*121, 59+i*153
                if i == 0:
                    label(page, (x+54, 36), role, 14, "ma")
                tile = elf.placed_tile(game, outfits[role], sand, 2, 0, 0, 0)
                page.paste(tile, (x, y))
                for offset, ground in ((0, sand), (54, stone)):
                    page.paste(elf.placed_tile(game, outfits[role], ground, 1, 0, 0, 0),
                               (x+offset, y+102))
            sheet = sheets[model]
            sy = 41+66*pose
            label(sheet, (10, sy+18), f"{pose:02}  {name}", 14)
            for j, role in enumerate(all_roles):
                tile = elf.placed_tile(game, outfits[role], sand, 1, 0, 0, 0).crop((7, 18, 47, 50))
                sheet.paste(tile.resize((80, 64), Image.Resampling.NEAREST), (175+j*83, sy))
        label(page, (12, 367), "Shattered Lands figures at the same scales", 15)
        refs = ((630, "Retail Thief"), (724, "Retail Mage"), (1252, "Retail Warrior"),
                (300, "Human Psionicist"), (301, "Human Druid"))
        for j, (pic, caption) in enumerate(refs):
            frame = pose
            if pic > 301 and pose%15 >= game.count(pic+pose//15):
                frame, caption = 0, caption+" (idle)"
            role = caption.split()[-1]
            x = 10+136*j
            label(page, (x+54, 384), caption, 12, "ma")
            for ground, scale, offset in ((sand, 2, 0), (sand, 1, 0), (stone, 1, 54)):
                atlas.floor = ground
                tile = atlas.tile(pic, frame, role, "Class colors", scale)
                if scale == 2:
                    page.paste(tile, (x, 401))
                else:
                    page.paste(tile, (x+offset, 503))
        frames.append(page)
    output.mkdir(parents=True, exist_ok=True)
    loop(frames, output/"halfling-singles.gif")
    for model, sheet in sheets.items():
        sex = "man" if model == 2068 else "woman"
        sheet.save(output/f"halfling-{sex}-singles.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    render(args.game_dir, args.output)
