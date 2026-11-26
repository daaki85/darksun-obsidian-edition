"""Compare original map art, reconstructed skin and two fitted outfits on the same floor.

python prototypes/bodyreview.py GAME_DIR OUTPUT_DIR
"""
import argparse
from pathlib import Path
from zipfile import ZipFile

from PIL import Image

import halfelfstudy as half
from elfreview import dwarf, elf, label, loop
from wornreview import Atlas

# Left and right columns in the review.
FIGURES = ((2095, 2099), (2055, 2053), (2061, 2059), (half.FIGURES[1], half.FIGURES[0]))
RACES = ("Human", "Dwarf", "Elf", "Half-elf")


def body_tile(study, key, pose):
    if key in half.FIGURES:
        return study.tile(key, pose, "Body base", 1)
    combat, frame = divmod(pose, 15)
    source = study.game.fr(key + combat, frame)
    bottom = 0
    if key in half.co.ELVES:
        rows = elf.render(study.game, key, pose, "Body base")
        pad = bottom = elf.PAD
    elif key in half.co.DWARVES:
        layers = {name: {} for name in ("head", "cloak", "regions")}
        indexed = dwarf.draw(study.game, key, pose, None, layers=layers)
        pixels = indexed.tobytes()
        rows = [[None if p == 255 else p for p in pixels[i:i + indexed.width]]
                for i in range(0, len(pixels), indexed.width)]
        pad = bottom = (indexed.width - len(source[0])) // 2
    else:
        if key == 2099:
            paint = study.body[pose]
        else:
            archive = Path(half.co.__file__).with_name("human_outfit_layers.zip")
            tag = "combat" if combat else "walk"
            with ZipFile(archive) as layers:
                paint = half.art.decode_frame(layers.read(f"Study/{tag}-body"), frame)[2]
        pad = half.MARGIN
        rows = half.co.Frame(paint, {}).canvas(source, pad)
    return elf.placed_tile(study.game, rows, study.floor, 1, pad, pad, bottom)


def review(game_dir, output):
    study, atlas = half.Study(game_dir), Atlas(game_dir)
    objects = {model: obj for obj, model in half.co.MODELS.items()}
    frames = []
    for pose, name in enumerate(dwarf.NAMES):
        page = Image.new("RGB", (904, 672), dwarf.PAPER)
        label(page, (10, 7), "Body and outfit detail on the arena floor", 20)
        label(page, (894, 11), f"{pose:02}   {name}", 15, "ra")
        for row, pair in enumerate(FIGURES):
            for side, key in enumerate(pair):
                left, top = side * 450 + 8, row * 156 + 41
                sex = "woman" if side else "man"
                label(page, (left, top), f"{RACES[row]} {sex}", 14)
                combat, frame = divmod(pose, 15)
                original = study.game.fig(key).rows(combat, frame)
                tiles = [elf.placed_tile(study.game, original, study.floor, 1, 0, 0, 0),
                         body_tile(study, key, pose)]
                for role in ("Gladiator", "Fighter"):
                    tile = (study.tile(key, pose, role, 1) if key in half.FIGURES else
                            atlas.tile(objects[key], pose, role, "Class colors", 1))
                    tiles.append(tile)
                for col, (caption, tile) in enumerate(zip(("Original", "Body", "Gladiator", "Fighter"), tiles)):
                    x = left + col * 106
                    page.paste(tile.resize((104, 88), Image.Resampling.NEAREST), (x, top + 19))
                    page.paste(tile, (x, top + 108))
                    label(page, (x + 53, top + 125), caption, 10)
        frames.append(page)
    output.mkdir(parents=True, exist_ok=True)
    loop(frames, output / "body-texture.gif")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    review(args.game_dir, args.output_dir)
