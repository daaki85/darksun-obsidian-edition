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
from contextlib import contextmanager
from typing import Callable, Dict, Iterator, List, Optional, Tuple

from . import game, icons, itemgate, pickpocket, ring
from .game import GameData
from .process import ProcessError

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
    return bool(typ) and bool(typ[0] & pickpocket.WEAPON_KINDS) and plus == 0 and game.item_power(rec) == 0


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


def _relink(gd: GameData, it: ring.Items, container: int, contents: int, kept: List[int],
            write: Callable[[int, bytes], None]) -> None:
    """The container's list made KEPT, in order; its thing given back to the free list if empty."""
    ds = gd.ds * 16
    if kept:
        for item, after in zip(kept, kept[1:] + [game.NO_ITEM]):
            write(it.items + item * game.ITEM_SIZE + game.ITEM_NEXT, struct.pack("<H", after))
        write(it.things + contents * 3, struct.pack("<BH", game.THING_ITEM, kept[0]))
        return
    write(it.things + contents * 3, struct.pack("<BH", 0, it.word(ring.FREE_THINGS)))
    write(ds + ring.FREE_THINGS, struct.pack("<H", contents))
    write(ds + ring.THINGS_USED, struct.pack("<H", max(0, it.word(ring.THINGS_USED) - 1)))
    write(it.items + container * game.ITEM_SIZE + ring.ITEM_CONTENTS, struct.pack("<H", NONE))


@contextmanager
def _loot_writes(gd: GameData) -> Iterator[Callable[[int, bytes], None]]:
    """Restore the item lists if a bulk-loot write fails, while the caller still holds the item gate."""
    guest = gd.guest
    previous = []

    def write(at: int, data: bytes) -> None:
        old = guest.read(at, len(data))
        if len(old) != len(data):
            raise ProcessError("Could not read the previous value for a bulk-loot write")
        if old != data:
            previous.append((at, old))
            guest.write(at, data)

    try:
        yield write
    except BaseException as error:
        restore_error = None
        for at, old in reversed(previous):
            try:
                if guest.read(at, len(old)) != old:
                    guest.write(at, old)
            except Exception as err:
                restore_error = err
        if restore_error is not None:
            raise ProcessError(f"Could not restore all item lists after bulk loot failed: {restore_error}") from error
        raise


def _takers(gd: GameData) -> List[int]:
    out = []
    for member in range(game.PARTY_SIZE):
        rec = gd.creature(member)
        if len(rec) >= game.CREATURE_SIZE and rec[game.CREATURE_NAME] and rec[game.CREATURE_STATUS] not in STATUS_GONE:
            out.append(member)
    return out


def _destinations(gd: GameData, it: ring.Items, contents: int,
                  write: Callable[[int, bytes], None]) -> Iterator[Tuple[int, int, int]]:
    """Yield (member, list, cell) in party order, making a backpack list only when needed."""
    for member in _takers(gd):
        used = _used(gd, it, member)
        free = [cell for cell in pickpocket.BACKPACK if cell not in used]
        if not free:
            continue
        thing = pickpocket.party_list(gd, it, member, free[0], write=write)
        if thing == contents:
            raise ValueError("The container and backpack share the same item list")
        if thing is not None:
            for cell in free:
                yield member, thing, cell


def take(gd: GameData, thing: int, mode: int) -> Tuple[List[str], bool]:
    """Container THING's things into the party's backpacks (mode ALL or NO_PLAIN_WEAPONS): the dice
    log's lines, and whether anything was taken."""
    # (the gate held before the lists are read: the game busy with them, ItemsBusy, tried again in
    # a later pass; what is moved worked out from them as they are with the game held still)
    itemgate.hold(gd, require_pause=True)
    it = ring.Items(gd)
    found = _contents(gd, it, thing)
    if found is None:
        return [], False
    container, contents = found
    records = dict(it.chain(contents, inside=False))
    names = {i: gd.item_label(rec, gd.item_type_record(rec)) for i, rec in records.items()}
    plain = [i for i, rec in records.items() if mode == NO_PLAIN_WEAPONS and plain_weapon(gd, rec)]
    if plain and len(plain) == len(records):
        return ["Only plain weapons there: left where they are."], False
    got: Dict[int, List[str]] = {}
    with _loot_writes(gd) as write:
        candidates = (i for i in records if i not in plain)
        plan = dict(zip(candidates, _destinations(gd, it, contents, write)))
        if not plan:
            return (["The party's backpacks are full: nothing taken."] if records else []), False
        kept = [i for i in records if i not in plan]
        _relink(gd, it, container, contents, kept, write)
        for item, (member, destination, cell) in plan.items():
            pickpocket.link_item(it, destination, item, cell, write)
            got.setdefault(member, []).append(names[item])
    for item in plan:
        icons.fit(gd, item)
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
