"""Mirlon's thieves' tools for a thief who takes his deal.

Mirlon, in the slave pens, carries a set of Thieves' Tools (worldgear.py), until now only for a
party that kills him. With the Loader, a party led by a thief can have them without a fight: when
the leader agrees to fetch his gem ("It's a deal! I'll be back soon.", once he has said where it
is), he sees what trade they're in and hands his tools over.

The game's scripts can't ask a character's class, so the Loader keeps a flag his script reads
(OFFER): set while the leader (the one whose turn it is, who talks) is a thief and Mirlon still
carries the tools, and the gift not yet made. In the Loader's copy of his script (143), that
reply's jump (to "Good luck!") goes to code after the script's end (as alagorn.py's): if OFFER,
his words and the Loader's flag GIVEN; then on to "Good luck!". On GIVEN the Loader moves his set,
the item itself (so killing him later finds none), into the leader's pack, once (MOVED).
"""

import struct
from typing import List, Optional, Tuple

from . import game, gpl, pickpocket, ring, tools
from .game import GameData
from .kalzith import _Script, _lines
from .pensasks import GOTO, LONGEST

SCRIPT = 143
PENS, NAME = 0x29, "Mirlon"
OFFER, GIVEN, MOVED = 800, 801, 802  # (the Loader's flags: past alagorn.py's, 784 on)
FLAG_READ, MENU = 141, 0x48
DEAL = "It's a deal! I'll be back soon. "  # (the reply, as the game has it)
WORDS = ("Wait. You've got a thief's hands -- I saw how you looked over my things. Take my tools; "
         "they'll serve you better than me in here. Call it an advance on the gem.")
THIEF = game.THIEF


def _deal(ops) -> Optional[Tuple[int, dict]]:
    """The menu (its index) and its reply DEAL, or None."""
    for i, op in enumerate(ops):
        if op.code != MENU:
            continue
        for reply in op.args[0]["replies"]:
            if reply["text"] == ("str", DEAL) and reply["goto"][0] == "n":
                return i, reply
    return None


def with_tools(script: bytes, field_types: bytes) -> bytes:
    """His script (the game's) with the tools given on the deal (unchanged if it isn't as
    expected)."""
    if gpl.encode_expr(("str", _lines(WORDS)[0])) in script:
        return script  # (done already)
    ops = gpl.decode(script, field_types)
    found = _deal(ops)
    if found is None:
        return script
    i, reply = found
    back = reply["goto"][1]
    s = _Script()
    s.label("deal")
    s.when(("expr", [("var", FLAG_READ, OFFER), "==", ("n", 1)]), lambda: (s.say(WORDS), s.page(), s.flag(GIVEN, 1)))
    s.op(GOTO, ("n", back))
    added = s.bytes(base=len(script), end=False)
    out = bytearray(script) + added
    if len(out) > LONGEST:
        return script
    menu = ops[i]
    old = gpl.encode_op(menu)
    reply["goto"] = ("n", s.at["deal"])
    new = gpl.encode_op(menu)
    if len(new) != len(old) or bytes(out[menu.at:menu.at + len(old)]) != old:
        return script
    out[menu.at:menu.at + len(new)] = new
    return bytes(out)


def script_chunks(chunks, field_types: bytes):
    key = ("GPL ", SCRIPT)
    if key not in chunks:
        return {}
    changed = with_tools(chunks[key], field_types)
    return {key: changed} if changed != chunks[key] else {}


# ---------------------------------------------------------------------------------------------
# In the game: the flag his script reads, and the tools handed over

def _mirlon(gd: GameData) -> Optional[int]:
    """His creature record, alive, among those of the pens."""
    for index in range(game.PARTY_SIZE, 128):
        rec = gd.creature(index)
        if len(rec) < game.CREATURE_SIZE:
            return None
        if gd.creature_name(index) == NAME and struct.unpack_from("<h", rec, 0)[0] > 0:
            return index
    return None


def _his_tools(gd: GameData, it: ring.Items, creature: int) -> Optional[Tuple[int, int, int]]:
    """(list, item, the item before it or -1) of the tools he carries, or None."""
    rec = gd.creature(creature)
    for list_no, offset in enumerate(game.CREATURE_ITEM_LISTS):
        thing, = struct.unpack_from("<h", rec, offset)
        before = -1
        for item, data in it.chain(thing, inside=False):
            if tools.is_tools(data):
                return list_no, item, before
            before = item
    return None


def is_thief(gd: GameData, member: int) -> bool:
    sheet = gd.sheet(member)
    rec = gd.creature(member)
    return len(sheet) >= game.SHEET_SIZE and len(rec) >= game.CREATURE_SIZE and rec[game.CREATURE_NAME] != 0 \
        and THIEF in sheet[game.SHEET_CLASSES:game.SHEET_CLASSES + 3] and rec[game.CREATURE_STATUS] in game.STATUS_ABLE


def watch(gd: GameData) -> List[str]:
    """In the pens: OFFER kept as it stands; once his script has set GIVEN, his tools moved into
    the leader's pack (MOVED). Lines for the dice log."""
    if gd.region() != PENS or gd.flag(MOVED):
        return []
    leader = gd.whose_turn()
    mirlon = _mirlon(gd)
    if mirlon is None or leader is None or not 0 <= leader < game.PARTY_SIZE:
        return []
    it = ring.Items(gd)
    held = _his_tools(gd, it, mirlon)
    if gd.flag(GIVEN):
        if held is None or gd.talk_target() != NAME:  # (only while he talks: a game loading can show anything)
            return []
        cell = pickpocket.free_cell(gd, it, leader)
        if cell is None:
            return []  # (no room: kept until there is, as long as he talks)
        list_no, item, before = held
        pickpocket._take(gd, it, mirlon, list_no, item, before)
        pickpocket.give(gd, ring.Items(gd), leader, item, cell)
        gd.set_flag(MOVED)
        gd.set_flag(OFFER, False)
        return [f"Mirlon gives {gd.creature_name(leader)} his Thieves' Tools"]
    offer = held is not None and is_thief(gd, leader)
    if gd.flag(OFFER) != offer:
        gd.set_flag(OFFER, offer)
    return []
