"""The game's item types and item names, with the Loader's own after them, in the Loader's copy
of GPLDATA.GFF.

The game reads its item types (GPLDATA's IT1R chunk: 115 of 20 bytes) and its item names (the
NAME chunk: 322 of 25 bytes) into memory as it starts and as each game is loaded, reserving as
much memory as the chunk is long; an item names its type and its name by number, and nothing in
the game checks either number against its own count. So the Loader's copy of the file has the
chunks grown: npcitems.TYPES after the game's types (numbered from game.GAME_TYPES) and
names.NAMES after its names (from names.OWN), and a few of the game's own types mended
(TYPE_FIXES). DSCLOG used to keep both lists itself and copy them in as the game read the
chunks; here they take none of its memory (the seventh memory pass).

DSCLOG still notes where the game's tables are (PROBE_TYPES_FILL, PROBE_NAMES_FILL), and counts
the Loader's types as in (its TYPES_FIRST) only when the type chunk the game read has them: with
the game's own file (no copy written) it has not, and the Loader gives none of its items.
"""

from typing import Dict, Tuple

from . import game, gff, names, npcitems

TYPES_CHUNK, NAMES_CHUNK = ("IT1R", 1), ("NAME", 1)
TYPE_SIZE, NAME_SIZE = game.ITEM_TYPE_SIZE, game.ITEM_NAME_SIZE
GAME_NAMES = names.OWN

LEATHER, METAL = 5, 4  # a type's +8: its material's low nibble
AIR_CLERIC = 1  # a type's +10h (the classes that may use it): the air cleric's bit
# The game's own types mended: (type, byte, value, or-ed in (else set)). Grey's Scale's arm and
# leg armour (54, 24) AC 3 (the game's 2); the Great Axe +3's type (2) metal (the game gave it no
# material, so its name showed none; its icon's head is the metal axe's grey and teal, its weight
# the metal great axe's 70); the pick (112: the game's, Deepbiter's and the stone picks') the
# footman's pick's 1d6+1 (Skills & Powers; the game's 1d4+1); the Quicksilver Glove's type (113)
# leather (no material, which the game's to-hit and damage took for wood: the user's, 2026-11-09);
# and the game's daggers (17, 33, 84, 94) for air clerics too (none had their bit; their sphere's
# weapons are daggers and missile and thrown ones).
TYPE_FIXES = ((54, 0x12, 3, False), (24, 0x12, 3, False), (2, 8, METAL, False), (112, 0x0C, 6, False),
              (113, 8, LEATHER, False),
              (17, 0x10, AIR_CLERIC, True), (33, 0x10, AIR_CLERIC, True), (84, 0x10, AIR_CLERIC, True),
              (94, 0x10, AIR_CLERIC, True))


class ItemTablesError(ValueError):
    """The game's chunks aren't the size the Loader's numbers assume."""


def types_chunk(own: bytes) -> bytes:
    """The game's IT1R chunk OWN, mended (TYPE_FIXES), with npcitems.TYPES after it."""
    if len(own) != game.GAME_TYPES * TYPE_SIZE:
        raise ItemTablesError(f"IT1R is {len(own)} bytes, not the {game.GAME_TYPES * TYPE_SIZE} of "
                              f"{game.GAME_TYPES} types")
    out = bytearray(own)
    for kind, at, value, ored in TYPE_FIXES:
        at += kind * TYPE_SIZE
        out[at] = (out[at] | value) if ored else value
    for rec in npcitems.TYPES:
        assert len(rec) == TYPE_SIZE
        out += rec
    return bytes(out)


def names_chunk(own: bytes) -> bytes:
    """The game's NAME chunk OWN with names.NAMES after it, each padded to 25 bytes with NULs."""
    if len(own) != GAME_NAMES * NAME_SIZE:
        raise ItemTablesError(f"NAME is {len(own)} bytes, not the {GAME_NAMES * NAME_SIZE} of "
                              f"{GAME_NAMES} names")
    out = bytearray(own)
    for entry in range(GAME_NAMES, GAME_NAMES + names.EXTRA):
        name = names.NAMES[entry]
        assert len(name) < names.KEPT, name  # (15 letters at most, as the game's own)
        out += name.ljust(NAME_SIZE, b"\0")
    return bytes(out)


def chunks(gpldata: gff.Chunks) -> Dict[Tuple[str, int], bytes]:
    """For the Loader's copy of GPLDATA: the two chunks grown (GPLDATA the game's chunks)."""
    return {TYPES_CHUNK: types_chunk(gpldata[TYPES_CHUNK]), NAMES_CHUNK: names_chunk(gpldata[NAMES_CHUNK])}


def write(source: str, dest: str) -> None:
    """The game's GPLDATA.GFF (SOURCE, only read) with only the item chunks grown, to DEST: when
    the copy with the new scripts couldn't be written, so that the Loader's items still have
    their types and names."""
    from .icons import with_chunks
    with open(source, "rb") as f:
        data = f.read()
    gff.write_atomic(dest, with_chunks(data, chunks(gff.read_gff(data))))
