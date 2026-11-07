"""Pehtucl's chest, locked and trapped (pehtuclchest.py): its script, its USE command in the pens'
master script, the poison needle's object, and its two flags clear of Alagorn's."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import dataitems, gpl, kalzith, pehtuclchest as chest

GPLDATA = os.environ.get("DSUN_GPLDATA")
OBJECTS = os.environ.get("DSUN_OBJECTS")


def flags_in(ops):
    """The flags a script's commands read or set (vars 13 and 141)."""
    out = set()
    for op in gpl.walk(ops):
        for arg in _args(op.args):
            if isinstance(arg, tuple) and len(arg) == 3 and arg[0] == "var" and arg[1] in (13, 141):
                out.add(arg[2])
    return out


def _args(x):
    if isinstance(x, tuple):
        yield x
        for y in x:
            yield from _args(y)
    elif isinstance(x, list):
        for y in x:
            yield from _args(y)
    elif isinstance(x, dict):
        for y in x.values():
            yield from _args(y)
    elif isinstance(x, gpl.Op):
        yield from _args(x.args)


class ScriptTests(unittest.TestCase):
    def test_decodes(self):
        """The script decodes whole, opens as the game's do, and uses only its two flags."""
        ops = gpl.decode(chest.script(), b"")
        self.assertEqual(ops[0].code, kalzith.BEGIN)
        self.assertEqual(flags_in(ops), {chest.DISARMED, chest.UNLOCKED})

    def test_checks_and_needle(self):
        """Its thief checks are open locks and find/remove traps by the one using it; the needle is
        the Loader's trap object, set off with the game's trap action."""
        ops = list(gpl.walk(gpl.decode(chest.script(), b"")))
        actions = [[a[1] for a in op.args if isinstance(a, tuple) and a[0] == "n"]
                   for op in ops if op.code == gpl.DO_ACTION]
        self.assertIn([gpl.ACTION_SKILL, chest.OPEN_LOCKS, chest.LOCK_BONUS], [a for a in actions if len(a) == 3])
        self.assertIn([gpl.ACTION_SKILL, chest.FIND_TRAPS, chest.TRAP_BONUS], [a for a in actions if len(a) == 3])
        self.assertIn([gpl.ACTION_TRAP, -chest.TRAP_OBJECT], [a[:2] for a in actions])

    def test_use_command_once_at_the_end(self):
        """The USE command goes in just before the master script's end, once, nothing of the game's
        moved."""
        master = gpl.encode_op((0x6E, [("n", 1), ("n", 5), ("n", -7)])) + gpl.encode_op((kalzith.END, []))
        out = chest.with_use(master)
        self.assertEqual(out[:len(master) - 1], master[:-1])
        ops = gpl.decode(out, b"")
        self.assertEqual((ops[-2].code, [a[1] for a in ops[-2].args]),
                         (chest.USE, [kalzith.START, chest.SCRIPT, -chest.OBJECT]))
        self.assertEqual(chest.with_use(out), out)


class WatchTests(unittest.TestCase):
    """Once the lock is picked (UNLOCKED), the chest's item record is a chest again: the game opens it."""

    def setUp(self):
        import struct
        from dsloader import game
        self.struct, self.game = struct, game
        DS, ITEMS = 0x1000, 0x30000
        mem = bytearray(0x40000)
        struct.pack_into("<HH", mem, DS * 16 + game.ITEMS_PTR, ITEMS & 0xF, ITEMS >> 4)
        self.at = ITEMS + 7 * game.ITEM_SIZE
        struct.pack_into("<h", mem, self.at, -chest.OBJECT)
        struct.pack_into("<H", mem, self.at + game.ITEM_TYPE, chest.SHUT_TYPE)
        self.mem, self.flags = mem, set()

        class Guest:
            def read(g, addr, n):
                return bytes(mem[addr:addr + n])

            def write(g, addr, data):
                mem[addr:addr + len(data)] = data

        test = self

        class GD:
            guest, ds = Guest(), DS

            def region(gd):
                return chest.REGION

            def flags_ready(gd):
                return True

            def flag(gd, n):
                return n in test.flags
        self.gd = GD()

    def kind(self):
        return self.struct.unpack_from("<H", self.mem, self.at + self.game.ITEM_TYPE)[0]

    def test_opened_once_unlocked(self):
        chest.watch(self.gd)
        self.assertEqual(self.kind(), chest.SHUT_TYPE)  # (still locked)
        self.flags.add(chest.UNLOCKED)
        chest.watch(self.gd)
        self.assertEqual(self.kind(), chest.CHEST_TYPE)


@unittest.skipUnless(OBJECTS and os.path.isfile(OBJECTS), "needs the game's SEGOBJEX.GFF (DSUN_OBJECTS)")
class NeedleTests(unittest.TestCase):
    def test_poison_needle(self):
        """A copy of the game's trap object 2039 under its own number: 2d6 of poison on its square
        (the game's is 4d6 of poison: 04h)."""
        from dsloader import gff
        with open(OBJECTS, "rb") as f:
            chunks = gff.read_gff(f.read())
        self.assertNotIn(("OJFF", chest.TRAP_OBJECT), chunks)
        out = chest.object_chunks(chunks)
        self.assertEqual(out[("OJFF", chest.TRAP_OBJECT)], chunks[("OJFF", chest.GAME_TRAP)])
        item = out[("RDFF", chest.TRAP_OBJECT)][dataitems.HEADER.size:]
        self.assertEqual(item[chest.TRAP_BYTE], 0x02)
        self.assertEqual(chunks[("RDFF", chest.GAME_TRAP)][dataitems.HEADER.size + chest.TRAP_BYTE], 0x04)
        import struct
        from dsloader import game
        shut = out[("RDFF", chest.OBJECT)][dataitems.HEADER.size:]
        self.assertEqual(struct.unpack_from("<H", shut, game.ITEM_TYPE)[0], chest.SHUT_TYPE)


@unittest.skipUnless(GPLDATA and os.path.isfile(GPLDATA), "needs the game's GPLDATA.GFF (DSUN_GPLDATA)")
class GameScriptsTests(unittest.TestCase):
    def test_flags_clear_of_alagorn(self):
        """Alagorn's menus keep their overflow in flags from 784 on: none of his reaches the chest's."""
        from dsloader import alagorn
        from dsloader.gff import read_gff
        with open(GPLDATA, "rb") as f:
            data = f.read()
        chunks = read_gff(data)
        field_types = next((v for k, v in chunks.items() if k[0] == "GPLX"), b"")[gpl.FIELD_TYPES_AT:]
        used = set()
        for script in alagorn.script_chunks(chunks, field_types, True, True, True).values():
            used |= flags_in(gpl.decode(script, field_types))
        self.assertLess(max((f for f in used if f >= alagorn.FLAGS), default=alagorn.FLAGS), chest.DISARMED)

    def test_in_the_scripts_copy(self):
        """The Loader's copy of GPLDATA has the chest's script and its USE command."""
        with open(GPLDATA, "rb") as f:
            out = kalzith.script_chunks(f.read())
        self.assertIn(("GPL ", chest.SCRIPT), out)
        self.assertIn(gpl.encode_op((chest.USE, [("n", kalzith.START), ("n", chest.SCRIPT), ("n", -chest.OBJECT)])),
                      out[("MAS ", kalzith.MASTER)])


if __name__ == "__main__":
    unittest.main()
