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
- The ranger's tracking at region 8's bodies: no one counts as a ranger, a ranger's level is
  tested as a bit of its class code, and the roll has to beat the score, not come under it. Now a
  ranger reads the tracks on a d20 under WIS + its level's bonus, for XP.
- The slave pens' sewer grate: hacking its lock off is never offered (the search for a weapon in
  hand stops at once), and a hack that works leaves it shut.

(The OpenDS fix that starts the final battle's stages without their pause is left out: with the
game's clock running, the stage gate waits its window out as it should.)
"""

from typing import Dict, NamedTuple, Tuple


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
)


def repaired(script: int, code: bytes) -> bytes:
    """CODE (GPL SCRIPT) with the repairs that fit it: a longer one run from after the script's end
    (after an exit, so a script that ran off its end still stops there), its bytes at AT a jump
    there and exits, and it a jump back."""
    out, added = bytearray(code), bytearray()
    for r in REPAIRS:
        if r.script != script or out[r.at:r.at + len(r.was)] != r.was or len(r.now) < len(r.was):
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
