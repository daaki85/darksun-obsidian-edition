"""The figures' shadows in Wake of the Ravager (DSCLOG2's FIGURE SHADOWS: FIG_PASS in the floor pass, the
redraws widened by FIG_WIDE_ALL and FIG_WIDE, sites 160 and 161): the header's fields, the patches, the pass and
the sites run in an emulated CPU with its VGA (needs nasm and unicorn, else skipped), and with DSUN_WOTR the
sequel's own bytes where it reads and patches."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import ravager, ravlog  # noqa: E402

try:
    from unicorn import Uc  # noqa: F401
    from test_dsclog_drawing import Scene, TSR, GAME_DS, FAR, SS
    from unicorn import x86_const as r
except ImportError:
    Uc = None

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASM = os.path.join(HERE, "dos", "dsclog2.asm")
WOTR = os.environ.get("DSUN_WOTR")
FIG_SHADOWS, FIG_PASSES, FIG_DRAWN, FIG_WIDES, FIG_KEPT, FIG_FROM_KEPT = 1960, 1962, 1964, 1966, 1968, 1970  # (the header)
FIG_OTHER, FIG_MISSED = 1978, 1980
LOAD = (GAME_DS - ravager.DGROUP) & 0xFFFF if Uc else 0
THINGS = ((LOAD + 0x3F49) & 0xFFFF) * 16 + 0x0C33
CACHE = ((GAME_DS - (0x47E0 - 0x42A2)) & 0xFFFF) * 16 + 0x0CA8
LIST, CREATURES, PICTURE = 0x2000, 0x6000, 0x7000
CAM = (800, 400)


def frame(w, h):
    """A frame of runs: every row one run across the whole width (its pixels colour 9, one repeat)."""
    out = bytearray(struct.pack("<HH", w, h))
    for y in range(h):
        out += bytes((y,)) + struct.pack("<HBB", 0x8000, w, 2) + bytes((((w - 1) << 1) | 1, 9))
    return bytes(out + b"\xff")


@unittest.skipIf(Uc is None, "unicorn not installed")
class PassTests(unittest.TestCase):
    def scene(self, statuses, seen=True):
        """Things 5, 6, 7 standing in the view (creatures 0, 1, 2 with STATUSES; None: not a creature), each
        an 8 x 16 frame, their feet 20 pixels apart; the floor all colour 40, DARK 40 -> 41."""
        s = Scene(ASM)
        s.fill_with = 40
        for p in range(4):
            s.planes[p][:16000] = bytes((40,)) * 16000
        s.put_at_far("FAR_DARK", bytes(41 if c == 40 else c for c in range(256)))
        s.put("dark_ready", b"\x01")
        s.put("fig_seen", bytes((int(seen),)))
        for name, value in (("game_ds", GAME_DS), ("clip_x0", 0), ("clip_y0", 0), ("clip_x1", 319), ("clip_y1", 199),
                            ("v_seg", 0xA000), ("v_y0", 0), ("v_x0", 0), ("v_row", 80), ("cam_x", CAM[0]),
                            ("cam_y", CAM[1])):
            s.word(name, value)
        s.ds(0x67B7, struct.pack("<HH", 0, LIST))
        s.ds(0x264E, struct.pack("<H", 3))
        s.ds(0x265D, struct.pack("<H", 3))
        s.ds(0x19C9, struct.pack("<HH", 0, CREATURES))
        pic = struct.pack("<IHI", 0, 1, 10) + frame(8, 16)
        s.mu.mem_write(PICTURE * 16, pic)
        for n, status in enumerate(statuses):
            thing, x, y = 5 + n, CAM[0] + 40 + 60 * n, CAM[1] + 100
            s.mu.mem_write(LIST * 16 + 8 * n, struct.pack("<HHBBH", x, y, 0, 0x20, thing))
            s.mu.mem_write(THINGS + 3 * thing, struct.pack("<BH", 2 if status is not None else 1, n))
            s.mu.mem_write(CREATURES * 16 + n * 0x31 + 0x14, bytes((status or 1,)))
            rec = bytearray(0x25)
            rec[7], rec[8:10], rec[0x10:0x12], rec[0x12] = 4, struct.pack("<H", 15), struct.pack("<H", n), 0
            s.ds(0x67BB + 0x25 * thing, bytes(rec))
            s.mu.mem_write(CACHE + 16 * n, struct.pack("<HIIHHBB", n, len(pic), 0, 0, PICTURE, 2, 0))
        return s

    def dark(self, s):
        """The screen's darkened pixels, (x, y)."""
        screen = s.screen()
        return {(i % 320, i // 320) for i, c in enumerate(screen) if c == 41}

    def test_living_creatures_cast_shadows(self):
        """Each living creature's frame casts its shadow from its feet down and to the right, half as tall; the
        dead (7), the dying (4) and what isn't a creature cast none."""
        s = self.scene([1, 7, None])
        s.call("fig_pass", fs=FAR)
        dark = self.dark(s)
        hdr = s.sym["hdr"]
        word = lambda at: struct.unpack("<H", s.get("hdr", 2, at))[0]
        self.assertEqual((word(FIG_PASSES), word(FIG_DRAWN)), (1, 1))
        # the first figure: left 40 - 4 = 36, top 100 - 15 = 85, feet at row 100; its rows 0-15 up 15..0, every
        # other one cast, on rows 100 + up / 2
        self.assertTrue(dark)
        self.assertEqual(min(y for _, y in dark), 100)  # (laid down from the feet: up 14 -> row 107)
        self.assertEqual(max(y for _, y in dark), 100 + 7)
        self.assertEqual(min(x for x, _ in dark), 36)  # (the feet's row: no lean)
        self.assertTrue(all(x < 36 + 8 + 15 for x, _ in dark))
        self.assertIn((36 + 14 + 1, 107), dark)  # (14 up: leant 14 + (14 + 10) // 20 = 15 right)
        self.assertFalse(any(x >= 90 for x, _ in dark))  # (the dead one's and the other thing's: none)
        self.assertEqual(hdr, s.sym["hdr"])

    def test_dying_none(self):
        s = self.scene([4, 8, 1])
        s.call("fig_pass", fs=FAR)
        dark = self.dark(s)
        self.assertTrue(dark)
        self.assertTrue(all(x >= 156 for x, _ in dark))  # (only the third's, at 40 + 120 - 4)

    def test_none_without_the_sites_or_switched_off(self):
        s = self.scene([1, 1, 1], seen=False)
        s.call("fig_pass", fs=FAR)
        self.assertFalse(self.dark(s))
        s = self.scene([1, 1, 1])
        s.put("hdr", struct.pack("<H", 0), FIG_SHADOWS)
        s.call("fig_pass", fs=FAR)
        self.assertFalse(self.dark(s))

    def test_picture_out_of_memory_none(self):
        """Out of memory and never kept: none."""
        s = self.scene([1, None, None])
        s.mu.mem_write(CACHE + 0x0E, b"\x00")
        s.call("fig_pass", fs=FAR)
        self.assertFalse(self.dark(s))
        self.assertEqual(struct.unpack("<H", s.get("hdr", 2, FIG_MISSED))[0], 1)

    def test_picture_out_of_memory_kept(self):
        """Out of memory: the shadow FIG_KEEP kept for the picture (its key: the slot's number and place), the same
        as from the picture; another frame's when this one wasn't kept."""
        live = self.scene([1, None, None])
        live.call("fig_pass", fs=FAR)
        for frame in (0, 3):
            s = self.scene([1, None, None])
            s.mu.mem_write(CACHE + 0x0E, b"\x00")
            runs = [(up, 0, 8) for up in range(0, 16, 2)]  # (the frame: every row one run of 8; rows 15 .. 0 up)
            kept = struct.pack("<HHBBBB", 0, 0, frame, 8, 15, len(runs)) + b"".join(bytes(r) for r in runs)
            s.mu.mem_write(FAR * 16 + s.sym["FAR_SC"], kept)
            s.call("fig_pass", fs=FAR)
            self.assertEqual(self.dark(s), self.dark(live))
            self.assertEqual(struct.unpack("<H", s.get("hdr", 2, FIG_FROM_KEPT))[0], 1)
            self.assertEqual(struct.unpack("<H", s.get("hdr", 2, FIG_OTHER))[0], 1 if frame else 0)
            self.assertEqual(struct.unpack("<H", s.get("hdr", 2, FIG_MISSED))[0], 0)

    def test_kept_as_drawn(self):
        """FIG_KEEP: a living creature's frame kept as the game draws it (its key, frame, width, bottom row and the
        runs every other row up from the feet), then the game's routine called with the call's arguments, the
        segment read from after the site, and back past it."""
        s = self.scene([1, None, None])
        game = 0x8000  # (the game's code: the site's way back at 8000:0010, the segment word there; its routine)
        s.mu.mem_write(game * 16 + 0x10, struct.pack("<H", 0x8100))
        s.mu.mem_write(0x8100 * 16 + 0x3BEC, b"\xb8\x34\x12\xcb")  # (mov ax,1234h / retf)
        s.mu.mem_write(game * 16 + 0x12, b"\xf4")
        sp = 0x700
        args = struct.pack("<HHHHHHH", 1, 50, 60, 0, 0, PICTURE, 0)
        s.mu.mem_write(SS * 16 + sp, struct.pack("<HHH", 0x10, game, 0x2) + args)
        for reg, value in dict(cs=TSR, ds=GAME_DS, ss=SS, esp=sp, edi=5, esi=0, eflags=0x2).items():
            s.mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        s.mu.emu_start(TSR * 16 + s.sym["fig_keep"], game * 16 + 0x12, count=100000)
        self.assertEqual((s.mu.reg_read(r.UC_X86_REG_AX), s.mu.reg_read(r.UC_X86_REG_SP)), (0x1234, sp + 6))
        slot = bytes(s.mu.mem_read(FAR * 16 + s.sym["FAR_SC"], 8 + 3 * 8))
        self.assertEqual(slot[:8], struct.pack("<HHBBBB", 0, 0, 0, 8, 15, 8))
        self.assertEqual(slot[8:], b"".join(bytes((up, 0, 8)) for up in range(14, -1, -2)))  # (the rows top down)
        self.assertEqual(struct.unpack("<H", s.get("hdr", 2, FIG_KEPT))[0], 1)

    def site(self, name, bp, stack, words):
        """Site NAME entered as SITE_INT leaves it (the INT's IP, CS and flags on the stack, then STACK), with the
        game's BP and WORDS at SS:BP + offset; (SP, IP, the stack's words from SP) as it comes back."""
        s = Scene(ASM)
        sp = 0x700
        s.mu.mem_write(SS * 16 + sp, struct.pack("<HHH", 0xFFF0, TSR, 0x202) + b"".join(struct.pack("<H", w) for w in stack))
        for off, w in words.items():
            s.mu.mem_write(SS * 16 + bp + off, struct.pack("<h", w))
        s.mu.mem_write(TSR * 16 + 0xFFF0, b"\xf4" * 16)
        for reg, value in dict(cs=TSR, ds=GAME_DS, ss=SS, esp=sp, ebp=bp, edi=0x1234, eflags=0x2).items():
            s.mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        try:
            s.mu.emu_start(TSR * 16 + s.sym[name], 0, count=2000)
        except Exception:
            pass
        out_sp = s.mu.reg_read(r.UC_X86_REG_SP)
        got = {off: struct.unpack("<h", s.mu.mem_read(SS * 16 + bp + off, 2))[0] for off in words}
        return s, out_sp, s.mu.reg_read(r.UC_X86_REG_IP) - 1, got, struct.unpack("<4H", s.mu.mem_read(SS * 16 + out_sp, 8))

    def test_fig_wide_all(self):
        """x1 ([BP-0Eh]) and y1 ([BP-12h]) further right and down, kept to the screen (13Fh, C7h); then the two
        pushes, [BP+8] and DI, made under the way back."""
        bp = 0x900
        s, sp, ip, got, top = self.site("fig_wide_all", bp, [], {-0x0E: 100, -0x12: 170, 8: 0x777})
        self.assertEqual(ip, 0xFFF0)
        self.assertEqual((got[-0x0E], got[-0x12]), (172, 0xC7))
        self.assertEqual(sp, 0x700 + 6 - 4)
        self.assertEqual(top[:2], (0x1234, 0x777))  # (DI, then [BP+8], as "push word [bp+8] / push di")
        self.assertEqual(struct.unpack("<H", s.get("fig_seen", 1) + b"\0")[0], 1)

    def test_fig_wide(self):
        """x1 and y1 (the routine's [BP+10h], [BP+12h]) further, then the routine's own start: BP pushed and set,
        8 bytes taken, back past the site."""
        stack = [0x1111, 0x2222, 800, 400, 1, 10, 20, 100, 120, 1]  # (the way back, camera x, y, page, x0..y1, flag)
        s, sp, ip, _, top = self.site("fig_wide", 0x900, stack, {})
        self.assertEqual(ip, 0xFFF0)
        frame = struct.unpack("<12H", s.mu.mem_read(SS * 16 + 0x700 + 6 - 2, 24))
        self.assertEqual(frame[0], 0x900)  # (the game's BP, pushed)
        self.assertEqual(frame[1:3], (0x1111, 0x2222))
        self.assertEqual(frame[8:10], (100 + 72, 120 + 44))
        self.assertEqual(sp, 0x700 + 6 - 2 - 8)
        self.assertEqual(s.mu.reg_read(r.UC_X86_REG_BP), 0x700 + 6 - 2)


@unittest.skipIf(Uc is None, "unicorn not installed")
class DustTests(unittest.TestCase):
    """DSCLOG2's DUST (SL's): a walker raises puffs (DUST_TICK, from the main loop), drawn in the floor pass through
    LIGHT (DUST_FLOOR), only with the Loader's DUST_ON."""

    scene = PassTests.scene

    def walk(self, on=True, steps=4):
        s = self.scene([1, None, None])
        s.put("hdr", struct.pack("<H", int(on)), 1972)
        s.put_at_far("FAR_LIGHT", bytes(42 if c == 40 else 0 for c in range(256)))
        s.ds(0x1408, struct.pack("<HH", *CAM))
        for n in range(steps):
            s.mu.mem_write(LIST * 16, struct.pack("<HH", CAM[0] + 40 + 5 * n, CAM[1] + 100))
            s.mu.mem_write(0x46C, struct.pack("<H", 1000 + n))
            s.call("dust_tick", fs=FAR)
        s.call("dust_floor", fs=FAR)
        return s

    def test_puffs_behind_a_walker(self):
        s = self.walk()
        self.assertGreaterEqual(struct.unpack("<H", s.get("hdr", 2, 1974))[0], 2)
        light = {(i % 320, i // 320) for i, c in enumerate(s.screen()) if c == 42}
        self.assertTrue(light)
        self.assertTrue(all(20 <= x <= 70 and 85 <= y <= 110 for x, y in light), sorted(light)[:5])

    def test_none_without_dust_on(self):
        s = self.walk(on=False)
        self.assertEqual(struct.unpack("<H", s.get("hdr", 2, 1974))[0], 0)
        self.assertFalse(any(c == 42 for c in s.screen()))


class HeaderTests(unittest.TestCase):
    @unittest.skipIf(Uc is None, "unicorn not installed")
    def test_fields_and_sites(self):
        from test_dsclog_drawing import build
        _, sym = build(ASM)
        for name, at in (("fig_shadows", FIG_SHADOWS), ("fig_passes", FIG_PASSES), ("fig_drawn", FIG_DRAWN),
                         ("fig_wides", FIG_WIDES), ("fig_kept", FIG_KEPT), ("fig_from_kept", FIG_FROM_KEPT),
                         ("dust_on", ravlog.DUST_ON), ("dust_puffs", ravlog.DUST_PUFFS), ("dust_sig", ravlog.DUST_SIG),
                         ("fig_other", FIG_OTHER), ("fig_missed", FIG_MISSED)):
            self.assertEqual(sym[name] - sym["hdr"], at, name)
        for name in ("fig_pass", "fig_wide", "fig_wide_all", "fig_of", "fig_keep", "fig_record"):
            self.assertLess(sym[name], sym["resident_end"], name)
        src = open(ASM).read()
        self.assertRegex(src, r"\n        dw fig_wide_all +; 160 SITE_FIG_WIDE_ALL")
        self.assertRegex(src, r"\n        dw fig_wide +; 161 SITE_FIG_WIDE")
        self.assertRegex(src, r"\n        dw fig_keep +; 162 SITE_FIG_KEEP")

    def test_patches(self):
        by = {p.name: p for p in ravager.PATCHES}
        self.assertEqual((by["fig_wide_all"].offset, by["fig_wide_all"].original.hex(), by["fig_wide_all"].replacement),
                         (0x2868C, "ff760857", bytes((0xCD, ravager.VEC_SITE, 160, 0x90))))
        self.assertEqual((by["fig_wide"].offset, by["fig_wide"].original.hex(), by["fig_wide"].replacement),
                         (0x2828C, "558bec83ec08", bytes((0xCD, ravager.VEC_SITE, 161, 0x90, 0x90, 0x90))))
        self.assertEqual((by["fig_keep"].offset, by["fig_keep"].original.hex(), by["fig_keep"].replacement),
                         (0x2A347, "9aec3b", bytes((0xCD, ravager.VEC_SITE, 162))))

    @unittest.skipUnless(WOTR, "DSUN_WOTR (the sequel's folder) not given")
    def test_the_games_bytes(self):
        """The redraw of what moved (its rectangle's x0, x1, y0, y1 at [BP-0Ch]..[BP-12h], then the floor's
        rectangle, 262C:04BF), the rectangle's redraw keeping its x1, y1 on the screen, and the thing drawer's
        reads of the draw list, the map thing and the picture cache that FIG_OF follows."""
        with open(os.path.join(WOTR, "DSUN.EXE"), "rb") as f:
            exe = f.read()
        self.assertEqual(exe[0x28641:0x2866A], bytes.fromhex(
            "83e2fc83e1fc83c1033b56f47d038956f43b4ef27e03894ef23b76f07d038976f03b5eee7e03895eee"))
        self.assertEqual(exe[0x2868C:0x286A6], bytes.fromhex("ff760857ff76ee8b46f24050ff76f0ff76f4ff760a9abf042c26"))
        self.assertEqual(exe[0x282C6:0x282E9], bytes.fromhex(
            "81ff40017c05bf3f01eb040bff7cd8817e12c8007c07c74612c700eb06837e12007cc4"))
        self.assertEqual(exe[0x26F64:0x26F96], bytes.fromhex(
            "c47ee2268a4505a820742732ed268b058a4f072bc12b46068946fe268b45028b4f082bc1268a4d042bc12b46088946fc"
            "eb12"))
        self.assertEqual(exe[0x26FA8:0x26FC7], bytes.fromhex("bea80c8b47108bd032e4268a4505a8807505b80000eb03b80100"
                                                             "32ed8a4f12"))
        self.assertEqual(exe[0x2A2AA:0x2A2B1], bytes.fromhex("662683bfae0c00"))  # (the slot's +6: below 0 none)
        self.assertEqual(exe[0x2A2C6:0x2A2CC], bytes.fromhex("26f687b60c02"))  # (+0Eh bit 2: in memory)
        self.assertEqual(exe[0x2A2E6:0x2A2EB], bytes.fromhex("268b87b20c"))  # (+0Ah: the picture, far)
        self.assertEqual(exe[0x2A322:0x2A34F], bytes.fromhex(  # (the call FIG_KEEP sits on, its arguments)
            "8a460eb400508bdec1e304b8a2428ec06626ffb7b20c8a4610b40050ff760aff7608ff76069aec3b401d83c40e"))


if __name__ == "__main__":
    unittest.main()
