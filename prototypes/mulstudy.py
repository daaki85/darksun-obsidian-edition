"""First Mul class fittings, using the retail figure and the human garment studies."""
import argparse
from functools import lru_cache
from math import exp, sin, pi
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageDraw

from elfreview import TERRAIN, dwarf, elf, label, loop
from outfitdetail import RAMPS, reference_folds
from wornreview import Atlas
from dsloader import art, classoutfits as co

MODEL = 2093
PAD = 8
ROLES = ("Original", "Body base", "Gladiator", "Fighter", "Cleric")
PARENTS = {"Gladiator": "Gladiator", "Fighter": "Warrior"}
# Position of the matching human cel in the Mul cel. Combat cels have
# different bounding boxes when the striking hand travels above the head.
REGISTER = ((1, 1), (0, 0), (0, 0), (1, 1), (0, 1), (1, 1), (0, 1), (0, 0), (0, 0), (0, 0),
            (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, -7), (0, -1), (-7, 1), (0, -3), (0, -7),
            (-9, 0), (-5, -7), (0, -1), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (1, 0))

# Per-row limits on the bald scalp, ear and jaw. Origins move separately
# from the shoulder in the backswing, recoil and bow poses.
FRONT = ((2, 4), (1, 5), (0, 6), (0, 6), (0, 6), (1, 6), (2, 5))
BACK = ((1, 3), (0, 4), (0, 5), (0, 5), (0, 5), (0, 4), (1, 4))
SIDE = ((2, 4), (1, 5), (0, 5), (0, 6), (1, 6), (2, 5))
HEADS = (
    (8, 0, FRONT), (9, 0, BACK), (5, 0, SIDE), (7, 0, FRONT), (6, 0, FRONT), (7, 0, FRONT),
    (7, 0, FRONT), (4, 0, BACK), (5, 0, BACK), (5, 0, BACK), (5, 0, BACK), (7, 0, SIDE),
    (10, 0, SIDE), (6, 0, SIDE), (9, 0, SIDE),
    (6, 2, ((2, 4), (1, 5), (0, 5), (0, 6), (1, 5), (2, 5))),
    (9, 0, FRONT), (3, 4, ((3, 5), (2, 6), (1, 6), (1, 6), (0, 6), (1, 5), (2, 4))),
    (4, 0, BACK), (2, 0, BACK), (4, 0, BACK),
    (6, 0, ((1, 4), (0, 5), (0, 5), (0, 5), (0, 5), (1, 4))),
    (11, 0, SIDE), (11, 0, SIDE), (5, 0, ((3, 5), (1, 6), (0, 8), (0, 8), (1, 8), (3, 6))),
    (6, 3, BACK), (5, 3, ((1, 4), (0, 5), (0, 5), (0, 5), (0, 5), (1, 4))),
    (1, 3, ((4, 7), (2, 6), (1, 6), (1, 6), (0, 6), (0, 5), (0, 4))),
    (5, 0, ((3, 7), (2, 8), (1, 9), (1, 9), (0, 10), (1, 9), (2, 8))),
)
# The original orange skin is lit differently from the human reference.
# Carry the depth of each reconstructed muscle plane into the Mul's ramp.
SKIN = {254: 129, 128: 129, 129: 129, 134: 135, 133: 135, 132: 136, 131: 136, 130: 137, 144: 138,
        145: 139, 146: 140, 147: 141, 148: 142, 149: 143, 150: 143, 151: 151, 152: 152, 153: 153}
NATIVE_LIGHT = {*range(135, 144), 149, 151, 152, 153}
MATERIAL = set(RAMPS["hide"]+RAMPS["linen"]+RAMPS["ochre"]
               ) | {203, 118, 119, 122, 124, 126, 214, 215, 168, 169}
DARK = {128, 129, 254}
# The Mul is broader through the upper arms on these frontal cels.
# At the armhole, extend the fitted leather or sleeve across the outer
# shoulder and keep the bare deltoid visible beneath its turned edge.
FRONT_WALK = {0, 3, 4, 5, 6}


def head_pixels(pose, w, h):
    left, top, spans = HEADS[pose]
    pixels = {(left+x, top+y) for y, (a, b) in enumerate(spans) for x in range(a, b+1)}
    if pose == 28:
        return {(w-1-x, h-1-y) for x, y in pixels}
    # These corners lie on the harness or the raised wrist, outside the jaw.
    outside = {8: {(5, 5), (9, 6)}, 10: {(7, 6)}, 23: {(13, 5)}, 26: {(5, 7)}}
    return pixels - outside.get(pose, set())


@lru_cache(maxsize=2)
def body_chunk(combat):
    tag = "combat" if combat else "walk"
    with ZipFile(Path(co.__file__).with_name("human_outfit_layers.zip")) as archive:
        return archive.read(f"Study/{tag}-body")


# Each cut was traced on the unpadded Mul body. The four cross-sections
# (row, left, right) locate the shoulder, ribs, girdle and hanging hem.
# The last number lifts one corner of the hem as the near knee advances.
ROBE_CUTS = (
    ((5, 4, 18), (9, 4, 17), (14, 7, 14), (23, 5, 17), 2),
    ((6, 5, 16), (10, 5, 16), (14, 7, 14), (23, 5, 17), -2),
    ((4, 3, 8), (9, 1, 8), (15, 2, 8), (23, -1, 10), 2),
    ((5, 3, 17), (9, 4, 16), (14, 5, 13), (22, 4, 15), 2),
    ((5, 3, 16), (9, 3, 15), (14, 5, 12), (22, 4, 14), -2),
    ((4, 4, 15), (9, 3, 15), (13, 5, 13), (22, 4, 15), -1),
    ((5, 3, 16), (9, 4, 15), (14, 5, 13), (22, 4, 14), 2),
    ((6, 1, 12), (9, 2, 12), (14, 4, 10), (22, 2, 12), 2),
    ((5, 1, 12), (9, 2, 13), (14, 4, 10), (23, 2, 12), 2),
    ((6, 2, 13), (9, 3, 13), (14, 5, 11), (22, 3, 13), -1),
    ((5, 3, 13), (9, 3, 13), (14, 5, 11), (23, 3, 13), -2),
    ((4, 5, 10), (9, 3, 10), (15, 3, 8), (22, -1, 9), 2),
    ((4, 8, 13), (9, 5, 12), (15, 5, 10), (22, 0, 13), -2),
    ((4, 4, 9), (9, 2, 10), (15, 2, 7), (22, -2, 8), 2),
    ((3, 6, 12), (8, 4, 12), (15, 4, 9), (22, 0, 13), 3),
    ((7, 5, 11), (11, 3, 11), (15, 3, 9), (23, 0, 13), 2),
    ((5, 7, 17), (9, 7, 17), (12, 7, 16), (16, 5, 17), 1),
    ((7, 8, 13), (10, 8, 14), (13, 8, 14), (17, 4, 15), -2),
    ((6, 3, 9), (10, 2, 10), (14, 2, 8), (23, 0, 11), -2),
    ((6, 4, 10), (9, 3, 10), (14, 4, 11), (22, 2, 14), -2),
    ((5, 5, 10), (9, 6, 12), (14, 6, 13), (22, 4, 16), -2),
    ((5, 5, 15), (10, 5, 13), (15, 6, 14), (23, 5, 16), 2),
    ((5, 7, 15), (9, 6, 13), (14, 4, 11), (22, 0, 12), 3),
    ((5, 7, 15), (9, 4, 12), (13, 4, 11), (20, 0, 12), 2),
    ((5, 5, 11), (10, 5, 10), (15, 4, 10), (23, 1, 12), 2),
    ((8, 7, 11), (12, 5, 12), (17, 6, 10), (25, 4, 14), -2),
    ((8, 4, 13), (13, 4, 12), (18, 6, 12), (26, 5, 15), 1),
    ((6, 6, 11), (9, 5, 12), (11, 5, 13), (16, 5, 16), 3),
    ((6, 2, 16), (10, 4, 15), (13, 5, 13), (18, 3, 14), 1),
)

# Near forearms that cross the linen, traced from elbow to wrist on the
# source (centre line and thickness). The garment turns under the sleeve.
CROSSING_ARMS = {
    2: ((2, 10), (5, 14), (11, 15), 3), 11: ((4, 10), (5, 13), (11, 14), 3),
    12: ((7, 8), (6, 10), (5, 14), 3), 13: ((4, 9), (3, 12), (5, 16), 3),
    14: ((5, 9), (7, 12), (15, 13), 3), 15: ((4, 10), (3, 14), (5, 17), 3),
    17: ((12, 10), (10, 13), (3, 17), 3), 18: ((11, 7), (10, 9), (7, 11), 2),
    19: ((4, 8), (4, 11), (1, 13), 2), 20: ((8, 7), (5, 8), (1, 8), 2),
    22: ((13, 7), (16, 9), (21, 10), 3), 23: ((14, 7), (15, 11), (18, 13), 3),
    24: ((6, 9), (6, 12), (11, 15), 3), 25: ((12, 10), (11, 12), (10, 14), 2),
    26: ((2, 8), (3, 10), (5, 11), 3), 27: ((3, 9), (2, 12), (4, 14), 3),
}


@lru_cache(maxsize=2)
def linen_grain(game):
    return reference_folds(game)["linen"]


# Warm middle tones keep broad lit planes ivory on arena sand. The old
# high-contrast brown/white trim is confined to the belt and turned hem.
MUL_LINEN = (208, 204, 207, 205, 194, 206, 120, 61, 123, 199, 125, 62, 155, 63)


def cleric_robe(game, pose, body, protected, arm):
    shoulder, ribs, waist, hem, lift = ROBE_CUTS[pose]
    height, width = len(body), len(body[0]) - 2*PAD
    result = [row[:] for row in body]
    grain = linen_grain(game)
    side = pose in (2, 11, 12, 13, 14, 15, 22, 23, 24)
    rear = pose in (1, 7, 8, 9, 10, 18, 19, 20, 25)
    cuts = (shoulder, ribs, waist, hem)
    for start, end in zip(cuts, cuts[1:]):
        for y in range(start[0], end[0] + (end == hem)):
            t = (y-start[0]) / (end[0]-start[0])
            left = round(start[1] + t*(end[1]-start[1]))
            right = round(start[2] + t*(end[2]-start[2]))
            for x in range(left, right+1):
                u = (x-left)/(right-left)
                # One knee pushes the corner up; two offset folds describe
                # the volume over the thighs, including the space between them.
                bottom = hem[0] - round(max(0, lift)*u + max(0, -lift)*(1-u)
                                        + 1.9*abs(2*u-1)**3)
                if y > bottom:
                    continue
                px, py = (width-1-x, height-1-y) if pose == 28 else (x, y)
                skin = body[py][px+PAD]
                if ((px, py) in protected or (y <= waist[0] and skin is None)
                        or (skin is not None and 0 <= px < width and arm.getpixel((px, py)))):
                    continue
                relief = grain[(y-waist[0]) % 8][(x-waist[1]) % 8]
                shade = 9.1 + .9*relief - 3.5*u + .8*sin(pi*u)
                if y < waist[0]:
                    # A shallow back yoke and diagonal front overlap leave the
                    # neck open. In profile only the near lapel is visible.
                    depth = (y-shoulder[0])/(waist[0]-shoulder[0])
                    if rear:
                        seam_y = shoulder[0] + 1 + round(2*sin(pi*u))
                        if y == seam_y:
                            shade -= 2.4
                    else:
                        seam = .76 - .65*depth
                        distance = (u-seam)*(right-left)
                        if abs(distance) < .68:
                            shade -= 3.3
                        elif .68 <= distance < 1.7:
                            shade += 2.1
                    shade += 1.5*(1-depth) - 1.3*exp(-.7*(y-waist[0]+1)**2)
                else:
                    drop = (y-waist[0])/(hem[0]-waist[0])
                    fold = (.41 if side else .53) + (.22 if lift > 0 else -.23)*drop
                    dist = (u-fold)*(right-left)
                    shade += 3.2*exp(-.45*(dist+1.7)**2) - 4.5*exp(-.65*dist**2)
                belt_y = waist[0] - int(u > .72)
                if y == belt_y:
                    color = 94 if u < .55 else 90
                else:
                    if y == bottom:
                        shade -= 4.0
                    if x == right:
                        shade -= 3.8
                    if x == left:
                        shade -= 1.8
                    color = MUL_LINEN[max(0, min(len(MUL_LINEN)-1, round(shade)))]
                result[py][px+PAD] = color
    return result


def fitted_rows(game, pose):
    cb, f = divmod(pose, 15)
    native, human = game.fr(MODEL+cb, f), game.fr(2095+cb, f)
    bare = co.Frame(art.decode_frame(body_chunk(cb), f)[2], {}).canvas(human, PAD)
    dx, dy = REGISTER[pose]
    w, h = len(native[0]), len(native)
    head = head_pixels(pose, w, h)
    fig = game.fig(MODEL)
    parts = fig.parts(cb, f)
    bow = game.bow(fig, native, parts) if pose in (24, 25, 26) else set()
    original = [[None]*PAD+list(r)+[None]*PAD for r in native]
    body = [r[:] for r in original]
    keep = head | bow
    for y, row in enumerate(native):
        for x, c in enumerate(row):
            if c is None or c in NATIVE_LIGHT or (x, y) in keep:
                continue
            u, v = x-dx+PAD, y-dy+PAD
            donor = bare[v][u] if 0 <= v < len(bare) and 0 <= u < len(bare[0]) else None
            # Keep the outline of the trailing foot where it meets the floor.
            if c in DARK and (y == h-1 or (y >= h-3 and native[y+1][x] is None)):
                body[y][x+PAD] = 129
                continue
            if donor in SKIN:
                body[y][x+PAD] = SKIN[donor]
                continue
            # The Mul has an extra row of muscle along parts of his arms
            # and calves. Follow the nearest lit skin inside the same limb.
            samples = [bare[v+j][u+i] for i, j in ((0, -1), (-1, 0), (1, 0), (0, 1))
                       if 0 <= v+j < len(bare) and 0 <= u+i < len(bare[0]) and bare[v+j][u+i] in SKIN]
            edge = x == w-1 or row[x+1] is None or y == h-1 or native[y+1][x] is None
            body[y][x+PAD] = 129 if edge else SKIN[samples[0]] if samples else 135
    # The near hand crosses the hip at side step two, and the draw hand
    # overlaps the tunic in the front bow. Keep those knuckles on top.
    for hx, hy in parts.hands.values():
        for ix, iy in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
            x, y = hx+ix, hy+iy
            if 0 <= x < w and 0 <= y < h and native[y][x] is not None:
                keep.add((x, y))
    # At a crossed arm the cloth must pass behind the forearm as well as
    # behind the fingertips. The Fighter guard can still cover the upper arm.
    arm = Image.new("1", (w, h))
    leather_keep = keep.copy()
    if pose in CROSSING_ARMS:
        elbow, bend, wrist, thickness = CROSSING_ARMS[pose]
        draw = ImageDraw.Draw(arm)
        draw.line((bend, wrist), fill=1, width=thickness)
        leather_keep.update((x, y) for y, row in enumerate(native) for x, c in enumerate(row)
                            if c is not None and arm.getpixel((x, y)))
        draw.line((elbow, bend), fill=1, width=thickness)
    out = {"Original": original, "Body base": body}
    for role, parent in PARENTS.items():
        frame = co.frames(parent, cb)[f]
        dressed = frame.canvas(human, PAD)
        cloth = {}
        for v, row in enumerate(dressed):
            for u, c in enumerate(row):
                if c in MATERIAL and c != bare[v][u]:
                    cloth[u, v] = c
        # Carry enclosed dark recesses with the material, particularly the
        # seam below a bone guard. Other black belongs to the native body.
        material_pixels = set(cloth)
        for v, row in enumerate(dressed):
            for u, c in enumerate(row):
                if c in DARK and c != bare[v][u] and sum((u+i, v+j) in material_pixels for i, j in
                                                         ((-1, 0), (1, 0), (0, -1), (0, 1))) >= 2:
                    cloth[u, v] = 88
        garment = [r[:] for r in body]
        for (u, v), c in cloth.items():
            x, y = u-PAD+dx, v-PAD+dy
            if not (0 <= y < h and -PAD <= x < w+PAD) or (x, y) in leather_keep:
                continue
            if not (0 <= x < w and native[y][x] is not None):
                continue
            if role == "Gladiator" and pose < 28 and v-PAD >= co.LANDMARKS[pose][-1]:
                # Dark leather at the turned-under hem separates the warm
                # kilt from the copper thigh, even on the sunlit floor.
                if c in RAMPS["hide"] and (u, v+1) not in material_pixels:
                    c = 89 if (u+1, v) in material_pixels else 88
            garment[y][x+PAD] = c
        if pose in FRONT_WALK and role != "Gladiator":
            _, _, _, _, sy, sl, sr, _ = co.LANDMARKS[pose]
            for y in (sy+dy, sy+dy+1):
                for x, step in ((sl+dx, -1), (sr+dx, 1)):
                    outer = x+step
                    if (0 <= outer < w and native[y][outer] in NATIVE_LIGHT and (outer, y) not in keep
                            and garment[y][x+PAD] != body[y][x+PAD]
                            and garment[y][outer+PAD] == body[y][outer+PAD]):
                        garment[y][outer+PAD] = 91
        if role == "Gladiator" and pose < 28:
            # A bronze clasp peeks out of the overlapped hide at the hip.
            # Follow the moving belt and leave it hidden behind a crossing arm.
            _, _, _, _, _, sl, sr, waist = co.LANDMARKS[pose]
            y = waist+dy
            hip = round((sl+sr)/2)+dx+1
            for x in (hip, hip-1, hip+1):
                if (0 < x < w-1 and 0 <= y < h and (x, y) not in leather_keep and (x-1, y) not in leather_keep
                        and garment[y][x+PAD] in RAMPS["hide"]
                        and garment[y][x+PAD-1] in RAMPS["hide"]):
                    garment[y][x+PAD] = 169
                    garment[y][x+PAD-1] = 95
                    break
        out[role] = garment
    out["Cleric"] = cleric_robe(game, pose, body, keep, arm)
    return out


def cleric_comparison(game, pose, rows, sand, previous_sheet):
    # Sample the lossless 2x proof at 61f043d so its pixels and registration
    # survive even after the old generator is changed.
    x = 8 + (pose % 2)*558 + ROLES.index("Cleric")*110
    y = 76 + (pose//2)*137
    before = previous_sheet.crop((x, y, x+108, y+102)).resize((54, 51), Image.Resampling.NEAREST)
    cb, f = divmod(pose, 15)
    npc = 1563 + cb
    caption = "Retail Priest"
    if f >= game.count(npc):
        npc, f = 1563, 0
        caption += " (idle)"
    def tile(pixels):
        return elf.placed_tile(game, pixels, sand, 1, 0, 0, 0)

    samples = (("Mul body", tile(rows["Body base"])), ("Previous robe", before),
               ("Refitted robe", tile(rows["Cleric"])), (caption, tile(game.fr(npc, f))))
    page = Image.new("RGB", (736, 276), dwarf.PAPER)
    label(page, (12, 7), "Mul Cleric fitting", 20)
    label(page, (724, 8), f"{pose:02}   {dwarf.NAMES[pose]}", 16, "ra")
    for j, (name, sample) in enumerate(samples):
        x = 16 + j*182
        label(page, (x+81, 35), name, 15, "ma")
        page.paste(sample.resize((162, 153), Image.Resampling.NEAREST), (x, 58))
        page.paste(sample, (x+54, 216))
    return page


def render(game_dir, output, previous_sheet=None):
    atlas = Atlas(game_dir)
    game = atlas.game
    sand = Image.open(TERRAIN).convert("RGB").crop((39, 130, 93, 181))
    paving = Image.open(TERRAIN.with_name("2026-11-09-figures-all-gone.png")).convert("RGB")
    paving = paving.crop((158, 21, 212, 72))
    frames = []
    comparisons = []
    before = Image.open(previous_sheet).convert("RGB") if previous_sheet else None
    sheet = Image.new("RGB", (2*5*110+28, 15*137+44), dwarf.PAPER)
    label(sheet, (12, 7), "Mul fittings   /   all 29 map poses", 20)
    references = ((1252, "Retail Warrior"), (1563, "Retail Priest"),
                  ("Gladiator", "Human Gladiator"), ("Warrior", "Human Warrior"),
                  ("Priest", "Human Priest"))
    for pose, name in enumerate(dwarf.NAMES):
        rows = fitted_rows(game, pose)
        page = Image.new("RGB", (846, 468), dwarf.PAPER)
        label(page, (12, 8), "Mul   /   revised fittings", 21)
        label(page, (832, 9), f"{pose:02}   {name}", 17, "ra")
        for j, role in enumerate(ROLES):
            x = 8+j*167
            label(page, (x+81, 43), role, 15, "ma")
            tile = elf.placed_tile(game, rows[role], sand, 1, 0, 0, 0)
            page.paste(tile.resize((162, 153), Image.Resampling.NEAREST), (x, 65))
            page.paste(tile, (x+25, 224))
            page.paste(elf.placed_tile(game, rows[role], paving, 1, 0, 0, 0), (x+83, 224))
            sx = 8 + pose % 2*558 + j*110
            sy = 43 + pose//2*137
            if j == 0:
                label(sheet, (sx, sy), f"{pose:02}   {name}", 14)
            label(sheet, (sx, sy+17), role, 12)
            sheet.paste(tile.resize((108, 102), Image.Resampling.NEAREST), (sx, sy+33))
        label(page, (12, 287), "Retail and human references", 17)
        for j, (reference, caption) in enumerate(references):
            x = 8+j*167
            if isinstance(reference, int):
                cb, f = divmod(pose, 15)
                pic = reference+cb
                if f >= game.count(pic):
                    pic, f = reference, 0
                    caption += " (idle)"
                ref = game.fr(pic, f)
                large = elf.placed_tile(game, ref, sand, 2, 0, 0, 0)
                small = elf.placed_tile(game, ref, paving, 1, 0, 0, 0)
            else:
                atlas.floor = sand
                large = atlas.tile(300, pose, reference, "Class colors", 2)
                atlas.floor = paving
                small = atlas.tile(300, pose, reference, "Class colors", 1)
            label(page, (x+81, 320), caption, 14, "ma")
            page.paste(large, (x, 348))
            page.paste(small, (x+109, 399))
        frames.append(page)
        if before is not None:
            comparisons.append(cleric_comparison(game, pose, rows, sand, before))
    output.mkdir(parents=True, exist_ok=True)
    loop(frames, output/"mul-study.gif")
    sheet.save(output/"mul-poses.png")
    if comparisons:
        loop(comparisons, output/"mul-cleric-fitting.gif")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--previous-sheet", type=Path, help="mul-poses.png from 61f043d for the fitting comparison")
    args = parser.parse_args()
    render(args.game_dir, args.output, args.previous_sheet)
