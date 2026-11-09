"""Creature sizes (AD&D's: T tiny, S small, M man-sized, L large, H huge, G gargantuan), which
Shattered Lands doesn't keep: people by race, monsters by name (as the game names them), from AD&D's
and Dark Sun's monster books where they give one. CREATURES.md shows them (doccreatures.py); UNSURE
are the mod's guesses, for checking. Meant for the rules that will go by size."""

from typing import Dict

SIZE_NAMES = {"T": "tiny", "S": "small", "M": "man-sized", "L": "large", "H": "huge", "G": "gargantuan"}

# people (the sheet's race, game.RACE_NAMES): Athasian elves are 6.5 to 7.5 feet, half-giants 10 to 12
RACES: Dict[int, str] = {1: "M", 2: "M", 3: "M", 4: "M", 5: "L", 6: "S", 7: "M", 8: "M"}
UNSURE_RACES = frozenset((8,))  # (a thri-kreen stands some 7 feet: AD&D's line between M and L)

# monsters (and the rest of the game's creatures whose race isn't a people's), by name
NAMES: Dict[str, str] = {
    # elementals and the outer planes
    "Air Elemental": "L", "Earth Elemental": "L", "Water Elemental": "L", "Fire Elemental": "L",
    "Lesser Air Eleme": "M", "Lesser Water Ele": "M", "Lsr Earth Elem": "M", "Lsr Fire Elem": "M",
    "Djinn": "L", "Red Slaad": "L", "Blue Slaad": "L", "Vrock": "L", "Babau": "M", "Psurlon": "M",
    "Psurlon Adept": "M", "Slig": "M", "Dust Devil": "M", "Insect Swarm": "L", "Evard's Tentacle": "L",
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
    "Sand Howler": "M", "Xorn": "M", "Strine": "M", "Daggoran": "L", "Dagolar Slime": "M",
    "Tyrian Slime": "M", "Silt Runner": "S",
    # the peoples of the wastes and the deep (race "monster" in the game)
    "Magera": "M", "Ssurran": "M", "Ssovan": "M", "Laussa": "M", "Shaman Follower": "M", "Tribesman": "M",
    "First Folk": "S", "Undermt Folk": "S", "Outcast": "M", "Blind One": "M", "Drummer": "M",
    "Guard": "M", "Slave": "M", "Slave Leaders": "M", "Wagon Guard": "M", "Worker": "M",
}

# the guesses (no book to go by for the game's own creatures, or the books disagree)
UNSURE = frozenset((
    "Spider Mage", "Cheee-smak-tunk!", "Churr-te-tunk!", "Click-tunk!", "Alita", "Rampager",
    "Mountain Stalker", "Styr", "Fire Eel", "Screamer Beetle", "Strine", "Daggoran", "Laussa",
    "Blind One", "Drummer", "First Folk", "Undermt Folk", "Insect Swarm", "Evard's Tentacle",
    "Animated Statue", "Dust Devil", "Lesser Air Eleme", "Lesser Water Ele", "Lsr Earth Elem",
    "Lsr Fire Elem", "Sand Howler", "Wyvern",
))


def size(name: str, race: int) -> str:
    """A creature's size letter: its name's, else its race's (a people's), else "M"."""
    if not 1 <= race <= 8 and name in NAMES:
        return NAMES[name]
    return RACES.get(race, NAMES.get(name, "M"))
