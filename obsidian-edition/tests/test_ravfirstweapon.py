"""A new warrior's starting weapon in Wake of the Ravager: a +1 of its first pick (ravfirstweapon.py)."""

import glob
import os
import struct
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import game, ravager, ravfirstweapon, ravlog, specialize, weaponchoice  # noqa: E402
from test_specialize import FinishNewTests  # noqa: E402

KIND = specialize.KINDS.index
W = ravfirstweapon
FIGHTER, GLADIATOR, RANGER, AIR_CLERIC = 9, 10, 13, 1
SHIELD, LONG_SWORD, PLAIN_LONG_SWORD, GYTHKA, BOW, ARROWS = 91, 97, 97, 52, 18, 6
TWO_HANDED = (61, 39, 101, 52, 85, 51, 113, 79, 114, 80, 115, 24, 98, 18)  # (+0Bh 40h in the sequel's table)


class RecordTests(unittest.TestCase):
    """PLUS_ONE's records: the sequel's item records, of the kind they are listed under, +1 but the bow."""

    def test_records(self):
        kinds = ravager.rav_kinds()
        for kind, weapons in W.PLUS_ONE.items():
            self.assertTrue(weapons, kind)
            for w in weapons:
                self.assertEqual(len(w.record), ravager.ITEM_SIZE)
                self.assertEqual(struct.unpack_from("<H", w.record, 0x0A)[0], w.type)
                self.assertEqual(kinds.get(w.type), kind, w)
                self.assertEqual((w.record[0x13], w.record[0x16]), (0xFF, 0 if kind == weaponchoice.BOW else 1), w)
        self.assertEqual(set(W.PLUS_ONE), set(range(len(specialize.KINDS))))  # (every kind has one)
        self.assertEqual(W.ARROWS_PLUS_ONE[0x16], 1)

    def test_missile_kinds(self):
        self.assertEqual({specialize.KINDS[k] for k in W.MISSILE_KINDS},
                         {"bow", "sling", "staff sling", "javelin", "darts", "chatkcha"})

    @unittest.skipUnless(os.environ.get("DSUN_WOTR"), "DSUN_WOTR: the player's Wake of the Ravager folder")
    def test_from_the_game(self):
        """The sequel's own: an OBJEX.GFF object's first item record; the mod's: ravgear.item_record's; one
        made +1: an object's record with a plus of 1 and MADE_VALUE."""
        from dsloader import dataitems, gff, ravgear
        folder = os.environ["DSUN_WOTR"]
        find = lambda name: next(f for f in glob.glob(os.path.join(folder, "*")) if os.path.basename(f).lower() == name)
        objects = gff.read_gff(open(find("objex.gff"), "rb").read())
        text = gff.read_gff(open(find(ravager.RESOURCE_FILE.lower()), "rb").read())[("TEXT", 1000)]
        records = set()
        for key, chunk in objects.items():
            if key[0] == "RDFF":
                try:
                    recs, _ = dataitems.records(chunk)
                except Exception:
                    continue
                records.update(r.data[:0x17] for r in recs[:1])
        mod = {ravgear.item_record(k, objects, text) for k in ravgear.MAGIC if k.endswith("+1")}
        mace = ravgear.item_record("obsidian mace", objects, text)
        self.assertEqual(ravlog.RAV_PLAIN_NEW[KIND("mace")][0][1], mace)
        for weapons in W.PLUS_ONE.values():
            for w in weapons:
                if w.new and not w.made:
                    self.assertIn(w.record, mod, w)
                elif w.made:
                    plain = bytearray(w.record)
                    plain[0x16] = 0
                    self.assertEqual(struct.unpack_from("<H", w.record, 6)[0], W.MADE_VALUE)
                    base = mace if w.new else next((r for r in records if r[:6] == bytes(plain[:6])
                                                    and r[8:] == bytes(plain[8:])), None)
                    self.assertIsNotNone(base, w)
                    self.assertEqual(bytes(plain[:6]) + bytes(plain[8:]), base[:6] + base[8:], w)
                else:
                    self.assertIn(w.record, records, w)
        self.assertIn(W.ARROWS_PLUS_ONE, records)


class AirDaggerTests(unittest.TestCase):
    def test_mod_types_table(self):
        """The sequel's daggers 37 and 72 the air clerics' too; nothing else changed."""
        table = bytes(ravager.GAME_TYPES * ravager.TYPE_SIZE)
        out = ravager.mod_types_table(table)
        for t in range(ravager.GAME_TYPES):
            classes = struct.unpack_from("<H", out, t * ravager.TYPE_SIZE + 0x0C)[0]
            self.assertEqual(classes, 1 if t in (37, 72) else 0, t)
        self.assertEqual(out[:37 * 15], table[:37 * 15])


class FireClericMaceTests(unittest.TestCase):
    def test_obsidian_mace_with_the_new_items(self):
        """startgear's plain mace in the sequel: the bone one, then ravgear's obsidian one with the new items
        (a fire cleric's, as in Shattered Lands)."""
        from types import SimpleNamespace
        typ = bytes(game.ITEM_TYPE_SIZE)
        with mock.patch("dsloader.startgear.can_use", lambda gd, sheet, t, r: t == 74):
            self.assertEqual(ravlog.rav_weapon(SimpleNamespace(new_items=False), b"", KIND("mace"), lambda t: typ), None)
            rec, weapon = ravlog.rav_weapon(SimpleNamespace(new_items=True), b"", KIND("mace"), lambda t: typ)
        self.assertEqual((struct.unpack_from("<H", rec, 0x0A)[0], weapon[0]), (74, 74))


class FillTests(FinishNewTests):
    """ravfirstweapon.fill on a party of one New character in the sequel's layout (the types in Shattered
    Lands', as the dice log's read-only view serves them)."""

    def setUp(self):
        ravlog.apply_layout()
        self.addCleanup(ravlog.restore_layout)
        super().setUp()
        rules = game.RULES_IN_FORCE
        game.RULES_IN_FORCE = game.RULES_ALWAYS
        self.addCleanup(setattr, game, "RULES_IN_FORCE", rules)
        for t in range(ravager.GAME_TYPES + 40):
            at = self.TYPES + t * game.ITEM_TYPE_SIZE
            self.mem[at + 0x10:at + 0x12] = b"\xff\xff"  # (every class may use every type, by the game's lists)
            kind = ravager.rav_kinds().get(t)
            if kind is not None:
                self.mem[at] = 0x02 if kind in W.MISSILE_KINDS else 0x01
                self.mem[at + 8] = 4  # (metal)
            if t in TWO_HANDED:
                self.mem[at + 0x0F] = weaponchoice.TWO_HANDED
        self.mem[self.TYPES + SHIELD * game.ITEM_TYPE_SIZE] = 0x04
        self.given = []
        for patch in (mock.patch("dsloader.npcitems.add_to", self.add_to),
                      mock.patch("dsloader.weaponchoice.bow_ahead", lambda gd, m: None)):
            patch.start()
            self.addCleanup(patch.stop)
        self.gd.item_name = lambda n: f"item {n:X}"

    def add_to(self, gd, creature, rec, slot=None):
        self.given.append(struct.unpack_from("<H", rec, game.ITEM_TYPE)[0])
        self.put(rec, 20 + self.items if slot is None else slot)
        return True

    def put(self, rec, slot):
        rec = bytearray(rec)
        rec[game.ITEM_SLOT] = slot
        at = self.ITEMS + self.items * game.ITEM_SIZE
        self.mem[at:at + game.ITEM_SIZE] = rec
        self.items += 1

    def character(self, classes, kinds, race=1):
        s = bytearray(game.SHEET_SIZE)
        s[game.SHEET_CLASSES:game.SHEET_CLASSES + 3] = bytes(classes)
        s[game.SHEET_LEVELS:game.SHEET_LEVELS + 3] = bytes((7, 0, 0))
        s[game.SHEET_RACE] = race
        s[game.SHEET_FLAGS:game.SHEET_FLAGS + 2] = b"\xff\xff"
        s = game.with_specs(bytes(s), [KIND(k) + 1 for k in kinds] + [0] * (game.SPEC_COUNT - len(kinds)))
        self.mem[self.SHEETS:self.SHEETS + game.SHEET_SIZE] = s

    def the(self, kind, n=0):
        return W.PLUS_ONE[KIND(kind)][n]

    def plus(self, n):
        return self.mem[self.ITEMS + n * game.ITEM_SIZE + game.ITEM_PLUS]

    def fighter(self, kinds):
        self.character((FIGHTER, 0, 0), kinds)
        right, left = game.WEAPON_HANDS
        self.put(self.the("long sword").record, right)
        self.put(bytes(game.ITEM_SIZE)[:0x0A] + struct.pack("<H", SHIELD) + bytes(game.ITEM_SIZE - 0x0C), left)
        return right, left

    def test_a_long_sword_pick_keeps_the_sword(self):
        self.fighter(["long sword"])
        self.assertEqual(W.fill(self.gd), [])

    def test_a_lotulis_pick_two_handed_shield_off(self):
        right, left = self.fighter(["lotulis"])
        out = W.fill(self.gd)
        self.assertEqual(self.item(0), (61, right))
        self.assertEqual(self.plus(0), 1)
        self.assertEqual(self.item(1), (SHIELD, 30))  # (into a backpack cell)
        self.assertIn("lotulis +1", out[0])
        self.assertIn("goes into the backpack", out[1])
        self.assertEqual(W.fill(self.gd), [])  # (once)

    def test_a_one_handed_pick_keeps_the_shield(self):
        right, left = self.fighter(["mace"])
        W.fill(self.gd)
        self.assertEqual((self.item(0), self.item(1)), ((67, right), (SHIELD, left)))

    def test_a_gladiator(self):
        """The right hand's sword the first pick's; the left's stays, unless the first is two-handed."""
        self.character((GLADIATOR, 0, 0), ["double spear", "long sword"])
        right, left = game.WEAPON_HANDS
        self.put(self.the("long sword").record, right)
        self.put(self.the("long sword").record, left)
        W.fill(self.gd)
        self.assertEqual((self.item(0), self.item(1)), ((39, right), (LONG_SWORD, 30)))
        self.setUp()
        self.character((GLADIATOR, 0, 0), ["axe", "long sword"])
        self.put(self.the("long sword").record, right)
        self.put(self.the("long sword").record, left)
        W.fill(self.gd)
        self.assertEqual((self.item(0), self.item(1)), ((8, right), (LONG_SWORD, left)))

    def test_a_ranger_plain_sword_made_plus_one(self):
        self.character((RANGER, 0, 0), ["long sword"])
        right, _ = game.WEAPON_HANDS
        plain = bytearray(self.the("long sword").record)
        plain[game.ITEM_PLUS] = 0
        self.put(bytes(plain), right)
        out = W.fill(self.gd)
        self.assertEqual((self.item(0), self.plus(0)), ((LONG_SWORD, right), 1))
        self.assertIn("long sword +1", out[0])

    def test_a_bow_pick_missile_slot_with_arrows(self):
        right, _ = self.fighter(["bow"])
        out = W.fill(self.gd)
        self.assertEqual(self.given, [BOW, ARROWS])
        self.assertEqual(self.item(2), (BOW, weaponchoice.MISSILE_SLOT))
        self.assertEqual(self.item(3), (ARROWS, weaponchoice.AMMO_SLOT))
        self.assertEqual(self.item(0), (LONG_SWORD, right))  # (the sword stays)
        self.assertIn("+1 arrows", out[1])

    def test_a_missile_pick_sends_the_old_one_to_the_backpack(self):
        """A thri-kreen's sling pick: its chatkcha to the backpack, the sling +1 in the missile slot, its gythka kept."""
        self.character((FIGHTER, 0, 0), ["sling"], race=8)
        right, _ = game.WEAPON_HANDS
        self.put(self.the("gythka").record, right)
        self.put(self.the("chatkcha").record, weaponchoice.MISSILE_SLOT)
        out = W.fill(self.gd)
        self.assertEqual((self.item(0), self.item(1), self.item(2)),
                         ((GYTHKA, right), (25, 30), (93, weaponchoice.MISSILE_SLOT)))
        self.assertIn("sling +1", out[0])
        self.assertIn("goes into the backpack", out[1])

    def test_a_kind_made_plus_one(self):
        right, _ = self.fighter(["two-handed sword"])
        out = W.fill(self.gd)
        self.assertEqual((self.item(0), self.plus(0)), ((101, right), 1))
        self.assertIn("made +1", out[0])

    def test_the_mods_only_with_the_new_items(self):
        self.fighter(["short sword"])
        out = W.fill(self.gd, new_items=False)
        self.assertIn("keeps the starting weapon", out[0])
        self.assertEqual(self.item(0)[0], LONG_SWORD)
        W.fill(self.gd)
        self.assertEqual(self.item(0)[0], self.the("short sword").type)

    def test_a_thri_kreen_keeps_its_own(self):
        self.character((FIGHTER, 0, 0), ["gythka"], race=8)
        right, _ = game.WEAPON_HANDS
        self.put(self.the("gythka").record, right)
        self.put(self.the("chatkcha").record, weaponchoice.MISSILE_SLOT)
        self.assertEqual(W.fill(self.gd), [])

    def test_no_pick_nothing(self):
        self.character((AIR_CLERIC, 0, 0), [])
        self.put(self.the("long sword").record, game.WEAPON_HANDS[0])
        self.assertEqual(W.fill(self.gd), [])

    def test_a_material_it_can_use(self):
        """A fighter/fire cleric (obsidian only, with the class restrictions): the obsidian long sword made +1."""
        from dsloader import restrict
        self.gd.rules = game.RULE_RESTRICT
        self.character((FIGHTER, 3, 0), ["long sword"], race=7)
        self.mem[self.TYPES + 73 * game.ITEM_TYPE_SIZE + 8] = restrict.OBSIDIAN
        right, _ = game.WEAPON_HANDS
        plain = bytearray(self.the("long sword").record)
        plain[game.ITEM_PLUS] = 0
        self.put(bytes(plain), right)
        W.fill(self.gd)
        self.assertEqual((self.item(0), self.plus(0)), ((73, right), 1))


class WeaponFirstTests(unittest.TestCase):
    def test_the_weapon_first_others_in_order(self):
        """A chain sling, arrows, double spear (slot 3): the spear first, then the sling and arrows, each record
        keeping its link."""
        from types import SimpleNamespace
        ravlog.apply_layout()
        self.addCleanup(ravlog.restore_layout)
        mem = bytearray(0x10000)
        DS, ITEMS = 0x100, 0x3000
        struct.pack_into("<HH", mem, DS * 16 + game.ITEMS_PTR, ITEMS, 0)
        chain = [(5, 93, 2), (7, 6, 1), (2, 39, 3)]  # (item, type, slot)
        for n, (index, type_, slot) in enumerate(chain):
            rec = bytearray(game.ITEM_SIZE)
            struct.pack_into("<H", rec, game.ITEM_TYPE, type_)
            struct.pack_into("<H", rec, game.ITEM_NEXT, chain[n + 1][0] if n + 1 < len(chain) else 9999)
            rec[game.ITEM_SLOT] = slot
            mem[ITEMS + index * game.ITEM_SIZE:ITEMS + (index + 1) * game.ITEM_SIZE] = rec
        guest = SimpleNamespace(read=lambda a, n: bytes(mem[a:a + n]),
                                write=lambda a, d: mem.__setitem__(slice(a, a + len(d)), d))

        def worn(member, lists=game.CREATURE_ITEM_LISTS):
            if lists != (game.CREATURE_ITEM_LISTS[1],):
                return
            index = chain[0][0]
            while index != 9999:
                rec = bytes(mem[ITEMS + index * game.ITEM_SIZE:ITEMS + (index + 1) * game.ITEM_SIZE])
                yield index, rec, b""
                index = struct.unpack_from("<H", rec, game.ITEM_NEXT)[0]

        def creature(i):
            rec = bytearray(game.CREATURE_SIZE)
            if i == 0:
                rec[game.CREATURE_NAME] = ord("S")
                rec[game.CREATURE_STATUS] = game.STATUS_NEW
            return bytes(rec)
        gd = SimpleNamespace(guest=guest, ds=DS, creature=creature, _worn=worn)
        W.weapon_first(gd)
        got = [(i, struct.unpack_from("<H", r, game.ITEM_TYPE)[0], r[game.ITEM_SLOT]) for i, r, _ in worn(0, (game.CREATURE_ITEM_LISTS[1],))]
        self.assertEqual(got, [(5, 39, 3), (7, 93, 2), (2, 6, 1)])


for _name in [n for n in vars(FinishNewTests) if n.startswith("test") and n not in vars(FillTests)]:
    setattr(FillTests, _name, None)  # (the harness's own tests are weaponchoice's: not run here again)


if __name__ == "__main__":
    unittest.main()
