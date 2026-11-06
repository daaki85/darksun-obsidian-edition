"""Pehtucl's chest (the slave pens' head templar's, object 1568 beside him: npcitems.PEHTUCL_CHEST,
the Cloak of Protection +1 in it), locked and trapped: a script of its own runs when it is used
(SCRIPT, by a USE command in the pens' master script, as the game's cell doors have theirs).

- A thief (the character using it) first looks for traps: find/remove traps (the scripts' skill
  check) finds and disarms the poison needle in its lock; failing, the thief springs it. Either
  way the needle is gone (DISARMED). Then open locks: success unlocks it for good (UNLOCKED);
  failing, it holds, and the thief may try again.
- Anyone else has no idea how to pick it, but may bash it, as the game's safe in GPL 71 is
  bashed: a d100 under 5, and 5 more for each of STR 18, 20, 22 and 24; success smashes the lock
  and springs the needle (unless a thief has disarmed it), failure only makes noise; again as
  often as wanted.
- The needle is a trap object of the Loader's own (TRAP_OBJECT, a copy of the game's trap object
  2039 casting the monsters' poison, spell 176: 10 damage, a save against poison), set off with
  the game's trap action, so the party's best at find/remove traps rolls to avoid it first, as
  for every trap in the game.

The two flags are the Loader's (DISARMED, UNLOCKED: the top of 784-796, which Alagorn's menus
keep for their overflow and don't reach: test_pehtuclchest). The chest, its cloak and its USE
command come with a new game: a save keeps the pens' objects and commands as they were made.
"""

from typing import Dict, Tuple

from . import dataitems, gpl, kalzith, npcitems

SCRIPT = 220  # the chest's (Kalzith's is 218, Semyon's 219; the game's run to 217)
USE = 0x6D  # (place in a script, script, object): what using the object runs (the cell doors': script 138)
OBJECT = npcitems.PEHTUCL_CHEST
DISARMED, UNLOCKED = 795, 796  # the Loader's flags: the needle gone; the lock open
TRAP_OBJECT, GAME_TRAP = 2667, 2039  # the poison needle (past the champions' 2660-2666), and its model
POISON_SPELL = 176  # the monsters' poison: 10 damage (game.POISON_POWERS)
ITEM_SPELL = 0x0F  # an item's spell, one past its number

NARRATION = 98  # (the dialogue window's lines as the game's safe has them)
ACTING = ("var", 137, 37)  # the character using it
NAME = ("field", 0x8025, [19])  # ... its name
STRENGTH = ("field", 0x8025, [23])  # ... its STR
NOT_THIEF = ("expr", [("var", 142, 26), "==", ("n", 0)])  # ... no thief levels (the safe's test)
WHERE = (("var", 137, 33), ("var", 137, 34))  # where the needle goes off (the safe's)
FLAG_READ = 0x8D
OPEN_LOCKS, FIND_TRAPS = 1, 2  # (gpl.SKILLS)
LOCK_BONUS = TRAP_BONUS = 0
BASH_CHANCE = (5, (17, 19, 21, 23))  # percent, and 5 more over each of these STR


def _skill(skill: int, bonus: int) -> tuple:
    return ("op", gpl.Op(0, gpl.DO_ACTION, [("n", gpl.ACTION_SKILL), ACTING, ("n", skill), ("n", bonus)]))


def _flag(flag: int) -> tuple:
    return ("var", FLAG_READ, flag)


def script() -> bytes:
    """The chest's script (SCRIPT)."""
    s = kalzith._Script()
    s.op(kalzith.BEGIN)

    def tell(*parts):
        for part in parts:
            s.op(0x4F, ("n", NARRATION), part if isinstance(part, tuple) else ("str", part))

    def needle():
        s.op(gpl.DO_ACTION, ("n", gpl.ACTION_TRAP), ("n", -TRAP_OBJECT), *WHERE)
        s.flag(DISARMED, 1)

    def opened():
        s.flag(UNLOCKED, 1)
        open_it(s)

    def thief():
        def disarm():
            tell(NAME, " checks the lock for traps, ")
            s.when(_skill(FIND_TRAPS, TRAP_BONUS),
                   lambda: (tell("and draws out a poisoned needle hidden in it. "), s.flag(DISARMED, 1)),
                   lambda: (tell("and pricks a finger on a poisoned needle! "), needle()))
        s.when(kalzith._is(_flag(DISARMED), 0), disarm)
        tell(NAME, " works at the lock ")
        s.when(_skill(OPEN_LOCKS, LOCK_BONUS),
               lambda: (tell("until it clicks open. "), opened()),
               lambda: tell("but it holds. "))

    def bash():
        chance, steps = BASH_CHANCE
        s.op(0x16, ("n", chance), ("var", 2, 5))
        for step in steps:
            s.when(("expr", [STRENGTH, ">", ("n", step)]), lambda: s.op(0x7A, ("var", 130, 5), ("n", 5)))
        tell(NAME, " smashes at the lock, ")
        s.when(("expr", ["(", "(", ("op", gpl.Op(0, 0x52, [("n", 99)])), ")", "+", ("n", 1), ")", ">", ("var", 130, 5)]),
               lambda: tell("making a lot of noise but little else. "),
               lambda: (tell("breaking it open"),
                        s.when(kalzith._is(_flag(DISARMED), 0),
                               lambda: (tell(", and a poisoned needle springs from it! "), needle()),
                               lambda: tell(". ")),
                        opened()))

    def not_thief():
        tell(NAME, " doesn't know how to pick the lock. ")
        s.op(0x51)
        tell("Bash it open? ")
        s.when(("expr", ["(", ("op", gpl.Op(0, 0x38, [])), ")"]), bash)

    def locked():
        tell("The chest is locked. ")
        s.when(NOT_THIEF, not_thief, thief)

    s.when(kalzith._is(_flag(UNLOCKED), 0), locked, lambda: open_it(s))
    return s.bytes()


def open_it(s) -> None:
    """The chest opened for the party (to be settled: whether the game opens it once the script
    has run, as it does a door)."""


def object_chunks(chunks) -> Dict[Tuple[str, int], bytes]:
    """For the Loader's copy of SEGOBJEX: the poison needle, a copy of the game's trap object
    GAME_TRAP under TRAP_OBJECT, casting POISON_SPELL."""
    if ("OJFF", GAME_TRAP) not in chunks or ("RDFF", GAME_TRAP) not in chunks:
        return {}
    record = bytearray(dataitems.renumbered(chunks[("RDFF", GAME_TRAP)], TRAP_OBJECT))
    record[dataitems.HEADER.size + ITEM_SPELL] = POISON_SPELL + 1
    return {("OJFF", TRAP_OBJECT): chunks[("OJFF", GAME_TRAP)], ("RDFF", TRAP_OBJECT): bytes(record)}


def with_use(master: bytes, field_types: bytes = b"") -> bytes:
    """The pens' master script with the chest's USE command (once), last, just before its end (as
    kalzith.with_talk: nothing of the game's may move)."""
    ops = gpl.decode(master, field_types)
    use = gpl.encode_op((USE, [("n", kalzith.START), ("n", SCRIPT), ("n", -OBJECT)]))
    if use in master:
        return master
    if ops[-1].code != kalzith.END:
        raise gpl.ScriptError("the master script doesn't end as expected")
    end = ops[-1].at
    return master[:end] + use + master[end:]


def script_chunks(chunks, field_types: bytes, out) -> Dict[Tuple[str, int], bytes]:
    """The chest's script, the master script with its USE command and the entry points' table with
    its entry (CHUNKS the game's GPLDATA, OUT what the Loader has changed so far)."""
    master = ("MAS ", kalzith.MASTER)
    if master not in chunks:
        return {}
    new = {("GPL ", SCRIPT): script(), master: with_use(out.get(master, chunks[master]), field_types)}
    if kalzith.ENTRIES in chunks:
        new[kalzith.ENTRIES] = kalzith.with_entry(out.get(kalzith.ENTRIES, chunks[kalzith.ENTRIES]), SCRIPT)
    return new
