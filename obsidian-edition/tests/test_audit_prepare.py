"""launch.prepare_patched_game's files, in a temporary dos folder (launch.DOS_DIR) and a fake game
folder, with the writers mocked (each writes a marker, or raises): the objects copy gating the
region copies and the scripts copy, stale region copies taken away, the scripts copy and RGN29 all
or nothing, the slave pens' clones going into Kalzith's RGN29 copy (or the region's own copy
without him), a failed write's earlier copy dropped, and LEFT_OUT (left_out_line) saying what was
left out."""

import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import champions, gamepatch, icons, kalzith, launch, scenepointer, tome, worldgear  # noqa: E402

REGIONS = worldgear.regions(worldgear.GIFTS + worldgear.MAGIC)
CLONES = tuple(g.clone[1] for g in worldgear.GIFTS + worldgear.MAGIC if g.clone)
# what a full objects copy reports as added (the clones, and the objects the scripts ask about)
ALL_NEW = tuple(sorted(set(CLONES) | {worldgear.ELVEN_CLOAK_OBJECT, tome.TOME_OBJECT, worldgear.HAYNEEDLE_OBJECT,
                                       champions.TOHR_KREEN}))
OBJECTS, SCRIPTS, PENS, RESOURCES = icons.OBJECTS_FILE, kalzith.SCRIPTS_FILE, kalzith.REGION_FILE, icons.RESOURCE_FILE


def _mark(dest, what="new"):
    with open(dest, "w") as f:
        f.write(what)


class PrepareTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.game, self.dos = os.path.join(tmp.name, "game"), os.path.join(tmp.name, "dos")
        os.mkdir(self.game)
        os.mkdir(self.dos)
        for name in ["DSUN.EXE", OBJECTS, SCRIPTS, RESOURCES, PENS] + [worldgear.region_file(r) for r in REGIONS]:
            _mark(os.path.join(self.game, name), "game")
        self.calls = {"regions": {}, "pens": None, "scripts": None}
        self.fail = set()  # (the writers to raise: "objects", "scripts", "resources", "patch", "region")
        self.new_objects = ALL_NEW
        self.kalzith_object = True  # (whether the objects copy could have Kalzith's object)

        def write_objects(source, dest, on):
            if "objects" in self.fail:
                raise OSError("disk full")
            _mark(dest)
            return True, self.new_objects, self.kalzith_object

        def write_region(source, dest, region, gifts):
            if "region" in self.fail:
                raise OSError("locked")
            self.calls["regions"][region] = [g.clone[1] for g in gifts]
            _mark(dest)

        def write_scripts(source, dest, *args):
            self.calls["scripts"] = args
            if "scripts" in self.fail:
                raise OSError("disk full")
            _mark(dest)

        def write_pens(source, dest, gifts=()):
            self.calls["pens"] = [g.clone[1] for g in gifts]
            _mark(dest)

        def write_resources(source, dest, *args):
            if "resources" in self.fail:
                raise OSError("disk full")
            _mark(dest)

        def write_patched(source, dest, skip=frozenset()):
            if "patch" in self.fail:
                raise gamepatch.PatchError("not GOG's DSUN.EXE")
            _mark(dest)

        # the game's folder as it was: no test may see it written (every writer only reads it)
        self.game_files = self.snapshot(self.game)
        self.addCleanup(self.game_unchanged)
        for target, name, f in ((launch, "DOS_DIR", self.dos), (icons, "write_objects", write_objects),
                                (worldgear, "write_region", write_region), (kalzith, "write_scripts", write_scripts),
                                (kalzith, "write_region", write_pens), (icons, "write_resources", write_resources),
                                (gamepatch, "write_patched", write_patched),
                                (scenepointer, "write_pointer", lambda *a: False)):
            p = mock.patch.object(target, name, f)
            p.start()
            self.addCleanup(p.stop)

    def game_unchanged(self):
        """Every file of the game's folder as it was, none added (a test may take one away first)."""
        now = self.snapshot(self.game)
        changed = sorted(name for name in now if self.game_files.get(name) != now[name])
        if changed:
            raise AssertionError(f"the game's folder changed: {changed}")

    @staticmethod
    def snapshot(folder):
        out = {}
        for name in sorted(os.listdir(folder)):
            with open(os.path.join(folder, name), "rb") as f:
                out[name] = f.read()
        return out

    def stale(self, *names):
        """Copies an earlier start left in dos/."""
        for name in names:
            _mark(os.path.join(self.dos, name), "stale")

    def there(self, name):
        path = os.path.join(self.dos, name)
        if not os.path.exists(path):
            return None
        with open(path) as f:
            return f.read()

    def prepare(self, **settings):
        return launch.prepare_patched_game(self.game, settings)

    def region_names(self, skip_pens=True):
        return [worldgear.region_file(r) for r in REGIONS if not (skip_pens and r == kalzith.REGION)]

    def test_all_on(self):
        self.assertIsNone(self.prepare())
        for name in (launch.PATCHED_EXE, OBJECTS, SCRIPTS, PENS, RESOURCES):
            self.assertEqual(self.there(name), "new", name)
        for name in self.region_names():
            self.assertEqual(self.there(name), "new", name)
        self.assertNotIn(kalzith.REGION, self.calls["regions"])  # (the pens: in Kalzith's copy)
        pens = [g.clone[1] for g in worldgear.GIFTS + worldgear.MAGIC if g.clone and g.region == kalzith.REGION]
        self.assertTrue(pens)
        self.assertEqual(self.calls["pens"], pens)
        self.assertEqual(launch.LEFT_OUT, [])
        self.assertIsNone(launch.left_out_line())

    def test_objects_fail(self):
        """No objects copy: no earlier one left, no region copies, scripts without Kalzith, no RGN29."""
        self.stale(OBJECTS, PENS, *self.region_names())
        self.fail.add("objects")
        self.assertIsNone(self.prepare())
        self.assertIsNone(self.there(OBJECTS))
        for name in self.region_names(skip_pens=False):
            self.assertIsNone(self.there(name), name)
        self.assertEqual(self.calls["regions"], {})
        self.assertIsNone(self.calls["pens"])
        self.assertIs(self.calls["scripts"][0], False)  # (Kalzith)
        self.assertEqual(self.there(SCRIPTS), "new")
        self.assertEqual(len(launch.LEFT_OUT), 1)
        self.assertIn(OBJECTS, launch.LEFT_OUT[0])
        self.assertIn(OBJECTS, launch.left_out_line())

    def test_objects_not_in_the_game(self):
        os.remove(os.path.join(self.game, OBJECTS))
        self.stale(OBJECTS)
        self.prepare()
        self.assertIsNone(self.there(OBJECTS))
        self.assertTrue(any("not in the game's folder" in line for line in launch.LEFT_OUT))

    def test_clone_not_in_the_objects(self):
        """A region's copy only for clones the objects copy has."""
        missing = next(g for g in worldgear.GIFTS + worldgear.MAGIC if g.clone and g.region != kalzith.REGION)
        self.new_objects = tuple(n for n in ALL_NEW if n != missing.clone[1])
        self.stale(worldgear.region_file(missing.region))
        self.prepare()
        mine = [g for g in worldgear.GIFTS + worldgear.MAGIC if g.region == missing.region and g.clone]
        if len(mine) == 1:
            self.assertIsNone(self.there(worldgear.region_file(missing.region)))
        self.assertNotIn(missing.clone[1], self.calls["regions"].get(missing.region, []))

    def test_new_items_off(self):
        """The gifts off: every earlier region copy taken away; Kalzith's RGN29 without clones."""
        self.stale(*self.region_names())
        self.prepare(new_items=False)
        for name in self.region_names():
            self.assertIsNone(self.there(name), name)
        self.assertEqual(self.calls["regions"], {})
        self.assertEqual(self.calls["pens"], [])
        self.assertEqual(self.there(PENS), "new")

    def test_kalzith_off_pens_clones_in_their_own_copy(self):
        """Kalzith off: the pens' clones in RGN29's copy all the same (the region's own), kept."""
        self.prepare(kalzith=False)
        self.assertIsNone(self.calls["pens"])
        self.assertTrue(self.calls["regions"].get(kalzith.REGION))
        self.assertEqual(self.there(PENS), "new")

    def test_kalzith_off_no_clones(self):
        """Kalzith off and no gifts: no RGN29 copy, an earlier one taken away."""
        self.stale(PENS)
        self.prepare(kalzith=False, new_items=False)
        self.assertIsNone(self.there(PENS))

    def test_scripts_fail(self):
        """All or nothing: neither the scripts copy nor RGN29 (Kalzith's, written first) is left."""
        self.stale(SCRIPTS, PENS)
        self.fail.add("scripts")
        self.assertIsNone(self.prepare())
        self.assertIsNone(self.there(SCRIPTS))
        self.assertIsNone(self.there(PENS))
        self.assertEqual(self.there(OBJECTS), "new")
        self.assertTrue(any(SCRIPTS in line for line in launch.LEFT_OUT))

    def test_region_fail(self):
        """A region copy that can't be written: none of it left, and said."""
        self.stale(*self.region_names())
        self.fail.add("region")
        self.prepare()
        for name in self.region_names():
            self.assertIsNone(self.there(name), name)
        self.assertTrue(launch.LEFT_OUT)

    def test_resources_fail(self):
        self.stale(RESOURCES)
        self.fail.add("resources")
        self.assertIsNone(self.prepare())
        self.assertIsNone(self.there(RESOURCES))
        self.assertTrue(any(RESOURCES in line for line in launch.LEFT_OUT))

    def test_patch_refused(self):
        """A DSUN.EXE that can't be patched: the reason returned, no copy made."""
        self.fail.add("patch")
        self.assertIn("GOG", self.prepare())
        self.assertEqual(os.listdir(self.dos), [])

    def test_no_kalzith_object_keeps_the_copy(self):
        """A copy of the game where Kalzith's object can't be made (a number of his taken): the
        objects copy is kept (icons, items, the region copies and gifts), the scripts are written
        without him, no RGN29 of his, and the player is told."""
        self.stale(PENS)
        self.kalzith_object = False
        self.prepare(new_items=False)
        self.assertEqual(self.there(OBJECTS), "new")
        self.assertIs(self.calls["scripts"][0], False)  # (Kalzith)
        self.assertIsNone(self.calls["pens"])
        self.assertIsNone(self.there(PENS))
        self.assertEqual(len(launch.LEFT_OUT), 1)
        self.assertIn("Kalzith", launch.LEFT_OUT[0])
        self.kalzith_object = True
        self.prepare()
        self.assertEqual(launch.LEFT_OUT, [])

    def test_no_kalzith_object_with_him_off_says_nothing(self):
        self.kalzith_object = False
        self.prepare(kalzith=False)
        self.assertEqual(self.there(OBJECTS), "new")
        self.assertEqual(launch.LEFT_OUT, [])

    def test_objects_not_written_is_said(self):
        self.stale(OBJECTS)
        with mock.patch.object(icons, "write_objects", lambda source, dest, on: (False, (), False)):
            self.prepare()
        self.assertIsNone(self.there(OBJECTS))
        self.assertTrue(any(OBJECTS in line for line in launch.LEFT_OUT))

    def test_stale_alagorn_line_not_repeated(self):
        """An earlier start's Alagorn line (a menu too long) isn't said at a start whose scripts
        didn't make one."""
        from dsloader import alagorn
        self.addCleanup(lambda: alagorn.LEFT_OUT.clear())
        alagorn.LEFT_OUT.append("Alagorn's arms menu (too long)")
        self.prepare(new_items=False)
        self.assertEqual(launch.LEFT_OUT, [])

    def test_left_out_cleared(self):
        self.fail.add("resources")
        self.prepare()
        self.assertTrue(launch.LEFT_OUT)
        self.fail.clear()
        self.prepare()
        self.assertEqual(launch.LEFT_OUT, [])


if __name__ == "__main__":
    unittest.main()
