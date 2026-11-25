"""Compare the Mul singles with the other fitted races at native map scale."""
import argparse
from pathlib import Path

from PIL import Image

import halfelfstudy
import halfgiantstudy
import halflingsingles
import mulsingles
from elfreview import TERRAIN, dwarf, elf, label, loop
from outfitdetail import reference_folds
from wornreview import Atlas


RACES = {
    "Druid": ("Mul", "Human", "Half-elf", "Halfling"),
    "Psionicist": ("Mul", "Human", "Half-elf", "Dwarf", "Elf", "Halfling", "Half-giant"),
    "Thief": ("Mul", "Human", "Half-elf", "Dwarf", "Elf", "Halfling"),
}
# Keep the Mul first and choose references that expose the overlap in each pose.
STILLS = (
    ("Druid", 8, (("Human", 0), ("Human", 1), ("Half-elf", 0), ("Halfling", 1))),
    ("Psionicist", 24, (("Human", 0), ("Elf", 1), ("Dwarf", 0), ("Half-giant", 0))),
    ("Thief", 8, (("Human", 0), ("Dwarf", 1), ("Elf", 0), ("Halfling", 0))),
    ("Thief", 12, (("Human", 0), ("Half-elf", 1), ("Elf", 0), ("Halfling", 1))),
)


def paint_sample(page, x, y, tile):
    # The full source tile is kept for the half-giant reach and raised bows.
    page.paste(tile.resize((162, 153), Image.Resampling.NEAREST), (x, y))
    page.paste(tile, (x+54, y+156))


def render(game_dir, output):
    atlas = Atlas(game_dir)
    study = halfelfstudy.Study(game_dir)
    game = atlas.game
    floor = Image.open(TERRAIN).convert("RGB").crop((39, 130, 93, 181))
    atlas.floor = study.floor = floor
    swatches = reference_folds(game)
    loops = {role: [] for role in RACES}
    still = Image.new("RGB", (846, 36+len(STILLS)*264), dwarf.PAPER)
    label(still, (12, 7), "Mul class outfits beside other races", 20)
    for pose, name in enumerate(dwarf.NAMES):
        mul = mulsingles.draw(game, pose, swatches)
        tiles = {}
        for sex in (0, 1):
            small = halflingsingles.draw(game, 2068+2*sex, pose, swatches)
            giant = halfgiantstudy.study_rows(game, 2072+2*sex, pose, swatches["linen"])
            halfelf = halfelfstudy.FIGURES[1-sex]
            for role, races in RACES.items():
                for race in races:
                    if race in ("Human", "Dwarf", "Elf"):
                        obj = {"Human": 300, "Dwarf": 302, "Elf": 304}[race]+sex
                        tile = atlas.tile(obj, pose, role, "Class colors", 1)
                    elif race == "Half-elf":
                        tile = study.tile(halfelf, pose, role, 1)
                    else:
                        rows = {"Mul": mul, "Halfling": small, "Half-giant": giant}[race][role]
                        tile = elf.placed_tile(game, rows, floor, 1, 0, 0, 0)
                    tiles[role, race, sex] = tile
        for role, races in RACES.items():
            width = 72+len(races)*166
            page = Image.new("RGB", (width, 480), dwarf.PAPER)
            label(page, (12, 6), f"{role} fittings", 20)
            label(page, (width-12, 8), f"{pose:02}   {name}", 16, "ra")
            for j, race in enumerate(races):
                x = 67+j*166
                label(page, (x+81, 38), "Mul (shared)" if race == "Mul" else race, 14, "ma")
                for sex in (0, 1):
                    y = 58+211*sex
                    if j == 0:
                        label(page, (7, y+90), ("Male", "Female")[sex], 14)
                    paint_sample(page, x, y, tiles[role, race, sex])
            loops[role].append(page)
        for row, (role, chosen, others) in enumerate(STILLS):
            if pose != chosen:
                continue
            y = 42+row*264
            label(still, (12, y), f"{role}   /   {name} ({pose:02})", 16)
            for j, (race, sex) in enumerate((("Mul", 0),)+others):
                x = 9+167*j
                caption = "Mul" if race == "Mul" else f"{race} {('man', 'woman')[sex]}"
                label(still, (x+81, y+26), caption, 14, "ma")
                paint_sample(still, x, y+49, tiles[role, race, sex])
    output.mkdir(exist_ok=True, parents=True)
    still.save(output/"mul-race-comparison.png")
    for role, frames in loops.items():
        loop(frames, output/f"mul-race-{role.lower()}.gif")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    render(args.game_dir, args.output)
