"""A saved Wake of the Ravager game's sellers given the mod's new items once (dsloader/shopstock.py).

Made-up records here; with DSUN_WOTR (the player's Wake of the Ravager folder) and DSUN_SL (Shattered
Lands'), the sellers' items from ravgear's chunks."""

import os
import struct
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dsloader import dataitems, gff, ravager, ravgear, shopstock  # noqa: E402

WOTR, SL = os.environ.get("DSUN_WOTR"), os.environ.get("DSUN_SL")
END = dataitems.HEADER.pack(dataitems.END, 0, 0, 0, 0, 0)


def item(picture):
    data = bytearray(0x17)
    struct.pack_into("<h", data, 0, -picture)
    return bytes(data)


def seller(obj, pictures):
    person = bytearray(0x31)
    struct.pack_into("<h", person, shopstock.CREATURE_OBJECT, -obj)
    recs = [dataitems.Record(1, 0, 2, 1, 0, bytes(person))]
    first = len(recs)
    recs.append(dataitems.Record(dataitems.FIRST, 0, dataitems.ITEM, 0, ravgear.PACK, item(pictures[0])))
    for p in pictures[1:]:
        recs.append(dataitems.Record(dataitems.NEXT, first, dataitems.ITEM, 0, ravgear.NEXT_FLAGS, item(p)))
        first = len(recs) - 1
    return dataitems.chunk(recs, END)


class FakeGD:
    def __init__(self, obj, marked=0):
        self.rec = bytearray(0x31)
        struct.pack_into("<h", self.rec, shopstock.CREATURE_OBJECT, -obj)
        self.rec[shopstock.CREATURE_MARK] = marked
        self.rec[0x21:0x27] = b"Notaku"

    def creature(self, index):
        return bytes(self.rec)

    def creature_name(self, index):
        return "Notaku"


class StockTests(unittest.TestCase):
    def test_seller_items_are_ravgears(self):
        ss1 = ravgear.picture_object("short sword +1")
        objects = {("RDFF", 58): seller(58, [632, 648, ss1])}
        stock = shopstock.seller_items(objects, (58, 153))
        self.assertEqual(list(stock), [58])  # (153 isn't in these chunks)
        self.assertEqual([-struct.unpack_from("<h", r, 0)[0] for r in stock[58]], [ss1])

    def test_top_up_adds_the_missing_and_marks(self):
        ss1, pick = ravgear.picture_object("short sword +1"), ravgear.picture_object("metal pick")
        stock = {58: [item(ss1), item(pick)]}
        added, marked = [], []
        with mock.patch.object(shopstock, "held_pictures", return_value={pick}):
            lines = shopstock.top_up(FakeGD(58), 5, stock, marked.append,
                                     add=lambda gd, c, rec: added.append(rec) or True)
        self.assertEqual(added, [item(ss1)])  # (the pick it holds already left out)
        self.assertEqual(marked, [5])
        self.assertEqual(lines, ["Notaku stocks 1 of the mod's new items"])

    def test_top_up_with_all_held_only_marks(self):
        ss1 = ravgear.picture_object("short sword +1")
        marked = []
        with mock.patch.object(shopstock, "held_pictures", return_value={ss1}):
            lines = shopstock.top_up(FakeGD(58), 5, {58: [item(ss1)]}, marked.append,
                                     add=lambda *a: self.fail("added"))
        self.assertEqual((lines, marked), ([], [5]))

    def test_no_room_said(self):
        ss1 = ravgear.picture_object("short sword +1")
        with mock.patch.object(shopstock, "held_pictures", return_value=set()):
            lines = shopstock.top_up(FakeGD(58), 5, {58: [item(ss1)]}, lambda c: None, add=lambda *a: False)
        self.assertEqual(lines, ["Notaku stocks 0 of the mod's new items (1 with no room)"])

    def test_sellers_are_ravgears_shops(self):
        for obj in shopstock.SELLERS:
            self.assertIn(obj, ravgear.WHERE)

    def test_mark_is_past_every_sellers_name(self):
        self.assertEqual(shopstock.CREATURE_MARK, ravager.CREATURE_SIZE - 1)


@unittest.skipUnless(WOTR and SL, "needs DSUN_WOTR and DSUN_SL")
class FilesTests(unittest.TestCase):
    def test_sellers_stock(self):
        with open(os.path.join(WOTR, ravager.OBJECTS_FILE), "rb") as f:
            objects = gff.read_gff(f.read())
        objects.update(ravgear.from_files(objects, SL, WOTR))
        stock = shopstock.seller_items(objects)
        for obj in shopstock.SELLERS:
            want = sorted(ravgear.picture_object(k) for k in ravgear.WHERE[obj])
            self.assertEqual(sorted(-struct.unpack_from("<h", r, 0)[0] for r in stock[obj]), want, obj)
            recs, _ = dataitems.records(objects[("RDFF", obj)])
            name = recs[0].data[0x21:0x31]
            self.assertEqual(name[-1], 0, obj)  # (the mark's byte free)


if __name__ == "__main__":
    unittest.main()
