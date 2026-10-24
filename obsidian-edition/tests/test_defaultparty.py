"""The game's own party made ready for the rule changes (defaultparty.py)."""

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import defaultparty as dp, game, specialize


def sheet(race, classes):
    s = bytearray(game.SHEET_SIZE)
    s[game.SHEET_RACE] = race
    s[game.SHEET_CLASSES:game.SHEET_CLASSES + 3] = bytes(classes)
    return bytes(s)


class FakeGame:
    def __init__(self, party):
        self.party = party  # [(name, sheet)]

    def creature_name(self, member):
        return self.party[member][0] if member < len(self.party) else ""

    def sheet(self, member):
        return self.party[member][1] if member < len(self.party) else b""


DEFAULT = [(name, sheet(m.race, m.classes)) for name, m in dp.PARTY.items()]


class DefaultPartyTests(unittest.TestCase):
    def test_known_by_name_race_and_classes(self):
        gd = FakeGame(DEFAULT + [("Gerakis", sheet(1, (10, 0, 0)))])  # (a human of that name)
        self.assertEqual([dp.who(gd, m) for m in range(5)], list(dp.PARTY) + [""])

    def test_kinds(self):
        """Each one past the kind's number, as the creation panel keeps them."""
        kinds = specialize.KINDS
        self.assertEqual(dp.kinds_bytes(dp.PARTY["Gerakis"]),
                         bytes((kinds.index("long sword") + 1, kinds.index("gythka") + 1, 0, 0)))
        self.assertEqual(dp.kinds_bytes(dp.PARTY["K'ratchek"]), bytes((kinds.index("chatkcha") + 1, 0, 0, 0)))
        self.assertEqual(dp.kinds_bytes(dp.PARTY["Cermak"]),
                         bytes((kinds.index("long sword") + 1, kinds.index("axe") + 1, 0, 0)))
        self.assertEqual(dp.kinds_bytes(dp.PARTY["Cilla"]), bytes(4))

    def ready(self, rules, done=None, new=True, gear=False):
        calls = []
        stub = lambda key: (lambda gd, member, name: calls.append((name, key)) or [f"{name} {key}"])
        with mock.patch("dsloader.tools.new_game", return_value=new), \
                mock.patch.object(dp, "set_kinds", stub("kinds")), \
                mock.patch.object(dp, "club_to_gythka", stub("gythka")), \
                mock.patch.object(dp, "take_armour", stub("armour")), \
                mock.patch.object(dp, "learn", stub("armor spell")), \
                mock.patch.object(dp, "set_kit", stub("kit")), \
                mock.patch.object(dp, "set_own", stub("own")), \
                mock.patch.object(dp, "gear", stub("gear")):
            lines = dp.ready(FakeGame(DEFAULT), rules, set() if done is None else done, gear)
        return calls, lines

    def test_by_the_rules(self):
        everything = game.RULE_SPECIALIZE | game.RULE_HALF_GIANT | game.RULE_RESTRICT
        calls, _ = self.ready(everything)
        self.assertEqual(calls, [("Gerakis", "kinds"), ("Gerakis", "gythka"), ("K'ratchek", "kinds"),
                                 ("Cermak", "kinds"), ("Cilla", "kinds"), ("Cilla", "armour"), ("Cilla", "armor spell")])
        calls, _ = self.ready(game.RULE_SPECIALIZE)  # (no gythka without the half-giants' rule)
        self.assertNotIn(("Gerakis", "gythka"), calls)
        calls, _ = self.ready(game.RULE_RESTRICT)
        self.assertEqual(calls, [("Cilla", "armour"), ("Cilla", "armor spell")])
        calls, _ = self.ready(game.RULE_KITS)  # (Cermak's kit; the others' features of their own)
        self.assertEqual(calls, [("Gerakis", "own"), ("K'ratchek", "own"), ("Cermak", "kit"), ("Cilla", "own")])

    def test_starting_gear(self):
        """Fuller starting gear: each of them, after the other changes (Cilla's armour gone first)."""
        calls, _ = self.ready(game.RULE_RESTRICT, gear=True)
        self.assertEqual(calls, [("Gerakis", "gear"), ("K'ratchek", "gear"), ("Cermak", "gear"),
                                 ("Cilla", "armour"), ("Cilla", "armor spell"), ("Cilla", "gear")])
        self.assertNotIn("gear", [key for _, key in self.ready(game.RULE_RESTRICT)[0]])

    def test_cermak_arcanist(self):
        """Set_kit writes Cermak's kit byte: the Arcanist for his preserver class (place 0, the
        one he has now), none for his gladiator class (place 1); a kit there already is kept."""
        from dsloader import kitpages, kits

        class Guest:
            def __init__(self):
                self.mem = bytearray(0x20000)

            def read(self, at, n):
                return bytes(self.mem[at:at + n])

            def write(self, at, data):
                self.mem[at:at + len(data)] = data

        class Gd:
            ds = 0x1000

            def __init__(self, cermak):
                self.guest = Guest()
                self.guest.write(self.ds * 16 + game.SHEETS_PTR, (0x10).to_bytes(2, "little") + (0x1100).to_bytes(2, "little"))
                self.at = 0x1100 * 16 + 0x10 + 2 * game.SHEET_SIZE
                self.guest.write(self.at, cermak)

            def sheet(self, member):
                return self.guest.read(self.at, game.SHEET_SIZE)

            def creature(self, member):
                rec = bytearray(game.CREATURE_SIZE)
                rec[game.CREATURE_SHEET_INDEX] = 2
                return bytes(rec)

            def max_spell_slots(self, member, bit, level):  # a 1st-level preserver's, the Arcanist's 1 more
                arcanist = kits.ARCANIST in kitpages.kit_ids(self.sheet(member))
                return 1 + arcanist if bit == 1 and level == 1 else 0

            def left(self, member, level):
                return self.guest.read(self.ds * 16 + game.SLOTS_LEFT["Wizard"] + member * game.SLOTS_STRIDE + level, 1)[0]

        cermak = bytearray(sheet(1, (11, 10, 0)))
        gd = Gd(bytes(cermak))
        gd.guest.write(gd.ds * 16 + game.SLOTS_LEFT["Wizard"] + 1, b"\x01")  # as the game filled it: WIZ 1/1
        self.assertEqual(dp.set_kit(gd, 0, "Cermak"), ["Cermak is an Arcanist."])
        self.assertEqual(kitpages.kit_ids(gd.sheet(0)), [kits.ARCANIST])
        self.assertEqual(kitpages.kit_names(gd.sheet(0)), ["Arcanist"])
        self.assertEqual((gd.left(0, 1), gd.left(0, 2)), (2, 0))  # the kit's slot added: WIZ 2/2
        self.assertEqual(dp.set_kit(gd, 0, "Cermak"), [])
        self.assertEqual(gd.left(0, 1), 2)
        # one already cast before the kit came: 1 left of 2, not a free one
        gd = Gd(bytes(cermak))
        dp.set_kit(gd, 0, "Cermak")
        self.assertEqual(gd.left(0, 1), 1)

        # Cilla's own feature: the kit byte's OWN_BIT, her (no) kits as they were; once
        cilla = bytearray(sheet(3, (11, 6, 17)))
        cilla[kitpages.KIT_BYTE] = 0xFF
        gd = Gd(bytes(cilla))
        self.assertEqual(kits.own_race(gd.sheet(0)), 0)
        self.assertEqual(dp.set_own(gd, 0, "Cilla"), [dp.OWN_LINES["Cilla"]])
        self.assertEqual((kits.own_race(gd.sheet(0)), gd.sheet(0)[kitpages.KIT_BYTE]), (kits.ELF, kits.OWN_BIT))
        self.assertEqual(kitpages.kit_ids(gd.sheet(0)), [])
        self.assertEqual(dp.set_own(gd, 0, "Cilla"), [])
        # Gerakis, a gladiator with a kit: kept with it
        gerakis = bytearray(sheet(5, (10, 0, 0)))
        gerakis[kitpages.KIT_BYTE] = 1
        gd = Gd(bytes(gerakis))
        dp.set_own(gd, 0, "Gerakis")
        self.assertEqual((kits.own_race(gd.sheet(0)), kitpages.kit_ids(gd.sheet(0))), (kits.HALF_GIANT, [kits.CHAMPION]))

    def test_once_and_only_while_new(self):
        done = set()
        self.assertTrue(self.ready(game.RULE_RESTRICT, done)[0])
        self.assertEqual(self.ready(game.RULE_RESTRICT, done)[0], [])
        self.assertEqual(self.ready(game.RULE_RESTRICT, new=False)[0], [])


class CillaFigureTests(unittest.TestCase):
    """Cilla, an elf, drawn with the elf woman's figure, not the half-elf woman's."""

    def record(self, figure, name=b"Cilla"):
        rec = bytearray(159)
        rec[0x32:0x32 + len(name) + 1] = name + b"\0"
        rec[dp.RDFF_FIGURE:dp.RDFF_FIGURE + 2] = figure.to_bytes(2, "little")
        return bytes(rec)

    def test_in_the_objects_file(self):
        game_ = {("RDFF", dp.CILLA_OBJECT): self.record(dp.HALF_ELF_WOMAN),
                 ("OJFF", dp.CILLA_OBJECT): bytes(12) + (2099).to_bytes(2, "little") + bytes(2),
                 ("OJFF", 305): bytes(12) + (2059).to_bytes(2, "little") + bytes(2)}
        copy = {**game_, ("OJFF", 305): bytes(12) + (2460).to_bytes(2, "little") + bytes(2)}
        out = dp.figure_chunks(game_, copy)
        self.assertEqual(out[("RDFF", dp.CILLA_OBJECT)][dp.RDFF_FIGURE], dp.ELF_WOMAN)
        self.assertEqual(out[("OJFF", dp.CILLA_OBJECT)][12:14], (2059).to_bytes(2, "little"))  # (the game's picture)
        self.assertEqual(dp.figure_chunks({("RDFF", dp.CILLA_OBJECT): self.record(dp.ELF_WOMAN)}), {})
        self.assertEqual(dp.figure_chunks({("RDFF", dp.CILLA_OBJECT): self.record(7, b"Other")}), {})
        self.assertEqual(dp.figure_chunks({}), {})

    def test_in_a_running_game(self):
        class Guest:
            def __init__(self):
                self.mem = bytearray(0x40000)

            def read(self, at, n):
                return bytes(self.mem[at:at + n])

            def write(self, at, data):
                self.mem[at:at + len(data)] = data

        class Gd(FakeGame):
            ds = 0x1000

            def __init__(self, party):
                super().__init__(party)
                self.guest = Guest()
                self.guest.write(self.ds * 16 + game.CREATURES_PTR, (0).to_bytes(2, "little") + (0x2000).to_bytes(2, "little"))
                self.base = 0x2000 * 16
                for m in range(len(party)):
                    self.guest.write(self.base + m * game.CREATURE_SIZE + dp.CREATURE_FIGURE, (dp.HALF_ELF_WOMAN).to_bytes(2, "little"))

            def creature(self, member):
                return self.guest.read(self.base + member * game.CREATURE_SIZE, game.CREATURE_SIZE)

        gd = Gd(DEFAULT)
        cilla = list(dp.PARTY).index("Cilla")
        self.assertTrue(dp.elf_figure(gd))
        self.assertEqual(gd.creature(cilla)[dp.CREATURE_FIGURE], dp.ELF_WOMAN)
        self.assertEqual(gd.creature(0)[dp.CREATURE_FIGURE], dp.HALF_ELF_WOMAN)  # (only hers)
        self.assertEqual(dp.elf_figure(gd), [])  # (once)


class SpellZeroTests(unittest.TestCase):
    def test_armor_is_a_spell(self):
        """Spell 0 (Armor) is one of the game's: named, levelled and listed."""
        self.assertEqual(game.SPELL_FIRST, 0)
        self.assertEqual(dp.KNOWN_STRIDE, 138)


if __name__ == "__main__":
    unittest.main()
