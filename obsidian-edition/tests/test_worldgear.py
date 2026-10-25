import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import game, icons, names, npcitems, restrict, worldgear  # noqa: E402


def gift(name):
    return next(g for g in worldgear.GIFTS + worldgear.MAGIC if g.name == name)


class WorldGearTests(unittest.TestCase):
    def test_weapons(self):
        """Each weapon given is one of the Loader's own, with its picture, in no list or slot."""
        for spec, plus, name in ((worldgear.BONE_SHORT_SWORD, 0, "Bone Short Sword"),
                                 (worldgear.OBSIDIAN_SHORT_SWORD, 0, "Obsidian Short Sword"),
                                 (worldgear.BONE_AXE, 0, "Bone Axe"), (worldgear.OBSIDIAN_AXE, 0, "Obsidian Axe"),
                                 (worldgear.OBSIDIAN_MACE, 0, "Obsidian Mace"),
                                 (worldgear.METAL_SHORT_SWORD, 0, "Short Sword"),
                                 worldgear.CLUB_1 + ("Gutterknot",), worldgear.PICK_1 + ("Deepbiter",),
                                 worldgear.STAFF_SLING_1 + ("Windlash",),
                                 worldgear.SHORT_SWORD_2 + ("Greenbright",),
                                 (worldgear.METAL_DAGGER, 0, "Metal Dagger"), (worldgear.METAL_MACE, 0, "Metal Mace"),
                                 (worldgear.METAL_GREAT_AXE, 0, "Metal Great Axe"),
                                 (worldgear.METAL_PICK, 0, "Metal Pick"), (worldgear.METAL_POLEARM, 0, "Metal Polearm")):
            rec = worldgear.weapon(spec, plus)
            self.assertEqual(len(rec), game.ITEM_SIZE)
            self.assertEqual(icons.which(rec), name)
            self.assertEqual(struct.unpack_from("<H", rec, 0)[0], icons.PICTURES[name])
            self.assertEqual(struct.unpack_from("<H", rec, game.ITEM_NEXT)[0], game.NO_ITEM)
            self.assertEqual(rec[game.ITEM_SLOT], 0xFF)
            self.assertEqual(rec[game.ITEM_PLUS], plus)

    def test_merchants(self):
        """The Weapon Merchant stocks every new plain weapon (the great axes in every material, a
        warrior's starting one being bone; every Wild Mul carries a bone one too), Jark all but the obsidian axe and the metal ones;
        the kinds of people carry theirs each; no one the party wouldn't fight has one (Krikor, Uskuye,
        Lt. Kwerin), and no one Thieves' Tools (a thief's Pick Pockets button instead: pickpocket.py)."""
        from dsloader import tools
        sold = [icons.which(r) for r in gift("Weapon Merchant").items]
        self.assertEqual(sold, ["Bone Short Sword", "Obsidian Short Sword", "Bone Axe", "Obsidian Axe", "Obsidian Mace",
                                "Short Sword", "Bone Great Axe", "Obsidian Great Axe", "Metal Great Axe", "Metal Pick", "Bone Dagger"])
        self.assertEqual([icons.which(r) for r in gift("Wild Mul").items], ["Bone Axe", "Bone Great Axe"])
        self.assertEqual(([icons.which(r) for r in gift("Scar's henchman").items], gift("Scar's henchman").objects),
                         (["Bone Axe"], (229,)))
        defilers = [(g.objects, [icons.which(r) or struct.unpack_from("<H", r, game.ITEM_TYPE)[0] for r in g.items])
                    for g in worldgear.GIFTS if g.name == "Defiler"]  # (a body to leave: a dagger each)
        self.assertEqual(defilers, [((258,), [17]), ((296,), ["Bone Dagger"])])
        self.assertEqual([icons.which(r) for r in gift("Jark").items],
                         ["Bone Short Sword", "Obsidian Short Sword", "Bone Axe", "Obsidian Mace", "Bone Great Axe",
                          "Obsidian Great Axe", "Bone Dagger"])
        self.assertFalse([g.name for g in worldgear.GIFTS + worldgear.MAGIC if any(tools.is_tools(r) for r in g.items)])
        self.assertNotIn("Mirlon", {g.name for g in worldgear.GIFTS})
        self.assertFalse({"Krikor", "Uskuye", "Kwerin"} & {g.name for g in worldgear.GIFTS + worldgear.MAGIC})
        self.assertEqual([gift(n).objects for n in ("Tari", "Renegade", "Wild Mul")], [(60, 243), (289,), (290,)])

    def test_metal_kinds(self):
        """Each metal weapon is of its kind and of metal (an earth cleric's, not a fire cleric's)."""
        from dsloader import specialize
        for spec, kind in ((worldgear.METAL_DAGGER, "dagger"), (worldgear.METAL_MACE, "mace"),
                           (worldgear.METAL_GREAT_AXE, "great axe"), (worldgear.METAL_PICK, "pick"),
                           (worldgear.METAL_POLEARM, "polearm"), (worldgear.METAL_SHORT_SWORD, "short sword")):
            self.assertEqual(specialize.KINDS[specialize.KIND_OF_TYPE[spec[0]]], kind)
            self.assertEqual(npcitems.TYPES[spec[0] - game.GAME_TYPES][8], 4)

    def test_churrr(self):
        """The Club +1 is Churrr's own, as loot."""
        self.assertEqual(icons.which(gift("Churrr").items[0]), "Gutterknot")

    def test_priced_as_the_game(self):
        """Melee weapons 20,800 a plus, as the game's Obsidian Bloodwrath +1; the staff sling as
        its Sling +1."""
        for spec, plus in (worldgear.CLUB_1, worldgear.PICK_1, worldgear.SHORT_SWORD_2):
            self.assertEqual(spec[3], 20800 * plus)
        self.assertEqual(worldgear.STAFF_SLING_1[0][3], 2800)

    def test_bracers(self):
        """AC 6, 5, 4 and 2, as a plus of 10 - AC, worn on the arms; the Loader's icon and name."""
        acs = {}
        for name in ("Mikquetzl", "Wyrmias", "Balkazar", "Dagolar"):
            g = gift(name)
            rec = g.items[0]  # (Wyrmias has the Golden Girdle of Urnst too)
            self.assertEqual(icons.which(rec), "Bracers of Defense")
            self.assertEqual(struct.unpack_from("<H", rec, game.ITEM_TYPE)[0], game.BRACERS_TYPE)
            self.assertEqual(struct.unpack_from("<H", rec, game.ITEM_NAME)[0], worldgear.BRACERS_NAME)
            acs[name] = 10 - rec[game.ITEM_PLUS]
            self.assertEqual(struct.unpack_from("<H", rec, 6)[0], 5000 * rec[game.ITEM_PLUS])
        self.assertEqual(acs, {"Mikquetzl": 6, "Wyrmias": 5, "Balkazar": 4, "Dagolar": 2})
        self.assertEqual(names.NAMES[worldgear.BRACERS_NAME], b"Bracers/Defns")

    def test_head_items(self):
        """Arrowbane and the Sunking Crown: worn on the head, not armour, each with its spell (one
        past the game's number, its icon shown too), Kel's and Keldar's (worn)."""
        for item, type_, spell, name in ((worldgear.ARROWBANE_ITEM, game.CIRCLET_TYPE, 36, "Arrowbane"),
                                         (worldgear.CROWN_ITEM, game.CROWN_TYPE, 76, "Sunking Crown")):
            self.assertEqual(struct.unpack_from("<H", item, game.ITEM_TYPE)[0], type_)
            self.assertEqual(item[worldgear.ITEM_SPELL], spell + 1)
            self.assertEqual(struct.unpack_from("<H", item, worldgear.ITEM_SPELL_SHOWN)[0], spell + 1)
            self.assertEqual(icons.which(item), name)
            typ = npcitems.TYPES[type_ - game.GAME_TYPES]
            self.assertEqual(typ[9], 6)  # (the head)
            self.assertFalse(restrict.is_armour(typ))
            self.assertEqual(names.NAMES[struct.unpack_from("<H", item, game.ITEM_NAME)[0]], name.encode())
        self.assertEqual([g.items for g in worldgear.MAGIC if g.name == "Kel"], [(worldgear.ARROWBANE_ITEM, worldgear.VEILED_ROBE, worldgear.MR_AMULET_ITEM)])
        self.assertEqual(gift("Keldar").objects, (28,))

    def test_girdles_and_amulet(self):
        """The girdles (worn at the waist) and the Amulet of Magic Resistance (worn at the neck):
        their types, names of 15 letters at most, icons, and places (the Troop Leader, Wyrmias,
        Kel)."""
        waist, neck = game.EQUIP_SLOTS.index("waist"), game.EQUIP_SLOTS.index("neck")
        for item, type_, slot, name in ((worldgear.BACK_GIRDLE_ITEM, game.BACK_GIRDLE_TYPE, waist, "Girdle of Back Defense"),
                                        (worldgear.URNST_GIRDLE_ITEM, game.URNST_GIRDLE_TYPE, waist, "Golden Girdle of Urnst"),
                                        (worldgear.MR_AMULET_ITEM, game.MR_AMULET_TYPE, neck, "Amulet of Magic Resistance")):
            self.assertEqual(struct.unpack_from("<H", item, game.ITEM_TYPE)[0], type_)
            typ = npcitems.TYPES[type_ - game.GAME_TYPES]
            self.assertEqual(typ[9], {waist: 2, neck: 7}[slot])  # (the game's Belt's and Necklace's)
            self.assertFalse(restrict.is_armour(typ))
            self.assertEqual(icons.which(item), name)
            self.assertEqual(item[game.ITEM_PLUS], 0)
        self.assertEqual(icons.which(worldgear.weapon(*worldgear.BOW_1)), "Dunesong")
        for entry in (worldgear.BACK_GIRDLE, worldgear.URNST_GIRDLE, worldgear.MR_AMULET):
            self.assertLessEqual(len(names.NAMES[entry]), 15)
        self.assertIn(worldgear.BACK_GIRDLE_ITEM, gift("Troop Leader").items)
        self.assertIn(worldgear.URNST_GIRDLE_ITEM, gift("Wyrmias").items)
        self.assertIn(worldgear.MR_AMULET_ITEM, gift("Kel").items)

    def test_wardens_plate(self):
        """The Warden's Plate: plate +1 of AC 3, 2, 2 (metal armour to the class rules) and the
        game's metal helm +1; the chest Resist Fire, the helm Cloak of Bravery, the arms and legs
        none; the helm on Dagolar, the arms in the Lower Castle's chest with Dark Flame, the legs
        in the Wagon Train's chest, the chest on Balkazar."""
        chest, arms, legs, helm = worldgear.WARDENS_PLATE
        for item, type_, slot, ac, spell, name in (
                (chest, game.PLATE_CHEST_TYPE, 1, 3, 87, "Warden's Chest"),
                (arms, game.PLATE_ARMS_TYPE, 3, 2, 0, "Warden's Arms"),
                (legs, game.PLATE_LEGS_TYPE, 0x0A, 2, 0, "Warden's Legs"),
                (helm, 89, None, None, 109, "Warden's Helm")):
            self.assertEqual(struct.unpack_from("<H", item, game.ITEM_TYPE)[0], type_)
            self.assertEqual(item[game.ITEM_PLUS], 1)
            self.assertEqual(item[worldgear.ITEM_SPELL], spell + 1 if spell else 0)
            self.assertEqual(struct.unpack_from("<H", item, worldgear.ITEM_SPELL_SHOWN)[0], spell + 1 if spell else 0)
            self.assertEqual(icons.which(item), name)
            self.assertEqual(names.NAMES[struct.unpack_from("<H", item, game.ITEM_NAME)[0]], name.encode())
            if slot is not None:
                typ = npcitems.TYPES[type_ - game.GAME_TYPES]
                self.assertEqual((typ[9], typ[0x12], typ[8]), (slot, ac, 4))  # (metal)
                self.assertTrue(restrict.is_armour(typ))
        where = {g.items[0]: (g.name, g.objects) for g in worldgear.MAGIC if set(g.items) & set(worldgear.WARDENS_PLATE)}
        self.assertEqual(where, {helm: ("Dagolar", (26,)), arms: ("Treasure chest", (1360,)),
                                 legs: ("Wagon Train chest", (1065,)), chest: ("Balkazar", (14,))})

    def test_elvenkind(self):
        """The Cloak and Boots of Elvenkind: their own types (the Cloak's, the Boots'), names and
        icons, no plus; the cloak with the Elven Leader's Gythka +1, the boots in the caravan's
        buried chest."""
        for item, type_, slot, name in ((worldgear.ELVEN_CLOAK, game.ELVEN_CLOAK_TYPE, 8, "Cloak of Elvenkind"),
                                        (worldgear.ELVEN_BOOTS, game.ELVEN_BOOTS_TYPE, 4, "Boots of Elvenkind")):
            self.assertEqual(struct.unpack_from("<H", item, game.ITEM_TYPE)[0], type_)
            self.assertEqual((item[game.ITEM_PLUS], item[worldgear.ITEM_SPELL]), (0, 0))
            self.assertEqual(npcitems.TYPES[type_ - game.GAME_TYPES][9], slot)
            self.assertEqual(npcitems.TYPES[type_ - game.GAME_TYPES][0x10:0x12], b"\x00\x06")  # (thieves, rangers)
            self.assertEqual(icons.which(item), name)
        self.assertEqual(names.NAMES[worldgear.CLOAK_OF_ELVENKIND], b"Cloak/Elvenkind")
        self.assertEqual(gift("Buried chest").objects, (worldgear.CARAVAN_CHEST,))

    def test_flame_blade(self):
        """The Flame Blade: the obsidian long sword +1 (a fire cleric's to wield), Focus Heat on
        what it hits (one past the game's number, its icon shown too), on the Hot Springs'
        Templar with the Drake Shield."""
        item = worldgear.FLAME_BLADE
        self.assertEqual(struct.unpack_from("<H", item, game.ITEM_TYPE)[0], 45)
        self.assertEqual((item[game.ITEM_PLUS], item[worldgear.ITEM_SPELL]), (1, 117))
        self.assertEqual(struct.unpack_from("<H", item, worldgear.ITEM_SPELL_SHOWN)[0], 117)
        self.assertEqual(icons.which(item), "Flame Blade")
        self.assertEqual(names.NAMES[worldgear.FLAME_BLADE_NAME], b"Flame Blade")
        templar = next(g for g in worldgear.MAGIC if item in g.items)
        self.assertEqual((templar.region, templar.name, templar.objects), (0x23, "Templar", (34,)))

    def test_axes(self):
        """The magic axes: a bone axe +1 (Drakejaw) on one of the Magera guarding the wagon's
        prisoners (an object of his own), an obsidian axe +2 (Glasshewer) on the elven slavers'
        Templar, a metal great axe +2 (Headsman) in the arena Announcer's stash; each named and
        priced 20,800 a plus."""
        cases = ((worldgear.BONE_AXE_1, game.BONE_AXE_TYPE, 1, "Drakejaw", "Magera", (71,), 0x08),
                 (worldgear.OBSIDIAN_AXE_2, game.OBSIDIAN_AXE_TYPE, 2, "Glasshewer", "Templar", (131,), 0x14),
                 (worldgear.GREAT_AXE_2, game.METAL_GREAT_AXE_TYPE, 2, "Headsman", "Announcer", (91,), None))
        for spec, type_, plus, name, holder, objects, region in cases:
            item = worldgear.weapon(*spec)
            self.assertEqual((struct.unpack_from("<H", item, game.ITEM_TYPE)[0], item[game.ITEM_PLUS]), (type_, plus))
            self.assertEqual(struct.unpack_from("<H", item, 6)[0], plus * worldgear.PLUS_VALUE)
            self.assertEqual(icons.which(item), name)
            self.assertEqual(names.NAMES[struct.unpack_from("<H", item, game.ITEM_NAME)[0]], name.encode())
            g = next(g for g in worldgear.MAGIC if item in g.items)
            self.assertEqual((g.name, g.objects, g.region), (holder, objects, region))
        rack = next(g for g in worldgear.MAGIC if g.name == "Weapon Rack")
        self.assertEqual((rack.clone, rack.instead), ((131, worldgear.PENS_RACK_OBJECT), (19, 0)))
        self.assertEqual(gift("Magera").clone, (122, 2562))
        # (the plain axes still the plain ones)
        self.assertEqual(icons.which(worldgear.weapon(worldgear.BONE_AXE)), "Bone Axe")
        self.assertEqual(icons.which(worldgear.weapon(worldgear.OBSIDIAN_AXE)), "Obsidian Axe")

    def test_weapons_for_the_few(self):
        """Galefang (an air cleric's dagger +2, DSCLOG's own type), Mindshard and Stillwater (a
        psionicist's short swords +1, obsidian and bone), Linebreaker and Thornwall (polearms +2 and
        +1): named, priced, with their holders (Stillwater in Chaya's chest, Thornwall on the pens'
        rack, its own object, in place of a plain one); Galefang's type an air cleric's, the short
        swords' a lone psionicist's."""
        import test_restrict
        cases = ((worldgear.AIR_DAGGER_2, game.AIR_DAGGER_TYPE, 2, "Galefang", "Rogue Shaman", (77,), 0x0F),
                 (worldgear.OBSIDIAN_SHORT_SWORD_1, game.OBSIDIAN_SHORT_SWORD_TYPE, 1, "Mindshard", "Maris", (228,), 0x22),
                 (worldgear.BONE_SHORT_SWORD_1, game.BONE_SHORT_SWORD_TYPE, 1, "Stillwater", "Chaya's chest", (2249,), None),
                 (worldgear.POLEARM_2, game.METAL_POLEARM_TYPE, 2, "Linebreaker", "Troop Leader", (18,), 0x21),
                 (worldgear.BONE_POLEARM_1, 19, 1, "Thornwall", "Weapon Rack", (1647,), 0x29))
        for spec, type_, plus, name, holder, objects, region in cases:
            item = worldgear.weapon(*spec)
            self.assertEqual((struct.unpack_from("<H", item, game.ITEM_TYPE)[0], item[game.ITEM_PLUS]), (type_, plus))
            self.assertEqual(struct.unpack_from("<H", item, 6)[0], plus * worldgear.PLUS_VALUE)
            self.assertEqual(icons.which(item), name)
            self.assertEqual(names.NAMES[struct.unpack_from("<H", item, game.ITEM_NAME)[0]], name.encode())
            g = next(g for g in worldgear.MAGIC if item in g.items)
            self.assertEqual((g.name, g.objects, g.region), (holder, objects, region))
        record = lambda t: npcitems.TYPES[t - game.GAME_TYPES]
        air = test_restrict.sheet(1, race=game.HUMAN)
        self.assertTrue(restrict.usable(air, game.AIR_DAGGER_TYPE, record(game.AIR_DAGGER_TYPE)))
        # (every dagger an air cleric's: DSCLOG gives the game's its bit too: test_dsclog)
        for t in (game.METAL_DAGGER_TYPE, game.BONE_DAGGER_TYPE):
            self.assertTrue(restrict.usable(air, t, record(t)))
        fire = test_restrict.sheet(3, race=game.HUMAN)
        self.assertFalse(restrict.usable(fire, game.AIR_DAGGER_TYPE, record(game.AIR_DAGGER_TYPE)))
        psionicist = test_restrict.sheet(12, race=game.HUMAN)
        for t in (game.OBSIDIAN_SHORT_SWORD_TYPE, game.BONE_SHORT_SWORD_TYPE):
            self.assertTrue(restrict.usable(psionicist, t, record(t)))
        # (the plain short swords and polearm still the plain ones)
        self.assertEqual(icons.which(worldgear.weapon(worldgear.BONE_SHORT_SWORD)), "Bone Short Sword")
        self.assertEqual(icons.which(worldgear.weapon(worldgear.OBSIDIAN_SHORT_SWORD)), "Obsidian Short Sword")
        self.assertEqual(icons.which(worldgear.weapon(worldgear.METAL_POLEARM)), "Metal Polearm")

    def test_magic_shields(self):
        """Gutterward (the game's wooden Shield +1) on a skeleton of the warrens, its own object;
        Ironbulwark (DSCLOG's metal shield +3) on the Guardian of Balkazar's fortress: named, priced,
        their icons; the metal shield a shield (not armour) for those who may hold the wooden one."""
        import test_restrict
        cases = ((worldgear.WOODEN_SHIELD_1, 16, 1, 25000, "Gutterward", "Skeleton", (2266,), 0x28, (85, 2585)),
                 (worldgear.METAL_SHIELD_3, game.METAL_SHIELD_TYPE, 3, 65000, "Ironbulwark", "Guardian", (216,), 0x0D, None))
        for item, type_, plus, value, name, holder, objects, region, clone in cases:
            self.assertEqual((struct.unpack_from("<H", item, game.ITEM_TYPE)[0], item[game.ITEM_PLUS]), (type_, plus))
            self.assertEqual(struct.unpack_from("<H", item, 6)[0], value)
            self.assertEqual(icons.which(item), name)
            self.assertEqual(names.NAMES[struct.unpack_from("<H", item, game.ITEM_NAME)[0]], name.encode())
            g = next(g for g in worldgear.MAGIC if item in g.items)
            self.assertEqual((g.name, g.objects, g.region, g.clone), (holder, objects, region, clone))
        metal = npcitems.TYPES[game.METAL_SHIELD_TYPE - game.GAME_TYPES]
        self.assertTrue(restrict.is_shield(metal))
        self.assertFalse(restrict.is_armour(metal))
        self.assertEqual(restrict.material(metal), 4)
        self.assertEqual(metal[0x10:0x12], test_restrict.record(16)[0x10:0x12])  # (the wooden one's classes)
        self.assertEqual(worldgear.BASE_TYPES[game.METAL_SHIELD_TYPE], 4)
        # (a plain wooden shield still the game's own)
        plain = bytearray(worldgear.WOODEN_SHIELD_1)
        plain[game.ITEM_PLUS] = 0
        self.assertIsNone(icons.which(bytes(plain)))

    def test_elven_gythka_2(self):
        """The Elven Leader's Gythka +1 a Gythka +2, in his pack and his script's object (an item),
        priced as two pluses; once."""
        from dsloader import dataitems as d
        gythka = bytearray(ITEM)
        struct.pack_into("<H", gythka, game.ITEM_TYPE, game.GYTHKA_TYPE)
        gythka[game.ITEM_PLUS] = 1
        gythka = bytes(gythka)
        chunks = {("RDFF", worldgear.ELVEN_LEADER): rdff(GUARD, [ITEM, gythka]),
                  ("RDFF", worldgear.ELVEN_GYTHKA): rdff(gythka)}
        out = worldgear.gythka_chunks(chunks, {})
        pack = d.items_of(out[("RDFF", worldgear.ELVEN_LEADER)])
        self.assertEqual([(r[game.ITEM_PLUS], struct.unpack_from("<H", r, 6)[0]) for r in pack],
                         [(0, 45), (2, 2 * worldgear.PLUS_VALUE)])
        recs, _ = d.records(out[("RDFF", worldgear.ELVEN_GYTHKA)])
        self.assertEqual(recs[0].data[game.ITEM_PLUS], 2)
        self.assertEqual(worldgear.gythka_chunks({k: out[k] for k in chunks}, {}), {})  # (not twice)
        self.assertNotEqual(icons.which(pack[1]), "Kreenfang")  # (Kreenfang is the gythka +1)

    def test_bracers_not_armour(self):
        """The bracers' type (as DSCLOG has it) isn't armour to the class rules; arm armour is."""
        bracers = npcitems.TYPES[game.BRACERS_TYPE - game.GAME_TYPES]
        self.assertFalse(restrict.is_armour(bracers))
        self.assertTrue(restrict.is_bracers(bracers))
        arm = bytes.fromhex("000000002400fa00" "0503000000000080" "6f170100")  # the leather Arm Armor's (7)
        self.assertTrue(restrict.is_armour(arm))
        self.assertFalse(restrict.is_bracers(arm))


def rdff(head: bytes, items=()) -> bytes:
    """An object's record (as the game's): HEAD (a person, 58 bytes, naming itself object 55;
    or an item, a chest) and ITEMS, each with its type and name, then the end."""
    from dsloader import dataitems as d
    recs = [d.Record(1, 0, 2 if len(head) != game.ITEM_SIZE else 1, 7, 71, head)]
    for i, item in enumerate(items):
        at = len(recs)
        recs.append(d.Record(2 if i == 0 else 4, 0 if i == 0 else at - 3, 1, 16 + i, 79 if i == 0 else 1, item))
        recs.append(d.Record(3, at, 5, struct.unpack_from("<H", item, 0x0A)[0], 4, b""))
        recs.append(d.Record(3, at, 3, struct.unpack_from("<H", item, 0x12)[0], 2, b""))
    return d.chunk(recs, b"\xff" + bytes(9))


GUARD = bytes(6) + struct.pack("<h", -55) + bytes(50)
ITEM = bytes.fromhex("0cfc000000002d000000510000000000" "04ff1c0000")  # (the bone long sword)


class DataTests(unittest.TestCase):
    """The items written into the objects' data (dataitems.py) and the clones' entities."""

    def setUp(self):
        self.chunks = {("RDFF", 55): rdff(GUARD, [ITEM]), ("OJFF", 55): b"guard's look",
                       ("RDFF", 1065): rdff(ITEM, [ITEM]), ("RDFF", 26): rdff(GUARD),
                       ("RDFF", 1564): rdff(ITEM, [ITEM, ITEM])}

    def test_read_and_written_back(self):
        from dsloader import dataitems as d
        for data in self.chunks.values():
            if data[:1] == b"\x01":
                self.assertEqual(d.chunk(*d.records(data)), data)

    def test_after_their_own(self):
        """Into a chest with an item of its own, and to a person with none: after theirs, each
        with its type and name, in no slot and no list."""
        from dsloader import dataitems as d
        gifts = [worldgear.Gift("Wagon Train chest", (worldgear.WARDENS_PLATE[2],), (1065,)),
                 worldgear.Gift("Dagolar", (worldgear.bracers(2), worldgear.WARDENS_PLATE[3]), (26,))]
        out = worldgear.object_chunks(self.chunks, gifts)
        chest = d.items_of(out[("RDFF", 1065)])
        self.assertEqual(len(chest), 2)
        self.assertEqual(icons.which(chest[1]), "Warden's Legs")
        self.assertEqual([icons.which(r) for r in d.items_of(out[("RDFF", 26)])], ["Bracers of Defense", "Warden's Helm"])
        recs, _ = d.records(out[("RDFF", 26)])
        self.assertEqual([(r.level, r.of, r.kind) for r in recs[1:]],
                         [(2, 0, 1), (3, 1, 5), (3, 1, 3), (4, 1, 1), (3, 4, 5), (3, 4, 3)])
        self.assertEqual((recs[2].number, recs[3].number), (game.BRACERS_TYPE, worldgear.BRACERS_NAME))
        for rec in chest[1:]:
            self.assertEqual((rec[game.ITEM_SLOT], rec[4:6], rec[8:10]), (0xFF, b"\0\0", b"\0\0"))

    def test_one_of_a_kind(self):
        """One Castle Guard's polearm: a new object for him (the kind's look, his record naming
        itself), the kind's own unchanged; his region's entity pointed to it."""
        from dsloader import dataitems as d
        guard = worldgear.Gift("Castle Guard", (worldgear.weapon(worldgear.METAL_POLEARM),), (55,), 0x1C, clone=(1, 2560))
        out = worldgear.object_chunks(self.chunks, [guard])
        self.assertNotIn(("RDFF", 55), out)
        self.assertEqual(out[("OJFF", 2560)], b"guard's look")
        self.assertEqual(struct.unpack_from("<h", out[("RDFF", 2560)], 10 + 6)[0], -2560)
        self.assertEqual([icons.which(r) for r in d.items_of(out[("RDFF", 2560)])], [None, "Metal Polearm"])
        entity = struct.Struct("<HHBBh")
        etab = entity.pack(1, 2, 0, 14, -9) + entity.pack(3, 4, 0, 14, -55) + entity.pack(5, 6, 0, 14, -55)
        new = worldgear.region_chunks(0x1C, {("ETAB", 0x1C): etab}, [guard])[("ETAB", 0x1C)]
        self.assertEqual([entity.unpack_from(new, i * 8)[4] for i in range(3)], [-9, -2560, -55])
        self.assertEqual(worldgear.region_chunks(0x1C, {("ETAB", 0x1C): new}, [guard]), {})  # (not twice)

    def test_switches(self):
        """The plain weapons, the magic ones (and the cloak's object), the bone scale set: each by
        its switch."""
        from dsloader import bonescale, dataitems as d
        none = worldgear.data_chunks(self.chunks, {"world_gear": False, "world_magic": False, "pens_gear": False})
        self.assertEqual(none, {})
        pens = worldgear.data_chunks(self.chunks, {"world_gear": False, "world_magic": False})
        self.assertEqual(set(pens), {("RDFF", 1564)})
        self.assertEqual([icons.which(r) for r in d.items_of(pens[("RDFF", 1564)])[2:]], [None, None, "Bone Helm"])
        self.assertEqual([r[:2] for r in d.items_of(pens[("RDFF", 1564)])[2:4]], [bonescale.ARM[:2], bonescale.LEG[:2]])
        magic = worldgear.data_chunks(self.chunks, {"world_gear": False, "pens_gear": False})
        self.assertIn(("RDFF", worldgear.ELVEN_CLOAK_OBJECT), magic)
        self.assertEqual(d.items_of(magic[("RDFF", worldgear.ELVEN_CLOAK_OBJECT)]), [])
        recs, _ = d.records(magic[("RDFF", worldgear.ELVEN_CLOAK_OBJECT)])
        self.assertEqual(icons.which(recs[0].data), "Cloak of Elvenkind")

    def test_every_object_named(self):
        """Every gift names objects; the clones' new numbers are free (past the icons' 2419-2551,
        none of the later icons' and none twice)."""
        pictures = {n for icon in icons.ICONS for n in icon[2:4]}
        clones = [g.clone[1] for g in worldgear.GIFTS + worldgear.MAGIC if g.clone]
        for g in worldgear.GIFTS + worldgear.MAGIC:
            self.assertTrue(g.objects, g.name)
        for n in clones:
            self.assertGreater(n, 2551)
            self.assertNotIn(n, pictures)
        self.assertEqual(len(set(clones)), len(clones))
        self.assertEqual(worldgear.regions(worldgear.GIFTS + worldgear.MAGIC), [0x06, 0x08, 0x1C, 0x1E, 0x28, 0x29])

    def test_regions_opened(self):
        """Every region file the Loader copies for a clone is one DSCLOG opens in the game's place
        (its D:\ copy named in its table of copies): else the game reads its own."""
        exe = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos", "DSCLOG.EXE")
        with open(exe, "rb") as f:
            data = f.read()
        for region in worldgear.regions(worldgear.GIFTS + worldgear.MAGIC):
            self.assertIn(b"D:\\" + worldgear.region_file(region).encode(), data, hex(region))

    def test_in_place_of_one(self):
        """Thornwall on the pens' weapon rack (a thing, its number first in its record): a new
        object, in place of the first of its two plain bone polearms (its type, name and header
        number following), the rest kept; the Lower Castle's rack, the same object, unchanged."""
        from dsloader import dataitems as d
        rack_head = bytes.fromhex("91f900000000010000006c000000000005ffef0000")
        polearm = bytes.fromhex("5efb000000000700000013000000000004ff120000")
        staff = bytes.fromhex("05fc000000000100000003000000000004ff040000")
        self.chunks[("RDFF", 1647)] = rdff(rack_head, [polearm, staff, polearm])
        self.chunks[("OJFF", 1647)] = b"rack's look"
        rack = next(g for g in worldgear.MAGIC if g.name == "Weapon Rack")
        out = worldgear.object_chunks(self.chunks, [rack])
        self.assertNotIn(("RDFF", 1647), out)
        self.assertEqual(out[("OJFF", worldgear.PENS_RACK_OBJECT)], b"rack's look")
        recs, _ = d.records(out[("RDFF", worldgear.PENS_RACK_OBJECT)])
        self.assertEqual(struct.unpack_from("<h", recs[0].data)[0], -worldgear.PENS_RACK_OBJECT)
        self.assertEqual(recs[0].data[2:], rack_head[2:])
        self.assertEqual([icons.which(r) for r in d.items_of(out[("RDFF", worldgear.PENS_RACK_OBJECT)])], ["Thornwall", None, None])
        self.assertEqual(d.items_of(out[("RDFF", worldgear.PENS_RACK_OBJECT)])[1:], [staff, polearm])
        self.assertEqual([(r.kind, r.number) for r in recs[2:4]], [(5, 19), (3, worldgear.THORNWALL)])
        self.assertEqual(len(recs), len(d.records(self.chunks[("RDFF", 1647)])[0]))
        # (none to replace: unchanged)
        self.assertEqual(d.with_item_replaced(self.chunks[("RDFF", 26)], lambda r: True, polearm), self.chunks[("RDFF", 26)])

    def test_pens_rack_with_kalzith(self):
        """The pens' copy, Kalzith's: the rack's entity pointed to its own object, and Kalzith
        after the game's entries."""
        from dsloader import kalzith
        entity = struct.Struct("<HHBBh")
        etab = b"".join(entity.pack(i, i, 0, 13, -9) for i in range(131)) + entity.pack(779, 550, 0, 13, -1647)
        rack = next(g for g in worldgear.MAGIC if g.name == "Weapon Rack")
        from unittest import mock
        with mock.patch.object(kalzith, "read_gff", lambda data: {("ETAB", kalzith.ETAB_ID): etab}):
            new = kalzith.region_chunks(b"", [rack])[("ETAB", kalzith.ETAB_ID)]
            plain = kalzith.region_chunks(b"")[("ETAB", kalzith.ETAB_ID)]
        self.assertEqual(entity.unpack_from(new, 131 * 8)[4], -worldgear.PENS_RACK_OBJECT)
        self.assertEqual(entity.unpack_from(new, 132 * 8)[4], -kalzith.OBJECT)
        self.assertEqual(entity.unpack_from(plain, 131 * 8)[4], -1647)

    def test_never_object_2563(self):
        """No object of the Loader's is numbered 2563 (with one, the game refuses to put an item down
        on another in a pack): the clones, the items' own pictures' objects, Kalzith's, the
        Elven Leader's cloak's and the hay stash's."""
        from dsloader import kalzith
        numbers = {g.clone[1] for g in worldgear.GIFTS + worldgear.MAGIC if g.clone}
        numbers |= set(icons.PICTURES.values()) | {kalzith.OBJECT, worldgear.ELVEN_CLOAK_OBJECT,
                                                    worldgear.HAYNEEDLE_OBJECT}
        self.assertNotIn(worldgear.NOT_AN_OBJECT, numbers)

if __name__ == "__main__":
    unittest.main()
