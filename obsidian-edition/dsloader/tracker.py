"""Watches the party and the monsters for kills, experience and level-ups.

The log notes each kill and, when the party's XP goes up (right after a kill the party makes),
lists what each character gained and for which kills, with each one's XP value from its
character sheet. A kill alone shows no XP: not every one gives the party any (the opening
fight in the arena gives none, whoever dies).

The game gives no bonus for high prime requisites, which the manual promises: 10% more XP for a
class whose prime requisites are all 16 or more. The tracker adds it to each gain it sees
(prime_bonus), whatever it came from.
"""

import struct
from typing import Dict, List, NamedTuple, Optional, Tuple

from . import aging, game
from .game import CLASS_NAMES, GameData, ordinal

XP_SETTLE = 0.5  # seconds to wait for every party member's XP to change
KILL_WINDOW = 5.0  # seconds before an XP award in which kills count towards it
# Going from one area to another, the game takes the party's XP away and gives it back a moment
# later (the log showed "XP: Azil Wildthorn -557, ..." then "+557"): a loss is held this long, and
# only logged if it isn't undone; a loss and its return log nothing
LOSS_WAIT = 60.0
# Going from one area to another, the game also drops the old area's people from the fight table
# and clears or reuses their records: none of that is a death (the log once listed every guard in
# the arena, "is killed", on leaving the pens). A creature gone from the table counts as
# killed only in the same area, its record still its own, and not when all of many go at once.
MASS_VANISH = 3
# The manual's prime requisites (0 STR to 5 CHA) of each class on a character sheet (CLASS_NAMES):
# a class whose prime requisites are all PRIME_BONUS_SCORE or more gains PRIME_BONUS_PERCENT more XP.
PRIME_REQUISITES = {**{c: (4,) for c in (1, 2, 3, 4)}, **{c: (4, 5) for c in (5, 6, 7, 8)},
                    9: (0,), 10: (0,), 11: (3,), 12: (2, 4), **{c: (0, 1, 4) for c in (13, 14, 15, 16)},
                    17: (1,)}
PRIME_BONUS_SCORE, PRIME_BONUS_PERCENT = 16, 10
ABILITY_NAMES = ("STR", "DEX", "CON", "INT", "WIS", "CHA")
XP_MOST = 2_000_000_000  # (the game's own cap, in its XP routine 6B817h)


def prime_bonus(sheet: bytes, gain: int) -> Tuple[int, List[str]]:
    """The XP a gain of GAIN on a sheet brings besides for high prime requisites: 10% for a class
    whose prime requisites on the sheet (the character's own scores, not an item's or a spell's)
    are all 16 or more. A sheet has one XP for all its classes (the game divides an award between
    them and adds one share, each class's), so a character of several classes gets 10% of the
    gain for each class that has it, divided by the classes: a fighter/thief with both 10%, with
    one 5%. A human counts only the class followed now (slot 0). (The bonus, and each such
    class's reason, "Fighter, STR 17".)"""
    if gain <= 0 or len(sheet) < game.SHEET_SIZE:
        return 0, []
    classes = list(sheet[game.SHEET_CLASSES:game.SHEET_CLASSES + 3])
    if sheet[game.SHEET_RACE] == game.HUMAN:
        classes = classes[:1]
    classes = [c for c in classes if c]
    scores = sheet[game.SHEET_ABILITIES:game.SHEET_ABILITIES + 6]
    why = []
    for cls in classes:
        primes = PRIME_REQUISITES.get(cls)
        if primes and all(scores[a] >= PRIME_BONUS_SCORE for a in primes):
            name = CLASS_NAMES[cls].split(" (")[0]
            why.append(f"{name}, " + " ".join(f"{ABILITY_NAMES[a]} {scores[a]}" for a in primes))
    if not why:
        return 0, []
    return gain * len(why) * PRIME_BONUS_PERCENT // (100 * len(classes)), why


class Member(NamedTuple):
    name: str
    xp: int
    max_hp: int
    levels: Tuple[int, int, int]
    classes: Tuple[int, int, int]
    race: int = 0


class Kill(NamedTuple):
    name: str
    xp: int
    at: float


class PartyTracker:
    def __init__(self, game_data: GameData):
        self.game = game_data
        self.members: Optional[List[Optional[Member]]] = None
        self.monsters: Dict[int, Tuple[int, str, int]] = {}  # combatant -> (creature, name, HP)
        self.region: Optional[int] = None
        self.kills: List[Kill] = []
        self.xp_before: Optional[List[Optional[Member]]] = None
        self.xp_changed_at = 0.0
        self.xp_started_at = 0.0
        self.loss: Optional[Tuple[List[Optional[Member]], float]] = None  # (XP before a loss, when)

    def reset(self) -> None:
        """Forget everything (a game was loaded)."""
        self.members = None
        self.monsters = {}
        self.region = None
        self.kills = []
        self.xp_before = None
        self.loss = None

    def _member(self, index: int) -> Optional[Member]:
        name = self.game.creature_name(index)
        sheet = self.game.sheet(index)
        if len(sheet) < game.SHEET_SIZE or not self.game.creature(index)[game.CREATURE_NAME]:
            return None
        return Member(name, struct.unpack_from("<I", sheet, game.SHEET_XP)[0],
                      struct.unpack_from("<h", sheet, game.SHEET_MAX_HP)[0],
                      tuple(sheet[game.SHEET_LEVELS:game.SHEET_LEVELS + 3]),
                      tuple(sheet[game.SHEET_CLASSES:game.SHEET_CLASSES + 3]), sheet[game.SHEET_RACE])

    def check(self, now: float) -> List[str]:
        out = self._check_monsters(now)
        members = [self._member(i) for i in range(game.PARTY_SIZE)]
        if self.members is None:
            self.members = members
            return out
        for old, new in zip(self.members, members):
            if old and new and old.name == new.name:
                out += self._level_changes(old, new)
        if any(old and new and old.name == new.name and new.xp != old.xp for old, new in zip(self.members, members)):
            if self.xp_before is None:
                self.xp_before = self.members
                self.xp_started_at = now
            self.xp_changed_at = now
        self.members = members
        if self.xp_before is not None and now - self.xp_changed_at >= XP_SETTLE:
            before, self.xp_before = self.xp_before, None
            if self.loss is not None:
                before, self.loss = self.loss[0], None  # (back, or not, from the held loss)
            elif self._only_losses(before, members):
                self.loss = (before, now)  # held: it may be an area change's
                return out
            out += self._xp_line(before, members, bonuses=self._prime_bonuses(before, members))
        elif self.loss is not None and self.xp_before is None and now - self.loss[1] >= LOSS_WAIT:
            before, self.loss = self.loss[0], None
            out += self._xp_line(before, members)
        return out

    def _prime_bonuses(self, before: List[Optional[Member]], after: List[Optional[Member]]) -> Dict[int, str]:
        """Give each member who gained XP the bonus for their prime requisites (prime_bonus), on
        their sheet, and remember their XP with it, so that it isn't taken for a gain of its own.
        A level the bonus alone reaches comes with the game's next award or level check. (Each
        member's note for the XP line.)"""
        notes = {}
        for i, (old, new) in enumerate(zip(before, after)):
            if not (old and new and old.name == new.name and new.xp > old.xp):
                continue
            bonus, why = prime_bonus(self.game.sheet(i), new.xp - old.xp)
            if not bonus:
                continue
            at = aging.sheet_address(self.game, i)
            xp = struct.unpack("<I", self.game.guest.read(at + game.SHEET_XP, 4))[0]  # (as it is now)
            given = min(xp + bonus, max(xp, XP_MOST)) - xp
            if not given:
                continue
            self.game.guest.write(at + game.SHEET_XP, struct.pack("<I", xp + given))
            after[i] = new._replace(xp=new.xp + given)
            notes[i] = f"{given:+d} for {'; '.join(why)}"
        return notes

    @staticmethod
    def _only_losses(before: List[Optional[Member]], after: List[Optional[Member]]) -> bool:
        changes = [new.xp - old.xp for old, new in zip(before, after) if old and new and old.name == new.name]
        return any(changes) and all(c <= 0 for c in changes)

    def _check_monsters(self, now: float) -> List[str]:
        out = []
        combatants = {c: i for c, i in self.game.combatants().items() if c >= game.PARTY_SIZE and i >= game.PARTY_SIZE}
        count = max(list(combatants.values()) + [i for i, _, _ in self.monsters.values()] + [0]) + 1
        table = self.game.creatures(count)

        def hp(index: int) -> Optional[int]:
            at = index * game.CREATURE_SIZE
            return struct.unpack_from("<h", table, at)[0] if at + 2 <= len(table) else None

        seen = {c: (i, self.game.creature_name(i) if c not in self.monsters else self.monsters[c][1], hp(i))
                for c, i in combatants.items() if hp(i) is not None}
        region, self.region = self.region, self.game.region()
        if region != self.region:  # a new area: its people, not deaths
            self.monsters = seen
            return out
        gone = [c for c, (i, _, _) in self.monsters.items() if seen.get(c, (None,))[0] != i]
        area_change = len(gone) >= MASS_VANISH and len(gone) == len(self.monsters)
        for combatant, (index, name, old_hp) in self.monsters.items():
            if combatant in gone:  # its record may remain, if it is still its own
                if area_change or self.game.creature_name(index) != name:
                    continue
                now_hp = hp(index)
            else:
                now_hp = seen[combatant][2]
            if now_hp is not None and old_hp > 0 >= now_hp:
                out.append(self._killed(index, name, now))
        self.monsters = seen
        return out

    def _killed(self, index: int, name: str, now: float) -> str:
        sheet = self.game.sheet(index)
        xp = struct.unpack_from("<I", sheet, game.SHEET_XP_VALUE)[0] if len(sheet) >= 8 else 0
        self.kills.append(Kill(name, xp, now))
        return f"{name} is killed"  # (its XP only with the party's gain: not every kill gives any)

    def _level_changes(self, old: Member, new: Member) -> List[str]:
        out = []
        for slot in range(3):
            if new.levels[slot] > old.levels[slot] and new.classes[slot]:
                cls = CLASS_NAMES.get(new.classes[slot], f"class {new.classes[slot]}")
                out.append(f"{new.name} is now a {ordinal(new.levels[slot])} level {cls}")
        if new.max_hp != old.max_hp and out:
            out.append(f"    max HP {old.max_hp} -> {new.max_hp} ({new.max_hp - old.max_hp:+d})")
        elif out and new.race == game.HUMAN and sum(1 for c in new.classes if c) > 1:
            # (the game's level-up routine, 87250h: a human's new class rolls once it passes the old)
            out.append("    no hit points: a human who changed class gains them in the new class only once "
                       "its level passes the old class's")
        elif out and sum(1 for c in new.classes if c) > 1:
            # every new class level rolls, but the game divides the whole total by the classes
            out.append("    max HP unchanged: the game divides the hit point total by the classes, and this "
                       "level's roll left a fraction, which counts at a later level")
        return out

    def _xp_line(self, before: List[Optional[Member]], after: List[Optional[Member]],
                 bonuses: Optional[Dict[int, str]] = None) -> List[str]:
        bonuses = bonuses or {}
        gains = [f"{new.name} {new.xp - old.xp:+d}" + (f" ({bonuses[i]})" if i in bonuses else "")
                 for i, (old, new) in enumerate(zip(before, after))
                 if old and new and old.name == new.name and new.xp != old.xp]
        if not gains:
            return []
        kills = [k for k in self.kills if self.xp_started_at - KILL_WINDOW <= k.at]
        self.kills = []
        line = "XP: " + ", ".join(gains)
        if kills:
            total = sum(k.xp for k in kills)
            line += f" (for {', '.join(f'{k.name} {k.xp}' for k in kills)}" + \
                (f": {total} XP)" if len(kills) > 1 else ")")
        return [line]
