"""Export the approved Mul art and its pose-fitted equipment surfaces.

python prototypes/mulequipment.py GAME_DIR PATH_TO_ARCHIVE
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw

import mulmultis as multi
import mulsingles as singles
import mulstudy as fit
from dsloader import classoutfits as co, spritegear as sg
from fittedraceequipment import make_layers, write_archive
from outfitdetail import reference_folds
from studyarmordetail import base_garment
from wornreview import Atlas


def foot_surfaces(source, parts, pose):
    if pose == 28:
        return sg._fallen_boot_cells(source, None, fit.MODEL)
    feet = [set(), set()]
    for y, row in enumerate(source):
        for x, color in enumerate(row):
            if color is None:
                continue
            nearby = [(max(left-x, x-right, 0), sole-y, foot)
                      for foot, (sole, left, right) in enumerate(parts.feet[:2])
                      if 0 <= sole-y <= 3 and left-1 <= x <= right+1]
            if nearby:
                feet[min(nearby)[2]].add((x, y))
    return feet


def layers(game, swatches, model, pose):
    combat, frame = divmod(pose, 15)
    source = game.fr(model+combat, frame)
    w, h = len(source[0]), len(source)
    figure = game.fig(model)
    parts = figure.parts(combat, frame)
    rows = multi.draw(game, pose, swatches)
    body = rows["Body base"]
    head = fit.head_pixels(pose, w, h)
    bow = game.bow(figure, source, parts) if pose in (24, 25, 26) else set()
    hands = {(hx+dx, hy+dy) for hx, hy in parts.hands.values()
             for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (0, 0))}
    hands.update(fit.ARM_EDGES.get(pose, ()))
    if pose in fit.CROSSING_ARMS:
        elbow, bend, wrist, width = fit.CROSSING_ARMS[pose]
        mask = Image.new("1", (w, h))
        ImageDraw.Draw(mask).line((elbow, bend, wrist), fill=1, width=width)
        hands.update((x, y) for y in range(h) for x in range(w) if mask.getpixel((x, y)))
    def native(x, y):
        return (w-1-x, h-1-y) if pose == 28 else (x, y)

    hood = {native(x, y) for x, y in multi.hood_pixels(pose)}
    guard = {native(x, y) for x, y in fit.shoulder_paint(model, pose)}
    feet = foot_surfaces(source, parts, pose)
    shoulder, rib, waist, _, _ = fit.ROBE_CUTS[pose]
    wy, wl, wr = waist
    output = {}
    for role, outfit in rows.items():
        if role in ("Original", "Body base"):
            continue
        base = base_garment(312, role)
        outer = "Druid" if base == "Druid" else "Thief"
        ramp = singles.MOSS if outer == "Druid" else singles.SLATE
        # A separately equipped cloak shares the Thief's actual moving hem
        # and folds. Stop at the nape, where the Thief's hood is sewn on.
        donor = rows[outer]
        forearm = {(x, y) for x, y in hands if 0 <= x < w and 0 <= y < h
                   and body[y][x+fit.PAD] is not None and outfit[y][x+fit.PAD] == body[y][x+fit.PAD]}
        face = {(x, y) for x, y in head if 0 <= x < w and 0 <= y < h and outfit[y][x+fit.PAD] is not None}
        if "Thief" in role:
            face.update((x, y) for x, y in hood if 0 <= y < h and 0 <= x+fit.PAD < len(body[y])
                        and outfit[y][x+fit.PAD] != body[y][x+fit.PAD])
        regions = {co.BOW: bow, co.FOREARM: forearm, co.CHEST: set(), co.ARMS: set(), co.LEGS: set()}
        keep = face | bow | forearm
        for bit, cells in zip((co.LEFT_FOOT, co.RIGHT_FOOT), feet):
            regions[bit] = {(x, y) for x, y in cells if outfit[y][x+fit.PAD] == body[y][x+fit.PAD]
                            and body[y][x+fit.PAD] is not None and (x, y) not in keep}
            keep.update(regions[bit])
        cloak, belt = {}, set()
        cape = {}
        for py, row in enumerate(outfit):
            for u, color in enumerate(row):
                px = u-fit.PAD
                point = px, py
                if point in keep:
                    continue
                x, y = native(px, py)
                bare = body[py][u]
                pigment = donor[py][u]
                if pigment in ramp and pigment != bare and point not in hood and point not in head:
                    # Retain the secondary class's sword belt, sash or bone on
                    # an existing outer garment when that garment is dyed.
                    if base != outer or color == rows[base][py][u]:
                        cloak[point] = round(5*ramp.index(pigment)/(len(ramp)-1))
                        cape[point] = pigment
                if base == "Druid":
                    # His leaf mantle ends at the ribs. A full-length worn
                    # cloak continues behind it, following the long slate
                    # drape on this figure in precisely the same stride.
                    trailing = rows["Thief"][py][u]
                    if (trailing in singles.SLATE and trailing != bare and point not in cape
                            and point not in hood and point not in head
                            and (bare is None or pose in singles.REAR and y > waist[0])):
                        cape[point] = trailing
                if color is None or color == bare or point in head:
                    continue
                covered = base == outer and point in cloak
                parent = rows[base][py][u]
                # Wrap one leather edge around the moving pelvis. From the
                # side the short return sits below the near hip; the rest
                # of the kilt and mantle keep their own material.
                belt_y = wy-round(.18*(x-(wl+wr)/2))
                near = wl if pose in singles.REAR else wr
                turned_edge = x == near and y == belt_y+1
                if wl <= x <= wr and not covered and (y == belt_y or turned_edge):
                    belt.add(point)
                if covered or color != parent or (point in guard and "Fighter" in role):
                    continue
                # Keep the neckline, waist fastening, hem and cloak lining.
                if y <= shoulder[0]+1 or abs(y-wy) <= 1 or bare is None:
                    continue
                if y >= wy+2:
                    below = py-1 if pose == 28 else py+1
                    if 0 <= below < h and outfit[below][u] is not None:
                        regions[co.LEGS].add(point)
                elif x < rib[1] or x > rib[2]:
                    regions[co.ARMS].add(point)
                else:
                    regions[co.CHEST].add(point)
        output[role] = make_layers(source, outfit, fit.PAD, 0, regions, cloak, face, belt, cape)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    game = Atlas(args.game_dir).game
    swatches = reference_folds(game)
    write_archive(args.archive, (fit.MODEL,), lambda model, pose: layers(game, swatches, model, pose))
