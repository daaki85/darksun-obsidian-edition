"""Dress the two human inventory poses over the figure in the player's RESOURCE.GFF."""

from pathlib import Path
from zipfile import ZipFile

from . import art, icons

FIRST = 0x6000
CLEAR = 255  # A painted cutout exposes the parchment. An absent pixel keeps retail art.
HUMAN = tuple((c,) for c in range(1, 9))
BUILDS = (HUMAN, HUMAN)


def picture_id(figure, classes):
    return FIRST + (figure << 8) + sum(1 << (c - 1) for c in classes)


def chunks(resources):
    result = {}
    with ZipFile(Path(__file__).with_name("inventory-garments.zip")) as archive:
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
