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


def wotr_record(obj, kind, power, name, uses=0):
    rec = bytearray(rt.ITEM)
    struct.pack_into("<hHHHHH", rec, 0, -obj, 0, rt.NONE, 0, rt.NONE, kind)
    rec[0x0E], rec[0x10], rec[0x12], rec[0x13], rec[0x14] = uses, power, 6, 0xFF, name
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
        creatures[at + 0x22:at + 0x28] = bytes([18, 17, 16, 15, 14, 13])  # (not these: the sheet's)
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
        self.assertEqual((len(cre), cre[0x21:0x24], cre[0x19:0x1F], cre[0x17]), (0x31, b"Lex", bytes(range(0x1B, 0x21)), 7))
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

    def test_bags_last_first(self):
        save = made_save()
        items = bytearray(save[("SAVE", rt.ITEMS)] + rt.SL_ITEM * b"\0")
        items[1 * rt.SL_ITEM:2 * rt.SL_ITEM] = sl_item(2419, nxt=2, contents=12)  # two bags, the first holding item 4
        items[4 * rt.SL_ITEM:5 * rt.SL_ITEM] = sl_item(2431)
        lists = bytearray(save[("SAVE", rt.LISTS)] + bytes(3))
        struct.pack_into("<BH", lists, 36, 1, 4)
        save[("SAVE", rt.ITEMS)], save[("SAVE", rt.LISTS)] = bytes(items), bytes(lists)
        out, _ = rt.roster(save, made_sequel())
        recs, _ = dataitems.records(out[("CHAR", 35)])
        self.assertEqual([(r.level, r.of, r.number, r.flags) for r in recs[2:]],
                         [(2, 0, 1, 16), (4, 2, 2, 2), (2, 3, 3, 4), (2, 2, 4, 4)])

    def test_counterpart_without_record(self):
        sequel = made_sequel()
        sequel.counterparts[1010] = 2228  # (as ITEMS.BIN pairs 1572: a picture, no record)
        _, moved = rt.roster(made_save(), sequel)
        self.assertEqual(moved[0].items[0], (1010, rt.MONEY_BAG))

    def test_broken_list(self):
        save = made_save()
        items = bytearray(save[("SAVE", rt.ITEMS)])
        items[2 * rt.SL_ITEM + rt.ITEM_NEXT:2 * rt.SL_ITEM + rt.ITEM_NEXT + 2] = struct.pack("<H", 1)
        save[("SAVE", rt.ITEMS)] = bytes(items)
        with self.assertRaises(gff.GffError):
            rt.roster(save, made_sequel())


def sl_scroll(obj, kind, word):
    rec = bytearray(sl_item(obj))
    struct.pack_into("<H", rec, rt.SL_TYPE, kind)
    struct.pack_into("<H", rec, rt.SCROLL_SPELL, word)
    return bytes(rec)


def scroll_sequel():
    """The sequel with a One-use Scroll of spell 1 (31300, SL 1400's pair), a Spellbook of spell 1
    (31002), a Rod (31201) and a priest's scroll of 242 (31407)."""
    objects = dict(made_sequel().objects)
    objects[("RDFF", 31300)] = wotr_record(31300, rt.WIZARD_SCROLL, 1, 3, uses=1)
    objects[("RDFF", 31002)] = wotr_record(31002, rt.WIZARD_SCROLL, 1, 4)
    objects[("RDFF", 31201)] = wotr_record(31201, rt.WIZARD_SCROLL, 5, 167)
    objects[("RDFF", 31407)] = wotr_record(31407, rt.PRIEST_SCROLL, 242, 73)
    objects[("RDFF", 21440)] = wotr_record(21440, 9, 0, 8)
    sequel = rt.Sequel({1010: 704, 1400: 31300}, objects)
    return sequel._replace(scrolls=rt.scroll_objects(sequel))


class ScrollTests(unittest.TestCase):
    def test_spells(self):
        self.assertEqual(rt.scroll_spell(sl_scroll(1400, rt.SL_WIZARD_SCROLL, 1)), (rt.WIZARD_SCROLL, 1))
        self.assertEqual(rt.scroll_spell(sl_scroll(1400, rt.SL_WIZARD_SCROLL, 46)), (rt.WIZARD_SCROLL, 44))
        self.assertIsNone(rt.scroll_spell(sl_scroll(1400, rt.SL_WIZARD_SCROLL, 35)))  # (34, dropped)
        self.assertIsNone(rt.scroll_spell(sl_scroll(1440, rt.SL_WIZARD_SCROLL, 197)))  # (Cat's Grace)
        self.assertEqual(rt.scroll_spell(sl_scroll(1419, rt.SL_PRIEST_SCROLL, 145)), (rt.PRIEST_SCROLL, 242))
        self.assertIsNone(rt.scroll_spell(sl_item(1010)))

    def test_objects(self):
        objs = scroll_sequel().scrolls
        self.assertEqual(objs[(rt.WIZARD_SCROLL, 1)], 31300)  # (ITEMS.BIN's pair before the lower one)
        self.assertEqual(objs[(rt.WIZARD_SCROLL, 0)], 31300)  # (a One-use Scroll)
        self.assertNotIn((rt.WIZARD_SCROLL, 5), objs)  # (a rod)
        self.assertEqual(objs[(rt.PRIEST_SCROLL, 242)], 31407)

    def test_items(self):
        sequel = scroll_sequel()
        rec, new = rt.item(sl_scroll(1440, rt.SL_WIZARD_SCROLL, 10), sequel)  # (Kalzith's Shield)
        self.assertEqual((new, struct.unpack_from("<HH", rec, 2)[0], struct.unpack_from("<H", rec, 0x10)[0],
                          rec[rt.SCROLL_USES]), (31300, 10, 10, 1))
        rec, new = rt.item(sl_scroll(1400, rt.SL_PRIEST_SCROLL, 145), sequel)
        self.assertEqual((new, struct.unpack_from("<H", rec, 0x10)[0]), (31407, 242))
        self.assertEqual(rt.item(sl_scroll(1440, rt.SL_WIZARD_SCROLL, 197), sequel)[1], 21440)  # (a keepsake)
        self.assertEqual(rt.item(sl_scroll(1400, rt.SL_WIZARD_SCROLL, 35), sequel)[1], rt.MONEY_BAG)  # (none made)
        # CHARTRAN's way (no scrolls): the pair, the spell word copied, the power the object's
        rec, new = rt.item(sl_scroll(1400, rt.SL_WIZARD_SCROLL, 10), sequel._replace(scrolls=None))
        self.assertEqual((new, struct.unpack_from("<H", rec, 2)[0], rec[0x10]), (31300, 10, 1))

    def test_lacking(self):
        save = made_save()
        items = bytearray(save[("SAVE", rt.ITEMS)])
        items[3 * rt.SL_ITEM:4 * rt.SL_ITEM] = sl_scroll(1440, rt.SL_WIZARD_SCROLL, 197)
        items[2 * rt.SL_ITEM:3 * rt.SL_ITEM] = sl_scroll(1441, rt.SL_WIZARD_SCROLL, 2)[:rt.ITEM_CONTENTS] + \
            struct.pack("<H", 11) + sl_scroll(1441, rt.SL_WIZARD_SCROLL, 2)[rt.ITEM_CONTENTS + 2:]
        save[("SAVE", rt.ITEMS)] = bytes(items)
        sequel = scroll_sequel()
        self.assertEqual(sorted(rt.lacking(save, sequel)), [1440])
        self.assertEqual(sorted(rt.lacking(save, sequel._replace(scrolls=None))), [1440, 1441])


class SpellMadeTests(unittest.TestCase):
    def setUp(self):
        save = made_save()
        items = bytearray(save[("SAVE", rt.ITEMS)]) + bytearray(rt.SL_ITEM)
        items[1 * rt.SL_ITEM:2 * rt.SL_ITEM] = sl_item(1010, nxt=4, slot=0, plus=1)
        hammer = bytearray(sl_item(1123, nxt=2))
        struct.pack_into("<H", hammer, rt.SL_TYPE, 30)
        items[4 * rt.SL_ITEM:5 * rt.SL_ITEM] = hammer
        save[("SAVE", rt.ITEMS)] = bytes(items)
        self.save = save

    def test_left_behind(self):
        _, moved = rt.roster(self.save, scroll_sequel())
        self.assertEqual(moved[0].items, [(1010, 704), (1123, rt.LEFT), (2419, 900), (2431, 900)])
        self.assertIn("left behind", rt.report(moved))

    def test_list_closes_over_it(self):
        out, _ = rt.roster(self.save, scroll_sequel())
        recs, _ = dataitems.records(out[("CHAR", 35)])
        self.assertEqual([(r.level, r.of, r.number) for r in recs[2:]], [(2, 0, 1), (4, 2, 2), (2, 3, 3)])
        self.assertEqual(struct.unpack_from("<H", recs[2].data, rt.ITEM_NEXT)[0], 2)

    def test_chartran_keeps_it(self):
        _, moved = rt.roster(self.save, made_sequel())
        self.assertEqual(moved[0].items[1], (1123, rt.MONEY_BAG))


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
            self.assertIn("Lex (roster place 4): 3 items, 2 of them a money bag", rt.report(moved))


def listed(place, name, act=b"\x18\x80"):
    """A roster's chunks for a character NAME listed at PLACE (ACT its CACT: 0 not listed)."""
    cre = bytearray(rt.CREATURE)
    cre[rt.CREATURE_NAME:rt.CREATURE_NAME + len(name)] = name
    chunk = dataitems.chunk([dataitems.Record(1, 1, 2, 0, 0, bytes(cre))], dataitems.HEADER.pack(dataitems.END, 1, 2, 0, 0, 0))
    return {("CHAR", place): chunk, ("CACT", place): act}


class PlacesTests(unittest.TestCase):
    def test_install(self):
        """The install's roster: 32-35 not listed (CACT 0), 36-39 its four: the party takes 32-35."""
        chunks = {}
        for p in range(32, 36):
            chunks.update(listed(p, b"Frin'kal", b"\0\0"))
        for p, n in zip(range(36, 40), (b"Clk'whrr", b"Meggyn", b"Zontorra", b"Borzak")):
            chunks.update(listed(p, n))
        self.assertEqual(rt.places(made_save(), chunks), {0: 33, 1: 32})
        self.assertIsNone(rt.roster_name(chunks, 32))
        self.assertEqual(rt.roster_name(chunks, 37), b"Meggyn")

    def test_own_place_again_then_free(self):
        chunks = {}
        for p, n in zip(range(32, 40), (b"A", b"Jenna", b"B", b"C", b"D", b"E", b"F", b"G")):
            chunks.update(listed(p, n))
        del chunks[("CACT", 36)]  # (a free place)
        self.assertEqual(rt.places(made_save(), chunks), {1: 33, 0: 36})

    def test_full(self):
        chunks = {}
        for p in range(32, 40):
            chunks.update(listed(p, b"X%d" % p))
        with self.assertRaisesRegex(gff.GffError, "needs 2 more places"):
            rt.places(made_save(), chunks)

    def test_roster_at_places(self):
        out, moved = rt.roster(made_save(), made_sequel(), {0: 38, 1: 32})
        self.assertEqual(sorted(k for k in out if k[0] == "CHAR"), [("CHAR", 32), ("CHAR", 38)])
        self.assertEqual([m.place for m in moved], [38, 32])


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
