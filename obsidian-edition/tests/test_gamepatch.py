import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import gamepatch


def fake_dsun() -> bytearray:
    data = bytearray(gamepatch.GOG_SIZE)
    for p in gamepatch.PATCHES:
        data[p.offset:p.offset + len(p.original)] = p.original
    return data


class GamePatchTests(unittest.TestCase):
    def test_patches_replace_known_bytes_only(self):
        original = fake_dsun()
        patched = gamepatch.patched(bytes(original))
        self.assertEqual(len(patched), len(original))
        changed = [i for i in range(len(original)) if original[i] != patched[i]]
        self.assertTrue(all(any(p.offset <= i < p.offset + len(p.original) for p in gamepatch.PATCHES)
                            for i in changed))
        rand = gamepatch.PATCHES[0]
        self.assertEqual(patched[rand.offset:rand.offset + 2], bytes((0xCD, gamepatch.VEC_RAND)))
        for p in gamepatch.PATCHES:
            self.assertEqual(len(p.replacement), len(p.original))

    def test_skipped_patches_keep_the_games_bytes(self):
        """A patch switched off (the Effects screen's click) is checked but left as the game's."""
        original = fake_dsun()
        patched = gamepatch.patched(bytes(original), frozenset(gamepatch.EFFECTS_KEPT))
        names = {p.name for p in gamepatch.PATCHES}
        self.assertTrue(set(gamepatch.EFFECTS_KEPT) <= names)
        for p in gamepatch.PATCHES:
            got = patched[p.offset:p.offset + len(p.original)]
            self.assertEqual(got, p.original if p.name in gamepatch.EFFECTS_KEPT else p.replacement, p.name)
        self.assertTrue(set(gamepatch.ROLL_STORE) <= names)  # (STORE and RECALL, switched the same way)

    def test_relocated_words_kept(self):
        """A word DOS relocates (from the EXE's relocation table) must be left as it was: the
        camera patch keeps its "mov ax,377Eh" at 1CA15h; a patch changing such a word is refused."""
        import struct
        data = fake_dsun()
        struct.pack_into("<HHH", data, 6, 1, 0, 0)  # (one entry, the image at offset 0)
        struct.pack_into("<H", data, 0x18, 0x40)
        struct.pack_into("<HH", data, 0x40, 0x26, 0x1C9F)  # (1C9F:0026 = 1CA16h)
        gamepatch.patched(bytes(data))
        struct.pack_into("<HH", data, 0x40, 0x20, 0x1C9F)  # (1CA10h: changed by the patch)
        with self.assertRaises(gamepatch.PatchError):
            gamepatch.patched(bytes(data))

    def test_camera_still(self):
        """The fight's step tests whether its figure is on the screen (the game's own routine,
        0AC0:AC7Ah, from 0AC0:C9F2h: a near call) before the view is moved, and pushes the same
        spot it did; a switch (CAMERA)."""
        p = next(p for p in gamepatch.PATCHES if p.name == "camera_still")
        self.assertEqual(gamepatch.CAMERA, ("camera_still",))
        self.assertEqual(p.offset, 0x1C9F2)
        r = p.replacement
        call = r.index(bytes.fromhex("0ee8")) + 1
        rel = int.from_bytes(r[call + 1:call + 3], "little", signed=True)
        self.assertEqual(0xC9F2 + call + 3 + rel, 0xAC7A)
        self.assertIn(bytes.fromhex("66ffb79d66"), r)  # (y, then x, as the game's: one push dword)
        self.assertEqual(r[0x23:0x26], bytes.fromhex("b87e37"))  # (mov ax,377Eh where the game has it)
        self.assertIn(bytes.fromhex("833e681100"), r)  # (in a fight only: IN_COMBAT, DS:1168h)

    def test_enter_out_of_the_save_windows_keys(self):
        """The save/load window's key table (Esc, Enter, Up, Down) without Enter, which PROBE_SAVE_PAGE
        then takes."""
        p = next(p for p in gamepatch.PATCHES if p.name == "save_enter")
        self.assertEqual(p.offset, 0x74300 + 0xB26 + 2)
        self.assertEqual(p.replacement, b"\xff\xff")

    def test_new_counts_as_okay(self):
        """Each of the game's "is it Okay" tests keeps its compare and turns its jz/jnz into
        jbe/ja, so that New (0) passes as Okay (1)."""
        okay = [p for p in gamepatch.PATCHES if p.name.startswith("new_okay_")]
        self.assertEqual(len(okay), len(gamepatch.NEW_AS_OKAY))
        for p in okay:
            self.assertEqual(p.original[:5], bytes.fromhex("26807f1c01"))
            self.assertEqual(p.replacement[:5], p.original[:5])
            self.assertEqual(p.replacement[5], {0x74: 0x76, 0x75: 0x77}[p.original[5]])
        self.assertIn(0x802AC, [p.offset for p in okay])  # (the thief skills)

    def test_other_versions_are_refused(self):
        with self.assertRaisesRegex(gamepatch.PatchError, "GOG release"):
            gamepatch.patched(bytes(1000))
        data = fake_dsun()
        data[gamepatch.PATCHES[1].offset] ^= 0xFF
        with self.assertRaisesRegex(gamepatch.PatchError, "save differs"):
            gamepatch.patched(bytes(data))

    def test_write_patched_leaves_the_original_alone(self):
        with tempfile.TemporaryDirectory() as d:
            src, dest = os.path.join(d, "DSUN.EXE"), os.path.join(d, "DSUNLOG.EXE")
            with open(src, "wb") as f:
                f.write(fake_dsun())
            gamepatch.write_patched(src, dest)
            gamepatch.write_patched(src, dest)  # again: nothing to do
            with open(src, "rb") as f:
                self.assertEqual(f.read(), bytes(fake_dsun()))
            with open(dest, "rb") as f:
                self.assertEqual(f.read(), gamepatch.patched(bytes(fake_dsun())))

    def test_page_free_skips_both_frees(self):
        """The game's jz past a failed first page lands on the end of the freeing, not on it."""
        p = next(p for p in gamepatch.PATCHES if p.name == "page_free")
        jz_end = 0x1F4B3 + 2  # (in the image: the file less its 5400h header) 1DF3:1583 + 2
        self.assertEqual(jz_end + p.original[1] - 0x1DF30, 0x15C0)  # the frees
        self.assertEqual(jz_end + p.replacement[1] - 0x1DF30, 0x15DE)  # past them
        self.assertEqual(p.offset - 0x5400, 0x1F4B3)

    def test_characters(self):
        """Every one of the game's 19/20s for the saved characters made CHARACTERS/+1, a byte each
        (a sign-extended byte: up to 127)."""
        patches = [p for p in gamepatch.PATCHES if p.name.startswith("characters_")]
        self.assertEqual(len(patches), 10)
        self.assertLess(gamepatch.CHARACTERS + 1, 0x80)
        for p in patches:
            self.assertEqual(p.original[:-1], p.replacement[:-1], p.name)
            want = (0x13, gamepatch.CHARACTERS) if p.name == "characters_full" else (0x14, gamepatch.CHARACTERS + 1)
            self.assertEqual((p.original[-1], p.replacement[-1]), want, p.name)

    def test_roster_delete_keeps_the_segment_loads(self):
        """The fixed DELETE: its two "mov ax,<segment>" where the game's were (fixed up on loading),
        and it ends where the game's did."""
        p = next(p for p in gamepatch.PATCHES if p.name == "roster_delete")
        for at in (0x54AE6, 0x54AFD):
            i = at - p.offset
            self.assertEqual(p.original[i:i + 3], bytes.fromhex("b8d002"))
            self.assertEqual(p.replacement[i:i + 3], bytes.fromhex("b8d002"))
        self.assertIn(bytes.fromhex("2603060200"), p.replacement)  # add ax,es:[2]: the scroll
        self.assertEqual(p.original[-4:], p.replacement[-7:-3])  # mov ax,es:[bx+6], then on


if __name__ == "__main__":
    unittest.main()


try:
    from unicorn import Uc, UC_ARCH_X86, UC_HOOK_CODE, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:
    Uc = None


@unittest.skipIf(Uc is None, "unicorn is not installed")
class PowerEndTests(unittest.TestCase):
    # The game's loop ending a caster's maintained power (5CEECh-5CF34h) as patched: the
    # power_end_* replacements at their places, the game's own bytes between them.
    LOOP = 0x5CEEC
    CODE = bytes.fromhex("8bde6bdb0ab890038ec0268b870a013b46fe752a3b36241e90b890037d202639bf0801"
                         "751926ffb70d01b8900326ffb70601909090909a4800980559594e463b36241e7cbb5f5ec9cb")

    def test_patches_in_the_loop(self):
        for p in gamepatch.PATCHES:
            if p.name.startswith("power_end_"):
                at = p.offset - self.LOOP
                self.assertEqual(self.CODE[at:at + len(p.replacement)], p.replacement, p.name)

    def test_each_record_removed_by_its_owner(self):
        """Every record of the power (spell, +4) cast by DI (+2) removed by its own owner (+0) and
        handle (+7), records after a removed one moving down and none skipped."""
        import struct
        es, ds, cs, ss = 0x390, 0x2000, 0x1000, 0x3000
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        records = [(1, 5, 30, 12, 7), (2, 5, 30, 12, 8), (3, 6, 30, 12, 9), (4, 5, 31, 12, 10),
                   (0, 5, 30, 12, 11)]  # (owner, caster, spell, id, handle)
        def store():
            for i, rec in enumerate(records):
                mu.mem_write(es * 16 + 0x106 + i * 10, struct.pack("<hhhBBBB", *rec, 0, 0))
            mu.mem_write(ds * 16 + 0x1E24, struct.pack("<H", len(records)))
        store()
        removed = []
        def remove(uc, address, size, data):  # (598:48h: owner, handle on the stack)
            if address != 0x598 * 16 + 0x48:
                return
            sp = uc.reg_read(r.UC_X86_REG_SP)
            owner, handle = struct.unpack("<HH", bytes(uc.mem_read(ss * 16 + sp + 4, 4)))
            hit = next(rec for rec in records if rec[0] == owner and rec[4] == handle & 0xFF)
            removed.append(hit)
            records.remove(hit)
            store()
        mu.hook_add(UC_HOOK_CODE, remove)
        mu.mem_write(0x598 * 16 + 0x48, b"\xcb")
        mu.mem_write(cs * 16 + 0x100, self.CODE[:-4] + b"\xf4")  # (a HLT for the "pop di")
        mu.mem_write(ss * 16 + 0x7FE, struct.pack("<H", 30))  # [BP-2]: the spell
        for name, value in dict(cs=cs, ds=ds, ss=ss, sp=0x7F0, bp=0x800, si=0, di=5).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(cs * 16 + 0x100, 0, count=2000)
        self.assertEqual(removed, [(1, 5, 30, 12, 7), (2, 5, 30, 12, 8), (0, 5, 30, 12, 11)])
        self.assertEqual(records, [(3, 6, 30, 12, 9), (4, 5, 31, 12, 10)])
