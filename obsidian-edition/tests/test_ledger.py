"""The dice log's readable layout (ledger.py): its rows and fills from the log's own lines."""
import unittest

from dsloader import ledger
from dsloader.ledger import Fill, Row

PARTY = {"Seneca", "Lex", "Jenna"}


def run(lines):
    lg = ledger.Ledger(PARTY.__contains__)
    out = []
    for line in lines:
        out += lg.feed(line)
    return out


def text(row):
    return "".join(f"[{p.slot[:-1] if p.slot[-1].isdigit() else p.slot}]" if p.slot else p.text for p in row.pieces)


def slot(row, kind):
    return next(p.slot for p in row.pieces if p.slot and p.slot.startswith(kind))


def roles(row):
    return {p.text: p.role for p in row.pieces if p.text.strip()}


ATTACK = ("Seneca attacks Arena Guard BACKSTAB with Bone Hayneedle +1 (1d4+1): d20 = 15, needs 4+ (85%), "
          "hits AC -3, target AC 8 -> HIT")


class LedgerTests(unittest.TestCase):
    def test_hit_with_damage_and_hp(self):
        """A hit: its row (outcome first, slots for the damage and the HP, the roll at the right), the
        THAC0 line made the to-hit working; the damage line fills its slot and gives its working; the
        HP line fills the HP slot."""
        ops = run([ATTACK, "    THAC0 19, +2 from behind, +2 backstab, +2 STR, +1 weapon = 12",
                   "  Seneca hits Arena Guard for 11: 1d4 = [3] +1 weapon +4 STR 18",
                   "  Arena Guard now 19/30 HP (-11)"])
        hit, to_hit, dmg_fill, dmg, hp_fill = ops
        self.assertEqual(text(hit), "● Seneca hits Arena Guard[damage] — backstab, Bone Hayneedle +1"
                                    "\t[hp]\td20 15 vs 4+ (85%) · AC 8")
        self.assertEqual(roles(hit)["hits"], ledger.GOOD)
        self.assertEqual(to_hit.kind, ledger.DETAIL)
        self.assertIn("vs AC 8 needs 4+; d20 15 → HIT (would hit AC −3)", text(to_hit))
        self.assertIsInstance(dmg_fill, Fill)
        self.assertEqual("".join(p.text for p in dmg_fill.pieces), " for 11")
        self.assertEqual(dmg_fill.slot, slot(hit, "damage"))
        self.assertEqual(text(dmg), "    damage: Bone Hayneedle +1 (1d4+1): 1d4 = [3] +1 weapon +4 STR 18")
        self.assertEqual("".join(p.text for p in hp_fill.pieces), "19/30 (−11)")

    def test_monster_hit_low_hp(self):
        """A monster's hit is bad for the party; a member left at a third or less is marked."""
        ops = run(["Guard attacks Jenna with Bone Spear (1d8): d20 = 15, needs 13+ (40%), hits AC 1, target AC 3 -> HIT",
                   "    THAC0 18, -2 DEX = 16", "  Guard hits Jenna for 6: 1d8 = [6]", "  Jenna now 5/24 HP (-6)"])
        self.assertTrue(text(ops[0]).startswith("○ Guard hits Jenna"))
        self.assertEqual(roles(ops[0])["hits"], ledger.BAD)
        hp = ops[-1]
        self.assertEqual(hp.pieces[0].text, "! 5/24 (−6)")
        self.assertEqual(hp.pieces[0].role, ledger.BAD)

    def test_miss(self):
        """A miss: dim, no slots; its roll and working."""
        ops = run(["Guard attacks Lex: d20 = 6, needs 13+ (40%), hits AC 10, target AC 3 -> miss", "    THAC0 18 = 18"])
        self.assertEqual(text(ops[0]), "○ Guard misses Lex\t\td20 6 vs 13+ (40%) · AC 3")
        self.assertEqual(roles(ops[0])["misses"], ledger.DIM)
        self.assertIn("d20 6 → miss (would hit AC 10)", text(ops[1]))

    def test_save_and_its_hp(self):
        """A monster's save: dim when made, good for the party when failed; the line itself under it;
        a hit's HP slot for the same creature, still empty, keeps the HP."""
        line = ("Arena Guard's saving throw vs Poison (10 damage) from Seneca (paralysis/poison/death): "
                "d20 = 7, needs 13 (40% to save) -> failed")
        ops = run([ATTACK, "    THAC0 19 = 12", line, "  Arena Guard now 19/30 HP (-11)"])
        save, detail, fill = ops[2], ops[3], ops[4]
        self.assertEqual(text(save), "  Arena Guard fails vs Poison (10 damage)\t\td20 7 vs 13+ (40%)")
        self.assertEqual(roles(save)["fails"], ledger.GOOD)
        self.assertEqual(text(detail), "    " + line)
        self.assertEqual(fill.slot, slot(ops[0], "hp"))  # (the hit's HP slot)

    def test_spell_save_tail(self):
        """A party member's spell save: good when made, what the save left after a dash, the total."""
        line = ("Lex's saving throw vs Fireball from Mage (petrification/polymorph): d20 = 6, doubled against "
                "fire = 12 +1 Blessed = 13, needs 11 (80% to save) -> saved: half damage, 19 of 38")
        save = run([line])[0]
        self.assertEqual(text(save), "  Lex saves vs Fireball — half damage, 19 of 38\t[hp]\td20 6 = 13 vs 11+ (80%)")
        self.assertEqual(roles(save)["saves"], ledger.GOOD)

    def test_round_turn_and_checks(self):
        ops = run(["Round 2: Jenna 32, Seneca 30", "Seneca's turn",
                   "Seneca hides in shadows: d100 = 56, needs 67 or less (57 +10 cloak) -> hidden",
                   "  Seneca moves silently: d100 = 21, needs 77 (67 +10 boots) or less -> unheard",
                   "Arena Guard is killed", "XP: Seneca +120 (for Arena Guard 120)"])
        self.assertTrue(text(ops[0]).startswith("── Round 2 · Jenna 32, Seneca 30 ─"))
        self.assertEqual(text(ops[1]), "▸ Seneca")
        self.assertEqual(text(ops[2]), "● Seneca hides in shadows — hidden\t\td100 56 vs 67 or less")
        self.assertEqual(roles(ops[2])["hidden"], ledger.GOOD)
        self.assertIn("(57 +10 cloak)", text(ops[3]))
        self.assertEqual(text(ops[4]), "  Seneca moves silently — unheard\t\td100 21 vs 77 or less")
        self.assertIn("(67 +10 boots)", text(ops[5]))
        self.assertEqual(text(ops[6]), "  Arena Guard is killed")
        self.assertEqual(ops[7].kind, ledger.PLAIN)

    def test_unmatched_lines_as_they_are(self):
        """A damage or HP line with no row waiting for it, and anything else, shown as written."""
        ops = run(["  Seneca hits Slig for 3: 1d4 = [3]", "  Slig now 5/8 HP (-3)", "Message: hello"])
        self.assertEqual(ops[0].kind, ledger.PLAIN)
        self.assertEqual(ops[0].plain_kind, "damage")
        self.assertEqual(text(ops[1]), "  Slig now 5/8 (−3)")
        self.assertEqual(text(ops[2]), "Message: hello")

    def test_fight_summary(self):
        """The fight's summary: its head, and its members' lines with it (not hidden as working)."""
        ops = run(["Fight over: 2 rounds, 1 kill; the party dealt 28 damage and took 6",
                   "    Seneca: 1 of 1 attacks hit, 21 dealt, 1 kill", "XP: Seneca +120", "    THAC0 19 = 12"])
        self.assertEqual([o.kind for o in ops], [ledger.SUMMARY, ledger.SUMMARY, ledger.PLAIN, ledger.DETAIL])
        self.assertEqual(ops[0].pieces[0].role, ledger.NOTE)
        self.assertEqual(text(ops[1]), "  Seneca: 1 of 1 attacks hit, 21 dealt, 1 kill")

    def test_slots_given_up(self):
        """A slot no fill came for is given up after KEEP rows (its line then shown as written)."""
        ops = run([ATTACK] + ["Message: x"] * (ledger.KEEP + 1) + ["  Seneca hits Arena Guard for 11: 1d4 = [3]"])
        self.assertIsInstance(ops[-1], Row)
        self.assertEqual(ops[-1].kind, ledger.PLAIN)


if __name__ == "__main__":
    unittest.main()
