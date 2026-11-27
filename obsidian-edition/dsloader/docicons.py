"""The items' icons for the item tables (ITEMS.md), drawn from the game's data as the game
shows them: `python -m dsloader.docicons GAME_FOLDER` writes docs/items/*.png from the
Loader's copy of SEGOBJEX.GFF (dos/, with its icons: start the game from the Loader once) and
the game's palette (its GPLDATA.GFF), each picture twice its size, the rest transparent.

ICONS: each image's name and the object whose picture it is (an item's +0, negated).

RAV_ICONS: the same for Wake of the Ravager's items (ITEMS.md's "Wake of the Ravager's items"), drawn from
the sequel's own OBJEX.GFF and palette (RESOURCE.GFF's PAL 1000; its pictures in the PLNR form, wotrart):
`python -m dsloader.docicons GAME_FOLDER --ravager WOTR_FOLDER` writes those as well."""

import itertools
import os
import struct
import sys
import zlib
from typing import Dict, List, Optional, Sequence, Tuple

from . import art, gff, icons, wotrart

ZOOM = 2
LEDGER = {name: number for name, _, number, _, _ in icons.ICONS}
# a Loader item's picture under another name: the metal Short Sword, as the other metal weapons are
RENAMED = {"Short Sword": "metal-short-sword"}

ICONS: Dict[str, int] = {
    # the Loader's (icons.py)
    **{RENAMED.get(name, name.lower().replace("'", "").replace(" ", "-").replace("+", "plus")): number
       for name, number in LEDGER.items()},
    "bone-scale-arm-armor": 1034, "bone-scale-leg-armor": 1035,
    "tome-of-understanding": 1446, "kalzith-scroll": 1440, "gythka-plus2": 2534,
    # the game's magic items
    "swiftbite": 2641, "draketooth": 30002, "hornblade": 2270, "gythka-plus3": 2271, "mace-plus2": 2642,
    "polearm-plus1": 1577, "cahulaks-plus1": 30003, "cahulaks-plus2": 2672, "dragonsbane": 2605, "els-drinker": 30001,
    "dags-dagger": 30005, "soulcrusher": 1607, "axe-plus1": 2284, "dark-flame": 30000, "bloodwrath": 1576,
    "terror-blade": 2041, "blackmace": 30006, "quarterstaff-plus2": 2272, "balks-staff": 30004,
    "parting-staff": 30044, "great-axe-plus3": 1018, "bow-plus2": 1039, "phrains-bow": 30007,
    "sling-plus2": 2533, "chatkcha-plus1": 2646, "arrows-plus3": 2273, "shimmer-armor": 30014,
    "drake-armor": 30013, "silk-armor": 2008, "tanelyvs-chest-armor": 2004, "tanelyvs-arm-armor": 1362, "tanelyvs-leg-armor": 1363,
    "greys-scale-arms": 2518, "greys-scale-legs": 2531, "wand-of-metal-detection": 30120, "stone-pick": 1381, "helm-of-might": 1519, "leather-helm": 1021,
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
    "staff-sling": 1016,
}

# Wake of the Ravager's items, by the sequel's object (its OJFF's picture): its magic items (their own objects,
# 600 on and 30000 on) and its plain weapons and chest armour (the picture its items show). Four of its items have
# no picture in its data (the Metal Dagger +1 and +2, Darts +1 and the Net +1, objects 731, 745, 732, 735).
RAV_ICONS: Dict[str, int] = {
    # magic weapons
    "wotr-stone-dagger-plus1": 631, "wotr-stone-dagger-plus2": 648, "wotr-quarterstaff-plus1": 632, "wotr-quarterstaff-plus2": 646,
    "wotr-quarterstaff-plus3": 665, "wotr-staff-paralysis": 30017, "wotr-metal-longsword-plus1": 633,
    "wotr-metal-longsword-plus2": 650, "wotr-obsidian-longsword-plus2": 645, "wotr-els-drinker": 681,
    "wotr-life-stealer": 682, "wotr-jasmine": 683, "wotr-mace-plus1": 634, "wotr-mace-plus2": 647,
    "wotr-axe-plus1": 635, "wotr-axe-plus2": 651, "wotr-lotulis-plus1": 637, "wotr-lotulis-plus2": 652,
    "wotr-double-spear-plus1": 636, "wotr-double-spear-plus3": 664, "wotr-trikal-plus2": 653,
    "wotr-gythka-plus1": 630, "wotr-gythka-plus3": 660, "wotr-great-axe-plus3": 661, "wotr-cahulaks-plus3": 662,
    "wotr-twohand-sword-plus3": 663, "wotr-polearm-plus3": 666,
    "wotr-toothed-club": 30014, "wotr-beast-club": 30016, "wotr-crystal-sword": 30015,
    "wotr-promere-hammer": 30000, "wotr-bloodletter": 30037,
    # missile weapons and ammunition
    "wotr-chatchka-focus-heat": 31213, "wotr-sling-plus2": 747, "wotr-javelin-plus2": 748, "wotr-javelin-lightning": 30023, "wotr-staff-sling-plus3": 762,
    "wotr-bow-of-accuracy": 760, "wotr-arrows-plus1": 730, "wotr-arrows-plus2": 746, "wotr-arrows-plus3": 761,
    "wotr-arrow-of-harm": 30024, "wotr-arrow-of-binding": 30025,
    # armour and worn items
    "wotr-promeres-armor": 802, "wotr-scale-armor-plus1": 852, "wotr-leather-armor-plus3": 853,
    "wotr-shield-plus1": 842, "wotr-shield-plus3": 843, "wotr-helm-plus1": 831, "wotr-helm-plus3": 805,
    "wotr-helm-of-domination": 30021, "wotr-helm-gaze-reflection": 837, "wotr-bracers-plus1": 30007,
    "wotr-bracers-plus3": 30008, "wotr-belt": 836, "wotr-boots": 1603, "wotr-stalker-cloak": 30011,
    "wotr-gloves-plus3": 680, "wotr-scarab": 30010, "wotr-fire-ruby": 30001, "wotr-ioun-stone": 30012,
    "wotr-circlet-of-clarity": 30018, "wotr-ring": 31200,
    # held, or used from the pack
    "wotr-rod": 31202, "wotr-lyre-of-the-winds": 30003, "wotr-deck-of-illusions": 30034, "wotr-gem": 30020,
    "wotr-powerstone": 30033, "wotr-spellbook": 31002, "wotr-scroll": 31300, "wotr-bracelet": 31400,
    "wotr-potion": 31900, "wotr-fruit": 31940,
    # plain weapons
    "wotr-obsidian-dagger": 612, "wotr-club": 609, "wotr-obsidian-longsword": 614, "wotr-metal-longsword": 603,
    "wotr-bone-mace": 610, "wotr-metal-axe": 607, "wotr-obsidian-great-axe": 608, "wotr-stone-pick": 628,
    "wotr-quarterstaff": 605, "wotr-bone-polearm": 606, "wotr-gythka": 615, "wotr-cahulaks": 611,
    "wotr-twohand-sword": 604, "wotr-lotulis": 600, "wotr-double-spear": 602,
    "wotr-trikal": 653,  # (the plain trikal's own picture, 601, is in neither of the forms read here: the +2's)
    "wotr-javelin": 702, "wotr-bow": 700, "wotr-sling": 705,
    "wotr-staff-sling": 706, "wotr-arrows": 701,
    # plain armour (the chest pieces) and shields
    "wotr-leather-armor": 810, "wotr-ring-armor": 812, "wotr-brigandine-armor": 811, "wotr-scale-armor": 813,
    "wotr-chain-armor": 814, "wotr-leather-shield": 840, "wotr-wooden-shield": 841, "wotr-helm": 830,
    "wotr-bracers": 825,
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


PLAN = b"\xffPLAN"  # (the sequel's other icon form: PLNR's header and colour map, then every pixel's code, unpacked)


def decode_plan(chunk: bytes) -> List[List[int]]:
    """A PLAN icon's rows of palette numbers: as wotrart.decode_plnr's, its codes one a pixel (no repeats)."""
    offset, = struct.unpack_from("<I", chunk, 6)
    width, height = struct.unpack_from("<HH", chunk, offset)
    at = offset + 4
    if chunk[at:at + 5] != PLAN:
        raise ValueError("not a PLAN picture")
    bits = chunk[at + 5]
    colours = chunk[at + 6:at + 6 + (1 << bits)]
    codes = list(itertools.islice(wotrart._codes(chunk[at + 6 + (1 << bits):], bits), width * height))
    codes += [0] * (width * height - len(codes))
    return [[colours[c] for c in codes[y * width:(y + 1) * width]] for y in range(height)]


def ravager_rows(chunks, obj: int) -> Optional[List[List[Optional[int]]]]:
    """The sequel's object OBJ's picture (PLNR or PLAN), as rows of palette numbers (None: transparent)."""
    if ("OJFF", obj) not in chunks:
        return None
    number = struct.unpack_from("<H", chunks[("OJFF", obj)], icons.OJFF_ICON)[0]
    if ("BMP ", number) not in chunks:
        return None
    chunk = chunks[("BMP ", number)]
    try:
        rows = wotrart.decode_plnr(chunk)
    except ValueError:
        try:
            rows = decode_plan(chunk)
        except ValueError:
            return None
    return [[p or None for p in row] for row in rows]


def write_ravager(wotr_dir: str, out_dir: str) -> List[str]:
    """Each of RAV_ICONS into OUT_DIR as NAME.png, from the sequel in WOTR_DIR; the names it couldn't draw."""
    with open(os.path.join(wotr_dir, "OBJEX.GFF"), "rb") as f:
        chunks = gff.read_gff(f.read())
    with open(os.path.join(wotr_dir, "RESOURCE.GFF"), "rb") as f:
        palette = art.palette_colours(gff.read_gff(f.read())[("PAL ", 1000)])
    os.makedirs(out_dir, exist_ok=True)
    missing = []
    for name, obj in sorted(RAV_ICONS.items()):
        rows = ravager_rows(chunks, obj)
        if rows is None:
            missing.append(name)
            continue
        with open(os.path.join(out_dir, name + ".png"), "wb") as f:
            f.write(png(rows, palette))
    return missing


if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "docs", "items")
    args = sys.argv[1:]
    wotr = None
    if "--ravager" in args:
        at = args.index("--ravager")
        wotr = args[at + 1]
        del args[at:at + 2]
    gone = write(args[0], os.path.join(here, "dos", "SEGOBJEX.GFF"), out) if args else []
    if wotr:
        gone += write_ravager(wotr, out)
    print("not drawn:", ", ".join(gone) if gone else "none")
