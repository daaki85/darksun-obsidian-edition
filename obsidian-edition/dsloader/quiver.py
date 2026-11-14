"""A party archer's quiver in a fight: topped up from its own pack as its turn starts, and the
arrows it has left floating over it after each shot (labels.py, as Armor's charges).

The game shoots only what is in the ammunition slot, and a stack readied there during a fight
after a volley can't be shot that turn (playtest/logs/2026-11-14-quiver-turn.md). So, as a party
member's turn starts in a fight, a quiver holding fewer than TOP_UP_UNDER (the most shots a round:
a grand master's bow) takes more from the member's backpack, up to TOP_UP_TO, from stacks of the
same kind: the same type, name and plus (spell arrows only from the same spell's). Only the count
of the stack already in the quiver changes, which the game reads at each shot; a backpack stack
emptied so is taken away. An empty quiver isn't filled: the game removed its stack, and a stack
put in a slot by memory in a fight isn't shot (the game's own list of what is readied).
"""

import struct
from typing import List, Optional, Tuple

from . import game, ring, spellarrows, weaponchoice

TOP_UP_UNDER = 5        # a quiver with fewer than this is topped up as the turn starts
TOP_UP_TO = 20          # ... to this many (the game's stack of arrows), what the pack has allowing
BACKPACK_FIRST = len(game.EQUIP_SLOTS)  # (an item's +11h from here on: a backpack cell)
KIND = ((game.ITEM_TYPE, 2), (game.ITEM_NAME, 2), (game.ITEM_PLUS, 1))

Item = Tuple[int, bytes]


def count(rec: bytes) -> int:
    return struct.unpack_from("<H", rec, weaponchoice.ITEM_COUNT)[0]


def same_kind(a: bytes, b: bytes) -> bool:
    """Whether two stacks are of one kind: the same type, name and plus."""
    return all(a[o:o + n] == b[o:o + n] for o, n in KIND)


def quiver(gd: game.GameData, member: int) -> Optional[Item]:
    """The member's ammunition slot's stack (item number, record), if any."""
    return next(((index, item) for index, item, _ in gd._worn(member)
                 if item[game.ITEM_SLOT] == weaponchoice.AMMO_SLOT), None)


def reserves(gd: game.GameData, member: int, stack: bytes) -> List[Item]:
    """The member's backpack stacks of STACK's kind, with arrows in them."""
    return [(index, item) for index, item, _ in gd._worn(member)
            if item[game.ITEM_SLOT] >= BACKPACK_FIRST and same_kind(item, stack) and count(item) > 0]


def shooter(gd: game.GameData, member: int) -> bool:
    """Whether the member has a missile weapon in its missile slot."""
    return any(item[game.ITEM_SLOT] == weaponchoice.MISSILE_SLOT for _, item, _ in gd._worn(member))


def _set_count(gd: game.GameData, index: int, n: int) -> None:
    gd.guest.write(spellarrows.item_address(gd, index) + weaponchoice.ITEM_COUNT, struct.pack("<H", n))


def top_up(gd: game.GameData, member: int) -> List[str]:
    """As the member's turn starts in a fight: its quiver topped up from its pack (TOP_UP_UNDER,
    TOP_UP_TO). Lines for the log."""
    if not 0 <= member < game.PARTY_SIZE or not shooter(gd, member):
        return []
    found = quiver(gd, member)
    if found is None:
        return []
    index, stack = found
    have = count(stack)
    if have <= 0 or have >= TOP_UP_UNDER:
        return []
    want, taken = TOP_UP_TO - have, 0
    for spare, rec in reserves(gd, member, stack):
        if taken >= want:
            break
        take = min(count(rec), want - taken)
        taken += take
        left = count(rec) - take
        if left:
            _set_count(gd, spare, left)
        else:
            _set_count(gd, spare, 0)
            ring.unlink(gd, ring.Items(gd), spare, "arrows moved to the quiver", empty=True)
    if not taken:
        return []
    _set_count(gd, index, have + taken)
    return [f"{gd.creature_name(member)} fills the quiver from the pack: +{taken}, {have + taken} "
            f"{gd.item_label(stack, gd.item_type_record(stack))} ready"]


def word(gd: game.GameData, stack: bytes) -> str:
    """The stack's kind in a word for its label: its name's last ("Arrows", "Stones")."""
    try:
        name = gd.item_label(stack, gd.item_type_record(stack)).split()
    except (struct.error, IndexError, ValueError):
        name = []
    return name[-1] if name else "Arrows"


def left_label(gd: game.GameData, member: int, last: Optional[bytes] = None) -> Optional[str]:
    """What floats over a party archer after a shot: "Arrows: 17 left" (the quiver and the pack's
    stacks of its kind), or "Out of arrows" (LAST, the stack it shot from, names the kind when the
    quiver is now empty). None for one with no missile weapon."""
    if not 0 <= member < game.PARTY_SIZE or not shooter(gd, member):
        return None
    found = quiver(gd, member)
    if found is None:
        return f"Out of {word(gd, last).lower()}" if last is not None else "Out of arrows"
    _, stack = found
    total = count(stack) + sum(count(rec) for _, rec in reserves(gd, member, stack))
    return f"{word(gd, stack)}: {total} left" if total else f"Out of {word(gd, stack).lower()}"
