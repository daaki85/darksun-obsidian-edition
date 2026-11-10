"""What the game knows about a monster that it never shows: what hurts it, what doesn't, what
its hits do besides damage.

From DSUN.EXE's damage code:

* Every creature record has a kind (a word at +16h: 0 for people, other numbers for the
  monster kinds). A table at MONSTER_KINDS_SEG gives each kind a dword of properties (bits
  the code asks about one at a time) and a resistance class.
* A resistance class is up to four rules, each a mask of damage kinds and the percent of the
  damage the creature takes when a hit has any of those kinds. The largest percent that
  applies counts; with none, the creature takes it all.
* Every hit has damage kinds: a spell's from its record, a weapon's from its item type
  (crushing, slashing or piercing), plus bits for how magical the weapon is (+1 or better,
  +2 or better, +3 or better). So "0% from crushing, slashing and piercing, 100% from +1 or
  better" is a monster only magical weapons hurt.
* Undead (race 9 on the character sheet) take nothing from poison and draining, and mind-
  affecting spells and charms and holds don't work on them.

With "Spells and psionics as the manual describes them" (gamepatch.SPELLS_MANUAL) the monsters are
the manual's too: the shadows drain STR (DSCLOG's SHADOW_DRAIN) and shrug off cold, the Babau and the
Blue Slaad carry a deadly poison, and the Styr, the Djinn and the Tari get kinds of their own
(MANUAL_MONSTERS), in the Loader's copy of SEGOBJEX (object_chunks) and in a running game (mend).
"""

import struct
from typing import Dict, List, NamedTuple, Optional, Tuple

from . import game

CREATURE_KIND = 0x16  # word: the monster's kind (0 for people)
MONSTER_KINDS_SEG = 0x3E45  # from the load segment, where the game has it ...
# ... but DSCLOG moves it at the game's start (its SEG_MOVE: the spell records' room): the game's
# table of its data segments (8 bytes a selector, the segment first, from the load segment +
# SEGMENT_TABLE) says where; the kinds' selector is KINDS_SELECTOR
SEGMENT_TABLE, KINDS_SELECTOR = 0x4137, 0x3C0
KIND_COUNT = 42
KIND_PROPERTIES_OFF = 0x00  # dword per kind
KIND_CLASS_OFF = 0xA8  # byte per kind: its resistance class (0: none)
CLASS_MASKS_OFF, CLASS_PERCENTS_OFF, CLASS_SIZE, CLASS_RULES = 0xD2, 0xDA, 12, 4
CLASS_COUNT = 16
UNDEAD_RACE = 9

# damage kinds (the word at +1Ah of a spell record, and what a weapon's hit carries)
POISON, FIRE, COLD, CRUSHING, SLASHING, PIERCING = 0x1, 0x2, 0x4, 0x8, 0x10, 0x20
ACID, ELECTRICITY, DRAINING, MAGIC, PSIONIC, DEATH = 0x40, 0x80, 0x100, 0x200, 0x400, 0x800
PLUS1, PLUS2, PLUS3 = 0x1000, 0x2000, 0x8000  # a weapon's magic (+3 also for Disintegrate)
WEAPON_KINDS = ((CRUSHING, "crushing"), (SLASHING, "edged"), (PIERCING, "pointed"))
# what spells and powers do, as the game's own spells carry them (0x200: a spell)
OTHER_KINDS = ((POISON | MAGIC, "poison"), (FIRE | MAGIC, "fire"), (COLD | MAGIC, "cold"),
               (ELECTRICITY | MAGIC, "electricity"), (ACID | MAGIC, "acid"),
               (DRAINING | MAGIC, "draining"), (PSIONIC, "psionic attacks"), (DEATH | MAGIC, "death spells"))

# property bits, as the damage and effect code uses them
PROPERTY_TEXT = {
    0: "unaffected by spells left on the ground (fogs, clouds, walls, Web, Grease...)",
    1: "unaffected by spells left on the ground (fogs, clouds, walls, Web, Grease...)",
    5: "can't be charmed or held",
    9: "not held by Grease, Web, Entangle, Solid Fog, Quicksand or walls",
    21: "unaffected by Wall of Fog",
}
# its turns: one in four, its power at a foe (5A90Fh's table, for the bits shown)
PROPERTY_TEXT[31] = "breathes fire for 3d6 one turn in four (a save halves)"
# its hits cast one of the monsters' powers on the target as well
SPECIAL_ATTACKS = {
    2: "2d6 cold", 3: "paralysis", 4: "2d6 acid", 13: "poison (10 damage)", 14: "poison (30 damage)",
    15: "deadly poison", 16: "20 acid, which can eat a worn piece of armour", 25: "disease (1 hit in 10)",
    24: "a corroding touch, which can eat a worn piece of armour and the weapon held",
}
# ... and as the monsters as the manual describes them have it, for a kind's bit (DSCLOG's SHADOW_DRAIN,
# TARI_BITE, DJINN_TURN)
SHADOW_KIND, GREATER_SHADOW_KIND, STYR_KIND, DJINN_KIND, TARI_KIND = 15, 13, 38, 39, 40
DRAIN_TEXT = "1 STR drained (Weakened, 2d4 turns; no save)"
MANUAL_SPECIAL = {(SHADOW_KIND, 2): DRAIN_TEXT, (GREATER_SHADOW_KIND, 3): DRAIN_TEXT,
                  (TARI_KIND, 25): "disease (1 bite in 20)"}
DJINN_NOTE = "turns invisible and makes 4 to 7 mirror images of itself at its first turn of a fight"
DRAIN_TURNS = (2, 4)  # (2d4 turns: DSCLOG's)
TURN_SECONDS = 600
# a creature's alignment (its sheet's byte 1Ah), in two letters for the Look box and in words
ALIGNMENTS = {1: ("LG", "lawful good"), 2: ("LN", "lawful neutral"), 3: ("LE", "lawful evil"),
              4: ("NG", "neutral good"), 5: ("TN", "true neutral"), 6: ("NE", "neutral evil"),
              7: ("CG", "chaotic good"), 8: ("CN", "chaotic neutral"), 9: ("CE", "chaotic evil")}
SHEET_ALIGNMENT = 0x1A
LOOK_WIDTH = 15  # the characters a Look box line has room for (NEEDS +2 WEAPON)
# ... and in pixels: the game's font (RESOURCE.GFF's FONT 100) is 6 wide but for these
LOOK_PIXELS = 86
LOOK_SIDE = "\x01"  # (DSCLOG: the line goes on LEVEL's row, to its right, LOOK_SIDE_X = 60 on)
SIDE_PIXELS = 33  # ... where up to the box's edge
FONT_WIDTHS = {**{c: 4 for c in " !*+,.:;Ij"}, **{c: 5 for c in "?fhknrstu"}, **{c: 2 for c in "il"},
               **{c: 7 for c in "$^|"}}


def look_pixels(text: str) -> int:
    """How wide TEXT is in the game's font."""
    return sum(FONT_WIDTHS.get(c, 6) for c in text)


def look_fit(*forms: str) -> str:
    """The first of FORMS (the fullest first) that fits a Look box line, else the last."""
    return next((f for f in forms if look_pixels(f) <= LOOK_PIXELS), forms[-1])
# the short forms for the game's small Look box
SHORT_KINDS = {"poison": "POISON", "fire": "FIRE", "cold": "COLD", "electricity": "ELEC", "acid": "ACID",
               "draining": "DRAIN", "psionic attacks": "PSI", "death spells": "DEATH"}


class Rule(NamedTuple):
    mask: int
    percent: int


def damage_percent(rules: List[Rule], kinds: int) -> int:
    """The percent of a hit's damage a creature with these rules takes, as the game works it
    out: the largest percent among the rules whose mask the hit's kinds touch, else 100."""
    best = -1
    for rule in rules:
        if rule.mask & kinds and rule.percent > best:
            best = rule.percent
    return 100 if best < 0 else best


def weapon_kinds(kind: int, plus: int) -> int:
    """The damage kinds of a weapon's hit: its own kind and its magic."""
    return kind | (PLUS1 if plus >= 1 else 0) | (PLUS2 if plus >= 2 else 0) | (PLUS3 if plus >= 3 else 0)


class Defences(NamedTuple):
    weapon_plus: int  # the least plus a weapon needs to hurt it (0: any, None-like 4: none do)
    weapons_immune: List[str]  # weapon kinds that never hurt it, whatever their plus ("crushing")
    weapons_half: bool  # non-magical weapons do half
    immune: List[str]  # other damage it takes none of ("fire")
    half: List[str]  # other damage it takes half of
    notes: List[str]  # other things its properties do
    special: List[str]  # what its hits do besides damage
    undead: bool


def defences(rules: List[Rule], properties: int, undead: bool, kind: int = 0, manual: bool = False) -> Defences:
    """What a monster's resistance rules and properties come to (KIND's own, as the monsters as the
    manual describes them have them, with MANUAL)."""
    # weapons: the least plus that does any damage, for each kind of weapon
    need = {}
    for bit, name in WEAPON_KINDS:
        need[name] = next((plus for plus in range(4) if damage_percent(rules, weapon_kinds(bit, plus)) > 0), 4)
    immune_kinds = [name for name, plus in need.items() if plus == 4]
    hurting = [plus for plus in need.values() if plus < 4]
    weapon_plus = min(hurting) if hurting else 0
    if immune_kinds and len(immune_kinds) == len(need):  # nothing hurts it: say so once
        weapon_plus = 4
    half = all(damage_percent(rules, weapon_kinds(bit, 0)) == 50 for bit, _ in WEAPON_KINDS)
    immune, halved = [], []
    for kinds, name in OTHER_KINDS:
        pct = damage_percent(rules, kinds)
        if undead and kinds & (POISON | DRAINING):
            pct = 0
        if pct == 0:
            immune.append(name)
        elif pct < 100:
            halved.append(name)
    notes = []
    for bit, text in sorted(PROPERTY_TEXT.items()):
        if properties & (1 << bit) and text not in notes:
            notes.append(text)
    if undead:
        notes.insert(0, "undead: mind-affecting spells, charms and holds don't work on it")
    if manual and kind == DJINN_KIND:
        notes.append(DJINN_NOTE)
    special = [(MANUAL_SPECIAL.get((kind, bit), text) if manual else text)
               for bit, text in sorted(SPECIAL_ATTACKS.items()) if properties & (1 << bit)]
    return Defences(weapon_plus, [] if weapon_plus == 4 else immune_kinds, half, immune, halved,
                    notes, special, undead)


def describe(d: Defences) -> List[str]:
    """Sentences for the Loader and the game's dialogue window."""
    out = []
    if d.weapon_plus == 4:
        out.append("Weapons can't hurt it.")
    elif d.weapon_plus:
        out.append(f"Only +{d.weapon_plus} or better weapons hurt it.")
    if d.weapons_immune:
        out.append(f"{' and '.join(d.weapons_immune).capitalize()} weapons can't hurt it.")
    if d.weapons_half:
        out.append("Half damage from non-magical weapons.")
    if d.immune:
        out.append(f"Immune to {', '.join(d.immune)}.")
    if d.half:
        out.append(f"Half damage from {', '.join(d.half)}.")
    out += [note[0].upper() + note[1:] + "." for note in d.notes]
    if d.special:
        out.append(f"Its hits also bring {', '.join(d.special)}.")
    return out


HALF_REASON = "non-magical weapons do half"


def weapon_reason(d: Defences) -> Optional[str]:
    """Why a weapon's hit may do less than its dice, if the monster's defences say (else None)."""
    if d.weapon_plus == 4:
        return "weapons can't hurt it"
    if d.weapon_plus:
        return f"only +{d.weapon_plus} or better weapons hurt it"
    if d.weapons_immune:
        return f"{' and '.join(d.weapons_immune)} weapons can't hurt it"
    if d.weapons_half:
        return HALF_REASON
    return None


def creature_defences(gd, tables: "MonsterTables", creature: int) -> Optional[Defences]:
    """A creature's defences, from its record's kind and its sheet's race (None: unreadable)."""
    rec, sheet = gd.creature(creature), gd.sheet(creature)
    if len(rec) < 0x3A or len(sheet) < 0x47:
        return None
    return tables.defences(struct.unpack_from("<H", rec, CREATURE_KIND)[0], sheet[0x18] == UNDEAD_RACE,
                           _manual(gd))


def _manual(gd) -> bool:
    """The game's copy has the monsters as the manual describes them (its spells' switch)."""
    try:
        return bool(gd.spells_manual())
    except (AttributeError, OSError, ValueError, struct.error):
        return False


def short_line(d: Defences, width: int = 15) -> str:
    """The most important defence in a few capitals, for the game's Look box."""
    if d.weapon_plus == 4:
        return "NO WEAPON HURTS"
    if d.weapon_plus:
        return f"NEEDS +{d.weapon_plus} WEAPON"
    if d.weapons_immune:
        return ("NO " + "/".join(k.upper()[:5] for k in d.weapons_immune))[:width]
    if d.immune:
        text = "IMM " + " ".join(SHORT_KINDS.get(k, k.upper()) for k in d.immune)
        return text if len(text) <= width else text[:width].rsplit(" ", 1)[0]
    if d.weapons_half:
        return "HALF FROM WPNS"
    if d.undead:
        return "UNDEAD"
    return ""


class MonsterTables:
    """The kinds table, read once from the running game (it's filled when the game starts)."""

    def __init__(self, read, load_seg: int):
        seg = struct.unpack("<H", read((load_seg + SEGMENT_TABLE) * 16 + KINDS_SELECTOR, 2))[0]
        base = (seg or load_seg + MONSTER_KINDS_SEG) * 16
        data = read(base, CLASS_MASKS_OFF + CLASS_SIZE * CLASS_COUNT)
        self.properties = list(struct.unpack_from(f"<{KIND_COUNT}I", data, KIND_PROPERTIES_OFF))
        self.classes = list(data[KIND_CLASS_OFF:KIND_CLASS_OFF + KIND_COUNT])
        self.rules: Dict[int, List[Rule]] = {}
        for c in range(1, CLASS_COUNT):
            masks = struct.unpack_from(f"<{CLASS_RULES}H", data, CLASS_MASKS_OFF + c * CLASS_SIZE)
            pcts = data[CLASS_PERCENTS_OFF + c * CLASS_SIZE:CLASS_PERCENTS_OFF + c * CLASS_SIZE + CLASS_RULES]
            self.rules[c] = [Rule(m, p) for m, p in zip(masks, pcts) if m]

    def defences(self, kind: int, undead: bool, manual: bool = False) -> Defences:
        if not 0 <= kind < KIND_COUNT:
            return defences([], 0, undead)
        return defences(self.rules.get(self.classes[kind], []), self.properties[kind], undead, kind, manual)


def monster_lines(gd, tables: MonsterTables, creature: int, ac: Optional[int]) -> Tuple[List[str], List[str]]:
    """(the Look box's three short lines, the full description) for a creature."""
    rec = gd.creature(creature)
    sheet = gd.sheet(creature)
    if len(rec) < 0x3A or len(sheet) < 0x47:
        return [], []
    hp = struct.unpack_from("<h", rec, 0)[0]
    kind = struct.unpack_from("<H", rec, CREATURE_KIND)[0]
    max_hp = struct.unpack_from("<h", sheet, 0x08)[0]
    thac0 = struct.unpack_from("b", rec, 0x1F)[0]  # (signed, as game.py reads it)
    mr = sheet[0x29]
    attacks = sheet[0x2A]
    undead = sheet[0x18] == UNDEAD_RACE
    d = tables.defences(kind, undead, _manual(gd))
    if ac is None:  # (no attack on it yet: counted as the game would, its armour and DEX)
        ac = gd.counted_ac(creature)
    ac_text = str(ac) if ac is not None else str(struct.unpack_from("b", sheet, 0x27)[0])
    alignment = ALIGNMENTS.get(sheet[SHEET_ALIGNMENT])
    # magic resistance beside the game's LEVEL; the alignment after THAC0 where it fits (the
    # description always has it); a line squeezed when it would run past the box's edge
    second = f"THAC0 {thac0}"
    if alignment and look_pixels(f"{second} AL {alignment[0]}") <= LOOK_PIXELS:
        second += f" AL {alignment[0]}"
    first = look_fit(f"HP {hp}/{max_hp} AC {ac_text}", f"HP{hp}/{max_hp} AC{ac_text}")
    short = [first, second]
    if mr:
        side = f"MR {mr}" if look_pixels(f"MR {mr}") <= SIDE_PIXELS else f"MR{mr}"
        short.insert(0, LOOK_SIDE + side)
    line = short_line(d)
    if line:
        short.append(line)
    per_round = f"{attacks // 2}" if attacks % 2 == 0 else f"{attacks}/2"  # the sheet keeps it doubled
    head = f"{gd.creature_name(creature)}: HP {hp}/{max_hp}, AC {ac_text}, THAC0 {thac0}"
    if attacks:  # monsters' sheets leave it 0: their attacks come from elsewhere
        head += f", {per_round} attack{'s' if attacks != 2 else ''} a round"
    full = [head + (f", magic resistance {mr}%" if mr else "") + (f", {alignment[1]}" if alignment else "") + "."]
    full += describe(d)
    return short, full


# The monsters the manual describes otherwise, given a kind of their own (kinds 38-40: no creature of
# the game's has one; gamepatch's "styr_kind", "djinn_kind", "tari_kind") and the manual's numbers where
# its record differs (Styr p. 51: HD 14, THAC0 7; Tari p. 52: HD 3, THAC0 17, AC 6, a bite of 1d3): by
# name and race, each field (where, the game's, the manual's): "c" the creature record's offset, "s" the
# sheet's (natural attacks at +2Bh: counts, dice, sides, bonuses, three of each)
class Manual(NamedTuple):
    name: bytes
    race: int
    objects: Tuple[int, ...]  # (its SEGOBJEX records)
    fields: Tuple[Tuple[str, int, int, int], ...]


MANUAL_MONSTERS = (
    Manual(b"Styr", 12, (99,), (("c", CREATURE_KIND, 0, STYR_KIND), ("c", 0x1F, 11, 7), ("s", 0x24, 10, 14))),
    Manual(b"Djinn", 14, (122,), (("c", CREATURE_KIND, 0, DJINN_KIND),)),
    Manual(b"Tari", 1, (60, 65, 243), (("c", CREATURE_KIND, 0, TARI_KIND), ("c", 0x1F, 18, 17), ("s", 0x24, 2, 3),
                                         ("s", 0x27, 10, 6), ("s", 0x31, 2, 3))),
)
RDFF_CREATURE, RDFF_SHEET = 0x0A, 0x4E  # (an object's RDFF record: its creature record, then its sheet's)
RDFF_SIZES = ((0x08, game.CREATURE_SIZE), (0x4C, game.SHEET_SIZE))  # (each part's size word before it)


def _set(record: bytearray, at: int, value: int, size: int) -> None:
    if size == 2:
        struct.pack_into("<H", record, at, value & 0xFFFF)
    else:
        record[at] = value & 0xFF


def _get(record: bytes, at: int, size: int) -> int:
    return struct.unpack_from("<H", record, at)[0] if size == 2 else record[at]


def _size(at: int) -> int:
    return 2 if at == CREATURE_KIND else 1


def object_chunks(chunks) -> Dict[Tuple[str, int], bytes]:
    """For the Loader's copy of SEGOBJEX with the monsters as the manual describes them: MANUAL_MONSTERS'
    records (in CHUNKS) with their kinds and the manual's numbers, each only if it is the game's own."""
    out: Dict[Tuple[str, int], bytes] = {}
    for m in MANUAL_MONSTERS:
        for number in m.objects:
            rec = chunks.get(("RDFF", number))
            if rec is None or len(rec) < RDFF_SHEET + game.SHEET_SIZE \
                    or any(struct.unpack_from("<H", rec, at)[0] != size for at, size in RDFF_SIZES):
                continue
            if rec[RDFF_CREATURE + game.CREATURE_NAME:].split(b"\0", 1)[0] != m.name \
                    or rec[RDFF_SHEET + game.SHEET_RACE] != m.race:
                continue
            base = {"c": RDFF_CREATURE, "s": RDFF_SHEET}
            if any(_get(rec, base[part] + at, _size(at)) != old for part, at, old, _ in m.fields):
                continue
            new = bytearray(rec)
            for part, at, _, value in m.fields:
                _set(new, base[part] + at, value, _size(at))
            out[("RDFF", number)] = bytes(new)
    return out


def mend(gd, manual: bool) -> List[str]:
    """MANUAL_MONSTERS in the running game (a saved game's, or one begun before the switch) made as the
    Loader's copy of SEGOBJEX has them with MANUAL, or as the game's without it: each creature on the
    map by name and race with every field one way, its other way written."""
    out: List[str] = []
    combatants = gd.combatants()
    creatures = game.far_pointer(gd.guest, gd.ds, game.CREATURES_PTR)
    sheets = game.far_pointer(gd.guest, gd.ds, game.SHEETS_PTR)
    indices = sorted(i for i in set(combatants.values()) if i >= game.PARTY_SIZE)
    table = gd.creatures(indices[-1] + 1) if indices else b""
    for index in indices:
        rec = table[index * game.CREATURE_SIZE:(index + 1) * game.CREATURE_SIZE]
        if len(rec) < game.CREATURE_SIZE:
            continue
        name = rec[game.CREATURE_NAME:game.CREATURE_NAME + 16].split(b"\0", 1)[0]
        m = next((m for m in MANUAL_MONSTERS if m.name == name), None)
        if m is None:
            continue
        sheet_index = struct.unpack_from("<H", rec, game.CREATURE_SHEET_INDEX)[0]
        sheet = gd.guest.read(sheets + sheet_index * game.SHEET_SIZE, game.SHEET_SIZE)
        if len(sheet) < game.SHEET_SIZE or sheet[game.SHEET_RACE] != m.race:
            continue
        parts = {"c": (rec, creatures + index * game.CREATURE_SIZE), "s": (sheet, sheets + sheet_index * game.SHEET_SIZE)}
        have = [_get(parts[part][0], at, _size(at)) for part, at, _, _ in m.fields]
        old, new = [f[2] for f in m.fields], [f[3] for f in m.fields]
        want = new if manual else old
        if have == want or have != (old if manual else new):
            continue
        for (part, at, _, _), value in zip(m.fields, want):
            data, address = parts[part]
            size = _size(at)
            gd.guest.write(address + at, struct.pack("<H", value) if size == 2 else bytes((value,)))
        out.append(f"({gd.creature_name(index)}: as the manual describes it)" if manual else
                   f"({gd.creature_name(index)}: as the game has it)")
    return out
