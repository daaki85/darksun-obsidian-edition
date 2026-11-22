"""The party's way into Wake of the Ravager (dsloader/ravtransfer.py): SSI's CHARTRAN in Python.

The records are made up here (no game file needed); with DSUN_WOTR naming the player's Wake of the
Ravager folder, the playtest kit's saves go through the real ITEMS.BIN and OBJEX.GFF too. On those
saves the module's chunks were found equal to CHARTRAN's byte for byte (2026-11-22,
playtest/logs/2026-11-22-ravager-transfer-format.md)."""

import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dsloader import dataitems, gff, ravtransfer as rt  # noqa: E402

WOTR = os.environ.get("DSUN_WOTR")
SAVES = os.path.join(os.path.dirname(__file__), "..", "..", "playtest", "saves")


def sl_item(obj, nxt=rt.NONE, contents=rt.NONE, slot=4, plus=0):
    rec = bytearray(rt.SL_ITEM)
    struct.pack_into("<hHHHH", rec, 0, -obj, 0, nxt, 0, contents)
    rec[0x0A:0x0C] = struct.pack("<H", 60)
    rec[0x0C:0x0E] = b"\x83\x09"  # (dropped)
    rec[0x10], rec[0x11], rec[0x12], rec[0x14] = 6, slot, 0x46, plus
    return bytes(rec)


def wotr_record(obj, kind, power, name):
    rec = bytearray(rt.ITEM)
    struct.pack_into("<hHHHHH", rec, 0, -obj, 0, rt.NONE, 0, rt.NONE, kind)
    rec[0x10], rec[0x12], rec[0x13], rec[0x14] = power, 6, 0xFF, name
    head = dataitems.Record(1, 0, 1, 1, 0, bytes(rec))
    return dataitems.chunk([head], dataitems.HEADER.pack(dataitems.END, 0, 0, 0, 0, 0))


def made_save(names=("Lex", "Jenna")):
    """Two members: Lex with a sword (counterpart 704) worn and a bag holding a ring (no counterpart);
    Jenna with nothing. Lex knows wizard spells 0, 35 and 34 (dropped) and a priest's 70; power 3."""
    creatures, sheets = bytearray(rt.SL_CREATURE * 4), bytearray(rt.SL_SHEET * 4)
    for m, name in enumerate(names):
        at = m * rt.SL_CREATURE
        struct.pack_into("<HHHH", creatures, at, 0x17 + m, 0x15, m, 0x8001 + m)
        struct.pack_into("<HHH", creatures, at + 8, 10 if m == 0 else rt.NONE, rt.NONE, rt.NONE)
        creatures[at + rt.SL_NAME:at + rt.SL_NAME + len(name)] = name.encode()
        creatures[at + 0x22:at + 0x28] = bytes([18, 17, 16, 15, 14, 13])
        sheets[m * rt.SL_SHEET:(m + 1) * rt.SL_SHEET] = bytes(range(m, m + rt.SL_SHEET))
    items = bytearray(rt.SL_ITEM * 4)
    items[1 * rt.SL_ITEM:2 * rt.SL_ITEM] = sl_item(1010, nxt=2, slot=0, plus=1)
    items[2 * rt.SL_ITEM:3 * rt.SL_ITEM] = sl_item(2419, contents=11)
    items[3 * rt.SL_ITEM:4 * rt.SL_ITEM] = sl_item(2431)
    lists = bytearray(3 * 12)
    struct.pack_into("<BH", lists, 30, 1, 1)
    struct.pack_into("<BH", lists, 33, 1, 3)
    spells = bytearray(rt.SL_SPELLS * 4)
    for s in (0, 34, 35, 70):
        spells[s] = 1
    powers = bytearray(rt.SL_POWERS * 4)
    powers[3] = 8
    return {("SAVE", rt.CREATURES): bytes(creatures), ("SAVE", rt.SHEETS): bytes(sheets),
            ("SAVE", rt.ITEMS): bytes(items), ("SAVE", rt.LISTS): bytes(lists),
            ("SAVE", rt.SPELLS): bytes(spells), ("SAVE", rt.POWERS): bytes(powers)}


def made_sequel():
    objects = {("RDFF", 704): wotr_record(704, 20, 0, 0x30), ("RDFF", rt.MONEY_BAG): wotr_record(900, 9, 0, 8)}
    return rt.Sequel({1010: 704}, objects)


class TablesTests(unittest.TestCase):
    def test_spells(self):
        self.assertEqual([rt.spell_place(s) for s in (0, 33, 34, 35, 41, 42, 43, 48, 49, 50, 51, 52, 63, 64, 65, 68, 69)],
                         [0, 33, None, 34, 40, None, 41, 46, None, 49, 50, 52, 63, None, 64, 67, None])

    def test_powers(self):
        row = bytes([0, 8, 0x0C, 4] + [0] * 16 + [0x10] + [0] * 13)
        powers, disciplines = rt.powers_known(row)
        self.assertEqual(powers[:4], bytes([0, 2, 2, 0]))  # (4: not a bit CHARTRAN keeps)
        self.assertEqual(powers[20], 4)
        self.assertEqual(disciplines, bytes([1 | 4]))
        self.assertEqual(rt.powers_known(bytes(34))[1], b"\0")

    def test_counterparts_first_wins(self):
        self.assertEqual(rt.counterparts(struct.pack("<HHHH", 5, 6, 5, 7)), {5: 6})


class RosterTests(unittest.TestCase):
    def setUp(self):
        self.out, self.moved = rt.roster(made_save(), made_sequel())

    def test_members_and_numbers(self):
        self.assertEqual([m.name for m in self.moved], ["Lex", "Jenna"])
        self.assertEqual(sorted(k for k in self.out if k[0] == "CHAR"), [("CHAR", 34), ("CHAR", 35)])
        self.assertEqual(self.out[("CACT", 35)], struct.pack("<H", 0x8001))

    def test_records(self):
        recs, end = dataitems.records(self.out[("CHAR", 35)])
        self.assertEqual([(r.level, r.of, r.kind, r.number, r.flags) for r in recs],
                         [(1, 5, 2, 0, 0), (3, 0, 3, 0, 15), (2, 0, 1, 1, 16), (4, 2, 1, 2, 2), (2, 3, 1, 3, 4)])
        self.assertEqual(end, dataitems.HEADER.pack(0xFF, 5, 2, 0, 0, 0))
        cre, sheet = recs[0].data, recs[1].data
        self.assertEqual((len(cre), cre[0x21:0x24], cre[0x19:0x1F], cre[0x17]), (0x31, b"Lex", bytes([18, 17, 16, 15, 14, 13]), 7))
        self.assertEqual((len(sheet), sheet[0x0E], sheet[0x12], sheet[0x37]), (0x42, 0x10, 0x18, 0x3D))

    def test_items(self):
        recs, _ = dataitems.records(self.out[("CHAR", 35)])
        sword, bag, ring = (r.data for r in recs[2:])
        self.assertEqual(struct.unpack_from("<hH", sword, 0x00)[0], -704)
        self.assertEqual((sword[0x0A], sword[0x13], sword[0x16], sword[0x14]), (20, 0, 1, 0x30))
        self.assertEqual(struct.unpack_from("<H", bag, rt.ITEM_CONTENTS)[0], 11)
        self.assertEqual((struct.unpack_from("<h", ring, 0)[0], ring[0x0A], ring[0x0C]), (-900, 9, 0))
        self.assertEqual(self.moved[0].items, [(1010, 704), (2419, 900), (2431, 900)])

    def test_spells_and_powers(self):
        self.assertEqual(self.out[("SPST", 35)], bytes([1, 0, 0, 0, 4, 0, 0, 0, 0]))
        self.assertEqual(self.out[("PSST", 35)][3], 2)
        self.assertEqual(self.out[("PSIN", 35)], b"\x01")

    def test_broken_list(self):
        save = made_save()
        items = bytearray(save[("SAVE", rt.ITEMS)])
        items[2 * rt.SL_ITEM + rt.ITEM_NEXT:2 * rt.SL_ITEM + rt.ITEM_NEXT + 2] = struct.pack("<H", 1)
        save[("SAVE", rt.ITEMS)] = bytes(items)
        with self.assertRaises(gff.GffError):
            rt.roster(save, made_sequel())


class FileTests(unittest.TestCase):
    def test_take_party_keeps_the_rest(self):
        with tempfile.TemporaryDirectory() as d:
            roster = _gff({("CHAR", 40): b"other", ("PREF", 100): b"p", ("CACT", 40): b"a", ("SPST", 40): b"s",
                            ("PSST", 40): b"t", ("PSIN", 40): b"i"})
            sequel = made_sequel()
            with open(os.path.join(d, "CHARSAVE.GFF"), "wb") as f:
                f.write(roster)
            with open(os.path.join(d, "ITEMS.BIN"), "wb") as f:
                f.write(struct.pack("<HH", 1010, 704))
            with open(os.path.join(d, "OBJEX.GFF"), "wb") as f:
                f.write(_gff(sequel.objects))
            save = os.path.join(d, "SAVE01.SAV")
            with open(save, "wb") as f:
                f.write(_gff(made_save()))
            moved = rt.take_party(save, d)
            got = gff.read_gff(open(os.path.join(d, "CHARSAVE.GFF"), "rb").read())
            self.assertEqual((got[("CHAR", 40)], got[("PREF", 100)]), (b"other", b"p"))
            self.assertIn(("CHAR", 35), got)
            self.assertTrue(os.path.exists(os.path.join(d, "CHARSAVE.GFF.BAK")))
            self.assertIn("Lex: 3 items, 2 of them a money bag", rt.report(moved))


def _gff(chunks):
    """A GFF file holding CHUNKS, each type's listed one by one (as a roster's are)."""
    types = {}
    for kind, cid in sorted(chunks):
        types.setdefault(kind, []).append(cid)
    data = bytearray(b"GFFI" + bytes(24))
    places = {}
    for key in sorted(chunks):
        places[key] = (len(data), len(chunks[key]))
        data += chunks[key]
    toc = bytearray(struct.pack("<IIH", 0, 0, len(types)))
    for kind, ids in types.items():
        toc += struct.pack("<4sI", kind.encode("latin1"), len(ids))
        for cid in ids:
            toc += struct.pack("<III", cid, *places[(kind, cid)])
    struct.pack_into("<II", data, 12, len(data), len(toc))
    return bytes(data + toc)


@unittest.skipUnless(WOTR, "DSUN_WOTR: the player's Wake of the Ravager folder")
class SequelTests(unittest.TestCase):
    def test_kit_saves(self):
        sequel = rt.load_sequel(WOTR)
        for name in ("trap-user", "selling-junk-user", "rest-no-call-user"):
            with open(os.path.join(SAVES, name, "SAVE01.SAV"), "rb") as f:
                out, moved = rt.roster(gff.read_gff(f.read()), sequel)
            self.assertEqual(len(moved), 4, name)
            for m in moved:
                recs, _ = dataitems.records(out[("CHAR", 35 - m.member)])
                self.assertEqual(len(recs) - 2, len(m.items), name)


if __name__ == "__main__":
    unittest.main()
