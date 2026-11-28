"""Wake of the Ravager's quests for the Journal tab (ravquests.py): the table's shape, the Loader's
layout for the sequel putting it in quests.py's place, the sequel's flags read from its saves, and,
with the sequel's folder (DSUN_WOTR), the table held to its scripts as test_quests.py holds Shattered
Lands': each "done" condition set beside a reward of the script named, every reward of the sequel's
routine in a quest or in the list of those left out, and each reward told by its message alone
unlike any other in its region."""

import glob
import os
import sys
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from dsloader import game, gff, gpl, journal, questdraft, quests, ravlog, ravquests
from dsloader.quests import FINISHED, HIGH, MEDIUM

WOTR = os.environ.get("DSUN_WOTR")
SAVES = os.path.join(os.path.dirname(HERE), "playtest", "saves")
STARTS = (0x14, 0x1B, 0x1C, 0x6D, 0x6E, 0x6F)  # (a call, or a script set on an object or a place: test_quests)
SHARED = 0x63  # (MAS 99: a master script of no region the party is in, whose scripts run beside the regions')


def conds(quest):
    return quest.given + quest.done + quest.steps


class TableTests(unittest.TestCase):
    def test_shape(self):
        keys = [q.key for q in ravquests.QUESTS]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(len({q.name for q in ravquests.QUESTS}), len(keys))
        for q in ravquests.QUESTS:
            with self.subTest(q.key):
                self.assertTrue(q.name and q.area and q.ended and q.sites)
                self.assertTrue(q.done or q.reward, "nothing ends it")
                self.assertEqual(bool(q.told), bool(q.given))
                self.assertFalse(q.ours, "the Loader adds nothing to the sequel's story")
                for text in (q.name, q.area, q.ended, q.told):
                    self.assertEqual(text, " ".join(text.split()))
                if q.reward and not q.done:
                    self.assertEqual(q.confidence, MEDIUM)
                for cond in conds(q):
                    if cond[0] == "flag":
                        self.assertTrue(0 <= cond[1] < game.FLAG_COUNT)
                    else:
                        self.assertTrue(0 <= cond[1] < journal.NUMBERS[0])

    def test_no_flag_means_two_things(self):
        seen = {}
        for q in ravquests.QUESTS:
            for cond in set(conds(q)):
                if cond[0] == "flag":
                    self.assertNotIn(cond[1], seen, f"{q.key} and {seen.get(cond[1])}")
                    seen[cond[1]] = q.key
            self.assertFalse(set(q.given) & set(q.done), q.key)

    def test_left_out_is_not_in(self):
        used = [site for q in ravquests.QUESTS for site in q.sites]
        self.assertEqual(len(used), len(set(used)))
        self.assertFalse(set(used) & set(ravquests.LEFT_OUT))

    def test_the_layout_puts_it_in_place(self):
        sl = quests.QUESTS
        try:
            ravlog.apply_layout()
            self.assertIs(quests.QUESTS, ravquests.QUESTS)
            self.assertIs(quests.BY_KEY, ravquests.BY_KEY)
            self.assertEqual((quests.SAVE_FLAGS, quests.SAVE_NUMBERS), (("SAVE", 30), ("SAVE", 31)))
            self.assertEqual((game.FLAGS_PTR, game.NUMBERS_PTR), (ravlog.RAV_FLAGS_PTR, ravlog.RAV_NUMBERS_PTR))
            done = quests.listing(quests.State(bytes(13) + b"\x01"), ())[1]  # (flag 104: Dmitri)
            self.assertEqual([q.key for q in done], ["dmitri"])
        finally:
            ravlog.restore_layout()
        self.assertIs(quests.QUESTS, sl)
        self.assertEqual(quests.SAVE_FLAGS, ("SAVE", 29))
        self.assertEqual(game.FLAGS_PTR, 0x1352)

    def test_the_sequel_reads_its_quests(self):
        """The pass's quest_look is the sequel's too (it reads the flags through game.FLAGS_PTR)."""
        names = [step.name for step in ravlog.RavDiceLog.PASS]
        self.assertIn("quest_look", names)
        self.assertNotIn("quest_look", ravlog.PASS_LEFT_OUT)

    def test_the_test_saves(self):
        """The sequel's test saves: SAVE 30 the flags (101 bytes), SAVE 31 the numbers; the roost's
        holds three flags and no quest of the table yet."""
        try:
            ravlog.apply_layout()
            for name, flags in (("ravager-after-ambush", [354]), ("ravager-roost", [74, 354, 369])):
                with open(os.path.join(SAVES, name, "SAVE01.SAV"), "rb") as f:
                    chunks = gff.read_gff(f.read())
                self.assertEqual(len(chunks[quests.SAVE_FLAGS]), 101)
                read = quests.save_state(chunks)
                self.assertEqual([n for n in range(game.FLAG_COUNT) if read.flag(n)], flags)
                self.assertEqual(read.number(87), 100)
                self.assertEqual(quests.listing(read, ()), ([], []))
        finally:
            ravlog.restore_layout()


@unittest.skipUnless(WOTR, "DSUN_WOTR: the player's Wake of the Ravager folder")
class ScriptTests(unittest.TestCase):
    """The table against the sequel's scripts."""

    @classmethod
    def setUpClass(cls):
        path = next(f for f in glob.glob(os.path.join(WOTR, "*")) if f.lower().endswith("gpldata.gff"))
        cls.flags = questdraft.load(path)
        cls.routine = {(s.script[1], s.at): s for s in cls.flags.sites()}
        cls.direct = {(s.script[1], s.at): s for s in cls.flags.direct_sites()}
        cls.regions = cls._regions(cls.flags)

    @staticmethod
    def _regions(flags):
        """Each script's regions: those whose master script starts it, itself or through one other."""
        def started(key):
            return {op.args[1][1] for op in gpl.walk(flags.ops.get(key, []))
                    if op.code in STARTS and op.args[1][0] == "n"}
        out = {}
        for kind, region in flags.ops:
            if kind == "MAS ":
                first = started(("MAS ", region))
                for script in first | {s for g in first for s in started(("GPL ", g))}:
                    out.setdefault(script, set()).add(region)
        return out

    def site(self, at):
        return self.routine.get(at) or self.direct[at]

    def test_the_scripts_decode(self):
        self.assertEqual(self.flags.rules, questdraft.SEQUEL)
        self.assertEqual(self.flags.undecoded, [])
        self.assertEqual(len(self.flags.ops), 350)
        for key, ops in self.flags.ops.items():  # (every jump lands on a command: the decoder's check)
            starts = {op.at for op in ops}
            for op in ops:
                if op.code in (0x13, 0x3E, 0x3F, 0x63, 0x64) and op.args and op.args[0][0] == "n":
                    self.assertIn(op.args[0][1], starts, f"{key} at {op.at}")

    def test_what_the_research_counted(self):
        sites = self.flags.sites()
        self.assertEqual((len(sites), len({s.script for s in sites}), sum(s.xp or 0 for s in sites)), (125, 60, 857150))
        self.assertEqual(len(self.direct), 103)
        self.assertEqual(self.flags.scratch(), [17, 19, 21, 23, 24, 46, 47, 51, 54, 56, 65, 67])

    def test_every_reward_is_in_a_quest_or_left_out(self):
        used = {}
        for q in ravquests.QUESTS:
            for at in q.sites:
                self.assertTrue(at in self.routine or at in self.direct, f"{q.key}: no reward at {at}")
                used[at] = q.key
        self.assertEqual(set(self.routine) - set(used), set(ravquests.LEFT_OUT))

    def near(self, q, cond):
        for at in q.sites:
            site = self.site(at)
            if cond[0] == "flag" and any(u.flag == cond[1] and u.value != 0 for u in site.near):
                return True
            if cond[0] == "number" and any(n == cond[1] and value >= cond[2] for n, value, _at in site.numbers):
                return True
        return False

    def in_script(self, q, cond):
        scripts = {("GPL ", at[0]) for at in q.sites}
        if cond[0] == "flag":
            return any(u.script in scripts for u in self.flags.set_in(cond[1]))
        return any(key in scripts and value is not None and value >= cond[2]
                   for key, _at, value in self.flags.number_sets(cond[1]))

    def test_done_is_set_by_the_reward(self):
        for q in ravquests.QUESTS:
            for cond in q.done:
                with self.subTest(q.key, cond=cond):
                    if q.confidence == HIGH:
                        self.assertTrue(self.near(q, cond), "not beside a reward of its script")
                    else:
                        self.assertTrue(self.in_script(q, cond), "not set in a script of its rewards")
                    if cond[0] == "flag" and not q.reward:
                        self.assertEqual(self.flags.cleared_in(cond[1]), [], "a script clears it")

    def test_given_is_set_by_the_game(self):
        for q in ravquests.QUESTS:
            for cond in q.given + q.steps:
                with self.subTest(q.key, cond=cond):
                    self.assertTrue(self.flags.set_in(cond[1]))

    def test_no_scratch_flag(self):
        scratch = set(self.flags.scratch())
        for q in ravquests.QUESTS:
            self.assertFalse(scratch & {c[1] for c in conds(q) if c[0] == "flag"}, q.key)

    def test_a_reward_told_by_its_message_is_like_no_other(self):
        for q in ravquests.QUESTS:
            if q.reward is None:
                continue
            with self.subTest(q.key):
                own = [self.routine[at] for at in q.sites if at in self.routine]
                self.assertTrue(any(q.reward.xp in s.amounts and s.party == q.reward.party
                                    and self.regions.get(s.script[1], set()) & set(q.reward.regions) for s in own))
                for at, s in self.routine.items():
                    if at in q.sites or s.party != q.reward.party:
                        continue
                    if not (self.regions.get(s.script[1], set()) - {SHARED}) & set(q.reward.regions):
                        continue
                    self.assertTrue(s.amounts and s.xp is not None, f"{at}: an amount not known, in its region")
                    self.assertNotIn(q.reward.xp, s.amounts, f"{at} gives the same in the same region")

    def test_no_line_is_the_games(self):
        """The table is in the project's own words: none of its lines holds one of the scripts' lines."""
        theirs = {" ".join(text.split()).casefold() for ops in self.flags.ops.values() for text in gpl.strings(ops)
                  if text and len(" ".join(text.split())) >= 20}
        for q in ravquests.QUESTS:
            for ours in (q.told, q.ended):
                self.assertFalse(any(line in ours.casefold() for line in theirs), f"{q.key}: {ours}")

    def test_a_finished_quest_from_the_game(self):
        """A reading with a quest's done flag lists it finished, the sequel's table in place."""
        try:
            ravlog.apply_layout()
            bits = bytearray(quests.FLAG_BYTES)
            bits[253 // 8] |= 1 << (253 % 8)
            self.assertEqual(quests.status(ravquests.BY_KEY["elder-brain"], quests.State(bytes(bits))), FINISHED)
        finally:
            ravlog.restore_layout()


if __name__ == "__main__":
    unittest.main()
