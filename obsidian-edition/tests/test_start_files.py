"""The Loader's start on the player's real game files: launch.prepare_patched_game on Shattered Lands
(DSUN_SL, its folder) with every switch at its default, its copies written into a temporary dos folder.
It must say no problem and leave nothing out. The writers are unit-tested on made-up data elsewhere;
this catches a writer that breaks on the real files (2026-11-26: weaponpages.slot's UnboundLocalError
stopped every start, on either engine). Wake of the Ravager's start the same: ravager.prepare on the
sequel's folder (DSUN_WOTR; with DSUN_SL, Shattered Lands' too, for the new items' pictures) writes every
copy with no problem. Without the folders they are skipped (CI has no game files)."""

import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import launch, ravager  # noqa: E402

SL = os.environ.get("DSUN_SL")
WOTR = os.environ.get("DSUN_WOTR")


@unittest.skipUnless(SL, "needs DSUN_SL (Shattered Lands' folder)")
class ShatteredLandsStartTests(unittest.TestCase):
    def test_every_copy_made(self):
        with tempfile.TemporaryDirectory() as dos:
            for name in os.listdir(launch.DOS_DIR):  # (the mod's own DOS programs the copies sit beside)
                if name.upper().endswith((".EXE", ".COM")) and name.upper() != launch.PATCHED_EXE:
                    with open(os.path.join(launch.DOS_DIR, name), "rb") as f, \
                            open(os.path.join(dos, name), "wb") as out:
                        out.write(f.read())
            with mock.patch.object(launch, "DOS_DIR", dos):
                problem = launch.prepare_patched_game(SL, dict(launch.SWITCH_DEFAULTS))
            self.assertIsNone(problem)
            self.assertIsNone(launch.left_out_line())
            self.assertTrue(os.path.isfile(os.path.join(dos, launch.PATCHED_EXE)))

    def test_every_copy_made_after_the_sequel(self):
        """The same with the sequel's layout left on, as a sequel's game played from the Loader's window
        leaves it (2026-11-27: the new items, people and icons were left out)."""
        from dsloader import ravlog
        ravlog.apply_layout()
        self.addCleanup(ravlog.restore_layout)
        self.test_every_copy_made()


@unittest.skipUnless(WOTR, "needs DSUN_WOTR (Wake of the Ravager's folder)")
class RavagerStartTests(unittest.TestCase):
    def test_every_copy_made(self):
        with tempfile.TemporaryDirectory() as dos:
            problem = ravager.prepare(WOTR, dos, dict(launch.SWITCH_DEFAULTS), SL)
            self.assertIsNone(problem)
            for name in (ravager.PATCHED_EXE, ravager.RESOURCE_COPY, ravager.SCRIPT_COPY, ravager.OBJECTS_COPY):
                self.assertTrue(os.path.getsize(os.path.join(dos, name)) > 0, name)


if __name__ == "__main__":
    unittest.main()
