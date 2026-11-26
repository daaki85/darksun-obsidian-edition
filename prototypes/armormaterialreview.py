"""Compare armor materials across the roster using pictures from two Loader checkouts.

python prototypes/armormaterialreview.py GAME_DIR OUTPUT_DIR --previous-checkout CHECKOUT
The earlier columns use b82788c. The optional --race selects individual animations.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from equipmentfitreview import slot_loadouts
from magicgearreview import GalleryPalette, NPC_NAMES, RACES, timeline, write_loop
from namedrobereview import stamp
from platefitreview import former, shared_crop
from wornreview import Atlas, TERRAIN, art, sprites, dwarf


CASES = ("Class colors", "Leather", "Full plate", "Warden’s Plate")
MATERIALS = ("Class colors", "Leather", "Plate", "Warden’s Plate", "Shattered Lands")
# The same previously reported Priest, Cleric/Psionicist and half-giant Psionicist poses.
STILL_POSE = (5, 3, 0, 6, 13, 0, 4, 0, 3, 0, 5, 12, 3, 0)
RACE_NAMES = {"human": "Human", "dwarf": "Dwarf", "elf": "Elf", "half-elf": "Half-elf",
              "half-giant": "Half-giant", "halfling": "Halfling", "mul": "Mul", "thri-kreen": "Thri-kreen"}


def capture(game_dir):
    atlas = Atlas(game_dir)
    atlas.gear["Leather"] = {}, (6, 7, 8)
    atlas.gear["Warden’s Plate"] = slot_loadouts(atlas)["All three"]
    saved = {}
    for _, people in RACES.values():
        for obj, _, role, _ in people:
            for combat in (False, True):
                for name in CASES:
                    gear, armor = atlas.gear[name]
                    picture = atlas.pictures.build(obj, combat, gear, armor, role=role)
                    saved[f"{obj}/{int(combat)}/{name}"] = picture.hex()
    return saved


def unpack(saved, palette):
    images = {}
    for key, encoded in saved.items():
        obj, combat, name = key.split("/")
        combat = bool(int(combat))
        side, _ = sprites.room(combat)
        picture = bytes.fromhex(encoded)
        for frame in range(14 if combat else 15):
            images[int(obj), 15*combat+frame, name] = palette.tile(art.decode_frame(picture, frame)[2], side)
    return images


def reference(obj, ref):
    return 291 if obj == 313 else ref


def fixture(game_dir, checkout):
    atlas = Atlas(game_dir)
    with Image.open(TERRAIN) as source:
        # The half-giant's raised fist needs the taller tile.
        palette = GalleryPalette(atlas, source.convert("RGB").crop((50, 142, 102, 194)))
    before = unpack(former(game_dir, checkout, __file__), palette)
    after = unpack(capture(game_dir), palette)
    references = {reference(obj, ref) for _, people in RACES.values() for obj, _, _, ref in people}
    retail = {(ref, pose): palette.tile(atlas.game.fr(ref+int(pose>=15), pose%15), 0)
              for ref in references for pose in range(27)}
    return palette, before, after, retail


def loadout_tiles(obj, ref, pose, before, after, retail):
    images = [after[obj, pose, "Class colors"]]
    for item in CASES[1:]:
        images.extend((before[obj, pose, item], after[obj, pose, item]))
    images.append(retail.get((reference(obj, ref), pose)))
    return images


def headings(board, palette, left, top, col):
    for title, start, count in zip(MATERIALS, (0, 1, 3, 5, 7), (1, 2, 2, 2, 1)):
        x = left+col*start
        palette.text(board, (x+col*count//2, top), title, 14, "ma")
        ImageDraw.Draw(board).line((x+2, top+22, x+col*count-2, top+22), fill=palette.text_ramp[2])
        if count == 2:
            for i, label in enumerate(("Earlier", "Revised")):
                palette.text(board, (x+(i*col)+col//2, top+27), label, 12, "ma", muted=True)


def view_for(people, poses, before, after, retail, palette):
    tiles = (tile for obj, _, _, ref in people for pose in poses
             for tile in loadout_tiles(obj, ref, pose, before, after, retail))
    return shared_crop(tiles, palette.floor)


def motion(palette, before, after, retail, race, crop, pose):
    title, people = RACES[race]
    w, h = crop[2]-crop[0], crop[3]-crop[1]
    col = max(w*3+5, 111)
    row = 40+h*4
    board = palette.board((14+8*col, 91+len(people)*row))
    palette.text(board, (8, 5), title+"  /  Armor colors", 19)
    palette.text(board, (board.width-8, 7), f"{pose:02}   {dwarf.NAMES[pose]}", 15, "ra")
    headings(board, palette, 7, 36, col)
    for r, (obj, who, role, ref) in enumerate(people):
        y = 86+r*row
        ImageDraw.Draw(board).line((8, y, board.width-8, y), fill=palette.text_ramp[1])
        name = f"{who}  ·  {role}" if role else "Original shell"
        npc = NPC_NAMES.get(reference(obj, ref), "Thri-kreen")
        palette.text(board, (8, y+4), name, 15)
        palette.text(board, (board.width-8, y+6), f"3× and game size  ·  Retail {npc}", 12, "ra", muted=True)
        for c, tile in enumerate(loadout_tiles(obj, ref, pose, before, after, retail)):
            center = 7+c*col+col//2
            if tile is not None:
                stamp(board, tile, crop, center, y+31, 3)
            else:
                palette.text(board, (center, y+66), "No matching pose", 12, "ma", muted=True)
    return board


def poster(palette, before, after, retail):
    left, col, top = 170, 115, 95
    rows = []
    for race, (_, people) in RACES.items():
        for person in people:
            pose = STILL_POSE[person[0]-300]
            crop = view_for((person,), (pose,), before, after, retail, palette)
            height = max(119, (crop[3]-crop[1])*3+12)
            rows.append((race, person, pose, crop, height))
    board = palette.board((left+8*col+6, top+sum(row[-1] for row in rows)+5))
    palette.text(board, (8, 6), "Armor colors on the fourteen party figures", 21)
    palette.text(board, (board.width-8, 9), "2× above  ·  Game size below", 14, "ra", muted=True)
    headings(board, palette, left, 43, col)
    y = top
    for race, person, pose, crop, row in rows:
        obj, who, role, ref = person
        ImageDraw.Draw(board).line((8,y,board.width-8,y), fill=palette.text_ramp[1])
        name = RACE_NAMES[race]+" "+who.lower() if who in ("Man","Woman") else who
        palette.text(board, (8, y+10), name, 15)
        if role:
            lines = role.split("/") if len(role)>20 else [role]
            for sub, text in enumerate(lines):
                palette.text(board, (8, y+33+14*sub), text, 12, muted=True)
        palette.text(board, (8, y+83), f"{pose:02}   {dwarf.NAMES[pose]}", 12, muted=True)
        palette.text(board, (8, y+101), "Ref. "+NPC_NAMES.get(reference(obj,ref),"Thri-kreen"), 12, muted=True)
        for c, tile in enumerate(loadout_tiles(obj, ref, pose, before, after, retail)):
            # Center each row vertically around this figure's registered crop.
            h = crop[3]-crop[1]
            stamp(board, tile, crop, left+c*col+col//2, y+(row-(h*3+2))//2, 2)
        y += row
    return board.convert("RGB")


def render(game_dir, output, checkout, races):
    palette, before, after, retail = fixture(game_dir, checkout)
    output.mkdir(parents=True, exist_ok=True)
    for race in races:
        if race == "poster":
            poster(palette, before, after, retail).save(output/"armor-colors-all.png", optimize=True)
            continue
        crop = view_for(RACES[race][1], range(29), before, after, retail, palette)
        frames = [motion(palette, before, after, retail, race, crop, pose) for pose in range(29)]
        write_loop(palette, frames, timeline(), output/f"armor-colors-{race}.gif")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--previous-checkout", type=Path, required=True)
    parser.add_argument("--race", nargs="+", choices=(*RACES, "poster"))
    args = parser.parse_args()
    render(args.game_dir, args.output, args.previous_checkout, args.race or (*RACES,"poster"))
