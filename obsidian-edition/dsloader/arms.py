"""Two plain weapons made magic (the MAGIC_ARMS switch, on unless turned off), in the game's data
(dataitems.py: the Loader's copy of SEGOBJEX, written as the game is started).

- The 2 handed Bone Gythka on the dead body lying by the stone arch in the arena, where every game
  starts: Kreenfang, a gythka +1. The body is the game's object 1204, "Dead Body" (an item whose
  contents are a list: its record has the gythka in it), used nowhere else; in the copy, that
  gythka is Kreenfang. Every other gythka stays plain: the one the arena also has lying loose
  (object 1011), and those in kreen hands.
- Kurzak's Short Sword (npcitems.py): Shadowseeker, a short sword +1. Whoever wields it (in either
  hand) can see the invisible: the game's own way with a magic item's spell (its +0Fh, one past
  the spell's number), which it puts on the wearer when the item is readied and takes off when
  it's put away, for a spell it counts as helpful (Detect Invisibility is; a weapon's other
  spells are cast on what it hits instead). Its item box shows the spell's icon (its +02h:
  right-clicked, the spell's description).

Each has a name of its own, as the Templar's Bloodwrath (an obsidian long sword +1, 20800) has, in
entries DSCLOG adds (names.py); is priced near it; and has an icon of its own (icons.py:
Kreenfang's blades in the fire colours, Shadowseeker's night steel). The game shows the plus with the
name ("+1 Kreenfang"), and it counts for hitting and damage as any magic weapon's.
"""

import struct
from typing import Dict, Tuple

from . import dataitems, game

BODY = 1204  # the arena's dead body with the gythka (its object)
SWORD_NAME, GYTHKA_NAME = 0x147, 0x148  # name entries DSCLOG adds
NAMES = {SWORD_NAME: b"Shadowseeker", GYTHKA_NAME: b"Kreenfang"}  # as DSCLOG's EXTRA_NAMES has them
# near the Bloodwrath's 20800 (the plain ones: 6 and 500); metal is the dearer, on Athas
GYTHKA_VALUE, SWORD_VALUE = 20800, 22000  # (the game's Gythka +1 and Bloodwrath +1: 20,800)
ITEM_VALUE = 0x06  # an item's price (npcitems.ITEM_VALUE)
ITEM_SPELL = 0x0F  # an item's spell, one past the spell's number (0: none)
ITEM_SPELL_SHOWN = 0x02  # (a word) the spell whose icon its box shows, the same
SWORD_SPELL = game.DETECT_INVISIBILITY + 1


def magic(rec: bytes, value: int, name: int, spell: int = 0) -> bytes:
    """REC made +1, named NAME, priced VALUE (with SPELL, if any)."""
    out = bytearray(rec)
    out[game.ITEM_PLUS] = 1
    struct.pack_into("<H", out, ITEM_VALUE, value)
    struct.pack_into("<H", out, game.ITEM_NAME, name)
    if spell:
        out[ITEM_SPELL] = spell
        struct.pack_into("<H", out, ITEM_SPELL_SHOWN, spell)
    return bytes(out)


def shadowseeker(sword: bytes) -> bytes:
    return magic(sword, SWORD_VALUE, SWORD_NAME, SWORD_SPELL)


def kreenfang_chunks(chunks) -> Dict[Tuple[str, int], bytes]:
    """For the Loader's copy of SEGOBJEX: the arena's dead body with its gythka Kreenfang."""
    key = ("RDFF", BODY)
    if key not in chunks:
        return {}

    def plain_gythka(rec: bytes) -> bool:
        return struct.unpack_from("<H", rec, game.ITEM_TYPE)[0] == game.GYTHKA_TYPE and rec[game.ITEM_PLUS] == 0

    changed = dataitems.with_item_changed(chunks[key], plain_gythka, lambda rec: magic(rec, GYTHKA_VALUE, GYTHKA_NAME))
    return {key: changed} if changed != chunks[key] else {}
