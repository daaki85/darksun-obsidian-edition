"""Magical items sold to a merchant kept, to buy back (game.RULE_BUYBACK; DSCLOG's SELL_KEEP).

The game destroys whatever the party sells: once the shop has paid (83CCAh on), it frees the thing
holding the item (0A0h:1C94h, at 83D9Eh). With the rule on, DSCLOG lets a magical item (a plus,
or a power: rings, wands, scrolls...) through without freeing it, and queues the thing and the
shop's merchant (SOLD_Q, SOLD_SEQ); here the item is put in that merchant's pack, where the shop
lists it (the shop sells whatever its merchant carries), at its own price, and the thing given
back to the game's free list. Anything else sold is gone, as in the game.
"""

import struct
from typing import List, Optional

from . import game, npcitems, pickpocket, ring

SOLD_SEQ, SOLD_Q, SOLD_SLOTS = 308, 310, 4  # (DSCLOG's header)
PERSON, MAX_CREATURES = 2, 512  # (an object's kind for a creature, as GameData.combatants reads them)


def free_thing(gd, it: ring.Items, thing: int) -> None:
    """THING given back to the game's free list of objects (as its allocator takes them, reversed)."""
    ds = gd.ds * 16
    gd.guest.write(it.things + thing * 3, struct.pack("<BH", 0, it.word(ring.FREE_THINGS)))
    gd.guest.write(ds + ring.FREE_THINGS, struct.pack("<H", thing))
    gd.guest.write(ds + ring.THINGS_USED, struct.pack("<H", max(it.word(ring.THINGS_USED) - 1, 0)))


def to_pack(gd, creature: int, item: int) -> bool:
    """ITEM (out of any list) put first in the creature's last non-empty item list, or a new one, in
    a backpack cell of its own (or its own slot byte kept, the pack full)."""
    it = ring.Items(gd)
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
        self.seen: Optional[int] = None  # (SOLD_SEQ as last looked at)

    def watch(self, gd, hdr: Optional[int]) -> List[str]:
        """Each item DSCLOG has kept since the last look: into its merchant's pack. The log's lines."""
        if hdr is None:
            return []
        seq = struct.unpack("<H", gd.guest.read(hdr + SOLD_SEQ, 2))[0]
        if self.seen is None or not 0 <= (seq - self.seen) % 0x10000 <= SOLD_SLOTS:
            self.seen = seq  # (the first look, or too many missed: only those from now on)
            return []
        out: List[str] = []
        while self.seen != seq:
            slot = self.seen % SOLD_SLOTS
            thing, merchant = struct.unpack("<HH", gd.guest.read(hdr + SOLD_Q + slot * 4, 4))
            self.seen = (self.seen + 1) % 0x10000
            out += self.keep(gd, thing, merchant)
        return out

    def keep(self, gd, thing: int, merchant: int) -> List[str]:
        it = ring.Items(gd)
        if not 0 <= thing < ring.THING_COUNT:
            return []
        kind, first = it.thing(thing)
        if kind != game.THING_ITEM or not 0 <= first < game.NO_ITEM:
            return []
        items = [index for index, _ in it.chain(thing, inside=False)]
        names = [gd.item_name(struct.unpack_from("<H", it.item(i), game.ITEM_NAME)[0]) for i in items]
        creature = None  # (the merchant's creature: its object a person's, of any of the 520)
        if 0 <= merchant < ring.THING_COUNT:
            mkind, mindex = it.thing(merchant)
            if mkind == PERSON and 0 <= mindex < MAX_CREATURES:
                creature = mindex
        if creature is None:  # (no merchant of the game's kind: gone, as the game would have it)
            for index in items:
                ring.unlink(gd, ring.Items(gd), index, "sold (no merchant to keep it)", empty=True)
            free_thing(gd, ring.Items(gd), thing)
            return []
        gd.guest.write(it.things + thing * 3 + 1, struct.pack("<h", game.NO_ITEM))  # (the items out of it)
        kept = []
        for index, name in zip(items, names):
            if to_pack(gd, creature, index):
                kept.append(name)
            else:  # (nowhere for it: its record back on the free list, as the game would have it)
                gd.guest.write(it.items + index * game.ITEM_SIZE + game.ITEM_NEXT,
                               struct.pack("<H", it.word(ring.FREE_ITEMS)))
                gd.guest.write(gd.ds * 16 + ring.FREE_ITEMS, struct.pack("<H", index))
        free_thing(gd, ring.Items(gd), thing)
        who = gd.creature_name(creature)
        return [f"{who} keeps the {name} for sale: it can be bought back" for name in kept]
