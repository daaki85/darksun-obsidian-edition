"""Psionic Blast's imagined wounds healed as the fight ends (the game's bug: always on).

The game's Psionic Blast (the effect routine's case 169, 796CBh) takes a target that fails its
save down to a fifth of its most hit points, for good. The power's wounds are imagined (AD&D's:
the victim believes it has lost them, and wakes from it), so DSCLOG's PROBE_WORN, at the
routine's "or byte [si],1" after the damage (79707h), adds each party member's loss to BLAST_HP;
once the fight is over (the game's fight flag down FIGHT_OVER seconds) the Loader gives the
hit points back to each member still standing (Okay), no more than its most, says so in the
dice log, and clears the field. While a member has them still to come, a blow that would kill it
knocks it out instead (PROBE_WORN at the damage routine's death test, 5860Bh: the blast's wounds
are imagined; Disintegrate still kills); one Out Cold at the fight's end gets them back too and
wakes, as the game wakes a creature (Okay, with hit points: 7C1F9h). One Dying or dead keeps
what it has. A game loaded (the game's clock gone back) clears the field with nothing given.
"""

import struct
from typing import Callable, List, Optional

from . import game

TSR_BLAST = 1814  # DSCLOG's header (BLAST_HP): a word for each of combatants 0-3 (the party), the
                  #   hit points Psionic Blast took this fight
FIGHT_OVER = 2.0  # seconds the fight flag stays down before the fight counts as over (dicelog's)


def take(guest, tsr_hdr: int) -> List[int]:
    """BLAST_HP's four words, cleared."""
    data = guest.read(tsr_hdr + TSR_BLAST, 2 * game.PARTY_SIZE)
    guest.write(tsr_hdr + TSR_BLAST, bytes(2 * game.PARTY_SIZE))
    return [max(0, v) for v in struct.unpack(f"<{game.PARTY_SIZE}h", data)]


def give_back(gd, tsr_hdr: int) -> List[str]:
    """The hit points Psionic Blast took this fight given back to the party (the module's
    notes): lines for the log."""
    out: List[str] = []
    table = game.far_pointer(gd.guest, gd.ds, game.CREATURES_PTR)
    for combatant, lost in enumerate(take(gd.guest, tsr_hdr)):
        member = gd.combatant_creature(combatant) if lost > 0 else None  # (the party's things 0-3)
        if member is None or not 0 <= member < game.PARTY_SIZE:
            continue
        rec, sheet = gd.creature(member), gd.sheet(member)
        if len(rec) < game.CREATURE_SIZE or len(sheet) < game.SHEET_SIZE:
            continue
        who = gd.creature_name(member)
        status = rec[game.CREATURE_STATUS]
        if status not in (game.STATUS_OKAY, game.OUT_COLD):
            out.append(f"{who}'s {lost} hit points lost to Psionic Blast don't come back: "
                       f"{who} is {game.STATUS_NAMES.get(status, 'down').lower()}")
            continue
        hp, = struct.unpack_from("<h", rec, 0)
        hp = max(hp, 0)
        most, = struct.unpack_from("<h", sheet, game.SHEET_MAX_HP)
        now = min(most, hp + lost) if most > 0 else hp + lost
        if now <= hp:
            continue
        at = table + member * game.CREATURE_SIZE
        gd.guest.write(at, struct.pack("<h", now))
        woke = status == game.OUT_COLD
        if woke:
            gd.guest.write(at + game.CREATURE_STATUS, bytes((game.STATUS_OKAY,)))
        out.append(f"{who} {'wakes and ' if woke else ''}shakes off Psionic Blast's imagined wounds "
                   f"as the fight ends: +{now - hp} HP, now {now}/{most}")
    return out


class BlastWatch:
    """Gives the hit points back once a fight is over."""

    def __init__(self):
        self._fight_seen = False
        self._out_since: Optional[float] = None
        self._clock: Optional[int] = None

    def tick(self, gd, tsr_hdr: Optional[int], now: float,
             in_combat: Optional[Callable[[], bool]] = None) -> List[str]:
        if gd is None or tsr_hdr is None:
            return []
        clock = gd.game_time()
        if clock is not None:
            if self._clock is not None and clock < self._clock:  # a game loaded: nothing to give
                take(gd.guest, tsr_hdr)
                self._fight_seen, self._out_since = False, None
            self._clock = clock
        if (in_combat or gd.in_combat)():
            self._fight_seen, self._out_since = True, None
            return []
        if not self._fight_seen:
            return []
        if self._out_since is None:
            self._out_since = now
        if now - self._out_since < FIGHT_OVER:
            return []
        self._fight_seen, self._out_since = False, None
        return give_back(gd, tsr_hdr)
