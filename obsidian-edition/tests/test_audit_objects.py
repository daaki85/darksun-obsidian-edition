"""The objects and pictures each module adds to the Loader's SEGOBJEX copy (icons.write_objects
merges them with dict.update: the last one wins, without a word) are each made by one module.

DeclaredTests (no game files): the numbers each module declares (icons.ICONS, the box copies
BOX_SMALL on, SHINE's own pictures, the bolt; the party's sprites; Kalzith's object, scrolls and
moved icons; Wake of the Ravager's walls; Whirlwind's funnel; worldgear's clones and its RDFFs for
the icons' cloak and Hayneedle; the champions; Pehtucl's needle; the tome), as chunk keys, overlap
nowhere.

BuiltTests (with the game's SEGOBJEX.GFF, DSUN_OBJECTS): icons.write_objects with every part's
function watched. No new chunk (one the game hasn't) comes from two parts, an existing one is
changed by two only when the later part is given the earlier ones' output to build on (BUILDS_ON),
and each part's new chunks are among those it declares (so the declared numbers stay the truth)."""

import functools
import os
import sys
import tempfile
import unittest
from unittest import mock

TESTS = os.path.dirname(os.path.abspath(__file__))
HERE = os.path.dirname(TESTS)
sys.path.insert(0, HERE)

from dsloader import (champions, defaultparty, gff, icons, kalzith, monsters, pehtuclchest,  # noqa: E402
                      sprites, tome, whirlart, worldgear, wotrart, arms)

OBJECTS = os.environ.get("DSUN_OBJECTS")


def _object(*numbers):
    """An object's chunks: its OJFF and its RDFF."""
    return {(kind, n) for n in numbers for kind in ("OJFF", "RDFF")}


def _pictures(*numbers):
    return {("BMP ", n) for n in numbers}


def declared():
    """{part: the chunk keys it may add}, from each module's numbers."""
    scrolls = range(len(kalzith.SCROLLS))
    party = len(sprites.PARTY_OBJECTS) + len(sprites.SPARES)
    clones = [g.clone[1] for g in worldgear.GIFTS + worldgear.MAGIC if g.clone]
    return {
        "icons.new_chunks": {("OJFF", number) for _, _, number, _, _ in icons.ICONS}
        | _pictures(*(n for _, _, number, icon, _ in icons.ICONS for n in (number, icon)))
        | _pictures(*range(icons.BOX_SMALL, icons.BOX_SMALL + len(icons.BOX_TALL)))
        | _pictures(*(own for _, _, _, own in icons.SHINE if own)),
        "icons.bolt_chunks": {("OJFF", icons.FOG_BOLT_OBJECT)} | _pictures(icons.FOG_BOLT_PICTURE),
        "sprites.new_chunks": _pictures(*range(sprites.SPRITE_BASE, sprites.SPRITE_BASE + 2 * party)),
        "kalzith.object_chunks": _object(kalzith.OBJECT)
        | {("OJFF", n) for k in scrolls for n in (kalzith.OLD_SCROLL_OBJECT + k, kalzith.SCROLL_OBJECT + k)}
        | _pictures(*(kalzith.MOVED_ICONS + k for k in scrolls)),
        "wotrart.area_chunks": {("OJFF", n) for n, _ in wotrart.AREA_OBJECTS.values()}
        | _pictures(*(p for _, p in wotrart.AREA_OBJECTS.values())),
        "whirlart.chunks": {("OJFF", whirlart.OBJECT)} | _pictures(whirlart.PICTURE),
        "worldgear.object_chunks": _object(*clones),
        "worldgear.data_chunks": {("RDFF", worldgear.ELVEN_CLOAK_OBJECT), ("RDFF", worldgear.HAYNEEDLE_OBJECT)},
        "champions.object_chunks": _object(*champions.OBJECTS, champions.BODY) | _pictures(champions.BODY),
        "pehtuclchest.object_chunks": _object(pehtuclchest.TRAP_OBJECT),
        "tome.object_chunks": _object(tome.TOME_OBJECT) | _pictures(tome.MOVED, tome.ICON),
    }


# the parts write_objects merges, as (module, function); and those given the parts' output before
# them to build on (an existing chunk they change again is theirs to change)
PARTS = ((icons, "new_chunks"), (sprites, "new_chunks"), (kalzith, "object_chunks"), (icons, "bolt_chunks"),
         (wotrart, "area_chunks"), (whirlart, "chunks"), (worldgear, "object_chunks"),
         (pehtuclchest, "object_chunks"), (champions, "object_chunks"), (arms, "kreenfang_chunks"),
         (worldgear, "cahulaks_chunks"), (worldgear, "gythka_chunks"), (tome, "object_chunks"),
         (worldgear, "data_chunks"), (defaultparty, "figure_chunks"), (monsters, "object_chunks"))
BUILDS_ON = {"pehtuclchest.object_chunks", "worldgear.cahulaks_chunks", "worldgear.gythka_chunks",
             "defaultparty.figure_chunks", "monsters.object_chunks"}
# worldgear.data_chunks is the sum of its own parts (and a few chunks of its own): its own are what
# is left once theirs are taken away
WORLDGEAR_PARTS = {"worldgear.object_chunks", "pehtuclchest.object_chunks", "champions.object_chunks",
                   "arms.kreenfang_chunks", "worldgear.cahulaks_chunks", "worldgear.gythka_chunks",
                   "tome.object_chunks"}


def _label(module, name):
    return f"{module.__name__.rsplit('.', 1)[1]}.{name}"


class DeclaredTests(unittest.TestCase):
    def test_disjoint(self):
        parts = declared()
        seen = {}
        for part, keys in parts.items():
            for key in keys:
                self.assertFalse(key in seen, f"{key} is {part}'s and {seen.get(key)}'s")
                seen[key] = part

    def test_cloak_and_hayneedle_are_icons_objects(self):
        """worldgear's RDFFs for the cloak and Hayneedle are for the icons' objects of those numbers."""
        objects = {number for _, _, number, _, _ in icons.ICONS}
        self.assertIn(worldgear.ELVEN_CLOAK_OBJECT, objects)
        self.assertIn(worldgear.HAYNEEDLE_OBJECT, objects)


@unittest.skipUnless(OBJECTS and os.path.isfile(OBJECTS), "needs the game's SEGOBJEX.GFF (DSUN_OBJECTS)")
class BuiltTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        made = []

        def watched(label, f):
            @functools.wraps(f)
            def w(*args, **kwargs):
                out = f(*args, **kwargs)
                made.append((label, set(out)))
                return out
            return w

        with open(OBJECTS, "rb") as f:
            cls.game = set(gff.read_gff(f.read()))
        patches = [mock.patch.object(m, n, watched(_label(m, n), getattr(m, n))) for m, n in PARTS]
        for p in patches:
            p.start()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                icons.write_objects(OBJECTS, os.path.join(tmp, icons.OBJECTS_FILE), {})
        finally:
            for p in patches:
                p.stop()
        own = set()
        for label, keys in made:
            if label == "worldgear.data_chunks":
                own |= keys - set().union(*(k for lb, k in made if lb in WORLDGEAR_PARTS))
        cls.made = [(lb, k) for lb, k in made if lb != "worldgear.data_chunks"] + [("worldgear.data_chunks", own)]

    def test_every_part_ran(self):
        labels = {lb for lb, _ in self.made}
        for part in ("icons.new_chunks", "kalzith.object_chunks", "worldgear.object_chunks",
                     "champions.object_chunks", "pehtuclchest.object_chunks", "tome.object_chunks"):
            self.assertIn(part, labels)

    def test_new_chunks_made_once(self):
        seen = {}
        for label, keys in self.made:
            for key in keys - self.game:
                self.assertFalse(key in seen, f"{key} made by {seen.get(key)} and {label}")
                seen[key] = label

    def test_game_chunks_changed_again_only_by_builders(self):
        seen = {}
        for label, keys in self.made:
            for key in keys & self.game:
                if key in seen:
                    self.assertIn(label, BUILDS_ON, f"{key} changed by {seen[key]} and again by {label}")
                seen[key] = label

    def test_new_chunks_declared(self):
        parts = declared()
        for label, keys in self.made:
            new = keys - self.game
            if label in parts:
                with self.subTest(part=label):
                    self.assertLessEqual(new, parts[label])
            else:
                self.assertEqual(new, set(), f"{label} makes new chunks no part declares")


if __name__ == "__main__":
    unittest.main()
