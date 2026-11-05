"""Sounds the mod adds: RESOURCE.GFF's BVOC chunks, in the Loader's copy of it (icons.write_resources).

The game's sounds are Creative Voice Files (BVOC 1-130): one block of 8-bit unsigned mono samples
at 8000 a second, then the terminator. The game finds a sound through its table of 181 (DSUN.EXE
3A98:08A2h, 6 bytes each: its kind, then a descriptor naming its BVOC); only 0-130 are digital ones,
131-180 another kind. So the mod's take BVOC numbers past the game's (used by none of its scripts,
GPL's 5Dh, or spell records, +0Fh, +13h, +16h), and DSCLOG plays each by lending itself the game's
entry 131 or 132 for the call, as a digital one with a descriptor of its own (PLAY_SOUND): no number
the game plays is changed. Seen played in DOSBox, 2026-11-05 (its output recorded and matched):

  * HIDE_SOUND: a breath that sinks away, as a thief or ranger hides in shadows and moves silently
    in a fight (stealth.py; DSCLOG plays it from the map's main loop: SOUND_REQ).
  * PICK_SOUND: a purse's coins, as a thief lifts something from a pocket or takes the coins
    (pickpocket.py; DSCLOG plays it with the message: PICK_SOUND). A weapon worth the quest's XP
    keeps the quest's sound.

Their samples are sound-data/hide.wav and sound-data/pick.wav (8000 Hz, 8-bit mono, the game's own form;
sound-data/make.py made them).
"""

import os
import struct
import wave
from typing import Dict, Tuple

HIDE_SOUND = 140
PICK_SOUND = 141
FILES = {HIDE_SOUND: "hide.wav", PICK_SOUND: "pick.wav"}
FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sound-data")
RATE = 8000
VOC_HEAD = b"Creative Voice File\x1a" + struct.pack("<HHH", 26, 0x010A, 0x1129)
SOUND_BLOCK, END_BLOCK = 1, 0
MOST = 24000  # the game's sound buffer is 24,001 bytes


def voc(samples: bytes, rate: int = RATE) -> bytes:
    """A Creative Voice File of 8-bit unsigned SAMPLES, as the game's BVOC chunks are made."""
    samples = samples[:MOST - len(VOC_HEAD) - 7]
    size = len(samples) + 2
    return (VOC_HEAD + bytes((SOUND_BLOCK, size & 0xFF, size >> 8 & 0xFF, size >> 16))
            + bytes((256 - 1000000 // rate, 0)) + samples + bytes((END_BLOCK,)))


def read_wav(path: str) -> bytes:
    """The samples of an 8000 Hz, 8-bit mono WAV file (ValueError for any other kind)."""
    with wave.open(path, "rb") as w:
        if (w.getnchannels(), w.getsampwidth(), w.getframerate()) != (1, 1, RATE):
            raise ValueError(f"{path}: not 8000 Hz 8-bit mono")
        return w.readframes(w.getnframes())


def chunks() -> Dict[Tuple[str, int], bytes]:
    """The mod's BVOC chunks (none whose file is missing or of another kind)."""
    out = {}
    for number, name in FILES.items():
        try:
            out[("BVOC", number)] = voc(read_wav(os.path.join(FOLDER, name)))
        except (OSError, EOFError, ValueError, wave.Error):
            pass
    return out
