"""A Battle Dancer's dance (kits.py): rolled for each one as a fight's first round begins, counted
down round by round, and given to DSCLOG (its KIT_DANCE bytes) to add to hit, to damage and to AC.

The dance is the Dancing proficiency's check at -4: a d20 against DEX - 4 (a natural 20 always
fails). Danced well (the roll that or less), +1 for as many rounds as it is above the roll (at
least 1); stumbled, -1 for 1d8 rounds.
The round it's rolled in is the first; it ends before the round after its last, and with the fight.
"""

import random
import struct
from typing import Callable, Dict, List

from . import game, kits

TSR_DANCE = 351  # DSCLOG's header: a signed byte for each party member (KIT_DANCE)


class Dances:
    def __init__(self):
        self.left: Dict[int, int] = {}  # party member: rounds of its dance left, this one counted

    def _set(self, gd, tsr_hdr, member: int, bonus: int) -> None:
        if bonus:
            gd.dance[member] = bonus
        else:
            gd.dance.pop(member, None)
        if tsr_hdr is not None:
            gd.guest.write(tsr_hdr + TSR_DANCE + member, struct.pack("b", bonus))

    def stop(self, gd, tsr_hdr) -> None:
        """Every dance over (the fight's end)."""
        for member in list(self.left) + list(gd.dance):
            self._set(gd, tsr_hdr, member, 0)
        self.left.clear()

    def round(self, gd, tsr_hdr, number: int,
              roll: Callable[[int, int], int] = random.randint) -> List[str]:
        """A round begins (NUMBER 1: a new fight's first): lines for the log."""
        out: List[str] = []
        if number == 1:
            self.stop(gd, tsr_hdr)
            for member in range(game.PARTY_SIZE):
                rec = gd.creature(member)
                if len(rec) < game.CREATURE_SIZE or not rec[game.CREATURE_NAME] \
                        or rec[game.CREATURE_STATUS] not in game.STATUS_ABLE \
                        or kits.BATTLE_DANCER not in gd.kit_ids(member):
                    continue
                dex, d20 = rec[game.CREATURE_ABILITIES + 1], roll(1, 20)
                fail = roll(1, kits.DANCE_FAIL_DIE)
                bonus, rounds = kits.dance(dex, d20, fail)
                self.left[member] = rounds
                self._set(gd, tsr_hdr, member, bonus)
                who = gd.creature_name(member)
                plural = "s" if rounds != 1 else ""
                if bonus > 0:
                    out.append(f"{who} dances: d20 = {d20}, needs {min(dex + kits.DANCE_CHECK, 19)} or less (DEX {dex} {kits.DANCE_CHECK}) -> +1 to hit, "
                               f"damage and AC for {rounds} round{plural}")
                else:
                    out.append(f"{who} dances: d20 = {d20}, needs {min(dex + kits.DANCE_CHECK, 19)} or less (DEX {dex} {kits.DANCE_CHECK}) -> stumbles: "
                               f"-1 to hit, damage and AC for {rounds} round{plural} (d{kits.DANCE_FAIL_DIE} = {fail})")
            return out
        for member in list(self.left):
            self.left[member] -= 1
            if self.left[member] <= 0:
                del self.left[member]
                self._set(gd, tsr_hdr, member, 0)
                out.append(f"{gd.creature_name(member)}'s dance is over")
        return out
