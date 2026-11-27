"""dos/shared_routines.inc: a routine DSCLOG and DSCLOG2 have the same, line for line, is written once
there (a macro, SHARED_name, expanded where each helper had it), so a fix to it reaches both helpers.
This fails on a routine written the same in both helpers' sources but not shared (the code audit of
2026-11-27, S5), and on a shared one either helper no longer expands."""
import os
import re
import unittest

DOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos")
LABEL = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):")
OTHER = re.compile(r"^(section|%|[A-Za-z_]\w*\s+(equ|db|dw|dd|times|resb)\b)")


def routines(path: str) -> dict:
    """{label: its lines}: each top-level label's lines to the next label, section, directive or
    data line, the comments and blank lines at its end left out (the next routine's heading)."""
    out, name, body = {}, None, []
    for line in open(path, encoding="latin-1").read().split("\n"):
        m = LABEL.match(line)
        if m or OTHER.match(line):
            if name:
                out[name] = body
            name, body = (m.group(1), [line]) if m else (None, [])
        elif name is not None:
            body.append(line)
    if name:
        out[name] = body
    for lines in out.values():
        while lines and (not lines[-1].strip() or lines[-1].lstrip().startswith(";")):
            lines.pop()
    return out


class SharedRoutines(unittest.TestCase):
    def test_none_written_twice(self):
        sl, sequel = (routines(os.path.join(DOS, f)) for f in ("dsclog.asm", "dsclog2.asm"))
        twice = sorted(k for k in sl if k in sequel and sl[k] == sequel[k] and len(sl[k]) > 2
                       and not any(line.lstrip().startswith("%") for line in sl[k]))
        self.assertEqual(twice, [], "the same in both helpers: move them into shared_routines.inc")

    def test_each_expanded_in_both(self):
        shared = re.findall(r"^%macro (SHARED_\w+) 0", open(os.path.join(DOS, "shared_routines.inc")).read(), re.M)
        self.assertTrue(shared)
        for helper in ("dsclog.asm", "dsclog2.asm"):
            src = open(os.path.join(DOS, helper), encoding="latin-1").read()
            for name in shared:
                with self.subTest(helper=helper, routine=name):
                    self.assertEqual(len(re.findall(rf"^\s+{name}\s*$", src, re.M)), 1)


if __name__ == "__main__":
    unittest.main()
