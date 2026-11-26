"""Compare both named robes with their earlier Loader pictures on the arena floor.

python prototypes/namedrobereview.py GAME_DIR OUTPUT_DIR --previous-checkout CHECKOUT
The published comparison uses a separate checkout of 63a8172.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from PIL import Image, ImageChops, ImageDraw

from magicgearreview import GalleryPalette, TICK_MS, write_loop
from wornreview import Atlas, TERRAIN, art, dwarf, sprites


SUBJECTS = ((308, "Half-giant man", "Cleric"), (309, "Half-giant woman", "Psionicist"),
            (312, "Mul", "Cleric"), (301, "Human woman", "Priest"))
ROBE_LABELS = {"Ashen Robe": "Ashen Robe", "Veiled Robe": "Robe of the Veiled Alliance"}
POSES = (0, 1, 2, 11, 12, 13, 14, 21, 22, 23)
FLOOR = (47, 138, 103, 194)


def capture(game_dir):
    atlas = Atlas(game_dir)
    saved = {}
    for obj, _, role in SUBJECTS:
        for combat in (False, True):
            for name in ("Class colors", *ROBE_LABELS):
                gear, armor = atlas.gear[name]
                saved[f"{obj}/{int(combat)}/{name}"] = atlas.pictures.build(obj, combat, gear, armor, role=role).hex()
    return saved


def earlier(game_dir, checkout):
    read = ("import json,runpy,sys; "
            "capture=runpy.run_path(sys.argv[1])['capture']; "
            "json.dump(capture(sys.argv[2]),sys.stdout)")
    args = [sys.executable, "-c", read, str(Path(__file__).resolve()), str(game_dir.resolve())]
    return json.loads(subprocess.check_output(args, cwd=checkout/"prototypes"))


def unpack(saved, palette):
    tiles = {}
    for key, encoded in saved.items():
        obj, combat, name = key.split("/")
        combat = bool(int(combat))
        side, _ = sprites.room(combat)
        chunk = bytes.fromhex(encoded)
        for pose in POSES:
            if bool(pose >= 15) == combat:
                rows = art.decode_frame(chunk, pose % 15)[2]
                tiles[int(obj), pose, name] = palette.tile(rows, side)
    return tiles


def fixture(game_dir, checkout):
    atlas = Atlas(game_dir)
    with Image.open(TERRAIN) as source:
        floor = source.convert("RGB").crop(FLOOR)
    palette = GalleryPalette(atlas, floor)
    before = unpack(earlier(game_dir, checkout), palette)
    after = unpack(capture(game_dir), palette)
    retail = {pose: palette.tile(atlas.game.fr(1563+int(pose >= 15), pose % 15), 0) for pose in POSES}
    # All columns and both robes share a floor-registered crop.
    a, b, c, d = (10, 12, 46, 54)
    for tile in (*before.values(), *after.values(), *retail.values()):
        l, t, r, bot = ImageChops.difference(floor, tile.convert("RGB")).getbbox()
        a, b, c, d = min(a, l), min(b, t), max(c, r), max(d, bot)
    box = max(0, a-2), max(0, b-2), min(floor.width, c+2), min(floor.height, d+2)
    return palette, before, after, retail, box


def stamp(board, tile, box, center, y, scale):
    small = tile.crop(box)
    big = small.resize((small.width*scale, small.height*scale), Image.Resampling.NEAREST)
    board.paste(big, (center-big.width//2, y))
    board.paste(small, (center-small.width//2, y+big.height+2))


def panel(palette, before, after, retail, box, robe, pose):
    w, h = box[2]-box[0], box[3]-box[1]
    col, row = max(w*3+8, 126), 67+h*4
    board = palette.board((26+col*6, 65+row*2+5))
    palette.text(board, (9, 7), ROBE_LABELS[robe], 20)
    palette.text(board, (10, 36), f"{pose:02}   {dwarf.NAMES[pose]}", 14)
    reference = retail[pose].crop(box)
    palette.text(board, (board.width-reference.width-14, 17), "Retail Priest", 14, "ra")
    board.paste(reference, (board.width-reference.width-8, 4))
    for i, (obj, who, role) in enumerate(SUBJECTS):
        row_id, group = divmod(i, 2)
        x, y = 8+group*(col*3+9), 62+row_id*row
        ImageDraw.Draw(board).line((x, y, x+col*3-4, y), fill=palette.text_ramp[1])
        palette.text(board, (x+1, y+5), f"{who}  ·  {role}", 16)
        palette.text(board, (x+3*col-5, y+7), "3× and game size", 12, "ra", muted=True)
        columns = (("Class colors", after[obj, pose, "Class colors"]), ("Earlier robe", before[obj, pose, robe]),
                   ("Revised robe", after[obj, pose, robe]))
        for j, (label, picture) in enumerate(columns):
            center = x+j*col+col//2
            palette.text(board, (center, y+31), label, 13, "ma")
            stamp(board, picture, box, center, y+52, 3)
    return board


def front_sheet(palette, before, after, box):
    width, height = box[2]-box[0], box[3]-box[1]
    left, col, row = 150, max(width*3+8, 128), height*4+12
    board = palette.board((left+5*col+8, 76+4*row))
    palette.text(board, (9, 7), "Class colors under the named robes  /  Front idle", 19)
    palette.text(board, (board.width-8, 10), "3× and game size", 13, "ra", muted=True)
    columns = (("Class colors", after, "Class colors"), ("Earlier Ashen", before, "Ashen Robe"),
               ("Revised Ashen", after, "Ashen Robe"), ("Earlier Veiled", before, "Veiled Robe"),
               ("Revised Veiled", after, "Veiled Robe"))
    for j, (label, _, _) in enumerate(columns):
        palette.text(board, (left+j*col+col//2, 47), label, 14, "ma")
    for i, (obj, who, role) in enumerate(SUBJECTS):
        y = 72+i*row
        ImageDraw.Draw(board).line((8, y, board.width-8, y), fill=palette.text_ramp[1])
        palette.text(board, (10, y+20), who, 16)
        palette.text(board, (10, y+45), role, 14, muted=True)
        for j, (_, source, name) in enumerate(columns):
            stamp(board, source[obj, 0, name], box, left+j*col+col//2, y+6, 3)
    return board.convert("RGB")


def timing():
    tick = 0
    for pose in POSES:
        duration = 960 if pose<3 or pose==23 else 320
        for _ in range(duration//TICK_MS):
            yield pose, tick
            tick += 1


def render(game_dir, output, previous):
    palette, before, after, retail, box = fixture(game_dir, previous)
    output.mkdir(exist_ok=True, parents=True)
    for robe, stem in (("Ashen Robe", "ashen"), ("Veiled Robe", "veiled")):
        boards = {pose:panel(palette, before, after, retail, box, robe, pose) for pose in POSES}
        write_loop(palette, boards, timing(), output/f"named-robe-{stem}.gif")
    front_sheet(palette, before, after, box).save(output/"named-robe-class-colors.png", optimize=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--previous-checkout", type=Path, required=True)
    args = parser.parse_args()
    render(args.game_dir, args.output, args.previous_checkout)
