"""The Loader's start on the player's real game files: launch.prepare_patched_game on Shattered Lands
(DSUN_SL, its folder) with every switch at its default, its copies written into a temporary dos folder.
It must say no problem and leave nothing out. The writers are unit-tested on made-up data elsewhere;
this catches a writer that breaks on the real files (2026-11-26: weaponpages.slot's UnboundLocalError
stopped every start, on either engine). Without DSUN_SL it is skipped (CI has no game files)."""

import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import launch  # noqa: E402

SL = os.environ.get("DSUN_SL")


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


if __name__ == "__main__":
    unittest.main()
