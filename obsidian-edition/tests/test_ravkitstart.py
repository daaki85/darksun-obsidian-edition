"""New characters' starting gear fitted to their kits in Wake of the Ravager (ravkitstart.py)."""

import glob
import os
import struct
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import game, kitpages, ravkitstart, ravlog, restrict, specialize  # noqa: E402
import test_ravfirstweapon  # noqa: E402

KIND = specialize.KINDS.index
K = ravkitstart
FIGHTER, GLADIATOR, PRESERVER, THIEF = 9, 10, 11, 17
SHIELD, RING_CHEST, LEATHER_CHEST, CHEST = 91, 33, 32, game.EQUIP_SLOTS.index("chest")
GONE = 0xEE  # (the harness's mark of an item left behind)


class KitGearTests(test_ravfirstweapon.FillTests):
    """ravkitstart.kit_gear on a party of one New character in the sequel's layout (FillTests' harness: the
    sequel's weapons of their kinds, metal, two-handed as the game has them)."""

    def setUp(self):
        super().setUp()
        game.RULES_IN_FORCE = game.RULES_ALWAYS | game.RULE_KITS
        for armour, material in ((RING_CHEST, restrict.METAL), (LEATHER_CHEST, restrict.LEATHER)):
            at = self.TYPES + armour * game.ITEM_TYPE_SIZE
            self.mem[at + 0x0F], self.mem[at + 8], self.mem[at + 9] = restrict.ARMOUR, material, 1  # (the chest's)
        self.mem[self.TYPES + SHIELD * game.ITEM_TYPE_SIZE + 0x0F] = restrict.ARMOUR
        self.taken = []
        worn = self.gd._worn

        def unlink(gd, it, item, what, empty=False):
            self.taken.append(item)
            self.mem[self.ITEMS + item * game.ITEM_SIZE + game.ITEM_SLOT] = GONE
            return True
        self.gd._worn = lambda i, *a: ((n, item, t) for n, item, t in worn(i) if item[game.ITEM_SLOT] != GONE)
        patch = mock.patch("dsloader.ring.unlink", unlink)
        patch.start()
        self.addCleanup(patch.stop)

    def kit(self, cls, kit, kinds=()):
        """A single-class character of class CLS with its kit KIT (1-3), weapon specs KINDS."""
        self.character((cls, 0, 0), kinds)
        self.mem[self.SHEETS + kitpages.KIT_BYTE] = kit
        return game.WEAPON_HANDS

    def plain_of(self, kind):
        return ravlog.RAV_PLAIN[KIND(kind)][0][1]

    def armour(self, type_, slot=CHEST):
        rec = bytearray(ravlog.RAV_LEATHER[0][1])
        struct.pack_into("<H", rec, game.ITEM_TYPE, type_)
        self.put(bytes(rec), slot)

    def test_shinobi_long_sword_a_short_sword_plus_one(self):
        """A thief's long sword +1 a short sword +1 (the mod's, with the new items), else a dagger +1."""
        right, _ = self.kit(THIEF, 3)
        self.put(self.the("long sword").record, right)
        out = K.kit_gear(self.gd)
        self.assertEqual((self.item(0), self.plus(0)), ((self.the("short sword").type, right), 1))
        self.assertIn("short sword +1 in place of", out[0])
        self.assertEqual(K.kit_gear(self.gd), [])  # (once)
        self.setUp()
        self.kit(THIEF, 3)
        self.put(self.the("long sword").record, right)
        K.kit_gear(self.gd, new_items=False)
        self.assertEqual((self.item(0), self.plus(0)), ((self.the("dagger").type, right), 1))

    def test_a_packed_weapon_into_the_hand(self):
        """The game's give routine drops a refused weapon in the backpack: made one the kit allows, in hand."""
        right, _ = self.kit(THIEF, 3)
        self.put(self.the("long sword").record, 20)
        K.kit_gear(self.gd)
        self.assertEqual(self.item(0), (self.the("short sword").type, right))

    def test_ravager(self):
        """A fighter's shield left behind, its ring armour made leather, a second long sword +1 in the left."""
        right, left = self.kit(FIGHTER, 3)
        self.put(self.the("long sword").record, right)
        self.put(ravkitstart.SHIELD_PLUS_ONE.record, left)
        self.armour(RING_CHEST)
        out = K.kit_gear(self.gd)
        self.assertEqual(self.taken, [1])
        self.assertEqual(self.item(2), (LEATHER_CHEST, CHEST))
        self.assertEqual((self.item(3), self.plus(3)), ((self.the("long sword").type, left), 1))
        self.assertEqual(len(out), 3, out)
        self.assertIn("leather armour in place of", out[1])
        self.assertIn("second", out[2])
        self.assertEqual(K.kit_gear(self.gd), [])

    def test_packed_armour_made_leather_and_worn(self):
        """The game's give routine drops armour the kit refuses into the backpack: made leather, worn in its slot."""
        self.kit(FIGHTER, 3)
        self.armour(RING_CHEST, 20)
        out = K.kit_gear(self.gd)
        self.assertEqual(self.item(0), (LEATHER_CHEST, CHEST))
        self.assertIn("leather armour in place of", out[0])

    def test_arena_champion_shield(self):
        right, left = self.kit(GLADIATOR, 1, ["long sword", "club"])
        self.put(self.the("long sword").record, right)
        self.put(self.the("long sword").record, left)
        out = K.kit_gear(self.gd)
        self.assertEqual((self.item(1), self.plus(1)), ((SHIELD, left), 1))
        self.assertIn("shield +1 in place of", out[0])
        self.assertEqual(K.kit_gear(self.gd), [])

    def test_brute_one_handed_left_behind(self):
        """After its first pick's great axe +1 (ravfirstweapon), the second long sword in the backpack is left."""
        right, _ = self.kit(GLADIATOR, 3, ["great axe", "lotulis"])
        self.put(self.the("great axe").record, right)
        self.put(self.the("long sword").record, 30)
        out = K.kit_gear(self.gd)
        self.assertEqual(self.taken, [1])
        self.assertIn("two-handed weapons only", out[0])

    def test_myrmidon_polearm(self):
        right, left = self.kit(FIGHTER, 1, ["long sword", "polearm"])
        self.put(self.the("long sword").record, right)
        self.put(ravkitstart.SHIELD_PLUS_ONE.record, left)
        out = K.kit_gear(self.gd)
        self.assertEqual(self.given, [80])  # (the sequel's plain polearm, two-handed: the backpack)
        self.assertIn("plain polearm in the backpack", out[0])
        self.assertEqual(K.kit_gear(self.gd), [])

    def test_battle_mage_its_spec(self):
        right, _ = self.kit(PRESERVER, 2, ["axe"])
        self.put(self.the("quarterstaff").record, right)
        out = K.kit_gear(self.gd)
        self.assertEqual((self.item(0), self.plus(0)), ((self.the("axe").type, right), 1))
        self.assertIn("Battle Mage's weapon spec", out[0])

    def test_a_plain_weapon_made_plain(self):
        """A ranger's plain long sword (no kit forbids it here: a Shinobi's for the test) made a plain one."""
        right, _ = self.kit(THIEF, 3)
        self.put(self.plain_of("long sword"), right)
        out = K.kit_gear(self.gd, new_items=False)
        self.assertEqual((self.item(0), self.plus(0)), ((self.plain_of("dagger")[0x0A], right), 0))
        self.assertIn("a plain dagger", out[0])

    def test_spellarcher_fine_bow(self):
        """A half-elf fighter/preserver Spellarcher's bow is made the Fine Bow (ravager.FINE_BOW_NAME), once."""
        from dsloader import kits, ravager, weaponchoice
        self.character((FIGHTER, PRESERVER, 0), ["bow"], race=4)
        self.mem[self.SHEETS + kitpages.KIT_BYTE] = 1
        self.assertEqual(kitpages.kit_ids(bytes(self.mem[self.SHEETS:self.SHEETS + game.SHEET_SIZE])), [kits.SPELLARCHER])
        bow = bytearray(self.plain_of("long sword"))
        struct.pack_into("<H", bow, game.ITEM_TYPE, 18)  # (the sequel's bow)
        self.put(bytes(bow), weaponchoice.MISSILE_SLOT)
        out = K.kit_gear(self.gd)
        self.assertEqual(struct.unpack_from("<H", self.mem, self.ITEMS + game.ITEM_NAME)[0], ravager.FINE_BOW_NAME)
        self.assertIn("Fine Bow (+1 to hit)", out[-1])
        self.assertEqual(K.kit_gear(self.gd), [])

    def test_no_kit_or_kits_off_nothing(self):
        right, left = self.kit(FIGHTER, 0)
        self.put(self.the("long sword").record, right)
        self.put(ravkitstart.SHIELD_PLUS_ONE.record, left)
        self.assertEqual(K.kit_gear(self.gd), [])
        self.mem[self.SHEETS + kitpages.KIT_BYTE] = 3
        game.RULES_IN_FORCE = game.RULES_ALWAYS & ~game.RULE_KITS
        self.assertEqual(K.kit_gear(self.gd), [])
        self.assertEqual(self.taken, [])


class RecordTests(unittest.TestCase):
    def test_shields(self):
        for shield, plus in ((K.SHIELD, 0), (K.SHIELD_PLUS_ONE, 1)):
            self.assertEqual(struct.unpack_from("<H", shield.record, 0x0A)[0], shield.type)
            self.assertEqual((len(shield.record), shield.record[0x13], shield.record[0x16]), (0x17, 0xFF, plus))

    @unittest.skipUnless(os.environ.get("DSUN_WOTR"), "DSUN_WOTR: the player's Wake of the Ravager folder")
    def test_from_the_game(self):
        """The shields are OBJEX.GFF's objects 840 and 842's first item records."""
        from dsloader import dataitems, gff
        folder = os.environ["DSUN_WOTR"]
        find = lambda name: next(f for f in glob.glob(os.path.join(folder, "*")) if os.path.basename(f).lower() == name)
        objects = gff.read_gff(open(find("objex.gff"), "rb").read())
        for obj, shield in ((840, K.SHIELD), (842, K.SHIELD_PLUS_ONE)):
            recs, _ = dataitems.records(objects[("RDFF", obj)])
            self.assertEqual(recs[0].data[:0x17], shield.record)


class GearPassTests(unittest.TestCase):
    def test_the_order(self):
        """ravlog's gear pass: the first pick's weapon, the kit's (its armour made leather before the classes' step
        leaves it behind), the classes', the fuller gear, the weapon first."""
        import inspect
        src = inspect.getsource(ravlog.RavDiceLog._gear_pass)
        at = [src.index(s) for s in ("ravfirstweapon.fill", "ravkitstart.kit_gear", "weaponchoice.class_gear",
                                     "out += startgear.fill", "ravfirstweapon.weapon_first")]
        self.assertEqual(at, sorted(at))


for _name in [n for n in dir(test_ravfirstweapon.FillTests) if n.startswith("test") and n not in vars(KitGearTests)]:
    setattr(KitGearTests, _name, None)  # (ravfirstweapon's and weaponchoice's own: not run here again)


if __name__ == "__main__":
    unittest.main()
