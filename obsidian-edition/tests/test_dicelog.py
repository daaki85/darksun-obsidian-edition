"""Decoding dice log entries into text, against a fake game memory."""

import os
import struct
import sys
import unittest
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import tracker as tracker_module
from dsloader import dicelog, game, names
from dsloader.dicelog import AcDetail, DiceLog, Entry, KIND_AC, KIND_ROLL, KIND_SAVE
from dsloader.textlog import KIND_MESSAGE, KIND_PORTRAIT, KIND_TEXT, DialogueEntry, TextBuffer
from dsloader.tracker import PartyTracker

LOAD_SEG = 0x1A2
DS = LOAD_SEG + game.DGROUP
CREATURES, SHEETS, ITEMS, ITEM_TYPES, NAMES = 0x71000, 0x70000, 0x6E000, 0x6D000, 0x72600
TSR_SEG, HDR = 0xD000, 0xD0000
STALKER = 7
FIREBALL, HOLD_PERSON = 27, 30


class FakeGuest:
    def __init__(self):
        self.mem = bytearray(0x110000)
        self.size = len(self.mem)

    def read(self, addr, size):
        return bytes(self.mem[addr:addr + size])

    def write(self, addr, data):
        self.mem[addr:addr + len(data)] = data


def far(addr):
    return struct.pack("<HH", addr & 0xF, addr >> 4)


def make_game():
    guest = FakeGuest()
    m = guest.mem
    for offset, addr in ((game.CREATURES_PTR, CREATURES), (game.SHEETS_PTR, SHEETS),
                         (game.ITEMS_PTR, ITEMS), (game.ITEM_TYPES_PTR, ITEM_TYPES),
                         (game.ITEM_NAMES_PTR, NAMES + 3)):
        m[DS * 16 + offset:DS * 16 + offset + 4] = far(addr)
    struct.pack_into("<h", m, DS * 16 + game.DIFFICULTY, 1)
    creatures = [("Dag", 16, 24, 1), ("Daaki", 16, 20, 1), ("Jellybelly", 15, 20, 1)] + [("", 20, 12, 0)] * 4 \
        + [("Mountain Stalker", 11, 12, 2)]
    for index, (name, thac0, strength, side) in enumerate(creatures):
        rec = CREATURES + index * game.CREATURE_SIZE
        struct.pack_into("<H", m, rec + game.CREATURE_SHEET_INDEX, index)
        m[rec + game.CREATURE_THAC0] = thac0
        m[rec + game.CREATURE_SIDE] = side
        m[rec + game.CREATURE_ABILITIES] = strength
        m[rec + game.CREATURE_NAME:rec + game.CREATURE_NAME + len(name)] = name.encode()
    table = (LOAD_SEG + game.COMBATANTS_SEG) * 16 + game.COMBATANTS_OFF
    for combatant, creature in ((0, 0), (1, 1), (2, 2), (0x29, STALKER)):
        struct.pack_into("<Bh", m, table + combatant * 3, 2, creature)
    # item names (GPLDATA's NAME list: 25 bytes each)
    for i, name in enumerate(["Sling", "Staff Sling"] + ["x"] * 26 + ["Long Sword"]):
        m[NAMES + i * 25 + 3:NAMES + i * 25 + 3 + len(name)] = name.encode()
    # items 5 (metal long sword +1) and 6 (wooden long sword, plain); item type 9 = 1d8
    for item, plus, item_type in ((5, 1, 9), (6, 0, 10)):
        rec = ITEMS + item * game.ITEM_SIZE
        struct.pack_into("<H", m, rec + 0x0A, item_type)
        m[rec + 0x12], m[rec + 0x14] = 28, plus
    for item_type, material in ((9, 4), (10, 0)):
        typ = ITEM_TYPES + item_type * game.ITEM_TYPE_SIZE
        m[typ + 0x08], m[typ + 0x0C], m[typ + 0x0D] = material, 8, 1
    # spells: names, and the rules the saving throw reads (Fireball doubles the d20)
    name = game.SPELL_NAMES
    for spell, text, flags in ((FIREBALL, b"FIREBALL", 0x0202), (HOLD_PERSON, b"HOLD PERSON", 0)):
        m[DS * 16 + name:DS * 16 + name + len(text)] = text
        info = LOAD_SEG * 16 + game.SPELL_INFO_OFF + (spell - 1) * game.SPELL_INFO_SIZE
        struct.pack_into("<BxxxxH", m, info, 3, name)
        rules = (LOAD_SEG + game.SPELLS_SEG) * 16 + game.SPELLS_OFF + spell * game.SPELL_SIZE
        struct.pack_into("<H", m, rules + 0x0A, flags)
        name += len(text) + 1
    # character sheets: Dag a half-giant fighter (CON 21), the stalker worth 500 XP
    for index, race, cls, level, con, base_ac in ((0, 5, 9, 4, 21, 10), (STALKER, 0, 0, 0, 12, 10)):
        sheet = SHEETS + index * game.SHEET_SIZE
        m[sheet + game.SHEET_RACE], m[sheet + game.SHEET_ABILITIES + 2] = race, con
        m[sheet + game.SHEET_CLASSES], m[sheet + game.SHEET_LEVELS] = cls, level
        m[sheet + game.SHEET_BASE_AC] = base_ac
    struct.pack_into("<I", m, SHEETS + STALKER * game.SHEET_SIZE + game.SHEET_XP_VALUE, 500)
    m[CREATURES + STALKER * game.CREATURE_SIZE + game.CREATURE_ABILITIES + 1] = 16  # DEX
    m[DS * 16 + game.DEX_AC + 16] = 0xFE  # DEX 16: AC -2
    hp = (LOAD_SEG + game.LEVEL_HP_SEG) * 16  # fighters roll d10 up to level 9; CON 21: at least 3
    m[hp + 0x10 + 9], m[hp + 4:hp + 7], m[hp + 0x38 + 21] = 1, bytes((10, 9, 3)), 3
    # DSCLOG's text buffer
    struct.pack_into("<HHHH", m, HDR + 126, 0, 0x800, 256, 0)
    # DSCLOG's names after the game's own, in the table it noted
    m[HDR + names.TSR_NAMES_PTR:HDR + names.TSR_NAMES_PTR + 4] = far(NAMES + 3)
    for entry, name in names.NAMES.items():
        m[NAMES + 3 + entry * 25:NAMES + 3 + entry * 25 + len(name)] = name
    log = DiceLog(guest)
    log.rand_addr = LOAD_SEG * 16 + dicelog.RAND_IP
    log.tsr_hdr = HDR
    log.last_seq = 0
    log.game = game.GameData(guest, DS)
    log.tracker = PartyTracker(log.game)
    log.text = TextBuffer(guest.read, HDR)
    return log


def set_effects(log, effects):
    m = log.guest.mem
    struct.pack_into("<h", m, DS * 16 + game.EFFECT_COUNT, len(effects))
    base = (LOAD_SEG + game.EFFECTS_SEG) * 16 + game.EFFECTS_OFF
    for i, (owner, caster, eid) in enumerate(effects):
        struct.pack_into("<hhhB", m, base + i * 10, owner, caster, 0, eid)


def words(*values):
    return struct.pack(f"<{len(values)}h", *values)


def entry(raw=0, code=b"", frame=b"", parent=b"", glob=(0, 0, 0, 0), locals_=b"", parent_code=b"",
          parent_locals=b"", kind=KIND_ROLL, bp=0xFE00, parent_bp=0xFE40):
    data = bytearray(Entry.SIZE)
    struct.pack_into("<8H", data, 0, 1, 0x10, 0x5000, raw & 0xFFFF, bp, DS, DS, parent_bp)
    data[16:16 + len(frame)] = frame
    data[48:48 + len(parent)] = parent
    struct.pack_into("<4H", data, 80, *glob)
    data[88:88 + len(locals_)] = locals_
    data[104:104 + len(code)] = code
    data[128:128 + len(parent_code)] = parent_code
    data[144:144 + len(parent_locals)] = parent_locals
    struct.pack_into("<H", data, 184, kind)
    return Entry.parse(bytes(data))


def locals_at(size, **at):
    """`size` bytes of locals ending at BP, with words at the given negative offsets (e.g. m20=9 for [bp-20h])."""
    data = bytearray(size)
    for name, value in at.items():
        struct.pack_into("<h", data, size - int(name[1:], 16), value)
    return bytes(data)


def raw_for(face, sides):
    """A rand() result that gives `face` (1-based) on a die with `sides` sides."""
    return (face - 1) * 0x8000 // sides + 1


def two_hands(m):
    """Dag's items 5 (type 9) and 6 (type 11) as melee weapons (class 1), the long sword in
    the right hand and item 6 in the left."""
    for typ in (9, 11):
        m[ITEM_TYPES + typ * game.ITEM_TYPE_SIZE + 0x0A] = 1
    m[ITEMS + 5 * game.ITEM_SIZE + game.ITEM_SLOT] = 3
    m[ITEMS + 6 * game.ITEM_SIZE + game.ITEM_SLOT] = 10
    struct.pack_into("<H", m, ITEMS + 6 * game.ITEM_SIZE + game.ITEM_TYPE, 11)
    # in Dag's first list (object 400): item 5, then 6
    things = (LOAD_SEG + game.COMBATANTS_SEG) * 16 + game.COMBATANTS_OFF
    struct.pack_into("<Bh", m, things + 400 * 3, game.THING_ITEM, 5)
    struct.pack_into("<h", m, CREATURES + 8, 400)
    struct.pack_into("<h", m, ITEMS + 5 * game.ITEM_SIZE + game.ITEM_NEXT, 6)
    struct.pack_into("<H", m, ITEMS + 6 * game.ITEM_SIZE + game.ITEM_NEXT, game.NO_ITEM)


class AttackTests(unittest.TestCase):
    def attack(self, d20, thac0, ac, item, item_type, after_f1, hit_bonus, attacker=0, combatant=0, **flags):
        # attack(): [BP+6] dword, THAC0, AC, attacker, sheet, item, item type, mode 1, attacker combatant,
        # two more, backstab, from behind
        frame = words(0, 0, 0, 0, thac0, ac, attacker, 0, item, item_type, 1, combatant, 0, 0,
                      1 if flags.get("m24") else 0, 1 if flags.get("m1a") else 0)
        parent_locals = locals_at(0x28, m20=after_f1, m8=hit_bonus, **flags)
        return entry(raw_for(d20, 20), dicelog.ATTACK_SITE, frame, glob=(0x29, 0, 0, 0), parent_locals=parent_locals)

    def test_attack_with_weapon_and_breakdown(self):
        log = make_game()
        set_effects(log, [(0, 2, 7)])  # Dag is Blessed
        lines = log.describe(self.attack(18, 8, 4, 5, 9, after_f1=9, hit_bonus=1))
        self.assertEqual(lines, [
            "Dag attacks Mountain Stalker with Long Sword +1 (1d8+1): d20 = 18, needs 4+ (85%), hits AC -10, target AC 4 -> HIT",
            "    THAC0 16, +1 Blessed, +6 STR, +1 weapon = 8"])
        self.assertEqual(log.last_ac, {STALKER: 4})  # the target's AC, for the viewer

    def test_material_penalty_rear_attack_and_miss(self):
        log = make_game()
        # base 16 - 2 (rear) - 6 (STR) = 8; wooden -3 -> 11
        lines = log.describe(self.attack(5, 11, 2, 6, 10, after_f1=8, hit_bonus=-3, m1a=1))
        self.assertEqual(lines, [
            "Dag attacks Mountain Stalker from behind with Wooden Long Sword (1d8): d20 = 5, needs 9+ (60%), hits AC 6, target AC 2 -> miss",
            "    THAC0 16, +2 from behind, +6 STR, -3 wooden = 11"])

    def test_miss_floats_over_the_target(self):
        """A miss floats "Miss" over its target (labels.py); a hit floats nothing."""
        log = make_game()
        floated = []
        log._float = lambda thing, text, colour, now: floated.append((thing, text))
        log.describe(self.attack(5, 11, 2, 6, 10, after_f1=8, hit_bonus=-3, m1a=1))
        log.describe(self.attack(18, 8, 4, 5, 9, after_f1=9, hit_bonus=1))
        self.assertEqual(floated, [(0x29, "Miss")])

    def test_backstab_is_named(self):
        log = make_game()
        lines = log.describe(self.attack(12, 11, 4, 6, 10, after_f1=8, hit_bonus=-3, m1a=1, m24=1))
        self.assertTrue(lines[0].startswith("Dag attacks Mountain Stalker BACKSTAB with Wooden Long Sword"))
        self.assertEqual(lines[1], "    THAC0 16, +2 from behind, +2 backstab, +4 STR, -3 wooden = 11")

    def test_girdle_of_urnst(self):
        """A sword's attack on a target wearing the Golden Girdle of Urnst: its 3 in the THAC0 line
        (DSCLOG's ITEM_REAR), not a club's."""
        from dsloader import specialize
        log = make_game()
        log.game.wears_type = lambda creature, item_type, slot: item_type == game.URNST_GIRDLE_TYPE
        sword = next(t for t, k in specialize.KIND_OF_TYPE.items() if k == specialize.KINDS.index("long sword"))
        club = next(t for t, k in specialize.KIND_OF_TYPE.items() if k == specialize.KINDS.index("club"))
        lines = log.describe(self.attack(18, 12, 4, 5, sword, after_f1=13, hit_bonus=1))
        self.assertEqual(lines[1], "    THAC0 16, -3 target's Girdle of Urnst, +6 STR, +1 weapon = 12")
        lines = log.describe(self.attack(18, 9, 4, 5, club, after_f1=10, hit_bonus=1))
        self.assertNotIn("Urnst", lines[1])

    def test_two_weapons(self):
        log = make_game()
        m = log.guest.mem
        dex = CREATURES + game.CREATURE_ABILITIES + 1
        # DEX 15 with two weapons ready: nothing changes
        m[dex] = 15
        lines = log.describe(self.attack(18, 9, 4, 5, 9, after_f1=10, hit_bonus=1, m16=2))
        self.assertEqual(lines[1], "    THAC0 16, +6 STR, +1 weapon = 9")
        # DEX 4: the game's table gives -2, which it turns into +2
        m[dex], m[DS * 16 + game.DEX_INITIATIVE + 4] = 4, 0xFE
        lines = log.describe(self.attack(18, 7, 4, 5, 9, after_f1=10, hit_bonus=3, m16=2))
        self.assertEqual(lines[1], "    THAC0 16, +6 STR, +1 weapon, +2 two weapons at DEX 4 = 7")
        # a ranger gets nothing either way (the rest shows as unexplained)
        struct.pack_into("<H", m, SHEETS + game.SHEET_FLAGS, game.SHEET_FLAG_RANGER)
        lines = log.describe(self.attack(18, 9, 4, 5, 9, after_f1=10, hit_bonus=1, m16=2))
        self.assertEqual(lines[1], "    THAC0 16, +6 STR, +1 weapon = 9")

    def test_two_weapons_adnd(self):
        """With the Loader's rule: -2 main hand, -4 off hand, the DEX reaction adjustment
        (the game's initiative table) added, never above 0."""
        log = make_game()
        log.set_rules(game.RULE_TWO_WEAPONS)
        self.addCleanup(setattr, game, "RULES_IN_FORCE", 0)
        m = log.guest.mem
        dex = CREATURES + game.CREATURE_ABILITIES + 1
        m[dex], m[DS * 16 + game.DEX_INITIATIVE + 17] = 17, 2
        two_hands(m)
        m[ITEMS + 5 * game.ITEM_SIZE + game.ITEM_SLOT] = 3  # the right hand: no penalty at DEX 17
        lines = log.describe(self.attack(18, 9, 4, 5, 9, after_f1=10, hit_bonus=1, m16=2))
        self.assertEqual(lines[1], "    THAC0 16, +6 STR, +1 weapon = 9")
        m[ITEMS + 5 * game.ITEM_SIZE + game.ITEM_SLOT] = 10  # the left hand: -4 + 2
        m[ITEMS + 6 * game.ITEM_SIZE + game.ITEM_SLOT] = 3
        lines = log.describe(self.attack(18, 11, 4, 5, 9, after_f1=10, hit_bonus=-1, m16=2))
        self.assertEqual(lines[1], "    THAC0 16, +6 STR, +1 weapon, -2 two weapons, off hand at DEX 17 = 11")
        m[dex], m[DS * 16 + game.DEX_INITIATIVE + 4] = 4, 0xFE  # DEX 4: -2 makes it worse
        lines = log.describe(self.attack(18, 15, 4, 5, 9, after_f1=10, hit_bonus=-5, m16=2))
        self.assertEqual(lines[1], "    THAC0 16, +6 STR, +1 weapon, -6 two weapons, off hand at DEX 4 = 15")
        # a shield in the other hand: no penalty (whatever the game's count said)
        m[ITEMS + 5 * game.ITEM_SIZE + game.ITEM_SLOT] = 3
        m[ITEMS + 6 * game.ITEM_SIZE + game.ITEM_SLOT] = 10
        m[ITEM_TYPES + 11 * game.ITEM_TYPE_SIZE + 0x0A] = 0
        lines = log.describe(self.attack(18, 9, 4, 5, 9, after_f1=10, hit_bonus=1, m16=2))
        self.assertEqual(lines[1], "    THAC0 16, +6 STR, +1 weapon = 9")

    def test_two_weapons_ranger_light_armour(self):
        """With the rule a ranger has no penalty only in light armour (DSCLOG's RG_TWO): a metal
        chest piece (item 7, type 12) brings AD&D's; leather takes it away again."""
        log = make_game()
        log.set_rules(game.RULE_TWO_WEAPONS)
        self.addCleanup(setattr, game, "RULES_IN_FORCE", 0)
        m = log.guest.mem
        dex = CREATURES + game.CREATURE_ABILITIES + 1
        m[dex], m[DS * 16 + game.DEX_INITIATIVE + 17] = 17, 2
        two_hands(m)
        struct.pack_into("<H", m, SHEETS + game.SHEET_FLAGS, game.SHEET_FLAG_RANGER)
        struct.pack_into("<h", m, ITEMS + 6 * game.ITEM_SIZE + game.ITEM_NEXT, 7)
        struct.pack_into("<H", m, ITEMS + 7 * game.ITEM_SIZE + game.ITEM_TYPE, 12)
        struct.pack_into("<H", m, ITEMS + 7 * game.ITEM_SIZE + game.ITEM_NEXT, game.NO_ITEM)
        m[ITEMS + 7 * game.ITEM_SIZE + game.ITEM_SLOT] = game.EQUIP_SLOTS.index("chest")
        typ = ITEM_TYPES + 12 * game.ITEM_TYPE_SIZE
        m[typ + 0x0F], m[typ], m[typ + 9] = 0x80, 0, game.EQUIP_SLOTS.index("chest")
        m[ITEMS + 5 * game.ITEM_SIZE + game.ITEM_SLOT] = 10  # the left hand
        m[ITEMS + 6 * game.ITEM_SIZE + game.ITEM_SLOT] = 3
        for material, thac0, bonus, want in (
                (4, 11, -1, "    THAC0 16, +6 STR, +1 weapon, -2 two weapons, off hand at DEX 17 = 11"),
                (5, 9, 1, "    THAC0 16, +6 STR, +1 weapon = 9"),
                (0x40, 9, 1, "    THAC0 16, +6 STR, +1 weapon = 9")):
            with self.subTest(material=material):
                m[typ + 8] = material
                lines = log.describe(self.attack(18, thac0, 4, 5, 9, after_f1=10, hit_bonus=bonus, m16=2))
                self.assertEqual(lines[1], want)
        # a Justifier (the ranger's second kit, kits on) in metal: none still
        m[typ + 8] = 4
        log.set_rules(game.RULE_TWO_WEAPONS | game.RULE_KITS)
        m[SHEETS + game.SHEET_CLASSES], m[SHEETS + 0x43] = 13, 2
        lines = log.describe(self.attack(18, 9, 4, 5, 9, after_f1=10, hit_bonus=1, m16=2))
        self.assertEqual(lines[1], "    THAC0 16, +6 STR, +1 weapon = 9")
        self.assertEqual(log.game.two_weapons(0, 10), ("two weapons, off hand (Justifier)", 0))

    def test_monster_natural_attack(self):
        log = make_game()
        lines = log.describe(self.attack(20, 11, 1, -1, -1, after_f1=11, hit_bonus=0, attacker=STALKER,
                                         combatant=0x29))
        self.assertEqual(lines[0], "Mountain Stalker attacks Mountain Stalker: d20 = 20 (natural 20), needs 10+ (55%), "
                                   "hits AC -9, target AC 1 -> HIT")
        self.assertEqual(lines[1], "    THAC0 11 = 11")

    def test_weapon_damage(self):
        log = make_game()
        parent = words(0, 0, 0, 0, 10, 4, 0, 0, 0, 0, 1)  # the attack's frame: ... [BP+0Eh] attacker, [BP+16h] mode
        dice = [entry(raw_for(face, 8), dicelog.DICE_SITE, words(0, 0, 2, 8, 1), parent, (0x29, 0, 0, 0),
                      parent_code=dicelog.WEAPON_DAMAGE_RETURN) for face in (2, 5)]
        self.assertEqual(log.describe(dice[0]), [])  # waits for the second die
        self.assertEqual(log.describe(dice[1]),
                         ["  Dag hits Mountain Stalker for 20: 2d8 = [2 + 5] +1 weapon +12 STR 24"])

    def test_look_box_describes_the_monster(self):
        log = make_game()
        m = log.guest.mem
        from dsloader import monsters
        stalker = CREATURES + STALKER * game.CREATURE_SIZE
        struct.pack_into("<hH", m, stalker, 38, STALKER)  # 38 HP now
        struct.pack_into("<H", m, stalker + monsters.CREATURE_KIND, 3)
        sheet = SHEETS + STALKER * game.SHEET_SIZE
        struct.pack_into("<h", m, sheet + game.SHEET_MAX_HP, 60)
        m[sheet + game.SHEET_MAGIC_RESISTANCE] = 30
        m[sheet + monsters.SHEET_ALIGNMENT] = 9  # chaotic evil
        kinds = (LOAD_SEG + monsters.MONSTER_KINDS_SEG) * 16  # kind 3: resistance class 11
        m[kinds + monsters.KIND_CLASS_OFF + 3] = 11
        struct.pack_into("<2H", m, kinds + monsters.CLASS_MASKS_OFF + 11 * monsters.CLASS_SIZE, 0x38, 0xB200)
        m[kinds + monsters.CLASS_PERCENTS_OFF + 11 * monsters.CLASS_SIZE + 1] = 100
        log.last_ac[STALKER], log._ac_whose[STALKER] = 4, "Mountain Stalker"
        struct.pack_into("<H", m, HDR + dicelog.TSR_HDR_OFF, 0)
        struct.pack_into("<HH", m, HDR + dicelog.TSR_LOOK_OFF, 0x300, 0x500)
        log.set_monster_info(True)
        self.assertEqual(struct.unpack_from("<H", m, HDR + dicelog.TSR_LOOK_ON)[0], 1)
        struct.pack_into("<HH", m, HDR + dicelog.TSR_LOOK_SEQ, 1, 0)
        struct.pack_into("<H", m, HDR + dicelog.TSR_LOOK_WHO, 0x29)
        lines = log._answer_look()
        self.assertEqual(struct.unpack_from("<H", m, HDR + dicelog.TSR_LOOK_REPLY)[0], 1)
        self.assertEqual(bytes(m[HDR + 0x300:HDR + 0x340]).split(b"\0")[0],
                         b"\x01MR 30|HP 38/60 AC 4|THAC0 11 AL CE|NEEDS +1 WEAPON")
        whole = bytes(m[HDR + 0x500:HDR + 0x600]).split(b"\0")[0].decode()
        self.assertIn("magic resistance 30 pct", whole)
        self.assertIn("Only +1 or better weapons hurt it.", whole)
        self.assertEqual(lines[0], "Look: Mountain Stalker: HP 38/60, AC 4, THAC0 11, magic resistance 30%, "
                                   "chaotic evil.")
        self.assertEqual(log._answer_look(), [])  # asked once
        # nothing special about it: the box's lines, but no window
        m[kinds + monsters.KIND_CLASS_OFF + 3] = 0
        struct.pack_into("<HH", m, HDR + dicelog.TSR_LOOK_SEQ, 5, 4)
        struct.pack_into("<H", m, HDR + dicelog.TSR_LOOK_WHO, 0x29)
        log._look_seq = 4
        self.assertEqual(len(log._answer_look()), 1)
        self.assertEqual(bytes(m[HDR + 0x300:HDR + 0x340]).split(b"\0")[0], b"\x01MR 30|HP 38/60 AC 4|THAC0 11 AL CE")
        self.assertEqual(m[HDR + 0x500], 0)
        # no magic resistance: nothing beside LEVEL
        m[sheet + game.SHEET_MAGIC_RESISTANCE] = 0
        struct.pack_into("<HH", m, HDR + dicelog.TSR_LOOK_SEQ, 6, 5)
        log._look_seq = 5
        self.assertEqual(log._answer_look(), ["Look: Mountain Stalker: HP 38/60, AC 4, THAC0 11, chaotic evil."])
        self.assertEqual(bytes(m[HDR + 0x300:HDR + 0x340]).split(b"\0")[0], b"HP 38/60 AC 4|THAC0 11 AL CE")
        m[sheet + monsters.SHEET_ALIGNMENT] = 0  # (none set: nothing said)
        struct.pack_into("<HH", m, HDR + dicelog.TSR_LOOK_SEQ, 7, 6)
        log._look_seq = 6
        log._answer_look()
        self.assertEqual(bytes(m[HDR + 0x300:HDR + 0x340]).split(b"\0")[0], b"HP 38/60 AC 4|THAC0 11")
        # an AC worked out for another creature in the record (an earlier fight's): the sheet's
        log._ac_whose[STALKER] = "Defiler"
        struct.pack_into("<HH", m, HDR + dicelog.TSR_LOOK_SEQ, 8, 7)
        log._look_seq = 7
        self.assertEqual(log._answer_look()[0][:41], "Look: Mountain Stalker: HP 38/60, AC 10, ")
        # a party member: nothing to add (the game shows the View Character screen)
        struct.pack_into("<HH", m, HDR + dicelog.TSR_LOOK_SEQ, 2, 1)
        struct.pack_into("<H", m, HDR + dicelog.TSR_LOOK_WHO, 0)
        self.assertEqual(log._answer_look(), [])
        self.assertEqual(struct.unpack_from("<H", m, HDR + dicelog.TSR_LOOK_REPLY)[0], 2)
        self.assertEqual(m[HDR + 0x300], 0)


class SlotsForTheGameTests(unittest.TestCase):
    def test_slot_lines(self):
        """For each kind of spells a heading, then each spell level's slots, each line keyed by
        the list and level (DSCLOG shows the ones the USE screen is on)."""
        log = make_game()
        key = lambda lst, level: chr(dicelog.SLOT_KEY | lst << 4 | level)
        log.game.spell_slots = lambda member: {
            0: [("Wizard", [(1, 2, 2), (2, 1, 1)]), ("Priest", [(1, 5, 8), (6, 2, 1)])]}.get(member, [])
        self.assertEqual(log.slots_lines(0).split("|"),
                         [key(1, 0) + "SPELLS LEFT", key(1, 1) + "WIZ 2/2", key(1, 2) + "WIZ 1/1",
                          key(2, 0) + "SPELLS LEFT", key(2, 1) + "PRI 5/8", key(2, 6) + "PRI 2/1"])
        self.assertEqual(log.slots_lines(1), "")
        # a multiclass preserver in armour: no wizard spells, its priest spells as ever
        log.game.no_spells = lambda member: True
        lines = log.slots_lines(0).split("|")
        self.assertEqual((lines[0], lines[3]), (key(1, 0) + "NO SPELLS IN ARMOUR", key(2, 0) + "SPELLS LEFT"))
        # the longest a member can have (a cleric/preserver: six priest levels, five wizard) fits
        log.game.no_spells = lambda member: False
        log.game.spell_slots = lambda member: [("Wizard", [(n, 9, 9) for n in range(1, 6)]),
                                               ("Priest", [(n, 9, 9) for n in range(1, 7)])]
        self.assertLess(len(log.slots_lines(0)), dicelog.SLOTS_SIZE)


class BackstabTests(unittest.TestCase):
    def test_backstab_multiplies_the_damage(self):
        log = make_game()
        sheet = SHEETS + 0 * game.SHEET_SIZE  # make Dag a 6th level thief
        log.guest.mem[sheet + game.SHEET_CLASSES + 1], log.guest.mem[sheet + game.SHEET_LEVELS + 1] = 17, 6
        # the attack's frame: ... [BP+16h] melee, [BP+1Eh] backstab, [BP+20h] from behind;
        # [BP-0Ah] attacks made this round
        parent = words(0, 0, 0, 0, 10, 4, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1)
        e = entry(raw_for(5, 8), dicelog.DICE_SITE, words(0, 0, 1, 8, 0), parent, (0x29, 0, 0, 0),
                  parent_code=dicelog.WEAPON_DAMAGE_RETURN, parent_locals=locals_at(0x28, ma=1))
        self.assertEqual(log.describe(e), ["  Dag hits Mountain Stalker for 51: (1d8 = [5] +12 STR 24) x3 backstab"])

    def test_enlarge_before_the_backstab(self):
        log = make_game()
        sheet = SHEETS + 0 * game.SHEET_SIZE
        log.guest.mem[sheet + game.SHEET_CLASSES + 1], log.guest.mem[sheet + game.SHEET_LEVELS + 1] = 17, 6
        # Dag (combatant 0, [BP+18h]) under two Enlarges, cast at levels 3 and 1 (one on someone else)
        log.game.effect_spells = lambda: [(game.Effect(0, 5, game.ENLARGE_EFFECT), 30),
                                          (game.Effect(0, 6, game.ENLARGE_EFFECT), 30),
                                          (game.Effect(7, 5, game.ENLARGE_EFFECT), 30),
                                          (game.Effect(0, 5, game.MIRROR_EFFECT), 31)]
        creature_of = log.game.combatant_creature
        log.game.combatant_creature = lambda combatant: combatant if combatant in (5, 6) else creature_of(combatant)
        log.game.effect_caster_level = lambda creature, spell: {5: 3, 6: 1}[creature]
        parent = words(0, 0, 0, 0, 10, 4, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1)
        e = entry(raw_for(5, 8), dicelog.DICE_SITE, words(0, 0, 1, 8, 0), parent, (0x29, 0, 0, 0),
                  parent_code=dicelog.WEAPON_DAMAGE_RETURN, parent_locals=locals_at(0x28, ma=1))
        # (5 + 12) x 140% = 23.8, rounded down; then x3
        self.assertEqual(log.describe(e), ["  Dag hits Mountain Stalker for 69: ((1d8 = [5] +12 STR 24) x140% Enlarge "
                                           "(level 4)) x3 backstab"])

    def backstab(self, level, rules):
        log = make_game()
        log.rules = rules
        sheet = SHEETS + 0 * game.SHEET_SIZE
        log.guest.mem[sheet + game.SHEET_CLASSES + 1], log.guest.mem[sheet + game.SHEET_LEVELS + 1] = 17, level
        parent = words(0, 0, 0, 0, 10, 4, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1)
        e = entry(raw_for(5, 8), dicelog.DICE_SITE, words(0, 0, 1, 8, 0), parent, (0x29, 0, 0, 0),
                  parent_code=dicelog.WEAPON_DAMAGE_RETURN, parent_locals=locals_at(0x28, ma=1))
        return log.describe(e)

    def test_dice_only(self):
        """RULE_BACKSTAB (DSCLOG's STAB_TIMES): the dice multiplied, STR added once."""
        self.assertEqual(self.backstab(6, game.RULE_BACKSTAB),
                         ["  Dag hits Mountain Stalker for 27: 1d8 = [5] +12 STR 24 +10 backstab (the dice x3)"])

    def test_times_by_level(self):
        """x4 at thief levels 9 to 12, x5 from 13 (the game's 595C4h, as AD&D's table)."""
        self.assertIn("+15 backstab (the dice x4)", self.backstab(12, game.RULE_BACKSTAB)[0])
        self.assertIn("+20 backstab (the dice x5)", self.backstab(13, game.RULE_BACKSTAB)[0])
        self.assertIn("x5 backstab", self.backstab(14, 0)[0])


class SaveTests(unittest.TestCase):
    def save_roll(self, log, natural, target=0x29, caster=0, spell=HOLD_PERSON):
        # the saving throw's frame: [BP+6] target, [BP+8] caster, [BP+0Ah] spell;
        # locals: far pointer to the target at [BP-1Eh], save value at [BP-1], save index at [BP-6]
        rec = CREATURES + STALKER * game.CREATURE_SIZE
        parent_locals = bytearray(locals_at(0x28, m1e=rec & 0xF, m1c=rec >> 4, m6=5))
        parent_locals[0x27] = 14
        return entry(raw_for(natural, 20), dicelog.DICE_SITE, words(0, 0, 1, 20),
                     words(0, 0, target, caster, spell), parent_locals=bytes(parent_locals), parent_bp=0xFD00)

    def probe(self, total, needed=14, target=0x29, caster=0, spell=HOLD_PERSON):
        return entry((needed << 8) | total, frame=words(0, 0, target, caster, spell),
                     locals_=locals_at(0x10, m6=5), kind=KIND_SAVE, bp=0xFD00)

    def magic_resistance(self, roll, target=0x29, spell=FIREBALL):
        # its caller: (target, spell, caster level); the return address is the overlay manager's
        return entry(raw_for(roll, 100), dicelog.DICE_SITE, words(0, 0, 1, 100), words(0, 0, target, spell, 9),
                     parent_code=bytes.fromhex("cd3f3310"))

    def test_spell_damage_then_save_with_probe(self):
        log = make_game()
        damage = [entry(raw_for(f, 6), dicelog.DICE_SITE, words(0, 0, 2, 6), words(0, 0, HOLD_PERSON),
                        parent_code=dicelog.SPELL_DAMAGE_RETURN) for f in (6, 4)]
        # the damage routine's arguments name the spell, so the line needn't wait for the save
        self.assertEqual(log.describe(damage[0], now=1.0) + log.describe(damage[1], now=1.0),
                         ["Hold Person damage: 2d6 = [6 + 4] = 10"])
        self.assertEqual(log.describe(self.save_roll(log, 13), now=1.1), [])
        self.assertEqual(log.describe(self.probe(15)),
                         ["Mountain Stalker's saving throw vs Hold Person from Dag (spell): d20 = 13 +2 other = 15, "
                          "needs 14 (45% to save) -> saved"])

    def test_power_duration_named(self):
        """A monster's power the game names none of (the Red Slaad's 182): named by its effect, and
        the dice rolled before the save said to be how long it would last."""
        log = make_game()
        log.game.spell_name = lambda spell: "Paralysing attack"
        log.game.power_effect = lambda spell: 34  # (Paralyzed)
        log.game.spell_duration = lambda spell, level, roll: (roll * 60, f"{roll} from the dice")
        for f in (4, 3):
            log.describe(entry(raw_for(f, 4), dicelog.DICE_SITE, words(0, 0, 2, 4), words(0, 0, 0x29, 182)),
                         now=1.0)
        self.assertEqual(log.describe(self.save_roll(log, 13, spell=182), now=1.1),
                         ["Paralysing attack: lasts 7 rounds unless saved against (2d4 = [4 + 3] = 7)"])

    def test_save_shows_what_it_leaves(self):
        """Fireball's damage for this target, then its save: the save line says what's left."""
        log = make_game()
        self.damage_formula(log, FIREBALL, 0x20, 0x01, 0x06)  # 1d6 a caster level
        dice = [entry(raw_for(f, 6), dicelog.DICE_SITE, words(0, 0, 3, 6), words(0, 0, FIREBALL, 3),
                      parent_code=dicelog.SPELL_DAMAGE_RETURN) for f in (6, 5, 4)]
        for d in dice:
            log.describe(d, now=1.0)
        log.describe(self.save_roll(log, 9, spell=FIREBALL), now=1.1)
        self.assertEqual(log.describe(self.probe(18, needed=14, spell=FIREBALL)),
                         ["Mountain Stalker's saving throw vs Fireball from Dag (spell): d20 = 9, doubled against fire = 18, "
                          "needs 14 (70% to save) -> saved: half damage, 7 of 15"])

    def test_save_not_doubled_with_the_rule(self):
        """With the Loader's rule the game doesn't double the d20, and neither does the log;
        the target's DEX defensive adjustment counts instead (DEX 16: +2)."""
        log = make_game()
        log.set_rules(game.RULE_NO_DOUBLE)
        self.addCleanup(setattr, game, "RULES_IN_FORCE", 0)
        self.damage_formula(log, FIREBALL, 0x20, 0x01, 0x06)
        for f in (6, 5, 4):
            log.describe(entry(raw_for(f, 6), dicelog.DICE_SITE, words(0, 0, 3, 6), words(0, 0, FIREBALL, 3),
                               parent_code=dicelog.SPELL_DAMAGE_RETURN), now=1.0)
        log.describe(self.save_roll(log, 9, spell=FIREBALL), now=1.1)
        self.assertEqual(log.describe(self.probe(11, needed=14, spell=FIREBALL)),
                         ["Mountain Stalker's saving throw vs Fireball from Dag (spell): d20 = 9 +2 DEX 16 dodging = 11, "
                          "needs 14 (45% to save) -> failed: full damage, 15"])
        log.set_rules(0)  # and the mark comes off again
        rules = (LOAD_SEG + game.SPELLS_SEG) * 16 + game.SPELLS_OFF + FIREBALL * game.SPELL_SIZE
        self.assertFalse(log.guest.mem[rules + 1] & game.CATEGORY_DODGE)

    def damage_formula(self, log, spell, b0, b1, b2):
        rules = (LOAD_SEG + game.SPELLS_SEG) * 16 + game.SPELLS_OFF + spell * game.SPELL_SIZE
        log.guest.mem[rules + 0x0C:rules + 0x0F] = bytes((b0, b1, b2))

    def test_damage_formula(self):
        log = make_game()
        self.damage_formula(log, FIREBALL, 0x20, 0x01, 0x06)  # 1d6 a caster level
        dice = [entry(raw_for(f, 6), dicelog.DICE_SITE, words(0, 0, 3, 6), words(0, 0, FIREBALL, 3),
                      parent_code=dicelog.SPELL_DAMAGE_RETURN) for f in (1, 2, 3)]
        lines = sum((log.describe(d) for d in dice), [])
        self.assertEqual(lines, ["Fireball damage: 3d6 = [1 + 2 + 3] = 6 (1d6 for each caster level: 3 at caster "
                                 "level 3)"])
        # 1d3 + 2 a level (Burning Hands' numbers), from a 20th level caster: counted as 10
        self.damage_formula(log, HOLD_PERSON, 0x02, 0x09, 0x03)
        e = entry(raw_for(2, 3), dicelog.DICE_SITE, words(0, 0, 1, 3), words(0, 0, HOLD_PERSON, 20),
                  parent_code=dicelog.SPELL_DAMAGE_RETURN)
        self.assertEqual(log.describe(e), ["Hold Person damage: 1d3 = [2] +20 = 22 (1d3 + 2 for each caster level: "
                                           "10 at caster level 20, which counts as 10)"])

    def test_flat_bonus_damage(self):
        """A flat bonus that comes once whatever the level (the patched Cause Serious Wounds:
        2d8+1): added, without a per-level explanation."""
        log = make_game()
        self.damage_formula(log, FIREBALL, 0x01, 0x17, 0x08)
        dice = [entry(raw_for(f, 8), dicelog.DICE_SITE, words(0, 0, 2, 8), words(0, 0, FIREBALL, 9),
                      parent_code=dicelog.SPELL_DAMAGE_RETURN) for f in (3, 5)]
        lines = sum((log.describe(d) for d in dice), [])
        self.assertEqual(lines, ["Fireball damage: 2d8 = [3 + 5] +1 = 9"])

    def test_missile_damage(self):
        """Flame Arrow, Minute Meteors, Magic Missile: rolled behind the overlay manager, with
        the spell in the dice routine's own arguments; the steps come from the dice."""
        log = make_game()
        self.damage_formula(log, FIREBALL, 0x20, 0x01, 0x06)  # 1d6 a caster level
        dice = [entry(raw_for(f, 6), dicelog.DICE_SITE, words(0, 0, 3, 6, 0, FIREBALL), words(0, 0, FIREBALL, -748),
                      parent_code=dicelog.OVERLAY_TRAP + bytes(8)) for f in (1, 2, 3)]
        lines = sum((log.describe(d) for d in dice), [])
        self.assertEqual(lines, ["Fireball damage: 3d6 = [1 + 2 + 3] = 6 (1d6 for each caster level, counted up "
                                 "to level 10: 3)"])

    def test_missile_fixed_dice(self):
        log = make_game()
        self.damage_formula(log, FIREBALL, 0, 0x20, 0x08)  # 4d8, nothing more for levels
        dice = [entry(raw_for(f, 8), dicelog.DICE_SITE, words(0, 0, 4, 8, 0, FIREBALL), words(0, 0, FIREBALL, -748),
                      parent_code=dicelog.OVERLAY_TRAP + bytes(8)) for f in (1, 7, 5, 1)]
        self.assertEqual(sum((log.describe(d) for d in dice), []), ["Fireball damage: 4d8 = [1 + 7 + 5 + 1] = 14"])

    def test_dispel_and_abjure(self):
        log = make_game()
        # Dispel Magic at level 7 on the stalker's Blessed (no such effect listed: nothing to weigh)
        e = entry(raw_for(60, 100), dicelog.DICE_SITE, words(0, 0, 1, 100),
                  words(0, 0, 0x29, 0, 0, 0, 0, 0, 0, 7), parent_locals=locals_at(0x28, m2=7),
                  parent_code=dicelog.DISPEL_ROLL_RETURN)
        self.assertEqual(log.describe(e), ["    Dispel Magic on Mountain Stalker's Blessed: d100 = 60, needs 85 or "
                                           "less (50 + 5 x 7) -> dispelled"])
        # Abjure at level 5 against the stalker (level 0 on its sheet): needs 6
        e = entry(raw_for(4, 20), dicelog.DICE_SITE, words(0, 0, 1, 20), words(0, 0, 0x29, 0, 0, 0, 0, 0, 0, 5),
                  parent_code=dicelog.ABJURE_ROLL_RETURN)
        self.assertEqual(log.describe(e), ["    Abjure on Mountain Stalker: d20 = 4, needs 6 or more (11 - caster "
                                           "level 5 + its level 0) -> fails"])

    def test_psp(self):
        log = make_game()
        dag = CREATURES + game.CREATURE_PSP
        struct.pack_into("<h", log.guest.mem, dag, 52)
        self.assertEqual(log.psp_changes(), [])  # the first look
        struct.pack_into("<h", log.guest.mem, dag, 34)
        self.assertEqual(log.psp_changes(), ["    Dag spends 18 PSP (52 -> 34)"])

    def test_script_request(self):
        """A script's REQUEST (DSCLOG's REQ_SITE), named; the everyday ones only with all rolls shown."""
        log = make_game()
        e = entry(8, frame=words(0, 0, 8, 0x7FFE, 1, 0), kind=dicelog.KIND_REQUEST)
        self.assertEqual(log.describe(e), ["Script: random monsters come (request 8: 32766, 1, 0)"])
        e = entry(10, frame=words(0, 0, 10, 3, 40, 12), kind=dicelog.KIND_REQUEST)
        self.assertEqual(log.describe(e), [])
        self.assertEqual(log.describe(e, show_all=True), ["Script: a map cell blocked (request 10: 3, 40, 12)"])

    def test_games_rest_fades_the_arrows(self):
        """The game's own rest (DSCLOG's REST_SITE: request 0, each member's turn): no line, but
        the spell arrows fade in the next pass, as for a script's rest request."""
        log = make_game()
        self.assertFalse(log._rest_due)
        e = entry(0, frame=words(0, 0, 1, 0, 0, 0), kind=dicelog.KIND_REQUEST)
        self.assertEqual(log.describe(e), [])
        self.assertTrue(log._rest_due)

    def test_spell_cast_floats_its_name(self):
        """A spell cast (DSCLOG's CAST_SITE: the caster at [BP+6], the spell its value): its name
        floats over the caster (labels.py), and no line."""
        log = make_game()
        floated = []
        log._float = lambda thing, text, colour, now: floated.append((thing, text))
        e = entry(game.FRIENDS_SPELL, frame=words(0, 0, 2, 0x29, game.FRIENDS_SPELL), kind=dicelog.KIND_CAST)
        self.assertEqual(log.describe(e), [])
        self.assertEqual(floated, [(2, log.game.spell_name(game.FRIENDS_SPELL))])

    def test_aim_refused(self):
        """A spell cast with a click that the game refused (DSCLOG's AIM_SITE), with the reason."""
        log = make_game()
        e = entry(0xFC | 27 << 8, kind=dicelog.KIND_AIM)
        e.extra = 0
        line = log.describe(e)
        self.assertEqual(len(line), 1)
        self.assertIn("there: no line of sight", line[0])

    def test_wall_instead(self):
        """Wall of Thorns' damage (DSCLOG's THORNS_DAMAGE: the damage | the spell << 8, the
        creature's AC + 80h in the extra's high byte): 8 + AC, the HP lost after it put down to it."""
        log = make_game()
        e = entry(13 | game.THORNS_SPELL << 8, kind=dicelog.KIND_WALL)
        e.extra = 40 | (5 + 0x80) << 8  # (the creature's AC + 80h in the high byte)
        self.assertEqual(log.describe(e), ["  Wall of Thorns' wall instead: 8 + AC 5 = 13"])
        self.assertEqual((log._spell_name, log._last_damage), ("Wall of Thorns", (game.THORNS_SPELL, 13)))
        e = entry(1 | game.THORNS_SPELL << 8, kind=dicelog.KIND_WALL)
        e.extra = 40 | (-9 + 0x80) << 8
        self.assertEqual(log.describe(e), ["  Wall of Thorns' wall instead: 8 + AC -9 = 1 (at least 1)"])

    def test_damage_source(self):
        """Two walls hurting the same creature before its HP is seen: each loss put down to the
        spell whose roll it matches (whole, or halved by a save), else the spell being cast."""
        log = make_game()
        e = entry(18 | game.THORNS_SPELL << 8, kind=dicelog.KIND_WALL)
        e.extra = 40 | (10 + 0x80) << 8
        log.describe(e)
        log._recent_damage.append((game.BLADE_SPELL, 34))
        log._spell_cast(game.BLADE_SPELL, 0.0)
        self.assertEqual(log._damage_source(18), (game.THORNS_SPELL, "Wall of Thorns"))
        self.assertEqual(log._damage_source(17), (game.BLADE_SPELL, "Blade Barrier"))  # (34 halved)
        self.assertEqual(log._damage_source(18), (game.BLADE_SPELL, "Blade Barrier"))  # (taken off: the spell cast)

    def test_abilities(self):
        """An ability score's change is told once it holds at two looks (Remove Curse's STR back)."""
        log = make_game()
        at = CREATURES + game.CREATURE_ABILITIES
        log.guest.mem[at:at + 6] = bytes((12, 14, 15, 10, 16, 9))
        self.assertEqual(log.ability_changes(), [])  # the first look
        log.guest.mem[at] = 16
        self.assertEqual(log.ability_changes(), [])  # once: it must hold
        self.assertEqual(log.ability_changes(), ["    Dag's STR 12 -> 16"])
        self.assertEqual(log.ability_changes(), [])
        log.guest.mem[at + 2] = 14
        log.ability_changes()
        log.guest.mem[at + 2] = 15  # (back before it held: nothing)
        self.assertEqual(log.ability_changes(), [])

    def test_psionic_names(self):
        log = make_game()
        m = log.guest.mem
        m[DS * 16 + game.SPELL_NAMES:DS * 16 + game.SPELL_NAMES + 30] = b"DETONATE\0DISINTEGRATE\0" + bytes(7)
        self.assertEqual(game.GameData(log.guest, DS).spell_name(139), "Disintegrate")

    def power_check_game(self):
        """Dag (combatant 0) knowing Graft Weapon (power 17: CON - 5) at 2, the Mountain
        Stalker's Synaptic Static about."""
        log = make_game()
        m = log.guest.mem
        m[(LOAD_SEG + game.POWERS_SEG) * 16 + 17 * game.POWER_SIZE] = (-5 & 0x1F) << 3 | 2
        own_seg = 0x6A00
        struct.pack_into("<H", m, (LOAD_SEG + game.SEGMENT_TABLE) * 16 + game.POWER_OWN_SELECTOR, own_seg)
        m[own_seg * 16 + game.POWER_OWN_OFF + 17] = 2 << 3
        log.game.spell_name = lambda spell: "Graft Weapon" if spell == game.PSIONIC_FIRST + 17 else "?"
        return log

    def test_power_check(self):
        """The d20 at or under the power's score ([BP-2]): CON 16 - 5 Graft Weapon + 1 practised = 12."""
        log = self.power_check_game()
        score = locals_at(0x28, m2=12)  # (the score is the byte at [BP-2])
        e = entry(raw_for(9, 20), dicelog.RANGE_SITE, words(0, 0, 1, 20), words(0, 0, 0, 17, 0),
                  parent_code=dicelog.POWER_CHECK_RETURN, parent_locals=score)
        self.assertEqual(log.describe(e), ["Dag uses Graft Weapon: power check d20 = 9, needs 12 or less -> it works",
                                           "    power score 12 = 16 CON - 5 Graft Weapon + 1 practised"])
        e = entry(raw_for(20, 20), dicelog.RANGE_SITE, words(0, 0, 1, 20), words(0, 0, 0, 17, 0),
                  parent_code=dicelog.POWER_CHECK_RETURN, parent_locals=score)
        self.assertEqual(log.describe(e)[0], "Dag uses Graft Weapon: power check d20 = 20, needs 12 or less "
                                             "(a 20 always fails) -> it fails")

    def test_other_ranges_left_out(self):
        """random(low, high) also makes points of some spells' pictures: no line for those."""
        log = self.power_check_game()
        e = entry(raw_for(3, 40), dicelog.RANGE_SITE, words(0, 0, 0, 40), parent_code=bytes(12))
        self.assertEqual(log.describe(e), [])
        self.assertTrue(any(dicelog.RANGE_SITE.startswith(f) for f in dicelog.FILTERS))

    def test_psionic_defence(self):
        """Two rolls of 1 to the defence (here 6), both over the attacker's d20 (4) to resist."""
        log = self.power_check_game()
        frame = locals_at(0x10)
        first = entry(raw_for(5, 6), dicelog.RANGE_SITE, words(0, 0, 1, 6, 4), words(0, 0, 0),
                      parent_code=dicelog.DEFENCE_FIRST_RETURN, parent_locals=frame)
        self.assertEqual(log.describe(first), [])
        second = entry(raw_for(6, 6), dicelog.RANGE_SITE, words(0, 0, 1, 6, 4), words(0, 0, 0),
                       parent_code=dicelog.DEFENCE_SECOND_RETURN, parent_locals=frame)
        self.assertEqual(log.describe(second), ["  Dag's psionic defence: d6 = 5 and 6, both need over 4 "
                                                "(the attacker's power check d20) -> resisted"])
        fail = entry(raw_for(2, 6), dicelog.RANGE_SITE, words(0, 0, 1, 6, 4), words(0, 0, 0),
                     parent_code=dicelog.DEFENCE_FIRST_RETURN, parent_locals=frame)
        self.assertEqual(log.describe(fail), ["  Dag's psionic defence: d6 = 2, needs over 4 "
                                              "(the attacker's power check d20) -> not resisted"])

    def test_static_contest(self):
        """With the Stalker's Synaptic Static about: Dag's d20 over [BP-8] disrupts the power; else the
        Stalker's at or under its Static score [BP-6] and no lower than Dag's."""
        log = self.power_check_game()
        frame = locals_at(0x28, m4=0x29, m6=11, m8=2)
        for first, second, verdict in ((5, 3, "disrupted by the static"), (2, 8, "disrupted by the static"),
                                       (2, 15, "not disrupted: the power check follows")):
            e = entry(raw_for(first, 20), dicelog.RANGE_SITE, words(0, 0, 1, 20), words(0, 0, 0, 17, 0),
                      parent_code=dicelog.STATIC_FIRST_RETURN, parent_locals=frame)
            self.assertEqual(log.describe(e), [])
            e = entry(raw_for(second, 20), dicelog.RANGE_SITE, words(0, 0, 1, 20), words(0, 0, 0, 17, 0),
                      parent_code=dicelog.STATIC_SECOND_RETURN, parent_locals=frame)
            self.assertEqual(log.describe(e), [
                f"Dag uses Graft Weapon within Mountain Stalker's Synaptic Static: d20 = {first} against 2, "
                f"Mountain Stalker's d20 = {second} against 11 (and at least {first}) -> {verdict}"])

    def test_out_cold_takes_the_most(self):
        log = make_game()
        m = log.guest.mem
        stalker = CREATURES + STALKER * game.CREATURE_SIZE
        struct.pack_into("<h", m, stalker, 30)
        m[stalker + game.CREATURE_STATUS] = game.OUT_COLD
        log.hp_changes(0.5)
        e = entry(raw_for(3, 6), dicelog.DICE_SITE, words(0, 0, 1, 6), words(0, 0, FIREBALL, 3),
                  parent_code=dicelog.SPELL_DAMAGE_RETURN)
        log.describe(e, now=1.0)
        struct.pack_into("<h", m, stalker, 24)
        self.assertEqual(log.hp_changes(1.5), ["  Mountain Stalker takes 6 from Fireball "
                                               "(Out Cold: the most the dice can do), now 24 HP"])

    def test_confusion(self):
        log = make_game()
        e = entry(raw_for(8, 10), dicelog.DICE_SITE, words(0, 0, 1, 10), words(0, 0, 0x29),
                  parent_code=dicelog.CONFUSION_ROLL_RETURN)
        self.assertEqual(log.describe(e), ["Mountain Stalker is confused: d10 = 8 -> fights for a side picked at random"])
        e = entry(raw_for(1, 2), dicelog.DICE_SITE, words(0, 0, 1, 2), words(0, 0, 0x29),
                  parent_code=dicelog.RANDOM_SIDE_RETURN)
        self.assertEqual(log.describe(e), ["    Mountain Stalker fights on the party's side this turn (d2 = 1)"])

    def test_charges(self):
        """A negative duration unit: the effect lasts that many uses (Stoneskin: 1 a level + 1d4)."""
        log = make_game()
        self.damage_formula(log, FIREBALL, 0, 0x01, 0)  # divisor 1, no level adjustment
        record = (LOAD_SEG + game.SPELLS_SEG) * 16 + game.SPELLS_OFF - 0x10 + FIREBALL * game.SPELL_SIZE
        struct.pack_into("<Hh", log.guest.mem, record + 5, 1, -1)
        e = entry(raw_for(3, 4), dicelog.DICE_SITE, words(0, 0, 1, 4), words(0, 0, FIREBALL, 5),
                  parent_code=dicelog.SPELL_DURATION_RETURN)
        self.assertEqual(log.describe(e), ["    Fireball has 8 charges (caster level 5: 1 for each caster level "
                                           "= 5 + 3 from the dice; dice 1d4 = [3])"])
        # the same roll with its return address taken by the overlay manager: known by the
        # spell record's duration dice (1d4 here) and the (spell, level) arguments
        log.guest.mem[record + 4] = 0x41
        e = entry(raw_for(2, 4), dicelog.DICE_SITE, words(0, 0, 1, 4), words(0, 0, FIREBALL, 5),
                  parent_code=dicelog.OVERLAY_TRAP + bytes(8))
        self.assertEqual(log.describe(e), ["    Fireball has 7 charges (caster level 5: 1 for each caster level "
                                           "= 5 + 2 from the dice; dice 1d4 = [2])"])

    def test_acid_each_round(self):
        log = make_game()
        e = [entry(raw_for(f, 4), dicelog.DICE_SITE, words(0, 0, 2, 4), words(0, 0, 0x29, 1),
                   parent_code=dicelog.CHARGE_USED_RETURN) for f in (3, 1)]
        self.assertEqual(log.describe(e[0]) + log.describe(e[1]),
                         ["    Acid on Mountain Stalker: 2d4 = [3 + 1] = 4 acid damage"])
        # the same routine for any other effect using a charge (Ironskin stopping a blow)
        e = [entry(raw_for(f, 4), dicelog.DICE_SITE, words(0, 0, 2, 4), words(0, 0, 0x29, 53),
                   parent_code=dicelog.CHARGE_USED_RETURN) for f in (3, 1)]
        self.assertEqual(log.describe(e[0]) + log.describe(e[1]), ["    Ironskin on Mountain Stalker: one charge used"])

    def test_acid_rounds(self):
        """An Acid's time (Acid Arrow's: 20 seconds a level) is rounds of burning (DSCLOG's
        ACID_ROUNDS: 1 a started minute); after a round's burn, its damage's own duration roll
        (the effect it no longer puts on) says nothing."""
        log = make_game()
        self.damage_formula(log, FIREBALL, 0, 0x01, 0)
        record = (LOAD_SEG + game.SPELLS_SEG) * 16 + game.SPELLS_OFF - 0x10 + FIREBALL * game.SPELL_SIZE
        struct.pack_into("<Hh", log.guest.mem, record + 5, 20, 1)
        log.guest.mem[record + 0x19] = dicelog.ACID
        duration = entry(raw_for(1, 1), dicelog.DICE_SITE, words(0, 0, 1, 1), words(0, 0, FIREBALL, 11),
                         parent_code=dicelog.SPELL_DURATION_RETURN)
        line = log.describe(duration)
        self.assertEqual(len(line), 1)
        self.assertTrue(line[0].startswith("    Fireball burns 4 rounds more, 2d4 at the start of each ("), line)
        burn = [entry(raw_for(f, 4), dicelog.DICE_SITE, words(0, 0, 2, 4), words(0, 0, 0x29, 1),
                      parent_code=dicelog.CHARGE_USED_RETURN) for f in (3, 1)]
        self.assertEqual(log.describe(burn[0]) + log.describe(burn[1]),
                         ["    Acid on Mountain Stalker: 2d4 = [3 + 1] = 4 acid damage"])
        self.assertEqual(log.describe(duration), [])
        self.assertEqual(len(log.describe(duration)), 1)  # (only the one after a burn)

    def test_sunstroke_heat(self):
        """Sunstroke's heat (DSCLOG's BURN_PASS through Acid's burn, its 1d4; HEAT_SITE's record:
        the damage | the spell << 8, the creature the extra): one line, the roll's own hidden line
        dropped, the HP lost after it put down to Sunstroke; its damage's duration roll says
        nothing."""
        log = make_game()
        roll = entry(raw_for(3, 4), dicelog.DICE_SITE, words(0, 0, 1, 4), words(0, 0, 0x29, 1),
                     parent_code=dicelog.CHARGE_USED_RETURN)
        self.assertEqual(log.describe(roll), [])
        log._pending.append(dicelog.PendingDice("1d4 = [3] = 3", 0.0))
        e = entry(3 | game.SUNSTROKE_SPELL << 8, kind=dicelog.KIND_HEAT)
        e.extra = 0x29
        self.assertEqual(log.describe(e), ["    Sunstroke's heat on Mountain Stalker: 1d4 = 3 fire damage"])
        self.assertEqual((log._pending, log._last_damage), ([], (game.SUNSTROKE_SPELL, 3)))
        duration = entry(raw_for(2, 4), dicelog.DICE_SITE, words(0, 0, 1, 4), words(0, 0, game.SUNSTROKE_SPELL, 11),
                         parent_code=dicelog.SPELL_DURATION_RETURN)
        self.assertEqual(log.describe(duration), [])
        self.assertFalse(log._sun_burn)

    def test_swept(self):
        """Whirlwind's damage after a failed save (DSCLOG's SWEPT_MARK: the combatant): its next turn lost."""
        log = make_game()
        self.assertEqual(log.describe(entry(0x29, kind=dicelog.KIND_SWEPT)),
                         ["    Mountain Stalker is swept off its feet: loses its next turn"])

    def test_mirror_images(self):
        """Mirror Images' d100: on a foe's spell (7A5BFh's 1d100, NS_IMAGE: the spell routine's
        target and caster), none from the target's own side; on an attack's hit (DSCLOG's NS_BLOW:
        the game's rand() from its code marked IMAGE, in a frame of target, attacker, chance); and
        the image used up."""
        log = make_game()
        spell = lambda roll, caster: entry(raw_for(roll, 100), dicelog.DICE_SITE, words(0, 0, 1, 100),
                                           words(0, 0, 0x29, caster), parent_code=dicelog.IMAGE_SPELL_RETURN)
        head = "    Mirror Images on Mountain Stalker: d100 = "
        self.assertEqual(log.describe(spell(30, 0)), [head + "30, 75 or less strikes an image -> an image is "
                                                      "struck instead, the spell lost"])
        self.assertEqual(log.describe(spell(76, 1)), [head + "76, 75 or less strikes an image -> the spell gets through"])
        self.assertEqual(log.describe(spell(5, 0x2A)), [head + "5, a spell from its own side -> no image takes it"])
        # the same with its return address taken by the overlay manager: the routine's arguments
        # (target, caster, ..., spell at +12h) and Mirror Images on the target tell it
        trapped = entry(raw_for(40, 100), dicelog.DICE_SITE, words(0, 0, 1, 100),
                        words(0, 0, 0x29, 0, 0, 0, 0, 0, 8), parent_code=dicelog.OVERLAY_TRAP + bytes(8))
        self.assertEqual(log.describe(trapped), [])
        set_effects(log, [(0x29, 0, game.MIRROR_EFFECT)])
        self.assertEqual(log.describe(trapped), [head + "40, 75 or less strikes an image -> an image is "
                                                 "struck instead, the spell lost"])
        # (and none for the game's sight of an image vanishing, cast by the creature on itself)
        vanish = entry(raw_for(40, 100), dicelog.DICE_SITE, words(0, 0, 1, 100),
                       words(0, 0, 0x29, 0x29, 0, 0, 0, 0, 0xBF), parent_code=dicelog.IMAGE_SPELL_RETURN)
        self.assertEqual(log.describe(vanish), [])
        blow = lambda roll, chance: entry(raw_for(roll, 100), dicelog.IMAGE_BLOW_SITE + bytes(8),
                                          words(0, 0, 0x29, 0, chance))
        self.assertEqual(log.describe(blow(50, 50)), [head + "50, 50 or less strikes an image -> an image is "
                                                      "struck instead, the blow lost"])
        self.assertEqual(log.describe(blow(76, 75)), [head + "76, 75 or less strikes an image -> the blow gets through"])
        e = [entry(raw_for(f, 4), dicelog.DICE_SITE, words(0, 0, 2, 4), words(0, 0, 0x29, 25),
                   parent_code=dicelog.CHARGE_USED_RETURN) for f in (3, 1)]
        self.assertEqual(log.describe(e[0]) + log.describe(e[1]), ["    Mirror Images on Mountain Stalker: an image vanishes"])

    def test_strength_roll(self):
        log = make_game()
        e = entry(raw_for(6, 6), dicelog.DICE_SITE, words(0, 0, 1, 6), words(0, 0, 1, 0, 0, 0, HOLD_PERSON),
                  parent_code=dicelog.STRENGTH_ROLL_RETURN)
        self.assertEqual(log.describe(e), ["Hold Person: 1d6 = 6 -> Daaki's STR +6 while it lasts (at most 24)"])

    def test_spell_handler_dice(self):
        log = make_game()
        e = [entry(raw_for(f, 8), dicelog.DICE_SITE, words(0, 0, 2, 8), words(0, 0, 0, 0x29, 0, 0, HOLD_PERSON),
                   parent_code=dicelog.SPELL_HANDLER_RETURNS[0][0]) for f in (3, 5)]
        self.assertEqual(log.describe(e[0]) + log.describe(e[1]), ["Hold Person: 2d8 = [3 + 5] +1 = 9"])

    def test_hp_after_a_spell(self):
        log = make_game()
        m = log.guest.mem
        stalker = CREATURES + STALKER * game.CREATURE_SIZE
        struct.pack_into("<h", m, stalker, 30)
        self.assertEqual(log.hp_changes(0.5), [])  # the first look
        e = entry(raw_for(3, 6), dicelog.DICE_SITE, words(0, 0, 1, 6), words(0, 0, FIREBALL, 3),
                  parent_code=dicelog.SPELL_DAMAGE_RETURN)
        log.describe(e, now=1.0)
        struct.pack_into("<h", m, stalker, 27)
        self.assertEqual(log.hp_changes(1.5), ["  Mountain Stalker takes 3 from Fireball, now 27 HP"])
        struct.pack_into("<h", m, stalker, 20)  # long after: not the spell's doing
        self.assertEqual(log.hp_changes(30.0), ["  Mountain Stalker now 20 HP (-7)"])
        struct.pack_into("<h", m, stalker, 25)
        self.assertEqual(log.hp_changes(31.0), ["  Mountain Stalker now 25 HP (+5)"])

    def test_regeneration(self):
        """A hit point back by itself, CON 20 or more (the game's own rule): said so."""
        log = make_game()
        m = log.guest.mem
        stalker = CREATURES + STALKER * game.CREATURE_SIZE
        struct.pack_into("<h", m, stalker, 20)
        m[stalker + game.CREATURE_ABILITIES + 2] = 22
        log.hp_changes(0.5)
        struct.pack_into("<h", m, stalker, 21)
        self.assertEqual(log.hp_changes(1.0), ["  Mountain Stalker regenerates 1 HP (CON 22), now 21 HP"])
        m[stalker + game.CREATURE_ABILITIES + 2] = 19
        struct.pack_into("<h", m, stalker, 22)
        self.assertEqual(log.hp_changes(2.0), ["  Mountain Stalker now 22 HP (+1)"])

    def test_a_hit_during_a_spell_is_not_the_spells(self):
        log = make_game()
        m = log.guest.mem
        stalker = CREATURES + STALKER * game.CREATURE_SIZE
        struct.pack_into("<h", m, stalker, 30)
        log.hp_changes(0.5)
        log._spell_cast(FIREBALL, 1.0)
        log._hit(STALKER, 12, 1.0)  # a weapon hit logged just before
        struct.pack_into("<h", m, stalker, 12)
        self.assertEqual(log.hp_changes(1.5), ["  Mountain Stalker takes 6 from Fireball and 12 from the hit, now 12 HP"])
        log._hit(STALKER, 5, 2.0)
        struct.pack_into("<h", m, stalker, 7)
        self.assertEqual(log.hp_changes(2.0), ["  Mountain Stalker now 7 HP (-5)"])

    def test_a_hit_that_takes_no_hp(self):
        """A weapon hit whose target loses no HP (HIT_WAIT on, or at the next round): said so;
        one that takes less than was rolled: how much."""
        log = make_game()
        m = log.guest.mem
        stalker = CREATURES + STALKER * game.CREATURE_SIZE
        struct.pack_into("<h", m, stalker, 30)
        log.hp_changes(0.5)
        log._hit(STALKER, 9, 1.0)
        self.assertEqual(log.hp_changes(2.0), [])  # (not yet: the game may not have taken it off)
        self.assertEqual(log.hp_changes(1.0 + dicelog.HIT_WAIT),
                         ["  Mountain Stalker takes none of the 9 damage: a protection or resistance took it"])
        log._hit(STALKER, 10, 5.0)
        struct.pack_into("<h", m, stalker, 25)
        self.assertEqual(log.hp_changes(5.5), ["  Mountain Stalker now 25 HP (-5: 5 of the 10 rolled)"])
        log._hit(STALKER, 9, 7.0)  # two hits before the HP is seen: taken one at a time
        log._hit(STALKER, 10, 7.1)
        struct.pack_into("<h", m, stalker, 16)
        self.assertEqual(log.hp_changes(7.2), ["  Mountain Stalker now 16 HP (-9)"])
        struct.pack_into("<h", m, stalker, 6)
        self.assertEqual(log.hp_changes(7.3), ["  Mountain Stalker now 6 HP (-10)"])
        struct.pack_into("<h", m, stalker, 0)
        log._hit(STALKER, 9, 8.0)  # (more than its HP: not resisted)
        self.assertEqual(log.hp_changes(8.1), ["  Mountain Stalker now 0 HP (-6)"])
        struct.pack_into("<h", m, stalker, 30)
        log.hp_changes(8.2)
        log._hit(STALKER, 4, 9.0)
        self.assertEqual(log.unhurt(6.1, force=True),
                         ["  Mountain Stalker takes none of the 4 damage: a protection or resistance took it"])

    def test_reduced_hits_seen_together(self):
        """Two hits on a creature that halves weapons, seen as one fall of HP: both of them, and
        no "takes none" later for the second."""
        log = make_game()
        m = log.guest.mem
        stalker = CREATURES + STALKER * game.CREATURE_SIZE
        struct.pack_into("<h", m, stalker, 30)
        log.hp_changes(0.5)
        log._weapon_reason = lambda index: "non-magical weapons do half"
        log._hit(STALKER, 8, 1.0)
        log._hit(STALKER, 6, 1.1)
        struct.pack_into("<h", m, stalker, 23)
        self.assertEqual(log.hp_changes(1.2),
                         ["  Mountain Stalker now 23 HP (-7: 7 of the 14 rolled, non-magical weapons do half)"])
        self.assertEqual(log.unhurt(1.2 + dicelog.HIT_WAIT, force=True), [])

    def test_doubled_roll(self):
        log = make_game()
        log.describe(self.save_roll(log, 7, spell=FIREBALL))
        self.assertEqual(log.describe(self.probe(14, needed=15, spell=FIREBALL)),
                         ["Mountain Stalker's saving throw vs Fireball from Dag (spell): d20 = 7, doubled against fire "
                          "= 14, needs 15 (65% to save) -> failed"])

    def test_modifiers_name_the_effects_that_count(self):
        log = make_game()
        set_effects(log, [(0x29, 0, 7), (0x29, 0, 58)])  # Blessed (saves), Displacement (AC only)
        log.describe(self.save_roll(log, 7))
        self.assertTrue(log.describe(self.probe(8))[0].endswith(
            "d20 = 7 +1 Blessed = 8, needs 14 (40% to save) -> failed"))
        log.describe(self.save_roll(log, 7))  # something the log can't account for
        self.assertTrue(log.describe(self.probe(10))[0].endswith(
            "d20 = 7 +1 Blessed +2 other = 10, needs 14 (50% to save) -> failed"))

    def test_modifiers_by_damage_kind_and_con(self):
        log = make_game()
        set_effects(log, [(0x29, 0, 40), (0x29, 0, 7)])  # Prot Fire, Blessed
        log.describe(self.save_roll(log, 7, spell=FIREBALL))
        self.assertEqual(log.describe(self.probe(18, needed=15, spell=FIREBALL)),
                         ["Mountain Stalker's saving throw vs Fireball from Dag (spell): d20 = 7, doubled against fire "
                          "= 14 +1 Blessed +3 Prot Fire = 18, needs 15 (75% to save) -> saved"])
        # paralysis/poison/death: a dwarf's CON counts twice over
        m = log.guest.mem
        m[SHEETS + STALKER * game.SHEET_SIZE + game.SHEET_RACE] = game.DWARF
        m[CREATURES + STALKER * game.CREATURE_SIZE + game.CREATURE_ABILITIES + 2] = 19
        m[DS * 16 + game.SAVE_CON + 19] = 1
        self.assertEqual(log.game.save_modifiers(0x29, 0, HOLD_PERSON, game.PPD_SAVE),
                         [(1, "Blessed"), (5, "dwarf CON 19"), (1, "CON 19")])

    def test_natural_20_needs_no_probe(self):
        log = make_game()
        self.assertEqual(log.describe(self.save_roll(log, 20)),
                         ["Mountain Stalker's saving throw vs Hold Person from Dag (spell): d20 = 20 (natural 20) -> saved"])

    def test_magic_resistance(self):
        log = make_game()
        log.describe(self.magic_resistance(40))
        self.assertEqual(log.describe(self.save_roll(log, 20, spell=FIREBALL))[:-1], [])  # none: no line
        sheet = SHEETS + 3 * game.SHEET_SIZE
        struct.pack_into("<H", log.guest.mem, CREATURES + STALKER * game.CREATURE_SIZE + game.CREATURE_SHEET_INDEX, 3)
        log.guest.mem[sheet + game.SHEET_MAGIC_RESISTANCE] = 50
        self.assertEqual(log.describe(self.magic_resistance(60)), [])
        self.assertEqual(log.describe(self.save_roll(log, 20, spell=FIREBALL))[0],
                         "Mountain Stalker magic resistance 50% vs Fireball: d100 = 60 -> not resisted")
        log.describe(self.magic_resistance(40), now=1.0)  # resisted: no saving throw follows
        self.assertEqual(log.flush(2.5),
                         ["Mountain Stalker magic resistance 50% vs Fireball: d100 = 40 -> resisted"])

    def test_amulet_of_magic_resistance(self):
        """The Amulet of Magic Resistance at the target's neck: its 15% in the line (AMULET_MR)."""
        log = make_game()
        log.game.wears_type = lambda creature, item_type, slot: item_type == game.MR_AMULET_TYPE \
            and slot == game.EQUIP_SLOTS.index("neck")
        log.describe(self.magic_resistance(10), now=1.0)
        self.assertEqual(log.flush(2.5), ["Mountain Stalker magic resistance 15% (+15 Amulet of Magic Resistance) "
                                          "vs Fireball: d100 = 10 -> resisted"])

    def test_dice_without_a_spell_are_shown_after_a_while(self):
        log = make_game()
        log.describe(entry(raw_for(3, 8), dicelog.DICE_SITE, words(0, 0, 1, 8)), now=5.0)
        log.describe(entry(raw_for(1, 1), dicelog.DICE_SITE, words(0, 0, 1, 1)), now=5.0)  # 1d1: not a roll
        self.assertEqual(log.flush(5.5), [])
        self.assertEqual(log.flush(6.1), ["Dice: 1d8 = [3] = 3"])


class OtherTests(unittest.TestCase):
    def test_items_still(self):
        """The item lists are changed only while the game's free lists stay as they are (not as
        START GAME builds them afresh)."""
        from unittest import mock
        from dsloader import ring
        log = make_game()
        m = log.guest.mem
        self.assertTrue(log._items_still())

        def sleep(seconds):  # (the game takes an item record meanwhile)
            at = DS * 16 + ring.FREE_ITEMS
            struct.pack_into("<H", m, at, struct.unpack_from("<H", m, at)[0] + 1)
        with mock.patch("dsloader.dicelog.time.sleep", sleep):
            self.assertFalse(log._items_still())
            with mock.patch("dsloader.weaponchoice.class_gear") as gear, \
                    mock.patch("dsloader.names.update", lambda *a: True):
                log.rules |= game.RULE_RESTRICT
                log._arena_ring(1e9)
                gear.assert_not_called()

    def test_ac_probe_remembers_the_ac(self):
        log = make_game()
        self.assertEqual(log.describe(entry(-2, frame=words(0, 0, 0x29, 0), kind=KIND_AC)), [])
        self.assertEqual(log.last_ac, {STALKER: -2})

    def test_effects_that_start_and_end(self):
        log = make_game()
        set_effects(log, [(0, 0, 46)])
        self.assertEqual(log.effect_changes(10.0), [])  # what was active before is not news
        set_effects(log, [(0, 0, 46), (0, 2, 7), (1, 2, 7)])
        self.assertEqual(log.effect_changes(20.0),
                         ["Jellybelly gives Blessed to Dag, Daaki: +1 to hit, +1 on saves"])
        set_effects(log, [(0, 0, 46)])
        self.assertEqual(log.effect_changes(21.0), ["Blessed ends on Dag, Daaki"])

    def test_effects_of_a_loaded_game_are_not_news(self):
        log = make_game()
        self.assertEqual(log.effect_changes(10.0), [])
        name = CREATURES + game.CREATURE_NAME
        log.guest.mem[name:name + 3] = b"Tom"  # another party: a game was loaded
        set_effects(log, [(0, 0, 63)])
        self.assertEqual(log.effect_changes(20.0), [])
        set_effects(log, [(0, 0, 63), (1, 0, 63)])  # the load settles over a moment
        self.assertEqual(log.effect_changes(20.0 + dicelog.LOAD_SETTLE / 2), [])
        set_effects(log, [(0, 0, 63), (1, 0, 63), (2, 0, 7)])
        self.assertEqual(log.effect_changes(30.0), ["Tom gives Blessed to Jellybelly: +1 to hit, +1 on saves"])

    def test_attach_needs_the_patched_game(self):
        log = make_game()
        m = log.guest.mem
        m[HDR:HDR + 8] = dicelog.HDR_SIG
        m[DS * 16 + game.BORLAND_SIG_OFFSET:DS * 16 + game.BORLAND_SIG_OFFSET + len(game.BORLAND_SIG)] = \
            game.BORLAND_SIG
        fresh = DiceLog(log.guest)
        with self.assertRaisesRegex(dicelog.DiceLogError, "without the dice log"):
            fresh.attach()
        m[log.rand_addr:log.rand_addr + 2] = dicelog.RAND_PATCHED
        self.assertEqual(fresh.attach(), "Dice log attached.")
        self.assertTrue(fresh.still_patched())
        m[log.rand_addr] = 0x8B  # the game was restarted without it
        self.assertFalse(fresh.still_patched())

    def test_ability_check(self):
        log = make_game()
        rec = CREATURES + 1 * game.CREATURE_SIZE  # Daaki
        log.guest.mem[rec + game.CREATURE_ABILITIES + 1] = 16  # DEX
        seg, off = dicelog.CHECK_MODS
        log.guest.mem[(LOAD_SEG + seg) * 16 + off + 3] = 0xFE  # -2
        e = entry(raw_for(14, 20), dicelog.CHECK_SITE, words(0, 0, 1, 3, 1))
        self.assertEqual(log.describe(e), ["Daaki DEX check: d20 = 14, needs 14 or less (DEX 16 -2) -> success"])

    def test_thief_skill(self):
        """Dag as a 4th level half-giant thief with DEX 16 opening a lock with a -10 for this lock:
        the game's chance was 24, so 5 went on armour."""
        log = make_game()
        m = log.guest.mem
        table = (LOAD_SEG + game.THIEF_TABLE_SEG) * 16
        m[table + game.THIEF_BASE + 1] = 18
        m[table + game.THIEF_DEX_LOW + 1], m[table + game.THIEF_DEX_HIGH + 1], m[table + game.THIEF_DEX_TOP + 1] = 11, 15, 20
        sheet = SHEETS
        m[sheet + game.SHEET_CLASSES + 1], m[sheet + game.SHEET_LEVELS + 1] = game.THIEF, 4
        m[CREATURES + game.CREATURE_ABILITIES + 1] = 16
        e = entry(1223, dicelog.PERCENT_SITE, words(0, 0, 0, 1, 0, -10), locals_=locals_at(0x10, m2=24))
        self.assertEqual(log.describe(e), ["Dag tries to open locks: d100 = 24, needs 24 or less -> success",
                                           "    open locks 24 = 18 + 16 thief level 4 + 5 DEX 16 - 10 this attempt "
                                           "- 5 equipment"])
        # an effect (Blind, Afraid...) takes 1000 off
        e = entry(1223, dicelog.PERCENT_SITE, words(0, 0, 0, 1, 0, 0), locals_=locals_at(0x10, m2=-961))
        self.assertEqual(log.describe(e), ["Dag tries to open locks: d100 = 24 -> failure (an effect stops it)"])

    def test_generic_shapes_when_showing_everything(self):
        log = make_game()
        d10 = bytes.fromhex("660fbfc0666bc00a66bb00800000669966f7fb40")
        range200 = bytes.fromhex("660fbfc06669c0c800000066bb00800000669966f7fb")
        self.assertEqual(log.describe(entry(raw_for(7, 10), d10)), [])
        self.assertEqual(log.describe(entry(raw_for(7, 10), d10), show_all=True), ["d10 = 7  (at 5000:0010)"])
        self.assertEqual(log.describe(entry(100 * 0x8000 // 200 + 1, range200), show_all=True),
                         ["0-199 = 100  (at 5000:0010)"])

    def test_poll_returns_new_entries_in_order_and_counts_missed_ones(self):
        log = make_game()
        nent, esize, ring = 4, Entry.SIZE, 0x100
        log.last_seq = 0
        struct.pack_into("<5H", log.guest.mem, HDR + 8, 6, 2, nent, esize, ring)
        struct.pack_into("<H", log.guest.mem, HDR + 20, 0)
        struct.pack_into("<H", log.guest.mem, HDR + dicelog.TSR_RING_SEG, HDR // 16)  # (the ring's segment)
        for seq in (3, 4, 5, 6):  # 1 and 2 were overwritten
            struct.pack_into("<H", log.guest.mem, HDR + ring + ((seq - 1) % nent) * esize, seq)
        self.assertEqual([e.seq for e in log.poll()], [3, 4, 5, 6])
        self.assertEqual(log.missed, 2)
        self.assertEqual(log.poll(), [])


class NewLinesTests(unittest.TestCase):
    def test_weapon_break_check(self):
        log = make_game()
        log._last_attacker = "Dag"
        wooden = words(0, 0, 6, 10)  # item 6, type 10: plain wood, can break
        self.assertEqual(log.describe(entry(raw_for(3, 8), dicelog.BREAK_ROLL_1, wooden)), [])  # 2 on 0-7: fine
        self.assertEqual(log.describe(entry(raw_for(1, 8), dicelog.BREAK_ROLL_1, wooden)), [])  # 0: one more roll
        self.assertEqual(log.describe(entry(raw_for(6, 20), dicelog.BREAK_ROLL_2, wooden)),
                         ["    Dag's Wooden Long Sword nearly broke: 0 on 0-7, then 5 on 0-19 (needed 0)"])
        log.describe(entry(raw_for(1, 8), dicelog.BREAK_ROLL_1, wooden))
        self.assertEqual(log.describe(entry(raw_for(1, 20), dicelog.BREAK_ROLL_2, wooden)),
                         ["    Dag's Wooden Long Sword BREAKS: 0 on 0-7 and 0 on 0-19 (1 in 160 after each hit)"])
        # a magical metal sword never breaks
        self.assertEqual(log.describe(entry(raw_for(1, 8), dicelog.BREAK_ROLL_1, words(0, 0, 5, 9))), [])

    def test_level_up_hit_points(self):
        log = make_game()
        # the caller's arguments: party member 0, class 9 (fighter), new level 4
        e = entry(raw_for(2, 10), dicelog.DICE_SITE, words(0, 0, 1, 10), words(0, 0, 0, 9, 4))
        self.assertEqual(log.describe(e), ["Dag's 4th Fighter level: hit points d10 = 2, raised to 3 for CON 21, "
                                           "doubled for a half-giant = 6"])

    def test_level_up_hit_points_best_of_two(self):
        """RULE_HP_BEST: the game rolls the die twice (DSCLOG's PROBE_HP_BEST); the line comes with
        the second, the better kept."""
        log = make_game()
        log.set_rules(game.RULE_HP_BEST)
        first = entry(raw_for(2, 10), dicelog.DICE_SITE, words(0, 0, 1, 10), words(0, 0, 0, 9, 4))
        second = entry(raw_for(7, 10), dicelog.DICE_SITE, words(0, 0, 1, 10), words(0, 0, 0, 9, 4))
        self.assertEqual(log.describe(first), [])
        self.assertEqual(log.describe(second), ["Dag's 4th Fighter level: hit points d10 = 2 and 7, the better 7, "
                                                "doubled for a half-giant = 14"])

    def test_special_effect_roll(self):
        log = make_game()
        e = entry(raw_for(1, 10), dicelog.DICE_SITE, words(0, 0, 1, 10), words(0, 0, 0x29, 0),
                  parent_code=dicelog.SPECIAL_EFFECT_RETURN)
        self.assertEqual(log.describe(e), ["    Dag's special effect on Mountain Stalker: d10 = 1, works on a 1 "
                                           "-> it works"])

    def test_ac_breakdown(self):
        log = make_game()
        # AC 4 = armour AC 7 (base 10, armour -3) + DEX -2 + spells -1
        log.describe(entry(4, frame=words(0, 0, 0x29, 0, 0), locals_=locals_at(0x10, m6=7), kind=KIND_AC))
        self.assertEqual(log.ac_detail[STALKER], AcDetail(10, -3, -2, -1, 4))

    def test_kill_and_experience(self):
        log = make_game()
        tracker, m = log.tracker, log.guest.mem
        struct.pack_into("<h", m, CREATURES + STALKER * game.CREATURE_SIZE, 20)
        self.assertEqual(tracker.check(1.0), [])
        struct.pack_into("<h", m, CREATURES + STALKER * game.CREATURE_SIZE, -3)
        self.assertEqual(tracker.check(2.0), ["Mountain Stalker is killed"])
        struct.pack_into("<I", m, SHEETS, 125)  # Dag's XP
        self.assertEqual(tracker.check(2.2), [])  # waits for the others' XP
        self.assertEqual(tracker.check(3.0), ["XP: Dag +125 (for Mountain Stalker 500)"])

    def test_leaving_an_area_kills_no_one(self):
        """Going to another area the game drops the old area's people and clears or reuses their
        records: no deaths logged (once every guard of the arena was "killed" on leaving the pens).
        One creature gone from the fight with its own record dead is still a kill."""
        def setup(extra):
            log = make_game()
            m = log.guest.mem
            table = (LOAD_SEG + game.COMBATANTS_SEG) * 16 + game.COMBATANTS_OFF
            for k, creature in enumerate(extra):
                rec = CREATURES + creature * game.CREATURE_SIZE
                m[rec + game.CREATURE_NAME:rec + game.CREATURE_NAME + 5] = b"Guard"
                struct.pack_into("<h", m, rec, 30)
                struct.pack_into("<Bh", m, table + (0x30 + k) * 3, 2, creature)
            struct.pack_into("<h", m, CREATURES + STALKER * game.CREATURE_SIZE, 20)
            log.tracker.check(1.0)
            return log, m, table

        def drop(m, table, combatants):
            for c in combatants:
                struct.pack_into("<Bh", m, table + c * 3, 0, 0)

        # a new area: the table emptied, the records zeroed
        log, m, table = setup([4, 5])
        struct.pack_into("<H", m, DS * 16 + game.REGION, 0x2A)
        drop(m, table, (0x29, 0x30, 0x31))
        for creature in (4, 5, STALKER):
            rec = CREATURES + creature * game.CREATURE_SIZE
            m[rec:rec + game.CREATURE_SIZE] = bytes(game.CREATURE_SIZE)
        self.assertEqual(log.tracker.check(2.0), [])
        # the area number not yet changed: all of them gone at once, their records cleared of HP
        log, m, table = setup([4, 5])
        drop(m, table, (0x29, 0x30, 0x31))
        for creature in (4, 5, STALKER):
            struct.pack_into("<h", m, CREATURES + creature * game.CREATURE_SIZE, 0)
        self.assertEqual(log.tracker.check(2.0), [])
        # one gone with its record reused by someone else
        log, m, table = setup([4])
        drop(m, table, (0x30,))
        rec = CREATURES + 4 * game.CREATURE_SIZE
        m[rec + game.CREATURE_NAME:rec + game.CREATURE_NAME + 5] = b"Slave"
        struct.pack_into("<h", m, rec, 0)
        self.assertEqual(log.tracker.check(2.0), [])
        # one gone, its own record dead: killed
        log, m, table = setup([4])
        drop(m, table, (0x30,))
        struct.pack_into("<h", m, CREATURES + 4 * game.CREATURE_SIZE, -2)
        self.assertEqual([l.split(" (")[0] for l in log.tracker.check(2.0)], ["Guard is killed"])

    def test_pockets_tried_after_a_save_forgotten_on_loading_it(self):
        """A pocket tried (and the thief caught) after the game was saved can be tried again once
        that save is loaded: the game's clock goes back past the try."""
        log = make_game()
        log.load_picked(["Dag|41|7|Trader@500", "Dag|41|8|Guard"])  # (the second from an older version)
        set_clock(log, 1000)
        log.lines(now=1.0)
        self.assertIsNone(log.take_picked())
        log._remember_pick("Dag|41|9|Slave")
        self.assertEqual(log.take_picked(), ["Dag|41|7|Trader@500", "Dag|41|8|Guard", "Dag|41|9|Slave@1000"])
        set_clock(log, 1300)
        log.lines(now=2.0)
        self.assertIsNone(log.take_picked())  # time moving on forgets nothing
        set_clock(log, 800)  # the game saved at 800, loaded
        log.lines(now=3.0)
        self.assertEqual(log.take_picked(), ["Dag|41|7|Trader@500"])
        self.assertEqual(log.picked, {"Dag|41|7|Trader"})

    def test_pockets_of_another_game_forgotten_in_a_new_one(self):
        """The Loader started with a new game under way (same party names): the tries of the
        last game, later than this game's clock, are forgotten at once; earlier ones stay."""
        log = make_game()
        log.load_picked(["Dag|41|7|Kurzak@5000", "Dag|41|8|Guard@100"])
        set_clock(log, 300)  # a new game, 300 seconds in
        log.lines(now=1.0)
        self.assertEqual(log.picked, {"Dag|41|8|Guard"})
        self.assertEqual(log.take_picked(), ["Dag|41|8|Guard@100"])

    def test_xp_taken_and_given_back(self):
        """Going between areas the game takes the XP away and gives it back: nothing logged. A
        loss that stays is logged once LOSS_WAIT has passed; a gain after a loss, as the net."""
        log = make_game()
        tracker, m = log.tracker, log.guest.mem
        struct.pack_into("<I", m, SHEETS, 1000)
        self.assertEqual(tracker.check(1.0), [])
        struct.pack_into("<I", m, SHEETS, 443)  # -557
        self.assertEqual(tracker.check(2.0) + tracker.check(3.0), [])
        struct.pack_into("<I", m, SHEETS, 1000)  # back
        self.assertEqual(tracker.check(4.0) + tracker.check(5.0) + tracker.check(200.0), [])
        struct.pack_into("<I", m, SHEETS, 900)  # a loss that stays
        self.assertEqual(tracker.check(201.0) + tracker.check(202.0), [])
        self.assertEqual(tracker.check(202.0 + tracker_module.LOSS_WAIT), ["XP: Dag -100"])
        struct.pack_into("<I", m, SHEETS, 800)
        tracker.check(300.0), tracker.check(301.0)
        struct.pack_into("<I", m, SHEETS, 1050)  # back, and 150 more
        self.assertEqual(tracker.check(302.0) + tracker.check(303.0), ["XP: Dag +150"])

    def test_level_up_without_hit_points(self):
        log = make_game()
        tracker, m = log.tracker, log.guest.mem
        m[SHEETS + game.SHEET_CLASSES:SHEETS + game.SHEET_CLASSES + 3] = bytes((10, 11, 0))
        m[SHEETS + game.SHEET_LEVELS:SHEETS + game.SHEET_LEVELS + 3] = bytes((3, 1, 0))
        self.assertEqual(tracker.check(1.0), [])
        m[SHEETS + game.SHEET_LEVELS + 1] = 2  # Preserver 2nd, still a 3rd level Gladiator
        self.assertEqual(tracker.check(2.0), ["Dag is now a 2nd level Preserver",
                                              "    max HP unchanged: the game divides the hit point total by "
                                              "the classes, and this level's roll left a fraction, which counts "
                                              "at a later level"])
        m[SHEETS + game.SHEET_LEVELS] = 4
        struct.pack_into("<h", m, SHEETS + game.SHEET_MAX_HP, struct.unpack_from("<h", m, SHEETS + 8)[0] + 5)
        self.assertEqual(tracker.check(3.0)[0], "Dag is now a 4th level Gladiator")

    def test_messages_and_dialogue_from_the_text_buffer(self):
        log = make_game()
        data = b""
        for kind, value, text in ((KIND_MESSAGE, 0, b"Long Sword is broken !"), (KIND_MESSAGE, 0, b""),
                                  (KIND_PORTRAIT, 119, b""),
                                  (KIND_TEXT, 115, b"Watch and enjoy! "), (KIND_TEXT, 115, b"END")):
            data += bytes((0xFE, kind)) + struct.pack("<IHH", 0, value, len(text)) + text
        log.guest.mem[HDR + 0x800:HDR + 0x800 + len(data)] = data
        struct.pack_into("<H", log.guest.mem, HDR + 126, len(data))
        messages = [line for line in log.lines(now=100.0) if line.startswith("Message:")]
        self.assertEqual(messages, ["Message: Long Sword is broken !"])  # an empty box is left out
        (said,) = log.take_dialogue()
        self.assertEqual((log.speaker(said.portrait), said.text), ("The Announcer", "Watch and enjoy!"))
        self.assertEqual(log.speaker(0), "Narration")
        self.assertEqual(log.speaker(57), "Portrait 57")
        log.speaker_names = {57: "Tithian", 119: "Herald"}  # names the player gave
        self.assertEqual((log.speaker(57), log.speaker(119)), ("Tithian", "Herald"))

    def test_round_status_keeps_the_order_in_view(self):
        log = make_game()
        log.game.game_time = lambda: 600
        log.game.whose_turn = lambda: 1
        log._round_time, log.round_number = 600, 3
        log.round_order = [(0, "Dag", 25), (1, "Daaki", 22), (2, "Jellybelly", 20), (0x29, "Mountain Stalker", 18)]
        log._acted = {0}
        struct.pack_into("<h", log.guest.mem, CREATURES + 2 * game.CREATURE_SIZE, 0)  # Jellybelly is down
        struct.pack_into("<h", log.guest.mem, CREATURES + 0 * game.CREATURE_SIZE, 30)
        struct.pack_into("<h", log.guest.mem, CREATURES + 1 * game.CREATURE_SIZE, 30)
        struct.pack_into("<h", log.guest.mem, CREATURES + STALKER * game.CREATURE_SIZE, 30)
        status = log.round_status()
        self.assertEqual(status["round"], 3)
        self.assertEqual(status["now"], ("Daaki", 22))
        self.assertEqual(status["next"], [("Mountain Stalker", 18)])
        self.assertEqual(status["done"], [("Dag", 25)])
        self.assertEqual(status["down"], [("Jellybelly", 20)])
        table = log.game.combatant_creature  # killed: the creature has left the fight's table
        log.game.combatant_creature = lambda c: None if c == 0x29 else table(c)
        self.assertEqual(log.round_status()["down"], [("Jellybelly", 20), ("Mountain Stalker", 18)])
        log.game.combatant_creature = table
        log.game.game_time = lambda: 600 + dicelog.FIGHT_GAP + 1  # the fight is over
        self.assertIsNone(log.round_status())

    def test_speakers_learned_from_conversations(self):
        log = make_game()
        struct.pack_into("<H", log.guest.mem, HDR + dicelog.TSR_SLOTS_OFF, 0x1800)  # spell slots out of the way
        talking_to = [None]
        log.game.talk_target = lambda: talking_to[0]
        def conversation(*portraits):
            data = b""
            for p in portraits:
                for kind, value, text in ((KIND_PORTRAIT, p, b""), (KIND_TEXT, 0, b"Hello. "), (KIND_TEXT, 0, b"END")):
                    data += bytes((0xFE, kind)) + struct.pack("<IHH", 0, value, len(text)) + text
            data += bytes((0xFE, KIND_TEXT)) + struct.pack("<IHH", 0, 0, 5) + b"CLOSE"
            start = struct.unpack_from("<H", log.guest.mem, HDR + 126)[0]
            log.guest.mem[HDR + 0x800 + start:HDR + 0x800 + start + len(data)] = data
            struct.pack_into("<H", log.guest.mem, HDR + 126, start + len(data))
            log.lines(now=100.0)
            log.take_dialogue()
        talking_to[0] = "Legcrusher"
        conversation(5, 100)  # two faces: a scene, can't tell who is who
        self.assertEqual(log.take_speakers(), {})
        conversation(0, 100)  # one face (and narration): that's Legcrusher talking
        self.assertEqual(log.take_speakers(), {100: "Legcrusher"})
        self.assertEqual(log.speaker(100), "Legcrusher")
        talking_to[0] = None
        conversation(57)  # not started on anyone
        self.assertEqual(log.take_speakers(), {})
        log.speaker_names = {100: "Legs"}  # the player's name comes first
        self.assertEqual(log.speaker(100), "Legs")

    def test_the_reply_chosen(self):
        log = make_game()
        m = log.guest.mem
        for n, text in enumerate((b"Yes", b"No", b"Maybe")):
            at = DS * 16 + game.REPLY_TEXTS + n * game.REPLY_SIZE
            m[at:at + len(text) + 1] = text + b"\0"
        m[DS * 16 + game.REPLY_CHOSEN] = 0xFF
        log.lines(now=1.0)
        self.assertEqual(log.take_dialogue(), [])
        m[DS * 16 + game.REPLY_CHOSEN] = 0  # the second row clicked, the list scrolled down one
        m[DS * 16 + game.REPLY_SCROLL] = 1
        log.lines(now=1.1)
        self.assertEqual([d.chosen for d in log.take_dialogue()], ["No"])
        log.lines(now=1.2)  # still flashing: not again
        self.assertEqual(log.take_dialogue(), [])
        m[DS * 16 + game.REPLY_CHOSEN] = 0xFF
        log.lines(now=1.3)
        self.assertEqual(log.take_dialogue(), [])

    def test_no_hp_or_psp_news_while_a_game_loads(self):
        log = make_game()
        m = log.guest.mem
        log.lines(now=10.0)
        m[CREATURES + game.CREATURE_NAME:CREATURES + game.CREATURE_NAME + 4] = b"Tavi"  # another game
        struct.pack_into("<h", m, CREATURES + game.CREATURE_PSP, 40)
        struct.pack_into("<h", m, CREATURES, 25)
        self.assertEqual([l for l in log.lines(now=10.5) if "HP" in l or "PSP" in l], [])
        struct.pack_into("<h", m, CREATURES + game.CREATURE_PSP, -4096)  # half-loaded, after the pause
        log.lines(now=20.0)
        struct.pack_into("<h", m, CREATURES + game.CREATURE_PSP, 418)
        self.assertEqual([l for l in log.lines(now=21.0) if "PSP" in l], [])


class InitiativeTests(unittest.TestCase):
    def setUp(self):
        self.log = log = make_game()
        m = log.guest.mem
        m[CREATURES + game.CREATURE_ABILITIES + 1] = 17  # Dag: DEX 17
        m[CREATURES + game.CREATURE_SIZE + game.CREATURE_ABILITIES + 1] = 12  # Daaki: DEX 12
        m[DS * 16 + game.DEX_INITIATIVE + 17] = 2
        m[DS * 16 + game.DEX_INITIATIVE + 16] = 1  # the stalker's DEX 16
        set_effects(log, [(0, 1, 22)])  # Dag is hasted
        self.table = (LOAD_SEG + game.INITIATIVE_SEG) * 16 + game.INITIATIVE_OFF

    def roll(self, creature, roll, tie, score):
        """The game's two rolls for a creature, and the score it keeps."""
        struct.pack_into("<hh", self.log.guest.mem, self.table + creature * 4, score, tie)
        out = self.log.describe(entry(raw_for(roll + 1, 10), dicelog.INITIATIVE_ROLL), now=1.0)
        return out + self.log.describe(entry(raw_for(tie + 1, 200), dicelog.INITIATIVE_TIE), now=1.0)

    def test_round_order(self):
        self.assertEqual(self.roll(0, 3, 50, 27), [])  # 20 + 3 + 2 DEX + 2 Hasted
        self.assertEqual(self.roll(1, 7, 120, 27), [])
        self.assertEqual(self.roll(STALKER, 9, 10, 30), [])
        self.assertEqual(self.log.lines(now=1.1), [])  # waits for the rest of the round's rolls
        self.assertEqual(self.log.lines(now=2.0), [
            "Initiative: Mountain Stalker 30, Daaki 27, Dag 27",
            "    Mountain Stalker 30 = 20 + 9 (0-9 roll) +1 DEX",
            "    Daaki 27 = 20 + 7 (0-9 roll), tie broken by 120 (0-199 roll)",
            "    Dag 27 = 20 + 3 (0-9 roll) +2 DEX +2 Hasted, tie broken by 50 (0-199 roll)"])

    def test_shown_before_the_rounds_first_attack(self):
        self.roll(0, 3, 50, -1)  # already acted: its score is gone, but the tie-break roll stays
        out = self.log.describe(entry(raw_for(14, 20), dicelog.ATTACK_SITE,
                                      words(0, 0, 0, 0, 0x29, 0, 0, 0, 0, 0, 0)), now=1.1)
        self.assertEqual(out[:2], ["Initiative: Dag 27",
                                   "    Dag 27 = 20 + 3 (0-9 roll) +2 DEX +2 Hasted"])


CLOCK = 0x6F000  # where the fake game keeps its clock


def set_clock(log, seconds):
    m = log.guest.mem
    m[DS * 16 + game.GAME_TIME_PTR:DS * 16 + game.GAME_TIME_PTR + 4] = far(CLOCK)
    m[DS * 16 + game.GAME_TIME_SCALE] = 1
    struct.pack_into("<i", m, CLOCK, seconds)


class RoundAndTurnTests(unittest.TestCase):
    def setUp(self):
        self.log = make_game()
        self.table = (LOAD_SEG + game.INITIATIVE_SEG) * 16 + game.INITIATIVE_OFF

    def round(self, seconds):
        set_clock(self.log, seconds)
        struct.pack_into("<hh", self.log.guest.mem, self.table, 25, 50)
        self.log.describe(entry(raw_for(6, 10), dicelog.INITIATIVE_ROLL), now=1.0)
        self.log.describe(entry(raw_for(51, 200), dicelog.INITIATIVE_TIE), now=1.0)
        return self.log.initiative_lines()[0]

    def test_rounds_count_up_and_restart_after_a_gap(self):
        self.assertEqual(self.round(600), "Round 1: Dag 25")
        self.assertEqual(self.round(660), "Round 2: Dag 25")
        self.assertEqual(self.round(5000), "Round 1: Dag 25")  # a new fight

    def test_monsters_acs_forgotten_in_a_new_fight(self):
        """The game reuses creature records: an AC from an earlier fight (the opening fight's
        Defiler, AC -9) isn't the new monster's in its Look box; the party's are kept."""
        self.round(600)
        self.log.last_ac.update({0: 4, 7: -9})
        self.assertEqual(self.round(660), "Round 2: Dag 25")
        self.assertEqual(self.log.last_ac, {0: 4, 7: -9})  # the same fight
        self.round(5000)
        self.assertEqual(self.log.last_ac, {0: 4})

    def test_whose_turn(self):
        m = self.log.guest.mem
        struct.pack_into("<h", m, DS * 16 + game.WHOSE_TURN, 0x29)
        set_clock(self.log, 600)
        self.assertEqual(self.log.turn_lines(), [])  # no fight yet
        self.round(600)
        struct.pack_into("<h", m, DS * 16 + game.WHOSE_TURN, 1)
        self.assertEqual(self.log.turn_lines(), ["Daaki's turn"])
        self.assertEqual(self.log.turn_lines(), [])  # still Daaki's
        struct.pack_into("<h", m, DS * 16 + game.WHOSE_TURN, 0x29)
        self.assertEqual(self.log.turn_lines(), ["Mountain Stalker's turn"])

    def test_last_turn_then_first_turn(self):
        """Last in one round and first in the next: a new turn (a thief hides again); someone
        else first: the last round's last turn isn't taken for a new one meanwhile; one first
        who can't act (out cold) passed over."""
        m = self.log.guest.mem
        stalker = CREATURES + STALKER * game.CREATURE_SIZE
        struct.pack_into("<h", m, stalker, 30)
        m[stalker + game.CREATURE_STATUS] = game.STATUS_OKAY
        self.round(600)
        struct.pack_into("<h", m, DS * 16 + game.WHOSE_TURN, 1)
        self.assertEqual(self.log.turn_lines(), ["Daaki's turn"])
        self.round(660)
        self.log.round_order = [(1, "Daaki", 25)]
        self.assertEqual(self.log.turn_lines(), ["Daaki's turn"])
        self.round(720)
        self.log.round_order = [(0x29, "Mountain Stalker", 25), (1, "Daaki", 20)]
        self.assertEqual(self.log.turn_lines(), [])  # (still showing Daaki's last)
        struct.pack_into("<h", m, DS * 16 + game.WHOSE_TURN, 0x29)
        self.assertEqual(self.log.turn_lines(), ["Mountain Stalker's turn"])
        # (the Stalker first in the next order but out cold: Daaki, last now, goes next)
        struct.pack_into("<h", m, DS * 16 + game.WHOSE_TURN, 1)
        self.assertEqual(self.log.turn_lines(), ["Daaki's turn"])
        self.round(780)
        m[stalker + game.CREATURE_STATUS] = game.OUT_COLD
        self.log.round_order = [(0x29, "Mountain Stalker", 25), (1, "Daaki", 20)]
        self.assertEqual(self.log.turn_lines(), ["Daaki's turn"])
        # (a name in the order matched to no one, as in the arena's opening show: passed over)
        self.round(840)
        self.log.round_order = [(None, "Defiler", 29), (1, "Daaki", 20)]
        self.assertEqual(self.log.turn_lines(), ["Daaki's turn"])

    def test_the_rounds_order_comes_before_its_first_turn(self):
        m = self.log.guest.mem
        self.round(600)
        set_clock(self.log, 660)  # the next round's rolls are in, but its order isn't shown yet
        self.log.describe(entry(raw_for(6, 10), dicelog.INITIATIVE_ROLL), now=5.0)
        self.log.describe(entry(raw_for(51, 200), dicelog.INITIATIVE_TIE), now=5.0)
        struct.pack_into("<h", m, DS * 16 + game.WHOSE_TURN, 1)
        self.assertEqual(self.log.turn_lines(), [])
        self.assertEqual(self.log.initiative_lines()[0], "Round 2: Dag 25")
        self.assertEqual(self.log.turn_lines(), ["Daaki's turn"])


class HitChanceTests(unittest.TestCase):
    def test_hit_chance(self):
        self.assertEqual(dicelog.hit_chance(4), 85)
        self.assertEqual(dicelog.hit_chance(1), 95)  # a 1 always misses
        self.assertEqual(dicelog.hit_chance(25), 5)  # a 20 always hits


CREATION = 0x6C000  # the character being made


def make_creation():
    """A dwarf Fighter/Thief on the creation screen; sheet 1 holds a Fighter/Thief whose hit points roll."""
    log = make_game()
    m = log.guest.mem
    m[DS * 16 + game.CREATION_SHEET_PTR:DS * 16 + game.CREATION_SHEET_PTR + 4] = far(CREATION)
    m[CREATION + game.SHEET_RACE] = 2
    m[CREATION + game.SHEET_CLASSES:CREATION + game.SHEET_CLASSES + 2] = bytes((3, 8))  # creation numbering
    tables = (LOAD_SEG + game.CREATION_SEG) * 16
    m[tables + game.CREATION_RACE_OFF + 2 * 6:tables + game.CREATION_RACE_OFF + 3 * 6] = \
        struct.pack("6b", 1, -1, 2, 0, 0, -2)
    for cls, prime, least in ((3, 0, 9), (8, 1, 9)):
        struct.pack_into("<hB", m, tables + game.CREATION_CLASS_OFF + cls * 3, prime, least)
    sheet = SHEETS + 1 * game.SHEET_SIZE
    m[sheet + game.SHEET_RACE], m[sheet + game.SHEET_ABILITIES + 2] = 2, 10
    m[sheet + game.SHEET_CLASSES:sheet + game.SHEET_CLASSES + 2] = bytes((9, 17))
    hp = (LOAD_SEG + game.LEVEL_HP_SEG) * 16  # thieves roll d6; CON 17: +3 a level
    m[hp + 0x10 + 17], m[hp + 12:hp + 15], m[hp + game.LEVEL_HP_CON_BONUS + 17] = 3, bytes((6, 9, 2)), 3
    m[CREATURES + 1 * game.CREATURE_SIZE + game.CREATURE_ABILITIES + 2] = 17
    return log


def ability_rolls(log, ability, tries):
    """The four 4d4 rolls for an ability; returns the lines from the last die."""
    out = []
    parent = words(0x04BB, 0x54FA, 3, ability, 1, 10, 2)
    for faces in tries:
        for face in faces:
            out = log.describe(entry(raw_for(face, 4), dicelog.DICE_SITE, words(0, 0, 4, 4), parent,
                                     parent_code=dicelog.CREATION_ABILITY_RETURN[0]))
    return out


class CreationTests(unittest.TestCase):
    def test_abilities(self):
        log = make_creation()
        # best of 7, 11, 9, 10 = 11, +4, +1 dwarf = 16: a Fighter's STR is at least 17
        self.assertEqual(ability_rolls(log, 0, [(1, 2, 2, 2), (4, 4, 2, 1), (3, 3, 2, 1), (4, 3, 2, 1)]), [])
        # CON: +2 dwarf, above the classes' least of 9
        ability_rolls(log, 2, [(4, 4, 4, 1), (1, 1, 1, 1), (2, 2, 2, 2), (3, 3, 3, 3)])
        # CHA: 4 + 4 - 2 dwarf = 6, raised to the least the Fighter and Thief allow
        ability_rolls(log, 5, [(1, 1, 1, 1)] * 4)
        # (the lines come when the die stops)
        self.assertEqual(log.creation_lines(),
                         ["Character creation, STR 17: best of four 4d4 (7, 11, 9, 10) = 11, +4, +1 dwarf = 16, "
                          "raised to 17 (the Fighter's prime requisite)",
                          "Character creation, CON 19: best of four 4d4 (13, 4, 8, 12) = 13, +4, +2 dwarf = 19",
                          "Character creation, CHA 9: best of four 4d4 (4, 4, 4, 4) = 4, +4, -2 dwarf = 6, "
                          "raised to 9 (the Thief's least)"])

    def test_only_the_character_the_die_stops_on(self):
        """The die rolls whole characters while it tumbles: only the last is logged, each ability
        checked against the one the game shows (one whose rolls were missed, the game's)."""
        log = make_creation()
        ability_rolls(log, 0, [(4, 4, 4, 4)] * 4)  # a first character's STR 21...
        ability_rolls(log, 2, [(4, 4, 4, 4)] * 4)  # ... and CON 22
        ability_rolls(log, 0, [(1, 2, 2, 2), (4, 4, 2, 1), (3, 3, 2, 1), (4, 3, 2, 1)])  # the next: STR 17
        shown = CREATION + game.SHEET_SIZE + game.CREATURE_ABILITIES
        log.guest.mem[shown:shown + 6] = bytes((17, 12, 18, 10, 11, 9))  # its CON's rolls missed
        lines = log.creation_lines()
        self.assertEqual(lines[:3],
                         ["Character creation, STR 17: best of four 4d4 (7, 11, 9, 10) = 11, +4, +1 dwarf = 16, "
                          "raised to 17 (the Fighter's prime requisite)",
                          "Character creation, DEX 12 (its rolls came too fast to record)",
                          "Character creation, CON 18 (its rolls came too fast to record)"])
        self.assertIn("Character creation: the six scores add up to 77", lines)  # (as the game shows them)

    def test_rolls_too_fast_for_the_ring(self):
        """The die tumbles faster than the ring is read: DSCLOG's own count and copy of each
        ability's four 4d4 (RL_TRY) give the lines for the character it stops on, and the rolls
        missed meanwhile go unmentioned."""
        log = make_creation()
        m = log.guest.mem
        log.lines(now=1.0)  # (the count as it was)
        shown = CREATION + game.SHEET_SIZE + game.CREATURE_ABILITIES
        m[shown:shown + 6] = bytes((17, 12, 18, 10, 11, 9))
        m[HDR + dicelog.TSR_TRIES:HDR + dicelog.TSR_TRIES + 24] = bytes(
            (7, 11, 9, 10, 8, 4, 5, 6, 12, 4, 4, 4, 6, 5, 5, 4, 7, 7, 6, 5, 4, 4, 4, 4))
        struct.pack_into("<H", m, HDR + dicelog.TSR_TRIES_SEQ, 24)
        log.missed = 40
        out = log.lines(now=2.0)
        self.assertNotIn("(40 rolls came too fast to record)", out)
        out = log.lines(now=2.5)
        self.assertEqual(out[:7], [
            "Character creation, STR 17: best of four 4d4 (7, 11, 9, 10) = 11, +4, +1 dwarf = 16, "
            "raised to 17 (the Fighter's prime requisite)",
            "Character creation, DEX 12 (its rolls came too fast to record)",  # (not the 17 they'd give)
            "Character creation, CON 18: best of four 4d4 (12, 4, 4, 4) = 12, +4, +2 dwarf = 18",
            "Character creation, INT 10: best of four 4d4 (6, 5, 5, 4) = 6, +4 = 10",
            "Character creation, WIS 11: best of four 4d4 (7, 7, 6, 5) = 7, +4 = 11",
            "Character creation, CHA 9: best of four 4d4 (4, 4, 4, 4) = 4, +4, -2 dwarf = 6, "
            "raised to 9 (the Thief's least)",
            "Character creation: the six scores add up to 77"])
        self.assertEqual(log.lines(now=3.0), [])  # (once)

    def test_hit_points(self):
        log = make_creation()
        for cls, sides, level, face in ((9, 10, 1, 10), (9, 10, 2, 5), (17, 6, 1, 3), (17, 6, 2, 6)):
            e = entry(raw_for(face, sides), dicelog.DICE_SITE, words(0, 0, 1, sides),
                      words(dicelog.CREATION_HP_CALLER, 0x54FA, 1, cls, level), parent_code=dicelog.LEVEL_HP_RETURN)
            self.assertEqual(log.describe(e), [])
        # (24 / 2 classes) + CON 17's +3 for each of the Fighter's 2 levels
        self.assertEqual(log.creation_hp_lines(),
                         ["Character creation, hit points 18: Fighter d10 per level: 10 + 5; Thief d6 per level: "
                          "3 + 6 = 24, / 2 classes = 12, +6 CON 17 = 18"])

    def test_hit_points_against_the_game(self):
        """A hit point roll missed: the game's own total, with the rolls that were caught."""
        log = make_creation()
        for cls, sides, level, face in ((9, 10, 1, 10), (17, 6, 1, 3), (17, 6, 2, 6)):
            e = entry(raw_for(face, sides), dicelog.DICE_SITE, words(0, 0, 1, sides),
                      words(dicelog.CREATION_HP_CALLER, 0x54FA, 1, cls, level), parent_code=dicelog.LEVEL_HP_RETURN)
            log.describe(e)
        struct.pack_into("<h", log.guest.mem, CREATION + game.SHEET_MAX_HP, 21)
        self.assertEqual(log.creation_hp_lines(),
                         ["Character creation, hit points 21 (some of its rolls came too fast to record; those "
                          "caught: Fighter d10 per level: 10; Thief d6 per level: 3 + 6 = 19, / 2 classes = 9 "
                          "(rounded down), +5 CON 17 = 14)"])

    def test_hit_points_shared(self):
        """RULE_MULTI_HP: as Demihuman Deities, CON's bonus (a warrior's, the character having a warrior
        class) on each die, the total shared between the classes."""
        log = make_creation()
        log.set_rules(game.RULE_MULTI_HP)
        for cls, sides, level, face in ((9, 10, 1, 10), (9, 10, 2, 5), (17, 6, 1, 1), (17, 6, 2, 6)):
            e = entry(raw_for(face, sides), dicelog.DICE_SITE, words(0, 0, 1, sides),
                      words(dicelog.CREATION_HP_CALLER, 0x54FA, 1, cls, level), parent_code=dicelog.LEVEL_HP_RETURN)
            self.assertEqual(log.describe(e), [])
        # (22 + CON 17's +3 on each of the 4 dice) / 2
        self.assertEqual(log.creation_hp_lines(),
                         ["Character creation, hit points 17: Fighter d10 per level: 10 + 5; Thief d6 per level: "
                          "1 + 6 = 22, +3 CON 17 on each of 4 dice = 34, / 2 classes = 17"])

    def test_hit_points_best_of_two(self):
        """RULE_HP_BEST: each level's die rolled twice, the better kept."""
        log = make_creation()
        log.set_rules(game.RULE_HP_BEST)
        for cls, sides, level, faces in ((9, 10, 1, (2, 10)), (9, 10, 2, (5, 1)), (17, 6, 1, (3, 3)), (17, 6, 2, (1, 6))):
            for face in faces:
                e = entry(raw_for(face, sides), dicelog.DICE_SITE, words(0, 0, 1, sides),
                          words(dicelog.CREATION_HP_CALLER, 0x54FA, 1, cls, level),
                          parent_code=dicelog.LEVEL_HP_RETURNS[1])
                self.assertEqual(log.describe(e), [])
        self.assertEqual(log.creation_hp_lines(),
                         ["Character creation, hit points 18: Fighter d10 per level: 10 (the better of 2 and 10) + "
                          "5 (the better of 5 and 1); Thief d6 per level: 3 (the better of 3 and 3) + "
                          "6 (the better of 1 and 6) = 24, / 2 classes = 12, +6 CON 17 = 18"])

    def test_random_name(self):
        log = make_creation()
        e = entry(raw_for(16, 33), dicelog.DICE_SITE, words(0, 0, 1, 33), parent_code=dicelog.RANDOM_NAME_RETURNS[0])
        self.assertEqual(log.describe(e), ["Character creation: a name picked at random, 1d33 = 16"])


if __name__ == "__main__":
    unittest.main()
