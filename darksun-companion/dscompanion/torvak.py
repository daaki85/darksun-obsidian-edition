"""Torvak, a half-giant gladiator in the arena's bone area at the start of a game (a prototype).

A new game starts in the arena (region 2Ah): the opening show (Celgor and the rampager), then the
party in the bone area by the great statue, before its first fight. With the Ledger, Torvak stands
there beside them: a half-giant gladiator, an Arena Champion, whom the party can talk to before
stepping out. He asks whether they are nervous about the fight and says he'll
look after them, and he joins them if asked (recruits.TORVAK, by DSCLOG's RECRUIT), so that a
player who made one character has a strong arm beside them for the first fight. With no empty
slot he says so and stays.

His object (OBJECT) is a peaceful slave's (Dinos's record) named and classed as a gladiator, with
the half-giant party figure's picture (the game's object 308, Gerakis's look). The arena's master
script makes him in the bone area the first time it runs (PLACED), as the pens' script makes Semyon in
his pen, and runs his conversation (SCRIPT) when he is talked to.
"""

import struct
from typing import Dict, Tuple

from . import gpl, recruits
from .kalzith import (ALWAYS, BEGIN, END, OJFF_PICTURE, RDFF_CLASS, RDFF_LEVEL, RDFF_NAME, RDFF_NAME_SIZE,
                      RDFF_SELF, START, TALK, _Script, leaves)
from .semyon import GONE_AT, REMOVE, _flag, recruited

OBJECT = 1007  # (free in the game's objects and the Ledger's)
NAME = "Torvak"
SLAVE, FIGURE = 183, 308  # whose record his is made from (Dinos's), and whose picture (a half-giant man's)
GLADIATOR, LEVEL = 10, 3
REGION, MASTER = 0x2A, 42  # the arena, and its master script
SCRIPT = 223  # his conversation (Kalzith's is 218, Semyon's 219, Alagorn's copies 220-222)
PORTRAIT = 100  # the game's portrait of a scarred, heavy-browed man
SPOT = (32, 11)  # (tiles) beside the gate, where a new game puts the party (488, 168: tile 30, 10),
                 # free to talk before the opening show and the first fight
MADE_AS = 6  # 25h's fifth number (as the game's for Semyon)
PLACED, MET = 787, 788  # (the companion's flags)


def object_chunks(chunks) -> Dict[Tuple[str, int], bytes]:
    """For the Ledger's copy of SEGOBJEX: his object (a half-giant's look) and record (a
    peaceful slave's, named and classed as a gladiator)."""
    if any(k not in chunks for k in (("RDFF", SLAVE), ("OJFF", SLAVE), ("OJFF", FIGURE))):
        return {}
    rec = bytearray(chunks[("RDFF", SLAVE)])
    struct.pack_into("<h", rec, RDFF_SELF, -OBJECT)
    rec[RDFF_NAME:RDFF_NAME + RDFF_NAME_SIZE] = NAME.encode("ascii").ljust(RDFF_NAME_SIZE, b"\0")
    rec[RDFF_CLASS], rec[RDFF_LEVEL] = GLADIATOR, LEVEL
    obj = bytearray(chunks[("OJFF", SLAVE)])
    obj[OJFF_PICTURE:OJFF_PICTURE + 2] = chunks[("OJFF", FIGURE)][OJFF_PICTURE:OJFF_PICTURE + 2]
    return {("OJFF", OBJECT): bytes(obj), ("RDFF", OBJECT): bytes(rec)}


def conversation() -> bytes:
    """His conversation (script SCRIPT)."""
    s = _Script()

    def reply(text):
        return lambda: (s.say(text), s.page())

    def nervous():
        s.say("You're gripping that weapon like it owes you money. Nervous about the fight?")
        s.menu([("A little, yes.", lambda: (s.say(
                    "Good. The ones who aren't nervous are the ones they drag out by the heels. Stay "
                    "close to me and keep your feet. I'll look after you."), s.page(), s.call("menu")), ALWAYS),
                ("Not at all.", lambda: (s.say(
                    "Ha! Then you're braver than I was my first time. Still, stay close. I'll look "
                    "after you all the same."), s.page(), s.call("menu")), ALWAYS)])

    def join():
        def joined():
            s.say("Then it's the two of us against whatever comes through that gate. Stay behind my "
                  "shield and keep your head down. I'll look after you.")
            s.page()
            s.op(REMOVE, ("n", -OBJECT), *(("n", v) for v in GONE_AT))
            s.leave()

        def no_room():
            s.say("You've more blades at your side than the gate has room for. I'll watch from "
                  "here.")
            s.page()
            s.call("menu")

        s.when(recruited(s, recruits.TORVAK), joined, no_room)

    def farewell():
        s.say("Keep your shield up and your back to the wall.")
        s.page()
        s.leave()

    def menu():
        s.menu([("Who are you?", reply(
                    "Torvak. Half-giant, gladiator, and still standing after more fights than I can "
                    "count. The crowd calls me the Wall."), ALWAYS),
                ("Are you fighting today?", reply(
                    "Not unless someone asks me to. The templars keep me by the gate to drag out "
                    "what's left of the new ones."), ALWAYS),
                ("What's it like out there?", nervous, ALWAYS),
                ("Fight beside me.", join, ALWAYS),
                ("Farewell.", leaves(farewell), ALWAYS)])

    s.sub("menu", menu)
    s.op(BEGIN)
    s.op(0x54, ("n", PORTRAIT))
    s.when(("expr", _flag(MET)),
           lambda: s.say("Still here? The crowd's getting restless."),
           lambda: (s.say("Easy, little one. First time out on the sand? I can smell the fear from "
                          "here."), s.flag(MET, 1)))
    s.call("menu")
    return s.bytes()


def placement(base: int) -> bytes:
    """For the end of the arena's master script, at offset BASE: him in the bone area the first
    time it runs (PLACED), and his talk command."""
    s = _Script()
    s.when(("expr", _flag(PLACED, 0)), lambda: (
        s.op(0x25, ("n", -OBJECT), ("n", 1), ("n", SPOT[0]), ("n", SPOT[1]), ("n", MADE_AS), ("n", 0)),
        s.flag(PLACED, 1)))
    s.op(TALK, ("n", START), ("n", SCRIPT), ("n", -OBJECT))
    return s.bytes(base=base, end=False)


def with_torvak(master: bytes, field_types: bytes = b"") -> bytes:
    """The arena's master script with his part (once), just before its end."""
    talk = gpl.encode_op((TALK, [("n", START), ("n", SCRIPT), ("n", -OBJECT)]))
    if talk in master:
        return master
    ops = gpl.decode(master, field_types)
    if ops[-1].code != END:
        raise gpl.ScriptError("the master script doesn't end as expected")
    end = ops[-1].at
    return master[:end] + placement(end) + master[end:]
