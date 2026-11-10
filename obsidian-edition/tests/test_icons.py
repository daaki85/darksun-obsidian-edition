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

    def test_repeats_packed(self):
        """Three alike or more are a repeat (a byte n odd, then the pixel), up to 128 a piece; the
        rest literal; read back the same."""
        import random
        rng = random.Random(5)
        rows = [[7] * 200, [1, 1, 2, 2, 2, 3] * 30, [rng.randrange(4) for _ in range(214)],
                [None] * 5 + [9] * 130 + [None] + [4, 5]]
        rows = [r + [None] * (214 - len(r)) for r in rows]
        chunk = icons.encode(rows)
        self.assertEqual(icons.decode(chunk), rows)
        self.assertEqual(icons._pack([7] * 3), bytes([5, 7]))
        self.assertEqual(icons._pack([7] * 131), bytes([255, 7, 5, 7]))
        self.assertEqual(icons._pack([1, 1, 2]), bytes([4, 1, 1, 2]))
        self.assertLess(len(icons.encode([[7] * 200])), 30)  # (head 10, size 4, y, run head 4, two repeats 4, FFh)

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
        """The Polearm's 36x36 diagonal drawn 16x16, unbroken; a picture that fits, as it is."""
        rows = [[7 if x == y else None for x in range(36)] for y in range(36)]
        out = icons.fit_box(rows)
        self.assertEqual((len(out), len(out[0])), (icons.BOX_PICTURE, icons.BOX_PICTURE))
        self.assertEqual([(x, y) for y, r in enumerate(out) for x, p in enumerate(r) if p is not None],
                         [(i, i) for i in range(16)])
        small = [[1, None], [None, 2]]
        self.assertIs(icons.fit_box(small), small)

    def test_tall_weapons_box_copies(self):
        """Each weapon picture taller than 16 (BOX_TALL) gets a copy for the item box, BOX_SMALL + its
        place, drawn 16 at most (a narrow one keeping its shape); the picture itself is kept, for the
        inventory and the ground. One the Loader changes (ICONS', SHINE's) is copied as it ends up."""
        gythka = icons.encode([[0x3A if x == y else None for x in range(22)] for y in range(22)])
        staff = icons.encode([[0x3A if x == 3 else None for x in range(7)] for y in range(27)])
        plain = icons.encode([[0x3A if x == y else None for x in range(16)] for y in range(16)])
        chunks = {("BMP ", 40): plain, ("BMP ", 2384): gythka, ("BMP ", 2157): staff}
        for _, number, _, _, _ in icons.ICONS:
            chunks[("OJFF", 0x10000 - number)] = bytes(12) + struct.pack("<H", 40) + b"rest"
        new = icons.new_chunks(chunks)
        self.assertNotIn(("BMP ", 2384), new)  # (the game's own kept)
        small = lambda n: icons.decode(new[("BMP ", icons.BOX_SMALL + icons.BOX_TALL.index(n))])
        self.assertEqual([len(small(2384)), len(small(2157)), max(len(r) for r in small(2157))], [16, 16, 4])
        for n in (2447, 2513):  # (Kreenfang's and the Metal Polearm's, ICONS': made from the plain 16)
            self.assertEqual(new[("BMP ", icons.BOX_SMALL + icons.BOX_TALL.index(n))], icons.encode(icons.fit_box(icons.decode(new[("BMP ", n)]))))
        self.assertEqual(len(icons.BOX_TALL), len(set(icons.BOX_TALL)))

    def test_box_table_in_dsclog(self):
        """DSCLOG's BOX_PICS table and BOX_SMALL are icons'."""
        import re
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos", "dsclog.asm"),
                  encoding="latin-1") as f:
            text = f.read()
        block = text[text.index("box_tall dw"):text.index("BOX_TALL_COUNT equ")]
        numbers = [int(n) for line in block.splitlines() for n in re.findall(r"\b\d+\b", line.split(";")[0])]
        self.assertEqual(tuple(numbers), icons.BOX_TALL)
        self.assertIn(f"BOX_SMALL equ {icons.BOX_SMALL}", text)

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
        copies = sum(1 for k in new if k[0] == "BMP " and k[1] >= icons.BOX_SMALL and k[1] < icons.BOX_SMALL + len(icons.BOX_TALL))
        self.assertEqual(len(new), 3 * len(icons.ICONS) + copies)  # (and the item box's copies of the tall ones)
        self.assertNotIn(("BMP ", 40), new)  # (the plain picture kept)
        for name, number, obj, icon, _ in icons.ICONS:
            self.assertEqual(struct.unpack_from("<H", new[("OJFF", obj)], icons.OJFF_ICON)[0], icon)
            self.assertEqual(new.get(("BMP ", obj)), chunks.get(("BMP ", 0x10000 - number)))
            self.assertEqual(icons.PICTURES[name], 0x10000 - obj)
        rings = [{p for r in icons.decode(new[("BMP ", icon)]) for p in r} - {None}
                 for name, _, _, icon, _ in icons.ICONS if "Ring" in name]
        self.assertLessEqual(rings[0], set(icons.VIOLET) | set(icons.WATER))  # Pehtucl's: violet, shining
        self.assertTrue(rings[0] & set(icons.WATER))
        self.assertLessEqual(rings[1], set(icons.FIRE))  # the arena's
        ids = [k for k in new if k[0] == "BMP "]
        self.assertEqual(len(ids), len(set(ids)))  # no icon numbered as another's map picture

    def test_game_items_made_to_shine(self):
        """The Parting Staff (object 30044): its icon, in place, with its blue gem (158-161) in the
        water's colours the game cycles; the rest of it as it was."""
        staff = [[158 if y < 3 else 64 if x == y else None for x in range(5)] for y in range(8)]
        chunks = {("OJFF", 30044): bytes(12) + struct.pack("<H", 2157) + b"rest",
                  ("BMP ", 2157): icons.encode(staff)}
        for _, number, _, _, _ in icons.ICONS:
            chunks[("OJFF", 0x10000 - number)] = bytes(12) + struct.pack("<H", 40) + b"rest"
        chunks[("BMP ", 40)] = icons.encode([[0x3A if x == y else None for x in range(16)] for y in range(16)])
        new = icons.new_chunks(chunks)
        self.assertNotIn(("OJFF", 30044), new)  # (the object as it was: its icon's number the same)
        rows = icons.decode(new[("BMP ", 2157)])
        self.assertTrue(all(p in icons.WATER for r in rows[:3] for p in r))
        self.assertEqual(rows[3:], staff[3:])

    def test_no_map_picture(self):
        """A plain item with no map picture of its own number (the game's necklaces): its icon still
        made, the object copied as it is, no map picture added (and nothing else lost)."""
        plain = icons.encode([[0x3A if x == y else None for x in range(16)] for y in range(16)])
        chunks = {}
        for _, number, _, _, _ in icons.ICONS:
            base = 0x10000 - number
            chunks[("OJFF", base)] = bytes(12) + struct.pack("<H", 40) + b"rest"
            if number != 0x86DD:  # (the Necklace's object, 31011, has none)
                chunks[("BMP ", base)] = b"map"
        chunks[("BMP ", 40)] = plain
        new = icons.new_chunks(chunks)
        amulet = next(e for e in icons.ICONS if e[0] == "Amulet of Magic Resistance")
        self.assertIn(("OJFF", amulet[2]), new)
        self.assertIn(("BMP ", amulet[3]), new)
        self.assertNotIn(("BMP ", amulet[2]), new)
        self.assertEqual(sum(1 for k in new if k[0] == "OJFF"), len(icons.ICONS))

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


class WriteAtomicTests(unittest.TestCase):
    """gff.write_atomic, which every copy's writer uses: a failed write leaves no .tmp (a copy's is
    megabytes) and the earlier file as it was."""

    def test_failed_replace_and_write(self):
        import tempfile
        from unittest import mock
        with tempfile.TemporaryDirectory() as d:
            dest = os.path.join(d, "SEGOBJEX.GFF")
            gff.write_atomic(dest, b"one")
            with mock.patch("os.replace", side_effect=PermissionError(13, "held by the game")):
                with self.assertRaises(PermissionError):
                    gff.write_atomic(dest, b"two")
            self.assertEqual(os.listdir(d), ["SEGOBJEX.GFF"])
            with open(dest, "rb") as f:
                self.assertEqual(f.read(), b"one")

            class Full:
                def __len__(self):
                    return 3
            with self.assertRaises(TypeError):  # (a write that fails part-way)
                gff.write_atomic(dest, Full())
            self.assertEqual(os.listdir(d), ["SEGOBJEX.GFF"])


OBJECTS = os.environ.get("DSUN_OBJECTS")


@unittest.skipUnless(OBJECTS and os.path.isfile(OBJECTS), "needs the game's SEGOBJEX.GFF (DSUN_OBJECTS)")
class BoxTallInDataTests(unittest.TestCase):
    def test_every_tall_weapon_icon_in_box_tall(self):
        """In the copy as built: every weapon's icon (an item of a weapon kind's type in any
        RDFF, and the ICONS and SHINE items made from one) taller than the box's 16 is in
        BOX_TALL, so the item box draws its small copy (a Metal Pick's 19, drawn bare, put its
        last line on the box's edge)."""
        import tempfile
        from dsloader import dataitems, specialize
        with tempfile.TemporaryDirectory() as d:
            dest = os.path.join(d, icons.OBJECTS_FILE)
            icons.write_objects(OBJECTS, dest, {})
            with open(dest, "rb") as f:
                chunks = gff.read_gff(f.read())
        weapons = set()
        for (kind, _), chunk in chunks.items():
            if kind != "RDFF":
                continue
            try:
                recs, _ = dataitems.records(chunk)
            except (ValueError, IndexError, struct.error):
                continue
            for rec in recs:
                if rec.kind == dataitems.ITEM and len(rec.data) >= game.ITEM_TYPE + 2 \
                        and specialize.kind_of(struct.unpack_from("<H", rec.data, game.ITEM_TYPE)[0]) is not None:
                    weapons.add(0x10000 - struct.unpack_from("<H", rec.data, 0)[0])
        weapons |= {number for _, plain, number, _, _ in icons.ICONS if 0x10000 - plain in weapons}
        weapons |= {number for _, number, _, _ in icons.SHINE if number in weapons}
        self.assertIn(1381, weapons)  # (the Stone pick: the check sees the game's weapons)
        tall = []
        for number in sorted(weapons):
            obj = chunks.get(("OJFF", number))
            if obj is None:
                continue
            icon = struct.unpack_from("<H", obj, icons.OJFF_ICON)[0]
            picture = chunks.get(("BMP ", icon))
            if picture is not None and len(icons.decode(picture)) > icons.BOX_PICTURE and icon not in icons.BOX_TALL:
                tall.append((number, icon, len(icons.decode(picture))))
        self.assertEqual(tall, [])
        for name, _, number, icon, _ in icons.ICONS:  # (the picks' icons, made from the Stone pick's)
            if name in icons.PICK_PICTURE_FROM:
                self.assertEqual(struct.unpack_from("<H", chunks[("OJFF", number)], icons.OJFF_ICON)[0], icon)
                self.assertIn(icon, icons.BOX_TALL, name)


if __name__ == "__main__":
    unittest.main()
