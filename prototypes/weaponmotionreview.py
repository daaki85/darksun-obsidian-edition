"""Render party weapon fits and a retail reference at native scale and 3x.

python prototypes/weaponmotionreview.py GAME_DIR OUTPUT_DIR [race ...]
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from elfreview import CYCLE
from magicgearreview import GalleryPalette, RACES
from wornreview import Atlas, TERRAIN, dwarf, game, sprites


CASES = ("Empty slots", "Sword and shield", "Staff", "Bow and quiver")
KREEN_CASES = ("Empty slots", "Sword and shield", "Gythka", "Bow and quiver", "Chatkcha")
SCALE, TILE_W, TILE_H = 3, 56, 56
COLUMN_WIDTH = TILE_W * SCALE + 5
QUIVER_CASES = ("Bow alone", "Bow + arrows", "Bow + spare blade")
SHAPE_ROWS = (("Blades", 22, ("Metal dagger", "Short sword", "Long sword")),
              ("Picks and polearm", 22, ("Stone pick", "Metal pick", "Polearm")),
              ("Carried missile weapons", 0, ("Sling", "Staff sling", "Bow and quiver")),
              ("Quiver contents", 1, QUIVER_CASES))


def subjects(race):
    return tuple((obj, gender, ("Warrior" if obj < 302 else "Fighter") if obj != 313 else None)
                 for obj, gender, _, _ in RACES[race][1])


def put_tile(board, tile, x, top, inset=None):
    enlarged = tile.resize((tile.width*SCALE, tile.height*SCALE), Image.Resampling.NEAREST)
    board.paste(enlarged, (x-enlarged.width//2, top))
    lower = top+enlarged.height+2
    if inset:
        crop = tile.crop(inset)
        detail = crop.resize((crop.width*8, crop.height*8), Image.Resampling.NEAREST)
        left = x-(tile.width+4+detail.width)//2
        board.paste(tile, (left, lower))
        board.paste(detail, (left+tile.width+4, lower))
    else:
        board.paste(tile, (x-tile.width//2, lower))


def make_pose(atlas, palette, race, pose):
    people = subjects(race)
    cases = KREEN_CASES if race == "thri-kreen" else CASES
    size = (14 + (len(cases)+1)*COLUMN_WIDTH, 66 + len(people)*255)
    board = palette.board(size)
    draw = ImageDraw.Draw(board)
    palette.text(board, (8, 6), f"{RACES[race][0]}  /  Weapons", 19)
    palette.text(board, (board.width-8, 8), f"{pose:02}   {dwarf.NAMES[pose]}", 15, "ra")
    labels = [*cases, "Retail thri-kreen" if race == "thri-kreen" else "Retail Warrior"]
    for col, caption in enumerate(labels):
        palette.text(board, (7+col*COLUMN_WIDTH+COLUMN_WIDTH//2, 38), caption, 13, "ma")
    combat, frame = divmod(pose, 15)
    side, _ = sprites.room(combat)
    for r, (obj, who, role) in enumerate(people):
        top = 61 + r*255
        draw.line((8, top, board.width-8, top), fill=palette.text_ramp[1])
        palette.text(board, (8, top+3), f"{who}  ·  {role}" if role else "Original party figure", 14)
        palette.text(board, (board.width-8, top+4), "3× above  ·  Game size below", 12, "ra", muted=True)
        for col, case in enumerate((*cases, None)):
            x = 7+col*COLUMN_WIDTH+COLUMN_WIDTH//2
            if case:
                rows = atlas.sequence(obj, bool(combat), role, case)[frame]
                tile = palette.tile(rows, side)
            elif pose <= 26:
                ref = 291 if race == "thri-kreen" else 1252
                tile = palette.tile(atlas.game.fr(ref+combat, frame), 0)
            else:
                palette.text(board, (x, top+100), "No matching pose", 12, "ma", muted=True)
                continue
            put_tile(board, tile, x, top+26)
    return board


def shape_sheet(atlas, palette, rows=SHAPE_ROWS, title="Weapon shapes and materials"):
    board = palette.board((14+5*COLUMN_WIDTH, 40+len(rows)*287))
    palette.text(board, (8, 6), f"Human Warrior  /  {title}", 19)
    for r, (caption, pose, weapons) in enumerate(rows):
        y = 36+r*287
        ImageDraw.Draw(board).line((8, y, board.width-8, y), fill=palette.text_ramp[1])
        palette.text(board, (8, y+4), f"{caption}  ·  {pose:02}  {dwarf.NAMES[pose]}", 15)
        # The six hilt/fletching pixels fall within this same rear-idle crop in every column.
        inset = (20, 28, 29, 35) if weapons == QUIVER_CASES and pose == 1 and len(rows) > 1 else None
        scale_label = "3× above  ·  Game size and 8× detail below" if inset else "3× above  ·  Game size below"
        palette.text(board, (board.width-8, y+6), scale_label, 12, "ra", muted=True)
        combat, frame = divmod(pose, 15)
        side, _ = sprites.room(combat)
        for col, label in enumerate(("Retail human", "Empty slots", *weapons)):
            x = 7+col*COLUMN_WIDTH+COLUMN_WIDTH//2
            if col == 0:
                tile = palette.tile(atlas.game.fr(2095+combat, frame), 0)
            else:
                tile = palette.tile(atlas.sequence(300, bool(combat), "Warrior", label)[frame], side)
            palette.text(board, (x, y+30), label, 13, "ma")
            put_tile(board, tile, x, y+52, inset)
    return board


def add_cases(atlas):
    atlas.gear.update({
        "Empty slots": ({}, ()),
        "Metal dagger": ({"right": (game.METAL_DAGGER_TYPE, 4)}, ()),
        "Metal pick": ({"right": (game.METAL_PICK_TYPE, 4)}, ()),
        "Long sword": atlas.gear["Sword"], "Stone pick": atlas.gear["Pick"],
        "Bow alone": atlas.gear["Bow"], "Bow + arrows": atlas.gear["Bow and quiver"],
        "Bow + spare blade": ({"missile": (1, 0), "ammo": (game.METAL_SHORT_SWORD_TYPE, 4)}, ()),
    })


def render(game_dir, directory, races):
    atlas = Atlas(game_dir)
    add_cases(atlas)
    with Image.open(TERRAIN) as source:
        floor = source.convert("RGB").crop((47, 138, 47+TILE_W, 138+TILE_H))
    palette = GalleryPalette(atlas, floor)
    directory.mkdir(parents=True, exist_ok=True)
    for race in races:
        if race == "shapes":
            shape_sheet(atlas, palette).convert("RGB").save(directory/"weapon-motion-shapes.png", optimize=True)
            continue
        if race == "quiver":
            poses = [shape_sheet(atlas, palette, (("Quiver contents", pose, QUIVER_CASES),), "Bow and quiver")
                     for pose in range(29)]
        else:
            poses = [make_pose(atlas, palette, race, pose) for pose in range(29)]
        # Hit, fall and the three single-frame archery views hold a little longer.
        duration = [500 if pose < 3 or pose >= 24 else 230 for pose in CYCLE]
        poses[0].save(directory/f"weapon-motion-{race}.gif", save_all=True,
                      append_images=[poses[pose] for pose in CYCLE[1:]], duration=duration, loop=0, disposal=1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("races", nargs="*")
    options = parser.parse_args()
    render(options.game_dir, options.output, options.races or (*RACES, "shapes", "quiver"))
