import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import kits  # noqa: E402


class KitEffectTests(unittest.TestCase):
    def test_ravager(self):
        self.assertEqual((kits.melee(kits.RAVAGER, False), kits.melee(kits.RAVAGER, True), kits.move(kits.RAVAGER)),
                         (1, 1, 0))
        self.assertEqual(kits.name(kits.RAVAGER), "Ravager")
        # the table by level (1-10, the highest the game goes; 10th's held past it), where it betters the sheet's base AC
        self.assertEqual([kits.ac(kits.RAVAGER, False, level) for level in (1, 2, 3, 9, 11, 12, 15, 18, 20)],
                         [-3, -3, -4, -7, -7, -7, -7, -7, -7])
        self.assertEqual(kits.ac(kits.RAVAGER, False, 1, base=5), 0)
        self.assertEqual(kits.ac(kits.RAVAGER, False, 3, base=8), -2)

    def test_brute(self):
        self.assertEqual((kits.melee(kits.BRUTE, True), kits.melee(kits.BRUTE, False)), (2, 0))

    def test_wanderer(self):
        self.assertEqual(kits.ac(kits.WANDERER, True), 1)
        self.assertEqual([kits.save(kits.WANDERER, 0, k) for k in (kits.FIRE, kits.COLD, 1, 0x08)], [3, 3, 0, 0])
        self.assertEqual(kits.save(kits.WANDERER, 300, kits.FIRE), 0)
        self.assertEqual(kits.save(kits.SENTINEL, 0, kits.FIRE), -1)

    def test_champion(self):
        self.assertEqual((kits.ac(kits.CHAMPION, True), kits.ac(kits.CHAMPION, False)), (-1, 0))
        self.assertEqual([kits.champion(kits.CHAMPION, s, m) for s in (True, False) for m in (True, False)],
                         [(1, 1), (0, 0), (-1, 0), (0, 0)])
        self.assertEqual(kits.champion(kits.SENTINEL, False, True), (0, 0))

    def test_sentinel(self):
        self.assertEqual((kits.ac(kits.SENTINEL, True), kits.ac(kits.SENTINEL, False)), (-2, 0))
        self.assertEqual((kits.melee(kits.SENTINEL, True), kits.move(kits.SENTINEL)), (0, 0))

    def test_none(self):
        self.assertEqual((kits.melee(0, True), kits.ac(0, True), kits.move(0), kits.name(0)), (0, 0, 0, ""))

    def test_seeker(self):
        """A Seeker's sphere weapons, as a cleric's of that sphere, but the bow whatever the sphere."""
        def weapon(flags, mat):
            t = bytearray(0x14)
            t[0], t[8] = flags, mat
            return bytes(t)
        S = kits.SEEKER
        obsidian_sword, bone_sword, bow = weapon(kits.MELEE, 3), weapon(kits.MELEE, 1), weapon(kits.MISSILE, 0)
        self.assertEqual([kits.forbids(S, obsidian_sword, 0, False, sphere=s) for s in range(4)], [True, False, False, True])
        self.assertEqual([kits.forbids(S, bone_sword, 0, False, sphere=s) for s in range(4)], [True, True, True, False])
        self.assertEqual([kits.forbids(S, bow, kits.BOW, False, sphere=s) for s in range(4)], [False] * 4)
        self.assertFalse(kits.forbids(S, weapon(kits.MELEE, 3), 2, False, sphere=0))  # (air: a dagger)
        self.assertFalse(kits.forbids(kits.JUSTIFIER, bone_sword, 0, False, sphere=2))

    def test_forbids(self):
        def typ(flags=0, kinds=0, mat=0x40):
            t = bytearray(0x14)
            t[0], t[0x0F], t[8] = flags, kinds, mat
            return bytes(t)
        R = kits.RAVAGER
        self.assertTrue(kits.forbids(R, typ(kits.SHIELD), None, False))
        self.assertTrue(kits.forbids(R, typ(kits.MISSILE), 13, False))
        self.assertTrue(kits.forbids(R, typ(kits.MELEE | kits.THROWN), 2, False))
        self.assertTrue(kits.forbids(R, typ(0, kits.ARMOUR, kits.METAL), None, False))
        self.assertFalse(kits.forbids(R, typ(0, kits.ARMOUR, kits.LEATHER), None, False))
        self.assertFalse(kits.forbids(R, typ(kits.MELEE, kits.TWO_HANDED, kits.METAL), 6, False))


if __name__ == "__main__":
    unittest.main()
