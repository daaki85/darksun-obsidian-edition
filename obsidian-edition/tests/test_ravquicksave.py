"""Quick save, quick load and autosave in Wake of the Ravager (DSCLOG2's QUICK SAVES, quicksave.py on
ravlog.QUICK_LAYOUT): the Loader's side on the sequel's header fields and addresses (every write inside the
ranges a read-only view lets through), DSCLOG2's QS_KEY, SAVE_TICK (the game's save with the Loader's file
and name, its GREQ chunk written as the game's SAVE window writes a slot's, a fight refused, the LOAD
window) and GREQ_LOAD (site 84) run in an emulated CPU (needs nasm and unicorn, else skipped); the named
saves of the sequel's folder; with DSUN_WOTR the sequel's own bytes where the helper calls and patches."""

import os
import shutil
import struct
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import gff, namedsaves, quicksave as q, ravager, ravlog  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE
    from unicorn import x86_const as r
except ImportError:
    Uc = None

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASM = os.path.join(HERE, "dos", "dsclog2.asm")
WOTR = os.environ.get("DSUN_WOTR")
LAY = ravlog.QUICK_LAYOUT
HDR, DS, TAIL_SEG, SAVE_OFF = 0x20000, 0x5000, 0x2800, 0x100


class Guest:
    """The game's memory, every write checked against the ranges QuickSave.ranges gives."""

    def __init__(self):
        self.m = bytearray(0x100000)
        self.allowed = None

    def read(self, at, n):
        return bytes(self.m[at:at + n])

    def write(self, at, data):
        if self.allowed is not None:
            assert any(s <= at and at + len(data) <= s + n for s, n in self.allowed), hex(at)
        self.m[at:at + len(data)] = data


class Game:
    def __init__(self):
        self.guest, self.ds = Guest(), DS
        self.area, self.fight, self.clock = 0x32, False, 3600 * 9 + 60 * 5
        struct.pack_into("<H", self.guest.m, HDR + LAY.tail_seg, TAIL_SEG)
        struct.pack_into("<H", self.guest.m, HDR + LAY.save_off, SAVE_OFF)
        struct.pack_into("<HH", self.guest.m, HDR + LAY.keys, 0xFFFF, 0xFFFF)
        struct.pack_into("<H", self.guest.m, DS * 16 + LAY.screen_is, q.ON_MAP)
        self.guest.write(DS * 16 + LAY.name_find, b"E")
        self.guest.write(DS * 16 + LAY.name_save, b"E")

    def creature(self, n):
        return bytes((4,)) * 0x31  # (SL's camp byte would read 4 here: the sequel has none)

    def region(self):
        return self.area

    def fight_on(self):
        return self.fight

    def game_time(self):
        return self.clock

    def _word(self, at):
        return struct.unpack_from("<H", self.guest.m, self.ds * 16 + at)[0]

    def hdr(self, field, value=None):
        if value is not None:
            struct.pack_into("<H", self.guest.m, HDR + field, value)
        return struct.unpack_from("<H", self.guest.m, HDR + field)[0]


class LoaderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.gd, self.qs, self.now, self.ticks = Game(), q.QuickSave(LAY), 100.0, 0
        self.gd.guest.allowed = self.qs.ranges(self.gd, HDR)
        self.free = mock.patch.object(q, "disk_free", return_value=500 * 1024 * 1024)
        self.free.start()

    def tearDown(self):
        self.free.stop()
        self.tmp.cleanup()

    def tick(self, seconds=1.0):
        self.now += seconds
        self.ticks += 5
        self.gd.hdr(LAY.main_ticks, self.ticks)
        return self.qs.tick(self.gd, HDR, self.tmp.name, False, self.now)

    def test_the_layout(self):
        """DSCLOG2's fields past DSCLOG's (whose +1878 to +1889 are other fields in DSCLOG2), MAIN_TICKS at
        DSCLOG's +260; the game's addresses the sequel's."""
        self.assertEqual((LAY.keys, LAY.seq, LAY.req, LAY.save_off, LAY.greq, LAY.main_ticks), (1904, 1908, 1912, 1914, 1916, 260))
        self.assertEqual((LAY.screen_is, LAY.save_path, LAY.name_find, LAY.name_save), (0x0DAB, 0x44F2, 0x2088, 0x20B9))
        self.assertEqual((ravager.DGROUP - LAY.window_from_ds, LAY.chosen, LAY.camp, LAY.kept_pages), (0x3C4C, 0, None, (b"E",)))

    def test_quick_save_with_its_greq(self):
        self.tick()
        self.assertEqual((self.gd.hdr(LAY.keys), self.gd.hdr(LAY.keys + 2)), (q.KEY_SAVE, q.KEY_LOAD))
        self.gd.hdr(LAY.seq, 1)
        self.tick()
        text = self.gd.guest.read(TAIL_SEG * 16 + SAVE_OFF, q.SAVE_FILE + q.SAVE_NAME)
        self.assertEqual(text[:q.SAVE_FILE].split(b"\0")[0], b"SAVQ01.SAV")
        self.assertEqual(text[q.SAVE_FILE:].split(b"\0")[0], b"Quick - Day 1, 09:05")
        self.assertEqual((self.gd.hdr(LAY.req), self.gd.hdr(LAY.greq)), (q.REQ_SAVE, q.GREQ_QUICK + 1))
        self.gd.hdr(LAY.req, q.DONE)
        self.assertEqual(self.tick(), ['Quick save: "Quick - Day 1, 09:05" (the QUICK page, slot 1)'])

    def test_quick_load_and_the_page_back(self):
        with open(os.path.join(self.tmp.name, "SAVQ07.SAV"), "wb") as f:
            f.write(b"x")
        self.tick()
        self.gd.hdr(LAY.seq + 2, 1)
        self.tick()
        self.assertEqual(self.gd.hdr(LAY.req), q.REQ_LOAD)
        self.assertEqual(self.gd.guest.read(DS * 16 + LAY.name_find, 1) + self.gd.guest.read(DS * 16 + LAY.name_save, 1), b"QQ")
        self.assertEqual(struct.unpack_from("<H", self.gd.guest.m, 0x3C4C * 16 - (ravager.DGROUP - DS) * 16)[0], 6)
        for _ in range(int(q.ANSWER_WAIT) + 3):  # (F9's window open, the main loop running in it: SAVE_REQ 0)
            self.gd.hdr(LAY.req, 0)
            self.tick()
        self.assertEqual(self.gd.guest.read(DS * 16 + LAY.name_find, 1), b"Q")  # (left: DSCLOG2's PAGE_BACK)
        self.assertFalse(LAY.page_back)

    def test_autosave_named_by_the_sequels_areas(self):
        self.tick()
        self.gd.area = 0x38
        for _ in range(6):
            self.tick()
        name = self.gd.guest.read(TAIL_SEG * 16 + SAVE_OFF + q.SAVE_FILE, q.SAVE_NAME).split(b"\0")[0]
        self.assertEqual(name, b"Auto Day 1, 09:05 Mines 1")  # (the sequel's short names: its narrow rows)
        self.assertEqual(self.gd.hdr(LAY.greq), q.GREQ_QUICK + 6)

    def test_autosave_names_fit_the_sequels_rows(self):
        """Every area's autosave name, and the fight's, at most RAV_NAME_MOST letters (its LOAD window cut
        "Auto - Day 1, 00:06 - after a fight" at 29), on the first day and the 147th."""
        self.assertEqual(q.auto_name(LAY.after_fight, 366, LAY.name_most, LAY.name_join), "Auto Day 1, 00:06 fight")
        for clock in (366, 86400 * 146 + 86399):
            for region in list(ravlog.REGIONS) + [0x77]:
                name = q.auto_name(LAY.region_name(region), clock, LAY.name_most, LAY.name_join)
                self.assertLessEqual(len(name), ravlog.RAV_NAME_MOST, name)
        self.assertEqual(q.auto_name("after a fight", 366), "Auto - Day 1, 00:06 - after a fight")  # (SL's)

    def test_no_camp(self):
        """SL's camp byte reads 4 in the sequel's records (Game.creature): the keys stay the Loader's."""
        self.tick()
        self.assertEqual(self.gd.hdr(LAY.keys), q.KEY_SAVE)

    def test_region_names(self):
        self.assertEqual(ravlog.region_name(0x32), "Tyr")
        self.assertEqual(ravlog.region_name(0x77), "Area 77h")
        self.assertEqual(ravlog.region_short(0x38), "Mines 1")
        self.assertEqual(set(ravlog.REGIONS_SHORT), set(ravlog.REGIONS))


def save_file(name, size=ravager.SHEET_SIZE):
    """A sequel's save: STXT 1 its name, SAVE 6 its 17 sheets."""
    chunks = {("STXT", 1): name.encode().ljust(43, b"\0"), ravager.SHEETS_CHUNK: bytes(range(size)) * 17,
              ("SAVE", 5): bytes(0x31 * 4)}
    from test_ravsheet import gff_file
    return gff_file(chunks)


class NamedSavesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.game, self.named = (os.path.join(self.tmp.name, n) for n in ("game", "named"))
        os.makedirs(self.game)

    def tearDown(self):
        self.tmp.cleanup()

    def test_the_sequels_page(self):
        """Its saves copied under their names (one page: "Page 1 slot NN"); the quick saves' page left
        out; Shattered Lands' tests don't take a sequel's save, nor its a Shattered Lands' one."""
        for name, title in (("SAVE01.SAV", "AFTER AMBUSH"), ("SAVE03.SAV", "AT THE ROOST"), ("SAVQ01.SAV", "Quick")):
            with open(os.path.join(self.game, name), "wb") as f:
                f.write(save_file(title, ravager.GAME_SHEET_SIZE if name == "SAVE03.SAV" else ravager.SHEET_SIZE))
        made = namedsaves.sync(self.game, self.named, wotr=True)
        self.assertEqual(sorted(made), ["Page 1 slot 01 - AFTER AMBUSH.SAV", "Page 1 slot 03 - AT THE ROOST.SAV"])
        self.assertEqual(namedsaves.sync(self.game, self.named), [])  # (as Shattered Lands': none)
        self.assertIsNone(namedsaves.save_name(save_file("x")))
        self.assertTrue(namedsaves.is_wotr_save(os.path.join(self.game, "SAVE01.SAV")))

    def test_restore_makes_the_loaders_sheets(self):
        copy = os.path.join(self.tmp.name, "Page 1 slot 03 - OLD.SAV")
        with open(copy, "wb") as f:
            f.write(save_file("OLD", ravager.GAME_SHEET_SIZE))
        with open(os.path.join(self.game, "SAVE04.SAV"), "wb") as f:
            f.write(save_file("THERE"))
        self.assertEqual(namedsaves.restore(copy, self.game, 1, 4, self.named, wotr=True), "OLD")
        chunks = gff.read_gff(open(os.path.join(self.game, "SAVE04.SAV"), "rb").read())
        self.assertEqual(len(chunks[ravager.SHEETS_CHUNK]), 17 * ravager.SHEET_SIZE)
        self.assertTrue(os.path.exists(os.path.join(self.named, "Replaced - Page 1 slot 04 - THERE.SAV")))
        with self.assertRaises(ValueError):
            namedsaves.restore(copy, self.game, 2, 4, self.named, wotr=True)  # (one page)


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class HelperTests(unittest.TestCase):
    """DSCLOG2's QS_KEY, SAVE_TICK and GREQ_LOAD."""
    TSR, GAME_DS, SS = 0x1000, 0x5000, 0x4000
    LOAD = GAME_DS - ravager.DGROUP

    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]

    def setUp(self):
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(self.TSR * 16, self.image)
        mu.mem_write(self.TSR * 16 + 0xFFF0, bytes((0xF4,)))
        self.calls, self.results = [], {"save": 1, "check": 0}
        routines = {"save": (0x46EF, 0x84), "load": (0x4736, 0x20), "open": (0x46E9, 0x52), "close": (0x46E9, 0x57),
                    "check": (0x27ED, 0x64), "delete": (0x27FC, 0x5C5), "write": (0x27FC, 0xE8)}
        for name, (seg, off) in routines.items():
            at = (self.LOAD + seg) * 16 + off
            mu.mem_write(at, b"\xcb")  # RETF
            mu.hook_add(UC_HOOK_CODE, lambda uc, *_, n=name: self.called(uc, n), begin=at, end=at)
        ds = self.GAME_DS * 16
        mu.mem_write(ds + 0x14D7, struct.pack("<HHHH", 0x10, 0x20, 0x300, 0x400))
        mu.mem_write(ds + 0x4458, bytes((0x58, 0x59)))
        mu.mem_write(ds + 0x144A, struct.pack("<HH", 0x1234, 0x5678))
        mu.mem_write(ds + 0x0DAB, struct.pack("<H", 1))
        mu.mem_write(ds + 0x2088, b"E")

    def called(self, uc, name):
        sp = uc.reg_read(r.UC_X86_REG_SS) * 16 + uc.reg_read(r.UC_X86_REG_SP)
        args = struct.unpack("<8H", uc.mem_read(sp + 4, 16))
        if name == "save":
            text = lambda off, seg: bytes(uc.mem_read(seg * 16 + off, 64)).split(b"\0")[0]
            self.calls.append((name, text(*args[0:2]), text(*args[2:4])))
        elif name == "check":
            self.calls.append((name, args[0] | args[1] << 16))
        elif name == "delete":
            self.calls.append((name, struct.pack("<HH", *args[0:2]), args[2] | args[3] << 16))
        elif name == "write":
            data = bytes(uc.mem_read(args[1] * 16 + args[0], 10))
            self.calls.append((name, data[:args[2]], struct.pack("<HH", *args[4:6]), args[6] | args[7] << 16))
        else:
            self.calls.append((name,))
        self.during = self.word("save_req")
        self.letters = self.letters_now()
        uc.reg_write(r.UC_X86_REG_AX, self.results.get(name, 0x7777))
        uc.reg_write(r.UC_X86_REG_BX, 0xDEAD)
        uc.reg_write(r.UC_X86_REG_ES, 0xBEEF)

    def letters_now(self):
        ds = self.GAME_DS * 16
        return bytes(self.mu.mem_read(ds + 0x2088, 1) + self.mu.mem_read(ds + 0x20B9, 1))

    def word(self, name, value=None):
        at = self.TSR * 16 + self.sym[name]
        if value is not None:
            self.mu.mem_write(at, struct.pack("<H", value))
        return struct.unpack("<H", self.mu.mem_read(at, 2))[0]

    def go(self, routine, **regs):
        mu = self.mu
        mu.mem_write(self.SS * 16 + 0x7F0, struct.pack("<H", 0xFFF0))
        for name, value in dict(cs=self.TSR, ds=self.GAME_DS, ss=self.SS, esp=0x7F0, eflags=0x2, **regs).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(self.TSR * 16 + self.sym[routine], self.TSR * 16 + 0xFFF0, count=200000)
        self.assertEqual((mu.reg_read(r.UC_X86_REG_SP), mu.reg_read(r.UC_X86_REG_DS)), (0x7F2, self.GAME_DS))

    def ask(self, request, greq=0):
        off = self.sym["save_text"]
        self.mu.mem_write(self.TSR * 16 + off, b"SAVQ03.SAV".ljust(64, b"\0") + b"Quick - Day 1".ljust(48, b"\0"))
        self.word("save_greq", greq)
        self.word("save_req", request)
        for name, value in (("s_ip", 0x1111), ("s_cs", 0x2222), ("s_fl", 0x0202)):
            self.word(name, value)
        self.go("save_tick")
        self.assertEqual([self.word(n) for n in ("s_ip", "s_cs", "s_fl")], [0x1111, 0x2222, 0x0202])

    def test_header(self):
        """The fields at quicksave's layout (ravlog.QUICK_LAYOUT), past DSCLOG's header and the recent ones."""
        hdr = self.sym["hdr"]
        for name, field in (("qs_keys", LAY.keys), ("qs_seq", LAY.seq), ("save_req", LAY.req), ("save_off", LAY.save_off),
                            ("save_greq", LAY.greq), ("main_ticks", LAY.main_ticks), ("tail_seg", LAY.tail_seg),
                            ("greq_saves", ravlog.QUICK_GREQ_SAVES), ("greq_loads", ravlog.QUICK_GREQ_LOADS)):
            self.assertEqual(self.sym[name] - hdr, field, name)
        self.assertEqual(struct.unpack_from("<HH", self.image, hdr + LAY.keys), (0xFFFF, 0xFFFF))
        tail = self.sym["TAIL_PARAS"] * 16  # (SAVE_TEXT: the tail's, kept with the segment; its offset there)
        self.assertEqual(struct.unpack_from("<H", self.image, hdr + LAY.save_off)[0], self.sym["save_text"] - tail)
        self.assertTrue(tail <= self.sym["save_text"] < self.sym["INSTALL_PARAS"] * 16)
        self.assertLess(self.sym["greq_load"], self.sym["resident_end"])

    def test_save_and_its_greq(self):
        self.ask(q.REQ_SAVE, q.GREQ_QUICK + 3)
        limits = struct.pack("<HHHH", 0x10, 0x20, 0x300, 0x400) + bytes((0x59,))
        self.assertEqual(self.calls, [("save", b"SAVQ03.SAV", b"Quick - Day 1"), ("open",), ("check", 0x56781234),
                                      ("delete", b"GREQ", 103), ("write", limits, b"GREQ", 103), ("close",)])
        self.assertEqual((self.word("save_req"), self.word("greq_saves"), self.word("quick_saves")), (q.DONE, 1, 1))

    def test_save_without_greq(self):
        self.ask(q.REQ_SAVE)
        self.assertEqual(self.calls, [("save", b"SAVQ03.SAV", b"Quick - Day 1")])
        self.assertEqual(self.word("save_req"), q.DONE)

    def test_the_roster_refused(self):
        self.results["check"] = 1
        self.ask(q.REQ_SAVE, 104)
        self.assertEqual([c[0] for c in self.calls], ["save", "open", "check", "close"])

    def test_save_failed(self):
        self.results["save"] = 0x100  # (AL 0: the game's test is of AL)
        self.ask(q.REQ_SAVE, 103)
        self.assertEqual(([c[0] for c in self.calls], self.word("save_req")), (["save"], q.FAILED))

    def test_no_save_in_a_fight(self):
        self.mu.mem_write((self.LOAD + 0x3C10) * 16 + 0x19, struct.pack("<H", 1))
        self.ask(q.REQ_SAVE, 103)
        self.assertEqual((self.calls, self.word("save_req")), ([], q.IN_FIGHT))

    def test_load_window(self):
        """The QUICK page (Q) while F9's LOAD window is up (its routine returns with it up, the screen word 2,
        the main loop running it), the game's (E) at the first pass on the map once it shuts."""
        ds = self.GAME_DS * 16
        self.ask(q.REQ_LOAD)
        self.assertEqual((self.calls, self.during, self.word("save_req")), ([("load",)], 0, q.DONE))
        self.assertEqual((self.letters, self.letters_now()), (b"QQ", b"QQ"))
        self.mu.mem_write(ds + 0x0DAB, struct.pack("<H", 2))
        self.ask(q.DONE)
        self.assertEqual((self.letters_now(), self.word("pages_back")), (b"QQ", 0))
        self.mu.mem_write(ds + 0x0DAB, struct.pack("<H", 1))
        self.ask(q.DONE)
        self.assertEqual((self.letters_now(), self.word("pages_back")), (b"EE", 1))

    def test_page_back(self):
        """The QUICK page left (the Loader's Q written, no load asked): the game's again at the main loop's
        next pass, so F1's SAVE window never opens on it; kept while a quick load waits for its window."""
        ds = self.GAME_DS * 16
        self.mu.mem_write(ds + 0x2088, b"Q")
        self.mu.mem_write(ds + 0x20B9, b"Q")
        self.ask(0)
        self.assertEqual((self.letters_now(), self.word("pages_back")), (b"EE", 1))
        self.ask(0)
        self.assertEqual((self.letters_now(), self.word("pages_back")), (b"EE", 1))
        self.mu.mem_write(ds + 0x2088, b"Q")
        self.word("s_fl", 0x0002)
        self.ask(q.REQ_LOAD)
        self.assertEqual((self.letters, self.letters_now(), self.word("pages_back")), (b"QQ", b"QQ", 1))

    def test_page_kept_off_the_map(self):
        """A window up (the screen word not 1; F9's LOAD window's 2, seen in play): the QUICK page kept."""
        ds = self.GAME_DS * 16
        self.mu.mem_write(ds + 0x2088, b"Q")
        self.mu.mem_write(ds + 0x20B9, b"Q")
        self.mu.mem_write(ds + 0x0DAB, struct.pack("<H", 2))
        self.ask(0)
        self.assertEqual((self.letters_now(), self.word("pages_back")), (b"QQ", 0))
        self.mu.mem_write(ds + 0x0DAB, struct.pack("<H", 1))
        self.ask(0)
        self.assertEqual((self.letters_now(), self.word("pages_back")), (b"EE", 1))

    def test_nothing_asked(self):
        for value in (0, q.DONE, q.FAILED, q.IN_FIGHT):
            self.ask(value)
            self.assertEqual((self.calls, self.word("save_req")), ([], value))

    def key(self, key, age=0, screen=1, loader=0):
        mu = self.mu
        mu.mem_write(0x46C, struct.pack("<H", 500))
        self.word("map_tick", 500 - age)
        self.word("stats_stamp", 500 - loader)
        self.word("pointer_ds", self.GAME_DS)
        mu.mem_write(self.GAME_DS * 16 + 0x0DAB, struct.pack("<H", screen))
        self.go("our_key", eax=key)
        return mu.reg_read(r.UC_X86_REG_EFLAGS) & 1, self.word("qs_seq"), struct.unpack(
            "<H", mu.mem_read(self.TSR * 16 + self.sym["qs_seq"] + 2, 2))[0]

    def test_keys(self):
        self.assertEqual(self.key(q.KEY_SAVE), (0, 0, 0))  # (none set: the game's: its F5, sound effects)
        self.mu.mem_write(self.TSR * 16 + self.sym["qs_keys"], struct.pack("<HH", q.KEY_SAVE, q.KEY_LOAD))
        self.assertEqual(self.key(q.KEY_SAVE), (1, 1, 0))
        self.assertEqual(self.key(q.KEY_LOAD, age=2), (1, 1, 1))
        self.assertEqual(self.key(q.KEY_SAVE, age=3), (0, 1, 1))  # (a window up: the loop not run)
        self.assertEqual(self.key(q.KEY_SAVE, screen=2), (0, 1, 1))  # (not the map)
        self.assertEqual(self.key(q.KEY_SAVE, loader=200), (0, 1, 1))  # (the Loader gone)
        self.assertEqual(self.key(0x1E61), (0, 1, 1))  # (a: the game's)

    def test_greq_load(self):
        """Site 84: "mov ax,es:[2]", 100 more on the quick saves' page."""
        mu = self.mu
        mu.mem_write(0x3000 * 16 + 2, struct.pack("<H", 0))
        for letter, want in ((b"E", 0), (b"Q", 100)):
            mu.mem_write(self.GAME_DS * 16 + 0x2088, letter)
            mu.mem_write(self.SS * 16 + 0x7F0, struct.pack("<HHH", 0xFFF0, self.TSR, 0x2))
            for name, value in dict(cs=self.TSR, ds=self.GAME_DS, ss=self.SS, esp=0x7F0, es=0x3000, eax=0x9999).items():
                mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
            mu.emu_start(self.TSR * 16 + self.sym["greq_load"], self.TSR * 16 + 0xFFF0, count=1000)
            self.assertEqual((mu.reg_read(r.UC_X86_REG_AX), mu.reg_read(r.UC_X86_REG_SP)), (want, 0x7F6), letter)
        self.assertEqual(self.word("greq_loads"), 1)


class PatchTests(unittest.TestCase):
    def test_site(self):
        p = next(p for p in ravager.PATCHES if p.name == "greq_load")
        self.assertEqual((p.offset, p.original.hex(), p.replacement), (0x7DA30, "26a10200", bytes((0xCD, ravager.VEC_SITE, 84, 0x90))))
        src = open(ASM).read()
        self.assertRegex(src, r"\n        dw greq_load +; 84 SITE_GREQ_LOAD")
        scroll = src[src.index("\nprobe_scroll:"):]
        self.assertIn("call save_tick", scroll[:scroll.index("iret")])
        self.assertIn("inc word [cs:main_ticks]", scroll[:scroll.index("iret")])
        ours = src[src.index("\nour_key:"):]
        self.assertIn("call qs_key", ours[:300])

    @unittest.skipUnless(WOTR, "DSUN_WOTR (the sequel's folder) not given")
    def test_the_games_bytes(self):
        """Where DSCLOG2 calls and patches, in the sequel's program: the SAVE window's wrapper (its save
        call, the roster's GREQ written), the load's GREQ read, F2's LOAD window, the selectors' segments
        (the table at file 4B080h, 8 bytes a selector), the two file names and the window's chosen row."""
        with open(os.path.join(WOTR, "DSUN.EXE"), "rb") as f:
            exe = f.read()
        table = 0x4B080
        seg = lambda sel: struct.unpack_from("<H", exe, table + sel)[0]
        self.assertEqual([seg(s) for s in (0x5D8, 0x600, 0x5D0, 0x110, 0x118, 0x2E0, 0x2F8, 0x388)],
                         [0x46EF, 0x4736, 0x46E9, 0x27ED, 0x27FC, 0x3C10, 0x3C4C, 0x3F49])
        self.assertEqual(exe[0x7D84A:0x7D856], bytes.fromhex("9a8400d80583c408b4000bc0"))  # save(file, name); AL
        self.assertEqual(exe[0x7D85F:0x7D86E], bytes.fromhex("9a5200d00566ff364a149a64001001"))  # open, check
        self.assertEqual(exe[0x7D8AA:0x7D8B5], bytes.fromhex("666847524551" "9ac5051801"))  # GREQ taken out
        self.assertEqual(exe[0x7D8C3:0x7D8D9], bytes.fromhex("666847524551666a09168d46ec509ae800180183c410"))
        self.assertEqual(exe[0x7D735:0x7D756], bytes.fromhex("a1d7148946eca1d9148946eea1db148946f0a1dd148946f2a05944"
                                                             "8846f4a05844"))
        self.assertEqual(exe[0x7D8D9:0x7D8DE], bytes.fromhex("9a5700d005"))  # close
        self.assertEqual(exe[0x7DA2B:0x7DA48], bytes.fromhex("b8f8028ec026a1020003c640660fbfc06650666847524551"
                                                             "9aab042801"))
        self.assertEqual(exe[0x79B74:0x79B79], bytes.fromhex("9a20000006"))  # F2: the LOAD window
        self.assertEqual(exe[0x79AFD:0x79B08], bytes.fromhex("b8e0028ec026833e190000"))  # F1: not in a fight
        data = 0x5200 + ravager.DGROUP * 16
        self.assertEqual(exe[data + 0x2085:data + 0x2090], b"SAVE??.SAV\0")
        self.assertEqual(exe[data + 0x20B6:data + 0x20C3], b"SAVE%.2d.SAV\0")
        self.assertEqual(exe[0x7D778:0x7D77B], bytes.fromhex("1e68f2"))  # (the save path, DS:44F2h)
        self.assertEqual(exe[0x7DB1E:0x7DB29], bytes.fromhex("b8f8028ec026833e000009"))  # (the chosen row, 2F8h:0)


if __name__ == "__main__":
    unittest.main()
