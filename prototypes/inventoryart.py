"""Pack the indexed human inventory plates. Pass the Shattered Lands game directory.

Each atlas row is one inventory pose. Columns follow the eight active class IDs.
Index zero preserves the installed art and index 255 cuts back to parchment.
"""

from pathlib import Path
import sys
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "obsidian-edition"))
from dsloader import art, icons, inventoryart


def main(game_dir):
    figures = art.GameArt(game_dir)
    dest = HERE.parent / "obsidian-edition/dsloader/inventory-garments.zip"
    with Image.open(HERE / "inventory-human.png") as atlas, ZipFile(dest, "w") as archive:
        for figure, builds in enumerate(inventoryart.BUILDS):
            w, h, _ = art.decode_frame(figures.figures[art.FIGURE_FIRST + figure])
            for (cls,) in builds:
                left, top = (cls - 1) * 48, figure * 95
                plate = atlas.crop((left, top, left + w, top + h))
                rows = [[plate.getpixel((x, y)) or None for x in range(w)] for y in range(h)]
                archive.writestr(ZipInfo(f"{figure}/body{cls}"), icons.encode(rows), ZIP_DEFLATED, 9)


if __name__ == "__main__":
    main(sys.argv[1])
