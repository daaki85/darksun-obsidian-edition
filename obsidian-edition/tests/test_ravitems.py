"""The party transfer's items the sequel lacks, as objects of the Loader's (dsloader/ravitems.py).

Made-up objects here; with DSUN_WOTR (the player's Wake of the Ravager folder) and DSUN_SL (Shattered
Lands'), the kit's trap-user party goes through with every item kept (no money bag)."""

import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dsloader import dataitems, gff, icons, names, npcitems, ravager, ravitems, ravtransfer as rt  # noqa: E402

WOTR, SL = os.environ.get("DSUN_WOTR"), os.environ.get("DSUN_SL")
SAVES = os.path.join(os.path.dirname(__file__), "..", "..", "playtest", "saves")


def record(obj, kind):
    data = bytearray(0x17)
    struct.pack_into("<hH", data, 0, -obj, 0)
    struct.pack_into("<H", data, 0x0A, kind)
    return dataitems.chunk([dataitems.Record(1, 0, 1, 1, 0, bytes(data))], dataitems.HEADER.pack(dataitems.END, 0, 0, 0, 0, 0))


def sl_item(obj, kind, name):
    rec = bytearray(rt.SL_ITEM)
    struct.pack_into("<h", rec, 0, -obj)
    struct.pack_into("<H", rec, 0x0A, kind)
    struct.pack_into("<H", rec, 0x12, name)
    return bytes(rec)


class NumbersTests(unittest.TestCase):
    def test_own_object(self):
        self.assertEqual([ravitems.own_object(o) for o in (2427, 1095, 30032, 31999, 0, 36000)],
                         [22427, 21095, 14032, 15999, None, None])

    def test_type_map_most(self):
        sl = {("RDFF", 1): record(1, 66), ("RDFF", 2): record(2, 66), ("RDFF", 3): record(3, 66)}
        wotr = {("RDFF", 10): record(10, 10), ("RDFF", 11): record(11, 10), ("RDFF", 12): record(12, 5)}
        self.assertEqual(ravitems.type_map({1: 10, 2: 11, 3: 12}, sl, wotr), {66: 10})

    def test_sequel_type(self):
        self.assertEqual(ravitems.sequel_type(115, {}), 102)
        self.assertEqual(ravitems.sequel_type(66, {66: 10}), 10)
        self.assertEqual(ravitems.sequel_type(60, {}), ravitems.KEEPSAKE_TYPE)


class NamesTests(unittest.TestCase):
    def test_names(self):
        sl = bytearray(25 * 4)
        sl[25:25 + 4], sl[50:50 + 12], sl[75:75 + 4] = b"Gem\0", b"Slavepen key", b"Gem\0"
        n = ravitems.Names(bytes(sl), b"Tombstone\r\nGem\r\n", [b"Old one"])
        self.assertEqual(n.number(1), 2)  # (the sequel's Gem: line 1, name 2)
        self.assertEqual(n.number(npcitems.SHORT_SWORD), 258)
        self.assertEqual(n.number(2), ravager.KEEPSAKE_NAMES_FIRST + 1)
        self.assertEqual(n.number(2), ravager.KEEPSAKE_NAMES_FIRST + 1)
        self.assertEqual(n.kept, [b"Old one", b"Slavepen key"])

    def test_item_names_table(self):
        table = ravager.item_names([b"Slavepen key"])
        at = (ravager.KEEPSAKE_NAMES_FIRST - ravager.NAMES_GAME) * ravager.NAME_KEPT
        self.assertEqual(table[at:at + 13], b"Slavepen key\0")
        self.assertEqual(len(table), ravager.NAMES_ROOM * ravager.NAME_KEPT)


class ObjectTests(unittest.TestCase):
    def test_picture_mapped(self):
        sl_palette = [(0, 0, 0)] * 256
        sl_palette[5], sl_palette[6] = (250, 0, 0), (0, 0, 250)
        stable = [(40, (255, 10, 10)), (41, (10, 10, 255))]
        out = icons.decode(ravitems.picture(icons.encode([[0, 5], [6, None]]), sl_palette, stable))
        self.assertEqual(out, [[0, 40], [41, None]])

    def test_item_records(self):
        recs, end = dataitems.records(ravitems.item_records(22427, 2000, b"t" * 15, 102, 258, 0))
        self.assertEqual([(r.level, r.of, r.kind, r.number, r.flags) for r in recs], [(1, 0, 1, 2000, 0), (3, 0, 4, 102, 5)])
        item = recs[0].data
        self.assertEqual((len(item), struct.unpack_from("<h", item, 0)[0], struct.unpack_from("<H", item, 0x0A)[0],
                          struct.unpack_from("<H", item, 0x14)[0], item[0x12:0x14]), (0x17, -22427, 102, 258, b"\x04\xff"))

    def test_make(self):
        pic = icons.encode([[1, 2]])
        sl_objects = {("OJFF", 2427): bytes(12) + struct.pack("<H", 900) + bytes(2), ("BMP ", 900): pic,
                      ("OJFF", 1095): bytes(12) + struct.pack("<H", 901) + bytes(2)}
        table = bytes(range(15)) * 102 + ravager.wotr_type(npcitems.TYPES[0])
        names_ = ravitems.Names(bytes(25 * 400), b"", [])
        pairs, chunks, failed = ravitems.make({2427: sl_item(2427, 115, npcitems.SHORT_SWORD), 1095: sl_item(1095, 60, 5)},
                                              sl_objects, {}, {}, names_, [(0, 0, 0)] * 256, [(1, (0, 0, 0))], table)
        self.assertEqual((pairs, failed), ({2427: 22427}, [(1095, "no picture")]))
        self.assertEqual(struct.unpack_from("<H", chunks[("OJFF", 22427)], 12)[0], 22427)
        recs, _ = dataitems.records(chunks[("RDFF", 22427)])
        self.assertEqual(recs[1].data, ravager.wotr_type(npcitems.TYPES[0]))


@unittest.skipUnless(WOTR and SL, "DSUN_WOTR and DSUN_SL: the player's two game folders")
class GameTests(unittest.TestCase):
    def test_trap_user_every_item(self):
        save = gff.read_gff(open(os.path.join(SAVES, "trap-user", "SAVE01.SAV"), "rb").read())
        with tempfile.TemporaryDirectory() as d:
            sequel, failed = rt.with_added(save, rt.load_sequel(WOTR), SL, WOTR, d)
            self.assertEqual(failed, [])
            _, moved = rt.roster(save, sequel)
            self.assertFalse([old for m in moved for old, new in m.items if new == rt.MONEY_BAG])
            again, _ = rt.with_added(save, rt.load_sequel(WOTR), SL, WOTR, d)  # (kept, not made again)
            self.assertEqual(again.counterparts, sequel.counterparts)
            copy, done = ravager.objects_fixed(open(os.path.join(WOTR, "OBJEX.GFF"), "rb").read(), frozenset(),
                                               ravager.read_added(d))
            self.assertEqual(done, ["mod_types", "transfer_items", "wide_sheets"])  # (the monsters' sheets 48h too)
            self.assertIn(("RDFF", 22427 if ("OJFF", 22427) in sequel.objects else 22419), gff.read_gff(copy))


if __name__ == "__main__":
    unittest.main()
