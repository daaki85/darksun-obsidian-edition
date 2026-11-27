"""Dress the two human inventory poses over the figure in the player's RESOURCE.GFF.

Each class's picture is a layer in inventory-garments.zip (`{figure}/body{class}`) over the stock
figure: a painted pixel replaces the stock one, CLEAR cuts back to the parchment, and an absent
pixel keeps the stock. A whole repainted figure is a layer too: the import command turns a picture
painted over the whole figure into one, keeping the stock head (HEAD) pixel for pixel unless told
not to, and drawing only in colours no area's palette changes (spritegear.STEADY). The inventory
is drawn in the area's palette, so a colour from the changing ranges (80-127 and the like) shows
as the painter meant only in some areas: the Druid's tan kilt was grey-green in the slave pens.

    python -m dsloader.inventoryart import GAME_DIR FIGURE CLASS PICTURE [--repaint-head]
    python -m dsloader.inventoryart steady GAME_DIR

FIGURE is 0 (man) or 1 (woman), CLASS 1-8 (Cleric, Druid, Fighter, Gladiator, Preserver,
Psionicist, Ranger, Thief). PICTURE is the whole figure at native size (48x95 for the man, 44x88
for the woman), on a transparent background or on the colour of its top-left pixel. `steady`
moves every layer's changing colours to fixed ones.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple
from zipfile import ZIP_DEFLATED, ZipFile

from . import art, icons

FIRST = 0x6000
CLEAR = 255  # A painted cutout exposes the parchment. An absent pixel keeps retail art.
HUMAN = tuple((c,) for c in range(1, 9))
GLADIATOR = ((4,),)
# Each figure's classes with a picture, by figure (0 the human man ... 11 the halfling woman): the
# humans in all eight, the other races' women as Gladiators (a single class: a multiclass falls back
# to the stock picture).
BUILDS = (HUMAN, HUMAN, (), GLADIATOR, (), GLADIATOR, (), GLADIATOR, (), GLADIATOR, (), GLADIATOR)
ARCHIVE = Path(__file__).with_name("inventory-garments.zip")
# The stock head each human figure keeps through every class, as (top, bottom, left, right),
# bottom and right excluded: the man's face below the stock helmet (his hair is the painter's, one
# for all classes), the woman's face, hair and tiara. The other races' figures keep no box.
HEAD = {0: (8, 15, 19, 32), 1: (0, 15, 14, 31)}

Rows = List[List[Optional[int]]]
RGB = Tuple[int, int, int]


def picture_id(figure, classes):
    return FIRST + (figure << 8) + sum(1 << (c - 1) for c in classes)


def chunks(resources):
    result = {}
    with ZipFile(ARCHIVE) as archive:
        for figure, builds in enumerate(BUILDS):
            original = resources.get(("BMP ", art.FIGURE_FIRST + figure))
            if not original:
                continue
            width, height, base = art.decode_frame(original)
            for classes in builds:
                w, h, paint = art.decode_frame(archive.read(f"{figure}/body{classes[0]}"))
                if (w, h) != (width, height):
                    continue  # Another edition or custom figure with different proportions.
                rows = [row[:] for row in base]
                for y, row in enumerate(paint):
                    for x, pixel in enumerate(row):
                        if pixel is not None:
                            rows[y][x] = None if pixel == CLEAR else pixel
                result["BMP ", picture_id(figure, classes)] = icons.encode(rows)
    return result


def _steady():
    from .spritegear import REGIONAL, STEADY
    return REGIONAL, STEADY


def nearest(rgb: RGB, colours: Sequence[RGB], allowed: Sequence[int]) -> int:
    """The entry of ALLOWED nearest RGB in COLOURS, weighed as the eye does."""
    r, g, b = rgb
    return min(allowed, key=lambda c: 3 * (colours[c][0] - r) ** 2 + 4 * (colours[c][1] - g) ** 2
               + 2 * (colours[c][2] - b) ** 2)


def layer_from_picture(picture: List[List[Optional[RGB]]], stock: Rows, colours: Sequence[RGB],
                       head: Optional[Tuple[int, int, int, int]] = None) -> Rows:
    """The layer that turns STOCK into PICTURE (rows of RGB, None where nothing is painted):
    None where the stock pixel stays (inside HEAD, or the same colour), CLEAR where the picture
    leaves a stock pixel bare, and elsewhere the nearest fixed colour."""
    if (len(picture), len(picture[0])) != (len(stock), len(stock[0])):
        raise ValueError(f"picture is {len(picture[0])}x{len(picture)}, the figure "
                         f"{len(stock[0])}x{len(stock)}")
    _, steady = _steady()
    found: Dict[RGB, int] = {}
    layer: Rows = []
    for y, (row, base) in enumerate(zip(picture, stock)):
        out: List[Optional[int]] = []
        for x, (rgb, old) in enumerate(zip(row, base)):
            if head and head[0] <= y < head[1] and head[2] <= x < head[3]:
                out.append(None)
            elif rgb is None:
                out.append(None if old is None else CLEAR)
            elif old is not None and tuple(colours[old]) == rgb:
                out.append(None)
            else:
                if rgb not in found:
                    found[rgb] = nearest(rgb, colours, steady)
                out.append(found[rgb])
        layer.append(out)
    return layer


def read_picture(path) -> List[List[Optional[RGB]]]:
    """PATH's pixels as RGB rows, None where transparent or the top-left pixel's colour."""
    from PIL import Image
    image = Image.open(path).convert("RGBA")
    w, h = image.size
    pixels = image.load()
    background = pixels[0, 0]
    return [[None if pixels[x, y][3] < 128 or pixels[x, y] == background else pixels[x, y][:3]
             for x in range(w)] for y in range(h)]


def steady_layer(layer: Rows, colours: Sequence[RGB]) -> Rows:
    """LAYER with every colour an area's palette may change moved to the nearest fixed one."""
    regional, steady = _steady()
    return [[nearest(colours[p], colours, steady) if p is not None and p != CLEAR and p in regional
             else p for p in row] for row in layer]


def _rewrite(entries: Dict[str, bytes]) -> None:
    with ZipFile(ARCHIVE) as archive:
        kept = {n: archive.read(n) for n in archive.namelist()}
    kept.update(entries)
    with ZipFile(ARCHIVE, "w", ZIP_DEFLATED) as archive:
        for name in sorted(kept):
            archive.writestr(name, kept[name])


def main(argv: List[str]) -> int:
    if len(argv) >= 5 and argv[0] == "import":
        game_dir, figure, cls, path = argv[1], int(argv[2]), int(argv[3]), argv[4]
        gameart = art.GameArt(game_dir)
        _, _, stock = art.decode_frame(gameart.figures[art.FIGURE_FIRST + figure])
        head = None if "--repaint-head" in argv else HEAD.get(figure)
        layer = layer_from_picture(read_picture(path), stock, gameart.colours, head)
        _rewrite({f"{figure}/body{cls}": icons.encode(layer)})
        painted = sum(p is not None for row in layer for p in row)
        print(f"{figure}/body{cls}: {painted} pixels over the stock figure")
        return 0
    if len(argv) == 2 and argv[0] == "steady":
        colours = art.GameArt(argv[1]).colours
        with ZipFile(ARCHIVE) as archive:
            entries = {}
            for name in archive.namelist():
                _, _, layer = art.decode_frame(archive.read(name))
                entries[name] = icons.encode(steady_layer(layer, colours))
        _rewrite(entries)
        print(f"{len(entries)} layers in steady colours")
        return 0
    print(__doc__.split("\n\n")[2], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
