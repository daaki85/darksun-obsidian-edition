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

    def test_mod_bytes_kept(self):
        """SL +42h-+45h whole at +3Ch-+3Fh both ways: the kit's and the new spells' bytes stay above the
        sound words (the Loader's copy of the game reads only their low bytes: ravager's sound_3c, sound_3e)."""
        self.assertEqual(rt.MOD_SHEET_BYTES, (0x3D, 0x3F))
        self.assertEqual(dataitems.records(self.out[("CHAR", 35)])[0][1].data[0x3C:0x40], bytes((0x42, 0x43, 0x44, 0x45)))
        out, _ = rt.roster(made_save(), scroll_sequel())
        self.assertEqual(dataitems.records(out[("CHAR", 35)])[0][1].data[0x3C:0x40], bytes((0x42, 0x43, 0x44, 0x45)))

    def test_specs_on_the_loader_sheet(self):
        """The Loader's way: a 48h sheet (ravager.SHEET_SIZE), SL's weapon specs and starting roll packed
        at +42h..+44h (the age at +41h), +45h..+47h 0; nothing there for a sheet with neither; SPST
        CHARTRAN's 9 bytes both ways; CHARTRAN's way the game's 42h sheet."""
        from dsloader import game, ravager
        save = made_save()
        sheets = bytearray(save[("SAVE", rt.SHEETS)])
        sheets[game.SPEC_SLOTS:game.SPEC_SLOTS + 4] = game.packed_specs([3, 0, 5], age=5, roll=9)
        sheets[rt.SL_SHEET + game.SPEC_SLOTS:rt.SL_SHEET + game.SPEC_SLOTS + 4] = bytes(4)
        save[("SAVE", rt.SHEETS)] = bytes(sheets)
        out, _ = rt.roster(save, scroll_sequel())
        lex, jenna = (dataitems.records(out[("CHAR", n)])[0][1].data for n in (35, 34))
        self.assertEqual((len(lex), len(jenna)), (ravager.SHEET_SIZE, ravager.SHEET_SIZE))
        # (V3: the first spec, then the others ascending)
        self.assertEqual(game.specs_of(lex[0x42:0x45] + b"\0"), (bytes((3, 5, 0, 0)), 9))
        self.assertEqual((lex[0x41], lex[0x45:]), (5, bytes(3)))
        self.assertEqual(jenna[0x42:], bytes(6))
        self.assertEqual(lex[4:0x42], rt.sheet(sheets[:rt.SL_SHEET])[4:0x41] + lex[0x41:0x42])
        self.assertEqual(struct.unpack_from("<I", lex, 0)[0], game.XP_CAP // 3)  # (its XP held: sl_xp_share)
        self.assertEqual(out[("SPST", 35)], bytes([1, 0, 0, 0, 4, 0, 0, 0, 0]))
        chartran, _ = rt.roster(save, made_sequel())
        self.assertEqual(len(dataitems.records(chartran[("CHAR", 35)])[0][1].data), 0x42)
        self.assertEqual(chartran[("SPST", 35)], bytes([1, 0, 0, 0, 4, 0, 0, 0, 0]))
        # (whatever layout is on: the transfer reads SL's sheet as SL's)
        from dsloader import ravlog
        ravlog.apply_layout()
        try:
            again = dataitems.records(rt.roster(save, scroll_sequel())[0][("CHAR", 35)])[0][1].data
        finally:
            ravlog.restore_layout()
        self.assertEqual(again, lex)
        # (an old unpacked SL sheet: its specs a byte each, packed here, no roll)
        sheets[game.SPEC_SLOTS:game.SPEC_SLOTS + 4] = bytes((2, 1, 0, 0))
        save[("SAVE", rt.SHEETS)] = bytes(sheets)
        old = dataitems.records(rt.roster(save, scroll_sequel())[0][("CHAR", 35)])[0][1].data
        self.assertEqual((game.specs_of(old[0x42:0x45] + b"\0"), old[0x41]), ((bytes((2, 1, 0, 0)), None), 0))

    def test_xp_held_at_sl_cap(self):
        """The Loader's way, XP past Shattered Lands' cap stays behind (the owner's, 2026-11-25): a fighter's
        2,000,000 arrives as 749,999, a fighter/thief's as 374,999, a human's as the cap less its old
        class's level's XP, XP below the share as it is; CHARTRAN's way, as it is; the report says so."""
        def sl_sheet(xp, race, classes, levels):
            rec = bytearray(rt.SL_SHEET)
            struct.pack_into("<I", rec, 0, xp)
            rec[rt.SL_SHEET_RACE] = race
            rec[rt.SL_SHEET_CLASSES:rt.SL_SHEET_CLASSES + 3] = bytes(classes)
            rec[rt.SL_SHEET_LEVELS:rt.SL_SHEET_LEVELS + 3] = bytes(levels)
            return bytes(rec)
        from dsloader import tables
        cases = ((sl_sheet(2000000, 3, (9, 0, 0), (10, 0, 0)), 749999),
                 (sl_sheet(2000000, 3, (9, 17, 0), (9, 11, 0)), 374999),
                 (sl_sheet(2000000, 3, (9, 11, 17), (8, 9, 11)), 249999),
                 (sl_sheet(2000000, 1, (11, 2, 0), (10, 7, 0)), 749999 - tables.XP["cleric"][6]),
                 (sl_sheet(100000, 3, (9, 0, 0), (7, 0, 0)), 100000))
        for rec, want in cases:
            self.assertEqual(struct.unpack_from("<I", rt.sheet(rec, loader=True), 0)[0], want)
            self.assertEqual(struct.unpack_from("<I", rt.sheet(rec), 0)[0], struct.unpack_from("<I", rec, 0)[0])
        moved = [rt.Moved(0, "Lex", [], 35, "", {}, (2000000, 749999))]
        self.assertIn("Lex: place 4 of the roster (CREATE CHARACTERS, ADD); XP 749,999 (Shattered Lands' cap: "
                      "2,000,000 in the save)", rt.player_report(moved, None, [], {}.get))

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


class AgeTests(unittest.TestCase):
    def wotr(self, race, age_byte, scores=(16, 15, 14, 13, 12, 11)):
        cre, sh = bytearray(rt.CREATURE), bytearray(rt.SHEET)
        sh[rt.WOTR_SHEET_RACE], sh[rt.WOTR_SHEET_AGE] = race, age_byte
        sh[rt.WOTR_SHEET_ABILITIES:rt.WOTR_SHEET_ABILITIES + 6] = bytes(scores)
        cre[rt.CREATURE_SCORES:rt.CREATURE_SCORES + 6] = bytes(scores)
        return bytes(cre), bytes(sh)

    def test_middle_age_reached(self):
        cre, sh = self.wotr(1, 39 - 15 + 1)  # (a human of 39)
        cre2, sh2, line = rt.aged(cre, sh, "Lex", 1)
        self.assertEqual(sh2[rt.WOTR_SHEET_AGE], 40 - 15 + 1)
        want = bytes((15, 15, 13, 14, 13, 11))  # (STR -1, CON -1, INT +1, WIS +1)
        self.assertEqual(sh2[rt.WOTR_SHEET_ABILITIES:rt.WOTR_SHEET_ABILITIES + 6], want)
        self.assertEqual(cre2[rt.CREATURE_SCORES:rt.CREATURE_SCORES + 6], want)
        self.assertEqual(line, "a year older: 40, middle-aged: STR -1, CON -1, INT +1, WIS +1")

    def test_plain_year_and_none(self):
        cre, sh = self.wotr(1, 5)
        self.assertEqual(rt.aged(cre, sh, "Lex", 1)[2], "a year older: 20")
        self.assertEqual(rt.aged(cre, sh, "Lex", 0), (cre, sh, "still 19"))
        self.assertEqual(rt.aged(*self.wotr(1, 0), "Lex", 1)[2], "no age yet")

    def test_most_age_not_reached(self):
        from dsloader import aging
        most = aging.most_age("Lex", 7)
        cre, sh = self.wotr(7, most - 1 - 15 + 1)  # (a mul a year short of the most)
        cre2, sh2, line = rt.aged(cre, sh, "Lex", 1)
        self.assertEqual((cre2, sh2), (cre, sh))
        self.assertIn("the most a mul lives", line)

    def test_gap(self):
        import random
        rng = random.Random(5)
        self.assertTrue(all(3 <= rt.roll_gap(rng) <= 12 for _ in range(50)))
        self.assertEqual(set(rt.gap_years(range(4), 12, rng).values()), {1})
        counts = sum(sum(rt.gap_years(range(4), 3, rng).values()) for _ in range(1000))
        self.assertAlmostEqual(counts / 4000, 0.25, delta=0.03)

    def test_carried_the_loaders_way(self):
        save = made_save()
        sheets = bytearray(save[("SAVE", rt.SHEETS)])
        sheets[0x16] |= 0x80  # (Lex's sheet packed: +17h its age)
        sheets[0x17], sheets[0x18] = 9, 1  # (a human of 23)
        save[("SAVE", rt.SHEETS)] = bytes(sheets)
        out, moved = rt.roster(save, scroll_sequel(), years={0: 1})
        sheet = dataitems.records(out[("CHAR", 35)])[0][1].data
        self.assertEqual((sheet[rt.WOTR_SHEET_AGE], moved[0].age), (10, "a year older: 24"))
        out, _ = rt.roster(save, made_sequel())
        self.assertEqual(dataitems.records(out[("CHAR", 35)])[0][1].data[rt.WOTR_SHEET_AGE], 0)  # (CHARTRAN's)


class PlayerReportTests(unittest.TestCase):
    def test_report(self):
        moved = [rt.Moved(0, "Lex", [(1010, 704), (2419, 22419), (1123, rt.LEFT), (2431, 900), (1010, 704)], 35,
                          "a year older: 24", {1010: 1, 2419: 2, 1123: 3, 2431: 4})]
        names = {1: "Long Sword", 2: "Short Sword", 3: "Shillelagh", 4: "Ring"}
        text = rt.player_report(moved, 7, [(2431, "no picture")], names.get)
        self.assertIn("7 months have passed", text)
        self.assertIn("Lex: place 4 of the roster (CREATE CHARACTERS, ADD); a year older: 24", text)
        self.assertIn("  the sequel's own: Long Sword (2)", text)
        self.assertIn("  made for the sequel by the Loader: Short Sword", text)
        self.assertIn("  left behind (a spell made it, and the spell is over): Shillelagh", text)
        self.assertIn("  a money bag (no picture): Ring", text)


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
            moved, failed = rt.take_party(save, d)
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


class ItemSpellTests(unittest.TestCase):
    """An item's spell, the Loader's way (ravtransfer.spell_map, item_spell): the mod's items keep it."""

    def test_spell_map(self):
        sl = {("SPIN", 117): b"FOCUS HEAT:  Inflicts 2 to 12 pts\r\n", ("SPIN", 73): b"CAUSE LIGHT WOUNDS: x",
              ("SPIN", 14): b"DETECT INVISIBILITY: x", ("SPIN", 200): b"NOTHING THERE: x", ("TEXT", 1): b"X: y"}
        names = [""] * 200
        names[174], names[118], names[13] = "Focus Heat", "Cause Light Wounds", "Detect Invisible"
        self.assertEqual(rt.spell_map(sl, names), {116: 174, 72: 118, 13: 13})

    def test_own_objects(self):
        sequel = made_sequel()
        objects = dict(sequel.objects)
        objects[("RDFF", 21500)] = wotr_record(21500, 106, 0, 30)  # (a Loader's object: the Searing Blade's)
        sequel = sequel._replace(counterparts={1010: 704, 1500: 21500}, objects=objects,
                                 scrolls={}, spells={116: 174, 3: 3})
        blade = bytearray(sl_item(1500))
        blade[rt.SL_ITEM_SPELL] = 117
        rec, new = rt.item(bytes(blade), sequel)
        self.assertEqual((new, struct.unpack_from("<H", rec, rt.ITEM_POWER)[0],
                          struct.unpack_from("<H", rec, rt.ITEM_SPELL_SHOWN)[0]), (21500, 175, 175))
        arrows = bytearray(sl_item(1500))
        struct.pack_into("<H", arrows, 0x12, 0x16D)  # (Chill Arrows, by name)
        self.assertEqual(struct.unpack_from("<H", rt.item(bytes(arrows), sequel)[0], rt.ITEM_POWER)[0], 4)
        blade[rt.SL_ITEM_SPELL] = 50  # (a spell the sequel lacks: none)
        self.assertEqual(struct.unpack_from("<H", rt.item(bytes(blade), sequel)[0], rt.ITEM_POWER)[0], 0)
        # the sequel's own object keeps its spell; CHARTRAN's way (no spells) changes nothing
        sword = bytearray(sl_item(1010))
        sword[rt.SL_ITEM_SPELL] = 117
        self.assertEqual(rt.item(bytes(sword), sequel)[0][rt.ITEM_POWER], 0)
        self.assertEqual(rt.item(bytes(blade), sequel._replace(spells=None))[0][rt.ITEM_POWER], 0)

    def test_tome(self):
        """The Tome of Understanding: the Loader's object of it with the power DSCLOG2's TOME knows (spell
        WOTR_TOME_SPELL + 1), on the item and shown; made a wizard scroll with a sequel scroll's OJFF."""
        from dsloader import ravitems, tome
        sequel = made_sequel()
        objects = dict(sequel.objects)
        own = ravitems.own_object(tome.TOME_OBJECT)
        objects[("RDFF", own)] = wotr_record(own, rt.WIZARD_SCROLL, 0, 30)
        sequel = sequel._replace(objects=objects, scrolls={}, spells={})
        rec, new = rt.item(tome.item(), sequel)
        self.assertEqual((new, struct.unpack_from("<H", rec, rt.ITEM_POWER)[0],
                          struct.unpack_from("<H", rec, rt.ITEM_SPELL_SHOWN)[0]), (21446, 318, 318))
        self.assertEqual(own, 21446)  # (DSCLOG2's TM_OBJECT)
        self.assertIn("TM_POWER    equ 317 + 1", open(os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), "dos", "dsclog2.asm")).read())

    @unittest.skipUnless(WOTR and os.environ.get("DSUN_SL"), "needs DSUN_WOTR and DSUN_SL (the games' folders)")
    def test_real_names(self):
        from dsloader import ravlog
        with open(os.path.join(os.environ["DSUN_SL"], "RESOURCE.GFF"), "rb") as f:
            sl = gff.read_gff(f.read())
        with open(os.path.join(WOTR, "RESOURCE.GFF"), "rb") as f:
            names = ravlog.spell_table(f.read())[1]
        spells = rt.spell_map(sl, names)
        # the mod's items' spells: Focus Heat, Cause Light Wounds, Detect Invisibility, Resist Fire,
        # Cloak of Bravery, Protection from Normal Missiles, Protection from Evil; the arrows' touches
        self.assertEqual([spells.get(s) for s in (116, 72, 13, 87, 109, 36, 76, 3, 10, 39)],
                         [174, 118, 13, 138, 167, 35, 122, 3, 10, 38])
