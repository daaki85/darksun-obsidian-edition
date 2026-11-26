"""Compare the detail pass with the three pose sheets saved from eaaf23e."""
import argparse
from pathlib import Path

from PIL import Image

import halfelfstudy as halfelf
import halflingmultis
import mulmultis as mul
from elfreview import TERRAIN, co, dwarf, elf, label, loop
from outfitdetail import reference_folds
from wornreview import Atlas


SINGLES = mul.fit.ROLES[2:] + mul.singles.NEW
MULTIS = tuple(role for roles in mul.GROUPS.values() for role in roles)
# Sample the view that shows the distinguishing material or fastening.
POSES = (3, 8, 12, 5, 13, 8, 8, 11, 3, 12, 6, 1, 4, 13, 8, 7, 5, 12)
NPCS = {"Cleric": (1563, "Priest"), "Thief": (630, "Thief")}


def crop_cell(sheet, x, y, w, h):
    return sheet.crop((x, y, x+2*w, y+2*h)).resize((w, h), Image.Resampling.NEAREST)


def sample(image, tile, x, y, title):
    label(image, (x+66, y), title, 12, "ma")
    image.paste(tile.resize((tile.width*3, tile.height*3), Image.Resampling.NEAREST),
                (x+66-tile.width*3//2, y+19))
    image.paste(tile, (x+66-tile.width//2, y+22+tile.height*3))


def render(game_dir, previous, output):
    atlas = Atlas(game_dir)
    game = atlas.game
    study = halfelf.Study(game_dir)
    swatches = reference_folds(game)
    male, female = halfelf.FIGURES[1], halfelf.FIGURES[0]
    singles = Image.open(previous/"mul-singles-poses.png").convert("RGB")
    multis = Image.open(previous/"mul-multiclass-poses.png").convert("RGB")
    old_druid = Image.open(previous/"half-elf-singles-male-poses.png").convert("RGB")
    output.mkdir(exist_ok=True, parents=True)

    # Both men share the same camera and floor as the original Druid sheet.
    atlas.floor = study.floor
    still = Image.new("RGB", (567, 43+4*207), dwarf.PAPER)
    label(still, (12, 6), "Half-elf Druid fitting", 20)
    frames = []
    examples = (0, 5, 12, 16)
    for pose, title in enumerate(dwarf.NAMES):
        x = 109+120*(halfelf.ROLES[2:]+halfelf.NEW_SINGLES).index("Druid")
        before = crop_cell(old_druid, x, 45+pose*80, 48, 40)
        view = (2, 4, 50, 44)
        tiles = (before, study.tile(male, pose, "Druid", 1).crop(view),
                 study.tile(female, pose, "Druid", 1).crop(view),
                 atlas.tile(300, pose, "Druid", "Class colors", 1).crop(view))
        page = Image.new("RGB", (594, 232), dwarf.PAPER)
        label(page, (9, 8), f"Half-elf Druid   /   {pose:02}   {title}", 18)
        for j, (tile, name) in enumerate(zip(tiles, ("Previous man", "Revised man", "Half-elf woman", "Human man"))):
            sample(page, tile, 7+147*j, 38, name)
        frames.append(page)
        if pose in examples:
            y = 40+examples.index(pose)*207
            label(still, (9, y), f"{pose:02}   {title}", 14)
            for j, (tile, name) in enumerate(zip(tiles[:3], ("Previous man", "Revised man", "Half-elf woman"))):
                sample(still, tile, 21+j*186, y+20, name)
    still.save(output/"half-elf-druid-fitting.png")
    loop(frames, output/"half-elf-druid-fitting.gif")

    sand = Image.open(TERRAIN).convert("RGB").crop((39, 130, 93, 181))
    atlas.floor = study.floor = sand
    view = (5, 12, 49, 51)
    poses = dict(zip(SINGLES+MULTIS, POSES, strict=True))
    for group, roles in (("singles", SINGLES), ("pairs", MULTIS[:9]), ("triples", MULTIS[9:])):
        sheet = Image.new("RGB", (724, 40+len(roles)*204), dwarf.PAPER)
        label(sheet, (10, 6), f"Mul {group} on the arena floor", 19)
        for i, role in enumerate(roles):
            pose = poses[role]
            if role in SINGLES:
                x = 123+110*(SINGLES.index(role)+2)
                before = crop_cell(singles, x, 44+pose*105, 54, 51).crop(view)
            else:
                before = crop_cell(multis, 134+88*MULTIS.index(role), 88+pose*80, 44, 39)
            current = mul.draw(game, pose, swatches)[role]
            tile = elf.placed_tile(game, current, sand, 1, 0, 0, 0).crop(view)
            if role in SINGLES:
                other = "Human man"
                human_role = "Priest" if role == "Cleric" else role
                peer = atlas.tile(300, pose, human_role, "Class colors", 1)
            elif role in co.DWARF_ROLES.values():
                other, peer = "Dwarf man", atlas.tile(302, pose, role, "Class colors", 1)
            elif role in co.ELF_ROLES.values():
                other, peer = "Elf man", atlas.tile(304, pose, role, "Class colors", 1)
            elif role in halflingmultis.GROUPS["druid"]:
                rows = halflingmultis.draw(game, pose, swatches)[2068][role]
                other, peer = "Halfling man", elf.placed_tile(game, rows, sand, 1, 0, 0, 0)
            else:
                other, peer = "Half-elf woman", study.tile(female, pose, role, 1)
            npc, name = next((value for key, value in NPCS.items() if key in role), (1252, "Warrior"))
            ref = pose if pose%15 < game.count(npc+pose//15) else 0
            retail = atlas.tile(npc, ref, "", "", 1).crop(view)
            y = 40+i*204
            label(sheet, (10, y), f"{role}    /    {pose:02}   {dwarf.NAMES[pose]}", 15)
            tiles = (before, tile, study.tile(male, pose, role, 1).crop(view), peer.crop(view), retail)
            names = ("Previous Mul", "Revised Mul", "Half-elf man", other, "SL "+name+(" (idle)" if ref!=pose else ""))
            for j, (image, caption) in enumerate(zip(tiles, names)):
                sample(sheet, image, 8+143*j, y+21, caption)
        sheet.save(output/f"mul-detail-{group}.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("game_dir", "previous", "output"):
        parser.add_argument(arg, type=Path)
    args = parser.parse_args()
    render(args.game_dir, args.previous, args.output)
