"""Wake of the Ravager's side of the Loader (dsloader.ravager): its patch table, its spell records'
fixes, the config that starts it, and the launch's choice of game. With DSUN_WOTR naming the
player's own Wake of the Ravager folder (never in the repository), the copy is made from its files."""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import gamepatch, gff, launch, ravager  # noqa: E402

WOTR = os.environ.get("DSUN_WOTR")


class TableTests(unittest.TestCase):
    def test_patches_reuse_sl_bytes_but_their_own(self):
        """A patch named after one of Shattered Lands' has its bytes, at the sequel's offset; only the
        path (the sequel's DS address) and the saving throw's compare (its branch the other way) differ."""
        sl = {p.name: p for p in gamepatch.PATCHES}
        own = set()
        for p in ravager.PATCHES:
            if (p.original, p.replacement) != (sl[p.name].original, sl[p.name].replacement):
                own.add(p.name)
        self.assertEqual(own, {"path", "save_signed"})
        self.assertEqual(len({p.name for p in ravager.PATCHES}), len(ravager.PATCHES))

    def test_path_writes_dot_backslash_at_its_ds(self):
        p = next(p for p in ravager.PATCHES if p.name == "path")
        self.assertEqual(p.replacement[:6], bytes.fromhex("c706f244") + b".\\")
        self.assertEqual(len(p.replacement), len(p.original))

    def test_spell_fixes_are_gamepatch_patches_in_its_records(self):
        names = {p.name for p in gamepatch.PATCHES}
        for name, (spell, field) in ravager.SPELL_FIXES.items():
            self.assertIn(name, names)
            self.assertLess(spell, ravager.SPELL_COUNT)
            self.assertLessEqual(field + len(next(p for p in gamepatch.PATCHES if p.name == name).original), 32)
        # (SSI fixed these two itself: not in the table)
        self.assertNotIn("dispel_effect", ravager.SPELL_FIXES)
        self.assertNotIn("bestow_curse_save", ravager.SPELL_FIXES)

    def test_spells_manual_switch_leaves_its_fixes_out(self):
        self.assertEqual(ravager.skipped({}), frozenset())
        self.assertEqual(ravager.skipped({"spells_manual": False}), frozenset(gamepatch.SPELLS_MANUAL))

    def test_conf_lines(self):
        lines = ravager.conf_lines(r"C:\GOG\Ravager", r"C:\mod\dos", cd=r"C:\GOG\Ravager\game.ins",
                                   game_end="GAMEEND.COM")
        self.assertIn("ems=false", lines)
        self.assertIn(r'mount c "C:\GOG\Ravager"', lines)
        self.assertIn(r'imgmount f "C:\GOG\Ravager\game.ins" -t iso', lines)
        self.assertIn(r'mount d "C:\mod\dos"', lines)
        self.assertLess(lines.index(r"d:\umbplus.com"), lines.index(r"d:\dsunlog2.exe -W0 -L"))
        self.assertLess(lines.index("c:"), lines.index(r"d:\dsunlog2.exe -W0 -L"))
        self.assertEqual(lines[-3:], [r"d:\gameend.com", "exit", ""])

    def test_not_a_wotr_dir(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(ravager.is_wotr_dir(d))
            with open(os.path.join(d, "DSUN.EXE"), "wb") as f:
                f.write(b"\0" * gamepatch.GOG_SIZE)  # (Shattered Lands' size)
            self.assertFalse(ravager.is_wotr_dir(d))
            with open(os.path.join(d, "DSUN.EXE"), "wb") as f:
                f.write(b"\0" * ravager.WOTR_SIZE)
            self.assertTrue(ravager.is_wotr_dir(d))

    def test_launch_takes_the_sequel_its_own_way(self):
        """_launch hands a Wake of the Ravager folder to _launch_wotr (its own DOSBox config)."""
        called = []
        real = launch._launch_wotr
        launch._launch_wotr = lambda game_dir, settings: called.append(game_dir) or ("proc", "why")
        try:
            with tempfile.TemporaryDirectory() as d:
                with open(os.path.join(d, "DSUN.EXE"), "wb") as f:
                    f.write(b"\0" * ravager.WOTR_SIZE)
                self.assertEqual(launch._launch(d, {}), ("proc", "why"))
                self.assertEqual(called, [d])
        finally:
            launch._launch_wotr = real


@unittest.skipUnless(WOTR, "DSUN_WOTR: the player's Wake of the Ravager folder")
class GameFileTests(unittest.TestCase):
    def test_copy_made(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(ravager.prepare(WOTR, d, {}))
            exe = open(os.path.join(d, ravager.PATCHED_EXE), "rb").read()
            orig = open(os.path.join(WOTR, "DSUN.EXE"), "rb").read()
            for p in ravager.PATCHES:
                self.assertEqual(exe[p.offset:p.offset + len(p.replacement)], p.replacement, p.name)
            changed = sum(len(p.original) for p in ravager.PATCHES)
            self.assertEqual(sum(a != b for a, b in zip(exe, orig)) <= changed, True)
            res = gff.read_gff(open(os.path.join(d, ravager.RESOURCE_COPY), "rb").read())
            game = gff.read_gff(open(os.path.join(WOTR, ravager.RESOURCE_FILE), "rb").read())
            self.assertEqual(res.keys(), game.keys())
            changed_spells = {k[1] for k in game if game[k] != res[k]}
            self.assertEqual(changed_spells, {s for s, _ in ravager.SPELL_FIXES.values()})

    def test_spells_manual_off(self):
        data = open(os.path.join(WOTR, ravager.RESOURCE_FILE), "rb").read()
        _, done = ravager.spell_fixed(data, ravager.skipped({"spells_manual": False}))
        self.assertEqual(set(done), {"cause_serious", "cause_critical", "brave_fear_21", "brave_fear_43",
                                     "brave_fear_78", "brave_fear_132", "scare_save"})


if __name__ == "__main__":
    unittest.main()
