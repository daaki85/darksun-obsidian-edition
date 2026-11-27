"""DSCLOG's header against the Loader, read from a fresh build's symbol map: every field's offset as
its comment in dsclog.asm gives it (the "+N" the Loader's TSR_* constants are copied from), every
TSR_* constant of the Loader's modules the offset of its own field, and the tables the two keep alike:
the spell arrows' spells and names (DSCLOG's ARROW_SPELLS and ARROW_NAME, spellarrows.ARROWS).

Skipped without nasm, unless DSUN_REQUIRE_NASM is set (the workflows set it), as test_audit_builds."""

import ast
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

TESTS = os.path.dirname(os.path.abspath(__file__))
HERE = os.path.dirname(TESTS)
DOS = os.path.join(HERE, "dos")
ASM = os.path.join(DOS, "dsclog.asm")
sys.path.insert(0, HERE)

from dsloader import names, spellarrows  # noqa: E402

_built = {}

# The Loader's constant for each field from POISON_USED (+1860) on, by the field's own label
FIELDS_BY_NAME = {"TSR_POISON_USED": "poison_used", "TSR_BAD_LUCK": "bad_luck", "TSR_LOADER_BEAT": "loader_beat",
                  "TSR_GEAR_WHO": "gear_who", "TSR_A20_LOST": "a20_lost",
                  "TSR_QS_KEYS": "qs_keys", "TSR_QS_SEQ": "qs_seq", "TSR_SAVE_REQ": "save_req",
                  "TSR_SAVE_OFF": "save_off", "TSR_SQUARES_ON": "squares_on",
                  "TSR_FIG_DUE": "fig_due"}


def symbols():
    """{name: value} for every label (its offset in DSCLOG's segment) and EQU of a build of
    dsclog.asm with a symbol map."""
    if "sym" not in _built:
        with tempfile.TemporaryDirectory() as tmp:
            src, out, mp = (os.path.join(tmp, n) for n in ("m.asm", "m.exe", "m.map"))
            with open(ASM, encoding="latin-1") as f:
                text = f.read()
            with open(src, "w", encoding="latin-1") as f:
                f.write(f"[map all {mp}]\n" + text)
            subprocess.run(["nasm", "-f", "bin", "-I", DOS + os.sep, "-o", out, src], check=True)
            with open(mp) as f:
                listing = f.read()
        sym = {}
        for line in listing.splitlines():
            parts = line.split()
            hexes = [p for p in parts[:-1] if re.fullmatch(r"[0-9A-F]+", p)]
            if len(parts) in (2, 3) and len(hexes) == len(parts) - 1:
                sym.setdefault(parts[-1], int(hexes[-1], 16))  # (a label's virtual address: its offset)
        _built["sym"] = sym
    return _built["sym"]


def header_fields():
    """[(label, offset its comment gives)] from "hdr:" to the text buffer's comment."""
    with open(ASM, encoding="latin-1") as f:
        lines = f.read().splitlines()
    start = lines.index("hdr:")
    out = []
    for line in lines[start + 1:]:
        if line.startswith("; TEXT BUFFER"):
            break
        m = re.match(r"^(\w+):?\s+(?:db|dw|dd|times)\b.*?;\s*\+(\d+)\b", line) or \
            re.match(r"^(\w+):\s*;\s*\+(\d+)\b", line)
        if m:
            out.append((m.group(1), int(m.group(2))))
    return out


def loader_constants():
    """[(module, name, value)] for every TSR_* the Loader's modules set to a number."""
    out = []
    for path in sorted(glob.glob(os.path.join(HERE, "dsloader", "*.py"))):
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            for target in node.targets:
                if isinstance(target, ast.Name):
                    pairs = [(target, node.value)]
                elif isinstance(target, ast.Tuple) and isinstance(node.value, ast.Tuple):
                    pairs = list(zip(target.elts, node.value.elts))
                else:
                    pairs = []
                for name, value in pairs:
                    if isinstance(name, ast.Name) and name.id.startswith("TSR_") \
                            and isinstance(value, ast.Constant) and isinstance(value.value, int):
                        out.append((os.path.basename(path), name.id, value.value))
    return out


# The TSR_* constants whose field has another name: {constant: field}.
ALIASES = {
    "TSR_ATTACK": "attack_seq", "TSR_BACK": "back_seq", "TSR_BIG": "big_off", "TSR_BLAST": "blast_hp",
    "TSR_BUILD": "dark_build", "TSR_CREATING": "lv_creating", "TSR_DAC": "dac_off",
    "TSR_DANCE": "kit_dance", "TSR_KEYS": "panel_keys", "TSR_LABELS": "lbl_off",
    "TSR_LARGE": "large_off", "TSR_LEARN": "learn_seq", "TSR_LIGHT": "light_off",
    "TSR_MOUSE": "panel_mx", "TSR_ON": "shadows_on", "TSR_PAN": "pan_x", "TSR_RED": "red_off",
    "TSR_RING_TAB": "ring_tab_off", "TSR_TAB": "tab_seq", "TSR_TABLE": "shadow_tab_off",
    "TSR_TARGET": "hit_target", "TSR_TRIES": "rl_tries", "TSR_TRIES_SEQ": "rl_seq",
    "TSR_WILD": "kit_wild",
}


class HeaderTests(unittest.TestCase):
    def setUp(self):
        if shutil.which("nasm"):
            return
        if os.environ.get("DSUN_REQUIRE_NASM"):
            self.fail("nasm is not on the PATH (DSUN_REQUIRE_NASM is set)")
        self.skipTest("needs nasm")

    def test_fields_where_their_comments_say(self):
        """Each field at the offset its "+N" says, from the header's start; in order, none twice."""
        sym = symbols()
        fields = header_fields()
        self.assertGreater(len(fields), 150)
        wrong = [f"{name}: +{said}, built at +{sym[name] - sym['hdr']}" for name, said in fields
                 if sym.get(name, -1) - sym["hdr"] != said]
        self.assertEqual(wrong, [])
        offsets = [said for _, said in fields]
        self.assertEqual(offsets, sorted(set(offsets)))

    def test_loader_constants_name_fields(self):
        """Every TSR_* constant of the Loader's is the offset of its own field: TSR_NAME the field
        "name" (lower case), or the field ALIASES gives it (a field moved or a constant naming the
        wrong field would read another field)."""
        at = dict(header_fields())
        found = loader_constants()
        self.assertGreater(len(found), 100)
        stray = []
        for module, name, value in found:
            field = ALIASES.get(name, name[4:].lower())
            if at.get(field) != value:
                stray.append(f"{module} {name} = {value}: {field} is at +{at.get(field)}")
        self.assertEqual(stray, [])
        self.assertEqual(sorted(set(ALIASES) - {name for _, name, _ in found}), [])  # (none stale)

    def test_same_name_same_field(self):
        """A TSR_* name used in more than one module is the same field in each."""
        seen = {}
        for module, name, value in loader_constants():
            seen.setdefault(name, set()).add(value)
        self.assertEqual({name: values for name, values in seen.items() if len(values) > 1}, {})

    def test_named_constants_are_their_own_fields(self):
        """The constants of the fields at the header's end, each against the field of its own name
        (two branches once added fields at the same offsets, and every constant still named a
        field: the other branch's)."""
        sym = symbols()
        found = {name: value for _, name, value in loader_constants()}
        for name, field in FIELDS_BY_NAME.items():
            self.assertIn(name, found)
            self.assertEqual(found[name], sym[field] - sym["hdr"], (name, field))
        last = max(said for _, said in header_fields())
        self.assertEqual(last, max(sym[field] - sym["hdr"] for field in FIELDS_BY_NAME.values()),
                         "a field after the last one named here: add it to FIELDS_BY_NAME")

    def test_spell_arrows(self):
        """DSCLOG's ARROW_SPELLS (the spell each kind of spell arrow casts, in order) and ARROW_NAME
        (the first kind's name entry, the rest after it) are spellarrows.ARROWS'."""
        sym = symbols()
        with open(os.path.join(DOS, "DSCLOG.EXE"), "rb") as f:
            exe = f.read()
        image = exe[int.from_bytes(exe[8:10], "little") * 16:]
        at = sym["arrow_spells"]
        self.assertEqual(list(image[at:at + len(spellarrows.ARROWS)]), [a.spell for a in spellarrows.ARROWS])
        self.assertEqual([a.name for a in spellarrows.ARROWS],
                         [sym["ARROW_NAME"] + i for i in range(len(spellarrows.ARROWS))])
        self.assertEqual(sym["NAMES_OWN"], names.OWN)
        self.assertEqual(sym["NAMES_EXTRA"], names.EXTRA)  # (the names DSCLOG lists, counted)


if __name__ == "__main__":
    unittest.main()
