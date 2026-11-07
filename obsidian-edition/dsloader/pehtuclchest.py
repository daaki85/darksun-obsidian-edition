"""Pehtucl's chest (the slave pens' head templar's, object 1568 beside him: npcitems.PEHTUCL_CHEST,
the Cloak of Protection +1 in it), locked and trapped: a script of its own runs when it is used
(SCRIPT, by a USE command in the pens' master script, as the game's cell doors have theirs).

- Only from beside it (as the game's safe: "You must be next to ..."). A thief (the character using it) first looks for traps: find/remove traps (the scripts' skill
  check) finds and disarms the poison needle in its lock; failing, the thief springs it. Either
  way the needle is gone (DISARMED). Then open locks: success unlocks it for good (UNLOCKED);
  failing, it holds, and the thief may try again.
- Anyone else has no idea how to pick it, but may bash it, as the game's safe in GPL 71 is
  bashed: a d100 under 5, and 5 more for each of STR 18, 20, 22 and 24; success smashes the lock
  and springs the needle (unless a thief has disarmed it), failure only makes noise; again as
  often as wanted.
- The needle is a trap object of the Loader's own (TRAP_OBJECT, a copy of the game's trap object
  2039), set off with the game's trap action (DSUN.EXE 80A11h): the party's best at find/remove
  traps rolls to avoid it first, as for every trap in the game, and Detect Traps avoids it; else
  NEEDLE_DICE d6 of poison to whoever stands at its square. A trap object's +0Fh (as an item, its
  spell's place) is what the routine reads: bits 0-2 the d6, bits 3-4 how far from its square it
  reaches, bits 5-6 the damage kind (DS:251Ch: poison, fire, edged, electricity), bit 7 Detect
  Traps no help (the game's 2039 is 04h: 4d6 of poison on its square, and no save: a trap's damage
  has none, the thief's roll or Detect Traps is all).

Shut: the game opens a container as its USE script ends, whatever the script said (seen in
DOSBox), so the chest is made with the game's safe's item type (SHUT_TYPE), which it doesn't open;
the script, unlocking it, ends with a click to wait for, and watch (each quarter second) makes it a
chest again (CHEST_TYPE) meanwhile, so the game opens it then and every time after. The script ends
each time with that click and the window cleared, as the safe's does (without them, shut, the
game waited on the window for good).

The two flags are the Loader's (DISARMED, UNLOCKED: past Alagorn's menus, which use 794 at most:
test_pehtuclchest; Legcrusher's 797 after them). The chest, its cloak and its USE
command come with a new game: a save keeps the pens' objects and commands as they were made.
"""

import struct
from typing import Dict, List, Optional, Tuple

from . import dataitems, game, gpl, itemgate, kalzith, npcitems

SCRIPT = 223  # the chest's (the game's run to 217; the Loader's: Kalzith's 218, Semyon's 219,
# Alagorn's copies 220-222: kalzith.LOADER_SCRIPTS, test_scriptnumbers)
USE = 0x6D  # (place in a script, script, object): what using the object runs (the cell doors': script 138)
OBJECT = npcitems.PEHTUCL_CHEST
DISARMED, UNLOCKED = 795, 796  # the Loader's flags: the needle gone; the lock open
TRAP_OBJECT, GAME_TRAP = 2667, 2039  # the poison needle (past the champions' 2660-2666), and its model
NEEDLE_DICE, NEEDLE_REACH, POISON_KIND = 2, 0, 0  # 2d6, on its square only, poison (DS:251Ch's first)
TRAP_BYTE = 0x0F  # (the trap object's descriptor, where an item has its spell)
NEEDLE = NEEDLE_DICE | NEEDLE_REACH << 3 | POISON_KIND << 5
REGION = kalzith.REGION  # the slave pens
CHEST_TYPE, SHUT_TYPE = 0x31, 0x67  # the chest's item type, and the one it has while locked: the
# game's safe's (GPL 71 hands that one's loot out itself), which the game doesn't open as a container
# once the USE script has run (with the chest's own type it opened it whatever the script said)

NEAR = 2  # (how far from it the one using it may stand: as the game's safe, op 80h, the distance)
DISTANCE = 0x80
NARRATION = 98  # (the dialogue window's lines as the game's safe has them)
ACTING = ("var", 137, 37)  # the character using it
NAME = ("field", 0x8025, [19])  # ... its name
STRENGTH = ("field", 0x8025, [23])  # ... its STR
THIEF_FLAG = 0x400  # (the sheet's class flags: a thief's, as the safe's script tests it)
NOT_THIEF = ("expr", ["(", "(", ("field", 0x8025, [71, 17]), "&", ("n", THIEF_FLAG), ")", "==", ("n", 0), ")"])
WHERE = (("var", 137, 33), ("var", 137, 34))  # where the needle goes off: the character's square,
LOCATE = 0x09  # as command 09h on it gives them (the safe's script does so before its trap)
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
        s.op(LOCATE, ACTING)
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
                   lambda: (tell("and springs a poisoned needle! "), needle()))
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

    def at_hand():
        far = ("op", gpl.Op(0, DISTANCE, [ACTING, ("n", -OBJECT)]))
        s.when(("expr", ["(", far, ")", ">", ("n", NEAR)]),
               lambda: tell("You must be next to the chest in order to work on it. "), locked)

    def shut():
        at_hand()
        s.op(0x4F, ("n", NARRATION), kalzith.MORE)  # (a click, and the window cleared: as the safe ends)
        s.op(0x4F, ("n", NARRATION), kalzith.CLEAR)

    s.when(kalzith._is(_flag(UNLOCKED), 0), shut, lambda: open_it(s))
    return s.bytes()


def open_it(s) -> None:
    """(Unlocked, the chest is opened by the game as the script ends: watch makes it a chest again
    while the script waits for its last click.)"""


def object_chunks(chunks, out=None) -> Dict[Tuple[str, int], bytes]:
    """For the Loader's copy of SEGOBJEX: the poison needle, a copy of the game's trap object
    GAME_TRAP under TRAP_OBJECT, its descriptor NEEDLE; and the chest shut (SHUT_TYPE: OUT's record
    of it if the Loader has changed it, the cloak put in it)."""
    if ("OJFF", GAME_TRAP) not in chunks or ("RDFF", GAME_TRAP) not in chunks or ("RDFF", OBJECT) not in chunks:
        return {}
    record = bytearray(dataitems.renumbered(chunks[("RDFF", GAME_TRAP)], TRAP_OBJECT))
    record[dataitems.HEADER.size + TRAP_BYTE] = NEEDLE
    chest = bytearray((out or {}).get(("RDFF", OBJECT), chunks[("RDFF", OBJECT)]))
    struct.pack_into("<H", chest, dataitems.HEADER.size + game.ITEM_TYPE, SHUT_TYPE)
    return {("OJFF", TRAP_OBJECT): chunks[("OJFF", GAME_TRAP)], ("RDFF", TRAP_OBJECT): bytes(record),
            ("RDFF", OBJECT): bytes(chest)}


def _chest(gd) -> Optional[int]:
    """The chest's item record's place in memory, if the game has made it (its picture: OBJECT)."""
    items = game.far_pointer(gd.guest, gd.ds, game.ITEMS_PTR)
    table = gd.guest.read(items, itemgate.ITEM_RECORDS * game.ITEM_SIZE)
    picture = struct.pack("<h", -OBJECT)
    for at in range(0, len(table) - game.ITEM_SIZE + 1, game.ITEM_SIZE):
        if table[at:at + 2] == picture:
            return items + at
    return None


def watch(gd) -> List[str]:
    """Each pass: once UNLOCKED is set (the script, as the lock gives), the chest a chest again
    (CHEST_TYPE), so the game opens it as the script ends and ever after. No lines."""
    if gd.region() != REGION or not gd.flags_ready() or not gd.flag(UNLOCKED):
        return []
    at = _chest(gd)
    if at is None or struct.unpack("<H", gd.guest.read(at + game.ITEM_TYPE, 2))[0] != SHUT_TYPE:
        return []
    itemgate.hold(gd)  # (an item record: as the game leaves its lists)
    gd.guest.write(at + game.ITEM_TYPE, struct.pack("<H", CHEST_TYPE))
    return []


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
