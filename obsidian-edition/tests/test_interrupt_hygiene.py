"""DSCLOG's interrupt hygiene, in the emulator (the code audit of 2026-11-18, section 4): handlers
that end with RETF 2 or run the game's code leave interrupts as their caller had them (IF_FRAME),
not on whatever it had; INT33 forgets the game's mouse handler when the game takes it away or
resets the driver; the timer's tick clears the direction flag before what it runs copies, and puts
the interrupted code's back; the arrow pointer in scenes leaves the screen alone while the game
copies through the VGA's latches (VGA_LATCHED); and A20, checked each pass of the main loop, is
turned on again if it was found off (A20_CHECK)."""
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
from dsloader import heapcheck  # noqa: E402
from dsloader.gamepatch import VEC_ADND_SLOTS, VEC_CHUNK_ID, VEC_TICK  # noqa: E402

TSR, GAME_DS, SS, CALLER, IF, DF = td.TSR, td.GAME_DS, td.SS, td.CALLER, td.IF, td.DF
STUBS = 0x7800
CF, ZF = 0x01, 0x40
HDR_A20_LOST, HDR_FAR_SEG = heapcheck.TSR_A20_LOST, 142

# The mouse driver's stand-in (STUBS:0): counts its calls (0100h) and notes the last AX (0102h);
# function 3 gives (100, 100), no buttons. The game's mouse handler (HANDLER): notes its flags
# (0104h) and counts (0106h). XMS's (XMS): notes AH (0108h), AX 1.
STUB_ASM = """
bits 16
org 0
int33:  inc word [cs:0x100]
        mov [cs:0x102], ax
        cmp ax, 3
        jne .x
        xor bx, bx
        mov cx, 100
        mov dx, 100
.x:     iret
handler:
        push ax
        pushf
        pop ax
        mov [cs:0x104], ax
        inc word [cs:0x106]
        pop ax
        retf
xms:    mov [cs:0x108], ah
        mov ax, 1
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


def stub_at(label):
    """LABEL's offset in STUB_ASM's code."""
    return len(assemble(STUB_ASM.split(label + ":")[0]))


@unittest.skipIf(td.Uc is None or not tdd.shutil.which("nasm"), "needs unicorn and nasm")
class Base(unittest.TestCase):
    def setUp(self):
        self.image = td.load_image()
        _, self.sym = tdd.build()
        self.mu = mu = td.Uc(td.UC_ARCH_X86, td.UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        mu.hook_add(td.UC_HOOK_INTR, td.real_mode_interrupt)
        mu.mem_write(STUBS * 16, assemble(STUB_ASM))
        self.word("old33", 0)
        self.word("old33", STUBS, 2)
        self.hdr = TSR * 16 + self.image.find(td.HDR_SIG)

    def word(self, name, value=None, plus=0):
        at = TSR * 16 + self.sym[name] + plus
        if value is not None:
            self.mu.mem_write(at, struct.pack("<H", value))
        return struct.unpack("<H", self.mu.mem_read(at, 2))[0]

    def stub(self, at):
        return struct.unpack("<H", self.mu.mem_read(STUBS * 16 + at, 2))[0]

    def run_code(self, code, flags=2, **regs):
        """CODE at CALLER:100h, then a HLT; the flags after it."""
        mu = self.mu
        mu.mem_write(CALLER * 16 + 0x100, code + b"\xf4")
        for name, value in dict(dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800, ebp=td.BP, eflags=flags | 2),
                                **regs).items():
            mu.reg_write(getattr(td.r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(CALLER * 16 + 0x100, CALLER * 16 + 0x100 + len(code), count=200_000)
        self.assertEqual(mu.reg_read(td.r.UC_X86_REG_IP), 0x100 + len(code))  # (at the HLT)
        return mu.reg_read(td.r.UC_X86_REG_EFLAGS)

    def run_near(self, name, flags=2, **regs):
        """DSCLOG's near routine NAME, called from its segment (a CALL and a HLT where the install
        code was, at RESIDENT_END); the flags after it."""
        mu = self.mu
        at = self.sym["resident_end"]
        mu.mem_write(TSR * 16 + at, b"\xe8" + struct.pack("<H", (self.sym[name] - (at + 3)) & 0xFFFF) + b"\xf4")
        for name_, value in dict(dict(cs=TSR, ds=GAME_DS, ss=SS, esp=0x800, ebp=td.BP, eflags=flags | 2),
                                 **regs).items():
            mu.reg_write(getattr(td.r, "UC_X86_REG_" + name_.upper()), value)
        mu.emu_start(TSR * 16 + at, TSR * 16 + at + 3, count=200_000)
        self.assertEqual(mu.reg_read(td.r.UC_X86_REG_IP), at + 3)
        return mu.reg_read(td.r.UC_X86_REG_EFLAGS)


class Int33Tests(Base):
    """INT33 keeps the game's mouse handler (DSCLOG's MOUSE_EVENT in its place) and forgets it when
    the game takes it away (0Ch with CX 0) or resets the driver (00h, 21h): a nudge or Enter on an
    enemy pending then calls nothing (it called the stale pointer)."""

    def setUp(self):
        super().setUp()
        self.mu.mem_write(0x33 * 4, struct.pack("<HH", self.sym["int33"], TSR))

    def call33(self, ax, cx=0, es=0x1234, dx=0x5678):
        self.run_code(b"\xcd\x33", eax=ax, ecx=cx, edx=dx, es=es)

    def handler(self):
        return self.word("game_handler"), self.word("game_handler", plus=2), self.word("game_mask")

    def test_kept_then_forgotten(self):
        for ax, cx in ((0x0C, 0), (0x00, 0), (0x21, 0)):
            with self.subTest(ax=ax):
                self.call33(0x0C, 0x1F)
                self.assertEqual(self.handler(), (0x5678, 0x1234, 0x1F))
                self.assertEqual(self.stub(0x102), 0x0C)  # (the driver told: MOUSE_EVENT, all events)
                self.call33(0x03)
                self.assertEqual(self.handler(), (0x5678, 0x1234, 0x1F))  # (anything else: kept)
                calls = self.stub(0x100)
                self.call33(ax, cx)
                self.assertEqual(self.handler(), (0, 0, 0))
                self.assertEqual((self.stub(0x100), self.stub(0x102)), (calls + 1, ax))  # (on to the driver)


class IfFrameTests(Base):
    """Handlers that end with RETF 2 (their flags the caller's results) or call the game's code: the
    interrupt flag as their caller had it, on or off (they turned it on whatever it was, and the INT
    alone would leave it off)."""

    def test_retf_2_keeps_the_callers(self):
        """PROBE_CHUNK_ID (the chunk loader's stack check, "cmp [9Ch],sp"): its compare's flags, and
        IF as the caller's."""
        mu = self.mu
        mu.mem_write(VEC_CHUNK_ID * 4, struct.pack("<HH", self.sym["probe_chunk_id"], TSR))
        for caller_if in (0, IF):
            for limit, carry in ((0x900, CF), (0x100, 0)):  # (the routine's SP, 800h, below the limit: CF)
                with self.subTest(caller_if=caller_if, limit=limit):
                    mu.mem_write(GAME_DS * 16 + 0x9C, struct.pack("<H", limit))
                    flags = self.run_code(bytes((0xCD, VEC_CHUNK_ID, 0x90, 0x90)), caller_if)
                    self.assertEqual(flags & IF, caller_if)
                    self.assertEqual(flags & CF, 0 if carry else CF)  # ("cmp [9Ch],sp": limit - SP)
                    self.assertEqual(mu.reg_read(td.r.UC_X86_REG_SP), 0x800)

    def test_the_games_code_run_as_the_caller_had_it(self):
        """PROBE_ADND_SLOTS with its rule off calls the game's slot routine (the INT's return +
        SLOT_CALL): with interrupts on if the caller had them on, off if off."""
        mu = self.mu
        mu.mem_write(VEC_ADND_SLOTS * 4, struct.pack("<HH", self.sym["probe_adnd_slots"], TSR))
        slot_call = 0x5E4C2 - 0x5E242
        # the game's routine: its flags noted at CALLER:0, AX 7, RETF
        mu.mem_write(CALLER * 16 + 0x102 + slot_call, assemble(
            "bits 16\npush ax\npushf\npop ax\nmov [cs:0], ax\npop ax\nmov ax, 7\nretf\n"))
        mu.mem_write(SS * 16 + 0x700, bytes((5, 12)))  # (the level and WIS, at the near pointer)
        for caller_if in (0, IF):
            with self.subTest(caller_if=caller_if):
                # the arguments pushed (class 2, the pointer 700h, spell level 1), then the INT and
                # its NOPs at CALLER:100h (its way back 102h)
                mu.mem_write(SS * 16 + 0x7FA, struct.pack("<HHH", 2, 0x700, 1))
                flags = self.run_code(bytes((0xCD, VEC_ADND_SLOTS, 0x90, 0x90, 0x90)), caller_if, esp=0x7FA)
                noted, = struct.unpack("<H", mu.mem_read(CALLER * 16, 2))
                self.assertEqual(noted & IF, caller_if)
                self.assertEqual(flags & IF, caller_if)
                self.assertEqual(mu.reg_read(td.r.UC_X86_REG_AX), 7)


class TickTests(Base):
    """PROBE_TICK, the game's timer handler's first instruction: the direction flag cleared for what
    it runs (the box's nudge calls the game's mouse handler; the labels and the scenes' arrow copy),
    the interrupted code's back after it."""

    def test_nudge_with_the_direction_flag_clear(self):
        mu = self.mu
        mu.mem_write(VEC_TICK * 4, struct.pack("<HH", self.sym["probe_tick"], TSR))
        self.word("game_handler", stub_at("handler"))
        self.word("game_handler", STUBS, 2)
        self.word("game_mask", 0x7F)
        mu.mem_write(TSR * 16 + self.sym["box_nudge"], b"\x01")
        mu.mem_write(0x46C, struct.pack("<H", 1000))
        self.word("box_at", 990)
        mu.mem_write(CALLER * 16 + 0x600, bytes((0xCD, VEC_TICK, 0x90, 0x90, 0x90)))
        flags = self.run_code(bytes((0xCD, VEC_TICK, 0x90, 0x90, 0x90)), DF)
        self.assertEqual(self.stub(0x106), 1)  # (the game's handler told the pointer moved)
        self.assertFalse(self.stub(0x104) & DF)
        self.assertTrue(flags & DF)  # (the interrupted code's back)
        self.assertEqual(mu.mem_read(TSR * 16 + self.sym["box_nudge"], 1), b"\x00")


class VgaLatchTests(Base):
    """The scenes' arrow, moved from the timer, leaves the screen alone while the game writes
    through the VGA's latches (write mode 1-3, or a bit mask): its read of what is under the arrow
    would load them anew. The graphics controller's index as the game had it."""

    def setUp(self):
        super().setUp()
        self.gc = {5: 0x40, 8: 0xFF}
        self.gc_index = 4
        self.ports = []
        from unicorn import UC_HOOK_INSN
        from unicorn.x86_const import UC_X86_INS_IN, UC_X86_INS_OUT

        def port_in(uc, port, size, _):
            if port == 0x3CE:
                return self.gc_index
            if port == 0x3CF:
                return self.gc.get(self.gc_index, 0)
            return 0

        def port_out(uc, port, size, value, _):
            if port == 0x3CE:
                self.gc_index = value & 0xFF
                if size == 2:
                    self.gc[self.gc_index] = value >> 8
            elif port == 0x3CF:
                self.gc[self.gc_index] = value & 0xFF
            self.ports.append(port)

        self.mu.hook_add(UC_HOOK_INSN, port_in, None, 1, 0, UC_X86_INS_IN)
        self.mu.hook_add(UC_HOOK_INSN, port_out, None, 1, 0, UC_X86_INS_OUT)

    def test_latched(self):
        for mode, mask, latched in ((0x40, 0xFF, False), (0x41, 0xFF, True), (0x40, 0x0F, True), (0x42, 0xFF, True)):
            with self.subTest(mode=mode, mask=mask):
                self.gc.update({5: mode, 8: mask})
                self.gc_index = 4
                flags = self.run_near("vga_latched")
                self.assertEqual(not flags & ZF, latched)
                self.assertEqual(self.gc_index, 4)  # (the index put back)
                self.assertEqual((self.gc[5], self.gc[8]), (mode, mask))

    def test_arrow_left_while_latched(self):
        """CP_FOLLOW (its fourth strike, not a fresh draw): in write mode 1 it doesn't ask where the
        pointer is, nor touch the screen; in write mode 0 it does."""
        self.mu.mem_write(0x33 * 4, struct.pack("<HH", 0, STUBS))
        self.word("tick_count", 4)
        self.word("cp_x", 100)
        self.word("cp_y", 100)
        self.gc.update({5: 0x41})
        self.run_near("cp_follow")
        self.assertEqual(self.stub(0x100), 0)
        self.gc.update({5: 0x40})
        self.run_near("cp_follow")
        self.assertEqual(self.stub(0x100), 1)


class A20Tests(Base):
    """A20_CHECK, each pass of the main loop with the far block in the HMA: A20 found off (the HMA's
    first words the interrupt vectors', 1 MB wrapping to 0) is turned on again through XMS (03h)
    and counted in A20_LOST; with A20 on, nothing; with the far block elsewhere, nothing tried."""

    def setUp(self):
        super().setUp()
        self.a20 = False
        self.hma = bytearray(0x10000)
        mu = self.mu

        def read(uc, offset, size, _):
            if self.a20:
                return int.from_bytes(self.hma[offset:offset + size], "little")
            return int.from_bytes(bytes(uc.mem_read(offset, size)), "little")

        def write(uc, offset, size, value, _):
            data = value.to_bytes(size, "little")
            if self.a20:
                self.hma[offset:offset + size] = data
            else:
                uc.mem_write(offset, data)

        mu.mmio_map(0x100000, 0x10000, read, None, write, None)
        xms = stub_at("xms")

        def turn_on(uc, address, size, _):
            if uc.reg_read(td.r.UC_X86_REG_AH) == 3:
                self.a20 = True
        mu.hook_add(td.UC_HOOK_CODE, turn_on, None, STUBS * 16 + xms, STUBS * 16 + xms)
        self.word("xms", xms)
        self.word("xms", STUBS, 2)
        mu.mem_write(TSR * 16 + self.sym["far_seg"], struct.pack("<H", 0xFFFF))
        mu.mem_write(0, struct.pack("<HH", 0x1234, 0x5678))  # (INT 0's vector)

    def lost(self):
        return struct.unpack("<H", self.mu.mem_read(self.hdr + HDR_A20_LOST, 2))[0]

    def test_on_nothing_done(self):
        self.a20 = True
        flags = self.run_near("a20_check", IF)
        self.assertEqual((self.lost(), self.stub(0x108)), (0, 0))
        self.assertTrue(flags & IF)

    def test_off_turned_on_again(self):
        flags = self.run_near("a20_check", IF)
        self.assertTrue(self.a20)
        self.assertEqual((self.lost(), self.stub(0x108)), (1, 3))
        self.assertEqual(self.word("far_seg"), 0xFFFF)
        self.assertEqual(bytes(self.mu.mem_read(0, 4)), struct.pack("<HH", 0x1234, 0x5678))  # (vector 0 as it was)
        self.assertTrue(flags & IF)
        self.run_near("a20_check")
        self.assertEqual(self.lost(), 1)  # (on now: not counted again)

    def test_stays_off_far_block_given_up(self):
        """XMS can't turn it on: the far block's segments the ROM's (F000h), where writes go nowhere,
        not the vectors; 8000h in A20_LOST for the Loader's line."""
        self.word("xms", 0, 2)  # (no XMS to ask)
        self.run_near("a20_check")
        self.assertEqual(self.lost(), 0x8001)
        for name in ("far_seg", "ring_seg", "panel_seg", "sc_seg", "tbuf_seg"):
            self.assertEqual(self.word(name), 0xF000, name)
        self.assertEqual(heapcheck.a20_line(self.lost()), heapcheck.a20_line(heapcheck.A20_STUCK))

    def test_not_in_the_hma(self):
        self.mu.mem_write(TSR * 16 + self.sym["far_seg"], struct.pack("<H", 0xC000))
        self.run_near("a20_check")
        self.assertEqual((self.lost(), self.stub(0x108)), (0, 0))


if __name__ == "__main__":
    unittest.main()
