"""The Loader's item icons: pictures made from the game's own, and SEGOBJEX's copy with them."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, gff, icons, npcitems, ring


def ranged_gff(types):
    """A GFF as the game's resource files are: TYPES {type: {id: chunk}}, each type's ids listed
    as runs and its chunks' places in a GFFI index chunk of its own (numbered in order)."""
    out = bytearray(28)
    gffi, listed = [], []
    for number, (kind, chunks) in enumerate(types.items()):
        table = bytearray(struct.pack("<I", len(chunks)))
        runs = []
        for cid in sorted(chunks):
            table += struct.pack("<II", len(out), len(chunks[cid]))
            out += chunks[cid]
            if runs and runs[-1][0] + runs[-1][1] == cid:
                runs[-1][1] += 1
            else:
                runs.append([cid, 1])
        gffi.append((number, len(out), len(table)))
        out += table
        listed.append((kind, len(chunks), number, runs))
    toc = bytearray(8) + struct.pack("<H", len(listed) + 1)
    toc += struct.pack("<4sI", b"GFFI", len(gffi)) + b"".join(struct.pack("<III", *e) for e in gffi)
    for kind, total, number, runs in listed:
        toc += struct.pack("<4sIIII", kind.encode("latin1"), 0x80000000 | len(runs), total, number, len(runs))
        toc += b"".join(struct.pack("<II", *r) for r in runs)
    struct.pack_into("<I", toc, 4, len(toc) - 2)
    struct.pack_into("<4sIIII", out, 0, b"GFFI", 0x30000, 28, len(out), len(toc))
    return bytes(out + toc + b"trailing bytes the game's file has")


class PictureTests(unittest.TestCase):
    ROWS = [[None, 1, 2, None], [None] * 4, [3] * 4, [None, None, None, 4]]

    def test_round_trip(self):
        chunk = icons.encode(self.ROWS)
        self.assertEqual(icons.decode(chunk), self.ROWS)
        self.assertEqual(struct.unpack_from("<I", chunk, 0)[0], len(chunk))
        self.assertEqual(chunk[-1], 0xFF)

    def test_long_runs(self):
        rows = [list(range(200))]
        self.assertEqual(icons.decode(icons.encode(rows)), rows)

    def test_shorter_blade_centred(self):
        """A diagonal of 12 on 16x16: 4 steps gone, the 8 left centred (4-11 each way)."""
        rows = [[7 if x == y and 2 <= x < 14 else None for x in range(16)] for y in range(16)]
        out = icons.shorter_blade(rows)
        points = [(x, y) for y, r in enumerate(out) for x, p in enumerate(r) if p is not None]
        self.assertEqual(points, [(i, i) for i in range(4, 12)])

    def test_fit_box(self):
        """The Polearm's 36x36 diagonal drawn 22x22, unbroken; a picture that fits, as it is."""
        rows = [[7 if x == y else None for x in range(36)] for y in range(36)]
        out = icons.fit_box(rows)
        self.assertEqual((len(out), len(out[0])), (icons.BOX_PICTURE, icons.BOX_PICTURE))
        self.assertEqual([(x, y) for y, r in enumerate(out) for x, p in enumerate(r) if p is not None],
                         [(i, i) for i in range(22)])
        small = [[1, None], [None, 2]]
        self.assertIs(icons.fit_box(small), small)

    def test_glow(self):
        rows = [[1, 2, None]]
        self.assertEqual(icons.glow(rows, lambda p, x, y: p == 2, icons.FIRE), [[1, icons.FIRE[1], None]])


class CopyTests(unittest.TestCase):
    def setUp(self):
        self.data = ranged_gff({
            "OJFF": {5: b"o5", 6: b"o6", 900: b"o900"},
            "BMP ": {1: b"b1", 2: b"b2", 7: b"b7"},
        })

    def test_added_in_order(self):
        """New ids between and after the old ones: every old chunk where it was, the new ones
        found, the runs sorted by id (the game's lookup needs them so)."""
        added = {("OJFF", 100): b"new100", ("OJFF", 7): b"new7", ("BMP ", 3): b"nb3", ("BMP ", 50): b"nb50"}
        out = icons.with_chunks(self.data, added)
        # appended only: the header's TOC offset and length aside, the file as it was
        self.assertEqual((out[:12], out[20:len(self.data)]), (self.data[:12], self.data[20:]))
        chunks = gff.read_gff(out)
        for key, chunk in {**gff.read_gff(self.data), **added}.items():
            if key[0] != "GFFI":  # (the index chunks grown by the new ones)
                self.assertEqual(chunks[key], chunk)
        toc_offset, toc_length = struct.unpack_from("<II", out, 12)
        self.assertEqual(toc_offset + toc_length, len(out))
        self.assertEqual(struct.unpack_from("<I", out, toc_offset + 4)[0], toc_length - 2)
        pos, runs = toc_offset + 10 + 8 + 2 * 12, {}
        for _ in range(2):
            kind, n, total, _, count = struct.unpack_from("<4sIIII", out, pos)
            runs[kind] = [struct.unpack_from("<II", out, pos + 20 + 8 * i) for i in range(count)]
            pos += 20 + 8 * count
        self.assertEqual(runs[b"OJFF"], [(5, 3), (100, 1), (900, 1)])
        self.assertEqual(runs[b"BMP "], [(1, 3), (7, 1), (50, 1)])

    def test_new_chunks(self):
        """Each icon's object: the plain one's with the new icon named; its map picture the plain
        one's; its icon made from the plain one's."""
        plain = icons.encode([[0x3A if x == y else None for x in range(16)] for y in range(16)])
        chunks = {}
        for _, number, _, _, _ in icons.ICONS:
            base = 0x10000 - number
            chunks[("OJFF", base)] = bytes(12) + struct.pack("<H", 40) + b"rest"
            chunks[("BMP ", base)] = b"map " + bytes([base & 0xFF])
        chunks[("BMP ", 40)] = plain
        new = icons.new_chunks(chunks)
        self.assertEqual(len(new), 3 * len(icons.ICONS) + 1)  # (and the Polearm's picture, fitted)
        self.assertEqual(new[("BMP ", 40)], plain)  # (16 pixels: it fits as it is)
        for name, number, obj, icon, _ in icons.ICONS:
            self.assertEqual(struct.unpack_from("<H", new[("OJFF", obj)], icons.OJFF_ICON)[0], icon)
            self.assertEqual(new[("BMP ", obj)], chunks[("BMP ", 0x10000 - number)])
            self.assertEqual(icons.PICTURES[name], 0x10000 - obj)
        rings = [{p for r in icons.decode(new[("BMP ", icon)]) for p in r} - {None}
                 for name, _, _, icon, _ in icons.ICONS if "Ring" in name]
        self.assertLessEqual(rings[0], set(icons.VIOLET))  # Pehtucl's
        self.assertLessEqual(rings[1], set(icons.FIRE))  # the arena's
        ids = [k for k in new if k[0] == "BMP "]
        self.assertEqual(len(ids), len(set(ids)))  # no icon numbered as another's map picture

    def test_fog_bolt(self):
        """Fogbolt's bolt: Magic Missile's object naming the grey picture, which is Magic Missile's
        frames pixel for pixel with its white, cyan and blue in greys (the rest as they were)."""
        from dsloader.art import decode_frame
        frames = [[[46, 220, None, 161, 7], [None, 220, 220, 46, None]],
                  [[161, 161, 161, None, 46, 46, 46, 46, 220, 3]]]
        bodies = [c[struct.unpack_from("<I", c, 6)[0]:] for c in map(icons.encode, frames)]  # (each frame)
        offsets, data = [], b""
        for body in bodies:
            offsets.append(6 + 4 * len(bodies) + len(data))
            data += body
        chunk = struct.pack("<IH", 0, len(bodies)) + b"".join(struct.pack("<I", o) for o in offsets) + data
        chunks = {("OJFF", icons.MISSILE_OBJECT): bytes(12) + struct.pack("<H", icons.MISSILE_PICTURE) + b"\xd0\x00",
                  ("BMP ", icons.MISSILE_PICTURE): chunk}
        new = icons.bolt_chunks(chunks)
        self.assertEqual(set(new), {("OJFF", icons.FOG_BOLT_OBJECT), ("BMP ", icons.FOG_BOLT_PICTURE)})
        self.assertEqual(new[("OJFF", icons.FOG_BOLT_OBJECT)],
                         bytes(12) + struct.pack("<H", icons.FOG_BOLT_PICTURE) + b"\xd0\x00")
        grey = new[("BMP ", icons.FOG_BOLT_PICTURE)]
        self.assertEqual(len(grey), len(chunk))
        for k, frame in enumerate(frames):
            expected = [[icons.FOG_BOLT_GREYS.get(p, p) if p is not None else None for p in row] for row in frame]
            self.assertEqual([list(row) for row in decode_frame(grey, k)[2]], expected)
            self.assertEqual([list(row) for row in decode_frame(chunk, k)[2]], frame)

    def test_new_spell_icons(self):
        """The new spells' icons (21196 + n): each from its game tile, the frame kept, the glyph
        changed: Fogbolt's cloud on Armor's grey, Reflected Image's hand mirror, Spook's ghost,
        Friends' heart."""
        def tile(colours):
            return [[colours[(x + y) % len(colours)] for x in range(16)] for y in range(16)]
        armor, mirror, scare, hold = tile([211, 212, 208, 214]), tile([70, 73, 42, 40]), tile([176, 177, 174]), \
            tile([139, 140, 134, 150])
        self.assertEqual((icons.FOG_ICON, icons.REFLECT_ICON, icons.SPOOK_ICON, icons.FRIENDS_ICON),
                         (21198, 21199, 21200, 21201))
        for make, base, glyph in ((icons.fog_icon, armor, icons.FOG_DARK), (icons.spook_icon, scare, 174),
                                  (icons.friends_icon, hold, icons.HEART_DARK)):
            out = make(base)
            self.assertEqual((len(out), len(out[0])), (16, 16))
            self.assertEqual([out[0], out[15]], [base[0], base[15]])
            inside = {p for row in out[1:15] for p in row[1:15]}
            self.assertIn(glyph, inside)
            self.assertNotEqual(out, base)
        fog = icons.fog_icon(armor)
        self.assertNotIn(214, {fog[y][x] for y in range(1, 15) for x in range(1, 15)} - {icons.FOG_LIGHT})
        reflect = icons.reflect_icon(mirror)
        self.assertEqual([reflect[0], reflect[-1]], [mirror[0], mirror[-1]])  # (its tile's border kept)
        self.assertEqual([row[0] for row in reflect], [row[0] for row in mirror])
        self.assertEqual(reflect[3][7:9], [70, 70])  # (the figure's head in the glass)
        self.assertEqual(reflect[3][4:7], [216, 216, 216])
        self.assertNotEqual(reflect, mirror)

    def test_pick_icon(self):
        """The Pick Pockets button's icon (ICON 3048, after Turn Undead's 3044-3047) from the
        earth tile: its frame kept, its glyph taken off, the purse in its dark line, a gold coin."""
        earth = [[(129 if x in (5, 6) and 2 < y < 13 else (136, 137)[(x + y) % 2]) for x in range(16)] for y in range(16)]
        out = icons.pick_icon(earth)
        self.assertEqual((icons.PICK_ICON, len(out), len(out[0])), (3048, 16, 16))
        self.assertEqual([out[0], out[15]], [earth[0], earth[15]])
        self.assertEqual(out[4][5:11], [129] * 6)  # (the drawstring)
        self.assertIn(64, {p for row in out for p in row})
        self.assertEqual(icons.decode(icons.encode(out)), out)

    def test_numbers_apart_from_the_rest(self):
        """No object or icon of these numbered as Kalzith's moved scroll icons or the party's
        sprites (the arms' first numbers were his: their boxes showed his pictures)."""
        from dsloader import kalzith, sprites
        ours = {n for _, _, obj, icon, _ in icons.ICONS for n in (obj, icon)}
        self.assertEqual(len(ours), 2 * len(icons.ICONS))
        moved = set(range(kalzith.MOVED_ICONS, kalzith.MOVED_ICONS + len(kalzith.SCROLLS)))
        self.assertFalse(ours & moved)
        party = set(range(sprites.SPRITE_BASE, sprites.SPRITE_BASE + 2 * (sprites.SPARES[-1] + 1 - sprites.PARTY_OBJECTS[0])))
        self.assertFalse(ours & party)


class WhichTests(unittest.TestCase):
    def test_items(self):
        self.assertEqual(icons.which(npcitems.SWORD), "Short Sword")
        self.assertEqual(icons.which(npcitems.CHEST_ARMOR), "Inixhide")
        self.assertEqual(icons.which(npcitems.CLOAK_ITEM), "Cloak of Protection +1")
        self.assertEqual(icons.which(ring.RING), "Ring of Protection +1")
        self.assertEqual(icons.which(npcitems.RING_ITEM), "Pehtucl's Ring of Protection +1")
        self.assertIsNone(icons.which(npcitems.HELM))
        magic = bytearray(npcitems.SWORD)
        magic[game.ITEM_PLUS] = 1
        self.assertEqual(icons.which(bytes(magic)), "Shadowseeker")
        gythka = bytearray(npcitems.SWORD)
        struct.pack_into("<H", gythka, game.ITEM_TYPE, game.GYTHKA_TYPE)
        self.assertIsNone(icons.which(bytes(gythka)))  # (the plain ones: the kreen's)
        gythka[game.ITEM_PLUS] = 1
        self.assertEqual(icons.which(bytes(gythka)), "Kreenfang")
        plain = bytearray(npcitems.CHEST_ARMOR)
        plain[game.ITEM_PLUS] = 0
        self.assertIsNone(icons.which(bytes(plain)))

    def test_starting_weapons(self):
        """The Loader's bone and obsidian short swords and axes by their types, and a great axe
        with no plus (the game's only one is +3: its picture's gem)."""
        rec = bytearray(npcitems.SWORD)
        for type_, name in ((game.BONE_SHORT_SWORD_TYPE, "Bone Short Sword"), (game.BONE_AXE_TYPE, "Bone Axe"),
                            (game.OBSIDIAN_SHORT_SWORD_TYPE, "Obsidian Short Sword"),
                            (game.OBSIDIAN_AXE_TYPE, "Obsidian Axe"), (icons.GREAT_AXE_TYPE, "Great Axe"),
                            (game.BONE_GREAT_AXE_TYPE, "Bone Great Axe"),
                            (game.OBSIDIAN_GREAT_AXE_TYPE, "Obsidian Great Axe"),
                            (game.BONE_DAGGER_TYPE, "Bone Dagger")):
            struct.pack_into("<H", rec, game.ITEM_TYPE, type_)
            self.assertEqual(icons.which(bytes(rec)), name)
        struct.pack_into("<H", rec, game.ITEM_TYPE, icons.GREAT_AXE_TYPE)
        rec[game.ITEM_PLUS] = 3
        self.assertIsNone(icons.which(bytes(rec)))  # (the game's Great Axe +3)
        rec[game.ITEM_PLUS] = 0
        struct.pack_into("<H", rec, game.ITEM_TYPE, icons.OBSIDIAN_MACE_TYPE)
        struct.pack_into("<H", rec, game.ITEM_NAME, icons.MACE_NAME)
        self.assertEqual(icons.which(bytes(rec)), "Obsidian Mace")
        struct.pack_into("<H", rec, game.ITEM_NAME, 55)
        self.assertIsNone(icons.which(bytes(rec)))  # (Blackmace)
        from dsloader import weaponchoice
        pictures = {t: p for t, _, p, _ in weaponchoice.PLAIN}
        self.assertEqual(pictures[game.BONE_SHORT_SWORD_TYPE], icons.PICTURES["Bone Short Sword"])
        self.assertEqual(pictures[game.BONE_AXE_TYPE], icons.PICTURES["Bone Axe"])
        self.assertEqual(pictures[game.BONE_GREAT_AXE_TYPE], icons.PICTURES["Bone Great Axe"])
        others = {t: p for kind in weaponchoice.OTHERS.values() for t, _, p, _ in kind}
        self.assertEqual(others[game.OBSIDIAN_GREAT_AXE_TYPE], icons.PICTURES["Obsidian Great Axe"])
        self.assertEqual(others[game.BONE_DAGGER_TYPE], icons.PICTURES["Bone Dagger"])

    def test_plain_without_the_copy(self):
        for name, number, _, _, _ in icons.ICONS:
            self.assertEqual(icons.picture(name, False), number)
            self.assertEqual(icons.picture(name, True), icons.PICTURES[name])


if __name__ == "__main__":
    unittest.main()
