"""A lock a thief failed, out of reach till a level is gained, in Wake of the Ravager: DSCLOG2's LOCK_SITE (site
241, at the sequel's thief skill check, 8C7E6h) run in an emulated CPU on LOCK_BARRED as the Loader writes it
(locks.table), and the Loader's side on the sequel's layout (RavDiceLog._locks_pass into the tail at the
header's +2114, locks.identity on the sequel's 25h-byte map things). With both games' files (DSUN_SL,
DSUN_WOTR) the check routine is checked to be Shattered Lands' at the sequel's 8C7CBh. Needs nasm and unicorn
for the helper's part, else skipped."""

import os
import shutil
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import dicelog, game, labels, locks, ravager, ravlog  # noqa: E402
from test_ravkits import ASM  # noqa: E402
from test_ravlog import FakeGuest  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:
    Uc = None

TSR, GDS, SS = 0x1000, 0x6000, 0x7000
TALK = GDS - (0x47E0 - 0x3C13)  # (the talk's segment: the load + 3C13h)
GAME_CS, GAME_IP = 0x5555, 0x1233
HLT = 0xFFF0
FRAME = 0x900  # (the game's BP: the skill check's frame)
LOCK_OFF, LOCK_BARS = 2114, 2116


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class LockSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]
        assert not cls.sym["tail_tables"] <= HLT < cls.sym["tail_mid"]

    def setUp(self):
        mu = self.mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        mu.mem_write(TSR * 16 + HLT, b"\xF4")
        mu.mem_write(0xF5 * 4, struct.pack("<HH", self.sym["site_int"], TSR))

    def header(self, at: int) -> int:
        return struct.unpack("<H", self.mu.mem_read(TSR * 16 + self.sym["hdr"] + at, 2))[0]

    def barred(self, rows) -> None:
        """LOCK_BARRED as the Loader writes it: where the header's +2114 says, in the tail."""
        at = TSR * 16 + self.sym["TAIL_PARAS"] * 16 + self.header(LOCK_OFF)
        self.mu.mem_write(at, locks.table(rows))

    def check(self, member: int, skill: int, chance: int = 55, region: int = 0x32, thing: int = 140) -> int:
        """The thief skill check reaching site 241 ("mov [bp-2],ax" made INT F5h, 241): [BP-2] after it."""
        mu = self.mu
        mu.mem_write(GDS * 16 + 0x140C, struct.pack("<H", region))
        mu.mem_write(TALK * 16 + 0x365, struct.pack("<h", thing))
        mu.mem_write(SS * 16 + FRAME - 2, struct.pack("<h", 0x1111))
        mu.mem_write(SS * 16 + FRAME + 6, struct.pack("<HHH", member, skill, 0))
        mu.mem_write(GAME_CS * 16 + GAME_IP, bytes((0xCD, 0xF5, 241, 0xF4)))
        sp = 0x7F0  # (INT F5h's frame, as the game's INT makes it: SITE's way in reads the byte)
        mu.mem_write(SS * 16 + sp - 6, struct.pack("<HHH", GAME_IP + 2, GAME_CS, 0x2))
        for reg, value in dict(cs=TSR, ds=GDS, es=0x1234, ss=SS, esp=sp - 6, ebp=FRAME,
                               eax=chance & 0xFFFF, eflags=0x2).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        mu.emu_start(TSR * 16 + self.sym["site_int"], GAME_CS * 16 + GAME_IP + 3, count=100000)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_IP), GAME_IP + 3)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_ESP) & 0xFFFF, sp)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_DS), GDS)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_ES), 0x1234)
        return struct.unpack("<h", mu.mem_read(SS * 16 + FRAME - 2, 2))[0]

    def test_a_lock_failed_is_out_of_reach(self):
        self.barred([[], [(0x32, 140)], [], []])
        self.assertEqual(self.check(1, locks.OPEN_LOCKS), locks.NEVER)
        self.assertEqual(self.header(LOCK_BARS), 1)

    def test_others_keep_their_chance(self):
        self.barred([[], [(0x32, 140)], [], []])
        self.assertEqual(self.check(0, locks.OPEN_LOCKS), 55)  # (another member)
        self.assertEqual(self.check(1, locks.OPEN_LOCKS, thing=141), 55)  # (another lock)
        self.assertEqual(self.check(1, locks.OPEN_LOCKS, region=0x33), 55)  # (another region)
        self.assertEqual(self.check(1, 2), 55)  # (another skill: find traps)
        self.assertEqual(self.check(4, locks.OPEN_LOCKS), 55)  # (not a party member)
        self.assertEqual(self.header(LOCK_BARS), 0)

    def test_none_barred_as_built(self):
        for m in range(4):  # (FFFFh pairs: none; the region a word the game keeps below FFFFh)
            self.assertEqual(self.check(m, locks.OPEN_LOCKS), 55)

    def test_every_member_and_place(self):
        rows = [[(5, 10 + m * 4 + i) for i in range(locks.LOCK_MAX)] for m in range(4)]
        self.barred(rows)
        for m in range(4):
            for i in range(locks.LOCK_MAX):
                self.assertEqual(self.check(m, locks.OPEN_LOCKS, region=5, thing=10 + m * 4 + i), locks.NEVER)

    def test_the_patch(self):
        patch = next(p for p in ravager.PATCHES if p.name == "lock_site")
        self.assertEqual((patch.offset, patch.original, patch.replacement),
                         (0x8C7E6, bytes.fromhex("8946fe"), bytes((0xCD, 0xF5, 241))))
        self.assertEqual(struct.unpack_from("<H", self.image, self.sym["site_table"] + 2 * 241)[0],
                         self.sym["lock_site"])


class LoaderTests(unittest.TestCase):
    """The Loader's side on the sequel: the table written into the tail, the lock's identity by its record."""
    DS = 0x1000

    def tearDown(self):
        ravlog.restore_layout()

    def test_identity_on_the_sequels_things(self):
        g = FakeGuest()
        log = ravlog.RavDiceLog(g)
        gd = ravlog.RavGameData(log.guest, self.DS, 0)
        self.assertEqual((locks.THING_OBJECT, locks.POSITIONS, locks.THING_SIZE), (0x67D6, 0x67C5, 0x25))
        base = self.DS * 16
        struct.pack_into("<h", g.mem, base + 0x67D6 + 7 * 0x25, 1234)
        struct.pack_into("<HH", g.mem, base + 0x67C5 + 7 * 0x25, 736, 1376)
        self.assertEqual(locks.identity(gd, 7), "o1234@736,1376")
        self.assertEqual(locks.things_now(gd, "o1234@736,1376"), [7])

    def test_layout_put_back(self):
        ravlog.RavDiceLog(FakeGuest())
        ravlog.restore_layout()
        self.assertEqual((locks.THING_OBJECT, locks.THING_SIZE), (game.THING_OBJECT, 32))

    def test_table_written_into_the_tail(self):
        g = FakeGuest()
        seg_base, hdr, tail, off = 0xC91B0, 0x20, 0xD4A0, 0x3A0
        struct.pack_into("<H", g.mem, seg_base + hdr + dicelog.TSR_HDR_OFF, hdr)
        struct.pack_into("<H", g.mem, seg_base + hdr + labels.TSR_TAIL_SEG, tail)
        struct.pack_into("<H", g.mem, seg_base + hdr + LOCK_OFF, off)
        struct.pack_into("<H", g.mem, seg_base + hdr + ravlog.HDR_LEN, LOCK_BARS + 2)
        log = ravlog.RavDiceLog(g)
        log.tsr_hdr = seg_base + hdr
        log.game = ravlog.RavGameData(log.guest, self.DS, 0)
        rows = [[], [(0x32, 140)], [], []]
        real, asked = locks.barred, []
        log.picked_at = {"o12@3,4": 7}
        locks.barred = lambda gd, tried, when=None: asked.append(when) or rows
        try:
            log._locks_pass()
        finally:
            locks.barred = real
        self.assertEqual(asked, [{"o12@3,4": 7}])  # (the times each was tried: the four failed last kept)
        at = tail * 16 + off
        self.assertEqual(bytes(g.mem[at:at + 64]), locks.table(rows))
        self.assertEqual(log.guest.dropped, 0)
        writes = g.writes
        locks.barred = lambda gd, tried, when=None: rows
        try:
            log._locks_pass()  # (unchanged: not written again)
        finally:
            locks.barred = real
        self.assertEqual(g.writes, writes)

    def test_none_without_the_field(self):
        g = FakeGuest()
        seg_base, hdr = 0xC91B0, 0x20
        struct.pack_into("<H", g.mem, seg_base + hdr + dicelog.TSR_HDR_OFF, hdr)
        log = ravlog.RavDiceLog(g)
        log.tsr_hdr = seg_base + hdr
        log.game = ravlog.RavGameData(log.guest, self.DS, 0)
        log._locks_pass()  # (an older helper: no tail, nothing written)
        self.assertEqual(g.writes, 0)

    def test_none_past_the_header(self):
        """A helper whose HDR_LEN (+30) is 0, as every one before it: its +2114 may be code, not LOCK_OFF, so
        nothing is written into its tail; HDR_LEN short of LOCK_OFF's word likewise."""
        for hdr_len in (0, LOCK_OFF):
            g = FakeGuest()
            seg_base, hdr, tail, off = 0xC91B0, 0x20, 0xD4A0, 0x3A0
            struct.pack_into("<H", g.mem, seg_base + hdr + dicelog.TSR_HDR_OFF, hdr)
            struct.pack_into("<H", g.mem, seg_base + hdr + labels.TSR_TAIL_SEG, tail)
            struct.pack_into("<H", g.mem, seg_base + hdr + LOCK_OFF, off)
            struct.pack_into("<H", g.mem, seg_base + hdr + ravlog.HDR_LEN, hdr_len)
            log = ravlog.RavDiceLog(g)
            log.tsr_hdr = seg_base + hdr
            log.game = ravlog.RavGameData(log.guest, self.DS, 0)
            real = locks.barred
            locks.barred = lambda gd, tried, when=None: [[], [(0x32, 140)], [], []]
            try:
                log._locks_pass()
            finally:
                locks.barred = real
            self.assertEqual(g.writes, 0, hdr_len)


@unittest.skipUnless(os.environ.get("DSUN_SL") and os.environ.get("DSUN_WOTR"), "needs both games' files")
class GameFileTests(unittest.TestCase):
    def test_the_check_is_shattered_lands(self):
        with open(os.path.join(os.environ["DSUN_SL"], "DSUN.EXE"), "rb") as f:
            sl = f.read()
        with open(os.path.join(os.environ["DSUN_WOTR"], "DSUN.EXE"), "rb") as f:
            rv = f.read()
        self.assertEqual(sl[0x803B8 + 0x16:0x803B8 + 0x37], rv[0x8C7CB + 0x16:0x8C7CB + 0x37])
        self.assertEqual(rv[0x8C7E6:0x8C7E9], bytes.fromhex("8946fe"))


if __name__ == "__main__":
    unittest.main()
