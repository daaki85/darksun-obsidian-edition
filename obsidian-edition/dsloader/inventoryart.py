"""Full-length inventory portraits. The fitted garment layers contain only new pixels.
Combine them with the figure in the player's RESOURCE.GFF. DOS requests the selected
creature's outfit every time the inventory draws a portrait (DSCLOG's inventory_figure).
"""

from pathlib import Path
from zipfile import ZipFile

from . import art, classoutfits, icons

FIRST = 0x6000
KREEN = (
    (1,),
    (2,),
    (3,),
    (4,),
    (6,),
    (7,),
    (1, 3),
    (1, 6),
    (1, 7),
    (2, 3),
    (2, 6),
    (3, 6),
    (6, 7),
    (1, 3, 6),
    (1, 6, 7),
    (2, 3, 6),
)
HUMAN = tuple((c,) for c in range(1, 9))
# Cilla's original Preserver/Druid/Thief combination is unique to the ready-made party.
ELF = (*classoutfits.ELF_ROLES, (2, 5, 8))
BUILDS = (
    HUMAN,
    HUMAN,
    classoutfits.DWARF_ROLES,
    classoutfits.DWARF_ROLES,
    ELF,
    ELF,
    classoutfits.HALF_ELF_ROLES,
    classoutfits.HALF_ELF_ROLES,
    classoutfits.HALF_GIANT_ROLES,
    classoutfits.HALF_GIANT_ROLES,
    classoutfits.HALFLING_ROLES,
    classoutfits.HALFLING_ROLES,
    classoutfits.MUL_ROLES,
    KREEN,
)


def picture_id(figure, classes):
    return FIRST + (figure << 8) + sum(1 << (c - 1) for c in classes)


def pieces(figure, classes):
    if figure == 13:
        return [f"mark{c}" for c in classes]
    # Keep the robe or kilt as the foundation. A second class contributes its
    # identifying cut or material in a different part of the portrait.
    main = next(c for c in (1, 2, 5, 7, 3, 4, 8, 6) if c in classes)
    layers = [f"body{main}"]
    for cls, accent in ((7, "green"), (5, "mantle"), (3, "bone"), (6, "sash"), (8, "hood")):
        if cls != main and cls in classes:
            layers.append(accent)
    return layers


def chunks(resources):
    result = {}
    with ZipFile(Path(__file__).with_name("inventory-garments.zip")) as archive:
        for figure, builds in enumerate(BUILDS):
            original = resources.get(("BMP ", art.FIGURE_FIRST + figure))
            if not original:
                continue
            width, height, base = art.decode_frame(original)
            layers = {}
            for classes in builds:
                rows = [row[:] for row in base]
                for name in pieces(figure, classes):
                    if name not in layers:
                        w, h, paint = art.decode_frame(archive.read(f"{figure}/{name}"))
                        if (w, h) != (width, height):
                            break  # another edition or a custom portrait with a different pose
                        layers[name] = [
                            (x, y, p)
                            for y, row in enumerate(paint)
                            for x, p in enumerate(row)
                            if p is not None
                        ]
                    for x, y, pixel in layers[name]:
                        rows[y][x] = pixel
                else:
                    result["BMP ", picture_id(figure, classes)] = icons.encode(rows)
    return result
