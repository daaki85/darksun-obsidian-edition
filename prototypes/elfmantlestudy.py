"""Render the male elf Preserver fold proposal beside the retail Mage and Thief.

python prototypes/elfmantlestudy.py GAME_DIR OUTPUT_DIR
"""
import argparse
from pathlib import Path

from PIL import Image

from wornreview import Atlas, dwarf, elf, label, sg, sprites
from dsloader import classoutfits

# Shoulder gathers break into two creases of unequal lengths. Indices are
# local light values, with 0 in the deepest return of the fold.
BACK = (
    "23466443222",
    "24575544332",
    "13667655432",
    "12465766543",
    "12355467432",
    "11365356322",
    "11465245321",
    "11475235421",
    "12564125421",
    "12563125421",
    "12653016321",
    "13553015321",
    "13542015311",
    "02442015211",
    "02331013201",
    "01221012101",
)
SIDE = (
    "233454332",
    "234675432",
    "234657543",
    "235546654",
    "135435564",
    "146324553",
    "146213452",
    "146213442",
    "146203442",
    "145203431",
    "135203431",
    "135203421",
    "124202421",
    "124102321",
    "023102210",
    "012101210",
)
PLUM = (17, 112, 174, 175, 74, 239, 233, 235)
# The shoulder and the spread of the lower fold, in native picture coordinates.
# Interpolate across the actual body rather than shifting the pattern when a
# hand temporarily hides a cell in a row.
RANGES = {
    1: ((4, 14), (5, 13), (2, 12)),
    7: ((1, 11), (2, 10), (0, 9)),
    8: ((-1, 8), (-1, 7), (-2, 7)),
    9: ((1, 11), (2, 10), (0, 9)),
    10: ((3, 13), (3, 12), (1, 11)),
    2: ((1, 6), (0, 3), (-3, 2)),
    11: ((0, 5), (-1, 3), (-4, 2)),
    12: ((6, 12), (4, 9), (-3, 9)),
    13: ((3, 9), (1, 7), (-4, 7)),
    14: ((4, 10), (2, 7), (-2, 7)),
}


def study_tile(atlas, pose, item, scale):
    frame = classoutfits.frames("Preserver", False, 2061)[pose]
    rows = [row[:] for row in atlas.sequence(304, False, "Preserver", item)[pose]]
    side, top = sprites.room(False)
    head = set(frame.head)
    design = BACK if pose in (1, 7, 8, 9, 10) else SIDE
    ramp = PLUM if item == "Class colors" else sg.CLOAK_COLOURS[65]
    shoulder, middle, hem = RANGES[pose]
    for x, y, _ in frame.cloak:
        if (x, y) in head or y < 6:
            continue
        start, end = (shoulder, middle) if y <= 11 else (middle, hem)
        drop = (y - 6) / 5 if y <= 11 else min(1, (y - 11) / 8)
        left, right = [a + (b - a) * drop for a, b in zip(start, end)]
        line = design[min(len(design) - 1, y - 6)]
        col = round((x - left) * (len(line) - 1) / (right - left))
        value = int(line[max(0, min(len(line) - 1, col))])
        rows[y + top][x + side] = ramp[round(value * (len(ramp) - 1) / 7)]
    return elf.placed_tile(atlas.game, rows, atlas.floor, scale, side, top, 0)


def comparison(atlas, pose):
    image = Image.new("RGB", (624, 278), dwarf.PAPER)
    label(image, (9, 7), "Male elf Preserver · cloak fold study", 18)
    label(image, (615, 10), dwarf.NAMES[pose], 13, "ra")
    for i, (title, obj) in enumerate((("Retail Mage", 724), ("Current mantle", 304),
                                      ("Proposed folds", 304), ("Retail Thief", 630))):
        x = 156 * i
        label(image, (x + 78, 39), title, 14, "ma")
        for scale, dx, y in ((3, 0, 59), (1, 52, 196)):
            tile = (study_tile(atlas, pose, "Class colors", scale) if i == 2
                    else atlas.tile(obj, pose, "Preserver", "Class colors", scale))
            image.paste(tile, (x + dx, y))
    label(image, (9, 253), "Same poses on arena ground · 3× above, game size below", 13)
    return image


def render(atlas, output):
    poses = (1, 7, 8, 9, 10, 2, 11, 12, 13, 14)
    frames = [comparison(atlas, pose) for pose in poses]
    frames[0].save(output / "elf-mantle-fold-study.gif", save_all=True, append_images=frames[1:],
                   duration=[750 if pose in (1, 2) else 240 for pose in poses], loop=0)
    sheet = Image.new("RGB", (785, 512), dwarf.PAPER)
    columns = (("Retail Mage", 724, "Class colors", False), ("Current mantle", 304, "Class colors", False),
               ("Proposed folds", 304, "Class colors", True), ("Current worn cloak", 304, "Cloak", False),
               ("Proposed worn cloak", 304, "Cloak", True))
    for i, (title, obj, item, proposed) in enumerate(columns):
        x = 200 + i * 130
        label(sheet, (x, 9), title, 12, "ma")
        for j, pose in enumerate((1, 12, 13)):
            y = 30 + j * 160
            if i == 0:
                label(sheet, (7, y + 47), dwarf.NAMES[pose], 13)
            for scale, offset in ((2, 0), (1, 95)):
                tile = (study_tile(atlas, pose, item, scale) if proposed
                        else atlas.tile(obj, pose, "Preserver", item, scale))
                sheet.paste(tile, (x - tile.width // 2, y + offset))
    sheet.save(output / "elf-mantle-fold-study.png")


# Trailing cloth outside the male elf's silhouette, from row 6 down.
# Narrowing the last runs opens the space beneath the lifted corner.
SWING_EDGES = {
    11: ((0, 0), (-1, -1), (-2, -1), (-3, -1), (-4, 0), (-5, 1), (-5, 1),
         (-6, 1), (-6, 1), (-6, 2), (-5, 2), (-5, 2), (-5, -2), (-4, -3)),
    12: ((4, 4), (2, 4), (0, 3), (-1, 2), (-2, 1), (-3, 1), (-4, 1),
         (-4, 1), (-5, 1), (-5, 1), (-6, -2), (-6, -4)),
    13: ((2, 2), (1, 2), (0, 2), (0, 2), (-1, 1), (-2, 1), (-2, 1),
         (-3, 2), (-3, 2), (-4, 2), (-5, 2), (-6, 2), (-6, -3)),
    14: ((3, 3), (2, 2), (1, 1), (0, 2), (-1, 3), (-1, 4), (-2, 4),
         (-2, 3), (-3, 3), (-3, 3), (-4, 3), (-4, 3), (-4, 3), (-4, 0), (-4, -2)),
}

# Pigments from the outer fold of retail Mage 724. Each maps to a plum
# pigment for the class mantle and a relief rank for the six-color worn dye.
MAGE_FOLD = {
    158: (17, 0), 159: (174, 1), 38: (112, 2), 160: (175, 2),
    71: (58, 3), 39: (239, 4), 161: (232, 5), 40: (233, 5),
    49: (115, 3), 50: (119, 4), 212: (118, 4),
}


def swing_tile(atlas, pose, item, scale):
    side, top = sprites.room(False)
    source = atlas.sequence(304, False, "Preserver", item)[pose]
    rows = [row[:] for row in source]
    frame = classoutfits.frames("Preserver", False, 2061)[pose]
    body = atlas.game.fr(2061, pose)
    mage = atlas.game.fr(724, pose)
    body_edge = [next((x for x, c in enumerate(row) if c is not None), len(row)) for row in body]
    cloth = {(x, y) for x, y, _ in frame.cloak}
    for x, y in cloth:
        if x < body_edge[y]:
            rows[y + top][x + side] = None
    for y, (left, right) in enumerate(SWING_EDGES[pose], 6):
        body_left = body_edge[y]
        # Read the continuous strip inward from the Mage's trailing edge.
        # Stop before the original arm, staff, or open ground.
        start = next(i for i, c in enumerate(mage[y]) if c in MAGE_FOLD)
        strip = []
        for color in mage[y][start:]:
            if color not in MAGE_FOLD:
                break
            strip.append(MAGE_FOLD[color])
        width = right - left + 1
        for offset in range(width):
            x = left + offset
            if x >= body_left or rows[y + top][x + side] is not None:
                continue
            # Keep the short underfold where the loose cloth turns into the
            # existing panel. The tucked edge moves with the hip.
            if x >= body_left - 2 and (x, y) in cloth:
                rows[y + top][x + side] = source[y + top][x + side]
                continue
            # Sample at pixel centers so rounding a narrow strip does not
            # discard both the highlight and the valley on a two-pixel hem.
            index = (2 * offset + 1) * len(strip) // (2 * width)
            plum, rank = strip[index]
            rows[y + top][x + side] = sg.CLOAK_COLOURS[65][rank] if item == "Cloak" else plum
    return elf.placed_tile(atlas.game, rows, atlas.floor, scale, side, top, 0)


def swing_comparison(atlas, output):
    columns = (("Original Mage", 724), ("Current Preserver", 304),
               ("Revised mantle", 304), ("Original Thief", 630))
    frames = []
    sheet = Image.new("RGB", (82 + 5 * 156, 34 + 4 * 132), dwarf.PAPER)
    label(sheet, (160 + 4 * 156, 8), "Equipped cloak study", 14, "ma")
    for i, (title, _) in enumerate(columns):
        label(sheet, (160 + i * 156, 8), title, 14, "ma")
    for step, pose in enumerate(SWING_EDGES, 1):
        image = Image.new("RGB", (624, 255), dwarf.PAPER)
        label(image, (8, 6), "Male elf Preserver · profile walk", 18)
        label(image, (616, 9), f"Step {step}/4", 14, "ra")
        label(sheet, (8, 89 + (step - 1) * 132), f"Step {step}", 14)
        for i, (title, obj) in enumerate(columns):
            x = 156 * i
            label(image, (x + 78, 37), title, 14, "ma")
            for scale, dx, y in ((3, 0, 57), (1, 52, 197)):
                tile = (swing_tile(atlas, pose, "Class colors", scale) if i == 2
                        else atlas.tile(obj, pose, "Preserver", "Class colors", scale))
                image.paste(tile, (x + dx, y))
                if scale == 3:
                    sheet.paste(tile, (82 + x, 34 + (step - 1) * 132))
        sheet.paste(swing_tile(atlas, pose, "Cloak", 3), (82 + 4 * 156, 34 + (step - 1) * 132))
        frames.append(image)
    frames[0].save(output / "elf-mantle-swing.gif", save_all=True, append_images=frames[1:],
                   duration=210, loop=0)
    sheet.save(output / "elf-mantle-swing.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    atlas = Atlas(args.game_dir)
    render(atlas, args.output)
    swing_comparison(atlas, args.output)
