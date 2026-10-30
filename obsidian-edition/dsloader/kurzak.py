"""Kurzak notices Legcrusher is gone.

When the party is slow to answer his call to the arena, Kurzak sends Legcrusher, the pens'
half-giant, to fetch them (script 136: "Legcrusher! Get gladiators!"). A party at the fountain can
kill Legcrusher when he comes, with no alarm; but Kurzak goes on calling for him at every fight
after, and greets them as if he were still about ("I had to send Legcrusher after you", script
141). In the Loader's copy of the scripts each of those lines asks first whether Legcrusher is
on the map (80h: how far he is from Kurzak, 999 once he's dead or gone, as the game's own scripts
ask it of others: Dinos of Gilal): if he is, the game's words; if not, Kurzak's own about his
missing monster trainer. Only the words change: what the scripts do next is the game's.

As pensasks.py does, nothing of the game's scripts moves: the first of the lines becomes a jump
(64h) to code put after the script's end (the rest of that command filler never reached), which
says one or the other and jumps back to what follows the game's lines.
"""

from typing import Dict, Optional, Sequence, Tuple

from . import gpl
from .kalzith import SPEAKS, _Script, _lines
from .pensasks import FILLER, GOTO, LONGEST

KURZAK, LEGCRUSHER = 29, 326  # their objects (npcitems.py's)
WHERE, GONE = 0x80, 999  # (two objects: how far apart, 999 when one isn't on the map)
SAY = 0x4F
CALL_SCRIPT, TALK_SCRIPT = 136, 141  # his call to the arena; his talk as the party comes

# (script, the first of the game's lines, Kurzak's words without Legcrusher)
LINES: Tuple[Tuple[int, str, str], ...] = (
    (CALL_SCRIPT, "Legcrusher! Get gladiators!",
     "Legcrusher! ... Legcrusher? Where has that lump got to? Gladiators! Get up here yourselves!"),
    (TALK_SCRIPT, "Good thing you got here. I thought I was going to have to send out ",
     "Good thing you got here. Legcrusher's gone missing, and I'd have had to come down "
     "there myself."),
    (TALK_SCRIPT, "I had to send Legcrusher after you. It's good that you found me before ",
     "I sent Legcrusher after you, and he never came back. You wouldn't know anything about "
     "that, would you? Never mind."),
)

# (as the game asks whether someone has died or gone: 80h from one who is there, Kurzak calling)
HERE = ("expr", ["(", ("op", (WHERE, [("n", -KURZAK), ("n", -LEGCRUSHER)])), ")", "<", ("n", GONE)])


def _run(ops: Sequence[gpl.Op], first: str) -> Optional[Tuple[int, int]]:
    """(the index of the game's line FIRST, the index past the lines that follow it), or None."""
    start = next((i for i, o in enumerate(ops) if o.code == SAY and o.args == [("n", SPEAKS), ("str", first)]), None)
    if start is None:
        return None
    end = start + 1
    while end < len(ops) and ops[end].code == SAY and ops[end].args[1][0] == "str":
        end += 1
    return start, end


def with_notice(script: bytes, field_types: bytes, number: int) -> bytes:
    """SCRIPT (the game's NUMBER) with Kurzak's lines about Legcrusher asking whether he is there
    (unchanged if they aren't as the game has them, or done already)."""
    ops = gpl.decode(script, field_types)
    s, jumps = _Script(), []
    for n, (where, first, words) in enumerate(LINES):
        if where != number or gpl.encode_expr(("str", _lines(words)[0])) in script:
            continue  # (another script's, or done already)
        run = _run(ops, first)
        if run is None:
            continue
        start, end = run
        label = f"line {n}"
        jumps.append((ops[start].at, ops[start + 1].at, label))
        s.label(label)
        s.when(HERE, lambda start=start, end=end: [s.op(SAY, *o.args) for o in ops[start:end]],
               lambda words=words: s.say(words))
        s.op(GOTO, ("n", ops[end].at))
    if not jumps:
        return script
    out = bytearray(script) + s.bytes(base=len(script), end=False)
    if len(out) > LONGEST:
        return script
    for at, past, label in jumps:
        jump = gpl.encode_op((GOTO, [("n", s.at[label])]))
        out[at:past] = jump + bytes([FILLER]) * (past - at - len(jump))
    return bytes(out)


def script_chunks(chunks, field_types: bytes, out: Dict[Tuple[str, int], bytes]) -> Dict[Tuple[str, int], bytes]:
    """The changed scripts, each from OUT (the Loader's changes so far) or else CHUNKS (the game's)."""
    changed = {}
    for number in sorted({where for where, _, _ in LINES}):
        key = ("GPL ", number)
        script = out.get(key, chunks.get(key))
        if script is None:
            continue
        new = with_notice(script, field_types, number)
        if new != script:
            changed[key] = new
    return changed
