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
