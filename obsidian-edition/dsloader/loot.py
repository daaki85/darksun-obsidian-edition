"""Looting a body (or any container) in one go: with its window open, T takes everything in it and
Shift+T all but plain weapons (the user's choice, 2026-11-11: the game makes each thing a click to
pick up and a click to put down, a body at a time).

DSCLOG's LOOT_KEY makes the key Escape, which shuts the window, and counts it (LOOT_SEQ, header
+1846) with the container's map thing (LOOT_THING, +1848: the game's DS:05E6h while the window is
open) and the mode (LOOT_MODE, +1850: 0 T, 1 Shift+T). Once the window is shut (DS:05E6h 9999
again), the dice log calls take(): each thing in the container, first to last, goes into the
backpack of the first party member, in the party's order, with a free cell (as a picked pocket's:
pickpocket.give), up and about (not dying or dead). What has no room stays in the container, and so
do plain weapons for Shift+T (a weapon with no plus and no power: the guards' bone swords). The
container's list is linked again from what stays, or given back to the game's free things when
nothing does (as the game leaves an emptied container: +08h 9999). What was taken, and what stayed,
is in the dice log, with the purse's sound."""

import struct
from typing import Dict, List, Optional, Tuple

from . import game, itemgate, pickpocket, ring
from .game import GameData

TSR_LOOT_SEQ, TSR_LOOT_THING, TSR_LOOT_MODE = 1846, 1848, 1850  # in DSCLOG's header
OPEN = 0x05E6  # the game's DS: the container whose window is open (NONE: none)
NONE = 9999
ALL, NO_PLAIN_WEAPONS = 0, 1
STATUS_GONE = (4, 5)  # (Dying, Dead)


def release(gd: GameData, tsr_hdr: int) -> None:
    """LOOT_THING made FFFFh: the T DSCLOG counted is taken, and the next T is counted (DSCLOG holds
    one, leaving it the game's key, while one is pending: a second body's T never replaces it)."""
    gd.guest.write(tsr_hdr + TSR_LOOT_THING, struct.pack("<H", 0xFFFF))


def window_open(gd: GameData) -> bool:
    return struct.unpack("<H", gd.guest.read(gd.ds * 16 + OPEN, 2))[0] != NONE


def plain_weapon(gd: GameData, rec: bytes) -> bool:
    """A weapon (melee, missile or thrown) with no plus and no magical power."""
    if struct.unpack_from("<H", rec, game.ITEM_TYPE)[0] >= game.NO_ITEM:
        return False
    typ = gd.item_type_record(rec)
    plus = struct.unpack_from("b", rec, game.ITEM_PLUS)[0]
    return bool(typ) and bool(typ[0] & pickpocket.WEAPON_KINDS) and plus == 0 and rec[game.ITEM_POWER] == 0


def _contents(gd: GameData, it: ring.Items, thing: int) -> Optional[Tuple[int, int]]:
    """(the container's item, its list's thing) for map thing THING, or None (not a container,
    or empty)."""
    if not 0 <= thing < ring.THING_COUNT:
        return None
    kind, item = it.thing(thing)
    if kind != game.THING_ITEM or not 0 <= item < game.NO_ITEM:
        return None
    contents, = struct.unpack_from("<H", it.item(item), ring.ITEM_CONTENTS)
    if not 0 <= contents < ring.THING_COUNT or it.thing(contents)[0] != game.THING_ITEM:
        return None
    return item, contents


def _relink(gd: GameData, it: ring.Items, container: int, contents: int, kept: List[int]) -> None:
    """The container's list made KEPT, in order; its thing given back to the free list if empty."""
    ds = gd.ds * 16
    if kept:
        for item, after in zip(kept, kept[1:] + [game.NO_ITEM]):
            gd.guest.write(it.items + item * game.ITEM_SIZE + game.ITEM_NEXT, struct.pack("<H", after))
        gd.guest.write(it.things + contents * 3, struct.pack("<BH", game.THING_ITEM, kept[0]))
        return
    gd.guest.write(it.things + contents * 3, struct.pack("<BH", 0, it.word(ring.FREE_THINGS)))
    gd.guest.write(ds + ring.FREE_THINGS, struct.pack("<H", contents))
    gd.guest.write(ds + ring.THINGS_USED, struct.pack("<H", max(0, it.word(ring.THINGS_USED) - 1)))
    gd.guest.write(it.items + container * game.ITEM_SIZE + ring.ITEM_CONTENTS, struct.pack("<H", NONE))


def _takers(gd: GameData) -> List[int]:
    out = []
    for member in range(game.PARTY_SIZE):
        rec = gd.creature(member)
        if len(rec) >= game.CREATURE_SIZE and rec[game.CREATURE_NAME] and rec[game.CREATURE_STATUS] not in STATUS_GONE:
            out.append(member)
    return out


def take(gd: GameData, thing: int, mode: int) -> Tuple[List[str], bool]:
    """Container THING's things into the party's backpacks (mode ALL or NO_PLAIN_WEAPONS): the dice
    log's lines, and whether anything was taken."""
    it = ring.Items(gd)
    found = _contents(gd, it, thing)
    if found is None:
        return [], False
    container, contents = found
    itemgate.hold(gd)  # (the game busy with its lists: ItemsBusy, tried again in a later pass)
    items = [i for i, _ in it.chain(contents, inside=False)]
    names = {i: gd.item_label(rec, gd.item_type_record(rec)) for i, rec in it.chain(contents, inside=False)}
    plan: Dict[int, Tuple[int, int]] = {}  # item: (member, cell)
    taken_cells: Dict[int, set] = {}
    takers = _takers(gd)
    ready: Dict[int, bool] = {}  # member: whether it has a backpack list to take into
    plain: List[int] = []
    for item in items:
        if mode == NO_PLAIN_WEAPONS and plain_weapon(gd, it.item(item)):
            plain.append(item)
            continue
        for member in takers:
            cells = taken_cells.setdefault(member, set())
            used = _used(gd, it, member) | cells  # (what it has, and what is planned for it already)
            cell = next((c for c in pickpocket.BACKPACK if c not in used), None)
            if cell is None:
                continue
            if member not in ready:  # (its backpack list, made now if it has none, before anything
                # is unlinked: with too few free things there is none, and nothing goes to it)
                ready[member] = pickpocket.party_list(gd, it, member, cell) is not None
                it = ring.Items(gd)  # (read again: the list may be new)
            if ready[member]:
                cells.add(cell)
                plan[item] = (member, cell)
                break
    if not plan:
        lines = []
        if plain and len(plain) == len(items):
            lines.append("Only plain weapons there: left where they are.")
        elif items:
            lines.append("The party's backpacks are full: nothing taken.")
        return lines, False
    kept = [i for i in items if i not in plan]
    _relink(gd, it, container, contents, kept)
    got: Dict[int, List[str]] = {}
    lost: List[int] = []
    for item, (member, cell) in plan.items():
        gd.guest.write(it.items + item * game.ITEM_SIZE + game.ITEM_NEXT, struct.pack("<H", game.NO_ITEM))
        if pickpocket.give(gd, ring.Items(gd), member, item, cell):
            got.setdefault(member, []).append(names[item])
        else:
            lost.append(item)
    if lost:  # (no list to be had for them: back in the container, after what stayed)
        fresh = ring.Items(gd)
        again = _contents(gd, fresh, thing)
        if again is None:  # (the container's list was given back: a new one, as the rack's)
            from .semyon import _new_contents
            new = _new_contents(gd, fresh, container)
            fresh = ring.Items(gd)
            again = (container, new) if new is not None else None
        if again is not None:
            _relink(gd, fresh, again[0], again[1], kept + lost)
            kept += lost
    lines = [f"{gd.creature_name(m)} takes {_listed(n)}" for m, n in got.items()]
    left_room = [names[i] for i in kept if i not in plain]
    if left_room:
        lines.append(f"No room in the backpacks for: {_listed(left_room)}")
    if plain:
        lines.append(f"Plain weapons left: {_listed([names[i] for i in plain])}")
    return lines, bool(got)


def _listed(names: List[str]) -> str:
    """NAMES in their order, a name more than once given once with how many: "Guava (4)"."""
    counts: Dict[str, int] = {}
    for name in names:
        counts[name] = counts.get(name, 0) + 1
    return ", ".join(f"{name} ({n})" if n > 1 else name for name, n in counts.items())


def _used(gd: GameData, it: ring.Items, member: int) -> set:
    rec = gd.creature(member)
    used = set()
    for offset in game.CREATURE_ITEM_LISTS:
        thing, = struct.unpack_from("<h", rec, offset)
        used.update(data[game.ITEM_SLOT] for _, data in it.chain(thing, inside=False))
    return used
