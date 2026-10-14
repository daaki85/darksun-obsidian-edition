"""Father Garyn's gift: the Tome of Understanding (tome.py), when the party brings him the ranike
pith, given by his own script.

In his talk (script 174), "I'm here to deliver a bag of pith to you." has him thank them the
first time (while flag FLAG is 0), tell them how the extract is made and to take it to Linara,
and set FLAG. In the Loader's copy of the scripts, the command setting it becomes a jump to code
after the script's end (as elvenleader.py's): the first time, a new page, his words, the tome
given (command 39h, a new item of its object, to the one talking to him), or left on the ground
by him when it can't be carried (25h); then FLAG set, as before, and back.
"""

from typing import Dict, Tuple

from . import gpl
from .kalzith import _Script, _lines
from .pensasks import GOTO, LONGEST
from .tome import TOME_OBJECT

SCRIPT = 174
GARYN = 112  # his object
FLAG = 625  # the pith delivered
GIVE, DROP, HERE, TEST, IF_NOT, END_IF, SET = 0x39, 0x25, 0x09, 0x18, 0x3E, 0x67, 0x16
ACTOR = ("var", 137, 37)  # the one talking to him
AT_X, AT_Y = ("var", 137, 33), ("var", 137, 34)  # where 09h puts him
DELIVERED = ("var", 13, FLAG)  # (setting it)
FIRST_TIME = ("expr", [("var", 141, FLAG), "==", ("n", 0)])  # (reading it)
WORDS = ("Before you go, take this, for your kindness to a village that has little to give. It is a "
         "tome of the old understanding, older than the sorcerer-kings. Whoever reads it will see "
         "more clearly than before; then its pages will be blank.")
CANT = "You cannot carry it just now. I will leave it here, by the wall."
EXTRACT = ("str", " She is a colleague in Gedron, a village northwest of here.")


def _delivered(ops) -> int:
    """The index of the command setting FLAG after the extract's words, or -1."""
    for i in range(len(ops) - 1):
        if ops[i].code == 0x4F and ops[i].args[1:] == [EXTRACT] \
                and ops[i + 1].code == SET and ops[i + 1].args == [("n", 1), DELIVERED]:
            return i + 1
    return -1


def with_tome(script: bytes, field_types: bytes) -> bytes:
    """His script (the game's) with the tome given the first time the pith is delivered
    (unchanged if it isn't as expected)."""
    if gpl.encode_expr(("str", _lines(WORDS)[0])) in script:
        return script  # (done already)
    ops = gpl.decode(script, field_types)
    at = _delivered(ops)
    if at < 0:
        return script
    s = _Script()
    s.label("tome")
    s.op(TEST, FIRST_TIME)
    s.op(IF_NOT, ("label", "after"))
    s.page()
    s.say(WORDS)
    give = ("op", gpl.Op(0, GIVE, [("n", 1), ("n", -TOME_OBJECT), ACTOR, ("n", 9999)]))
    s.op(TEST, ("expr", ["(", give, ")", "==", ("n", 0)]))
    s.op(IF_NOT, ("label", "given"))
    s.page()
    s.say(CANT)
    s.op(HERE, ("n", -GARYN))
    s.op(DROP, ("n", -TOME_OBJECT), ("n", 1), AT_X, AT_Y, ("n", 6), ("n", 0))
    s.label("given")
    s.op(END_IF)
    s.label("after")
    s.op(END_IF)
    s.op(SET, ("n", 1), DELIVERED)
    s.op(GOTO, ("n", ops[at + 1].at))
    added = s.bytes(base=len(script), end=False)
    out = bytearray(script) + added
    if len(out) > LONGEST:
        return script
    jump = gpl.encode_op((GOTO, [("n", s.at["tome"])]))
    place = ops[at].at
    if len(jump) > ops[at + 1].at - place:
        return script
    out[place:place + len(jump)] = jump
    return bytes(out)


def script_chunks(chunks, field_types: bytes) -> Dict[Tuple[str, int], bytes]:
    key = ("GPL ", SCRIPT)
    if key not in chunks:
        return {}
    changed = with_tome(chunks[key], field_types)
    return {key: changed} if changed != chunks[key] else {}
