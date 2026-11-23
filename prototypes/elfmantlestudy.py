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


# Profile overlays in native coordinates, starting at row 7. Each line gives
# the trailing edge and the painted ranks up to the leading edge. The collar
# stays on its original pixels. The corner lifts in step 2, then unrolls in 3.
PROFILE_SWING = {
    11: (
        (0, "245654"), (-1, "2456754"), (-2, "24676653"),
        (-3, "246654532"), (-4, "246545431"), (-4, "356435431"),
        (-5, "246424531"), (-6, "245324431"), (-6, "353213421"),
        (-6, "34210331"), (-6, "2410231"), (-5, "31021"),
        (-5, "2011"), (-4, "10"),
    ),
    12: (
        (5, "2456654"), (3, "245676654"), (1, "24567546543"),
        (0, "24665456432"), (-1, "24654565432"), (-2, "24643654321"),
        (-3, "2464354321"), (-4, "246324321"), (-5, "24532321"),
        (-5, "3532131"), (-5, "342101"), (-5, "241"), (-5, "1"),
    ),
    13: (
        (3, "245654"), (2, "2456754"), (1, "24567543"),
        (0, "246655432"), (-1, "246545431"), (-1, "356435431"),
        (-2, "246435431"), (-2, "356425431"), (-3, "246424321"),
        (-4, "24632431"), (-5, "24532310"), (-6, "24532110"),
        (-6, "3521"), (-6, "21"),
    ),
    14: (
        (4, "245654"), (3, "2456754"), (2, "245675432"),
        (1, "246655432"), (0, "2465454321"), (0, "3564354321"),
        (-1, "2464354321"), (-2, "2464245321"), (-2, "356424321"),
        (-3, "246324321"), (-4, "24532431"), (-4, "35321310"),
        (-4, "3421010"), (-4, "241"), (-4, "1"),
    ),
}


def swing_tile(atlas, pose, item, scale):
    side, top = sprites.room(False)
    rows = [row[:] for row in atlas.sequence(304, False, "Preserver", item)[pose]]
    frame = classoutfits.frames("Preserver", False, 2061)[pose]
    old_cloth = {(x, y) for x, y, _ in frame.cloak}
    head = set(frame.head)
    # The single-class Fighter supplies the leather and limbs under this
    # mantle. Only uncover pixels inside the native body when lifting the hem.
    under = atlas.sequence(304, False, "Fighter", "Class colors")[pose]
    body = atlas.game.fr(2061, pose)
    for x, y in old_cloth - head:
        if y >= 7:
            on_body = 0 <= x < len(body[y]) and body[y][x] is not None
            rows[y + top][x + side] = under[y + top][x + side] if on_body else None
    ramp = PLUM if item == "Class colors" else sg.CLOAK_COLOURS[65]
    for y, (left, ranks) in enumerate(PROFILE_SWING[pose], 7):
        for x, rank in enumerate(ranks, left):
            if (x, y) in head:
                continue
            if (x, y) not in old_cloth and rows[y + top][x + side] is not None:
                continue
            rows[y + top][x + side] = ramp[round(int(rank) * (len(ramp) - 1) / 7)]
    return elf.placed_tile(atlas.game, rows, atlas.floor, scale, side, top, 0)


def swing_comparison(atlas, output):
    columns = (("Original Mage", 724), ("Current Preserver", 304),
               ("Trailing mantle", 304), ("Original Thief", 630))
    frames = []
    sheet = Image.new("RGB", (82 + 5 * 156, 34 + 4 * 132), dwarf.PAPER)
    label(sheet, (160 + 4 * 156, 8), "Equipped cloak study", 14, "ma")
    for i, (title, _) in enumerate(columns):
        label(sheet, (160 + i * 156, 8), title, 14, "ma")
    for step, pose in enumerate(PROFILE_SWING, 1):
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
