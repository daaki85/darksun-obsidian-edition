"""Compare the male half-elf's reconstructed skin in every pose on the game floor."""
import argparse
from pathlib import Path

from PIL import Image

from bodyreview import body_tile
from elfreview import dwarf, elf, label, loop
from halfelfstudy import FIGURES, Study


def sample(page, tile, x, y, scale):
    page.paste(tile.resize((tile.width*scale, tile.height*scale), Image.Resampling.NEAREST), (x, y))
    page.paste(tile, (x+tile.width*(scale-1)//2, y+tile.height*scale+3))


def render(game_dir, out):
    study = Study(game_dir)
    key = FIGURES[1]
    frames = []
    examples = (0, 8, 12, 19)
    still = Image.new("RGB", (672, 42+len(examples)*239), dwarf.PAPER)
    label(still, (10, 8), "Male half-elf body fitting", 20)
    sheet = Image.new("RGB", (112+6*120, 55+29*86), dwarf.PAPER)
    label(sheet, (9, 6), "Male half-elf through all 29 poses", 19)
    names = ("Retail elf", "Previous body", "Revised body", "Human body", "Gladiator", "Druid")
    for i, name in enumerate(names):
        label(sheet, (172+120*i, 33), name, 14, "ma")
    for pose, title in enumerate(dwarf.NAMES):
        rows, pad = study.registered.rows(key, pose, "Body base")
        previous = elf.placed_tile(study.game, rows, study.floor, 1, pad, pad, 0)
        cb, f = divmod(pose, 15)
        retail = elf.placed_tile(study.game, study.game.fr(2061+cb, f), study.floor, 1, 0, 0, 0)
        tiles = (retail, previous, study.tile(key, pose, "Body base", 1), body_tile(study, 2095, pose),
                 study.tile(key, pose, "Gladiator", 1), study.tile(key, pose, "Druid", 1))
        page = Image.new("RGB", (984, 255), dwarf.PAPER)
        label(page, (12, 8), "Male half-elf body fitting", 20)
        label(page, (972, 8), f"{pose:02}   {title}", 17, "ra")
        label(sheet, (6, 81+86*pose), f"{pose:02}  {title}", 12)
        for i, (name, tile) in enumerate(zip(names, tiles)):
            label(page, (82+i*164, 42), name, 15, "ma")
            sample(page, tile, 4+164*i, 66, 3)
            sheet.paste(tile.crop((2, 4, 50, 44)).resize((96,80), Image.Resampling.NEAREST),
                        (124+120*i, 55+pose*86))
        frames.append(page)
        if pose in examples:
            y = 42+examples.index(pose)*239
            label(still, (11, y), f"{pose:02}   {title}", 16)
            for i, column in enumerate((1, 2, 4, 5)):
                tile = tiles[column]
                label(still, (84+168*i, y+23), names[column], 14, "ma")
                sample(still, tile, 6+168*i, y+45, 3)
    out.mkdir(exist_ok=True, parents=True)
    still.save(out/"half-elf-man-body.png")
    sheet.save(out/"half-elf-man-body-poses.png")
    loop(frames, out/"half-elf-man-body.gif")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    render(args.game_dir, args.output_dir)
