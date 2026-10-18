"""Merzol's hay stash: Hayneedle (a bone dagger +1, worldgear.py) hidden with his ceramic pieces.

Searching the slave pens' hay (script 137) the first time, while flag FLAG is 0, says "You find a
large sack of ceramic pieces.", leaves the sack (object SACK) where the searcher stands (25h, at
where 09h put them) and sets FLAG. In the Loader's copy of the scripts, the command setting it
becomes a jump to code after the script's end (as garyn.py's): a line saying so, the dagger left
beside the sack (a new item of its own object, HAYNEEDLE_OBJECT), then FLAG set, as before, and
back.
"""

from typing import Dict, Tuple

from . import gpl
from .kalzith import _Script, _lines
from .pensasks import GOTO, LONGEST
from .worldgear import HAYNEEDLE_OBJECT

SCRIPT = 137
FLAG = 502  # the stash found
SACK = 1387  # the sack of ceramic pieces' object
DROP, SET = 0x25, 0x16
FOUND = ("var", 13, FLAG)  # (setting it)
WHO = 98  # (the hay's line's speaker: the game's)
AT_X, AT_Y = ("var", 137, 33), ("var", 137, 34)  # where 09h puts the searcher
WORDS = "Beneath it, wrapped in a strip of old hide, is a slender bone dagger."


def _found(ops) -> int:
    """The index of the command setting FLAG after the sack is left, or -1."""
    for i in range(len(ops) - 1):
        if ops[i].code == DROP and ops[i].args[:1] == [("n", -SACK)] \
                and ops[i + 1].code == SET and ops[i + 1].args == [("n", 1), FOUND]:
            return i + 1
    return -1


def with_dagger(script: bytes, field_types: bytes) -> bytes:
    """The hay's script (the game's) with Hayneedle left beside the sack (unchanged if it isn't
    as expected)."""
    if gpl.encode_expr(("str", _lines(WORDS)[0])) in script:
        return script  # (done already)
    ops = gpl.decode(script, field_types)
    at = _found(ops)
    if at < 0:
        return script
    s = _Script()
    s.label("dagger")
    s.say(WORDS, who=WHO)
    s.op(DROP, ("n", -HAYNEEDLE_OBJECT), ("n", 1), AT_X, AT_Y, ("n", 6), ("n", 0))
    s.op(SET, ("n", 1), FOUND)
    s.op(GOTO, ("n", ops[at + 1].at))
    added = s.bytes(base=len(script), end=False)
    out = bytearray(script) + added
    if len(out) > LONGEST:
        return script
    jump = gpl.encode_op((GOTO, [("n", s.at["dagger"])]))
    place = ops[at].at
    if len(jump) > ops[at + 1].at - place:
        return script
    out[place:place + len(jump)] = jump
    return bytes(out)


def script_chunks(chunks, field_types: bytes) -> Dict[Tuple[str, int], bytes]:
    key = ("GPL ", SCRIPT)
    if key not in chunks:
        return {}
    changed = with_dagger(chunks[key], field_types)
    return {key: changed} if changed != chunks[key] else {}
