"""The mod's room in Wake of the Ravager's records (dsloader.ravager): the sound words' low bytes alone
(sound_3c, sound_3e, run in an emulated CPU with the game's code round them), so the transfer's kit and
second sphere can stay in +3Dh and +3Fh; and the starting age's roll in a member's known-spells bits
115-119 (known_roll, with_known_roll). The emulation needs unicorn, else skipped."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import ravager  # noqa: E402

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


class KnownRollTests(unittest.TestCase):
    def test_round_trip(self):
        spells = bytes([1, 0, 0, 0, 4, 0, 0, 0, 0])
        for roll in (0, 1, 7, 25, 29):
            with self.subTest(roll=roll):
                bits = ravager.with_known_roll(spells, roll)
                self.assertEqual(len(bits), ravager.KNOWN_BITSET)
                self.assertEqual(bits[:9], spells)
                self.assertEqual(ravager.known_roll(bits), roll)

    def test_none(self):
        """None kept: 0 in the bits, as the game's own characters have them (CHARSAVE's 15 zero bytes)."""
        self.assertIsNone(ravager.known_roll(bytes(15)))
        self.assertEqual(ravager.with_known_roll(b"\x01", None), b"\x01" + bytes(14))
        self.assertIsNone(ravager.known_roll(bytes(9)))  # (CHARTRAN's 9: no room)

    def test_only_bits_115_on(self):
        """The roll is in bits 115-119 (byte 14's top five); the spells' bits 0-114 untouched both ways."""
        full = bytes([0xFF] * 14 + [0x07])  # (bits 0-114 all set)
        bits = ravager.with_known_roll(full, 12)
        self.assertEqual(bits[:14], full[:14])
        self.assertEqual(bits[14] & 0x07, 0x07)
        self.assertEqual(bits[14] >> 3, 13)
        self.assertEqual(ravager.with_known_roll(bits, None), full)
        self.assertIsNone(ravager.known_roll(full))


if __name__ == "__main__":
    unittest.main()
