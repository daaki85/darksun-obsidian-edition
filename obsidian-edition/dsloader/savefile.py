"""Reading the party from a Shattered Lands save file (SAVEnn.SAV).

The save holds the same structures as memory, so the viewer's layout decodes
it directly. That makes saves a quick way to check a layout without running
the game:
  SAVE chunk 5: the current region's creature table (58-byte records, party first)
  SAVE chunk 6: the party's character sheets (71-byte records)
"""

import struct
from typing import Tuple

from . import game
from .gff import Chunks, GffError, read_gff
from .layout import Layout

CREATURE_CHUNK = ("SAVE", 5)
SHEET_CHUNK = ("SAVE", 6)


def party_chunks(chunks: Chunks) -> Tuple[bytes, bytes]:
    """The party tables from a parsed save, with complete records and valid sheet links."""
    try:
        creatures, sheets = chunks[CREATURE_CHUNK], chunks[SHEET_CHUNK]
    except KeyError as err:
        kind, number = err.args[0]
        raise GffError(f"missing {kind} {number} chunk") from None
    if len(creatures) < game.PARTY_SIZE * game.CREATURE_SIZE or len(creatures) % game.CREATURE_SIZE:
        raise GffError("the save's creature records are incomplete")
    if not sheets or len(sheets) % game.SHEET_SIZE:
        raise GffError("the save's character sheets are incomplete")
    for at in range(0, game.PARTY_SIZE * game.CREATURE_SIZE, game.CREATURE_SIZE):
        if creatures[at + game.CREATURE_NAME]:
            index, = struct.unpack_from("<H", creatures, at + game.CREATURE_SHEET_INDEX)
            if (index + 1) * game.SHEET_SIZE > len(sheets):
                raise GffError("a party member's character sheet is missing")
    return creatures, sheets


class SaveMemory:
    """The save's creature table and sheet table laid end to end, read like guest memory."""

    def __init__(self, data: bytes):
        self.data = data

    def read(self, addr: int, size: int) -> bytes:
        start = max(addr, 0)
        return self.data[start:max(addr + size, start)]

    def snapshot(self) -> bytes:
        return self.data


def load_party(path: str, layout: Layout) -> SaveMemory:
    """Read a save and point `layout`'s slots at the party records inside it."""
    with open(path, "rb") as f:
        chunks = read_gff(f.read())
    try:
        creatures, sheets = party_chunks(chunks)
    except GffError as err:
        raise GffError(f"{path}: {err}") from err
    mem = SaveMemory(creatures + sheets)
    sheet = layout.records.get("sheet")

    creature = layout.name_record
    if not creature.stride:
        raise ValueError(f"The layout's {creature.name!r} record needs a stride to read saves")
    for slot in range(layout.count):
        layout.clear_slot(slot)
        base = slot * creature.stride
        name = layout.name.display(mem.read(base, creature.stride), 0)
        if name and name not in ("?", "-"):
            creature.slots[slot] = base
            if sheet is not None:  # the game's own link: the creature's sheet number
                if len(creatures) < base + creature.stride:
                    raise GffError("the save's creatures are cut short")
                index = struct.unpack_from("<H", creatures, base + game.CREATURE_SHEET_INDEX)[0]
                sheet.slots[slot] = len(creatures) + index * game.SHEET_SIZE
            layout.link_slot(slot, mem.data)
    return mem
