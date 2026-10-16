"""The kits' effects, as DSCLOG makes them (its KIT_* routines): for the Loader and the dice log.

A kit is a sheet's KIT_BYTE (kitpages.py, which also numbers them: kitpages.kit_at); these take
that number, 0 for none (the rule off, more than one class, none chosen).
"""

from typing import Optional, Tuple

from .game import FOG_SPELL, FRIENDS_SPELL, NEW_SPELLS, REFLECT_SPELL, SPOOK_SPELL
from .kitpages import KIT_IDS, KITS

RAVAGER, SENTINEL, STALKER = KIT_IDS["Ravager"], KIT_IDS["Sentinel"], KIT_IDS["Stalker"]
MYRMIDON, CHAMPION = KIT_IDS["Myrmidon"], KIT_IDS["Arena Champion"]
ASSASSIN, SWASHBUCKLER = KIT_IDS["Assassin"], KIT_IDS["Swashbuckler"]
CRUSADER, SCHOLAR, BATTLE_MAGE, MIND_WARRIOR = (KIT_IDS["Crusader"], KIT_IDS["Scholar"], KIT_IDS["Battle Mage"],
                                                KIT_IDS["Mind Warrior"])
ELEMENTALIST, SEEKER, JUSTIFIER = KIT_IDS["Elementalist"], KIT_IDS["Seeker"], KIT_IDS["Justifier"]
WIZARD, PRIEST = 1, 2  # (the kinds of magic, as game.MAGIC_KINDS has their bits)
# a Seeker's priest slots at spell levels 1, 2 and 3, by ranger level from 6 (the 10th's on: DSCLOG's
# SEEKER_SLOTS); a Justifier's one 1st-level slot from 10th level
SEEKER_SLOTS = ((1, 0, 0), (2, 0, 0), (2, 1, 0), (2, 2, 0), (2, 2, 1))
SEEKER_FIRST, JUSTIFIER_FIRST = 6, 10
MIND_BENDER, KINETICIST = KIT_IDS["Mind Bender"], KIT_IDS["Kineticist"]
# the psionic powers' disciplines, by power (0-33: spells 138-171): psychokinesis to PK_LAST,
# psychometabolism, telepathy from TP_FIRST (the defences among them)
PK_LAST, TP_FIRST = 5, 20
HEALER = KIT_IDS["Healer"]
# the healing spells' dice (DSCLOG's CURE_SPELLS): Cure Light, Serious and Critical Wounds, Blood Flow
CURE_LIGHT, CURE_SERIOUS, CURE_CRITICAL, BLOOD_FLOW = 71, 112, 127, 108
CURE_DICE = {CURE_LIGHT: (1, 8), CURE_SERIOUS: (2, 8), CURE_CRITICAL: (3, 8), BLOOD_FLOW: (2, 6)}
# the kits with a warrior's THAC0 (PROBE_THAC0)
WARRIOR_THAC0 = frozenset((SWASHBUCKLER, CRUSADER, BATTLE_MAGE, MIND_WARRIOR))
TWIN_BLADE, BRUTE = KIT_IDS["Twin-blade"], KIT_IDS["Brute"]
GROVE_WARDEN, LIFEBINDER = KIT_IDS["Grove Warden"], KIT_IDS["Lifebinder"]
WANDERER, ARCANIST = KIT_IDS["Wanderer"], KIT_IDS["Arcanist"]
# the item type's +00h flags and +0Fh kind flags, +08h material (restrict.py's)
MELEE, MISSILE, SHIELD, THROWN, TWO_HANDED, ARMOUR = 0x01, 0x02, 0x04, 0x10, 0x40, 0x80
METAL, LEATHER, NO_MATERIAL = 4, 5, 0x40
# a Lifebinder's weapon kinds (specialize.KINDS' numbers): club, mace, quarterstaff, sling, staff sling
BLUNT = frozenset((1, 4, 8, 14, 15))
# a Shinobi's: dagger, short sword, quarterstaff, chatkcha, bow, sling, staff sling
SHINOBI_KINDS = frozenset((2, 3, 8, 12, 13, 14, 15))
SHINOBI = KIT_IDS["Shinobi"]
BOW = 13  # (the bow's weapon kind: a Seeker keeps it whatever its sphere)
# an Elementalist's second sphere: the low three bits of the sheet's byte SPHERE2, 0 none, else the
# sphere (0 air, 1 earth, 2 fire, 3 water) + 1 (DSCLOG's SPHERE2; the bits above it are the new spells
# known, game.NEW_KNOWN)
SPHERE2, SPHERE2_MASK = 0x45, 0x07
# a Battle Mage's weapon specs to choose from (DSCLOG's KIT_BM_KINDS): the one-handed melee ones, not
# thrown: long sword, club, dagger, short sword, mace, axe, pick
BATTLE_MAGE_KINDS = frozenset((0, 1, 2, 3, 4, 5, 7))
# the Shinobi's wizard spells (DSCLOG's SHINOBI_SPELLS): (spell, spell level). It learns one at each
# level up from thief level SHINOBI_FIRST, none from scrolls; it casts at its thief level less 5.
# Fogbolt, Reflected Image, Spook and Friends, new spells, only with the new spells on (their known bits: NS_KNOWS)
SHINOBI_SPELLS = ((6, 1), (2, 1), (9, 1), (4, 1), (11, 1), (FOG_SPELL, 1),  # Gaze Reflection, Charm Person, Shield, Color Spray, Wall of Fog, Fogbolt
                  (REFLECT_SPELL, 1), (SPOOK_SPELL, 1), (FRIENDS_SPELL, 1),  # Reflected Image, Spook, Friends
                  (17, 2), (19, 2), (12, 2), (13, 2), (15, 2),  # Invisibility, Mirror Image, Blur, Detect Invisibility, Fog Cloud
                  (25, 3), (29, 3), (36, 3), (30, 3))  # Blink, Haste, Protection from Normal Missiles, Hold Person
SHINOBI_FIRST, WIZARD_LAST = 6, 68  # (wizard spells are 0 to WIZARD_LAST)
RANGER_CLASSES = range(13, 17)
# the charms (DSCLOG's KIT_CHARMS): Charm Person, Charm Monster, Domination, Charm Person or
# Mammal, and the psionic Domination and Mass Domination
CHARMS = (2, 40, 61, 82, 158, 159)
SPELL_LAST = 137  # (the wizards' and priests' spells: 0 to this; psionic powers and monsters' after)
FIRE, COLD = 0x02, 0x04  # (a spell record's +1Ah: what it is, as the game's Resist Fire and Resist Cold read it)
# a Ravager's base AC by level, 1-10, the highest the game goes (DSCLOG's RAVAGER_AC)
RAVAGER_AC = (7, 7, 6, 6, 5, 5, 4, 4, 3, 3)
# the multiclass kits (kitpages.MULTI)
BATTLE_DANCER, SHADOWBLADE, SCOUT = KIT_IDS["Battle Dancer"], KIT_IDS["Shadowblade"], KIT_IDS["Military Scout"]
AVENGER, RESCUER = KIT_IDS["Wilderness Avenger"], KIT_IDS["Rescuer"]
GHETTO, WAYFINDER = KIT_IDS["Ghetto Fighter"], KIT_IDS["Wayfinder"]
SPELLARCHER, TITAN_MIND, POISONER = KIT_IDS["Spellarcher"], KIT_IDS["Titan Mind"], KIT_IDS["Poisoner"]
SPIRIT_CALLER, WASTE_SEER = KIT_IDS["Spirit Caller"], KIT_IDS["Wasteland Seer"]
WILD_FURY = KIT_IDS["Wild Fury"]
# a Battle Dancer's weapon kinds: the long sword and the bow (DSCLOG's kit_dancer)
DANCER_KINDS = frozenset((0, BOW))
DAGGER = 2  # (the dagger's weapon kind: a Ghetto Fighter's +1)
# by kit, what it adds to each thief skill (pick pockets, open locks, find/remove traps, move
# silently, hide in shadows, hear noise, climb walls, read languages: DSCLOG's KIT_SKILLS)
SKILLS = {SWASHBUCKLER: (-10,) * 8, ASSASSIN: (-15, -15, 0, 0, 0, 0, 0, 0),
          SHADOWBLADE: (-10, 0, 0, 5, 10, 0, 0, 0), GHETTO: (5, 0, -5, 0, 5, 0, 0, 0),
          WAYFINDER: (-10, 0, 0, 10, 10, 0, 0, 0)}
# a Military Scout's skills that change with the sky: +10 under the open sky, -5 under a roof
SCOUT_SKILLS, SCOUT_OUT, SCOUT_IN = frozenset((2, 3, 4, 6)), 10, -5
# a Battle Dancer's dance (rolled by the Loader as a fight starts: dance.py): d20 against DEX, +1
# to hit, to damage and on AC for DEX less the roll in rounds (at least 1); failed, -1 for 1d8 rounds
DANCE_FAIL_DIE = 8
UNDEAD_RACE = 9  # (a Wilderness Avenger's +1 to hit and damage against them)
AVENGER_STEALTH = 5  # (its hiding and moving silently: 5 a level of its best class, as a ranger's)


def name(kid: int) -> str:
    return KITS[kid // 4][kid % 4 - 1] if kid else ""


WARRIOR_ATTACKS = frozenset((CRUSADER, MIND_WARRIOR))


def warrior_attacks(halves: int, sheet: bytes) -> int:
    """The melee attacks a round (in halves) of a character who isn't a warrior (HALVES the game's,
    2 or fewer), as DSCLOG's WAR_KIT_HALVES: a Crusader's or Mind Warrior's (kit awake) a warrior's
    extra attacks, 3/2 a round from 7th level of the kit's class, 2 from 13th; else HALVES."""
    from . import kitpages
    if halves > 2:
        return halves
    for kid in WARRIOR_ATTACKS & set(kitpages.kit_ids(sheet)):
        level = kitpages.kit_level(sheet, kid)
        halves = max(halves, 4 if level >= 13 else 3 if level >= 7 else halves)
    return halves


def melee(kid: int, two_handed: bool, kind: Optional[int] = None) -> int:
    """Added to hit and to damage with a melee weapon (KIT_MELEE; TWO_HANDED: one that takes both
    hands, its type's +0Fh 40h; KIND its weapon kind): a Ravager's 1, a Brute's 2 with a
    two-handed one, a Ghetto Fighter's 1 with a dagger."""
    if kid == RAVAGER:
        return 1
    if kid == GHETTO:
        return int(kind == DAGGER)
    return 2 if kid == BRUTE and two_handed else 0


def extra(kid: int, dance: int = 0, undead: bool = False) -> int:
    """Added to hit and to damage with any weapon, melee or missile (KIT_EXTRA): a Battle Dancer's
    DANCE (+1 or -1, while it lasts), a Wilderness Avenger's 1 against undead (UNDEAD)."""
    if kid == BATTLE_DANCER:
        return dance
    return int(kid == AVENGER and undead)


def dance(dex: int, d20: int, fail_roll: int) -> Tuple[int, int]:
    """A Battle Dancer's dance as a fight starts: (bonus, rounds) for a D20 against DEX (+0, as the
    Dancing proficiency): danced, +1 for DEX less the roll in rounds (at least 1); stumbled, -1 for
    FAIL_ROLL (a d8) rounds."""
    if d20 <= dex:
        return 1, max(1, dex - d20)
    return -1, fail_roll


def two_weapon_base(kid: int, base: int) -> int:
    """AD&D's penalty for two weapons in a hand (BASE: -2 the main hand, -4 the off hand) with the
    kit's: a Ghetto Fighter's 2 better (none, -2)."""
    return base + 2 if kid == GHETTO else base


def ac(kid: int, shield: bool, level: int = 0, base: int = 10) -> int:
    """Added to AC (KIT_AC; lower is better): a Ravager's base AC by its level (RAVAGER_AC) where
    better than its sheet's BASE, armour improving it as before; a Wanderer's 1 worse; a Sentinel's
    2 better with a shield in a hand, an Arena Champion's 1; a Grove Warden's 1 better for every 3 levels (LEVEL, its
    class level)."""
    if kid == RAVAGER:
        table = RAVAGER_AC[min(max(level, 1), len(RAVAGER_AC)) - 1]
        return -max(0, base - table)
    if kid == WANDERER:
        return 1
    if kid == SENTINEL and shield:
        return -2
    if kid == CHAMPION and shield:
        return -1
    if kid == GROVE_WARDEN:
        return -(level // 3)
    return 0


def dance_ac(kid: int, dance: int) -> int:
    """Added to AC by a Battle Dancer's dance (KIT_AC; lower is better): 1 better while it danced
    well, 1 worse while it stumbled."""
    return -dance if kid == BATTLE_DANCER else 0


def thac0(kid: int, level: int, game_thac0: int) -> int:
    """The THAC0 the game gives a character of kit KID (PROBE_THAC0), its own GAME_THAC0 at class
    level LEVEL: a Swashbuckler's, Crusader's, Battle Mage's or Mind Warrior's a warrior's (21 less
    the level, 1 at best) where better; a Scholar's 1 worse."""
    if kid == SCHOLAR:
        return game_thac0 + 1
    if kid in WARRIOR_THAC0:
        return min(game_thac0, max(1, 21 - level))
    return game_thac0


def slot_level(kid: int, level: int) -> int:
    """The class level the spell slots are counted from (PROBE_SLOT_LEVEL): an Elementalist's a
    level behind."""
    return max(0, level - 1) if kid == ELEMENTALIST else level


def slots(kid: int, magic: int, level: int, spell_level: int, game_slots: int) -> int:
    """The spell slots at SPELL_LEVEL of a character of kit KID and class level LEVEL, the game
    giving GAME_SLOTS of MAGIC (WIZARD or PRIEST) (PROBE_SLOTS): an Arcanist's wizard slots 1 more
    at each spell level it has any, a Battle Mage's 1 fewer, a Crusader's and a Wilderness
    Avenger's priest slots 1 fewer; a
    Seeker's and a Justifier's priest slots their own tables' (SEEKER_SLOTS), WIS's left out, and a
    Shinobi's wizard slots the Seeker's by its thief level."""
    if kid == ARCANIST and magic == WIZARD:
        return game_slots + 1 if game_slots else 0
    if (kid == BATTLE_MAGE and magic == WIZARD) or (kid in (CRUSADER, AVENGER) and magic == PRIEST):
        return max(0, game_slots - 1)
    if kid == SHINOBI and magic == WIZARD:
        kid = SEEKER
    elif kid in (SEEKER, JUSTIFIER) and magic != PRIEST:
        return game_slots
    if kid in (SEEKER, JUSTIFIER):
        if not 1 <= spell_level <= 3:
            return 0
        if kid == JUSTIFIER:
            return int(level >= JUSTIFIER_FIRST and spell_level == 1)
        if level < SEEKER_FIRST:
            return 0
        return SEEKER_SLOTS[min(level, SEEKER_FIRST + len(SEEKER_SLOTS) - 1) - SEEKER_FIRST][spell_level - 1]
    return game_slots


def psp_cost(kid: int, power: int, cost: int) -> int:
    """The PSP power POWER (0-33) costs a character of kit KID to use, the game asking COST
    (KIT_PSP): a Mind Bender's telepathy 2 less and its psychokinesis 2 more, a Kineticist's the
    other way about (psychometabolism as it is); a Titan Mind's psychometabolism 2 less and its
    telepathy 2 more (psychokinesis as it is); never below 1, and a cost of 0 as it is."""
    if cost <= 0 or kid not in (MIND_BENDER, KINETICIST, TITAN_MIND):
        return cost
    if kid == TITAN_MIND:
        return cost if power <= PK_LAST else max(1, cost + (2 if power >= TP_FIRST else -2))
    change = -2 if kid == MIND_BENDER else 2
    if power <= PK_LAST:
        change = -change
    elif power < TP_FIRST:
        change = 0
    return max(1, cost + change)


def cure_bonus(kid: int, spell: int, outdoors: bool = False) -> int:
    """Added to the healing of SPELL cast by a character of kit KID (PROBE_CURE): a Healer's 1 a
    die of Cure Light, Serious and Critical Wounds; a Rescuer's too, under the open sky (OUTDOORS)."""
    if (kid == HEALER or kid == RESCUER and outdoors) and spell in CURE_DICE and spell != BLOOD_FLOW:
        return CURE_DICE[spell][0]
    return 0


def cure_die(kid: int, spell: int) -> int:
    """The sides of the die more a Lifebinder's SPELL heals (PROBE_CURE: the cures and Blood
    Flow), or 0."""
    return CURE_DICE[spell][1] if kid == LIFEBINDER and spell in CURE_DICE else 0


def ranger_cast_drop(kid: int) -> int:
    """How much less than its ranger level a ranger casts at (PROBE_RANGER_CAST; the game's 7): a
    Seeker's 5 (1st at 6th level, 5th at 10th), a Justifier's 9 (1st at 10th)."""
    return {SEEKER: 5, JUSTIFIER: 9}.get(kid, 7)


def shinobi_cast(level: int) -> int:
    """The level a Shinobi of thief level LEVEL casts its wizard spells at (DSCLOG's SHINOBI_CAST):
    5 less, 1st at 6th level."""
    return max(0, level - (SHINOBI_FIRST - 1))


def spook_penalty(preserver_level: int, shinobi_thief_level: int = 0) -> int:
    """Spook's save modifier (DSCLOG's SPOOK_SAVE): 1 worse for each 2 levels the caster casts it at,
    a preserver's level or a Shinobi's casting level (shinobi_cast of SHINOBI_THIEF_LEVEL), the more;
    no worse than game.SPOOK_MOST."""
    from .game import SPOOK_MOST
    level = max(preserver_level, shinobi_cast(shinobi_thief_level) if shinobi_thief_level else 0)
    return -min(SPOOK_MOST, level // 2)


def cast_level(kid: int, spell: int, level: int, thief_level: int) -> int:
    """The level a spell is cast at, LEVEL from the classes, with the kit's: a Shinobi's for a
    wizard spell its thief level's (shinobi_cast) if better. As the game's caster level routine
    (81B16h: the spell levels it may cast, half that rounded up; Dispel Magic) has it with
    PROBE_CAST_LEVEL, and the level a spell's duration and damage take (5E25Ch) with
    PROBE_SPELL_LEVEL."""
    if kid == SHINOBI and (spell <= WIZARD_LAST or spell in NEW_SPELLS):
        return max(level, shinobi_cast(thief_level))
    return level


SKY_KITS, SKY_MORE = frozenset((SPIRIT_CALLER, WASTE_SEER)), 2


def sky_level(kid: int, spell: int, level: int, outdoors: bool) -> int:
    """The level priest spell SPELL takes for its duration and damage, LEVEL the game's, with a
    Spirit Caller's or Wasteland Seer's (PROBE_SPELL_LEVEL's SKY_LEVEL): 2 more under the open sky
    (OUTDOORS), 1 less under a roof, no less than 1."""
    if kid not in SKY_KITS or not WIZARD_LAST < spell <= SPELL_LAST:
        return level
    return level + SKY_MORE if outdoors else level - 1 if level > 1 else level


def spell_class_level(kid: int, cls: int, level: int, ranger_rule: bool) -> int:
    """The level of class CLS (LEVEL) that a spell's duration and damage count (the game's routine
    at 5E25Ch, which takes the best of the caster's classes that cast the spell), with
    PROBE_RANGER_LEVEL's: a ranger's whole in the game, 7 less with the rule (RANGER_RULE), a
    Seeker's 5 less and a Justifier's 9 (ranger_cast_drop) whatever the rule; no less than 0."""
    if cls not in RANGER_CLASSES:
        return level
    drop = ranger_cast_drop(kid) if kid in (SEEKER, JUSTIFIER) or ranger_rule else 0
    return max(0, level - drop)


def hit_die(kid: int, sides: int) -> int:
    """A level's hit die, SIDES the class's (PROBE_HIT_DIE, PROBE_CR_DIE): a Battle Mage's a d6,
    a Mind Warrior's a d8, an Arcanist's a d3."""
    return {BATTLE_MAGE: 6, MIND_WARRIOR: 8, ARCANIST: 3}.get(kid, sides)


def max_psp(kid: int, psp: int) -> int:
    """The most PSP a level up gives, PSP the game's (PROBE_MAX_PSP): a Mind Warrior's a tenth
    fewer (rounded down)."""
    return psp - psp // 10 if kid == MIND_WARRIOR else psp


def shinobi_pick_level(level: int) -> int:
    """The highest spell level a Shinobi of thief level LEVEL may learn (CHOOSE A SPELL's), half its
    casting level rounded up, as the game's for a preserver."""
    return (shinobi_cast(level) + 1) // 2


def pick_list(kid: int, known, most: int, new_spells: bool = True):
    """The spells a character of kit KID may pick at a level up, for a Shinobi (PROBE_PICK_LIST):
    its own up to spell level MOST that it doesn't know (KNOWN(spell) true), Fogbolt only with the
    new spells on (NEW_SPELLS); None for others (the game's list)."""
    if kid != SHINOBI:
        return None
    return [spell for spell, lvl in SHINOBI_SPELLS
            if lvl <= most and not known(spell) and (new_spells or spell not in NEW_SPELLS)]


def move(kid: int) -> int:
    """Added to Move in a fight (KIT_MOVE): a Stalker's 2."""
    return 2 if kid == STALKER else 0


def initiative(kid: int, outdoors: bool = False) -> int:
    """Added to initiative (PROBE_INIT): a Sentinel's 2, a Military Scout's 2 under the open sky
    (OUTDOORS)."""
    if kid == SENTINEL:
        return 2
    return 2 if kid == SCOUT and outdoors else 0


# Path-finder: while a Wayfinder of the party is up, each party member's Move in a fight and
# initiative 1 more (DSCLOG's PATH_UP, in KIT_MOVE and PROBE_INIT); while one is down (stunned to
# petrified) and none up, 1 less (PATH_DOWN)
PATH_MOVE, PATH_INITIATIVE = 1, 1
# attacking from behind: 2 to hit (the game's), a Rescuer's 1 (DSCLOG's KIT_REAR); a Military
# Scout never backstabs (KIT_REAR takes it back)
REAR, RESCUER_REAR = 2, 1


def rear_to_hit(kid: int) -> int:
    """What attacking from behind adds to hit for a character of kit KID (KIT_REAR)."""
    return RESCUER_REAR if kid == RESCUER else REAR


def backstabs(kid: int) -> bool:
    """Whether a character of kit KID can backstab (KIT_REAR: a Military Scout can't)."""
    return kid != SCOUT


GHETTO_OTHER_TO_HIT = -1  # (a Ghetto Fighter with anything but a dagger, melee or missile: KIT_TO_HIT)


def ghetto_to_hit(kid: int, kind: Optional[int]) -> int:
    """A Ghetto Fighter's 1 worse to hit with anything but a dagger (KIND the weapon kind, None
    for none)."""
    return GHETTO_OTHER_TO_HIT if kid == GHETTO and kind != DAGGER else 0
SCOUT_MISSILE_KINDS = frozenset((BOW, BOW + 1, BOW + 2))  # (the bow, sling and staff sling)


def arrow_plus(kid: int, plus: int) -> int:
    """An arrow's plus as a character of kit KID shoots it from a bow (PROBE_ARROW): a Spellarcher's
    1 better, and at least +1 (magical, so it hurts what only magic weapons hurt)."""
    return max(plus, 0) + 1 if kid == SPELLARCHER else plus


POISONER_TO_HIT = -1  # (every attack, melee or missile: KIT_TO_HIT)
POISON_POWER = 176  # the monsters' "poison (10 damage)", a Poisoner's first hit in a fight (PROBE_POISON)


# a Wild Fury's Wild Fighting (wild.py; DSCLOG's KIT_WILD): checked against CON as a fight starts,
# for the fight. Passed, 1 more attack a round in melee (2 halves) and 3 more damage; failed, 3
# worse to hit and AC 3 worse (no worse than WILD_AC_MOST), every fight.
WILD_TO_HIT, WILD_DAMAGE, WILD_HALVES, WILD_AC, WILD_AC_MOST = -3, 3, 2, 3, 10


def wild_check(con: int, d20: int) -> bool:
    """A Wild Fury's Wild Fighting check: a D20 of CON or less (the proficiency's, +0)."""
    return d20 <= con


def wild_ac(ac: int) -> int:
    """AC (lower is better) fighting wild: WILD_AC worse, but no worse than WILD_AC_MOST (one
    already worse kept as it is)."""
    return ac if ac >= WILD_AC_MOST else min(ac + WILD_AC, WILD_AC_MOST)


def missile_to_hit(kid: int, kind: Optional[int], outdoors: bool) -> int:
    """Added to hit with a missile weapon of KIND (KIT_TO_HIT): a Military Scout's 1 with a bow,
    sling or staff sling under the open sky."""
    return int(kid == SCOUT and outdoors and kind in SCOUT_MISSILE_KINDS)


def save(kid: int, spell: int, kinds: int = 0) -> int:
    """Added to a saving throw against SPELL (KIT_SAVE; KINDS its record's +1Ah): a Sentinel's -1
    against a wizard's or priest's spell, a Myrmidon's -4 against a charm, a Wanderer's +3 against
    fire and cold (as the game's Resist Fire and Resist Cold)."""
    if kid == SENTINEL and 0 <= spell <= SPELL_LAST:
        return -1
    if kid == MYRMIDON and spell in CHARMS:
        return -4
    if kid == WANDERER and 0 <= spell < 256 and kinds & (FIRE | COLD):
        return 3
    return 0


def champion(kid: int, shield: bool, melee: bool) -> Tuple[int, int]:
    """(to hit, damage) an Arena Champion adds to an attack (KIT_CHAMPION), in melee only: with a
    shield in a hand +1 and +1; with none, -1 to hit."""
    if kid != CHAMPION or not melee:
        return 0, 0
    return (1, 1) if shield else (-1, 0)


def thief_skill(kid: int, skill: int, outdoors: bool = False) -> int:
    """Added to a thief skill (game.THIEF_SKILLS' numbers; the helper's KIT_SKILL): SKILLS' (an
    Assassin's -15 to pick pockets and open locks, a Swashbuckler's -10 to every one, a
    Shadowblade's, Ghetto Fighter's and Wayfinder's); a Military Scout's +10 to finding traps,
    moving silently, hiding and climbing under the open sky (OUTDOORS), -5 under a roof."""
    if kid == SCOUT:
        return (SCOUT_OUT if outdoors else SCOUT_IN) if skill in SCOUT_SKILLS else 0
    return SKILLS[kid][skill] if kid in SKILLS and 0 <= skill < 8 else 0


def stealth(kid: int) -> int:
    """Added to a ranger's hiding in shadows and moving silently (the stealth rule's, rolled by
    the Loader): a Stalker's 15."""
    return 15 if kid == STALKER else 0


def second_sphere(kid: int, sheet: bytes) -> Optional[int]:
    """An Elementalist's second sphere (0 air to 3 water), or None (not one, or none chosen), as
    DSCLOG's EL_SECOND."""
    if kid != ELEMENTALIST or len(sheet) <= SPHERE2 or not 1 <= sheet[SPHERE2] & SPHERE2_MASK <= 4:
        return None
    return (sheet[SPHERE2] & SPHERE2_MASK) - 1


_PRIEST, _WARRIOR = frozenset(range(1, 9)), frozenset((9, 10)) | frozenset(RANGER_CLASSES)
_NO_SHIELD = frozenset(range(5, 9)) | {11}  # (druids and the preserver: no shield)
# By kit, the classes (1-17) a human with it may not change to (DSCLOG's DUAL_BANS): its own slot
# table would take the new class's place (a Seeker's or Justifier's priest slots, a Shinobi's
# wizard ones); a warrior's THAC0 is a warrior class's already (Swashbuckler, Crusader, Battle
# Mage, Mind Warrior); it needs a shield the class can't hold (Arena Champion, Sentinel), or a
# two-handed melee weapon the class can't use (Brute: a psionicist's, an air cleric's); a Stalker's
# hiding would add to a thief's own (the thief); a Grove Warden's AC to a gladiator's own (the gladiator).
DUAL_BANS = {SEEKER: _PRIEST, JUSTIFIER: _PRIEST, SHINOBI: frozenset((11,)),
             **{k: _WARRIOR for k in WARRIOR_THAC0},
             CHAMPION: _NO_SHIELD, SENTINEL: _NO_SHIELD, BRUTE: frozenset((12, 1)),
             STALKER: frozenset((17,)), GROVE_WARDEN: frozenset((10,))}


def dual_banned(kid: int, cls: int) -> bool:
    """Whether a human with kit KID (asleep or not) may not change to class CLS (1-17), as DSCLOG's
    PROBE_DUAL_BAN greys it on the DUAL window (DUAL_BANS)."""
    return cls in DUAL_BANS.get(kid, ())


# Kits barred from going together, either way round (DSCLOG's KIT_PAIRS): one needing a shield and one
# forbidding it (Arena Champion, Sentinel; Twin-blade, Shinobi, Ravager); two-weapon fighting and
# an off hand free of weapons (Twin-blade, Healer); a two-handed weapon and weapons it can't be
# (Brute; Shinobi, Lifebinder); two ACs that grow by level, one on top of the other (Ravager, Grove
# Warden); a warrior's THAC0 twice over (WARRIOR_THAC0: Swashbuckler, Crusader, Battle Mage, Mind Warrior).
KIT_PAIRS = frozenset(frozenset(p) for p in (
    (CHAMPION, TWIN_BLADE), (CHAMPION, SHINOBI), (CHAMPION, RAVAGER), (SENTINEL, TWIN_BLADE),
    (SENTINEL, SHINOBI), (SENTINEL, RAVAGER), (TWIN_BLADE, HEALER), (BRUTE, SHINOBI), (BRUTE, LIFEBINDER),
    (RAVAGER, GROVE_WARDEN),
    *((a, b) for a in WARRIOR_THAC0 for b in WARRIOR_THAC0 if a < b)))


def dual_kit_banned(kid: int, classes, kids) -> bool:
    """Whether a human changing class may not take kit KID for its new class, CLASSES (1-17) the
    classes it had and KIDS their kits (asleep too), as DSCLOG's DK_BANNED blanks it on the KIT
    menu: the kit's DUAL_BANS hold one of the classes, or it and one of the kits are a KIT_PAIRS
    pair. (The kits' own DUAL_BANS on the new class are the DUAL window's: dual_banned.)"""
    return any(c in DUAL_BANS.get(kid, ()) for c in classes) or any(frozenset((kid, k)) in KIT_PAIRS for k in kids)


def spell_spheres(kid: int, cls: int, second: Optional[int], spheres: int) -> int:
    """A spell's mask of the classes that cast it (SPHERES), for a caster of class CLS with kit KID:
    an Elementalist's second sphere's spells its own class's too (DSCLOG's EL_SPHERES: the second
    sphere's cleric bit, 4 the air cleric's to 20h the water cleric's, brings its class's, 2 << CLS)."""
    if kid == ELEMENTALIST and second is not None and spheres & (4 << second):
        spheres |= 2 << cls
    return spheres


def allows(kid: int, typ: bytes, kind: Optional[int], chosen: Optional[int], specialize: bool) -> bool:
    """Whether the kit lets a character use an item type whatever its classes' lists and
    restrictions (TYP its record, KIND its weapon kind or None), as DSCLOG's KIT_ALLOWS: a Battle
    Mage the weapons of its chosen weapon spec (CHOSEN, with weapon specialization on: SPECIALIZE)
    and light armour (leather, or of no material; not a shield); a Battle Dancer long swords and
    bows (DANCER_KINDS), whatever its cleric's sphere."""
    if kid == BATTLE_DANCER:
        return kind in DANCER_KINDS
    if kid != BATTLE_MAGE:
        return False
    flags, kinds, mat = typ[0], typ[0x0F], typ[8] & 0x4F
    if kinds & ARMOUR:
        return not flags & SHIELD and mat in (LEATHER, NO_MATERIAL)
    return specialize and kind is not None and kind == chosen


def forbids_off_hand(kid: int, typ: bytes) -> bool:
    """Whether the kit keeps an item from the off hand: anything a Battle Mage's, a weapon a
    Healer's (DSCLOG's KIT_FORBIDS with KF_OFF_HAND)."""
    return kid == BATTLE_MAGE or kid == HEALER and bool(typ[0] & (MELEE | MISSILE | THROWN))


# the kits held to light armour asleep too (DSCLOG's KIT_LIGHT): a thief's own limit kept after
# dual-classing, and an archer's
LIGHT_KITS = frozenset((ASSASSIN, SHINOBI, SHADOWBLADE, POISONER, SPELLARCHER))


def light_only(kid: int, typ: bytes) -> bool:
    """Whether kit KID, awake or asleep, keeps its character from item type TYP: armour that isn't
    light, for LIGHT_KITS (DSCLOG's KIT_LIGHT)."""
    return kid in LIGHT_KITS and bool(typ[0x0F] & ARMOUR) and not typ[0] & SHIELD \
        and typ[8] & 0x4F not in (LEATHER, NO_MATERIAL)


def forbids(kid: int, typ: bytes, kind: Optional[int], half_giant: bool, spec: bool = False,
            off_hand: bool = False, sphere: int = 0) -> bool:
    """Whether the kit keeps a character from an item type (TYP its record; KIND its weapon kind,
    or None), as DSCLOG's KIT_FORBIDS: a Ravager a shield, a missile or thrown weapon and armour that isn't
    light; a Twin-blade a shield, and a two-handed weapon (but a
    half-giant's, HALF_GIANT: with the rule for its hands); a Brute a one-handed melee weapon, a
    shield (but a half-giant's), and, choosing a weapon spec (SPEC), a missile weapon; a Stalker
    armour that isn't light; a Grove Warden a metal weapon; a Lifebinder a weapon of a kind not
    blunt; a Shinobi a shield, armour that isn't light, a weapon not of SHINOBI_KINDS; a Seeker a
    weapon (of a kind) its SPHERE (0 air to 3 water) doesn't allow, as a cleric's
    (restrict.sphere_allows), but the bow; a Shadowblade and a Ghetto Fighter a shield. Going to the off hand (OFF_HAND): nothing for a Battle
    Mage, no weapon for a Healer."""
    flags, kinds, mat = typ[0], typ[0x0F], typ[8] & 0x4F
    weapon = bool(flags & (MELEE | MISSILE))
    if off_hand and forbids_off_hand(kid, typ):
        return True
    light = not kinds & ARMOUR or bool(flags & SHIELD) or mat in (LEATHER, NO_MATERIAL)
    if kid == RAVAGER:
        return bool(flags & (SHIELD | MISSILE | THROWN)) or not light
    if kid == TWIN_BLADE:
        return bool(flags & SHIELD) or weapon and bool(kinds & TWO_HANDED) and not half_giant
    if kid == BRUTE:
        if flags & SHIELD:
            return not half_giant
        if flags & MELEE:
            return not kinds & TWO_HANDED
        return bool(flags & MISSILE) and spec
    if kid == STALKER:
        return bool(kinds & ARMOUR) and not flags & SHIELD and mat not in (LEATHER, NO_MATERIAL)
    if kid == GROVE_WARDEN:
        return weapon and mat == METAL
    if kid == LIFEBINDER:
        return kind is not None and kind not in BLUNT
    if kid == SEEKER:
        from . import restrict
        return weapon and kind is not None and kind != BOW and not restrict.sphere_allows(sphere, typ, kind)
    if kid == SHINOBI:
        if flags & SHIELD:
            return True
        if kinds & ARMOUR:
            return mat not in (LEATHER, NO_MATERIAL)
        return kind is not None and kind not in SHINOBI_KINDS
    if kid == BATTLE_DANCER:
        return kind is not None and kind not in DANCER_KINDS
    if kid in (SHADOWBLADE, GHETTO):
        return bool(flags & SHIELD)
    return False
