"""Render fitted half-elf garments and equipment through the Loader's native picture builder.

python prototypes/halfelfloaderreview.py GAME_DIR OUTPUT_DIR
"""
import argparse
from pathlib import Path

from PIL import ImageDraw

from equipmentfitreview import slot_loadouts
from magicgearitems import loadouts
from magicgearreview import GalleryPalette, NPC_NAMES, timeline, write_loop
from namedrobereview import stamp
from platefitreview import shared_crop
from wornreview import Atlas, dwarf, sprites


CASES = (("Class colors", "Class outfit"), ("Warden", "Warden’s Plate"), ("Ashen Robe", "Ashen Robe"),
         ("Magic cloak", "Elven cloak"), ("Sword and shield", "Sword + shield"),
         ("Bow and quiver", "Bow + arrows"), (None, "Shattered Lands"))
ROLES = (("Cleric/Preserver", 1563), ("Druid", 724), ("Thief", 630))
FIGURES = ((306, "man"), (307, "woman"))
STILL_POSES = ((0, 13, 8), (8, 22, 16))


def fixture(game_dir):
    atlas = Atlas(game_dir)
    atlas.gear.update(loadouts(atlas))
    atlas.gear["Warden"] = slot_loadouts(atlas)["All three"]
    palette = GalleryPalette(atlas, atlas.floor)
    images = {}
    for obj, _ in FIGURES:
        for role, ref in ROLES:
            for combat in (False, True):
                pad, _ = sprites.room(combat)
                if atlas.sequence(obj, combat, role, "Class colors") == atlas.sequence(obj, combat, None, "Class colors"):
                    raise ValueError(f"Missing Loader outfit for {obj} {role}")
                for case, _ in CASES:
                    if case is None:
                        source = [atlas.game.fr(ref + combat, f) for f in range(atlas.game.count(ref + combat))]
                    else:
                        source = atlas.sequence(obj, combat, role, case)
                    for frame, rows in enumerate(source):
                        tile = palette.tile(rows, pad if case else 0)
                        images[obj, role, 15*combat + frame, case] = tile
    return palette, images, shared_crop(images.values(), palette.floor)


def board(palette, images, crop, subjects, title, scale):
    width, height = crop[2]-crop[0], crop[3]-crop[1]
    col = max(123, width*scale+6)
    row = height*(scale+1)+31
    result = palette.board((14+len(CASES)*col, 72+row*len(subjects)))
    palette.text(result, (8, 5), title, 19)
    palette.text(result, (result.width-8, 9), f"{scale}× and game size", 14, "ra", muted=True)
    for n, (_, label) in enumerate(CASES):
        palette.text(result, (7+col*n+col//2, 42), label, 14, "ma")
    for i, (obj, who, role, ref, pose) in enumerate(subjects):
        y = 65+i*row
        ImageDraw.Draw(result).line((8,y,result.width-8,y), fill=palette.text_ramp[1])
        palette.text(result, (8,y+3), f"Half-elf {who}   ·   {role}", 14)
        palette.text(result, (result.width-8,y+3), f"{pose:02}   {dwarf.NAMES[pose]}   ·   Retail {NPC_NAMES[ref]}",
                     13, "ra", muted=True)
        for n, (case, _) in enumerate(CASES):
            tile = images.get((obj, role, pose, case))
            center = 7+col*n+col//2
            if tile is None:
                palette.text(result, (center,y+row//2), "No matching pose", 12, "ma", muted=True)
            else:
                stamp(result, tile, crop, center, y+24, scale)
    return result


def render(game_dir, output):
    palette, images, crop = fixture(game_dir)
    output.mkdir(parents=True, exist_ok=True)
    subjects = []
    for index, (obj, who) in enumerate(FIGURES):
        title = f"Half-elf {who}   /   Fitted equipment"
        boards = []
        for pose in range(29):
            rows = [(obj, who, role, ref, pose) for role, ref in ROLES]
            boards.append(board(palette, images, crop, rows, title, 3))
        write_loop(palette, boards, timeline(), output/f"half-elf-loader-{who}.gif")
        for (role, ref), pose in zip(ROLES, STILL_POSES[index]):
            subjects.append((obj, who, role, ref, pose))
    cells = board(palette, images, crop, subjects, "Half-elf outfits and equipment", 2)
    cells.convert("RGB").save(output/"half-elf-loader-gear.png", optimize=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    render(args.game_dir, args.output_dir)
