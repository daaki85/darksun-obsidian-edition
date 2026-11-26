"""Animate magical leather and bone dyes on the approved, unregistered outfits.

python prototypes/studymagicreview.py GAME_DIR OUTPUT_DIR

These are material previews on the fitted study fabric. The actual fitted item
slots are only exercised by the companion Loader gallery.
"""
import argparse
from pathlib import Path

from PIL import Image

from studyarmordetail import (Atlas, NAMES, dwarf, he, hg, landmarks, sg, study_rows,
                            study_surface)
from wornreview import TERRAIN
from magicgearitems import loadouts
from magicgearreview import GalleryPalette, NPC_NAMES, TICK_MS, timeline

GROUPS = {
    "half-elves": ((306, "Druid"), (307, "Cleric/Preserver")),
    "half-giants": ((308, "Cleric/Fighter"), (309, "Psionicist")),
    "halflings-mul": ((310, "Cleric/Thief"), (311, "Fighter/Psionicist"), (312, "Druid/Fighter")),
}
COLUMNS = ("Class colors", "Leather", "Magical leather", "Bone", "Magical bone", "Retail reference")
REFERENCES = {306: 1252, 307: 724, 308: 1563, 309: 724, 310: 1563, 311: 1252, 312: 1252}
COL_WIDTH, ROW_HEIGHT, LEFT, TOP = 158, 209, 135, 76


def appearances(atlas, study, swatches, materials, obj, role, pose):
    rows = study_rows(obj, pose, atlas.game, study, swatches)
    source = rows[role]
    cuts = landmarks(obj, pose, atlas.game)
    _, surface, additions, covered, signature = study_surface(atlas.game, obj, pose, rows, role, cuts)
    # Both named samples are chest pieces. Use the pose's moving waist to
    # keep the estimated chest dye off kilts, shin guards and lower robe.
    _, waist, _, _, top = cuts
    surface = {(x, y) for x, y in surface
               if (len(source)-1-y if pose == 28 else y-top) < waist}
    variants = [source]
    for shades, glow in materials:
        dyed = [row[:] for row in source]
        sg.dye_garment(dyed, surface, shades, 0, source)
        sg.retain_cloth_shadows(dyed, surface, 0, source)
        enchanted = [row[:] for row in dyed]
        sg.shine_armour(enchanted, surface, sg.ARMOUR_CHEST, None, 0, glow)
        differences = {(x, y) for y, row in enumerate(enchanted) for x, c in enumerate(row)
                       if c != source[y][x]}
        glints = {(x, y) for y, row in enumerate(enchanted) for x, c in enumerate(row)
                  if c != dyed[y][x]}
        assert differences <= surface and not differences & (additions | covered)
        assert not signature or signature - differences
        assert bool(glints) == bool(surface) and all(enchanted[y][x] in glow for x, y in glints)
        variants.extend((dyed, enchanted))
    return variants, cuts


def materials_from(atlas):
    gear = loadouts(atlas)
    materials = []
    for name in ("Magic leather", "Magic bone"):
        _, armor = gear[name]
        # Use the item's actual dye and shine for the exposed study garment.
        # Both cases equip one item on the chest.
        dyes = {(sg.ARMOUR[item & (sg.MAGIC_ARMOUR-1)][1],
                 sg.GLOWS[(item >> sg.GLOW_SHIFT) % len(sg.GLOWS)]) for item in armor}
        assert len(armor) == 1 and armor[0] & sg.MAGIC_ARMOUR, name
        assert sg.ARMOUR[armor[0] & (sg.MAGIC_ARMOUR-1)][0] == sg.ARMOUR_CHEST, name
        materials.append(dyes.pop())
    return materials


def render(game_dir, output):
    output.mkdir(parents=True, exist_ok=True)
    atlas = Atlas(game_dir)
    # The half-giants raise the bow five pixels above the regular 44-pixel tile.
    # Extend the tile upward while keeping the same floor and ground line.
    with Image.open(TERRAIN) as arena:
        floor = arena.convert("RGB").crop((50, 142, 102, 194))
    study = he.Study(game_dir)
    swatches = hg.reference_folds(atlas.game)
    materials = materials_from(atlas)
    palette = GalleryPalette(atlas, floor)
    for name, subjects in GROUPS.items():
        template = palette.board((LEFT + len(COLUMNS)*COL_WIDTH, TOP + len(subjects)*ROW_HEIGHT))
        palette.text(template, (10, 7), "Class outfit material study", 19)
        palette.text(template, (10, 31), "Estimated visible chest fabric", 12)
        for col, title in enumerate(COLUMNS):
            palette.text(template, (LEFT + COL_WIDTH*col + COL_WIDTH//2, 53), title, 13, "ma")
        for i, (obj, role) in enumerate(subjects):
            y = TOP+i*ROW_HEIGHT
            palette.text(template, (10, y+33), NAMES[obj], 13)
            palette.text(template, (10, y+54), role, 11)
            palette.text(template, (10, y+167), "3× and game size", 11, muted=True)
        frames = []
        for pose in range(29):
            board = template.copy()
            palette.text(board, (board.width-9, 13), f"{pose:02d}  {dwarf.NAMES[pose]}", 14, "ra")
            for i, (obj, role) in enumerate(subjects):
                variants, cuts = appearances(atlas, study, swatches, materials, obj, role, pose)
                tiles = [palette.tile(rows, cuts[3]) for rows in variants]
                npc = REFERENCES[obj]
                x, y = LEFT+COL_WIDTH*(len(COLUMNS)-1), TOP+ROW_HEIGHT*i
                if pose < 27:
                    cb, f = divmod(pose, 15)
                    tiles.append(palette.tile(atlas.game.fr(npc+cb, f), 0))
                    palette.text(board, (x, y+171), NPC_NAMES[npc], 11, muted=True)
                else:
                    palette.text(board, (x+COL_WIDTH//2, y+55), "No matching pose", 12, "ma", muted=True)
                for col, tile in enumerate(tiles):
                    x = LEFT+COL_WIDTH*col
                    board.paste(tile.resize((156, 156), Image.Resampling.NEAREST), (x, y))
                    board.paste(tile, (x+104, y+157))
            frames.append(board)
        ticks = (palette.at_phase(frames[pose], phase) for pose, phase in timeline())
        first = next(ticks)
        first.save(output/f"magic-study-{name}.gif", save_all=True, append_images=ticks,
                   duration=TICK_MS, loop=0, disposal=1, optimize=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    render(args.game_dir, args.output)
