"""The Elven Leader's gift: the Cloak of Elvenkind with his Gythka (+2: worldgear.py), given by his own script.

After the fight with his men (script 46), he says "You are true warriors! ... I give you a gift
that I received from a thri-kreen I once knew. Here." and gives the one talking to him the
Gythka (object 2534: command 39h, a new item of that object to them), or, when they can't
carry it, says so and leaves it on the ground by him (25h). Then a click (the window's "more")
and the talk goes on.

In the Loader's copy of the scripts, that click becomes a jump to code after the script's end
(as alagorn.py's): a new page, his words for the cloak, the cloak given the same way, an object
of the Loader's own (CLOAK: its record the Cloak of Elvenkind's, worldgear.py, in the Loader's
copy of SEGOBJEX), or left on the ground by him with a word when it can't be carried; then the
click, and back.
"""

from typing import Dict, Tuple

from . import gpl
from .kalzith import MORE, _Script, _lines
from .pensasks import GOTO, LONGEST

SCRIPT = 46
LEADER = 124  # his object
CLOAK = 2546  # the cloak's object (its picture's: worldgear.ELVEN_CLOAK_OBJECT)
GIVE, DROP, HERE, TEST, IF_NOT, END_IF, SAY = 0x39, 0x25, 0x09, 0x18, 0x3E, 0x67, 0x4F
ACTOR = ("var", 137, 37)  # the one talking to him
AT_X, AT_Y = ("var", 137, 33), ("var", 137, 34)  # where 09h puts him
NARRATE = 98  # (the window the game's click after the gift is in)
WORDS = ("And take this cloak, woven by my own tribe for our best runners. Wear it with the hood "
         "up, and the desert itself will not see you.")
CANT = "You can't carry this either, so it waits here with the other."
GIFT = ("str", "received from a thri-kreen I once knew. Here. ")


def _gift_given(ops) -> int:
    """The index of the click after the gift (the window's "more", after the "can't carry it"
    part's end), or -1."""
    here = next((i for i, o in enumerate(ops) if o.code == SAY and o.args[1] == GIFT), None)
    if here is None:
        return -1
    for i in range(here + 1, min(here + 12, len(ops) - 1)):
        if ops[i].code == END_IF and ops[i + 1].code == SAY and ops[i + 1].args == [("n", NARRATE), MORE]:
            return i + 1
    return -1


def with_cloak(script: bytes, field_types: bytes) -> bytes:
    """His script (the game's) with the cloak given after the Gythka (unchanged if it isn't as
    expected)."""
    if gpl.encode_expr(("str", _lines(WORDS)[0])) in script:
        return script  # (done already)
    ops = gpl.decode(script, field_types)
    click = _gift_given(ops)
    if click < 0:
        return script
    s = _Script()
    s.label("cloak")
    s.page()
    s.say(WORDS)
    give = ("op", gpl.Op(0, GIVE, [("n", 1), ("n", -CLOAK), ACTOR, ("n", 9999)]))
    s.op(TEST, ("expr", ["(", give, ")", "==", ("n", 0)]))
    s.op(IF_NOT, ("label", "given"))
    s.page()
    s.say(CANT)
    s.op(HERE, ("n", -LEADER))
    s.op(DROP, ("n", -CLOAK), ("n", 1), AT_X, AT_Y, ("n", 6), ("n", 0))
    s.label("given")
    s.op(END_IF)
    s.op(SAY, ("n", NARRATE), MORE)
    s.op(GOTO, ("n", ops[click + 1].at))
    added = s.bytes(base=len(script), end=False)
    out = bytearray(script) + added
    if len(out) > LONGEST:
        return script
    jump = gpl.encode_op((GOTO, [("n", s.at["cloak"])]))
    at = ops[click].at
    out[at:at + len(jump)] = jump
    return bytes(out)


def script_chunks(chunks, field_types: bytes) -> Dict[Tuple[str, int], bytes]:
    key = ("GPL ", SCRIPT)
    if key not in chunks:
        return {}
    changed = with_cloak(chunks[key], field_types)
    return {key: changed} if changed != chunks[key] else {}
