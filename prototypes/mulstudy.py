"""First Mul class fittings, using the retail figure and the human garment studies."""
import argparse
from functools import lru_cache
from pathlib import Path
from zipfile import ZipFile

from PIL import Image

from elfreview import TERRAIN, dwarf, elf, label, loop
from outfitdetail import RAMPS
from wornreview import Atlas
from dsloader import art, classoutfits as co

MODEL = 2093
PAD = 8
ROLES = ("Original", "Body base", "Gladiator", "Fighter", "Cleric")
PARENTS = {"Gladiator": "Gladiator", "Fighter": "Warrior", "Cleric": "Priest"}
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
                    cloth[u, v] = 88 if role != "Cleric" else 204
        garment = [r[:] for r in body]
        for (u, v), c in cloth.items():
            x, y = u-PAD+dx, v-PAD+dy
            if not (0 <= y < h and -PAD <= x < w+PAD) or (x, y) in keep:
                continue
            if role != "Cleric" and not (0 <= x < w and native[y][x] is not None):
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
                        garment[y][outer+PAD] = 205 if role == "Cleric" else 91
        if role == "Cleric":
            # Turn the hem over the leading shin. These cells lie just
            # outside the old priest hem where it meets the wider Mul calf.
            for x, y in {10: ((14, 20),), 12: ((3, 22),), 26: ((3, 25),)}.get(pose, ()):
                garment[y][x+PAD] = 205
            # Close the fold under the striking arm as the sleeve crosses
            # the torso. The openings outside the elbow and bow stay clear.
            if pose == 15:
                for y, shade in ((16, 205), (17, 204), (18, 207)):
                    garment[y][2+PAD] = shade
            elif pose == 20:
                garment[9][5+PAD] = 205
        if role == "Gladiator" and pose < 28:
            # A bronze clasp peeks out of the overlapped hide at the hip.
            # Follow the moving belt and leave it hidden behind a crossing arm.
            _, _, _, _, _, sl, sr, waist = co.LANDMARKS[pose]
            y = waist+dy
            hip = round((sl+sr)/2)+dx+1
            for x in (hip, hip-1, hip+1):
                if (0 < x < w-1 and 0 <= y < h and (x, y) not in keep
                        and garment[y][x+PAD] in RAMPS["hide"]
                        and garment[y][x+PAD-1] in RAMPS["hide"]):
                    garment[y][x+PAD] = 169
                    garment[y][x+PAD-1] = 95
                    break
        out[role] = garment
    return out


def render(game_dir, output):
    atlas = Atlas(game_dir)
    game = atlas.game
    sand = Image.open(TERRAIN).convert("RGB").crop((39, 130, 93, 181))
    paving = Image.open(TERRAIN.with_name("2026-11-09-figures-all-gone.png")).convert("RGB")
    paving = paving.crop((158, 21, 212, 72))
    frames = []
    sheet = Image.new("RGB", (2*5*110+28, 15*137+44), dwarf.PAPER)
    label(sheet, (12, 7), "Mul fittings   /   all 29 map poses", 20)
    references = ((1252, "Retail Warrior"), (1563, "Retail Priest"),
                  ("Gladiator", "Human Gladiator"), ("Warrior", "Human Warrior"),
                  ("Priest", "Human Priest"))
    for pose, name in enumerate(dwarf.NAMES):
        rows = fitted_rows(game, pose)
        page = Image.new("RGB", (846, 468), dwarf.PAPER)
        label(page, (12, 8), "Mul   /   first fittings", 21)
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
    output.mkdir(parents=True, exist_ok=True)
    loop(frames, output/"mul-study.gif")
    sheet.save(output/"mul-poses.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    render(args.game_dir, args.output)
