"""DSCLOG's room (dos/dsclog.asm, DEVELOPMENT-INTERNALS.md's limits): its build fails only when a limit is
passed (a negative `times`), which says nothing until the port that fills it. These tests keep a margin in
the segment (`kept_end`, everything reached through CS) and in upper memory once installed (`UMB_KEPT`
against `UMB_ROOM`), so the change that comes near a limit fails here first, with the way out named (the
tail, code in the tail, the Loader's files: DEVELOPMENT-INTERNALS' "DSCLOG's segment"). As
test_dsclog2_room.py does for the sequel's helper (2026-11-27's code audit, R2). Also: the Python
constants that name a DSCLOG2 symbol agree with it (C-1)."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos")
SEGMENT = 0x10000
SEGMENT_MARGIN = 256    # bytes of the segment kept free (2026-11-27: 336 on the test branch, 640 here)
UMB_MARGIN = 32         # paragraphs of upper memory kept free (2026-11-27: 86 on the test branch)
# Names a Python module and DSCLOG2 both have for different things (kept, but not compared)
NOT_THE_SAME = {("ravlog", "SH_LEVELS"),     # (a header offset there; DSCLOG2's is the sheet's levels)
                ("ravarrows", "KNOWN_SEG")}  # (the load segment's + there; DSCLOG2's is DS less it)


def build_map(asm: str):
    """{section: {label: offset}} and {equ: value} of dos/ASM, from nasm's symbol map."""
    with tempfile.TemporaryDirectory() as tmp:
        src, out, mp = (os.path.join(tmp, n) for n in ("m.asm", "m.exe", "m.map"))
        with open(os.path.join(DOS, asm)) as f:
            source = f.read()
        with open(src, "w") as f:
            f.write(f"[map symbols {mp}]\n" + source)
        run = subprocess.run(["nasm", "-f", "bin", "-I", DOS + "/", "-o", out, src], capture_output=True, text=True)
        if run.returncode:
            raise AssertionError(run.stderr)
        with open(mp) as f:
            listing = f.read()
    sections, equs = {}, {}
    for block in listing.split("---- Section ")[1:]:
        name = block.split()[0]
        for line in block.splitlines()[1:]:
            parts = line.split()
            if len(parts) == 3 and all(c in "0123456789ABCDEF" for c in parts[1]):
                sections.setdefault(name, {})[parts[2]] = int(parts[1], 16)
    for line in listing.split("No Section")[1].split("---- Section")[0].splitlines():
        parts = line.split()
        if len(parts) == 2 and all(c in "0123456789ABCDEF" for c in parts[0]):
            equs[parts[1]] = int(parts[0], 16)
    return sections, equs


@unittest.skipUnless(shutil.which("nasm"), "needs nasm")
class RoomTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sections, cls.equs = build_map("dsclog.asm")

    def test_the_segment_keeps_its_margin(self):
        used = self.sections["image"]["kept_end"]
        self.assertLessEqual(used, SEGMENT - SEGMENT_MARGIN,
                             f"DSCLOG's segment is {used} bytes, {SEGMENT - used} free: under {SEGMENT_MARGIN}. "
                             "Move tables or long routines to its tail (DEVELOPMENT-INTERNALS: DSCLOG's segment)")

    def test_upper_memory_keeps_its_margin(self):
        kept, room = self.equs["UMB_KEPT"], self.equs["UMB_ROOM"]
        self.assertLessEqual(kept, room - UMB_MARGIN,
                             f"DSCLOG's upper memory once installed is {kept} paragraphs of {room}: under "
                             f"{UMB_MARGIN} spare. Free some (the tail's tables to the Loader's files)")


@unittest.skipUnless(shutil.which("nasm"), "needs nasm")
class SequelConstantsTests(unittest.TestCase):
    def test_python_names_agree_with_dsclog2(self):
        """Every int of the sequel's modules named as a DSCLOG2 equ has its value (NOT_THE_SAME aside)."""
        import importlib
        _, equs = build_map("dsclog2.asm")
        shared = 0
        names = ("ravager", "ravlog", "ravspells", "ravarrows")  # (those there are: ravarrows came with the spell arrows)
        for module in [importlib.import_module("dsloader." + n) for n in names
                       if os.path.exists(os.path.join(os.path.dirname(DOS), "dsloader", n + ".py"))]:
            short = module.__name__.rsplit(".", 1)[1]
            for name, value in vars(module).items():
                if name not in equs or (short, name) in NOT_THE_SAME:
                    continue
                if isinstance(value, int) and not isinstance(value, bool):
                    shared += 1
                    with self.subTest(module=short, name=name):
                        self.assertEqual(value, equs[name])
        self.assertGreater(shared, 20)  # (the check reads the map: a broken parse finds none)


if __name__ == "__main__":
    unittest.main()
