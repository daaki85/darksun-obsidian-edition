"""Review both fitted armor looks and the half-elf weapon grips through every pose.

python prototypes/halfelfequipreview.py GAME_DIR OUTPUT_DIR
"""
import argparse
from functools import lru_cache
from pathlib import Path

from PIL import Image

from elfreview import dwarf, elf, label, loop
from wornreview import Atlas, art, sprites, sg

ARMOR = ("Empty", "Leather", "Chest plate", "Full plate", "Magic chest", "Ashen Robe", "Veiled Robe")
WEAPONS = ("Empty", "Club", "Sword and shield", "Bow only", "Ammo only", "Bow and quiver", "Sling", "Chatkcha")


def review(game_dir, output):
    atlas = Atlas(game_dir)
    atlas.gear.update({"Empty": ({}, ()), "Leather": ({}, (6, 7, 8)),
                       "Magic chest": ({}, (88 | sg.MAGIC_ARMOUR,)),
                       "Bow only": ({"missile": (1, 0)}, ()), "Ammo only": ({"ammo": (62, 0)}, ())})
    output.mkdir(exist_ok=True, parents=True)

    @lru_cache(None)
    def sequence(obj, combat, role, item):
        chunk = atlas.pictures.build(obj, combat, *atlas.gear[item], role=role)
        return [art.decode_frame(chunk, f)[2] for f in range(14 if combat else 15)]

    for stem, title, items, subjects in (
        ("armor", "Half-elf woman", ARMOR, ((307, "Fighter"), (307, "Preserver"))),
        ("weapons", "Half-elf man", WEAPONS, ((306, "Fighter"), (306, "Preserver"))),
    ):
        frames = []
        for pose, name in enumerate(dwarf.NAMES):
            combat, f = divmod(pose, 15)
            side, top = sprites.room(combat)
            board = Image.new("RGB", ((len(items)+1)*160+12, 416), dwarf.PAPER)
            label(board, (8, 5), title, 17)
            label(board, (board.width-8, 8), f"{pose:02d}  {name}", 13, "ra")
            for col, item in enumerate(items):
                x = 6+col*160
                label(board, (x+78, 33), item, 12, "ma")
                for i, (obj, role) in enumerate(subjects):
                    y = 50+i*183
                    rows = sequence(obj, bool(combat), role, item)[f]
                    tile = elf.placed_tile(atlas.game, rows, atlas.floor, 1, side, top, 0)
                    board.paste(tile.resize((156, 132), Image.Resampling.NEAREST), (x, y))
                    board.paste(tile, (x+102, y+132))
                    label(board, (x+3, y+145), role, 10)
            x = 6+len(items)*160
            label(board, (x+78, 33), "Shattered Lands", 12, "ma")
            for i, (npc, caption) in enumerate(((1252, "Warrior"), (724, "Mage"))):
                y = 50+i*183
                if pose < 27:
                    tile = atlas.tile(npc, pose, "", "", 1)
                    board.paste(tile.resize((156, 132), Image.Resampling.NEAREST), (x, y))
                    board.paste(tile, (x+102, y+132))
                else:
                    label(board, (x+78, y+60), "No matching cel", 12, "ma")
                label(board, (x+3, y+145), caption, 10)
            frames.append(board)
        loop(frames, output/f"half-elf-equipped-{stem}.gif")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    review(args.game_dir, args.output)
