"""Banter: recruits in the party talking with each other (a prototype).

The game has no banter of its own, so it is made of what it has. The Ledger keeps a flag for each
recruit, set while that recruit is in the party (IN_PARTY: by the creature's tag, recruits.TAGS
and on, and the slot not Gone); the scripts test those flags at a few moments and play a short
exchange, once (its own flag: Banter.flag):

  * an NPC just talked to: when Semyon joins with Torvak along (MEETING), and at the end of a talk
    with Kalzith (KALZITH);
  * an area: entering the slave pens (PENS, in the pens' master script);
  * a quest just done: the vulture given to Dinos (VULTURE).

Each line shows its speaker's portrait, with the speaker's name before the words.
"""

import struct
from typing import Callable, NamedTuple, Tuple

from . import game, recruits
from .recruits import SEMYON, TORVAK

# The companion's flags: each recruit in the party (the Ledger's), and each exchange once played
IN_PARTY = {SEMYON.number: 790, TORVAK.number: 791}
PORTRAITS = {SEMYON.number: 118, TORVAK.number: 100}  # (semyon.PORTRAIT, torvak.PORTRAIT)
PARTY_SEG, STATUS, GONE = 0x3972, 0x333, 8  # each party slot's status (8: Gone, dropped)


class Banter(NamedTuple):
    flag: int  # set once it has played
    needs: Tuple[recruits.Recruit, ...]  # who must be in the party (IN_PARTY)
    lines: Tuple[Tuple[recruits.Recruit, str], ...]


MEETING = Banter(792, (TORVAK,), (
    (TORVAK, "Another one? This one's thinner than a kank's leg."),
    (SEMYON, "Thin is quick, big fellow. I'll see trouble coming before it sees us. You can be "
             "the one it runs into."),
    (TORVAK, "Ha! Fair enough. Stay where I can see you, scout."),
))
KALZITH = Banter(793, (SEMYON, TORVAK), (
    (SEMYON, "A defiler, right here in the pens. They say his kind leave nothing green behind "
             "them, only ash."),
    (TORVAK, "I've watched the templars' sorcerers burn the sand black in the arena. That one has "
             "the same look about him. Hungry."),
    (SEMYON, "Then we keep him friendly, and we keep him well away from anything that grows."),
))
PENS = Banter(794, (SEMYON, TORVAK), (
    (TORVAK, "The pens. I slept on that straw for six seasons, waiting for my name to be called."),
    (SEMYON, "And they tied me to a post out on the sand for three days. Neither of us goes back "
             "in there to stay. Agreed?"),
    (TORVAK, "Agreed, little scout."),
))
VULTURE = Banter(795, (SEMYON, TORVAK), (
    (SEMYON, "Dinos looked pleased with that bird."),
    (TORVAK, "Pleased? He'll be picking feathers out of the stew for a week. Still, a full belly "
             "is a full belly."),
))
BANTERS = (MEETING, KALZITH, PENS, VULTURE)


def _test(b: Banter) -> tuple:
    parts = ["(", ("var", 0x8D, b.flag), "==", ("n", 0), ")"]
    for r in b.needs:
        parts += ["and", "(", ("var", 0x8D, IN_PARTY[r.number]), "==", ("n", 1), ")"]
    return ("expr", parts)


def play(s, b: Banter, portrait: int = 0) -> None:
    """In script S (a kalzith._Script): B, if it hasn't played and its recruits are in the party;
    then PORTRAIT shown again (the talk's own, if it goes on)."""
    def lines():
        s.flag(b.flag, 1)
        for who, text in b.lines:
            s.op(0x54, ("n", PORTRAITS[who.number]))
            s.say(f"{who.name}: {text}")
            s.page()
        if portrait:
            s.op(0x54, ("n", portrait))
    s.when(_test(b), lines)


def piece(b: Banter, base: int) -> bytes:
    """B as a piece of another script, at offset BASE (no end of its own)."""
    from .kalzith import _Script
    s = _Script()
    play(s, b)
    return s.bytes(base=base, end=False)


def with_banter(script: bytes, b: Banter, field_types: bytes = b"") -> bytes:
    """SCRIPT (a master script) with B played just before its end (once in the script)."""
    from . import gpl
    flag = gpl.encode_op((0x16, [("n", 1), ("var", 13, b.flag)]))
    if flag in script:
        return script
    ops = gpl.decode(script, field_types)
    if ops[-1].code != 0x31:
        raise gpl.ScriptError("the script doesn't end as expected")
    end = ops[-1].at
    return script[:end] + piece(b, end) + script[end:]


def in_party(gd) -> dict:
    """{recruit number: True if in the party} for each recruit with an IN_PARTY flag."""
    tags = set()
    status = gd.guest.read((gd.load_seg + PARTY_SEG) * 16 + STATUS, game.PARTY_SIZE)
    for slot, (creature, _) in enumerate(game.party_records(gd.guest, gd.ds)):
        if creature is None or status[slot] == GONE:
            continue
        tags.add(struct.unpack("<H", gd.guest.read(creature + 6, 2))[0])
    return {n: recruits.TAGS + n in tags for n in IN_PARTY}


def watch(gd) -> None:
    """Each recruit's IN_PARTY flag as the party stands (the Ledger's poll)."""
    for number, here in in_party(gd).items():
        if gd.flag(IN_PARTY[number]) != here:
            gd.set_flag(IN_PARTY[number], here)
