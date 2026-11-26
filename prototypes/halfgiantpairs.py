"""Render both half-giants' legal pairs beside their parent singles."""
import argparse
from pathlib import Path

from PIL import Image

import outfits
from elfreview import TERRAIN, dwarf, elf, label, loop
from halfgiantstudy import MODELS, PAIRS, study_rows
from outfitdetail import reference_folds


def render(game_dir, output):
    game = outfits.Game(game_dir)
    texture = reference_folds(game)["linen"]
    floor = Image.open(TERRAIN).convert("RGB").crop((45, 144, 99, 195))
    frames = []
    sheets = {model: Image.new("RGB", (3*560, 10*138), dwarf.PAPER) for model in MODELS}
    output.mkdir(parents=True, exist_ok=True)
    for pose, name in enumerate(dwarf.NAMES):
        page = Image.new("RGB", (812, 524), dwarf.PAPER)
        label(page, (14, 7), "Half-giant multiclasses", 20)
        label(page, (798, 10), f"{pose:02}   {name}", 15, "ra")
        for i, model in enumerate(MODELS):
            rows = study_rows(game, model, pose, texture, pairs=True)
            y = 64+i*183
            label(page, (9, y+41), ("Man", "Woman")[i], 13)
            for j, pair in enumerate(PAIRS):
                x = 72+j*148
                if i == 0:
                    label(page, (x+54, 40), pair, 14, "ma")
                native = elf.placed_tile(game, rows[pair], floor, 1, 0, 0, 0)
                tile = native.resize((108, 102), Image.Resampling.NEAREST)
                page.paste(tile, (x, y))
                # Put the pair between its parents on a single native-size ground line.
                first, second = pair.split("/")
                for n, k in enumerate((first, pair, second)):
                    small = elf.placed_tile(game, rows[k], floor, 1, 0, 0, 0)
                    # Crop the panel's blank margins to keep columns separate.
                    page.paste(small.crop((4, 0, 50, 51)), (x-15+46*n, y+106))
                sheet = sheets[model]
                sx = (pose % 3)*560+j*112
                sy = (pose//3)*138
                if j == 0:
                    label(sheet, (sx+2, sy+1), f"{pose:02}   {name}", 14)
                label(sheet, (sx+2, sy+19), pair, 11)
                sheet.paste(tile, (sx, sy+35))
        label(page, (14, 415), "Small trios read left to right in the order of the class names, with the pair in the middle.", 14)
        for j, (npc, caption) in enumerate(((1252, "Retail Warrior"), (1563, "Retail Priest"), (630, "Retail Thief"))):
            pic = npc+pose//15
            frame = pose % 15
            if frame >= game.count(pic):
                pic, frame = npc, 0
                caption += " (idle)"
            ref = elf.placed_tile(game, game.fr(pic, frame), floor, 1, 0, 0, 0)
            x = 114+j*235
            page.paste(ref, (x, 452))
            label(page, (x+60, 470), caption, 13)
        frames.append(page)
    loop(frames, output/"half-giant-pairs.gif")
    for model, sheet in sheets.items():
        sex = "man" if model == 2072 else "woman"
        sheet.save(output/f"half-giant-{sex}-pairs.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    render(args.game_dir, args.output)
