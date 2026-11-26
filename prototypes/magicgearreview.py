"""Render all 29 equipped Loader poses with Shattered Lands' cycling palette indices.

python prototypes/magicgearreview.py GAME_DIR OUTPUT_DIR [race ...]
The floor, held figure and material pixels are stationary during each hold.
Pose holds are slowed for inspection. The palette runs follow their measured arena periods.
"""

import argparse
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw

from elfreview import CYCLE
from wornreview import Atlas, TERRAIN, dwarf, sg, sprites


CASES = ("Empty", "Magic leather", "Magic bone", "Magic cloak", "Magic bracers", "Magic boots")
RACES = {
    "human": ("Humans", ((300, "Man", "Psionicist", 724), (301, "Woman", "Priest", 1563))),
    "dwarf": ("Dwarves", ((302, "Man", "Cleric/Fighter", 1563),
                          (303, "Woman", "Fighter/Psionicist/Thief", 630))),
    "elf": ("Elves", ((304, "Man", "Preserver/Ranger", 724), (305, "Woman", "Cleric/Psionicist", 1563))),
    "half-elf": ("Half-elves", ((306, "Man", "Preserver", 724), (307, "Woman", "Fighter", 1252))),
    "half-giant": ("Half-giants", ((308, "Man", None, 1252), (309, "Woman", None, 1563))),
    "halfling": ("Halflings", ((310, "Man", None, 1252), (311, "Woman", None, 630))),
    "mul": ("Mul", ((312, "Mul", None, 1252),)),
    "thri-kreen": ("Thri-kreen", ((313, "Thri-kreen", None, 1252),)),
}
NPC_NAMES = {630: "Thief", 724: "Mage", 1252: "Warrior", 1563: "Priest"}
TICK_MS = 40
# Time between steps of each DAC colour run, measured in DOSBox on the arena map.
CYCLE_MS = {sg.GREEN_GLOW: 209, sg.VIOLET_GLOW: 167, sg.BLUE_GLOW: 84, sg.FIRE_GLOW: 167}
# Simultaneous native-index RGB samples from a settled Slave Pens frame.
# Keep the portrait palette for fixed colours in the Loader art comparisons.
SLAVE_PENS_GLOWS = {
    sg.FIRE_GLOW: ((255, 166, 0), (255, 125, 0), (255, 65, 0), (190, 16, 0), (190, 16, 0),
                   (255, 65, 0), (255, 125, 0), (255, 166, 0), (255, 211, 0)),
    sg.BLUE_GLOW: ((170, 162, 255), (125, 117, 231), (85, 85, 255), (85, 85, 255), (125, 117, 231)),
    sg.VIOLET_GLOW: ((199, 77, 255), (231, 162, 255), (211, 20, 255), (174, 32, 255), (162, 0, 255)),
    sg.GREEN_GLOW: ((0, 211, 81), (0, 255, 142), (0, 211, 81), (0, 166, 40), (0, 166, 40)),
}
LEFT, COL, TOP = 142, 143, 64


def arena_palette(game_palette):
    colors = list(game_palette)
    for group, indices in enumerate(sg.GLOWS):
        for index, rgb in zip(indices, SLAVE_PENS_GLOWS[group]):
            colors[index] = rgb
    return colors


def phase_map(tick):
    """Native palette lookups after TICK_MS times tick milliseconds on the map."""
    result = list(range(256))
    for group, run in enumerate(sg.GLOWS):
        steps = (tick * TICK_MS) // CYCLE_MS[group]
        for n, index in enumerate(run):
            result[index] = run[(n - steps) % len(run)]
    return result


def timeline():
    step = 0
    for pose in CYCLE:
        duration = 960 if pose < 3 or pose >= 24 else 320
        for _ in range(duration // TICK_MS):
            yield pose, step
            step += 1


class GalleryPalette:
    """Share one GIF palette; retain distinct cycled indices with equal RGB today."""

    def __init__(self, atlas, floor):
        game = arena_palette(atlas.game.palette)
        moving = {index for group in sg.GLOWS for index in group}
        fixed = list(dict.fromkeys(rgb for i, rgb in enumerate(game) if i not in moving))
        fixed += [rgb for _, rgb in floor.getcolors() if rgb not in fixed]
        fixed += [ImageColor.getrgb(c) for c in (dwarf.PAPER, dwarf.INK, dwarf.MUTED)
                  if ImageColor.getrgb(c) not in fixed]
        paper, ink = (ImageColor.getrgb(c) for c in (dwarf.PAPER, dwarf.INK))
        text_ramp = [tuple(round((a*(5-i) + b*i)/5) for a, b in zip(paper, ink)) for i in range(6)]
        fixed += [rgb for rgb in text_ramp if rgb not in fixed]
        self.rgb = {rgb: i for i, rgb in enumerate(fixed)}
        self.text_ramp = [self.rgb[rgb] for rgb in text_ramp]
        colors = fixed[:]
        self.index = []
        for i, rgb in enumerate(game):
            if i in moving:
                self.index.append(len(colors))
                colors.append(rgb)
            else:
                self.index.append(self.rgb[rgb])
        if len(colors) > 256:
            raise ValueError("Game palette and arena tile exceed one GIF palette")
        self.data = bytes(channel for rgb in colors for channel in rgb).ljust(768, b'\0')
        self.floor = Image.new("P", floor.size)
        self.floor.putpalette(self.data)
        self.floor.putdata([self.rgb[floor.getpixel((x, y))]
                            for y in range(self.floor.height) for x in range(self.floor.width)])

    def board(self, size):
        im = Image.new("P", size, self.rgb[ImageColor.getrgb(dwarf.PAPER)])
        im.putpalette(self.data)
        return im

    def at_phase(self, frame, phase):
        table = list(range(256))
        for source, target in enumerate(phase_map(phase)):
            table[self.index[source]] = self.index[target]
        return frame.point(table)

    def tile(self, rows, left):
        tile = self.floor.copy()
        width = len(rows[0]) - left*2
        ox = (tile.width-width)//2 - left
        oy = tile.height-2-len(rows)
        for y, row in enumerate(rows):
            for x, p in enumerate(row):
                if p is not None:
                    tx, ty = x+ox, y+oy
                    if not (0 <= tx < tile.width and 0 <= ty < tile.height):
                        raise ValueError(f"Visible pixel outside review tile at {(tx, ty)}")
                    tile.putpixel((tx, ty), self.index[p])
        return tile

    def text(self, board, position, text, size=13, anchor="la", muted=False):
        font = dwarf.board_font(size)
        left, top, right, bottom = font.getbbox(text, anchor=anchor)
        mask = Image.new("L", (right-left, bottom-top))
        ImageDraw.Draw(mask).text((-left, -top), text, font=font, fill=255, anchor=anchor)
        levels = 4 if muted else 5
        stamp = mask.point([self.text_ramp[round(c*levels / 255)] for c in range(256)], mode="P")
        board.paste(stamp, (position[0]+left, position[1]+top))


def draw_pose(atlas, palette, title, subjects, pose):
    row_height = palette.floor.height * 4 + 4
    board = palette.board((LEFT + COL*(len(CASES)+1)+6, TOP + row_height*len(subjects)+6))
    palette.text(board, (8, 6), f"{title}  /  Magical equipment", 18)
    palette.text(board, (board.width-8, 8), f"{pose:02d}   {dwarf.NAMES[pose]}", 15, "ra")
    combat, frame = divmod(pose, 15)
    side, _ = sprites.room(combat)
    for col, label in enumerate((*CASES, "Retail reference")):
        palette.text(board, (LEFT+col*COL+COL//2, 40), label, 13, "ma")
    for r, (obj, gender, role, ref) in enumerate(subjects):
        y = TOP + row_height*r
        palette.text(board, (10, y+18), gender, 16)
        parts = role.split("/") if role else []
        names = [role] if role and len(role) <= 16 else parts
        for j, part in enumerate(names):
            palette.text(board, (10, y+45+j*16), part, 12)
        if not role:
            palette.text(board, (10, y+45), "Base figure", 12)
        palette.text(board, (10, y+row_height-34), "3× and game size", 11, muted=True)
        for col, item in enumerate((*CASES, None)):
            x = LEFT + col*COL + COL//2
            if item is None:
                if pose >= 27:
                    palette.text(board, (x, y+56), "No matching pose", 12, "ma", muted=True)
                    continue
                rows = atlas.game.fr(ref+combat, frame)
                tile = palette.tile(rows, 0)
                palette.text(board, (x-25, y+palette.floor.height*3+12), NPC_NAMES[ref], 11, "ra", muted=True)
            else:
                rows = atlas.sequence(obj, bool(combat), role, item)[frame]
                tile = palette.tile(rows, side)
            # Keep a fixed, foot-registered crop, including the giant's hair and
            # the far edge of a rear-facing cape. Validate both horizontal edges.
            bounds = (3, 0, 49, tile.height)
            for a, b in ((0, bounds[0]), (bounds[2], tile.width)):
                strip = (a, 0, b, tile.height)
                if tile.crop(strip).tobytes() != palette.floor.crop(strip).tobytes():
                    raise ValueError(f"Side of review tile cuts into {obj} {pose} {item}")
            cut = tile.crop(bounds)
            board.paste(cut.resize((cut.width*3, cut.height*3), Image.Resampling.NEAREST),
                        (x-cut.width*3//2, y))
            board.paste(cut, (x-cut.width//2, y+cut.height*3+2))
    return board


def render(atlas, output, races):
    from magicgearitems import loadouts

    atlas.gear.update(loadouts(atlas))
    output.mkdir(parents=True, exist_ok=True)
    for race in races:
        title, subjects = RACES[race]
        floor = atlas.floor
        if race == "half-giant":
            # The raised hand reaches above the ordinary 44-pixel terrain sample.
            with Image.open(TERRAIN) as arena:
                floor = arena.convert("RGB").crop((50, 142, 102, 194))
        palette = GalleryPalette(atlas, floor)
        poses = [draw_pose(atlas, palette, title, subjects, pose) for pose in range(29)]
        tick = (palette.at_phase(poses[pose], phase) for pose, phase in timeline())
        first = next(tick)
        path = output / f"magic-gear-{race}.gif"
        first.save(path, save_all=True, append_images=tick, duration=TICK_MS, loop=0,
                   disposal=1, optimize=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("races", nargs="*", metavar="RACE")
    args = parser.parse_args()
    render(Atlas(args.game_dir), args.output, args.races or RACES)
