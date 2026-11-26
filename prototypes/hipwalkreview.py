"""Show hip equipment on a moving party figure before and after its fitting.

python prototypes/hipwalkreview.py GAME_DIR OUTPUT_DIR --previous-checkout CHECKOUT [--race RACE ...]
The published comparison uses a checkout of b833c37 with its own Loader and outfit archives.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from PIL import Image, ImageChops, ImageDraw

from magicgearreview import GalleryPalette, RACES
from weaponmotionreview import COLUMN_WIDTH, SCALE, TILE_H, TILE_W, subjects
from wornreview import Atlas, TERRAIN, art, dwarf, sprites


WALK = (0, 3, 4, 5, 6, 1, 7, 8, 9, 10, 2, 11, 12, 13, 14)
COLUMNS = ("No weapons", "Earlier sword", "Fitted sword", "Earlier pair", "Fitted pair")
GROUPS = {race: subjects(race) for race in RACES}
GROUPS["class-cloaks"] = ((301, "Human woman", "Thief"), (308, "Half-giant man", "Ranger"))


def cloak_slots(group):
    return (False,) if group in ("thri-kreen", "class-cloaks") else (False, True)


def captures(game_dir, races):
    atlas = Atlas(game_dir)
    captures = {}
    for race in races:
        for obj, _, role in GROUPS[race]:
            sword = atlas.gear["Sword"][0]["right"]
            dagger = atlas.gear["Dagger"][0]["right"]
            for cloaked in cloak_slots(race):
                cloak = atlas.gear["Cloak"][0] if cloaked else {}
                for name, hands in (("empty", {}), ("sword", {"right": sword}),
                                    ("pair", {"right": sword, "left": dagger})):
                    key = f"{obj}/{role or ''}/{int(cloaked)}/{name}"
                    captures[key] = atlas.pictures.build(obj, False, {**cloak, **hands}, (), role=role).hex()
    return captures


def previous_captures(game_dir, checkout, races):
    # Load the earlier path first. Importing old art through today's equipment code
    # would silently change the comparison when that code is edited later.
    run = ("import json,runpy,sys; "
           "capture=runpy.run_path(sys.argv[1])['captures']; "
           "json.dump(capture(sys.argv[2],sys.argv[3:]),sys.stdout)")
    args = [sys.executable, "-c", run, str(Path(__file__).resolve()), str(game_dir.resolve()), *races]
    return json.loads(subprocess.check_output(args, cwd=checkout/"prototypes"))


def tiles(palette, captures):
    side = sprites.room(False)[0]
    result = {}
    for key, hex_picture in captures.items():
        obj, role, cloaked, item = key.split("/")
        picture = bytes.fromhex(hex_picture)
        result[int(obj), role or None, bool(int(cloaked)), item] = [
            palette.tile(art.decode_frame(picture, pose)[2], side) for pose in range(15)]
    return result


def belt_crop(before, after, obj, role, pose, floor):
    # One crop for every column and both cloak states, registered to this pose.
    area = Image.new("L", floor.size)
    for images in (before, after):
        empty = images[obj, role, False, "empty"][pose].convert("RGB")
        for name in ("sword", "pair"):
            kit = images[obj, role, False, name][pose].convert("RGB")
            area = ImageChops.lighter(area, ImageChops.difference(empty, kit).convert("L"))
    box = area.getbbox() or ImageChops.difference(empty, floor.convert("RGB")).getbbox()
    x1, y1, x2, y2 = box
    x = max(0, min(TILE_W-22, (x1+x2)//2-11))
    y = max(0, min(TILE_H-13, y1-1))
    return x, y, x+22, y+13


def panel(palette, race, pose, cloaked, before, after):
    people = GROUPS[race]
    board = palette.board((14+len(COLUMNS)*COLUMN_WIDTH, 77+len(people)*267))
    title = "Class cloaks" if race == "class-cloaks" else RACES[race][0]
    palette.text(board, (8, 6), f"{title}  /  Hip weapons", 19)
    palette.text(board, (board.width-8, 8), f"{pose:02}   {dwarf.NAMES[pose]}", 15, "ra")
    layer = "Wearing a cloak" if cloaked else "Cloak slot empty"
    if race == "class-cloaks":
        layer = "Class cloak  ·  Cloak slot empty"
    palette.text(board, (8, 35), layer if race != "thri-kreen" else "Original shell", 13)
    for col, caption in enumerate(COLUMNS):
        x = 7 + col*COLUMN_WIDTH + COLUMN_WIDTH//2
        palette.text(board, (x, 54), caption, 13, "ma")
    for row, (obj, who, role) in enumerate(people):
        top = 76+row*267
        ImageDraw.Draw(board).line((8, top, board.width-8, top), fill=palette.text_ramp[1])
        palette.text(board, (8, top+4), f"{who}  ·  {role}" if role else "Original party figure", 14)
        palette.text(board, (board.width-8, top+6), "3× above  ·  Game size and 5× belt detail below", 12, "ra", muted=True)
        crop = belt_crop(before, after, obj, role, pose, palette.floor)
        cases = ((after, "empty"), (before, "sword"), (after, "sword"), (before, "pair"), (after, "pair"))
        for col, (source, case) in enumerate(cases):
            tile = source[obj, role, cloaked, case][pose]
            x = 7+col*COLUMN_WIDTH+COLUMN_WIDTH//2
            y = top+28
            board.paste(tile.resize((TILE_W*SCALE, TILE_H*SCALE), Image.Resampling.NEAREST), (x-TILE_W*SCALE//2, y))
            y += TILE_H*SCALE+3
            board.paste(tile, (x-85, y+9))
            board.paste(tile.crop(crop).resize((110, 65), Image.Resampling.NEAREST), (x-26, y))
    return board


def render(game_dir, output, checkout, races):
    atlas = Atlas(game_dir)
    with Image.open(TERRAIN) as source:
        floor = source.convert("RGB").crop((47, 138, 47+TILE_W, 138+TILE_H))
    palette = GalleryPalette(atlas, floor)
    before = tiles(palette, previous_captures(game_dir, checkout, races))
    after = tiles(palette, captures(game_dir, races))
    output.mkdir(parents=True, exist_ok=True)
    for race in races:
        states = [(pose, cloaked) for cloaked in cloak_slots(race) for pose in WALK]
        frames = [panel(palette, race, pose, cloaked, before, after) for pose, cloaked in states]
        frames[0].save(output/f"hip-walk-{race}.gif", save_all=True, append_images=frames[1:], loop=0, disposal=1,
                       duration=[740 if pose < 3 else 250 for pose, _ in states])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--previous-checkout", type=Path, required=True)
    parser.add_argument("--race", nargs="+", choices=GROUPS)
    args = parser.parse_args()
    render(args.game_dir, args.output, args.previous_checkout, args.race or tuple(GROUPS))
