"""A lock a thief failed to pick is out of reach until the thief gains a level (Player's Option:
Skills & Powers: "If a thief fails to open a lock, he cannot attempt to open that lock again until
advancing a level"), with Thieves as in AD&D (RULE_THIEF_TABLE).

The game rolls open locks only in its scripts' skill checks (803B8h: a safe, a grate, cell doors,
and the Loader's Pehtucl's chest), for the character who used the lock. The dice log sees each roll
(PERCENT_SITE) and, for a party member's failure, remembers the lock with the pockets tried
(DiceLog.picked, KEY): the party, the region, the lock (the thing the script was started on, by
what it is: its object and its place on the map, `o1234@x,y`, since the game hands the map's
thing numbers out again as it makes and drops things; an older key's bare thing number is read
as before), the member and its thief level then. A save loaded from before it forgets it, as a pocket tried.

LOCK_BARRED (DSCLOG's, its offset at the header's +1844) holds, for each member 0-3, up to LOCK_MAX
(region, thing) word pairs: the locks that member failed at the thief level it has now. DSCLOG's
LOCK_SITE (the check's chance, 803D3h) makes the chance LOCK_NEVER for them, which no d100 is under,
and the dice log says why. A level gained, the pair is gone from the table and the lock can be tried.
"""

import struct
from typing import Dict, Iterable, List, Mapping, Optional, Tuple

from . import game, pickpocket
from .game import GameData

TSR_HDR_OFF, TSR_LOCK_OFF = 20, 1844  # DSCLOG's header: its own offset; LOCK_BARRED's
LOCK_MAX = 4  # (DSCLOG's) pairs a member
NONE = 0xFFFF
OPEN_LOCKS = 1  # (game.THIEF_SKILLS' second)
NEVER = -2000  # (DSCLOG's LOCK_NEVER: the chance of a lock out of reach)
# the map things' object numbers and places (DS), a record of THING_SIZE bytes each (game's: the sequel's
# own in ravlog.rav_items: 67D6h and 67C5h, 25h bytes)
THING_OBJECT, POSITIONS, THING_SIZE = game.THING_OBJECT, game.POSITIONS, 32


def talk_thing(gd: GameData) -> Optional[int]:
    """The thing the running script was started on (the lock used), or None."""
    thing, = struct.unpack("<h", gd.guest.read((gd.load_seg + game.TALK_SEG) * 16 + game.TALK_TARGET, 2))
    return thing if 0 <= thing < game.THINGS else None


def key(party: str, region: int, thing, member: str, level: int) -> str:
    """THING: the lock's identity (identity()), or a bare thing number (older keys, tests)."""
    return f"{party}|lock|{region}|{thing}|{member}|L{level}"


def identity(gd: GameData, thing: int) -> Optional[str]:
    """THING's lasting name: its object and its place on the map ("o1234@736,1376"), or None."""
    if not 0 <= thing < game.THINGS:
        return None
    base = gd.ds * 16
    obj, = struct.unpack("<h", gd.guest.read(base + THING_OBJECT + thing * THING_SIZE, 2))
    x, y = struct.unpack("<HH", gd.guest.read(base + POSITIONS + thing * THING_SIZE, 4))
    return f"o{abs(obj)}@{x},{y}" if obj else None


def things_now(gd: GameData, ident: str) -> List[int]:
    """The map things that are IDENT now (its thing number may differ from when it was failed)."""
    data_obj = gd.guest.read(gd.ds * 16 + THING_OBJECT, game.THINGS * THING_SIZE)
    data_pos = gd.guest.read(gd.ds * 16 + POSITIONS, game.THINGS * THING_SIZE)
    out = []
    for t in range(game.THINGS):
        obj, = struct.unpack_from("<h", data_obj, t * THING_SIZE)
        x, y = struct.unpack_from("<HH", data_pos, t * THING_SIZE)
        if obj and f"o{abs(obj)}@{x},{y}" == ident:
            out.append(t)
    return out


def failed_key(gd: GameData, member: int) -> Optional[str]:
    """The key to remember for MEMBER's failure on the lock being used now (None: no lock known)."""
    thing = talk_thing(gd)
    if thing is None:
        return None
    lock = identity(gd, thing)
    return key(gd.creature_name(0), gd.region(), lock if lock is not None else thing,
               gd.creature_name(member), pickpocket.thief_level(gd, member))


def barred(gd: GameData, tried: Iterable[str], when: Optional[Mapping[str, Optional[int]]] = None
           ) -> List[List[Tuple[int, int]]]:
    """For each member 0-3, the (region, thing) of each lock in TRIED it failed at its thief level now,
    in the region the party is in (at most LOCK_MAX: the latest kept, by WHEN, each key's game time as
    DiceLog.picked_at keeps it; a key with none counts as the oldest)."""
    when = when or {}
    tried = sorted(set(tried), key=lambda k: (when.get(k) or 0, k))
    party, region = gd.creature_name(0), gd.region()
    out: List[List[Tuple[int, int]]] = []
    for member in range(game.PARTY_SIZE):
        name, level = gd.creature_name(member), pickpocket.thief_level(gd, member)
        head = f"{party}|lock|{region}|"
        tail = f"|{name}|L{level}"
        things: Dict[int, None] = {}  # (in the order failed, the latest last)
        for k in tried:
            if not (k.startswith(head) and k.endswith(tail)):
                continue
            lock = k[len(head):-len(tail)]
            found = [int(lock)] if lock.isdigit() else things_now(gd, lock) if lock.startswith("o") else []
            for t in found:  # (an older key: the thing number as it was)
                things.pop(t, None)
                things[t] = None
        out.append([(region, t) for t in things][-LOCK_MAX:])
    return out


def table(rows: List[List[Tuple[int, int]]]) -> bytes:
    """LOCK_BARRED's bytes for BARRED's rows."""
    out = bytearray()
    for member in range(game.PARTY_SIZE):
        pairs = rows[member] if member < len(rows) else []
        for i in range(LOCK_MAX):
            region, thing = pairs[i] if i < len(pairs) else (NONE, NONE)
            out += struct.pack("<HH", region & 0xFFFF, thing & 0xFFFF)
    return bytes(out)


def write(gd: GameData, tsr_hdr: int, data: bytes) -> bool:
    """LOCK_BARRED written; False when DSCLOG has none (its offset 0: not this build's)."""
    base = tsr_hdr - struct.unpack("<H", gd.guest.read(tsr_hdr + TSR_HDR_OFF, 2))[0]
    offset = struct.unpack("<H", gd.guest.read(tsr_hdr + TSR_LOCK_OFF, 2))[0]
    if not offset:
        return False
    gd.guest.write(base + offset, data)
    return True
