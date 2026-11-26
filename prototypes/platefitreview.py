"""Compare the plate fits and the half-giant Psionicist's hem to the previous Loader.

python prototypes/platefitreview.py GAME_DIR OUTPUT_DIR --previous-checkout CHECKOUT
Use d748d13 for the published comparisons.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from PIL import Image, ImageChops, ImageDraw

from elfreview import CYCLE
from equipmentfitreview import slot_loadouts
from magicgearreview import GalleryPalette, write_loop
from namedrobereview import stamp
from wornreview import Atlas, TERRAIN, art, dwarf, sprites


# Object, label, role, loadouts. Poses 03 and 00 reproduce the published dye sheet.
PEOPLE = (
    (301, "Human woman", "Priest", ("Class colors", "Chest plate", "Full plate")),
    (305, "Elf woman", "Cleric/Psionicist", ("Class colors", "Chest plate", "Full plate")),
    (309, "Half-giant woman", "Psionicist", ("Class colors", "Legs only", "All three")),
)
CLERIC_COLUMNS = ("Class colors", "Earlier full plate", "Chest plate", "Full plate", "Retail Priest", "Retail armor")
HEM_COLUMNS = ("Original figure", "Earlier outfit", "Revised outfit", "Earlier legs", "Revised legs", "All three slots")
HEM_POSES = (0, 3, 4, 5, 6, 0, 1, 7, 8, 9, 10, 2, 11, 12, 13, 14)


def capture(game_dir):
    atlas = Atlas(game_dir)
    atlas.gear.update(slot_loadouts(atlas))
    saved = {}
    for obj, _, role, cases in PEOPLE:
        for combat in (False, True):
            for name in cases:
                gear, armor = atlas.gear[name]
                picture = atlas.pictures.build(obj, combat, gear, armor, role=role)
                saved[f"{obj}/{int(combat)}/{name}"] = picture.hex()
    return saved


def former(game_dir, checkout, script=__file__):
    code = ("import json,runpy,sys; "
            "capture=runpy.run_path(sys.argv[1])['capture']; "
            "json.dump(capture(sys.argv[2]),sys.stdout)")
    args = [sys.executable, "-c", code, str(Path(script).resolve()), str(game_dir.resolve())]
    return json.loads(subprocess.check_output(args, cwd=checkout/"prototypes"))


def unpack(snapshot, palettes):
    result = {}
    for key, hexcode in snapshot.items():
        obj, combat, item = key.split("/")
        obj, combat = int(obj), bool(int(combat))
        side, _ = sprites.room(combat)
        picture = bytes.fromhex(hexcode)
        for frame in range(14 if combat else 15):
            rows = art.decode_frame(picture, frame)[2]
            result[obj, combat*15+frame, item] = palettes[obj].tile(rows, side)
    return result


def shared_crop(tiles, ground):
    ground = ground.convert("RGB")
    left, top, right, bottom = ground.width, ground.height, 0, 0
    for tile in tiles:
        if tile is not None:
            box = ImageChops.difference(tile.convert("RGB"), ground).getbbox()
            if box:
                a, b, c, d = box
                left, top, right, bottom = min(left, a), min(top, b), max(right, c), max(bottom, d)
    return max(left-2, 0), max(top-2, 0), min(right+2, ground.width), min(bottom+2, ground.height)


def fixture(game_dir, checkout):
    atlas = Atlas(game_dir)
    # The exact grounded tile used by armor-dye-class-figures.png. The half-giant
    # uses the taller tile in the original armor slot animation.
    robe = GalleryPalette(atlas, atlas.floor)
    with Image.open(TERRAIN) as source:
        giant = GalleryPalette(atlas, source.convert("RGB").crop((50, 142, 102, 194)))
    palettes = {301: robe, 305: robe, 309: giant}
    before = unpack(former(game_dir, checkout), palettes)
    after = unpack(capture(game_dir), palettes)
    retail = {}
    for obj, palette, last in ((1563, robe, 27), (1342, robe, 24), (2074, giant, 29)):
        for pose in range(last):
            combat, frame = divmod(pose, 15)
            retail[obj, pose] = palette.tile(atlas.game.fr(obj+combat, frame), 0)
    return palettes, before, after, retail


def tiles_for(obj, pose, before, after, retail):
    if obj == 309:
        return (retail[2074, pose], before[obj, pose, "Class colors"], after[obj, pose, "Class colors"],
                before[obj, pose, "Legs only"], after[obj, pose, "Legs only"], after[obj, pose, "All three"])
    return (after[obj, pose, "Class colors"], before[obj, pose, "Full plate"], after[obj, pose, "Chest plate"],
            after[obj, pose, "Full plate"], retail.get((1563, pose)), retail.get((1342, pose)))


def board(palette, before, after, retail, crop, rows):
    hem = rows[0][0] == 309
    columns = HEM_COLUMNS if hem else CLERIC_COLUMNS
    width, height = crop[2]-crop[0], crop[3]-crop[1]
    scale = 3 if hem else 4
    col = max(width*scale+8, 136)
    row = 42 + height*(scale+1)
    im = palette.board((14+col*len(columns), 76+row*len(rows)))
    title = "Half-giant Psionicist  /  Warden’s Plate" if hem else "Plate over the Priest and Cleric robes"
    palette.text(im, (8, 7), title, 19)
    palette.text(im, (im.width-8, 10), f"{scale}× above  ·  Game size below", 13, "ra", muted=True)
    for c, label in enumerate(columns):
        palette.text(im, (7+c*col+col//2, 45), label, 14, "ma")
    for r, (obj, who, role, pose) in enumerate(rows):
        y = 70+r*row
        ImageDraw.Draw(im).line((8, y, im.width-8, y), fill=palette.text_ramp[1])
        palette.text(im, (8, y+4), who+"  ·  "+role, 15)
        palette.text(im, (im.width-8, y+5), f"{pose:02}   {dwarf.NAMES[pose]}", 14, "ra")
        for c, tile in enumerate(tiles_for(obj, pose, before, after, retail)):
            center = 7+c*col+col//2
            if tile is None:
                palette.text(im, (center, y+71), "No matching pose", 13, "ma", muted=True)
            else:
                stamp(im, tile, crop, center, y+32, scale)
    return im


def hem_timing():
    tick = 0
    for pose in HEM_POSES:
        for _ in range(22 if pose in (0, 1, 2) else 7):
            yield pose, tick
            tick += 1


def render(game_dir, out, checkout):
    palettes, before, after, retail = fixture(game_dir, checkout)
    out.mkdir(parents=True, exist_ok=True)
    plate_rows = [p[:3] for p in PEOPLE[:2]]
    floor = palettes[301].floor
    visible = (tile for obj, _, _ in plate_rows for p in range(29) for tile in tiles_for(obj, p, before, after, retail))
    crop = shared_crop(visible, floor)
    poses = [board(palettes[301], before, after, retail, crop, [(*row, pose) for row in plate_rows]) for pose in range(29)]
    poses[0].save(out/"plate-fit-clerics.gif", save_all=True, append_images=[poses[p] for p in CYCLE[1:]],
                  duration=[700 if p<3 or p>=24 else 260 for p in CYCLE], loop=0, disposal=1)
    exact = [(*row, pose) for row, pose in zip(plate_rows, (3, 0))]
    board(palettes[301], before, after, retail, crop, exact).convert("RGB").save(out/"plate-fit-clerics.png", optimize=True)

    giant = palettes[309]
    visible = (tile for p in HEM_POSES for tile in tiles_for(309, p, before, after, retail))
    crop = shared_crop(visible, giant.floor)
    frames = {p: board(giant, before, after, retail, crop, [(*PEOPLE[2][:3], p)]) for p in set(HEM_POSES)}
    write_loop(giant, frames, hem_timing(), out/"plate-fit-half-giant-hem.gif")
    idle = frames[0]
    hem_box = (16, 31, 37, 44)  # waist, upper legs and the raised knee, in the front-idle terrain tile
    closeup = giant.board((idle.width, idle.height+112))
    closeup.paste(idle, (0, 0))
    giant.text(closeup, (8, idle.height+3), "6× hem and raised knee", 14)
    col = (idle.width-14)//len(HEM_COLUMNS)
    for i, tile in enumerate(tiles_for(309, 0, before, after, retail)):
        detail = tile.crop(hem_box)
        detail = detail.resize((detail.width*6, detail.height*6), Image.Resampling.NEAREST)
        closeup.paste(detail, (7+i*col+(col-detail.width)//2, idle.height+28))
    closeup.convert("RGB").save(out/"plate-fit-half-giant-hem.png", optimize=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--previous-checkout", type=Path, required=True)
    args = parser.parse_args()
    render(args.game_dir, args.output, args.previous_checkout)
