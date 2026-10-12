"""Dinos and the Trustee asked about Kalzith and Semyon.

Both of the game's people answer questions about the others in the pens from a menu ("What do you
know about Gilal?", "What can you tell me about Dinos?"); with the Ledger, the same menus also ask
about Kalzith once the Ledger has found him in the pens (kalzith.py), and about Semyon while he
is in his pen (semyon.py). As the game's own, a question isn't shown again once answered in that
talk.

Nothing of the game's scripts moves (their jumps go to fixed offsets): two of their commands
become jumps (64h) to code put after the script's end. The one starting the menu's part, which
clears the menu's local, goes to a piece doing that, then setting the questions' flags, and
jumping back; the menu itself goes to a copy of it (the game's own bytes) with the new questions
after its last about someone, followed by a jump on to what comes after the game's menu. The
answers are subroutines, as the game's are.

The Trustee's script is then longer than the game's buffer for scripts allows (10000 bytes,
less some): the Ledger's copy of the game has a bigger one (gamepatch.SCRIPT_BUFFER).
"""

from typing import Callable, NamedTuple, Optional, Sequence

from . import gamepatch, gpl, kalzith, semyon, vulture
from .kalzith import _Script

GOTO, MENU, SET, TEST, SKIP_UNLESS = 0x64, 0x48, 0x16, 0x18, 0x63
WHERE = 0x80  # (the person talking, an object): 999 when the object isn't on the map (only for
# the game's objects, below 520: Kalzith's, 1000, is never found, so his question waits on the
# flag the Ledger sets once it has found him in the pens and given him his scrolls)
GONE = 999
LOCAL, SET_LOCAL, FLAG = 0x8E, 14, 0x8D
# The longest script the buffer runs: in the game's, of 10000 bytes, one of 9800 ran and one of
# 10000 didn't; so as much less again, to be safe
LONGEST = gamepatch.SCRIPT_BUFFER - 400


def _is(flag: int, value: int = 1) -> list:
    return ["(", ("var", FLAG, flag), "==", ("n", value), ")"]


def _here(obj: int) -> list:
    return ["(", "(", ("op", (WHERE, [kalzith.ACTOR, ("n", -obj)])), ")", "<", ("n", GONE), ")"]


def _all(*parts: list) -> tuple:
    out = list(parts[0])
    for part in parts[1:]:
        out += ["and"] + part
    return ("expr", out)


# Who is known, alive or dead. Kalzith: once the Ledger has found him in the pens (STOCKED),
# dead by its flag (kalzith.DIED: the game's 80h can't see him). Semyon: once he has been in his
# pen (PLACED), alive while there and not marked dead, dead by the Ledger's flag (semyon.DIED).
KALZITH_ALIVE = _all(_is(kalzith.STOCKED), _is(kalzith.DIED, 0))
KALZITH_DEAD = _all(_is(kalzith.STOCKED), _is(kalzith.DIED))
SEMYON_ALIVE = _all(_is(semyon.PLACED), _is(semyon.DIED, 0), _here(semyon.SEMYON))
SEMYON_DEAD = _all(_is(semyon.PLACED), _is(semyon.DIED))


class Ask(NamedTuple):
    text: str  # the question (as the game's: two spaces first)
    flag: Optional[int]  # the companion's flag showing it (set as the menu's part starts); None:
    shown: tuple  # (values) shown when any of them is true (with no flag: the one, tested as
    # the menu is shown)
    answer: str
    dead: Optional[tuple] = None  # (a value) when true, DEAD_ANSWER instead (as Dinos does)
    dead_answer: str = ""
    then: Optional[Callable[[_Script], None]] = None  # what comes of it, after the answer


# The cooked vulture (vulture.py): the party asks Dinos about it while one of them carries it (the
# game's 33h test, as the campfire's script asks about the plucked one). He takes it (5Ch, as the
# campfire takes the plucked one), and they eat together: the Ledger's flag MEAL, on which it
# gives each a full rest, and the XP as the game's quests give theirs (its routine: the window,
# the words and the quest's sound).
PARTY, TAKE = 32766, 0x5C
PARTY_XP = ("var", 7, 16)  # the experience points the game's routine gives each party member
CALL, XP_ROUTINE = 0x14, (("n", 135), ("n", 74))  # (offset, script): its routine for them
CARRIED = ("op", (0x33, [("n", PARTY), 77, 80, [(72, 4, ("n", -vulture.COOKED))]]))


def _meal(s: _Script) -> None:
    s.op(TAKE, ("n", 1), ("n", -vulture.COOKED), ("n", PARTY), ("n", 9999))
    s.flag(vulture.MEAL, 1)
    s.page()
    # the XP as the game's quests give it: the amount, then the game's routine for it (script 74
    # at 135: its own window, "Each party member receives 100 experience points!", and the
    # quest's sound), as Dinos's own script does for Gilal (350)
    s.op(0x16, ("n", vulture.XP_REWARD), PARTY_XP)
    s.op(CALL, *XP_ROUTINE)
    from . import banter  # (Semyon and Torvak on the meal, if both are along: banter.py)
    banter.play(s, banter.VULTURE, DINOS_PORTRAIT)


# As the game's people do for the dead: the Trustee asks "What was X like?" instead, Dinos keeps
# the question and answers otherwise.
DINOS_SCRIPT, TRUSTEE_SCRIPT = 139, 146
DINOS_PORTRAIT = 117  # (his script's)
DINOS_ASKS = (
    Ask("  What do you know about Kalzith?", 766, (KALZITH_ALIVE, KALZITH_DEAD),
        "The defiler in the middle pens. The templars bring him out when the crowd wants to watch "
        "magic burn. He's polite enough to me, and grateful for the scraps I save him. Don't let "
        "the guards hear you asking about him.",
        KALZITH_DEAD,
        "You know what happened to him better than I do. He was polite enough to me, defiler or "
        "not."),
    Ask("  What do you know about Semyon?", 767, (SEMYON_ALIVE, SEMYON_DEAD),
        "Semyon? The templars had him tied out in the arena for a while. Word is he was asking too "
        "many questions about the Veiled Alliance. He's back in his pen now and keeps his head "
        "down. Smart man.",
        SEMYON_DEAD,
        "Semyon? Dead, from what I hear. Asking too many questions about the Veiled Alliance will "
        "do that."),
)
VULTURE = Ask("  We cooked the vulture from the arena.", None, (CARRIED,), vulture.MEAL_TEXT, then=_meal)
TRUSTEE_ASKS = (
    Ask("  What can you tell me about Kalzith?", 768, (KALZITH_ALIVE,),
        "Keep clear of that one. A defiler. The templars put him in here until the arena wants "
        "him. Mind you, he never gave me any trouble."),
    Ask("  What was Kalzith like?", 773, (KALZITH_DEAD,),
        "Quiet, for a defiler. Never gave me any trouble. The templars won't miss him; the crowd "
        "might."),
    Ask("  What can you tell me about Semyon?", 769, (SEMYON_ALIVE,),
        "Semyon? The templars tied him out in the arena for asking after the Veiled Alliance. "
        "He's back in his pen now. Mouthy. If he talks to you about rebels, you didn't hear it "
        "from me."),
    Ask("  What was Semyon like?", 774, (SEMYON_DEAD,),
        "Mouthy. Always asking after the Veiled Alliance. That kind of talk gets a man killed in "
        "here."),
)
QUESTION = "  What"  # (the new questions go after the menu's last asking about someone: before
# Dinos's "Let's change the subject.", the Trustee's "How can I get to Dinos?", and "Goodbye.")
# (the script, its menu's first question, the questions added)
MENUS = ((DINOS_SCRIPT, "  What do you know about Gilal?", DINOS_ASKS, None),
         (TRUSTEE_SCRIPT, "  What can you tell me about Dinos?", TRUSTEE_ASKS, None),
         # Dinos's first menu ("I'm <name>", "Why are you in here?", ... "Goodbye."): the vulture,
         # just before "Goodbye."
         (DINOS_SCRIPT, "<name>", (VULTURE,), "Goodbye."))


def _answer(s: _Script, ask: Ask) -> None:
    if ask.dead is None:
        s.say(ask.answer)
    else:
        s.when(ask.dead, lambda: s.say(ask.dead_answer), lambda: s.say(ask.answer))
    if ask.then:
        ask.then(s)


def with_asks(script: bytes, field_types: bytes, first: str, asks: Sequence[Ask],
              before: Optional[str] = None, original: Optional[bytes] = None) -> bytes:
    """SCRIPT with ASKS in its menu whose first question is FIRST (once; unchanged without it):
    after its last question about someone, or just before the reply BEFORE. ORIGINAL: the game's
    script SCRIPT was made from by an earlier call (its commands are where they were, but the
    jumps put over two of them don't decode as a whole), to find the menu in."""
    if gpl.encode_expr(("str", asks[0].text)) in script:
        return script
    original = original or script
    ops = gpl.decode(original, field_types)
    m = next((i for i, o in enumerate(ops) if o.code == MENU and o.args[0]["replies"]
              and o.args[0]["replies"][0]["text"] == ("str", first)), None)
    if m is None or m < 2 or ops[m - 1].code != SKIP_UNLESS or ops[m - 2].code != TEST:
        return script
    test = ops[m - 2].args[0]  # (the menu's loop: while its local is 0)
    if not (test[0] == "expr" and len(test[1]) == 3 and test[1][0][:2] == ("var", LOCAL)):
        return script
    loop = test[1][0][2]
    flagged = [ask for ask in asks if ask.flag is not None]
    start = next((i for i in range(m - 1, -1, -1) if ops[i].code == SET
                  and ops[i].args == [("n", 0), ("var", SET_LOCAL, loop)]), None)
    if (flagged and start is None) or m + 1 >= len(ops):
        return script  # (the questions' flags need the menu's part's start to be set at)
    menu_op = ops[m]
    menu = menu_op.args[0]
    if script[menu_op.at:ops[m + 1].at] != gpl.encode_op(menu_op):
        return script  # (the copy must be the game's bytes, not an earlier call's jump)
    s = _Script()
    jumps = []
    if flagged:
        start_op = ops[start]
        if script[start_op.at:ops[start + 1].at] != original[start_op.at:ops[start + 1].at]:
            return script
        s.label("start")
        s.op(SET, *start_op.args)
        for ask in flagged:
            s.flag(ask.flag, 0)
            for shown in ask.shown:
                s.when(shown, lambda ask=ask: s.flag(ask.flag, 1))
        s.op(GOTO, ("n", ops[start + 1].at))
        jumps.append((start_op.at, "start"))
    replies = list(menu["replies"])
    if before is None:
        at = 1 + max(i for i, r in enumerate(replies)
                     if r["text"][0] == "str" and str(r["text"][1]).startswith(QUESTION))
    else:
        at = next((i for i, r in enumerate(replies) if r["text"] == ("str", before)), None)
        if at is None:
            return script
    for ask in asks:
        name = s._new("reply")
        s.sub(name, lambda ask=ask: (_answer(s, ask), ask.flag is not None and s.flag(ask.flag, 0)))
        shown = ("var", FLAG, ask.flag) if ask.flag is not None else ask.shown[0]
        replies.insert(at, {"text": ("str", ask.text), "goto": ("label", name),
                            "if": shown, "before": [], "after": []})
        at += 1
    s.label("menu")
    s.op(MENU, dict(menu, replies=replies))
    s.op(GOTO, ("n", ops[m + 1].at))
    added = s.bytes(base=len(script), end=False)

    out = bytearray(script) + added
    if len(out) > LONGEST:
        return script
    for at, to in [(where, s.at[label]) for where, label in jumps] + [(menu_op.at, s.at["menu"])]:
        jump = gpl.encode_op((GOTO, [("n", to)]))
        out[at:at + len(jump)] = jump
    return bytes(out)


def script_chunks(chunks, field_types: bytes, vulture: bool = True) -> dict:
    """For the Ledger's copy of GPLDATA: Dinos's and the Trustee's talks with the questions (the
    vulture's only with the vulture quest on)."""
    out = {}
    for number, first, asks, before in MENUS:
        if VULTURE in asks and not vulture:
            continue
        key = ("GPL ", number)
        if key in chunks:
            script = out.get(key, chunks[key])
            changed = with_asks(script, field_types, first, asks, before, chunks[key])
            if changed != script:
                out[key] = changed
    return out
