"""The cahulaks' rule (game.RULE_CAHULAKS; DSCLOG's CAHULAKS): a hit tangles a man-sized or smaller
target that fails a save against petrification (it loses its next turn). Shattered Lands keeps no
size for its creatures (their races and kinds mix the small and the huge), so the Loader keeps
DSCLOG's BIG up to date: a bit for each combatant that can't be tangled (why_not): too big (large or
bigger by sizes.py), with nothing a rope could tangle (a slime, a swarm, an elemental, a shadow), or
one the mod keeps from being tangled. DSCLOG itself leaves out half-giants (their race), whoever they are."""

import struct
from typing import Optional

TSR_FAR_SEG = 142  # DSCLOG's header: its far block's segment
TSR_BIG = 1840     # ... BIG's offset in it
MAP_COUNT = 520    # (combatants: map things, a bit each)
BIG_BYTES = MAP_COUNT // 8 + 1

# too big to tangle: large, huge or gargantuan (sizes.py: people by race, the rest by name)
# ... and those with no body a rope could tangle
SHAPELESS = frozenset((
    "Air Elemental", "Earth Elemental", "Water Elemental", "Fire Elemental", "Lesser Air Eleme",
    "Lesser Water Ele", "Lsr Earth Elem", "Lsr Fire Elem", "Dust Devil", "Insect Swarm",
    "Evard's Tentacle", "Dagolar Slime", "Tyrian Slime", "Shadow",
))
# ... and those the mod keeps from being tangled whatever their size: the spiders (the Dark Spider,
# the Spider Mage and the "-tunk!" princes of their kind) and other beasts of Athas
UNTANGLED = frozenset((
    "Sand Howler", "Screamer Beetle", "Xorn", "Strine", "Daggoran", "Magera", "Alita", "Dark Spider",
    "Spider Mage", "Cheee-smak-tunk!", "Churr-te-tunk!", "Click-tunk!",
))
BIG_NAMES = SHAPELESS | UNTANGLED  # (by name whatever the size; the large by sizes.py)


def why_not(name: str, race: int = 0) -> str:
    """Why a creature (NAME, its sheet's RACE) can't be tangled, or "" if it can."""
    from . import sizes
    if race == 5:  # (game.RACE_HALF_GIANT: DSCLOG's own test)
        return "too big (a half-giant)"
    if name in SHAPELESS:
        return "nothing to tangle"
    if sizes.size(name, race) in "LHG":
        return "too big"
    if name in UNTANGLED:
        return "can't be tangled"
    return ""


def big_table(gd) -> bytes:
    """BIG for the combatants as they are now: bit N % 8 of byte N / 8 for combatant N whose
    creature is in BIG_NAMES."""
    out = bytearray(BIG_BYTES)
    for combatant, creature in gd.combatants().items():
        if not 0 <= combatant < MAP_COUNT:
            continue
        sheet = gd.sheet(creature)
        race = sheet[0x18] if len(sheet) > 0x18 else 0  # (game.SHEET_RACE)
        if why_not(gd.creature_name(creature), race):
            out[combatant // 8] |= 1 << (combatant % 8)
    return bytes(out)


class Big:
    """Keeps DSCLOG's BIG as big_table has it, written only when it changes."""

    def __init__(self):
        self._table: Optional[bytes] = None

    def update(self, gd, tsr_hdr: int) -> None:
        guest = gd.guest
        table = big_table(gd)
        if table == self._table:
            return
        far = struct.unpack("<H", guest.read(tsr_hdr + TSR_FAR_SEG, 2))[0] * 16
        off = struct.unpack("<H", guest.read(tsr_hdr + TSR_BIG, 2))[0]
        if not off:  # (a helper from before BIG: nothing to keep)
            return
        guest.write(far + off, table)
        self._table = table
