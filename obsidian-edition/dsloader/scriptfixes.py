"""Bugs in the game's own scripts (GPLDATA.GFF, the GOG release's), mended in the Loader's copy:
a trigger or call re-pointed to the handler it was meant to have, or a check made to read what it
meant to. Found by the OpenDS project (its fix.ds1.deadtriggers and fix.ds1.script-repairs), by
yuan-ti (github.com/CalvinRodo/yuan-ti), which checked them against the GOG file, and by the
Loader's own sweep of the scripts for checks like those; checked here too, each repair applied only where its
script holds the expected bytes (another release, or a script the Loader changed there, is left
as it is).

- Darkhold: story beats re-register some creatures' triggers to script 200 at 909h, a lone exit,
  so the wyvern scene's creature and two in the queen's chamber lose their look text, and the
  portcullis guard no longer fights back when attacked.
- The Lava Rifts: the ranger's re-armed sight trigger points at the hermit's handler (endless
  hermit talk, and a second Iron Necklace).
- Gedron: once the extract is delivered, Linara's talk ends with no menu, so Jasmine's spellbook
  can't come up.
- Checks of the active member's race or sex, or a ranger's flag, read from its combat record,
  which holds none of them, so they always read 0: a halfling isn't greeted as one, nor a woman
  told she is one, nor a thri-kreen hears the bell the mastyrial hears near Demothi's camp.
- Tests asking the wrong question: "not a dwarf or not a halfling" (true of everyone), and a
  class tested as the whole class word, so a multi-class preserver or psionicist fails it; and
  Dagolar's slime book's "magical training", which took fighters and air clerics but not the
  other clerics or druids.
- The ranger's tracking at region 8's bodies: no one counts as a ranger, a ranger's level is
  tested as a bit of its class code, and the roll has to beat the score, not come under it. Now a
  ranger reads the tracks on a d20 under WIS + its level's bonus, for XP.
- The slave pens' sewer grate: hacking its lock off is never offered (the search for a weapon in
  hand stops at once), and a hack that works leaves it shut; one that fails says the weapon
  breaks, and keeps it (now one that can break, as in a fight, is gone; a metal or magic one
  rings off the grate unharmed); and an attack on it always broke the lock (now a Strength roll,
  as ripping it open has).
- The Rebel Mindhome's 5000 XP for killing the spiders came again at every talk to their leader;
  now once.
- Region 9's messenger (the slaves' rising from the sand) came only if the party left the region
  and came back after the elves had gone; now he comes. The Draj serf left behind on the way to
  region 10 gave a second obelisk gem; now he comes along.
- The slave pens: Pehtucl's ambush at the fountain sent every Arena Guard and Guard in the pens
  after the party, not only the five it makes; now those five (and Pehtucl). And a guard attacked
  in the passage before the fountain, where the party stands, raised the alarm the fountain's
  roar masks in its room; now there too.

(The OpenDS fix that starts the final battle's stages without their pause is left out: with the
game's clock running, the stage gate waits its window out as it should.)
"""

from typing import Dict, NamedTuple, Tuple

from . import gpl


class Repair(NamedTuple):
    script: int  # GPL chunk
    at: int  # offset in it
    was: bytes
    now: bytes  # (longer than WAS: run from after the script's end, the bytes at AT a jump there)
    what: str
    relocate: Tuple[int, ...] = ()  # offsets in NOW of addresses written from its own start


# The jump: the command that ends a WHILE's loop (its address a big-endian word below 8000h), as the
# Loader's other script changes jump (pensasks.GOTO); the game's scripts have no other plain jump
JUMP, EXIT = 0x64, 0x31

def _through_71(field: int) -> str:
    """The active member's FIELD as the scripts read a class or level: through its combat record's
    field 71, the character's own record (race 20, sex 21, the flags word 17)."""
    return "b18025" + "0247" + f"{field:02x}"

TEST, IF, ELSE, ENDIF, PRINT, TAKE = 0x18, 0x3E, 0x3F, 0x67, 0x4F, 0x5C


def _grate_hack_fails() -> Tuple[bytes, Tuple[int, ...]]:
    """A hack at the sewer grate that fails: a weapon that can break "breaks against the grate" and
    is gone (the game's said so and kept it); one that can't rings off it unharmed. What can break
    is the game's rule for a weapon breaking in a fight (Game.item_breaks): wood, bone, stone or
    obsidian (its type's +8, low 4 bits 0 to 3) with no plus, no spell and not its type's 80h. The
    weapon is the one the search found in the right hand (2Ch), its holder the one hacking (local
    big number 37). IF jumps to its ELSE, ELSE to its ENDIF, written from the detour's start."""
    weapon = ("field", 0x802C, [72])
    material = ("field", 0x802C, [4, 8])  # (field 4, the item's type, leads to the type's record)
    magic = gpl.encode_op((TEST, [("expr", [
        "(", ("field", 0x802C, [15]), "!=", ("n", 0), ")", "or",
        "(", ("field", 0x802C, [0]), ">", ("n", 0), ")", "or",
        "(", material, "<", ("n", 0), ")", "or",
        "(", "(", material, "&", ("n", 15), ")", ">", ("n", 3), ")"])]))
    rings = gpl.encode_op((PRINT, [("n", 98), ("str", " rings off the grate, unharmed. ")]))
    breaks = (gpl.encode_op((PRINT, [("n", 98), ("str", " breaks against the grate. ")]))
              + gpl.encode_op((TAKE, [("n", 1), weapon, ("var", 137, 37), ("n", 9999)])))
    if_at = len(magic)
    else_at = if_at + 3 + len(rings)
    endif_at = else_at + 3 + len(breaks)
    code = (magic + bytes((IF,)) + else_at.to_bytes(2, "big") + rings
            + bytes((ELSE,)) + endif_at.to_bytes(2, "big") + breaks + bytes((ENDIF,)))
    return code, (if_at + 1, else_at + 1)


_FAILS, _FAILS_RELOCATE = _grate_hack_fails()

# Pehtucl's ambush at the fountain (GPL 145 at E7Dh, the slave pens): his guards, made at his
# square (command 25h: kind, how many, x, y, ...; the game's makes each of a number in turn, the
# same routine for each), then hunt orders (08h), a no-orders handler (6Fh: GPL 74 at 100) and a
# sight trigger (1Bh: GPL 74 at 89, range 5), each given to a kind (-90 Arena Guard, -293 Guard,
# -37 Pehtucl): every creature of that kind in the region, so the pens' other guards came from
# across the map. Now each guard is made alone and the orders go to the one just made (local big
# number 40, as the game's other scripts give a new creature its orders: GPL 10, 52, 57); Pehtucl's
# by his kind as before (the pens hold one -37, him)
CREATE, HUNT, NO_ORDERS, SIGHT = 0x25, 0x08, 0x6F, 0x1B
MADE = ("var", 137, 40)  # (the creature command 25h made last)
AMBUSH = ((-90, 4), (-293, 1))  # (kind, how many: the game's)
AMBUSH_HANDLERS = (100, 74), (89, 74)  # (place, script) of the no-orders handler and the sight trigger


def _orders(who) -> bytes:
    (idle_at, idle), (sight_at, sight) = AMBUSH_HANDLERS
    return (gpl.encode_op((HUNT, [who])) + gpl.encode_op((NO_ORDERS, [("n", idle_at), ("n", idle), who]))
            + gpl.encode_op((SIGHT, [("n", sight_at), ("n", sight), who, ("n", 5)])))


def _ambush() -> Tuple[bytes, bytes]:
    """(the game's bytes at GPL 145's E7Dh, to EDBh; the ambush's guards hunting alone)."""
    where = (("var", 137, 33), ("var", 137, 34))  # (Pehtucl's square: command 09h on him, at E7Ah)

    def create(kind: int, count: int) -> bytes:
        return gpl.encode_op((CREATE, [("n", kind), ("n", count), *where, ("n", 6), ("n", 1)]))
    was = bytes.fromhex("259100" "5a8f04892189228f068f01" "259101258f01892189228f068f01"
                        "0891005a" "08910125" "08910025"
                        "6f0064004a91005a" "6f0064004a910125" "6f0064004a910025"
                        "1b0059004a91005a8f05" "1b0059004a9101258f05" "1b0059004a9100258f05")
    now = b"".join(create(kind, 1) + _orders(MADE) for kind, count in AMBUSH for _ in range(count))
    return was, now + _orders(("n", -37))


_AMBUSH_WAS, _AMBUSH_NOW = _ambush()

# GPL 137 at FB5h: a guard (or Pehtucl) attacked within the fountain's room (x 54-80, y over 73)
# doesn't raise the alarm, "the roar of the fountain masks his voice"; the ambush is at its south
# edge (Pehtucl stops at 60,94), and the party, following him, stands in the passage west of the
# room's wall (x 53-55, y 92-95), so a fight there raised it. Now the passage too, from the wall
# at x 40-41 (y over 90)
X, Y = ("var", 137, 33), ("var", 137, 34)
FOUNTAIN_ROOM = (53, 81, 73)  # (x over, x under, y over: the game's)
FOUNTAIN_PASSAGE = (41, 81, 90)


def _zone(x_over: int, x_under: int, y_over: int) -> list:
    return ["(", X, ">", ("n", x_over), ")", "and", "(", X, "<", ("n", x_under), ")", "and",
            "(", Y, ">", ("n", y_over), ")"]


_FOUNTAIN_WAS = bytes.fromhex("18e28921d98f35e1d5e28921da8f51e1d5e28922d98f49e1" "3e1081")
_FOUNTAIN_NOW = (gpl.encode_op((TEST, [("expr", ["(", *_zone(*FOUNTAIN_ROOM), ")", "or",
                                                  "(", *_zone(*FOUNTAIN_PASSAGE), ")"])]))
                 + _FOUNTAIN_WAS[-3:])  # (its IF, to the alarm, kept)

REPAIRS = (
    Repair(41, 0x1D, bytes.fromhex("66090900c8"), bytes.fromhex("6600010029"),
           "Darkhold: the wyvern scene's creature keeps its look text"),
    Repair(195, 0x2B, bytes.fromhex("650909"), bytes.fromhex("65033b"),
           "Darkhold: the portcullis guard fights back when attacked"),
    Repair(203, 0x3FE, bytes.fromhex("66090900c8"), bytes.fromhex("66038900cb"),
           "Darkhold: a creature in the queen's chamber keeps its look text"),
    Repair(203, 0x406, bytes.fromhex("66090900c8"), bytes.fromhex("66038900cb"),
           "Darkhold: another creature in the queen's chamber keeps its look text"),
    Repair(100, 0x684, bytes.fromhex("1b00560064"), bytes.fromhex("1b01bd0064"),
           "the Lava Rifts: the ranger keeps his own sight trigger, not the hermit's"),
    Repair(68, 0xAA, bytes.fromhex("13134e"), bytes.fromhex("1300d1"),
           "Gedron: Linara's talk goes on to her menu after the extract"),
    # Checks that read a field the record they read has none of, so always 0 (yuan-ti's, and the
    # Loader's own sweep of the scripts for more). A lengthened test takes its branch along to
    # where it runs, so the branch follows it there as in the game's.
    Repair(31, 0x3B, bytes.fromhex("18b180250114d78f063e0077"),
           bytes.fromhex(f"18{_through_71(0x14)}d78f063e0077"),
           "a halfling hears the halfling's greeting meant for one"),
    Repair(31, 0x254, bytes.fromhex("17b180250114"), bytes.fromhex(f"17{_through_71(0x14)}"),
           "the halfling's insult names the race of the one it's said to"),
    Repair(42, 0x121E, bytes.fromhex("18b180250115d78f023e1232"),
           bytes.fromhex(f"18{_through_71(0x15)}d78f023e1232"),
           "a woman hears 'no woman would think of fighting Draj!'"),
    Repair(42, 0x154C, bytes.fromhex("18b180250115d78f023e1561"),
           bytes.fromhex(f"18{_through_71(0x15)}d78f023e1561"),
           "a woman's purse is 'her purse'"),
    Repair(80, 0x8D7, bytes.fromhex("18e2b180250114d78f08e13e0942"),
           bytes.fromhex(f"18e2{_through_71(0x14)}d78f08e13e0942"),
           "a thri-kreen hears the bell from Demothi's camp that the mastyrial hears"),
    Repair(203, 0x101B, bytes.fromhex("18b180250114da8f083e1043"),
           bytes.fromhex(f"18{_through_71(0x14)}da8f083e1043"),
           "a thri-kreen asked for help is told 'your help', not 'the help of any humanoid'"),
    # Tests that ask the wrong question: "not a dwarf or not a halfling", true of everyone, where it
    # means neither ("bother someone your own size", or "someone else" to the small); a class bit
    # tested as the whole word (== 80h, == 100h), so a preserver or psionicist with another class
    # never boasts of scrying the haystack or reading the man's thoughts (now `& bit > 0`, as the
    # game's other tests of a class read)
    Repair(44, 0x2F9, bytes.fromhex("18e2b18025024714d88f02e1d6e2"),
           bytes.fromhex("18e2b18025024714d88f02e1d5e2"),
           "someone small isn't told to 'go bother someone your own size'"),
    *(Repair(142, at, bytes.fromhex(f"18b18025024711d7{bit:04x}3e{back:04x}"),
             bytes.fromhex(f"18e2b18025024711dd{bit:04x}e1d98f003e{back:04x}"),
             f"the haystack: a {who} with another class may still claim to have {how}")
      for at, bit, back, who, how in ((0x14B0, 0x80, 0x14C2, "preserver", "scried it"),
                                      (0x14C3, 0x100, 0x14D5, "psionicist", "read his thoughts"))),
    # Dagolar's slime book (region 27h, by his jars of slime and glyph circle): "magical training"
    # tested the class bits against 417 (1A1h: psionicist, preserver, fighter and the air cleric
    # alone), most likely a slip for 415 (19Fh: every cleric, druid, preserver and psionicist)
    Repair(56, 0x125, bytes.fromhex("18e2b18025024711dd01a1e1"), bytes.fromhex("18e2b18025024711dd019fe1"),
           "Dagolar's slime book: read with magical training by a cleric, druid, preserver or psionicist"),
    # The ranger's tracking (region 8's bodies): a ranger is the flags word's bit, its ranger level
    # the class whose code is 13 to 16 (the game's tests a bit of the class code), and the roll
    # comes under the score (the game's over it)
    Repair(210, 0x5FD, bytes.fromhex("18e28c20b1802601110200e13e0742"),
           bytes.fromhex("18e28c20b180260247110200e13e0742"),
           "the ranger's tracking: a ranger is found"),
    *(Repair(210, at, bytes.fromhex(f"18e28c20b180260247{f:02x}0200e13e{back:04x}"),
             bytes.fromhex(f"18e2b180260247{f:02x}d98f0ce1d5e2b180260247{f:02x}da8f11e13e{back:04x}"),
             f"the ranger's tracking: a ranger's level in its {n} class counted")
      for at, f, back, n in ((0x60C, 0x23, 0x0621, "first"), (0x622, 0x24, 0x0637, "second"),
                             (0x638, 0x25, 0x064D, "third"))),
    Repair(210, 0x6CC, bytes.fromhex("188204dae28c528f14e1"), bytes.fromhex("18e28c528f14e1da8204"),
           "the ranger's tracking: the roll succeeds under the score"),
    # The slave pens' sewer grate: hacking at its lock is offered (the game's test of a hack
    # wants 1 where it means 0), says his or her as picking it does, and opens it when it works
    # (half the time: RAND(3) is 0 to 3; always with Bloodwrath, -1576); a weapon it says breaks
    # does, if it's one that can (not metal, not magic)
    Repair(137, 0xA65, bytes.fromhex("18e28c4989258200e1d5e28e03d78f01e1"),
           bytes.fromhex("18e28c4989258200e1d5e28e03d78f00e1"),
           "the sewer grate: hacking its lock off is offered"),
    Repair(137, 0x9E0,
           bytes.fromhex("4f0062920541cfae3c7979f3cdd766cf283461c7af9a0e9a32a0d9bf1eb41bf36641df4f4d08"
                         "3469e68018"),
           bytes.fromhex("4f0062920541cfae3c7979f3cdd766cf283461c7af9a0e9a32a0d9bf1eb41bf36641df4f4d08"
                         "0180" "18b18025024715d78f013e003f4f00629205d1a79a00603f004c4f00629205d1979200"
                         "6067"),
           "the sewer grate: a hack at its lock says his or her", relocate=(51, 64)),
    Repair(137, 0xA14, bytes.fromhex("4f006292055c8018"),
           bytes.fromhex("4f006292055c80184f00628100168f01cd01f9"),
           "the sewer grate: a hack that works opens it"),
    Repair(137, 0xA31, bytes.fromhex("4f00629205418b965c3af9a0c39f0e9ddcfa20e9a32a0cfcb0f4cab90030"), _FAILS,
           "the sewer grate: a wooden, bone or stone weapon a hack breaks is gone, metal or magic unharmed",
           relocate=_FAILS_RELOCATE),
    # Attacking the grate (its attack trigger, B49h) broke the lock when the grate's field 43 was
    # below 220: a field no record the grate can be has, so 0, and always (yuan-ti's). Now the
    # Strength roll ripping it open has (AA6h: RAND(30) < STR), so "fails to damage the lock" can be
    Repair(137, 0xB5C, bytes.fromhex("18b18027012bda00dc3e0b98"),
           bytes.fromhex("18e28c528f1ee1dab1802501173e0b98"),
           "the sewer grate: an attack breaks its lock on a Strength roll"),
    # The Rebel Mindhome (script 204): with the four spiders dead, every talk to the leader
    # ran the thanks and its 5000 XP award again; the first sets flag 695, which nothing read. The
    # award now only while it is 0 (yuan-ti's)
    Repair(204, 0x5C9, bytes.fromhex("1613888710140087004a"),
           bytes.fromhex("18cd02b7d78f003e0014" "1613888710140087004a" "67"),
           "the Rebel Mindhome's 5000 XP for the spiders is given once", relocate=(8,)),
    # Region 9: the messenger's sight trigger (object -1297, GPL 133, "men burst from the ground")
    # is registered by MAS 9 at 63h only if the elves have left (flag 245) when the region loads;
    # they leave during a stay (GPL 58 sets 245 at 1Ah, 99h or CCh), so without leaving and coming
    # back he never came. Where 58 sets the flag, the trigger as MAS 9 registers it, while flag 339
    # is 0 (yuan-ti's; GPL 133 clears -1297's sight triggers first, so two can't run it twice)
    *(Repair(58, at, bytes.fromhex("168f018df5"),
             bytes.fromhex("168f018df5" "18cd0153d78f00" "3e0019" "1b000100859105118f0f" "67"),
             "region 9: the messenger comes once the elves have left", relocate=(13,))
      for at in (0x1A, 0x99, 0xCC)),
    # Region 38's way to region 10 (GPL 60 at CD8h) took the following Draj serf along only within
    # 14: one further behind stayed, without his orders, and talking to him again ran the whole
    # deal and gave a second obelisk gem (-1352). Now within 127 (yuan-ti's, off by default there)
    Repair(60, 0xCD8, bytes.fromhex("18e28c808925910103e1da8f0e"), bytes.fromhex("18e28c808925910103e1da8f7f"),
           "the Draj serf comes along to region 10 however far behind"),
    # The slave pens: Pehtucl's ambush at the fountain hunts the party with its own guards only, and
    # a fight in the passage before the fountain doesn't raise the alarm (above)
    Repair(145, 0xE7D, _AMBUSH_WAS, _AMBUSH_NOW,
           "Pehtucl's ambush: only the guards he calls hunt the party, not every guard in the pens"),
    Repair(137, 0xFB5, _FOUNTAIN_WAS, _FOUNTAIN_NOW,
           "the fountain's roar masks a guard's yell in the passage before it too"),
)


def repaired(script: int, code: bytes) -> bytes:
    """CODE (GPL SCRIPT) with the repairs that fit it: a longer one run from after the script's end
    (after an exit, so a script that ran off its end still stops there), its bytes at AT a jump
    there and exits, and it a jump back."""
    out, added = bytearray(code), bytearray()
    for r in REPAIRS:
        if r.script != script or out[r.at:r.at + len(r.was)] != r.was or len(r.now) < len(r.was):
            continue
        if len(r.now) > len(r.was) and len(r.was) < 3:  # (no room there for the jump, 3 bytes)
            continue
        if len(r.now) == len(r.was):
            out[r.at:r.at + len(r.was)] = r.now
            continue
        if not added:
            added.append(EXIT)
        start = len(code) + len(added)
        detour = bytearray(r.now) + bytes((JUMP,)) + (r.at + len(r.was)).to_bytes(2, "big")
        for i in r.relocate:
            detour[i:i + 2] = (int.from_bytes(detour[i:i + 2], "big") + start).to_bytes(2, "big")
        added += detour
        out[r.at:r.at + len(r.was)] = (bytes((JUMP,)) + start.to_bytes(2, "big")).ljust(len(r.was), bytes((EXIT,)))
    if len(out) + len(added) > _longest():
        return code
    return bytes(out + added)


def _longest() -> int:
    from .pensasks import LONGEST  # (the longest script the Loader writes)
    return LONGEST


def script_chunks(chunks, out: Dict[Tuple[str, int], bytes]) -> Dict[Tuple[str, int], bytes]:
    """The repaired scripts, each from OUT (the Loader's changes so far) or else CHUNKS (the game's)."""
    changed: Dict[Tuple[str, int], bytes] = {}
    for script in sorted({r.script for r in REPAIRS}):
        key = ("GPL ", script)
        code = out.get(key, chunks.get(key))
        if code is not None:
            fixed = repaired(script, code)
            if fixed != code:
                changed[key] = fixed
    return changed
