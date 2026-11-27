"""A Spellarcher's spell arrows made in Wake of the Ravager (DSCLOG2's SPELL ARROWS, site 240 and PICK POCKETS'
180-185; ravarrows.py through ravlog's RavDiceLog._answer_arrows): the header's words and the site, the patch's
bytes at the sequel's address (with DSUN_WOTR), the arrows' objects and the buttons' icons in the Loader's copies
(with DSUN_WOTR and DSUN_SL), the Loader's make on the sequel's layout, and DSCLOG2's buttons run in an emulated
CPU (needs nasm and unicorn, else skipped)."""

import os
import shutil
import struct
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import game, gff, ravager, ravarrows, ravitems, ravlog, spellarrows, weaponchoice  # noqa: E402
import test_ravkits  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE
    from unicorn import x86_const as r
except ImportError:
    Uc = None

WOTR = os.environ.get("DSUN_WOTR")
SL = os.environ.get("DSUN_SL")
ASM = test_ravkits.ASM
TSR, SS, DS = 0x1000, 0x4000, 0x5000
LOAD = DS - ravager.DGROUP
SHEET = 0x6000  # (the sheet on show's segment: [1429h])
SPELLARCHER = ((9, 11), 4, 1)  # (a half-elf fighter/preserver: the Spellarcher)
MAGE = ((9, 11), 4, 0)
HALT = 0xFFF0


class LoaderTests(unittest.TestCase):
    def test_patch(self):
        p = next(p for p in ravager.PATCHES if p.name == "arrows_close")
        self.assertEqual((p.offset, p.original), (0x9659E, bytes.fromhex("66833e9a2b00")))
        self.assertEqual(p.replacement, bytes((0xCD, ravager.VEC_SITE, 240)) + b"\x90" * 3)

    @unittest.skipUnless(WOTR, "DSUN_WOTR not set")
    def test_the_sequels_bytes(self):
        exe = open(os.path.join(WOTR, "DSUN.EXE"), "rb").read()
        self.assertEqual(exe[0x9659E:0x965A4], bytes.fromhex("66833e9a2b00"))

    def test_arrows_item(self):
        """The sequel's plain Arrows with the arrows' object, the mod's name, the spell + 1, worth nothing."""
        rec = ravarrows.arrows_item(2, 5)
        self.assertEqual(len(rec), ravager.ITEM_SIZE)
        self.assertEqual(struct.unpack_from("<hH", rec, 0), (-(ravitems.OWN_FIRST + 2618), 5))
        self.assertEqual(struct.unpack_from("<H", rec, 0x0A)[0], 6)  # (arrows)
        self.assertEqual(struct.unpack_from("<H", rec, 0x10)[0], 11)  # (Shocking Grasp, the sequel's 10)
        self.assertEqual(struct.unpack_from("<H", rec, 0x14)[0], ravager.mod_name(0x16E))
        self.assertEqual(struct.unpack_from("<H", rec, weaponchoice.ITEM_VALUE)[0], 0)
        self.assertEqual(rec[0x16], 0)  # (no plus of their own: ARROW_PLUS's by the archer's level)
        self.assertTrue(ravarrows.is_arrows_of(rec, 2))
        self.assertFalse(ravarrows.is_arrows_of(rec, 1))
        # (the same object the party transfer gives Shattered Lands' Shocking Arrows)
        self.assertEqual(ravarrows.own_object(2), ravitems.own_object(0x10000 - spellarrows.PICTURES[0x16E]))
        # (DSCLOG2's ARROW_PLUS names, WC_ARROWS spells)
        self.assertEqual([ravarrows.name_number(a.row) for a in ravarrows.ARROWS],
                         [256 + 43, 256 + 44, 256 + 45])
        self.assertEqual([a.spell for a in ravarrows.ARROWS], [3, 10, 38])


class FakeGame:
    """The bits of GameData make asks for, on the sequel's layout: party member 0 a Spellarcher."""
    def __init__(self, known=(3, 10), slots=None):
        self.ds = 0x1000
        self.known = set(known)
        self.slots = {1: 2, 3: 0} if slots is None else slots
        self.written = []
        self.quiver = None
        self.guest = mock.Mock()
        self.guest.write = lambda at, data: self.written.append((at, data))
        self.guest.read = self.read
        self.armoured = False

    def read(self, at, size):
        known = ravarrows.known_at(self, 0)
        if known <= at < known + ravarrows.KNOWN_SIZE:
            byte = at - known
            return bytes((sum(1 << (s % 8) for s in self.known if s // 8 == byte),))
        slots = self.ds * 16 + game.SLOTS_LEFT["Wizard"]
        return bytes((self.slots.get(at - slots, 0),))

    def creature_name(self, member):
        return "Lex"

    def no_spells(self, member):
        return self.armoured

    def _worn(self, member):
        if self.quiver is not None:
            rec = bytearray(ravarrows.arrows_item(*self.quiver))
            rec[game.ITEM_SLOT] = weaponchoice.AMMO_SLOT
            yield 9, bytes(rec), b""


class MakeTests(unittest.TestCase):
    def setUp(self):
        ravlog.apply_layout()
        self.addCleanup(ravlog.restore_layout)

    def patched(self):
        return (mock.patch.object(spellarrows, "is_spellarcher", lambda gd, m: m == 0),
                mock.patch.object(spellarrows, "item_address", lambda gd, index: 0x50000 + index * game.ITEM_SIZE),
                mock.patch.object(weaponchoice, "bow_ahead"),
                mock.patch("dsloader.npcitems.add_to", return_value=True))

    def test_make_a_new_stack(self):
        """The quiver empty: one arrow of the spell's in it, a 1st-level slot used (2 to 1), the bow put first."""
        gd = FakeGame()
        a, b, ahead, add = self.patched()
        with a, b, ahead as ahead, add as add:
            done = ravarrows.make(gd, 0, 1)
            self.assertEqual(done.text, "")
            self.assertIn("makes one of the chill arrows in the quiver (1 of 24 now)", done.log[0])
            self.assertIn("preserver level", done.log[0])
            rec = add.call_args[0][2]
            self.assertEqual(rec, ravarrows.arrows_item(1, 1))
            self.assertEqual(add.call_args[0][3], weaponchoice.AMMO_SLOT)
            ahead.assert_called_with(gd, 0)
            self.assertEqual(gd.written[-1], (gd.ds * 16 + 0x4469 + 1, bytes((1,))))  # (the sequel's SLOTS_LEFT)

    def test_onto_the_stack_and_full(self):
        gd = FakeGame()
        gd.quiver = (2, 7)
        a, b, ahead, add = self.patched()
        with a, b, ahead, add as add:
            done = ravarrows.make(gd, 0, 2)
            self.assertIn("makes one of the shocking arrows (8 of 24 now)", done.log[0])
            self.assertIn((0x50000 + 9 * game.ITEM_SIZE + 2, struct.pack("<H", 8)), gd.written)
            self.assertEqual(add.call_count, 0)
            gd.written.clear()
            gd.quiver = (2, 24)
            self.assertIn("are a full stack (24)", ravarrows.make(gd, 0, 2).text)
            self.assertEqual(gd.written, [])

    def test_refusals(self):
        """Not known, no slot left, in armour, not a Spellarcher, Burning Hands: words, nothing written."""
        a, b, ahead, add = self.patched()
        with a, b, ahead, add as add:
            gd = FakeGame(known=(3,))
            self.assertIn("can't weave Shocking Grasp", ravarrows.make(gd, 0, 2).text)
            gd = FakeGame(known=(38,))
            self.assertIn("no 3rd-level spell left", ravarrows.make(gd, 0, 3).text)
            gd.armoured = True
            gd.known.add(3)
            self.assertIn("in armour", ravarrows.make(gd, 0, 1).text)
            self.assertIn("can't weave", ravarrows.make(FakeGame(), 1, 1).text)
            self.assertIn("No spell arrows", ravarrows.make(FakeGame(), 0, 0).text)
            self.assertEqual(add.call_count, 0)


class LeftoverTests(unittest.TestCase):
    """#223's leftovers: the starting arrows, the strays, the Fine Bow's name, the light on the pointer."""
    def setUp(self):
        ravlog.apply_layout()
        self.addCleanup(ravlog.restore_layout)

    def test_lit_patches(self):
        """The pointer on a button lights that button (the handler's [BP-2]), not Turn Undead's place ([2B9Eh])."""
        for name, at in (("arrows_lit_on", 0x975B2), ("arrows_lit_off", 0x975F7)):
            p = next(p for p in ravager.PATCHES if p.name == name)
            self.assertEqual((p.offset, p.original, p.replacement),
                             (at, bytes.fromhex("ff369e2b"), bytes.fromhex("ff76fe90")))

    @unittest.skipUnless(WOTR, "DSUN_WOTR not set")
    def test_lit_bytes_in_the_sequel(self):
        exe = open(os.path.join(WOTR, "DSUN.EXE"), "rb").read()
        self.assertEqual(exe[0x975AE:0x975B6], bytes.fromhex("6a016a04ff369e2b"))  # (on: frame 4)
        self.assertEqual(exe[0x975F3:0x975FB], bytes.fromhex("6a016a05ff369e2b"))  # (off: frame 5)
        self.assertEqual(exe[0x97631:0x97634], bytes.fromhex("ff76fe"))  # (the press: the button's own)

    def test_starting_arrows(self):
        """Chill Touch and Shocking Grasp picked: the bow's +1 arrows go, 24 of each in their place, the first in
        the quiver; knowing none, the arrows kept; once (spell arrows had: none)."""
        gd = FakeGame()
        plus_one = bytearray(bytes.fromhex("26fd0c000f2778000f27060000000000000005ff1e0001"))
        plus_one[game.ITEM_SLOT] = weaponchoice.AMMO_SLOT
        worn = [(5, bytes(plus_one), b"")]
        gd._worn = lambda member: iter(list(worn))

        def add(gd_, member, rec, slot=None):
            worn.append((20 + len(worn), rec[:game.ITEM_SLOT] + bytes((slot if slot is not None else 14,))
                         + rec[game.ITEM_SLOT + 1:], b""))
            return True

        def unlink(gd_, it, index, what, empty=False):
            worn[:] = [w for w in worn if w[0] != index]
            return True
        with mock.patch("dsloader.npcitems.add_to", side_effect=add), \
                mock.patch("dsloader.ring.unlink", side_effect=unlink), mock.patch("dsloader.ring.Items"), \
                mock.patch.object(weaponchoice, "bow_ahead") as ahead, \
                mock.patch.object(ravarrows, "objects_ready", return_value=True):
            lines = ravarrows.starting_arrows(gd, 0)
            self.assertEqual(lines, ["Lex starts with 24 chill arrows in the quiver: Chill Touch picked",
                                     "Lex starts with 24 shocking arrows in the pack: Shocking Grasp picked"])
            # (added first, chill in the pack as the +1 arrows held the quiver; those gone, chill moved there)
            self.assertEqual(len(worn), 2)
            chill = next(w[1] for w in worn if ravarrows.is_arrows_of(w[1], 1))
            shock = next(w[1] for w in worn if ravarrows.is_arrows_of(w[1], 2))
            self.assertEqual((chill[game.ITEM_SLOT], shock[game.ITEM_SLOT]), (weaponchoice.AMMO_SLOT, 14))
            self.assertEqual(struct.unpack_from("<H", chill, 2)[0], 24)
            ahead.assert_called_with(gd, 0)
            self.assertEqual(ravarrows.starting_arrows(gd, 0), [])  # (once)
            worn[:] = [(5, bytes(plus_one), b"")]
            self.assertEqual(ravarrows.starting_arrows(FakeGame(known=()), 0), [])

    def test_starting_arrows_full_pack(self):
        """No room for any spell arrows (a full pack, the quiver the +1 arrows'): the +1 arrows kept, nothing said
        (the review of #229: they were taken first, and the archer was left with none)."""
        gd = FakeGame()
        plus_one = bytearray(bytes.fromhex("26fd0c000f2778000f27060000000000000005ff1e0001"))
        plus_one[game.ITEM_SLOT] = weaponchoice.AMMO_SLOT
        worn = [(5, bytes(plus_one), b"")]
        gd._worn = lambda member: iter(list(worn))
        with mock.patch("dsloader.npcitems.add_to", return_value=False) as add, \
                mock.patch("dsloader.ring.unlink") as unlink, mock.patch("dsloader.ring.Items"), \
                mock.patch.object(weaponchoice, "bow_ahead") as ahead, \
                mock.patch.object(ravarrows, "objects_ready", return_value=True):
            self.assertEqual(ravarrows.starting_arrows(gd, 0), [])
            self.assertEqual(add.call_count, 2)  # (both tried)
            unlink.assert_not_called()
            ahead.assert_not_called()
        self.assertEqual([w[0] for w in worn], [5])

    def test_starting_arrows_room_for_one(self):
        """Room for one stack (chill, in the pack): the +1 arrows go only after it is in, then chill to the quiver."""
        gd = FakeGame()
        plus_one = bytearray(bytes.fromhex("26fd0c000f2778000f27060000000000000005ff1e0001"))
        plus_one[game.ITEM_SLOT] = weaponchoice.AMMO_SLOT
        worn = [(5, bytes(plus_one), b"")]
        gd._worn = lambda member: iter(list(worn))
        order = []

        def add(gd_, member, rec, slot=None):
            order.append(("add", slot))
            if len([w for w in worn if w[0] != 5]) and slot is None:
                return False  # (the pack full after one)
            worn.append((30 + len(order), rec[:game.ITEM_SLOT] + bytes((slot if slot is not None else 14,))
                         + rec[game.ITEM_SLOT + 1:], b""))
            return True

        def unlink(gd_, it, index, what, empty=False):
            order.append(("unlink", index))
            worn[:] = [w for w in worn if w[0] != index]
            return True
        with mock.patch("dsloader.npcitems.add_to", side_effect=add), \
                mock.patch("dsloader.ring.unlink", side_effect=unlink), mock.patch("dsloader.ring.Items"), \
                mock.patch.object(weaponchoice, "bow_ahead"), \
                mock.patch.object(ravarrows, "objects_ready", return_value=True):
            lines = ravarrows.starting_arrows(gd, 0)
        self.assertEqual(lines, ["Lex starts with 24 chill arrows in the quiver: Chill Touch picked"])
        self.assertEqual(order[:3], [("add", None), ("add", None), ("unlink", 5)])
        self.assertEqual(len(worn), 1)
        self.assertEqual(worn[0][1][game.ITEM_SLOT], weaponchoice.AMMO_SLOT)

    def test_starting_arrows_no_objects(self):
        """The arrows' objects not in the Loader's OBJEX copy (objects_ready: RAV_SKIP's spell_arrows): the +1
        arrows kept, nothing tried (a spell arrow there would be an item of no object), and none due."""
        gd = FakeGame()
        plus_one = bytearray(bytes.fromhex("26fd0c000f2778000f27060000000000000005ff1e0001"))
        plus_one[game.ITEM_SLOT] = weaponchoice.AMMO_SLOT
        gd._worn = lambda member: iter([(5, bytes(plus_one), b"")])
        with mock.patch("dsloader.npcitems.add_to") as add, mock.patch("dsloader.ring.unlink") as unlink, \
                mock.patch.object(ravarrows, "objects_ready", return_value=False):
            self.assertEqual(ravarrows.starting_arrows(gd, 0), [])
            self.assertFalse(ravarrows.arrows_due(gd, 0))
        add.assert_not_called()
        unlink.assert_not_called()
        with mock.patch.object(ravarrows, "objects_ready", return_value=True):
            self.assertTrue(ravarrows.arrows_due(gd, 0))
            self.assertFalse(ravarrows.arrows_due(FakeGame(known=()), 0))  # (no touch spell picked)

    def test_objects_ready_all_three(self):
        """objects_ready wants every one of the arrows' three objects in the OBJEX copy: two are not enough."""
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, ravager.OBJECTS_COPY)
            self.assertFalse(ravarrows.objects_ready(d))  # (no copy)
            for rows, want in ((ravarrows.ARROWS[:2], False), (ravarrows.ARROWS, True)):
                chunks = {("OJFF", ravarrows.own_object(a.row)): b"\0" * 16 for a in rows}
                with open(path, "wb") as f:
                    f.write(b"GFFI")
                os.utime(path, (len(rows), len(rows)))  # (a new time: read again)
                with mock.patch.object(gff, "read_gff", return_value=chunks):
                    self.assertEqual(ravarrows.objects_ready(d), want, len(rows))

    def test_fine_bow_waits_on_the_arrows(self):
        """ravkitstart.fine_bow names the bow only once the starting arrows are in: a full pack leaves it plain
        (tried again in a later pass, not marked done); with room, the arrows in and then the bow named, by its
        name word alone (the arrows' moves relink the records)."""
        from dsloader import ravkitstart, specialize
        bow = bytearray(23)
        struct.pack_into("<H", bow, game.ITEM_TYPE, 18)
        gd = FakeGame()
        gd._worn = lambda member: iter([(4, bytes(bow), b"")])
        lines = ["Lex starts with 24 chill arrows in the quiver: Chill Touch picked"]
        with mock.patch.object(specialize, "kind_of", return_value=weaponchoice.BOW), \
                mock.patch.object(game, "far_pointer", return_value=0x60000), \
                mock.patch.object(ravarrows, "objects_ready", return_value=True), \
                mock.patch.object(ravarrows, "starting_arrows", return_value=[]):
            self.assertEqual(ravkitstart.fine_bow(gd, 0), [])  # (no room: due still)
            self.assertEqual(gd.written, [])
        with mock.patch.object(specialize, "kind_of", return_value=weaponchoice.BOW), \
                mock.patch.object(game, "far_pointer", return_value=0x60000), \
                mock.patch.object(ravarrows, "starting_arrows", return_value=lines):
            out = ravkitstart.fine_bow(gd, 0)
        self.assertEqual(out, ["Lex starts with a Fine Bow (+1 to hit): a Spellarcher's"] + lines)
        self.assertEqual(gd.written, [(0x60000 + 4 * game.ITEM_SIZE + game.ITEM_NAME,
                                       struct.pack("<H", ravager.FINE_BOW_NAME))])

    def test_strays_on_the_sequels_names(self):
        """return_strays with the sequel's names: another member's chill arrows back onto the Spellarcher's stack;
        nothing with a screen up (the map not on: DS:0DABh)."""
        lists = {0: [(9, self._arrows(1, 3, weaponchoice.AMMO_SLOT))], 1: [(12, self._arrows(1, 2, 15))]}
        gd = mock.Mock()
        gd.ds = 0x1000
        gd.in_combat.return_value = False
        gd._word.return_value = 1
        gd.creature.return_value = b"x" * game.CREATURE_SIZE
        gd._worn = lambda m: iter([(i, rec, b"") for i, rec in lists.get(m, [])])
        gd.creature_name = lambda m: ("Lex", "Bo")[m] if m < 2 else "?"
        writes = []
        gd.guest.write = lambda at, data: writes.append((at, data))

        def unlink(gd_, it, index, what, empty=False):
            for m in lists:
                lists[m] = [x for x in lists[m] if x[0] != index]
            return True
        with mock.patch.object(spellarrows, "is_spellarcher", lambda gd_, m: m == 0), \
                mock.patch.object(spellarrows, "item_address", lambda gd_, index: 0x50000 + index * game.ITEM_SIZE), \
                mock.patch("dsloader.ring.unlink", side_effect=unlink), mock.patch("dsloader.ring.held"), \
                mock.patch("dsloader.ring.Items"):
            gd._word.return_value = 3  # (a screen up: left be)
            self.assertEqual(ravarrows.return_strays(gd), [])
            gd._word.return_value = 1
            self.assertEqual(ravarrows.return_strays(gd),
                             ["The chill arrows go back to Lex from Bo: only a Spellarcher carries them (2)"])
            self.assertIn((0x50000 + 9 * game.ITEM_SIZE + 2, struct.pack("<H", 5)), writes)
            self.assertEqual(lists[1], [])

    @staticmethod
    def _arrows(row, count, slot):
        rec = bytearray(ravarrows.arrows_item(row, count))
        rec[game.ITEM_SLOT] = slot
        return bytes(rec)

    def test_fine_bow_named(self):
        """The dice log names the Loader's own items (256 on: DSCLOG2's ITEM_NAMES), the Fine Bow "item 305" before."""
        gd = ravlog.RavGameData.__new__(ravlog.RavGameData)
        gd._name_list = lambda: ["Club"] * 255
        self.assertEqual(gd.item_name(ravager.FINE_BOW_NAME), "Fine Bow")
        self.assertEqual(gd.item_name(ravarrows.name_number(2)), "Shocking Arrows")
        self.assertEqual(gd.item_name(1), "Club")
        gd.mod_names = ravager.item_names([b"Lucky Stone"])
        self.assertEqual(gd.item_name(ravager.KEEPSAKE_NAMES_FIRST), "Lucky Stone")
        self.assertEqual(gd.item_name(ravager.NAMES_GAME + ravager.NAMES_ROOM - 1), f"item {ravager.NAMES_GAME + ravager.NAMES_ROOM - 1}")


class CopyTests(unittest.TestCase):
    @unittest.skipUnless(WOTR and SL, "DSUN_WOTR and DSUN_SL not set")
    def test_objects_and_icons(self):
        """The Loader's OBJEX copy has the arrows' three objects with no party transferred (their RDFF item the
        sequel's arrows with the spell); its RESOURCE copy ICON 3050-3052; RAV_SKIP's spell_arrows neither."""
        data = open(os.path.join(WOTR, "OBJEX.GFF"), "rb").read()
        arrows = lambda chunks: ravarrows.from_files(chunks, SL, WOTR)
        out, done = ravager.objects_fixed(data, frozenset(), None, None, arrows)
        self.assertIn(ravarrows.SKIP, done)
        chunks = gff.read_gff(out)
        from dsloader import dataitems
        for a in ravarrows.ARROWS:
            obj = ravarrows.own_object(a.row)
            for kind in ravitems.OBJECT_KINDS:
                self.assertIn((kind, obj), chunks)
            rec = dataitems.records(chunks[("RDFF", obj)])[0][0].data
            self.assertEqual(struct.unpack_from("<hHH", rec, 0x0A)[0], 6)
            self.assertEqual(struct.unpack_from("<H", rec, 0x10)[0], a.spell + 1)
        out, done = ravager.objects_fixed(data, {ravarrows.SKIP}, None, None, arrows)
        self.assertNotIn(("OJFF", ravarrows.own_object(1)), gff.read_gff(out))
        res = open(os.path.join(WOTR, ravager.RESOURCE_FILE), "rb").read()
        out, done = ravager.resources_fixed(res, sl_dir=SL)
        self.assertIn(ravarrows.SKIP, done)
        from dsloader import wotrart
        got = gff.read_gff(out)
        for icon in (3050, 3051, 3052):
            rows = wotrart.decode_plnr(got[("ICON", icon)])
            self.assertEqual((len(rows), len(rows[0])), (16, 16))
        self.assertNotIn(("ICON", 3049), got)
        # (without Shattered Lands: the sequel's own touch spells' icons)
        bare = ravarrows.resource_chunks(gff.read_gff(res), None)
        self.assertEqual(bare[("ICON", 3050)], gff.read_gff(res)[("ICON", 21003)])


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class HelperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]

    def test_header_and_site(self):
        hdr = self.sym["hdr"]
        for name, at in (("arrows_on", ravlog.AR_ON), ("arrows_seq", ravlog.AR_SEQ), ("arrows_reply", ravlog.AR_REPLY),
                         ("arrows_who", ravlog.AR_WHO), ("arrows_row", ravlog.AR_ROW),
                         ("arrows_shown", ravlog.AR_SHOWN), ("arrows_late", ravlog.AR_LATE),
                         ("extras_drawn", ravlog.AR_DRAWN)):
            self.assertEqual(self.sym[name] - hdr, at, name)
        self.assertEqual(self.sym["fine_hits"] - hdr, 2096)
        hdr_len = struct.unpack_from("<H", self.image, hdr + ravlog.HDR_LEN)[0]  # (HDR_LEN: the header's end)
        self.assertEqual(hdr_len, self.sym["hdr_end"] - hdr)
        self.assertGreaterEqual(hdr_len, max(ravlog.AR_DRAWN, ravlog.LOCK_BARS) + 2)
        self.assertLessEqual(ravlog.AR_DRAWN + 2, 2200)  # (the header's room up to +2199)
        table = self.sym["site_table"]
        word = lambda n: struct.unpack_from("<H", self.image, table + 2 * n)[0]
        self.assertEqual(word(240), self.sym["pp_close"])
        for n in list(range(216, 240)) + list(range(241, 260)):
            if table + 2 * n < self.sym["site_table"] + 2 * 241:
                self.assertEqual(word(n), self.sym["site_none"], n)
        self.assertLess(self.sym["pp_icons2"], self.sym["resident_end"])

    def setUp(self):
        self.mu = Uc(UC_ARCH_X86, UC_MODE_16)
        self.mu.mem_map(0, 0x100000)
        self.mu.mem_write(TSR * 16, self.image)
        self.mu.mem_write(TSR * 16 + HALT, b"\xf4" * 16)
        ravlog.apply_layout()
        self.addCleanup(ravlog.restore_layout)
        old = game.RULES_IN_FORCE
        game.RULES_IN_FORCE = old | game.RULE_KITS
        self.addCleanup(setattr, game, "RULES_IN_FORCE", old)
        self.put("hdr", struct.pack("<H", game.RULE_KITS >> 16), test_ravkits.RULES_HI)
        self.calls = []  # (the game's far routines reached: (segment less the load, offset))
        for seg, off in ((0x47C1, 0x6B), (0x46BD, 0x4D), (0x28FF, 0x4AB), (0x344C, 0x92)):
            self.mu.mem_write((LOAD + seg) * 16 + off, b"\xcb")  # (retf)
        self.mu.hook_add(UC_HOOK_CODE, self.far_call)

    def far_call(self, mu, address, size, data):
        for seg, off in ((0x47C1, 0x6B), (0x46BD, 0x4D), (0x28FF, 0x4AB), (0x344C, 0x92)):
            if address == (LOAD + seg) * 16 + off:
                sp = mu.reg_read(r.UC_X86_REG_SP)
                args = struct.unpack("<6H", mu.mem_read(SS * 16 + sp + 4, 12))
                self.calls.append((seg, off, args))

    def put(self, name, data, plus=0):
        self.mu.mem_write(TSR * 16 + self.sym[name] + plus, data)

    def get(self, name, size=2):
        data = bytes(self.mu.mem_read(TSR * 16 + self.sym[name], size))
        return struct.unpack("<H", data)[0] if size == 2 else data

    def show(self, who=SPELLARCHER, known=(3,), on=1, fight=0, element=0, pick_on=2):
        """PP_SHOW for the member on show (party member 2) WHO, knowing the sequel's wizard spells KNOWN."""
        self.put("arrows_on", struct.pack("<H", on))
        self.put("pick_on", struct.pack("<H", pick_on))
        classes, race, byte = who
        self.mu.mem_write(SHEET * 16, test_ravkits.wotr_sheet(classes, (5, 5), race, byte))
        self.mu.mem_write(DS * 16 + 0x1429, struct.pack("<HH", 0, SHEET))
        self.mu.mem_write(DS * 16 + 0x9C1C, struct.pack("<H", element))
        self.mu.mem_write(DS * 16 + 0x9D77, struct.pack("<H", 0xBE5))
        self.mu.mem_write((LOAD + 0x3C10) * 16 + 0x19, struct.pack("<H", fight))
        self.mu.mem_write((LOAD + 0x3E71) * 16 + 0xB44, struct.pack("<H", 2))
        bits = bytearray(15)
        for s in known:
            bits[s // 8] |= 1 << (s % 8)
        self.mu.mem_write((LOAD + 0x3D62) * 16 + 0x39C + 2 * 15, bytes(bits))
        return self.site("pp_show")

    def site(self, routine, ebp=0x7F8, stack=()):
        sp = 0x7F0 - 2 * len(stack)
        self.mu.mem_write(SS * 16 + sp, b"".join(struct.pack("<H", w) for w in stack))
        sp -= 6
        self.mu.mem_write(SS * 16 + sp, struct.pack("<HHH", HALT, TSR, 0x2))
        for name, value in dict(cs=TSR, ds=DS, ss=SS, esp=sp, eflags=0x2, ebp=ebp).items():
            self.mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        self.mu.emu_start(TSR * 16 + self.sym[routine], TSR * 16 + HALT, count=200000)
        self.assertEqual(self.mu.reg_read(r.UC_X86_REG_IP), HALT)
        return self.mu.reg_read(r.UC_X86_REG_EFLAGS)

    def test_one_button_in_turn_undeads_place(self):
        """Knowing Chill Touch: its arrows in Turn Undead's place (element 9, icon 3050, kind 3), a button (ZF
        clear), nothing beside it (no game routine called)."""
        flags = self.show(known=(3,))
        self.assertFalse(flags & 0x40)
        word = lambda at: struct.unpack("<H", self.mu.mem_read(at, 2))[0]
        self.assertEqual((word(DS * 16 + 0x9C1C), word(DS * 16 + 0x9D77)), (9, 3050))
        self.assertEqual(self.get("pp_shown", 1)[0], 3)
        self.assertEqual(self.get("pp_extra", 4), bytes(4))
        self.assertEqual(self.get("arrows_shown"), 1)
        self.assertEqual(self.calls, [])

    def test_three_buttons(self):
        """All three touch spells: Chill in Turn Undead's place, Shocking and Vampiric beside it (APFM 2BE7h,
        2BE8h): each one's icon loaded (ICON 3051, 3052), its handler set (Turn Undead's, 698h:66h), its frame
        drawn (index 1Ah, 1Bh)."""
        self.show(known=(3, 10, 38))
        self.assertEqual(self.get("pp_shown", 1)[0], 3)
        self.assertEqual(self.get("pp_extra", 4), bytes((4, 5, 0, 0)))
        self.assertEqual(self.get("pp_extra_on", 4), bytes((1, 1, 0, 0)))
        loads = [c for c in self.calls if c[0] == 0x28FF]
        self.assertEqual([c[2][2] for c in loads], [3051, 3052])  # (ICON, then the number: "ICON" dword first)
        regs = [c for c in self.calls if c[0] == 0x46BD]
        self.assertEqual([c[2][2] for c in regs], [0x2BE7, 0x2BE8])
        self.assertEqual([c[2][3:5] for c in regs], [(0x66, LOAD + 0x47C1)] * 2)
        draws = [c for c in self.calls if c[0] == 0x47C1]
        self.assertEqual([c[2][3] for c in draws], [0x1A, 0x1B])  # (frames; no icon drawn: none loaded here)
        self.assertEqual(self.get("extras_drawn"), 2)
        # another character on show, a plain mage: the slots' handlers taken off
        self.calls.clear()
        self.show(who=MAGE, known=(3, 10, 38))
        self.assertEqual(self.get("pp_shown", 1)[0], 0)
        regs = [c for c in self.calls if c[0] == 0x46BD]
        self.assertEqual([(c[2][2], c[2][3]) for c in regs], [(0x2BE7, 0), (0x2BE8, 0)])
        self.assertEqual(self.get("pp_extra_on", 4), bytes(4))

    def test_none(self):
        """Not a Spellarcher, the Loader not asking, a fight, no touch spell known (Burning Hands, 1, never):
        no button."""
        for kwargs in (dict(who=MAGE), dict(on=0), dict(fight=1), dict(known=(1, 2))):
            with self.subTest(**{k: str(v) for k, v in kwargs.items()}):
                flags = self.show(**kwargs)
                self.assertTrue(flags & 0x40)
                self.assertEqual(self.get("pp_shown", 1)[0], 0)

    def test_name_and_click(self):
        """The handler's frame naming the button: CHILL ARROWS for Turn Undead's place, SHOCKING ARROWS for
        2BE7h, the game's TURN UNDEAD for any other; let go of, the kind armed."""
        self.show(known=(3, 10))
        frame = 0x600
        for button, want in ((0x2BEF, b"CHILL ARROWS"), (0x2BE7, b"SHOCKING ARROWS")):
            self.mu.mem_write(SS * 16 + frame + 8, struct.pack("<H", button))
            self.mu.mem_write(SS * 16 + frame, struct.pack("<H", 0))
            # (PP_TEXT: under two pushes of the game's)
            self.site("pp_text", ebp=frame, stack=(0, 0))
            sp = self.mu.reg_read(r.UC_X86_REG_SP)
            off, seg = struct.unpack("<HH", self.mu.mem_read(SS * 16 + sp, 4))
            self.assertEqual(seg, TSR)
            self.assertEqual(bytes(self.mu.mem_read(TSR * 16 + off, len(want))), want)
            flags = self.site("pp_click", ebp=frame)
            self.assertFalse(flags & 0x40)
            self.assertEqual(self.get("pp_arming", 1)[0], 3 if button == 0x2BEF else 4)

    def test_close(self):
        """PP_CLOSE: the icons beside Turn Undead's let go of (1D0h:92h), the slots forgotten; the game's compare."""
        self.put("pp_icons2", struct.pack("<HH", 0x10, 0x7000))
        self.put("pp_extra_on", b"\x01\x01\0\0")
        self.mu.mem_write(DS * 16 + 0x2B9A, bytes(4))
        flags = self.site("pp_close")
        self.assertTrue(flags & 0x40)  # (Turn Undead's icon none: ZF)
        self.assertEqual([c[:2] for c in self.calls], [(0x344C, 0x92)])
        self.assertEqual(self.get("pp_extra_on", 4), bytes(4))

    def test_ask(self):
        """ARROWS_ASK: the member and the spell's place to the Loader (ARROWS_SEQ); answered with no words,
        nothing shown; not answered in time, marked answered and counted late."""
        self.mu.mem_write((LOAD + 0x3E71) * 16 + 0xB44, struct.pack("<H", 2))
        self.put("arrows_which", b"\x02")
        self.put("stats_stamp", struct.pack("<H", 0))  # (the Loader's last pass: the BIOS timer's 0)

        def answer(mu, address, size, data):
            seq = self.get("arrows_seq")
            if seq != self.get("arrows_reply"):
                self.put("arrows_reply", struct.pack("<H", seq))
        hook = self.mu.hook_add(UC_HOOK_CODE, answer)
        self.mu.reg_write(r.UC_X86_REG_DS, DS)
        self.call("arrows_ask")
        self.assertEqual((self.get("arrows_seq"), self.get("arrows_reply"), self.get("arrows_who"),
                          self.get("arrows_row"), self.get("arrows_late")), (1, 1, 2, 2, 0))
        self.mu.hook_del(hook)
        self.call("arrows_ask")  # (no answer: the BIOS ticks run on)
        self.assertEqual((self.get("arrows_seq"), self.get("arrows_reply"), self.get("arrows_late")), (2, 2, 1))

    def call(self, routine):
        sp = 0x7F0
        self.mu.mem_write(SS * 16 + sp, struct.pack("<H", HALT))
        for name, value in dict(cs=TSR, ds=DS, ss=SS, esp=sp, eflags=0x202, ebp=0x7F8).items():
            self.mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        ticks = [0]

        def tick(mu, address, size, data):  # (the BIOS timer runs on as the wait loops)
            ticks[0] += 1
            if ticks[0] % 50 == 0:
                now = struct.unpack("<H", mu.mem_read(0x46C, 2))[0]
                mu.mem_write(0x46C, struct.pack("<H", (now + 1) & 0xFFFF))
        hook = self.mu.hook_add(UC_HOOK_CODE, tick)
        self.mu.mem_write(0x46C, struct.pack("<H", 0))
        self.mu.emu_start(TSR * 16 + self.sym[routine], TSR * 16 + HALT, count=500000)
        self.mu.hook_del(hook)
        self.assertEqual(self.mu.reg_read(r.UC_X86_REG_IP), HALT)


if __name__ == "__main__":
    unittest.main()
