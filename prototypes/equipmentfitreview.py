"""Compare the fitted equipment slots and the rear cape against an earlier Loader.

python prototypes/equipmentfitreview.py GAME_DIR OUTPUT_DIR --previous-checkout CHECKOUT
The published comparison uses a checkout of 9882a56. The two renderers run in separate
processes so each uses its own outfit archive, equipment masks and drawing code.
"""

import argparse
import json
from pathlib import Path
import subprocess
import sys

from PIL import Image, ImageDraw

from magicgearitems import EquippedItem, loadouts
from magicgearreview import GalleryPalette, RACES, TICK_MS, draw_pose, timeline
from wornreview import Atlas, Loadout, TERRAIN, dwarf, icons, sprites, worldgear

# The Warrior's raised rear shoulder exposes the armor on his arm in step two.
SLOT_SUBJECTS = ((300, "Human man", "Warrior", 1252),
                 (309, "Half-giant woman", "Psionicist", 724), (312, "Mul", "Druid/Fighter", 1252))
CLOAK_SUBJECTS = SLOT_SUBJECTS[1:]
REAR = (1, 7, 8, 9, 10)
ATLAS_POSES = (8, 12, 0, 16, 10, 11, 14, 4, 1, 8, 9, 3, 2, 0)


def slot_loadouts(atlas):
    """Use the named Warden's Plate item records and its in-game icon glow for each slot."""
    catalog = dict(atlas.game.chunks)
    catalog.update(icons.new_chunks(atlas.game.chunks))
    gear = {"Empty": ({}, ())}
    pieces = Loadout([])
    for name, slot, record in zip(("Chest only", "Arms only", "Legs only"), ("chest", "arm", "legs"),
                                  worldgear.WARDENS_PLATE[:3]):
        item = EquippedItem(slot, record, atlas.game.item_types)
        weapons, armor = sprites.worn(item, 0, catalog)
        assert not weapons and len(armor) == 1
        gear[name] = weapons, armor
        pieces.items.append((len(pieces.items), item.record, item.kind))
    gear["All three"] = sprites.worn(pieces, 0, catalog)
    return gear


def rear_snapshot(game_dir):
    atlas = Atlas(game_dir)
    atlas.gear.update(loadouts(atlas))
    return {str(obj): atlas.sequence(obj, False, role, "Magic cloak") for obj, _, role, _ in CLOAK_SUBJECTS}


def older_cloaks(game_dir, checkout):
    # Run this module's capture helper with the earlier checkout first on sys.path.
    # Moving old region masks into the current renderer would not reproduce its pictures.
    code = ("import json,runpy,sys; "
            "capture=runpy.run_path(sys.argv[1])['rear_snapshot']; "
            "json.dump(capture(sys.argv[2]),sys.stdout)")
    return json.loads(subprocess.check_output([sys.executable, "-c", code, str(Path(__file__).resolve()),
                                               str(game_dir.resolve())], cwd=checkout/"prototypes"))


def rear_timeline():
    # First pass at walk speed. The second holds each rear step to inspect the fold and hairline.
    tick = 0
    for duration in (320, 680):
        for pose in REAR:
            for _ in range((960 if pose == 1 else duration) // TICK_MS):
                yield pose, tick
                tick += 1


def slot_sheet(atlas, palette, cases):
    col, left, top, row = 158, 205, 75, 115
    board = palette.board((left + len(cases)*col + 6, top + len(ATLAS_POSES)*row))
    palette.text(board, (9, 6), "Warden’s Plate  /  Armor slots across the playable figures", 19)
    palette.text(board, (9, 34), "2× and game size", 14, muted=True)
    for i, item in enumerate(cases):
        palette.text(board, (left + i*col + col//2, 49), item, 14, "ma")
    for (race, (_, people)) in RACES.items():
        for obj, who, role, _ in people:
            pose = ATLAS_POSES[obj-300]
            combat, frame = divmod(pose, 15)
            side, _ = sprites.room(combat)
            y = top + (obj-300)*row
            ImageDraw.Draw(board).line((9, y, board.width-9, y), fill=palette.text_ramp[1])
            title = race.capitalize() + " " + who.lower() if who in ("Man", "Woman") else who
            palette.text(board, (9, y+17), title, 16)
            palette.text(board, (9, y+44), role or "Original figure", 13)
            palette.text(board, (9, y+71), f"{pose:02d}   {dwarf.NAMES[pose]}", 13, muted=True)
            for i, item in enumerate(cases):
                rows = atlas.sequence(obj, bool(combat), role, item)[frame]
                tile = palette.tile(rows, side)
                x = left + i*col
                board.paste(tile.resize((104, 104), Image.Resampling.NEAREST), (x, y+6))
                board.paste(tile, (x+105, y+58))
    return board.convert("RGB")


def render(game_dir, output, previous):
    from magicgearreview import write_loop

    atlas = Atlas(game_dir)
    atlas.gear.update(loadouts(atlas))
    with Image.open(TERRAIN) as arena:
        floor = arena.convert("RGB").crop((50, 142, 102, 194))
    palette = GalleryPalette(atlas, floor)
    output.mkdir(exist_ok=True, parents=True)

    slots = slot_loadouts(atlas)
    atlas.gear.update(slots)
    boards = [draw_pose(atlas, palette, "Warden’s Plate", SLOT_SUBJECTS, pose, tuple(slots),
                        "Armor slots", columns=5) for pose in range(29)]
    write_loop(palette, boards, timeline(), output/"fitted-armor-slots.gif")
    slot_sheet(atlas, palette, tuple(slots)).save(output/"fitted-armor-slots-all.png", optimize=True)

    if previous:
        old = older_cloaks(game_dir, previous)

        def coats(obj, combat, role, item):
            if item == "Previous cloak":
                return old[str(obj)]
            return atlas.sequence(obj, combat, role, "Empty" if item == "Class colors" else "Magic cloak")

        cases = ("Class colors", "Previous cloak", "Revised cloak")
        boards = {pose: draw_pose(atlas, palette, "Cloak of Elvenkind", CLOAK_SUBJECTS, pose, cases,
                                  "Rear walk", columns=3, sequence=coats) for pose in REAR}
        write_loop(palette, boards, rear_timeline(), output/"fitted-cloak-rear.gif")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--previous-checkout", type=Path)
    args = parser.parse_args()
    render(args.game_dir, args.output, args.previous_checkout)
