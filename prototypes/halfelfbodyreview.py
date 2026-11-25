"""Compare the male half-elf's reconstructed skin in every pose on the game floor."""
import argparse
from pathlib import Path

from PIL import Image

from bodyreview import body_tile
from elfreview import dwarf, elf, label, loop
from halfelfstudy import FIGURES, NEW_SINGLES, ROLES, Study
from wornreview import Atlas


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


def garment_review(game_dir, out, previous_sheet):
    """Compare against the men's singles sheet at 1ec61d3, on its original tile."""
    study, atlas = Study(game_dir), Atlas(game_dir)
    atlas.floor = study.floor
    key = FIGURES[1]
    previous = Image.open(previous_sheet).convert("RGB")
    roles = ROLES[2:]+NEW_SINGLES
    frames = []
    chosen = (0, 4, 12)
    still = Image.new("RGB", (900, 35+214*2*len(chosen)), dwarf.PAPER)
    label(still, (12, 7), "Male half-elf garment fitting", 18)
    for pose, title in enumerate(dwarf.NAMES):
        page = Image.new("RGB", (900, 474), dwarf.PAPER)
        label(page, (12, 7), f"Male half-elf garment fitting   /   {pose:02}   {title}", 18)
        for i, role in enumerate(("Druid", "Preserver")):
            y = 35+i*214
            label(page, (12, y), role, 16)
            x0 = 109+120*roles.index(role)
            y0 = 45+80*pose
            old = previous.crop((x0, y0, x0+96, y0+80)).resize((48, 40), Image.Resampling.NEAREST)
            view = (2, 4, 50, 44)
            if role == "Druid":
                peer = study.tile(FIGURES[0], pose, role, 1)
                reference = "Half-elf woman"
            else:
                peer = atlas.tile(304, pose, role, "Class colors", 1)
                reference = "Elf Preserver"
            retail = 2099 if role == "Druid" else 724
            action = pose if pose%15 < study.game.count(retail+pose//15) else 0
            retail_name = "SL woman" if role == "Druid" else "SL mage"
            if action != pose:
                retail_name += " (idle)"
            tiles = (study.tile(key, pose, "Body base", 1).crop(view), old,
                     study.tile(key, pose, role, 1).crop(view), peer.crop(view),
                     atlas.tile(retail, action, "", "", 1).crop(view))
            for j, (name, tile) in enumerate(zip(("Body base", "Previous", "Refitted", reference, retail_name), tiles)):
                label(page, (90+180*j, y+21), name, 14, "ma")
                sample(page, tile, 18+180*j, y+42, 3)
        frames.append(page)
        if pose in chosen:
            y = 35+chosen.index(pose)*428
            still.paste(page.crop((0,35,900,463)), (0,y))
            label(still, (888, y), f"{pose:02}   {title}", 15, "ra")
    still.save(out/"half-elf-man-garment-fit.png")
    loop(frames, out/"half-elf-man-garment-fit.gif")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--previous-singles", type=Path, help="male singles sheet from 1ec61d3")
    args = parser.parse_args()
    render(args.game_dir, args.output_dir)
    if args.previous_singles:
        garment_review(args.game_dir, args.output_dir, args.previous_singles)
