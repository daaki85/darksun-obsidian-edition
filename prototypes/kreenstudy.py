"""Study two kinds of pigment on the retail Thri-kreen's own thoracic plates."""
import argparse
from pathlib import Path

from PIL import Image

import outfits
from elfreview import TERRAIN, dwarf, elf, label, loop
from dsloader import spriteparts as sp


# Each row gives the inclusive ends of a visible strip of carapace at native
# resolution, starting at the named y. The narrowed / missing ends in the
# melee and bow cels are where a claw, elbow or bow crosses the shell.
PLATES = (
    (11, ((12,18),(12,18),(12,18),(13,17),(14,17))),  # front
    (11, ((9,13),(8,14),(8,14),(8,13),(8,12))),      # rear
    (10, ((19,23),(18,23),(18,22),(18,22),(18,21))), # profile
    (10, ((11,17),(11,17),(11,17),(12,16),(13,16))),
    (11, ((12,18),(12,18),(12,18),(13,17),(14,17))),
    (11, ((12,18),(12,18),(12,18),(13,17),(14,17))),
    (9,  ((11,17),(11,17),(11,17),(12,16),(13,16))),
    (10, ((9,13),(8,14),(8,14),(8,13),(8,12))),
    (11, ((10,14),(9,15),(9,15),(9,14),(9,13))),
    (11, ((9,13),(8,14),(8,14),(8,13),(8,12))),
    (10, ((9,13),(8,14),(8,14),(8,13),(8,12))),
    (9,  ((20,24),(19,24),(19,23),(19,23),(19,22))),
    (10, ((20,24),(19,24),(19,23),(19,23),(19,22))),
    (10, ((19,23),(18,23),(18,22),(18,22),(18,21))),
    (9,  ((20,24),(19,24),(19,23),(19,23),(19,22))),
    (10, ((9,13),(9,13),(9,13),(10,14),(11,14))),    # front strikes
    (10, ((15,20),(14,20),(14,19),(13,18),(12,16))),
    (10, ((12,16),(11,16),(11,15),(11,14))),
    (10, ((4,7),(4,8),(4,8),(5,9),(5,9))),           # rear strikes
    (11, ((8,13),(8,13),(8,13),(9,13),(10,13))),
    (9,  ((9,12),(9,12),(9,13),(10,13),(10,13))),
    (11, ((11,15),(12,16),(12,16),(12,16),(13,17))), # profile strikes
    (8,  ((17,20),(17,21),(16,20),(16,18))),          # the lower claws cross
    (8,  ((16,19),(15,18),(12,14),(12,16))),
    (11, ((13,17),(12,16),(12,15),(13,16),(12,15))), # bow
    (9,  ((4,7),(4,7),(4,7),(5,7))),
    (10, ((11,14),(11,14),(11,15))),                  # bow shaft below
    (14, ((8,12),(8,13),(9,14),(10,14))),             # recoil
    (12, ((12,17),(11,17),(11,16),(11,16),(11,15))), # fallen, back exposed
)

ROLES = ("Cleric", "Psionicist")
PIGMENTS = {
    "Cleric": (205, 194, 206, 121, 123, 199),
    "Psionicist": (69, 70, 71, 72, 73),
}
# Keep black incised lines and retail features showing through the pigment.
SHELL = frozenset((129, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142,
                   143, 179, 180, 181, 182, 183, 184, 185, 186, 200, 201))


def draw(game, pose):
    combat, frame = divmod(pose, 15)
    source = game.fr(sp.KREEN+combat, frame)
    out = {role: [row[:] for row in source] for role in ROLES}
    top, widths = PLATES[pose]
    bow = set()
    if combat and frame in sp.BOW_FRAMES:
        fig = game.fig(sp.KREEN)
        bow = game.bow(fig, source, fig.parts(combat, frame))
    for depth, (left, right) in enumerate(widths):
        y = top+depth
        for x in range(left, right+1):
            color = source[y][x]
            if color not in SHELL or (x,y) in bow:
                continue
            red, green, blue = game.palette[color]
            light = (3*red+6*green+blue)//300
            # Two short ivory strokes break at the joint. The teal fork
            # converges on the middle ridge; its dark lip follows the shell.
            offset = x-left
            if depth in (0, 1, 3) and offset in ((1, 2, 3) if depth != 1 else (0, 1)):
                out["Cleric"][y][x] = PIGMENTS["Cleric"][min(5, light+int(offset == 1))]
            middle = (left+right)//2
            spread = max(0, 2-depth)
            if x in (middle-spread, middle+spread) or (depth in (1, 2) and x == middle+spread+1):
                out["Psionicist"][y][x] = PIGMENTS["Psionicist"][min(4, light+int(x <= middle))]
    return {"Retail": source, **out}


def render(game_dir, output):
    game = outfits.Game(game_dir)
    sand = Image.open(TERRAIN).convert("RGB").crop((31, 126, 93, 176))
    stone = Image.open(TERRAIN.with_name("2026-11-09-figures-all-gone.png")).convert("RGB").crop((152, 18, 214, 68))
    names = ("Retail party", *ROLES, "Retail Thri-kreen")
    sheet = Image.new("RGB", (130+4*124, 57+100*29), dwarf.PAPER)
    label(sheet, (10, 7), "Thri-kreen shell pigment study", 19)
    for i, name in enumerate(names):
        label(sheet, (192+i*124, 33), name, 13, "ma")
    pages = []
    details = (0, 8, 12)
    still = Image.new("RGB", (768, 38+len(details)*207), dwarf.PAPER)
    label(still, (12, 6), "Thri-kreen   /   natural shell and pigment", 19)
    for pose, title in enumerate(dwarf.NAMES):
        cb, f = divmod(pose, 15)
        drawn = draw(game, pose)
        # Object 215's combat sheet ends before the player's hit and fall.
        # Keep the retail comparison on an explicitly labelled idle then.
        match = f < game.count(291+cb)
        npc = game.fr(291+cb, f) if match else game.fr(291, 0)
        figrows = (*drawn.values(), npc)
        page = Image.new("RGB", (768, 312), dwarf.PAPER)
        label(page, (12, 8), "Thri-kreen shell pigment study", 19)
        label(page, (756, 10), f"{pose:02}   {title}", 16, "ra")
        label(sheet, (6, 95+pose*100), f"{pose:02}   {title}", 12)
        for i, (name, rows) in enumerate(zip(names, figrows)):
            caption = name+" (idle)" if i == 3 and not match else name
            label(page, (96+192*i, 42), caption, 14, "ma")
            tile = elf.placed_tile(game, rows, sand, 1, 0, 0, 0)
            page.paste(tile.resize((186,150), Image.Resampling.NEAREST), (3+192*i, 68))
            page.paste(tile, (31+192*i, 230))
            page.paste(elf.placed_tile(game, rows, stone, 1, 0, 0, 0), (99+192*i, 230))
            sheet.paste(tile.resize((124,100), Image.Resampling.NEAREST), (130+124*i, 57+100*pose))
        pages.append(page)
        if pose in details:
            y = 38+details.index(pose)*207
            label(still, (12, y), f"{pose:02}   {title}", 15)
            for i, (name, rows) in enumerate(zip(names, figrows)):
                tile = elf.placed_tile(game, rows, sand, 1, 0, 0, 0)
                label(still, (96+192*i, y+23), name, 13, "ma")
                still.paste(tile.resize((124,100), Image.Resampling.NEAREST), (34+192*i, y+45))
                still.paste(tile, (65+192*i, y+151))

    output.mkdir(parents=True, exist_ok=True)
    still.save(output/"thri-kreen-markings.png")
    sheet.save(output/"thri-kreen-poses.png")
    loop(pages, output/"thri-kreen-markings.gif")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    render(args.game_dir, args.output)
