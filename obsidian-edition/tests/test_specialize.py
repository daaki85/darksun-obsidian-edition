"""Weapon specialization's kinds (specialize.py)."""

import os
import struct
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, restrict, specialize
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_restrict  # noqa: E402

# The game's weapon types (DSUN's IT1R: a weapon's flags at +0, 1 melee, 2 missile, 10h thrown),
# and the ones that are no kind: spell-made weapons, gloves, the broken weapon
WEAPON_TYPES = (0, 1, 2, 3, 17, 18, 19, 20, 21, 22, 28, 29, 30, 31, 32, 33, 37, 41, 44, 45, 46, 47, 48, 50,
                63, 64, 69, 80, 81, 84, 85, 93, 94, 97, 98, 107, 111, 112, 113)
NO_KIND = (28, 29, 30, 31, 32, 37, 93, 107, 113)


class KindTests(unittest.TestCase):
    def test_sixteen_kinds_four_pages(self):
        self.assertEqual(len(specialize.KINDS), 16)
        self.assertEqual(specialize.KINDS[specialize.DEFAULT], "long sword")
        self.assertEqual([specialize.page_of(k) for k in range(16)], [0] * 4 + [1] * 4 + [2] * 4 + [3] * 4)

    def test_every_weapon_sorted(self):
        """Every weapon type is a kind, or one of the few that are none; every kind has a type."""
        for t in WEAPON_TYPES:
            self.assertEqual(specialize.kind_of(t) is None, t in NO_KIND, t)
        self.assertEqual(set(specialize.KIND_OF_TYPE.values()), set(range(16)))

    def test_some_kinds(self):
        name = lambda t: specialize.KINDS[specialize.kind_of(t)]
        self.assertEqual(name(98), "long sword")  # Bloodwrath
        self.assertEqual(name(game.GYTHKA_TYPE), "gythka")
        self.assertEqual(name(game.SHORT_SWORD_TYPE), "short sword")
        self.assertEqual(name(0), "staff sling")
        self.assertIsNone(specialize.kind_of(game.CLOAK_TYPE))


def sheet(chosen=(), classes=(9, 0, 0), levels=(4, 0, 0)):
    s = bytearray(game.SHEET_SIZE)
    for i, k in enumerate(chosen):
        s[game.SPEC_SLOTS + i] = k + 1
    s[game.SHEET_CLASSES:game.SHEET_CLASSES + 3] = bytes(classes)
    s[game.SHEET_LEVELS:game.SHEET_LEVELS + 3] = bytes(levels)
    return bytes(s)


class SkillTests(unittest.TestCase):
    """specialize.skill: as DSCLOG's SPEC_OF (tests/test_dsclog.py SpecializeTests)."""
    LONG_SWORD, AXE = 45, 22

    def test_levels(self):
        S = specialize
        self.assertEqual(S.skill(sheet(), self.AXE), S.NONE)
        self.assertEqual(S.skill(sheet((0,)), self.AXE), S.PLAIN)
        self.assertEqual(S.skill(sheet((0,)), self.LONG_SWORD), S.SPECIAL)
        self.assertEqual(S.skill(sheet((0,), levels=(5, 0, 0)), self.LONG_SWORD), S.MASTER)
        self.assertEqual(S.skill(sheet((0,), levels=(9, 0, 0)), self.LONG_SWORD), S.GRAND)
        self.assertEqual(S.skill(sheet((0, 5), classes=(10, 0, 0), levels=(9, 0, 0)), self.AXE), S.SPECIAL)
        self.assertEqual(S.skill(sheet((0,), classes=(13, 0, 0)), self.LONG_SWORD), S.EXPERT)
        self.assertEqual(S.skill(sheet((0,), classes=(11, 17, 9), levels=(5, 5, 5)), self.LONG_SWORD), S.MASTER)

    def test_dual_class(self):
        """A human fighter turned preserver: no specialization until the new class's level passes
        the fighter's, then the fighter's again."""
        S = specialize
        s = bytearray(sheet((0,), classes=(11, 9, 0), levels=(3, 5, 0)))
        s[game.SHEET_RACE] = game.HUMAN
        self.assertEqual(S.skill(bytes(s), self.LONG_SWORD), S.PLAIN)
        s[game.SHEET_LEVELS] = 6
        self.assertEqual(S.skill(bytes(s), self.LONG_SWORD), S.MASTER)
        s[game.SHEET_RACE] = 2  # (an elf's are multiclass: all at once)
        s[game.SHEET_LEVELS] = 3
        self.assertEqual(S.skill(bytes(s), self.LONG_SWORD), S.MASTER)

    def test_bonuses(self):
        S = specialize
        self.assertEqual([(S.to_hit(l), S.damage(l)) for l in range(6)],
                         [(0, 0), (0, 0), (0, 0), (1, 2), (3, 3), (3, 3)])



class AttacksTests(unittest.TestCase):
    """specialize.attacks, as DSCLOG's PROBE_ATTACKS (the Characters tab's attacks line)."""

    def test_rates(self):
        from dsloader import specialize as sp
        self.assertEqual(sp.attacks(3, sp.PLAIN), 2)            # 3/2 to 1: a kind not chosen
        self.assertEqual(sp.attacks(4, sp.PLAIN), 3)            # 2 to 3/2
        self.assertEqual(sp.attacks(3, sp.SPECIAL), 3)
        self.assertEqual(sp.attacks(4, sp.GRAND), 6)            # one more
        self.assertEqual(sp.attacks(3, sp.EXPERT), 3)           # a ranger's: the game's
        self.assertEqual(sp.attacks(3, sp.NONE), 3)             # none chosen: the game's
        self.assertEqual(sp.attacks(3, sp.PLAIN, missile=True), 3)
        self.assertEqual(sp.attacks(2, sp.PLAIN), 2)            # not a warrior


class SpecializationsTests(unittest.TestCase):
    """GameData.specializations: the Characters tab's Weapons line."""

    def gd(self, s, rules=game.RULE_SPECIALIZE):
        gd = object.__new__(game.GameData)
        gd.rules = rules
        gd.sheet = lambda creature: s
        return gd

    def test_names(self):
        s = sheet((0, 5), classes=(10, 0, 0), levels=(9, 0, 0))
        self.assertEqual(self.gd(s).specializations(0), [("long sword", "specialized"), ("axe", "specialized")])
        self.assertEqual(self.gd(sheet((0,), classes=(13, 0, 0))).specializations(0), [("long sword", "expertise")])
        self.assertEqual(self.gd(sheet((0,), levels=(9, 0, 0))).specializations(0), [("long sword", "grand mastery")])
        self.assertEqual(self.gd(s, rules=0).specializations(0), [])


class PageLabelTests(unittest.TestCase):
    def test_short_forms(self):
        from dsloader import weaponpages
        labels = [weaponpages.page_text(k) for k in range(16)]
        self.assertEqual(labels[:4], ["LNG SWORD", "CLUB", "DAGGER", "SHRT SWORD"])
        self.assertEqual(labels[8], "QTR STAFF")
        self.assertEqual(labels[15], "STF SLING")
        self.assertTrue(all(len(t) <= 10 for t in labels))

    def test_ids_clear_of_the_game(self):
        """The game's own buttons and pictures run to 833h (the dialogue window's replies are
        81Ch-821h): the pages' come after."""
        from dsloader import weaponpages
        ids = [weaponpages.ROW_FIRST + k for k in range(16)] + [weaponpages.MORE, weaponpages.BACK, weaponpages.VIEW]
        self.assertTrue(all(0x834 <= i < 0xBB8 for i in ids))

    def test_picker_clear_of_the_game(self):
        """The level-up window's rows come after the pages', and its id is none of the game's
        windows (3000-3013, 3020, 3024...) nor the panel's."""
        from dsloader import weaponpages
        rows = [weaponpages.PICK_FIRST + k for k in range(16)]
        pages = [weaponpages.ROW_FIRST + k for k in range(16)] + [weaponpages.MORE, weaponpages.BACK, weaponpages.VIEW]
        self.assertTrue(all(0x834 <= i < 0xBB8 and i not in pages for i in rows))
        self.assertNotIn(weaponpages.PICKER, set(range(3000, 3014)) | {3020, 3024} | set(weaponpages.PAGES)
                         | {weaponpages.WARRIOR_DISCIPLINES, weaponpages.WARRIOR_SPHERES})
        # (six slots across, three rows, inside the 214 by 156 window and above its title)
        w = weaponpages
        left = (w.PICK_WIDTH - w.PICK_COLUMNS * w.PICK_PITCH + (w.PICK_PITCH - w.PICK_SLOT)) // 2
        xs = [left + w.PICK_PITCH * (k % w.PICK_COLUMNS) for k in range(16)]
        ys = [w.PICK_TOP + w.PICK_PITCH * (k // w.PICK_COLUMNS) for k in range(16)]
        self.assertGreaterEqual(min(xs), 4)
        self.assertLessEqual(max(xs) + w.PICK_SLOT, w.PICK_WIDTH - 4)
        self.assertLess(max(ys) + w.PICK_SLOT, w.PICK_TITLE_Y)

    def test_picker_matches_dsclog(self):
        """DSCLOG's PK_HOVER finds the slot under the pointer, and PROBE_PK_TITLE and PROBE_PK_WIN
        place the lines and the window, from numbers of its own: weaponpages' layout."""
        import os
        import re
        from dsloader import weaponpages as w
        with open(os.path.join(os.path.dirname(__file__), "..", "dos", "dsclog.asm")) as f:
            source = f.read()
        equ = {m.group(1): m.group(2).split(";")[0].strip()
               for m in re.finditer(r"^(\w+)\s+equ\s+(.+)$", source, re.M)}

        def value(name):
            expr = equ[name]
            for other in sorted(equ, key=len, reverse=True):
                if other in expr and other != name:
                    expr = re.sub(r"\b%s\b" % other, str(value(other)), expr)
            return eval(expr.replace("/", "//"))

        left = (w.PICK_WIDTH - w.PICK_COLUMNS * w.PICK_PITCH + (w.PICK_PITCH - w.PICK_SLOT)) // 2
        self.assertEqual((value("PK_PICK_WIDTH"), value("PK_PICK_Y")), (w.PICK_WIDTH, w.PICK_TITLE_Y))
        self.assertEqual((value("PK_PICK_X"), value("PK_PICK_TOP")),
                         ((320 - w.PICK_WIDTH) // 2, (200 - w.PICK_HEIGHT) // 2))
        self.assertEqual((value("PK_SLOTS_X"), value("PK_SLOTS_Y")),
                         (value("PK_PICK_X") + left, value("PK_PICK_TOP") + w.PICK_TOP))
        self.assertEqual((value("PK_PITCH"), value("PK_SLOT")), (w.PICK_PITCH, w.PICK_SLOT))



class NewCharacterTests(unittest.TestCase):
    """weaponchoice: a new character's kinds made whole, and its starting weapon."""

    def kinds(self, chosen, classes):
        from dsloader import weaponchoice
        return weaponchoice.kinds_for(sheet(chosen, classes=classes))

    def test_defaults(self):
        self.assertEqual(self.kinds((), (10, 0, 0)), [1, 2, 0, 0])  # a gladiator: long sword, club
        self.assertEqual(self.kinds((), (9, 0, 0)), [1, 0, 0, 0])
        self.assertEqual(self.kinds((), (15, 0, 0)), [1, 0, 0, 0])  # a ranger
        self.assertEqual(self.kinds((2,), (10, 0, 0)), [3, 2, 0, 0])  # (kinds + 1 in the sheet)
        self.assertEqual(self.kinds((1,), (10, 0, 0)), [2, 1, 0, 0])

    def test_allowed_kinds(self):
        """A fighter/psionicist's choice kept to what the psionicist may use: its long sword
        default becomes the club, the first allowed."""
        from dsloader import weaponchoice
        psi_kinds = sorted(restrict.PSIONICIST_KINDS)
        s = sheet((0,), classes=(9, 12, 0))
        self.assertEqual(weaponchoice.kinds_for(s, psi_kinds), [2, 0, 0, 0])
        s = sheet((2,), classes=(9, 12, 0))  # (the dagger: allowed)
        self.assertEqual(weaponchoice.kinds_for(s, psi_kinds), [3, 0, 0, 0])

    def test_myrmidon_keeps_its_second(self):
        """A Myrmidon (kits on) keeps a second kind marked; another fighter doesn't."""
        from dsloader import weaponchoice
        s = bytearray(sheet((0, 5), classes=(9, 0, 0)))
        s[0x43] = 1
        old = game.RULES_IN_FORCE
        try:
            game.RULES_IN_FORCE = game.RULE_KITS
            self.assertEqual(weaponchoice.kinds_for(bytes(s)), [1, 6, 0, 0])
            s[0x43] = 2
            self.assertEqual(weaponchoice.kinds_for(bytes(s)), [1, 0, 0, 0])
        finally:
            game.RULES_IN_FORCE = old

    def test_battle_mage_keeps_its_own(self):
        """A Battle Mage (kits on) keeps its one weapon spec, the long sword if none was marked, of
        its own kinds (restrict.allowed_kinds); another preserver none."""
        from dsloader import kits, weaponchoice
        old = game.RULES_IN_FORCE
        try:
            game.RULES_IN_FORCE = game.RULE_KITS | game.RULE_SPECIALIZE
            for chosen, want in (((5,), [6, 0, 0, 0]), ((), [1, 0, 0, 0]), ((5, 2), [6, 0, 0, 0])):
                s = bytearray(sheet(chosen, classes=(11, 0, 0)))
                s[0x43] = 2
                allowed = restrict.allowed_kinds(bytes(s), lambda t: bytes(game.ITEM_TYPE_SIZE))
                self.assertEqual(allowed, sorted(kits.BATTLE_MAGE_KINDS))
                self.assertEqual(weaponchoice.kinds_for(bytes(s), allowed), want)
            s[0x43] = 1
            self.assertEqual(weaponchoice.kinds_for(bytes(s)), [0, 0, 0, 0])
        finally:
            game.RULES_IN_FORCE = old

    def test_extra_kinds_cleared(self):
        self.assertEqual(self.kinds((2, 5), (9, 0, 0)), [3, 0, 0, 0])
        self.assertEqual(self.kinds((2,), (11, 0, 0)), [0, 0, 0, 0])

    def test_plain_weapon(self):
        from dsloader import weaponchoice
        start = bytes.fromhex("0cfc00001f002d000f27510000000000040a1c0000")
        new, slot = weaponchoice.plain_weapon(start, specialize.KINDS.index("dagger"))
        self.assertEqual(new.hex(), "60fb00001f0002000f271100000000000403100000"[:6] + new.hex()[6:])
        self.assertEqual((struct.unpack_from("<H", new, 0x0A)[0], struct.unpack_from("<H", new, 0x12)[0], slot), (17, 0x10, None))
        self.assertEqual(struct.unpack_from("<H", new, 0x0C)[0], 0)
        _, slot = weaponchoice.plain_weapon(start, specialize.KINDS.index("bow"))
        self.assertEqual(slot, game.EQUIP_SLOTS.index("missile"))
        self.assertEqual(len(weaponchoice.PLAIN), len(specialize.KINDS))



class StartWeaponTests(unittest.TestCase):
    """weaponchoice.start_weapon: in a material the character can use (the game's weapon types,
    as tests/test_dsclog.py's KindsAllowedTests has them)."""

    def start(self, kind, classes):
        from dsloader import weaponchoice
        from test_dsclog import KindsAllowedTests
        s = test_restrict.sheet(*classes)
        record = KindsAllowedTests.record.__get__(KindsAllowedTests("test_as_the_python"))
        got = weaponchoice.start_weapon(s, [specialize.KINDS.index(kind) + 1, 0, 0, 0], record)
        return (specialize.KINDS[got[0]], got[1][0]) if got else None

    def test_materials(self):
        self.assertEqual(self.start("long sword", (9,)), ("long sword", 81))  # the game's bone one
        self.assertEqual(self.start("long sword", (9, 3)), ("long sword", 45))  # fire: obsidian
        self.assertEqual(self.start("long sword", (9, 2)), ("long sword", 45))  # earth: obsidian
        self.assertEqual(self.start("dagger", (9, 2)), ("dagger", 17))
        self.assertEqual(self.start("mace", (9, 3)), ("mace", 46))  # a plain obsidian mace, the Loader's


class FinishNewTests(unittest.TestCase):
    """weaponchoice.finish_new on a party of one New character (a fake of the game's memory)."""
    DS, SHEETS, ITEMS, TYPES = 0x100, 0x2000, 0x3000, 0x4000

    def setUp(self):
        from unittest import mock
        self.mem = bytearray(0x10000)
        for ptr, at in ((game.SHEETS_PTR, self.SHEETS), (game.ITEMS_PTR, self.ITEMS), (game.ITEM_TYPES_PTR, self.TYPES)):
            struct.pack_into("<HH", self.mem, self.DS * 16 + ptr, at, 0)
        test = self

        class Guest:
            def read(self, at, n):
                return bytes(test.mem[at:at + n])

            def write(self, at, data):
                test.mem[at:at + len(data)] = data

        class Gd:
            guest, ds, rules = Guest(), self.DS, 0

            def creature(self, i):
                rec = bytearray(game.CREATURE_SIZE)
                if i == 0:
                    rec[game.CREATURE_NAME] = ord("G")
                    rec[game.CREATURE_STATUS] = game.STATUS_NEW
                return bytes(rec)

            def creature_name(self, i):
                return "Grog"

            def item_name(self, n):
                return "Leather Shield"

            def _worn(self, i):
                for n in range(test.items):
                    item = test.mem[test.ITEMS + n * game.ITEM_SIZE:test.ITEMS + (n + 1) * game.ITEM_SIZE]
                    yield n, bytes(item), b""
        self.gd = Gd()
        self.items = 0
        for patch in (mock.patch("dsloader.pickpocket.free_cell", lambda gd, it, m: 30),
                      mock.patch("dsloader.ring.Items", lambda gd: None),
                      mock.patch("dsloader.restrict.allowed_kinds", lambda sheet, read: list(range(16))),
                      mock.patch("dsloader.pickpocket.place", self.place)):
            patch.start()
            self.addCleanup(patch.stop)

    def place(self, gd, member, item, slot):  # (the harness has no lists: the slot byte alone)
        self.mem[self.ITEMS + item * game.ITEM_SIZE + game.ITEM_SLOT] = slot
        return True

    def give(self, type_, name, slot):
        rec = bytearray(game.ITEM_SIZE)
        struct.pack_into("<H", rec, game.ITEM_TYPE, type_)
        struct.pack_into("<H", rec, game.ITEM_NAME, name)
        rec[game.ITEM_SLOT] = slot
        at = self.ITEMS + self.items * game.ITEM_SIZE
        self.mem[at:at + game.ITEM_SIZE] = rec
        self.items += 1

    def item(self, n):
        at = self.ITEMS + n * game.ITEM_SIZE
        return (struct.unpack_from("<H", self.mem, at + game.ITEM_TYPE)[0], self.mem[at + game.ITEM_SLOT])

    def setup_character(self, kind, classes=(9, 0, 0), race=7):
        from dsloader import weaponchoice
        s = bytearray(sheet((specialize.KINDS.index(kind),), classes=classes))
        s[game.SHEET_RACE] = race
        s[game.SHEET_FLAGS:game.SHEET_FLAGS + 2] = b"\xff\xff"
        self.mem[self.SHEETS:self.SHEETS + game.SHEET_SIZE] = s
        right, left = game.WEAPON_HANDS
        self.give(weaponchoice.START_TYPE, weaponchoice.START_NAME, right)
        self.give(36, 0x40, left)  # (a shield)
        for t in range(game.GAME_TYPES + 25):  # (every class may use every type, as far as the game's lists go)
            self.mem[self.TYPES + t * game.ITEM_TYPE_SIZE + 0x10:self.TYPES + t * game.ITEM_TYPE_SIZE + 0x12] = b"\xff\xff"
        great_axe = weaponchoice.PLAIN[specialize.KINDS.index("great axe")][0]
        self.mem[self.TYPES + great_axe * game.ITEM_TYPE_SIZE + 0x0F] = weaponchoice.TWO_HANDED
        return right, left

    def test_two_handed_takes_the_shield_off(self):
        from dsloader import weaponchoice
        right, left = self.setup_character("great axe")
        out = weaponchoice.finish_new(self.gd)
        self.assertEqual(self.item(0), (weaponchoice.PLAIN[specialize.KINDS.index("great axe")][0], right))
        self.assertEqual(self.item(1), (36, 30))  # (into a backpack cell)
        self.assertIn("goes into the backpack", out[0])

    def test_one_hand_keeps_the_shield(self):
        from dsloader import weaponchoice
        right, left = self.setup_character("axe")
        weaponchoice.finish_new(self.gd)
        self.assertEqual(self.item(1), (36, left))

    def test_missile_slot_keeps_the_shield(self):
        """A staff sling (two-handed, as the bow) goes in the missile slot, not a hand: the game asks
        nothing of the hands for it, so the shield stays."""
        from dsloader import weaponchoice
        right, left = self.setup_character("staff sling")
        staff_sling = weaponchoice.PLAIN[specialize.KINDS.index("staff sling")][0]
        self.mem[self.TYPES + staff_sling * game.ITEM_TYPE_SIZE + 0x0F] = weaponchoice.TWO_HANDED
        weaponchoice.finish_new(self.gd)
        self.assertEqual(self.item(0), (staff_sling, weaponchoice.MISSILE_SLOT))
        self.assertEqual(self.item(1), (36, left))

    def test_a_half_giant_keeps_the_shield(self):
        from dsloader import weaponchoice
        right, left = self.setup_character("great axe", race=game.RACE_HALF_GIANT)
        self.gd.rules = game.RULE_HALF_GIANT
        weaponchoice.finish_new(self.gd)
        self.assertEqual(self.item(1), (36, left))

    def test_made_once(self):
        """A long sword handed over later stays one: the character has its kind's weapon."""
        from dsloader import weaponchoice
        right, left = self.setup_character("club", classes=(10, 0, 0))
        weaponchoice.finish_new(self.gd)
        self.give(weaponchoice.START_TYPE, weaponchoice.START_NAME, left)
        self.assertEqual(weaponchoice.finish_new(self.gd), [])
        self.assertEqual(self.item(2)[0], weaponchoice.START_TYPE)


class ClassGearTests(FinishNewTests):
    """weaponchoice.class_gear: a New character's starting gear its classes can't use left behind."""

    def test_druid_leaves_the_armour(self):
        from dsloader import restrict, weaponchoice
        s = bytearray(sheet((), classes=(9, 5, 17)))  # (fighter/druid/thief, a half-elf)
        s[game.SHEET_RACE] = 7
        s[game.SHEET_FLAGS:game.SHEET_FLAGS + 2] = b"\xff\xff"
        self.mem[self.SHEETS:self.SHEETS + game.SHEET_SIZE] = s
        for t in (12, 13):  # (12 leather armour, 13 a long sword: types the game lets every class use)
            at = self.TYPES + t * game.ITEM_TYPE_SIZE
            self.mem[at + 0x10:at + 0x12] = b"\xff\xff"
        armour, sword = 12, 13
        self.give(armour, 0x20, 30)  # (in the backpack)
        self.give(sword, 0x21, game.WEAPON_HANDS[0])
        taken = []

        def unlink(gd, it, item, what, empty=False):
            taken.append(item)
            return empty  # (as ring.unlink does for a list's only item: the character's may empty)
        kinds = {armour: "armour", sword: "weapon"}
        with mock.patch("dsloader.ring.unlink", unlink), \
                mock.patch.object(restrict, "is_weapon", lambda typ: kinds.get(typ[0]) == "weapon"), \
                mock.patch.object(restrict, "is_armour", lambda typ: kinds.get(typ[0]) == "armour"), \
                mock.patch.object(restrict, "is_shield", lambda typ: False):
            for t in kinds:
                self.mem[self.TYPES + t * game.ITEM_TYPE_SIZE] = t  # (each type known by its first byte)
            out = weaponchoice.class_gear(self.gd)
        self.assertEqual(taken, [0])  # (the armour: a druid wears none; the sword stays)
        self.assertIn("left behind", out[0])

    def test_druid_leaves_the_shield_the_last_of_its_list(self):
        """A half-elf fighter/druid's shield, alone in its list once the armour is gone, goes too
        (it stayed: the list's only item was kept, as a container's must be)."""
        from dsloader import restrict, weaponchoice
        s = bytearray(sheet((), classes=(9, 5, 0)))
        s[game.SHEET_RACE] = 7
        s[game.SHEET_FLAGS:game.SHEET_FLAGS + 2] = b"\xff\xff"
        self.mem[self.SHEETS:self.SHEETS + game.SHEET_SIZE] = s
        shield = 4
        at = self.TYPES + shield * game.ITEM_TYPE_SIZE
        self.mem[at + 0x10:at + 0x12] = b"\xff\xff"
        self.mem[at] = shield
        self.give(shield, 0x05, game.WEAPON_HANDS[1])
        asked = []

        def unlink(gd, it, item, what, empty=False):
            asked.append(empty)
            return empty
        with mock.patch("dsloader.ring.unlink", unlink), \
                mock.patch.object(restrict, "is_weapon", lambda typ: False), \
                mock.patch.object(restrict, "is_armour", lambda typ: False), \
                mock.patch.object(restrict, "is_shield", lambda typ: typ[0] == shield):
            out = weaponchoice.class_gear(self.gd)
        self.assertEqual(asked, [True])
        self.assertIn("Shield is left behind", out[0])


class KitGearTests(FinishNewTests):
    """weaponchoice.kit_gear: a New character's starting gear fitted to its kit."""

    def setUp(self):
        super().setUp()
        rules = game.RULES_IN_FORCE
        game.RULES_IN_FORCE = game.RULE_KITS
        self.addCleanup(setattr, game, "RULES_IN_FORCE", rules)
        from dsloader import weaponchoice
        for t in range(game.GAME_TYPES + 25):
            self.mem[self.TYPES + t * game.ITEM_TYPE_SIZE + 0x10:self.TYPES + t * game.ITEM_TYPE_SIZE + 0x12] = b"\xff\xff"
        for kind, plain in enumerate(weaponchoice.PLAIN):  # (melee weapons, but the missile ones)
            self.mem[self.TYPES + plain[0] * game.ITEM_TYPE_SIZE] = 0x02 if kind in weaponchoice.MISSILE_KINDS else 0x01
        for shield in (4, 36):
            self.mem[self.TYPES + shield * game.ITEM_TYPE_SIZE] = 0x04
        great_axe = weaponchoice.PLAIN[specialize.KINDS.index("great axe")][0]
        self.mem[self.TYPES + great_axe * game.ITEM_TYPE_SIZE + 0x0F] = weaponchoice.TWO_HANDED

    def character(self, cls, kit, chosen=()):
        s = bytearray(sheet(tuple(specialize.KINDS.index(k) for k in chosen), classes=(cls, 0, 0)))
        s[game.SHEET_FLAGS:game.SHEET_FLAGS + 2] = b"\xff\xff"
        s[0x43] = kit
        self.mem[self.SHEETS:self.SHEETS + game.SHEET_SIZE] = s
        return game.WEAPON_HANDS

    def test_shinobi_long_sword(self):
        from dsloader import weaponchoice
        right, left = self.character(17, 3)
        self.give(weaponchoice.START_TYPE, weaponchoice.START_NAME, right)
        out = weaponchoice.kit_gear(self.gd)
        self.assertEqual(self.item(0), (weaponchoice.PLAIN[specialize.KINDS.index("short sword")][0], right))
        self.assertIn("a Shinobi can't use it", out[0])
        self.assertEqual(weaponchoice.kit_gear(self.gd), [])  # (once)

    def test_ravager_shield(self):
        from dsloader import weaponchoice
        right, left = self.character(9, 3)
        self.give(weaponchoice.START_TYPE, weaponchoice.START_NAME, right)
        self.give(4, 0x05, left)
        taken = []

        def unlink(gd, it, item, what, empty=False):  # (the harness has no lists: the record emptied)
            taken.append(item)
            at = self.ITEMS + item * game.ITEM_SIZE
            self.mem[at:at + game.ITEM_SIZE] = bytes(game.ITEM_SIZE)
            return True
        given = []

        def add_to(gd, creature, rec, slot=None):  # (the harness has no lists: the next record)
            given.append((rec, slot))
            at = self.ITEMS + self.items * game.ITEM_SIZE
            rec = bytearray(rec)
            rec[game.ITEM_SLOT] = slot
            self.mem[at:at + game.ITEM_SIZE] = rec
            self.items += 1
            return True
        with mock.patch("dsloader.ring.unlink", unlink), mock.patch("dsloader.npcitems.add_to", add_to):
            out = weaponchoice.kit_gear(self.gd)
            self.assertEqual(weaponchoice.kit_gear(self.gd), [])
        self.assertEqual(self.item(0), (weaponchoice.START_TYPE, right))
        self.assertEqual(taken, [1])  # (the shield taken away, not put in the backpack)
        self.assertIn("left behind", out[0])
        self.assertEqual(self.item(2), (weaponchoice.START_TYPE, left))  # (a second of its weapon, for the left hand)
        self.assertEqual(len(given), 1)
        self.assertIn("second", out[1])

    def test_myrmidon_two_weapons(self):
        """A Myrmidon with weapon specialization: a plain weapon of its second kind in the backpack."""
        from dsloader import weaponchoice
        right, left = self.character(9, 1, ("long sword", "axe"))
        self.gd.rules = game.RULE_SPECIALIZE | game.RULE_KITS
        self.give(weaponchoice.START_TYPE, weaponchoice.START_NAME, right)
        self.give(4, 0x05, left)
        given = []

        def add_to(gd, creature, rec, slot=None):
            given.append((rec, slot))
            at = self.ITEMS + self.items * game.ITEM_SIZE
            rec = bytearray(rec)
            rec[game.ITEM_SLOT] = 20 if slot is None else slot
            self.mem[at:at + game.ITEM_SIZE] = rec
            self.items += 1
            return True
        with mock.patch("dsloader.npcitems.add_to", add_to):
            out = weaponchoice.kit_gear(self.gd)
            self.assertEqual(weaponchoice.kit_gear(self.gd), [])
        self.assertEqual(self.item(2), (weaponchoice.PLAIN[specialize.KINDS.index("axe")][0], 20))
        self.assertEqual(self.item(1), (4, left))  # (the shield kept)
        self.assertIn("Myrmidon", out[0])

    def test_brute_two_handed(self):
        """Without weapon specialization (its chosen kind would be one already): a great axe, and
        the off-hand club left behind (no use to a Brute)."""
        from dsloader import weaponchoice
        right, left = self.character(10, 3)
        self.give(weaponchoice.START_TYPE, weaponchoice.START_NAME, right)
        self.give(18, 0x11, left)
        taken = []

        def unlink(gd, it, item, what, empty=False):
            taken.append(item)
            at = self.ITEMS + item * game.ITEM_SIZE
            self.mem[at:at + game.ITEM_SIZE] = bytes(game.ITEM_SIZE)
            return True
        with mock.patch("dsloader.ring.unlink", unlink):
            out = weaponchoice.kit_gear(self.gd)
            self.assertEqual(weaponchoice.kit_gear(self.gd), [])
        self.assertEqual(self.item(0), (weaponchoice.PLAIN[specialize.KINDS.index("great axe")][0], right))
        self.assertEqual(taken, [1])
        self.assertIn("left behind", out[-1])

    def test_arena_champion_shield(self):
        from dsloader import weaponchoice
        right, left = self.character(10, 1)
        self.give(weaponchoice.START_TYPE, weaponchoice.START_NAME, right)
        self.give(18, 0x11, left)
        out = weaponchoice.kit_gear(self.gd)
        self.assertEqual(self.item(1), (4, left))
        self.assertIn("shield", out[0])
        self.assertEqual(weaponchoice.kit_gear(self.gd), [])

    def test_battle_mage_weapon(self):
        from dsloader import weaponchoice
        right, left = self.character(11, 2, ("axe",))
        self.give(3, 0x04, right)  # (the quarterstaff)
        self.assertEqual(weaponchoice.kit_gear(self.gd), [])  # (weapon specialization off: no spec)
        self.gd.rules = game.RULE_SPECIALIZE
        weaponchoice.kit_gear(self.gd)
        self.assertEqual(self.item(0), (weaponchoice.PLAIN[specialize.KINDS.index("axe")][0], right))

    def test_no_kit(self):
        from dsloader import weaponchoice
        right, left = self.character(17, 0)
        self.give(weaponchoice.START_TYPE, weaponchoice.START_NAME, right)
        self.assertEqual(weaponchoice.kit_gear(self.gd), [])
        self.assertEqual(self.item(0), (weaponchoice.START_TYPE, right))

if __name__ == "__main__":
    unittest.main()
