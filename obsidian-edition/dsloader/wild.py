"""A Blood-Fury's Wild Fighting (kits.py): checked for each one as a fight's first round begins,
kept for the fight, and given to DSCLOG (its KIT_WILD bits) for to hit, damage, attacks and AC.

The check is the Wild Fighting proficiency's (The Complete Barbarian's Handbook): a d20 against
CON (+0). Passed, 1 more attack a round in melee and 3 more damage; failed, 3 worse to hit and AC 3
worse (no worse than 10); either for the whole fight.
"""

import random
from typing import Callable, Dict, List

from . import game, kits

TSR_WILD = 355  # DSCLOG's header (KIT_WILD): bit N member N's check failed, bit N + 4 passed


class WildFights:
    def __init__(self):
        self.fighting: Dict[int, bool] = {}  # party member fighting wild: whether its check passed

    def _write(self, gd, tsr_hdr) -> None:
        gd.wild = dict(self.fighting)
        if tsr_hdr is not None:
            bits = 0
            for member, passed in self.fighting.items():
                bits |= 1 << (member + 4 if passed else member)
            gd.guest.write(tsr_hdr + TSR_WILD, bytes((bits,)))

    def stop(self, gd, tsr_hdr) -> None:
        """The fight over."""
        self.fighting.clear()
        self._write(gd, tsr_hdr)

    def round(self, gd, tsr_hdr, number: int,
              roll: Callable[[int, int], int] = random.randint) -> List[str]:
        """A round begins (NUMBER 1: a new fight's first): lines for the log."""
        if number != 1:
            return []
        self.stop(gd, tsr_hdr)  # (a fight whose end went unseen)
        out: List[str] = []
        for member in range(game.PARTY_SIZE):
            rec = gd.creature(member)
            if len(rec) < game.CREATURE_SIZE or not rec[game.CREATURE_NAME] \
                    or rec[game.CREATURE_STATUS] not in game.STATUS_ABLE \
                    or kits.BLOOD_FURY not in gd.kit_ids(member):
                continue
            who = gd.creature_name(member)
            con, d20 = rec[game.CREATURE_ABILITIES + 2], roll(1, 20)
            passed = kits.wild_check(con, d20)
            self.fighting[member] = passed
            check = f"{who} fights wild: d20 = {d20}, needs {con} or less (CON {con})"
            if passed:
                out.append(f"{check} -> 1 more attack a round and +3 damage for the fight")
            else:
                out.append(f"{check} -> fails: -3 to hit and AC 3 worse for the fight")
        self._write(gd, tsr_hdr)
        return out
