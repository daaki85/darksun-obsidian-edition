"""The mod's six new wizard spells in Wake of the Ravager's RESOURCE.GFF copy (dsloader.ravspells): their
numbers, records, descriptions and icons. With DSUN_WOTR (and DSUN_SL for the icons: Shattered Lands'
drawn ones) the copy is made from the player's own files (never in the repository)."""
import os
import struct
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
        self.assertEqual((fog[4], fog[0x11:0x13], fog[0x19]), (0x42, b"\0\x40", ravspells.FOG_EFFECT))
        self.assertEqual(ravspells.record(chunks, ravspells.CLAW)[0x19], ravspells.CLAW_EFFECT)
        friends = ravspells.record(chunks, ravspells.FRIENDS)
        self.assertEqual((friends[1:3], friends[0x0C], friends[0x1D]), (b"\xff\xff", 7, 1))

    def test_sites(self):
        """The program's patches are DSCLOG2's SITE 140-149 (each its routine in the site table), past the
        other threads' 130-139 and short of 150, 86 (the item box's INFO), and the 6th-level priest spells'
        222 and 225-227; the effect records after the game's 113."""
        import re
        src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos", "dsclog2.asm")).read()
        routine = {ravspells.NS_CMP: "ns_cmp", ravspells.NS_KNOW: "ns_know", ravspells.NS_LEVEL: "ns_level",
                   ravspells.NS_LIST: "ns_list", ravspells.NS_CAST: "ns_cast", ravspells.NS_EFFECT: "ns_effect",
                   ravspells.NS_ABILITY: "ns_ability", ravspells.NS_CLAW: "ns_claw",
                   ravspells.NS_SCROLL: "ns_scroll", ravspells.NS_LEARN: "ns_learn",
                   ravspells.NS_INFO: "ns_info", ravspells.PRIEST_SPHERE: "priest_sphere",
                   ravspells.WW_SETUP: "ww_setup_s", ravspells.WW_GATE: "ww_gate_s", ravspells.WW_DRAW: "ww_draw_s"}
        self.assertEqual(sorted(routine), [86, *range(140, 150), 222, 225, 226, 227])
        for number, name in routine.items():
            self.assertRegex(src, r"\n        dw %s +; %d SITE_" % (name, number))
        names = {p.name for p in ravager.PATCHES}
        for p in ravspells.program_patches():
            self.assertIn(p.name, names)
            if p.name not in ("ns_effects", ravspells.SPHERES_SKIP):
                self.assertEqual(p.replacement[:2], bytes((0xCD, ravager.VEC_SITE)), p.name)
                self.assertIn(p.replacement[2], routine, p.name)
                self.assertEqual(len(p.replacement), len(p.original), p.name)
        effects = ravspells.effect_patch().replacement
        self.assertEqual(len(effects), 4 * 31)
        self.assertEqual(effects[31:31 + 11], b"Erdlu Claw\0")
        self.assertEqual(effects[29:31], (21320).to_bytes(2, "little"))
        for name, value in (("NS_GRACE_EFFECT", 113), ("NS_CLAW_EFFECT", 114), ("NS_FOG_EFFECT", 115),
                            ("NS_FRIENDS_EFFECT", 116), ("NS_FIRST", 320)):
            self.assertRegex(src, r"\n%s +equ %d\b" % (name, value))


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

    def test_priest_resources(self):
        patched, _ = ravager.resources_fixed(self.data, frozenset(), None, SL)
        records = gff.read_gff(patched)
        for number, name in ((326, b"WHIRLWIND"), (327, b"RESTORE YOUTH")):
            data = records["DATA", number]
            self.assertEqual(len(data), ravager.SPELL_SIZE)
            self.assertEqual(data[32:64].rstrip(b"\0"), name)
            self.assertTrue(records["SPIN", number + 1].startswith(name))
            self.assertEqual(len(sequelicons.decode(records["ICON", 21000 + number])), 16)
        self.assertEqual(records["DATA", 327][0x1C:0x1F], bytes(3))
        self.assertNotIn(records["ICON", 21326], [v for (k, _), v in self.game.items() if k == "ICON"])  # (not Sand Storm's)
        self.assertNotEqual(records["ICON", 21327], self.game["ICON", 21194])
        self.assertEqual(records["DATA", 326][0x17], ravspells.WHIRL_AREA)
        self.assertEqual(records["DATA", 326][0x19:0x20], bytes.fromhex("42 08 02 00 11 08 A1"))

    def test_priest6_spheres(self):
        """The 6th-level spheres' patch: the sequel's bytes there, made Shattered Lands' (game.PRIEST6_MASKS by
        element: Blade Barrier air, Sunstroke fire, Wall of Thorns earth), where ravager's SPHERES_FILE says."""
        exe = open(os.path.join(WOTR, "DSUN.EXE"), "rb").read()
        self.assertEqual(ravspells.SPHERES_FILE, ravager.SPHERES_FILE)
        at = ravspells.SPHERES_FILE + ravspells.BLADE_BARRIER
        self.assertEqual(exe[at:at + 7], ravspells.SPHERES_WAS)
        now = dict(zip(range(208, 215), ravspells.SPHERES_NOW))
        self.assertEqual((now[208], now[213], now[214]), (ravager.AIR, ravager.FIRE, ravager.EARTH))
        self.assertEqual(ravager.skipped({"new_spells": False}) >= {ravspells.SPHERES_SKIP, "ww_setup"}, True)
        self.assertNotIn(ravspells.SPHERES_SKIP, ravager.skipped({"new_spells": True}))

    def test_area_segment_relocations(self):
        """WW_SETUP's WW_REFS are every MZ relocation of selector 3D0h's segment (41F1h), and its selector."""
        import re
        exe = open(os.path.join(WOTR, "DSUN.EXE"), "rb").read()
        count, paragraphs = struct.unpack_from("<HH", exe, 6)
        start, = struct.unpack_from("<H", exe, 0x18)
        fixups = set()
        for index in range(count):
            off, seg = struct.unpack_from("<HH", exe, start + index * 4)
            place = (paragraphs + seg) * 16 + off
            if exe[place:place + 2] == bytes.fromhex("f1 41"):
                fixups.add((seg, off))
        helper = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos",
                                   "dsclog2.asm")).read()
        table = helper.split("ww_refs dw ", 1)[1].split("ww_refs_end:", 1)[0]
        values = [int(word, 16) for word in re.findall(r"0x[0-9A-F]+", table)]
        self.assertEqual(set(zip(values[::2], values[1::2])), fixups)
        self.assertEqual(tuple(values[-2:]), (0x45E8, 0x3D0))

    def test_funnel(self):
        """Whirlwind's funnel (whirlart's, four frames) in the objects' copy with the new spells' rule, and none
        without it."""
        import tempfile
        from dsloader import whirlart
        with tempfile.TemporaryDirectory() as temp:
            copy = os.path.join(temp, "OBJEX2.GFF")
            for enabled in (True, False):
                with self.subTest(enabled=enabled):
                    skip = ravager.skipped({"new_spells": enabled, "new_items": False})
                    ravager.write_objects(WOTR, copy, skip)
                    chunks = gff.read_gff(open(copy, "rb").read())
                    self.assertEqual(("OJFF", whirlart.OBJECT) in chunks, enabled)
                    self.assertEqual(("BMP ", whirlart.OBJECT) in chunks, enabled)
                    if enabled:
                        self.assertEqual(struct.unpack_from("<H", chunks["BMP ", whirlart.OBJECT], 4)[0], 4)

    def test_program(self):
        """The patches' bytes are the sequel's DSUN.EXE's, its effect records 113-116 empty, and
        dos/ns_cmp_table.inc NS_CMP's table from the patched program."""
        import tempfile
        with open(os.path.join(WOTR, "DSUN.EXE"), "rb") as f:
            exe = f.read()
        for p in ravspells.program_patches():
            self.assertEqual(exe[p.offset:p.offset + len(p.original)], p.original, p.name)
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "x.exe")
            ravager.write_patched(WOTR, out)
            with open(out, "rb") as f:
                patched = f.read()
        inc = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos", "ns_cmp_table.inc")
        with open(inc) as f:
            self.assertEqual(f.read(), ravspells.cmp_table_asm(patched))

    def test_item_powers(self):
        """The sequel's items whose power (the spell + 1) is a new spell's, 321 to 326, are the game's own
        effects (the psionic powerstone, Ioun stones...), none of them the type DSCLOG2's NS_BOOK takes as a
        wizard's scroll or book (77, the spellbooks' and scrolls'), and NS_CMP's item sites each say where
        their item is."""
        import struct
        from dsloader import dataitems
        self.assertEqual(set(ravspells.PLUS1_ITEM), set(ravspells.PLUS1_SITES))
        with open(os.path.join(WOTR, "OBJEX.GFF"), "rb") as f:
            objects = gff.read_gff(f.read())
        powered, books = [], []
        for (kind, number), chunk in objects.items():
            if kind != "RDFF":
                continue
            try:
                item = dataitems.records(chunk)[0][0].data
            except (IndexError, ValueError, struct.error):
                continue
            if len(item) < 0x12:
                continue
            kind_of = struct.unpack_from("<H", item, 0x0A)[0]
            if 321 <= struct.unpack_from("<H", item, 0x10)[0] <= 326:
                powered.append((number, kind_of))
            if number in (31002, 31010, 31300):
                books.append(kind_of)
        self.assertIn((30033, 78), powered)  # (the powerstone, 146h)
        self.assertNotIn(77, [k for _, k in powered])
        self.assertEqual(books, [77, 77, 77])
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos",
                               "dsclog2.asm")) as f:
            self.assertIn("NS_BOOK_TYPE equ 77", f.read())

    @unittest.skipUnless(SL, "DSUN_SL: Shattered Lands' folder, for the drawn icons")
    def test_drawn_icons(self):
        """With Shattered Lands' files the icons are the mod's drawn ones, not the templates'."""
        got = ravspells.icons_for(self.game, SL)
        for spell in ravspells.SPELLS:
            self.assertNotEqual(got[("ICON", 21000 + spell)], self.game[("ICON", 21000 + ravspells.TEMPLATES[spell])])


if __name__ == "__main__":
    unittest.main()
