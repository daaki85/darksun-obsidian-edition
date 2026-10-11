"""Runs DSCLOG's interrupt handlers in a CPU emulator (needs `pip install unicorn`).

Checks its rand() returns what Borland's rand() returns, keeps the registers
the game relies on, and records the entries the companion decodes; and that
the probes do the game instructions they replace.
"""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dscompanion.dicelog import FILTERS, HDR_SIG, Entry
from dscompanion.textlog import TextBuffer
from dscompanion.gamepatch import (VEC_MC_ROLL, VEC_MC_CON, VEC_MC_UNCON, VEC_NO_CAST, VEC_CAN_USE, VEC_VIEW_DAM, VEC_DAM_LINE, VEC_SPEC_DAMAGE, VEC_ATTACKS, VEC_XP_NEXT, VEC_SCRIPT_RAND, VEC_ITEM_ARMOUR, VEC_ITEM_SKIP, VEC_ITEM_WEAPON, VEC_AC, VEC_DOUBLE, VEC_MSG, VEC_NEXT, VEC_RAND, VEC_RING_AC, VEC_USE_ITEM,
                                  VEC_RING_SAVE, VEC_SAVE, VEC_TEXT, VEC_TWO, VEC_GRACE_CAST, VEC_GRACE_EFFECT,
                                  VEC_GRACE_ABILITY, VEC_NAMES_FILL, VEC_NAMES_SIZE, VEC_STEALTH, VEC_TYPES_FILL,
                                  VEC_TYPES_SIZE, VEC_LEVEL, VEC_HD_ROLL, VEC_HD_CON, VEC_THIEF_SKILL, VEC_TWO_HANDED,
                                  VEC_SPELL_TEXT, VEC_CHUNK_ID)
from dscompanion import game, restrict, specialize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_restrict  # noqa: E402 (its item types and sheets)

try:
    from unicorn import Uc, UC_ARCH_X86, UC_HOOK_CODE, UC_HOOK_INTR, UC_HOOK_MEM_WRITE, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:  # optional dependency
    Uc = None

EXE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos", "DSCLOG.EXE")
TSR, GAME_DS, SS, CALLER, PARENT, RAND = 0x2000, 0x3000, 0x4000, 0x5000, 0x6000, 0x7000
RING_SEG = 0xC000  # where the tests put the ring (DSCLOG's install puts it past its image)
IF = 0x200  # the interrupt flag
# CHOOSE A SPELL as the tests' stand-in (at its stub, DS + 430Ah - 4356h : 5Ch): the call counted at
# DS:F000h, the spell levels on offer (preserver level 9, through PROBE_PICK_LEVEL) kept from DS:F002h,
# and a spell (20h on) learnt by member 3, unless DS:F010h is set (EXIT: nothing learnt, not counted)
PICK_STUB = "5350068b1e00f0b009cd%02x888702f0803e10f0007511ff0600f08cd82d560b8ec026c68726030107585bcb"
CR_TABLE = 0xE800  # (a creature table for PROBE_CR_SPELLS's tests, in the game's data segment)
KNOWN_3 = 0x168 + 3 * 0x8A  # member 3's known spells, from DS less 0B56h (DSCLOG's KNOWN_OFF)
BP, PARENT_BP = 0x1000, 0x1100


def borland_rand(seed):
    seed = (seed * 0x015A4E35 + 1) & 0xFFFFFFFF
    high = seed >> 16
    return seed, high & 0x7FFF, 0xFFFF if high & 0x8000 else 0


def load_image():
    with open(EXE, "rb") as f:
        exe = f.read()
    image = bytearray(exe[struct.unpack_from("<H", exe, 8)[0] * 16:])
    image[268:270] = struct.pack("<H", RING_SEG)  # (the ring's segment, as DSCLOG's install sets it)
    return bytes(image)


def fill_probes(image):
    """PROBE_NAMES_FILL and PROBE_TYPES_FILL, in that order: "add sp,0Ch", its three pushes back,
    then "or ax,ax" (other probes replace an "add sp,0Ch" the same way)."""
    import re
    return [m.start() - 15 for m in re.finditer(re.escape(bytes.fromhex("83c40c" "2eff36")), image)
            if image[m.start() + 18:m.start() + 20] == bytes.fromhex("09c0")]


def real_mode_interrupt(mu, intno, _):
    """Unicorn stops at INT; do what a real-mode CPU does: push FLAGS, CS, IP and jump via the IVT."""
    sp, ss = mu.reg_read(r.UC_X86_REG_SP), mu.reg_read(r.UC_X86_REG_SS)
    flags = mu.reg_read(r.UC_X86_REG_EFLAGS) & 0xFFFF
    frame = struct.pack("<HHH", mu.reg_read(r.UC_X86_REG_IP), mu.reg_read(r.UC_X86_REG_CS), flags)
    mu.mem_write(ss * 16 + sp - 6, frame)
    mu.reg_write(r.UC_X86_REG_SP, sp - 6)
    mu.reg_write(r.UC_X86_REG_EFLAGS, flags & ~(IF | 0x100))
    off, seg = struct.unpack("<HH", mu.mem_read(intno * 4, 4))
    mu.reg_write(r.UC_X86_REG_CS, seg)
    mu.reg_write(r.UC_X86_REG_IP, off)



def first_kit(sheet: bytes) -> int:
    """The sheet's first kit that counts (kitpages.kit_ids), or 0: a one-kit sheet's kit."""
    from dscompanion import kitpages
    ids = kitpages.kit_ids(sheet)
    return ids[0] if ids else 0


def any_kit(sheet: bytes) -> int:
    """The sheet's first kit, asleep or not, or 0."""
    from dscompanion import kitpages
    found = kitpages.kits_of(sheet)
    return found[0][0] if found else 0

class HeaderTests(unittest.TestCase):
    def test_built_in_filters_match_the_companion(self):
        image = load_image()
        hdr = struct.unpack_from("<H", image, 20)[0]
        self.assertEqual(image[hdr:hdr + 8], HDR_SIG)
        n = struct.unpack_from("<H", image, hdr + 32)[0]
        built_in = tuple(image[hdr + 34 + i * 9 + 1:hdr + 34 + i * 9 + 1 + image[hdr + 34 + i * 9]]
                         for i in range(n))
        self.assertEqual(built_in, FILTERS)
        self.assertEqual(tuple(image[hdr + 112:hdr + 117]), (VEC_RAND, VEC_SAVE, VEC_AC, VEC_TEXT, VEC_MSG))


@unittest.skipIf(Uc is None, "unicorn is not installed")
class StubTests(unittest.TestCase):
    def test_matches_borland_rand_and_logs_entries(self):
        image = load_image()
        hdr_off = struct.unpack_from("<H", image, 20)[0]
        ring = struct.unpack_from("<H", image, 16)[0]
        probe_save, probe_ac = struct.unpack_from("<HH", image, hdr_off + 108)
        int_rand = struct.unpack_from("<H", image, hdr_off + 118)[0]

        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, image)
        mu.mem_write(TSR * 16 + hdr_off + 32, struct.pack("<H", 0))  # no filters: record every call
        for vec, off in ((VEC_RAND, int_rand), (VEC_SAVE, probe_save), (VEC_AC, probe_ac)):
            mu.mem_write(vec * 4, struct.pack("<HH", off, TSR))
        mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        mu.mem_write(TSR * 16 + hdr_off + 24, struct.pack("<4H", 0x494A, 0, 0, 0))
        seed = 0x12345678
        mu.mem_write(GAME_DS * 16 + 0x4122, struct.pack("<I", seed))
        mu.mem_write(GAME_DS * 16 + 0x494A, struct.pack("<H", 0xBEEF))
        # the caller's frame: saved BP, return address into PARENT, arguments; its locals below BP
        mu.mem_write(SS * 16 + BP, struct.pack("<HHH", PARENT_BP, 0x40, PARENT) + bytes(range(1, 29)))
        mu.mem_write(SS * 16 + BP - 16, bytes(range(200, 216)))
        mu.mem_write(SS * 16 + PARENT_BP + 2, bytes(range(100, 132)))
        mu.mem_write(SS * 16 + PARENT_BP - 0x28, bytes(range(150, 190)))
        mu.mem_write(PARENT * 16 + 0x40, bytes(range(50, 66)))
        # the patched rand(): INT VEC_RAND; the caller: CALL FAR rand; then code the log copies
        mu.mem_write(RAND * 16 + 0x822, bytes((0xCD, VEC_RAND, 0x90, 0x90, 0x90)))
        call = b"\x9a" + struct.pack("<HH", 0x822, RAND)
        after = bytes(range(0x80, 0x98))
        mu.mem_write(CALLER * 16 + 0x10, call + after)

        for n in range(70):  # more than the ring holds
            mu.reg_write(r.UC_X86_REG_CS, CALLER)
            mu.reg_write(r.UC_X86_REG_DS, GAME_DS)
            mu.reg_write(r.UC_X86_REG_SS, SS)
            mu.reg_write(r.UC_X86_REG_ES, 0x1234)
            mu.reg_write(r.UC_X86_REG_ESP, 0x800)
            mu.reg_write(r.UC_X86_REG_EBP, BP)
            mu.reg_write(r.UC_X86_REG_EAX, 0xAAAA0000 | n)
            mu.reg_write(r.UC_X86_REG_ESI, 0x5151)
            mu.reg_write(r.UC_X86_REG_EDI, 0x7171)
            mu.reg_write(r.UC_X86_REG_EFLAGS, IF | 2)
            mu.emu_start(CALLER * 16 + 0x10, CALLER * 16 + 0x10 + len(call))
            self.assertTrue(mu.reg_read(r.UC_X86_REG_EFLAGS) & IF)  # interrupts are back on

            seed, value, dx = borland_rand(seed)
            self.assertEqual(mu.reg_read(r.UC_X86_REG_EAX), 0xAAAA0000 | value)
            self.assertEqual(mu.reg_read(r.UC_X86_REG_DX), dx)
            self.assertEqual(struct.unpack("<I", mu.mem_read(GAME_DS * 16 + 0x4122, 4))[0], seed)
            for reg, want in ((r.UC_X86_REG_SI, 0x5151), (r.UC_X86_REG_DI, 0x7171),
                              (r.UC_X86_REG_ES, 0x1234), (r.UC_X86_REG_DS, GAME_DS),
                              (r.UC_X86_REG_BP, BP), (r.UC_X86_REG_SP, 0x800)):
                self.assertEqual(mu.reg_read(reg), want)

            nent = struct.unpack("<H", mu.mem_read(TSR * 16 + hdr_off + 12, 2))[0]
            e = Entry.parse(bytes(mu.mem_read(RING_SEG * 16 + ring + (n % nent) * Entry.SIZE, Entry.SIZE)))
            self.assertEqual((e.seq, e.ip, e.cs, e.raw, e.bp, e.ss, e.ds, e.parent_bp),
                             (n + 1, 0x15, CALLER, value, BP, SS, GAME_DS, PARENT_BP))
            self.assertEqual(e.arg(2), 0x40)
            self.assertEqual(e.frame[4:], bytes(range(1, 29)))
            self.assertEqual(e.parent, bytes(range(100, 132)))
            self.assertEqual(e.glob, (0xBEEF, 0, 0, 0))
            self.assertEqual(e.locals, bytes(range(200, 216)))
            self.assertEqual(e.code, after)
            self.assertEqual(e.parent_code, bytes(range(50, 66)))
            self.assertEqual(e.parent_locals, bytes(range(150, 190)))

        seq, widx, nent = struct.unpack("<HHH", mu.mem_read(TSR * 16 + hdr_off + 8, 6))
        self.assertEqual((seq, widx), (70, 70 % nent))

        def call_with_filters(*filters):
            packed = b"".join(bytes([len(f)]) + f.ljust(8, b"\0") for f in filters)
            mu.mem_write(TSR * 16 + hdr_off + 32, struct.pack("<H", len(filters)) + packed)
            mu.reg_write(r.UC_X86_REG_CS, CALLER)
            mu.reg_write(r.UC_X86_REG_DS, GAME_DS)
            mu.reg_write(r.UC_X86_REG_SS, SS)
            mu.reg_write(r.UC_X86_REG_ESP, 0x800)
            mu.reg_write(r.UC_X86_REG_EBP, BP)
            mu.emu_start(CALLER * 16 + 0x10, CALLER * 16 + 0x10 + len(call))
            self.assertEqual(mu.reg_read(r.UC_X86_REG_SP), 0x800)
            self.assertEqual(mu.reg_read(r.UC_X86_REG_DS), GAME_DS)
            return struct.unpack("<H", mu.mem_read(TSR * 16 + hdr_off + 8, 2))[0], \
                struct.unpack("<H", mu.mem_read(TSR * 16 + hdr_off + 106, 2))[0]

        # no filter matches: the call is counted as skipped, not recorded, and rand() still works
        self.assertEqual(call_with_filters(b"\x11" * 8, after[:7] + b"\x00"), (70, 1))
        seed, value, _ = borland_rand(seed)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_AX), value)
        # the second filter matches: recorded
        self.assertEqual(call_with_filters(b"\x11" * 8, after[:8]), (71, 1))
        # a shorter filter matches on its own length
        self.assertEqual(call_with_filters(after[:3]), (72, 1))
        self.assertEqual(call_with_filters(after[:2] + b"\x00"), (72, 2))

        call_at = [0x400]

        def run_probe(vector, bp_bytes, si, rest=b"\x90\x90\x90\x90\xf4"):
            mu.mem_write(SS * 16 + BP - 8, bp_bytes)
            code = bytes((0xCD, vector)) + rest
            call_at[0] += 0x10  # fresh code each time: the emulator caches translated code
            at = call_at[0]
            mu.mem_write(CALLER * 16 + at, code)
            # the saving throw's "mov ax, <spell table segment>", where DSUN.EXE has it
            mu.mem_write(CALLER * 16 + at - (0x79BB7 - 0x79A85), struct.pack("<H", 0x3E56))
            mu.reg_write(r.UC_X86_REG_CS, CALLER)
            mu.reg_write(r.UC_X86_REG_DS, GAME_DS)
            mu.reg_write(r.UC_X86_REG_SS, SS)
            mu.reg_write(r.UC_X86_REG_ESP, 0x800)
            mu.reg_write(r.UC_X86_REG_EBP, BP)
            mu.reg_write(r.UC_X86_REG_ESI, si)
            mu.reg_write(r.UC_X86_REG_EBX, 0xB0B0)
            mu.reg_write(r.UC_X86_REG_EAX, 0x12340000)
            mu.reg_write(r.UC_X86_REG_EFLAGS, IF | 2)
            mu.emu_start(CALLER * 16 + at, CALLER * 16 + at + len(code) - 1)
            seq = struct.unpack("<H", mu.mem_read(TSR * 16 + hdr_off + 8, 2))[0]
            nent = struct.unpack("<H", mu.mem_read(TSR * 16 + hdr_off + 12, 2))[0]
            e = Entry.parse(bytes(mu.mem_read(RING_SEG * 16 + ring + ((seq - 1) % nent) * Entry.SIZE, Entry.SIZE)))
            return e

        # the save probe: [bp-2] = total 15, [bp-1] = needs 12 -> CMP leaves carry clear (JAE taken)
        e = run_probe(VEC_SAVE, bytes([0] * 6 + [15, 12]), 0x5151)
        self.assertEqual((e.kind, e.raw & 0xFF, e.raw >> 8, e.bp, e.extra), (1, 15, 12, BP, 0x3E56))
        self.assertTrue(mu.reg_read(r.UC_X86_REG_EFLAGS) & IF)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_AL), 15)
        self.assertFalse(mu.reg_read(r.UC_X86_REG_EFLAGS) & 1)
        self.assertEqual((mu.reg_read(r.UC_X86_REG_SI), mu.reg_read(r.UC_X86_REG_BX)), (0x5151, 0xB0B0))
        self.assertEqual(mu.reg_read(r.UC_X86_REG_SP), 0x800)
        e = run_probe(VEC_SAVE, bytes([0] * 6 + [9, 12]), 0x5151)
        self.assertTrue(mu.reg_read(r.UC_X86_REG_EFLAGS) & 1)  # 9 < 12: carry set, JAE not taken
        # the AC probe: [bp-6] = 7 and SI = -3 -> AX = 4
        e = run_probe(VEC_AC, bytes([0, 0, 7, 0, 0, 0, 0, 0]), 0xFFFD, rest=b"\x90\x90\x90\xf4")
        self.assertEqual((e.kind, e.raw, e.extra), (2, 4, 0))
        self.assertEqual(mu.reg_read(r.UC_X86_REG_AX), 4)
        self.assertEqual((mu.reg_read(r.UC_X86_REG_SI), mu.reg_read(r.UC_X86_REG_BX)), (0xFFFD, 0xB0B0))
        self.assertEqual(mu.reg_read(r.UC_X86_REG_SP), 0x800)


    def test_text_probes_copy_the_text_and_do_the_routines_prologue(self):
        image = load_image()
        hdr_off = struct.unpack_from("<H", image, 20)[0]
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, image)
        probe_text, probe_msg = struct.unpack_from("<HH", image, hdr_off + 132)
        for vec, off in ((VEC_TEXT, probe_text), (VEC_MSG, probe_msg)):
            mu.mem_write(vec * 4, struct.pack("<HH", off, TSR))
        mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        mu.mem_write(GAME_DS * 16 + 0x100, b"Do not worry, \0")
        mu.mem_write(GAME_DS * 16 + 0x200, b"Long Sword is broken !\0")
        buf = TextBuffer(lambda a, n: bytes(mu.mem_read(a, n)), TSR * 16 + hdr_off)

        def call(vector, args, at):
            # the routine starts with INT (was PUSH BP / MOV BP,SP) then a NOP; its caller's
            # return address and arguments are on the stack
            mu.mem_write(CALLER * 16 + at, bytes((0xCD, vector, 0x90, 0xF4)))
            mu.mem_write(SS * 16 + 0x800, struct.pack("<HH", 0x1234, 0x5678) + args)
            for reg, value in ((r.UC_X86_REG_CS, CALLER), (r.UC_X86_REG_SS, SS), (r.UC_X86_REG_DS, GAME_DS),
                               (r.UC_X86_REG_ESP, 0x800), (r.UC_X86_REG_EBP, BP), (r.UC_X86_REG_ESI, 0x5151),
                               (r.UC_X86_REG_EAX, 0xAAAA), (r.UC_X86_REG_EFLAGS, IF | 2)):
                mu.reg_write(reg, value)
            mu.emu_start(CALLER * 16 + at, CALLER * 16 + at + 3)
            # as if PUSH BP / MOV BP,SP had run
            self.assertEqual(mu.reg_read(r.UC_X86_REG_SP), 0x7FE)
            self.assertEqual(mu.reg_read(r.UC_X86_REG_BP), 0x7FE)
            self.assertEqual(struct.unpack("<H", mu.mem_read(SS * 16 + 0x7FE, 2))[0], BP)
            for reg, want in ((r.UC_X86_REG_SI, 0x5151), (r.UC_X86_REG_AX, 0xAAAA), (r.UC_X86_REG_DS, GAME_DS)):
                self.assertEqual(mu.reg_read(reg), want)
            self.assertTrue(mu.reg_read(r.UC_X86_REG_EFLAGS) & IF)
            return buf.poll()

        recs = call(VEC_TEXT, struct.pack("<HHHH", 1, 0, 0, 119), 0x100)  # a portrait
        self.assertEqual([(x.kind, x.value, x.text) for x in recs], [(1, 119, "")])
        recs = call(VEC_TEXT, struct.pack("<HHHH", 2, 0x100, GAME_DS, 115), 0x110)
        self.assertEqual([(x.kind, x.value, x.text) for x in recs], [(2, 115, "Do not worry, ")])
        recs = call(VEC_MSG, struct.pack("<HH", 0x200, GAME_DS), 0x120)
        self.assertEqual([(x.kind, x.text) for x in recs], [(16, "Long Sword is broken !")])
        # "show the replies" passes no pointer: whatever lies above its arguments is not text
        recs = call(VEC_TEXT, struct.pack("<HHHH", 3, 0x100, GAME_DS, 0), 0x130)
        self.assertEqual([(x.kind, x.text) for x in recs], [(3, "")])


@unittest.skipIf(Uc is None, "unicorn is not installed")
class NextTests(unittest.TestCase):
    """PROBE_NEXT, in the game's overlaid combat routine: it goes on where the compare and the
    JNE it replaces would have, by way of a frame the overlay manager can fix up while the
    turn's summary is up."""
    DLG = (GAME_DS + 0x42CA - 0x4356) & 0xFFFF  # the dialogue window's overlay stub
    MOVED = (0x7777, 0x0100)  # where the fake overlay manager says the combat routine is now

    def setUp(self):
        image = load_image()
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, image)
        self.hdr = TSR * 16 + image.find(HDR_SIG)
        handler = image.find(bytes.fromhex("fb66600689e3368b4722"))  # sti, pushad, push es, ...
        self.assertGreater(handler, 0)
        mu.mem_write(VEC_NEXT * 4, struct.pack("<HH", handler, TSR))
        mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        mu.mem_write(GAME_DS * 16 + 0x4979, struct.pack("<H", 44))  # a monster's turn now
        mu.mem_write(self.DLG * 16 + 0x25, b"\xCB")  # feeding the window: retf
        # waiting for Continue: the combat routine is moved meanwhile, and the overlay manager
        # fixes up the return address in the frame BP points at (push bp / mov bp,sp /
        # mov bx,[bp] / mov word [ss:bx+2],IP / mov word [ss:bx+4],CS / pop bp / retf)
        mu.mem_write(self.DLG * 16 + 0x34, bytes.fromhex("5589e58b5e00") + bytes.fromhex("36c74702") +
                     struct.pack("<H", self.MOVED[1]) + bytes.fromhex("36c74704") +
                     struct.pack("<H", self.MOVED[0]) + bytes.fromhex("5dcb"))

    def run_next(self, local, popups, until):
        """INT VEC_NEXT + 2 NOPs + the game's JNE +5 at CALLER:0600h, [BP-2] = LOCAL."""
        mu = self.mu
        mu.mem_write(CALLER * 16 + 0x600, bytes((0xCD, VEC_NEXT, 0x90, 0x90, 0x75, 0x05)))
        mu.mem_write(SS * 16 + BP - 2, struct.pack("<H", local))
        mu.mem_write(self.hdr + 140, struct.pack("<HH", 1, popups))  # the summary is ready
        msg = TSR * 16 + struct.unpack("<H", mu.mem_read(self.hdr + 144, 2))[0]
        mu.mem_write(msg, b"Slig attacks\0")
        regs = dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800, ebp=BP, eflags=IF | 2, eax=0x1111, ebx=0x2222,
                    ecx=0x3333, edx=0x4444, esi=0x5555, edi=0x6666, es=0x7070)
        for name, value in regs.items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(CALLER * 16 + 0x600, until[0] * 16 + until[1], count=200000)
        self.assertEqual((mu.reg_read(r.UC_X86_REG_CS), mu.reg_read(r.UC_X86_REG_IP)), until)
        kept = [name for name in regs if name not in ("cs", "eflags")]
        self.assertEqual([mu.reg_read(getattr(r, "UC_X86_REG_" + name.upper())) for name in kept],
                         [regs[name] for name in kept])

    def test_no_summary_goes_on_as_the_jump_would(self):
        self.run_next(0, popups=0, until=(CALLER, 0x606))  # [BP-2] = 0: past the JNE
        self.run_next(3, popups=0, until=(CALLER, 0x60B))  # not 0: to its target

    def test_back_where_the_overlay_manager_says(self):
        """The summary shown, the way back is the one the overlay manager left in the frame."""
        self.run_next(3, popups=1, until=self.MOVED)
        self.assertEqual(self.mu.mem_read(self.hdr + 138, 2), struct.pack("<H", 1))  # the turn counted


@unittest.skipIf(Uc is None, "unicorn is not installed")
class UseItemTests(unittest.TestCase):
    """PROBE_USE_ITEM, where the game uses the item on the pointer on what's under it: on as the
    compare and JNE it replaces would go, or, for the Ledger's thieving tools, to the routine's
    end (DSUN.EXE: 7361Ah, 7361Dh and 7371Dh, less the address after the INT)."""
    NONE, SOME, DONE = 0x605, 0x608, 0x602 + 0x106

    def setUp(self):
        image = load_image()
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, image)
        self.hdr = TSR * 16 + image.find(HDR_SIG)
        handler = image.find(bytes.fromhex("fb66600689e3ba0300"))  # sti, pushad, push es, mov bx,sp, mov dx,3
        self.assertGreater(handler, 0)
        mu.mem_write(VEC_USE_ITEM * 4, struct.pack("<HH", handler, TSR))
        mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        self.taken = 0

        def companion(uc, access, address, size, value, _):  # answers as soon as it's asked
            if address == self.hdr + 180:
                uc.mem_write(self.hdr + 182, struct.pack("<H", value))
                uc.mem_write(self.hdr + 186, struct.pack("<H", self.taken))
        mu.hook_add(UC_HOOK_MEM_WRITE, companion, begin=self.hdr + 180, end=self.hdr + 181)

    def run_use(self, si, until, on=1):
        mu = self.mu
        mu.mem_write(CALLER * 16 + 0x600, bytes((0xCD, VEC_USE_ITEM, 0x90, 0x90, 0x90)))
        mu.mem_write(self.hdr + 178, struct.pack("<H", on))
        mu.mem_write(TSR * 16 + struct.unpack("<H", mu.mem_read(self.hdr + 176, 2))[0], b"\0")
        for name, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800, ebp=BP, eflags=IF | 2, esi=si).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(CALLER * 16 + 0x600, CALLER * 16 + until, count=100000)
        self.assertEqual((mu.reg_read(r.UC_X86_REG_IP), mu.reg_read(r.UC_X86_REG_SP), mu.reg_read(r.UC_X86_REG_SI)),
                         (until, 0x800, si))

    def test_nothing_there(self):
        self.run_use(0xFFFF, self.NONE)

    def test_not_ours(self):
        """The Ledger is told what was used on what: the pointer's item 1, item 231 in the
        segment the routine's "mov dx,<segment>" (3FEh past the INT) loads."""
        mu = self.mu
        mu.mem_write(GAME_DS * 16 + 0x17A0, struct.pack("<h", 1))
        mu.mem_write(CALLER * 16 + 0x602 + 0x3FE, struct.pack("<H", 0x9000))
        mu.mem_write(0x9000 * 16 + 1 * 10 + 0x44, struct.pack("<H", 231))
        self.run_use(300, self.SOME, on=0)
        self.run_use(300, self.SOME)  # the Ledger says it's not its tools
        self.assertEqual(struct.unpack("<HH", mu.mem_read(self.hdr + 184, 2) + mu.mem_read(self.hdr + 188, 2)),
                         (300, 231))

    def test_the_tools(self):
        self.taken = 1
        self.run_use(300, self.DONE)

    def test_xp(self):
        """What was lifted is worth XP (Kurzak's sword): before its text, DSCLOG's GIVE_XP calls
        the game's routine for a quest's XP (who, amount) and plays the quest's sound, once."""
        mu, calls = self.mu, []
        image = load_image()
        xp_who = image.find(HDR_SIG) + 262
        give_xp = image.find(bytes.fromhex("2e833e") + struct.pack("<H", xp_who) + bytes.fromhex("ff74"))
        self.assertGreater(give_xp, 0)
        to_game = GAME_DS - 0x4356  # (the game's segments, from its DS)
        xp, sound = (to_game + 0x4251) * 16 + 0x005C, (to_game + 0x1A0A) * 16 + 0x0663
        for at in (xp, sound):
            mu.mem_write(at, b"\xcb")  # retf

        def called(uc, address, size, _):
            sp = uc.reg_read(r.UC_X86_REG_SS) * 16 + uc.reg_read(r.UC_X86_REG_SP)
            args = struct.unpack("<HH", uc.mem_read(sp + 4, 4))
            calls.append(("xp", args) if address == xp else ("sound", args[:1]))
        mu.hook_add(UC_HOOK_CODE, called, begin=xp, end=xp)
        mu.hook_add(UC_HOOK_CODE, called, begin=sound, end=sound)
        back = 0xE000  # (past the image: where its RET comes back to)

        def run():
            for name, value in dict(cs=TSR, ds=GAME_DS, ss=SS, esp=0x7FE, ebp=BP).items():
                mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
            mu.mem_write(SS * 16 + 0x7FE, struct.pack("<H", back))
            mu.emu_start(TSR * 16 + give_xp, TSR * 16 + back, count=10000)
            self.assertEqual((mu.reg_read(r.UC_X86_REG_IP), mu.reg_read(r.UC_X86_REG_SP)), (back, 0x800))
        mu.mem_write(self.hdr + 262, struct.pack("<HH", 3, 200))  # Cilla (3), 200
        run()
        self.assertEqual(calls, [("xp", (3, 200)), ("sound", (53,))])
        self.assertEqual(struct.unpack("<H", mu.mem_read(self.hdr + 262, 2))[0], 0xFFFF)
        run()
        self.assertEqual(len(calls), 2)  # (asked for once)


@unittest.skipIf(Uc is None, "unicorn is not installed")
class PickKeyTests(unittest.TestCase):
    """PROBE_PICK, where the conversation window passes on a key it doesn't know: P asks the
    Ledger to pick a pocket only with that switched on too (bit 1), not for the tools alone."""
    JUMP = 0x7DD70 - 0x7D9FF

    def setUp(self):
        from dscompanion.gamepatch import VEC_PICK
        image = load_image()
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, image)
        self.hdr = TSR * 16 + image.find(HDR_SIG)
        handler = image.find(bytes.fromhex("fb66600689e3368147"))  # sti, pushad, push es, mov bx,sp, add [ss:bx+..]
        self.assertGreater(handler, 0)
        mu.mem_write(VEC_PICK * 4, struct.pack("<HH", handler, TSR))
        mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)

        def companion(uc, access, address, size, value, _):  # answers at once, with nothing to show
            uc.mem_write(self.hdr + 174, struct.pack("<H", value))
        mu.hook_add(UC_HOOK_MEM_WRITE, companion, begin=self.hdr + 172, end=self.hdr + 173)
        mu.mem_write(TSR * 16 + struct.unpack("<H", mu.mem_read(self.hdr + 176, 2))[0], b"\0")

    def press(self, key, on):
        mu = self.mu
        mu.mem_write(CALLER * 16 + 0x600, bytes((0xCD, 0xFC, 0x90)))
        mu.mem_write(self.hdr + 178, struct.pack("<H", on))
        mu.mem_write(SS * 16 + BP - 0x0C, struct.pack("<H", key))
        for name, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800, ebp=BP, eflags=IF | 2).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        before = struct.unpack("<H", mu.mem_read(self.hdr + 172, 2))[0]
        mu.emu_start(CALLER * 16 + 0x600, CALLER * 16 + 0x602 + self.JUMP, count=200000)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_IP), 0x602 + self.JUMP)
        return struct.unpack("<H", mu.mem_read(self.hdr + 172, 2))[0] != before

    def test_p_only_with_its_switch(self):
        P = 0x1950
        self.assertFalse(self.press(P, 0))
        self.assertFalse(self.press(P, 1))  # (the tools only)
        self.assertTrue(self.press(P, 3))
        self.assertTrue(self.press(0x1970, 3))  # (p too)
        self.assertFalse(self.press(0x1E41, 3))  # (another key)


@unittest.skipIf(Uc is None, "unicorn is not installed")
class BeltTests(unittest.TestCase):
    """PROBE_BELT, at the end of the game's thief skill routine (where "mov ax,si" was): a thief
    wearing a belt gets 5 more to pick pockets and open locks, with SKILLS_ON's belt bit."""
    CREATURES, ITEMS = 0x9000, 0xA000
    DS = 0x8000  # (the game's DS: its things table, 9E4h paragraphs below, clear of DSCLOG's image)

    def setUp(self):
        from dscompanion.gamepatch import VEC_BELT
        image = load_image()
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, image)
        self.hdr = TSR * 16 + image.find(HDR_SIG)
        handler = image.find(bytes.fromhex("fb89f0837e0a00"))
        self.assertGreater(handler, 0)
        mu.mem_write(VEC_BELT * 4, struct.pack("<HH", handler, TSR))
        mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        mu.mem_write(self.DS * 16 + 0x1665, struct.pack("<HH", 0, self.CREATURES))
        mu.mem_write(self.DS * 16 + 0x165D, struct.pack("<HH", 0, self.ITEMS))
        things = (self.DS + 0x3972 - 0x4356) * 16 + 0xC36  # (the things table, from the game's DS)
        # object 3: creature 1, whose first list is object 10: item 4
        for thing, kind, index in ((3, 2, 1), (10, 1, 4)):
            mu.mem_write(things + thing * 3, struct.pack("<BH", kind, index))
        mu.mem_write(self.CREATURES * 16 + 0x3A + 8, struct.pack("<HHH", 10, 9999, 9999))
        self.wear(5)

    def wear(self, slot):
        rec = bytearray(21)
        struct.pack_into("<H", rec, 4, 9999)
        rec[0x11] = slot
        self.mu.mem_write(self.ITEMS * 16 + 4 * 21, bytes(rec))

    def chance(self, skill, on=2, si=40):
        mu = self.mu
        mu.mem_write(self.hdr + 266, struct.pack("<H", on))
        mu.mem_write(SS * 16 + BP + 8, struct.pack("<I", skill))
        mu.mem_write(CALLER * 16 + 0x600, bytes((0xCD, 0xD9)))
        for name, value in dict(cs=CALLER, ds=self.DS, ss=SS, esp=0x800, ebp=BP, eflags=IF | 2,
                                esi=si, edi=3, ebx=0x1234, ecx=0x5678, edx=0x9ABC, es=0x4444).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(CALLER * 16 + 0x600, CALLER * 16 + 0x602, count=10000)
        self.assertEqual([mu.reg_read(x) for x in (r.UC_X86_REG_SP, r.UC_X86_REG_SI, r.UC_X86_REG_DI, r.UC_X86_REG_BX,
                                                   r.UC_X86_REG_CX, r.UC_X86_REG_DX, r.UC_X86_REG_ES)],
                         [0x800, si, 3, 0x1234, 0x5678, 0x9ABC, 0x4444])
        return mu.reg_read(r.UC_X86_REG_AX)

    def test_pockets_and_locks(self):
        self.assertEqual([self.chance(skill) for skill in range(4)], [45, 45, 40, 40])

    def test_off(self):
        self.assertEqual(self.chance(0, on=1), 40)  # (the stealth bit alone)
        self.assertEqual(self.chance(0, on=0), 40)

    def test_no_belt(self):
        self.wear(20)  # (in the pack)
        self.assertEqual(self.chance(1), 40)

    def test_assassin(self):
        """An Assassin (kits on): 15 less to pick pockets and open locks (kits.thief_skill), the
        belt's 5 still added, never below 0."""
        from dscompanion import kits
        sheets = 0xB000
        self.mu.mem_write(self.DS * 16 + 0x1661, struct.pack("<HH", 0, sheets))
        self.mu.mem_write(self.CREATURES * 16 + 0x3A + 4, struct.pack("<H", 2))  # (creature 1: sheet 2)
        sheet = bytearray(game.SHEET_SIZE)
        sheet[0x21], sheet[0x43] = 17, 2
        self.mu.mem_write(sheets * 16 + 2 * 0x47, bytes(sheet))
        self.mu.mem_write(self.hdr + 270, struct.pack("<H", 1))
        self.assertEqual([self.chance(skill) for skill in range(4)], [30, 30, 40, 40])
        self.assertEqual(self.chance(0, si=5), 0)
        self.assertEqual(self.chance(0, on=0), 25)
        self.assertEqual([kits.thief_skill(kits.ASSASSIN, k) for k in range(4)], [-15, -15, 0, 0])

    def test_swashbuckler(self):
        """A Swashbuckler (kits on): 10 less to every skill (kits.thief_skill), the belt's 5 still
        added to pick pockets and open locks, never below 0; kits off, none."""
        from dscompanion import kits
        sheets = 0xB000
        self.mu.mem_write(self.DS * 16 + 0x1661, struct.pack("<HH", 0, sheets))
        self.mu.mem_write(self.CREATURES * 16 + 0x3A + 4, struct.pack("<H", 2))
        sheet = bytearray(game.SHEET_SIZE)
        sheet[0x21], sheet[0x43] = 17, 1
        self.mu.mem_write(sheets * 16 + 2 * 0x47, bytes(sheet))
        self.mu.mem_write(self.hdr + 270, struct.pack("<H", 1))
        self.assertEqual([self.chance(skill) for skill in range(8)], [35, 35, 30, 30, 30, 30, 30, 30])
        self.assertEqual(self.chance(4, si=5), 0)
        self.mu.mem_write(self.hdr + 270, struct.pack("<H", 0))
        self.assertEqual([self.chance(skill) for skill in range(5)], [45, 45, 40, 40, 40])
        self.assertEqual({kits.thief_skill(kits.SWASHBUCKLER, k) for k in range(8)}, {-10})


@unittest.skipIf(Uc is None, "unicorn is not installed")
class RingTests(unittest.TestCase):
    """The ring probes: a worn ring's plus counts for AC and (all worn rings) on saves."""
    THINGS_SEG, CREATURES, ITEMS, TYPES = 0x8000, 0x9000, 0xA000, 0xB000

    def setUp(self):
        image = load_image()
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, image)
        # the handlers aren't in the header: find them by their first instructions
        ac = image.find(bytes.fromhex("268a470f98" "83f966"))
        save = image.find(bytes.fromhex("5589e5505351520631f6c45e02"))
        self.assertGreater(min(ac, save), 0)
        mu.mem_write(VEC_RING_AC * 4, struct.pack("<HH", ac, TSR))
        mu.mem_write(VEC_RING_SAVE * 4, struct.pack("<HH", save, TSR))
        mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        mu.mem_write(GAME_DS * 16 + 0x1665, struct.pack("<HH", 0, self.CREATURES))
        mu.mem_write(GAME_DS * 16 + 0x165D, struct.pack("<HH", 0, self.ITEMS))
        things = self.THINGS_SEG * 16 + 0xC36
        # object 3: creature 1, whose lists start at objects 10 (item 4, then 5) and 11 (item 7)
        for thing, kind, index in ((3, 2, 1), (10, 1, 4), (11, 1, 7), (12, 1, 5)):
            mu.mem_write(things + thing * 3, struct.pack("<BH", kind, index))
        mu.mem_write(self.CREATURES * 16 + 0x3A + 8, struct.pack("<HHH", 10, 9999, 11))
        # items: type, slot, plus, next
        for item, typ, slot, plus, nxt in ((4, 102, 4, 1, 5), (5, 102, 0xFF, 2, 9999), (7, 102, 4, 2, 9999)):
            rec = bytearray(21)
            struct.pack_into("<H", rec, 4, nxt)
            struct.pack_into("<H", rec, 0x0A, typ)
            rec[0x11], rec[0x14] = slot, plus
            mu.mem_write(self.ITEMS * 16 + item * 21, bytes(rec))
        self.at = 0x600

    def run_at(self, code, **regs):
        mu = self.mu
        self.at += 0x20
        mu.mem_write(CALLER * 16 + self.at, code)
        for name, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800, ebp=BP, eflags=IF | 2, **regs).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(CALLER * 16 + self.at, CALLER * 16 + self.at + 2)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_SP), 0x800)

    def save(self, thing):
        """INT VEC_RING_SAVE where "xor si,si" was, then the code after it in the game."""
        code = bytes((0xCD, VEC_RING_SAVE)) + bytes.fromhex("8bdf6bdb03b8") + struct.pack("<H", self.THINGS_SEG)
        self.run_at(code, edi=thing, esi=0x5555, eax=0x1111, ebx=0x2222, ecx=0x3333, edx=0x4444, es=0x6666)
        mu = self.mu
        self.assertEqual([mu.reg_read(x) for x in (r.UC_X86_REG_AX, r.UC_X86_REG_BX, r.UC_X86_REG_CX,
                                                   r.UC_X86_REG_DX, r.UC_X86_REG_ES, r.UC_X86_REG_DI,
                                                   r.UC_X86_REG_BP, r.UC_X86_REG_DS)],
                         [0x1111, 0x2222, 0x3333, 0x4444, 0x6666, thing, BP, GAME_DS])
        return mu.reg_read(r.UC_X86_REG_SI)

    def test_saves_count_worn_rings(self):
        self.assertEqual(self.save(3), 3)  # items 4 and 7 (+1, +2); item 5 is only carried

    def test_saves_not_a_creature(self):
        self.assertEqual(self.save(10), 0)

    def test_saves_count_a_cloak_of_protection(self):
        """Item 7 made a cloak of protection (+2, the second of DSCLOG's types) worn on the back:
        counted once the types are in (TYPES_FIRST, the header's +212), with ring 4's +1."""
        mu = self.mu
        rec = self.ITEMS * 16 + 7 * 21
        mu.mem_write(rec + 0x0A, struct.pack("<H", 116))
        mu.mem_write(rec + 0x11, bytes([12]))
        hdr = TSR * 16 + load_image().find(HDR_SIG)
        self.assertEqual(self.save(3), 1)  # no types yet: the ring alone
        mu.mem_write(hdr + 212, struct.pack("<H", 115))
        self.assertEqual(self.save(3), 3)
        mu.mem_write(rec + 0x11, bytes([0xFF]))  # only carried
        self.assertEqual(self.save(3), 1)

    def test_saves_count_a_robe(self):
        """Item 7 made a robe (robes.py: TYPES_FIRST + 25) worn on the chest: the Veiled Robe (+2)
        +1 on every save, the Ashen Robe (+1) against a wizard's or priest's spell (0-137) alone;
        with ring 4's +1. (KIT_SAVE's things table: the game's DS less 9E4h paragraphs.)"""
        mu = self.mu
        things = (GAME_DS - 0x9E4) * 16 + 0xC36
        for thing, kind, index in ((3, 2, 1), (10, 1, 4), (11, 1, 7), (12, 1, 5)):
            mu.mem_write(things + thing * 3, struct.pack("<BH", kind, index))
        rec = self.ITEMS * 16 + 7 * 21
        mu.mem_write(rec + 0x0A, struct.pack("<H", 115 + 25))
        mu.mem_write(rec + 0x11, bytes([9]))
        mu.mem_write(TSR * 16 + load_image().find(HDR_SIG) + 212, struct.pack("<H", 115))
        for plus, spell, want in ((2, 10, 2), (2, 200, 2), (1, 10, 2), (1, 200, 1), (1, 137, 2)):
            with self.subTest(plus=plus, spell=spell):
                mu.mem_write(rec + 0x14, bytes([plus]))
                mu.mem_write(SS * 16 + BP + 0x14, struct.pack("<H", spell))
                self.assertEqual(self.save(3), want)
        mu.mem_write(rec + 0x11, bytes([0xFF]))  # only carried
        self.assertEqual(self.save(3), 1)

    def test_ac_counts_rings(self):
        """AX gets the type's flags (sign-extended); bit 80h is set for the ring type."""
        mu = self.mu
        for typ, flags, want in ((102, 0x00, 0x0080), (6, 0x80, 0xFF80), (6, 0x00, 0), (102, 0x02, 0x0082)):
            mu.mem_write(self.TYPES * 16 + 0x0F, bytes([flags]))
            self.run_at(bytes((0xCD, VEC_RING_AC)), es=self.TYPES, ebx=0, ecx=typ, eax=0x1234)
            self.assertEqual(mu.reg_read(r.UC_X86_REG_AX), want)
            self.assertEqual((mu.reg_read(r.UC_X86_REG_CX), mu.reg_read(r.UC_X86_REG_BX)), (typ, 0))



@unittest.skipIf(Uc is None, "unicorn is not installed")
class ProtectionRuleTests(RingTests):
    """RULE_PROTECTION: the better ring only, a ring's AC lost to magical armour, a cloak of
    protection lost to magical or metal armour (helms too) or a shield."""
    RULES, TYPES_FIRST = 170, 212  # the header's words
    CLOAK = 116  # (the second of DSCLOG's types, the first being 115)
    # (RingTests' own are the game's way, without the rule)
    test_saves_count_worn_rings = test_saves_count_a_cloak_of_protection = test_ac_counts_rings = None

    def setUp(self):
        super().setUp()
        mu = self.mu
        hdr = TSR * 16 + load_image().find(HDR_SIG)
        mu.mem_write(hdr + self.RULES, struct.pack("<H", 1024))
        mu.mem_write(hdr + self.TYPES_FIRST, struct.pack("<H", 115))
        mu.mem_write(GAME_DS * 16 + 0x1669, struct.pack("<HH", 0, self.TYPES))
        # types: flags word, material (+08h), AC flag (+0Fh)
        for typ, flags, material, ac in ((4, 4, 5, 0x80), (6, 0, 5, 0x80), (57, 0, 4, 0x80), (89, 0, 0x84, 0x84),
                                         (15, 0, 1, 0x80), (self.CLOAK, 0, 5, 0x80), (102, 0, 0x40, 0)):
            rec = bytearray(0x14)
            struct.pack_into("<H", rec, 0, flags)
            rec[0x08], rec[0x0F] = material, ac
            mu.mem_write(self.TYPES * 16 + typ * 0x14, bytes(rec))
        self.wear(7, 102, 11, 2)  # creature 1: ring 4 (+1) on the left hand's finger, ring 7 (+2) the right's

    def wear(self, item, typ, slot, plus=0):
        rec = self.ITEMS * 16 + item * 21
        self.mu.mem_write(rec + 0x0A, struct.pack("<H", typ))
        self.mu.mem_write(rec + 0x11, bytes([slot]))
        self.mu.mem_write(rec + 0x14, bytes([plus & 0xFF]))

    def counts(self, item, typ):
        """INT VEC_RING_AC for creature 1's item ITEM of type TYPE: whether bit 80h is left set
        (the things table's segment where the game's code has it, A8h bytes past the INT)."""
        self.mu.mem_write(CALLER * 16 + self.at + 0x20 + 2 + 0xA8, struct.pack("<H", self.THINGS_SEG))
        self.run_at(bytes((0xCD, VEC_RING_AC)), es=self.TYPES, ebx=typ * 0x14, ecx=typ, edx=item, edi=3,
                    eax=0x1234)
        mu = self.mu
        self.assertEqual([mu.reg_read(x) for x in (r.UC_X86_REG_BX, r.UC_X86_REG_CX, r.UC_X86_REG_DX,
                                                   r.UC_X86_REG_DI, r.UC_X86_REG_ES)],
                         [typ * 0x14, typ, item, 3, self.TYPES])
        return bool(mu.reg_read(r.UC_X86_REG_AX) & 0x80)

    def test_the_better_ring(self):
        self.assertEqual((self.counts(4, 102), self.counts(7, 102)), (False, True))
        self.assertEqual(self.save(3), 2)
        self.wear(7, 102, 11, 1)  # equal: the left hand's
        self.assertEqual((self.counts(4, 102), self.counts(7, 102)), (True, False))
        self.assertEqual(self.save(3), 1)

    def test_rule_off(self):
        self.mu.mem_write(TSR * 16 + load_image().find(HDR_SIG) + self.RULES, struct.pack("<H", 0))
        self.assertEqual((self.counts(4, 102), self.counts(7, 102)), (True, True))
        self.assertEqual(self.save(3), 3)

    def test_ring_ac_lost_to_magical_armour(self):
        self.wear(5, 6, 9, 1)  # leather chest armour +1 worn
        self.assertEqual((self.counts(4, 102), self.counts(7, 102)), (False, False))
        self.assertEqual(self.save(3), 2)  # (the saves stay)

    def test_cloak(self):
        self.wear(7, self.CLOAK, 12, 1)
        self.wear(5, 15, 9)  # bone scale: natural
        self.assertTrue(self.counts(7, self.CLOAK))
        self.assertEqual(self.save(3), 2)  # ring 4 and the cloak
        for typ, slot, plus in ((57, 9, 0), (6, 9, 1), (4, 10, 0), (4, 3, 0), (89, 7, 0), (6, 7, 1)):
            self.wear(5, typ, slot, plus)  # metal, magical leather, a shield in either hand, metal or magic helm
            self.assertFalse(self.counts(7, self.CLOAK), (typ, slot, plus))
            self.assertEqual(self.save(3), 1, (typ, slot, plus))
        self.wear(5, 57, 0xFF)  # only carried
        self.assertTrue(self.counts(7, self.CLOAK))


@unittest.skipIf(Uc is None, "unicorn is not installed")
class BracersTests(ProtectionRuleTests):
    """Bracers of defense (the ninth of DSCLOG's types, worn in the arm armour's slot): their plus
    counts for AC without armour on the arms, legs, head or chest, with or without RULE_PROTECTION,
    and they aren't armour to a ring's or cloak's rule."""
    BRACERS = 123
    test_the_better_ring = test_rule_off = test_ring_ac_lost_to_magical_armour = test_cloak = None

    def setUp(self):
        super().setUp()
        rec = bytearray(0x14)
        rec[0x08], rec[0x09], rec[0x0F] = 0x40, 3, 0x80
        self.mu.mem_write(self.TYPES * 16 + self.BRACERS * 0x14, bytes(rec))
        self.wear(7, self.BRACERS, 0, 4)  # creature 1: ring 4 (+1) on a finger, the bracers on the arms

    def test_alone(self):
        self.assertTrue(self.counts(7, self.BRACERS))
        self.assertTrue(self.counts(4, 102))  # (not magical armour: the ring counts)

    def test_lost_to_armour(self):
        for typ, slot, plus in ((6, 9, 0), (15, 6, 0), (57, 9, 1), (89, 7, 0)):  # leather, bone scale
            self.wear(5, typ, slot, plus)  # legs, metal +1, a helm
            self.assertFalse(self.counts(7, self.BRACERS), (typ, slot))
        self.wear(5, 4, 10)  # a shield: they stay
        self.assertTrue(self.counts(7, self.BRACERS))
        self.wear(5, 6, 0xFF)  # armour only carried
        self.assertTrue(self.counts(7, self.BRACERS))

    def test_without_the_rule(self):
        self.mu.mem_write(TSR * 16 + load_image().find(HDR_SIG) + self.RULES, struct.pack("<H", 0))
        self.wear(5, 6, 9)
        self.assertFalse(self.counts(7, self.BRACERS))
        self.wear(5, 6, 0xFF)
        self.assertTrue(self.counts(7, self.BRACERS))

    def test_not_before_the_types(self):
        """Before DSCLOG's types are in, type 123 is nothing of its own: the game's way."""
        self.mu.mem_write(TSR * 16 + load_image().find(HDR_SIG) + self.TYPES_FIRST, struct.pack("<H", 0))
        self.wear(5, 6, 9)
        self.assertTrue(self.counts(7, self.BRACERS))


@unittest.skipIf(Uc is None, "unicorn is not installed")
class RobeTests(BracersTests):
    """The robes (robes.py: the 26th of DSCLOG's types, worn on the chest): as the bracers, their
    plus counts for AC without armour on the arms, legs or head, and they aren't armour."""
    BRACERS = 140

    def setUp(self):
        ProtectionRuleTests.setUp(self)
        rec = bytearray(0x14)
        rec[0x08], rec[0x09], rec[0x0F] = 0x40, 1, 0x80
        self.mu.mem_write(self.TYPES * 16 + self.BRACERS * 0x14, bytes(rec))
        self.wear(7, self.BRACERS, 9, 4)  # creature 1: ring 4 (+1) on a finger, the robe on the chest


@unittest.skipIf(Uc is None, "unicorn is not installed")
class ScriptRandTests(unittest.TestCase):
    """The scripts' random command (PROBE_SCRIPT_RAND): EAX and EDX N + 1, as the replaced code
    leaves them, and the command recorded with its result, N, the script's position and the
    searches' counts."""
    COUNTS = 0xA000

    DS = 0x9000  # (the game's DS: its data well clear of DSCLOG's image, at TSR)

    def setUp(self):
        image = load_image()
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, image)
        self.hdr_off = struct.unpack_from("<H", image, 20)[0]
        self.ring = struct.unpack_from("<H", image, 16)[0]
        at = image.find(bytes.fromhex("fb66406689c25589e5"))
        self.assertGreater(at, 0)
        mu.mem_write(VEC_SCRIPT_RAND * 4, struct.pack("<HH", at, TSR))
        mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        data = (self.DS + 0x3781 - 0x4356) * 16
        mu.mem_write(data + 0x192, b"\x01")  # the running script's slot: 1, at 2116
        mu.mem_write(data + 0x295 + 2, struct.pack("<H", 2116))
        mu.mem_write(self.DS * 16 + 0x1356, struct.pack("<HH", 0, self.COUNTS))
        mu.mem_write(self.COUNTS * 16 + 21 * 2, struct.pack("<3H", 4, 3, 2))  # junk, hay, wardrobe

    def test_recorded(self):
        mu = self.mu
        mu.mem_write(SS * 16 + 0x7FC, struct.pack("<I", 0x7000))  # rand(), pushed
        mu.mem_write(CALLER * 16 + 0x600, bytes((0xCD, VEC_SCRIPT_RAND)))
        for name, value in dict(cs=CALLER, ds=self.DS, ss=SS, esp=0x7FC, ebp=BP, eflags=IF | 2, eax=10,
                                ebx=0x2222, ecx=0x3333, edx=0x4444, esi=0x1111, edi=0x5555, es=0x6666).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(CALLER * 16 + 0x600, CALLER * 16 + 0x602)
        self.assertEqual([mu.reg_read(x) for x in (r.UC_X86_REG_SP, r.UC_X86_REG_EAX, r.UC_X86_REG_EDX, r.UC_X86_REG_BX,
                                                   r.UC_X86_REG_CX, r.UC_X86_REG_SI, r.UC_X86_REG_DI, r.UC_X86_REG_BP,
                                                   r.UC_X86_REG_DS, r.UC_X86_REG_ES)],
                         [0x7FC, 11, 11, 0x2222, 0x3333, 0x1111, 0x5555, BP, self.DS, 0x6666])
        seq, _, nent = struct.unpack("<HHH", mu.mem_read(TSR * 16 + self.hdr_off + 8, 6))
        e = Entry.parse(bytes(mu.mem_read(RING_SEG * 16 + self.ring + ((seq - 1) % nent) * Entry.SIZE, Entry.SIZE)))
        self.assertEqual((e.kind, e.raw & 0xFF, e.raw >> 8 & 0xFF, e.extra), (5, 0x7000 * 11 >> 15, 10, 2116))
        self.assertEqual((e.arg(2), e.arg(4), e.arg(6)), (4, 3, 2))
        self.assertEqual((e.ip, e.cs), (0x602, CALLER))  # (the code after the INT)


class KindTableTests(unittest.TestCase):
    def test_kinds_match_the_companion(self):
        """DSCLOG's weapon kinds by item type are specialize.py's."""
        from dscompanion import specialize
        image = load_image()
        want = bytearray(140)
        for t, k in specialize.KIND_OF_TYPE.items():
            want[t] = k + 1
        self.assertGreater(image.find(bytes(want)), 0)


@unittest.skipIf(Uc is None, "unicorn is not installed")
class SpecializeTests(unittest.TestCase):
    """Weapon specialization in the weapon attack routine (PROBE_ATTACKS, PROBE_SPEC_DAMAGE): the
    attacks a round, the THAC0, the damage bonus and dice, by the attacker's chosen kinds."""
    DS = 0x9000  # (the game's DS: its things table 9E4h paragraphs below, its spells' 6A2h, clear of DSCLOG's image)
    SHEETS = 0x8000
    RULES = 170
    LONG_SWORD, AXE = 45, 22  # (item types: obsidian long sword, axe)
    TWO_HANDED, SHIELD, BOW = 60, 4, 13  # (item types as these tests make them)
    CREATURES, ITEMS, ITEM_TYPES = 0x8A00, 0x8B00, 0x8C00

    def setUp(self):
        image = load_image()
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, image)
        attacks = image.find(bytes.fromhex("9850e8"))
        damage = image.find(bytes.fromhex("0146eee8"))
        self.assertGreater(attacks, 0)
        self.assertGreater(damage, 0)
        mu.mem_write(VEC_ATTACKS * 4, struct.pack("<HH", attacks, TSR))
        mu.mem_write(VEC_SPEC_DAMAGE * 4, struct.pack("<HH", damage, TSR))
        mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        mu.mem_write(self.DS * 16 + 0x1661, struct.pack("<HH", 0, self.SHEETS))
        mu.mem_write(self.DS * 16 + 0x1665, struct.pack("<HH", 0, self.CREATURES))
        mu.mem_write(self.DS * 16 + 0x165D, struct.pack("<HH", 0, self.ITEMS))
        mu.mem_write(self.DS * 16 + 0x1669, struct.pack("<HH", 0, self.ITEM_TYPES))
        for typ, flags, kinds in ((self.AXE, 1, 0), (self.LONG_SWORD, 1, 0), (self.TWO_HANDED, 1, 0x40),
                                  (self.SHIELD, 4, 0x80), (self.BOW, 2, 0x40)):
            rec = bytearray(0x14)
            rec[0], rec[0x0F] = flags, kinds
            mu.mem_write(self.ITEM_TYPES * 16 + typ * 0x14, bytes(rec))

    def attack(self, halves, weapon, chosen=(), classes=(9, 0, 0), levels=(5, 0, 0), rules=4096, missile=False, race=0,
               kit=0, shield=False):
        """(attacks in halves, THAC0, damage bonus, sides) after both probes, with THAC0 15, a
        damage bonus of 1 before the STR bonus of 2 is added, 1d8; the attacker (thing 7,
        creature 5) with a shield in its left hand or none (SHIELD)."""
        mu = self.mu
        hdr = TSR * 16 + load_image().find(HDR_SIG)
        mu.mem_write(hdr + self.RULES, struct.pack("<H", rules & 0xFFFF))
        mu.mem_write(hdr + 270, struct.pack("<H", rules >> 16))
        sheet = bytearray(0x47)
        sheet[0x43] = kit
        for i, k in enumerate(chosen):
            sheet[0x14 + i] = k + 1
        sheet[0x21:0x24], sheet[0x24:0x27] = bytes(classes), bytes(levels)
        sheet[0x18] = race
        mu.mem_write(self.SHEETS * 16 + 3 * 0x47, bytes(sheet))  # (sheet 3)
        rec = bytearray(0x3A)
        struct.pack_into("<HHHH", rec, 4, 3, 0, 0, 0)
        struct.pack_into("<HHH", rec, 8, 8 if shield else 0x270F, 0x270F, 0x270F)
        mu.mem_write(self.CREATURES * 16 + 5 * 0x3A, bytes(rec))
        things = (self.DS + 0x3972 - 0x4356) * 16 + 0xC36
        mu.mem_write(things + 7 * 3, struct.pack("<Bh", 2, 5))
        mu.mem_write(things + 8 * 3, struct.pack("<Bh", 1, 3))
        item = bytearray(0x15)
        struct.pack_into("<H", item, 4, 0x270F)
        struct.pack_into("<H", item, 0x0A, self.SHIELD)
        item[0x11] = 10  # (the left hand)
        mu.mem_write(self.ITEMS * 16 + 3 * 0x15, bytes(item))
        mu.mem_write(SS * 16 + BP + 0x0A, struct.pack("<H", 15))
        mu.mem_write(SS * 16 + BP + 0x10, struct.pack("<H", 3))
        mu.mem_write(SS * 16 + BP + 0x14, struct.pack("<HHH", weapon, 2 if missile else 0, 7))
        mu.mem_write(SS * 16 + BP - 0x12, struct.pack("<HHH", 1, 8, 1))  # damage bonus, sides, count
        mu.mem_write(CALLER * 16 + 0x600, bytes((0xCD, VEC_ATTACKS, 0x90, 0x90, 0xB8, 2, 0, 0xCD, VEC_SPEC_DAMAGE, 0x90)))
        for name, value in dict(cs=CALLER, ds=self.DS, ss=SS, esp=0x7FC, ebp=BP, eflags=IF | 2, eax=halves,
                                ebx=0x2222, ecx=0x3333, edx=0x4444, esi=0x5555, es=0x6666).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(CALLER * 16 + 0x600, CALLER * 16 + 0x60A)
        self.assertEqual([mu.reg_read(x) for x in (r.UC_X86_REG_SP, r.UC_X86_REG_BX, r.UC_X86_REG_CX, r.UC_X86_REG_DX,
                                                   r.UC_X86_REG_SI, r.UC_X86_REG_ES)],
                         [0x7FC, 0x2222, 0x3333, 0x4444, 0x5555, 0x6666])
        attacks, = struct.unpack("<h", mu.mem_read(SS * 16 + BP - 8, 2))
        thac0, = struct.unpack("<h", mu.mem_read(SS * 16 + BP + 0x0A, 2))
        bonus, sides = struct.unpack("<hh", mu.mem_read(SS * 16 + BP - 0x12, 4))
        return attacks, thac0, bonus, sides

    def test_off(self):
        self.assertEqual(self.attack(3, self.AXE, chosen=(0,), rules=0), (3, 15, 3, 8))

    def test_ravager(self):
        """A Ravager's +1 to hit and damage in melee, kits on (kits.melee); none with a missile,
        or with kits off; a Brute's +2 with a two-handed melee weapon only."""
        kits = game.RULE_KITS
        self.assertEqual(self.attack(3, self.AXE, rules=kits, kit=3), (3, 14, 4, 8))
        self.assertEqual(self.attack(3, self.LONG_SWORD, chosen=(0,), levels=(4, 0, 0), rules=4096 | kits, kit=3),
                         (3, 13, 6, 8))
        self.assertEqual(self.attack(2, self.AXE, rules=kits, kit=3, missile=True)[1:3], (15, 3))
        self.assertEqual(self.attack(3, self.AXE, rules=0, kit=3)[1:3], (15, 3))
        self.assertEqual(self.attack(3, self.AXE, rules=kits, kit=2)[1:3], (15, 3))  # (a Sentinel)
        glad = dict(classes=(10, 0, 0), levels=(3, 0, 0), rules=kits, kit=3)
        self.assertEqual(self.attack(3, self.TWO_HANDED, **glad)[1:3], (13, 5))
        self.assertEqual(self.attack(3, self.AXE, **glad)[1:3], (15, 3))
        self.assertEqual(self.attack(2, self.BOW, missile=True, **glad)[1:3], (15, 3))

    def test_no_choices_as_the_game(self):
        """Monsters, and characters who haven't chosen yet: the game's own numbers."""
        self.assertEqual(self.attack(3, self.AXE), (3, 15, 3, 8))

    def test_specialization(self):
        self.assertEqual(self.attack(3, self.LONG_SWORD, chosen=(0,), levels=(4, 0, 0)), (3, 14, 5, 8))

    def test_other_kind_plain_rate(self):
        self.assertEqual(self.attack(3, self.AXE, chosen=(0,)), (2, 15, 3, 8))
        self.assertEqual(self.attack(4, self.AXE, chosen=(0,), levels=(7, 0, 0)), (3, 15, 3, 8))
        self.assertEqual(self.attack(3, 9999, chosen=(0,)), (2, 15, 3, 8))  # (bare hands: no kind)

    def test_mastery(self):
        self.assertEqual(self.attack(3, self.LONG_SWORD, chosen=(0,), levels=(5, 0, 0)), (3, 12, 6, 8))

    def test_grand_mastery(self):
        self.assertEqual(self.attack(4, self.LONG_SWORD, chosen=(0,), levels=(9, 0, 0)), (6, 12, 6, 10))

    def test_arena_champion(self):
        """An Arena Champion in melee: with a shield in a hand +1 to hit and damage, without one -1
        to hit; nothing with a missile (kits.champion), for another kit, or with kits off."""
        from dscompanion import kits
        glad = dict(classes=(10, 0, 0), levels=(3, 0, 0), rules=game.RULE_KITS, kit=1)
        self.assertEqual(self.attack(3, self.AXE, shield=True, **glad), (3, 14, 4, 8))
        self.assertEqual(self.attack(3, self.AXE, **glad), (3, 16, 3, 8))
        self.assertEqual(self.attack(2, self.BOW, missile=True, shield=True, **glad)[1:3], (15, 3))
        self.assertEqual(self.attack(2, self.BOW, missile=True, **glad)[1:3], (15, 3))
        self.assertEqual(self.attack(3, self.AXE, **dict(glad, kit=2)), (3, 15, 3, 8))
        self.assertEqual(self.attack(3, self.AXE, **dict(glad, rules=0)), (3, 15, 3, 8))
        self.assertEqual(kits.champion(kits.CHAMPION, True, True), (1, 1))

    def test_myrmidon(self):
        """A Myrmidon's second kind goes on to mastery and grand mastery as the first does (as
        specialize.skill); another fighter's second (none should have one) doesn't."""
        kits = 4096 | game.RULE_KITS
        self.assertEqual(self.attack(3, self.AXE, chosen=(0, 5), levels=(5, 0, 0), rules=kits, kit=1), (3, 12, 6, 8))
        self.assertEqual(self.attack(4, self.AXE, chosen=(0, 5), levels=(9, 0, 0), rules=kits, kit=1), (6, 12, 6, 10))
        self.assertEqual(self.attack(3, self.AXE, chosen=(0, 5), levels=(5, 0, 0), rules=kits, kit=2), (3, 14, 5, 8))
        self.assertEqual(self.attack(3, self.AXE, chosen=(0, 5), levels=(5, 0, 0), rules=4096, kit=1), (3, 14, 5, 8))
        from dscompanion import specialize
        sheet = bytearray(game.SHEET_SIZE)
        sheet[0x14:0x16], sheet[0x21], sheet[0x24], sheet[0x43] = bytes((1, 6)), 9, 9, 1
        old = game.RULES_IN_FORCE
        try:
            game.RULES_IN_FORCE = kits
            self.assertEqual(specialize.skill(bytes(sheet), self.AXE), specialize.GRAND)
            game.RULES_IN_FORCE = 4096
            self.assertEqual(specialize.skill(bytes(sheet), self.AXE), specialize.SPECIAL)
        finally:
            game.RULES_IN_FORCE = old

    def test_gladiator_weapons(self):
        """A gladiator: specialization with each chosen kind, never mastery."""
        glad = dict(classes=(10, 0, 0), levels=(9, 0, 0))
        self.assertEqual(self.attack(4, self.AXE, chosen=(0, 5), **glad), (4, 14, 5, 8))
        self.assertEqual(self.attack(4, self.LONG_SWORD, chosen=(0, 5), **glad), (4, 14, 5, 8))

    def test_battle_mage(self):
        """A Battle Mage (kits and weapon specialization on): the expertise rate with its chosen
        weapon spec, 3/2 a round, 2 from 7th level, no bonuses; the game's 1 with another weapon,
        or with either rule off (specialize.skill, expert_attacks)."""
        from dscompanion import specialize
        both = 4096 | game.RULE_KITS
        mage = dict(classes=(11, 0, 0), levels=(3, 0, 0), chosen=(0,), kit=2)
        self.assertEqual(self.attack(2, self.LONG_SWORD, rules=both, **mage), (3, 15, 3, 8))
        self.assertEqual(self.attack(2, self.LONG_SWORD, rules=both, **dict(mage, levels=(7, 0, 0))), (4, 15, 3, 8))
        self.assertEqual(self.attack(2, self.AXE, rules=both, **mage), (2, 15, 3, 8))
        self.assertEqual(self.attack(2, self.LONG_SWORD, rules=4096, **mage), (2, 15, 3, 8))
        self.assertEqual(self.attack(2, self.LONG_SWORD, rules=game.RULE_KITS, **mage), (2, 15, 3, 8))
        self.assertEqual(self.attack(2, self.LONG_SWORD, rules=both, **dict(mage, kit=1)), (2, 15, 3, 8))
        sheet = bytearray(game.SHEET_SIZE)
        sheet[0x14], sheet[0x21], sheet[0x24], sheet[0x43] = 1, 11, 7, 2
        old = game.RULES_IN_FORCE
        try:
            game.RULES_IN_FORCE = both
            skill = specialize.skill(bytes(sheet), self.LONG_SWORD)
            self.assertEqual((skill, specialize.skill(bytes(sheet), self.AXE)), (specialize.EXPERT, specialize.PLAIN))
            self.assertEqual([specialize.expert_attacks(2, skill, bytes(sheet)),
                              specialize.expert_attacks(2, specialize.PLAIN, bytes(sheet))], [4, 2])
            game.RULES_IN_FORCE = 4096
            self.assertEqual(specialize.skill(bytes(sheet), self.LONG_SWORD), specialize.PLAIN)
        finally:
            game.RULES_IN_FORCE = old

    def test_justifier(self):
        """A Justifier (kits on): its chosen weapon spec and the bow specialized, +1 to hit and +2
        damage, where another ranger has expertise; another kind the plain rate (specialize.skill)."""
        from dscompanion import specialize
        both = 4096 | game.RULE_KITS
        just = dict(classes=(13, 0, 0), levels=(4, 0, 0), chosen=(0,), kit=2, rules=both)
        self.assertEqual(self.attack(3, self.LONG_SWORD, **just), (3, 14, 5, 8))
        self.assertEqual(self.attack(2, 1, missile=True, **just)[1:3], (14, 5))  # (item type 1: a bow)
        self.assertEqual(self.attack(3, self.AXE, **just), (2, 15, 3, 8))
        self.assertEqual(self.attack(3, self.LONG_SWORD, **dict(just, kit=3)), (3, 15, 3, 8))  # (a Seeker)
        self.assertEqual(self.attack(3, self.LONG_SWORD, **dict(just, rules=4096)), (3, 15, 3, 8))
        sheet = bytearray(game.SHEET_SIZE)
        sheet[0x14], sheet[0x21], sheet[0x24], sheet[0x43] = 1, 13, 4, 2
        old = game.RULES_IN_FORCE
        try:
            game.RULES_IN_FORCE = both
            self.assertEqual([specialize.skill(bytes(sheet), t) for t in (self.LONG_SWORD, 1, self.AXE)],
                             [specialize.SPECIAL, specialize.SPECIAL, specialize.PLAIN])
            game.RULES_IN_FORCE = 4096
            self.assertEqual(specialize.skill(bytes(sheet), self.LONG_SWORD), specialize.EXPERT)
        finally:
            game.RULES_IN_FORCE = old

    def test_ranger_expertise(self):
        """A ranger: the rate with the chosen kind, no bonuses; another kind, the plain rate."""
        ranger = dict(classes=(13, 0, 0), levels=(4, 0, 0))
        self.assertEqual(self.attack(3, self.LONG_SWORD, chosen=(0,), **ranger), (3, 15, 3, 8))
        self.assertEqual(self.attack(3, self.AXE, chosen=(0,), **ranger), (2, 15, 3, 8))

    def test_missile_rate(self):
        """A missile weapon: the weapon's rate (the game's), or a specialist's when greater, by the
        fighter's or gladiator's level (1-6, 7-12): AD&D's for the sling, a step above for the bow,
        staff sling and chatkcha; a grand master one more, as in melee. As specialize.missile_attacks."""
        from dscompanion import specialize
        BOW, SLING, STAFF_SLING, CHATKCHA = 1, 64, 0, 48
        cases = ((4, BOW, 13, (9, 0, 0), (4, 0, 0), (6, 14, 5, 8)),       # bow 3/1 at 1-6
                 (4, BOW, 13, (9, 0, 0), (7, 0, 0), (8, 12, 6, 8)),       # 4/1 at 7 (and mastery)
                 (4, BOW, 13, (9, 0, 0), (9, 0, 0), (10, 12, 6, 10)),     # grand mastery: one more
                 (4, BOW, 13, (10, 0, 0), (8, 0, 0), (8, 14, 5, 8)),      # a gladiator
                 (2, SLING, 14, (9, 0, 0), (2, 0, 0), (3, 14, 5, 8)),     # sling 3/2
                 (2, SLING, 14, (11, 9, 0), (3, 7, 0), (4, 12, 6, 8)),    # 2/1 by the fighter level
                 (2, STAFF_SLING, 15, (9, 0, 0), (4, 0, 0), (3, 14, 5, 8)),   # staff sling 3/2 at 1-6
                 (2, STAFF_SLING, 15, (9, 0, 0), (8, 0, 0), (4, 12, 6, 8)),   # 2/1 at 7-12
                 (2, CHATKCHA, 12, (9, 0, 0), (7, 0, 0), (4, 12, 6, 8)),  # chatkcha, as the staff sling
                 (4, BOW, 0, (9, 0, 0), (6, 0, 0), (4, 15, 3, 8)),        # another kind: the game's
                 (4, BOW, 0, (9, 0, 0), (8, 0, 0), (6, 15, 3, 8)),        # from 7th, a specialist's 1-6
                 (2, CHATKCHA, 0, (10, 0, 0), (7, 0, 0), (3, 15, 3, 8)),  # a gladiator's chatkcha 3/2
                 (4, BOW, 13, (13, 0, 0), (8, 0, 0), (8, 15, 3, 8)),      # a ranger's expertise: the rate
                 (4, BOW, 0, (13, 0, 0), (4, 0, 0), (6, 15, 3, 8)),       # every ranger's bow, chosen or not
                 (4, BOW, 0, (9, 14, 0), (8, 3, 0), (8, 15, 3, 8)),       # a fighter/ranger: the higher level
                 (2, SLING, 0, (13, 0, 0), (6, 0, 0), (2, 15, 3, 8)),     # a ranger's unchosen sling: the game's
                 (2, SLING, 0, (13, 0, 0), (8, 0, 0), (3, 15, 3, 8)),     # ... 3/2 from 7th
                 (2, SLING, 0, (11, 0, 0), (8, 0, 0), (2, 15, 3, 8)))     # not a warrior: the game's
        for halves, weapon, kind, classes, levels, want in cases:
            with self.subTest(weapon=weapon, classes=classes, levels=levels):
                self.assertEqual(self.attack(halves, weapon, chosen=(kind,), classes=classes, levels=levels,
                                             missile=True), want)
                sheet = bytearray(0x47)
                sheet[0x14] = kind + 1
                sheet[0x21:0x24], sheet[0x24:0x27] = bytes(classes), bytes(levels)
                self.assertEqual(specialize.missile_attacks(halves, specialize.skill(bytes(sheet), weapon), weapon,
                                                            bytes(sheet)), want[0])
        # (a human ranger turned preserver: no bow expertise until the preserver level passes the ranger's)
        self.assertEqual(self.attack(4, BOW, chosen=(0,), classes=(11, 13, 0), levels=(3, 5, 0), missile=True,
                                     race=1), (4, 15, 3, 8))
        self.assertEqual(self.attack(4, BOW, chosen=(0,), classes=(11, 13, 0), levels=(6, 5, 0), missile=True,
                                     race=1), (6, 15, 3, 8))

    def test_dual_class(self):
        """A human fighter turned preserver: the game's numbers until its preserver level passes
        the fighter's, then mastery again (specialize.skill)."""
        human = dict(classes=(11, 9, 0), race=1)
        self.assertEqual(self.attack(2, self.LONG_SWORD, chosen=(0,), levels=(3, 5, 0), **human), (2, 15, 3, 8))
        self.assertEqual(self.attack(2, self.LONG_SWORD, chosen=(0,), levels=(6, 5, 0), **human), (2, 12, 6, 8))

    def test_not_a_warrior(self):
        self.assertEqual(self.attack(2, self.AXE, chosen=(0,), classes=(11, 0, 0)), (2, 15, 3, 8))

    def dam_line(self, halves, weapon, chosen=(), classes=(9, 0, 0), levels=(5, 0, 0), rules=4096, kit=0):
        """(attacks, bonus, sides, count) for the DAM line (PROBE_DAM_LINE): bonus 4, 1d8 pushed."""
        mu = self.mu
        at = load_image().find(bytes.fromhex("268a472a2ef706"))
        self.assertGreater(at, 0)
        mu.mem_write(VEC_DAM_LINE * 4, struct.pack("<HH", at, TSR))
        mu.mem_write(TSR * 16 + load_image().find(HDR_SIG) + self.RULES, struct.pack("<H", rules & 0xFFFF))
        mu.mem_write(TSR * 16 + load_image().find(HDR_SIG) + 270, struct.pack("<H", rules >> 16))
        sheet = bytearray(0x47)
        sheet[0x2A], sheet[0x43] = halves, kit
        for i, k in enumerate(chosen):
            sheet[0x14 + i] = k + 1
        sheet[0x21:0x24], sheet[0x24:0x27] = bytes(classes), bytes(levels)
        mu.mem_write(self.SHEETS * 16, bytes(sheet))
        mu.mem_write(SS * 16 + 0x7F6, struct.pack("<HHH", 1, 8, 4))  # pushed: count, sides, bonus
        mu.mem_write(CALLER * 16 + 0x600, bytes((0xCD, VEC_DAM_LINE, 0x90, 0x90)))
        for name, value in dict(cs=CALLER, ds=self.DS, ss=SS, esp=0x7F6, ebp=BP, eflags=IF | 2, eax=0x1200,
                                ebx=0, edx=0x4444, esi=weapon, es=self.SHEETS).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(CALLER * 16 + 0x600, CALLER * 16 + 0x604)
        self.assertEqual([mu.reg_read(x) for x in (r.UC_X86_REG_SP, r.UC_X86_REG_BP, r.UC_X86_REG_DX, r.UC_X86_REG_SI)],
                         [0x7F6, BP, 0x4444, weapon])
        count, sides, bonus = struct.unpack("<HHH", mu.mem_read(SS * 16 + 0x7F6, 6))
        return mu.reg_read(r.UC_X86_REG_AX) & 0xFF, bonus, sides, count

    def test_dam_line(self):
        self.assertEqual(self.dam_line(3, self.AXE, rules=0), (3, 4, 8, 1))
        self.assertEqual(self.dam_line(3, self.AXE, chosen=(0,)), (2, 4, 8, 1))
        self.assertEqual(self.dam_line(3, self.LONG_SWORD, chosen=(0,), levels=(4, 0, 0)), (3, 6, 8, 1))
        self.assertEqual(self.dam_line(4, self.LONG_SWORD, chosen=(0,), levels=(9, 0, 0)), (6, 7, 10, 1))

    def test_off_hand_attacks(self):
        """With the rule for two weapons (AD&D's), a weapon in the off hand (the item at [BP+12h], in
        slot 10: the helper's item 3) attacks once a round, the extra attacks the main hand's; a
        missile weapon, the main hand or the rule off keep theirs (OFF_HAND_HALVES)."""
        two = 4
        for item, rules, missile, want in ((3, two | 4096, False, 2), (0x270F, two | 4096, False, 3),
                                           (3, 4096, False, 3), (3, two, False, 2), (3, two | 4096, True, 3)):
            with self.subTest(item=item, rules=rules, missile=missile):
                self.setUp()
                self.mu.mem_write(SS * 16 + BP + 0x12, struct.pack("<H", item))
                self.assertEqual(self.attack(3, self.AXE, rules=rules, missile=missile)[0], want)
        self.setUp()
        self.mu.mem_write(SS * 16 + BP + 0x12, struct.pack("<H", 3))  # (a 7th-level Crusader: 3/2, the off hand 1)
        self.assertEqual(self.attack(2, self.AXE, rules=two | game.RULE_KITS, classes=(1, 0, 0), kit=3,
                                     levels=(7, 0, 0))[0], 2)

    def test_warrior_kits_attacks(self):
        """A Crusader (cleric) or Mind Warrior (psionicist), the rule for kits on: a warrior's extra
        attacks in melee, 3/2 a round from 7th level, 2 from 13th, weapon specialization on or off;
        not with a missile weapon, nor for another kit or with the rule off (kits.warrior_attacks)."""
        from dscompanion import kits as kit_rules
        on = game.RULE_KITS
        def fresh(probe):  # (a new emulator for each: its cached code at CALLER would be the last probe's)
            def run(*args, **kw):
                self.setUp()
                return probe(*args, **kw)
            return run
        self.attack, self.dam_line, self.view_dam = fresh(self.attack), fresh(self.dam_line), fresh(self.view_dam)
        crusader, mind = dict(classes=(1, 0, 0), kit=3), dict(classes=(12, 0, 0), kit=2)
        for who in (crusader, mind):
            for level, want in ((6, 2), (7, 3), (12, 3), (13, 4)):
                with self.subTest(who=who, level=level):
                    lv = dict(who, levels=(level, 0, 0))
                    self.assertEqual(self.attack(2, self.AXE, rules=on, **lv)[0], want)
                    self.assertEqual(self.attack(2, self.AXE, rules=on | 4096, **lv)[0], want)
                    self.assertEqual(self.dam_line(2, self.AXE, rules=on, **lv)[0], want)
                    self.assertEqual(self.view_dam(2, self.AXE, rules=on, **lv)[0], want)
                    sheet = bytearray(game.SHEET_SIZE)
                    sheet[0x21], sheet[0x24], sheet[0x43] = who["classes"][0], level, who["kit"]
                    self.assertEqual(kit_rules.warrior_attacks(2, bytes(sheet)), want)
        seven = dict(crusader, levels=(7, 0, 0))
        self.assertEqual(self.attack(2, 1, rules=on, missile=True, **seven)[0], 2)
        self.assertEqual(self.view_dam(2, 1, rules=on, missile=True, **seven)[0], 2)
        self.assertEqual(self.attack(2, self.AXE, rules=0, **seven)[0], 2)
        self.assertEqual(self.dam_line(2, self.AXE, rules=0, **seven)[0], 2)
        self.assertEqual(self.attack(2, self.AXE, rules=on, **dict(seven, kit=2))[0], 2)  # (a Healer)


    ITEMS, TYPES, WHO = 0x8800, 0x9000, 0x9800

    def view_dam(self, halves, weapon, chosen=(), classes=(9, 0, 0), levels=(5, 0, 0), rules=4096, missile=False,
                 kit=0):
        """(attacks, bonus, sides) for View Character's DAM line (PROBE_VIEW_DAM): DX the bonus 4,
        1d8, character 2 on show, its weapon item 1."""
        mu = self.mu
        at = load_image().find(bytes.fromhex("8956f2e8"))
        self.assertGreater(at, 0)
        mu.mem_write(VEC_VIEW_DAM * 4, struct.pack("<HH", at, TSR))
        mu.mem_write(TSR * 16 + load_image().find(HDR_SIG) + self.RULES, struct.pack("<H", rules & 0xFFFF))
        mu.mem_write(TSR * 16 + load_image().find(HDR_SIG) + 270, struct.pack("<H", rules >> 16))
        sheet = bytearray(0x47)
        sheet[0x43] = kit
        for i, k in enumerate(chosen):
            sheet[0x14 + i] = k + 1
        sheet[0x21:0x24], sheet[0x24:0x27] = bytes(classes), bytes(levels)
        mu.mem_write(self.SHEETS * 16 + 2 * 0x47, bytes(sheet))
        mu.mem_write(self.DS * 16 + 0x165D, struct.pack("<HH", 0, self.ITEMS))
        mu.mem_write(self.DS * 16 + 0x1669, struct.pack("<HH", 0, self.TYPES))
        mu.mem_write(self.ITEMS * 16 + 0x15 + 0x0A, struct.pack("<H", weapon))
        mu.mem_write(self.TYPES * 16 + weapon * 0x14, bytes((2 if missile else 1,)))
        mu.mem_write(self.WHO * 16 + 0x25B, struct.pack("<H", 2))
        mu.mem_write(CALLER * 16 + 0x602 - 0x84, struct.pack("<H", self.WHO))
        mu.mem_write(SS * 16 + BP - 0x0E, struct.pack("<HHHHHHH", 0, 0, 1, 0, halves, 8, 1))  # bonus .. count
        mu.mem_write(CALLER * 16 + 0x600, bytes((0xCD, VEC_VIEW_DAM, 0x90)))
        for name, value in dict(cs=CALLER, ds=self.DS, ss=SS, esp=0x7FC, ebp=BP, eflags=IF | 2, eax=0x1111,
                                ebx=0x2222, ecx=0x3333, edx=4, esi=0x5555, edi=0x7777, es=0x6666).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(CALLER * 16 + 0x600, CALLER * 16 + 0x603)
        self.assertEqual([mu.reg_read(getattr(r, "UC_X86_REG_" + x)) for x in ("SP", "AX", "BX", "CX", "DX", "SI", "DI", "ES")],
                         [0x7FC, 0x1111, 0x2222, 0x3333, 4, 0x5555, 0x7777, 0x6666])
        bonus, = struct.unpack("<h", mu.mem_read(SS * 16 + BP - 0x0E, 2))
        attacks, sides = struct.unpack("<hh", mu.mem_read(SS * 16 + BP - 6, 2) + mu.mem_read(SS * 16 + BP - 4, 2))
        return attacks, bonus, sides

    def test_view_dam(self):
        self.assertEqual(self.view_dam(3, self.AXE, chosen=(0,), rules=0), (3, 4, 8))
        self.assertEqual(self.view_dam(3, self.AXE), (3, 4, 8))
        self.assertEqual(self.view_dam(3, self.AXE, chosen=(0,)), (2, 4, 8))
        self.assertEqual(self.view_dam(3, self.LONG_SWORD, chosen=(0,), levels=(4, 0, 0)), (3, 6, 8))
        self.assertEqual(self.view_dam(4, self.LONG_SWORD, chosen=(0,), levels=(9, 0, 0)), (6, 7, 10))
        self.assertEqual(self.view_dam(4, 1, chosen=(13,), levels=(4, 0, 0), missile=True), (4, 6, 8))
        self.assertEqual(self.view_dam(3, 1, chosen=(0,), missile=True), (3, 4, 8))
        kits = game.RULE_KITS  # (a Ravager: +1 in melee, the rule for weapon specialization on or off)
        self.assertEqual(self.view_dam(3, self.AXE, rules=kits, kit=3), (3, 5, 8))
        self.assertEqual(self.view_dam(3, self.LONG_SWORD, chosen=(0,), levels=(4, 0, 0), rules=4096 | kits, kit=3),
                         (3, 7, 8))
        self.assertEqual(self.view_dam(3, 1, rules=kits, kit=3, missile=True), (3, 4, 8))



@unittest.skipIf(Uc is None, "unicorn is not installed")
class CanUseTests(unittest.TestCase):
    """PROBE_CAN_USE (class restrictions) against restrict.py, for every class pairing, race and
    item type of tests/test_restrict.py."""
    TYPES_SEG, SHEET = 0x8000, 0x9000
    RULES = 170

    def setUp(self):
        image = load_image()
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, image)
        at = image.find(bytes.fromhex("26234712"))
        self.assertGreater(at, 0)
        mu.mem_write(VEC_CAN_USE * 4, struct.pack("<HH", at, TSR))
        mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        mu.mem_write(GAME_DS * 16 + 0x1669, struct.pack("<HH", 0, self.TYPES_SEG))
        for t in test_restrict.TYPES:
            mu.mem_write(self.TYPES_SEG * 16 + t * 0x14, test_restrict.record(t))
        mu.mem_write(CALLER * 16 + 0x600, bytes((0xCD, VEC_CAN_USE, 0x90, 0x90)))

    def can_use(self, sheet, t, rules=8192, slot=7):
        """The equip routine putting item type T in SLOT (7 the right hand, 14 the off hand: its
        [BP+8], BP the can-use routine's [BP])."""
        mu = self.mu
        mu.mem_write(TSR * 16 + load_image().find(HDR_SIG) + self.RULES, struct.pack("<H", rules))
        mu.mem_write(SS * 16 + BP, struct.pack("<H", PARENT_BP))
        mu.mem_write(SS * 16 + PARENT_BP + 8, struct.pack("<H", slot))
        mu.mem_write(self.SHEET * 16 + 0x100, sheet)
        for name, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x7FC, ebp=BP, eflags=IF | 2, eax=test_restrict.TYPES[t][3],
                                ebx=0x100, ecx=0x3333, edx=t, esi=0x5555, edi=0x7777, es=self.SHEET).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(CALLER * 16 + 0x600, CALLER * 16 + 0x604)
        self.assertEqual([mu.reg_read(getattr(r, "UC_X86_REG_" + x)) for x in ("SP", "BX", "CX", "DX", "SI", "DI", "ES", "DS")],
                         [0x7FC, 0x100, 0x3333, t, 0x5555, 0x7777, self.SHEET, GAME_DS])
        return mu.reg_read(r.UC_X86_REG_AX)

    def test_dual_class(self):
        """A fighter turned psionicist (or cleric): its long sword back once the new level passes."""
        for new in (12, 3):
            for first in (3, 4, 5, 6):
                s = bytearray(test_restrict.sheet(new, 9, race=game.HUMAN))
                s[0x14] = 1
                s[0x24:0x26] = bytes((first, 5))
                for t in (45, 81, 22, 17):
                    with self.subTest(new=new, level=first, type=t):
                        mask = test_restrict.TYPES[t][3] & int.from_bytes(s[0x12:0x14], "little")
                        expected = mask if mask and restrict.allowed(bytes(s), t, test_restrict.record(t)) else 0
                        self.assertEqual(self.can_use(bytes(s), t), expected)

    def test_rangers_bow(self):
        """A ranger's bow, whatever a fire cleric's sphere forbids (restrict.specialized_back)."""
        cases = [(test_restrict.sheet(3, 15), None), (test_restrict.sheet(15, 3), None)]
        for first in (4, 6):
            cases.append((test_restrict.sheet(3, 15, race=game.HUMAN), (first, 5)))
        for s, levels in cases:
            s = bytearray(s)
            if levels:
                s[0x24:0x26] = bytes(levels)
            for t in (1, 22):
                with self.subTest(classes=tuple(s[0x21:0x23]), levels=levels, type=t):
                    mask = test_restrict.TYPES[t][3] & int.from_bytes(s[0x12:0x14], "little")
                    expected = mask if mask and restrict.allowed(bytes(s), t, test_restrict.record(t)) else 0
                    self.assertEqual(self.can_use(bytes(s), t), expected)
        self.assertNotEqual(self.can_use(test_restrict.sheet(3, 15), 1), 0)

    @staticmethod
    def expected(s, t, off_hand=False):
        """PROBE_CAN_USE's AX by restrict.py: the game's mask (1 for an item only the kit lets the
        character use, KIT_ALLOWS), or 0; the class restrictions with their rule in force."""
        s, rec = bytes(s), test_restrict.record(t)
        mask = test_restrict.TYPES[t][3] & int.from_bytes(s[0x12:0x14], "little")
        restricted = not game.RULES_IN_FORCE & game.RULE_RESTRICT or restrict.allowed(s, t, rec)
        ok = (mask or restrict.kit_allows(s, t, rec)) and restricted \
            and not restrict.kit_forbids(s, t, rec, off_hand=off_hand)
        return (mask or 1) if ok else 0

    def test_battle_mage(self):
        """KIT_ALLOWS: a Battle Mage its chosen weapon spec's weapons (with weapon specialization)
        and light armour, whatever a preserver's lists and restrictions (kits.allows); nothing in
        the off hand all the same."""
        from dscompanion import kits
        hdr = TSR * 16 + load_image().find(HDR_SIG)
        old = game.RULES_IN_FORCE
        try:
            self.mu.mem_write(hdr + 270, struct.pack("<H", 1))
            for spec in (game.RULE_SPECIALIZE, 0):
                for restrict_rule in (game.RULE_RESTRICT, 0):
                    rules = spec | restrict_rule
                    game.RULES_IN_FORCE = rules | game.RULE_KITS
                    for kit, chosen in ((2, 1), (2, 6), (2, 0), (1, 1)):
                        s = bytearray(test_restrict.sheet(11))
                        s[0x43], s[0x14] = kit, chosen
                        for t in test_restrict.TYPES:
                            for slot in (7, 14):
                                with self.subTest(rules=rules, kit=kit, chosen=chosen, type=t, slot=slot):
                                    self.assertEqual(self.can_use(bytes(s), t, rules=rules, slot=slot),
                                                     self.expected(s, t, off_hand=slot == 14))
            game.RULES_IN_FORCE = game.RULE_KITS | game.RULE_SPECIALIZE | game.RULE_RESTRICT
            mage = bytearray(test_restrict.sheet(11))
            mage[0x43], mage[0x14] = 2, 1  # (the long sword)
            leather = next(t for t in test_restrict.TYPES if restrict.is_armour(test_restrict.record(t))
                           and restrict.is_light(test_restrict.record(t)))
            self.assertTrue(restrict.usable(bytes(mage), 81, test_restrict.record(81)))
            self.assertTrue(restrict.usable(bytes(mage), leather, test_restrict.record(leather)))
            self.assertFalse(restrict.usable(bytes(mage), 22, test_restrict.record(22)))  # (an axe: not its own)
            self.assertNotEqual(self.can_use(bytes(mage), 81, rules=game.RULE_SPECIALIZE | game.RULE_RESTRICT), 0)
            self.assertEqual(self.can_use(bytes(mage), 81, rules=game.RULE_SPECIALIZE | game.RULE_RESTRICT, slot=14), 0)
            self.assertEqual(sorted(kits.BATTLE_MAGE_KINDS), [0, 1, 2, 3, 4, 5, 7])
        finally:
            game.RULES_IN_FORCE = old

    def test_elementalist(self):
        """An Elementalist's second sphere's weapons as well as its own sphere's (CLASS_FORBIDS's
        EL_SECOND; restrict.elementalist_sphere)."""
        hdr = TSR * 16 + load_image().find(HDR_SIG)
        old = game.RULES_IN_FORCE
        try:
            self.mu.mem_write(hdr + 270, struct.pack("<H", 1))
            game.RULES_IN_FORCE = game.RULE_RESTRICT | game.RULE_KITS
            for cls in (1, 2, 3, 4):
                for kit, second in ((1, 0), (1, 1), (1, 2), (1, 3), (1, None), (2, 1)):
                    s = bytearray(test_restrict.sheet(cls))
                    s[0x43], s[0x45] = kit, 0 if second is None else second + 1
                    for t in test_restrict.TYPES:
                        with self.subTest(cls=cls, kit=kit, second=second, type=t):
                            self.assertEqual(self.can_use(bytes(s), t, rules=game.RULE_RESTRICT), self.expected(s, t))
            fire = bytearray(test_restrict.sheet(1))  # (an air cleric: the bone long sword with water)
            fire[0x43], fire[0x45] = 1, 4
            self.assertTrue(restrict.allowed(bytes(fire), 81, test_restrict.record(81)))
            fire[0x45] = 0
            self.assertFalse(restrict.allowed(bytes(fire), 81, test_restrict.record(81)))
        finally:
            game.RULES_IN_FORCE = old
            self.mu.mem_write(hdr + 270, struct.pack("<H", 0))

    def test_kits(self):
        """KIT_FORBIDS in PROBE_CAN_USE as restrict.kit_forbids (kits.forbids): the Twin-blade,
        Brute, Stalker, Grove Warden and Lifebinder, a half-giant or not, the rule for half-giants'
        hands on or off, for every item type of tests/test_restrict.py."""
        hdr = TSR * 16 + load_image().find(HDR_SIG)
        old = game.RULES_IN_FORCE
        try:
            for half_rule in (game.RULE_HALF_GIANT, 0):
                rules = game.RULE_RESTRICT | half_rule
                game.RULES_IN_FORCE = rules | game.RULE_KITS
                self.mu.mem_write(hdr + 270, struct.pack("<H", 1))
                for cls, kit in ((10, 2), (10, 3), (13, 1), (5, 1), (5, 2), (17, 3), (9, 3),
                                 (13, 3), (14, 3), (15, 3), (16, 3), (13, 2)):
                    for race in (2, game.RACE_HALF_GIANT):
                        s = bytearray(test_restrict.sheet(cls, race=race))
                        s[0x43] = kit
                        for t in test_restrict.TYPES:
                            with self.subTest(half_rule=half_rule, cls=cls, kit=kit, race=race, type=t):
                                self.assertEqual(self.can_use(bytes(s), t, rules=rules), self.expected(s, t))
            # the off hand: a Healer no weapon, a Battle Mage nothing (the right hand as before)
            for cls, kit in ((1, 2), (11, 2), (1, 0), (11, 1)):
                s = bytearray(test_restrict.sheet(cls))
                s[0x43] = kit
                for t in test_restrict.TYPES:
                    for slot in (7, 14):
                        with self.subTest(cls=cls, kit=kit, type=t, slot=slot):
                            self.assertEqual(self.can_use(bytes(s), t, rules=rules, slot=slot),
                                             self.expected(s, t, off_hand=slot == 14))
            # a weapon of a kind it specialized in: no kit's limit on it, but the off hand's
            for cls, kit, kind in ((17, 3, "long sword"), (5, 2, "axe"), (10, 3, "axe"), (1, 2, "long sword"),
                                   (9, 3, "bow")):
                s = bytearray(test_restrict.sheet(cls))
                s[0x43], s[0x14] = kit, specialize.KINDS.index(kind) + 1
                for t in test_restrict.TYPES:
                    for slot in (7, 14):
                        with self.subTest(cls=cls, kit=kit, kind=kind, type=t, slot=slot):
                            self.assertEqual(self.can_use(bytes(s), t, rules=rules, slot=slot),
                                             self.expected(s, t, off_hand=slot == 14))
            # a human Lifebinder (druid 2) turned fighter (7, a long sword spec), now a thief: the
            # long sword the kit's to forbid while the fighter class sleeps, its own once passed
            for thief in (6, 7, 8):
                s = bytearray(test_restrict.sheet(17, 9, 5, race=game.HUMAN))
                s[0x24:0x27], s[0x43], s[0x14] = bytes((thief, 7, 2)), 2, 1
                game.RULES_IN_FORCE = rules | game.RULE_KITS
                self.assertEqual(restrict.specs_awake(bytes(s)), thief > 7)
                self.assertEqual(restrict.kit_forbids(bytes(s), 45, test_restrict.record(45)), thief <= 7)
                for t in test_restrict.TYPES:
                    with self.subTest(thief=thief, type=t):
                        self.assertEqual(self.can_use(bytes(s), t, rules=rules), self.expected(s, t))
            game.RULES_IN_FORCE = game.RULE_KITS
            shinobi = bytearray(test_restrict.sheet(17))
            shinobi[0x43], shinobi[0x14] = 3, 1  # (a long sword spec: a thief turned ... back again)
            self.assertFalse(restrict.kit_forbids(bytes(shinobi), 45, test_restrict.record(45)))
            self.assertTrue(restrict.kit_forbids(bytes(shinobi), 45, test_restrict.record(45), spec=True))
            self.assertTrue(restrict.kit_forbids(bytes(shinobi), 22, test_restrict.record(22)))  # (an axe: not chosen)
            healer, mage = bytearray(test_restrict.sheet(1)), bytearray(test_restrict.sheet(11))
            healer[0x43], mage[0x43] = 2, 2
            self.assertTrue(restrict.kit_forbids(bytes(healer), 22, test_restrict.record(22), off_hand=True))
            self.assertFalse(restrict.kit_forbids(bytes(healer), 22, test_restrict.record(22)))
            self.assertFalse(restrict.kit_forbids(bytes(healer), 4, test_restrict.record(4), off_hand=True))  # (a shield)
            self.assertTrue(restrict.kit_forbids(bytes(mage), 4, test_restrict.record(4), off_hand=True))
            brute = bytearray(test_restrict.sheet(10))
            brute[0x43] = 3
            self.assertFalse(restrict.kit_forbids(bytes(brute), 1, test_restrict.record(1)))  # (a bow, to use ...)
            self.assertTrue(restrict.kit_forbids(bytes(brute), 1, test_restrict.record(1), spec=True))  # (... not as a spec)
            self.assertTrue(restrict.kit_forbids(bytes(brute), 22, test_restrict.record(22)))  # (an axe: one hand)
            self.assertFalse(restrict.kit_forbids(bytes(brute), 3, test_restrict.record(3)))  # (a quarterstaff)
            shinobi = bytearray(test_restrict.sheet(17))
            shinobi[0x43] = 3
            self.assertEqual([t for t in (17, 1, 3, 0, 6, 90, 22, 45, 4, 57, 48)
                              if not restrict.kit_forbids(bytes(shinobi), t, test_restrict.record(t))],
                             [17, 1, 3, 0, 6, 90, 48])  # (dagger, bow, quarterstaff, staff sling, leather, silk, chatkcha)
        finally:
            game.RULES_IN_FORCE = old
            self.mu.mem_write(hdr + 270, struct.pack("<H", 0))

    def test_off_as_the_game(self):
        psi = test_restrict.sheet(12)
        self.assertEqual(self.can_use(psi, 57, rules=0), 0x100 & 0x126F)
        self.assertEqual(self.can_use(test_restrict.sheet(11), 57, rules=0), 0)

    def test_every_pairing(self):
        sheet, classes = test_restrict.sheet, range(18)
        for race in (game.HUMAN, 2):
            for a in range(1, 18):
                for b in classes:
                    s = sheet(a, b, race=race) if b else sheet(a, race=race)
                    for t in test_restrict.TYPES:
                        with self.subTest(race=race, classes=(a, b), type=t):
                            mask = test_restrict.TYPES[t][3] & int.from_bytes(s[0x12:0x14], "little")
                            expected = mask if mask and restrict.allowed(s, t, test_restrict.record(t)) else 0
                            self.assertEqual(self.can_use(s, t), expected)



@unittest.skipIf(Uc is None, "unicorn is not installed")
class NoCastTests(unittest.TestCase):
    """PROBE_NO_CAST: a multiclass preserver in armour can't cast (restrict.no_spells)."""
    SHEETS, CREATURES, ITEMS, TYPES_SEG = 0x8000, 0x8400, 0x8800, 0x9000
    THINGS_SEG = GAME_DS + 0x3972 - 0x4356
    RULES = 170
    WHO = 1

    def setUp(self):
        image = load_image()
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, image)
        at = image.find(bytes.fromhex("5589e5508b460689460a"), image.find(bytes.fromhex("26234712")))
        self.assertGreater(at, 0)
        mu.mem_write(VEC_NO_CAST * 4, struct.pack("<HH", at, TSR))
        mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        for ptr, seg in ((0x1661, self.SHEETS), (0x1665, self.CREATURES), (0x165D, self.ITEMS), (0x1669, self.TYPES_SEG)):
            mu.mem_write(GAME_DS * 16 + ptr, struct.pack("<HH", 0, seg))
        for t in test_restrict.TYPES:
            mu.mem_write(self.TYPES_SEG * 16 + t * 0x14, test_restrict.record(t))
        mu.mem_write(CALLER * 16 + 0x600, bytes((0xCD, VEC_NO_CAST, 0x90)))

    def no_cast(self, sheet, worn, ax=0, rules=8192):
        """AX after the probe, the character wearing (type, slot) pairs: list +8 one thing, the
        items chained, and list +0Ah empty."""
        mu = self.mu
        mu.mem_write(TSR * 16 + load_image().find(HDR_SIG) + self.RULES, struct.pack("<H", rules))
        mu.mem_write(self.SHEETS * 16 + self.WHO * 0x47, sheet)
        rec = bytearray(0x3A)
        rec[8:14] = struct.pack("<HHH", 4 if worn else 0x270F, 0x270F, 0x270F)
        mu.mem_write(self.CREATURES * 16 + self.WHO * 0x3A, bytes(rec))
        mu.mem_write(self.THINGS_SEG * 16 + 0xC36 + 4 * 3, struct.pack("<Bh", 1, 10))
        for n, (t, slot) in enumerate(worn):
            item = bytearray(0x15)
            item[4:6] = struct.pack("<H", 10 + n + 1 if n + 1 < len(worn) else 0x270F)
            item[0x0A:0x0C] = struct.pack("<H", t)
            item[0x11] = slot
            mu.mem_write(self.ITEMS * 16 + (10 + n) * 0x15, bytes(item))
        mu.mem_write(SS * 16 + 0x7F8, struct.pack("<HH", self.WHO, 0))
        for name, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x7F8, ebp=BP, eflags=IF | 2, eax=ax,
                                ebx=0x2222, ecx=0x3333, edx=self.WHO, esi=0x5555, edi=0x7777, es=0x6666).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(CALLER * 16 + 0x600, CALLER * 16 + 0x603)
        self.assertEqual([mu.reg_read(getattr(r, "UC_X86_REG_" + x)) for x in ("SP", "BP", "BX", "CX", "DX", "SI", "DI", "ES", "DS")],
                         [0x7FC, BP, 0x2222, 0x3333, self.WHO, 0x5555, 0x7777, 0x6666, GAME_DS])
        return mu.reg_read(r.UC_X86_REG_AX)

    def test_preserver_in_armour(self):
        sheet = test_restrict.sheet
        chest, head, hand, cloak = 9, 7, 3, 12
        self.assertEqual(self.no_cast(sheet(9, 11), [(65, cloak), (5, head)]), 1)
        self.assertEqual(self.no_cast(sheet(11, 17), [(6, chest)]), 1)
        self.assertEqual(self.no_cast(sheet(9, 11), [(4, hand), (65, cloak)]), 0)  # a shield
        self.assertEqual(self.no_cast(sheet(9, 11), [(6, 20)]), 0)  # (carried, not worn)
        self.assertEqual(self.no_cast(sheet(9, 11), []), 0)
        self.assertEqual(self.no_cast(sheet(11), [(6, chest)]), 0)
        self.assertEqual(self.no_cast(sheet(11, 9, race=game.HUMAN), [(6, chest)]), 0)
        self.assertEqual(self.no_cast(sheet(9, 11), [(6, chest)], rules=0), 0)
        self.assertEqual(self.no_cast(sheet(9, 17), [(6, chest)], ax=1), 1)  # (the game's own reasons)



@unittest.skipIf(Uc is None, "unicorn is not installed")
class MultiHpTests(unittest.TestCase):
    """PROBE_MC_ROLL, PROBE_MC_CON, PROBE_MC_UNCON against game.multiclass_gain and con_share."""
    SHEETS = 0x8000
    RULES = 170

    def setUp(self):
        image = load_image()
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, image)
        add = image.find(bytes.fromhex("26014f0acf"))  # PROBE_MC_ROLL's last two instructions
        self.assertGreater(add, 0)
        start = image.rfind(bytes.fromhex("2ef706"), 0, add)  # its rule test, its first instruction
        con = image.find(bytes.fromhex("01c7cf"), add)  # PROBE_MC_CON: call con_share, add di,ax, iret
        uncon = image.find(bytes.fromhex("29c2cf"), add)
        self.assertGreater(con, 0)
        self.assertGreater(uncon, 0)
        mu.mem_write(VEC_MC_ROLL * 4, struct.pack("<HH", start, TSR))
        mu.mem_write(VEC_MC_CON * 4, struct.pack("<HH", con - 3, TSR))
        mu.mem_write(VEC_MC_UNCON * 4, struct.pack("<HH", uncon - 3, TSR))
        mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        mu.mem_write(GAME_DS * 16 + 0x1661, struct.pack("<HH", 0, self.SHEETS))

    def run_probe(self, vector, sheet, rules, **regs):
        mu = self.mu
        mu.mem_write(TSR * 16 + load_image().find(HDR_SIG) + self.RULES, struct.pack("<H", rules))
        mu.mem_write(self.SHEETS * 16 + 2 * 0x47, sheet)
        mu.mem_write(CALLER * 16 + 0x600, bytes((0xCD, vector)))
        values = dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x7FC, ebp=BP, eflags=IF | 2, eax=0x1111, ebx=2 * 0x47,
                      ecx=0x3333, edx=0x4444, esi=2, edi=0x7777, es=self.SHEETS)
        values.update(regs)
        for name, value in values.items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(CALLER * 16 + 0x600, CALLER * 16 + 0x602)
        return {x: mu.reg_read(getattr(r, "UC_X86_REG_" + x.upper())) for x in ("sp", "ax", "bx", "cx", "dx", "si", "di", "es")}

    def sheets(self):
        sheet = test_restrict.sheet
        return [sheet(9), sheet(9, 11), sheet(9, 11, 17), sheet(11, 9, race=game.HUMAN)]

    def test_roll(self):
        for s in self.sheets():
            for gain in range(0, 21):
                for rules in (0, 16384):
                    with self.subTest(sheet=s[0x21:0x24], gain=gain, rules=rules):
                        self.mu.mem_write(self.SHEETS * 16 + 2 * 0x47 + 0x0A, struct.pack("<H", 0))
                        out = self.run_probe(VEC_MC_ROLL, s[:0x0A] + struct.pack("<H", 100) + s[0x0C:], rules, ecx=gain)
                        base, = struct.unpack("<H", self.mu.mem_read(self.SHEETS * 16 + 2 * 0x47 + 0x0A, 2))
                        added = game.multiclass_gain(s, gain) if rules else gain
                        self.assertEqual(base, 100 + added)
                        self.assertEqual((out["sp"], out["ax"], out["dx"], out["si"], out["di"]), (0x7FC, 0x1111, 0x4444, 2, 0x7777))

    def test_con(self):
        for s in self.sheets():
            for bonus in range(-3, 13):
                for rules in (0, 16384):
                    with self.subTest(sheet=s[0x21:0x24], bonus=bonus, rules=rules):
                        share = game.con_share(s, bonus) if rules else bonus
                        out = self.run_probe(VEC_MC_CON, s, rules, eax=bonus & 0xFFFF, edi=50)
                        self.assertEqual(out["di"], 50 + share)
                        self.assertEqual((out["sp"], out["bx"], out["cx"], out["dx"], out["si"], out["es"]),
                                         (0x7FC, 2 * 0x47, 0x3333, 0x4444, 2, self.SHEETS))
                        out = self.run_probe(VEC_MC_UNCON, s, rules, eax=bonus & 0xFFFF, edx=50)
                        self.assertEqual(out["dx"], (50 - share) & 0xFFFF)


@unittest.skipIf(Uc is None, "unicorn is not installed")
class KindsAllowedTests(unittest.TestCase):
    """DSCLOG's KINDS_ALLOWED against restrict.allowed_kinds, on the game's weapon types (their
    flags, material and classes, as DSUN's IT1R has them): a kind open if any of its types is
    usable, so a fire or earth cleric's long sword (obsidian or metal) and mace (obsidian)."""
    # type: (flags, material byte, classes)
    WEAPONS = {45: (1, 3, 0x167E), 63: (1, 4, 0x1672), 81: (1, 1, 0x1678), 47: (1, 4, 0x1672),
               41: (1, 1, 0x1672), 50: (1, 1, 0x1772), 85: (1, 3, 0x1676), 97: (1, 1, 0x1FF2),
               98: (1, 3, 0x1776), 17: (1, 3, 0x1FF6), 33: (1, 2, 0x1FF2), 84: (0x11, 4, 0x1FF2),
               94: (1, 3, 0x1FF2), 20: (1, 1, 0x167A), 46: (1, 3, 0x167E), 18: (1, 0, 0x177A),
               22: (1, 4, 0x177A), 2: (1, 0x40, 0x166C), 112: (1, 2, 0x177A), 3: (1, 0, 0x1EFA),
               80: (1, 0, 0x1EFA), 19: (1, 1, 0x167A), 111: (1, 1, 0x167A), 44: (1, 1, 0x177B),
               21: (1, 1, 0x167B), 48: (0x12, 3, 0x1F77), 1: (0x0A, 0, 0x177B), 69: (0x0A, 0, 0x177B),
               64: (2, 5, 0x1EF9), 0: (2, 5, 0x1EF1), game.SHORT_SWORD_TYPE: (1, 4, 0x1672),
               game.BONE_SHORT_SWORD_TYPE: (1, 1, 0x1778), game.BONE_AXE_TYPE: (1, 1, 0x1778),
               game.OBSIDIAN_SHORT_SWORD_TYPE: (1, 3, 0x177E), game.OBSIDIAN_AXE_TYPE: (1, 3, 0x177E),
               game.METAL_SHORT_SWORD_TYPE: (1, 4, 0x1672), game.METAL_DAGGER_TYPE: (1, 4, 0x1FF2),
               game.METAL_MACE_TYPE: (1, 4, 0x1672), game.METAL_GREAT_AXE_TYPE: (1, 4, 0x1662),
               game.METAL_PICK_TYPE: (1, 4, 0x1772), game.METAL_POLEARM_TYPE: (1, 4, 0x1672),
               game.AIR_DAGGER_TYPE: (1, 4, 0x1FF3), game.BONE_GREAT_AXE_TYPE: (1, 1, 0x1668),
               game.OBSIDIAN_GREAT_AXE_TYPE: (1, 3, 0x166E), game.BONE_DAGGER_TYPE: (1, 1, 0x1FFA)}
    TYPES = 0x8000  # (segment)

    def record(self, t):
        rec = bytearray(game.ITEM_TYPE_SIZE)
        if t in self.WEAPONS:
            flags, material, classes = self.WEAPONS[t]
            rec[0], rec[8] = flags, material
            rec[0x10:0x12] = classes.to_bytes(2, "little")
        return bytes(rec)

    def test_as_the_python(self):
        image = load_image()
        import re
        start = re.search(rb"\x51\x52\x56\x57\xe8..\x16", image, re.S).start()  # (KINDS_ALLOWED: its kit first)
        self.assertGreater(start, 0)
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, image)
        mu.mem_write(TSR * 16 + 0xFFF0, bytes((0xF4,)))  # (hlt: where KINDS_ALLOWED returns)
        mu.mem_write(GAME_DS * 16 + 0x1669, struct.pack("<HH", 0, self.TYPES))
        mu.mem_write(self.TYPES * 16, b"".join(self.record(t) for t in range(140)))
        sheet = test_restrict.sheet
        combos = [(9,), (13,), (10,), (11,), (12,), (17,), (9, 12), (9, 17), (9, 11), (13, 5), (13, 12)]
        for c in range(1, 5):
            combos += [(c,), (9, c), (12 + c, c)]
        for classes in combos:
            s = sheet(*classes)
            with self.subTest(classes=classes):
                mu.mem_write(SS * 16 + 0x500, s)
                mu.mem_write(SS * 16 + 0x7FC, struct.pack("<H", 0xFFF0))
                for name, value in dict(cs=TSR, ds=GAME_DS, es=SS, ebx=0x500, ss=SS, esp=0x7FC).items():
                    mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
                mu.emu_start(TSR * 16 + start, TSR * 16 + 0xFFF0)
                got = mu.reg_read(r.UC_X86_REG_AX)
                want = restrict.allowed_kinds(s, self.record)
                self.assertEqual([k for k in range(16) if got >> k & 1], want)
        old, hdr = game.RULES_IN_FORCE, TSR * 16 + image.find(HDR_SIG)
        try:  # the kits that limit weapons: a Brute's two-handed melee kinds (no missile spec), a Lifebinder's blunt
            game.RULES_IN_FORCE = game.RULE_KITS
            mu.mem_write(hdr + 270, struct.pack("<H", 1))
            for classes, kit in (((10,), 3), ((10,), 2), ((5,), 2), ((17,), 3), ((5,), 1), ((11,), 2), ((11,), 1),
                                 ((13,), 3), ((14,), 3), ((15,), 3), ((16,), 3), ((13,), 2), ((1,), 1), ((3,), 1)):
                s = bytearray(sheet(*classes))
                s[0x43] = kit
                with self.subTest(classes=classes, kit=kit):
                    mu.mem_write(SS * 16 + 0x500, bytes(s))
                    mu.mem_write(SS * 16 + 0x7FC, struct.pack("<H", 0xFFF0))
                    for name, value in dict(cs=TSR, ds=GAME_DS, es=SS, ebx=0x500, ss=SS, esp=0x7FC).items():
                        mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
                    mu.emu_start(TSR * 16 + start, TSR * 16 + 0xFFF0)
                    got = mu.reg_read(r.UC_X86_REG_AX)
                    self.assertEqual([k for k in range(16) if got >> k & 1], restrict.allowed_kinds(bytes(s), self.record))
            game.RULES_IN_FORCE = game.RULE_KITS | game.RULE_RESTRICT  # an Elementalist's second sphere's kinds too
            for cls, second in ((1, 3), (3, 3), (3, 0), (2, 2)):
                s = bytearray(sheet(cls))
                s[0x43], s[0x45] = 1, second + 1
                with self.subTest(cls=cls, second=second):
                    mu.mem_write(SS * 16 + 0x500, bytes(s))
                    mu.mem_write(SS * 16 + 0x7FC, struct.pack("<H", 0xFFF0))
                    for name, value in dict(cs=TSR, ds=GAME_DS, es=SS, ebx=0x500, ss=SS, esp=0x7FC).items():
                        mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
                    mu.emu_start(TSR * 16 + start, TSR * 16 + 0xFFF0)
                    got = mu.reg_read(r.UC_X86_REG_AX)
                    want = restrict.allowed_kinds(bytes(s), self.record)
                    self.assertEqual([k for k in range(16) if got >> k & 1], want)
                    s[0x45] = 0
                    self.assertLessEqual(set(restrict.allowed_kinds(bytes(s), self.record)), set(want))
        finally:
            game.RULES_IN_FORCE = old
            mu.mem_write(hdr + 270, struct.pack("<H", 0))
        ranger = restrict.allowed_kinds(sheet(13), self.record)  # (no bow: a ranger's expertise already)
        self.assertNotIn(specialize.KINDS.index("bow"), ranger)
        self.assertIn(specialize.KINDS.index("bow"), restrict.allowed_kinds(sheet(9), self.record))
        fire = restrict.allowed_kinds(sheet(9, 3), self.record)
        self.assertEqual([specialize.KINDS[k] for k in fire],
                         ["long sword", "dagger", "short sword", "mace", "axe", "great axe", "chatkcha"])


@unittest.skipIf(Uc is None, "unicorn is not installed")
class XpNextTests(unittest.TestCase):
    """View Character's next-level XP (PROBE_XP_NEXT): for more than one class, the class (or
    classes) whose next level it is before the ")", by the game's own XP tables; for one, the
    game's ")" as before, and for a human (who dual-classes: the game counts the first class
    only). (The screen's copy of the sheet numbers classes 1-8: 3 fighter, 5 preserver, 6
    psionicist, 8 thief; its +18h is the race, 1 human, 3 elf.)"""
    SHEET, TABLE = 0x8000, 0x9000
    RULES = 170

    def setUp(self):
        image = load_image()
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, image)
        at = image.find(bytes.fromhex("50535152565706" "0fa8"))
        self.assertGreater(at, 18)
        mu.mem_write(VEC_XP_NEXT * 4, struct.pack("<HH", at - 15, TSR))  # (past the three pops)
        mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        mu.mem_write(CALLER * 16 + 0x602 - 0x8B, bytes((0xB8,)) + struct.pack("<H", self.TABLE))  # mov ax,seg
        mu.mem_write(SS * 16 + BP + 0x0A, struct.pack("<HH", 0, self.SHEET))
        for cls, level, xp in ((3, 4, 16000), (5, 4, 20000), (8, 5, 20000), (6, 4, 20000), (3, 9, 0), (3, 10, 0)):
            mu.mem_write(self.TABLE * 16 + cls * 40 + level * 2 + 0x27C, struct.pack("<H", xp // 100))

    def run_with(self, classes, levels, least, rules=0, race=3):
        mu = self.mu
        mu.mem_write(TSR * 16 + load_image().find(HDR_SIG) + self.RULES, struct.pack("<H", rules))
        sheet = bytearray(0x30)
        sheet[0x18] = race
        sheet[0x21:0x24], sheet[0x24:0x27] = bytes(classes), bytes(levels)
        mu.mem_write(self.SHEET * 16, bytes(sheet))
        mu.mem_write(SS * 16 + BP - 6, struct.pack("<I", least))
        mu.mem_write(SS * 16 + 0x7FC, struct.pack("<HH", GAME_DS, 0x50))  # pushed: DS, the length
        mu.mem_write(CALLER * 16 + 0x600, bytes((0xCD, VEC_XP_NEXT, 0x90)))
        for name, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x7FC, ebp=BP, eflags=IF | 2, eax=0x1111,
                                ebx=0x2222, ecx=0x3333, edx=0x4444, esi=0x5555, edi=0x6666, es=0x7777).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(CALLER * 16 + 0x600, CALLER * 16 + 0x603)
        self.assertEqual([mu.reg_read(x) for x in (r.UC_X86_REG_SP, r.UC_X86_REG_AX, r.UC_X86_REG_BX, r.UC_X86_REG_CX,
                                                   r.UC_X86_REG_DX, r.UC_X86_REG_SI, r.UC_X86_REG_DI, r.UC_X86_REG_BP,
                                                   r.UC_X86_REG_DS, r.UC_X86_REG_ES)],
                         [0x7FA, 0x1111, 0x2222, 0x3333, 0x4444, 0x5555, 0x6666, BP, GAME_DS, 0x7777])
        off, seg, length = struct.unpack("<HHH", mu.mem_read(SS * 16 + 0x7FA, 6))
        self.assertEqual(length, 0x50)
        if seg == GAME_DS:
            return off
        return bytes(mu.mem_read(seg * 16 + off, 12)).split(b"\0")[0].decode()

    def test_one_class_due(self):
        self.assertEqual(self.run_with((3, 5, 8), (4, 4, 5), 16000), " F)")  # (Xan)

    def test_two_due_at_once(self):
        self.assertEqual(self.run_with((3, 5, 8), (5, 4, 5), 20000), " Pr/T)")

    def test_preserver_and_psionicist(self):
        self.assertEqual(self.run_with((5, 6, 0), (4, 4, 0), 20000), " Pr/Ps)")

    def test_one_class_as_the_game(self):
        """An elf fighter: one class, nothing to tell apart."""
        self.assertEqual(self.run_with((3, 0, 0), (4, 0, 0), 16000), 0x10F4)

    def test_human_as_the_game(self):
        """A dual-classed human: the game's own line, whatever the slots hold."""
        self.assertEqual(self.run_with((3, 8, 0), (4, 5, 0), 16000, race=1), 0x10F4)

    def test_at_the_cap(self):
        """A class at the level cap (9, or 10 with that rule) has no next level, so isn't named."""
        self.assertEqual(self.run_with((3, 5, 0), (9, 4, 0), 20000), " Pr)")
        self.assertEqual(self.run_with((3, 5, 0), (10, 4, 0), 20000, rules=128), " Pr)")


@unittest.skipIf(Uc is None, "unicorn is not installed")
class ItemSaveTests(unittest.TestCase):
    """The acid's and corroding touch's item checks (PROBE_ITEM_*): the number a d20 needs, the
    game's or (RULE_ITEM_SAVES) the easier of it and AD&D's, and each check recorded."""
    ITEMS, TYPES = 0xA000, 0xB000
    RULES = 170
    # item: (type, material, plus, power)
    GEAR = {4: (6, 5, 0, 0), 5: (57, 4, 0, 0), 6: (79, 5, 1, 89), 7: (81, 1, 0, 0), 8: (63, 4, 1, 0),
            9: (17, 3, 0, 0), 10: (90, 0x40, 2, 0)}

    def setUp(self):
        image = load_image()
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, image)
        self.hdr_off = struct.unpack_from("<H", image, 20)[0]
        self.ring = struct.unpack_from("<H", image, 16)[0]
        for vec, head in ((VEC_ITEM_WEAPON, "5650535157ba08002b56fe"), (VEC_ITEM_ARMOUR, "5650535157ba0a002b56fe"),
                          (VEC_ITEM_SKIP, "5589e5836606bf5d2ef706")):
            at = image.find(bytes.fromhex(head))
            self.assertGreater(at, 0, head)
            mu.mem_write(vec * 4, struct.pack("<HH", at, TSR))
        mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        mu.mem_write(GAME_DS * 16 + 0x165D, struct.pack("<HH", 0, self.ITEMS))
        mu.mem_write(GAME_DS * 16 + 0x1669, struct.pack("<HH", 0, self.TYPES))
        for item, (typ, material, plus, power) in self.GEAR.items():
            rec = bytearray(21)
            struct.pack_into("<H", rec, 0x0A, typ)
            rec[0x0F], rec[0x14] = power & 0xFF, plus & 0xFF
            mu.mem_write(self.ITEMS * 16 + item * 21, bytes(rec))
            mu.mem_write(self.TYPES * 16 + typ * 0x14 + 8, bytes([material]))
        # the routine's frame: the saved BP (its caller's, the special attack's: 187 on target 3
        # from 44), its argument (the target); the list's entry 2 holds the item
        mu.mem_write(SS * 16 + BP, struct.pack("<HHHH", PARENT_BP, 0, 0, 3))
        mu.mem_write(SS * 16 + PARENT_BP, struct.pack("<HHHHHHHH", 0, 0, 0, 3, 44, 0, 0, 187))
        self.at = 0x600

    def rules(self, value):
        self.mu.mem_write(TSR * 16 + load_image().find(HDR_SIG) + self.RULES, struct.pack("<H", value))

    def run_int(self, vec, item, word, roll, armour):
        """INT VEC with the list's entry 2 the item, [BP-2] WORD (the plus or the power), AX the
        d20: DX, ZF and the entry recorded (None if none)."""
        mu = self.mu
        list_at = BP - (0x31E if armour else 0x320) + 2 * 0x0A
        mu.mem_write(SS * 16 + list_at, struct.pack("<H", item))
        mu.mem_write(SS * 16 + BP - 2, struct.pack("<h", word))
        seq_at = TSR * 16 + self.hdr_off + 8
        before = struct.unpack("<H", mu.mem_read(seq_at, 2))[0]
        self.at += 0x20
        mu.mem_write(CALLER * 16 + self.at, bytes((0xCD, vec)))
        for name, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800, ebp=BP, eflags=IF | 2, eax=roll,
                                esi=2, ebx=0x2222, ecx=0x3333, edx=0x4444, edi=0x5555, es=0x6666).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(CALLER * 16 + self.at, CALLER * 16 + self.at + 2)
        self.assertEqual([mu.reg_read(x) for x in (r.UC_X86_REG_SP, r.UC_X86_REG_AX, r.UC_X86_REG_BX,
                                                   r.UC_X86_REG_CX, r.UC_X86_REG_SI, r.UC_X86_REG_DI,
                                                   r.UC_X86_REG_BP, r.UC_X86_REG_DS, r.UC_X86_REG_ES)],
                         [0x800, roll, 0x2222, 0x3333, 2, 0x5555, BP, GAME_DS, 0x6666])
        seq, widx, nent = struct.unpack("<HHH", mu.mem_read(seq_at, 6))
        entry = None
        if seq != before:
            entry = Entry.parse(bytes(mu.mem_read(RING_SEG * 16 + self.ring + ((seq - 1) % nent) * Entry.SIZE,
                                                  Entry.SIZE)))
        dx = struct.unpack("<h", struct.pack("<H", mu.reg_read(r.UC_X86_REG_DX)))[0]
        return dx, bool(mu.reg_read(r.UC_X86_REG_EFLAGS) & 0x40), entry

    def weapon(self, item, roll=10):
        return self.run_int(VEC_ITEM_WEAPON, item, self.GEAR[item][2], roll, False)

    def armour(self, item, roll=10):
        return self.run_int(VEC_ITEM_ARMOUR, item, self.GEAR[item][3], roll, True)

    def test_weapons_the_games(self):
        self.rules(0)
        for item, want in ((7, 8), (8, 7), (9, 8)):
            dx, _, e = self.weapon(item, 12)
            self.assertEqual(dx, want, item)
            self.assertEqual((e.kind, e.raw, e.extra, e.arg(6), e.parent_arg(0x0E)), (4, 12 | want << 8, item, 3, 187))

    def test_weapons_the_easier(self):
        """Bone (11) and metal +1 (12) keep the game's 8 and 7; obsidian gets AD&D's 5."""
        self.rules(2048)
        self.assertEqual([self.weapon(item)[0] for item in (7, 8, 9)], [8, 7, 5])

    def test_armour_the_games(self):
        """No magical power: destroyed without a roll (ZF set, recorded with no d20); with one,
        10 less it (Drake Armor's 89: never)."""
        self.rules(0)
        for item in (4, 5, 10):
            dx, zf, e = self.run_int(VEC_ITEM_SKIP, item, 0, 0x1234, True)
            self.assertTrue(zf, item)
            self.assertEqual((e.kind, e.raw & 0xFF, e.extra), (4, 0, 0x8000 | item))
        dx, zf, e = self.run_int(VEC_ITEM_SKIP, 6, 89, 0x1234, True)
        self.assertEqual((zf, e), (False, None))
        self.assertEqual(self.armour(6)[0], 10 - 89)

    def test_armour_the_easier(self):
        """Leather 10, metal 13, cloth +2 10; Drake Armor keeps the game's (never)."""
        self.rules(2048)
        for item in (4, 5, 6, 10):
            dx, zf, e = self.run_int(VEC_ITEM_SKIP, item, self.GEAR[item][3], 0x1234, True)
            self.assertEqual((zf, e), (False, None), item)
        self.assertEqual([self.armour(item)[0] for item in (4, 5, 6, 10)], [10, 13, 10 - 89, 10])
        dx, _, e = self.armour(5, 14)
        self.assertEqual((e.raw, e.extra), (14 | 13 << 8, 0x8000 | 5))


@unittest.skipIf(Uc is None, "unicorn not installed")
class RuleTests(RingTests):
    """The companion's rule changes: two weapons' to-hit, and the doubled save d20."""
    RULES = 170  # the header's RULES word

    def setUp(self):
        super().setUp()
        image = load_image()
        def handler(vector):  # (the helper's install code: "mov ax,25xxh / mov dx,handler")
            at = image.find(bytes((0xB8, vector, 0x25, 0xBA)))
            return struct.unpack_from("<H", image, at + 4)[0] if at > 0 else -1
        two, double = handler(VEC_TWO), handler(VEC_DOUBLE)
        self.assertGreater(min(two, double), 0)
        self.mu.mem_write(VEC_TWO * 4, struct.pack("<HH", two, TSR))
        self.mu.mem_write(VEC_DOUBLE * 4, struct.pack("<HH", double, TSR))

    def rules(self, value):
        self.mu.mem_write(TSR * 16 + self.RULES, struct.pack("<H", value))

    def two(self, dex_adjust, item):
        """INT VEC_TWO with AX the DEX's initiative adjustment, [BP+0Ah] the attack's item and
        CX the attacker's object (3: creature 1): the adjustment in DX."""
        self.mu.mem_write(SS * 16 + BP + 0x0A, struct.pack("<H", item))
        self.run_at(bytes((0xCD, VEC_TWO)), eax=dex_adjust & 0xFFFF, ebx=0x2222, ecx=3, es=0x6666)
        self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_BX, r.UC_X86_REG_CX, r.UC_X86_REG_ES)],
                         [0x2222, 3, 0x6666])
        return struct.unpack("<h", struct.pack("<H", self.mu.reg_read(r.UC_X86_REG_DX)))[0]

    def hands(self, right=(81, 3), left=(81, 10)):
        """Creature 1's items 4 and 7 as (type, slot); type 81 is a melee weapon (class 1),
        type 90 a shield (class 0)."""
        self.mu.mem_write(GAME_DS * 16 + 0x1669, struct.pack("<HH", 0, self.TYPES))
        things = (GAME_DS + 0x3972 - 0x4356) * 16 + 0xC36  # where the game keeps them, from DS
        for thing, kind, index in ((3, 2, 1), (10, 1, 4), (11, 1, 7), (12, 1, 5)):
            self.mu.mem_write(things + thing * 3, struct.pack("<BH", kind, index))
        for typ, cls in ((81, 1), (90, 0), (60, 2)):
            self.mu.mem_write(self.TYPES * 16 + typ * 0x14 + 0x0A, bytes([cls]))
        for item, (typ, slot) in ((4, right), (7, left)):
            rec = bytearray(self.mu.mem_read(self.ITEMS * 16 + item * 21, 21))
            struct.pack_into("<H", rec, 0x0A, typ)
            rec[0x11] = slot
            self.mu.mem_write(self.ITEMS * 16 + item * 21, bytes(rec))

    def test_two_weapons_the_games(self):
        self.rules(0)
        self.hands()
        self.assertEqual([self.two(adj, 4) for adj in (-6, -1, 0, 3)], [6, 1, 0, 0])

    def test_two_weapons_adnd(self):
        """A weapon in each hand: item 4 in the right (main), item 7 in the left (off)."""
        self.rules(4)
        self.hands()
        self.assertEqual([self.two(adj, 4) for adj in (-3, 0, 1, 2, 5)], [-5, -2, -1, 0, 0])
        self.assertEqual([self.two(adj, 7) for adj in (-3, 0, 2, 3, 4, 5)], [-7, -4, -2, -1, 0, 0])

    def test_twin_blade(self):
        """A Twin-blade (kits on): no AD&D two-weapon penalty, as kits.py's; the game's own bonus
        without the rule kept."""
        self.hands()
        seg, off = struct.unpack("<HH", self.mu.mem_read(GAME_DS * 16 + 0x1665, 4))[::-1]
        sheets = 0xB800
        self.mu.mem_write(GAME_DS * 16 + 0x1661, struct.pack("<HH", 0, sheets))
        self.mu.mem_write(seg * 16 + off + 0x3A + 4, struct.pack("<H", 1))  # (creature 1: sheet 1)
        sheet = bytearray(game.SHEET_SIZE)
        sheet[0x21], sheet[0x43] = 10, 2
        self.mu.mem_write(sheets * 16 + 0x47, bytes(sheet))
        self.mu.mem_write(TSR * 16 + self.RULES + 100, struct.pack("<H", 1))  # (RULES_HI, +270)
        try:
            self.rules(4)
            self.assertEqual([self.two(adj, 4) for adj in (-3, 0)] + [self.two(adj, 7) for adj in (-3, 0)], [0] * 4)
            self.rules(0)
            self.assertEqual(self.two(-6, 4), 6)
        finally:
            self.mu.mem_write(TSR * 16 + self.RULES + 100, struct.pack("<H", 0))

    def test_one_weapon_no_penalty(self):
        """A shield in the other hand, a bow in the missile slot, or the weapon not in a hand:
        no penalty, whatever the DEX."""
        self.rules(4)
        for right, left in (((81, 3), (90, 10)), ((81, 3), (60, 2)), ((81, 3), (81, 0xFF)), ((81, 2), (81, 10))):
            self.hands(right, left)
            self.assertEqual([self.two(adj, 4) for adj in (-3, 0)], [0, 0], (right, left))

    def test_doubled_save(self):
        for rules, want in ((0, 14), (16, 7)):
            self.rules(rules)
            self.run_at(bytes((0xCD, VEC_DOUBLE)), eax=7)
            self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AL), want)

    def level(self, level):
        """INT VEC_LEVEL with ES:BX a sheet whose class level (+24h) is LEVEL: (below the cap,
        at it), from the flags the game's JL and JZ read; AX and interrupts as they were."""
        image = load_image()
        probe = image.find(bytes.fromhex("fb50b0092ef606") + struct.pack("<H", self.RULES) + bytes([128]))
        self.assertGreater(probe, 0)
        self.mu.mem_write(VEC_LEVEL * 4, struct.pack("<HH", probe, TSR))
        self.mu.mem_write(self.TYPES * 16 + 0x100 + 0x24, bytes([level]))
        self.run_at(bytes((0xCD, VEC_LEVEL)), es=self.TYPES, ebx=0x100, eax=0x1234)
        flags = self.mu.reg_read(r.UC_X86_REG_EFLAGS)
        self.assertEqual((self.mu.reg_read(r.UC_X86_REG_AX), bool(flags & IF)), (0x1234, True))
        return bool(flags & 0x80) != bool(flags & 0x800), bool(flags & 0x40)

    def test_level_cap(self):
        """The game's cap of 9, or 10 with rule 128."""
        self.rules(0)
        self.assertEqual([self.level(n) for n in (1, 8, 9, 10)],
                         [(True, False), (True, False), (False, True), (False, False)])
        self.rules(128)
        self.assertEqual([self.level(n) for n in (8, 9, 10, 11)],
                         [(True, False), (True, False), (False, True), (False, False)])

    def hit_dice(self, cls, levels=9):
        """INT VEC_HD_ROLL with ES:BX a hit point group whose dice go up to LEVELS and the
        game's [BP+8] the class: the levels that roll dice, in AL."""
        image = load_image()
        probe = image.find(bytes.fromhex("268a4701") + bytes.fromhex("2ef606") + struct.pack("<H", self.RULES))
        self.assertGreater(probe, 0)
        self.mu.mem_write(VEC_HD_ROLL * 4, struct.pack("<HH", probe, TSR))
        self.mu.mem_write(self.TYPES * 16 + 0x200, bytes([6, levels, 2, 6]))
        self.mu.mem_write(SS * 16 + BP + 8, struct.pack("<H", cls))
        self.run_at(bytes((0xCD, VEC_HD_ROLL)), es=self.TYPES, ebx=0x200, eax=0x1200)
        self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AH), 0x12)
        return self.mu.reg_read(r.UC_X86_REG_AL)

    def test_thief_hit_dice(self):
        """A thief (17) rolls up to 10th with rule 128; a psionicist (12) still stops at 9th."""
        self.rules(0)
        self.assertEqual([self.hit_dice(c) for c in (17, 12)], [9, 9])
        self.rules(128)
        self.assertEqual([self.hit_dice(c) for c in (17, 12)], [10, 9])
        self.assertEqual(self.hit_dice(17, levels=10), 10)  # (a preserver's group: as it was)

    def thief_skill(self, skill, level, dex, base_race):
        """INT VEC_THIEF_SKILL with DX the skill's base + race adjustment (the game's bases at
        ES:0), SI the thief level, the game's [BP+8] the skill and [BP-0Ch] DEX: (SI, CF), with
        DX and ES as they were."""
        image = load_image()
        probe = image.find(bytes.fromhex("fb2ef706") + struct.pack("<HH", self.RULES, 256))
        self.assertGreater(probe, 0)
        self.mu.mem_write(VEC_THIEF_SKILL * 4, struct.pack("<HH", probe, TSR))
        self.mu.mem_write(self.TYPES * 16, bytes([28, 18, 13, 28, 18, 23, 78, 252]))  # the game's bases
        self.mu.mem_write(SS * 16 + BP + 8, struct.pack("<I", skill))
        self.mu.mem_write(SS * 16 + BP - 0x0C, struct.pack("<H", dex))
        self.run_at(bytes((0xCD, VEC_THIEF_SKILL)), es=self.TYPES, esi=level, edx=base_race, eax=0x1234, ebx=0x5678)
        regs = [self.mu.reg_read(x) for x in (r.UC_X86_REG_AX, r.UC_X86_REG_BX, r.UC_X86_REG_ES, r.UC_X86_REG_BP)]
        self.assertEqual(regs, [0x1234, 0x5678, self.TYPES, BP])
        return self.mu.reg_read(r.UC_X86_REG_SI), self.mu.reg_read(r.UC_X86_REG_EFLAGS) & 1

    def test_thief_skills(self):
        """The game's sum without rule 256 (on to its DEX formula); with it, AD&D's table, the race
        and Dark Sun's DEX adjustment (past the game's formula). Azil: 3rd level elf, DEX 22."""
        self.rules(0)
        self.assertEqual(self.thief_skill(1, 3, 22, 18 - 5), (13 + 12, 0))  # open locks
        self.rules(256)
        self.assertEqual(self.thief_skill(0, 3, 22, 28 + 5), (40 + 5 + 27, 1))  # pick pockets
        self.assertEqual(self.thief_skill(1, 3, 22, 18 - 5), (33 - 5 + 30, 1))
        self.assertEqual(self.thief_skill(3, 3, 22, 28 + 5), (27 + 5 + 30, 1))  # move silently
        self.assertEqual(self.thief_skill(4, 3, 22, 18 + 10), (20 + 10 + 22, 1))  # hide
        self.assertEqual(self.thief_skill(5, 3, 22, 23 + 5), (15 + 5, 1))  # hear noise: no DEX
        self.assertEqual(self.thief_skill(6, 3, 22, 78), (87, 1))  # climb walls
        self.assertEqual(self.thief_skill(4, 1, 9, 18), (10 - 10, 1))  # DEX 9
        self.assertEqual(self.thief_skill(3, 1, 7, 28), ((15 - 20) & 0xFFFF, 1))  # below 9: as 9 (the game clamps at 0 later)
        self.assertEqual(self.thief_skill(0, 12, 24, 28), (80 + 27, 1))  # past 10th and DEX 22
        self.assertEqual(self.thief_skill(7, 3, 22, (252 - 256) & 0xFFFF), (0, 1))  # read languages
        self.assertEqual(self.thief_skill(0, 0, 22, 28), (28, 0))  # no thief level: the game's

    def test_bone_helm_counts_as_a_helm(self):
        """Helms give AC 1 (rule 1): the companion's bone helm (type 117) as the game's (5)."""
        for typ in (5, 117):
            for rules, want in ((1, 1), (0, 0)):
                self.rules(rules)
                self.mu.mem_write(self.TYPES * 16 + 0x12, bytes([9]))
                self.run_at(bytes((0xCD, VEC_RING_AC)), es=self.TYPES, ebx=0, ecx=typ, eax=0)
                self.assertEqual(self.mu.mem_read(self.TYPES * 16 + 0x12, 1)[0], want, (typ, rules))

    def two_handed(self, race, flags=0x40):
        """INT VEC_TWO_HANDED with ES:BX an item type whose +0Fh is FLAGS, for the character on
        show (number 2, at the game's 0348h:25Bh) of RACE: ZF (the game's JE: not two-handed),
        with AX, BX and ES as they were."""
        image = load_image()
        probe = image.find(bytes.fromhex("fb2ef706") + struct.pack("<HH", self.RULES, 512))
        self.assertGreater(probe, 0)
        self.mu.mem_write(VEC_TWO_HANDED * 4, struct.pack("<HH", probe, TSR))
        who = (GAME_DS + 0x3931 - 0x4356) & 0xFFFF  # (as the running game has it: DS - 0A25h)
        self.mu.mem_write(who * 16 + 0x25B, struct.pack("<H", 2))
        sheets = self.TYPES * 16 + 0x400
        self.mu.mem_write(GAME_DS * 16 + 0x1661, struct.pack("<HH", 0x400, self.TYPES))
        self.mu.mem_write(sheets + 2 * 0x47 + 0x18, bytes([race]))
        self.mu.mem_write(self.TYPES * 16 + 0x300 + 0x0F, bytes([flags]))
        self.run_at(bytes((0xCD, VEC_TWO_HANDED)), es=self.TYPES, ebx=0x300, eax=0x1234)
        regs = [self.mu.reg_read(x) for x in (r.UC_X86_REG_AX, r.UC_X86_REG_BX, r.UC_X86_REG_ES)]
        self.assertEqual(regs, [0x1234, 0x300, self.TYPES])
        return bool(self.mu.reg_read(r.UC_X86_REG_EFLAGS) & 0x40)

    def test_half_giants_two_handed_in_one_hand(self):
        """Rule 512: a half-giant's two-handed weapon counts as one-handed; anyone else's, or
        without the rule, as the game has it; a one-handed weapon is one-handed for all."""
        self.rules(0)
        self.assertEqual([self.two_handed(r) for r in (5, 1)], [False, False])  # (ZF clear: two-handed)
        self.rules(512)
        self.assertEqual([self.two_handed(r) for r in (5, 1)], [True, False])
        self.assertEqual([self.two_handed(r, flags=0) for r in (5, 1)], [True, True])

    def spell_text(self, spin, length=112):
        """INT VEC_SPELL_TEXT after the game read SPIN chunk SPIN (LENGTH bytes) into the buffer
        at the game's [BP-8]: (the buffer's text, AX), with SP back past the read's arguments."""
        image = load_image()
        # its rule test and "cmp di,0Fh", after three pops, "add sp,0Ch" and three pushes (33 bytes)
        anchor = image.find(bytes.fromhex("2ef606") + struct.pack("<H", self.RULES) + bytes.fromhex("207425" "83ff0f"))
        self.assertGreater(anchor, 0)
        probe = anchor - 33
        self.assertEqual(image[probe:probe + 3], bytes.fromhex("2e8f06"))
        self.mu.mem_write(VEC_SPELL_TEXT * 4, struct.pack("<HH", probe, TSR))
        buf = self.TYPES * 16 + 0x500
        self.mu.mem_write(buf, b"FLAMING SPHERE:  Creates a burning globe.\r\n\0".ljust(200, b"\0"))
        self.mu.mem_write(SS * 16 + BP - 8, struct.pack("<HH", 0x500, self.TYPES))
        code = bytes.fromhex("666a00666a00666a00") + bytes((0xCD, VEC_SPELL_TEXT))  # 12 bytes of arguments
        self.at += 0x20
        self.mu.mem_write(CALLER * 16 + self.at, code)
        for name, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800, ebp=BP, eflags=IF | 2, edi=spin, eax=length).items():
            self.mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        self.mu.emu_start(CALLER * 16 + self.at, CALLER * 16 + self.at + len(code))
        self.assertEqual(self.mu.reg_read(r.UC_X86_REG_SP), 0x800)
        text = bytes(self.mu.mem_read(buf, 200)).split(b"\0")[0]
        return text, self.mu.reg_read(r.UC_X86_REG_AX)

    def test_cats_grace_description(self):
        """Rule 32: Flaming Sphere's description (SPIN 15) is Cat's Grace's; others, and without
        the rule, the game's."""
        grace = b"CAT'S GRACE:  Raises the target's dexterity by 1 to 6 pts. Maximum dexterity is 24.\r\n"
        self.rules(32)
        self.assertEqual(self.spell_text(15), (grace, len(grace)))
        self.assertEqual(self.spell_text(14)[0][:15], b"FLAMING SPHERE:")
        self.assertEqual(self.spell_text(15, 0xFFFF)[1], 0xFFFF)  # (no chunk read)
        self.rules(0)
        self.assertEqual(self.spell_text(15), (b"FLAMING SPHERE:  Creates a burning globe.\r\n", 112))

    def chunk_id(self, kind, number, resources_on=1, limit=0x0100):
        """INT VEC_CHUNK_ID at the start of a chunk-loading routine whose [BP+6] is KIND and
        [BP+0Ah] NUMBER, the game's stack limit (DS:9Ch) LIMIT: (the number it then loads, CF from
        the stack check)."""
        image = load_image()
        icon = image.find(bytes.fromhex("66817e06") + b"ICON")
        self.assertGreater(icon, 0)
        probe = image.rfind(bytes.fromhex("2ef606") + struct.pack("<H", self.RULES), 0, icon) - 1
        self.assertEqual(image[probe], 0xFB)  # (its STI)
        on, = struct.unpack_from("<H", image, image.find(bytes.fromhex("2e833e"), probe) + 3)
        self.mu.mem_write(TSR * 16 + on, struct.pack("<H", resources_on))
        self.mu.mem_write(VEC_CHUNK_ID * 4, struct.pack("<HH", probe, TSR))
        self.mu.mem_write(SS * 16 + BP + 6, kind + struct.pack("<I", number))
        self.mu.mem_write(GAME_DS * 16 + 0x9C, struct.pack("<H", limit))
        self.run_at(bytes((0xCD, VEC_CHUNK_ID)), eax=0x1234)
        self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), 0x1234)
        number, = struct.unpack("<I", self.mu.mem_read(SS * 16 + BP + 0x0A, 4))
        self.assertTrue(self.mu.reg_read(r.UC_X86_REG_EFLAGS) & IF)  # (interrupts on: RETF 2 keeps flags)
        return number, self.mu.reg_read(r.UC_X86_REG_EFLAGS) & 1

    def test_cats_grace_icon(self):
        """Rule 32, with the copy of RESOURCE.GFF open: Flaming Sphere's icon (21014) is asked for as
        Cat's Grace's (21900); other icons and chunks, or without the rule or the copy, as asked.
        The stack check as the game's: CF when its limit is below SP (0x800), not when above."""
        self.rules(32)
        self.assertEqual(self.chunk_id(b"ICON", 21014), (21900, 1))
        self.assertEqual(self.chunk_id(b"ICON", 21015)[0], 21015)
        self.assertEqual(self.chunk_id(b"SPIN", 21014)[0], 21014)
        self.assertEqual(self.chunk_id(b"ICON", 21014, resources_on=0)[0], 21014)
        self.assertEqual(self.chunk_id(b"ICON", 21014, limit=0x900)[1], 0)
        self.rules(0)
        self.assertEqual(self.chunk_id(b"ICON", 21014)[0], 21014)

    def con_levels(self, cls, level):
        """INT VEC_HD_CON with AL a class's level, ES:BX its group (dice up to 9), the game's
        [BP-4] a sheet whose second class (CX = 1) is CLS: whether the level is past the cap
        (the game's JNG not taken); DX and the sheet's ES:BX as they were."""
        image = load_image()
        probe = image.find(bytes.fromhex("fb52268a5701"))
        self.assertGreater(probe, 0)
        self.mu.mem_write(VEC_HD_CON * 4, struct.pack("<HH", probe, TSR))
        self.mu.mem_write(self.TYPES * 16 + 0x200, bytes([6, 9, 2, 6]))
        self.mu.mem_write(self.CREATURES * 16 + 0x300 + 0x21, bytes([12, cls, 0]))
        self.mu.mem_write(SS * 16 + BP - 4, struct.pack("<HH", 0x300, self.CREATURES))
        self.run_at(bytes((0xCD, VEC_HD_CON)), es=self.TYPES, ebx=0x200, ecx=1, edx=0x5555, eax=level)
        mu = self.mu
        self.assertEqual([mu.reg_read(x) for x in (r.UC_X86_REG_DX, r.UC_X86_REG_ES, r.UC_X86_REG_BX)],
                         [0x5555, self.TYPES, 0x200])
        flags = mu.reg_read(r.UC_X86_REG_EFLAGS)
        return not (flags & 0x40 or bool(flags & 0x80) != bool(flags & 0x800))

    def test_thief_con_levels(self):
        self.rules(0)
        self.assertEqual([self.con_levels(17, n) for n in (9, 10)], [False, True])
        self.rules(128)
        self.assertEqual([self.con_levels(c, n) for c, n in ((17, 9), (17, 10), (12, 10))], [False, False, True])



@unittest.skipIf(Uc is None, "unicorn not installed")
class GraceTests(RuleTests):
    """Cat's Grace (spell 14, rule 32): Strength's code, its own effect (54), DEX."""

    def setUp(self):
        super().setUp()
        image = load_image()
        for vector, start in ((VEC_GRACE_CAST, "8b460e2ef606aa0020"), (VEC_GRACE_EFFECT, "c746ec4300817e0e9400"),
                              (VEC_GRACE_ABILITY, "8946f6b90700")):
            at = image.find(bytes.fromhex(start))
            self.assertGreater(at, 0)
            self.mu.mem_write(vector * 4, struct.pack("<HH", at, TSR))

    def word(self, offset, value=None):
        at = SS * 16 + (BP + offset) % 0x10000
        if value is not None:
            self.mu.mem_write(at, struct.pack("<h", value))
        return struct.unpack("<h", self.mu.mem_read(at, 2))[0]

    def test_cast_goes_to_strength(self):
        for rules, spell, want in ((32, 14, 23), (0, 14, 14), (32, 20, 20), (32, 23, 23)):
            self.rules(rules)
            self.word(0x0E, spell)
            self.run_at(bytes((0xCD, VEC_GRACE_CAST)))
            self.assertEqual((self.word(-0x1A), self.mu.reg_read(r.UC_X86_REG_AX)), (want, spell if want == spell else 23))

    def test_its_own_effect(self):
        for rules, spell, want in ((32, 14, 54), (0, 14, 0x43), (32, 23, 0x43), (32, 0x94, 0x42), (0, 0x94, 0x42)):
            self.rules(rules)
            self.word(0x0E, spell)
            self.run_at(bytes((0xCD, VEC_GRACE_EFFECT)))
            self.assertEqual(self.word(-0x14), want, (rules, spell))

    def test_adds_to_dex(self):
        effects = 0x9800
        self.mu.mem_write(effects * 16 + 0x10F, bytes([5]))
        for effect, dex, want in ((54, 15, 20), (54, 21, 24), (67, 15, 15)):
            self.word(-0x340, dex)
            self.word(-0x342, 18)  # STR, untouched
            self.run_at(bytes((0xCD, VEC_GRACE_ABILITY)), eax=effect, ebx=0, es=effects, ecx=0)
            self.assertEqual((self.word(-0x340), self.word(-0x342), self.word(-0x0A)), (want, 18, effect))
            self.assertEqual(self.mu.reg_read(r.UC_X86_REG_CX), 7)


@unittest.skipIf(Uc is None, "unicorn not installed")
class NamesTests(unittest.TestCase):
    """The game's name table: room for NAMES_EXTRA more names, and DSCLOG's copied in."""
    NAMES_SEG = 0x5000

    def setUp(self):
        self.image = image = load_image()
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, image)
        size = image.find(bytes.fromhex("8146fc5203" "8356fe00"))
        fill = fill_probes(image)[0]
        self.assertGreater(min(size, fill), 0)
        mu.mem_write(VEC_NAMES_SIZE * 4, struct.pack("<HH", size, TSR))
        mu.mem_write(VEC_NAMES_FILL * 4, struct.pack("<HH", fill, TSR))
        mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        mu.mem_write(GAME_DS * 16 + 0x166D, struct.pack("<HH", 4, self.NAMES_SEG))
        self.hdr = TSR * 16 + image.find(HDR_SIG)

    def interrupt(self, vector, **regs):
        mu = self.mu
        mu.mem_write(CALLER * 16 + 0x600, bytes((0xCD, vector, 0x90)))
        for name, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800, ebp=BP, eflags=IF | 2, **regs).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(CALLER * 16 + 0x600, CALLER * 16 + 0x602)
        return mu.reg_read(r.UC_X86_REG_SP)

    def test_room(self):
        """In place of "push dword 1": the chunk's size (the dword at [BP-4]) gets the room."""
        for size, want in ((8050, 8900), (0xFF00, 0xFF00 + 850)):
            self.mu.mem_write(SS * 16 + BP - 4, struct.pack("<I", size))
            self.assertEqual(self.interrupt(VEC_NAMES_SIZE), 0x7FC)
            self.assertEqual(struct.unpack("<II", self.mu.mem_read(SS * 16 + 0x7FC, 4) +
                                           self.mu.mem_read(SS * 16 + BP - 4, 4)), (1, want))

    def test_filled(self):
        """In place of "add sp,0Ch": with the chunk read (AX 0), DSCLOG's names after the game's."""
        names = self.NAMES_SEG * 16 + 4 + 0x142 * 25
        self.assertEqual(self.interrupt(VEC_NAMES_FILL, eax=0), 0x80C)
        self.assertEqual(bytes(self.mu.mem_read(names, 50)),
                         b"Ring/Protection".ljust(25, b"\0") + b"Thieves' Tools".ljust(25, b"\0"))
        self.assertEqual(struct.unpack("<HH", self.mu.mem_read(self.hdr + 200, 4)), (4, self.NAMES_SEG))
        self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_AX, r.UC_X86_REG_DS, r.UC_X86_REG_BP)],
                         [0, GAME_DS, BP])

    def test_not_read(self):
        self.assertEqual(self.interrupt(VEC_NAMES_FILL, eax=1), 0x80C)
        self.assertEqual(bytes(self.mu.mem_read(self.NAMES_SEG * 16 + 4 + 0x142 * 25, 4)), bytes(4))
        self.assertEqual(bytes(self.mu.mem_read(self.hdr + 200, 4)), bytes(4))
        self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), 1)


@unittest.skipIf(Uc is None, "unicorn not installed")
class StealthTests(unittest.TestCase):
    """A hidden thief's attack (RULE_STEALTH, 64): from behind, a backstab when it can be."""
    SHEETS, TYPES = 0x8000, 0x9000

    def setUp(self):
        self.image = image = load_image()
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, image)
        self.hdr = TSR * 16 + image.find(HDR_SIG)
        at = image.find(bytes.fromhex("2ef606") + struct.pack("<H", 170) + bytes([64]))
        self.assertGreater(at, 0)
        mu.mem_write(VEC_STEALTH * 4, struct.pack("<HH", at - 15, TSR))  # (after its three pops)
        mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        mu.mem_write(GAME_DS * 16 + 0x1661, struct.pack("<HH", 0, self.SHEETS))
        mu.mem_write(GAME_DS * 16 + 0x1669, struct.pack("<HH", 0, self.TYPES))
        mu.mem_write(TSR * 16 + 170, struct.pack("<H", 64))

    def word(self, offset, value=None):
        at = SS * 16 + (BP + offset) % 0x10000
        if value is not None:
            self.mu.mem_write(at, struct.pack("<h", value))
        return struct.unpack("<h", self.mu.mem_read(at, 2))[0]

    def attack(self, attacker=2, hidden=0b0100, behind=0, stab=0, thac0=15, thief=True, melee=1,
               weight=20, target_object=0):
        """INT VEC_STEALTH with SI the attacker; its sheet 5 ([BP-12h]) a thief or not, its
        weapon of type 7 ([BP-4]): ([BP-1Ah], [BP-24h], [BP-20h], what was pushed, STEALTH,
        STEALTH_USED)."""
        mu = self.mu
        mu.mem_write(self.hdr + 204, struct.pack("<HH", hidden, 0))
        mu.mem_write(self.SHEETS * 16 + 5 * 0x47 + 0x12, struct.pack("<H", 0x400 if thief else 0))
        mu.mem_write(self.TYPES * 16 + 7 * 0x14 + 4, struct.pack("<H", weight))
        for offset, value in ((-0x12, 5), (-4, 7), (-0x1A, behind), (-0x24, stab), (-0x20, thac0),
                              (-0x1C, target_object), (0x0E, melee)):
            self.word(offset, value)
        mu.mem_write(CALLER * 16 + 0x600, bytes((0xCD, VEC_STEALTH, 0x90)))
        for name, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800, ebp=BP, eflags=IF | 2, esi=attacker,
                                eax=0x1111, ebx=0x2222, es=0x6666).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(CALLER * 16 + 0x600, CALLER * 16 + 0x602)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_SP), 0x7FE)
        self.assertEqual([mu.reg_read(x) for x in (r.UC_X86_REG_AX, r.UC_X86_REG_BX, r.UC_X86_REG_ES)],
                         [0x1111, 0x2222, 0x6666])
        pushed, = struct.unpack("<h", mu.mem_read(SS * 16 + 0x7FE, 2))
        stealth, used = struct.unpack("<HH", mu.mem_read(self.hdr + 204, 4))
        return self.word(-0x1A), self.word(-0x24), self.word(-0x20), pushed, stealth, used

    def test_backstab(self):
        self.assertEqual(self.attack(), (1, 1, 11, 1, 0, 1))

    def test_behind_already(self):
        """The game had it from behind: only the backstab's +2 more."""
        self.assertEqual(self.attack(behind=1, thac0=13), (1, 1, 11, 1, 0, 1))

    def test_no_backstab(self):
        """From behind only: not a thief, a missile, a weapon too heavy."""
        for kw in (dict(thief=False), dict(melee=2), dict(weight=41)):
            self.assertEqual(self.attack(**kw), (1, 0, 13, 1, 0, 1), kw)

    def test_not_hidden(self):
        self.assertEqual(self.attack(hidden=0b1011), (0, 0, 15, 0, 0b1011, 0))
        self.assertEqual(self.attack(attacker=0x29, hidden=0b1111), (0, 0, 15, 0, 0b1111, 0))

    def test_an_object(self):
        """Attacking an object (no back): nothing, but the hiding is over."""
        self.assertEqual(self.attack(target_object=1), (0, 0, 15, 0, 0, 1))

    def test_rule_off(self):
        self.mu.mem_write(TSR * 16 + 170, struct.pack("<H", 0))
        self.assertEqual(self.attack(), (0, 0, 15, 0, 0b0100, 0))


@unittest.skipIf(Uc is None, "unicorn not installed")
class TypesTests(unittest.TestCase):
    """The game's item type table: room for TYPES_EXTRA more, and DSCLOG's copied in after."""
    TYPES_SEG = 0x5000

    def setUp(self):
        image = load_image()
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, image)
        size = image.find(bytes.fromhex("8146fc0802" "8356fe00"))  # 26 types of 20 bytes: 208h
        names_fill, fill = fill_probes(image)
        self.assertGreater(min(size, fill - names_fill), 0)
        mu.mem_write(VEC_TYPES_SIZE * 4, struct.pack("<HH", size, TSR))
        mu.mem_write(VEC_TYPES_FILL * 4, struct.pack("<HH", fill, TSR))
        mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        mu.mem_write(GAME_DS * 16 + 0x1669, struct.pack("<HH", 0, self.TYPES_SEG))
        self.hdr = TSR * 16 + image.find(HDR_SIG)

    def interrupt(self, vector, **regs):
        mu = self.mu
        mu.mem_write(CALLER * 16 + 0x600, bytes((0xCD, vector, 0x90)))
        for name, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800, ebp=BP, eflags=IF | 2, **regs).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(CALLER * 16 + 0x600, CALLER * 16 + 0x602)
        return mu.reg_read(r.UC_X86_REG_SP)

    def test_room_and_filled(self):
        """The game's 115 types (2300 bytes): 500 bytes more reserved, and after the read
        DSCLOG's types at 115 on, the number noted, and Grey's Scale's arm and leg armour AC 3."""
        from dscompanion import npcitems
        self.mu.mem_write(SS * 16 + BP - 4, struct.pack("<I", 2300))
        self.assertEqual(self.interrupt(VEC_TYPES_SIZE), 0x7FC)
        self.assertEqual(struct.unpack("<I", self.mu.mem_read(SS * 16 + BP - 4, 4))[0], 2820)
        self.mu.mem_write(SS * 16 + 0x7FC, bytes(4))
        self.assertEqual(self.interrupt(VEC_TYPES_FILL, eax=0), 0x80C)
        at = self.TYPES_SEG * 16 + 115 * 20
        self.assertEqual(bytes(self.mu.mem_read(at, 20 * len(npcitems.TYPES))), b"".join(npcitems.TYPES))
        first, off, seg = struct.unpack("<HHH", self.mu.mem_read(self.hdr + 212, 6))
        self.assertEqual((first, off, seg), (115, 0, self.TYPES_SEG))
        for kind in (24, 54):  # (Grey's Scale's legs and arms)
            self.assertEqual(self.mu.mem_read(self.TYPES_SEG * 16 + kind * 20 + 0x12, 1)[0], 3)
        self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_AX, r.UC_X86_REG_DS)], [0, GAME_DS])

    def test_not_read(self):
        self.mu.mem_write(SS * 16 + BP - 4, struct.pack("<I", 2460))
        self.assertEqual(self.interrupt(VEC_TYPES_FILL, eax=1), 0x80C)
        self.assertEqual(bytes(self.mu.mem_read(self.hdr + 212, 6)), bytes(6))


if __name__ == "__main__":
    unittest.main()


@unittest.skipIf(Uc is None, "unicorn is not installed")
class SavePageTests(unittest.TestCase):
    """PROBE_SAVE_PAGE (PgUp, PgDn) and PROBE_SAVE_CLICK (PAGE 1, PAGE 2) in the save/load window's
    event routine: the page's letter in the game's two save names, the window's own routines run
    (here each a RETF, counted), and the routine going on where it should."""
    DS, OV = 0x9000, 0xA000  # the game's DS; the window's overlay segment (DSUN.EXE 74300h)
    SAVE = DS + 0x3BA7 - 0x4356
    KEY_AT, CLICK_AT = 0x601, 0x89F  # (where the patches are, in the overlay: 74901h, 74B9Fh)
    DONE, KEY_END, CLICK_END, ENTER = 0x721, 0xAEC, 0xAE5, 0x968  # 74A21h, 74DECh, 74DE5h, 74C68h
    STUBS = {"scan": (OV, 0xE2), "row": (OV, 0xB36), "pick": (OV, 0xBCD),
             "button": (DS + 0x2A1D - 0x4356, 0x71A), "window": (DS + 0x25EC - 0x4356, 0x618)}

    def setUp(self):
        import re
        from dscompanion.gamepatch import VEC_SAVE_CLICK, VEC_SAVE_PAGE
        image = load_image()
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, image)
        mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        # the two handlers: "push bp / mov bp,sp / sti / pushad / push es", then sp_done's value
        starts = {struct.unpack_from("<H", image, m.end() + 2)[0]: m.start()
                  for m in re.finditer(re.escape(bytes.fromhex("5589e5fb6660062ec706")), image)}
        mu.mem_write(VEC_SAVE_PAGE * 4, struct.pack("<HH", starts[0x74A21 - 0x74903], TSR))
        mu.mem_write(VEC_SAVE_CLICK * 4, struct.pack("<HH", starts[(0x74A21 - 0x74BA1) & 0xFFFF], TSR))
        mu.mem_write(self.OV * 16 + self.KEY_AT, bytes((0xCD, VEC_SAVE_PAGE, 0x90)))
        mu.mem_write(self.OV * 16 + self.CLICK_AT, bytes((0xCD, VEC_SAVE_CLICK, 0x90)))
        self.calls = {}
        for name, (seg, off) in self.STUBS.items():
            mu.mem_write(seg * 16 + off, b"\xcb")  # RETF
            mu.hook_add(UC_HOOK_CODE, lambda *_, n=name: self.calls.__setitem__(n, self.calls.get(n, 0) + 1),
                        begin=seg * 16 + off, end=seg * 16 + off)
        mu.mem_write(self.DS * 16 + 0x1DCF, b"SAVE??.SAV\0SAVE%.2d.SAV\0")
        mu.mem_write(self.SAVE * 16 + 0x4E4, struct.pack("<HIH", 3, 0x12345678, 0))  # row 3, saving

    def page(self):
        return bytes(self.mu.mem_read(self.DS * 16 + 0x1DCF + 3, 1)) + bytes(self.mu.mem_read(self.DS * 16 + 0x1DDA + 3, 1))

    def run_at(self, at, word, value):
        """The event routine (its BP+WORD holding VALUE) at the patch AT: where it goes on, and SI."""
        mu = self.mu
        self.calls.clear()
        mu.mem_write(SS * 16 + BP + word, struct.pack("<H", value))
        for name, v in dict(cs=self.OV, ds=self.DS, ss=SS, esp=0x800, ebp=BP, eflags=IF | 2, esi=0x4321,
                            edi=1, es=0x4444).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), v)
        ends = (self.DONE, self.KEY_END, self.CLICK_END, self.ENTER)
        mu.hook_add(UC_HOOK_CODE, lambda m, *_: m.emu_stop() if m.reg_read(r.UC_X86_REG_CS) == self.OV
                    and m.reg_read(r.UC_X86_REG_IP) in ends else None)
        mu.emu_start(self.OV * 16 + at, 0, count=20000)
        self.assertEqual([mu.reg_read(x) for x in (r.UC_X86_REG_SP, r.UC_X86_REG_DI, r.UC_X86_REG_ES)],
                         [0x800, 1, 0x4444])
        return mu.reg_read(r.UC_X86_REG_IP), mu.reg_read(r.UC_X86_REG_SI)

    def test_keys(self):
        self.assertEqual(self.run_at(self.KEY_AT, 0x12, 0x5100), (self.DONE, 0x4321))  # PgDn
        self.assertEqual(self.page(), b"BB")
        self.assertEqual(self.calls, {"scan": 1, "row": 10, "button": 2, "pick": 1, "window": 1})
        self.run_at(self.KEY_AT, 0x12, 0x5100)
        self.run_at(self.KEY_AT, 0x12, 0x5100)
        self.assertEqual(self.page(), b"DD")
        self.assertEqual(self.run_at(self.KEY_AT, 0x12, 0x5100), (self.KEY_END, 0x4321))  # (the last page)
        self.assertEqual((self.page(), self.calls), (b"DD", {}))
        self.assertEqual(self.run_at(self.KEY_AT, 0x12, 0x49E0), (self.DONE, 0x4321))  # PgUp, the grey key
        self.assertEqual(self.page(), b"CC")
        self.run_at(self.KEY_AT, 0x12, 0x4900)
        self.run_at(self.KEY_AT, 0x12, 0x4900)
        self.assertEqual(self.page(), b"EE")
        self.assertEqual(self.run_at(self.KEY_AT, 0x12, 0x4900), (self.KEY_END, 0x4321))  # (the first page)
        self.assertEqual(self.run_at(self.KEY_AT, 0x12, 0x1E61), (self.KEY_END, 0x4321))  # another key
        self.assertEqual((self.page(), self.calls), (b"EE", {}))

    def test_buttons(self):
        for button, page in ((0x818, b"DD"), (0x816, b"BB"), (0x817, b"CC"), (0x815, b"EE")):
            self.assertEqual(self.run_at(self.CLICK_AT, 8, button), (self.DONE, 0))  # (the routine returns 0)
            self.assertEqual(self.page(), page)
        self.assertEqual(self.run_at(self.CLICK_AT, 8, 0x815), (self.CLICK_END, 0x4321))  # (the page shown)
        self.assertEqual(self.run_at(self.CLICK_AT, 8, 0x819), (self.CLICK_END, 0x4321))  # another button
        self.assertEqual((self.page(), self.calls), (b"EE", {}))

    def test_loading_a_page_with_no_saves(self):
        self.mu.mem_write(self.SAVE * 16 + 0x4EA, struct.pack("<H", 1))  # the load window; no saves found
        self.assertEqual(self.run_at(self.KEY_AT, 0x12, 0x5100), (self.KEY_END, 0x4321))
        self.assertEqual(self.page(), b"EE")  # (back)
        self.assertEqual(self.calls, {"scan": 4})  # (pages 2, 3 and 4 looked at)
        # a button's page is shown even with none, its first row chosen (SAVE_LABEL greys LOAD)
        self.assertEqual(self.run_at(self.CLICK_AT, 8, 0x817), (self.DONE, 0))
        self.assertEqual(self.page(), b"CC")
        self.assertEqual(self.calls, {"scan": 1, "row": 10, "button": 2, "pick": 1, "window": 1})
        self.assertEqual(struct.unpack("<H", self.mu.mem_read(self.SAVE * 16 + 0x4E4, 2))[0], 0)

    def test_enter(self):
        """Enter (out of the window's key table) goes on to LOAD or SAVE, as the table took it, but
        not in the load window on a row with no save (the game would start a new game)."""
        mu = self.mu
        self.assertEqual(self.run_at(self.KEY_AT, 0x12, 0x1C0D), (self.ENTER, 0x4321))  # (saving)
        mu.mem_write(self.SAVE * 16 + 0x4EA, struct.pack("<H", 1))  # loading, row 3
        self.assertEqual(self.run_at(self.KEY_AT, 0x12, 0x1C0D), (self.KEY_END, 0x4321))  # (no save there)
        mu.mem_write(self.SAVE * 16 + 2 + 3 * 0x7D, b"SAVE04.SAV\0")
        self.assertEqual(self.run_at(self.KEY_AT, 0x12, 0x1C0D), (self.ENTER, 0x4321))
        self.assertEqual(self.calls, {})

    def test_loading_passes_a_page_with_no_saves(self):
        """PgDn in the load window: page 2 has none, page 3 a save in its third row."""
        mu = self.mu
        mu.mem_write(self.SAVE * 16 + 0x4EA, struct.pack("<H", 1))
        rows = self.SAVE * 16 + 2 + 2 * 0x7D
        scan = self.STUBS["scan"]
        # the folder search: a save in the third row when the page's letter is C
        mu.hook_add(UC_HOOK_CODE, lambda m, *_: m.mem_write(rows, b"x" if bytes(m.mem_read(self.DS * 16 + 0x1DD2, 1)) == b"C"
                                                             else b"\0"),
                    begin=scan[0] * 16 + scan[1], end=scan[0] * 16 + scan[1])
        self.assertEqual(self.run_at(self.KEY_AT, 0x12, 0x5100), (self.DONE, 0x4321))
        self.assertEqual(self.page(), b"CC")
        self.assertEqual(struct.unpack("<H", mu.mem_read(self.SAVE * 16 + 0x4E4, 2))[0], 2)  # (chosen: that row)


@unittest.skipIf(Uc is None, "unicorn not installed")
class LevelPickTests(unittest.TestCase):
    """PROBE_LV_PICK: at a level gained, a warrior short of weapon kinds has the psionicists' pop-up
    called (here a stand-in that counts its calls), if there is a kind it can pick (the stand-in
    weapons are bone: none for a fire cleric); the PROBE_PK_* probes in that pop-up, out of weapon
    mode, do just what they replaced."""
    SHEETS, TYPES_SEG = 0x8000, 0x9000
    RULES, RULES_HI = 170, 270
    STAND_IN, CALLS = 0x700, 0x7F0
    SPELL_STAND_IN, SPELL_CALLS = 0x720, 0x7F2
    PLAIN_TYPES = (81, 18, 17, 115, 20, 22, 2, 112, 3, 19, 44, 21, 48, 1, 64, 0)

    def setUp(self):
        import re
        from dscompanion.gamepatch import VEC_LV_PICK
        self.image = image = load_image()
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, image)
        at = image.find(bytes.fromhex("fb66600689e31e5636c57722"))
        self.assertGreater(at, 0)
        mu.mem_write(VEC_LV_PICK * 4, struct.pack("<HH", at, TSR))
        mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        mu.mem_write(GAME_DS * 16 + 0x1661, struct.pack("<HH", 0, self.SHEETS))
        mu.mem_write(GAME_DS * 16 + 0x1669, struct.pack("<HH", 0, self.TYPES_SEG))
        for t in self.PLAIN_TYPES:  # (every class may use them; melee, bone)
            rec = bytearray(game.ITEM_TYPE_SIZE)
            rec[0], rec[8] = 1, 1
            rec[0x10:0x12] = b"\xff\xff"
            mu.mem_write(self.TYPES_SEG * 16 + t * game.ITEM_TYPE_SIZE, bytes(rec))
        # the level-up routine: the INT, its NOPs and the JNZ; the far call to the pop-up 13h on
        mu.mem_write(CALLER * 16 + 0x600, bytes((0xCD, VEC_LV_PICK, 0x90, 0x90, 0x75, 0x07)))
        mu.mem_write(CALLER * 16 + 0x602 + 0x13, struct.pack("<HH", self.STAND_IN, CALLER))
        mu.mem_write(CALLER * 16 + self.STAND_IN, bytes.fromhex("2eff06f007cb"))  # inc word [cs:7F0h]; retf
        # CHOOSE A SPELL's far call ("push si; lcall"), past the JNZ: its stand-in counts at 7F2h
        mu.mem_write(CALLER * 16 + 0x606, bytes((0x56, 0x9A)) + struct.pack("<HH", self.SPELL_STAND_IN, CALLER))
        mu.mem_write(CALLER * 16 + self.SPELL_STAND_IN, bytes.fromhex("2eff06f207cb"))
        self.stops = []

        def stop(uc, address, size, _):
            uc.emu_stop()
            self.stops.append(address - CALLER * 16)
        mu.hook_add(UC_HOOK_CODE, stop, begin=CALLER * 16 + 0x606, end=CALLER * 16 + 0x606)
        mu.hook_add(UC_HOOK_CODE, stop, begin=CALLER * 16 + 0x60D, end=CALLER * 16 + 0x60D)

    def level_up(self, classes, levels, chosen=(), member=1, cls=None, rules=4096, race=2, kit=0):
        """(the pop-up's calls, where the routine went on) for a level gained in class CLS."""
        from dscompanion import kitpages
        mu = self.mu
        mu.mem_write(TSR * 16 + self.image.find(HDR_SIG) + self.RULES, struct.pack("<H", rules & 0xFFFF))
        mu.mem_write(TSR * 16 + self.image.find(HDR_SIG) + self.RULES_HI, struct.pack("<H", rules >> 16))
        mu.mem_write(CALLER * 16 + self.CALLS, bytes(4))
        sheet = bytearray(test_restrict.sheet(*classes, race=race))
        sheet[kitpages.KIT_BYTE] = kit
        sheet[0x24:0x24 + len(levels)] = bytes(levels)
        sheet[0x12:0x14] = b"\xff\x07"
        for i, k in enumerate(chosen):
            sheet[0x14 + i] = k + 1
        mu.mem_write(self.SHEETS * 16 + member * 0x47, bytes(sheet))
        mu.mem_write(SS * 16 + BP + 8, struct.pack("<H", classes[0] if cls is None else cls))
        self.stops.clear()
        for name, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x7FC, ebp=BP, eflags=IF | 2, esi=member,
                                es=0x6666).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(CALLER * 16 + 0x600, CALLER * 16 + 0x6FF, count=200000)
        self.assertEqual([mu.reg_read(getattr(r, "UC_X86_REG_" + x)) for x in ("SP", "SI", "ES", "DS")],
                         [0x7FC, member, 0x6666, GAME_DS])
        return struct.unpack("<H", mu.mem_read(CALLER * 16 + self.CALLS, 2))[0], self.stops[0]

    def test_asked_while_short(self):
        cases = [  # (classes, levels, kinds it has, asked)
            ((10,), (5,), (), True), ((10,), (5,), (0,), True), ((10,), (5,), (0, 1), False),
            ((10,), (6,), (0, 1), True), ((10,), (6,), (0, 1, 2), False), ((10,), (9,), (0, 1, 2), True),
            ((9,), (2,), (), True), ((9,), (2,), (3,), False), ((14,), (3,), (), True),
            ((9, 4), (4, 4), (), True), ((9, 3), (4, 4), (), False), ((11,), (5,), (), False), ((12,), (5,), (), False),
        ]
        for classes, levels, chosen, asked in cases:
            with self.subTest(classes=classes, levels=levels, chosen=chosen):
                self.assertEqual(self.level_up(classes, levels, chosen)[0], int(asked))

    def test_not_asked(self):
        self.assertEqual(self.level_up((10,), (5,), rules=0)[0], 0)
        self.assertEqual(self.level_up((10,), (5,), member=4)[0], 0)  # (not in the party)
        # a human fighter turned preserver: not until the preserver's level passes the fighter's
        self.assertEqual(self.level_up((11, 9), (3, 4), race=game.HUMAN)[0], 0)
        self.assertEqual(self.level_up((11, 9), (5, 4), race=game.HUMAN)[0], 1)

    def spell_calls(self):
        return struct.unpack("<H", self.mu.mem_read(CALLER * 16 + self.SPELL_CALLS, 2))[0]

    def test_shinobi_picks_a_spell(self):
        """A Shinobi gone up a thief level, from SHINOBI_FIRST, on to the preservers' CHOOSE A
        SPELL (past the JNZ); before that, or the kits off, or another thief, to the JNZ's target."""
        from dscompanion import kits
        for level, kit, rules, to in ((6, 3, game.RULE_KITS, 0x606), (10, 3, game.RULE_KITS, 0x606),
                                      (5, 3, game.RULE_KITS, 0x60D), (6, 1, game.RULE_KITS, 0x60D),
                                      (6, 3, 0, 0x60D)):
            with self.subTest(level=level, kit=kit, rules=rules):
                self.assertEqual(self.level_up((17,), (level,), cls=17, kit=kit, rules=rules), (0, to))
        self.assertEqual(self.level_up((17,), (8,), cls=17, kit=3, rules=game.RULE_KITS, member=4)[1], 0x60D)
        self.assertEqual(kits.SHINOBI_FIRST, 6)

    def test_scholar_picks_one_more(self):
        """A Scholar gone up a preserver level has CHOOSE A SPELL once from the probe (then the
        game's own, past the JNZ); another preserver, or the kits off, none from the probe."""
        for kit, rules, calls in ((1, game.RULE_KITS, 1), (2, game.RULE_KITS, 0), (0, game.RULE_KITS, 0),
                                  (1, 0, 0)):
            with self.subTest(kit=kit, rules=rules):
                self.assertEqual(self.level_up((11,), (5,), cls=11, kit=kit, rules=rules), (0, 0x606))
                self.assertEqual(self.spell_calls(), calls)

    def test_goes_on_as_the_compare(self):
        """A preserver's level on to its spell (past the JNZ), any other to the JNZ's target."""
        self.assertEqual(self.level_up((11,), (5,), cls=11)[1], 0x606)
        self.assertEqual(self.level_up((10,), (5,), cls=10)[1], 0x60D)
        self.assertEqual(self.level_up((10,), (5,), cls=10, rules=0)[1], 0x60D)

    def run_probe(self, pattern, vector, code, regs, stop):
        import re
        at = re.search(pattern, self.image, re.S).start()
        mu = self.mu
        mu.mem_write(vector * 4, struct.pack("<HH", at, TSR))
        self.code_at = getattr(self, "code_at", 0x800) + 0x20  # (each its own: the emulator keeps
        mu.mem_write(CALLER * 16 + self.code_at, bytes(code))    #  the code it has translated)
        values = dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x7FC, ebp=BP, eflags=IF | 2)
        values.update(regs)
        for name, value in values.items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(CALLER * 16 + self.code_at, CALLER * 16 + self.code_at + stop)

    def test_popup_probes_as_the_game(self):
        from dscompanion.gamepatch import VEC_PK_COUNT, VEC_PK_WIN, VEC_PK_LEFT, VEC_PK_TITLE, VEC_PK_FILL, VEC_PK_CLICK
        mu = self.mu
        mu.mem_write(GAME_DS * 16 + 0x4AEC, bytes((3,)))
        self.run_probe(rb"\xa0\xec\x4a\x2e\x80\x3e", VEC_PK_LEFT, (0xCD, VEC_PK_LEFT, 0x90), dict(eax=0x1200), 3)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_AX), 0x1203)
        for ax, zero in ((0, True), (5, False)):
            self.run_probe(rb"\x89\xc2\x2e\x80\x3e..\x00\x74\x03\xba\x02\x00", VEC_PK_COUNT, (0xCD, VEC_PK_COUNT, 0x90, 0x90), dict(eax=ax, edx=0x99), 4)
            self.assertEqual(mu.reg_read(r.UC_X86_REG_DX), ax)
            self.assertEqual(bool(mu.reg_read(r.UC_X86_REG_EFLAGS) & 0x40), zero)
        self.run_probe(rb"\x83\xec\x02\x55\x89\xe5\x50.{18}\xc7\x46\x08\x5d\x44", VEC_PK_WIN, (0xCD, VEC_PK_WIN, 0x90), {}, 3)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_SP), 0x7FA)
        self.assertEqual(struct.unpack("<H", mu.mem_read(SS * 16 + 0x7FA, 2))[0], 0x445D)
        self.run_probe(rb"\x83\xec\x04\x55\x89\xe5\x50.{18}\x8c\x5e\x0a", VEC_PK_TITLE, bytes((0xCD, VEC_PK_TITLE, 0x90, 0x90)) + bytes(16), {}, 4)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_SP), 0x7F8)
        self.assertEqual(struct.unpack("<HH", mu.mem_read(SS * 16 + 0x7F8, 4)), (0x3026, GAME_DS))
        after = CALLER * 16 + self.code_at + 2  # (the line's colours, in the pushes after it: the game's)
        self.assertEqual((mu.mem_read(after + 6, 1)[0], mu.mem_read(after + 0xC, 1)[0]), (0xD0, 0xD3))
        self.run_probe(rb"\x31\xff\x89\xfe\x2e\x80\x3e", VEC_PK_FILL, (0xCD, VEC_PK_FILL, 0x90, 0x90), dict(esi=5, edi=6), 4)
        self.assertEqual((mu.reg_read(r.UC_X86_REG_SI), mu.reg_read(r.UC_X86_REG_DI)), (0, 0))
        mu.mem_write(SS * 16 + BP + 8, struct.pack("<H", 0x2C38))
        self.run_probe(rb"\x55\x89\xe5\x53\x8b\x5e\x00\x36\x8b\x47\x08", VEC_PK_CLICK, (0xCD, VEC_PK_CLICK, 0x90), {}, 3)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_AX), 0x2C38)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_SP), 0x7FC)

    def test_hit_die_best_of_two(self):
        """PROBE_HP_BEST: with the rule, the first roll sends the game back to roll again (872FDh,
        1Eh before the INT's return); the second gives CX the better of the two. Without, CX the
        roll, as the "mov cx,ax" it replaced."""
        import re
        from dscompanion.gamepatch import VEC_HP_BEST
        mu = self.mu
        at = re.search(rb"\x2e\xf7\x06..\x00\x80\x74", self.image, re.S).start()
        mu.mem_write(VEC_HP_BEST * 4, struct.pack("<HH", at, TSR))
        int_at = 0xA00 + 0x8731B - 0x872FD - 2  # (the INT, so that going back lands on 0xA00)
        mu.mem_write(CALLER * 16 + int_at, bytes((0xCD, VEC_HP_BEST)))

        def roll(ax):
            for name, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x7FC, ebp=BP, eflags=IF | 2, eax=ax,
                                    ecx=0x3333).items():
                mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
            mu.emu_start(CALLER * 16 + int_at, 0, count=40)
            return mu.reg_read(r.UC_X86_REG_IP), mu.reg_read(r.UC_X86_REG_CX), mu.reg_read(r.UC_X86_REG_SP)
        for rules, first, second in ((32768, 3, 8), (32768, 9, 2), (32768, 5, 5)):
            with self.subTest(first=first, second=second):
                mu.mem_write(TSR * 16 + self.image.find(HDR_SIG) + self.RULES, struct.pack("<H", rules))
                mu.mem_write(CALLER * 16 + 0xA00, bytes((0xF4,)))  # (hlt: back at the roll)
                mu.mem_write(CALLER * 16 + int_at + 2, bytes((0xF4,)))
                self.assertEqual(roll(first)[:3:2], (0xA01, 0x7FC))  # back to roll again (past the hlt)
                self.assertEqual(roll(second), (int_at + 3, max(first, second), 0x7FC))
        mu.mem_write(TSR * 16 + self.image.find(HDR_SIG) + self.RULES, struct.pack("<H", 0))
        self.assertEqual(roll(4)[:2], (int_at + 3, 4))

    def test_effects_rows_pops(self):
        """PROBE_EF_ROWS does the "pop di / pop si" it replaced (nothing drawn: the rule off, or
        the lower panel in use, past 21 cells)."""
        from dscompanion.gamepatch import VEC_EF_ROWS
        mu = self.mu
        for rules, cells in ((0, 3), (4096, 30)):
            with self.subTest(rules=rules, cells=cells):
                mu.mem_write(TSR * 16 + self.image.find(HDR_SIG) + self.RULES, struct.pack("<H", rules))
                mu.mem_write(SS * 16 + BP - 4, struct.pack("<H", cells))
                mu.mem_write(SS * 16 + 0x7F8, struct.pack("<HH", 0x1111, 0x2222))  # (DI's, then SI's)
                self.run_probe(rb"\xfb\x66\x60\x06\xe8..\x74.\x83\x7e\xfc\x15", VEC_EF_ROWS,
                               (0xCD, VEC_EF_ROWS), dict(esp=0x7F8, esi=5, edi=6), 2)
                self.assertEqual([mu.reg_read(getattr(r, "UC_X86_REG_" + x)) for x in ("DI", "SI", "SP", "BP")],
                                 [0x1111, 0x2222, 0x7FC, BP])


@unittest.skipIf(Uc is None, "unicorn is not installed")
class TomeTests(unittest.TestCase):
    """PROBE_TOME (the Tome of Understanding, tome.py), where the game would show its message
    for a scroll it has no use for: the tome raises its reader's WIS and goes on to the game's
    using the scroll up (8B7E2h, 2Ch before the INT's way back); at 25 already, the message only
    (8B810h, past the NOPs); any other scroll, the game's own "push ds / push 3440h"."""
    SHEETS, CREATURES, WHO = 0x8000, 0x8800, 0x9000
    INT_AT = 0x600

    def setUp(self):
        from dscompanion.gamepatch import VEC_TOME
        from dscompanion import tome
        self.assertEqual(tome.TOME_SPELL, 0xB0)
        image = load_image()
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, image)
        at = image.find(bytes.fromhex("807efdb074"))  # cmp byte [bp-3], TOME_SPELL / je
        self.assertGreater(at, 0)
        mu.mem_write(VEC_TOME * 4, struct.pack("<HH", at, TSR))
        mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        mu.mem_write(GAME_DS * 16 + 0x1661, struct.pack("<HH", 0, self.SHEETS))
        mu.mem_write(GAME_DS * 16 + 0x1665, struct.pack("<HH", 0, self.CREATURES))
        back = self.INT_AT + 2
        mu.mem_write(CALLER * 16 + self.INT_AT, bytes((0xCD, VEC_TOME, 0x90, 0x90, 0xF4)))  # (8B810h: hlt)
        mu.mem_write(CALLER * 16 + back - 0x2C, b"\xf4\xb8" + struct.pack("<H", self.WHO))  # 8B7E2h: hlt; the "mov ax"
        mu.mem_write(self.WHO * 16 + 0x25B, struct.pack("<H", 1))  # the reader: party member 1
        mu.mem_write(self.CREATURES * 16 + 0x3A + 0x28, b"Cilla\0")

    def read(self, spell, wis):
        mu = self.mu
        mu.mem_write(self.SHEETS * 16 + 0x47 + 0x1F, bytes((wis,)))
        mu.mem_write(self.CREATURES * 16 + 0x3A + 0x26, bytes((wis,)))
        mu.mem_write(SS * 16 + BP - 3, bytes((spell,)))
        mu.mem_write(SS * 16 + BP - 0x54, bytes(0x50))
        for name, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800, ebp=BP, eflags=IF | 2, eax=0x1111,
                                esi=0x2222).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(CALLER * 16 + self.INT_AT, 0, count=400)
        text = bytes(mu.mem_read(SS * 16 + BP - 0x54, 0x50)).split(b"\0")[0]
        regs = {x: mu.reg_read(getattr(r, "UC_X86_REG_" + x.upper())) for x in ("ip", "sp", "ax", "si", "bp")}
        return regs, text, mu.mem_read(self.SHEETS * 16 + 0x47 + 0x1F, 1)[0], mu.mem_read(self.CREATURES * 16 + 0x3A + 0x26, 1)[0]

    def test_read(self):
        regs, text, sheet, creature = self.read(0xB0, 18)
        self.assertEqual((regs["ip"], regs["sp"], regs["ax"], regs["si"], regs["bp"]),
                         (self.INT_AT + 2 - 0x2C + 1, 0x800, 0x1111, 0x2222, BP))  # (past the hlt)
        self.assertEqual((text, sheet, creature), (b"Cilla reads the tome: WIS 19.", 19, 19))
        self.assertEqual(self.read(0xB0, 8)[1], b"Cilla reads the tome: WIS 9.")

    def test_wise_enough(self):
        regs, text, sheet, creature = self.read(0xB0, 25)
        self.assertEqual((regs["ip"], regs["sp"], regs["ax"]), (self.INT_AT + 5, 0x7FC, 0x1111))
        self.assertEqual(struct.unpack("<HH", self.mu.mem_read(SS * 16 + 0x7FC, 4)), (BP - 0x54, SS))
        self.assertEqual((text, sheet, creature), (b"Cilla can grow no wiser.", 25, 25))

    def test_other_scrolls(self):
        regs, text, sheet, _ = self.read(0xAD, 18)
        self.assertEqual((regs["ip"], regs["sp"], regs["ax"]), (self.INT_AT + 5, 0x7FC, 0x1111))
        self.assertEqual(struct.unpack("<HH", self.mu.mem_read(SS * 16 + 0x7FC, 4)), (0x3440, GAME_DS))
        self.assertEqual((text, sheet), (b"", 18))


@unittest.skipIf(Uc is None, "unicorn is not installed")
class KitTests(unittest.TestCase):
    """The kits' routines against kitpages.py: WP_IDS (the panel's windows for the classes being
    made, the rules on or off) as panel_windows, and KIT_OF_SHEET (the Effects screen's line) as
    kit_name."""
    DS = 0x9000  # (the game's DS: its things table 9E4h paragraphs below, its spells' 6A2h, clear of DSCLOG's image)
    RULES, RULES_HI = 170, 270
    CREATION, SHEET = 0x8000, 0x8100

    def setUp(self):
        self.image = load_image()
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        mu.mem_write(TSR * 16 + 0xFFF0, bytes((0xF4,)))
        mu.mem_write(self.DS * 16 + 0x119C, struct.pack("<HH", 0, self.CREATION))
        self.hdr = TSR * 16 + self.image.find(HDR_SIG)

    def rules(self, rules):
        self.mu.mem_write(self.hdr + self.RULES, struct.pack("<H", rules & 0xFFFF))
        self.mu.mem_write(self.hdr + self.RULES_HI, struct.pack("<H", rules >> 16))

    def call(self, pattern, **regs):
        import re
        at = re.search(pattern, self.image, re.S).start()
        mu = self.mu
        mu.mem_write(SS * 16 + 0x7FC, struct.pack("<H", 0xFFF0))
        for name, value in dict(cs=TSR, ds=self.DS, ss=SS, esp=0x7FC, **regs).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(TSR * 16 + at, TSR * 16 + 0xFFF0)

    def test_panel_windows(self):
        from dscompanion import kitpages
        combos = [(c, 0, 0) for c in range(1, 9)] + [(3, 6, 0), (3, 8, 0), (7, 1, 0), (1, 5, 0), (5, 8, 0),
                                                     (3, 5, 8), (4, 2, 0), (6, 8, 0)]
        for rules in (0, game.RULE_SPECIALIZE, game.RULE_KITS, game.RULE_SPECIALIZE | game.RULE_KITS):
            self.rules(rules)
            for classes in combos:
                with self.subTest(rules=rules, classes=classes):
                    sheet = bytearray(game.SHEET_SIZE)
                    sheet[0x21:0x24] = bytes(classes)
                    self.mu.mem_write(self.CREATION * 16, bytes(sheet))
                    self.call(rb"\x53\x51\xe8..\x89\xc1\xe8..\x88\xc3\xb8\xc4\x0b")
                    got = (self.mu.reg_read(r.UC_X86_REG_AX), self.mu.reg_read(r.UC_X86_REG_DX))
                    self.assertEqual(got, kitpages.panel_windows(classes, rules))
        self.assertEqual(kitpages.panel_windows((8, 0, 0), game.RULE_KITS), (kitpages.KIT_DISCIPLINES,
                                                                              kitpages.KIT_SPHERES))

    def test_effects_line(self):
        """KIT_OF_SHEET: the Effects screen's line for kit AL ("KIT: RAVAGER")."""
        from dscompanion import kitpages
        for name, kid in kitpages.KIT_IDS.items():
            with self.subTest(name=name):
                self.call(rb"\x50\x51\x57\xbe..\x2e\x80\x3c\x00", eax=kid)
                si = self.mu.reg_read(r.UC_X86_REG_SI)
                text = bytes(self.mu.mem_read(TSR * 16 + si, 24)).split(b"\0")[0].decode()
                self.assertEqual(text, "KIT: " + kitpages.row_text(name))

    CREATURES, ITEMS, TYPES = 0x8200, 0x8300, 0x8400

    def test_two_kits_ac(self):
        """KIT_AC for a human with a kit for each of two classes, both awake: a Ravager fighter 3 who
        became a Wanderer druid, now 4: both kits' (kits.ac), added."""
        from dscompanion import kits, kitpages
        self.rules(game.RULE_KITS)
        for druid, both in ((4, True), (2, False)):
            with self.subTest(druid=druid):
                self.creature(5, 0)
                sheet = bytearray(self.mu.mem_read(self.SHEET * 16 + 5 * 0x47, game.SHEET_SIZE))
                sheet[0x18], sheet[0x21:0x23], sheet[0x24:0x26], sheet[kitpages.KIT_BYTE] = 1, bytes((5, 9)), bytes((druid, 3)), 0b1111
                self.mu.mem_write(self.SHEET * 16 + 5 * 0x47, bytes(sheet))
                self.assertEqual(kitpages.kit_ids(bytes(sheet)), [kits.RAVAGER, kits.WANDERER] if both else [kits.WANDERER])
                want = 10 + kits.ac(kits.WANDERER, False) + (kits.ac(kits.RAVAGER, False, 3, 10) if both else 0)
                self.assertEqual(self.kit_ac(), want)

    def test_grove_warden_ac(self):
        """KIT_AC for a Grove Warden: 1 better for every 3 druid levels (kits.ac)."""
        from dscompanion import kits
        self.rules(game.RULE_KITS)
        for level in range(1, 11):
            with self.subTest(level=level):
                self.creature(5, 1, level=level)
                self.assertEqual(self.kit_ac(), 10 + kits.ac(kits.GROVE_WARDEN, False, level))

    def test_ravager_ac(self):
        """KIT_AC for a Ravager: its table by level where better than the sheet's base AC (+27h),
        the armour's improvement kept (kits.ac)."""
        from dscompanion import kits
        self.rules(game.RULE_KITS)
        for level in (1, 2, 3, 8, 9, 12, 17, 18, 20):
            for base in (10, 5, 0):
                with self.subTest(level=level, base=base):
                    self.creature(9, 3, level=level, base=base)
                    self.assertEqual(self.kit_ac(), 10 + kits.ac(kits.RAVAGER, False, level, base))
        self.creature(9, 3, level=1, base=10)
        self.assertEqual(self.kit_ac(), 7)

    def test_shield_ac(self):
        """KIT_AC with a shield in a hand and without: a Sentinel's 2, an Arena Champion's 1;
        a Wanderer's 1 worse, shield or not."""
        from dscompanion import kits, kitpages
        self.rules(game.RULE_KITS)
        for cls, kit in ((9, 2), (10, 1), (5, 3), (10, 2), (9, 0)):
            for shield in (True, False):
                with self.subTest(cls=cls, kit=kit, shield=shield):
                    self.creature(cls, kit, shield=shield)
                    sheet = bytearray(game.SHEET_SIZE)
                    sheet[0x21], sheet[kitpages.KIT_BYTE] = cls, kit
                    self.assertEqual(self.kit_ac(), 10 + kits.ac(first_kit(bytes(sheet)), shield))

    def kit_ac(self):
        """KIT_AC for thing 7, the game's AC 10: the AC."""
        self.mu.mem_write(SS * 16 + BP + 6, struct.pack("<H", 7))
        self.call(rb"\x2e\xf7\x06..\x01\x00(?:\x74.|\x0f\x84..)\x53\x51\x52\x06\x89\xc1", eax=10, ebp=BP)
        return struct.unpack("<h", struct.pack("<H", self.mu.reg_read(r.UC_X86_REG_AX)))[0]

    def creature(self, cls, kit, index=5, level=1, base=10, shield=False):
        """Creature INDEX (its sheet the same number) of class CLS with kit KIT, its base AC BASE,
        a shield in its left hand or not (SHIELD); the things table's thing 7 is it, thing 8 the
        shield's item list."""
        from dscompanion import kitpages
        mu = self.mu
        mu.mem_write(self.DS * 16 + 0x1665, struct.pack("<HH", 0, self.CREATURES))
        mu.mem_write(self.DS * 16 + 0x1661, struct.pack("<HH", 0, self.SHEET))
        rec = bytearray(0x3A)
        rec[4:6] = struct.pack("<H", index)
        struct.pack_into("<HHH", rec, 8, 8 if shield else 0x270F, 0x270F, 0x270F)
        mu.mem_write(self.CREATURES * 16 + index * 0x3A, bytes(rec))
        mu.mem_write(self.DS * 16 + 0x165D, struct.pack("<HH", 0, self.ITEMS))
        mu.mem_write(self.DS * 16 + 0x1669, struct.pack("<HH", 0, self.TYPES))
        item = bytearray(0x15)
        struct.pack_into("<H", item, 4, 0x270F)
        struct.pack_into("<H", item, 0x0A, 4)
        item[0x11] = 10  # (a shield, type 4, in the left hand)
        mu.mem_write(self.ITEMS * 16 + 3 * 0x15, bytes(item))
        mu.mem_write(self.TYPES * 16 + 4 * 0x14, bytes((4,)) + bytes(14) + bytes((0x80,)))
        sheet = bytearray(game.SHEET_SIZE)
        sheet[0x21], sheet[0x24], sheet[kitpages.KIT_BYTE] = cls, level, kit
        sheet[0x27] = base & 0xFF
        mu.mem_write(self.SHEET * 16 + index * 0x47, bytes(sheet))
        things = ((self.DS + 0x3972 - 0x4356) & 0xFFFF) * 16 + 0xC36
        mu.mem_write(things + 7 * 3, struct.pack("<Bh", 2, index))
        mu.mem_write(things + 8 * 3, struct.pack("<Bh", 1, 3))

    def test_ac_and_move(self):
        """KIT_AC and KIT_MOVE as kits.ac (without a shield) and kits.move."""
        from dscompanion import kits, kitpages
        for rules in (game.RULE_KITS, 0):
            self.rules(rules)
            for cls, kit in ((9, 3), (9, 2), (9, 1), (13, 1), (17, 1), (9, 0)):
                with self.subTest(rules=rules, cls=cls, kit=kit):
                    self.creature(cls, kit)
                    sheet = bytearray(game.SHEET_SIZE)
                    sheet[0x21], sheet[kitpages.KIT_BYTE] = cls, kit
                    kid = first_kit(bytes(sheet)) if rules else 0
                    self.mu.mem_write(SS * 16 + BP + 6, struct.pack("<H", 7))
                    self.assertEqual(self.kit_ac(), 10 + kits.ac(kid, False, 1))
                    self.call(rb"\x50\x89\xf0\xe8..\x1d", eax=120, esi=5)
                    self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), 120 + 10 * kits.move(kid))

    def test_saves(self):
        """KIT_SAVE (thing 7 saving) as kits.save, for spells, psionic powers, monsters' attacks
        and the charms."""
        from dscompanion import kits, kitpages
        self.rules(game.RULE_KITS)
        spells = (self.DS - (0x4356 - 0x3CB4)) * 16 + 0x40  # (the spell records, 20h each)
        kinds = {13: kits.FIRE, 40: kits.COLD, 61: kits.FIRE | 1, 137: 0x08, 177: kits.COLD}
        for spell, k in kinds.items():
            self.mu.mem_write(spells + spell * 0x20 + 0x1A, bytes((k,)))
        for cls, kit in ((9, 1), (9, 2), (9, 3), (13, 1), (5, 3), (9, 0)):
            self.creature(cls, kit)
            sheet = bytearray(game.SHEET_SIZE)
            sheet[0x21], sheet[kitpages.KIT_BYTE] = cls, kit
            kid = first_kit(bytes(sheet))
            for spell in (0, 2, 13, 40, 61, 82, 137, 138, 158, 159, 177, 300):
                with self.subTest(cls=cls, kit=kit, spell=spell):
                    self.call(rb"\x50\x53\x51\x06\x89\xc1\x8c\xd8", eax=spell, esi=3, edi=7)
                    want = 3 + kits.save(kid, spell, kinds.get(spell, 0))
                    self.assertEqual(self.mu.reg_read(r.UC_X86_REG_SI), want & 0xFFFF)
        self.assertEqual(kits.save(kits.WANDERER, 13, kits.FIRE), 3)
        self.assertEqual((kits.save(kits.SENTINEL, 13), kits.save(kits.SENTINEL, 158), kits.save(kits.MYRMIDON, 2),
                          kits.save(kits.MYRMIDON, 13)), (-1, 0, -4, 0))

    def test_initiative(self):
        """PROBE_INIT: the game's 20 added, and kits.initiative (a Sentinel's 2)."""
        from dscompanion import kits, kitpages
        from dscompanion.gamepatch import VEC_INIT
        at = self.image.find(bytes.fromhex("83c214"))
        self.assertGreater(at, 0)
        self.mu.mem_write(VEC_INIT * 4, struct.pack("<HH", at, TSR))
        self.mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        self.mu.mem_write(CALLER * 16 + 0x600, bytes((0xCD, VEC_INIT, 0x90)))
        self.rules(game.RULE_KITS)
        for cls, kit in ((9, 2), (9, 3), (17, 2), (9, 0)):
            with self.subTest(cls=cls, kit=kit):
                self.creature(cls, kit)
                sheet = bytearray(game.SHEET_SIZE)
                sheet[0x21], sheet[kitpages.KIT_BYTE] = cls, kit
                for name, value in dict(cs=CALLER, ds=self.DS, ss=SS, esp=0x7FC, eflags=IF | 2, edx=5, esi=5,
                                        eax=0x1111).items():
                    self.mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
                self.mu.emu_start(CALLER * 16 + 0x600, CALLER * 16 + 0x603)
                self.assertEqual(self.mu.reg_read(r.UC_X86_REG_DX), 25 + kits.initiative(first_kit(bytes(sheet))))
                self.assertEqual((self.mu.reg_read(r.UC_X86_REG_AX), self.mu.reg_read(r.UC_X86_REG_SP)), (0x1111, 0x7FC))

    def test_thac0(self):
        """PROBE_THAC0: 20 less SI, and kits.thac0 (a warrior's for the Swashbuckler, Crusader,
        Battle Mage and Mind Warrior where better; the Scholar's 1 worse); kits off, the game's."""
        from dscompanion import kits, kitpages
        from dscompanion.gamepatch import VEC_THAC0, PATCHES
        self.assertIn(("thac0", 0x876BB), [(p.name, p.offset) for p in PATCHES])
        at = self.image.find(bytes.fromhex("535106b9140029f1"))
        self.assertGreater(at, 0)
        self.mu.mem_write(VEC_THAC0 * 4, struct.pack("<HH", at, TSR))
        self.mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        self.mu.mem_write(CALLER * 16 + 0x600, bytes((0xCD, VEC_THAC0, 0x90, 0x90, 0x90)))
        cases = [(17, 1, 1), (17, 1, 9), (17, 2, 5), (17, 3, 5), (1, 3, 4), (1, 1, 4), (11, 2, 6), (11, 1, 6),
                 (11, 3, 6), (12, 2, 7), (12, 1, 7), (9, 1, 5), (17, 0, 5), (2, 3, 20)]
        for rules in (game.RULE_KITS, 0):
            self.rules(rules)
            for cls, kit, level in cases:
                with self.subTest(rules=rules, cls=cls, kit=kit, level=level):
                    self.creature(cls, kit, level=level)
                    sheet = bytearray(game.SHEET_SIZE)
                    sheet[0x21], sheet[0x24], sheet[kitpages.KIT_BYTE] = cls, level, kit
                    kid = first_kit(bytes(sheet)) if rules else 0
                    own = 20 - level // 2  # (as a thief's: SI the most taken off 20)
                    self.mu.mem_write(SS * 16 + BP + 6, struct.pack("<H", 5))
                    for name, value in dict(cs=CALLER, ds=self.DS, ss=SS, esp=0x7FC, ebp=BP, eflags=IF | 2,
                                            esi=20 - own, ebx=0x2222, ecx=0x3333, es=0x6666).items():
                        self.mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
                    self.mu.emu_start(CALLER * 16 + 0x600, CALLER * 16 + 0x605)
                    self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), kits.thac0(kid, level, own))
                    self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_BX, r.UC_X86_REG_CX, r.UC_X86_REG_ES,
                                                                    r.UC_X86_REG_SP)], [0x2222, 0x3333, 0x6666, 0x7FC])
        # A human Mind Warrior (psionicist 6) who became a thief: the kit asleep (the game's THAC0)
        # until the thief level passes 6, then a warrior's by its psionicist level (21 - 6 = 15)
        self.rules(game.RULE_KITS)
        for thief, want in ((4, 18), (6, 18), (7, 15)):
            with self.subTest(thief=thief):
                sheet = bytearray(game.SHEET_SIZE)
                sheet[0x18], sheet[0x21:0x23], sheet[0x24:0x26], sheet[kitpages.KIT_BYTE] = 1, bytes((17, 12)), bytes((thief, 6)), 2
                self.mu.mem_write(self.SHEET * 16 + 5 * game.SHEET_SIZE, bytes(sheet))
                self.assertEqual(first_kit(bytes(sheet)), kits.MIND_WARRIOR if thief > 6 else 0)
                self.assertEqual(any_kit(bytes(sheet)), kits.MIND_WARRIOR)
                self.mu.mem_write(SS * 16 + BP + 6, struct.pack("<H", 5))
                for name, value in dict(cs=CALLER, ds=self.DS, ss=SS, esp=0x7FC, ebp=BP, eflags=IF | 2,
                                        esi=2, ebx=0x2222, ecx=0x3333, es=0x6666).items():
                    self.mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
                self.mu.emu_start(CALLER * 16 + 0x600, CALLER * 16 + 0x605)
                self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), want)
        self.assertEqual([kits.thac0(kits.SWASHBUCKLER, 9, 16), kits.thac0(kits.SCHOLAR, 9, 18),
                          kits.thac0(kits.CRUSADER, 25, 4), kits.thac0(0, 9, 16)], [12, 19, 1, 16])

    KIT_CASES = ((11, 3), (11, 2), (11, 1), (1, 3), (1, 1), (13, 3), (13, 2), (13, 1), (17, 1), (9, 0))

    def kit_of(self, cls, kit, rules=game.RULE_KITS):
        from dscompanion import kitpages
        sheet = bytearray(game.SHEET_SIZE)
        sheet[0x21], sheet[kitpages.KIT_BYTE] = cls, kit
        return first_kit(bytes(sheet)) if rules & game.RULE_KITS else 0

    def test_slots(self):
        """PROBE_SLOTS: the slots the game's routine gives ([BP-2]), with kits.slots."""
        from dscompanion import kits
        from dscompanion.gamepatch import VEC_SLOTS
        at = self.image.find(bytes.fromhex("5351068b4efe"))
        self.assertGreater(at, 0)
        self.mu.mem_write(VEC_SLOTS * 4, struct.pack("<HH", at, TSR))
        self.mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        self.mu.mem_write(CALLER * 16 + 0x600, bytes((0xCD, VEC_SLOTS, 0x90)))
        for rules in (game.RULE_KITS, 0):
            self.rules(rules)
            for cls, kit in self.KIT_CASES + ((17, 3),):
                kid = self.kit_of(cls, kit, rules)
                for level in (1, 5, 6, 7, 8, 9, 10, 12):
                    self.creature(cls, kit, level=level)
                    for magic in (kits.WIZARD, kits.PRIEST):
                        for spell_level in (1, 2, 3, 4):
                            for given in (0, 1, 3):
                                with self.subTest(rules=rules, cls=cls, kit=kit, level=level, magic=magic,
                                                  spell_level=spell_level, given=given):
                                    self.mu.mem_write(SS * 16 + BP - 2, struct.pack("<H", given))
                                    self.mu.mem_write(SS * 16 + BP + 6, struct.pack("<HHH", 7, magic, spell_level))
                                    for name, value in dict(cs=CALLER, ds=self.DS, ss=SS, esp=0x7FC, ebp=BP,
                                                            eflags=IF | 2, ebx=0x2222, ecx=0x3333, edx=0x4444,
                                                            es=0x6666).items():
                                        self.mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
                                    self.mu.emu_start(CALLER * 16 + 0x600, CALLER * 16 + 0x603)
                                    self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX),
                                                     kits.slots(kid, magic, level, spell_level, given))
                                    self.assertEqual([self.mu.reg_read(x) for x in (
                                        r.UC_X86_REG_BX, r.UC_X86_REG_CX, r.UC_X86_REG_DX, r.UC_X86_REG_ES,
                                        r.UC_X86_REG_SP)], [0x2222, 0x3333, 0x4444, 0x6666, 0x7FC])
        self.assertEqual([kits.slots(kits.SEEKER, kits.PRIEST, lv, sl, 9) for lv in (5, 6, 8, 10, 15) for sl in (1, 3)],
                         [0, 0, 1, 0, 2, 0, 2, 1, 2, 1])
        self.assertEqual([kits.slots(kits.ARCANIST, kits.WIZARD, 5, 1, n) for n in (0, 2)], [0, 3])

    def test_slot_level(self):
        """PROBE_SLOT_LEVEL: the class level the slot rules are given (ES:BX the sheet + DI), an
        Elementalist's 1 less (kits.slot_level); AH kept."""
        from dscompanion import kits
        from dscompanion.gamepatch import VEC_SLOT_LEVEL
        at = self.image.find(bytes.fromhex("53515288e589fa29fb"))
        self.assertGreater(at, 0)
        self.mu.mem_write(VEC_SLOT_LEVEL * 4, struct.pack("<HH", at, TSR))
        self.mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        self.mu.mem_write(CALLER * 16 + 0x600, bytes((0xCD, VEC_SLOT_LEVEL, 0x90, 0x90)))
        for rules in (game.RULE_KITS, 0):
            self.rules(rules)
            for cls, kit in self.KIT_CASES + ((1, 2),):
                for level in (0, 1, 7):
                    with self.subTest(rules=rules, cls=cls, kit=kit, level=level):
                        sheet = bytearray(game.SHEET_SIZE)
                        sheet[0x21], sheet[0x24], sheet[0x43] = cls, level, kit
                        self.mu.mem_write(self.SHEET * 16, bytes(sheet))
                        for name, value in dict(cs=CALLER, ds=self.DS, ss=SS, esp=0x7FC, eflags=IF | 2,
                                                eax=0x5500, ebx=0, edi=0, es=self.SHEET, ecx=0x3333).items():
                            self.mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
                        self.mu.emu_start(CALLER * 16 + 0x600, CALLER * 16 + 0x604)
                        kid = self.kit_of(cls, kit, rules)
                        self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), 0x5500 | kits.slot_level(kid, level))
                        self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_BX, r.UC_X86_REG_CX,
                                                                        r.UC_X86_REG_SP)], [0, 0x3333, 0x7FC])
        # A human Elementalist who became a fighter: its cleric slots (the class at place 1) a level
        # behind once the fighter level passes the cleric's; the fighter's place as it is
        from dscompanion import kitpages
        self.rules(game.RULE_KITS)
        for fighter, place in ((3, 1), (5, 1), (5, 0)):
            with self.subTest(fighter=fighter, place=place):
                sheet = bytearray(game.SHEET_SIZE)
                sheet[0x18], sheet[0x21:0x23], sheet[0x24:0x26], sheet[0x43] = 1, bytes((9, 1)), bytes((fighter, 4)), 1
                self.mu.mem_write(self.SHEET * 16, bytes(sheet))
                for name, value in dict(cs=CALLER, ds=self.DS, ss=SS, esp=0x7FC, eflags=IF | 2, eax=0x5500,
                                        ebx=place, edi=place, es=self.SHEET, ecx=0x3333, edx=0x4444).items():
                    self.mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
                self.mu.emu_start(CALLER * 16 + 0x600, CALLER * 16 + 0x604)
                level = sheet[0x24 + place]
                behind = bool(kitpages.kit_at(sheet, place)) and kitpages.kit_awake(sheet, place)
                self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), 0x5500 | (level - 1 if behind else level))
                self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_BX, r.UC_X86_REG_CX, r.UC_X86_REG_DX,
                                                                r.UC_X86_REG_DI)], [place, 0x3333, 0x4444, place])
        # a second class's level (DI 1): the sheet's own kit, none for more than one class
        sheet = bytearray(game.SHEET_SIZE)
        sheet[0x21], sheet[0x22], sheet[0x25], sheet[0x43] = 1, 5, 7, 1
        self.mu.mem_write(self.SHEET * 16, bytes(sheet))
        self.rules(game.RULE_KITS)
        for name, value in dict(cs=CALLER, ds=self.DS, ss=SS, esp=0x7FC, eflags=IF | 2, eax=0, ebx=1, edi=1,
                                es=self.SHEET).items():
            self.mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        self.mu.emu_start(CALLER * 16 + 0x600, CALLER * 16 + 0x604)
        self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), 7)

    PSP_CASES = ((12, 1), (12, 3), (12, 2), (12, 0), (11, 1))

    def run_int(self, vector, handler_hex, code_len, **regs):
        """INT VECTOR (its handler found by HANDLER_HEX) and the NOPs after it, CODE_LEN in all, run
        from a call site of its own (the emulator keeps code it has seen)."""
        at = self.image.find(bytes.fromhex(handler_hex))
        self.assertGreater(at, 0)
        self.mu.mem_write(vector * 4, struct.pack("<HH", at, TSR))
        if not getattr(self, "hooked", False):
            self.mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
            self.hooked = True
        site = 0x400 + (vector & 0x1F) * 0x10
        self.mu.mem_write(CALLER * 16 + site, bytes((0xCD, vector)) + b"\x90" * (code_len - 2))
        for name, value in dict(cs=CALLER, ds=self.DS, ss=SS, esp=0x7FC, ebp=BP, eflags=IF | 2, **regs).items():
            self.mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        self.mu.emu_start(CALLER * 16 + site, CALLER * 16 + site + code_len, count=20000)
        self.assertEqual((self.mu.reg_read(r.UC_X86_REG_IP), self.mu.reg_read(r.UC_X86_REG_SP)),
                         (site + code_len, 0x7FC))

    def test_psp(self):
        """PROBE_PSP_USE (DI), PROBE_PSP_TABLE (AL from the table) and PROBE_PSP_DEFENCE (AX taken
        off the record's PSP) as kits.psp_cost: a Mind Bender's telepathy 2 less and psychokinesis
        2 more, a Kineticist's the other way, psychometabolism as it is; kits off, the game's."""
        from dscompanion import kits
        from dscompanion.gamepatch import VEC_PSP_USE, VEC_PSP_TABLE, VEC_PSP_DEFENCE
        table = 0x8500
        for rules in (game.RULE_KITS, 0):
            self.rules(rules)
            for cls, kit in self.PSP_CASES:
                kid = self.kit_of(cls, kit, rules)
                self.creature(cls, kit)  # (combatant 7, creature 5)
                for power in (0, 5, 6, 19, 20, 33):
                    for cost in (0, 1, 2, 9):
                        with self.subTest(rules=rules, cls=cls, kit=kit, power=power, cost=cost):
                            want = kits.psp_cost(kid, power, cost)
                            self.mu.mem_write(SS * 16 + BP + 0x0A, struct.pack("<H", power))
                            self.run_int(VEC_PSP_USE, "505389f88b5e0a", 6, esi=7, edi=cost, eax=0x1111,
                                         ebx=0x2222)
                            self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_DI, r.UC_X86_REG_AX,
                                                                            r.UC_X86_REG_BX)], [want, 0x1111, 0x2222])
                            self.mu.mem_write(table * 16 + power * 8 + 1, bytes((cost,)))
                            self.run_int(VEC_PSP_TABLE, "535188e5260fb64701", 5, esi=7, eax=0x7700, es=table,
                                         ebx=power * 8)
                            self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), 0x7700 | want)
                            self.assertEqual(self.mu.reg_read(r.UC_X86_REG_BX), power * 8)
                            if power != 20:
                                continue
                            rec = self.CREATURES * 16 + 5 * 0x3A
                            self.mu.mem_write(rec + 2, struct.pack("<h", 50))
                            self.mu.mem_write(SS * 16 + BP - 6, struct.pack("<H", 5))
                            self.run_int(VEC_PSP_DEFENCE, "535189c18b46fa", 4, eax=cost, es=self.CREATURES,
                                         ebx=5 * 0x3A, ecx=0x3333)
                            self.assertEqual(struct.unpack("<h", self.mu.mem_read(rec + 2, 2))[0], 50 - want)
                            self.assertEqual(self.mu.reg_read(r.UC_X86_REG_CX), 0x3333)
        self.assertEqual([kits.psp_cost(kits.MIND_BENDER, p, 9) for p in (0, 6, 20)], [11, 9, 7])
        self.assertEqual([kits.psp_cost(kits.KINETICIST, p, 2) for p in (0, 6, 20)], [1, 2, 4])

    SEED = 0x4122  # (DS: the game's rand() seed, the header's seed_off)

    def test_cure(self):
        """PROBE_CURE: the healing pushed for the routine that heals (with DI after it) as the
        caster's kit has it (kits.cure_bonus; a Lifebinder's die from the game's seed, which moves
        on), then CS pushed as the code did."""
        from dscompanion import kits
        from dscompanion.gamepatch import VEC_CURE
        at = self.image.find(bytes.fromhex("83ec025589e560"))
        self.assertGreater(at, 0)
        self.mu.mem_write(VEC_CURE * 4, struct.pack("<HH", at, TSR))
        self.mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        site = 0x480
        for rules in (game.RULE_KITS, 0):
            self.rules(rules)
            for cls, kit in ((1, 2), (5, 2), (1, 1), (5, 0), (9, 1)):
                kid = self.kit_of(cls, kit, rules)
                self.creature(cls, kit)
                for spell in (kits.CURE_LIGHT, kits.CURE_SERIOUS, kits.CURE_CRITICAL, kits.BLOOD_FLOW, 72, 71 + 256):
                    with self.subTest(rules=rules, cls=cls, kit=kit, spell=spell):
                        self.mu.mem_write(SS * 16 + BP + 8, struct.pack("<H", 7))
                        self.mu.mem_write(SS * 16 + BP + 0x0E, struct.pack("<H", spell))
                        seed = 0x12345678
                        self.mu.mem_write(self.DS * 16 + self.SEED, struct.pack("<I", seed))
                        site += 0x10  # (code the emulator hasn't seen)
                        self.mu.mem_write(CALLER * 16 + site, bytes((0x50, 0x57, 0xCD, VEC_CURE, 0x90)))
                        for name, value in dict(cs=CALLER, ds=self.DS, ss=SS, esp=0x7FC, ebp=BP, eflags=IF | 2,
                                                eax=10, edi=0x0505, ebx=0x2222).items():
                            self.mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
                        self.mu.emu_start(CALLER * 16 + site, CALLER * 16 + site + 4)
                        sp = self.mu.reg_read(r.UC_X86_REG_SP)
                        self.assertEqual(sp, 0x7FC - 6)
                        pushed_cs, pushed_di, healing = struct.unpack("<HHH", self.mu.mem_read(SS * 16 + sp, 6))
                        die = 0
                        sides = kits.cure_die(kid, spell % 256 if spell < 256 else 0)
                        if sides:
                            nxt = (seed * 0x015A4E35 + 1) & 0xFFFFFFFF
                            die = ((nxt >> 16) & 0x7FFF) * sides // 32768 + 1
                            self.assertEqual(struct.unpack("<I", self.mu.mem_read(self.DS * 16 + self.SEED, 4))[0], nxt)
                        want = 10 + (kits.cure_bonus(kid, spell) if spell < 256 else 0) + die
                        self.assertEqual((pushed_cs, pushed_di, healing), (CALLER, 0x0505, want))
                        self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_AX, r.UC_X86_REG_BX,
                                                                        r.UC_X86_REG_DI, r.UC_X86_REG_BP)],
                                         [10, 0x2222, 0x0505, BP])
        self.assertEqual([kits.cure_bonus(kits.HEALER, s) for s in (71, 112, 127, 108)], [1, 2, 3, 0])
        self.assertEqual([kits.cure_die(kits.LIFEBINDER, s) for s in (71, 108, 72)], [8, 6, 0])

    def test_ranger_cast(self):
        """PROBE_RANGER_CAST: DX (a ranger's level) 7 less, a Seeker's 5, a Justifier's 9."""
        from dscompanion import kits
        from dscompanion.gamepatch import VEC_RANGER_CAST
        for rules in (game.RULE_KITS, 0):
            self.rules(rules)
            for cls, kit in ((13, 3), (13, 2), (13, 1), (14, 0)):
                kid = self.kit_of(cls, kit, rules)
                self.creature(cls, kit)
                with self.subTest(rules=rules, cls=cls, kit=kit):
                    self.mu.mem_write(SS * 16 + BP + 6, struct.pack("<H", 7))
                    self.run_int(VEC_RANGER_CAST, "50530652", 3, edx=10, eax=0x1111, ebx=0x2222, es=0x6666)
                    self.assertEqual(self.mu.reg_read(r.UC_X86_REG_DX), 10 - kits.ranger_cast_drop(kid))
                    self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_AX, r.UC_X86_REG_BX,
                                                                    r.UC_X86_REG_ES)], [0x1111, 0x2222, 0x6666])

    def test_psp_keep(self):
        """PROBE_PSP_KEEP (SI the combatant) and PROBE_PSP_KEEP_DX (DX): the table's cost to keep a
        power up (+2) as kits.psp_cost, 63h (none) as it is."""
        from dscompanion import kits
        from dscompanion.gamepatch import VEC_PSP_KEEP, VEC_PSP_KEEP_DX
        table = 0x8500
        for rules in (game.RULE_KITS, 0):
            self.rules(rules)
            for cls, kit in self.PSP_CASES:
                kid = self.kit_of(cls, kit, rules)
                self.creature(cls, kit)
                for power in (0, 6, 20):
                    for keep in (0, 1, 4, 0x63):
                        with self.subTest(rules=rules, cls=cls, kit=kit, power=power, keep=keep):
                            want = keep if keep == 0x63 else kits.psp_cost(kid, power, keep)
                            self.mu.mem_write(table * 16 + power * 8 + 2, bytes((keep,)))
                            for vector, regs in ((VEC_PSP_KEEP, dict(esi=7, edx=0x4444)),
                                                 (VEC_PSP_KEEP_DX, dict(esi=0x5555, edx=7))):
                                self.run_vector(vector, 5, eax=0x7700, es=table, ebx=power * 8, **regs)
                                self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), 0x7700 | want)
                                self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_BX, r.UC_X86_REG_SI,
                                                                                r.UC_X86_REG_DX)],
                                                 [power * 8, regs["esi"], regs["edx"]])

    def run_vector(self, vector, code_len, **regs):
        """INT VECTOR as run_int, its handler where the helper's install sets it (the vectors read
        from the image's own install code: "mov ax,25xxh / mov dx,handler")."""
        at = self.image.find(bytes((0xB8, vector, 0x25, 0xBA)))
        self.assertGreater(at, 0)
        handler = struct.unpack_from("<H", self.image, at + 4)[0]
        self.run_int(vector, self.image[handler:handler + 8].hex(), code_len, **regs)

    def test_hit_round(self):
        """PROBE_HIT_ROUND: creature SI marked hit this round (ES:SI+0AFh), but not a Battle Mage."""
        from dscompanion.gamepatch import VEC_HIT_ROUND
        marks = 0x8600
        for rules in (game.RULE_KITS, 0):
            self.rules(rules)
            for cls, kit in ((11, 2), (11, 1), (11, 0), (1, 2)):
                self.creature(cls, kit)  # (creature 5)
                with self.subTest(rules=rules, cls=cls, kit=kit):
                    self.mu.mem_write(marks * 16 + 5 + 0xAF, b"\0")
                    self.run_vector(VEC_HIT_ROUND, 6, esi=5, es=marks, eax=0x1111)
                    battle_mage = rules and (cls, kit) == (11, 2)
                    self.assertEqual(self.mu.mem_read(marks * 16 + 5 + 0xAF, 1)[0], 0 if battle_mage else 1)
                    self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), 0x1111)

    def test_arcanist_second_spell(self):
        """PROBE_CAST_MARK, PROBE_CAST_DONE, PROBE_END_TURN and PROBE_ROUND_MARK: in a fight (ES:[19h]
        not 0) a spell aimed on the map marks its caster (ES:BX+0AFh) and finishing the cast ends
        the turn (the actions routine called with 0); an Arcanist's first preserver spell of its
        turn (DS:[54FBh] 0, party member DS:[54FCh]) does neither, the end asked from another code
        segment being let go (the routine's own ending it still does), till the main loop runs;
        its second does, as does a priest spell, an item or another kit's; a turn's start (SI)
        clears the mark and the count. The JE after the finishing routine's compare keeps the
        game's flags."""
        from dscompanion.gamepatch import VEC_CAST_MARK, VEC_CAST_DONE, VEC_END_TURN, VEC_ROUND_MARK
        marks, fight = 0x8600, 0x8700
        ZF, OUT = 0x40, 0x592AF - 0x59260
        def ends(thing=2, caller=0x1234, actions=0):
            """Whether the actions routine (CALLER the segment calling it) goes on to set them."""
            site = 0x640  # (past run_int's sites: the emulator keeps code it has seen)
            code = bytes((0xCD, VEC_END_TURN, 0x90, 0xEB, 0xFE)) + bytes(OUT - 2) + bytes((0xEB, 0xFE))
            self.mu.mem_write(CALLER * 16 + site, code)
            install = self.image.find(bytes((0xB8, VEC_END_TURN, 0x25, 0xBA)))
            self.mu.mem_write(VEC_END_TURN * 4, struct.pack("<HH", struct.unpack_from("<H", self.image, install + 4)[0], TSR))
            self.mu.mem_write(SS * 16 + BP + 4, struct.pack("<HHH", caller, thing, actions))
            for name, value in dict(cs=CALLER, ds=self.DS, ss=SS, esp=0x7FC, ebp=BP, eflags=IF | 2, eax=0x1111,
                                    esi=0x5555).items():
                self.mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
            self.mu.emu_start(CALLER * 16 + site, 0, count=60)
            ip = self.mu.reg_read(r.UC_X86_REG_IP)
            self.assertIn(ip, (site + 3, site + 3 + OUT))
            self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_AX, r.UC_X86_REG_SP, r.UC_X86_REG_BP,
                                                            r.UC_X86_REG_SI)], [0x1111, 0x7FC, BP, actions])
            return ip == site + 3
        def cast(kind, aimed=True):
            """(marked, turn ends) for party member 2's cast of KIND."""
            self.mu.mem_write(self.DS * 16 + 0x54FB, bytes((kind, 2)))
            if aimed:
                self.run_vector(VEC_CAST_MARK, 6, ebx=2, es=marks, eax=0x1111)
                self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_AX, r.UC_X86_REG_BX)], [0x1111, 2])
            self.run_vector(VEC_CAST_DONE, 6, es=fight, eax=0x1111, ebx=0x2222)
            self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_AX, r.UC_X86_REG_BX)], [0x1111, 0x2222])
            self.assertFalse(self.mu.reg_read(r.UC_X86_REG_EFLAGS) & ZF)  # (in a fight: the game's)
            return self.mu.mem_read(marks * 16 + 2 + 0xAF, 1)[0], ends()
        def new_turn():
            self.mu.mem_write(marks * 16 + 2 + 0xAF, b"\1")
            self.run_vector(VEC_ROUND_MARK, 6, esi=2, es=marks)
            self.assertEqual(self.mu.mem_read(marks * 16 + 2 + 0xAF, 1)[0], 0)
        self.mu.mem_write(fight * 16 + 0x19, struct.pack("<H", 1))
        for rules in (game.RULE_KITS, 0):
            self.rules(rules)
            for cls, kit in ((11, 3), (11, 2), (1, 3)):
                self.creature(cls, kit, index=2)
                arcanist = bool(rules) and (cls, kit) == (11, 3)
                with self.subTest(rules=rules, cls=cls, kit=kit):
                    new_turn()
                    self.assertEqual(cast(0), (0, False) if arcanist else (1, True))
                    self.assertTrue(ends(caller=CALLER))  # (the fight's own routines: the turn ends)
                    self.assertTrue(ends(thing=1))  # (another's turn)
                    self.assertEqual(ends(actions=0x10), True)
                    self.assertEqual(cast(0), (1, True))
                    new_turn()
                    self.assertEqual([cast(0, aimed=False), cast(0, aimed=False)],
                                     [(0, False), (0, True)] if arcanist else [(0, True)] * 2)
                    new_turn()
                    self.assertEqual([cast(1), cast(3)], [(1, True)] * 2)  # (a priest spell, an item)
                    new_turn()
                    self.assertEqual(cast(0)[1], not arcanist)
                    new_turn()  # (a turn's start lets the held turn go)
                    self.assertTrue(ends())
        self.mu.mem_write(fight * 16 + 0x19, struct.pack("<H", 0))  # (out of a fight: the game's)
        self.run_vector(VEC_CAST_DONE, 6, es=fight)
        self.assertTrue(self.mu.reg_read(r.UC_X86_REG_EFLAGS) & ZF)
        self.assertTrue(ends())

    SHINOBI_CASES = ((17, 3), (17, 1), (11, 1), (13, 2))

    def test_cast_level(self):
        """PROBE_CAST_LEVEL and PROBE_SPELL_LEVEL: AX the level the routines' classes give ([BP-2],
        DI), a Shinobi's for a wizard spell its thief level less 5 where better (kits.cast_level)."""
        from dscompanion import kits
        from dscompanion.gamepatch import VEC_CAST_LEVEL, VEC_SPELL_LEVEL
        for rules in (game.RULE_KITS, 0):
            self.rules(rules)
            for cls, kit in self.SHINOBI_CASES + ((13, 3),):
                kid = self.kit_of(cls, kit, rules)
                for level in (1, 5, 6, 8, 10):
                    self.creature(cls, kit, level=level)
                    for spell in (0, 30, 68, 69, 86, 137, 138):
                        for given in (0, 2, 7, 10):
                            with self.subTest(rules=rules, cls=cls, kit=kit, level=level, spell=spell, given=given):
                                self.mu.mem_write(SS * 16 + BP - 2, struct.pack("<H", given))
                                self.mu.mem_write(SS * 16 + BP + 6, struct.pack("<HH", 7, spell))
                                for vector, length, di, want in (
                                        (VEC_CAST_LEVEL, 3, 0x5555, kits.cast_level(kid, spell, given, level)),
                                        (VEC_SPELL_LEVEL, 2, given, kits.cast_level(kid, spell, given, level))):
                                    self.run_vector(vector, length, eax=0x1111, ebx=0x2222, ecx=0x3333, edi=di, es=0x6666)
                                    self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), want)
                                    self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_BX, r.UC_X86_REG_CX,
                                                                                    r.UC_X86_REG_DI, r.UC_X86_REG_ES)],
                                                     [0x2222, 0x3333, di, 0x6666])
        self.assertEqual([kits.shinobi_cast(n) for n in (1, 5, 6, 8, 10)], [0, 0, 1, 3, 5])

    def test_elementalist_spells(self):
        """PROBE_EL_CAST and PROBE_EL_LEVEL: the spell's mask read (EDX, EBX), an Elementalist's
        second sphere's spells its own class's too (kits.spell_spheres); PROBE_EL_GRANT: its second
        sphere's cleric bit in the priest mask the spells are given by ([BP-6]), SI cleared."""
        from dscompanion import kits
        from dscompanion.gamepatch import VEC_EL_CAST, VEC_EL_LEVEL, VEC_EL_GRANT
        spells = 0x6600
        for rules in (game.RULE_KITS, 0):
            self.rules(rules)
            for cls, kit, second in ((1, 1, 2), (2, 1, 0), (4, 1, 3), (1, 1, None), (1, 2, 2), (13, 3, 2)):
                self.creature(cls, kit)  # (combatant 7, creature 5, sheet 5)
                self.mu.mem_write(self.SHEET * 16 + 5 * 0x47 + kits.SPHERE2, bytes((0 if second is None else second + 1,)))
                elementalist = rules and cls <= 4 and kit == 1 and second is not None
                kid = kits.ELEMENTALIST if elementalist else 0
                self.mu.mem_write(SS * 16 + BP + 6, struct.pack("<H", 7))
                for mask in (0x110112, 0x104046, 0x10808A, 0x120222, 0x13C3FE, 0x81001, 0):
                    with self.subTest(rules=rules, cls=cls, kit=kit, second=second, mask=hex(mask)):
                        want = kits.spell_spheres(kid, cls, second, mask)
                        self.mu.mem_write(spells * 16 + 0x10 + 0x19D, struct.pack("<I", mask))
                        self.run_vector(VEC_EL_CAST, 6, eax=0x11112222, ebx=0x3333, esi=0x10, edx=0, es=spells)
                        self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_EDX, r.UC_X86_REG_EAX,
                                                                        r.UC_X86_REG_BX, r.UC_X86_REG_SI, r.UC_X86_REG_ES)],
                                         [want, 0x11112222, 0x3333, 0x10, spells])
                        self.run_vector(VEC_EL_LEVEL, 6, eax=0x11112222, ebx=0x10, ecx=0x4444, edx=0x5555, es=spells)
                        self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_EBX, r.UC_X86_REG_EAX,
                                                                        r.UC_X86_REG_CX, r.UC_X86_REG_DX)],
                                         [want, 0x11112222, 0x4444, 0x5555])
                with self.subTest(rules=rules, cls=cls, kit=kit, second=second, probe="grant"):
                    self.mu.mem_write(SS * 16 + BP - 6, struct.pack("<I", 2 << cls))
                    self.run_vector(VEC_EL_GRANT, 2, eax=0x1111, ebx=0x2222, ecx=0x3333, esi=0x5555, es=0x6666)
                    got, = struct.unpack("<I", self.mu.mem_read(SS * 16 + BP - 6, 4))
                    self.assertEqual(got, (2 << cls) | (4 << second if elementalist else 0))
                    self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_SI, r.UC_X86_REG_AX, r.UC_X86_REG_BX,
                                                                    r.UC_X86_REG_CX, r.UC_X86_REG_ES)],
                                     [0, 0x1111, 0x2222, 0x3333, 0x6666])
        # PROBE_EL_KNOW: member 5's class bit (EAX) tested against the spell's mask, ZF as the test
        from dscompanion.gamepatch import VEC_EL_KNOW
        for rules in (game.RULE_KITS, 0):
            self.rules(rules)
            for cls, kit, second in ((2, 1, 3), (1, 1, 2), (2, 1, None), (2, 2, 3)):
                self.creature(cls, kit)
                self.mu.mem_write(self.SHEET * 16 + 5 * 0x47 + kits.SPHERE2, bytes((0 if second is None else second + 1,)))
                kid = kits.ELEMENTALIST if rules and kit == 1 and second is not None else 0
                for mask in (0x120222, 0x10808A, 0x104046, 0x13C3FE):
                    with self.subTest(rules=rules, cls=cls, kit=kit, second=second, mask=hex(mask), probe="know"):
                        self.mu.mem_write(spells * 16 + 0x20 + 0x19D, struct.pack("<I", mask))
                        bit = 2 << cls
                        self.run_vector(VEC_EL_KNOW, 6, eax=bit, ebx=0x20, ecx=0x12345678, esi=5, es=spells)
                        zf = bool(self.mu.reg_read(r.UC_X86_REG_EFLAGS) & 0x40)
                        self.assertEqual(zf, not kits.spell_spheres(kid, cls, second, mask) & bit)
                        self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_EAX, r.UC_X86_REG_EBX, r.UC_X86_REG_ECX,
                                                                        r.UC_X86_REG_SI, r.UC_X86_REG_ES)],
                                         [bit, 0x20, 0x12345678, 5, spells])
        self.assertEqual(kits.spell_spheres(kits.ELEMENTALIST, 1, 2, 0x110112), 0x110116)  # (fire's: the air cleric's too)
        self.assertEqual(kits.spell_spheres(kits.ELEMENTALIST, 1, 2, 0x10808A), 0x10808A)


    def test_dual_ban(self):
        """PROBE_DUAL_BAN: the game's yes (AX 1) to a class on the DUAL window made no for a class
        the kit bars (kits.dual_banned), ZF as "or ax,ax"; the game's no kept."""
        from dscompanion import kits, kitpages
        from dscompanion.gamepatch import VEC_DUAL_BAN
        self.creature(13, 3)  # (DS:1661h the sheets)
        for rules in (game.RULE_KITS, 0):
            self.rules(rules)
            for cls, kit in ((13, 3), (14, 2), (13, 1), (17, 3), (17, 1), (11, 2), (1, 3), (12, 2), (10, 1),
                             (9, 2), (10, 3), (10, 2), (5, 2)):
                sheet = bytearray(game.SHEET_SIZE)
                sheet[0x18], sheet[0x21], sheet[0x24], sheet[kitpages.KIT_BYTE] = 1, cls, 5, kit
                self.mu.mem_write(self.SHEET * 16 + 2 * game.SHEET_SIZE, bytes(sheet))
                self.mu.mem_write(SS * 16 + BP + 6, struct.pack("<H", 2))
                kid = any_kit(bytes(sheet)) if rules else 0
                for new in (1, 2, 5, 8, 9, 10, 11, 12, 13, 16, 17):
                    for given in (0, 1):
                        with self.subTest(rules=rules, cls=cls, kit=kit, new=new, given=given):
                            self.run_vector(VEC_DUAL_BAN, 2, eax=given, ebx=0x2222, esi=new, es=0x6666)
                            want = int(given and not kits.dual_banned(kid, new))
                            self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), want)
                            self.assertEqual(bool(self.mu.reg_read(r.UC_X86_REG_EFLAGS) & 0x40), not want)
                            self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_BX, r.UC_X86_REG_SI,
                                                                            r.UC_X86_REG_ES)], [0x2222, new, 0x6666])
        self.assertEqual([kits.dual_banned(kits.SEEKER, c) for c in (1, 8, 9, 11)], [True, True, False, False])
        self.assertEqual([kits.dual_banned(kits.SHINOBI, c) for c in (1, 11)], [False, True])

    def picker_sheet(self, cls, kit, level):
        from dscompanion import kitpages
        sheet = bytearray(game.SHEET_SIZE)
        sheet[0x21], sheet[0x24], sheet[kitpages.KIT_BYTE] = cls, level, kit
        self.mu.mem_write(self.CREATION * 16, bytes(sheet))  # (DS:[119Ch] points at it)

    def test_pick_level(self):
        """PROBE_PICK_LEVEL: AL (the preserver level) + 1, a Shinobi's casting level + 1."""
        from dscompanion import kits
        from dscompanion.gamepatch import VEC_PICK_LEVEL
        for rules in (game.RULE_KITS, 0):
            self.rules(rules)
            for cls, kit in self.SHINOBI_CASES:
                kid = self.kit_of(cls, kit, rules)
                for level in (5, 6, 8, 10):
                    with self.subTest(rules=rules, cls=cls, kit=kit, level=level):
                        self.picker_sheet(cls, kit, level)
                        al = level if cls == 11 else 0
                        self.run_vector(VEC_PICK_LEVEL, 2, eax=0x1100 | al, ebx=0x2222, es=0x6666)
                        want = (kits.shinobi_cast(level) if kid == kits.SHINOBI else al) + 1
                        self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AL), want)
                        self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_BX, r.UC_X86_REG_ES)],
                                         [0x2222, 0x6666])

    def dual_sheet(self, classes, levels, kit, member=3):
        """Human member MEMBER's sheet (DS:[1661h] the sheets): CLASSES, LEVELS, the kit byte KIT."""
        from dscompanion import kitpages
        sheet = bytearray(game.SHEET_SIZE)
        sheet[0x18], sheet[kitpages.KIT_BYTE] = 1, kit
        sheet[0x21:0x21 + len(classes)], sheet[0x24:0x24 + len(levels)] = bytes(classes), bytes(levels)
        self.mu.mem_write(self.DS * 16 + 0x1661, struct.pack("<HH", 0, self.SHEET))
        self.mu.mem_write(self.SHEET * 16 + member * 0x47, bytes(sheet))
        return bytes(sheet)

    def test_cr_spells(self):
        """PROBE_CR_SPELLS: a new preserver of level [BP-2] 1-3 picks its spells on CHOOSE A SPELL (2,
        4, or 4 and two of 2nd level) and goes on past the game's grants (66F83h); another level:
        AX [BP-2], on as before."""
        from dscompanion.gamepatch import VEC_CR_SPELLS, VEC_PICK_LEVEL
        at = self.image.find(bytes((0xB8, VEC_PICK_LEVEL, 0x25, 0xBA)))
        self.mu.mem_write(VEC_PICK_LEVEL * 4, struct.pack("<HH", struct.unpack_from("<H", self.image, at + 4)[0], TSR))
        self.rules(0)
        stub = (self.DS + 0x430A - 0x4356) * 16 + 0x5C
        # the stub as the window: count the calls, and the spell levels on offer at preserver level 9
        self.mu.mem_write(stub, bytes.fromhex(PICK_STUB % VEC_PICK_LEVEL))
        at = self.image.find(bytes((0xB8, VEC_CR_SPELLS, 0x25, 0xBA)))
        self.mu.mem_write(VEC_CR_SPELLS * 4, struct.pack("<HH", struct.unpack_from("<H", self.image, at + 4)[0], TSR))
        if not getattr(self, "hooked", False):
            self.mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
            self.hooked = True
        site = 0x400 + (VEC_CR_SPELLS & 0x1F) * 0x10
        past = site + 2 + (0x66F83 - 0x66F2F)
        self.mu.mem_write(CALLER * 16 + site, bytes((0xCD, VEC_CR_SPELLS, 0x90)))
        self.mu.mem_write(CALLER * 16 + past, b"\x90")
        self.mu.mem_write(self.DS * 16 + 0x1665, struct.pack("<HH", CR_TABLE, self.DS))
        status = self.DS * 16 + CR_TABLE + 3 * 0x3A + 0x1C  # (member 3's, SI)
        # (the game's own party, Okay when START GAME makes it, keeps the game's spells)
        for level, picks, okay in ((0, None, 0), (1, (2, 2), 0), (2, (2, 2, 2, 2), 0), (3, (2, 2, 2, 2, 4, 4), 0),
                                   (4, None, 0), (1, None, 1), (3, None, 1)):
            with self.subTest(level=level, okay=okay):
                self.mu.mem_write(status, bytes((okay,)))
                self.mu.mem_write(self.DS * 16 + 0xF000, bytes(0x12))
                self.mu.mem_write((self.DS - 0xB56) * 16 + KNOWN_3, bytes(0x8A))
                self.mu.mem_write(SS * 16 + BP - 2, struct.pack("<H", level))
                for name, value in dict(cs=CALLER, ds=self.DS, ss=SS, esp=0x7FC, ebp=BP, eflags=IF | 2, esi=3,
                                        eax=0x1234, ecx=0x5678).items():
                    self.mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
                end = past if picks else site + 3
                self.mu.emu_start(CALLER * 16 + site, CALLER * 16 + end, count=50000)
                self.assertEqual((self.mu.reg_read(r.UC_X86_REG_IP), self.mu.reg_read(r.UC_X86_REG_SP)), (end, 0x7FC))
                count, = struct.unpack("<H", self.mu.mem_read(self.DS * 16 + 0xF000, 2))
                self.assertEqual(count, len(picks) if picks else 0)
                if picks:
                    self.assertEqual(bytes(self.mu.mem_read(self.DS * 16 + 0xF002, len(picks))), bytes(picks))
                    self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_AX, r.UC_X86_REG_CX, r.UC_X86_REG_SI,
                                                                    r.UC_X86_REG_BP)], [level, 0x5678, 3, BP])
                else:
                    self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), level)

    def test_cr_spells_exit(self):
        """EXIT on CHOOSE A SPELL (the window left with no spell learnt): the picks are over, and the
        ones left are the game's own starting spells not yet known (PICK_FILL): 1st level Grease (7),
        Magic Missile (8), Shield (0Bh), Wall of Fog (9); 2nd level Fog Cloud (0Fh), Mirror Image (16h)."""
        from dscompanion.gamepatch import VEC_CR_SPELLS, VEC_PICK_LEVEL
        at = self.image.find(bytes((0xB8, VEC_PICK_LEVEL, 0x25, 0xBA)))
        self.mu.mem_write(VEC_PICK_LEVEL * 4, struct.pack("<HH", struct.unpack_from("<H", self.image, at + 4)[0], TSR))
        self.rules(0)
        self.mu.mem_write((self.DS + 0x430A - 0x4356) * 16 + 0x5C, bytes.fromhex(PICK_STUB % VEC_PICK_LEVEL))
        at = self.image.find(bytes((0xB8, VEC_CR_SPELLS, 0x25, 0xBA)))
        self.mu.mem_write(VEC_CR_SPELLS * 4, struct.pack("<HH", struct.unpack_from("<H", self.image, at + 4)[0], TSR))
        if not getattr(self, "hooked", False):
            self.mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
            self.hooked = True
        site = 0x480
        past = site + 2 + (0x66F83 - 0x66F2F)
        self.mu.mem_write(CALLER * 16 + site, bytes((0xCD, VEC_CR_SPELLS, 0x90)))
        self.mu.mem_write(CALLER * 16 + past, b"\x90")
        self.mu.mem_write(self.DS * 16 + 0x1665, struct.pack("<HH", CR_TABLE, self.DS))
        self.mu.mem_write(self.DS * 16 + CR_TABLE + 3 * 0x3A + 0x1C, b"\x00")  # (New)
        known = (self.DS - 0xB56) * 16 + KNOWN_3
        for level, before, want in ((1, (), (7, 8)), (3, (), (7, 8, 9, 0x0B, 0x0F, 0x16)),
                                    (1, (7,), (7, 8, 0x0B)), (2, (8, 9), (7, 8, 9, 0x0B))):
            with self.subTest(level=level, before=before):
                self.mu.mem_write(self.DS * 16 + 0xF000, bytes(0x12))
                self.mu.mem_write(self.DS * 16 + 0xF010, b"\x01")
                self.mu.mem_write(known, bytes(0x8A))
                for spell in before:
                    self.mu.mem_write(known + spell, b"\x01")
                self.mu.mem_write(SS * 16 + BP - 2, struct.pack("<H", level))
                for name, value in dict(cs=CALLER, ds=self.DS, ss=SS, esp=0x7FC, ebp=BP, eflags=IF | 2, esi=3,
                                        eax=0x1234, ecx=0x5678).items():
                    self.mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
                self.mu.emu_start(CALLER * 16 + site, CALLER * 16 + past, count=50000)
                self.assertEqual((self.mu.reg_read(r.UC_X86_REG_IP), self.mu.reg_read(r.UC_X86_REG_SP)), (past, 0x7FC))
                got = bytes(self.mu.mem_read(known, 0x8A))
                self.assertEqual(tuple(i for i, b in enumerate(got) if b & 0x0F), want)
                self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_CX, r.UC_X86_REG_SI)], [0x5678, 3])

    def test_dual_kit_banned(self):
        """DK_BANNED: a kit for a human's new class (first on its sheet) barred by its other classes
        or their kits, asleep too (kits.dual_kit_banned)."""
        from dscompanion import kitpages, kits
        self.rules(game.RULE_KITS)
        import re
        at = re.search(rb"\x66\x60\x88\xc1\xe8", self.image).start()
        cases = [((11, 9), (1, 4), 0b01), ((11, 9), (1, 4), 0b10), ((10, 9), (1, 4), 0b11), ((1, 10), (1, 4), 0b10),
                 ((17, 10), (1, 4), 0b10), ((17, 12, 11), (1, 3, 4), 0b0100), ((12, 17), (1, 4), 0b11),
                 ((5, 10), (1, 4), 0b11), ((13, 1), (1, 4), 0), ((9, 17, 2), (1, 2, 3), 0b0011)]
        for classes, levels, kit in cases:
            sheet = self.dual_sheet(classes, levels, kit, member=0)
            others = [c for c in classes[1:]]
            kids = [k for k, place, _ in kitpages.kits_of(sheet) if place]
            for kid in sorted(kitpages.KIT_IDS.values()):
                with self.subTest(classes=classes, kit=kit, kid=kid):
                    self.mu.mem_write(TSR * 16 + 0xFFF0, b"\x90")
                    mu = self.mu
                    mu.mem_write(SS * 16 + 0x7FC, struct.pack("<H", 0xFFF0))
                    for name, value in dict(cs=TSR, ds=self.DS, ss=SS, esp=0x7FC, es=self.SHEET, ebx=0, eax=kid,
                                            eflags=2).items():
                        mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
                    mu.emu_start(TSR * 16 + at, TSR * 16 + 0xFFF0)
                    self.assertEqual(bool(mu.reg_read(r.UC_X86_REG_EFLAGS) & 1), kits.dual_kit_banned(kid, others, kids))
                    self.assertEqual(mu.reg_read(r.UC_X86_REG_AX), kid)
        self.assertTrue(kits.dual_kit_banned(kits.SHINOBI, [11], []))
        self.assertTrue(kits.dual_kit_banned(kits.HEALER, [10], [kits.TWIN_BLADE]))
        self.assertFalse(kits.dual_kit_banned(kits.HEALER, [10], [kits.CHAMPION]))

    def test_dual_kit(self):
        """PROBE_DUAL_KIT: the new class's kit on the game's three-choice menu (4D0:25h, through its
        stub at DS less 1A2h): "KIT: NONE", the class's three kits, a barred one blank; the row
        clicked goes in the kit byte's bits for the new class; an Elementalist's second sphere on
        the menu again. Then the compare, its flags back."""
        from dscompanion import kitpages, kits
        from dscompanion.gamepatch import VEC_DUAL_KIT
        stub = (self.DS + 0x41B4 - 0x4356) * 16 + 0x25
        record = self.DS * 16 + 0xF000

        def run(new_class, rows):
            # the menu: its stack's args copied to DS:F010 + 40h a call, AX the next of ROWS
            self.mu.mem_write(record, struct.pack("<H", 0) + bytes(14))
            code = bytes.fromhex("5657511e07" "8b360" "0f0" "c1e606" "81c610f0".replace(" ", ""))
            code = bytes.fromhex(
                "56575106" "1e07"                   # push si/di/cx/es; push ds; pop es
                "8b3e00f0" "c1e706" "81c710f0"      # mov di,[F000h]; shl di,6; add di,F010h
                "89e6" "83c60c"                     # mov si,sp; add si,0Ch (past 4 pushes and the far return)
                "b91600" "36" "f3a4"                # mov cx,22; ss rep movsb... (ss: on the source)
                "8b3e00f0" "d1e7" "8b85f0f0"        # mov di,[F000h]; shl di,1; mov ax,[di+F0F0h]
                "ff0600f0" "07595f5e" "cb")         # inc word [F000h]; pop es/cx/di/si; retf
            self.mu.mem_write(stub, code)
            self.mu.mem_write(self.DS * 16 + 0xF0F0, b"".join(struct.pack("<H", x) for x in rows))
            self.mu.mem_write(SS * 16 + BP + 8, struct.pack("<H", new_class))
            self.run_vector(VEC_DUAL_KIT, 4, esi=3, eax=0x1234)
            calls, = struct.unpack("<H", self.mu.mem_read(record, 2))
            menus = []
            for n in range(calls):
                x, y, t_off, t_seg, flag, *opts = struct.unpack("<HHHHH6H", self.mu.mem_read(record + 0x10 + n * 0x40, 22))
                text = lambda off, seg: bytes(self.mu.mem_read(seg * 16 + off, 20)).split(b"\0")[0].decode()
                menus.append([text(t_off, t_seg)] + [text(opts[i], opts[i + 1]) for i in (0, 2, 4)])
            zf = bool(self.mu.reg_read(r.UC_X86_REG_EFLAGS) & 0x40)
            self.assertEqual(zf, new_class == 12)
            self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), 0x1234)
            return menus, bytes(self.mu.mem_read(self.SHEET * 16 + 3 * 0x47, game.SHEET_SIZE))

        self.rules(game.RULE_KITS)
        # a Myrmidon fighter 5 becomes a preserver: Scholar taken; Battle Mage barred (a warrior THAC0)
        self.dual_sheet((11, 9), (1, 5), 1)
        menus, sheet = run(11, [1])
        self.assertEqual(menus, [["KIT: NONE", "SCHOLAR", "", "ARCANIST"]])
        self.assertEqual(kitpages.kits_of(sheet), [(kits.MYRMIDON, 1, False), (kits.SCHOLAR, 0, True)])
        # the barred row clicked, or the title: none
        for row in (2, 0, 4):
            self.dual_sheet((11, 9), (1, 5), 1)
            _, sheet = run(11, [row])
            self.assertEqual(sheet[kitpages.KIT_BYTE], 1)
        # a Twin-blade gladiator becomes a fire cleric: Healer and Crusader barred; an Elementalist picks water
        self.dual_sheet((3, 10), (1, 5), 2)
        menus, sheet = run(3, [1, 3])
        self.assertEqual(menus, [["KIT: NONE", "ELEMENTALIST", "", ""],
                                 ["SPHERE 2: NONE", "AIR", "EARTH", "WATER"]])
        self.assertEqual(kitpages.kits_of(sheet), [(kits.TWIN_BLADE, 1, False), (kits.ELEMENTALIST, 0, True)])
        self.assertEqual(kits.second_sphere(kits.ELEMENTALIST, sheet), 3)
        # twice changed: the third kit's bits above the second's
        self.dual_sheet((12, 11, 9), (1, 6, 5), 0b0101)
        menus, sheet = run(12, [1])
        self.assertEqual(menus, [["KIT: NONE", "MIND BENDER", "", "KINETICIST"]])  # (the Mind Warrior: a fighter's)
        self.assertEqual(kitpages.kits_of(sheet)[-1], (kits.MIND_BENDER, 0, True))
        self.assertEqual(sheet[kitpages.KIT_BYTE], 0b010101)
        # without the rule: no menu
        self.rules(0)
        self.dual_sheet((11, 9), (1, 5), 1)
        menus, sheet = run(11, [1])
        self.assertEqual((menus, sheet[kitpages.KIT_BYTE]), ([], 1))

    def test_dual_spells(self):
        """PROBE_DUAL_SPELLS: a new preserver picks two spells on CHOOSE A SPELL (620:5Ch, through
        its stub at DS less 4Ch), the spell levels on offer up to 1st meanwhile (PICK_CAP, as
        PROBE_PICK_LEVEL gives them), as it was after."""
        from dscompanion.gamepatch import VEC_DUAL_SPELLS, VEC_PICK_LEVEL
        at = self.image.find(bytes((0xB8, VEC_PICK_LEVEL, 0x25, 0xBA)))
        self.mu.mem_write(VEC_PICK_LEVEL * 4, struct.pack("<HH", struct.unpack_from("<H", self.image, at + 4)[0], TSR))
        self.rules(0)
        self.picker_sheet(11, 0, 9)
        stub = (self.DS + 0x430A - 0x4356) * 16 + 0x5C
        # the stub as the window: count the call, and the preserver level 9's spell levels then
        self.mu.mem_write(stub, bytes.fromhex(PICK_STUB % VEC_PICK_LEVEL))
        self.mu.mem_write(self.DS * 16 + 0xF000, bytes(0x12))
        self.mu.mem_write((self.DS - 0xB56) * 16 + KNOWN_3, bytes(0x8A))
        self.run_vector(VEC_DUAL_SPELLS, 22, esi=3, eax=0x1234, ecx=0x5678)
        count, = struct.unpack("<H", self.mu.mem_read(self.DS * 16 + 0xF000, 2))
        self.assertEqual(count, 2)
        self.assertEqual(bytes(self.mu.mem_read(self.DS * 16 + 0xF002, 2)), bytes((2, 2)))  # (up to 1st: AL 1, + 1)
        self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_AX, r.UC_X86_REG_CX, r.UC_X86_REG_SI)],
                         [0x1234, 0x5678, 3])
        self.run_vector(VEC_PICK_LEVEL, 2, eax=9)
        self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AL), 10)  # (no cap after)

    def test_sound_bytes(self):
        """PROBE_SOUND_42 / PROBE_SOUND_44: the sheet's (ES:BX) sound numbers at 42h and 44h, read
        a byte only, the kit (43h) and the second sphere (45h) above them left out."""
        from dscompanion.gamepatch import VEC_SOUND_42, VEC_SOUND_44
        sheet = 0x6666 * 16 + 0x2222
        self.mu.mem_write(sheet + 0x42, bytes((0x17, 0x05, 0x00, 0x03)))
        self.run_vector(VEC_SOUND_42, 4, ebx=0x2222, es=0x6666, edx=0xFFFF, eax=0x1111)
        self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_DX, r.UC_X86_REG_AX)], [0x17, 0x1111])
        self.run_vector(VEC_SOUND_44, 4, ebx=0x2222, es=0x6666, edx=0x3333, eax=0xFFFF)
        self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_AX, r.UC_X86_REG_DX)], [0, 0x3333])

    def test_pick_list(self):
        """PROBE_PICK_LIST: DI the list's length (AX), for a Shinobi its own spells up to the spell
        level on offer it doesn't know, put in the list (kits.pick_list)."""
        from dscompanion import kits
        from dscompanion.gamepatch import VEC_PICK_LIST
        seg, who = 0x8700, 2
        site = 0x400 + (VEC_PICK_LIST & 0x1F) * 0x10
        self.mu.mem_write(CALLER * 16 + site + 2 + (0x8562E - 0x85641), struct.pack("<H", seg))
        self.mu.mem_write(seg * 16 + 0x25B, struct.pack("<H", who))
        known_at = (self.DS - (0x4356 - 0x3800)) * 16 + 0x168 + who * 0x8A
        known = {2, 17, 29}
        self.mu.mem_write(known_at, bytes(1 if n in known else 0 for n in range(0x8A)))
        for rules in (game.RULE_KITS, 0):
            self.rules(rules)
            for cls, kit in self.SHINOBI_CASES:
                kid = self.kit_of(cls, kit, rules)
                for most in (1, 2, 3):
                    with self.subTest(rules=rules, cls=cls, kit=kit, most=most):
                        self.picker_sheet(cls, kit, 10)
                        self.mu.mem_write(self.DS * 16 + 0x4AEC, bytes((most,)))
                        self.mu.mem_write(seg * 16 + 7, struct.pack("<3H", 40, 41, 42))
                        self.run_vector(VEC_PICK_LIST, 2, eax=3, ebx=0x2222, ecx=0x3333, esi=0x4444, es=0x6666)
                        want = kits.pick_list(kid, known.__contains__, most)
                        if want is None:
                            want = [40, 41, 42]
                        di = self.mu.reg_read(r.UC_X86_REG_DI)
                        self.assertEqual(list(struct.unpack("<%dH" % di, self.mu.mem_read(seg * 16 + 7, 2 * di))), want)
                        self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_AX, r.UC_X86_REG_BX, r.UC_X86_REG_CX,
                                                                        r.UC_X86_REG_SI, r.UC_X86_REG_ES, r.UC_X86_REG_DS)],
                                         [3, 0x2222, 0x3333, 0x4444, 0x6666, self.DS])
        self.assertEqual(kits.pick_list(kits.SHINOBI, known.__contains__, 2), [6, 9, 4, 11, 19, 12, 13, 15])

    def test_ranger_level(self):
        """PROBE_RANGER_LEVEL: AL the class's level (ES:BX the sheet + the class's place), a ranger's
        7 less with the rule, a Seeker's 5 and a Justifier's 9 whatever it (kits.spell_class_level)."""
        from dscompanion import kits
        from dscompanion.gamepatch import VEC_RANGER_LEVEL
        for rules in (game.RULE_KITS | game.RULE_RANGER_CAST, game.RULE_KITS, game.RULE_RANGER_CAST, 0):
            self.rules(rules)
            for cls, kit in ((13, 0), (14, 1), (13, 3), (16, 2), (1, 0), (11, 3), (17, 3)):
                kid = self.kit_of(cls, kit, rules)
                for level in (1, 7, 8, 9, 12):
                    with self.subTest(rules=rules, cls=cls, kit=kit, level=level):
                        self.creature(cls, kit, level=level)
                        self.mu.mem_write(SS * 16 + BP + 6, struct.pack("<H", 7))
                        self.run_vector(VEC_RANGER_LEVEL, 4, eax=0x1100, ebx=5 * 0x47, ecx=0x3333, es=self.SHEET)
                        want = kits.spell_class_level(kid, cls, level, bool(rules & game.RULE_RANGER_CAST))
                        self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), 0x1100 | want)
                        self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_BX, r.UC_X86_REG_CX,
                                                                        r.UC_X86_REG_ES)], [5 * 0x47, 0x3333, self.SHEET])
        self.assertEqual([kits.spell_class_level(0, 13, 9, True), kits.spell_class_level(0, 13, 9, False),
                          kits.spell_class_level(kits.SEEKER, 13, 9, False), kits.spell_class_level(0, 1, 6, True),
                          kits.spell_class_level(kits.JUSTIFIER, 13, 7, True)], [2, 9, 4, 6, 0])

    def test_hit_die(self):
        """PROBE_HIT_DIE: AL the group's die (ES:BX), a Battle Mage's a d6, a Mind Warrior's a d8 and
        an Arcanist's a d3 (kits.hit_die; [BP-4] the sheet)."""
        from dscompanion import kits
        from dscompanion.gamepatch import VEC_HIT_DIE
        group = 0x8800
        for rules in (game.RULE_KITS, 0):
            self.rules(rules)
            for cls, kit in ((11, 2), (11, 1), (11, 3), (12, 2), (12, 1), (9, 2), (17, 2)):
                kid = self.kit_of(cls, kit, rules)
                self.creature(cls, kit, index=5)
                for die in (4, 6, 10):
                    with self.subTest(rules=rules, cls=cls, kit=kit, die=die):
                        self.mu.mem_write(group * 16, bytes((die,)))
                        self.mu.mem_write(SS * 16 + BP - 4, struct.pack("<HH", 5 * 0x47, self.SHEET))
                        self.run_vector(VEC_HIT_DIE, 5, eax=0x1100, ebx=0, ecx=0x3333, es=group)
                        self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), 0x1100 | kits.hit_die(kid, die))
                        self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_BX, r.UC_X86_REG_CX,
                                                                        r.UC_X86_REG_ES)], [0, 0x3333, group])
        self.assertEqual([kits.hit_die(kits.BATTLE_MAGE, 4), kits.hit_die(kits.MIND_WARRIOR, 6),
                          kits.hit_die(kits.ARCANIST, 4), kits.hit_die(kits.SCHOLAR, 4)], [6, 8, 3, 4])

    def made(self, cls, kit, seen=True):
        """The sheet being made of creation class CLS (1-8) with kit KIT, PROBE_WP_CLASS having seen
        its classes (SEEN) or another's."""
        from dscompanion import kitpages
        from dscompanion.gamepatch import VEC_WP_CLASS
        mu = self.mu
        mu.mem_write(self.DS * 16 + 0xEA2, bytes(8))  # (no panel window up)
        sheet = bytearray(game.SHEET_SIZE)
        sheet[0x21] = cls if seen else cls % 8 + 1
        mu.mem_write(self.CREATION * 16, bytes(sheet))
        if not getattr(self, "hooked", False):
            mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
            self.hooked = True
        at = self.image.find(bytes((0xB8, VEC_WP_CLASS, 0x25, 0xBA)))
        mu.mem_write(VEC_WP_CLASS * 4, struct.pack("<HH", struct.unpack_from("<H", self.image, at + 4)[0], TSR))
        site = 0x600  # (a site of its own: run_vector's for VEC_CR_DIE shares the low bits)
        mu.mem_write(CALLER * 16 + site, bytes((0xCD, VEC_WP_CLASS, 0x90)))
        for name, value in dict(cs=CALLER, ds=self.DS, ss=SS, esp=0x7FC, ebp=BP, eflags=IF | 2).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(CALLER * 16 + site, CALLER * 16 + site + 3, count=20000)
        sheet[0x21], sheet[kitpages.KIT_BYTE] = cls, kit
        mu.mem_write(self.CREATION * 16, bytes(sheet))

    def test_cr_die(self):
        """PROBE_CR_DIE: AL the class's die at creation (ES:BX+14Ah), the kit's (kits.hit_die) for
        the sheet being made; a kit left from other classes (a class just clicked) taken away from it
        and from the party's sheet ([348h:25Bh] its number, the segment read from the overlay's code
        past the INT), the class's die then."""
        from dscompanion import kits, kitpages
        from dscompanion.gamepatch import VEC_CR_DIE
        table, member_seg = 0x8800, 0x8900
        site = 0x400 + (VEC_CR_DIE & 0x1F) * 0x10
        self.mu.mem_write(CALLER * 16 + site + 2 + 0x10, struct.pack("<H", member_seg))
        self.mu.mem_write(member_seg * 16 + 0x25B, struct.pack("<H", 2))
        self.mu.mem_write(self.DS * 16 + 0x1661, struct.pack("<HH", 0, self.SHEET))
        for rules in (game.RULE_KITS, 0):
            self.rules(rules)
            for cls, kit in ((5, 2), (5, 3), (5, 1), (6, 2), (6, 1), (3, 2)):
                for seen in (True, False):
                    for die in (4, 6, 10):
                        with self.subTest(rules=rules, cls=cls, kit=kit, seen=seen, die=die):
                            self.made(cls, kit, seen)
                            self.mu.mem_write(self.SHEET * 16 + 2 * 0x47 + kitpages.KIT_BYTE, bytes((kit,)))
                            self.mu.mem_write(table * 16 + cls + 0x14A, bytes((die,)))
                            self.run_vector(VEC_CR_DIE, 5, eax=0x1100, ebx=cls, ecx=0x3333, es=table)
                            kid = cls * 4 + kit if rules and seen else 0
                            self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), 0x1100 | kits.hit_die(kid, die))
                            self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_BX, r.UC_X86_REG_CX,
                                                                            r.UC_X86_REG_ES)], [cls, 0x3333, table])
                            left = kit if seen or not rules else 0
                            self.assertEqual([self.mu.mem_read(at * 16 + off + kitpages.KIT_BYTE, 1)[0] for at, off
                                              in ((self.CREATION, 0), (self.SHEET, 2 * 0x47))], [left, left])

    def test_cr_psp(self):
        """PROBE_CR_PSP: the creation PSP routine's end ("pop bp / retf"), the sheet being made's
        most PSP (+0Ch) a tenth less for a Mind Warrior (kits.max_psp); the flags as at the INT
        (IF set again: a click on a score once stopped the game here)."""
        from dscompanion import kits
        from dscompanion.gamepatch import VEC_CR_PSP
        mu = self.mu
        if not getattr(self, "hooked", False):
            mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
            self.hooked = True
        at = self.image.find(bytes((0xB8, VEC_CR_PSP, 0x25, 0xBA)))
        mu.mem_write(VEC_CR_PSP * 4, struct.pack("<HH", struct.unpack_from("<H", self.image, at + 4)[0], TSR))
        site, back = 0x500, 0x520
        mu.mem_write(CALLER * 16 + site, bytes((0xCD, VEC_CR_PSP)))
        for rules in (game.RULE_KITS, 0):
            self.rules(rules)
            for cls, kit in ((6, 2), (6, 1), (5, 2)):
                for psp in (0, 9, 10, 52, 125):
                    with self.subTest(rules=rules, cls=cls, kit=kit, psp=psp):
                        self.made(cls, kit)
                        mu.mem_write(self.CREATION * 16 + 0x0C, struct.pack("<H", psp))
                        mu.mem_write(SS * 16 + 0x7F6, struct.pack("<HHH", 0x1234, back, CALLER))
                        for name, value in dict(cs=CALLER, ds=self.DS, ss=SS, esp=0x7F6, ebp=BP, eflags=IF | 2,
                                                eax=0x1111, ebx=0x2222, ecx=0x3333, edx=0x4444).items():
                            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
                        mu.emu_start(CALLER * 16 + site, CALLER * 16 + back, count=20000)
                        kid = cls * 4 + kit if rules else 0
                        self.assertEqual(struct.unpack("<H", mu.mem_read(self.CREATION * 16 + 0x0C, 2))[0],
                                         kits.max_psp(kid, psp))
                        self.assertEqual([mu.reg_read(x) for x in (r.UC_X86_REG_IP, r.UC_X86_REG_SP, r.UC_X86_REG_BP,
                                                                   r.UC_X86_REG_AX, r.UC_X86_REG_BX, r.UC_X86_REG_CX,
                                                                   r.UC_X86_REG_DX)],
                                         [back, 0x7FC, 0x1234, 0x1111, 0x2222, 0x3333, 0x4444])
                        self.assertTrue(mu.reg_read(r.UC_X86_REG_EFLAGS) & IF)

    def test_max_psp(self):
        """PROBE_MAX_PSP: ES:BX the sheet ([BP-8]), and SI (the most PSP) a tenth less for a Mind
        Warrior (kits.max_psp)."""
        from dscompanion import kits
        from dscompanion.gamepatch import VEC_MAX_PSP
        for rules in (game.RULE_KITS, 0):
            self.rules(rules)
            for cls, kit in ((12, 2), (12, 1), (12, 0), (9, 2)):
                kid = self.kit_of(cls, kit, rules)
                self.creature(cls, kit, index=5)
                for psp in (0, 9, 10, 37, 125):
                    with self.subTest(rules=rules, cls=cls, kit=kit, psp=psp):
                        self.mu.mem_write(SS * 16 + BP - 8, struct.pack("<HH", 5 * 0x47, self.SHEET))
                        self.run_vector(VEC_MAX_PSP, 3, eax=0x1111, esi=psp, ecx=0x3333, edx=0x4444, es=0x6666)
                        self.assertEqual(self.mu.reg_read(r.UC_X86_REG_SI), kits.max_psp(kid, psp))
                        self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_AX, r.UC_X86_REG_BX,
                                                                        r.UC_X86_REG_CX, r.UC_X86_REG_DX,
                                                                        r.UC_X86_REG_ES)],
                                         [0x1111, 5 * 0x47, 0x3333, 0x4444, self.SHEET])
        self.assertEqual([kits.max_psp(kits.MIND_WARRIOR, 37), kits.max_psp(kits.MIND_BENDER, 37)], [34, 37])

    def test_pick_any(self):
        """PROBE_PICK_ANY: [BP-2] and flags as "mov [bp-2],ax / or ax,ax" (the JG after going on for
        a preserver level); for a Shinobi, CHOOSE A SPELL (on PICK_OPEN past the INT, DI 1) while it
        has a spell to learn up to its spell level (kits.pick_list), else AX 0."""
        from dscompanion import kits
        from dscompanion.gamepatch import VEC_PICK_ANY
        who, site, open_at = 5, 0x700, 0x855CB - 0x85582
        at = self.image.find(bytes((0xB8, VEC_PICK_ANY, 0x25, 0xBA)))
        self.mu.mem_write(VEC_PICK_ANY * 4, struct.pack("<HH", struct.unpack_from("<H", self.image, at + 4)[0], TSR))
        if not getattr(self, "hooked", False):
            self.mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
            self.hooked = True
        self.mu.mem_write(CALLER * 16 + site, bytes((0xCD, VEC_PICK_ANY, 0x90, 0x90, 0x90, 0xF4)))
        self.mu.mem_write(CALLER * 16 + site + 2 + open_at, bytes((0xF4,)))
        known_at = (self.DS - (0x4356 - 0x3800)) * 16 + 0x168 + who * 0x8A
        for rules in (game.RULE_KITS, 0):
            self.rules(rules)
            for cls, kit in self.SHINOBI_CASES:
                kid = self.kit_of(cls, kit, rules)
                for level, known in ((5, ()), (6, ()), (6, (6, 2, 9, 4, 11)), (8, (6, 2, 9, 4, 11)),
                                     (10, tuple(n for n, _ in kits.SHINOBI_SPELLS))):
                    for ax in (0, 3):
                        with self.subTest(rules=rules, cls=cls, kit=kit, level=level, known=known, ax=ax):
                            self.creature(cls, kit, index=who, level=level)
                            self.mu.mem_write(known_at, bytes(1 if n in known else 0 for n in range(0x8A)))
                            self.mu.mem_write(SS * 16 + BP - 2, b"\xff\xff")
                            for name, value in dict(cs=CALLER, ds=self.DS, ss=SS, esp=0x7FC, ebp=BP, eflags=IF | 2,
                                                    eax=ax, ebx=0x2222, ecx=0x3333, esi=who, edi=0, es=0x6666).items():
                                self.mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
                            self.mu.emu_start(CALLER * 16 + site, 0, count=5000)
                            ip = self.mu.reg_read(r.UC_X86_REG_IP)
                            opens = kid == kits.SHINOBI and bool(
                                kits.pick_list(kid, known.__contains__, kits.shinobi_pick_level(level)))
                            want_ax = (0 if kid == kits.SHINOBI else ax)
                            self.assertEqual(ip, site + 2 + open_at + 1 if opens else site + 6)
                            self.assertEqual(self.mu.reg_read(r.UC_X86_REG_DI), 1 if opens else 0)
                            if not opens:
                                self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), want_ax)
                                flags = self.mu.reg_read(r.UC_X86_REG_EFLAGS)
                                self.assertEqual((bool(flags & 0x40), bool(flags & 0x800)), (want_ax == 0, False))
                            self.assertEqual(struct.unpack("<H", self.mu.mem_read(SS * 16 + BP - 2, 2))[0], ax)
                            self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_BX, r.UC_X86_REG_CX, r.UC_X86_REG_SI,
                                                                            r.UC_X86_REG_ES, r.UC_X86_REG_SP, r.UC_X86_REG_BP)],
                                             [0x2222, 0x3333, who, 0x6666, 0x7FC, BP])
        self.assertEqual([kits.shinobi_pick_level(n) for n in (5, 6, 7, 8, 9, 10)], [0, 1, 1, 2, 2, 3])

    def test_scroll_learn(self):
        """PROBE_SCROLL_LEARN: AX and ZF as "or ax,ax", but a Shinobi learns no scroll (AX 0, ZF)."""
        from dscompanion import kits
        from dscompanion.gamepatch import VEC_SCROLL_LEARN
        seg, who = 0x8700, 5
        site = 0x400 + (VEC_SCROLL_LEARN & 0x1F) * 0x10
        self.mu.mem_write(CALLER * 16 + site + 2 + (0x8B6C2 - 0x8B6D5), struct.pack("<H", seg))
        self.mu.mem_write(seg * 16 + 0x25B, struct.pack("<H", who))
        for rules in (game.RULE_KITS, 0):
            self.rules(rules)
            for cls, kit in self.SHINOBI_CASES:
                kid = self.kit_of(cls, kit, rules)
                self.creature(cls, kit, index=who, level=8)
                for ax in (0, 1):
                    with self.subTest(rules=rules, cls=cls, kit=kit, ax=ax):
                        self.run_vector(VEC_SCROLL_LEARN, 2, eax=ax, ebx=0x2222, esi=0x4444, es=0x6666)
                        want = 0 if kid == kits.SHINOBI else ax
                        self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), want)
                        self.assertEqual(bool(self.mu.reg_read(r.UC_X86_REG_EFLAGS) & 0x40), not want)
                        self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_BX, r.UC_X86_REG_SI,
                                                                        r.UC_X86_REG_ES)], [0x2222, 0x4444, 0x6666])

    # spell levels as the game's table has them (wizard spells 1-68)
    WIZARD_LEVELS = {s: 1 if s <= 11 else 2 if s <= 24 else 3 if s <= 39 else 4 if s <= 55 else 5 for s in range(1, 69)}

    def int_setup(self, who, intelligence, known):
        """Party member WHO a preserver of INT INTELLIGENCE knowing the spells KNOWN; the game's
        spell levels; the rule for INT on."""
        self.rules(game.RULE_INT_LEARN)
        self.creature(11, 0, index=who, level=5)
        self.mu.mem_write(self.CREATURES * 16 + who * 0x3A + 0x25, bytes((intelligence,)))
        levels = ((self.DS + 0x3FB9 - 0x4356) & 0xFFFF) * 16 + 0x19C
        for spell, level in self.WIZARD_LEVELS.items():
            self.mu.mem_write(levels + spell * 7, bytes((level,)))
        known_at = (self.DS - (0x4356 - 0x3800)) * 16 + 0x168 + who * 0x8A
        self.mu.mem_write(known_at, bytes(1 if n in known else 0 for n in range(0x8A)))
        return known_at

    def said(self, vector, site):
        """INT VECTOR (a message probe) run from SITE: the far pointer it leaves pushed, the text."""
        install = self.image.find(bytes((0xB8, vector, 0x25, 0xBA)))
        self.mu.mem_write(vector * 4, struct.pack("<HH", struct.unpack_from("<H", self.image, install + 4)[0], TSR))
        if not getattr(self, "hooked", False):
            self.mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
            self.hooked = True
        self.mu.mem_write(CALLER * 16 + site, bytes((0xCD, vector, 0x90, 0x90, 0xF4)))
        for name, value in dict(cs=CALLER, ds=self.DS, ss=SS, esp=0x7FC, ebp=BP, eflags=IF | 2, eax=0x1111).items():
            self.mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        self.mu.emu_start(CALLER * 16 + site, CALLER * 16 + site + 4, count=500)
        self.assertEqual((self.mu.reg_read(r.UC_X86_REG_SP), self.mu.reg_read(r.UC_X86_REG_AX)), (0x7F8, 0x1111))
        off, seg = struct.unpack("<HH", self.mu.mem_read(SS * 16 + 0x7F8, 4))
        text = bytes(self.mu.mem_read(seg * 16 + off, 40)).split(b"\0")[0] if seg == TSR else b""
        return seg, off, text

    def test_int_learn(self):
        """PROBE_SCROLL_LEARN with the rule for INT (intlearn.py): a preserver's spell level full
        for its INT refuses the scroll (AX 0; PROBE_LEARN_REFUSED's TOO MANY..., the scroll kept);
        else a d100 against INT's chance, a failure letting the game teach it and use the scroll up,
        then PROBE_LEARN_SAID taking it back with YOU FAIL...; the try told in the header (+272).
        Without the rule, or a priest spell, the game's own (its messages pushed as they were)."""
        from dscompanion import intlearn
        from dscompanion.gamepatch import VEC_SCROLL_LEARN, VEC_LEARN_SAID, VEC_LEARN_REFUSED
        seg, who = 0x8700, 2
        site = 0x400 + (VEC_SCROLL_LEARN & 0x1F) * 0x10
        self.mu.mem_write(CALLER * 16 + site + 2 + (0x8B6C2 - 0x8B6D5), struct.pack("<H", seg))
        self.mu.mem_write(seg * 16 + 0x25B, struct.pack("<H", who))
        hdr = self.hdr
        def learn(spell, ax=1):
            self.mu.mem_write(SS * 16 + BP - 3, bytes((spell,)))
            before = struct.unpack("<H", self.mu.mem_read(hdr + 272, 2))[0]
            self.run_vector(VEC_SCROLL_LEARN, 2, eax=ax, ebx=0x2222, esi=0x4444, es=0x6666, edx=0x5555)
            self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_BX, r.UC_X86_REG_SI, r.UC_X86_REG_ES,
                                                            r.UC_X86_REG_DX)], [0x2222, 0x4444, 0x6666, 0x5555])
            ax = self.mu.reg_read(r.UC_X86_REG_AX)
            self.assertEqual(bool(self.mu.reg_read(r.UC_X86_REG_EFLAGS) & 0x40), not ax)
            seq, *told = struct.unpack("<H6B", self.mu.mem_read(hdr + 272, 8))
            return ax, (told if seq != before else None)
        first = [s for s in range(1, 12)]
        # INT 9: 6 1st-level spells at most, 35%
        known_at = self.int_setup(who, 9, first[:6])
        ax, told = learn(8)
        self.assertEqual((ax, told), (0, [who, 8, 9, 35, 6, intlearn.FULL]))
        self.assertEqual(self.said(VEC_LEARN_REFUSED, 0x680)[2], b"TOO MANY SPELLS OF THAT LEVEL")
        self.assertEqual(self.said(VEC_LEARN_REFUSED, 0x690)[:2], (self.DS, 0x3405))  # (once only)
        ax, told = learn(12)  # (a 2nd-level spell: room)
        self.assertEqual(told[:4], [who, 12, 9, 35])
        results = set()
        for n in range(40):
            self.int_setup(who, 9, first[:5])
            ax, told = learn(8)
            roll, result = told[4], told[5]
            self.assertTrue(1 <= roll <= 100)
            self.assertEqual(result, intlearn.LEARNT if roll <= 35 else intlearn.FAILED)
            self.assertEqual(ax, 1)
            self.mu.mem_write(known_at + 8, b"\1")  # (the game teaches it)
            seg_, off, text = self.said(VEC_LEARN_SAID, 0x6A0 + (n % 2) * 0x10)
            if result == intlearn.FAILED:
                self.assertEqual(text, b"YOU FAIL TO LEARN THE SPELL")
                self.assertEqual(self.mu.mem_read(known_at + 8, 1)[0] & 0x0F, 0)
            else:
                self.assertEqual((seg_, off), (self.DS, 0x33F1))
                self.assertEqual(self.mu.mem_read(known_at + 8, 1)[0], 1)
            results.add(result)
        self.assertEqual(results, {intlearn.LEARNT, intlearn.FAILED})
        # INT 19 and more: no most, 95%
        self.int_setup(who, 19, first[:10])
        self.assertEqual(learn(11)[1][:4], [who, 11, 19, 95])
        # the game's own: the rule off, a priest spell, or a spell it knows (AX 0 already)
        self.int_setup(who, 9, first[:6])
        self.rules(0)
        self.assertEqual(learn(8), (1, None))
        self.rules(game.RULE_INT_LEARN)
        self.assertEqual(learn(80), (1, None))
        self.assertEqual(learn(8, ax=0), (0, None))
        self.assertEqual([intlearn.chance(i) for i in (3, 9, 12, 18, 19, 24, 25, 30)], [35, 35, 50, 85, 95, 100, 100, 100])
        self.assertEqual([intlearn.most(i) for i in (9, 13, 17, 18, 19)], [6, 9, 14, 18, None])

    def test_int_pick(self):
        """CHOOSE A SPELL with the rule for INT: PROBE_PICK_LIST leaves out the spells of a level the
        preserver knows its INT's most of; PROBE_PICK_ANY doesn't open it (AX 0) when no spell is
        left to learn at a level on offer that isn't full."""
        from dscompanion.gamepatch import VEC_PICK_LIST, VEC_PICK_ANY
        seg, who = 0x8700, 2
        site = 0x400 + (VEC_PICK_LIST & 0x1F) * 0x10
        self.mu.mem_write(CALLER * 16 + site + 2 + (0x8562E - 0x85641), struct.pack("<H", seg))
        self.mu.mem_write(seg * 16 + 0x25B, struct.pack("<H", who))
        first = list(range(1, 12))
        for rules, known, want in ((game.RULE_INT_LEARN, first[:6], [12, 13]), (game.RULE_INT_LEARN, first[:5], [7, 8, 12, 13]),
                                   (0, first[:6], [7, 8, 12, 13])):
            with self.subTest(rules=rules, known=known):
                self.int_setup(who, 9, known)
                self.rules(rules)
                self.picker_sheet(11, 0, 5)
                self.mu.mem_write(self.DS * 16 + 0x4AEC, bytes((2,)))
                self.mu.mem_write(seg * 16 + 7, struct.pack("<4H", 7, 8, 12, 13))
                self.run_vector(VEC_PICK_LIST, 2, eax=4, ebx=0x2222, ecx=0x3333, esi=0x4444, es=0x6666)
                di = self.mu.reg_read(r.UC_X86_REG_DI)
                self.assertEqual(list(struct.unpack("<%dH" % di, self.mu.mem_read(seg * 16 + 7, 2 * di))), want)
                self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_AX, r.UC_X86_REG_BX, r.UC_X86_REG_CX,
                                                                r.UC_X86_REG_SI, r.UC_X86_REG_ES)],
                                 [4, 0x2222, 0x3333, 0x4444, 0x6666])
        # PROBE_PICK_ANY: preserver level 1 (1st-level spells on offer), INT 9
        at = self.image.find(bytes((0xB8, VEC_PICK_ANY, 0x25, 0xBA)))
        self.mu.mem_write(VEC_PICK_ANY * 4, struct.pack("<HH", struct.unpack_from("<H", self.image, at + 4)[0], TSR))
        for rules, known, level, opens in ((game.RULE_INT_LEARN, first[:6], 1, False), (game.RULE_INT_LEARN, first[:5], 1, True),
                                           (game.RULE_INT_LEARN, first[:6], 3, True), (0, first[:6], 1, True)):
            with self.subTest(rules=rules, known=known, level=level):
                self.int_setup(who, 9, known)
                self.rules(rules)
                self.creature(11, 0, index=who, level=level)
                self.mu.mem_write(self.CREATURES * 16 + who * 0x3A + 0x25, bytes((9,)))
                self.run_vector(VEC_PICK_ANY, 5, eax=level, esi=who, ebx=0x2222, edi=0)
                self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), level if opens else 0)
                self.assertEqual(bool(self.mu.reg_read(r.UC_X86_REG_EFLAGS) & 0x40), not opens)

    def test_kit_at(self):
        """KIT_AT: the kit of the class at place DI (kitpages.kit_at), two bits a class in KIT_BYTE."""
        from dscompanion import kitpages
        self.rules(game.RULE_KITS)
        cases = [((c, 0, 0), (1, 0, 0), kit, 1) for c in range(1, 18) for kit in (0, 1, 2, 3, 4, 0xFF)]
        cases += [((9, 12, 0), (1, 1, 0), 1, 1), ((9, 11, 0), (4, 3, 0), 0b0110, 1), ((9, 11, 0), (4, 3, 0), 0b0110, 2),
                  ((12, 9, 11), (5, 4, 3), 0b111001, 1), ((12, 9, 11), (5, 4, 3), 0b111001, 1)]
        for classes, levels, kit, race in cases:
            for place in range(3):
                with self.subTest(classes=classes, kit=kit, place=place):
                    sheet = bytearray(game.SHEET_SIZE)
                    sheet[0x18], sheet[kitpages.KIT_BYTE] = race, kit
                    sheet[0x21:0x24], sheet[0x24:0x27] = bytes(classes), bytes(levels)
                    self.mu.mem_write(self.SHEET * 16, bytes(sheet))
                    self.call(rb"\x51\x57\x30\xc9\x2e\xf7\x06..\x01\x00", es=self.SHEET, ebx=0, edi=place)
                    self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AL), kitpages.kit_at(bytes(sheet), place))
                    self.assertEqual(self.mu.reg_read(r.UC_X86_REG_DI), place)

    def test_kit_is(self):
        """KIT_IS and KIT_HAS: whether the sheet has kit AL, awake (kitpages.kit_ids) or at all, its
        class's place in KIT_WHERE (KIT_LEVEL's), AL kept."""
        from dscompanion import kitpages, kits
        self.rules(game.RULE_KITS)
        import re
        at = re.search(rb"\x56\xbe\x01\x00\xeb", self.image, re.S).start()  # (KIT_IS; KIT_HAS after it)
        where = struct.unpack_from("<H", self.image, re.search(rb"\x2e\x89\x3e(..)\x38\xc0", self.image, re.S).start() + 3)[0]
        # (a Myrmidon fighter 3, then a Scholar preserver 5 (fighter awake), then a psionicist 4 (fighter
        # awake, the preserver asleep))
        for classes, levels, kit in (((11, 9, 0), (5, 3, 0), 0b0101), ((12, 11, 9), (4, 5, 3), 0b000101),
                                     ((9, 0, 0), (3, 0, 0), 1)):
            sheet = bytearray(game.SHEET_SIZE)
            sheet[0x18], sheet[kitpages.KIT_BYTE] = 1, kit
            sheet[0x21:0x24], sheet[0x24:0x27] = bytes(classes), bytes(levels)
            self.mu.mem_write(self.SHEET * 16, bytes(sheet))
            for kid in sorted(kitpages.KIT_IDS.values()):
                for has, start in ((False, at), (True, at + 6)):
                    with self.subTest(classes=classes, kid=kid, has=has):
                        self.mu.mem_write(TSR * 16 + 0xFFF0, b"\x90")
                        mu = self.mu
                        mu.mem_write(SS * 16 + 0x7FC, struct.pack("<H", 0xFFF0))
                        for name, value in dict(cs=TSR, ds=self.DS, ss=SS, esp=0x7FC, es=self.SHEET, ebx=0,
                                                eax=0x1200 | kid).items():
                            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
                        mu.emu_start(TSR * 16 + start, TSR * 16 + 0xFFF0)
                        found = [k for k, _, awake in kitpages.kits_of(bytes(sheet)) if has or awake]
                        self.assertEqual(not mu.reg_read(r.UC_X86_REG_EFLAGS) & 0x40, kid not in found)
                        self.assertEqual(mu.reg_read(r.UC_X86_REG_AX), 0x1200 | kid)
                        if kid in found:
                            place, = struct.unpack("<H", mu.mem_read(TSR * 16 + where, 2))
                            self.assertEqual(place, kitpages.kit_place_of(bytes(sheet), kid))
        self.assertEqual(kitpages.KIT_IDS["Ravager"], 15)
        self.assertEqual(kitpages.KIT_IDS["Shinobi"], 35)


@unittest.skipIf(Uc is None, "unicorn is not installed")
class AdndTablesTests(unittest.TestCase):
    """RULE_HI_TABLES (game.RULE_ADND_TABLES) against tables.py: PROBE_XP (the XP the next level
    needs), PROBE_PRIEST_THAC0 (what a class group takes off 20) and PROBE_ADND_SLOTS (a class's
    slots at a spell level); with the rule off, the game's."""
    DS, TABLE, PAIR = 0x9000, 0x8000, 0x700
    RULES, RULES_HI = 170, 270

    def setUp(self):
        self.image = load_image()
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        self.hdr = TSR * 16 + self.image.find(HDR_SIG)

    def rules(self, on):
        self.mu.mem_write(self.hdr + self.RULES_HI, struct.pack("<H", 8 if on else 0))

    def run_vector(self, vector, code_len, stack=b"", **regs):
        """INT VECTOR and its NOPs (CODE_LEN in all), STACK the words on the stack at the INT."""
        at = self.image.find(bytes((0xB8, vector, 0x25, 0xBA)))
        self.assertGreater(at, 0)
        self.mu.mem_write(vector * 4, struct.pack("<HH", struct.unpack_from("<H", self.image, at + 4)[0], TSR))
        site = 0x400 + (vector & 0x1F) * 0x10  # (one for each vector: the emulator keeps code it has seen)
        self.mu.mem_write(CALLER * 16 + site, bytes((0xCD, vector)) + b"\x90" * (code_len - 2))
        sp = 0x7FC - len(stack)
        self.mu.mem_write(SS * 16 + sp, stack)
        for name, value in dict(cs=CALLER, ds=self.DS, ss=SS, esp=sp, ebp=BP, eflags=IF | 2, **regs).items():
            self.mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        self.mu.emu_start(CALLER * 16 + site, CALLER * 16 + site + code_len, count=20000)
        self.assertEqual((self.mu.reg_read(r.UC_X86_REG_IP), self.mu.reg_read(r.UC_X86_REG_SP)),
                         (site + code_len, sp))

    def test_xp(self):
        """PROBE_XP: the table's word (BX the row x 40 + the level x 2) x 100, or AD&D's."""
        from dscompanion import tables
        from dscompanion.gamepatch import VEC_XP
        for on in (False, True):
            self.rules(on)
            for row, name in enumerate(tables.ROWS, 1):
                for level in (0, 1, 2, 5, 9, 10):
                    with self.subTest(on=on, row=name, level=level):
                        bx = row * 40 + level * 2
                        self.mu.mem_write(self.TABLE * 16 + bx + 0x27C, struct.pack("<H", 123))
                        self.run_vector(VEC_XP, 4, eax=0xDEAD0000 | 123, ebx=bx, ecx=0x3333, edx=0x4444,
                                        esi=0x5555, es=self.TABLE)
                        want = tables.xp_needed(name, level) if on else 12300
                        self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_EAX, r.UC_X86_REG_BX,
                                                                        r.UC_X86_REG_CX, r.UC_X86_REG_DX,
                                                                        r.UC_X86_REG_SI)],
                                         [want, bx, 0x3333, 0x4444, 0x5555])

    def test_priest_thac0(self):
        """PROBE_PRIEST_THAC0: [BP-2] the AX given, but a priest's (CX 0, its level at [BP-0Ah])
        AD&D's with the rule: 2 for every 3 levels."""
        from dscompanion import tables
        from dscompanion.gamepatch import VEC_PRIEST_THAC0
        for on in (False, True):
            self.rules(on)
            for group in range(4):
                for level in range(1, 11):
                    with self.subTest(on=on, group=group, level=level):
                        self.mu.mem_write(SS * 16 + BP - 0x0A + group * 2, bytes((level, 0)))
                        self.run_vector(VEC_PRIEST_THAC0, 3, eax=77, ebx=0x2222, ecx=group, edx=0x4444,
                                        esi=0x5555)
                        got, = struct.unpack("<H", self.mu.mem_read(SS * 16 + BP - 2, 2))
                        want = 20 - tables.priest_thac0(level) if on and group == 0 else 77
                        self.assertEqual(got, want)
                        self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_BX, r.UC_X86_REG_CX,
                                                                        r.UC_X86_REG_DX, r.UC_X86_REG_SI)],
                                         [0x2222, group, 0x4444, 0x5555])

    # the game's routine, a stand-in: AX = the level x 100 + WIS + the spell level x 1000, BX and CX spoilt
    STUB = bytes.fromhex("55" "89e5" "8b5e08" "368a07" "b400" "6bc064" "360fb64f01" "01c8"
                         "8b4e0a" "69c9e803" "01c8" "bbffff" "b9ffff" "5d" "cb")

    def test_slots(self):
        """PROBE_ADND_SLOTS: the routine's count; with the rule, for a cleric, druid or preserver,
        AD&D's for the level and the routine's for WIS alone (asked with the level 0, then the
        level put back)."""
        from dscompanion import tables
        from dscompanion.gamepatch import VEC_ADND_SLOTS
        self.mu.mem_write(CALLER * 16 + 0x400 + (VEC_ADND_SLOTS & 0x1F) * 0x10 + 2 + 0x5E4C2 - 0x5E242, self.STUB)
        for on in (False, True):
            self.rules(on)
            for cls in (1, 4, 5, 8, 11, 13, 9):
                for level in (1, 3, 9, 10):
                    for spell in range(1, 6):
                        with self.subTest(on=on, cls=cls, level=level, spell=spell):
                            self.mu.mem_write(SS * 16 + self.PAIR, bytes((level, 17)))
                            stack = struct.pack("<HHH", cls, self.PAIR, spell)
                            self.run_vector(VEC_ADND_SLOTS, 5, stack=stack, eax=0x1111, ebx=0x2222,
                                            ecx=0x3333, esi=0x5555, edi=0x6666)
                            ours = tables.slots(cls, level, spell) if on else None
                            want = ours + 17 + spell * 1000 if ours is not None else level * 100 + 17 + spell * 1000
                            self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), want)
                            self.assertEqual(bytes(self.mu.mem_read(SS * 16 + self.PAIR, 2)), bytes((level, 17)))
                            self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_BX, r.UC_X86_REG_CX,
                                                                            r.UC_X86_REG_SI, r.UC_X86_REG_DI,
                                                                            r.UC_X86_REG_BP)],
                                             [0x2222, 0x3333, 0x5555, 0x6666, BP])


@unittest.skipIf(Uc is None, "unicorn is not installed")
class ChaPriceTests(AdndTablesTests):
    """RULE_HI_CHA_PRICES (game.RULE_CHA_PRICES) against prices.py: PROBE_PRICE (CX the price a
    shop asks, ES:BX+6 the item's) and PROBE_PRICE_EAX (EAX, sign-extended, as the game reads it),
    by the leader's CHA (the party member at DS:4979h, its creature record's +27h)."""
    test_xp = test_priest_thac0 = test_slots = None  # (AdndTablesTests' own)
    ITEM, CREATURES = 0x8000, 0x8100

    def setUp(self):
        super().setUp()
        self.mu.mem_write(self.DS * 16 + 0x1665, struct.pack("<HH", 0, self.CREATURES))

    def leader(self, member, cha, on=True):
        self.mu.mem_write(self.hdr + self.RULES_HI, struct.pack("<H", 16 if on else 0))
        self.mu.mem_write(self.DS * 16 + 0x4979, struct.pack("<H", member))
        self.mu.mem_write(self.CREATURES * 16 + member * 0x3A + 0x27, bytes((cha,)))

    def test_prices(self):
        from dscompanion import prices
        from dscompanion.gamepatch import VEC_PRICE, VEC_PRICE_EAX
        for on in (False, True):
            for member, cha in ((0, 15), (1, 16), (2, 18), (3, 19), (0, 20), (2, 25), (5, 25)):
                for value in (0, 1, 3, 10, 1000, 9999, 30000, 43500):
                    with self.subTest(on=on, member=member, cha=cha, value=value):
                        self.leader(member, cha, on)
                        self.mu.mem_write(self.ITEM * 16 + 0x20 + 6, struct.pack("<H", value))
                        want = prices.price(value, cha) if on and member < 4 else value
                        self.run_vector(VEC_PRICE, 4, es=self.ITEM, ebx=0x20, ecx=0x3333, eax=0x1111,
                                        edx=0x4444)
                        self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_CX, r.UC_X86_REG_AX,
                                                                        r.UC_X86_REG_BX, r.UC_X86_REG_DX,
                                                                        r.UC_X86_REG_ES)],
                                         [want, 0x1111, 0x20, 0x4444, self.ITEM])
                        self.run_vector(VEC_PRICE_EAX, 6, es=self.ITEM, ebx=0x20, ecx=0x3333, eax=0xDEADBEEF)
                        self.assertEqual(self.mu.reg_read(r.UC_X86_REG_EAX), want - 0x10000 & 0xFFFFFFFF
                                         if want >= 0x8000 else want)
                        self.assertEqual(self.mu.reg_read(r.UC_X86_REG_CX), 0x3333)


@unittest.skipIf(Uc is None, "unicorn is not installed")
class RolledTests(AdndTablesTests):
    """RULE_HI_ROLLED (game.RULE_ROLLED): the creation screen's sites sharing VEC_CR_SPELLS, the
    INT followed by the site's number. RL_ROLL keeps the die's total as a loop sets CHR, RL_SCORE
    keeps a click's raise to the points to spare, RL_HP leaves the hit points as they are, and
    RL_SUM draws "SUM:" and the totals; with the rule off, the game's."""
    test_xp = test_priest_thac0 = test_slots = None  # (AdndTablesTests' own)
    CREATURE, WINDOW, LOG = 0x8000, 0x12345678, 0x6800
    # the game's text routine, a stand-in: x, y and the text (its far pointer, the last argument)
    # added to a log at LOG:2, LOG:0 where the next goes
    TEXT = bytes.fromhex("5589e51e560657c5761eb800688ec0268b3e00008b460aab8b460cabacaa08c075fa26893e0000"
                         "5f075e1f5dcb")

    def setUp(self):
        super().setUp()
        self.mu.mem_write(self.DS * 16 + 0x11A0, struct.pack("<HH", 0, self.CREATURE))
        self.mu.mem_write(self.DS * 16 + 0x11A4, struct.pack("<I", self.WINDOW))
        self.mu.mem_write(self.DS * 16 + 0xF62, struct.pack("<4h", 33, 137, 77, 185))  # (the scores' box)
        self.mu.mem_write((self.DS + 0x2B7A - 0x4356) * 16 + 0x16D, self.TEXT)

    def rules(self, on):
        self.mu.mem_write(self.hdr + self.RULES_HI, struct.pack("<H", 32 if on else 0))

    def scores(self, *values):
        self.mu.mem_write(self.CREATURE * 16 + 0x22, bytes(values))

    def run_site(self, site, code_len, stack=b"", popped=0, **regs):
        """INT VEC_CR_SPELLS, the site's number and NOPs (CODE_LEN in all); STACK the words on the
        stack at the INT, POPPED bytes of it gone after."""
        from dscompanion.gamepatch import VEC_CR_SPELLS
        at = self.image.find(bytes((0xB8, VEC_CR_SPELLS, 0x25, 0xBA)))
        self.mu.mem_write(VEC_CR_SPELLS * 4, struct.pack("<HH", struct.unpack_from("<H", self.image, at + 4)[0], TSR))
        ip = 0x600 + site * 0x10  # (one for each site: the emulator keeps code it has seen)
        self.mu.mem_write(CALLER * 16 + ip, bytes((0xCD, VEC_CR_SPELLS, site)) + b"\x90" * (code_len - 3))
        sp = 0x7FC - len(stack)
        self.mu.mem_write(SS * 16 + sp, stack)
        for name, value in dict(cs=CALLER, ds=self.DS, ss=SS, esp=sp, ebp=BP, eflags=IF | 2, **regs).items():
            self.mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        self.mu.emu_start(CALLER * 16 + ip, CALLER * 16 + ip + code_len, count=20000)
        self.assertEqual((self.mu.reg_read(r.UC_X86_REG_IP), self.mu.reg_read(r.UC_X86_REG_SP)),
                         (ip + code_len, sp + popped))

    def roll(self, last, di=1):
        """RL_ROLL: CHR (SI 5) set to LAST, DI the die's flag."""
        from dscompanion.gamepatch import RL_ROLL
        self.run_site(RL_ROLL, 4, es=self.CREATURE, ebx=5, esi=5, edi=di, eax=0x1100 | last)
        self.assertEqual(self.mu.mem_read(self.CREATURE * 16 + 0x27, 1)[0], last)

    def click(self, score, value):
        """RL_SCORE: AL the value a click on SCORE would set ([BP-2] the game's)."""
        from dscompanion.gamepatch import RL_SCORE
        self.mu.mem_write(SS * 16 + BP - 2, struct.pack("<H", value))
        self.run_site(RL_SCORE, 3, es=self.CREATURE, ebx=score, esi=score, eax=0x2200, ecx=0x3333,
                      edx=0x4444)
        self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_AH, r.UC_X86_REG_BX, r.UC_X86_REG_CX,
                                                        r.UC_X86_REG_DX, r.UC_X86_REG_SI)],
                         [0x22, score, 0x3333, 0x4444, score])
        return self.mu.reg_read(r.UC_X86_REG_AL)

    def test_scores(self):
        for on in (False, True):
            with self.subTest(on=on):
                self.rules(on)
                self.scores(17, 14, 17, 18, 19, 0)
                self.roll(17)  # the die: 102
                self.assertEqual(self.click(0, 18), 17 if on else 18)  # nothing to spare
                self.assertEqual(self.click(0, 16), 16)  # lowering: always
                self.scores(17, 12, 17, 18, 19, 17)  # DEX lowered by 2
                self.assertEqual(self.click(0, 18), 18)
                self.assertEqual(self.click(0, 22), 19 if on else 22)  # as far as the 2 to spare
                self.assertEqual(self.click(3, 3), 3)  # round from the least: down
                self.scores(17, 12, 17, 18, 19, 0)
                self.roll(15)  # rolled again: 98
                self.assertEqual(self.click(1, 13), 12 if on else 13)
                self.scores(17, 12, 15, 18, 19, 0)
                self.roll(15, di=0)  # kept, not rolled (96): the die's 98 stays
                self.assertEqual(self.click(1, 14), 14)
                self.assertEqual(self.click(1, 15), 14 if on else 15)
                self.scores(18, 14, 17, 18, 19, 0)
                self.roll(18, di=0)  # raised to a new class's least (104): the most is 104
                self.assertEqual(self.click(1, 15), 14 if on else 15)
                self.scores(18, 13, 17, 18, 19, 18)
                self.assertEqual(self.click(1, 14), 14)

    def test_hit_points(self):
        from dscompanion.gamepatch import RL_HP
        for on in (False, True):
            for step in (1, -1):
                with self.subTest(on=on, step=step):
                    self.rules(on)
                    self.mu.mem_write(SS * 16 + BP - 2, struct.pack("<h", step))
                    self.run_site(RL_HP, 3, eax=9, ebx=0x2222)
                    self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), 9 if on else 9 + step & 0xFFFF)

    def drawn(self):
        """The text routine's calls since the last: (x, y, text) each."""
        mem = self.mu.mem_read(self.LOG * 16, 0x100)
        end, at, out = struct.unpack_from("<H", mem)[0], 2, []
        while at < end:
            x, y = struct.unpack_from("<hh", mem, at)
            text = bytes(mem[at + 4:mem.index(0, at + 4)])
            out.append((x, y, text.decode()))
            at += 4 + len(text) + 1
        self.mu.mem_write(self.LOG * 16, struct.pack("<H", 2))
        return out

    def test_sum(self):
        from dscompanion.gamepatch import RL_SUM
        self.mu.mem_write(self.LOG * 16, struct.pack("<H", 2))
        for on in (False, True):
            with self.subTest(on=on):
                self.rules(on)
                self.scores(17, 14, 17, 18, 19, 0)
                self.roll(17)
                self.scores(17, 12, 17, 18, 19, 17)
                self.run_site(RL_SUM, 3, stack=struct.pack("<HH", 0x1111, 0x2222), popped=4,
                              eax=0x1111, ebx=0x2222, esi=0x5555, edi=0x6666)
                self.assertEqual([self.mu.reg_read(x) for x in (r.UC_X86_REG_AX, r.UC_X86_REG_BX,
                                                                r.UC_X86_REG_SI, r.UC_X86_REG_DI,
                                                                r.UC_X86_REG_BP, r.UC_X86_REG_DS)],
                                 [0x1111, 0x2222, 0x5555, 0x6666, BP, self.DS])
                self.assertEqual(self.drawn(), [(10, 177, "SUM:"), (33, 177, "100/102")] if on else [])

    SHEET = 0x8800

    def test_con(self):
        """RL_CON: after a click on CON (RL_SCORE keeping the most hit points before it), the sheet's
        hit points move as far as the most did (ES:BX the sheet, as "les bx,[119Ch]" leaves it)."""
        from dscompanion.gamepatch import RL_CON
        self.mu.mem_write(self.DS * 16 + 0x119C, struct.pack("<HH", 0, self.SHEET))
        for on in (False, True):
            for before, after, hp in ((20, 23, 15), (23, 20, 18), (20, 20, 12)):
                with self.subTest(on=on, before=before, after=after):
                    self.rules(on)
                    self.scores(17, 14, 17, 18, 19, 17)
                    self.roll(17)
                    self.mu.mem_write(self.DS * 16 + 0x4996, struct.pack("<H", before))
                    self.click(2, 18)
                    self.mu.mem_write(self.DS * 16 + 0x4996, struct.pack("<H", after))
                    self.mu.mem_write(self.SHEET * 16 + 8, struct.pack("<H", hp))
                    self.run_site(RL_CON, 4, es=0, ebx=0, eax=0x1234)
                    self.assertEqual((self.mu.reg_read(r.UC_X86_REG_ES), self.mu.reg_read(r.UC_X86_REG_BX),
                                      self.mu.reg_read(r.UC_X86_REG_AX)), (self.SHEET, 0, 0x1234))
                    got, = struct.unpack("<H", self.mu.mem_read(self.SHEET * 16 + 8, 2))
                    self.assertEqual(got, hp + after - before if on else hp)

    def test_tries(self):
        """RL_TRY: AX (a 4d4) plus the word at DS:499Ah, the 4d4 kept for the dice log at the
        header's +282 (four for each ability, [BP+8], the try in DI) and +280 counted."""
        from dscompanion.gamepatch import RL_TRY
        self.mu.mem_write(self.DS * 16 + 0x499A, struct.pack("<H", 5))
        seq0, = struct.unpack("<H", self.mu.mem_read(self.hdr + 280, 2))
        for n, (ability, try_, roll) in enumerate(((0, 0, 7), (0, 3, 11), (5, 2, 16), (6, 0, 9), (2, 4, 9))):
            with self.subTest(ability=ability, try_=try_):
                self.mu.mem_write(SS * 16 + BP + 8, struct.pack("<H", ability))
                self.run_site(RL_TRY, 4, eax=roll, edi=try_, ebx=0x2222)
                self.assertEqual((self.mu.reg_read(r.UC_X86_REG_AX), self.mu.reg_read(r.UC_X86_REG_BX)),
                                 (roll + 5, 0x2222))
        tries = bytes(self.mu.mem_read(self.hdr + 282, 24))
        self.assertEqual((tries[0], tries[3], tries[22]), (7, 11, 16))
        self.assertEqual(struct.unpack("<H", self.mu.mem_read(self.hdr + 280, 2))[0], seq0 + 3)  # (not the two out of range)
