"""PROBE_SCROLL (the map's main loop asking where the pointer is) and interrupts: the pass's own work
with interrupts on when the game had them on (a sound, the clicks), off where the original was (its
INT 33h), round TARGET_CLICK's calls to the game's mouse handler, which the driver calls with them
off, and while DSCLOG draws on the screen (DRAW_MASKED: the view drawn again, the panel, the labels,
the dust): the game draws its pointer from the mouse's interrupt, and one drawn in the middle of
those left images of itself on the map (the user's report after 2.15.0, which drew with them on)."""
import os
import struct
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import test_dsclog as td  # noqa: E402
import test_dsclog_drawing as tdd  # noqa: E402

TSR, GAME_DS, SS, CALLER, IF = td.TSR, td.GAME_DS, td.SS, td.CALLER, td.IF
STUBS = 0x7800                  # the INT 33h stand-in and the game's mouse handler's
DGROUP_SEG, CENTRE_SEG = 0x4356, 0x191F
MAP_THINGS, CAM_X = 0x6694, 0x1178

# INT 33h: function 3 notes its caller's flags (STUBS:0100h) and gives buttons 0 at (100, 100);
# function 4 notes nothing. The game's handler notes its flags (0102h) and counts (0104h). The
# view's centring (CENTRE_SEG:CENTRE_OFF, as DSCLOG's CENTRE has it) notes its flags (0106h) and
# counts (0108h).
STUB_ASM = """
bits 16
org 0
int33:  push bp
        mov bp, sp
        cmp ax, 3
        jne .x
        push ax
        mov ax, [bp + 6]
        mov [cs:0x100], ax
        pop ax
        xor bx, bx
        mov cx, 100
        mov dx, 100
.x:     pop bp
        iret
handler:
        pushf
        pop ax
        mov [cs:0x102], ax
        inc word [cs:0x104]
        retf
"""
CENTRE_ASM = """
bits 16
        pushf
        pop ax
        mov [cs:0x%X], ax
        inc word [cs:0x%X]
        retf
"""


def assemble(text):
    with tempfile.TemporaryDirectory() as tmp:
        src, out = os.path.join(tmp, "s.asm"), os.path.join(tmp, "s.bin")
        with open(src, "w") as f:
            f.write(text)
        subprocess.run(["nasm", "-f", "bin", "-o", out, src], check=True)
        with open(out, "rb") as f:
            return f.read()


@unittest.skipIf(td.Uc is None, "unicorn not installed")
class ScrollInterruptTests(unittest.TestCase):
    def setUp(self):
        from dsloader.gamepatch import VEC_SCROLL
        self.vec = VEC_SCROLL
        image = td.load_image()
        _, self.sym = tdd.build()
        self.mu = mu = td.Uc(td.UC_ARCH_X86, td.UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, image)
        mu.hook_add(td.UC_HOOK_INTR, td.real_mode_interrupt)
        at = td.install_at(image, VEC_SCROLL)
        self.assertGreater(at, 0)
        mu.mem_write(VEC_SCROLL * 4, struct.pack("<HH", struct.unpack_from("<H", image, at + 4)[0], TSR))
        stubs = assemble(STUB_ASM)
        mu.mem_write(STUBS * 16, stubs)
        mu.mem_write(0x33 * 4, struct.pack("<HH", 0, STUBS))
        handler = len(assemble(STUB_ASM.split("handler:")[0]))
        self.word("game_handler", handler)
        self.word("game_handler", STUBS, 2)
        centre_off, = struct.unpack("<H", mu.mem_read(TSR * 16 + self.sym["centre"], 2))
        self.centre = ((GAME_DS - DGROUP_SEG + CENTRE_SEG) & 0xFFFF) * 16 + centre_off
        self.centre_seg = (GAME_DS - DGROUP_SEG + CENTRE_SEG) & 0xFFFF
        # the stub's notes kept 0x200 on past its code, in its own segment
        code = assemble(CENTRE_ASM % (centre_off + 0x200, centre_off + 0x202))
        mu.mem_write(self.centre, code)
        mu.mem_write(GAME_DS * 16 + CAM_X, struct.pack("<HH", 0, 0))

    def word(self, name, value=None, plus=0):
        at = TSR * 16 + self.sym[name] + plus
        if value is not None:
            self.mu.mem_write(at, struct.pack("<H", value))
        return struct.unpack("<H", self.mu.mem_read(at, 2))[0]

    def notes(self, at, n=1):
        return struct.unpack("<%dH" % n, self.mu.mem_read(at, 2 * n))

    def run_pass(self, flags):
        """The main loop's call: far pointers to x (CALLER:0) and y (CALLER:2) pushed, the INT and
        its "test ax,<segment>", then a HLT. The flags after it."""
        mu = self.mu
        code = bytes((0xCD, self.vec, 0xA9, 0, 0, 0xF4))
        mu.mem_write(CALLER * 16 + 0x100, code)
        mu.mem_write(SS * 16 + 0x800 - 8, struct.pack("<HHHH", 0, CALLER, 2, CALLER))
        for name, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800 - 8, ebp=td.BP,
                                eflags=flags | 2).items():
            mu.reg_write(getattr(td.r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(CALLER * 16 + 0x100, CALLER * 16 + 0x100 + len(code) - 1, count=2_000_000)
        self.assertEqual(mu.reg_read(td.r.UC_X86_REG_IP), 0x100 + len(code) - 1)  # (at the HLT)
        self.assertEqual(mu.reg_read(td.r.UC_X86_REG_SP), 0x800 - 8)
        self.assertEqual(self.notes(CALLER * 16, 2), (100, 100))  # (where the pointer is)
        return mu.reg_read(td.r.UC_X86_REG_EFLAGS)

    def test_redraw_with_interrupts_off(self):
        """The view drawn again in the pass (VIEW_REDRAW): with interrupts off though the caller had
        them on (DRAW_MASKED: no pointer drawn by the mouse's interrupt in the middle of it); the
        pointer read with them off, as the game's own routine reads it; the caller's flags back."""
        self.word("view_redraw", 1)
        flags = self.run_pass(IF)
        drew_flags, drew = self.notes(self.centre + 0x200, 2)
        self.assertEqual(drew, 1)
        self.assertFalse(drew_flags & IF, hex(drew_flags))
        read_flags, = self.notes(STUBS * 16 + 0x100)
        self.assertFalse(read_flags & IF, hex(read_flags))
        self.assertTrue(flags & IF)

    def test_off_when_the_caller_had_them_off(self):
        self.word("view_redraw", 1)
        flags = self.run_pass(0)
        drew_flags, drew = self.notes(self.centre + 0x200, 2)
        self.assertEqual(drew, 1)
        self.assertFalse(drew_flags & IF)
        self.assertFalse(flags & IF)

    def test_target_click_with_interrupts_off(self):
        """TARGET_CLICK's press and release reach the game's mouse handler with interrupts off (as
        the driver calls it), and the view is drawn with them off too (DRAW_MASKED)."""
        self.word("game_mask", 0x7F)
        self.word("hit_target", 5)
        self.mu.mem_write(GAME_DS * 16 + MAP_THINGS + 5 * 32 + 9, struct.pack("<HH", 150, 120))
        self.mu.mem_write(TSR * 16 + self.sym["t_click"], b"\x01")
        self.word("view_redraw", 1)
        self.run_pass(IF)
        handler_flags, calls = self.notes(STUBS * 16 + 0x102, 2)
        self.assertEqual(calls, 2)
        self.assertFalse(handler_flags & IF, hex(handler_flags))
        drew_flags, drew = self.notes(self.centre + 0x200, 2)
        self.assertEqual(drew, 1)
        self.assertFalse(drew_flags & IF)


if __name__ == "__main__":
    unittest.main()
