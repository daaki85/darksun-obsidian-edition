"""A party archer's arrows left, floating over it after each shot (labels.py, as Armor's charges):
"Arrows: 17 left", what its quiver holds, or "Out of arrows" at none.
"""

import struct
from typing import Optional, Tuple

from . import game, weaponchoice

Item = Tuple[int, bytes]


def count(rec: bytes) -> int:
    return struct.unpack_from("<H", rec, weaponchoice.ITEM_COUNT)[0]


def quiver(gd: game.GameData, member: int) -> Optional[Item]:
    """The member's ammunition slot's stack (item number, record), if any."""
    return next(((index, item) for index, item, _ in gd._worn(member)
                 if item[game.ITEM_SLOT] == weaponchoice.AMMO_SLOT), None)


# An item type's first word: bit 3 set for a missile weapon that shoots ammunition (a bow, a crossbow):
# the games' count of a shot's ammunition (SL's 58C97h, the sequel's 5D3BAh) gives one without it (a
# chatkcha, a sling there) no end of shots, so no arrows to count
TYPE_FLAGS, SHOOTS_AMMO = 0, 0x08


def shooter(gd: game.GameData, member: int) -> bool:
    """Whether the member has a missile weapon that shoots ammunition in its missile slot (a thrown
    chatkcha is no archer's: it was "Out of arrows" after every throw)."""
    return any(item[game.ITEM_SLOT] == weaponchoice.MISSILE_SLOT
               and gd.item_type_record(item)[TYPE_FLAGS] & SHOOTS_AMMO for _, item, _ in gd._worn(member))


def word(gd: game.GameData, stack: bytes) -> str:
    """The stack's kind in a word for its label: its name's last ("Arrows", "Stones")."""
    try:
        name = gd.item_label(stack, gd.item_type_record(stack)).split()
    except (struct.error, IndexError, ValueError):
        name = []
    return name[-1] if name else "Arrows"


def left_label(gd: game.GameData, member: int, last: Optional[bytes] = None) -> Optional[str]:
    """What floats over a party archer after a shot: "Arrows: 17 left" (what its quiver holds), or
    "Out of arrows" (LAST, the stack it shot from, names the kind once the game has taken the
    emptied stack away). None for one with no missile weapon."""
    if not 0 <= member < game.PARTY_SIZE or not shooter(gd, member):
        return None
    found = quiver(gd, member)
    if found is None:
        return f"Out of {word(gd, last).lower()}" if last is not None else "Out of arrows"
    _, stack = found
    total = count(stack)
    return f"{word(gd, stack)}: {total} left" if total else f"Out of {word(gd, stack).lower()}"
