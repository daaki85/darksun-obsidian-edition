"""Review each Mul single against its previous fitting, human parent and retail material."""
import argparse
from pathlib import Path

from PIL import Image

import mulsingles as singles
from elfreview import TERRAIN, dwarf, elf, label, loop
from outfitdetail import reference_folds
from wornreview import Atlas


# Each still isolates a different fit question. The loop uses every pose.
CASES = (
    ("Gladiator", "Gladiator", 1252, "Warrior", 8),
    ("Fighter", "Warrior", 1252, "Warrior", 12),
    ("Cleric", "Priest", 1563, "Priest", 13),
    ("Druid", "Druid", 630, "Thief", 0),
    ("Psionicist", "Psionicist", 724, "Mage", 24),
    ("Thief", "Thief", 630, "Thief", 8),
)
COLUMNS = ("Retail Mul", "Cleaned body", "Previous Mul", "Revised Mul", "Human", "Retail material")


def page(title, scale):
    width = 54*scale+4
    height = 51*scale+54
    im = Image.new("RGB", (131+6*width, 82+len(CASES)*height), dwarf.PAPER)
    label(im, (10, 7), title, 20)
    label(im, (10, 36), "Large figures on sand. Game size on paving below each figure, with the previous fitting on sand.", 13)
    for j, name in enumerate(COLUMNS):
        label(im, (128+(j+.5)*width, 60), name, 15, "ma")
    return im


def render(game_dir, output, previous):
    atlas = Atlas(game_dir)
    game = atlas.game
    folds = reference_folds(game)
    sand = Image.open(TERRAIN).convert("RGB").crop((39, 130, 93, 181))
    stone = Image.open(TERRAIN.with_name("2026-11-09-figures-all-gone.png")).convert("RGB").crop((158, 21, 212, 72))
    roles = singles.fit.ROLES+singles.NEW
    still = page("Mul single classes  /  fitting details", 3)
    frames = []
    with Image.open(previous) as old:
        for pose, name in enumerate(dwarf.NAMES):
            frame = page(f"Mul single classes  /  {pose:02}   {name}", 2)
            outfits = singles.draw(game, pose, folds)
            for i, (role, parent, npc, npc_name, example) in enumerate(CASES):
                x = 123+110*roles.index(role)
                y = 44+105*pose
                before = old.crop((x, y, x+108, y+102)).resize((54, 51), Image.Resampling.NEAREST)
                ref_pose = pose if pose%15 < game.count(npc+pose//15) else 0
                ref_name = npc_name+" (idle)" if ref_pose != pose else npc_name
                samples = []
                for ground in (sand, stone):
                    atlas.floor = ground
                    def tile(key):
                        return elf.placed_tile(game, outfits[key], ground, 1, 0, 0, 0)
                    samples.append((tile("Original"), tile("Body base"), before, tile(role),
                                    atlas.tile(300, pose, parent, "Class colors", 1),
                                    atlas.tile(npc, ref_pose, "", "", 1)))
                displays = [(frame, 2)]
                if pose == example:
                    displays.append((still, 3))
                for im, scale in displays:
                    width = 54*scale+4
                    top = 80+i*(51*scale+54)
                    label(im, (8, top+15), role, 16)
                    label(im, (8, top+41), name, 13)
                    label(im, (8, top+63), f"SL {ref_name}", 12)
                    for j, (large, small) in enumerate(zip(*samples)):
                        left = 129+j*width
                        im.paste(large.resize((54*scale, 51*scale), Image.Resampling.NEAREST), (left, top))
                        im.paste(small, (left+(width-54)//2, top+51*scale+1))
            frames.append(frame)
    output.mkdir(exist_ok=True, parents=True)
    still.save(output/"mul-fitting-details.png")
    loop(frames, output/"mul-fitting-review.gif")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("previous", type=Path, help="mul-singles-poses.png at 6363eea")
    args = parser.parse_args()
    render(args.game_dir, args.output, args.previous)
