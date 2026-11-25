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


def druid_contact(name, pose, samples, previous, reference):
    page = Image.new("RGB", (830, 303), dwarf.PAPER)
    label(page, (12, 8), "Mul Druid  /  mantle attachment", 20)
    label(page, (818, 10), f"{pose:02}   {name}", 16, "ra")
    # The two Mul fittings use the same native ground anchor and sand tile.
    x = 123+110*(singles.fit.ROLES+singles.NEW).index("Druid")
    y = 44+105*pose
    old = previous.crop((x, y, x+108, y+102)).resize((54, 51), Image.Resampling.NEAREST)
    sand, paving = samples
    tiles = (("Cleaned body", sand[1], paving[1]), ("Previous Mul", old, old),
             ("Refitted Mul", sand[3], paving[3]), ("Human Druid", sand[4], paving[4]),
             ("SL "+reference, sand[5], paving[5]))
    for j, (caption, large, small) in enumerate(tiles):
        left = 8+164*j
        label(page, (left+79, 43), caption, 14, "ma")
        crop = large.crop((7, 12, 47, 51))
        page.paste(crop.resize((160, 156), Image.Resampling.NEAREST), (left, 65))
        page.paste(small, (left+53, 223))
    label(page, (10, 278), "4× on sand above, game size below. Previous fitting from bf80eb5.", 14)
    return page


def front_review(atlas, folds, sand, output, previous):
    poses = (0, 3, 4, 5, 6, 15, 16, 17, 24)
    poses_sheet = Image.open(previous).convert("RGB")
    roles = singles.fit.ROLES + singles.NEW
    frames = {}
    strip = Image.new("RGB", (740, 494), dwarf.PAPER)
    label(strip, (12, 8), "Mul front walk", 21)
    details = Image.new("RGB", (658, 517), dwarf.PAPER)
    label(details, (10, 8), "Mul front walk details", 20)
    examples = {("Druid", 5): 0, ("Druid", 6): 1, ("Thief", 5): 2}
    for (role, pose), column in examples.items():
        label(details, (183+188*column, 44), f"{role} · step {pose-2}", 15, "ma")
    label(details, (10, 152), "Previous", 16)
    label(details, (10, 380), "Revised", 16)
    for column, name in enumerate(("Idle", "Step 1", "Step 2", "Step 3", "Step 4")):
        label(strip, (180+124*column, 42), name, 15, "ma")
    atlas.floor = sand
    for pose in poses:
        rows = singles.draw(atlas.game, pose, folds)
        page = Image.new("RGB", (737, 410), dwarf.PAPER)
        label(page, (10, 8), "Mul Druid and Thief", 20)
        label(page, (725, 10), f"{pose:02}  {dwarf.NAMES[pose]}", 16, "ra")
        for j, title in enumerate(("Body", "Previous Mul", "Revised Mul", "Human", "Retail Thief")):
            label(page, (160+127*j, 47), title, 15, "ma")
        for index, role in enumerate(("Druid", "Thief")):
            left = 123+110*roles.index(role)
            top = 44+105*pose
            old = poses_sheet.crop((left, top, left+108, top+102)).resize((54, 51), Image.Resampling.NEAREST)
            body, revised = (elf.placed_tile(atlas.game, rows[name], sand, 1, 0, 0, 0)
                             for name in ("Body base", role))
            npc_pose = pose if pose%15 < atlas.game.count(630+pose//15) else 0
            tiles = (body, old, revised, atlas.tile(300, pose, role, "Class colors", 1),
                     atlas.tile(630, npc_pose, "", "", 1))
            y = 69+168*index
            label(page, (10, y+41), role, 18)
            for j, tile in enumerate(tiles):
                x = 100+127*j
                crop = tile.crop((7, 12, 47, 51))
                page.paste(crop.resize((120, 117), Image.Resampling.NEAREST), (x, y))
                page.paste(crop, (x+40, y+120))
            if (role, pose) in examples:
                column = examples[role, pose]
                for j, tile in enumerate((old, revised)):
                    crop = tile.crop((12, 15, 42, 51))
                    details.paste(crop.resize((180, 216), Image.Resampling.NEAREST),
                                  (94+188*column, 64+228*j))
            if pose in poses[:5]:
                for row, tile in enumerate((old, revised)):
                    y = 64+index*215+row*104
                    label(strip, (12, y+28), role, 16)
                    label(strip, (12, y+52), ("Previous", "Revised")[row], 14)
                    crop = tile.crop((9, 17, 47, 51))
                    strip.paste(crop.resize((114, 102), Image.Resampling.NEAREST),
                                (124+124*poses.index(pose), y))
        frames[pose] = page.quantize(256, dither=Image.Dither.NONE)
    details.save(output/"mul-front-details.png")
    strip.save(output/"mul-front-walk.png")
    cycle = (0, 3, 4, 5, 6, 3, 4, 5, 6, 0, 15, 16, 17, 0, 24)
    frames[0].save(output/"mul-front-fit.gif", save_all=True, loop=0, disposal=1,
                   append_images=[frames[p] for p in cycle[1:]],
                   duration=[800 if p in (0, 24) else 340 if p >= 15 else 220 for p in cycle])


def render(game_dir, output, previous, previous_druid=None, previous_front=None):
    atlas = Atlas(game_dir)
    game = atlas.game
    folds = reference_folds(game)
    sand = Image.open(TERRAIN).convert("RGB").crop((39, 130, 93, 181))
    stone = Image.open(TERRAIN.with_name("2026-11-09-figures-all-gone.png")).convert("RGB").crop((158, 21, 212, 72))
    roles = singles.fit.ROLES+singles.NEW
    still = page("Mul single classes  /  fitting details", 3)
    frames = []
    druid_frames = []
    druid_sheet = Image.open(previous_druid).convert("RGB") if previous_druid else None
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
                if role == "Druid" and druid_sheet is not None:
                    druid_frames.append(druid_contact(name, pose, samples, druid_sheet, ref_name))
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
    if previous_front is not None:
        front_review(atlas, folds, sand, output, previous_front)
    if druid_frames:
        druid_frames[22].save(output/"mul-druid-side-strike.png")
        loop(druid_frames, output/"mul-druid-contact.gif")
    still.save(output/"mul-fitting-details.png")
    loop(frames, output/"mul-fitting-review.gif")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("previous", type=Path, help="mul-singles-poses.png at 6363eea")
    parser.add_argument("--previous-druid", type=Path, help="mul-singles-poses.png at bf80eb5")
    parser.add_argument("--previous-front", type=Path, help="mul-singles-poses.png at b8447ce")
    args = parser.parse_args()
    render(args.game_dir, args.output, args.previous, args.previous_druid, args.previous_front)
