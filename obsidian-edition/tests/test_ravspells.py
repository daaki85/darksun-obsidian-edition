"""The mod's six new wizard spells in Wake of the Ravager's RESOURCE.GFF copy (dsloader.ravspells): their
numbers, records, descriptions and icons. With DSUN_WOTR (and DSUN_SL for the icons: Shattered Lands'
drawn ones) the copy is made from the player's own files (never in the repository)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, gff, ravager, ravspells, sequelicons, spelltexts  # noqa: E402

WOTR = os.environ.get("DSUN_WOTR")
SL = os.environ.get("DSUN_SL")


class TableTests(unittest.TestCase):
    def test_numbers_past_the_table(self):
        """Six numbers past the sequel's 320 records, in Shattered Lands' order (196-201 there)."""
        self.assertEqual(list(ravspells.SPELLS), list(range(ravager.SPELL_COUNT, ravager.SPELL_COUNT + 6)))
        self.assertEqual([ravspells.SL_NUMBER[s] for s in ravspells.SPELLS], list(game.NEW_SPELLS))
        self.assertEqual([ravspells.SPELLS[s] for s in ravspells.SPELLS], list(game.NEW_SPELLS.values()))
        self.assertEqual(ravspells.SPELL_SIZE, ravager.SPELL_SIZE)

    def test_texts(self):
        got = ravspells.texts()
        self.assertEqual(sorted(n for _, n in got), list(range(321, 327)))
        self.assertTrue(got[("SPIN", 324)].startswith(b"REFLECTED IMAGE:"))
        self.assertTrue(all(v.endswith(b"\r\n") and len(v) < 195 for v in got.values()))
        self.assertEqual(got[("SPIN", 321)], spelltexts.TEXTS[197].encode() + b"\r\n")

    def test_switch(self):
        self.assertNotIn(ravspells.SKIP, ravager.skipped({}))
        self.assertIn(ravspells.SKIP, ravager.skipped({"new_spells": False}))

    def test_record_from_templates(self):
        """Each record is its template's first 32 bytes with SL's NS_PATCHES, then the name and short name."""
        def rec(name):
            return bytes(range(32)) + name.ljust(41, b"\0")
        chunks = {("DATA", n): rec(b"X") for n in range(0, 40)}
        r = ravspells.record(chunks, ravspells.REFLECT)
        self.assertEqual(r[4], 0x11)
        self.assertEqual(r[5:7], b"\0\0")
        self.assertEqual(r[32:48], b"REFLECTED IMAGE\0")
        self.assertEqual(r[64:73], b"REFLIMAG\0")
        spook = ravspells.record(chunks, ravspells.SPOOK)
        self.assertEqual((spook[4], spook[7:9], spook[0x11:0x13], spook[0x19]), (0x13, b"\x3c\0", b"\x04\x43", 35))
        fog = ravspells.record(chunks, ravspells.FOG)
        self.assertEqual((fog[4], fog[0x11:0x13]), (0x42, b"\0\x40"))
        friends = ravspells.record(chunks, ravspells.FRIENDS)
        self.assertEqual((friends[1:3], friends[0x0C], friends[0x1D]), (b"\xff\xff", 7, 1))


@unittest.skipUnless(WOTR, "DSUN_WOTR: the player's Wake of the Ravager folder")
class GameFileTests(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(WOTR, ravager.RESOURCE_FILE), "rb") as f:
            self.data = f.read()
        self.game = gff.read_gff(self.data)

    def test_free_numbers(self):
        """Every record 0-319 is the game's (no free wizard number below 120: 115-119 are priest
        spells), and none past it."""
        names = [self.game[("DATA", n)][32:64].split(b"\0")[0].strip() for n in range(320)]
        self.assertTrue(all(names))
        self.assertEqual(names[115:120], [b"BLESS", b"CURSE", b"CURE LIGHT WOUNDS", b"CAUSE LIGHT WOUNDS", b"ENTANGLE"])
        self.assertFalse(any(("DATA", n) in self.game for n in ravspells.SPELLS))
        self.assertFalse(any(("SPIN", n + 1) in self.game or ("ICON", 21000 + n) in self.game for n in ravspells.SPELLS))

    def test_copy_has_them(self):
        out, done = ravager.resources_fixed(self.data, frozenset(), None, SL)
        self.assertIn(ravspells.SKIP, done)
        got = gff.read_gff(out)
        for spell in ravspells.SPELLS:
            self.assertEqual(len(got[("DATA", spell)]), ravager.SPELL_SIZE)
            self.assertIn(("SPIN", spell + 1), got)
            rows = sequelicons.decode(got[("ICON", 21000 + spell)])
            self.assertEqual((len(rows), len(rows[0])), (16, 16))
        off, _ = ravager.resources_fixed(self.data, frozenset({ravspells.SKIP}), None, SL)
        without = gff.read_gff(off)
        self.assertNotIn(("DATA", ravspells.GRACE), without)
        self.assertEqual(set(got) - set(without), set(ravspells.chunks(self.game)))
        for key, value in without.items():  # (nothing else changed: the GFFI index grows)
            if key[0] != "GFFI":
                self.assertEqual(got[key], value, key)
        self.assertEqual(got[("DATA", ravspells.REFLECT)][:4], self.game[("DATA", 19)][:4])

    @unittest.skipUnless(SL, "DSUN_SL: Shattered Lands' folder, for the drawn icons")
    def test_drawn_icons(self):
        """With Shattered Lands' files the icons are the mod's drawn ones, not the templates'."""
        got = ravspells.icons_for(self.game, SL)
        for spell in ravspells.SPELLS:
            self.assertNotEqual(got[("ICON", 21000 + spell)], self.game[("ICON", 21000 + ravspells.TEMPLATES[spell])])


if __name__ == "__main__":
    unittest.main()
