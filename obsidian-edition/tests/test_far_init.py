"""Where the helpers put their far block (FAR_INIT, DSCLOG2's and DSCLOG's): the HMA when XMS gives it
(or says there is none and it is all zero, as DOSBox 0.74 does), else a block of upper memory, else
of conventional memory, else nothing (CF, and the helper says so and is not loaded). Run in an
emulated CPU (needs unicorn and nasm, else skipped) with XMS (INT 2Fh, its entry point) and DOS's
memory calls (INT 21h 48h, 58h) played by the test, so each case DOSBox, DOSBox-X or a machine with
DOS=HIGH could give is driven: the HMA given, none (90h), in use (91h), A20 that won't come on,
no upper memory, too little memory.

The emulated CPU has no A20 gate: FFFFh:0010h is linear 100000h (A20 on); a case with A20 off
mirrors the HMA's first word onto 0000h:0000h, as the wrap does. INSTALL (the caller) and the HMA
handed back when A20 fails are DSCLOG2's (DSCLOG's install opens its files, and it keeps an HMA it
can't use: harmless in DOSBox, whose A20 always comes on)."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from unicorn import Uc, UC_ARCH_X86, UC_HOOK_INTR, UC_HOOK_MEM_WRITE, UC_MODE_16
    from unicorn import x86_const as r
    from test_dsclog_drawing import build
except ImportError:  # optional dependency
    Uc = None
import shutil

DOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos")
ASMS = {"DSCLOG2": os.path.join(DOS, "dsclog2.asm"), "DSCLOG": os.path.join(DOS, "dsclog.asm")}
PSP = 0x0FF0                    # (the image a paragraph block past its PSP, as DOS loads an EXE)
TSR = PSP + 0x10
ENV = 0x0F00
STACK_SEG = 0x3800
XMS_SEG, XMS_INT = 0x3F00, 0xF0  # the XMS entry point: INT F0h (the test's), RETF
HMA = 0x100000
CONV_SEG, UMB_SEG = 0x4000, 0xCA01  # where the test's DOS hands out blocks
HDR_FAR_SEG = 142
CF = 1


class Machine:
    """A helper's image loaded at TSR:0 with the test's XMS and DOS. xms: whether XMS is there;
    hma: 'given', or XMS's error for function 01h (90h none, 91h in use); a20: whether A20 comes
    on; hma_bytes: what the HMA holds (zero, or something else's); umb, conv: the paragraphs DOS
    has free in upper and conventional memory."""

    def __init__(self, asm, xms=True, hma="given", a20=True, hma_dirty=False, umb=0x2000, conv=0x8000):
        exe, self.sym = build(asm)
        image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]
        self.entry = struct.unpack_from("<HH", exe, 0x14)  # (IP, CS: DSCLOG2's install, a segment of its own)
        self.code = TSR + self.sym.get("INSTALL_PARAS", 0)  # (FAR_INIT's segment: the install's)
        self.xms, self.hma, self.a20, self.umb, self.conv = xms, hma, a20, umb, conv
        self.hma_owned = False
        self.a20_enabled = False
        self.xms_calls, self.allocs, self.printed, self.vectors_set = [], [], [], []
        self.exit = None
        self.link, self.strategy = 0, 0
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x110000)
        mu.mem_write(TSR * 16, image)
        mu.mem_write(PSP * 16, b"\xCD\x20" + b"\x00" * 0x2A + struct.pack("<H", ENV))
        mu.mem_write(XMS_SEG * 16, bytes((0xCD, XMS_INT, 0xCB)))
        mu.mem_write(HMA, b"\xA5" * 0x10000 if hma_dirty else bytes(0x10000))
        mu.mem_write(0, b"\x34\x12")
        if not a20:  # (A20 off: FFFFh:0010h is 0000h:0000h)
            mu.mem_write(HMA, b"\x34\x12")
            mu.hook_add(UC_HOOK_MEM_WRITE, self._wrap, begin=HMA, end=HMA + 1)
        mu.hook_add(UC_HOOK_INTR, self._int)

    def _wrap(self, mu, access, address, size, value, _):
        mu.mem_write(address - HMA, value.to_bytes(size, "little"))

    # the registers
    def reg(self, name):
        return self.mu.reg_read(getattr(r, "UC_X86_REG_" + name))

    def set(self, **regs):
        for name, value in regs.items():
            self.mu.reg_write(getattr(r, "UC_X86_REG_" + name), value)

    def carry(self, on):
        flags = self.reg("EFLAGS")
        self.set(EFLAGS=(flags | CF) if on else (flags & ~CF))

    def word(self, name):
        return struct.unpack("<H", self.mu.mem_read(TSR * 16 + self.sym[name], 2))[0]

    # the interrupts
    def _int(self, mu, intno, _):
        ax = self.reg("AX")
        ah, al = ax >> 8, ax & 0xFF
        if intno == 0x2F:
            if ax == 0x4300:
                self.set(AX=(ax & 0xFF00) | (0x80 if self.xms else 0))
            elif ax == 0x4310 and self.xms:
                self.set(ES=XMS_SEG, BX=0)
        elif intno == XMS_INT:
            self._xms(ah)
        elif intno == 0x21:
            self._dos(ah, al)
        else:
            raise AssertionError(f"INT {intno:02X}h")

    def _xms(self, ah):
        self.xms_calls.append(ah)
        bx = self.reg("BX") & 0xFF00
        if ah == 1:
            if self.hma == "given":
                self.hma_owned = True
                self.set(AX=1)
            else:
                self.set(AX=0, BX=bx | self.hma)
        elif ah == 2:
            ok = self.hma_owned
            self.hma_owned = False
            self.set(AX=int(ok), BX=bx | (0 if ok else 0x93))
        elif ah in (3, 5):
            self.a20_enabled = self.a20
            self.set(AX=int(self.a20), BX=bx | (0 if self.a20 else 0x82))
        elif ah in (4, 6):
            self.a20_enabled = False
            self.set(AX=1)
        else:
            raise AssertionError(f"XMS {ah:02X}h")

    def _dos(self, ah, al):
        bx = self.reg("BX")
        if ah == 0x48:
            upper_ok = self.link and self.strategy & 0xC0
            lower_ok = not (self.link and self.strategy & 0x40)
            for where, ok in (("umb", upper_ok), ("conv", lower_ok)):
                if ok and getattr(self, where) >= bx:
                    seg = (UMB_SEG if where == "umb" else CONV_SEG) + sum(
                        n + 1 for w, _, n in self.allocs if w == where)
                    setattr(self, where, getattr(self, where) - bx - 1)
                    self.allocs.append((where, seg, bx))
                    self.set(AX=seg)
                    self.carry(False)
                    return
            self.set(AX=8, BX=max(self.umb if upper_ok else 0, self.conv if lower_ok else 0))
            self.carry(True)
        elif ah == 0x58:
            if al == 0:
                self.set(AX=self.strategy)
            elif al == 1:
                self.strategy = bx
            elif al == 2:
                self.set(AX=(self.reg("AX") & 0xFF00) | self.link)
            elif al == 3:
                self.link = bx
            self.carry(False)
        elif ah == 0x35:
            self.set(ES=0, BX=0)
        elif ah == 0x25:
            self.vectors_set.append(al)
        elif ah in (0x49, 0x4A):
            self.carry(False)
        elif ah == 0x09:
            at = self.reg("DS") * 16 + self.reg("DX")
            text = bytes(self.mu.mem_read(at, 200)).split(b"$")[0]
            self.printed.append(text.decode("ascii", "replace").strip())
        elif ah in (0x4C, 0x31):
            self.exit = (ah, al)
            self.mu.emu_stop()
        else:
            raise AssertionError(f"INT 21h AH={ah:02X}h")

    # the runs
    def far_init(self):
        """FAR_INIT called (CS the install's, DS the image's segment): CF, and FAR_SEG."""
        self.set(CS=self.code, DS=TSR, ES=TSR, SS=STACK_SEG, SP=0x100)
        end = TSR * 16 + self.sym["far_init.ret"]
        self.mu.emu_start(TSR * 16 + self.sym["far_init"], end, count=2_000_000)
        self.assertion_at_end = self.reg("CS") * 16 + self.reg("IP") == end
        return bool(self.reg("EFLAGS") & CF), self.word("far_seg")

    def install(self):
        """The helper run as DOS starts an EXE (DS = ES = its PSP, CS:IP its header's), to its INT 21h 4Ch
        or 31h."""
        ip, cs = self.entry
        self.set(CS=TSR + cs, DS=PSP, ES=PSP, SS=STACK_SEG, SP=0x100)
        self.mu.emu_start((TSR + cs) * 16 + ip, 0, count=5_000_000)
        return self.exit


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class FarInitTests(unittest.TestCase):

    def each(self, helpers=tuple(ASMS), **kw):
        for name in helpers:
            asm = ASMS[name]
            with self.subTest(helper=name):
                yield name, Machine(asm, **kw)

    def far_bytes(self, m, seg):
        top = m.sym.get("FAR_TOP", m.sym.get("FAR_END"))
        return bytes(m.mu.mem_read(seg * 16 + m.sym["FAR_RING"], top - m.sym["FAR_RING"]))

    def test_the_hma_given(self):
        """XMS gives the HMA: FAR_SEG FFFFh, A20 on (XMS 03h), the block cleared, no DOS memory."""
        for _, m in self.each(hma="given", hma_dirty=True):
            carry, seg = m.far_init()
            self.assertTrue(m.assertion_at_end)
            self.assertEqual((carry, seg), (False, 0xFFFF))
            self.assertEqual(m.xms_calls, [1, 3])
            self.assertTrue(m.hma_owned and m.a20_enabled)
            self.assertEqual(m.allocs, [])
            self.assertEqual(self.far_bytes(m, 0xFFFF), bytes(len(self.far_bytes(m, 0xFFFF))))

    def test_no_hma_as_xms_has_it_but_unused(self):
        """DOSBox 0.74: XMS says there is no HMA (90h) though A20 and the memory work; all zero,
        so it is used."""
        for _, m in self.each(hma=0x90):
            carry, seg = m.far_init()
            self.assertEqual((carry, seg), (False, 0xFFFF))
            self.assertEqual(m.xms_calls, [1, 3])
            self.assertEqual(m.allocs, [])

    def test_no_hma_as_xms_has_it_and_something_there(self):
        """90h with something in the HMA (its owner not XMS's): left alone, upper memory instead."""
        for _, m in self.each(hma=0x90, hma_dirty=True):
            carry, seg = m.far_init()
            self.assertFalse(carry)
            self.assertEqual(m.allocs[0][0], "umb")
            self.assertEqual(seg, m.allocs[0][1] - 1)
            self.assertEqual(bytes(m.mu.mem_read(HMA + 0x10, 16)), b"\xA5" * 16)

    def test_the_hma_in_use_goes_to_upper_memory(self):
        """91h (DOS=HIGH, or another program has it): no A20 call, a block of upper memory, FAR_SEG
        a paragraph below it, cleared; DOS's link and strategy back as they were."""
        for _, m in self.each(hma=0x91):
            m.mu.mem_write(UMB_SEG * 16, b"\xEE" * 0x10000)
            carry, seg = m.far_init()
            self.assertFalse(carry)
            self.assertEqual(m.xms_calls, [1])
            self.assertEqual(len(m.allocs), 1)
            where, at, paras = m.allocs[0]
            self.assertEqual((where, seg), ("umb", at - 1))
            top = m.sym.get("FAR_TOP", m.sym.get("FAR_END"))
            self.assertGreaterEqual(paras * 16, top - m.sym["FAR_RING"])
            self.assertEqual(self.far_bytes(m, seg), bytes(len(self.far_bytes(m, seg))))
            self.assertEqual((m.link, m.strategy), (0, 0))

    def test_no_upper_memory_goes_to_conventional(self):
        for _, m in self.each(hma=0x91, umb=0):
            carry, seg = m.far_init()
            self.assertFalse(carry)
            self.assertEqual([w for w, _, _ in m.allocs], ["conv"])
            self.assertEqual(seg, CONV_SEG - 1)
            self.assertEqual((m.link, m.strategy), (0, 0))

    def test_upper_memory_too_small_goes_to_conventional(self):
        for _, m in self.each(hma=0x91, umb=0x0F00):
            carry, seg = m.far_init()
            self.assertFalse(carry)
            self.assertEqual([w for w, _, _ in m.allocs], ["conv"])

    def test_no_xms(self):
        """No XMS driver at all: no far call, upper memory."""
        for _, m in self.each(xms=False):
            carry, seg = m.far_init()
            self.assertFalse(carry)
            self.assertEqual(m.xms_calls, [])
            self.assertEqual(m.allocs[0][0], "umb")

    def test_too_little_memory(self):
        """No HMA and too little memory anywhere: CF, FAR_SEG still 0, nothing allocated."""
        for _, m in self.each(hma=0x91, umb=0x100, conv=0x100):
            carry, seg = m.far_init()
            self.assertTrue(m.assertion_at_end)
            self.assertEqual((carry, seg), (True, 0))
            self.assertEqual(m.allocs, [])
            self.assertEqual((m.link, m.strategy), (0, 0))

    def test_a20_refused_gives_the_hma_back(self):
        """XMS gives the HMA but A20 won't come on (03h fails): upper memory, and the HMA handed back
        (XMS 02h), not kept by a helper that never uses it."""
        for _, m in self.each(("DSCLOG2",), hma="given", a20=False):
            carry, seg = m.far_init()
            self.assertFalse(carry)
            self.assertEqual(m.allocs[0][0], "umb")
            self.assertEqual(m.xms_calls, [1, 3, 2])
            self.assertFalse(m.hma_owned)

    def test_a20_said_on_but_wrapping_gives_the_hma_back(self):
        """03h says yes but FFFFh:0010h is still 0000h:0000h (the wrap test): the interrupt vectors
        untouched, upper memory, the HMA handed back."""
        for _, m in self.each(("DSCLOG2",), hma="given", a20=False):
            m.a20 = True  # (XMS says yes; the mirror hook keeps the wrap)
            carry, seg = m.far_init()
            self.assertFalse(carry)
            self.assertEqual(bytes(m.mu.mem_read(0, 2)), b"\x34\x12")
            self.assertEqual(m.allocs[0][0], "umb")
            self.assertEqual(m.xms_calls[-1], 2)
            self.assertFalse(m.hma_owned)

    def test_install_without_memory_says_so_and_hooks_nothing(self):
        """The caller (INSTALL): with no room it says so and ends with 4C01h, no vector set, not
        resident."""
        for name, m in self.each(("DSCLOG2",), hma=0x91, umb=0x100, conv=0x100):
            self.assertEqual(m.install(), (0x4C, 1))
            self.assertEqual(m.vectors_set, [])
            self.assertTrue(any("no memory" in line for line in m.printed), m.printed)

    def test_install_in_the_hma_stays_resident(self):
        """And with the HMA: every vector set, resident (31h), the far block's segment FFFFh in the
        header."""
        for name, m in self.each(("DSCLOG2",), hma="given"):
            ah, _ = m.install()
            self.assertEqual(ah, 0x31)
            self.assertGreater(len(m.vectors_set), 3)
            self.assertEqual(struct.unpack("<H", m.mu.mem_read(TSR * 16 + HDR_FAR_SEG, 2))[0], 0xFFFF)

    def test_install_in_upper_memory_stays_resident(self):
        for name, m in self.each(("DSCLOG2",), hma=0x91):
            ah, _ = m.install()
            self.assertEqual(ah, 0x31)
            self.assertEqual(m.allocs[0][0], "umb")
            self.assertEqual(struct.unpack("<H", m.mu.mem_read(TSR * 16 + HDR_FAR_SEG, 2))[0],
                             m.allocs[0][1] - 1)


if __name__ == "__main__":
    unittest.main()
