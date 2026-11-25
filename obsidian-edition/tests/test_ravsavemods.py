"""The dice log's saving throw modifiers and THAC0 line for Wake of the Ravager (dsloader.ravlog): the
sequel's save modifiers' routine (628h:A7h, 83606h) modelled by RavGameData.save_modifiers, and the attack
set-up's locals (5C5E1h) and to-hit routine (628h:66h) behind RavDiceLog's THAC0 line, the cahulaks' heads
named."""
import os
import struct
import sys
import types
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import dicelog, game, ravager, ravlog  # noqa: E402

DS = 0x4982


class FakeGuest:
    def __init__(self, size=0x110000):
        self.mem = bytearray(size)

    def read(self, addr, size):
        return bytes(self.mem[addr:addr + size])

    def write(self, addr, data):
        self.mem[addr:addr + len(data)] = data


def spell(category=0, kinds=0, target_kind=0, reach=40):
    """A spell record's first 32 bytes: its range (+9), target kind (+0Ch), no area (+17h), category (+11h)
    and kinds (+1Ah) words."""
    rec = bytearray(32)
    struct.pack_into("<H", rec, 9, reach)
    rec[0x0C], rec[0x17] = target_kind, 0xFF
    struct.pack_into("<H", rec, 0x11, category)
    struct.pack_into("<H", rec, 0x1A, kinds)
    return bytes(rec)


def item(kind, slot, plus):
    rec = bytearray(ravager.ITEM_SIZE)
    struct.pack_into("<H", rec, 0x0A, kind)
    rec[0x13], rec[0x16] = slot, plus & 0xFF
    return rec


class SaveModifierTests(unittest.TestCase):
    """RavGameData.save_modifiers: target combatant 1 (creature 1), caster 30 (creature 30)."""

    def setUp(self):
        ravlog.apply_layout()
        self.addCleanup(ravlog.restore_layout)
        g = FakeGuest()
        for table, values in ((game.SAVE_WIS, {18: 4}), (game.SAVE_CON, {18: 0, 17: 0}), (game.DEX_AC, {17: -3})):
            for score, value in values.items():
                g.mem[DS * 16 + table + score] = value & 0xFF
        self.data = data = ravlog.RavGameData(g, DS, rules=0)
        self.sheets = {1: bytearray(ravager.SHEET_SIZE), 30: bytearray(ravager.SHEET_SIZE)}
        self.creatures = {1: bytearray(ravager.CREATURE_SIZE), 30: bytearray(ravager.CREATURE_SIZE)}
        for c in self.creatures.values():
            c[game.CREATURE_ABILITIES:game.CREATURE_ABILITIES + 6] = bytes((12, 17, 12, 12, 18, 12))
        self.effects, self.worn, self.record = [], [], spell()
        data.combatant_creature = lambda c: c if c in (1, 30) else None
        data.sheet = lambda c: bytes(self.sheets[c])
        data.creature = lambda c: bytes(self.creatures[c])
        data.spell_record = lambda s: self.record
        data.effects = lambda: [game.Effect(owner, caster, eid) for owner, caster, eid, _ in self.effects]
        data._first_effect = lambda who, eid: next((self.raw(e) for e in self.effects if e[0] == who and e[2] == eid), None)
        data._worn = lambda c, lists=None: self.worn if c == 1 else []
        data.kit_ids = lambda c: []

    def raw(self, e):
        rec = bytearray(10)
        struct.pack_into("<hh", rec, 0, e[0], e[1])
        rec[6], rec[8] = e[2], e[3]
        return bytes(rec)

    def mods(self, spell_no=5, save=4):
        return self.data.save_modifiers(1, 30, spell_no, save)

    def test_psionic_blast_like(self):
        """A mind spell (category 10h: WIS) on a member with a ring of protection +2 and one +3 (the better
        counts), a cloak +2 in no armour, Blessed, Barkskin and her own side's Prayer: each named."""
        self.record = spell(category=0x4010)
        self.worn = [(1, item(45, 4, 2), bytes(20)), (2, item(45, 11, 3), bytes(20)),
                     (3, item(103, 12, 2), bytes(20)), (4, item(45, 11, 0), bytes(20))]
        self.effects = [(1, 1, 9, 0), (1, 1, 6, 0), (1, 1, 72, 0)]
        self.assertEqual(self.mods(), [(3, "Ring of Protection"), (2, "Cloak of Protection"), (1, "Barkskin"),
                                       (1, "Blessed"), (1, "Prayer, its caster's side"), (4, "WIS 18")])

    def test_cloak_not_in_metal_armour(self):
        """The cloak doesn't count with metal armour on the chest (PROT_SCAN's P_METAL_ARMOUR)."""
        plate = bytearray(20)
        plate[0x0F], plate[8], plate[9] = 0x80, 2, 9
        self.worn = [(3, item(103, 12, 2), bytes(20)), (5, item(20, 9, 0), bytes(plate))]
        self.assertEqual(self.mods(), [])

    def test_robes(self):
        """The Veiled Robe +1 on every save, the Ashen Robe against a wizard's or priest's spell only."""
        self.worn = [(1, item(127, 9, 2), bytes(20))]
        self.assertEqual(self.mods(0x100), [(1, "Veiled Robe")])
        self.worn = [(1, item(127, 9, 1), bytes(20))]
        self.assertEqual(self.mods(5), [(1, "Ashen Robe")])
        self.assertEqual(self.mods(0x100), [])

    def test_lightning(self):
        """Lightning Bolt (kinds 80h): Protected vs Lightning +4, Protected vs Weather +6, a druid +2; life
        drained 2 levels -4; Vulnerable to Weather -20."""
        self.record = spell(kinds=0x80)
        self.sheets[1][game.SHEET_CLASSES], self.sheets[1][game.SHEET_LEVELS] = 6, 5
        self.effects = [(1, 1, 78, 0), (1, 1, 80, 0), (1, 1, 59, 2), (1, 1, 107, 0)]
        self.assertEqual(self.mods(32), [(-4, "Life Drained (2)"), (6, "Protected vs Weather"),
                                         (-20, "Vulnerable to Weather"), (4, "Protected vs Lightning"),
                                         (2, "druid against fire and electricity")])
        self.assertEqual(dict((w, a) for a, w in self.mods(5)).get("Protected vs Weather"), None)

    def test_unseen_by_the_caster(self):
        """+4 against a caster who is Blind, or can't see the Invisible target, for a spell of range 8 or
        less at level 1 (680h:20h): not a farther one, not a caster with Detect Invisible."""
        self.record = spell(reach=6)
        self.effects = [(30, 30, 10, 0)]
        self.assertEqual(self.mods(), [(4, "the caster is Blind")])
        self.effects = [(1, 1, 53, 0)]
        self.assertEqual(self.mods(), [(4, "Invisible to the caster")])
        self.effects = [(1, 1, 53, 0), (30, 30, 25, 0)]
        self.assertEqual(self.mods(), [])
        self.record = spell(reach=40)
        self.effects = [(1, 1, 53, 0)]
        self.assertEqual(self.mods(), [])
        self.record = spell(reach=40, target_kind=3)  # (a close target kind: range 8)
        self.assertEqual(self.mods(), [(4, "Invisible to the caster")])

    def test_dodge_psionicist_and_con(self):
        """DEX dodging (category 40h), a psionicist's +2 against the mind (category 6) and a dwarf's CON
        on paralysis/poison/death; CON as in AD&D takes a dwarf's table adjustment away."""
        self.record = spell(category=0x46)
        self.sheets[1][game.SHEET_CLASSES], self.sheets[1][game.SHEET_LEVELS] = 12, 3
        self.sheets[1][game.SHEET_RACE] = 2
        self.creatures[1][game.CREATURE_ABILITIES + 2] = 18
        self.assertEqual(self.mods(save=game.PPD_SAVE), [(2, "psionicist against the mind"), (3, "DEX 17 dodging"),
                                                         (4, "WIS 18"), (5, "dwarf CON 18")])

    def test_dual_class_psionicist(self):
        """A human's later class counts only while its level is below the first's (98h:C1h)."""
        sheet = self.sheets[1]
        sheet[game.SHEET_RACE] = 1
        sheet[game.SHEET_CLASSES:game.SHEET_CLASSES + 2] = bytes((9, 12))
        sheet[game.SHEET_LEVELS:game.SHEET_LEVELS + 2] = bytes((7, 4))
        self.assertEqual(self.data.dual_level(1, 12), 4)
        sheet[game.SHEET_LEVELS:game.SHEET_LEVELS + 2] = bytes((4, 7))
        self.assertEqual(self.data.dual_level(1, 12), 0)

    def test_spell_record_layout(self):
        """The sequel's records as the dice log serves them (RESOURCE.GFF's first 32 bytes) hold the words
        the routine reads: Psionic Blast's category has WIS's bits, Lightning Bolt's kinds electricity's."""
        path = os.path.join(os.environ.get("DSUN_WOTR", "/tmp/playtest/rav"), ravager.RESOURCE_FILE)
        if not os.path.isfile(path):
            self.skipTest("no Wake of the Ravager install")
        with open(path, "rb") as f:
            table, names = ravlog.spell_table(f.read())
        blast, bolt = names.index("Psionic Blast"), names.index("Lightning Bolt")
        self.assertTrue(struct.unpack_from("<H", table, blast * 32 + 0x11)[0] & game.SAVE_WIS_CATEGORY)
        self.assertTrue(struct.unpack_from("<H", table, bolt * 32 + 0x1A)[0] & 0x80)
        self.assertEqual(bolt, 32)


class AttackLineTests(unittest.TestCase):
    """RavDiceLog's THAC0 line from the sequel's set-up's locals: [BP-1Eh] the THAC0, [BP-8] the weapon's
    bonus, the flags bytes [BP-19h] and [BP-21h]."""

    def setUp(self):
        self.log = log = ravlog.RavDiceLog(FakeGuest())
        self.addCleanup(ravlog.restore_layout)
        data = ravlog.RavGameData(log.guest, DS, rules=0)
        rec = bytearray(ravager.CREATURE_SIZE)
        rec[game.CREATURE_THAC0] = 13
        self.effects = []
        data.creature = lambda c: bytes(rec)
        data.sheet = lambda c: bytes(ravager.SHEET_SIZE)
        data.effects = lambda: [game.Effect(*e) for e in self.effects]
        data._first_effect = lambda who, eid: None
        data.combatant_creature = lambda c: c
        data.kit_ids = lambda c: []
        data.wears_type = lambda *a: False
        data.two_weapons = lambda creature, slot, head=None: (f"cahulaks, {head} head at DEX 15", -2 if head == "main" else -4)
        log.game = data

    def line(self, thac0, after, bonus, item_type=24, rear=0, backstab=0, kit=()):
        locals_ = bytearray(0x28)
        struct.pack_into("<h", locals_, 0x28 - 0x1E, after)
        struct.pack_into("<h", locals_, 0x28 - 8, bonus)
        locals_[0x28 - 0x19], locals_[0x28 - 0x18] = rear, 0xFF  # (the next byte another local's)
        locals_[0x28 - 0x21], locals_[0x28 - 0x20] = backstab, 0xFF
        data = bytearray(dicelog.Entry.SIZE)
        data[144:144 + 0x28] = locals_
        e = dicelog.Entry.parse(bytes(data))
        weapon = types.SimpleNamespace(plus=4, nonmagical_flag=0, material=0)
        return self.log._thac0_breakdown(e, thac0, 0, 1, 20, weapon, 1, item_type, kit=kit)

    def test_cahulaks_heads(self):
        """Each swing the main head's -2 (in the set-up's bonus); the round's last the off head's -4 (its
        more added after the set-up): named, not "in bonuses"."""
        self.assertEqual(self.line(5, 7, 2), "THAC0 13, +6 STR, +4 weapon, -2 cahulaks, main head at DEX 15 = 5")
        self.assertEqual(self.line(7, 7, 2), "THAC0 13, +6 STR, +4 weapon, -4 cahulaks, off head at DEX 15 = 7")

    def test_flags_are_bytes(self):
        """From behind and backstab are the set-up's bytes (the byte after each not read with them)."""
        self.assertEqual(self.line(6, 8, 2, item_type=1, rear=1),
                         "THAC0 13, +2 from behind, +3 STR, +4 weapon, -2 off-hand and other = 6")
        self.assertEqual(self.line(7, 9, 2, item_type=1),
                         "THAC0 13, +4 STR, +4 weapon, -2 off-hand and other = 7")

    def test_sequel_effects(self):
        """The sequel's to-hit routine's effects (628h:66h): the attacker's Blessed and Impeded, the target's
        Blurry, each named; the rest STR."""
        self.effects = [(1, 1, 9), (1, 1, 50), (20, 20, 13)]
        self.assertEqual(self.line(13, 17, 4, item_type=1),
                         "THAC0 13, +1 Blessed, -2 Impeded, -2 target's Blurry, -1 STR, +4 weapon = 13")

    def test_nauseated_after_the_setup(self):
        """A nauseated attacker's -2 (DSCLOG2's STINK_SWING) is added after the set-up: named."""
        self.effects = [(1, 1, ravager.NAUSEATED)]
        kit = self.log._after_setup(1)
        self.assertEqual(self.line(7, 9, 4, item_type=1, kit=kit),
                         "THAC0 13, +4 STR, +4 weapon, -2 Nauseated = 7")

    def test_anti_magic_shell(self):
        """The plus doesn't count against a target in an Anti Magic Shell (the set-up's [BP-8] 0)."""
        self.effects = [(20, 20, 4)]
        self.assertEqual(self.line(7, 7, 0, item_type=1), "THAC0 13, +6 STR = 7")


if __name__ == "__main__":
    unittest.main()
