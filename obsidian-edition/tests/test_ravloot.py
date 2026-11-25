"""Looting with T, selling with S and the M, U and I keys in Wake of the Ravager (DSCLOG2's LOOT_KEY, SELL_KEY,
MAP_KEY and SHOP_LOOP, site 82; loot.py and sell.py on the sequel's words through ravlog's layout): the
layout's names, the read-only view's item gate, the status names, DSCLOG2's routines run in an emulated CPU
(needs nasm and unicorn, else skipped), and with DSUN_WOTR the sequel's own bytes at every address used."""

import os
import shutil
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import game, icons, itemgate, loot, psiblast, ravager, ravlog, ring, sell  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:
    Uc = None

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASM = os.path.join(HERE, "dos", "dsclog2.asm")
WOTR = os.environ.get("DSUN_WOTR")


class LayoutTests(unittest.TestCase):
    def tearDown(self):
        ravlog.restore_layout()

    def test_the_sequels_words(self):
        sl = (ring.FREE_THINGS, itemgate.FREE_ITEMS, loot.OPEN, loot.STATUS_GONE, game.MONEY_SEG, game.POWER_BYTES,
              dict(game.STATUS_NAMES), icons.fit)
        ravlog.apply_layout()
        for module in (ring, itemgate):
            self.assertEqual((module.FREE_THINGS, module.THINGS_USED, module.FREE_ITEMS, module.REGION),
                             (0x56EF, 0x55C6, 0x5AF3, 0x140C), module.__name__)
        self.assertEqual((loot.OPEN, loot.STATUS_GONE, game.MONEY_SEG, game.POWER_BYTES), (0x05D6, (4, 7), 0x3C13, 2))
        self.assertEqual((game.STATUS_NAMES[5], game.STATUS_NAMES[7]), ("Animated", "Dead"))
        self.assertIsNone(icons.fit(None, 0))  # (no Shattered Lands icons put on the sequel's items)
        ravlog.restore_layout()
        self.assertEqual((ring.FREE_THINGS, itemgate.FREE_ITEMS, loot.OPEN, loot.STATUS_GONE, game.MONEY_SEG,
                          game.POWER_BYTES, game.STATUS_NAMES, icons.fit), sl)
        self.assertEqual(game.STATUS_NAMES[5], "Dead")

    def test_a_power_past_255(self):
        """The sequel's power a word: a power 256 (its low byte 0) is no plain weapon's, nor plain gear."""
        rec = bytearray(ravager.ITEM_SIZE)
        struct.pack_into("<H", rec, 0x10, 0x100)
        self.assertEqual(game.item_power(bytes(rec)), 0)  # (SL's byte)
        ravlog.apply_layout()
        self.assertEqual(game.item_power(bytes(rec)), 0x100)

    def test_blast_names_the_sequels_status(self):
        """psiblast's line for one who can't get them back names the sequel's status (7 Dead, not Petrified)."""
        ravlog.apply_layout()
        self.assertEqual(game.STATUS_NAMES.get(7, "down").lower(), "dead")
        self.assertIn("STATUS_NAMES", open(psiblast.__file__).read())


class GateTests(unittest.TestCase):
    """ReadOnlyGuest's writes inside the writable ranges go through its item gate (as GuestMemory's)."""

    class Gate:
        def __init__(self):
            self.opened = 0

        def covers(self, addr, size):
            return addr == 0x100

        def open(self):
            self.opened += 1

    def test_gate(self):
        from test_ravlog import FakeGuest
        view = ravlog.ReadOnlyGuest(FakeGuest())
        view.item_gate = gate = self.Gate()
        view.writable = [(0x100, 2), (0x200, 2)]
        view.write(0x100, b"\1\2")
        view.write(0x200, b"\3\4")
        view.write(0x300, b"\5\6")
        self.assertEqual((gate.opened, view.guest.writes, view.dropped), (1, 2, 1))


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class HelperTests(unittest.TestCase):
    """DSCLOG2's LOOT_KEY, SELL_KEY, SHOP_LOOP and MAP_KEY."""
    TSR, GAME_DS, SS = 0x1000, 0x5000, 0x4000

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
        mu.mem_write(0x46C, struct.pack("<H", 500))
        self.word("pointer_ds", self.GAME_DS)
        self.word("map_tick", 500)
        self.word("stats_stamp", 500)  # (the Loader passing)
        self.game(0x05D6, 9999)
        self.game(0x0DAB, 1)  # (on the map)

    def word(self, name, value=None):
        at = self.TSR * 16 + self.sym[name]
        if value is not None:
            self.mu.mem_write(at, struct.pack("<H", value))
        return struct.unpack("<H", self.mu.mem_read(at, 2))[0]

    def game(self, at, value, size=2):
        self.mu.mem_write(self.GAME_DS * 16 + at, value.to_bytes(size, "little"))

    def go(self, routine, frame=b"", **regs):
        mu = self.mu
        mu.mem_write(self.SS * 16 + 0x7F0, struct.pack("<H", 0xFFF0) + frame)
        for name, value in dict(cs=self.TSR, ds=self.GAME_DS, ss=self.SS, esp=0x7F0, eflags=0x2, **regs).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(self.TSR * 16 + self.sym[routine], self.TSR * 16 + 0xFFF0, count=100000)
        return mu.reg_read(r.UC_X86_REG_AX)

    def key(self, key, read=1):
        self.mu.mem_write(self.TSR * 16 + self.sym["mk_read"], bytes((read,)))
        return self.go("our_key", eax=key)

    def test_header(self):
        """DSCLOG's offsets (loot.py's and sell.py's TSR_ fields)."""
        hdr = self.sym["hdr"]
        for name, field in (("loot_seq", loot.TSR_LOOT_SEQ), ("loot_thing", loot.TSR_LOOT_THING),
                            ("loot_mode", loot.TSR_LOOT_MODE), ("sell_seq", sell.TSR_SELL_SEQ),
                            ("sell_member", sell.TSR_SELL_MEMBER), ("sell_merchant", sell.TSR_SELL_MERCHANT),
                            ("shop_at", sell.TSR_SHOP_AT)):
            self.assertEqual(self.sym[name] - hdr, field, name)
        self.assertEqual(struct.unpack_from("<H", self.image, hdr + loot.TSR_LOOT_THING)[0], 0xFFFF)
        for name in ("loot_key", "sell_key", "shop_loop", "map_key", "mk_read", "overhead"):
            self.assertLess(self.sym[name], self.sym["resident_end"], name)

    def test_loot_key(self):
        self.assertEqual(self.key(0x1474), 0x1474)  # (no window: the game's T)
        self.game(0x05D6, 300)
        self.assertEqual((self.key(0x1474, read=0), self.word("loot_seq")), (0x011B, 0))  # (a peek: not counted)
        self.assertEqual((self.key(0x1474), self.word("loot_seq"), self.word("loot_thing"), self.word("loot_mode")),
                         (0x011B, 1, 300, 0))
        self.assertEqual((self.key(0x1454), self.word("loot_seq")), (0x1454, 1))  # (one pending: the game's key)
        self.word("loot_thing", 0xFFFF)
        self.mu.mem_write(0x417, bytes((2,)))  # (left Shift)
        self.assertEqual((self.key(0x1474), self.word("loot_seq"), self.word("loot_mode")), (0x011B, 2, 1))
        self.word("loot_thing", 0xFFFF)
        self.word("stats_stamp", 100)  # (no Loader: the game's T, the window kept)
        self.assertEqual((self.key(0x1474), self.word("loot_seq")), (0x1474, 2))

    def test_shop_loop_and_sell_key(self):
        self.game(0x143D, 1, 1)
        self.game(0x1A30, 33)
        self.mu.mem_write((self.GAME_DS + 0x3E71 - 0x47E0) * 16 + 0x0B44, struct.pack("<H", 2))
        self.assertEqual(self.key(0x1F73), 0x1F73)  # (no shop's loop yet: the game's S)
        self.go("shop_loop", frame=struct.pack("<HH", self.TSR, 0x0202))
        self.assertEqual((self.word("shop_at"), self.word("shop_passes")), (500, 1))
        flags = struct.unpack("<H", self.mu.mem_read(self.SS * 16 + 0x7F4, 2))[0]
        self.assertEqual(flags & 0x40, 0x40)  # (ZF: the loop goes on, byte [143Dh] 1)
        self.word("stats_stamp", 100)  # (no Loader: the game's S, the shop kept)
        self.assertEqual((self.key(0x1F73), self.word("sell_seq")), (0x1F73, 0))
        self.word("stats_stamp", 500)
        self.assertEqual((self.key(0x1F73, read=0), self.word("sell_seq")), (0x011B, 0))
        self.assertEqual((self.key(0x1F53), self.word("sell_seq"), self.word("sell_member"), self.word("sell_merchant"),
                          self.word("shop_at")), (0x011B, 1, 2, 33, 0))
        self.assertEqual(self.key(0x1F73), 0x1F73)  # (shut: the next S is the game's)
        self.game(0x143D, 0, 1)
        self.go("shop_loop", frame=struct.pack("<HH", self.TSR, 0x0242))
        flags = struct.unpack("<H", self.mu.mem_read(self.SS * 16 + 0x7F4, 2))[0]
        self.assertEqual((flags & 0x40, self.word("shop_at")), (0, 0))  # (ZF clear: the loop ends; no stamp)
        self.mu.mem_write(0x46C, struct.pack("<H", 503))
        self.word("shop_at", 500)
        self.assertEqual(self.key(0x1F73), 0x1F73)  # (the loop not run for 3 ticks: no shop)

    def test_map_key(self):
        def mk(key, read=1):
            self.mu.mem_write(self.TSR * 16 + self.sym["mk_read"], bytes((read,)))
            return self.go("map_key", eax=key)
        self.assertEqual(mk(0x326D, read=0), 0x186F)  # (M on the map: O, the overhead map)
        self.assertEqual(self.mu.mem_read(self.TSR * 16 + self.sym["overhead"], 1), b"\0")
        self.assertEqual(mk(0x326D), 0x186F)
        self.assertEqual(self.mu.mem_read(self.TSR * 16 + self.sym["overhead"], 1), b"m")
        self.mu.mem_write(0x46C, struct.pack("<H", 510))  # (the map's loop not run since: the map up)
        self.assertEqual(mk(0x324D), 0x011B)  # (M again: Escape)
        self.assertEqual(mk(0x1675), 0x1675)  # (U on the overhead map: the game's)
        self.mu.mem_write(0x46C, struct.pack("<H", 500))
        self.assertEqual(mk(0x1769), 0x1769)  # (I on the map: the game's, OVERHEAD 'i')
        self.mu.mem_write(0x46C, struct.pack("<H", 510))
        self.assertEqual(mk(0x1769), 0x011B)  # (I on the inventory: Escape)
        self.assertEqual(mk(0x1675), 0x1675)  # (U there: the game switches; OVERHEAD 'u')
        self.assertEqual(mk(0x1675), 0x011B)


class PatchTests(unittest.TestCase):
    def test_site(self):
        p = next(p for p in ravager.PATCHES if p.name == "shop_loop")
        self.assertEqual((p.offset, p.original.hex(), p.replacement),
                         (0x88D99, "803e3d1401", bytes((0xCD, ravager.VEC_SITE, 82, 0x90, 0x90))))
        src = open(ASM).read()
        self.assertRegex(src, r"\n        dw shop_loop +; 82 SITE_SHOP_LOOP")
        int16 = src[src.index("\nint16:"):]
        self.assertEqual(int16[:int16.index("\nour_key:")].count("call map_key"), 2)  # (a peek and a read)
        ours = src[src.index("\nour_key:"):]
        self.assertLess(ours.index("call loot_key"), ours.index("call qs_key"))
        tick = src[src.index("\npanel_tick:"):]
        self.assertIn("mov byte [cs:overhead], 0", tick[:300])

    @unittest.skipUnless(WOTR, "DSUN_WOTR (the sequel's folder) not given")
    def test_the_games_bytes(self):
        """The sequel's program where the port reads and writes: the shop's loop and its flag, the container's
        window, the allocator's free lists, the item table's size, the money, the status names."""
        with open(os.path.join(WOTR, "DSUN.EXE"), "rb") as f:
            exe = f.read()
        self.assertEqual(exe[0x88D52:0x88D58], bytes.fromhex("558bec83ec18"))  # (the shop's loop)
        self.assertEqual(exe[0x88D99:0x88DA0], bytes.fromhex("803e3d140174ba"))  # (its test, je back)
        self.assertEqual(exe[0x7BCA6:0x7BCAB], bytes.fromhex("c6063d1401"))  # (a merchant's shop: 143Dh 1)
        self.assertEqual(exe[0x7BCAD:0x7BCB3], bytes.fromhex("c706301a0f27"))  # (none: 1A30h 9999)
        self.assertEqual(exe[0x607E8:0x607EE], bytes.fromhex("c706d6050f27"))  # (the container's window shut)
        self.assertEqual(exe[0x23234:0x23237], bytes.fromhex("68ef56"))  # (the free things' list)
        self.assertEqual(exe[0x23252:0x23256], bytes.fromhex("ff06c655"))  # (... and the count out)
        self.assertEqual(exe[0x2349C:0x2349F], bytes.fromhex("a3f35a"))  # (the free item records)
        self.assertEqual(exe[0x72FF7:0x72FFD], bytes.fromhex("6668f0230000"))  # (400 item records of 17h bytes)
        self.assertEqual(exe[0x91021:0x91026], bytes.fromhex("6626a15703"))  # (the money, 2E8h:357h)
        self.assertEqual(struct.unpack_from("<H", exe, 0x4B080 + 0x2E8)[0], 0x3C13)
        data = 0x5200 + ravager.DGROUP * 16
        names = []
        for n in range(9):
            off, = struct.unpack_from("<H", exe, data + 0x1463 + 4 * n)
            names.append(exe[data + off:data + off + 12].split(b"\0")[0].decode())
        ravlog.apply_layout()
        try:
            self.assertEqual(names, [game.STATUS_NAMES[n] for n in range(9)])
        finally:
            ravlog.restore_layout()


if __name__ == "__main__":
    unittest.main()
