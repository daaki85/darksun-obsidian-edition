"""Prototype, not part of the Ledger: class outfits as presets of the gear the Loader already
draws (the back-up to outfits.py). Nothing here draws: a class is a few lines of a table, and the
pictures are made by the Loader's own code, as it makes them for worn gear in the game
(sprites.Pictures.build, spritegear.armed): the figure's clothes recoloured shade for shade
(chest, arms, legs), boots, and the human woman's cloak fitted to the wearer.

    python3 prototypes/presets.py GAME_DIR OUT_DIR

writes OUT_DIR/preset_<class>.png (the thirteen figures, the same twelve frames as outfits.py's
sheets) and OUT_DIR/preset_vs_outfit.png (three figures in each class: the game's own, the preset,
and outfits.py's picture).

What a preset can't do, being the gear's drawing and no more: cover skin (a figure drawn mostly
bare, the mul, the dwarves, changes little but for its cloak), a hood, a robe closed in front.

Each class's "items" are numbers no item of the game's has (PRESET_BASE and on), entered in
spritegear's tables of armour, cloak and boots colours when this module is loaded: in the Loader
they would be entries of those tables, and a class would wear them under whatever is really worn.
"""

import os
import sys
from typing import Dict, List, NamedTuple, Optional, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "obsidian-edition"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import art, halfelf, sprites, spritegear as sg  # noqa: E402
import outfits as O  # noqa: E402

PRESET_BASE = 0x7000


class Preset(NamedTuple):
    """A class's colours, each dark to light (None: that part as the figure has it)."""
    name: str
    chest: Optional[Tuple[int, ...]]
    arms: Optional[Tuple[int, ...]]
    legs: Optional[Tuple[int, ...]]
    boots: Optional[Tuple[int, ...]]
    cloak: Optional[Tuple[int, ...]]


BLUE, GREEN, RED = (158, 159, 38, 160, 71, 161), (69, 188, 53, 189, 54, 190), (129, 202, 195, 163, 32, 77)
LEATHER, SLATE = (129, 204, 203, 128, 205), (69, 210, 49, 24, 50)
PRESETS = [
    Preset("Warrior", LEATHER, None, LEATHER, LEATHER[:4], None),
    Preset("Thief", SLATE, None, SLATE, (69, 48, 210, 49), GREEN),
    Preset("Priest", RED, RED, RED, (69, 210, 194, 213), RED),
    Preset("Mage", (129, 128, 205, 180, 201), BLUE, (188, 53, 189, 54, 55, 56), (204, 129, 134, 136, 138), BLUE),
]


def wear(i: int) -> Tuple[Dict[str, Tuple[int, ...]], Tuple[int, ...]]:
    """Preset I as the gear and armour spritegear.armed takes, its colours entered in the tables."""
    p, base = PRESETS[i], PRESET_BASE + 16 * i
    armour = []
    for k, (piece, shades) in enumerate(((sg.ARMOUR_CHEST, p.chest), (sg.ARMOUR_ARMS, p.arms), (sg.ARMOUR_LEGS, p.legs))):
        if shades:
            sg.ARMOUR[base + k] = (piece, shades, sg.PLAIN)
            armour.append(base + k)
    gear: Dict[str, Tuple[int, ...]] = {}
    if p.boots:
        sg.BOOTS[base + 3] = p.boots
        gear["boots"] = (base + 3, 0)
    if p.cloak:
        sg.CLOAK_COLOURS[base + 4] = p.cloak
        gear["cloak"] = (base + 4, 0)
    return gear, tuple(armour)


def objects(pics: sprites.Pictures) -> Dict[object, int]:
    """The party object of each of outfits.py's figures (300 + the figure picked at creation)."""
    out: Dict[object, int] = {O.HALF_ELF_MAN: halfelf.MAN, O.HALF_ELF_WOMAN: halfelf.WOMAN}
    for obj in sprites.PARTY_OBJECTS:
        if obj not in (halfelf.MAN, halfelf.WOMAN) and pics.model(obj) in dict(O.FIGURES):
            out.setdefault(pics.model(obj), obj)
    return out


def pictures(pics: sprites.Pictures, obj: int, i: int) -> Tuple[bytes, bytes]:
    """A party object's walking and fighting pictures in preset I, as the Loader would write them."""
    gear, armour = wear(i)
    return pics.build(obj, False, gear, armour), pics.build(obj, True, gear, armour)


def frames(chunk: bytes) -> List[O.Rows]:
    import struct
    return [art.decode_frame(chunk, f)[2] for f in range(struct.unpack_from("<H", chunk, 4)[0])]


def draw(tile, rows, cx: int, base: int, palette) -> None:
    """A picture standing on BASE, its middle at CX (as the game stands a figure's picture)."""
    bx, by = cx - len(rows[0]) // 2, base - len(rows)
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c is not None and 0 <= bx + x < tile.width and 0 <= by + y < tile.height:
                tile.putpixel((bx + x, by + y), palette[c])


def main(argv: List[str]) -> None:
    from PIL import Image, ImageDraw, ImageFont
    if len(argv) < 2:
        raise SystemExit(__doc__)
    game = O.Game(argv[0])
    os.makedirs(argv[1], exist_ok=True)
    pics = sprites.Pictures(game.chunks)
    objs = objects(pics)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    except OSError:
        font = ImageFont.load_default()
    ink, ground = (40, 24, 12), (196, 150, 104)
    CW, CH, BASE, Z, LW, TOP = 52, 60, 54, 3, 170, 52
    made = {}
    for i, p in enumerate(PRESETS):
        img = Image.new("RGB", (LW + len(O.COLUMNS) * CW * Z, TOP + len(O.FIGURES) * CH * Z), ground)
        d = ImageDraw.Draw(img)
        d.text((8, 6), f"{p.name}: a preset of the Loader's own gear drawing (clothes recoloured, boots, the fitted cloak)", fill=ink, font=font)
        for ci, (name, _, _) in enumerate(O.COLUMNS):
            d.text((LW + ci * CW * Z + CW * Z // 2 - 20, 30), name, fill=ink, font=font)
        for mi, (key, label) in enumerate(O.FIGURES):
            walk, fight = (frames(c) for c in pictures(pics, objs[key], i))
            made[(i, key)] = (walk, fight)
            tile = Image.new("RGB", (len(O.COLUMNS) * CW, CH), ground)
            for ci, (_, cb, f) in enumerate(O.COLUMNS):
                draw(tile, (walk, fight)[cb][f], ci * CW + CW // 2, BASE, game.palette)
            img.paste(tile.resize((tile.width * Z, CH * Z), Image.NEAREST), (LW, TOP + mi * CH * Z))
            d.text((8, TOP + mi * CH * Z + CH * Z // 2 - 8), label, fill=ink, font=font)
        path = os.path.join(argv[1], f"preset_{p.name.lower()}.png")
        img.save(path, optimize=True)
        print(path)
    # three figures in each class: the game's own, the preset, outfits.py's
    who = [(2095, "human man"), (2059, "elf woman"), (2093, "mul")]
    cols = [(0, 0), (0, 1), (0, 2), (0, 12), (1, 1), (1, 7)]
    Z, CW, CH, BASE = 4, 46, 58, 52
    img = Image.new("RGB", (120 + len(who) * 3 * len(cols) * CW * Z // 3 * 1, 40 + len(PRESETS) * 3 * CH * Z), ground)
    img = Image.new("RGB", (150 + len(who) * len(cols) * CW * Z, 40 + len(PRESETS) * 3 * CH * Z), ground)
    d = ImageDraw.Draw(img)
    for wi, (_, label) in enumerate(who):
        d.text((150 + wi * len(cols) * CW * Z + 8, 10), label + ": front, back, side, walking, two attacks", fill=ink, font=font)
    npcs = {o.name: n for n, o in O.OUTFITS.items()}
    for i, p in enumerate(PRESETS):
        for k, kind in enumerate(("the game's own", "preset", "outfits.py")):
            y0 = 40 + (i * 3 + k) * CH * Z
            d.text((8, y0 + CH * Z // 2 - 16), p.name, fill=ink, font=font)
            d.text((8, y0 + CH * Z // 2 + 2), kind, fill=ink, font=font)
            tile = Image.new("RGB", (len(who) * len(cols) * CW, CH), ground)
            for wi, (key, _) in enumerate(who):
                full = game.full(key, npcs[p.name])
                for ci, (cb, f) in enumerate(cols):
                    cx = (wi * len(cols) + ci) * CW + CW // 2
                    if k == 0:
                        draw(tile, game.fig(key).rows(cb, f), cx, BASE, game.palette)
                    elif k == 1:
                        draw(tile, made[(i, key)][cb][f], cx, BASE, game.palette)
                    else:
                        rows, ox, oy, own = full[cb][f]
                        draw(tile, rows[:len(own) - oy], cx, BASE, game.palette)
            img.paste(tile.resize((tile.width * Z, CH * Z), Image.NEAREST), (150, y0))
    path = os.path.join(argv[1], "preset_vs_outfit.png")
    img.save(path, optimize=True)
    print(path)


if __name__ == "__main__":
    main(sys.argv[1:])
