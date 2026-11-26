"""See-through figures in the sequel (DSCLOG2's SEE-THROUGH FIGURES: GHOST_DRAW in FIG_KEEP's place of the game's
picture call, site 162; GHOST_UNION in FIG_WIDE_ALL, site 160), their tables in the far block and only the pixels
and spans in GHOST's block of upper memory; and the Loader's RavGhosts. Emulated (nasm and unicorn, else skipped)."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import ghost, ravlog  # noqa: E402

try:
    from unicorn import x86_const as r
    from test_dsclog_drawing import Scene, TSR, GAME_DS, FAR, SS, build
    from test_ravshadows import PassTests, PICTURE, ASM
except ImportError:
    Scene = None

GHOST = 0x9000  # (GHOST's block, in the test)


@unittest.skipIf(Scene is None, "nasm or unicorn not installed")
class GhostTests(unittest.TestCase):
    scene = PassTests.scene

    def keep(self, thing, stealth=0, tab=b"", on=1):
        """FIG_KEEP entered for THING with an 8 x 16 frame of colour 9 at page 3's (50, 60); the floor colour 40;
        BLEND: REP number r over colour c is 100 + r, REP: 9 -> 5. The game's routine sets AX 1234h."""
        s = self.scene([1, None, None])
        pages = ((GAME_DS - 0x47E0 + 0x0BF3) & 0xFFFF) * 16  # (the sequel's page table: page 3 the whole screen)
        for field, value in ((4, 0xA000), (0x404, 0), (0x604, 0), (0x804, 319), (0xA04, 199), (0xC04, 0)):
            s.mu.mem_write(pages + 6 + field, struct.pack("<H", value))
        s.word("ghost_on", on)
        s.word("ghost_seg", GHOST)
        s.word("stealth", stealth)
        blend = bytes(100 + rep for rep in range(ghost.REP_COUNT) for c in range(256))
        s.put_at_far("FAR_GH_BLEND", blend)
        s.put_at_far("FAR_GH_REP", bytes(5 if c == 9 else 0 for c in range(256)))
        s.put_at_far("FAR_GH_TAB", tab.ljust(80, b"\0"))
        game = 0x8000
        s.mu.mem_write(game * 16 + 0x10, struct.pack("<H", 0x8100))
        s.mu.mem_write(0x8100 * 16 + 0x3BEC, b"\xb8\x34\x12\xcb")
        s.mu.mem_write(game * 16 + 0x12, b"\xf4")
        sp = 0x700
        args = struct.pack("<HHHHHHH", 3, 50, 60, 0, 0, PICTURE, 0)
        s.mu.mem_write(SS * 16 + sp, struct.pack("<HHH", 0x10, game, 0x2) + args)
        for reg, value in dict(cs=TSR, ds=GAME_DS, ss=SS, esp=sp, edi=thing, esi=0, eax=0, eflags=0x2).items():
            s.mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        s.mu.emu_start(TSR * 16 + s.sym["fig_keep"], game * 16 + 0x12, count=200000)
        return s

    def figure(self, s):
        screen = s.screen()
        return {(i % 320, i // 320): c for i, c in enumerate(screen) if c != 40}

    def test_hidden_member_see_through(self):
        s = self.keep(1, stealth=0b10)
        self.assertNotEqual(s.mu.reg_read(r.UC_X86_REG_AX), 0x1234)  # (the game's routine not called)
        got = self.figure(s)
        self.assertEqual(set(got.values()), {105})
        self.assertEqual(len(got), 8 * 16)
        self.assertEqual(min(got), (50, 60))
        self.assertEqual(struct.unpack("<H", s.get("hdr", 2, ravlog.GHOST_DRAWS))[0], 1)
        self.assertEqual(s.get("gh_shown", 1)[0], 0b10)

    def test_marked_creature(self):
        s = self.keep(9, tab=bytes((0, 0b10)))
        self.assertEqual(set(self.figure(s).values()), {105})

    def test_others_the_games(self):
        for kw in ({"thing": 1}, {"thing": 1, "stealth": 0b10, "on": 0}, {"thing": 9, "tab": bytes((0, 0b100))}):
            s = self.keep(**kw)
            self.assertEqual(s.mu.reg_read(r.UC_X86_REG_AX), 0x1234, kw)
            self.assertEqual(self.figure(s), {}, kw)

    def test_union(self):
        """GHOST_UNION: the whole view once a member drawn see-through is hidden no longer, or GHOST_TAB changed."""
        for stealth, shown, changed, whole in ((0, 1, 0, True), (1, 1, 0, False), (0, 0, 1, True), (0, 0, 0, False)):
            s = Scene(ASM)
            s.word("ghost_on", 1)
            s.word("stealth", stealth)
            s.word("gh_shown", shown)
            s.mu.mem_write(FAR * 16 + s.sym["FAR_GH_CHANGED"], bytes((changed,)))
            bp = 0x900
            for off, v in ((-0x0C, 10), (-0x0E, 20), (-0x10, 30), (-0x12, 40)):
                s.mu.mem_write(SS * 16 + bp + off, struct.pack("<H", v))
            s.call("ghost_union", ss=SS, ebp=bp)
            rect = struct.unpack("<hhhh", s.mu.mem_read(SS * 16 + bp - 0x12, 8))  # (y1, y0, x1, x0)
            self.assertEqual(rect, (0xC7, 0, 0x13F, 0) if whole else (40, 30, 20, 10), (stealth, shown, changed))

    def test_layout(self):
        _, sym = build(ASM)
        self.assertLessEqual(sym["FAR_TOP"], 0x10000)
        self.assertEqual(sym["FAR_GH_BLEND"] % 16, 0)
        self.assertLessEqual(sym["FAR_GH_BLEND"] + ghost.REP_COUNT * 256 - 1, 0xFFFF)
        for name, at in (("ghost_seg", ravlog.GHOST_SEG), ("ghost_on", ravlog.GHOST_ON), ("ghost_blend", ravlog.GHOST_BLEND),
                         ("ghost_rep", ravlog.GHOST_REP), ("ghost_tab", ravlog.GHOST_TAB),
                         ("ghost_draws", ravlog.GHOST_DRAWS)):
            self.assertEqual(sym[name] - sym["hdr"], at, name)
        src = open(ASM).read()
        self.assertIn("GHOST_PARAS equ (GH_SPANS + GH_SPANS_MOST * 8 + 15) / 16", src)
        self.assertIn("GH_PIX_MOST equ 4096", src)  # (the block: 4,096 + 192 x 8 = 5,632 bytes)


class LoaderTests(unittest.TestCase):
    def test_tables_in_the_sequels_colours(self):
        dac = bytearray(768)
        for i in range(256):
            dac[i * 3:i * 3 + 3] = bytes((i // 4, (255 - i) // 4, (i * 7 % 256) // 4))
        blend, rep = ghost.tables(bytes(dac), ravlog.RavGhosts.FIRST, ravlog.RavGhosts.LAST)
        self.assertEqual(len(blend), ghost.REP_COUNT * 256)
        self.assertTrue(all(32 <= c for c in blend))  # (never a cycled colour)

    def test_table_by_the_sequels_effects(self):
        E = type("E", (), {})
        def eff(owner, id_):
            e = E()
            e.owner, e.id = owner, id_
            return e
        g = ravlog.RavGhosts()
        self.assertEqual(ghost.ghost_table([eff(9, 53)], g.INVISIBLE, g.DETECT)[1], 0b10)
        self.assertEqual(ghost.ghost_table([eff(9, 53), eff(0, 25)], g.INVISIBLE, g.DETECT)[1], 0)
        self.assertEqual(ghost.ghost_table([eff(9, 23)], g.INVISIBLE, g.DETECT)[1], 0)  # (SL's number: not the sequel's)


if __name__ == "__main__":
    unittest.main()
