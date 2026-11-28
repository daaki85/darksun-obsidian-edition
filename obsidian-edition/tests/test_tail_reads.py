"""Each helper's tables are read through the segment they are in. DSCLOG and DSCLOG2 load in two parts:
the image (CS) and the tail (TAIL_SEG: CS + TAIL_PARAS once installed; `section tail` and `section tailz`).
A table read through the tail's segment that sits in the image reads the tail's bytes at the image's
offsets, with no error: on 2026-11-27 DSCLOG2's tail moved out of its segment (48b3673e) and SAVE_BANDS
stayed behind, so every saving throw the sequel worked out was nonsense (81/2/235/0/208) until 2026-11-28.

So, in a fresh build of each helper, with nasm's map telling each symbol's section:
- SAVE_BANDS is in the tail and is tables.RAV_SAVE_BANDS byte for byte (both games);
- no code reads a tail symbol through CS, or an image symbol through FS, from the image's code; the
  tail's own code (run with CS the tail, GS the image) reads no image symbol through CS and no tail
  symbol through GS;
- with DS loaded from TAIL_SEG (to the routine's POP DS or RET, and in the routines it calls, two deep),
  no image symbol is read or taken as an address;
- after TAIL_FS, no register holding an image symbol's address is read through FS.

The check reads the source line by line, so it is a net for the usual ways, not a proof. Needs nasm."""

import os
import re
import subprocess
import sys
import tempfile
import unittest

TESTS = os.path.dirname(os.path.abspath(__file__))
HERE = os.path.dirname(TESTS)
DOS = os.path.join(HERE, "dos")
sys.path.insert(0, HERE)
sys.path.insert(0, TESTS)

from dsloader import tables  # noqa: E402
from test_audit_builds import _need_nasm  # noqa: E402

HELPERS = ("dsclog.asm", "dsclog2.asm")
# (helper, symbol): read with DS the tail's but rightly so
ALLOWED = {
    # KIT_OF_SHEET copies a kit's name from the tail (DS) into KIT_LINE through CS ([cs:di]), and hands
    # back SI = KIT_LINE for EF_LINE, which reads it through CS.
    ("dsclog.asm", "kit_line"),
}
ID = re.compile(r"(?<![\w.])[A-Za-z_.][A-Za-z0-9_.]*")
LABEL = re.compile(r"^([A-Za-z_.][A-Za-z0-9_.]*):")
ENDS_DS = re.compile(r"\bpop\s+ds\b|\bret[fn]?\b|\biret\b|\bjmp\s+(far|\[)|mov\s+ds\s*,")
ENDS_FS = re.compile(r"\bret[fn]?\b|\biret\b|call\s+tail_fs\b|\bpop\s+fs\b|mov\s+fs\s*,")
SEG_READ = re.compile(r"\[\s*(cs|fs|gs)\s*:([^\]]*)\]")
FS_READ = re.compile(r"\[\s*fs\s*:([^\]]*)\]")
REG = re.compile(r"\b(bx|si|di|ebx|esi|edi)\b")


def build(source, folder=DOS):
    """SOURCE (in FOLDER) built with nasm's map: (the file's bytes, {symbol: (section, real, virtual)})."""
    with tempfile.TemporaryDirectory() as tmp:
        src, out, mp = (os.path.join(tmp, n) for n in ("m.asm", "m.exe", "m.map"))
        with open(src, "w") as f:
            f.write(f'[map symbols {mp}]\n%include "{source}"\n')
        subprocess.run(["nasm", "-f", "bin", "-I", folder + os.sep, "-o", out, src], check=True, cwd=folder)
        with open(out, "rb") as f:
            exe = f.read()
        with open(mp) as f:
            listing = f.read()
    symbols, section = {}, None
    for line in listing.splitlines():
        m = re.match(r"---- (?:Section (\S+)|No Section)", line)
        if m:
            section = m.group(1)
            continue
        parts = line.split()
        if section and len(parts) == 3 and all(re.fullmatch(r"[0-9A-F]+", p) for p in parts[:2]):
            symbols[parts[2]] = (section, int(parts[0], 16), int(parts[1], 16))
    return exe, symbols


def source_lines(path):
    """(file, line number, label or None, code without its label and comment), the includes in place."""
    folder = os.path.dirname(path)
    with open(path, errors="replace") as f:
        text = f.read().split("\n")
    for n, line in enumerate(text, 1):
        m = re.match(r'\s*%include\s+"([^"]+)"', line)
        if m:
            yield from source_lines(os.path.join(folder, m.group(1)))
            continue
        code = line.split(";")[0]
        label = LABEL.match(code)
        yield os.path.basename(path), n, label.group(1) if label else None, LABEL.sub("", code)


def wrong_reads(source, symbols, folder=DOS):
    """The reads of SOURCE through a segment its symbol is not in, as text."""
    src = list(source_lines(os.path.join(folder, source)))
    section_of = {k: v[0] for k, v in symbols.items()}
    starts, owner, where = {}, [], []
    parent, section = None, "image"
    for i, (_f, _n, label, code) in enumerate(src):
        m = re.match(r"\s*section\s+(\w+)", code)
        if m:
            section = m.group(1)
        if label and not label.startswith("."):
            parent = label
            starts[parent] = i
        owner.append(parent)
        where.append(section)
    bad = []

    def full(ident, i):
        return owner[i] + ident if ident.startswith(".") and owner[i] else ident

    def ds_tail(i0, why, depth, seen):
        for i in range(i0, len(src)):
            f, n, _label, code = src[i]
            if i > i0 and ENDS_DS.search(code):
                return
            call = re.match(r"\s*call\s+([A-Za-z_]\w*)\s*$", code)
            if call and depth < 2 and call.group(1) in starts and call.group(1) not in seen:
                seen.add(call.group(1))
                ds_tail(starts[call.group(1)], f"{why} -> {call.group(1)}", depth + 1, seen)
            body = re.sub(r"\[\s*(cs|es|fs|gs|ss)\s*:[^\]]*\]", "", code)  # (reads through another segment)
            if re.match(r"\s*(call|j\w+|loop\w*)\b", body):
                continue
            for ident in ID.findall(body):
                name = full(ident, i)
                if (section_of.get(name) == "image" and not name.startswith(f"{owner[i]}.")
                        and (source, name) not in ALLOWED):
                    bad.append(f"{f}:{n}: {name} (image) with DS the tail's ({why}): {code.strip()}")

    def fs_tail(i0, why):
        held = {}
        for i in range(i0 + 1, len(src)):
            f, n, _label, code = src[i]
            if ENDS_FS.search(code):
                return
            for mem in FS_READ.findall(code):
                for reg in REG.findall(mem):
                    if held.get(reg):
                        bad.append(f"{f}:{n}: {held[reg]} (image) read through FS the tail's ({why}): {code.strip()}")
            m = re.match(r"\s*(mov|lea)\s+(\w+)\s*,\s*(.*)$", code)
            if m:
                image = [x for x in ID.findall(m.group(3)) if section_of.get(x) == "image"]
                held[m.group(2)] = image[0] if image and "[" not in m.group(3) else None

    for i, (f, n, _label, code) in enumerate(src):
        if re.search(r"mov\s+ds\s*,\s*\[cs:\s*tail_seg\]", code):
            ds_tail(i, f"{f}:{n}", 0, set())
        if re.search(r"call\s+tail_fs\b", code):
            fs_tail(i, f"{f}:{n}")
        in_tail = where[i] in ("tail", "tailz")
        for seg, mem in SEG_READ.findall(code):
            for ident in ID.findall(mem):
                name = full(ident, i)
                sec = section_of.get(name)
                if sec is None:
                    continue
                tail = sec in ("tail", "tailz")
                if (seg == "cs" and tail != in_tail) or (seg == "gs" and in_tail and tail) or (
                        seg == "fs" and not tail and not in_tail):
                    bad.append(f"{f}:{n}: {name} ({sec}) through {seg.upper()}"
                               f"{' in the tail' if in_tail else ''}: {code.strip()}")
    return sorted(set(bad))


class TailReadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.built = {}

    def setUp(self):
        _need_nasm(self)

    def helper(self, source):
        if source not in self.built:
            self.built[source] = build(source)
        return self.built[source]

    def test_save_bands_in_the_tail(self):
        """Both helpers' SAVE_BANDS (SAVE_BASE's, read through TAIL_SEG) are in the tail, and are the
        Player's Handbook's (tables.RAV_SAVE_BANDS, the psionicists' set fifth)."""
        want = bytes(b for group in tables.RAV_SAVE_BANDS for first, saves in group for b in (first, *saves))
        for source in HELPERS:
            with self.subTest(source):
                exe, symbols = self.helper(source)
                self.assertEqual(symbols["save_bands"][0], "tail")
                self.assertEqual(symbols["save_bands_end"][0], "tail")
                start, end = symbols["save_bands"][1], symbols["save_bands_end"][1]
                self.assertEqual(exe[start:end], want)

    def test_every_table_through_its_own_segment(self):
        for source in HELPERS:
            with self.subTest(source):
                _exe, symbols = self.helper(source)
                self.assertEqual(wrong_reads(source, symbols), [])


if __name__ == "__main__":
    unittest.main()
