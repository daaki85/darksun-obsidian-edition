"""The game's people wearing and wielding their gear from the moment they are on the map (a fix of
the game's).

The game makes a person's items in its backpack list (+0Ch) and puts them on only at that person's
first action in a fight: weapons to the held list (+0Ah), armour and ammunition to the worn list
(+08h), each in its slot (seen in DOSBox, 2026-11-06: an Arena Guard's leather chest armour to
slot 9, arm armour to 0, arrows to 1, his obsidian long sword to the right hand, 3, his bow to the
missile slot, 2; Kurzak with two weapons, Shadowseeker +1 in the main hand, his obsidian long sword
in the off hand). Until then a person is AC 10 with its armour unworn and fights with nothing, and
the Look box (which lists the held list) shows no weapon: in a fight's first round anyone who
hasn't acted yet was easier to hit, anyone killed before acting never wore its armour, and an
opening blow from outside a fight (the game starts the fight after it: a sling shot at Legcrusher
hit AC 9, the fight on only once his "Help! Somebody sound the alarm!" was read) met no armour.

So each person on the map (not the party; not the champions, put in place by champions.Gear) has
its gear put where the game would put it, as soon as it is there (People.watch, from the dice
log's pass): by its type's kind (TYPE_FLAGS) and where it is worn (TYPE_WORN), into a slot that
is free: the best melee weapon (its plus) in the right hand, a shield in the left, or else a
second melee weapon there; a missile weapon in the missile slot, its ammunition in the ammunition
slot; chest, arm, leg armour and a helm in theirs, and a cloak, a belt, boots, an amulet and up to
two rings (the game wasn't seen to put those on: they are worn as the party's are, and count by
the same rules, a cloak of protection with a shield none under AD&D's). Keys, food, scrolls and
the rest stay in the pack. Nothing is moved that the game has put in place already.
"""

import struct
from typing import Dict, List, Optional, Sequence, Set, Tuple

from . import game, itemgate, pickpocket, restrict, ring

ARM, AMMO, MISSILE, RIGHT, FINGER, WAIST, LEGS, HEAD, NECK, CHEST, LEFT, FINGER2, CLOAK, FOOT = range(14)  # (the game's slots)
TYPE_FLAGS, TYPE_WORN = restrict.TYPE_FLAGS, pickpocket.TYPE_WORN
HAND = 5  # (TYPE_WORN: held in a hand, a weapon or a shield)
WORN_SLOTS = {1: CHEST, 2: WAIST, 3: ARM, 4: FOOT, 6: HEAD, 7: NECK, 8: CLOAK, 10: LEGS, 11: AMMO}  # (TYPE_WORN:
# the slot; the game's item types read in the running game, 2026-11-06: 2 the girdles, 3 armour and bracers, 4 boots,
# 6 helms and circlets, 7 the amulet, 8 cloaks, 9 rings, 12 bows and slings)
FINGER_WORN = 9  # (a ring: the first finger free, then the other)
MISSILE_WORN = 12  # (TYPE_WORN of a bow or a sling)
SEEN = 128  # (creature records looked at: as champions.SEEN)


def plan(items: Sequence[Tuple[int, bytes, bytes]], taken: Set[int]) -> List[Tuple[int, int]]:
    """(item, slot) for each of a person's backpack ITEMS ((item, record, its type's record)) that
    goes on, into slots not in TAKEN, as the game would put them."""
    free = lambda slot: slot not in taken and slot not in [s for _, s in out]
    out: List[Tuple[int, int]] = []
    melee, shields = [], []
    for item, data, typ in items:
        if len(typ) <= max(TYPE_FLAGS, TYPE_WORN):
            continue
        flags, worn = typ[TYPE_FLAGS], typ[TYPE_WORN]
        if flags & restrict.SHIELD:
            shields.append(item)
        elif worn == MISSILE_WORN or (flags & restrict.MISSILE and not flags & restrict.MELEE):
            if free(MISSILE):
                out.append((item, MISSILE))
        elif flags & (restrict.MELEE | restrict.THROWN) and worn == HAND:
            plus = struct.unpack("b", data[game.ITEM_PLUS:game.ITEM_PLUS + 1])[0]
            melee.append((-plus, len(melee), item))
        elif worn == FINGER_WORN:
            finger = next((f for f in (FINGER, FINGER2) if free(f)), None)
            if finger is not None:
                out.append((item, finger))
        elif worn in WORN_SLOTS and free(WORN_SLOTS[worn]):
            out.append((item, WORN_SLOTS[worn]))
    melee.sort()
    if melee and free(RIGHT):
        out.append((melee.pop(0)[2], RIGHT))
    if shields and free(LEFT):
        out.append((shields[0], LEFT))
    elif melee and free(LEFT) and RIGHT in taken | {s for _, s in out}:
        out.append((melee[0][2], LEFT))
    return out


class People:
    """Puts the game's people's gear on as they come on the map (watch, each pass), once each."""

    def __init__(self):
        self.done: Set[Tuple[int, bytes, int]] = set()  # (creature, name, object) seen to, this area
        self._region: Optional[int] = None

    def reset(self) -> None:
        """Forget who was seen to (a game loaded: its people are made again)."""
        self.done.clear()

    def watch(self, gd) -> List[str]:
        region = gd.region()
        if region != self._region:  # (another area: its people made anew)
            self._region = region
            self.done.clear()
        from .champions import CREATURE_OBJECT, DEAD_STATUS, champion_of
        table = gd.creatures(SEEN)
        size = game.CREATURE_SIZE
        on_map = set(gd.combatants().values())
        for index in range(game.PARTY_SIZE, len(table) // size):
            rec = table[index * size:(index + 1) * size]
            if index not in on_map or len(rec) < size or champion_of(rec) is not None:
                continue
            name = rec[game.CREATURE_NAME:game.CREATURE_NAME + 16].split(b"\0", 1)[0]
            key = (index, name, struct.unpack_from("<h", rec, CREATURE_OBJECT)[0])
            if key in self.done:
                continue
            if struct.unpack_from("<h", rec, 0)[0] <= 0 or rec[game.CREATURE_STATUS] in DEAD_STATUS:
                continue
            moves = self.moves(gd, index)
            if moves:
                itemgate.hold(gd)  # (before anything moves: the game busy with its lists, a later pass)
                for item, slot in moves:
                    pickpocket.place(gd, index, item, slot)
            self.done.add(key)
        return []

    @staticmethod
    def moves(gd, index: int) -> List[Tuple[int, int]]:
        """Person INDEX's (item, slot) moves out of its backpack: none if it carries nothing."""
        it = ring.Items(gd)
        rec = gd.creature(index)
        lists = [struct.unpack_from("<h", rec, o)[0] for o in game.CREATURE_ITEM_LISTS]
        taken = {data[game.ITEM_SLOT] for thing in lists[:2] for _, data in it.chain(thing, inside=False)}
        pack = [(item, data, gd.item_type_record(data)) for item, data in it.chain(lists[2], inside=False)
                if struct.unpack_from("<H", data, game.ITEM_TYPE)[0] < game.NO_ITEM]
        return plan(pack, taken)
