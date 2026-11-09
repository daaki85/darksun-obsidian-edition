"""A fight's tally, said as it ends: the rounds, the kills, the damage the party dealt and took, and
each member's hits, damage and kills (the readable layout's summary, mock-up G).

It reads the dice log's own lines as they are written (feed): the rounds, the weapon attacks and
their hits' damage, a spell's damage to each creature, the kills. The dice log calls end() when the
fight is over (the game's fight flag down a moment after it was up), and writes what it gives:

    Fight over: 3 rounds, 4 kills; the party dealt 61 damage and took 19
        Seneca: 2 of 2 attacks hit, 30 dealt, 1 kill
        Jenna: 3 of 3 attacks hit, 22 dealt, took 6

A kill is put to whoever hurt the creature last (a weapon's hit, or the caster of the spell that
hurt it, when a saving throw against it or the spell's attack roll named the caster). A spell's
damage counts as the party's only when its caster is known to be a party member (a monster's spells
on its own side, and a spell whose caster no line named, are not the party's)."""

import re
from typing import Callable, Dict, List, Optional

from .ledger import save_source

ROUND = re.compile(r"Round (?P<n>\d+)\b")
ATTACK = re.compile(r"(?P<who>.+?) attacks (?P<target>.+?)(?: from behind| BACKSTAB| unseen)?(?: with .+?)?: d20 = .*"
                    r"-> (?P<result>HIT|miss)$")
HIT_FOR = re.compile(r"  (?P<who>.+?) hits (?P<target>.+?) for (?P<n>\d+): ")
TAKES = re.compile(r"  (?P<who>.+?) takes (?P<n>\d+) from (?P<what>.+?)(?:,| \(|$)")
KILLED = re.compile(r"(?P<who>.+) is killed$")
SAVE_VS = re.compile(r".+?'s saving throw vs (?P<what>.+?): ")
SPELL_ATTACK = re.compile(r"(?P<who>.+?)'s (?P<what>.+?) at .+?: (?:touch )?attack d20 = ")


class Member:
    def __init__(self):
        self.attacks = self.hits = self.dealt = self.took = self.kills = 0


class FightTally:
    def __init__(self, is_party: Callable[[str], bool]):
        self.is_party = is_party
        self._reset()

    def _reset(self) -> None:
        self.rounds = 0
        self.kills = 0
        self.dealt = 0  # (by the whole party, spells too)
        self.took = 0
        self.members: Dict[str, Member] = {}
        self._last_hurt: Dict[str, str] = {}  # creature -> the party member who hurt it last
        self._caster: Dict[str, str] = {}  # spell -> who cast it last (a party member or not)

    def _member(self, name: str) -> Member:
        return self.members.setdefault(name, Member())

    @property
    def started(self) -> bool:
        return self.rounds > 0

    def feed(self, lines: List[str]) -> None:
        for line in lines:
            self._line(line)

    def _line(self, line: str) -> None:
        m = ROUND.match(line)
        if m:
            n = int(m.group("n"))
            if n == 1 and self.rounds > 1:  # (a new fight never told as over: start afresh)
                self._reset()
            self.rounds = max(self.rounds, n)
            return
        if not self.started:
            return
        m = ATTACK.match(line)
        if m:
            if self.is_party(m.group("who")):
                member = self._member(m.group("who"))
                member.attacks += 1
                member.hits += m.group("result") == "HIT"
            return
        m = HIT_FOR.match(line)
        if m:
            self._hurt(m.group("who"), m.group("target"), int(m.group("n")))
            return
        m = TAKES.match(line)
        if m:
            self._hurt(self._caster.get(m.group("what")), m.group("who"), int(m.group("n")))
            return
        m = KILLED.match(line)
        if m and not line.startswith(" "):
            who = m.group("who")
            if not self.is_party(who):
                self.kills += 1
                by = self._last_hurt.get(who)
                if by:
                    self._member(by).kills += 1
            return
        m = SAVE_VS.match(line)  # (a spell's caster: named on its targets' saving throws ...)
        if m:
            spell, who, _ = save_source(m.group("what"))
            if who:
                self._caster[re.sub(r" \(.*\)$", "", spell)] = who
            return
        m = SPELL_ATTACK.match(line)  # (... and on its attack roll)
        if m:
            self._caster[m.group("what")] = m.group("who")

    def _hurt(self, by: Optional[str], target: str, n: int) -> None:
        if self.is_party(target):
            self.took += n
            self._member(target).took += n
        elif by is not None and self.is_party(by):
            self.dealt += n
            self._member(by).dealt += n
            self._last_hurt[target] = by
        elif by is not None:
            self._last_hurt.pop(target, None)  # (a monster hurt it last: its kill no member's)

    def end(self) -> List[str]:
        """The tally's lines, and the tally started afresh (nothing if no round was seen)."""
        if not self.started:
            return []
        rounds = f"{self.rounds} round{'s' if self.rounds != 1 else ''}"
        kills = f"{self.kills} kill{'s' if self.kills != 1 else ''}"
        out = [f"Fight over: {rounds}, {kills}; the party dealt {self.dealt} damage and took {self.took}"]
        for name, m in self.members.items():
            parts = []
            if m.attacks:
                parts.append(f"{m.hits} of {m.attacks} attacks hit")
            if m.dealt:
                parts.append(f"{m.dealt} dealt")
            if m.kills:
                parts.append(f"{m.kills} kill{'s' if m.kills != 1 else ''}")
            if m.took:
                parts.append(f"took {m.took}")
            if parts:
                out.append(f"    {name}: " + ", ".join(parts))
        self._reset()
        return out
