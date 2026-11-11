"""A lock a thief failed to pick is out of reach until the thief gains a level (Player's Option:
Skills & Powers: "If a thief fails to open a lock, he cannot attempt to open that lock again until
advancing a level"), with Thieves as in AD&D (RULE_THIEF_TABLE).

The game rolls open locks only in its scripts' skill checks (803B8h: a safe, a grate, cell doors,
and the Loader's Pehtucl's chest), for the character who used the lock. The dice log sees each roll
(PERCENT_SITE) and, for a party member's failure, remembers the lock with the pockets tried
(DiceLog.picked, KEY): the party, the region, the thing the script was started on (the lock), the
member and its thief level then. A save loaded from before it forgets it, as a pocket tried.

LOCK_BARRED (DSCLOG's, its offset at the header's +1844) holds, for each member 0-3, up to LOCK_MAX
(region, thing) word pairs: the locks that member failed at the thief level it has now. DSCLOG's
LOCK_SITE (the check's chance, 803D3h) makes the chance LOCK_NEVER for them, which no d100 is under,
and the dice log says why. A level gained, the pair is gone from the table and the lock can be tried.
"""

import struct
from typing import Iterable, List, Optional, Tuple

from . import game, pickpocket
from .game import GameData

TSR_HDR_OFF, TSR_LOCK_OFF = 20, 1844  # DSCLOG's header: its own offset; LOCK_BARRED's
LOCK_MAX = 4  # (DSCLOG's) pairs a member
NONE = 0xFFFF
OPEN_LOCKS = 1  # (game.THIEF_SKILLS' second)
NEVER = -2000  # (DSCLOG's LOCK_NEVER: the chance of a lock out of reach)


def talk_thing(gd: GameData) -> Optional[int]:
    """The thing the running script was started on (the lock used), or None."""
    thing, = struct.unpack("<h", gd.guest.read((gd.load_seg + game.TALK_SEG) * 16 + game.TALK_TARGET, 2))
    return thing if 0 <= thing < game.THINGS else None


def key(party: str, region: int, thing: int, member: str, level: int) -> str:
    return f"{party}|lock|{region}|{thing}|{member}|L{level}"


def failed_key(gd: GameData, member: int) -> Optional[str]:
    """The key to remember for MEMBER's failure on the lock being used now (None: no lock known)."""
    thing = talk_thing(gd)
    if thing is None:
        return None
    return key(gd.creature_name(0), gd.region(), thing, gd.creature_name(member),
               pickpocket.thief_level(gd, member))


def barred(gd: GameData, tried: Iterable[str]) -> List[List[Tuple[int, int]]]:
    """For each member 0-3, the (region, thing) of each lock in TRIED it failed at its thief level now,
    in the region the party is in (at most LOCK_MAX: the latest kept)."""
    tried = set(tried)
    party, region = gd.creature_name(0), gd.region()
    out: List[List[Tuple[int, int]]] = []
    for member in range(game.PARTY_SIZE):
        name, level = gd.creature_name(member), pickpocket.thief_level(gd, member)
        head = f"{party}|lock|{region}|"
        tail = f"|{name}|L{level}"
        things = sorted(int(k[len(head):-len(tail)]) for k in tried
                        if k.startswith(head) and k.endswith(tail) and k[len(head):-len(tail)].isdigit())
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
