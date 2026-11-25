"""The item types and names the Loader's copy of GPLDATA.GFF has (dsloader/itemtables.py): the
game's own, mended, then the Loader's."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, gff, itemtables, names, npcitems  # noqa: E402

# a stand-in for the game's chunks: each type's bytes its number (made even: no class bit 1), each name "N<number>"
OWN_TYPES = b"".join(bytes([k & 0xFE]) * 20 for k in range(game.GAME_TYPES))
OWN_NAMES = b"".join(b"N%d" % k + bytes(25 - len(b"N%d" % k)) for k in range(names.OWN))


class ChunkTests(unittest.TestCase):
    def test_types(self):
        """The game's 115 with the Loader's 44 after them (numbered from 115), and the game's own
        mended: Grey's Scale's arms and legs AC 3, the Great Axe +3 metal, the pick 1d6+1, the
        Quicksilver Glove leather, the daggers for air clerics too; the rest as the game's."""
        out = itemtables.types_chunk(OWN_TYPES)
        self.assertEqual(len(out), 20 * (game.GAME_TYPES + len(npcitems.TYPES)))
        self.assertEqual(out[20 * game.GAME_TYPES:], b"".join(npcitems.TYPES))
        rec = lambda k: out[20 * k:20 * k + 20]
        for kind in (24, 54):
            self.assertEqual(rec(kind)[0x12], 3)
        self.assertEqual([rec(2)[8], rec(113)[8], rec(112)[0x0C]], [4, 5, 6])
        for dagger in (17, 33, 84, 94):
            self.assertEqual(rec(dagger)[0x10], dagger & 0xFE | 1)
        changed = {k for k in range(game.GAME_TYPES) if rec(k) != OWN_TYPES[20 * k:20 * k + 20]}
        self.assertEqual(changed, {2, 17, 24, 33, 54, 84, 94, 112, 113})
        for kind in changed:  # (one byte each)
            self.assertEqual(sum(a != b for a, b in zip(rec(kind), OWN_TYPES[20 * kind:20 * kind + 20])), 1)
        self.assertEqual(npcitems.TYPES[127 - 115][0x0C], 6)  # (the Loader's Metal Pick's 1d6+1 too)

    def test_names(self):
        """The game's 322 with names.NAMES after them, each padded to 25 with NULs."""
        out = itemtables.names_chunk(OWN_NAMES)
        self.assertEqual(out[:len(OWN_NAMES)], OWN_NAMES)
        self.assertEqual(len(out), 25 * (names.OWN + names.EXTRA))
        for entry, name in names.NAMES.items():
            self.assertEqual(out[25 * entry:25 * entry + 25], name.ljust(25, b"\0"))

    def test_other_sizes_refused(self):
        with self.assertRaises(itemtables.ItemTablesError):
            itemtables.types_chunk(OWN_TYPES + bytes(20))
        with self.assertRaises(itemtables.ItemTablesError):
            itemtables.names_chunk(OWN_NAMES[:-25])


def _gff(chunks):
    """A small GFF file of CHUNKS ({(type, id): bytes}): header, the chunks, a table of contents
    listing each by itself (GFFI first, empty), as the game's files are laid out."""
    kinds = {}
    for (kind, cid), data in chunks.items():
        kinds.setdefault(kind, []).append((cid, data))
    kinds = {"GFFI": [(0, b"")], **kinds}
    body = bytearray(20)
    entries = []
    for kind, items in kinds.items():
        listed = []
        for cid, data in items:
            listed.append((cid, len(body), len(data)))
            body += data
        entries.append((kind, listed))
    toc = bytearray(8) + struct.pack("<H", len(entries))
    for kind, listed in entries:
        toc += struct.pack("<4sI", kind.encode("latin1"), len(listed))
        for e in listed:
            toc += struct.pack("<III", *e)
    struct.pack_into("<4s4sIII", body, 0, b"GFFI", b"V3.0", 20, len(body), len(toc))
    return bytes(body + toc)


class FileTests(unittest.TestCase):
    def test_write(self):
        """write: the file with the two chunks grown, the rest as it was."""
        import tempfile
        source = _gff({itemtables.TYPES_CHUNK: OWN_TYPES, itemtables.NAMES_CHUNK: OWN_NAMES, ("TEXT", 5): b"kept"})
        with tempfile.TemporaryDirectory() as d:
            src, dest = os.path.join(d, "a.gff"), os.path.join(d, "b.gff")
            with open(src, "wb") as f:
                f.write(source)
            itemtables.write(src, dest)
            with open(dest, "rb") as f:
                out = gff.read_gff(f.read())
        self.assertEqual(out[itemtables.TYPES_CHUNK], itemtables.types_chunk(OWN_TYPES))
        self.assertEqual(out[itemtables.NAMES_CHUNK], itemtables.names_chunk(OWN_NAMES))
        self.assertEqual(out[("TEXT", 5)], b"kept")


if __name__ == "__main__":
    unittest.main()
