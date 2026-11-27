"""Render the body, Gladiator and cloth comparisons from two checkouts.

python prototypes/materialfoldreview.py GAME_DIR OUTPUT_DIR --previous-checkout CHECKOUT
Use --previous-cloth-checkout when the wider cloth study has an earlier baseline.
Both checkouts must have the retail study tools.
"""
import argparse
from pathlib import Path
import zlib

from PIL import Image, ImageChops, ImageDraw

from bodyreview import body_tile, elf, half
from elfreview import CYCLE, label
import halfgiantstudy
import halflingstudy
import mulstudy
from platefitreview import former
from wornreview import Atlas, dwarf, sprites, TERRAIN

PEOPLE = ("Human man", "Human woman", "Dwarf man", "Dwarf woman", "Elf man", "Elf woman",
          "Half-elf man", "Half-elf woman", "Half-giant man", "Half-giant woman",
          "Halfling man", "Halfling woman", "Mul")
# Fixed direction within a row. Idle, four steps, then the three strike poses.
MATERIALS = (
    (300, "Psionicist", "Front", 1252), (301, "Psionicist", "Front", 1252),
    (308, "Psionicist", "Rear", 724), (309, "Ranger", "Rear", 630),
    (304, "Ranger", "Side", 630), (306, "Ranger/Thief", "Side", 630),
    (307, "Cleric/Thief", "Rear", 1563), (311, "Cleric", "Side", 1563),
    (312, "Druid/Thief", "Rear", 630))
DIRECTIONS = {"Front": (0, 3, 4, 5, 6, 15, 16, 17), "Rear": (1, 7, 8, 9, 10, 18, 19, 20),
              "Side": (2, 11, 12, 13, 14, 21, 22, 23)}
TILE = (54, 52)
KEY = (255, 0, 255)


def capture(game_dir):
    atlas = Atlas(game_dir)
    study = half.Study(game_dir)
    game = study.game
    study.floor = Image.new("RGB", TILE, KEY)
    linen = halfgiantstudy.reference_folds(game)["linen"]
    pictures = {}

    def save(obj, role, pose, tile):
        pictures[f"{obj}/{role}/{pose}"] = zlib.compress(tile.tobytes()).hex()

    def tile(rows, left=0):
        return elf.placed_tile(game, rows, study.floor, 1, left, 0, 0)

    for obj in range(300, 313):
        key = half.FIGURES[obj == 306] if obj in (306, 307) else atlas.pictures.model(obj)
        roles = ["Gladiator", *[r for o, r, _, _ in MATERIALS if o == obj]]
        for pose in range(29):
            cb, f = divmod(pose, 15)
            if obj < 308:
                body = body_tile(study, key, pose)
            else:
                if obj < 310:
                    rows = halfgiantstudy.study_rows(game, key, pose, linen)
                elif obj < 312:
                    rows = halflingstudy.rows_for(game, key, pose, linen)
                else:
                    rows = mulstudy.fitted_rows(game, pose)
                margin = half.co.FITTED_ARCHIVES[key][1]
                body = tile(rows["Body base"], margin)
            stock = game.fig(key).model
            save(obj, "Source", pose, tile(game.fr(stock + cb, f)))
            save(obj, "Body", pose, body)
            for role in roles:
                rows = atlas.sequence(obj, cb, role, "Class colors")[f]
                save(obj, role, pose, tile(rows, sprites.room(cb)[0]))
    for ref in {ref for _, _, _, ref in MATERIALS}:
        for cb in (0, 1):
            for f in range(game.count(ref + cb)):
                save(ref, "Retail", cb * 15 + f, tile(game.fr(ref + cb, f)))
    return pictures


def unpack(snapshot, floor):
    tiles = {}
    background = Image.new("RGB", TILE, KEY)
    for key, data in snapshot.items():
        sprite = Image.frombytes("RGB", TILE, zlib.decompress(bytes.fromhex(data)))
        diff = ImageChops.difference(sprite, background)
        r, g, b = diff.split()
        mask = ImageChops.lighter(ImageChops.lighter(r, g), b).point(lambda value: 255 if value else 0)
        result = floor.copy()
        result.paste(sprite, mask=mask)
        tiles[key] = result
    return tiles


def panel(title, captions, rows, zoom=2):
    tile_width, tile_height = rows[0][1][0].size
    col = tile_width * (zoom + 1) + 7
    row = 26 + tile_height * zoom + 2
    width = 10 + col * len(captions)
    im = Image.new("RGB", (width, 62 + len(rows) * row), dwarf.PAPER)
    label(im, (7, 4), title, 17)
    label(im, (width - 7, 7), f"{zoom}× and game size", 13, "ra")
    for j, cap in enumerate(captions):
        label(im, (5 + col * j + col // 2, 37), cap, 13, "ma")
    for i, (name, tiles) in enumerate(rows):
        y = 58 + i * row
        ImageDraw.Draw(im).line((5, y, width - 6, y), fill="#585148")
        label(im, (7, y + 3), name, 13)
        for j, t in enumerate(tiles):
            if t is not None:
                scaled = t.resize((tile_width * zoom, tile_height * zoom), Image.Resampling.NEAREST)
                x = 5 + col * j
                im.paste(scaled, (x, y + 23))
                im.paste(t, (x + scaled.width + 2, y + 23 + scaled.height - t.height))
    return im


def save_loop(frames, times, path):
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=times, loop=0, disposal=1)


def shoulders(before, after, output):
    frames = []
    for step, pose in enumerate(range(11, 15), 1):
        rows = []
        for obj, role in ((304, "Ranger"), (306, "Ranger/Thief")):
            key = f"{obj}/{role}/{pose}"
            rows.append((f"{PEOPLE[obj - 300]}   ·   {role}",
                         (before[key], after[key], after[f"630/Retail/{pose}"])))
        frames.append(panel(f"Cloak at the shoulder · step {step}/4", ("Earlier", "Revised", "Retail Thief"), rows, 3))
    frames[-1].save(output / "cloak-shoulder.png", optimize=True)
    save_loop(frames, [330, 330, 330, 850], output / "cloak-shoulder.gif")


def render(game_dir, output, previous, previous_cloth=None, bodies_only=False):
    with Image.open(TERRAIN) as image:
        sand = image.convert("RGB").crop((45, 142, 99, 194))
    with Image.open(TERRAIN.with_name("2026-11-09-figures-all-gone.png")) as image:
        paving = image.convert("RGB").crop((158, 20, 212, 72))
    raw_before = former(game_dir, previous, __file__)
    raw_after = capture(game_dir)
    output.mkdir(exist_ok=True, parents=True)
    for floor, surface in ((sand, "sand"), (paving, "stone")):
        before, after = unpack(raw_before, floor), unpack(raw_after, floor)

        def body_row(obj, pose):
            key = f"{obj}/Body/{pose}"
            gladiator = f"{obj}/Gladiator/{pose}"
            tiles = (before[key], after[key], before[gladiator], after[gladiator],
                     after[f"{obj}/Source/{pose}"], after.get(f"1252/Retail/{pose}"))
            return f"{PEOPLE[obj - 300]}   ·   {pose:02}  {dwarf.NAMES[pose]}", tiles
        body_labels = ("Earlier body", "Revised body", "Earlier Gladiator", "Revised Gladiator", "Retail source figure", "Retail Warrior")
        if surface == "stone":
            poses = (1, 14, 8, 8, 21, 6, 21, 9, 15, 17, 10, 10, 19)
            panel("Gladiators on paving", body_labels, [body_row(300 + i, f) for i, f in enumerate(poses)]).save(
                output / "gladiator-contrast-stone.png", optimize=True)
            continue
        if bodies_only:
            examples = []
            for obj, pose in ((300, 12), (303, 5), (304, 21), (307, 13), (309, 15), (310, 6), (312, 19)):
                body = f"{obj}/Body/{pose}"
                pictures = (after[f"{obj}/Source/{pose}"], before[body], after[body], after[f"{obj}/Gladiator/{pose}"])
                examples.append((f"{PEOPLE[obj - 300]}   ·   {pose:02}  {dwarf.NAMES[pose]}",
                                 [tile.crop((11, 7, 43, 52)) for tile in pictures]))
            panel("Light on exposed skin", ("Retail source", "Earlier body", "Revised body", "Gladiator"),
                  examples, zoom=4).save(output / "bare-body-closeups.png", optimize=True)
        for start, end, name in ((300, 306, "original-six"), (306, 313, "later-seven")):
            frames = [panel("Gladiators and exposed skin", body_labels,
                            [body_row(o, f) for o in range(start, end)]) for f in CYCLE]
            save_loop(frames, [850 if f < 3 or f >= 24 else 300 for f in CYCLE], output / f"gladiator-contrast-{name}.gif")
        if bodies_only:
            continue
        shoulders(before, after, output)
        if previous_cloth:
            before = unpack(former(game_dir, previous_cloth, __file__), floor)
        detail_poses = (0, 0, 7, 10, 14, 14, 19, 13, 7)
        rows = []
        for (obj, role, _, ref), pose in zip(MATERIALS, detail_poses):
            key = f"{obj}/{role}/{pose}"
            rows.append((f"{PEOPLE[obj - 300]}   ·   {role}   ·   {pose:02}  {dwarf.NAMES[pose]}",
                         (before[key], after[key], after[f"{ref}/Retail/{pose}"])))
        panel("Detail in the class outfits", ("Earlier", "Revised", "Shattered Lands"), rows, 3).save(
            output / "cloth-folds.png", optimize=True)
        for group, cases in (("wraps", MATERIALS[:4]), ("cloaks", MATERIALS[4:])):
            frames = []
            for step in range(8):
                rows = []
                for o, r, direction, ref in cases:
                    f = DIRECTIONS[direction][step]
                    key = f"{o}/{r}/{f}"
                    rows.append((f"{PEOPLE[o - 300]}   ·   {r}   ·   {f:02}  {dwarf.NAMES[f]}",
                                 (before[key], after[key], after[f"{ref}/Retail/{f}"])))
                frames.append(panel("Cloth on the arena floor", ("Earlier", "Revised", "Shattered Lands"), rows, 3))
            save_loop(frames, [950, 350, 350, 350, 600, 350, 350, 600], output / f"cloth-folds-{group}.gif")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--previous-checkout", type=Path, required=True)
    parser.add_argument("--previous-cloth-checkout", type=Path)
    parser.add_argument("--bodies-only", action="store_true", help="write the body and Gladiator comparisons only")
    args = parser.parse_args()
    render(args.game_dir, args.output, args.previous_checkout, args.previous_cloth_checkout, args.bodies_only)
