"""Alagorn tells of Kreenfang and Shadowseeker (alagorn.py), on a script shaped as his: a part
for each kind with its queries, "none carried" and a menu whose stories end the loop."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import alagorn, gpl, icons, tome
from dsloader.kalzith import _Script

GOTO, MENU, SET, TEST, IF_NOT, END_IF, RETURN, BACK = 0x64, 0x48, 0x16, 0x18, 0x3E, 0x67, 0x15, 0x19
FIELDS = bytes(alagorn.HAS_PICTURE) + b"\x10" + bytes(16)  # (the game's field types: the picture's a word)


def query(picture):
    return ("op", gpl.Op(0, alagorn.QUERY, [("n", alagorn.PARTY), 77, 80, [(alagorn.HAS_PICTURE, 4, ("n", picture))]]))


def zero(*locals_):
    return alagorn._zero(list(locals_))


def alagorns(last="Other", kinds=alagorn.KINDS, done=alagorn.DONE, split=False):
    """Two kinds, each of two items: (part, menu, stories), the game's way (SPLIT: the test for
    none carried in two, each of a local, as script 212's clothes)."""
    s = _Script()
    s.op(BACK)  # (as script 212 starts: each part after a 19h, where his talk calls it)
    for k, kind in enumerate(kinds):
        first = kind.first_reply.strip()
        s.op(SET, query(-30000 - 2 * k), ("var", 14, 0))
        s.op(SET, query(-30001 - 2 * k), ("var", 14, 1))
        if split:
            s.op(TEST, zero(0))
            s.op(IF_NOT, ("label", f"has {k}"))
            s.op(TEST, zero(1))
        else:
            s.op(TEST, zero(0, 1))
        s.op(IF_NOT, ("label", f"has {k}"))
        s.op(0x4F, ("n", 115), ("str", kind.none_text))
        s.op(BACK)
        s.label(f"has {k}")
        s.op(END_IF)
        s.op(0x4F, ("n", 115), ("str", "Let me see. "))
        s.label(f"loop {k}")
        s.op(TEST, ("expr", ["(", ("var", 0x8E, done), "==", ("n", 0), ")"]))
        s.op(0x63, ("label", f"out {k}"))
        s.op(MENU, {"before": [], "title": ("str", "What item do you show him?"), "replies": [
            {"text": ("str", f"  {name}"), "goto": ("label", f"story {k} {i}"), "if": ("var", 0x8E, i),
             "before": [], "after": []} for i, name in enumerate((first, last))]})
        s.op(GOTO, ("label", f"loop {k}"))
        s.label(f"out {k}")
        s.op(BACK)
    for k in range(len(kinds)):
        for i in range(2):
            s.label(f"story {k} {i}")
            s.op(0x4F, ("n", 115), ("str", f"Story {k} {i}. "))
            s.op(SET, ("n", 0), ("var", 14, i))
            s.op(TEST, zero(1 - i))
            s.op(IF_NOT, ("label", f"end {k} {i}"))
            s.op(SET, ("n", 1), ("var", 14, done))
            s.label(f"end {k} {i}")
            s.op(END_IF)
            s.op(RETURN)
    return s.bytes(end=False)


class AlagornTests(unittest.TestCase):
    def setUp(self):
        self.script = alagorns()
        self.out = alagorn.with_items(self.script, FIELDS, alagorn.kinds(arms=True, magic=False))
        self.ops = gpl.decode(self.script, FIELDS)
        r = gpl._Reader(self.out, FIELDS)
        r.i = len(self.script)
        self.added = []
        while r.i < len(self.out):
            self.added.append(gpl._op(r))

    def jump_from(self, op):
        """Where a command of the game's now jumps (None: left as it was)."""
        if self.out[op.at] == self.script[op.at]:
            return None
        r = gpl._Reader(self.out, FIELDS)
        r.i = op.at
        jump = gpl._op(r)
        self.assertEqual(jump.code, GOTO)
        return jump.args[0][1]

    def test_game_commands_stay(self):
        """The game's script is all there (but the commands made jumps), longer only at its end."""
        self.assertGreater(len(self.out), len(self.script))
        jumped = [op for op in self.ops if self.jump_from(op) is not None]
        # each kind: its first test, its menu, its two stories' tests
        self.assertEqual([op.code for op in jumped], [TEST, MENU, TEST, MENU, TEST, TEST, TEST, TEST])
        self.assertTrue(all(self.jump_from(op) >= len(self.script) for op in jumped))

    def test_items_looked_for_by_picture(self):
        sets = [op for op in self.added if op.code == SET and op.args[0][0] == "op"]
        self.assertEqual([alagorn._sets(op) for op in sets],
                         [(2, alagorn._picture("Shadowseeker")), (2, alagorn._picture("Kreenfang"))])

    def test_menus_have_the_new_reply(self):
        menus = [op.args[0]["replies"] for op in self.added if op.code == MENU]
        self.assertEqual([[r["text"][1] for r in m] for m in menus],
                         [["  Darkflame", "  Other", "  Shadowseeker"],
                          ["  Balkazar's Staff", "  Other", "  Kreenfang"]])
        self.assertEqual([m[2]["if"] for m in menus], [("var", 0x8E, 2)] * 2)

    def test_stories_wait_for_the_new_one(self):
        tests = [alagorn._locals(op.args[0]) for op in self.added if op.code == TEST]
        self.assertIn([1, 2], tests)  # (the first story: the second and the new one left)
        self.assertIn([0, 2], tests)
        self.assertIn([0, 1, 2], tests)  # (the new story, and none carried)

    def test_new_story_said(self):
        lines = " ".join(s for s in gpl.strings(self.added))
        self.assertIn("Shadowseeker! The head guards of the Draj slave pens", lines)
        self.assertIn("Kreenfang!", lines)

    def test_once(self):
        self.assertEqual(alagorn.with_items(self.out, FIELDS), self.out)

    def test_the_worlds_too(self):
        """With the world's magic weapons: Greenbright and the Flame Blade with the swords, Gutterknot, Deepbiter,
        Windlash and the axes with the weapons, each its own local and story, before a "Nothing" reply."""
        script = alagorns(last=alagorn.NOTHING.strip())
        out = alagorn.with_items(script, FIELDS)
        r = gpl._Reader(out, FIELDS)
        r.i = len(script)
        added = []
        while r.i < len(out):
            added.append(gpl._op(r))
        menus = [[x["text"][1] for x in op.args[0]["replies"]] for op in added if op.code == MENU]
        self.assertEqual(menus, [["  Darkflame", "  Shadowseeker", "  Greenbright", "  Flame Blade", "  Mindshard",
                                  "  Stillwater", alagorn.NOTHING],
                                 ["  Balkazar's Staff", "  Kreenfang", "  Gutterknot", "  Deepbiter", "  Windlash",
                                  "  Drakejaw", "  Glasshewer", "  Headsman", "  Galefang", "  Linebreaker",
                                  "  Thornwall", alagorn.NOTHING]])
        sets = [alagorn._sets(op) for op in added if op.code == SET and op.args[0][0] == "op"]
        self.assertEqual(sets, [(2, alagorn._picture("Shadowseeker")), (3, alagorn._picture("Greenbright")),
                                (4, alagorn._picture("Flame Blade")), (5, alagorn._picture("Mindshard")),
                                (6, alagorn._picture("Stillwater")),
                                (2, alagorn._picture("Kreenfang")), (3, alagorn._picture("Gutterknot")),
                                (4, alagorn._picture("Deepbiter")), (5, alagorn._picture("Windlash")),
                                (6, alagorn._picture("Drakejaw")), (7, alagorn._picture("Glasshewer")),
                                (8, alagorn._picture("Headsman")), (9, alagorn._picture("Galefang")),
                                (10, alagorn._picture("Linebreaker")), (11, alagorn._picture("Thornwall"))])
        lines = " ".join(gpl.strings(added))
        for name in ("Greenbright!", "A Flame Blade!", "Mindshard!", "Stillwater!", "Gutterknot!", "Deepbiter!",
                     "Windlash!", "Drakejaw!", "Glasshewer!", "Headsman!", "Galefang!", "Linebreaker!", "Thornwall!"):
            self.assertIn(name, lines)
        self.assertIn([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], [alagorn._locals(op.args[0]) for op in added if op.code == TEST])

    def test_switches(self):
        """Only the switches' items; none, no change."""
        self.assertEqual([[i for i, _ in k.items] for k in alagorn.kinds(arms=False, magic=True)],
                         [["Greenbright", "Flame Blade", "Mindshard", "Stillwater"],
                          ["Gutterknot", "Deepbiter", "Windlash", "Drakejaw", "Glasshewer", "Headsman", "Galefang",
                           "Linebreaker", "Thornwall"]])
        self.assertEqual(alagorn.kinds(arms=False, magic=False), ())
        self.assertEqual(alagorn.script_chunks({("GPL ", alagorn.SCRIPT): self.script}, FIELDS, False, False), {})

    def new_ops(self, script, kinds):
        out = alagorn.with_items(script, FIELDS, kinds)
        r = gpl._Reader(out, FIELDS)
        r.i = len(script)
        added = []
        while r.i < len(out):
            added.append(gpl._op(r))
        return added

    def test_rings_armour_clothes_and_other(self):
        """Script 212's kinds: the rings of protection, the Warden's Plate, the cloaks, boots,
        bracers, circlet and crown, and the tome; their locals past the loop's own (6 there), and
        its test for none carried in two."""
        kinds = alagorn.kinds(script=alagorn.OTHER_SCRIPT)
        script = alagorns(last="Nothing", kinds=kinds, done=6, split=True)
        self.assertTrue(alagorn._nothing({"text": ("str", "Nothing")}))  # (script 212's, unindented)
        added = self.new_ops(script, kinds)
        menus = [[x["text"][1] for x in op.args[0]["replies"]] for op in added if op.code == MENU]
        self.assertEqual(menus, [["  Light of Dawn", "  Ring of Protection", "  Nothing"],
                                 ["  Tanelyv's Armor", "  Inixhide", "  Warden's Helm", "  Warden's Arms", "  Warden's Legs",
                                  "  Warden's Chest", "  Nothing"],
                                 ["  El's Shield", "  Gutterward", "  Ironbulwark", "  Nothing"],
                                 ["  Belt of Might", "  Cloak of Protection", "  Cloak of Elvenkind",
                                  "  Boots of Elvenkind", "  Bracers of Defense", "  Arrowbane", "  Sunking Crown",
                                  "  Ashen Robe", "  Veiled Robe", "  Nothing"],
                                 ["  Orb of Knowledge", "  Tome of Understanding", "  Nothing"]])
        locals_ = [op.args[1][2] for op in added if op.code == SET and op.args[1][:2] == ("var", 14)
                   and op.args[0][0] in ("op", "expr")]
        self.assertEqual(locals_, [2, 2, 3, 4, 5, 7, 2, 3, 2, 3, 4, 5, 7, 8, 9, 10, 2])
        sets = [alagorn._sets(op) for op in added if op.code == SET and op.args[0][0] == "op"]
        self.assertIn((2, -tome.TOME_OBJECT), sets)  # (the tome by its own object's picture)
        flags = [op.args for op in added if op.code == SET and op.args[0] == ("n", 1)]
        self.assertTrue(flags and all(f == [("n", 1), ("var", 14, 6)] for f in flags))
        lines = " ".join(gpl.strings(added))
        for name in ("A Ring of Protection!", "Inixhide!", "The Warden's Chest!", "Gutterward!", "Ironbulwark!", "A Cloak of Protection!", "A Cloak of Elvenkind!",
                     "Bracers of Defense!", "Arrowbane!", "The Sunking Crown!", "The Tome of Understanding!"):
            self.assertIn(name, lines)

    def test_either_ring(self):
        """One line for the Rings of Protection, shown with either (the arena's, Pehtucl's): the
        two queries joined with "or", as the game's own tests join them."""
        value = alagorn._carried("Ring of Protection")
        self.assertEqual(value[0], "expr")
        parts = value[1]
        self.assertEqual([p for p in parts if isinstance(p, str)], ["(", ")", "or", "(", ")"])
        pictures = [p[1].args[3][0][2][1] for p in parts if isinstance(p, tuple)]
        self.assertEqual(pictures, [icons.PICTURES["Ring of Protection +1"] - 0x10000,
                                    icons.PICTURES["Pehtucl's Ring of Protection +1"] - 0x10000])
        self.assertEqual(alagorn._carried("Arrowbane")[0], "op")  # (one picture: the query alone)
        self.assertEqual([[i for i, _ in k.items] for k in alagorn.kinds(False, False, alagorn.OTHER_SCRIPT)],
                         [["Ring of Protection"], ["Inixhide"], ["Cloak of Protection"]])
        self.assertEqual(alagorn.kinds(False, False, alagorn.OTHER_SCRIPT, pens=False), ())

    def test_split_test_kept(self):
        """A test for none carried in two (script 212's clothes): both tests again, each to the
        game's own place (its ifs and elses stay nested), the new items in the second."""
        kinds = alagorn.kinds(script=alagorn.OTHER_SCRIPT)
        script = alagorns(last="Nothing", kinds=kinds, done=6, split=True)
        game = gpl.decode(script, FIELDS)
        targets = [op.args[0] for op in game if op.code == IF_NOT][:2]
        added = self.new_ops(script, kinds)
        tests = [(alagorn._locals(a.args[0]), b.args[0]) for a, b in zip(added, added[1:])
                 if a.code == TEST and b.code == IF_NOT]
        self.assertEqual(tests[:2], [([0], targets[0]), ([1, 2], targets[1])])

    def test_past_the_loops_local(self):
        """The new items' locals skip the loop's own."""
        kinds = alagorn.kinds(script=alagorn.OTHER_SCRIPT)
        kinds = tuple(k for k in kinds if k.first_reply in (alagorn.ARMOUR[0], alagorn.CLOTHES[0]))
        added = self.new_ops(alagorns(last="Nothing", kinds=kinds, done=4), kinds)
        sets = [alagorn._sets(op)[0] for op in added if op.code == SET and op.args[0][0] == "op"]
        self.assertEqual(sets, [2, 3, 5, 6, 7, 2, 3, 5, 6, 7, 8, 9, 10])

    def test_past_the_locals_flags(self):
        """Items past the script's locals (the loop's own one of them) kept in the Loader's flags
        from FLAGS on: set by their query, shown by them, cleared by their story, counted in the
        tests for none carried and none left."""
        from unittest import mock
        kinds = alagorn.kinds(arms=False, magic=True)
        script = alagorns(last=alagorn.NOTHING.strip(), kinds=kinds, done=6)
        with mock.patch.object(alagorn, "LOCALS", 11):  # (locals 2-10 less the loop's: eight for nine weapons)
            added = self.new_ops(script, kinds)
        weapons = [op for op in added if op.code == MENU][1].args[0]["replies"]
        shown = [r["if"] for r in weapons if r["text"][1].strip() in ("Linebreaker", "Thornwall")]
        self.assertEqual(shown, [("var", 142, 10), ("var", alagorn.FLAG_READ, alagorn.FLAGS)])
        flags = [op for op in added if op.code == SET and op.args[1] == ("var", alagorn.FLAG_SET, alagorn.FLAGS)]
        self.assertEqual([op.args[0][0] for op in flags], ["op", "n"])  # (its query; its story's clearing)
        tests = [op.args[0] for op in added if op.code == TEST and ("var", alagorn.FLAG_READ, alagorn.FLAGS) in op.args[0][1]]
        self.assertTrue(tests)

    def test_every_magic_item_told(self):
        """Each magic item the Loader adds has a story: named ones their own, the rings and cloaks
        of protection one for their kind (whichever the party carries), as the bracers."""
        told = {n for kinds in (alagorn.ARMS, alagorn.PENS, alagorn.MAGIC) for items in kinds.values()
                for name, _ in items for n in alagorn.PICTURES_OF.get(name, (name,))}
        self.assertEqual(told, {"Shadowseeker", "Kreenfang", "Greenbright", "Flame Blade", "Gutterknot", "Deepbiter",
                                "Windlash", "Bracers of Defense", "Arrowbane", "Sunking Crown", "Warden's Helm",
                                "Warden's Arms", "Warden's Legs", "Warden's Chest", "Cloak of Elvenkind",
                                "Boots of Elvenkind", "Tome of Understanding", "Ring of Protection +1",
                                "Pehtucl's Ring of Protection +1", "Cloak of Protection +1", "Inixhide",
                                "Drakejaw", "Glasshewer", "Headsman", "Galefang", "Mindshard", "Stillwater",
                                "Linebreaker", "Thornwall", "Ashen Robe", "Veiled Robe", "Gutterward", "Ironbulwark"})
        for name in told - {"Tome of Understanding"}:
            self.assertIn(name, icons.PICTURES)

    def test_copies(self):
        """Script 212's clothes told by a copy (220), its rings and other items by another (221),
        each called from his talk (211) at the same place; its armour and shields by 212 itself."""
        kinds = alagorn.kinds(script=alagorn.OTHER_SCRIPT)
        script = alagorns(last="Nothing", kinds=kinds, done=6)
        entries = [alagorn._entry(script, FIELDS, k) for k in kinds]
        self.assertEqual(len(set(entries)), 5)
        talk = _Script()
        for entry in entries:
            talk.op(alagorn.CALL, ("n", entry), ("n", alagorn.OTHER_SCRIPT))
        talk = talk.bytes(end=False)
        out = alagorn.script_chunks({("GPL ", 212): script, ("GPL ", 211): talk}, FIELDS)
        self.assertEqual(sorted(out), [("GPL ", 211), ("GPL ", 212), ("GPL ", 220), ("GPL ", 221)])
        calls = [op.args for op in gpl.decode(out[("GPL ", 211)], FIELDS)]
        self.assertEqual(calls, [[("n", entries[0]), ("n", 221)], [("n", entries[1]), ("n", 212)],
                                 [("n", entries[2]), ("n", 212)], [("n", entries[3]), ("n", 220)],
                                 [("n", entries[4]), ("n", 221)]])
        reply = lambda name: gpl.encode_expr(("str", f"  {name}"))
        for number, has, hasnt in ((212, "Warden's Helm", "Arrowbane"), (212, "Ironbulwark", "Arrowbane"), (220, "Arrowbane", "Tome of Understanding"),
                                   (221, "Tome of Understanding", "Warden's Helm"),
                                   (221, "Ring of Protection", "Cloak of Protection")):
            self.assertIn(reply(has), out[("GPL ", number)])
            self.assertNotIn(reply(hasnt), out[("GPL ", number)])
        # without his talk, no copies (nothing would call them)
        out = alagorn.script_chunks({("GPL ", 212): script}, FIELDS)
        self.assertEqual(sorted(out), [("GPL ", 212)])

    def test_other_script_unchanged(self):
        other = _Script()
        other.op(0x4F, ("n", 115), ("str", "Hello. "))
        script = other.bytes(end=False)
        self.assertEqual(alagorn.with_items(script, FIELDS), script)
        self.assertEqual(alagorn.script_chunks({("GPL ", 1): script}, FIELDS), {})


if __name__ == "__main__":
    unittest.main()
