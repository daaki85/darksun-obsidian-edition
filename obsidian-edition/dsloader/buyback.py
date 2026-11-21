"""Magical items sold to a merchant kept, to buy back (game.RULE_BUYBACK; DSCLOG's SELL_KEEP).

The game destroys whatever the party sells: once the shop has paid (83CCAh on), it empties the
item list of the thing holding it (0A0h:1C94h, at 83D9Eh), its items back on the free list. That
thing is the pointer's (DS:179Eh, 523: one of the few past the 520 objects), so it is never
freed, only emptied. With the rule on and the Loader there (its heartbeat fresh: without it nothing
would take the item off the pointer, and it is freed as the game does), DSCLOG lets a magical item
(a plus, or a power: rings, wands, scrolls...) through without emptying it, and queues the thing,
the shop's merchant and the list's first item (SOLD_Q, SOLD_ITEMS, SOLD_SEQ); here the items are
put in that merchant's pack, where the shop lists it (the shop sells whatever its merchant
carries), at their own price, and the thing's list emptied as the game would have; each entry is
then marked seen to (its item DONE), so that one left by a Loader that went away is seen to by the
next. Only while the thing's list still starts with that item (another picked up meanwhile is left
where it is). Anything else sold is gone, as in the game.
"""

import struct
from typing import List, Optional

from . import game, itemgate, npcitems, pickpocket, ring

SOLD_SEQ, SOLD_Q, SOLD_SLOTS = 308, 310, 4  # (DSCLOG's header)
SOLD_ITEMS = 1868  # (each entry's item, DSCLOG's SOLD_ITEMS: DONE once the Loader has seen to it)
DONE = 0xFFFF
PERSON, MAX_CREATURES = 2, 512  # (an object's kind for a creature, as GameData.combatants reads them)
LAST_THING = ring.THING_COUNT + 4  # (the things table's few past the 520 objects: the pointer's, 523)


def _thing(gd, it: ring.Items, thing: int):
    """(kind, first) of THING, any of the table's (Items.thing reads the first 520 only)."""
    return struct.unpack("<Bh", gd.guest.read(it.things + thing * 3, 3))


def _items(it: ring.Items, first: int) -> List[int]:
    """The item numbers in a list from its FIRST (not into containers: they go with their bag)."""
    out: List[int] = []
    index = first
    while 0 <= index < ring.ITEM_RECORDS and len(out) < ring.MAX_ITEMS and index not in out:
        out.append(index)
        index = struct.unpack_from("<h", it.item(index), game.ITEM_NEXT)[0]
    return out


def _empty(gd, it: ring.Items, thing: int) -> None:
    """THING emptied (its items taken elsewhere), as 0A0h:1C94h leaves it: the pointer's all
    zeros, as the game has it with nothing held (a list of kind 1 there, even empty, and the
    game's inventory screen picks nothing up); one of the 520 an empty list."""
    if thing >= ring.THING_COUNT:
        gd.guest.write(it.things + thing * 3, bytes(3))
    else:
        gd.guest.write(it.things + thing * 3 + 1, struct.pack("<h", game.NO_ITEM))


def to_pack(gd, creature: int, item: int) -> bool:
    """ITEM (out of any list) put first in the creature's last non-empty item list, or a new one, in
    a backpack cell of its own (or its own slot byte kept, the pack full)."""
    it = ring.held(gd)
    lists = [struct.unpack_from("<h", gd.creature(creature), o)[0] for o in game.CREATURE_ITEM_LISTS]
    thing = next((t for t in reversed(lists) if 0 <= t < ring.THING_COUNT), None)
    if thing is None:
        thing = npcitems._new_list(gd, it, creature, lists)
        if thing is None:
            return False
        it = ring.Items(gd)
    kind, first = it.thing(thing)
    if kind != game.THING_ITEM:
        return False
    cell = pickpocket.free_cell(gd, it, creature)
    at = it.items + item * game.ITEM_SIZE
    gd.guest.write(at + game.ITEM_NEXT, struct.pack("<h", first))
    if cell is not None:
        gd.guest.write(at + game.ITEM_SLOT, bytes((cell,)))
    gd.guest.write(it.things + thing * 3 + 1, struct.pack("<h", item))
    return True


class Buyback:
    def __init__(self):
        self.seen: Optional[int] = None  # (SOLD_SEQ as last looked at, every entry seen to then)
        self.kept: List[str] = []  # (the items kept, by name)

    def watch(self, gd, hdr: Optional[int]) -> List[str]:
        """Each sale DSCLOG has queued that no Loader has seen to yet, oldest first: its items into
        its merchant's pack. Looked at when SOLD_SEQ moves, and at the first look (a sale left by
        a Loader that went away). No lines for the log."""
        if hdr is None:
            return []
        seq = struct.unpack("<H", gd.guest.read(hdr + SOLD_SEQ, 2))[0]
        if seq == self.seen:
            return []
        if all(item == DONE for item in struct.unpack(f"<{SOLD_SLOTS}H", gd.guest.read(hdr + SOLD_ITEMS, 2 * SOLD_SLOTS))):
            self.seen = seq
            return []
        # (the gate held before the queue and the lists are read: the game held still till the
        # items are moved, and if it is busy with its lists, ItemsBusy and nothing done yet: a later pass)
        itemgate.hold(gd)
        try:
            seq = struct.unpack("<H", gd.guest.read(hdr + SOLD_SEQ, 2))[0]
            items = struct.unpack(f"<{SOLD_SLOTS}H", gd.guest.read(hdr + SOLD_ITEMS, 2 * SOLD_SLOTS))
            for k in range(SOLD_SLOTS):
                slot = (seq + k) % SOLD_SLOTS  # (SEQ's own slot the oldest: the next to be written)
                if items[slot] == DONE:
                    continue
                thing, merchant = struct.unpack("<HH", gd.guest.read(hdr + SOLD_Q + slot * 4, 4))
                busy = False
                try:
                    self.keep(gd, thing, merchant, items[slot])
                except itemgate.ItemsBusy:  # (nothing moved: this one and those after, a later pass)
                    busy = True
                    raise
                finally:  # (else seen to, even a sale that failed part way: not tried every pass)
                    if not busy:
                        gd.guest.write(hdr + SOLD_ITEMS + slot * 2, struct.pack("<H", DONE))
            self.seen = seq
        finally:
            itemgate.release(gd)
        return []

    def keep(self, gd, thing: int, merchant: int, item: Optional[int] = None) -> List[str]:
        """THING's items into MERCHANT's pack, if its list still starts with ITEM (None: any)."""
        # (before anything is moved: the game busy with its lists, ItemsBusy and the sale tried
        # again in a later pass, not the thing emptied and its items left in no list)
        itemgate.hold(gd)
        it = ring.Items(gd)
        if not 0 <= thing < LAST_THING:
            return []
        kind, first = _thing(gd, it, thing)
        if kind != game.THING_ITEM or not 0 <= first < ring.ITEM_RECORDS:
            return []
        if item is not None and first != item:  # (another item on the pointer now: not the one sold)
            return []
        items = _items(it, first)
        names = [gd.item_name(struct.unpack_from("<H", it.item(i), game.ITEM_NAME)[0]) for i in items]
        creature = None  # (the merchant's creature: its object a person's, of any of the 520)
        if 0 <= merchant < ring.THING_COUNT:
            mkind, mindex = it.thing(merchant)
            if mkind == PERSON and 0 <= mindex < MAX_CREATURES:
                creature = mindex
        _empty(gd, it, thing)  # (the items out of it, as the game would have them)
        kept = []
        for index, name in zip(items, names):
            if creature is not None and to_pack(gd, creature, index):
                kept.append(name)
            else:  # (no merchant of the game's kind, or nowhere for it: gone, as the game has it)
                ring.free(gd, index, f"sold: {name}")
        self.kept += kept  # (for tests: the log says nothing, the shop's list shows it)
        return []
