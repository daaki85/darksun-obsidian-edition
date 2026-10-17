"""Class restrictions (the Options tab's rule): what a character's classes keep it from equipping,
on top of the game's own class lists (each item type's mask of the classes that may use it, of
which one of the character's classes is enough). The strictest class wins. DSCLOG's
PROBE_CAN_USE does this in the game; this is its model, for the tests and the Loader.

- A psionicist, whatever its other classes allow: light armour only (leather, hide, silk), a
  leather shield only, and of weapons only daggers, short swords, maces, clubs, chatkchas, bows
  and slings.
- A thief: light armour only, but a multiclass one (a fighter/thief, a cleric/thief), or a human
  thief who was a fighter, gladiator, ranger or cleric (dual_warrior), may wear what its other class
  allows; it then has no thief skills and no backstab in armour that isn't light (thief_heavy).
  A multiclass one a shield only a leather one that another of its classes allows.
- A preserver of that one class: no armour and no shield (a Battle Mage, kits.py, may wear light
  armour all the same: kit_allows); a human preserver who was a warrior may (dual_warrior).
- A druid: no armour, no shield.
- A cleric: only the weapons of its sphere, or of any of its spheres (a ranger who became a
  cleric keeps the ranger's): air, missile and thrown weapons and daggers; earth, stone,
  obsidian, metal and wood; fire, obsidian; water, bone and wood.

- A multiclass preserver, or a human who has been a preserver and a fighter, gladiator or ranger
  (in either order): no spells, wizard or priest, while it wears armour (DSCLOG's PROBE_NO_CAST,
  at the game's test for its "No spell use" effect); a shield doesn't count.

A human who was a fighter, gladiator or ranger and has changed class keeps the weapons it
specialized in, whatever the new class allows, once its new class's level has passed the old
(asleep till then, as the class is). A ranger's bow is its own the same way (every ranger has
expertise with it): a multiclass ranger may use bows whatever its other classes allow (a fire
cleric's sphere), and so may a human once ranger, as its chosen weapons. No kit keeps a
character from a kind it specialized in either (kit_forbids), while its specs count
(specs_awake), but for the off hand's rules.

Helms count as armour. A human who has changed class (dual-classed: the class it has now is the
first) is held only by that class; another race's classes (multiclass) all hold it. Weapons of
no kind (spell-made weapons, gloves, the broken weapon) are as the game has them.
"""

from typing import Iterable, List, Optional, Set

from . import game, specialize

# Item type record fields (DSUN's IT1R, 20 bytes each)
TYPE_FLAGS, TYPE_MATERIAL, TYPE_KIND_FLAGS, TYPE_CLASSES = 0x00, 0x08, 0x0F, 0x10
MELEE, MISSILE, SHIELD, THROWN = 0x01, 0x02, 0x04, 0x10
ARMOUR = 0x80  # (+0Fh: shields have it too)
BRACERS_SLOT = 3  # (+9: where it is worn, as arm armour)
CLOAK_SLOT = 8  # (+9: worn as a cloak)
WOOD, BONE, STONE, OBSIDIAN, METAL, LEATHER = range(6)  # (the material's low nibble)
NO_MATERIAL = 0x40  # (with a low nibble of 0)

# Class numbers (game.CLASS_NAMES): a cleric, druid and ranger for each element
CLERICS, DRUIDS, RANGERS = range(1, 5), range(5, 9), range(13, 17)
PRESERVER, PSIONICIST, THIEF = 11, 12, 17
AIR, EARTH, FIRE, WATER = range(4)
THIEF_BIT = 0x400  # (the sheet's class flags, +12h)

PSIONICIST_KINDS = frozenset(specialize.KINDS.index(k) for k in
                             ("dagger", "short sword", "mace", "club", "chatkcha", "bow", "sling"))


def material(typ: bytes) -> int:
    """The material's number (WOOD..LEATHER), or -1 for none."""
    low = typ[TYPE_MATERIAL] & 0x0F
    return -1 if typ[TYPE_MATERIAL] & NO_MATERIAL and not low else low


def is_weapon(typ: bytes) -> bool:
    return bool(typ[TYPE_FLAGS] & (MELEE | MISSILE))


def is_shield(typ: bytes) -> bool:
    return bool(typ[TYPE_FLAGS] & SHIELD)


def is_armour(typ: bytes) -> bool:
    """Body, arm and leg armour and helms: not shields, nor bracers of defense (worn on the arms,
    of no material: DSCLOG's BRACERS), nor a cloak of protection (worn as a cloak)."""
    return bool(typ[TYPE_KIND_FLAGS] & ARMOUR) and not is_shield(typ) and not is_bracers(typ) \
        and not is_robe(typ) and typ[9] != CLOAK_SLOT


def is_bracers(typ: bytes) -> bool:
    return len(typ) > 9 and typ[9] == BRACERS_SLOT and typ[8] & 0x40 and not typ[8] & 0x0F


def is_robe(typ: bytes) -> bool:
    """A robe (robes.py): worn on the chest, of no material, for preservers, psionicists and
    druids alone (DSCLOG's ROBE: not armour)."""
    return len(typ) > 0x11 and typ[9] == 1 and typ[8] == 0x40 and typ[TYPE_CLASSES:TYPE_CLASSES + 2] == b"\x90\x01"


def is_light(typ: bytes) -> bool:
    return material(typ) in (LEATHER, -1)


def spheres(classes: Iterable[int]) -> Set[int]:
    return {(c - 1) % 4 for c in classes if c in CLERICS or c in RANGERS}


def elementalist_sphere(sheet: bytes) -> Set[int]:
    """An Elementalist's (kits.py, the rule for kits in force) second sphere, as a set (empty for none)."""
    from . import kitpages, kits
    if not game.RULES_IN_FORCE & game.RULE_KITS:
        return set()
    second = kits.second_sphere(kits.ELEMENTALIST if kits.ELEMENTALIST in kitpages.kit_ids(sheet) else 0, sheet)
    return set() if second is None else {second}


def sphere_allows(sphere: int, typ: bytes, kind: int) -> bool:
    if sphere == AIR:
        return bool(typ[TYPE_FLAGS] & (MISSILE | THROWN)) or kind == specialize.KINDS.index("dagger")
    return material(typ) in {EARTH: (STONE, OBSIDIAN, METAL, WOOD), FIRE: (OBSIDIAN,), WATER: (BONE, WOOD)}[sphere]


WARRIORS = frozenset((9, 10)) | frozenset(RANGERS)


def specialized_back(sheet: bytes, kind: int) -> bool:
    """A human who was a fighter, gladiator or ranger and has dual-classed keeps the weapons it
    specialized in once the new class's level has passed the old: none of the new class's
    limits on them. A ranger's bow is its own too: a multiclass ranger's always, a human's while
    it is a ranger or once its new class's level has passed its ranger level."""
    human = sheet[game.SHEET_RACE] == game.HUMAN
    classes = sheet[game.SHEET_CLASSES:game.SHEET_CLASSES + 3]
    levels = sheet[game.SHEET_LEVELS:game.SHEET_LEVELS + 3]
    if kind == specialize.KINDS.index("bow") and any(
            c in RANGERS and (not human or i == 0 or levels[i] < levels[0]) for i, c in enumerate(classes)):
        return True
    if not human or kind + 1 not in sheet[game.SPEC_SLOTS:game.SPEC_SLOTS + game.SPEC_COUNT]:
        return False
    return any(classes[i] in WARRIORS and levels[i] < levels[0] for i in (1, 2))


def specs_awake(sheet: bytes) -> bool:
    """Whether the character's weapon specs count (DSCLOG's SPECS_AWAKE): one class, or not a
    human; a human's warrior class now, or before and passed by the class it has now; a Battle
    Mage's kit awake. Not while the class or kit that gave them sleeps."""
    from . import kitpages, kits
    classes = sheet[game.SHEET_CLASSES:game.SHEET_CLASSES + 3]
    levels = sheet[game.SHEET_LEVELS:game.SHEET_LEVELS + 3]
    if not classes[1] or sheet[game.SHEET_RACE] != game.HUMAN:
        return True
    if any(c in WARRIORS and (i == 0 or levels[i] < levels[0]) for i, c in enumerate(classes)):
        return True
    return bool(game.RULES_IN_FORCE & game.RULE_KITS) and kits.BATTLE_MAGE in kitpages.kit_ids(sheet)


def kit_forbids(sheet: bytes, item_type: int, typ: bytes, spec: bool = False, off_hand: bool = False) -> bool:
    """Whether one of the character's kits that count (kits.py, the rule for kits in force) keeps it
    from an item type, whatever the class restrictions; SPEC: choosing a weapon spec; OFF_HAND: to
    the off hand."""
    from . import kitpages, kits
    if not game.RULES_IN_FORCE & game.RULE_KITS:
        return False
    if any(kits.light_only(kid, typ) for kid, _, _ in kitpages.kits_of(sheet)):
        return True  # (a thief's or archer's kit, asleep too: light armour only)
    kind = specialize.kind_of(item_type) if is_weapon(typ) else None
    chosen = not spec and kind is not None and kind + 1 in sheet[game.SPEC_SLOTS:game.SPEC_SLOTS + game.SPEC_COUNT] \
        and specs_awake(sheet)
    half_giant = sheet[game.SHEET_RACE] == game.RACE_HALF_GIANT and bool(game.RULES_IN_FORCE & game.RULE_HALF_GIANT)
    for kid in kitpages.kit_ids(sheet):
        if chosen:  # (a kind it specialized in, its specs counting: none, but for the off hand's rules)
            if off_hand and kits.forbids_off_hand(kid, typ):
                return True
            continue
        sphere = (kitpages.kit_class_of(sheet, kid) - 1) % 4  # (a ranger's, for a Seeker)
        if kits.forbids(kid, typ, kind, half_giant, spec, off_hand, sphere):
            return True
    return False


def forbidding_kit(sheet: bytes, item_type: int, typ: bytes) -> Optional[int]:
    """The first of the character's kits that keeps it from an item type (kit_forbids, not
    choosing a spec nor for the off hand), or None."""
    from . import kitpages, kits
    if not game.RULES_IN_FORCE & game.RULE_KITS:
        return None
    for kid, _, _ in kitpages.kits_of(sheet):
        if kits.light_only(kid, typ):
            return kid
    kind = specialize.kind_of(item_type) if is_weapon(typ) else None
    half_giant = sheet[game.SHEET_RACE] == game.RACE_HALF_GIANT and bool(game.RULES_IN_FORCE & game.RULE_HALF_GIANT)
    for kid in kitpages.kit_ids(sheet):
        sphere = (kitpages.kit_class_of(sheet, kid) - 1) % 4
        if kits.forbids(kid, typ, kind, half_giant, False, False, sphere):
            return kid
    return None


def kit_allows(sheet: bytes, item_type: int, typ: bytes) -> bool:
    """Whether the character's kit (kits.allows, the rule for kits in force) lets it use an item
    type whatever its classes' lists and restrictions: a Battle Mage its chosen weapon spec's
    weapons and light armour, a Battle Dancer long swords and bows."""
    from . import kitpages, kits
    if not game.RULES_IN_FORCE & game.RULE_KITS:
        return False
    kind = specialize.kind_of(item_type) if is_weapon(typ) else None
    chosen = sheet[game.SPEC_SLOTS] - 1 if sheet[game.SPEC_SLOTS] else None
    return any(kits.allows(kid, typ, kind, chosen, bool(game.RULES_IN_FORCE & game.RULE_SPECIALIZE))
               for kid in kitpages.kit_ids(sheet))


def allowed(sheet: bytes, item_type: int, typ: bytes) -> bool:
    """Whether the character may equip an item of this type, given that the game lets it (the
    class restrictions; the kit's are kit_forbids, and what its kit allows, kit_allows, passes)."""
    if kit_allows(sheet, item_type, typ):
        return True
    classes = [c for c in sheet[game.SHEET_CLASSES:game.SHEET_CLASSES + 3] if c]
    human = sheet[game.SHEET_RACE] == game.HUMAN
    holding = classes[:1] if human else classes
    multiclass = not human and len(classes) > 1
    armour, shield = is_armour(typ), is_shield(typ)
    kind = specialize.kind_of(item_type) if is_weapon(typ) else None
    if kind is not None and specialized_back(sheet, kind):
        kind = None  # (its own: as the game has it)
    if PSIONICIST in holding:
        if armour and not is_light(typ) or shield and material(typ) != LEATHER:
            return False
        if kind is not None and kind not in PSIONICIST_KINDS:
            return False
    if THIEF in holding and armour and not is_light(typ) and not multiclass and not dual_warrior(sheet):
        return False
    if THIEF in holding and multiclass:
        if shield:
            others = int.from_bytes(typ[TYPE_CLASSES:TYPE_CLASSES + 2], "little")
            others &= int.from_bytes(sheet[game.SHEET_FLAGS:game.SHEET_FLAGS + 2], "little") & ~THIEF_BIT
            if material(typ) != LEATHER or not others:
                return False
    if holding == [PRESERVER] and (armour or shield) and not dual_warrior(sheet):
        return False
    if any(c in DRUIDS for c in holding) and (armour or shield):
        return False
    if any(c in CLERICS for c in holding) and kind is not None:
        if not any(sphere_allows(s, typ, kind) for s in spheres(classes) | elementalist_sphere(sheet)):
            return False
    return True


def dual_warrior(sheet: bytes) -> bool:
    """A human whose class now is thief or preserver and who was a fighter, gladiator or ranger
    before, or a thief who was a cleric before: it may wear what the warrior or cleric could
    (DSCLOG's DUAL_WARRIOR)."""
    classes = sheet[game.SHEET_CLASSES:game.SHEET_CLASSES + 3]
    before = set(WARRIORS) | (set(CLERICS) if classes[0] == THIEF else set())
    return sheet[game.SHEET_RACE] == game.HUMAN and classes[0] in (THIEF, PRESERVER) \
        and any(c in before for c in classes[1:])


def class_and_warrior(sheet: bytes, cls: int) -> bool:
    """Whether the character has class CLS and a fighter, gladiator or ranger class (DSCLOG's
    CLASS_AND_WARRIOR)."""
    classes = sheet[game.SHEET_CLASSES:game.SHEET_CLASSES + 3]
    return cls in classes and any(c in WARRIORS for c in classes)


def no_spells(sheet: bytes, worn: Iterable[bytes]) -> bool:
    """Whether a character can't cast for the armour it wears (the type records of what it has on
    its arms, legs, head and chest): a multiclass preserver, or a human who has been a preserver
    and a warrior."""
    classes = [c for c in sheet[game.SHEET_CLASSES:game.SHEET_CLASSES + 3] if c]
    if sheet[game.SHEET_RACE] == game.HUMAN:
        if not class_and_warrior(sheet, PRESERVER):
            return False
    elif len(classes) < 2 or PRESERVER not in classes:
        return False
    return any(is_armour(t) for t in worn)


def thief_heavy(sheet: bytes, worn: Iterable[bytes]) -> bool:
    """Whether a character with a thief class wears armour that isn't light (the type records of
    what it has on its arms, legs, head and chest): no thief skills, no backstab (DSCLOG's
    THIEF_HEAVY)."""
    return THIEF in sheet[game.SHEET_CLASSES:game.SHEET_CLASSES + 3] \
        and any(is_armour(t) and not is_light(t) for t in worn)


def usable(sheet: bytes, type_: int, typ: bytes, kit: bool = True) -> bool:
    """Whether the game's class lists, these restrictions and the kit's let the character use an
    item of this type (TYP its record); KIT false: the classes' alone (what the kit forbids not
    counted)."""
    flags = int.from_bytes(sheet[game.SHEET_FLAGS:game.SHEET_FLAGS + 2], "little")
    game_lets = bool(int.from_bytes(typ[TYPE_CLASSES:TYPE_CLASSES + 2], "little") & flags)
    return (game_lets or kit_allows(sheet, type_, typ)) and allowed(sheet, type_, typ) \
        and not (kit and kit_forbids(sheet, type_, typ))


def allowed_kinds(sheet: bytes, type_record) -> List[int]:
    """The weapon kinds a character can choose: those with an item type of the game's (any
    material: a fire cleric's long sword the obsidian one) that it can use (a fighter/psionicist,
    say, only the psionicist's). TYPE_RECORD(type) gives an item type's record. DSCLOG's
    KINDS_ALLOWED. Not the bow for a ranger: it has expertise with the bow already. A Battle Mage
    (kits.py) its own, whatever its class; a Spellarcher the bow only."""
    from . import kitpages, kits
    if game.RULES_IN_FORCE & game.RULE_KITS and kits.BATTLE_MAGE in kitpages.kit_ids(sheet):
        return sorted(kits.BATTLE_MAGE_KINDS)
    if game.RULES_IN_FORCE & game.RULE_KITS and kits.SPELLARCHER in kitpages.kit_ids(sheet):
        return [kits.BOW]
    ranger = int.from_bytes(sheet[game.SHEET_FLAGS:game.SHEET_FLAGS + 2], "little") & 0x200
    return [kind for kind, name in enumerate(specialize.KINDS)
            if not (ranger and name == "bow")
            and any(usable(sheet, t, type_record(t)) and not kit_forbids(sheet, t, type_record(t), spec=True)
                    for t in specialize._TYPES[name])]
