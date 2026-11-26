"""Compare Loader outfit dyes at game size and 3x.

python prototypes/armordyereview.py GAME_DIR OUTPUT_DIR
"""

import argparse
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

from wornreview import Atlas, dwarf, elf, sprites


# A row always uses the same pose in all equipment columns.
CLASS_FIGURES = (
    (300, "Human man", "Psionicist", 5, 724),
    (301, "Human woman", "Priest", 3, 1563),
    (302, "Dwarf man", "Cleric/Fighter", 0, 1563),
    (303, "Dwarf woman", "Fighter/Psionicist/Thief", 6, 630),
    (304, "Elf man", "Preserver/Ranger", 13, 724),
    (305, "Elf woman", "Cleric/Psionicist", 0, 1563),
    (306, "Half-elf man", "Preserver", 4, 724),
    (307, "Half-elf woman", "Fighter", 0, 1252),
)
STOCK_FIGURES = (
    (306, "Half-elf man", None, 4, None),
    (307, "Half-elf woman", None, 0, None),
    (308, "Half-giant man", None, 3, None),
    (309, "Half-giant woman", None, 8, None),
    (310, "Halfling man", None, 5, None),
    (311, "Halfling woman", None, 12, None),
    (312, "Mul", None, 3, None),
    (313, "Thri-kreen", None, 0, None),
)
NPC_NAMES = {1252: "Warrior", 1563: "Priest", 724: "Mage", 630: "Thief"}
GEAR = ("Class colors", "Full leather", "Full plate", "Ashen Robe", "Veiled Robe")
LEFT = 186
COL = 171
TOP = 100
ROW = 140


def caption(board, position, text, size, colour=dwarf.INK, anchor="la"):
    ImageDraw.Draw(board).text(position, text, font=dwarf.board_font(size), fill=colour, anchor=anchor)


def tiles(atlas, obj, role, pose, ref):
    combat, frame = divmod(pose, 15)
    side, top = sprites.room(combat)
    pictures = []
    for item in GEAR:
        rows = atlas.sequence(obj, bool(combat), role, item)[frame]
        pictures.append(elf.placed_tile(atlas.game, rows, atlas.floor, 1, side, top, 0))
    if ref is not None:
        pictures.append(atlas.tile(ref, pose, "", "", 1))
    return pictures


def put_tiles(board, pictures, floor, y):
    # Use one crop per row so a change in silhouette or registration stays visible.
    # Anchor it to the floor, and include the whole visible sprite and one pixel of air.
    box = (7, 5, 45, 44)
    for tile in pictures:
        bounds = ImageChops.difference(tile, floor).getbbox()
        if bounds:
            box = (min(box[0], max(0, bounds[0] - 1)), min(box[1], max(0, bounds[1] - 1)),
                   max(box[2], min(tile.width, bounds[2] + 1)), tile.height)
    for col, tile in enumerate(pictures):
        cut = tile.crop(box)
        big = cut.resize((cut.width*3, cut.height*3), Image.Resampling.NEAREST)
        width = big.width + 3 + cut.width
        x = LEFT + col*COL + (COL-width)//2
        board.paste(big, (x, y+ROW-big.height-4))
        board.paste(cut, (x+big.width+3, y+ROW-cut.height-4))


def sheet(atlas, subjects, title, subtitle, output):
    has_refs = subjects[0][-1] is not None
    headers = ["Class colors" if has_refs else "Original colors", *GEAR[1:]]
    if has_refs:
        headers.append("Retail reference")
    board = Image.new("RGB", (LEFT+COL*len(headers)+6, TOP+ROW*len(subjects)+8), dwarf.PAPER)
    pen = ImageDraw.Draw(board)
    caption(board, (12, 8), title, 22)
    caption(board, (13, 40), subtitle, 13, dwarf.MUTED)
    for col, text in enumerate(headers):
        caption(board, (LEFT+COL*col+COL//2, 75), text, 14, anchor="ma")
    for i, (obj, name, role, pose, ref) in enumerate(subjects):
        y = TOP + ROW*i
        pen.line((12, y, board.width-10, y), fill="#514b43")
        caption(board, (13, y+12), name, 16)
        if role:
            parts = role.split("/")
            lines = [role] if len(parts) < 3 else ["/".join(parts[:2])+"/", parts[2]]
            for j, line in enumerate(lines):
                caption(board, (13, y+36+j*16), line, 13)
        caption(board, (13, y+78), dwarf.NAMES[pose], 12, dwarf.MUTED)
        if has_refs:
            caption(board, (13, y+97), "Ref. "+NPC_NAMES[ref], 12, dwarf.MUTED)
        put_tiles(board, tiles(atlas, obj, role, pose, ref), atlas.floor, y)
    board.save(output)


def main(game_dir, output):
    atlas = Atlas(game_dir)
    atlas.gear["Full leather"] = ({}, (6, 7, 8))
    output.mkdir(parents=True, exist_ok=True)
    sheet(atlas, CLASS_FIGURES, "Armor on class outfits",
          "Loader renders on the arena floor. Each figure appears at 3× and game size.",
          output / "armor-dye-class-figures.png")
    sheet(atlas, STOCK_FIGURES, "Armor on base figures",
          "Half-elves use these figures outside the fitted Fighter and Preserver builds. The thri-kreen cannot wear body armor.",
          output / "armor-dye-original-figures.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    main(args.game_dir, args.output)
