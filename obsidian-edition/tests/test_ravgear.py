"""The magic weapons the sequel lacks and the mod's plain items, put in its shops, people and containers
(dsloader/ravgear.py).

Made-up records here; with DSUN_WOTR (the player's Wake of the Ravager folder) and DSUN_SL (Shattered
Lands'), the whole set is built from their files."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dsloader import dataitems, gff, ravager, ravgear, ravitems  # noqa: E402

WOTR, SL = os.environ.get("DSUN_WOTR"), os.environ.get("DSUN_SL")
END = dataitems.HEADER.pack(dataitems.END, 0, 0, 0, 0, 0)


def item(obj):
    data = bytearray(0x17)
    struct.pack_into("<h", data, 0, -obj)
    return bytes(data)


def person(lists):
    """A person's RDFF: kind 2 (the creature), then each list (flags, its items' objects)."""
    recs = [dataitems.Record(1, 0, 2, 1, 0, bytes(10))]
    for flags, objs in lists:
        first = len(recs)
        recs.append(dataitems.Record(dataitems.FIRST, 0, dataitems.ITEM, 0, flags, item(objs[0])))
        for o in objs[1:]:
            recs.append(dataitems.Record(dataitems.NEXT, first, dataitems.ITEM, 0, ravgear.NEXT_FLAGS, item(o)))
            first = len(recs) - 1
    return dataitems.chunk(recs, END)


def pack_chain(rdff):
    """The objects of the pack's items, in their chain's order."""
    recs, _ = dataitems.records(rdff)
    head = next(i for i, r in enumerate(recs) if r.kind == dataitems.ITEM and r.level == dataitems.FIRST
                and r.flags == ravgear.PACK)
    out, at = [], head
    while at is not None:
        out.append(-struct.unpack_from("<h", recs[at].data, 0)[0])
        at = next((i for i, r in enumerate(recs) if r.kind == dataitems.ITEM and r.level == dataitems.NEXT
                   and r.of == at), None)
    return out


class TableTests(unittest.TestCase):
    def test_counts(self):
        magic = [k for k, g in ravgear.GEAR.items() if g.plus]
        self.assertEqual(len(magic), 14)
        self.assertEqual(len(ravgear.GEAR) - len(magic), 15)

    def test_where_names_gear(self):
        for obj, keys in ravgear.WHERE.items():
            for k in keys:
                self.assertIn(k, ravgear.GEAR, obj)

    def test_every_item_placed(self):
        used = {k for keys in ravgear.WHERE.values() for k in keys}
        self.assertEqual(used, set(ravgear.GEAR))

    def test_short_sword_plus_one_at_notaku(self):
        self.assertEqual(ravgear.WHERE[58], ("short sword +1",))

    def test_drawn_pictures_clear_of_the_transfer(self):
        # the transfer's numbers: 20000 + SL's below 10000, 14000 + SL's 30000 on (SL's highest is 32003);
        # 13000-13999 drew another picture in the game (2026-11-25)
        objs = [ravgear.picture_object(k) for k in ravgear.drawn()]
        self.assertTrue(objs)
        for o in objs:
            self.assertTrue(16004 <= o < 20000, o)
        self.assertEqual(len(set(objs)), len(objs))

    def test_plain_pictures_are_the_transfer_numbers(self):
        for key, g in ravgear.GEAR.items():
            if g.picture.make is None:
                self.assertEqual(ravgear.picture_object(key), ravitems.own_object(g.picture.sl), key)

    def test_magic_values(self):
        for key, g in ravgear.GEAR.items():
            if g.plus and "sling" not in key and "cahulaks +1" != key:
                self.assertEqual(g.value, ravgear.MELEE_PLUS * g.plus, key)


class RecordTests(unittest.TestCase):
    def test_pack_appended(self):
        rdff = person([(17, [600]), (4, [601, 602])])
        out = ravgear.with_pack_items(rdff, [item(700), item(701)])
        self.assertEqual(pack_chain(out), [601, 602, 700, 701])

    def test_new_pack(self):
        rdff = person([(17, [600])])
        out = ravgear.with_pack_items(rdff, [item(700)])
        self.assertEqual(pack_chain(out), [700])

    def test_item_record(self):
        like = ravgear.GEAR["short sword +1"].like
        template = bytearray(0x17)
        template[0x12] = 5
        objects = {("RDFF", like): dataitems.chunk([dataitems.Record(1, 0, 1, 1, 0, bytes(template))], END)}
        rec = ravgear.item_record("short sword +1", objects, b"")
        g = ravgear.GEAR["short sword +1"]
        self.assertEqual(struct.unpack_from("<h", rec, 0)[0], -ravgear.picture_object("short sword +1"))
        self.assertEqual(struct.unpack_from("<H", rec, ravgear.ITEM_VALUE)[0], g.value)
        self.assertEqual(struct.unpack_from("<H", rec, ravitems.ITEM_TYPE)[0], g.type)
        self.assertEqual(struct.unpack_from("<H", rec, ravitems.ITEM_NAME)[0],
                         ravager.mod_name(ravgear.SHORT_SWORD_NAME))
        self.assertEqual(rec[ravgear.ITEM_PLUS], 1)
        self.assertEqual(rec[0x12], 5)  # (the template's)


class StableColourTests(unittest.TestCase):
    def test_screen_own_left_out(self):
        base = bytes(range(256)) * 3
        resources = {("PAL ", 1000): base}
        numbers = [c for c, _ in ravitems.stable_colours(resources, [base])]
        self.assertEqual(numbers[0], 16)
        self.assertNotIn(2, numbers)


@unittest.skipUnless(WOTR and SL, "needs DSUN_WOTR and DSUN_SL")
class FilesTests(unittest.TestCase):
    def test_built(self):
        with open(os.path.join(WOTR, ravager.OBJECTS_FILE), "rb") as f:
            objects = gff.read_gff(f.read())
        out = ravgear.from_files(objects, SL, WOTR)
        for key in ravgear.GEAR:
            obj = ravgear.picture_object(key)
            for kind in ("OJFF", "BMP ", "RDFF"):
                self.assertIn((kind, obj), out, key)
        for obj, keys in ravgear.WHERE.items():
            chain = pack_chain(out[("RDFF", obj)])
            self.assertEqual(chain[-len(keys):], [ravgear.picture_object(k) for k in keys], obj)


if __name__ == "__main__":
    unittest.main()
