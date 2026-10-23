"""Bugs in the game's own scripts (GPLDATA.GFF, the GOG release's), mended in the Loader's copy:
each re-points one trigger or call to the handler it was meant to have. Found by the OpenDS
project (its fix.ds1.deadtriggers and fix.ds1.script-repairs) and checked against the GOG file by
yuan-ti (github.com/CalvinRodo/yuan-ti); checked here too, each repair applied only where its
script holds the expected bytes (another release, or a script the Loader changed there, is left
as it is).

- Darkhold: story beats re-register some creatures' triggers to script 200 at 909h, a lone exit,
  so the wyvern scene's creature and two in the queen's chamber lose their look text, and the
  portcullis guard no longer fights back when attacked.
- The Lava Rifts: the ranger's re-armed sight trigger points at the hermit's handler (endless
  hermit talk, and a second Iron Necklace).
- Gedron: once the extract is delivered, Linara's talk ends with no menu, so Jasmine's spellbook
  can't come up.

(The OpenDS fix that starts the final battle's stages without their pause is left out: with the
game's clock running, the stage gate waits its window out as it should.)
"""

from typing import Dict, NamedTuple, Tuple


class Repair(NamedTuple):
    script: int  # GPL chunk
    at: int  # offset in it
    was: bytes
    now: bytes
    what: str


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
)


def repaired(script: int, code: bytes) -> bytes:
    """CODE (GPL SCRIPT) with the repairs that fit it."""
    out = bytearray(code)
    for r in REPAIRS:
        if r.script == script and out[r.at:r.at + len(r.was)] == r.was:
            out[r.at:r.at + len(r.was)] = r.now
    return bytes(out)


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
