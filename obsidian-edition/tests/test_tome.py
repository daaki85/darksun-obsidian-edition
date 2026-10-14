"""The Tome of Understanding (tome.py) and Father Garyn's gift of it (garyn.py), on a script
shaped as his: the extract's words, the pith delivered (its flag), his talk going on."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import dataitems, game, garyn as g, gpl, icons, names, tome
from dsloader.kalzith import _Script
from test_elvenleader import FIELDS, added

DOT = icons.encode([[74, 182], [78, 45]])  # (a book's icon: two reds, two golds)


class TomeItemTests(unittest.TestCase):
    def test_a_scroll_the_game_has_no_use_for(self):
        """A scroll (type 96) of an object in the game's scrolls' numbers, its spell byte one past
        TOME_SPELL (172 or more: the game keeps such a scroll; DSCLOG's probe reads it)."""
        rec = tome.item()
        self.assertEqual(len(rec), game.ITEM_SIZE)
        self.assertTrue(1400 <= -struct.unpack_from("<h", rec, 0)[0] <= 1499)
        self.assertEqual(struct.unpack_from("<H", rec, game.ITEM_TYPE)[0], 96)
        self.assertTrue(0xAC <= rec[0x0F] - 1 < 0xC4)
        self.assertEqual(struct.unpack_from("<H", rec, game.ITEM_NAME)[0], tome.NAME)
        self.assertEqual(struct.unpack_from("<H", rec, 0x06)[0], 43500)
        self.assertTrue(tome.is_tome(rec))

    def test_name_in_dsclog(self):
        self.assertEqual(names.NAMES[tome.NAME], b"Tome/Understand")
        self.assertLessEqual(len(names.NAMES[tome.NAME]), 15)

    def chunks(self):
        book = bytearray(16)
        struct.pack_into("<H", book, icons.OJFF_ICON, 765)
        owner = bytearray(16)
        struct.pack_into("<H", owner, icons.OJFF_ICON, tome.TOME_OBJECT)
        scroll = bytearray(16)
        scroll[4] = 4  # (a scroll's kind)
        return {("OJFF", tome.BOOK): bytes(book), ("BMP ", tome.BOOK): b"book on the map", ("BMP ", 765): DOT,
                ("OJFF", tome.SCROLL): bytes(scroll),
                ("OJFF", 1298): bytes(owner), ("BMP ", tome.TOME_OBJECT): b"someone's icon"}

    def test_objects(self):
        """Its object the book's with an icon of its own (night steel, a fire emblem); the
        picture its number had moved, with its owners; its record."""
        out = tome.object_chunks(self.chunks(), 636)
        self.assertEqual(out[("BMP ", tome.MOVED)], b"someone's icon")
        self.assertEqual(struct.unpack_from("<H", out[("OJFF", 1298)], icons.OJFF_ICON)[0], tome.MOVED)
        self.assertEqual(struct.unpack_from("<H", out[("OJFF", tome.TOME_OBJECT)], icons.OJFF_ICON)[0], tome.ICON)
        self.assertEqual(out[("OJFF", tome.TOME_OBJECT)][4], 4)  # (the scroll's kind: its icon clicked)
        self.assertEqual(out[("BMP ", tome.TOME_OBJECT)], b"book on the map")
        rows = icons.decode(out[("BMP ", tome.ICON)])
        self.assertEqual(rows[0][0], tome.COVER[74])
        self.assertIn(rows[0][1], icons.FIRE)
        recs, _ = dataitems.records(out[("RDFF", tome.TOME_OBJECT)])
        self.assertEqual((recs[0].number, recs[0].data[:2]), (636, tome.item()[:2]))

    def test_taken(self):
        chunks = self.chunks()
        chunks[("OJFF", tome.TOME_OBJECT)] = b"x"
        with self.assertRaises(KeyError):
            tome.object_chunks(chunks)


def his():
    s = _Script()
    s.op(0x4F, ("n", 115), ("str", "Thank you. "))
    s.op(0x4F, ("n", 115), ("str", "The extract is made by mixing the pith with the concoctions "))
    s.op(0x4F, ("n", 115), g.EXTRACT)
    s.op(g.SET, ("n", 1), g.DELIVERED)
    s.op(g.SET, ("n", 0), ("var", 14, 13))
    s.op(0x4F, ("n", 115), ("str", "You will find Linara in Gedron. "))
    return s.bytes(end=True)


class GarynTests(unittest.TestCase):
    def setUp(self):
        self.script = his()
        self.out = g.with_tome(self.script, FIELDS)
        self.ops = gpl.decode(self.script, FIELDS)
        self.added = added(self.script, self.out)

    def test_the_flag_jumps_to_the_tome(self):
        flag = next(o for o in self.ops if o.code == g.SET and o.args[1] == g.DELIVERED)
        r = gpl._Reader(self.out, FIELDS)
        r.i = flag.at
        jump = gpl._op(r)
        self.assertEqual((jump.code, jump.args), (0x64, [("n", len(self.script))]))
        self.assertEqual(self.out[:flag.at], self.script[:flag.at])

    def test_first_time_given_or_left(self):
        self.assertEqual((self.added[0].code, self.added[0].args), (g.TEST, [g.FIRST_TIME]))
        give = next(o for o in self.added if o.code == g.TEST and "Op(at=" in str(o.args))
        self.assertIn("('n', -1446), ('var', 137, 37), ('n', 9999)", str(give.args))
        drop = next(o for o in self.added if o.code == g.DROP)
        self.assertEqual(drop.args[0], ("n", -tome.TOME_OBJECT))
        lines = " ".join(gpl.strings(self.added))
        self.assertIn("take this, for your kindness", lines)
        self.assertIn("I will leave it here", lines)

    def test_then_the_flag_and_back(self):
        after = next(o for o in self.ops if o.code == g.SET and o.args[1] == ("var", 14, 13))
        self.assertEqual([(o.code, o.args) for o in self.added[-2:]],
                         [(g.SET, [("n", 1), g.DELIVERED]), (0x64, [("n", after.at)])])

    def test_once(self):
        self.assertEqual(g.with_tome(self.out, FIELDS), self.out)

    def test_other_script_unchanged(self):
        s = _Script()
        s.op(0x4F, ("n", 115), ("str", "Hello. "))
        script = s.bytes(end=True)
        self.assertEqual(g.with_tome(script, FIELDS), script)
        self.assertEqual(g.script_chunks({("GPL ", 174): script}, FIELDS), {})


if __name__ == "__main__":
    unittest.main()
