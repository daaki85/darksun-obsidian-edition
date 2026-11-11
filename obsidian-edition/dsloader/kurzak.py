"""Kurzak notices Legcrusher is gone.

When the party is slow to answer his call to the arena, Kurzak sends Legcrusher, the pens'
half-giant, to fetch them (script 136: "Legcrusher! Get gladiators!"). A party at the fountain can
kill Legcrusher when he comes, with no alarm; but Kurzak goes on calling for him at every fight
after, greets them as if he were still about ("I had to send Legcrusher after you", script
141), even "I'm glad you listened to Legcrusher" when Legcrusher found them before he died, and
asked "Who is the half-giant?" says he's the monster trainer, good with monsters. Dinos too warns
them that Kurzak will send out Legcrusher (script 139). In the Loader's copy of the scripts each of those lines asks first whether
Legcrusher is dead (DEAD, a flag the dice log sets once it sees him dead: watch): if not, the
game's words; if so, Kurzak's own about his missing monster trainer. Only the words change: what
the scripts do next is the game's. (Not whether he is on the map, as the game's scripts ask it of
others: script 136 makes him only as Kurzak calls, after the call's first line, and he is off the
map again once he has fetched the party, so that asked "gone" of a living Legcrusher.)

At the fountain (the user's design, 2026-11-11): when Legcrusher comes for a party in the
fountain's room or the passage before it (scriptfixes' zone, where the alarm script lets "the
roar of the fountain" mask a yell), he says they are out of their cells, bellows for the guards,
the fountain drowns him, and he attacks: his side made the party's foes (fields 74 and 75 = 2,
as the guards' sight trigger does) and the ambush guards' orders (hunt, a no-orders handler, a
sight trigger: scriptfixes._orders). Elsewhere his words as the game's (FOUNTAIN_LINE on).

As pensasks.py does, nothing of the game's scripts moves: the first of the lines becomes a jump
(64h) to code put after the script's end (the rest of that command filler never reached), which
says one or the other and jumps back to what follows the game's lines.
"""

from typing import Dict, Optional, Sequence, Tuple

from . import gpl
from .kalzith import SPEAKS, _Script, _lines
from .pensasks import FILLER, GOTO, LONGEST

KURZAK, LEGCRUSHER = 29, 326  # their objects (npcitems.py's)
DEAD = 797  # the Loader's flag: Legcrusher seen dead (past Alagorn's menus, 794 at most, and Pehtucl's chest's 795-796)
SAY = 0x4F
CALL_SCRIPT, TALK_SCRIPT, DINOS_SCRIPT = 136, 141, 139  # his call to the arena; his talk; Dinos's

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
    (TALK_SCRIPT, "Oh, that's the monster trainer. His name is Legcrusher. ",
     "That was Legcrusher, the monster trainer. He's gone missing. Not too bright, but good with "
     "monsters. If you see him, send him back."),
    (TALK_SCRIPT, "I'm glad you listened to Legcrusher. I hate it when we lose gladiators ",
     "So Legcrusher found you. Then where's he got to? He never came back. Never mind."),
    (DINOS_SCRIPT, "Kurzak's looking for you. You better go fight before he sends ",
     "Kurzak's looking for you. You'd better go fight before he comes down here himself."),
)

# Legcrusher at the fountain: the game's line his fetching speech opens with (script 136), and his
# words there instead
FOUNTAIN_LINE = "Kurzak told me to bring you to the arena. If ya don't go, "
# (each a window of its own: his, the narration's with the window's emblem, in the game's words for a
# guard's yell masked there, GPL 137 at FF2h; then his again)
FOUNTAIN_WORDS = ("Gladiators out of cells! Bad gladiators! Guards! GUARDS!",
                  "Legcrusher tries to yell for help but the roar of the fountain masks his voice.",
                  "Nobody come? Then Legcrusher take you back himself!")
NARRATION, LOCATE, END = 98, 0x09, 0x31
PORTRAIT, EMBLEM, HIS_FACE = 0x54, 0, 100  # (the window's portrait: 0 its emblem; his, as 136 at 2B6h sets it)
SIDE, ATTITUDE, AGAINST = 74, 75, 2  # (an object's fields, as the guards' sight trigger sets them: GPL 74 at 2Bh)
X, Y = ("var", 137, 33), ("var", 137, 34)  # (LOCATE's square)

# (Legcrusher alive: DEAD clear, read as the game's scripts read a flag)
HERE = ("expr", ["(", ("var", 0x8D, DEAD), "==", ("n", 0), ")"])


def watch(gd) -> bool:
    """DEAD set once a creature named Legcrusher is seen dead (wherever he fell). True when it
    was set now."""
    from . import kalzith
    if not gd.flags_ready() or gd.flag(DEAD) or not kalzith.dead(gd, "Legcrusher"):
        return False
    gd.set_flag(DEAD)
    return True


def _run(ops: Sequence[gpl.Op], first: str) -> Optional[Tuple[int, int]]:
    """(the index of the game's line FIRST, the index past the lines that follow it), or None."""
    start = next((i for i, o in enumerate(ops) if o.code == SAY and o.args == [("n", SPEAKS), ("str", first)]), None)
    if start is None:
        return None
    end = start + 1
    while end < len(ops) and ops[end].code == SAY and ops[end].args[1][0] == "str":
        end += 1
    return start, end


def with_notice(script: bytes, field_types: bytes, number: int, original: Optional[bytes] = None) -> bytes:
    """SCRIPT (the game's NUMBER, or the Loader's copy of it so far) with Kurzak's lines about
    Legcrusher asking whether he is there (unchanged if they aren't as the game has them, or done
    already). ORIGINAL: the game's script, whose commands the copy's are where they were (another
    part's code after its end, and its jumps, may not read on from there)."""
    try:
        ops = gpl.decode(original or script, field_types)
    except gpl.ScriptError:
        return script
    s, jumps = _Script(), []
    for n, (where, first, words) in enumerate(LINES):
        if where != number or gpl.encode_expr(("str", _lines(words)[0])) in script:
            continue  # (another script's, or done already)
        run = _run(ops, first)
        if run is None:
            continue
        start, end = run
        if script[ops[start].at:ops[end].at] != (original or script)[ops[start].at:ops[end].at]:
            continue  # (changed already by another part)
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


def at_fountain() -> tuple:
    """The test: Legcrusher (LOCATE on his kind) in the fountain's room or the passage before it."""
    from .scriptfixes import FOUNTAIN_PASSAGE, FOUNTAIN_ROOM

    def zone(x_over: int, x_under: int, y_over: int) -> list:
        return ["(", X, ">", ("n", x_over), ")", "and", "(", X, "<", ("n", x_under), ")", "and",
                "(", Y, ">", ("n", y_over), ")"]
    return ("expr", ["(", *zone(*FOUNTAIN_ROOM), ")", "or", "(", *zone(*FOUNTAIN_PASSAGE), ")"])


def with_fountain(script: bytes, field_types: bytes, original: Optional[bytes] = None) -> bytes:
    """Script 136 (CALL_SCRIPT, or the Loader's copy so far) with Legcrusher's fetching speech
    asking first whether he is at the fountain (unchanged if the line isn't as the game has it, or
    done already)."""
    from .scriptfixes import AMBUSH_HANDLERS, HUNT, NO_ORDERS, SIGHT
    if gpl.encode_expr(("str", _lines(FOUNTAIN_WORDS[0])[0])) in script:
        return script
    try:
        ops = gpl.decode(original or script, field_types)
    except gpl.ScriptError:
        return script
    run = _run(ops, FOUNTAIN_LINE)
    if run is None:
        return script
    start, end = run
    if script[ops[start].at:ops[end].at] != (original or script)[ops[start].at:ops[end].at]:
        return script

    def fountain():
        s.op(PORTRAIT, ("n", HIS_FACE))
        s.say(FOUNTAIN_WORDS[0])
        s.page()
        s.op(PORTRAIT, ("n", EMBLEM))
        s.say(FOUNTAIN_WORDS[1], NARRATION)
        s.page()
        s.op(PORTRAIT, ("n", HIS_FACE))
        s.say(FOUNTAIN_WORDS[2])
        s.page()
        s.op(0x40, ("field", LEGCRUSHER, [SIDE]), ("n", AGAINST))
        s.op(0x40, ("field", LEGCRUSHER, [ATTITUDE]), ("n", AGAINST))
        who = ("n", -LEGCRUSHER)
        (idle_at, idle), (sight_at, sight) = AMBUSH_HANDLERS  # (the ambush guards' orders)
        s.op(HUNT, who)
        s.op(NO_ORDERS, ("n", idle_at), ("n", idle), who)
        s.op(SIGHT, ("n", sight_at), ("n", sight), who, ("n", 5))
        s.op(END)

    s = _Script()
    s.label("fountain")
    s.op(LOCATE, ("n", -LEGCRUSHER))
    s.when(at_fountain(), fountain,
           lambda: [s.op(SAY, *o.args) for o in ops[start:end]])
    s.op(GOTO, ("n", ops[end].at))
    out = bytearray(script) + s.bytes(base=len(script), end=False)
    if len(out) > LONGEST:
        return script
    jump = gpl.encode_op((GOTO, [("n", s.at["fountain"])]))
    past = ops[start + 1].at
    at = ops[start].at
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
        new = with_notice(script, field_types, number, chunks.get(key))
        if number == CALL_SCRIPT:
            new = with_fountain(new, field_types, chunks.get(key))
        if new != script:
            changed[key] = new
    return changed
