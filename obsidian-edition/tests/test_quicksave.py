"""Quick save, quick load and autosave (quicksave.py): the slots' rotation, the names, when an
autosave is due, what is asked of DSCLOG and what is said; and DSCLOG's side run in a CPU
emulator (needs unicorn and nasm): QS_KEY counting the two keys on the map only, SAVE_TICK calling
the game's save with the Loader's file and name, refusing in a fight, opening the LOAD window."""

import os
import shutil
import struct
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import quicksave as q  # noqa: E402
from test_dsclog_drawing import GAME_DS, SS, TICK, TSR, Scene, Uc  # noqa: E402

try:
    from unicorn import UC_HOOK_CODE
    from unicorn import x86_const as r
except ImportError:  # optional dependency
    pass

HDR, DS, TAIL_SEG, SAVE_OFF = 0x20000, 0x3000, 0x2800, 0x100


class Guest:
    def __init__(self):
        self.m = bytearray(0x100000)

    def read(self, at, n):
        return bytes(self.m[at:at + n])

    def write(self, at, data):
        self.m[at:at + len(data)] = data


class Game:
    """What quicksave.py asks of GameData."""

    def __init__(self):
        self.guest, self.ds = Guest(), DS
        self.area, self.fight, self.clock = 0x29, False, 86400 * 46 + 14 * 3600 + 20 * 60
        self.camp = False
        struct.pack_into("<H", self.guest.m, HDR + q.TSR_TAIL_SEG, TAIL_SEG)
        struct.pack_into("<H", self.guest.m, HDR + q.TSR_SAVE_OFF, SAVE_OFF)
        struct.pack_into("<HH", self.guest.m, HDR + q.TSR_QS_KEYS, 0xFFFF, 0xFFFF)
        struct.pack_into("<H", self.guest.m, DS * 16 + q.SCREEN_IS, q.ON_MAP)

    def creature(self, n):
        return bytes(0x1D) + bytes((4 if self.camp else 1,)) + bytes(28)

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


class SlotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.game = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, slot, stamp, folder=None):
        path = os.path.join(folder or self.game, q.slot_file(slot))
        with open(path, "wb") as f:
            f.write(b"save")
        os.utime(path, (stamp, stamp))

    def test_files(self):
        self.assertEqual((q.slot_file(1), q.slot_file(10)), ("SAVQ01.SAV", "SAVQ10.SAV"))
        self.assertEqual(set(q.QUICK_SLOTS) & set(q.AUTO_SLOTS), set())  # (neither pushes the other out)
        self.assertEqual(sorted(q.QUICK_SLOTS + q.AUTO_SLOTS), list(range(1, 11)))

    def test_first_empty_then_oldest(self):
        self.assertEqual(q.next_slot(self.game, q.QUICK_SLOTS), 1)
        self.put(1, 500)
        self.put(2, 400)
        self.assertEqual(q.next_slot(self.game, q.QUICK_SLOTS), 3)
        for slot, stamp in ((3, 300), (4, 900), (5, 800)):
            self.put(slot, stamp)
        self.assertEqual(q.next_slot(self.game, q.QUICK_SLOTS), 3)  # (the oldest)
        self.put(3, 1000)
        self.assertEqual(q.next_slot(self.game, q.QUICK_SLOTS), 2)
        self.assertEqual(q.next_slot(self.game, q.AUTO_SLOTS), 6)  # (its own slots: all empty)
        self.put(7, 50)
        self.assertEqual(q.next_slot(self.game, q.AUTO_SLOTS), 6)

    def test_newest_of_both_kinds(self):
        self.assertIsNone(q.newest_slot(self.game))
        self.put(2, 400)
        self.put(8, 900)
        self.put(4, 700)
        self.assertEqual(q.newest_slot(self.game), 8)

    def test_cloud_saves_over_the_game_folder(self):
        """GOG's DOSBox mounts cloud_saves over the game folder: a slot's save is there first."""
        cloud = os.path.join(self.game, "cloud_saves")
        os.makedirs(cloud)
        self.put(1, 100)  # (an old one in the game folder)
        self.put(1, 900, cloud)
        self.put(2, 500, cloud)
        self.assertEqual(q.slot_path(self.game, 1), os.path.join(cloud, "SAVQ01.SAV"))
        self.assertEqual(q.next_slot(self.game, (1, 2)), 2)

    def test_names(self):
        clock = 86400 * 46 + 14 * 3600 + 20 * 60
        self.assertEqual(q.quick_name(clock), "Quick - Day 47, 14:20")
        self.assertEqual(q.quick_name(None), "Quick")
        self.assertEqual(q.auto_name("The slave pens", clock), "Auto - Day 47, 14:20 - The slave pens")
        self.assertEqual(q.auto_name("after a fight", clock), "Auto - Day 47, 14:20 - after a fight")
        long = q.auto_name("A very long name of an area that goes on", 86400 * 1234 + 5)
        self.assertLessEqual(len(long), q.NAME_MOST)
        self.assertTrue(long.startswith("Auto - Day 1235, 00:00 - A very long"), long)


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        self.gd, self.qs, self.now, self.ticks = Game(), q.QuickSave(), 100.0, 0
        self.free = mock.patch.object(q, "disk_free", return_value=500 * 1024 * 1024)
        self.free.start()

    def tearDown(self):
        self.free.stop()
        self.tmp.cleanup()

    def tick(self, seconds=1.0, running=True, loading=False):
        """A pass SECONDS later, the map's main loop having run meanwhile (or not)."""
        self.now += seconds
        if running:
            self.ticks += 7
            self.gd.hdr(q.TSR_MAIN_TICKS, self.ticks)
        return self.qs.tick(self.gd, HDR, self.dir, loading, self.now)

    def press(self, which):
        self.gd.hdr(q.TSR_QS_SEQ + 2 * which, self.gd.hdr(q.TSR_QS_SEQ + 2 * which) + 1)

    def asked(self):
        """(SAVE_REQ, the file, the name) as written for DSCLOG."""
        text = self.gd.guest.read(TAIL_SEG * 16 + SAVE_OFF, q.SAVE_FILE + q.SAVE_NAME)
        return (self.gd.hdr(q.TSR_SAVE_REQ), text[:q.SAVE_FILE].split(b"\0")[0].decode(),
                text[q.SAVE_FILE:].split(b"\0")[0].decode())

    def answer(self, value):
        self.gd.hdr(q.TSR_SAVE_REQ, value)

    def test_keys_are_the_loaders_to_set(self):
        self.tick()
        self.assertEqual((self.gd.hdr(q.TSR_QS_KEYS), self.gd.hdr(q.TSR_QS_KEYS + 2)), (q.KEY_SAVE, q.KEY_LOAD))
        self.qs.keys = False  # (the switch off: the keys stay the game's)
        self.tick()
        self.assertEqual((self.gd.hdr(q.TSR_QS_KEYS), self.gd.hdr(q.TSR_QS_KEYS + 2)), (q.NO_KEY, q.NO_KEY))
        self.press(0)
        self.assertEqual(self.tick(), [])
        self.assertEqual(self.gd.hdr(q.TSR_SAVE_REQ), 0)

    def test_camping_leaves_the_keys_to_the_game(self):
        """The party in the game's camp (its F9 breaks it): the keys the game's, and no autosave."""
        self.tick()
        self.gd.camp = True
        self.gd.area = 0x2A
        for _ in range(8):
            self.tick()
        self.assertEqual((self.gd.hdr(q.TSR_QS_KEYS), self.gd.hdr(q.TSR_QS_KEYS + 2)), (q.NO_KEY, q.NO_KEY))
        self.assertEqual(self.gd.hdr(q.TSR_SAVE_REQ), 0)
        self.gd.camp = False
        self.tick()
        self.assertEqual((self.gd.hdr(q.TSR_QS_KEYS), self.gd.hdr(q.TSR_QS_KEYS + 2)), (q.KEY_SAVE, q.KEY_LOAD))

    def test_quick_save(self):
        self.gd.hdr(q.TSR_QS_SEQ, 41)  # (pressed before the Loader came: not acted on)
        self.assertEqual(self.tick(), [])
        self.assertEqual(self.gd.hdr(q.TSR_SAVE_REQ), 0)
        self.press(0)
        self.assertEqual(self.tick(), [])
        self.assertEqual(self.asked(), (q.REQ_SAVE, "SAVQ01.SAV", "Quick - Day 47, 14:20"))
        self.answer(0)  # (DSCLOG at it)
        self.assertEqual(self.tick(), [])
        self.answer(q.DONE)
        self.assertEqual(self.tick(), ['Quick save: "Quick - Day 47, 14:20" (the QUICK page, slot 1)'])
        self.assertEqual((self.gd.hdr(q.TSR_SAVE_REQ), self.qs.label), (0, "Quick save"))
        self.assertEqual(self.tick(), [])  # (once)

    def test_the_games_save_path_goes_before_the_file(self):
        self.gd.guest.write(DS * 16 + q.SAVE_PATH, b"C:\\SAVES\\\0")
        self.tick()
        self.press(0)
        self.tick()
        self.assertEqual(self.asked()[1], "C:\\SAVES\\SAVQ01.SAV")
        self.answer(q.DONE)
        self.tick()
        self.gd.guest.write(DS * 16 + q.SAVE_PATH, b"C:\\" + b"A" * 55 + b"\\\0")  # (too long for SAVE_TEXT)
        self.gd.guest.write(TAIL_SEG * 16 + SAVE_OFF, bytes(q.SAVE_FILE + q.SAVE_NAME))
        self.press(0)
        self.assertIn("too long a name", self.tick()[0])
        self.assertEqual(self.asked(), (0, "", ""))

    def test_quick_save_refused(self):
        self.tick()
        self.gd.fight = True
        self.press(0)
        self.assertEqual(self.tick(), ["Quick save: not in a fight (the game saves none there)"])
        self.assertEqual(self.gd.hdr(q.TSR_SAVE_REQ), 0)  # (not asked)
        self.gd.fight = False
        self.press(0)
        self.tick()
        self.answer(q.IN_FIGHT)  # (a fight begun before DSCLOG came to it)
        self.assertEqual(self.tick(), ["Quick save: not in a fight (the game saves none there)"])
        self.press(0)
        self.tick()
        self.answer(q.FAILED)
        self.assertEqual(self.tick(), ["Quick save: the game could not write SAVQ01.SAV"])
        self.assertIsNone(self.qs.label)

    def test_a_request_never_taken_is_given_up(self):
        """A window opened between the key and the request: the map's loop doesn't run, DSCLOG never
        takes it; the request is withdrawn, so it isn't carried out unseen later."""
        self.tick()
        self.press(0)
        self.tick()
        self.assertEqual(self.tick(q.ANSWER_WAIT - 2), [])
        self.assertEqual(self.tick(3), ["Quick save: not made, the game was busy"])
        self.assertEqual(self.gd.hdr(q.TSR_SAVE_REQ), 0)

    def test_rotation(self):
        self.tick()
        for n in range(7):
            self.press(0)
            self.tick()
            slot = int(self.asked()[1][4:6])
            self.assertEqual(slot, n % 5 + 1)
            path = os.path.join(self.dir, q.slot_file(slot))
            with open(path, "wb") as f:
                f.write(b"x")
            os.utime(path, (1000 + n, 1000 + n))
            self.answer(q.DONE)
            self.tick()

    def test_quick_load(self):
        self.tick()
        self.press(1)
        self.assertEqual(self.tick(), ["Quick load: no quick save or autosave yet"])
        self.assertEqual(self.gd.hdr(q.TSR_SAVE_REQ), 0)
        for slot, stamp in ((2, 500), (7, 900)):
            path = os.path.join(self.dir, q.slot_file(slot))
            with open(path, "wb") as f:
                f.write(b"x")
            os.utime(path, (stamp, stamp))
        self.gd.guest.write(DS * 16 + 0x1DCF, b"SAVE??.SAV\0SAVE%.2d.SAV\0")
        self.press(1)
        self.assertEqual(self.tick(), [])
        self.assertEqual(self.gd.hdr(q.TSR_SAVE_REQ), q.REQ_LOAD)
        self.assertEqual(self.gd.guest.read(DS * 16 + 0x1DCF, 24), b"SAVQ??.SAV\0SAVQ%.2d.SAV\0")  # (the page)
        row = struct.unpack("<H", self.gd.guest.read((DS - q.WINDOW_FROM_DS) * 16 + q.CHOSEN, 2))[0]
        self.assertEqual(row, 6)  # (slot 7: the newest)
        self.answer(q.DONE)
        self.assertEqual(self.tick(), [])
        self.assertEqual(self.gd.hdr(q.TSR_SAVE_REQ), 0)

    def page(self, letter=None):
        if letter is not None:
            for at in (q.NAME_FIND, q.NAME_SAVE):
                self.gd.guest.write(DS * 16 + at, letter)
        return self.gd.guest.read(DS * 16 + q.NAME_FIND, 1) + self.gd.guest.read(DS * 16 + q.NAME_SAVE, 1)

    def test_the_window_never_opens_on_the_quick_page(self):
        """A save made by hand on the QUICK page would be written over in turn: with the window shut
        the page goes back to the one of pages 1 to 4 shown last; while the window is up (the map's
        loop not running, DS:0BC9h 2) the QUICK page stays, for looking and loading."""
        self.page(b"C")
        self.tick()
        self.tick()
        self.assertEqual(self.page(), b"CC")
        self.page(b"Q")  # (F9's window, or the QUICK button clicked)
        struct.pack_into("<H", self.gd.guest.m, DS * 16 + q.SCREEN_IS, 2)
        for _ in range(3):
            self.tick(running=False)
        self.assertEqual(self.page(), b"QQ")  # (the window up: left alone)
        struct.pack_into("<H", self.gd.guest.m, DS * 16 + q.SCREEN_IS, q.ON_MAP)
        self.tick()
        self.assertEqual(self.page(), b"CC")  # (shut: the next SAVE window opens on page 3)
        # a game started on the QUICK page with nothing seen before: page 1
        self.qs = q.QuickSave()
        self.page(b"Q")
        self.tick()
        self.tick()
        self.assertEqual(self.page(), b"EE")
        # ... and not while a request is with DSCLOG (F9's: the page just made QUICK for it)
        path = os.path.join(self.dir, q.slot_file(1))
        with open(path, "wb") as f:
            f.write(b"x")
        self.press(1)
        self.tick()
        self.assertEqual((self.gd.hdr(q.TSR_SAVE_REQ), self.page()), (q.REQ_LOAD, b"QQ"))
        self.tick()
        self.assertEqual(self.page(), b"QQ")

    def test_autosave_in_a_new_area(self):
        self.assertEqual(self.tick(), [])  # (the first look: where the party is, no save)
        self.tick(30)
        self.assertEqual(self.gd.hdr(q.TSR_SAVE_REQ), 0)
        self.gd.area = 0x2A
        self.tick()
        self.tick(q.AREA_WAIT - 1.5)
        self.assertEqual(self.gd.hdr(q.TSR_SAVE_REQ), 0)  # (not yet: the area settling)
        self.tick(2)
        self.assertEqual(self.asked(), (q.REQ_SAVE, "SAVQ06.SAV", "Auto - Day 47, 14:20 - The arena"))
        self.answer(q.DONE)
        self.assertEqual(self.tick(), ['Autosave: "Auto - Day 47, 14:20 - The arena" (the QUICK page, slot 6)'])
        self.assertEqual(self.qs.label, "Autosave")
        self.tick(30)
        self.assertEqual(self.gd.hdr(q.TSR_SAVE_REQ), 0)  # (once for the area)

    def test_no_autosave_while_the_map_is_away(self):
        """A talk, a screen or a window up as the party comes in (the main loop not running, or the
        game not on the map): the wait starts when the map is back."""
        self.tick()
        self.gd.area = 0x2A
        for _ in range(10):
            self.tick(running=False)
        self.assertEqual(self.gd.hdr(q.TSR_SAVE_REQ), 0)
        struct.pack_into("<H", self.gd.guest.m, DS * 16 + q.SCREEN_IS, 2)
        for _ in range(10):
            self.tick()
        self.assertEqual(self.gd.hdr(q.TSR_SAVE_REQ), 0)
        struct.pack_into("<H", self.gd.guest.m, DS * 16 + q.SCREEN_IS, q.ON_MAP)
        self.tick()
        self.tick(q.AREA_WAIT)
        self.assertEqual(self.gd.hdr(q.TSR_SAVE_REQ), q.REQ_SAVE)

    def test_no_autosave_for_a_game_loaded(self):
        """A save of another area loaded: the dice log says a game is loading; where it is becomes
        where the party is, with no save."""
        self.tick()
        self.gd.area = 0x2A
        self.tick(loading=True)
        for _ in range(10):
            self.tick()
        self.assertEqual(self.gd.hdr(q.TSR_SAVE_REQ), 0)

    def test_autosave_after_a_fight(self):
        self.tick()
        self.gd.fight = True
        self.tick(20)
        self.gd.fight = False
        self.tick()
        self.gd.fight = True  # (the arena's next wave, before the wait is up)
        self.tick(2)
        self.gd.fight = False
        self.tick()
        self.tick(q.FIGHT_WAIT - 1)
        self.assertEqual(self.gd.hdr(q.TSR_SAVE_REQ), 0)
        self.tick(1.5)
        self.assertEqual(self.asked(), (q.REQ_SAVE, "SAVQ06.SAV", "Auto - Day 47, 14:20 - after a fight"))
        self.answer(q.DONE)
        self.tick()
        # another fight over within AUTO_GAP of that save: none
        self.gd.fight = True
        self.tick(5)
        self.gd.fight = False
        self.tick()
        self.tick(q.FIGHT_WAIT + 1)
        self.assertEqual(self.gd.hdr(q.TSR_SAVE_REQ), 0)
        # ... and one after it
        self.tick(q.AUTO_GAP)
        self.gd.fight = True
        self.tick(5)
        self.gd.fight = False
        self.tick()
        self.tick(q.FIGHT_WAIT + 1)
        self.assertEqual(self.gd.hdr(q.TSR_SAVE_REQ), q.REQ_SAVE)

    def test_autosave_switched_off(self):
        self.qs.auto = False
        self.tick()
        self.gd.area = 0x2A
        for _ in range(10):
            self.tick()
        self.assertEqual(self.gd.hdr(q.TSR_SAVE_REQ), 0)
        self.press(0)  # (the keys are another switch)
        self.tick()
        self.assertEqual(self.gd.hdr(q.TSR_SAVE_REQ), q.REQ_SAVE)

    def test_disk_nearly_full(self):
        """No save asked for (the game's "Disk Space Low !!!" box would stop the game for a click):
        a quick save says so each time, an autosave once."""
        self.tick()
        with mock.patch.object(q, "disk_free", return_value=100 * 1024):
            self.press(0)
            self.assertEqual(self.tick(), ["No quick save or autosave: the disk is nearly full (100 KB free)"])
            self.press(0)
            self.assertEqual(len(self.tick()), 1)
            self.gd.area = 0x2A
            self.tick()
            self.assertEqual(self.tick(q.AREA_WAIT), [])  # (said already)
            self.assertEqual(self.gd.hdr(q.TSR_SAVE_REQ), 0)

    def test_a_new_dsclog_starts_again(self):
        self.tick()
        self.press(0)
        self.tick()
        self.assertEqual(self.gd.hdr(q.TSR_SAVE_REQ), q.REQ_SAVE)
        other = HDR + 0x1000  # (the game started again: the helper elsewhere, its counts from 0)
        struct.pack_into("<H", self.gd.guest.m, other + q.TSR_TAIL_SEG, TAIL_SEG)
        self.assertEqual(self.qs.tick(self.gd, other, self.dir, False, self.now + 1), [])
        self.assertEqual(struct.unpack_from("<H", self.gd.guest.m, other + q.TSR_SAVE_REQ)[0], 0)
        self.assertEqual(struct.unpack_from("<HH", self.gd.guest.m, other + q.TSR_QS_KEYS), (q.KEY_SAVE, q.KEY_LOAD))


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class HelperTests(unittest.TestCase):
    """DSCLOG's QS_KEY and SAVE_TICK."""

    SAVE = ((GAME_DS - 0x4356 + 0x4242) & 0xFFFF, 0x0089)
    LOADW = ((GAME_DS - 0x4356 + 0x428A) & 0xFFFF, 0x0020)
    FIGHT = ((GAME_DS - (0x4356 - 0x377E)) & 0xFFFF) * 16 + 0x19

    def setUp(self):
        self.scene = scene = Scene()
        self.hdr = scene.sym["hdr"]
        self.calls = []
        self.result = 1
        mu = scene.mu
        for name, (seg, off) in (("save", self.SAVE), ("load", self.LOADW)):
            mu.mem_write(seg * 16 + off, b"\xcb")  # RETF
            mu.hook_add(UC_HOOK_CODE, lambda uc, *_, n=name: self.called(uc, n), begin=seg * 16 + off, end=seg * 16 + off)

    def called(self, uc, name):
        sp = uc.reg_read(r.UC_X86_REG_SS) * 16 + uc.reg_read(r.UC_X86_REG_SP)
        args = struct.unpack("<HHHH", uc.mem_read(sp + 4, 8))
        text = lambda off, seg: bytes(uc.mem_read(seg * 16 + off, 64)).split(b"\0")[0]
        self.calls.append((name, text(*args[:2]), text(*args[2:])) if name == "save" else (name,))
        self.during = self.req()  # (SAVE_REQ while the game's routine runs)
        uc.reg_write(r.UC_X86_REG_AX, self.result)
        uc.reg_write(r.UC_X86_REG_BX, 0xDEAD)  # (the game's routines keep neither BX nor ES)
        uc.reg_write(r.UC_X86_REG_ES, 0xBEEF)
        self.ran_in = uc.reg_read(r.UC_X86_REG_GS)  # (GS under the game's routine: DSCLOG's segment, SAVE_FAR's)
        uc.reg_write(r.UC_X86_REG_GS, 0x6666)  # (... and nothing says the game, or a handler under it, keeps GS)

    def field(self, field, n=2):
        return bytes(self.scene.mu.mem_read(TSR * 16 + self.hdr + field, n))

    def req(self, value=None):
        if value is not None:
            self.scene.mu.mem_write(TSR * 16 + self.hdr + q.TSR_SAVE_REQ, struct.pack("<H", value))
        return struct.unpack("<H", self.field(q.TSR_SAVE_REQ))[0]

    def write_text(self, file, name):
        tail, off = struct.unpack("<H", self.field(q.TSR_TAIL_SEG))[0], struct.unpack("<H", self.field(q.TSR_SAVE_OFF))[0]
        self.scene.mu.mem_write(tail * 16 + off, file.ljust(q.SAVE_FILE, b"\0") + name.ljust(q.SAVE_NAME, b"\0"))

    def tick(self):
        self.scene.call("save_tick", esi=0x1111, edi=0x2222, gs=0x7777)
        mu = self.scene.mu
        self.assertEqual([mu.reg_read(x) for x in (r.UC_X86_REG_SI, r.UC_X86_REG_DI, r.UC_X86_REG_DS, r.UC_X86_REG_SP,
                                                   r.UC_X86_REG_GS)],
                         [0x1111, 0x2222, GAME_DS, 0x7F2, 0x7777])  # (GS the caller's again: TAIL_CALL)

    def test_the_work_is_in_the_tail(self):
        """SAVE_TICK in the segment is a test and a call: its work (SAVE_FAR) and TINT_PASS's
        (TINT_FAR) are code in the tail, past the segment's 64 KB, run through TAIL_CALL with GS
        DSCLOG's segment; the answer is written to DSCLOG's SAVE_REQ though the game's routine
        changed GS."""
        import test_header_offsets
        sym = test_header_offsets.symbols()
        tail_paras = struct.unpack_from("<H", self.scene.image, self.hdr + 1836)[0]
        tail_len = len(self.scene.image) - tail_paras * 16
        for name in ("save_far", "tint_far"):
            self.assertLess(sym[name], tail_len, name)  # (an offset in the tail)
            self.assertNotIn(name, self.scene.sym)  # (not a label of the segment's)
        self.assertEqual(tail_len % 16, 0)  # (KEPT_PARAS counts whole paragraphs: the code's end is kept)
        self.assertLess(self.scene.sym["tail_call"] - self.scene.sym["save_tick"], 0x20)  # (the stub is short)
        self.write_text(b"SAVQ01.SAV", b"x")
        self.req(q.REQ_SAVE)
        self.tick()
        self.assertEqual(self.ran_in, TSR)
        self.assertEqual(self.req(), q.DONE)

    def test_header(self):
        """The fields where quicksave.py reads them; no key until the Loader sets them; SAVE_TEXT
        in the tail with room for the file and the name."""
        self.assertEqual(self.field(q.TSR_QS_KEYS, 12)[:10], struct.pack("<HHHHH", 0xFFFF, 0xFFFF, 0, 0, 0))
        tail = self.scene.image[struct.unpack_from("<H", self.scene.image, self.hdr + 1836)[0] * 16:]
        off, = struct.unpack("<H", self.field(q.TSR_SAVE_OFF))
        self.assertEqual(tail[off:off + q.SAVE_FILE + q.SAVE_NAME], bytes(q.SAVE_FILE + q.SAVE_NAME))
        self.assertLessEqual(off + q.SAVE_FILE + q.SAVE_NAME, len(tail))

    def test_nothing_asked(self):
        for value in (0, q.DONE, q.FAILED, q.IN_FIGHT, 77):  # (none, or an answer the Loader hasn't read)
            self.req(value)
            self.tick()
            self.assertEqual((self.req(), self.calls), (value, []))

    def test_save(self):
        self.write_text(b"C:\\DS\\SAVQ03.SAV", b"Quick - Day 47, 14:20")
        self.req(q.REQ_SAVE)
        self.tick()
        self.assertEqual(self.calls, [("save", b"C:\\DS\\SAVQ03.SAV", b"Quick - Day 47, 14:20")])
        self.assertEqual((self.during, self.req()), (0, q.DONE))  # (0 while the game's routine ran)
        self.tick()
        self.assertEqual(len(self.calls), 1)  # (once)

    def test_save_failed(self):
        self.result = 0
        self.req(q.REQ_SAVE)
        self.tick()
        self.assertEqual((len(self.calls), self.req()), (1, q.FAILED))

    def test_no_save_in_a_fight(self):
        self.scene.mu.mem_write(self.FIGHT, struct.pack("<H", 1))
        self.req(q.REQ_SAVE)
        self.tick()
        self.assertEqual((self.calls, self.req()), ([], q.IN_FIGHT))

    def test_load_window(self):
        self.scene.mu.mem_write(self.FIGHT, struct.pack("<H", 1))  # (the game lets a game be loaded in a fight)
        self.req(q.REQ_LOAD)
        self.tick()
        self.assertEqual((self.calls, self.during, self.req()), ([("load",)], 0, q.DONE))

    def key(self, key, age=0):
        """QS_KEY for KEY, the map's main loop last run AGE BIOS ticks ago: (CF, AX, the two counts)."""
        scene = self.scene
        scene.word("map_tick", TICK - age)
        scene.call("qs_key", eax=key, ebx=0x3333, es=0x4444)
        mu = scene.mu
        self.assertEqual([mu.reg_read(x) for x in (r.UC_X86_REG_BX, r.UC_X86_REG_ES)], [0x3333, 0x4444])
        return (mu.reg_read(r.UC_X86_REG_EFLAGS) & 1, mu.reg_read(r.UC_X86_REG_AX),
                struct.unpack("<HH", self.field(q.TSR_QS_SEQ, 4)))

    def test_keys(self):
        self.assertEqual(self.key(q.KEY_SAVE), (0, q.KEY_SAVE, (0, 0)))  # (no keys set: the game's)
        self.scene.mu.mem_write(TSR * 16 + self.hdr + q.TSR_QS_KEYS, struct.pack("<HH", q.KEY_SAVE, q.KEY_LOAD))
        self.assertEqual(self.key(q.KEY_SAVE), (1, q.KEY_SAVE, (1, 0)))
        self.assertEqual(self.key(q.KEY_LOAD, age=2), (1, q.KEY_LOAD, (1, 1)))
        self.assertEqual(self.key(q.KEY_SAVE), (1, q.KEY_SAVE, (2, 1)))
        self.assertEqual(self.key(0x4000), (0, 0x4000, (2, 1)))  # (F6: the game's)
        # a window, a talk or a menu up (the map's loop not run lately): the game's keys
        self.assertEqual(self.key(q.KEY_SAVE, age=3), (0, q.KEY_SAVE, (2, 1)))
        self.assertEqual(self.key(q.KEY_LOAD, age=40), (0, q.KEY_LOAD, (2, 1)))

    def test_our_key_takes_them(self):
        """Through OUR_KEY (INT 16h's): taken from the game (CF), and the other keys as before."""
        scene = self.scene
        scene.mu.mem_write(TSR * 16 + self.hdr + q.TSR_QS_KEYS, struct.pack("<HH", q.KEY_SAVE, q.KEY_LOAD))
        scene.word("map_tick", TICK)
        scene.call("our_key", eax=q.KEY_SAVE)
        self.assertEqual(scene.mu.reg_read(r.UC_X86_REG_EFLAGS) & 1, 1)
        scene.call("our_key", eax=0x1E61)  # a
        self.assertEqual(scene.mu.reg_read(r.UC_X86_REG_EFLAGS) & 1, 0)
        self.assertEqual(struct.unpack("<HH", self.field(q.TSR_QS_SEQ, 4)), (1, 0))


if __name__ == "__main__":
    unittest.main()
