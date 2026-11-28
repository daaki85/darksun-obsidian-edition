"""The sequel's redrawn figures (ravfigures): the Loader's file of them read whole, every drawing decoded and
every script step on a drawing its picture has, Notaku's combat drawings with no box round them, the moved
objects; a file not the game's left as it is; with DSUN_WOTR the sequel's own files, every chunk the figures
replace there (ravager's copies: test_ravager's test_copy_made)."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import art, gff, ravfigures, sequelicons  # noqa: E402

WOTR = os.environ.get("DSUN_WOTR")
COMBAT = 0x20  # (a script step's flag: a drawing of the combat picture, CBMP)
SLOTS, STEP = 36, 8  # (SCMD: 36 words, the step each animation starts at, then 8-byte steps)


def frame_count(chunk):
    return struct.unpack_from("<H", chunk, 4)[0]


def drawn(chunk, i):
    """True if frame I is the run-length kind art.decode_frame reads (the cinematic's packed and planar frames aren't)."""
    off, = struct.unpack_from("<I", chunk, 6 + 4 * i)
    return chunk[off + 4:off + 9] not in (b"\xffPLNR", b"\xffPLAN")


class FigureFileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = ravfigures.load()

    def test_the_files_and_their_counts(self):
        files = self.data["files"]
        self.assertEqual(set(files), set(ravfigures.FILES))
        self.assertEqual(len(self.data["objects"]), 32)
        self.assertEqual(set(files["RGN03A.GFF"]), {("ETAB", 58)})
        self.assertEqual({k[1] for k in files["RESOURCE.GFF"]}, {11001, 11002, 11005, 11006, 11007, 11008, 11012, 11013, 11014, 11016})
        pictures = {k[1] for k in files["OBJEX.GFF"] if k[0] == "BMP "}
        self.assertGreaterEqual(len(pictures), 260)
        self.assertTrue(self.data["source"])

    def test_every_drawing_decodes_and_every_step_has_its_drawing(self):
        for name in ("OBJEX.GFF", "RESOURCE.GFF"):
            chunks = self.data["files"][name]
            for (kind, pic), chunk in chunks.items():
                if kind in ("BMP ", "CBMP"):
                    for i in range(frame_count(chunk)):
                        if drawn(chunk, i):
                            w, h, rows = art.decode_frame(chunk, i)
                            self.assertEqual((len(rows), len(rows[0]) if rows else 0), (h, w), (name, kind, pic, i))
                if kind == "SCMD":
                    steps = [struct.unpack_from("<BBBBHBB", chunk, 2 * SLOTS + STEP * k)
                             for k in range((len(chunk) - 2 * SLOTS) // STEP)]
                    for k, st in enumerate(steps):  # (a bank the figures leave is the game's: GameFileTests)
                        bank = ("CBMP" if st[2] & COMBAT else "BMP ", pic)
                        if bank in chunks:
                            self.assertLess(st[0], frame_count(chunks[bank]), (name, pic, k))

    def test_notaku_fights_with_no_box(self):
        chunk = self.data["files"]["OBJEX.GFF"][("CBMP", 2409)]
        for i in range(frame_count(chunk)):
            w, h, rows = art.decode_frame(chunk, i)
            edge = [rows[y][x] for x in range(w) for y in (0, h - 1)] + [rows[y][x] for y in range(h) for x in (0, w - 1)]
            self.assertLess(sum(c is not None for c in edge) * 5, len(edge), i)  # (his feet and weapon may touch it)

    def test_objects_moved_only_from_the_games_picture(self):
        obj, old, new = self.data["objects"][0]
        rec = bytearray(16)
        game = {k: b"x" for k in self.data["files"]["OBJEX.GFF"] if k not in self.data["added"]["OBJEX.GFF"]}
        struct.pack_into("<H", rec, ravfigures.PICTURE, old)
        out = ravfigures.object_chunks({**game, ("OJFF", obj): bytes(rec)}, self.data)
        self.assertEqual(struct.unpack_from("<H", out[("OJFF", obj)], ravfigures.PICTURE)[0], new)
        struct.pack_into("<H", rec, ravfigures.PICTURE, old + 1)  # (another picture: the object left)
        out = ravfigures.object_chunks({**game, ("OJFF", obj): bytes(rec)}, self.data)
        self.assertNotIn(("OJFF", obj), out)

    def test_a_file_not_the_games_left_alone(self):
        self.assertEqual(ravfigures.object_chunks({("BMP ", 25): b"x"}, self.data), {})
        self.assertEqual(ravfigures.resource_chunks({}, self.data), {})
        self.assertEqual(ravfigures.region_chunks("RGN03A.GFF", {}, self.data), {})

    def test_region_moves_only_the_selected_ground_placement_once(self):
        placed = struct.Struct("<HHBBh")
        key = ("ETAB", 51)
        records = [(599, 1261, 0, 32, 9606), (521, 1263, 0, 32, 9606),
                   (599, 1261, 2, 32, 9606), (599, 1261, 0, 32, -9606)]
        stock = {key: b"".join(placed.pack(*row) for row in records)}
        result = ravfigures.region_chunks("rgn033.gff", stock)
        self.assertEqual(list(placed.iter_unpack(result[key])), [(599, 1278, 0, 32, 9606)] + records[1:])
        self.assertEqual(ravfigures.region_chunks("RGN033.GFF", result), {})

    def test_mines_bowls_sit_within_reach_of_each_seated_diner(self):
        room = self.data["files"]["RGN03A.GFF"][("ETAB", 58)]
        seats = {obj: (x, y, z) for x, y, z, _, obj in struct.iter_unpack("<HHBBh", room)}
        for seat in range(5):
            diner_x, diner_y, diner_z = seats[5166 + seat]
            bowl_x, bowl_y, bowl_z = seats[10379 + seat]
            self.assertLessEqual(abs(bowl_x - diner_x), 1)
            # Further back, the animated hands hide the whole bowl while eating.
            self.assertIn(diner_y - bowl_y, (0, 1))
            self.assertEqual(diner_z - bowl_z, 5)

    def test_headquarters_stacks_share_their_front_floor_line(self):
        placed = struct.Struct("<HHBBh")
        key = ("ETAB", 51)
        # Back and front barrels, the sacks they support, the crate beneath the vase,
        # and another placement of the same sacks on the floor.
        rows = [(677, 1269, 9508), (677, 1290, 9646), (566, 1289, 9646),
                (551, 1303, 9646), (567, 1310, 9646), (552, 1278, 9642),
                (606, 1281, 9645), (599, 1261, 9606), (664, 1341, 9642)]
        stock = {key: b"".join(placed.pack(x, y, 0, 32, obj) for x, y, obj in rows)}
        result = ravfigures.region_chunks("RGN033.GFF", stock)
        expected_y = [1276, 1290, 1296, 1305, 1310, 1289, 1291, 1278, 1341]
        self.assertEqual(list(placed.iter_unpack(result[key])),
                         [(x, ny, 0, 32, obj) for (x, _, obj), ny in zip(rows, expected_y)])
        self.assertEqual(ravfigures.region_chunks("RGN033.GFF", result), {})

    def test_torn_beds_move_only_their_two_supported_pillows(self):
        placed = struct.Struct("<HHBBh")
        key = ("ETAB", 51)
        records = [(1761, 1124, 0, 34, 9586), (1727, 783, 0, 2, 9586),
                   (1729, 812, 0, 32, 9594), (1914, 1155, 0, 32, 9594)]
        stock = {key: b"".join(placed.pack(*row) for row in records)}
        result = ravfigures.region_chunks("RGN033.GFF", stock)
        self.assertEqual(list(placed.iter_unpack(result[key])),
                         [(1761, 1135, 0, 34, 9586), (1727, 794, 0, 2, 9586)] + records[2:])
        self.assertEqual(ravfigures.region_chunks("RGN033.GFF", result), {})

    def test_openable_furniture_keeps_both_poses(self):
        closed = [[1, 1], [2, 2], [3, 3]]
        opened = [[None, 7], [8, 8], [9, None]]
        result = ravfigures.lowered_furniture(art.plnr_frames([closed, opened]))
        self.assertEqual(frame_count(result), 2)
        self.assertEqual(art.decode_frame(result, 0)[2], [[None, None], [1, 1], [3, 3]])
        self.assertEqual(art.decode_frame(result, 1)[2], [[None, None], [None, 7], [9, None]])

    def test_cleared_edges(self):
        from dsloader import sprites
        rows = [[5, 5, 5, 5], [5, 1, 5, 5], [5, 2, 3, 5], [5, 5, 5, 5]]
        out = ravfigures.cleared_edges(sprites.encode_frames([rows]))
        self.assertEqual(art.decode_frame(out, 0)[2],
                         [[None] * 4, [None, 1, None, None], [None, 2, 3, None], [None] * 4])


@unittest.skipUnless(WOTR, "DSUN_WOTR: the sequel's folder")
class GameFileTests(unittest.TestCase):
    def test_reviewed_furniture_matches_a_single_pass_over_stock(self):
        with open(os.path.join(WOTR, "OBJEX.GFF"), "rb") as f:
            stock = gff.read_gff(f.read())
        package = ravfigures.object_chunks(stock)
        grouped = [pic for _, pictures, _ in ravfigures.ASSEMBLIES for pic in pictures]
        for pic in (*ravfigures.FURNITURE, *grouped):
            if pic in ravfigures.SHELF_SPACING:  # Occupied shelf boards have their own tests below.
                continue
            key = ("BMP ", pic)
            percent = 82 if pic in (3172, 3173, 3174, 3558, 3795, 3796, 3797, 3798) else 66
            states = 2 if pic in ravfigures.OPENABLE else 1
            self.assertEqual(("SCMD", pic) in stock, states == 2, pic)
            self.assertNotIn(("SCMD", pic), package)
            self.assertEqual(frame_count(stock[key]), states, pic)
            self.assertEqual(frame_count(package[key]), states, pic)
            for index in range(states):
                original = sequelicons.decode(stock[key], index)
                w, h, actual = art.decode_frame(package[key], index)
                self.assertEqual((w, h), (len(original[0]), len(original)), pic)
                self.assertTrue(any(p is not None for row in actual for p in row), pic)
                for distance, row in enumerate(reversed(actual)):
                    # Nearest source row measured upwards from the unchanged base.
                    offset = (100 * distance + percent // 2) // percent
                    expected = original[h - 1 - offset] if offset < h else [None] * w
                    self.assertEqual(row, expected, (pic, distance))

    def test_set_tables_match_and_keep_their_place_settings(self):
        with open(os.path.join(WOTR, "OBJEX.GFF"), "rb") as f:
            stock = gff.read_gff(f.read())
        package = ravfigures.object_chunks(stock)
        feast, alternate, empty = (("BMP ", pic) for pic in (1321, 2624, 2625))
        self.assertEqual(package[feast], package[alternate])
        table = sequelicons.decode(package[feast])
        original = sequelicons.decode(stock[feast])
        bare = [[None] * 50] + sequelicons.decode(stock[empty])
        self.assertEqual(table[-11:], sequelicons.decode(package[empty])[-11:])
        for left, top, right, bottom, drop in ((19, 0, 41, 11, 14), (24, 13, 45, 34, 6), (9, 25, 22, 36, 5)):
            for y in range(top, bottom):
                for x in range(left, right):
                    if original[y][x] != bare[y][x]:
                        # At their reduced separation, the foreground platter covers the rear setting.
                        front = y + drop - 6
                        if top == 0 and 13 <= front < 34 and 24 <= x < 45 and original[front][x] != bare[front][x]:
                            continue
                        self.assertEqual(table[y + drop][x], original[y][x])
        imported = {feast: b"custom catalogue art", empty: stock[empty]}
        ravfigures._lower_set_tables(stock, imported)
        self.assertEqual(imported[feast], b"custom catalogue art")

    def test_volcano_barrel_move_is_confined_to_the_southern_stack(self):
        with open(os.path.join(WOTR, "RGN03D.GFF"), "rb") as f:
            stock = gff.read_gff(f.read())
        key = ("ETAB", 61)
        changed = ravfigures.region_chunks("RGN03D.GFF", stock)[key]
        records = struct.Struct("<HHBBh")
        differences = [(a, b) for a, b in zip(records.iter_unpack(stock[key]), records.iter_unpack(changed)) if a != b]
        barrels = [(a, b) for a, b in differences if a[4] in (10649, 10650)]
        self.assertEqual(len(barrels), 1)
        before, after = barrels[0]
        self.assertEqual((before[:3], before[4]), ((1200, 1392, 0), 10650))
        self.assertEqual(after, (1200, 1400, *before[2:]))

    def test_mine_worktables_lower_as_complete_surfaces(self):
        with open(os.path.join(WOTR, "OBJEX.GFF"), "rb") as f:
            stock = gff.read_gff(f.read())
        package = ravfigures.object_chunks(stock)
        for first, second in ((3766, 3767), (3770, 3771), (3772, 3773), (3774, 3775)):
            keys = (("BMP ", first), ("BMP ", second))
            originals = [sequelicons.decode(stock[key]) for key in keys]
            revised = [sequelicons.decode(package[key]) for key in keys]
            if first == 3766:  # One continuous front-to-back surface across the native boundary.
                originals = [originals[0] + originals[1]]
                revised = [revised[0] + revised[1]]
            for before, after in zip(originals, revised):
                self.assertEqual(len(after), len(before), first)
                self.assertEqual(after[:5], [[None] * len(before[0])] * 5, first)
                self.assertEqual(after[5:-11], before[:-16], first)
                self.assertEqual(after[-11:], [before[-1 - n] for n in (15, 14, 12, 11, 9, 8, 6, 5, 3, 2, 0)], first)
            # A future replacement of either piece must also protect its partner.
            imported = {keys[0]: stock[keys[0]], keys[1]: package[keys[1]]}
            expected = imported.copy()
            ravfigures._lower_mine_worktables(stock, imported)
            self.assertEqual(imported, expected)

    def test_silver_seats_follow_their_own_table_depth(self):
        record = struct.Struct("<HHBBh")
        for name, seat, table, expected in (("RGN03D.GFF", 10594, (830, 133), 111),
                                            ("RGN03E.GFF", 10796, (1702, 1102), 1074)):
            with open(os.path.join(WOTR, name), "rb") as f:
                stock = gff.read_gff(f.read())
            key = ("ETAB", int(name[3:6], 16))
            revised = ravfigures.region_chunks(name, stock)
            old_rows = list(record.iter_unpack(stock[key]))
            new_rows = list(record.iter_unpack(revised[key]))
            self.assertEqual(len(old_rows), len(new_rows))
            changes = [(a, b) for a, b in zip(old_rows, new_rows) if a != b and a[4] != 10650]
            self.assertEqual(len(changes), 1)
            before, after = changes[0]
            self.assertEqual(before[4], seat)
            self.assertEqual(after, (before[0], expected, *before[2:]))
            self.assertEqual(table[1] - expected, round((table[1] - before[1]) * 0.66))
            self.assertTrue(any(row[:2] == table for row in new_rows))
            self.assertEqual(ravfigures.region_chunks(name, revised), {})

    def test_volcano_shelves_keep_every_occupied_row(self):
        with open(os.path.join(WOTR, "OBJEX.GFF"), "rb") as f:
            stock = gff.read_gff(f.read())
        package = ravfigures.object_chunks(stock)
        for pic in (2979, 2980, 2981, 2982):
            key = ("BMP ", pic)
            original = sequelicons.decode(stock[key])
            revised = sequelicons.decode(package[key])
            _, omitted = ravfigures.SHELF_SPACING[pic]
            for y in omitted:
                # Between the side rails, the omitted rows contain only empty space or shelf wood.
                self.assertTrue(all(v is None or 212 <= v <= 222 for v in original[y][7:-7]), (pic, y))
            self.assertEqual(revised, [[None] * 64] * len(omitted) +
                             [row for y, row in enumerate(original) if y not in omitted])
            self.assertEqual(revised[-1], original[-1])

    def test_mine_shelf_preserves_all_six_loose_orbs(self):
        with open(os.path.join(WOTR, "OBJEX.GFF"), "rb") as f:
            stock = gff.read_gff(f.read())
        key = ("BMP ", 1140)
        package = ravfigures.object_chunks(stock)
        self.assertEqual(package[key], ravfigures._lower_stocked_shelf(stock[key], 1140))
        shelf = sequelicons.decode(package[key])
        original = sequelicons.decode(stock[key])
        orb = sequelicons.decode(stock[("BMP ", 1052)])
        self.assertEqual((len(shelf), len(shelf[0])), (50, 64))
        self.assertTrue(all(p is None for row in shelf[:8] for p in row))
        self.assertEqual(shelf[-1], original[-1])
        for x, y in ((6, 8), (26, 9), (45, 8), (19, 22), (11, 35), (32, 37)):
            for dy, row in enumerate(orb):
                for dx, colour in enumerate(row):
                    if colour is not None:
                        self.assertEqual(shelf[y + dy][x + dx], colour, (x, y, dx, dy))

    def test_split_beds_match_a_single_scaled_blanket_at_every_placement(self):
        from dsloader import sprites
        with open(os.path.join(WOTR, "OBJEX.GFF"), "rb") as f:
            stock = gff.read_gff(f.read())
        built = {**stock, **ravfigures.object_chunks(stock)}
        pairs = {}
        for name in os.listdir(WOTR):
            if not (len(name) == 10 and name.startswith("RGN") and name.endswith(".GFF")):
                continue
            with open(os.path.join(WOTR, name), "rb") as f:
                region = gff.read_gff(f.read())
            region.update(ravfigures.region_chunks(name, region))
            for (kind, _), data in region.items():
                if kind != "ETAB":
                    continue
                for x, y, height, _, obj in struct.iter_unpack("<HHBBh", data):
                    rec = built.get(("OJFF", abs(obj)))
                    if not rec:
                        continue
                    pic, = struct.unpack_from("<H", rec, ravfigures.PICTURE)
                    if pic in (524, 525, 530, 531):
                        ax, ay = struct.unpack_from("<hh", rec, 2)
                        # Both pieces share the head’s top left after removing the native overlap.
                        offset = {525: 39, 531: 41}.get(pic, 0)
                        pos = (name, x - ax, y - height - ay - offset)
                        pairs.setdefault(pos, []).append(pic)
        self.assertCountEqual([name for name, _, _ in pairs],
                              ["RGN032.GFF", "RGN032.GFF", "RGN033.GFF", "RGN033.GFF", "RGN038.GFF", "RGN03E.GFF"])
        for parts in pairs.values():
            self.assertIn(sorted(parts), ([524, 525], [530, 531]))

        def assembled(chunks, head, foot, foot_height):
            canvas = [[None] * 40 for _ in range(68)]
            for pic, offset, height in ((head, 0, 46), (foot, 68 - foot_height, foot_height)):
                rows = sequelicons.decode(chunks[("BMP ", pic)])
                self.assertEqual((len(rows), len(rows[0])), (height, 40))
                for y, row in enumerate(rows, offset):
                    for x, pixel in enumerate(row):
                        if pixel is not None:
                            canvas[y][x] = pixel
            return canvas

        for spec in ((524, 525, 29), (530, 531, 27)):
            full_bed = sprites.encode_frames([assembled(stock, *spec)])
            self.assertEqual(assembled(built, *spec), sequelicons.decode(ravfigures.lowered_furniture(full_bed)))

    def test_empty_temple_throne_keeps_the_seated_position(self):
        with open(os.path.join(WOTR, "OBJEX.GFF"), "rb") as f:
            stock = gff.read_gff(f.read())
        built = ravfigures.object_chunks(stock)
        picture, obj = ("BMP ", 789), ("OJFF", 3530)
        self.assertEqual(built[picture], ravfigures.lowered_furniture(stock[picture]))
        # One map square is 16 px. The script places the empty seat in its centre.
        for step in (0, 1):
            ax, ay = struct.unpack_from("<bb", stock[("SCMD", 788)], 72 + 8 * step + 5)
            self.assertEqual(struct.unpack_from("<hh", built[obj], 2), (ax + 8, ay + 8))
        self.assertEqual(built[obj][:2] + built[obj][6:], stock[obj][:2] + stock[obj][6:])
        self.assertNotIn(obj, ravfigures.object_chunks({**stock, obj: built[obj]}))
        custom = bytearray(stock[obj])
        struct.pack_into("<hh", custom, 2, 5, 7)
        self.assertNotIn(obj, ravfigures.object_chunks({**stock, obj: bytes(custom)}))

    def test_partial_squash_keeps_the_upper_art_and_floor_line(self):
        with open(os.path.join(WOTR, "OBJEX.GFF"), "rb") as f:
            stock = gff.read_gff(f.read())
        package = ravfigures.object_chunks(stock)
        for pic, depth in ravfigures.BASE_ROWS.items():
            key = ("BMP ", pic)
            original = sequelicons.decode(stock[key], 0)
            width, height, actual = art.decode_frame(package[key], 0)
            self.assertEqual((width, height), (len(original[0]), len(original)), pic)
            self.assertEqual(frame_count(package[key]), frame_count(stock[key]), pic)
            # Nearest source rows measured upwards through the base, leaving the art above it intact.
            offsets = {
                9: (0, 2, 3, 5, 6, 8),
                16: (0, 2, 3, 5, 6, 8, 9, 11, 12, 14, 15),
                18: (0, 2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17),
                22: (0, 2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18, 20, 21),
                43: (0, 2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18, 20, 21, 23, 24,
                     26, 27, 29, 30, 32, 33, 35, 36, 38, 39, 41, 42),
            }[depth]
            rise = depth - len(offsets)
            self.assertEqual(actual[:rise], [[None] * width] * rise, pic)
            self.assertEqual(actual[rise:height - depth + rise], original[:-depth], pic)
            self.assertEqual(actual[-len(offsets):], [original[-1 - row] for row in reversed(offsets)], pic)

    def test_elderbrain_encounter_keeps_each_frame_outline(self):
        with open(os.path.join(WOTR, "RESOURCE.GFF"), "rb") as f:
            stock = gff.read_gff(f.read())
        revised = ravfigures.resource_chunks(stock)
        for picture, count in ((11008, 1), (11016, 29)):
            key = ("BMP ", picture)
            self.assertEqual(frame_count(stock[key]), count)
            self.assertEqual(frame_count(revised[key]), count)
            for frame in range(count):
                with self.subTest(picture=picture, frame=frame):
                    before = sequelicons.decode(stock[key], frame)
                    after = sequelicons.decode(revised[key], frame)
                    self.assertNotEqual(after, before)
                    self.assertEqual([[p is None for p in row] for row in after],
                                     [[p is None for p in row] for row in before])

    def test_every_replaced_chunk_is_the_games(self):
        data = ravfigures.load()
        for name in ravfigures.FILES:
            with open(os.path.join(WOTR, name), "rb") as f:
                own = gff.read_gff(f.read())
            added = data["added"].get(name, set())
            for k in data["files"][name]:
                self.assertEqual(k in own, k not in added, (name, k))
        with open(os.path.join(WOTR, "OBJEX.GFF"), "rb") as f:
            own = gff.read_gff(f.read())
        made = ravfigures.object_chunks(own, data)
        self.assertEqual({i for kind, i in made if kind == "OJFF"}, {i for i, _, _ in data["objects"]} | {3530})
        merged = {**own, **made}
        bad = []
        for (kind, pic), script in merged.items():  # (every step of a script the figures bring, on a drawing there is)
            if kind != "SCMD" or ("SCMD", pic) not in made:
                continue
            for k in range((len(script) - 2 * SLOTS) // STEP):
                st = struct.unpack_from("<BBBBHBB", script, 2 * SLOTS + STEP * k)
                bank = merged.get(("CBMP" if st[2] & COMBAT else "BMP ", pic))
                if bank is None or st[0] >= frame_count(bank):
                    bad.append((pic, k))
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
