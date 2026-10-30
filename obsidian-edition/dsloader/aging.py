"""Ages (the Options' rule, game.RULE_AGING): each party member's age, from Dark Sun's tables.

A character's age is rolled once, the first time the Loader sees it without one (a new character,
the game's own party, one from an earlier version): its race's starting age (Table 7: a base and
dice). It stays there unless magic changes it (Haste: a year; Restore Youth: back). On reaching
middle, old and venerable age (Table 8) its scores change, once and for good, the changes adding
up; on reaching its race's maximum age (a base and dice, its own roll kept secret: the same each
time for the same character) it dies of old age. Thri-kreen have only a venerable age.

Kept in the sheet's +17h (game.SHEET_AGE): the age less the race's base starting age, plus 1, so 0
is "none yet" (a thri-kreen starts at its base, 6). Shown on the inventory panel (DSCLOG, from the
Loader's STATS: dicelog.stats_entry), on the Characters tab and in the dice log.
"""

import random
import struct
from typing import Dict, List, NamedTuple, Optional, Tuple

from . import game


class RaceAges(NamedTuple):
    start: int  # the base starting age
    start_dice: Tuple[int, int]  # (count, sides) added to it
    most: int  # the base maximum age
    most_dice: Tuple[int, int]
    middle: Optional[int]  # the age categories (Table 8); None: the race hasn't that one
    old: Optional[int]
    venerable: int


# Dark Sun's Table 7 (starting and maximum age) and Table 8 (aging effects), by game.RACE_NAMES
RACES: Dict[int, RaceAges] = {
    1: RaceAges(15, (1, 8), 80, (2, 20), 40, 53, 80),  # human
    2: RaceAges(25, (4, 6), 200, (3, 20), 100, 133, 200),  # dwarf
    3: RaceAges(15, (3, 4), 100, (2, 20), 50, 67, 100),  # elf
    4: RaceAges(15, (2, 4), 90, (2, 20), 45, 60, 90),  # half-elf
    5: RaceAges(20, (5, 4), 120, (1, 100), 60, 80, 120),  # half-giant
    6: RaceAges(25, (3, 6), 90, (4, 12), 45, 60, 90),  # halfling
    7: RaceAges(15, (1, 6), 80, (1, 10), 40, 53, 80),  # mul
    8: RaceAges(6, (0, 0), 25, (1, 10), None, None, 25),  # thri-kreen
}
YOUNG, MIDDLE, OLD, VENERABLE = range(4)
CATEGORY_NAMES = ("", "middle-aged", "old", "venerable")
STR, DEX, CON, INT, WIS, CHA = range(6)  # (the sheet's abilities in order: game.SHEET_ABILITIES)
ABILITY_NAMES = ("STR", "DEX", "CON", "INT", "WIS", "CHA")
CHANGES = {MIDDLE: {STR: -1, CON: -1, INT: 1, WIS: 1},
           OLD: {STR: -2, DEX: -2, CON: -1, WIS: 1},
           VENERABLE: {STR: -1, DEX: -1, CON: -1, INT: 1, WIS: 1}}
ONLY_VENERABLE = {STR: -1, DEX: -1}  # (Table 8's ++: the races with no middle or old age)
LOWEST, HIGHEST = 3, 25  # (the scores' bounds)


def age_of(sheet: bytes) -> Optional[int]:
    """The character's age, None if it has none yet (or its race has no ages)."""
    stored = game.sheet_age(sheet)
    race = RACES.get(sheet[game.SHEET_RACE]) if len(sheet) > game.SHEET_RACE else None
    return race.start + stored - 1 if stored and race else None


def stored(race: int, age: int) -> int:
    """The +17h byte for AGE (1 to 255)."""
    return max(1, min(255, age - RACES[race].start + 1))


def category(race: int, age: int) -> int:
    ages = RACES[race]
    if age >= ages.venerable:
        return VENERABLE
    if ages.old is not None and age >= ages.old:
        return OLD
    if ages.middle is not None and age >= ages.middle:
        return MIDDLE
    return YOUNG


def next_category(race: int, age: int) -> Optional[Tuple[int, int]]:
    """(the next category, the age it comes at), None once venerable."""
    ages = RACES[race]
    for cat, at in ((MIDDLE, ages.middle), (OLD, ages.old), (VENERABLE, ages.venerable)):
        if at is not None and age < at:
            return cat, at
    return None


def changes(race: int, before: int, after: int) -> Dict[int, int]:
    """The scores' changes from age BEFORE to AFTER: each category reached (or, younger, left)."""
    out: Dict[int, int] = {}
    lo, hi = sorted((category(race, before), category(race, after)))
    sign = 1 if after >= before else -1
    for cat in range(lo + 1, hi + 1):
        if RACES[race].middle is None and cat != VENERABLE:
            continue  # (no middle or old age: venerable's alone)
        table = ONLY_VENERABLE if RACES[race].middle is None else CHANGES[cat]
        for ability, n in table.items():
            out[ability] = out.get(ability, 0) + sign * n
    return {a: n for a, n in out.items() if n}


def natural_start(name: str, race: int) -> Tuple[int, List[int]]:
    """The character's starting age, its true age: its race's base and dice, rolled from the
    character's name and race, so the same each time: Restore Youth takes back the years past it,
    never below it. 16-bit, as DSCLOG's AGE_ROLL works it out to show it on the creation screen
    (CR_AGE): the name's bytes hashed (h = h * 31 + byte, from race * 257), then each die from
    h = h * 25173 + 13849, its high byte mod the sides, plus 1."""
    ages = RACES[race]
    count, sides = ages.start_dice
    h = race * 257 & 0xFFFF
    for byte in name.encode("cp437", "replace")[:15]:
        h = (h * 31 + byte) & 0xFFFF
    faces = []
    for _ in range(count):
        h = (h * 25173 + 13849) & 0xFFFF
        faces.append((h >> 8) % sides + 1)
    return ages.start + sum(faces), faces


def roll_start(race: int, rng: random.Random) -> Tuple[int, List[int]]:
    """A starting age for RACE and the dice rolled."""
    ages = RACES[race]
    count, sides = ages.start_dice
    faces = [rng.randint(1, sides) for _ in range(count)]
    return ages.start + sum(faces), faces


def most_age(name: str, race: int) -> int:
    """The character's maximum age: its race's base and dice, rolled with the character's name and
    race for the seed, so the same each time (Table 7's secret roll)."""
    ages = RACES[race]
    rng = random.Random(f"{name}|{race}")
    count, sides = ages.most_dice
    return ages.most + sum(rng.randint(1, sides) for _ in range(count))


def dice_text(count: int, sides: int, faces: List[int]) -> str:
    return f"{count}d{sides} = [{' + '.join(map(str, faces))}]" if count else ""


def sheet_address(gd: "game.GameData", member: int) -> int:
    index = struct.unpack_from("<H", gd.creature(member), game.CREATURE_SHEET_INDEX)[0]
    return game.far_pointer(gd.guest, gd.ds, game.SHEETS_PTR) + index * game.SHEET_SIZE


def give_ages(gd: "game.GameData") -> List[str]:
    """A starting age for each party member who has none (natural_start): lines for the dice log."""
    out = []
    for member in range(game.PARTY_SIZE):
        rec, sheet = gd.creature(member), gd.sheet(member)
        if len(rec) < game.CREATURE_SIZE or len(sheet) < game.SHEET_SIZE or not rec[game.CREATURE_NAME]:
            continue
        race = sheet[game.SHEET_RACE]
        if race not in RACES or age_of(sheet) is not None:
            continue
        age, faces = natural_start(gd.creature_name(member), race)
        specs = game.packed_specs(game.spec_kinds(sheet), stored(race, age))
        gd.guest.write(sheet_address(gd, member) + game.SPEC_SLOTS, specs)
        ages = RACES[race]
        roll = f": {ages.start} + {dice_text(*ages.start_dice, faces)}" if faces else ""
        nxt = next_category(race, age)
        later = f"; {CATEGORY_NAMES[nxt[0]]} at {nxt[1]}" if nxt else ""
        race_name = game.RACE_NAMES[race]
        article = "an" if race_name[0] in "aeiou" else "a"
        out.append(f"{gd.creature_name(member)} is {age} ({article} {race_name}{roll}){later}.")
    return out


# Natural aging (flavour): a year of age for each 365 days of the game's clock (game time, in
# seconds since the game began), on top of each character's stored age; the clock is in the save,
# so a game loaded is as old as it was
YEAR = 365 * 24 * 60 * 60


def natural_years(gd: "game.GameData") -> int:
    """The years the game's clock has run (0 without one)."""
    seconds = gd.game_time()
    return max(0, seconds // YEAR) if seconds else 0


def age_now(gd: "game.GameData", member: int) -> Optional[int]:
    """A party member's age: its stored age (magic's years in it) and the years the game has run."""
    age = age_of(gd.sheet(member))
    return age + natural_years(gd) if age is not None else None


def age_by(gd: "game.GameData", member: int, years: int, why: str) -> List[str]:
    """Party member MEMBER aged YEARS (younger for fewer than 0, never below its starting age's
    base): its scores changed by the categories reached or left, its death at its maximum age.
    Lines for the dice log."""
    sheet = gd.sheet(member)
    stored_age = age_of(sheet) if len(sheet) >= game.SHEET_SIZE else None
    if stored_age is None or not years:
        return []
    race = sheet[game.SHEET_RACE]
    natural = natural_years(gd)
    before = stored_age + natural
    after = max(RACES[race].start + natural, before + years)
    gd.guest.write(sheet_address(gd, member) + game.SHEET_AGE, bytes([stored(race, after - natural)]))
    word = "ages" if after > before else "grows younger"
    years = abs(after - before)
    return _changed(gd, member, race, before, after,
                    f"{gd.creature_name(member)} {word} {years} year{'s' if years != 1 else ''} ({why}): now {after}")


def natural_tick(gd: "game.GameData", years_before: int, years_after: int) -> List[str]:
    """The game's clock past another year (YEARS_BEFORE to YEARS_AFTER): each party member with
    an age a year older (its scores at the categories reached, its death at its maximum)."""
    out = []
    for member in range(game.PARTY_SIZE):
        sheet = gd.sheet(member)
        rec = gd.creature(member)
        stored_age = age_of(sheet) if len(sheet) >= game.SHEET_SIZE else None
        if stored_age is None or len(rec) < game.CREATURE_SIZE or rec[game.CREATURE_STATUS] in _dead():
            continue
        before, after = stored_age + years_before, stored_age + years_after
        out += _changed(gd, member, sheet[game.SHEET_RACE], before, after,
                        f"A year has passed: {gd.creature_name(member)} is {after}")
    return out


def _dead() -> Tuple[int, ...]:
    from . import kalzith
    return tuple(kalzith.DEAD_STATUS)


def _changed(gd: "game.GameData", member: int, race: int, before: int, after: int, line: str) -> List[str]:
    """LINE, with the score changes of the categories reached or left from BEFORE to AFTER (made
    on the sheet and the creature) and death at the most the race lives."""
    at = sheet_address(gd, member)
    name = gd.creature_name(member)
    out = [line]
    delta = changes(race, before, after)
    if delta:
        creature = game.far_pointer(gd.guest, gd.ds, game.CREATURES_PTR) + member * game.CREATURE_SIZE
        parts = []
        for ability, n in sorted(delta.items()):
            for base, off in ((at, game.SHEET_ABILITIES), (creature, game.CREATURE_ABILITIES)):
                score = gd.guest.read(base + off + ability, 1)[0]
                new = score + n  # (within 3 to 25, but never the wrong way: a 26 from magic not cut)
                new = min(new, max(score, HIGHEST)) if n > 0 else max(new, min(score, LOWEST))
                gd.guest.write(base + off + ability, bytes([new]))
            parts.append(f"{ABILITY_NAMES[ability]} {n:+d}")
        left = CATEGORY_NAMES[category(race, before)]
        reached = CATEGORY_NAMES[category(race, after)] or f"no longer {left}"
        out[0] += f", {reached}: {', '.join(parts)}"
    if after >= most_age(name, race) and after > before:
        race_name = game.RACE_NAMES[race]
        out[0] += f"; that is the most {'an' if race_name[0] in 'aeiou' else 'a'} {race_name} lives: {name} dies of old age"
        kill(gd, member)
    return [out[0] + "."]


def kill(gd: "game.GameData", creature: int) -> None:
    """Creature record CREATURE (its number) dead (old age, a failed system shock): no hit points,
    the game's dead status."""
    from . import kalzith
    at = game.far_pointer(gd.guest, gd.ds, game.CREATURES_PTR) + creature * game.CREATURE_SIZE
    gd.guest.write(at, struct.pack("<h", 0))
    gd.guest.write(at + game.CREATURE_STATUS, bytes([kalzith.DEAD_STATUS[1]]))


# System shock (the Player's Handbook's CON table): the chance, by CON 1 to 25, to survive magic
# that ages or reshapes the body
SYSTEM_SHOCK = (0, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 88, 90, 95, 97, 99, 99, 99, 99, 99,
                99, 99, 100)


def system_shock(con: int) -> int:
    return SYSTEM_SHOCK[max(1, min(25, con))]


def hasted(gd: "game.GameData", creature: int, rng: Optional[random.Random] = None) -> List[str]:
    """Haste's magical aging on CREATURE (the AD&D spell ages its target a year): a system shock
    roll by its CON, death if it fails; a party member then a year older (age_by). Lines for the
    dice log."""
    from . import kalzith
    rng = rng or random.Random()
    rec = gd.creature(creature)
    if len(rec) < game.CREATURE_SIZE or rec[game.CREATURE_STATUS] in kalzith.DEAD_STATUS:
        return []
    con = rec[game.CREATURE_ABILITIES + 2]
    if not con:  # (no scores: nothing to roll against)
        return []
    chance, roll = system_shock(con), rng.randint(1, 100)
    name = gd.creature_name(creature)
    line = (f"{name}'s system shock (Haste's aging): d100 = {roll}, needs {chance} or less (CON {con}) -> "
            + ("survives" if roll <= chance else f"fails: {name} dies"))
    if roll > chance:
        kill(gd, creature)
        return [line]
    out = [line]
    if creature < game.PARTY_SIZE:
        out += ["  " + text for text in age_by(gd, creature, 1, "Haste")]
    return out


def describe(sheet: bytes, natural: int = 0) -> Optional[str]:
    """ "23, middle-aged; old at 53" for the Characters tab (NATURAL, the game's years, added),
    None without an age."""
    age = age_of(sheet)
    if age is None:
        return None
    age += natural
    race = sheet[game.SHEET_RACE]
    now = CATEGORY_NAMES[category(race, age)]
    nxt = next_category(race, age)
    return f"{age}" + (f", {now}" if now else "") + (f"; {CATEGORY_NAMES[nxt[0]]} at {nxt[1]}" if nxt else "")


def restore(gd: "game.GameData", creature: int, level: int, rng: Optional[random.Random] = None) -> List[str]:
    """Restore Youth on CREATURE, cast at LEVEL: a year of its magical aging (its years past its
    true age, natural_start's) taken back a level, after a system shock roll by its CON that a
    failure ends in death; nothing to take back, no roll. Lines for the dice log."""
    from . import kalzith
    rng = rng or random.Random()
    rec = gd.creature(creature)
    if creature >= game.PARTY_SIZE or len(rec) < game.CREATURE_SIZE or rec[game.CREATURE_STATUS] in kalzith.DEAD_STATUS:
        return []
    sheet = gd.sheet(creature)
    age = age_of(sheet)
    if age is None:
        return []
    natural = natural_years(gd)  # (the game's years count in both: only magic's are taken back)
    age += natural
    name = gd.creature_name(creature)
    true_age = natural_start(name, sheet[game.SHEET_RACE])[0] + natural
    if age <= true_age:
        return [f"Restore Youth: {name} has no magical years to take back ({age}, {name}'s true age)."]
    con = rec[game.CREATURE_ABILITIES + 2]
    chance, roll = system_shock(con), rng.randint(1, 100)
    line = (f"{name}'s system shock (Restore Youth): d100 = {roll}, needs {chance} or less (CON {con}) -> "
            + ("survives" if roll <= chance else f"fails: {name} dies"))
    if roll > chance:
        kill(gd, creature)
        return [line]
    years = min(max(1, level), age - true_age)
    return [line] + ["  " + text for text in age_by(gd, creature, -years, "Restore Youth")]
