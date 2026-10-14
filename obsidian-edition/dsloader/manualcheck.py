"""No manual check: the dragon's question (the game's copy protection) taken out.

Leaving the sewers, the Tari's warrens (region 28h; script 120: "Do you want to leave the
sewers?"), until it has been answered there, the game runs script 20: a dragon "creates a
mindlink" and asks for a word from the manual ("The 3rd word on page 14, line 1, begins with
the letter 'p'. What is that word?"), one of twenty at random; three wrong answers and the
party dies. Answered, script 86 (at 1087) sets what the right answer sets: 255 in a variable
of the game's (7, 4), and, in that region (28h), the bit (12 of 135, 73) that script 120
tests to ask only once.

In the Loader's copy of the scripts, script 20 does only that: no dragon, no question. It
starts at the same place (1, after its first command), the one entry point the game's table
has for it, so a save made anywhere goes on the same way.
"""

from typing import Dict, Tuple

from . import gpl

SCRIPT = 20
REGION = 0x28  # the warrens (script 86 sets the bit only there)
START, SWITCH, CASE, END_SWITCH, SET, SET_BIT, END = 0x19, 0x17, 0x27, 0x61, 0x16, 0x7A, 0x31
QUESTION = ("str", " word on page ")  # (in the game's script: how it's known)


def answered() -> bytes:
    """Script 20 as the right answer leaves things (script 86 from 1087, without its words)."""
    head = [(START, []), (SET, [("n", 255), ("var", 7, 4)]), (SWITCH, [("var", 137, 36)])]
    case_at = len(gpl.encode(head))
    bit = (SET_BIT, [("var", 135, 73), ("n", 12)])
    after = case_at + len(gpl.encode_op((CASE, [("n", REGION), ("n", 0)]))) + len(gpl.encode_op(bit))
    return gpl.encode(head + [(CASE, [("n", REGION), ("n", after)]), bit, (END_SWITCH, []), (END, [])])


def is_the_question(script: bytes, field_types: bytes) -> bool:
    try:
        return any(s == QUESTION[1] for s in gpl.strings(gpl.decode(script, field_types)))
    except gpl.ScriptError:
        return False


def script_chunks(chunks, field_types: bytes) -> Dict[Tuple[str, int], bytes]:
    """For the Loader's copy of GPLDATA: script 20 without the question (unchanged if it isn't
    the game's dragon)."""
    key = ("GPL ", SCRIPT)
    if key not in chunks or not is_the_question(chunks[key], field_types):
        return {}
    return {key: answered()}
