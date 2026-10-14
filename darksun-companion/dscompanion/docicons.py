"""The items' icons for the guide's tables (README.md), drawn from the game's data as the game
shows them: `python -m dscompanion.docicons GAME_FOLDER` writes docs/items/*.png from the
Loader's copy of SEGOBJEX.GFF (dos/, with its icons: start the game from the Loader once) and
the game's palette (its GPLDATA.GFF), each picture twice its size, the rest transparent.

ICONS: each image's name and the object whose picture it is (an item's +0, negated)."""

import os
import struct
import sys
import zlib
from typing import Dict, List, Optional, Sequence, Tuple

from . import art, gff, icons

ZOOM = 2
LEDGER = {name: number for name, _, number, _, _ in icons.ICONS}

ICONS: Dict[str, int] = {
    # the Loader's (icons.py)
    **{name.lower().replace("'", "").replace(" ", "-").replace("+", "plus"): number
       for name, number in LEDGER.items()},
    "bone-scale-arm-armor": 1034, "bone-scale-leg-armor": 1035, "thieves-tools": 1068,
    "tome-of-understanding": 1446, "kalzith-scroll": 1440, "gythka-plus2": 2534,
    # the game's magic items
    "swiftbite": 2641, "draketooth": 30002, "hornblade": 2270, "gythka-plus3": 2271, "mace-plus2": 2642,
    "polearm-plus1": 1577, "cahulaks-plus1": 30003, "dragonsbane": 2605, "els-drinker": 30001,
    "dags-dagger": 30005, "soulcrusher": 1607, "axe-plus1": 2284, "dark-flame": 30000, "bloodwrath": 1576,
    "terror-blade": 2041, "blackmace": 30006, "quarterstaff-plus2": 2272, "balks-staff": 30004,
    "parting-staff": 30044, "great-axe-plus3": 1018, "bow-plus2": 1039, "phrains-bow": 30007,
    "sling-plus2": 2533, "chatkcha-plus1": 2646, "arrows-plus3": 2273, "shimmer-armor": 30014,
    "drake-armor": 30013, "silk-armor": 2008, "tanelyvs-arm-armor": 1362, "tanelyvs-leg-armor": 1363,
    "greys-scale-arms": 2531, "greys-scale-legs": 2518, "helm-of-might": 1519, "leather-helm": 1021,
    "helm-of-contemplation": 30019, "els-shield": 30015, "drake-shield": 30016, "chameleon-gloves": 30020,
    "quicksilver-gauntlets": 30021, "belt-of-might": 30017, "serpent-boots": 31013, "living-cloak": 30022,
    "silver-necklace": 30018, "obsidian-necklace": 31011, "iron-necklace": 31012, "golden-torque": 30052,
    "light-of-dawn": 30008, "steadfast-ring": 30009, "ring-of-insight": 30010, "els-ring": 30012,
    "storm-ring": 31010, "wind-ring": 30011, "orb-of-knowledge": 31014, "dagolars-wand": 31006,
    "wand-of-missiles": 31007, "derths-wand": 31008, "wildwynd-wand": 31009, "llods-rod": 30114,
    "scroll": 1400, "apple": 31024,
    # the game's plain weapons
    "bone-long-sword": 1012, "obsidian-long-sword": 1013, "metal-long-sword": 1014, "club": 1185,
    "obsidian-dagger": 1184, "stone-dagger": 1190, "bone-mace": 1187, "metal-axe": 1183, "quarterstaff": 1019,
    "bone-polearm": 1186, "gythka": 1011, "cahulaks": 1188, "chatkcha": 1010, "bow": 1017, "sling": 1015,
    "staff-sling": 1016, "stone-pick": 1381,
}


def rows_of(chunks, obj: int) -> Optional[List[List[Optional[int]]]]:
    """Object OBJ's picture, as rows of palette numbers (None: transparent)."""
    if ("OJFF", obj) not in chunks:
        return None
    number = struct.unpack_from("<H", chunks[("OJFF", obj)], icons.OJFF_ICON)[0]
    if ("BMP ", number) not in chunks:
        return None
    return icons.decode(chunks[("BMP ", number)])


def png(rows: Sequence[Sequence[Optional[int]]], palette: Sequence[Tuple[int, int, int]], zoom: int = ZOOM) -> bytes:
    """An RGBA PNG of ROWS, ZOOM times its size."""
    width = max((len(r) for r in rows), default=0) * zoom
    raw = b""
    for row in rows:
        line = b""
        for p in list(row) + [None] * (width // zoom - len(row)):
            line += (bytes(palette[p]) + b"\xff" if p is not None else bytes(4)) * zoom
        raw += (b"\0" + line) * zoom

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    header = struct.pack(">IIBBBBB", width, len(rows) * zoom, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def write(game_dir: str, objects_file: str, out_dir: str) -> List[str]:
    """Each of ICONS into OUT_DIR as NAME.png; the names it couldn't draw."""
    with open(objects_file, "rb") as f:
        chunks = gff.read_gff(f.read())
    with open(os.path.join(game_dir, "GPLDATA.GFF"), "rb") as f:
        palette = art.palette_colours(gff.read_gff(f.read())[("PAL ", 1)])
    os.makedirs(out_dir, exist_ok=True)
    missing = []
    for name, obj in sorted(ICONS.items()):
        rows = rows_of(chunks, obj)
        if rows is None:
            missing.append(name)
            continue
        with open(os.path.join(out_dir, name + ".png"), "wb") as f:
            f.write(png(rows, palette))
    return missing


if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gone = write(sys.argv[1], os.path.join(here, "dos", "SEGOBJEX.GFF"), os.path.join(here, "docs", "items"))
    print("not drawn:", ", ".join(gone) if gone else "none")
