"""Compare shipped Gladiators with their previous Loader build and retail party pictures."""
import argparse
from pathlib import Path
import zlib

from PIL import Image, ImageOps

from elfreview import dwarf, elf, label, loop
from materialfoldreview import PEOPLE, TILE
from platefitreview import former
from wornreview import Atlas, TERRAIN, sprites


NAMES = (*PEOPLE, "Thri-kreen")
LOOKS = ("Stock", "Before", "After")
POSES = (0, 1, 2, 16, 19, 22)


def capture(game_dir):
    atlas = Atlas(game_dir)
    with Image.open(TERRAIN) as image:
        sand = image.convert("RGB").crop((45, 142, 99, 194))
    pictures = {}
    for obj in range(300, 314):
        model = atlas.pictures.model(obj)
        for combat in (False, True):
            poses = atlas.sequence(obj, combat, "Gladiator", "Class colors")
            for frame, dressed in enumerate(poses):
                pose = 15 * int(combat) + frame
                retail = atlas.game.fr(model + combat, frame)
                for look, rows, margin in (("Stock", retail, 0), ("Gladiator", dressed, sprites.room(combat)[0])):
                    tile = elf.placed_tile(atlas.game, rows, sand, 1, margin, 0, 0)
                    pictures[f"{obj}/{look}/{pose}"] = zlib.compress(tile.tobytes()).hex()
    return pictures


def tiles(previous, current):
    for obj in range(300, 314):
        for pose in range(29):
            stock = f"{obj}/Stock/{pose}"
            outfit = f"{obj}/Gladiator/{pose}"
            assert current[stock] == previous[stock]
            if obj == 313:
                assert previous[outfit] == current[outfit]
            for look, encoded in zip(LOOKS, (current[stock], previous[outfit], current[outfit])):
                yield (obj, pose, look), Image.frombytes("RGB", TILE, zlib.decompress(bytes.fromhex(encoded)))


def lineup(pictures):
    col = 64
    group = 3 * TILE[1] + 24
    sheet = Image.new("RGB", (90 + len(NAMES) * col, 73 + len(POSES) * group), dwarf.PAPER)
    label(sheet, (7, 4), "Gladiators on arena sand  ·  Game size", 17)
    for i, name in enumerate(NAMES):
        race, _, sex = name.rpartition(" ")
        center = 87 + i * col + TILE[0] // 2
        label(sheet, (center, 34), race or sex, 11, "ma")
        if race:
            label(sheet, (center, 49), sex, 11, "ma")
    for i, pose in enumerate(POSES):
        y = 69 + group * i
        label(sheet, (7, y), f"{pose:02}   {dwarf.NAMES[pose]}", 14)
        for row, look in enumerate(LOOKS):
            top = y + 21 + row * TILE[1]
            label(sheet, (7, top + 22), look, 13)
            for col_index in range(len(NAMES)):
                sheet.paste(pictures[300 + col_index, pose, look], (87 + col_index * col, top))
    return sheet


def motion(pictures, objects, pose):
    scale = 3
    col = TILE[0] * (scale + 1) + 8
    row = TILE[1] * scale + 8
    sheet = Image.new("RGB", (62 + col * len(objects), 65 + row * len(LOOKS)), dwarf.PAPER)
    label(sheet, (8, 5), f"{pose:02}    {dwarf.NAMES[pose]}", 17)
    label(sheet, (sheet.width - 8, 6), "3× and game size", 14, "ra")
    for i, obj in enumerate(objects):
        x = 59 + i * col
        label(sheet, (x + col // 2, 35), NAMES[obj - 300], 14, "ma")
        for j, look in enumerate(LOOKS):
            y = 60 + j * row
            if i == 0:
                label(sheet, (6, y + row // 2), look, 13)
            tile = pictures[obj, pose, look]
            sheet.paste(tile.resize((TILE[0] * scale, TILE[1] * scale), Image.Resampling.NEAREST), (x, y))
            sheet.paste(tile, (x + TILE[0] * scale + 2, y + TILE[1] * (scale - 1)))
    return sheet


def render(game_dir, previous_checkout, output):
    previous = former(game_dir, previous_checkout, __file__)
    pictures = dict(tiles(previous, capture(game_dir)))
    output.mkdir(parents=True, exist_ok=True)
    sheet = lineup(pictures)
    sheet.save(output / "gladiator-leather-game-size.png", optimize=True)
    ImageOps.grayscale(sheet).save(output / "gladiator-leather-greyscale.png", optimize=True)
    # Show the human pilot as a still so the strap and clasp can be inspected without pausing a GIF.
    front = motion(pictures, (300, 301), 0)
    side = motion(pictures, (300, 301), 2)
    pilot = Image.new("RGB", (front.width + side.width, front.height))
    pilot.paste(front)
    pilot.paste(ImageOps.grayscale(side), (front.width, 0))
    pilot.save(output / "gladiator-leather-humans.png", optimize=True)
    for name, objects in (("humans-dwarves", range(300, 304)), ("elves-half-elves", range(304, 308)),
                          ("half-giants-halflings", range(308, 312)), ("mul-thri-kreen", range(312, 314))):
        loop([motion(pictures, objects, pose) for pose in range(29)], output / f"gladiator-leather-{name}.gif")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--previous-checkout", type=Path, required=True)
    args = parser.parse_args()
    render(args.game_dir, args.previous_checkout, args.output)
