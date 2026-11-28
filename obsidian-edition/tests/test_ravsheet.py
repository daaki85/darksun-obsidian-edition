"""The mod's room in Wake of the Ravager's records (dsloader.ravager): the sound words' low bytes alone
(sound_3c, sound_3e, run in an emulated CPU with the game's code round them), so the transfer's kit and
second sphere can stay in +3Dh and +3Fh; and the sheet made 48h bytes (SHEET_SIZE) for the weapon specs
and the starting age's roll: each patch's shape run in an emulated CPU, the patched program scanned for
a 42h stride left (with DSUN_WOTR), DSCLOG2's NEW_SHEET (site 50) run, and the game folder's files
widened and narrowed (widen_files). The emulation needs unicorn (and nasm for DSCLOG2), else skipped."""

import os
import re
import shutil
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import dataitems, gamepatch, gff, ravager  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:
    Uc = None

WOTR = os.environ.get("DSUN_WOTR")
CODE, SHEET, STACK = 0x1000, 0x2000, 0x3000
PATCHES = {p.name: p for p in ravager.PATCHES}
# The game's code after each site (DSUN.EXE, image 6013Bh and 89862h): "jnz +3 / mov dx,62h" (a sound
# of 0 is 62h), and "jz +0Ah / mov al,[bp-4]" (the sound pushed, AH as the site left it)
AFTER_3C = bytes.fromhex("7503ba6200")
AFTER_3E = bytes.fromhex("740a8a46fc")


@unittest.skipIf(Uc is None, "needs unicorn")
class SoundWordTests(unittest.TestCase):
    def run_site(self, name: str, after: bytes, word: int, offset: int):
        """The site NAME (its replacement bytes) then AFTER, with ES:BX a sheet whose word at OFFSET
        is WORD; (AX, DX, [BP-4]) at the end."""
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        code = PATCHES[name].replacement + after + b"\x90" * 7 + b"\xf4"  # (the jz's +0Ah lands on the HLT)
        mu.mem_write(CODE * 16, code)
        sheet = bytearray(ravager.SHEET_SIZE)
        struct.pack_into("<H", sheet, offset, word)
        mu.mem_write(SHEET * 16 + 0x40, bytes(sheet))
        mu.mem_write(STACK * 16 + 0x100 - 4, b"\xaa\xaa")
        for reg, value in ((r.UC_X86_REG_ES, SHEET), (r.UC_X86_REG_BX, 0x40), (r.UC_X86_REG_SS, STACK),
                           (r.UC_X86_REG_BP, 0x100), (r.UC_X86_REG_SP, 0x80), (r.UC_X86_REG_AX, 0x1234),
                           (r.UC_X86_REG_DX, 0x5678), (r.UC_X86_REG_CS, CODE)):
            mu.reg_write(reg, value)
        mu.emu_start(CODE * 16, CODE * 16 + len(code) - 1)
        return (mu.reg_read(r.UC_X86_REG_AX), mu.reg_read(r.UC_X86_REG_DX),
                struct.unpack("<H", mu.mem_read(STACK * 16 + 0x100 - 4, 2))[0])

    def test_turn_sound(self):
        """+3Ch at a member's turn: the low byte, whatever the kit above it; 62h for 0."""
        for word, sound in ((0x0042, 0x42), (0x0342, 0x42), (0x8100, 0x62), (0x0100, 0x62), (0, 0x62),
                            (0xFFC8, 0xC8)):
            with self.subTest(word=hex(word)):
                ax, dx, _ = self.run_site("sound_3c", AFTER_3C, word, 0x3C)
                self.assertEqual(dx, sound)

    def test_second_sound(self):
        """+3Eh: its low byte kept in [BP-4] and pushed with AH 0; none played (the jz) for a low byte 0."""
        for word, low in ((0x0044, 0x44), (0x4744, 0x44), (0x0800, 0), (0, 0), (0xFF97, 0x97)):
            with self.subTest(word=hex(word)):
                ax, _, kept = self.run_site("sound_3e", AFTER_3E, word, 0x3E)
                self.assertEqual(kept, low)
                self.assertEqual(ax, low)  # (AL the sound, AH 0, as pushed; 0 when the jz skipped it)

    def test_same_length_and_bytes(self):
        for name in ("sound_3c", "sound_3e"):
            p = PATCHES[name]
            self.assertEqual(len(p.original), len(p.replacement))
            self.assertIn(b"\x26\x0a\x47", p.replacement)  # (or al,es:[bx+N])

    @unittest.skipUnless(WOTR, "DSUN_WOTR: the player's Wake of the Ravager folder")
    def test_in_the_program(self):
        """The originals are the program's, and the game's code after them is AFTER_*."""
        with open(os.path.join(WOTR, "DSUN.EXE"), "rb") as f:
            exe = f.read()
        for name, after in (("sound_3c", AFTER_3C), ("sound_3e", AFTER_3E)):
            p = PATCHES[name]
            self.assertEqual(exe[p.offset:p.offset + len(p.original)], p.original)
            end = p.offset + len(p.original)
            self.assertEqual(exe[end:end + len(after)], after)


def run_code(code: bytes, **regs):
    """CODE then a HLT in an emulated CPU (16-bit), registers REGS (ES 2000h, SS 3000h, SP 80h by
    default); the machine after it."""
    mu = Uc(UC_ARCH_X86, UC_MODE_16)
    mu.mem_map(0, 0x100000)
    mu.mem_write(CODE * 16, code + b"\xf4")
    values = dict(cs=CODE, es=SHEET, ss=STACK, sp=0x80)
    values.update(regs)
    for name, value in values.items():
        mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
    mu.emu_start(CODE * 16, CODE * 16 + len(code))
    return mu


@unittest.skipIf(Uc is None, "needs unicorn")
class SheetPatchShapeTests(unittest.TestCase):
    """Each kind of the 48h sheet's patches, its replacement run: the stride, the party's loop, the
    table's allocation, the record size, the record read; and the save's chunk size as data."""

    def test_strides(self):
        """imul ax,ax,48h and imul dx,dx,48h: sheet N's offset, each register its own."""
        kinds = {PATCHES["sheet_stride_%x" % at].replacement for at in ravager.SHEET_STRIDES}
        self.assertEqual(kinds, {bytes.fromhex("6bc048"), bytes.fromhex("6bd248")})
        for n in (0, 1, 4, 16):
            mu = run_code(bytes.fromhex("6bc048"), ax=n, dx=0x1234)
            self.assertEqual((mu.reg_read(r.UC_X86_REG_AX), mu.reg_read(r.UC_X86_REG_DX)), (n * 0x48, 0x1234))
            mu = run_code(bytes.fromhex("6bd248"), ax=0x1234, dx=n)
            self.assertEqual((mu.reg_read(r.UC_X86_REG_AX), mu.reg_read(r.UC_X86_REG_DX)), (0x1234, n * 0x48))

    def test_party_loop(self):
        mu = run_code(PATCHES["sheet_party_loop"].replacement, edi=0x90)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_DI), 0x90 + ravager.SHEET_SIZE)

    def test_table_allocation(self):
        """push dword 17 x 48h, the far heap's size argument."""
        mu = run_code(PATCHES["sheet_table"].replacement)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_SP), 0x80 - 4)
        self.assertEqual(struct.unpack("<I", mu.mem_read(STACK * 16 + 0x7C, 4))[0], 17 * ravager.SHEET_SIZE)

    def test_record_size(self):
        """The sheets' entry of 6D0h's record sizes (ES:616Dh) 48h, the others' untouched."""
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu = run_code(PATCHES["sheet_record_size"].replacement)
        self.assertEqual(struct.unpack("<3H", mu.mem_read(SHEET * 16 + 0x616B, 6)), (0, ravager.SHEET_SIZE, 0))

    def test_record_load(self):
        """push 48h: memcpy's length for a sheet record read into its slot."""
        mu = run_code(PATCHES["sheet_record_load"].replacement)
        self.assertEqual(struct.unpack("<H", mu.mem_read(STACK * 16 + 0x7E, 2))[0], ravager.SHEET_SIZE)

    def test_save_size(self):
        p = PATCHES["sheet_save_size"]
        self.assertEqual(struct.unpack("<I", p.original)[0], 17 * ravager.GAME_SHEET_SIZE)
        self.assertEqual(struct.unpack("<I", p.replacement)[0], ravager.SHEETS_COUNT * ravager.SHEET_SIZE)

    def test_summoned_sheet(self):
        """Sheet 4's fields by a constant offset (the summoned ally's): each write lands on sheet 4's
        field in the 48h table, none on the 42h table's place of it (sheet 3's or another of 4's)."""
        self.assertEqual(len(ravager.SHEET4_FIELDS), 5)
        for at, opcode, field, imm in ravager.SHEET4_FIELDS:
            p = PATCHES["sheet4_%x" % at]
            mu = run_code(p.replacement, ebx=0x40, eax=0xB1A7)
            table = mu.mem_read(SHEET * 16 + 0x40, 17 * ravager.SHEET_SIZE)
            want = {0x88: b"\xa7", 0x89: b"\xa7\xb1"}.get(opcode, imm)
            at48 = ravager.SUMMON_SHEET * ravager.SHEET_SIZE + field
            self.assertEqual(bytes(table[at48:at48 + len(want)]), want, p.name)
            self.assertEqual(bytes(table[:at48]) + bytes(table[at48 + len(want):]), bytes(len(table) - len(want)),
                             p.name)
            self.assertLess(field, ravager.GAME_SHEET_SIZE)

    def test_same_lengths(self):
        for p in ravager.PATCHES:
            if p.name.startswith("sheet_"):
                self.assertEqual(len(p.original), len(p.replacement), p.name)
        self.assertEqual(len(ravager.SHEET_STRIDES), 386)
        self.assertEqual(PATCHES["sheet_new_tail"].replacement, bytes((0xCD, ravager.VEC_SITE, 50)))


@unittest.skipUnless(WOTR, "DSUN_WOTR: the player's Wake of the Ravager folder")
class StrideScanTests(unittest.TestCase):
    """The patched program: no "imul r,r,42h" left before a load of the sheets' pointer, and no other
    sheet-sized constant but the template's three copies (kept 42h: ravager's sheet_new_tail)."""

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(WOTR, "DSUN.EXE"), "rb") as f:
            cls.exe = f.read()
        cls.patched = gamepatch.patched(cls.exe, patches=ravager.PATCHES, size=ravager.WOTR_SIZE)

    @staticmethod
    def strides(data: bytes, size: int):
        return [m.start() for m in re.finditer(rb"\x6b[\xc0-\xff]" + bytes((size,)), data)
                if m.start() >= 0x5200 and re.search(rb"\xc5\x19|\xc7\x19", data[m.start() + 3:m.start() + 16])]

    def test_no_42h_stride_left(self):
        self.assertEqual(self.strides(self.exe, 0x42), list(ravager.SHEET_STRIDES))
        self.assertEqual(self.strides(self.patched, 0x42), [])
        self.assertEqual(self.strides(self.patched, 0x48), list(ravager.SHEET_STRIDES))
        self.assertEqual(self.strides(self.exe, 0x48), [])  # (none of the game's own)
        # (nor any imul of 42h at all, register or memory, byte or word immediate)
        self.assertEqual(len(re.findall(rb"\x6b[\x00-\xff]\x42", self.patched[0x5200:])) -
                         len(re.findall(rb"\x6b[\x00-\xff]\x42", self.exe[0x5200:])), -386)

    @staticmethod
    def constant_offsets(data: bytes):
        """Every "les bx,[19C5h]" followed by ES:[BX+disp16] uses with no index added (the sheet a
        constant): (the use's file offset, disp16)."""
        imms = {0x88: 0, 0x89: 0, 0x8A: 0, 0x8B: 0, 0x38: 0, 0x39: 0, 0x3A: 0, 0x3B: 0, 0xFE: 0, 0xFF: 0,
                0xC6: 1, 0xC7: 2, 0x80: 1, 0x83: 1, 0x81: 2}
        found = []
        for m in re.finditer(rb"\xc4\x1e\xc5\x19", data):
            at = m.end()
            while data[at] == 0x26 and data[at + 1] in imms and data[at + 2] & 0xC7 == 0x87:
                found.append((at, struct.unpack_from("<H", data, at + 3)[0]))
                at += 5 + imms[data[at + 1]]
        return found

    def test_no_constant_sheet_left(self):
        """The program's sheet uses by a constant offset are sheet 4's five (SHEET4_FIELDS), each made
        4 x 48h + its field; every other use after a load of the pointer is a field of sheet 0."""
        old = [(at, d) for at, d in self.constant_offsets(self.exe) if d >= ravager.GAME_SHEET_SIZE]
        fields = [(at, ravager.SUMMON_SHEET * ravager.GAME_SHEET_SIZE + field)
                  for at, _, field, _ in ravager.SHEET4_FIELDS]
        self.assertEqual(old, fields)
        new = [(at, d) for at, d in self.constant_offsets(self.patched) if d >= ravager.GAME_SHEET_SIZE]
        self.assertEqual(new, [(at, ravager.SUMMON_SHEET * ravager.SHEET_SIZE + field)
                               for at, _, field, _ in ravager.SHEET4_FIELDS])

    def test_sizes_left(self):
        """push 42h for a memcpy: the template's three alone (69C67h's sheet a far argument); the
        table's 462h gone."""
        left = []
        for m in re.finditer(rb"\x6a\x42", self.patched[0x5200:]):
            at = m.start() + 0x5200
            if b"\x9a\x5a\x3f\x00\x00" in self.patched[at:at + 40]:  # (a memcpy, 0:3F5Ah, of 42h)
                left.append(at - 0x5200)
        self.assertEqual(left, [0x6950B, 0x69560, 0x69C67])
        self.assertNotIn(bytes.fromhex("666862040000"), self.patched)
        table = 0x5200 + 0x3F38 * 16
        self.assertEqual(struct.unpack_from("<6I", self.patched, table),
                         (0x2E40, 0x390, 0x624, 0x540, 0x80A, 17 * ravager.SHEET_SIZE))

    def test_new_tail_site(self):
        """Site 50 replaces the "add sp,0Ah" right after the template's memcpy into the new sheet."""
        at = PATCHES["sheet_new_tail"].offset
        self.assertEqual(self.exe[at - 5:at], bytes.fromhex("9a5a3f0000"))  # (call 0:3F5Ah)
        self.assertEqual(self.exe[at - 0x1D:at - 0x1B], bytes.fromhex("6a42"))  # (push 42h: 69560h)


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class NewSheetTests(unittest.TestCase):
    """DSCLOG2's NEW_SHEET (site 50) as the game reaches it after the creation screen's memcpy: the
    new sheet's +42h..+47h cleared, the rest and the next sheet untouched, the stack as after "add sp,0Ah",
    every register kept."""

    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos", "dsclog2.asm"))
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]

    def test_clears_the_tail(self):
        tsr, sheets, ss = 0x1000, 0x6000, 0x4000
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(tsr * 16, self.image)
        mu.mem_write(tsr * 16 + 0xFFF0, b"\xf4")
        dst = 3 * ravager.SHEET_SIZE + 0x10  # (sheet 3, the table at 6000h:10h)
        mu.mem_write(sheets * 16, b"\xee" * 0x200)
        # the IRET frame (to the HLT), then memcpy's arguments: the destination, the template, 42h
        mu.mem_write(ss * 16 + 0x7FA, struct.pack("<HHH", 0xFFF0, tsr, 0x202) + struct.pack("<HHHHH", dst, sheets, 0x29, 0x360, 0x42))
        regs = dict(cs=tsr, ds=0x5000, es=0x7000, ss=ss, esp=0x7FA, ebp=0x600, eax=0x1111, ebx=0x2222,
                    ecx=0x3333, edx=0x4444, esi=0x5555, edi=0x6666, eflags=0x2)
        for name, value in regs.items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(tsr * 16 + self.sym["new_sheet"], tsr * 16 + 0xFFF0)
        table = bytes(mu.mem_read(sheets * 16, 0x200))
        self.assertEqual(table[dst + 0x42:dst + 0x48], bytes(6))
        self.assertEqual(table[:dst + 0x42] + table[dst + 0x48:], b"\xee" * (0x200 - 6))
        for name, value in regs.items():
            if name not in ("esp", "eflags"):
                self.assertEqual(mu.reg_read(getattr(r, "UC_X86_REG_" + name.upper())), value, name)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_SP), 0x800 + 10)  # (as after the game's add sp,0Ah)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_EFLAGS) & 0x400, 0)  # (DF as it was)
        self.assertEqual(struct.unpack("<H", mu.mem_read(tsr * 16 + self.sym["sheets_made"], 2))[0], 1)


def record_list(*sheet_sizes) -> bytes:
    """A CHAR-like record list: a creature (31h) and sheets of SHEET_SIZES, an item between."""
    recs = [dataitems.Record(1, 0, 2, 0, 0, bytes(range(0x31)))]
    for size in sheet_sizes:
        recs.append(dataitems.Record(3, 0, ravager.SHEET_KIND, 0, 15, bytes((i * 7) & 0xFF for i in range(size))))
        recs.append(dataitems.Record(2, 0, 1, 1, 16, bytes(0x17)))
    return dataitems.chunk(recs, dataitems.HEADER.pack(dataitems.END, len(recs), 2, 0, 0, 0))


def gff_file(chunks) -> bytes:
    from test_ravtransfer import rt
    return rt._gff_file(chunks)


class WidenTests(unittest.TestCase):
    def test_records(self):
        """A sheet record 42h made 48h (zeros after) and back (the six dropped); the others untouched;
        none to change: None (by length, so twice is once)."""
        old = record_list(0x42, 0x42)
        wide = ravager.resized_sheets(old, ravager.SHEET_SIZE)
        recs = dataitems.records(wide)[0]
        self.assertEqual([len(x.data) for x in recs], [0x31, 0x48, 0x17, 0x48, 0x17])
        self.assertEqual(recs[1].data, dataitems.records(old)[0][1].data + bytes(6))
        self.assertIsNone(ravager.resized_sheets(wide, ravager.SHEET_SIZE))
        self.assertEqual(ravager.resized_sheets(wide, ravager.GAME_SHEET_SIZE), old)
        mixed, end = dataitems.records(record_list(0x42, 0x48))  # (the transfer's 48h beside CHARTRAN's 42h)
        made = dataitems.records(ravager.resized_sheets(dataitems.chunk(mixed, end), ravager.SHEET_SIZE))[0]
        self.assertEqual(made, [mixed[0], mixed[1]._replace(data=mixed[1].data + bytes(6))] + mixed[2:])
        self.assertIsNone(ravager.resized_sheets(b"\x01\x02", ravager.SHEET_SIZE))  # (not a record list)

    def test_save_table(self):
        table = bytes(range(256)) * 4 + bytes(range(0x462 - 1024))
        wide = ravager.resized_chunks({ravager.SHEETS_CHUNK: table, ("SAVE", 5): bytes(0x462)}, ravager.SHEET_SIZE)
        self.assertEqual(list(wide), [ravager.SHEETS_CHUNK])  # (only SAVE 6 is the sheets)
        sheets = wide[ravager.SHEETS_CHUNK]
        self.assertEqual(len(sheets), 17 * 0x48)
        for i in range(17):
            self.assertEqual(sheets[i * 0x48:(i + 1) * 0x48], table[i * 0x42:(i + 1) * 0x42] + bytes(6))
        self.assertEqual(ravager.resized_chunks({ravager.SHEETS_CHUNK: sheets}, ravager.SHEET_SIZE), {})
        self.assertEqual(ravager.resized_chunks({ravager.SHEETS_CHUNK: sheets}, ravager.GAME_SHEET_SIZE),
                         {ravager.SHEETS_CHUNK: table})

    def test_folder(self):
        """The roster and the saves widened (the quick saves' SAVQnn.SAV too), a backup of each first (.42H);
        twice is once; narrowed back to the same chunks (a .48H backup); other files untouched."""
        roster = {("CHAR", 32): record_list(0x42), ("CHAR", 33): record_list(0x48), ("CACT", 32): b"\x01\x00",
                  ("SPST", 32): bytes(9)}
        save = {ravager.SHEETS_CHUNK: bytes(range(256)) * 4 + bytes(0x462 - 1024), ("SAVE", 1): bytes(10)}
        with tempfile.TemporaryDirectory() as d:
            for name, chunks in (("CHARSAVE.GFF", roster), ("SAVE01.SAV", save), ("save02.sav", save),
                                 ("SAVQ03.SAV", save), ("RGN001.GFF", roster), ("DARKRUN.GFF", {("ETME", 0): b"x"})):
                with open(os.path.join(d, name), "wb") as f:
                    f.write(gff_file(chunks))
            before = {n: open(os.path.join(d, n), "rb").read() for n in os.listdir(d)}
            self.assertEqual(ravager.widen_files(d), ["CHARSAVE.GFF", "SAVE01.SAV", "SAVQ03.SAV", "save02.sav"])
            for n in ("CHARSAVE.GFF", "SAVE01.SAV", "SAVQ03.SAV", "save02.sav"):
                self.assertEqual(open(os.path.join(d, n + ".42H"), "rb").read(), before[n])
            for n in ("RGN001.GFF", "DARKRUN.GFF"):
                self.assertEqual(open(os.path.join(d, n), "rb").read(), before[n])
            wide = gff.read_gff(open(os.path.join(d, "CHARSAVE.GFF"), "rb").read())
            self.assertEqual({len(x.data) for k in (32, 33) for x in dataitems.records(wide[("CHAR", k)])[0] if x.kind == 3},
                             {0x48})
            self.assertEqual(len(gff.read_gff(open(os.path.join(d, "SAVE01.SAV"), "rb").read())[ravager.SHEETS_CHUNK]), 0x4C8)
            self.assertEqual(ravager.widen_files(d), [])
            self.assertEqual(ravager.widen_files(d, ravager.GAME_SHEET_SIZE), ["CHARSAVE.GFF", "SAVE01.SAV", "SAVQ03.SAV", "save02.sav"])
            narrow = gff.read_gff(open(os.path.join(d, "CHARSAVE.GFF"), "rb").read())
            self.assertEqual(narrow[("CHAR", 32)], roster[("CHAR", 32)])
            self.assertEqual({len(x.data) for x in dataitems.records(narrow[("CHAR", 33)])[0] if x.kind == 3}, {0x42})
            self.assertEqual(gff.read_gff(open(os.path.join(d, "SAVE01.SAV"), "rb").read())[ravager.SHEETS_CHUNK],
                             save[ravager.SHEETS_CHUNK])
            self.assertTrue(os.path.exists(os.path.join(d, "CHARSAVE.GFF.48H")))

    @unittest.skipUnless(WOTR, "DSUN_WOTR: the player's Wake of the Ravager folder")
    def test_the_games_files(self):
        """The install's roster (19 sheets) and its saves, widened in a copy and narrowed back: the same
        chunks as the game's. The copies are narrowed first, so a folder the Loader has already widened
        (one that has been played) tests the same as a stock one."""
        with tempfile.TemporaryDirectory() as d:
            names = [n for n in os.listdir(WOTR) if n.upper() == "CHARSAVE.GFF" or n.upper().endswith(".SAV")]
            for n in names:
                shutil.copyfile(os.path.join(WOTR, n), os.path.join(d, n))
            ravager.widen_files(d, ravager.GAME_SHEET_SIZE)
            own = {n: gff.read_gff(open(os.path.join(d, n), "rb").read()) for n in names}
            self.assertEqual(sorted(ravager.widen_files(d)), sorted(names))
            self.assertEqual(ravager.widen_files(d), [])
            ravager.widen_files(d, ravager.GAME_SHEET_SIZE)
            for n in names:
                self.assertEqual(gff.read_gff(open(os.path.join(d, n), "rb").read()), own[n], n)

if __name__ == "__main__":
    unittest.main()
