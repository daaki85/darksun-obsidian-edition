"""The weapons for the kits with too few (worldgear.py): Hayneedle in Merzol's hay stash
(haystash.py, on a script shaped as the hay's: the sack found, left, its flag set), Nightsliver,
Dunesong and Skycutter with their holders."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import dataitems, game, gpl, haystash as h, icons, names, restrict, worldgear
from dsloader.kalzith import _Script
from test_elvenleader import FIELDS, added


def hay():
    s = _Script()
    s.op(0x4F, ("n", 98), ("str", "You find a large sack of ceramic pieces. "))
    s.op(0x09, ("var", 137, 37))
    s.op(h.DROP, ("n", -h.SACK), ("n", 1), h.AT_X, h.AT_Y, ("n", 6), ("n", 0))
    s.op(h.SET, ("n", 1), h.FOUND)
    s.op(0x4F, ("n", 98), ("str", "Done. "))
    return s.bytes(end=True)


class HayStashTests(unittest.TestCase):
    def setUp(self):
        self.script = hay()
        self.out = h.with_dagger(self.script, FIELDS)
        self.ops = gpl.decode(self.script, FIELDS)
        self.added = added(self.script, self.out)

    def test_the_flag_jumps_to_the_dagger(self):
        flag = next(o for o in self.ops if o.code == h.SET and o.args[1] == h.FOUND)
        r = gpl._Reader(self.out, FIELDS)
        r.i = flag.at
        jump = gpl._op(r)
        self.assertEqual((jump.code, jump.args), (0x64, [("n", len(self.script))]))
        self.assertEqual(self.out[:flag.at], self.script[:flag.at])

    def test_left_beside_the_sack(self):
        drop = next(o for o in self.added if o.code == h.DROP)
        self.assertEqual(drop.args, [("n", -worldgear.HAYNEEDLE_OBJECT), ("n", 1), h.AT_X, h.AT_Y, ("n", 6), ("n", 0)])
        self.assertIn("bone dagger", " ".join(gpl.strings(self.added)))

    def test_then_the_flag_and_back(self):
        after = next(o for o in self.ops if o.code == 0x4F and ("str", "Done. ") in o.args)
        self.assertEqual([(o.code, o.args) for o in self.added[-2:]],
                         [(h.SET, [("n", 1), h.FOUND]), (0x64, [("n", after.at)])])

    def test_once(self):
        self.assertEqual(h.with_dagger(self.out, FIELDS), self.out)

    def test_other_script_unchanged(self):
        s = _Script()
        s.op(0x4F, ("n", 98), ("str", "Hello. "))
        script = s.bytes(end=True)
        self.assertEqual(h.with_dagger(script, FIELDS), script)
        self.assertEqual(h.script_chunks({("GPL ", h.SCRIPT): script}, FIELDS), {})
        self.assertEqual(set(h.script_chunks({("GPL ", h.SCRIPT): self.script}, FIELDS)), {("GPL ", h.SCRIPT)})


class WeaponTests(unittest.TestCase):
    def test_named_priced_held(self):
        """Each its type, plus, price, name (DSCLOG's) and icon; Nightsliver in place of the
        Hermit's stone dagger, Dunesong at the Bowyer's with Windlash, Skycutter on a Gemfields
        thri-kreen of its own."""
        cases = ((worldgear.BONE_DAGGER_1, game.BONE_DAGGER_TYPE, 1, worldgear.PLUS_VALUE, "Hayneedle"),
                 (worldgear.OBSIDIAN_DAGGER_2, 17, 2, 2 * worldgear.PLUS_VALUE, "Nightsliver"),
                 (worldgear.BOW_1, 1, 1, worldgear.PLUS_VALUE, "Dunesong"),
                 (worldgear.CHATKCHA_2, 48, 2, 3500, "Skycutter"))
        for spec, type_, plus, value, name in cases:
            item = worldgear.weapon(*spec)
            self.assertEqual((struct.unpack_from("<H", item, game.ITEM_TYPE)[0], item[game.ITEM_PLUS]), (type_, plus))
            self.assertEqual(struct.unpack_from("<H", item, 6)[0], value)
            self.assertEqual(icons.which(item), name)
            self.assertEqual(names.NAMES[struct.unpack_from("<H", item, game.ITEM_NAME)[0]], name.encode())
            self.assertEqual(-struct.unpack_from("<h", item, 0)[0], icons.ICONS[[i[0] for i in icons.ICONS].index(name)][2])
        held = {g.name: g for g in worldgear.MAGIC}
        self.assertEqual((held["Hermit"].objects, held["Hermit"].region, held["Hermit"].instead), ((81,), 0x1B, (33, 0)))
        self.assertIn(worldgear.weapon(*worldgear.BOW_1), held["Bowyer"].items)
        self.assertIn(worldgear.weapon(*worldgear.STAFF_SLING_1), held["Bowyer"].items)
        self.assertEqual((held["Thrikreen"].objects, held["Thrikreen"].region, held["Thrikreen"].clone),
                         ((215,), 0x06, (22, 2598)))
        self.assertEqual(worldgear.HAYNEEDLE_ITEM, worldgear.weapon(*worldgear.BONE_DAGGER_1))
        # (the plain ones still the plain ones)
        self.assertEqual(icons.which(worldgear.weapon(worldgear.BONE_DAGGER)), "Bone Dagger")
        for spec in ((17, 0x10, 0xFB60, 2), (1, 0x02, 0xFC07, 30), (48, 0x39, 0xFC0E, 2)):
            self.assertIsNone(icons.which(worldgear.weapon(spec)))

    def test_the_hermits_stone_dagger_replaced(self):
        from test_worldgear import GUARD, rdff
        staff = worldgear.weapon((3, 0x04, 0xFC05, 1))
        hermit = rdff(GUARD, [staff, worldgear.weapon((33, 0x10, 0xFB5A, 1))])
        out = worldgear.object_chunks({("RDFF", 81): hermit}, [g for g in worldgear.MAGIC if g.name == "Hermit"])
        items = dataitems.items_of(out[("RDFF", 81)])
        self.assertEqual([icons.which(r) for r in items], [None, "Nightsliver"])
        self.assertEqual(struct.unpack_from("<H", items[0], game.ITEM_TYPE)[0], 3)  # (his staff kept)

    def test_hayneedles_own_object(self):
        """With the world's magic: Hayneedle's record as an object of its own (the stash's script
        drops it); its picture's object one of the icons'."""
        self.assertIn(worldgear.HAYNEEDLE_OBJECT, [i[2] for i in icons.ICONS])
        self.assertNotIn(worldgear.HAYNEEDLE_OBJECT, [g.clone[1] for g in worldgear.MAGIC + worldgear.GIFTS if g.clone])

    def test_daggers_for_water_and_fire(self):
        """Hayneedle a water cleric's (bone), Nightsliver a fire cleric's (obsidian)."""
        import test_restrict
        from dsloader import npcitems
        water = test_restrict.sheet(4, race=game.HUMAN)
        self.assertTrue(restrict.usable(water, game.BONE_DAGGER_TYPE,
                                        npcitems.TYPES[game.BONE_DAGGER_TYPE - game.GAME_TYPES]))
        fire = test_restrict.sheet(3, race=game.HUMAN)
        self.assertTrue(restrict.usable(fire, 17, test_restrict.record(17)))


if __name__ == "__main__":
    unittest.main()
