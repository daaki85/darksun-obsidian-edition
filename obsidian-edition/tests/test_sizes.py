"""The creature size rule (game.RULE_SIZE; DSCLOG's SIZE): AD&D's large weapon dice on a large target
(SIZE_DICE, from CAH_SWING), Hold Person and Charm Person sparing one (SIZE_SPARED, from SAVE_SUM), what
counts as large (IS_LARGE: Enlarged, the Loader's LARGE_BITS, a half-giant), and the Loader's side
(sizes.py)."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, sizes, specialize  # noqa: E402

import test_cahulaks as tc  # noqa: E402
import test_dsclog as td  # noqa: E402

SS, BP, GAME_DS = td.SS, td.BP, td.GAME_DS
RULE = 16384  # RULES_HI's RULE_HI_SIZE
LONG_SWORD, MACE, AXE = 41, 20, 22  # (types of those kinds: DSCLOG's KIND_OF_TYPE)


def load_tests(loader, tests, pattern):
    suite = loader.loadTestsFromTestCase(LoaderTests)
    suite.addTests(SizeTests(name) for name in sorted(vars(SizeTests)) if name.startswith("test_"))
    return suite


class Gd:
    """A game for sizes.py: combatant N is creature N, NAMES and RACES by creature, EFFECTS (owner, id)."""
    def __init__(self, names, races, effects=()):
        self.names, self.races, self._effects = names, races, effects

    def combatants(self):
        return {n: n for n in range(len(self.names))}

    def combatant_creature(self, combatant):
        return combatant if 0 <= combatant < len(self.names) else None

    def creature_name(self, creature):
        return self.names[creature]

    def sheet(self, creature):
        return bytes(0x18) + bytes([self.races[creature]]) + bytes(0x2E)

    def effects(self):
        return [game.Effect(owner, owner, effect) for owner, effect in self._effects]


class LoaderTests(unittest.TestCase):
    def test_rule(self):
        self.assertEqual(game.RULE_SIZE >> 16, RULE)
        self.assertIn(("creature_size", game.RULE_SIZE), game.RULE_SETTINGS)

    def test_large_dice(self):
        """One entry a weapon kind; AD&D's large dice where they differ from its small ones."""
        self.assertEqual(len(sizes.LARGE_DICE), len(specialize.KINDS))
        kinds = dict(zip(specialize.KINDS, sizes.LARGE_DICE))
        self.assertEqual(kinds["long sword"], (1, 12, 0))
        self.assertEqual(kinds["great axe"], (2, 8, 0))
        self.assertIsNone(kinds["axe"])
        self.assertEqual(sizes.dice_change(LONG_SWORD, True, 0), (1, 12, 0))
        self.assertIsNone(sizes.dice_change(LONG_SWORD, False, 0))
        self.assertEqual(sizes.dice_change(sizes.SHILLELAGH_TYPE, False, None), (1, 6, 1))
        self.assertIsNone(sizes.dice_change(sizes.SHILLELAGH_TYPE, True, None))
        self.assertEqual(sizes.dice_change(sizes.HAMMER_TYPE, True, None), (1, 4, -1))

    def test_large_table(self):
        gd = Gd(["Cermak", "Bulette", "Guard", "Guard", "Gerakis", "Silt Horror", "Slig"], [1, 12, 12, 1, 5, 12, 14])
        table = sizes.large_table(gd)
        self.assertEqual(len(table), sizes.LARGE_BYTES)
        bits = {n for n in range(sizes.MAP_COUNT) if table[n // 8] >> (n % 8) & 1}
        self.assertEqual(bits, {1, 2, 4, 5})  # (the monster Guard, not the human one; the half-giant)

    def test_spared(self):
        """Hold Person and Charm Person on a large one (or an Enlarged); Charm Person or Mammal only
        on a large person (a mammal monster is charmed whatever its size); other spells never."""
        gd = Gd(["Cermak", "Gerakis", "Bulette", "Tyr"], [1, 5, 12, 1], effects=((3, sizes.ENLARGED),))
        self.assertFalse(sizes.spared(gd, 30, 0))
        self.assertTrue(sizes.spared(gd, 30, 1))
        self.assertTrue(sizes.spared(gd, 86, 2))
        self.assertTrue(sizes.spared(gd, 2, 3))   # (Enlarged)
        self.assertTrue(sizes.spared(gd, 82, 1))
        self.assertFalse(sizes.spared(gd, 82, 2))  # (a beast: the mammal half)
        self.assertFalse(sizes.spared(gd, 63, 1))  # (Hold Monster)
        self.assertFalse(sizes.spared(gd, 30, 9))


@unittest.skipIf(td.Uc is None, "unicorn not installed")
class SizeTests(tc.CahulaksTests):
    def large(self, thing, on=True):
        tail, = struct.unpack("<H", self.mu.mem_read(self.hdr + 1834, 2))
        off, = struct.unpack("<H", self.mu.mem_read(self.hdr + 1842, 2))
        at = tail * 16 + off + thing // 8
        byte = self.mu.mem_read(at, 1)[0]
        self.mu.mem_write(at, bytes([byte | 1 << (thing % 8) if on else byte & ~(1 << (thing % 8))]))

    def dice(self, kind, rules=RULE, index=0, made=0, item=3, count=2, sides=4, bonus=0):
        """CAH_SWING (with no cahulaks: SIZE_DICE alone) on the target set: [BP-0Eh..-12h] after."""
        self.rules_hi(rules)
        self.word("cah_who", -1)
        self.frame(m4=99, m14=index, mA=made, m8=2, p12=item, p14=kind, p16=1, p18=6, pA=12,
                   mE=count, m10=sides, m12=bonus)
        self.assertEqual(self.where("cahulaks_swing", ()), "end")
        return struct.unpack("<hhh", self.mu.mem_read(SS * 16 + BP - 0x12, 6))[::-1]

    def test_header(self):
        tail, = struct.unpack("<H", self.mu.mem_read(self.hdr + 1834, 2))
        off, = struct.unpack("<H", self.mu.mem_read(self.hdr + 1842, 2))
        self.assertTrue(tail and off)  # (LARGE_BITS: in the tail, not in the map's image section)
        self.assertEqual(bytes(self.mu.mem_read(tail * 16 + off, sizes.LARGE_BYTES)), bytes(sizes.LARGE_BYTES))

    def test_large_dice(self):
        """SIZE_DICE: a long sword's 1d12 on a large target (the Loader's bit), a mace's 1d6 (its +1 off),
        an axe as it was; on a smaller one as they were; Shillelagh 1d6+1 on a smaller one and its 2d4
        on a large one; the Spiritual Hammer 1d4 on a large one; only the call's first swing, an item,
        and the rule on."""
        self.target(thing=20, race=1)
        self.large(20)
        self.assertEqual(self.dice(LONG_SWORD, count=1, sides=8), (1, 12, 0))
        self.assertEqual(self.dice(MACE, count=1, sides=6, bonus=1), (1, 6, 0))
        self.assertEqual(self.dice(AXE, count=1, sides=6), (1, 6, 0))
        self.assertEqual(self.dice(sizes.SHILLELAGH_TYPE), (2, 4, 0))
        self.assertEqual(self.dice(sizes.HAMMER_TYPE, count=1, sides=4, bonus=1), (1, 4, 0))
        for change in (dict(rules=0), dict(index=1), dict(item=-1)):
            self.assertEqual(self.dice(LONG_SWORD, count=1, sides=8, **change), (1, 8, 0), change)
        self.assertEqual(self.dice(LONG_SWORD, count=1, sides=8, index=2, made=2), (1, 12, 0))
        self.large(20, False)
        self.assertEqual(self.dice(LONG_SWORD, count=1, sides=8), (1, 8, 0))
        self.assertEqual(self.dice(sizes.SHILLELAGH_TYPE), (1, 6, 1))
        self.assertEqual(self.dice(sizes.HAMMER_TYPE, count=1, sides=4, bonus=1), (1, 4, 1))

    def test_what_is_large(self):
        """IS_LARGE: the Loader's bit, a half-giant (its race), or Enlarged (the game's effect 16)."""
        self.target(thing=21, race=game.RACE_HALF_GIANT, creature=8)
        self.assertEqual(self.dice(LONG_SWORD, count=1, sides=8), (1, 12, 0))
        self.target(thing=22, race=1)
        self.assertEqual(self.dice(LONG_SWORD, count=1, sides=8), (1, 8, 0))
        self.effects((22, sizes.ENLARGED))
        self.assertEqual(self.dice(LONG_SWORD, count=1, sides=8), (1, 12, 0))
        self.effects((23, sizes.ENLARGED), (22, 3))
        self.assertEqual(self.dice(LONG_SWORD, count=1, sides=8), (1, 8, 0))

    def save(self, spell, thing, rules=RULE, mods=2):
        """SAVE_SUM with a d20 of 10 and MODS on SPELL at THING: the sum."""
        self.rules_hi(rules)
        self.frame(m2=10 | 14 << 8, m20=0, p6=thing, p8=6, pA=spell)
        self.where("save_sum", (8,), eax=mods & 0xFF)
        got = self.mu.mem_read(SS * 16 + BP - 2, 1)[0]
        return got - 256 if got >= 128 else got

    def test_spared(self):
        """SIZE_SPARED: Hold Person (both) and Charm Person on a large target, Charm Person or Mammal on
        a large person, saved (SAVE_MOST, 110); a man-sized one, a beast for Charm Person or Mammal,
        another spell or the rule off: the sum as it was."""
        self.effects()
        self.target(thing=30, race=game.RACE_HALF_GIANT, creature=8)
        self.target(thing=31, race=1, creature=9)
        self.target(thing=32, race=12, creature=10)
        self.large(32)
        for spell in (2, 30, 86, 82):
            self.assertEqual(self.save(spell, 30), 110, spell)
            self.assertEqual(self.save(spell, 31), 12, spell)
        self.assertEqual(self.save(30, 32), 110)
        self.assertEqual(self.save(82, 32), 12)
        self.assertEqual(self.save(63, 30), 12)
        self.assertEqual(self.save(30, 30, rules=0), 12)


if __name__ == "__main__":
    unittest.main()
