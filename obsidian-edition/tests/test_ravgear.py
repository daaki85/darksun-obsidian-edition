"""The magic weapons the sequel lacks and the mod's plain items, put in its shops, people and containers
(dsloader/ravgear.py).

Made-up records here; with DSUN_WOTR (the player's Wake of the Ravager folder) and DSUN_SL (Shattered
Lands'), the whole set is built from their files."""

import os
import shutil
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import dataitems, game, gff, ravager, ravgear, ravitems, ravspells  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:
    Uc = None

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


class BookTests(unittest.TestCase):
    """The new wizard spells' spellbooks (ravgear.BOOKS)."""

    def objects(self):
        rdff = {like: dataitems.chunk([dataitems.Record(1, 0, dataitems.ITEM, 0, 0, item(like)),
                                       dataitems.Record(3, 0, 4, 77, 5, bytes(15))], END)
                for like in ravgear.BOOK_LIKE.values()}
        out = {("RDFF", like): chunk for like, chunk in rdff.items()}
        out.update({("OJFF", like): bytes([like & 0xFF]) * 16 for like in rdff})
        return out

    def test_one_of_each_spell_in_the_taught_numbers(self):
        self.assertEqual(sorted(b.spell for b in ravgear.BOOKS.values()), sorted(ravspells.SPELLS))
        objects = [b.object for b in ravgear.BOOKS.values()]
        self.assertEqual(len(set(objects)), len(objects))  # (a shop shows items of one object as one)
        for obj in objects:
            self.assertIn(obj, ravgear.SPELLBOOKS)
            self.assertNotIn(obj, range(31300, 31400))  # (a one-use scroll: cast, not learnt)

    def test_prices_a_level(self):
        for key, b in ravgear.BOOKS.items():
            self.assertEqual(b.value, 6000 if b.spell == ravspells.GRACE else 3000, key)

    def test_record_teaches_its_spell(self):
        objects = self.objects()
        for key, b in ravgear.BOOKS.items():
            rec = ravgear.item_record(key, objects, b"")
            self.assertEqual(struct.unpack_from("<h", rec, 0)[0], -b.object)
            self.assertEqual(struct.unpack_from("<H", rec, ravgear.ITEM_POWER)[0], b.spell + 1)
            self.assertEqual(struct.unpack_from("<H", rec, ravgear.ITEM_SPELL)[0], b.spell + 1)
            self.assertEqual(struct.unpack_from("<H", rec, ravgear.ITEM_VALUE)[0], b.value)
            chunks = ravgear.book_chunks(key, objects)
            self.assertEqual(chunks[("OJFF", b.object)], objects[("OJFF", b.like)])  # (the book's picture)
            recs, _ = dataitems.records(chunks[("RDFF", b.object)])
            self.assertEqual(recs[0].data, rec)
            self.assertEqual(ravgear.picture_object(key), b.object)

    def test_notaku_sells_all_six(self):
        self.assertEqual(ravgear.BOOK_WHERE[58], tuple(ravgear.BOOKS))
        self.assertEqual(ravgear.placed()[58], ravgear.WHERE[58] + tuple(ravgear.BOOKS))
        self.assertEqual(ravgear.placed(books=False), ravgear.WHERE)

    def test_switch(self):
        """The books with the new spells' switch only (ravager.write_objects: ravspells.SKIP)."""
        from unittest import mock
        for skip, want in ((frozenset(), True), (frozenset({ravspells.SKIP}), False)):
            asked = []
            with mock.patch.object(ravager, "_write_copy", lambda g, n, d, fixed, s: fixed(b"", s)), \
                    mock.patch.object(ravager, "read_added", lambda d: {}), \
                    mock.patch.object(ravager, "objects_fixed", lambda d, s, added, gear, arrows=None, party=None, funnel=None: (gear({}), [])), \
                    mock.patch.object(ravgear, "from_files", lambda c, sl, g, books=True: asked.append(books) or {}):
                ravager.write_objects("wotr", "dos/OBJEX2.GFF", skip, sl_dir="sl")
            self.assertEqual(asked, [want], skip)


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
        for key, book in ravgear.BOOKS.items():
            for kind in ("OJFF", "RDFF", "BMP "):
                self.assertNotIn((kind, book.object), objects, key)  # (numbers free in the sequel)
            for kind in ("OJFF", "RDFF"):
                self.assertIn((kind, book.object), out, key)
            recs, _ = dataitems.records(out[("RDFF", book.object)])
            self.assertEqual(struct.unpack_from("<H", recs[0].data, ravgear.ITEM_POWER)[0], book.spell + 1)
            like, = struct.unpack_from("<H", objects[("OJFF", book.like)], ravitems.OJFF_ICON)
            self.assertEqual(struct.unpack_from("<H", out[("OJFF", book.object)], ravitems.OJFF_ICON)[0], like)
        for obj, keys in ravgear.placed().items():
            chain = pack_chain(out[("RDFF", obj)])
            self.assertEqual(chain[-len(keys):], [ravgear.picture_object(k) for k in keys], obj)
        bare = ravgear.from_files(objects, SL, WOTR, books=False)
        self.assertFalse([k for k in bare if k[1] in ravgear.SPELLBOOKS])


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class BoneHelmTests(unittest.TestCase):
    """DSCLOG2's PROBE_HELM_AC and PROBE_BOX_AC give the mod's Bone Helm (its type 104, AC 0 in its record)
    AC 1 with RULE_HELMS, whatever its name; another type keeps its record's AC."""

    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos", "dsclog2.asm"))
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]

    def ac(self, probe, kind, rules, type_ac=0):
        tsr, types, ss = 0x1000, 0x6000, 0x4000
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(tsr * 16, self.image)
        mu.mem_write(tsr * 16 + self.sym["rules"], struct.pack("<H", rules))
        mu.mem_write(tsr * 16 + 0xFFF0, b"\xf4")
        mu.mem_write(types * 16 + 0x0E, bytes([type_ac]))
        mu.mem_write(ss * 16 + 0x7FA, struct.pack("<HHH", 0xFFF0, tsr, 0x202))
        regs = dict(cs=tsr, ds=0x5000, es=types, ss=ss, esp=0x7FA, ebp=0x600, ebx=0, eax=0x7777)
        regs["ecx" if probe == "probe_helm_ac" else "esi"] = kind
        for name, value in regs.items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(tsr * 16 + self.sym[probe], tsr * 16 + 0xFFF0)
        return mu.reg_read(r.UC_X86_REG_AX)

    def test_bone_helm(self):
        for probe in ("probe_helm_ac", "probe_box_ac"):
            self.assertEqual(self.ac(probe, ravager.BONE_HELM_TYPE, game.RULE_HELMS), 1, probe)
            self.assertEqual(self.ac(probe, ravager.BONE_HELM_TYPE, 0), 0, probe)
            self.assertEqual(self.ac(probe, 60, game.RULE_HELMS, 3), 3, probe)

    def test_the_gears_helm_is_that_type(self):
        self.assertEqual(ravgear.GEAR["bone helm"].type, ravager.BONE_HELM_TYPE)


if __name__ == "__main__":
    unittest.main()
