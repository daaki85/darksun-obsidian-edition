"""Render current ordinary and magical plate on the three midtone-study subjects."""
import argparse
from pathlib import Path

from PIL import Image
from equipmentfitreview import slot_loadouts
from magicgearreview import GalleryPalette, timeline, write_loop
from namedrobereview import stamp
from platefitreview import shared_crop
from platemidtones import PEOPLE
from wornreview import Atlas, TERRAIN, dwarf, sprites


def render(game_dir, output):
    atlas = Atlas(game_dir)
    atlas.gear["Warden’s Plate"] = slot_loadouts(atlas)["All three"]
    cases = ("Class colors", "Full plate", "Warden’s Plate")
    with Image.open(TERRAIN) as arena:
        palette = GalleryPalette(atlas, arena.convert("RGB").crop((50, 142, 102, 194)))
    tiles = {}
    for obj, _, role in PEOPLE:
        for name in cases:
            for combat in (False, True):
                side, _ = sprites.room(combat)
                for frame, rows in enumerate(atlas.sequence(obj, combat, role, name)):
                    tiles[obj, name, 15*combat+frame] = palette.tile(rows, side)
    boxes = {obj: shared_crop((tiles[obj, name, i] for i in range(29) for name in cases), palette.floor)
             for obj, _, _ in PEOPLE}
    heights = {obj: 37 + (box[3]-box[1])*4 for obj, box in boxes.items()}
    frames = []
    for pose in range(29):
        board = palette.board((492, 66+sum(heights.values())))
        palette.text(board, (8, 5), "Current Warden’s Plate", 19)
        palette.text(board, (484, 8), f"{pose:02d}  {dwarf.NAMES[pose]}", 14, "ra")
        for i, name in enumerate(cases):
            palette.text(board, (82+164*i, 39), name, 15, "ma")
        y = 64
        for obj, who, role in PEOPLE:
            palette.text(board, (8, y), f"{who}  ·  {role}", 15)
            palette.text(board, (484, y+2), "3× and game size", 12, "ra", muted=True)
            for i, name in enumerate(cases):
                stamp(board, tiles[obj, name, pose], boxes[obj], 82+164*i, y+23, 3)
            y += heights[obj]
        frames.append(board)
    output.mkdir(parents=True, exist_ok=True)
    frames[0].convert("RGB").save(output/"current-warden-plate.png", optimize=True)
    write_loop(palette, frames, timeline(), output/"current-warden-plate.gif")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    render(args.game_dir, args.output)
