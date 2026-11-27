"""DSCLOG2's room (dos/dsclog2.asm, THE IMAGE'S PARTS): everything its handlers reach through CS, the
segment (the header and the code that stays, to IMAGE_END), has to fit 64 KB; the tables and buffers
kept outside it are the tail's (a section of its own, TAIL_PARAS paragraphs into the image, reached
through TAIL_FS), and the install is a third part (INSTALL_PARAS on, where the EXE header's CS:IP
starts it), not kept. These tests keep a margin in the segment, so that a port that would fill it fails
here first, with the way out named, rather than as a build that wraps past FFFFh (nasm's "word data
exceeds bounds") and a helper that hooks garbage; and they check that no code reads a part's labels
through the wrong segment."""

import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos")
ASM = os.path.join(DOS, "dsclog2.asm")
SEGMENT = 0x10000
MARGIN = 2048           # the room the segment must keep free (bytes): more code goes to the tail first
LABEL = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)(?::|\s+(?:db|dw|dd|times|resb)\b)")


def _sections(listing):
    """{section: {label: offset}} from nasm's map (labels with no dot: not the local ones)."""
    out = {}
    for block in listing.split("---- Section ")[1:]:
        name = block.split()[0]
        for line in block.splitlines()[1:]:
            parts = line.split()
            if len(parts) == 3 and all(c in "0123456789ABCDEF" for c in parts[1]) and "." not in parts[2]:
                out.setdefault(name, {})[parts[2]] = int(parts[1], 16)
    return out


@unittest.skipUnless(shutil.which("nasm"), "needs nasm")
class RoomTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            src, out, mp = (os.path.join(tmp, n) for n in ("m.asm", "m.exe", "m.map"))
            with open(ASM) as f:
                cls.source = f.read()
            with open(src, "w") as f:
                f.write(f"[map symbols {mp}]\n" + cls.source)
            run = subprocess.run(["nasm", "-f", "bin", "-I", DOS + "/", "-o", out, src],
                                 capture_output=True, text=True)
            cls.errors = run.stderr
            if run.returncode:
                raise AssertionError(run.stderr)
            with open(out, "rb") as f:
                cls.exe = f.read()
            with open(mp) as f:
                listing = f.read()
        cls.sections = _sections(listing)
        cls.equs = {}
        for line in listing.split("No Section")[1].split("---- Section")[0].splitlines():
            parts = line.split()
            if len(parts) == 2 and all(c in "0123456789ABCDEF" for c in parts[0]):
                cls.equs[parts[1]] = int(parts[0], 16)

    def test_no_warnings(self):
        """nasm says nothing: a word past FFFFh ("word data exceeds bounds") is the segment overflowing,
        a label's offset wrapped, the helper broken in the game."""
        self.assertEqual(self.errors.strip(), "", "nasm's warnings (the segment full? THE IMAGE'S PARTS)")

    def test_the_segment_keeps_its_margin(self):
        """The segment (the header to IMAGE_END, all reached through CS) leaves MARGIN of its 64 KB free;
        when a port takes it, move its tables and buffers to the tail (section tail; read through
        TAIL_FS), as the AD&D tables, the item names and the labels' slots are."""
        used = self.sections["image"]["image_end"]
        self.assertLessEqual(used, SEGMENT - MARGIN,
                             f"DSCLOG2's segment is {used} bytes, {SEGMENT - used} free: under {MARGIN}. "
                             "Move tables or buffers to its tail (THE IMAGE'S PARTS in dsclog2.asm)")

    def test_the_tail_and_the_install_fit_their_segments(self):
        for part, end in (("tail", "tail_end"), ("install", "install_end")):
            self.assertLessEqual(self.sections[part][end], SEGMENT, part)

    def test_the_parts_are_where_the_paragraphs_say(self):
        """The tail at TAIL_PARAS x 16 in the image (its signature first; the header's +1836 the same),
        the install at INSTALL_PARAS x 16, where the EXE header starts it (CS:IP), the stack past it."""
        exe, equs = self.exe, self.equs
        image = exe[32:]
        tail, install = equs["TAIL_PARAS"] * 16, equs["INSTALL_PARAS"] * 16
        self.assertEqual(tail, self.sections["image"]["image_end"])
        self.assertEqual(image[tail:tail + 12], b"DSCLOG2 TAIL")
        hdr = image.find(b"DSCLOGR1")
        self.assertEqual(hdr, 0)
        self.assertEqual(struct.unpack_from("<H", image, hdr + 1836)[0], equs["TAIL_PARAS"])
        self.assertEqual(install, tail + self.sections["tail"]["tail_end"])
        ip, cs = struct.unpack_from("<HH", exe, 0x14)
        self.assertEqual((cs, ip), (equs["INSTALL_PARAS"], self.sections["install"]["install"]))
        self.assertEqual(len(image), install + self.sections["install"]["install_end"])
        self.assertEqual(struct.unpack_from("<H", exe, 0x0E)[0] * 16, len(image))  # (SS: just past it)

    def test_no_label_read_through_the_wrong_segment(self):
        """The segment's code never names a tail or install label after "cs:" (the tail's are read
        through TAIL_FS, the install's are gone once it stays), and the install's code never names one
        of the segment's after "cs:" (its CS is its own: DS is the segment there). A port written
        before a table moved fails here, not in the game."""
        image, tail, install = (set(self.sections[s]) for s in ("image", "tail", "install"))
        wrong = {"image": tail | install, "tail": set(), "install": image | tail}
        section, found = "image", []
        for number, line in enumerate(self.source.splitlines(), 1):
            code = line.split(";")[0]
            m = re.match(r"\s*section\s+(\w+)", code)
            if m:
                section = m.group(1)
                continue
            for operand in re.findall(r"\[\s*cs\s*:([^\]]*)\]", code):
                names = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", operand)) & wrong.get(section, set())
                if names:
                    found.append(f"line {number} ({section}): {line.strip()}")
        self.assertEqual(found, [])


@unittest.skipUnless(shutil.which("nasm"), "needs nasm")
class InstallTests(unittest.TestCase):
    """The install, run as DOS starts the EXE, keeps the PSP, the segment and the tail (31h's DX), and
    sets the header's +1834 to the tail's segment for the Loader."""

    def test_tail_segment_and_what_stays(self):
        try:
            from test_far_init import ASMS, Machine, TSR, Uc
        except ImportError:
            self.skipTest("needs unicorn")
        if Uc is None:
            self.skipTest("needs unicorn")
        m = Machine(ASMS["DSCLOG2"], hma="given")
        self.assertEqual(m.install(), (0x31, 0))
        self.assertEqual(m.reg("DX"), 0x10 + m.sym["INSTALL_PARAS"])  # (the install's paragraph: all before it)
        tail_seg = struct.unpack("<H", m.mu.mem_read(TSR * 16 + 1834, 2))[0]
        self.assertEqual(tail_seg, TSR + m.sym["TAIL_PARAS"])
        self.assertEqual(bytes(m.mu.mem_read(tail_seg * 16, 12)), b"DSCLOG2 TAIL")


if __name__ == "__main__":
    unittest.main()
