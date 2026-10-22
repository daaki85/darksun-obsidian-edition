"""Weapon specialization (the Options tab's rule): the weapon kinds a fighter, gladiator or ranger
can choose, and which of the game's item types each takes in.

The game has no notion of a weapon's kind: its item types are one per weapon and material (a
metal, a bone and an obsidian long sword are three), and its named weapons are types of their
own (Bloodwrath, Swiftbite). KIND_OF_TYPE sorts every weapon type into one of the sixteen KINDS,
by its dice, weight and name; the spell-made weapons (Flame Blade, Shillelagh, Spiritual
Hammer), the gloves and the broken weapon are none. For specialization alone the spell-made ones
count as their AD&D weapon's kind (CONJURED_KINDS, spec_kind_of): the Flame Blade a long sword
(AD&D's scimitar, which Athas hasn't), Shillelagh a club, Spiritual Hammer a mace (the war
hammer's nearest); restrictions treat them as the game does.

The kinds come in the order of the weapon window's slots, long sword first: the default for a
pick left unmade; a gladiator's second is the club, the next.
"""

from typing import Dict, List, Optional, Tuple

from . import game

KINDS = ("long sword", "club", "dagger", "short sword",
         "mace", "axe", "great axe", "pick",
         "quarterstaff", "polearm", "gythka", "cahulaks",
         "chatkcha", "bow", "sling", "staff sling")
DEFAULT = 0  # long sword

# The game's item types (DSUN's IT1R, numbered from 0) by kind, and the Loader's own short sword
_TYPES = {
    "long sword": (45, 63, 81, 47, 41, 50, 85, 97, 98),  # obsidian, metal, bone; Dragonsbane and El's
    # Drinker (47), Draketooth, Swiftbite, Dark Flame, Hornblade, Bloodwrath: all 1d8 blades
    "dagger": (17, 33, 84, 94, game.METAL_DAGGER_TYPE, game.AIR_DAGGER_TYPE, game.BONE_DAGGER_TYPE),  # obsidian, stone; Dag's Dagger, Terror Blade; the Loader's metal and bone
    "short sword": (game.SHORT_SWORD_TYPE, game.BONE_SHORT_SWORD_TYPE, game.OBSIDIAN_SHORT_SWORD_TYPE,
                    game.METAL_SHORT_SWORD_TYPE),  # Kurzak's (metal); the Loader's
    "mace": (20, 46, game.METAL_MACE_TYPE),  # bone (Mace, Wyvern Hook); Blackmace; the Loader's metal
    "club": (18,),  # Club, Striker
    "axe": (22, game.BONE_AXE_TYPE, game.OBSIDIAN_AXE_TYPE),  # Axe, Soulcrusher (metal); the Loader's
    "great axe": (2, game.METAL_GREAT_AXE_TYPE, game.BONE_GREAT_AXE_TYPE, game.OBSIDIAN_GREAT_AXE_TYPE),
    "pick": (112, game.METAL_PICK_TYPE),
    "quarterstaff": (3, 80),  # Quarterstaff, Parting Staff; Balk's Staff
    "polearm": (19, 111, game.METAL_POLEARM_TYPE),
    "gythka": (game.GYTHKA_TYPE,),
    "cahulaks": (21,),
    "chatkcha": (48,),
    "bow": (1, 69),  # Bow, Seeker; Phrain's Bow
    "sling": (64,),
    "staff sling": (0,),
}
KIND_OF_TYPE: Dict[int, int] = {t: KINDS.index(kind) for kind, types in _TYPES.items() for t in types}


def kind_of(item_type: int) -> Optional[int]:
    """The weapon kind (its number in KINDS) of an item type, or None for one that is none."""
    return KIND_OF_TYPE.get(item_type)


# the weapons spells make, by item type (the game's), and the kind each counts as for
# specialization (DSCLOG's CONJURED_KINDS): Shillelagh, the Flame Blade, Spiritual Hammer
CONJURED_KINDS: Dict[int, int] = {28: KINDS.index("club"), 29: KINDS.index("long sword"), 30: KINDS.index("mace")}


def spec_kind_of(item_type: int) -> Optional[int]:
    """The kind an item type counts as for weapon specialization: kind_of's, or a spell-made
    weapon's (CONJURED_KINDS); DSCLOG's SPEC_KIND."""
    return CONJURED_KINDS.get(item_type, KIND_OF_TYPE.get(item_type))


# A character's skill with a weapon, as DSCLOG's SPEC_OF works it out (game.SPEC_SLOTS holds the
# chosen kinds, kind + 1 each): NONE when it has chosen none (monsters too: the game's numbers),
# PLAIN with a weapon of another kind (or as a dual-classed warrior whose warrior class isn't
# back yet), EXPERT a ranger's (the
# attacks only), SPECIAL, MASTER (a fighter's own kind, its first, from 5th level), GRAND (9th)
NONE, PLAIN, EXPERT, SPECIAL, MASTER, GRAND = range(6)
SKILL_NAMES = {SPECIAL: "specialized", MASTER: "mastery", GRAND: "grand mastery"}
FIGHTER, GLADIATOR = 9, 10
MASTERY, GRAND_MASTERY = 5, 9


RANGERS = range(13, 17)


def active_classes(sheet: bytes) -> List[Tuple[int, int]]:
    """(class, level) for the classes whose abilities a character has now: all of them, but a
    human's earlier ones (dual-classed: the class it has now is the first) only once the new
    class's level has passed theirs."""
    classes = sheet[game.SHEET_CLASSES:game.SHEET_CLASSES + 3]
    levels = sheet[game.SHEET_LEVELS:game.SHEET_LEVELS + 3]
    human = sheet[game.SHEET_RACE] == game.HUMAN
    return [(classes[i], levels[i]) for i in range(3)
            if classes[i] and not (human and i and levels[i] >= levels[0])]


def skill(sheet: bytes, item_type: Optional[int]) -> int:
    """The character's skill with a weapon type, as DSCLOG's SPEC_OF_SHEET: a Justifier's (kits.py)
    expertise is specialization."""
    level = _skill(sheet, item_type)
    return SPECIAL if level == EXPERT and justifier(sheet) else level


def justifier(sheet: bytes) -> bool:
    """A Justifier (kits.py), the rule for kits in force (game.RULES_IN_FORCE)."""
    from . import kitpages, kits
    return bool(game.RULES_IN_FORCE & game.RULE_KITS) and kits.JUSTIFIER in kitpages.kit_ids(sheet)


def _skill(sheet: bytes, item_type: Optional[int]) -> int:
    from . import kitpages, kits
    chosen = sheet[game.SPEC_SLOTS:game.SPEC_SLOTS + game.SPEC_COUNT]
    if not any(chosen):
        return NONE
    kind = spec_kind_of(item_type) if item_type is not None else None
    bm = kitpages.kit_place_of(sheet, kits.BATTLE_MAGE)
    if game.RULES_IN_FORCE & game.RULE_KITS and bm is not None and sheet[0x22]:
        # (a Battle Mage who has changed class: its weapon spec the kit's alone, nothing while asleep)
        if not kitpages.kit_awake(sheet, bm):
            return NONE
        return EXPERT if kind is not None and kind + 1 == chosen[0] else PLAIN
    if kind is None or kind + 1 not in chosen:
        # (every ranger's expertise with the bow, chosen or not)
        if kind == KINDS.index("bow") and any(c in RANGERS for c, _ in active_classes(sheet)):
            return EXPERT
        return PLAIN
    active = active_classes(sheet)
    classes = {c for c, _ in active}
    if not classes & ({FIGHTER, GLADIATOR} | set(RANGERS)):
        # (a Battle Mage's, Crusader's or Mind Warrior's expertise; else a dual-classed warrior, until
        # the new class's level passes the old)
        return EXPERT if battle_mage(sheet) or war_kit(sheet) is not None else PLAIN
    if not {FIGHTER, GLADIATOR} & classes:
        return EXPERT
    first = chosen.index(kind + 1)
    if first > 1 or first == 1 and not myrmidon(sheet):
        return SPECIAL  # (a fighter's first kind goes on to mastery, a Myrmidon's second too)
    fighter = next((level for c, level in active if c == FIGHTER), 0)
    return GRAND if fighter >= GRAND_MASTERY else MASTER if fighter >= MASTERY else SPECIAL


def myrmidon(sheet: bytes) -> bool:
    """A Myrmidon (kits.py), the rule for kits in force (game.RULES_IN_FORCE)."""
    from . import kitpages
    return bool(game.RULES_IN_FORCE & game.RULE_KITS) and kitpages.KIT_IDS["Myrmidon"] in kitpages.kit_ids(sheet)


def battle_mage(sheet: bytes) -> bool:
    """A Battle Mage (kits.py), the rule for kits in force (game.RULES_IN_FORCE)."""
    from . import kitpages, kits
    return bool(game.RULES_IN_FORCE & game.RULE_KITS) and kits.BATTLE_MAGE in kitpages.kit_ids(sheet)


def war_kit(sheet: bytes) -> Optional[int]:
    """The Crusader or Mind Warrior kit of the character (awake, the rule for kits in force), which
    has expertise in its one chosen weapon spec, or None."""
    from . import kitpages, kits
    if not game.RULES_IN_FORCE & game.RULE_KITS:
        return None
    return next((k for k in kits.WAR_KIT_EXPERT if k in kitpages.kit_ids(sheet)), None)


def expert_attacks(halves: int, level: int, sheet: bytes) -> int:
    """The melee attacks a round (in halves) of a character who isn't a warrior (HALVES the game's,
    2 or fewer) with skill LEVEL, as DSCLOG's EXPERT_HALVES: a Battle Mage's, Crusader's or Mind
    Warrior's chosen weapon spec (EXPERT) the expertise rate, 3/2 a round, 2 from 7th level (of the
    kit's class); else HALVES."""
    from . import kitpages, kits
    if level != EXPERT or halves > 2:
        return halves
    kid = kits.BATTLE_MAGE if battle_mage(sheet) else war_kit(sheet)
    return 4 if kid is not None and kitpages.kit_level(sheet, kid) >= 7 else 3


def attacks(halves: int, level: int, missile: bool = False) -> int:
    """The attacks a round (in halves) with a weapon, from the game's (sheet +2Ah) and the skill
    with it, as DSCLOG's PROBE_ATTACKS has them: a warrior (more than 2 halves) in melee half an
    attack less with a kind not chosen, a grand master one more; missiles as the game has them."""
    if missile or halves <= 2:
        return halves
    return halves - 1 if level == PLAIN else halves + 2 if level == GRAND else halves


# A specialist's rate of fire (in halves) by kind, at specialist levels 1-6, 7-12 and 13 on
# (DSCLOG's MISSILE_RATE): AD&D's for the sling; the bow, staff sling and chatkcha (AD&D's other
# thrown weapons) a step above AD&D's
MISSILE_RATES = {"bow": (6, 8, 10), "sling": (3, 4, 5), "staff sling": (3, 4, 5), "chatkcha": (3, 4, 5)}


def warrior_level(sheet: bytes) -> int:
    """The specialist's level: the highest fighter, gladiator or ranger level of the classes it has now."""
    return max((level for c, level in active_classes(sheet) if c in (FIGHTER, GLADIATOR) or c in RANGERS),
               default=0)


def missile_attacks(halves: int, level: int, item_type: Optional[int], sheet: bytes) -> int:
    """A missile weapon's attacks a round (in halves): the weapon type's (HALVES, its +0Bh, as the
    game has it), or a specialist's rate of fire (LEVEL EXPERT or above: a ranger's too) when greater;
    a warrior's of a kind not chosen (PLAIN), from 7th level, the specialist's a band lower, as in melee."""
    kind = kind_of(item_type) if item_type is not None else None
    rates = MISSILE_RATES.get(KINDS[kind]) if kind is not None else None
    if level < PLAIN or not rates:
        return halves
    warrior = warrior_level(sheet)
    band = 0 if warrior < 7 else 1 if warrior < 13 else 2
    if level == PLAIN:
        return max(halves, rates[band - 1]) if band else halves
    rate = max(halves, rates[band])
    return rate + 2 if level == GRAND else rate  # (a grand master one more, as in melee)


def to_hit(level: int) -> int:
    """What the skill adds to hit (takes off THAC0)."""
    return 3 if level >= MASTER else 1 if level == SPECIAL else 0


def damage(level: int) -> int:
    """What the skill adds to the damage."""
    return 3 if level >= MASTER else 2 if level == SPECIAL else 0
