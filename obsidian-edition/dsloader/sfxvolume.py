"""The game menu's SOUND EFFECT VOLUME where both games start it: their speech and sound effects
loud enough under the Loader's emulators.

Both games keep it in two bytes of their data segment (the menu's slider, 0-255, then the sound
driver's volume, 0-127), which start at the slider's 100 and the volume's 63, half. The driver turns
the card's mixer down by it, and the emulated Sound Blaster mixer takes far more off at half than a
card did: Wake of the Ravager's narration came out 16 dB under its recording in GOG's DOSBox and 24
dB under in DOSBox-X, while its CD music, which never passes the card's mixer there, played at full
(playtest/logs/2026-11-28-ravager-voice-volume.md). So:

- Wake of the Ravager starts it at full in both emulators (ravager's `sfx_volume_full` patch): its
  speech and effects as recorded, as loud as its music.
- Shattered Lands, whose music is MIDI, keeps GOG's DOSBox's level: in DOSBox-X it starts at 79
  (gamepatch's `sfx_volume_dosbox_x`), which plays the effects as loud as GOG's DOSBox at 63.

The patches set the start of a new game. A loaded game takes the two bytes from the roster
(CHARSAVE.GFF's PREF 100, written at every save: the slider at +2, the volume at +3, the game's load
at 7D97Eh in the sequel, 74821h in Shattered Lands), so `set_roster` writes the Loader's values there
too, but only over the ones the game or the Loader start with: a volume the player set stays.
"""
import os
from typing import Iterable, Optional, Tuple

from . import gff

ROSTER = "CHARSAVE.GFF"
PREF_ID = 100
SLIDER_AT, VOLUME_AT = 2, 3  # (in the PREF chunk)

Level = Tuple[int, int]  # (the slider, the driver's volume)
GAME = (100, 63)  # what both games start with
RAVAGER_STOCK = (255, 63)  # (the sequel's own CHARSAVE.GFF as GOG installs it)
FULL = (255, 127)  # the sequel's, both emulators
SL_DOSBOX_X = (159, 79)  # Shattered Lands' in DOSBox-X
CLOUD_SAVES = "cloud_saves"  # (GOG's DOSBox overlays this folder on C:, so the roster may be there)


def ravager_level() -> Tuple[Level, Tuple[Level, ...]]:
    """The sequel's: (the level to write, the levels it replaces)."""
    return FULL, (GAME, RAVAGER_STOCK)


def sl_level(dosbox_x: bool) -> Tuple[Level, Tuple[Level, ...]]:
    """Shattered Lands': in DOSBox-X SL_DOSBOX_X over the game's; in GOG's DOSBox the game's back
    over SL_DOSBOX_X (a roster saved under DOSBox-X)."""
    return (SL_DOSBOX_X, (GAME,)) if dosbox_x else (GAME, (SL_DOSBOX_X,))


def _find(folder: str, name: str) -> Optional[str]:
    try:
        for entry in os.listdir(folder):
            if entry.lower() == name.lower():
                return os.path.join(folder, entry)
    except OSError:
        pass
    return None


def rosters(game_dir: str) -> list:
    """GAME_DIR's roster files: its own and, when GOG's cloud_saves folder has one, that one."""
    found = [_find(game_dir, ROSTER)]
    cloud = _find(game_dir, CLOUD_SAVES)
    if cloud and os.path.isdir(cloud):
        found.append(_find(cloud, ROSTER))
    return [path for path in found if path]


def level(data: bytes) -> Optional[Level]:
    """The roster DATA's (slider, volume), None without a PREF chunk long enough."""
    places = gff.index_places(data, "PREF")
    if PREF_ID not in places:
        return None
    _, offset, length = places[PREF_ID]
    if length <= VOLUME_AT or offset + length > len(data):
        return None
    return data[offset + SLIDER_AT], data[offset + VOLUME_AT]


def with_level(data: bytes, wanted: Level, replaces: Iterable[Level]) -> Optional[bytes]:
    """DATA with its PREF's level WANTED if it is one of REPLACES, else None (nothing to change)."""
    now = level(data)
    if now is None or now == tuple(wanted) or now not in {tuple(r) for r in replaces}:
        return None
    _, offset, _ = gff.index_places(data, "PREF")[PREF_ID]
    out = bytearray(data)
    out[offset + SLIDER_AT], out[offset + VOLUME_AT] = wanted
    return bytes(out)


def set_roster(game_dir: str, wanted: Level, replaces: Iterable[Level]) -> list:
    """Each of GAME_DIR's rosters with the level WANTED where it had one of REPLACES; the paths
    changed. A roster that can't be read or written is left as it is."""
    replaces = tuple(replaces)
    changed = []
    for path in rosters(game_dir):
        try:
            with open(path, "rb") as f:
                data = f.read()
            new = with_level(data, wanted, replaces)
            if new is not None:
                gff.write_atomic(path, new)
                changed.append(path)
        except (OSError, gff.GffError):
            continue
    return changed
