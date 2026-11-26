"""Creature sizes (AD&D's: T tiny, S small, M man-sized, L large, H huge, G gargantuan), which
Shattered Lands doesn't keep: people by race, monsters by name (as the game names them), from AD&D's
and Dark Sun's monster books where they give one. CREATURES.md shows them (doccreatures.py); UNSURE
are the mod's guesses, for checking. The creature size rule goes by them (below)."""

from typing import Dict, Optional

from . import game

SIZE_NAMES = {"T": "tiny", "S": "small", "M": "man-sized", "L": "large", "H": "huge", "G": "gargantuan"}

# people (the sheet's race, game.RACE_NAMES): Athasian elves are 6.5 to 7.5 feet, half-giants 10 to 12
RACES: Dict[int, str] = {1: "M", 2: "M", 3: "M", 4: "M", 5: "L", 6: "S", 7: "M", 8: "M"}
UNSURE_RACES = frozenset((8,))  # (a thri-kreen stands some 7 feet: AD&D's line between M and L)

# monsters (and the rest of the game's creatures whose race isn't a people's), by name
NAMES: Dict[str, str] = {
    # elementals and the outer planes
    "Air Elemental": "L", "Earth Elemental": "L", "Water Elemental": "L", "Fire Elemental": "L",
    "Lesser Air Eleme": "M", "Lesser Water Ele": "M", "Lsr Earth Elem": "M", "Lsr Fire Elem": "M",
    "Djinn": "L", "Red Slaad": "L", "Blue Slaad": "L", "Vrock": "L", "Babau": "M", "Psurlon": "L",
    "Psurlon Adept": "L", "Slig": "M", "Dust Devil": "M", "Insect Swarm": "L", "Evard's Tentacle": "L",
    "Animated Statue": "L",
    # the undead
    "Aposs": "M", "Convert": "M", "Cragg": "M", "Shadow": "M", "Shadow Guard": "M", "Shadow King": "M",
    "Shadow Prince": "M", "Shadow Worker": "M", "Skull Elder": "M", "Tanelyv": "M", "Tara's Follower": "M",
    "Tristram": "M", "Tynan": "M", "Zombie": "M",
    # spiders and scorpions
    "Dark Spider": "L", "Spider Mage": "L", "Cheee-smak-tunk!": "L", "Churr-te-tunk!": "L",
    "Click-tunk!": "L", "Mastyrial": "L", "Black Mastyrial": "L", "Alita": "L",
    # beasts
    "Bulette": "L", "Rampager": "L", "Silt Horror": "G", "Mountain Stalker": "L", "Otyugh": "L",
    "Wyvern": "L", "Dune Reaper": "H", "Styr": "L", "Fire Eel": "L", "Screamer Beetle": "L",
    "Sand Howler": "M", "Xorn": "L", "Strine": "M", "Daggoran": "L", "Dagolar Slime": "M",
    "Tyrian Slime": "M", "Silt Runner": "S",
    # the peoples of the wastes and the deep (race "monster" in the game)
    "Magera": "L", "Ssurran": "M", "Ssovan": "M", "Laussa": "M", "Shaman Follower": "M", "Tribesman": "M",
    "First Folk": "S", "Undermt Folk": "S", "Outcast": "M", "Drummer": "L", "Slave": "L",
    # (the six of one great tusked figure, the game's race 12 and kind 31: large, the user's call; the
    # game has no other non-person creature of these names, so no kind check: tests/test_sizenames.py)
    "Blind One": "L", "Guard": "L", "Slave Leaders": "L", "Wagon Guard": "L", "Worker": "L",
}

# the guesses (no book to go by for the game's own creatures, or the books disagree)
UNSURE = frozenset((
    "Spider Mage", "Cheee-smak-tunk!", "Churr-te-tunk!", "Click-tunk!", "Alita", "Rampager",
    "Mountain Stalker", "Styr", "Fire Eel", "Screamer Beetle", "Strine", "Daggoran", "Laussa",
    "First Folk", "Undermt Folk", "Insect Swarm", "Evard's Tentacle",
    "Animated Statue", "Dust Devil", "Lesser Air Eleme", "Lesser Water Ele", "Lsr Earth Elem",
    "Lsr Fire Elem", "Sand Howler", "Wyvern",
))


# Wake of the Ravager's monsters (OBJEX.GFF's creatures whose race isn't a people's), by name: its own
# table (its "Guard" and "Slave" are people, not Shattered Lands' tusked figures). The sequel's dice log
# puts it in force while attached (ravlog.apply_layout: TABLE). Its Draxans and the regions' other
# monsters aren't in OBJEX: they stay man-sized until named here.
RAV_NAMES: Dict[str, str] = {
    "Air Drake": "G", "Earth Drake": "G", "Fire Drake": "G", "Tarrasque": "G",
    "Air Elemental": "L", "Earth Elemental": "L", "Fire Elemental": "L", "Water Elemental": "L",
    "Gr. Fire Elem": "H", "Grt Air Elem": "H", "Grt Earth Elem": "H", "Grt Fire Elem": "H", "Grtr Water Elem": "H",
    "Beasthead Giant": "H", "Umber Hulk": "L", "Shambling Mound": "L", "Magma Golem": "L", "Obsidian Golem": "L",
    "Giant Skeleton": "L", "Giant Snake": "L", "Great Feyr": "L", "Greater Feyr": "L", "Psurlon": "L",
    "Female Hlfgnt": "L", "Int. Devourer": "T", "Int.Devourer": "T", "Aurumvorax": "S",
}
RAV_UNSURE = frozenset(("Air Drake", "Earth Drake", "Fire Drake", "Gr. Fire Elem", "Grt Air Elem", "Grt Earth Elem",
                        "Grt Fire Elem", "Grtr Water Elem", "Beasthead Giant", "Giant Snake", "Great Feyr",
                        "Greater Feyr"))
RAV_SPELLS = {2: "Charm Person", 30: "Hold Person", 136: "Hold Person"}  # (the sequel's numbers: no Charm Person or Mammal)
RAV_SHILLELAGH_TYPE, RAV_HAMMER_TYPE = 90, 95  # (the sequel's item types: Shillelagh, Spirit hammer)
TABLE = NAMES  # (the names' table in force: RAV_NAMES while the sequel's dice log is attached)


def size(name: str, race: int) -> str:
    """A creature's size letter: its name's, else its race's (a people's), else "M"."""
    if not 1 <= race <= 8 and name in TABLE:
        return TABLE[name]
    return RACES.get(race, TABLE.get(name, "M"))


def _race(sheet: bytes) -> int:
    """The sheet's race (game.SHEET_RACE: the sequel's +12h while its layout is in force), 0 if short."""
    return sheet[game.SHEET_RACE] if len(sheet) > game.SHEET_RACE else 0


# ---------------------------------------------------------------------------------------------
# The creature size rule (game.RULE_SIZE; DSCLOG's SIZE): a combatant large or bigger (here; or a
# half-giant, or Enlarged: DSCLOG's IS_LARGE) takes AD&D's large dice from a weapon, and isn't held
# or charmed by Hold Person, Charm Person or Charm Person or Mammal (its person half).

# by weapon kind (specialize.KINDS' order), AD&D's dice against a large target (count, sides, the
# bonus's change), None where they are the small ones: the game's dice are AD&D's small and man-sized
# (DSCLOG's LARGE_DICE, byte for byte)
LARGE_DICE = ((1, 12, 0), (1, 3, 0), (1, 3, 0), (1, 8, 0), (1, 6, -1), (1, 10, 0), (2, 8, 0), (2, 4, -1), None,
              (2, 6, 0), (1, 10, 0), None, (1, 4, 0), None, None, None,
              (3, 6, 0), (1, 12, 0), None, None, None, (1, 2, 0))
SHILLELAGH_TYPE, HAMMER_TYPE = 28, 30  # (Shillelagh's 2d4 is AD&D's large: 1d6+1 smaller; the Hammer's 1d4 large)
SPELLS = {2: "Charm Person", 30: "Hold Person", 86: "Hold Person", 82: "Charm Person or Mammal"}
PERSON_ONLY = frozenset((82,))  # (Charm Person or Mammal: a mammal is charmed whatever its size)
ENLARGED = 16  # (the game's effect)
TSR_TAIL_SEG, TSR_LARGE = 1834, 1842  # DSCLOG's header: the tail's segment, LARGE_BITS' offset in it
MAP_COUNT = 520
LARGE_BYTES = MAP_COUNT // 8 + 1


def dice_change(item_type: int, large: bool, kind: Optional[int]):
    """(count, sides, bonus change) the rule rolls for a hit with ITEM_TYPE (its weapon KIND) on a
    LARGE target or a smaller one, or None for the game's own."""
    if item_type == SHILLELAGH_TYPE:
        return None if large else (1, 6, 1)
    if not large:
        return None
    if item_type == HAMMER_TYPE:
        return (1, 4, -1)
    return LARGE_DICE[kind] if kind is not None and 0 <= kind < len(LARGE_DICE) else None


def large_by_table(name: str, race: int) -> bool:
    """Large or bigger by this table (DSCLOG adds half-giants by race, which this counts too, and the Enlarged)."""
    return size(name, race) in "LHG"


def large_table(gd) -> bytes:
    """LARGE_BITS for the combatants as they are now: bit N % 8 of byte N / 8 for combatant N large or bigger."""
    out = bytearray(LARGE_BYTES)
    for combatant, creature in gd.combatants().items():
        if not 0 <= combatant < MAP_COUNT:
            continue
        sheet = gd.sheet(creature)
        race = _race(sheet)
        if large_by_table(gd.creature_name(creature), race):
            out[combatant // 8] |= 1 << (combatant % 8)
    return bytes(out)


class Large:
    """Keeps DSCLOG's LARGE_BITS (in its tail) as large_table has it, written when it changes."""

    def __init__(self):
        self._table: Optional[bytes] = None

    def update(self, gd, tsr_hdr: int) -> None:
        import struct
        table = large_table(gd)
        if table == self._table:
            return
        seg, = struct.unpack("<H", gd.guest.read(tsr_hdr + TSR_TAIL_SEG, 2))
        off, = struct.unpack("<H", gd.guest.read(tsr_hdr + TSR_LARGE, 2))
        if not seg or not off:  # (a DSCLOG from before LARGE_BITS)
            return
        gd.guest.write(seg * 16 + off, table)
        self._table = table


def is_large(gd, combatant: int) -> bool:
    """DSCLOG's IS_LARGE: COMBATANT Enlarged, large or bigger by this table, or a half-giant."""
    if any(e.owner == combatant and e.id == ENLARGED for e in gd.effects()):
        return True
    creature = gd.combatant_creature(combatant)
    if creature is None:
        return False
    sheet = gd.sheet(creature)
    race = _race(sheet)
    return race == 5 or large_by_table(gd.creature_name(creature), race)


def spared(gd, spell: int, target: int) -> bool:
    """DSCLOG's SIZE_SPARED: SPELL (Hold or Charm Person) can't take on TARGET for its size."""
    if spell not in SPELLS:
        return False
    if spell in PERSON_ONLY:
        creature = gd.combatant_creature(target)
        sheet = gd.sheet(creature) if creature is not None else b""
        if not 1 <= _race(sheet) <= 8:
            return False
    return is_large(gd, target)
