"""DSCLOG's shared frame code from the sixth memory pass, run in a CPU emulator (needs `pip install
unicorn`): FAR_GAME (the GAME_FAR macro's far call into the game), FRAME_UP and FRAME_DOWN (an
interrupt's frame a word up or down), OVR_FRAME (a handler's frame for the overlay manager), and
the sites that use them."""
import os
import re
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

import test_dsclog as td  # noqa: E402
import test_dsclog_drawing as tdd  # noqa: E402

TSR, GAME_DS, SS = td.TSR, td.GAME_DS, td.SS
STUB = 0xFF00  # (code of the test's own, in DSCLOG's segment past its image: a near call reaches it)


@unittest.skipIf(td.Uc is None, "unicorn not installed")
class FrameCodeTests(unittest.TestCase):
    def setUp(self):
        from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
        self.image, self.sym = tdd.build()
        self.mu = Uc(UC_ARCH_X86, UC_MODE_16)
        self.mu.mem_map(0, 0x100000)
        self.mu.mem_write(TSR * 16, td.load_image())
        self.at = STUB

    def run_stub(self, code, stop, **regs):
        """CODE at a fresh place in DSCLOG's segment (the emulator keeps code it has run), run to its
        offset STOP from there."""
        r = td.r
        self.at += 0x40
        self.mu.mem_write(TSR * 16 + self.at, bytes(code))
        values = dict(cs=TSR, ds=GAME_DS, ss=SS, esp=0x800, ebp=0x1111, eflags=td.IF | 2)
        values.update(regs)
        for name, value in values.items():
            self.mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        self.mu.emu_start(TSR * 16 + self.at, TSR * 16 + self.at + stop)

    def near(self, name, at):
        """A near call at AT (in the stub) to DSCLOG's routine NAME."""
        return b"\xe8" + struct.pack("<H", (self.sym[name] - (at + 3)) & 0xFFFF)

    def reg(self, name):
        return self.mu.reg_read(getattr(td.r, "UC_X86_REG_" + name.upper()))

    def word(self, sp):
        return struct.unpack("<H", self.mu.mem_read(SS * 16 + sp, 2))[0]

    def test_far_game_calls_the_game_as_a_far_call_would(self):
        """GAME_FAR -100h, 234h from DS 3000h: the routine at 2F00h:234h, with the stack a "call far"
        leaves (the way back to past the two words, in DSCLOG's segment, then the arguments); back
        there, every register but AX as it was."""
        seg, off = GAME_DS - 0x100, 0x234
        # the game's routine: [BP+2] its way back, [BP+6] the argument; AX the argument, the way
        # back in CX:DX's places of memory (2F00h:300h), then RETF
        self.mu.mem_write(seg * 16 + off, bytes.fromhex("5589e5" "8b4602" "2ea30003" "8b4604" "2ea30203"
                                                        "8b4606" "5dcb"))
        code = b"\x68\x34\x12" + b"\x0e" + self.near("far_game", self.at + 0x40 + 4)
        code += struct.pack("<HH", (seg - GAME_DS) & 0xFFFF, off) + b"\x83\xc4\x02"
        self.run_stub(code, len(code), ebx=0xB0B0, ecx=0xC0C0, edx=0xD0D0, esi=0x5151, edi=0xD1D1, es=0xE5E5)
        self.assertEqual(self.reg("ax"), 0x1234)
        back = struct.unpack("<HH", self.mu.mem_read(seg * 16 + 0x300, 4))
        self.assertEqual(back, (self.at + 3 + 1 + 3 + 4, TSR))
        self.assertEqual([self.reg(n) for n in ("bx", "cx", "dx", "si", "di", "bp", "es", "ds", "sp")],
                         [0xB0B0, 0xC0C0, 0xD0D0, 0x5151, 0xD1D1, 0x1111, 0xE5E5, GAME_DS, 0x800])

    def frame(self, sp, ip=0x1A1A, cs=0x2B2B, fl=0x0246):
        self.mu.mem_write(SS * 16 + sp, struct.pack("<HHHHHH", ip, cs, fl, 0x4444, 0x5555, 0x6666))

    def test_frame_up_drops_the_word_under_the_frame(self):
        """Two FRAME_UPs: the interrupt's frame (IP, CS, flags) four bytes up, over the two words
        under it; registers and flags as they were."""
        self.frame(0x7F0)
        code = self.near("frame_up", self.at + 0x40) + self.near("frame_up", self.at + 0x43)
        self.run_stub(code, 6, esp=0x7F0, eax=0xA1A1, eflags=td.IF | 0x83)
        self.assertEqual(self.reg("sp"), 0x7F4)
        self.assertEqual([self.word(0x7F4 + 2 * k) for k in range(4)], [0x1A1A, 0x2B2B, 0x0246, 0x6666])
        self.assertEqual([self.reg("ax"), self.reg("bp"), self.reg("eflags") & 0xFFF], [0xA1A1, 0x1111, td.IF | 0x83])

    def test_frame_down_makes_room_under_the_frame(self):
        """Two FRAME_DOWNs: the frame four bytes down, the two words under it (where the frame was)
        room for the site to write; registers and flags as they were."""
        self.frame(0x7F0)
        code = self.near("frame_down", self.at + 0x40) + self.near("frame_down", self.at + 0x43)
        self.run_stub(code, 6, esp=0x7F0, eax=0xA1A1, eflags=td.IF | 0x83)
        self.assertEqual(self.reg("sp"), 0x7EC)
        self.assertEqual([self.word(0x7EC + 2 * k) for k in range(3)], [0x1A1A, 0x2B2B, 0x0246])
        self.assertEqual(self.word(0x7F6), 0x4444)  # (the caller's own words below the room kept)
        self.assertEqual([self.reg("ax"), self.reg("bp"), self.reg("eflags") & 0xFFF], [0xA1A1, 0x1111, td.IF | 0x83])

    def test_ovr_frame_pushes_the_way_back_as_a_far_call(self):
        """OVR_FRAME after PUSHAD and PUSH ES (34 bytes over the interrupt's IP, CS, flags): CS then IP
        pushed, then BP, BP = SP, BX the SP before them; other registers and flags as they were."""
        self.mu.mem_write(SS * 16 + 0x7DE, bytes(34) + struct.pack("<HHH", 0x1A1A, 0x2B2B, 0x0246))
        self.run_stub(self.near("ovr_frame", self.at + 0x40), 3, esp=0x7DE, eax=0xA1A1, ecx=0xC1C1,
                      eflags=td.IF | 0x83)
        self.assertEqual([self.reg("sp"), self.reg("bp"), self.reg("bx")], [0x7D8, 0x7D8, 0x7DE])
        self.assertEqual([self.word(0x7D8 + 2 * k) for k in range(3)], [0x1111, 0x1A1A, 0x2B2B])
        self.assertEqual([self.reg("ax"), self.reg("cx"), self.reg("eflags") & 0xFFF], [0xA1A1, 0xC1C1, td.IF | 0x83])

    def test_box_pops_drop_their_bytes(self):
        """BOX_POP4, BOX_POP6, BOX_POP10 as the game's "add sp,4" / 6 / 0Ah after the INT: back at the
        frame's IP with SP past the bytes, registers as they were."""
        for name, n in (("box_pop4", 4), ("box_pop6", 6), ("box_pop10", 10)):
            back = 0x40 + n * 0x10
            self.mu.mem_write(td.CALLER * 16 + back, b"\xf4")
            self.mu.mem_write(SS * 16 + 0x7E0, struct.pack("<HHH", back, td.CALLER, td.IF | 2) + bytes(n))
            code = b"\xe9" + struct.pack("<H", (self.sym[name] - (self.at + 0x40 + 3)) & 0xFFFF)
            self.at += 0x40
            self.mu.mem_write(TSR * 16 + self.at, code)
            for reg, value in dict(cs=TSR, ss=SS, esp=0x7E0, eax=0x7777, ebp=0x1111).items():
                self.mu.reg_write(getattr(td.r, "UC_X86_REG_" + reg.upper()), value)
            self.mu.emu_start(TSR * 16 + self.at, td.CALLER * 16 + back)
            self.assertEqual([self.reg("sp"), self.reg("ax"), self.reg("bp")], [0x7E6 + n, 0x7777, 0x1111], name)

    def test_no_far_pointer_left_for_a_single_call(self):
        """The GAME_FAR sites' far pointers are gone; th_far is GAME_FAR."""
        with open(tdd.ASM) as f:
            asm = f.read()
        for name in ("th_call", "xp_call", "drop_call", "sp_btn", "pick_far", "spread_far", "reach_line_at",
                     "blow_charge", "free_call", "box_line", "blow_rand", "n_ip"):
            self.assertIsNone(re.search(r"^%s\s+d[wd]\b" % name, asm, re.M), name)
        self.assertIn("game_far %1 - DGROUP_SEG, %2", asm)


if __name__ == "__main__":
    unittest.main()
