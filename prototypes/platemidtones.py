"""Build a review-only full plate study from original, softened and refitted Loader pictures."""
import argparse
from pathlib import Path

from wornreview import Atlas, art

PEOPLE = ((301, "Human woman", "Priest"), (300, "Human man", "Psionicist"),
          (308, "Half-giant man", "Cleric/Fighter"))
SLOTS = {"Class": (), "Chest": (88,), "Arms": (25,), "Legs": (26,), "Plate": (88, 25, 26)}


def capture(game_dir):
    atlas = Atlas(game_dir)
    chunks = {}
    for obj, _, role in PEOPLE:
        for combat in (False, True):
            for name, pieces in SLOTS.items():
                chunk = atlas.pictures.build(obj, combat, {}, pieces, role=role)
                chunks[f"{obj}/{int(combat)}/{name}"] = chunk.hex()
    return chunks


def unpack(chunks):
    rows = {}
    for key, hexcode in chunks.items():
        obj, combat, name = key.split("/")
        combat = int(combat)
        picture = bytes.fromhex(hexcode)
        for frame in range(14 if combat else 15):
            rows[int(obj), combat*15 + frame, name] = art.decode_frame(picture, frame)[2]
    return rows


def changes(base, worn):
    return {(x, y) for y, row in enumerate(worn) for x, c in enumerate(row) if c != base[y][x]}


def trial(base, current, fitted, light):
    """Grow the present steel across neighboring raised planes, separately for each piece."""
    full = [row[:] for row in current["Plate"]]
    allowed = changes(base, fitted["Plate"])
    for name in ("Chest", "Arms", "Legs"):
        plane = changes(base, fitted[name]) & allowed
        metal = plane & changes(base, current[name])
        target = round(0.70 * len(plane))
        def priority(p):
            x, y = p
            joins = sum(q in metal for q in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)))
            return light[base[y][x]] + min(joins, 2) * 0.06, -y, -x
        while len(metal) < target:
            x, y = max(plane - metal, key=priority)
            metal.add((x, y))
            full[y][x] = fitted["Plate"][y][x]
    assert changes(base, current["Plate"]) <= changes(base, full) <= allowed
    assert all(full[y][x] == fitted["Plate"][y][x] for x, y in changes(base, full))
    return full


def render(game_dir, output, earlier, refit):
    from PIL import Image, ImageDraw
    from elfreview import CYCLE
    from magicgearreview import GalleryPalette
    from namedrobereview import stamp
    from platefitreview import former, shared_crop
    from wornreview import TERRAIN, dwarf, sprites

    atlas = Atlas(game_dir)
    with Image.open(TERRAIN) as source:
        palette = GalleryPalette(atlas, source.convert("RGB").crop((50, 142, 102, 194)))
    light = [(0.30*r + 0.59*g + 0.11*b)/255 for r, g, b in atlas.game.palette]
    old = unpack(former(game_dir, earlier, __file__))
    fitted = unpack(former(game_dir, refit, __file__))
    current = unpack(capture(game_dir))
    tiles = {}
    counts = {}
    for obj, _, _ in PEOPLE:
        for pose in range(29):
            base = current[obj, pose, "Class"]
            assert base == fitted[obj, pose, "Class"] == old[obj, pose, "Class"]
            live, suit = ({name: version[obj, pose, name] for name in SLOTS}
                          for version in (current, fitted))
            sample = trial(base, live, suit, light)
            variants = (base, old[obj, pose, "Plate"], live["Plate"], sample)
            side, _ = sprites.room(pose >= 15)
            ref = palette.tile(atlas.game.fr(1342 + int(pose >= 15), pose % 15), 0) if pose < 24 else None
            tiles[obj, pose] = [*(palette.tile(v, side) for v in variants), ref]
            counts[obj, pose] = [len(changes(base, v)) for v in (*variants[1:], suit["Plate"])]
    widths = {obj: shared_crop((tile for pose in range(29) for tile in tiles[obj, pose]), palette.floor)
              for obj, _, _ in PEOPLE}
    col = 177
    headings = ("Class outfit", "Earlier plate", "Current plate", "Midtone trial", "Retail armor")
    def board(pose):
        row_heights = {obj: 45 + (box[3] - box[1]) * 4 for obj, box in widths.items()}
        im = palette.board((5*col+12, 72+sum(row_heights.values())))
        palette.text(im, (10, 6), "Full plate  /  Midtone study", 20)
        palette.text(im, (im.width-10, 10), f"{pose:02d}  {dwarf.NAMES[pose]}   ·   3× and game size", 14, "ra")
        for i, heading in enumerate(headings):
            palette.text(im, (6 + col*i+col//2, 45), heading, 15, "ma")
        y = 69
        for obj, who, role in PEOPLE:
            ImageDraw.Draw(im).line((8, y, im.width-8, y), fill=palette.text_ramp[1])
            palette.text(im, (8, y+5), f"{who}  ·  {role}", 15)
            for i, tile in enumerate(tiles[obj, pose]):
                cx = 6+col*i+col//2
                if tile is None:
                    palette.text(im, (cx, y+68), "No matching pose", 12, "ma", muted=True)
                else:
                    stamp(im, tile, widths[obj], cx, y+32, 3)
            y += row_heights[obj]
        return im
    output.mkdir(parents=True, exist_ok=True)
    frames = [board(i) for i in range(29)]
    frames[0].convert("RGB").save(output/"plate-midtone-idle.png", optimize=True)
    frames[CYCLE[0]].save(output/"plate-midtone-poses.gif", save_all=True,
                          append_images=[frames[i] for i in CYCLE[1:]], loop=0, disposal=1,
                          duration=[900 if i < 3 or i >= 24 else 320 for i in CYCLE], optimize=True)
    for obj, _, role in PEOPLE:
        print(role, "earlier/current/trial/refitted max:", counts[obj, 0],
              "all poses:", [sum(counts[obj, pose][i] for pose in range(29)) for i in range(4)])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("game_dir", "output", "earlier_checkout", "refitted_checkout"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    render(args.game_dir, args.output, args.earlier_checkout, args.refitted_checkout)
