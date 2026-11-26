"""The Journal tab's quests (quests.py): the table's shape, what is open and what is finished, the
reading of the game's flags and numbers (from memory and from the test saves), the last reading
kept for when the game isn't running, the tab on a real window, and, with the game's GPLDATA.GFF
(DSUN_GPLDATA), the table held to the scripts: each "done" flag set beside a reward in the script
named, each "given" flag set by the game, every reward of the game's routine in a quest or in the
list of those left out, and each reward told by its message alone unlike any other."""

import glob
import io
import os
import struct
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from dsloader import champions, dicelog, game, gff, gpl, journal, questdraft, quests, ring, semyon, vulture
from dsloader.quests import FINISHED, HIGH, MEDIUM, OPEN, F, N, State

GPLDATA = os.environ.get("DSUN_GPLDATA")
SAVES = os.path.join(os.path.dirname(HERE), "playtest", "saves")
FIRST_OURS = 756  # (the game's flags run to 755: DEVELOPMENT.md's The Loader's game flags)
EACH, ONE = "Each party member receives {} experience points!", "Cilla receives {} experience points!"


def state(*flags, numbers=None):
    """A reading with FLAGS set and NUMBERS ({number: value}; None: the numbers not read)."""
    bits = bytearray(quests.FLAG_BYTES)
    for n in flags:
        bits[n // 8] |= 1 << (n % 8)
    if numbers is None:
        return State(bytes(bits))
    words = [0] * quests.NUMBER_COUNT
    for n, value in numbers.items():
        words[n] = value
    return State(bytes(bits), struct.pack(f"<{quests.NUMBER_COUNT}h", *words))


def conds(quest):
    return quest.given + quest.done + quest.steps


class TableTests(unittest.TestCase):
    def test_shape(self):
        keys = [q.key for q in quests.QUESTS]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(len({q.name for q in quests.QUESTS}), len(keys))
        for q in quests.QUESTS:
            with self.subTest(q.key):
                self.assertTrue(q.name and q.area and q.ended)
                self.assertTrue(q.done or q.reward, "nothing ends it")
                self.assertEqual(bool(q.told), bool(q.given), "an open quest's words go with what gives it")
                self.assertIn(q.confidence, (HIGH, MEDIUM))
                self.assertTrue(q.ours or q.sites, "the game's quests name the rewards they were read from")
                self.assertTrue(set(q.steps) <= set(q.given) | set(q.done) or not q.steps)
                for text in (q.name, q.area, q.ended, q.told):
                    self.assertEqual(text, " ".join(text.split()))
                if q.reward and not q.done:
                    self.assertEqual(q.confidence, MEDIUM, "a message alone is never sure")

    def test_no_flag_means_two_things(self):
        """A flag belongs to one quest; a number's stage may end one errand and begin the next."""
        seen = {}
        for q in quests.QUESTS:
            for cond in set(conds(q)):
                if cond[0] == "flag":
                    self.assertNotIn(cond[1], seen, f"{q.key} and {seen.get(cond[1])} share flag {cond[1]}")
                    seen[cond[1]] = q.key
        for q in quests.QUESTS:  # (and within a quest, what gives it never ends it)
            self.assertFalse(set(q.given) & set(q.done), q.key)

    def test_whose_flags(self):
        for q in quests.QUESTS:
            for cond in conds(q):
                if cond[0] == "flag":
                    self.assertTrue(0 <= cond[1] < game.FLAG_COUNT)
                    self.assertEqual(cond[1] >= FIRST_OURS, q.ours, f"{q.key}: flag {cond[1]}")
                else:
                    self.assertTrue(0 <= cond[1] < journal.NUMBERS[0], "one of the game's own numbers")
                    self.assertFalse(q.ours)

    def test_our_quests_use_the_modules_flags(self):
        by = quests.BY_KEY
        self.assertEqual((by["shipment"].given, by["shipment"].done), ((F(semyon.TOLD),), (F(semyon.FOUND),)))
        self.assertEqual((by["champions"].given, by["champions"].done), ((F(champions.KING),), (F(champions.FOUGHT),)))
        self.assertEqual(by["proper-meal"].done, (F(vulture.EATEN),))
        self.assertEqual(by["arena-ring"].done, (F(ring.XP_GIVEN),))

    def test_left_out_is_not_in(self):
        used = {site for q in quests.QUESTS for site in q.sites}
        self.assertFalse(used & set(quests.LEFT_OUT))
        for site in used | set(quests.LEFT_OUT):
            self.assertIn(site[0], set(quests.SCRIPT_REGIONS) | {6, 62, 91, 92, 125}, site)


class LogicTests(unittest.TestCase):
    def test_given_then_done(self):
        gilal = quests.BY_KEY["gilal"]
        self.assertIsNone(quests.status(gilal, state()))
        self.assertEqual(quests.status(gilal, state(527)), OPEN)
        self.assertEqual(quests.status(gilal, state(528)), FINISHED)  # (the game clears 527 then)
        self.assertEqual(quests.status(gilal, state(527, 528)), FINISHED)
        self.assertIsNone(quests.status(gilal, None))

    def test_done_only_is_not_listed_before(self):
        self.assertEqual(quests.listing(state()), ([], []))
        open_, finished = quests.listing(state(26, 503))
        self.assertEqual(([q.key for q in open_], [q.key for q in finished]), ([], ["bound-prisoner", "escape"]))

    def test_numbers(self):
        keys = lambda s: tuple([q.key for q in part] for part in quests.listing(s))
        self.assertEqual(keys(state(581, numbers={96: 1})), (["notaku-delivery"], []))
        self.assertEqual(keys(state(numbers={96: 2})), (["notaku-bloom"], ["notaku-delivery"]))
        self.assertEqual(keys(state(numbers={96: 4})), (["notaku-stinger"], ["notaku-delivery", "notaku-bloom"]))
        self.assertEqual(keys(state(numbers={96: 6})), ([], ["notaku-delivery", "notaku-bloom", "notaku-stinger"]))
        self.assertEqual(keys(state(581)), (["notaku-delivery"], []))  # (the numbers not read: the flag still tells)
        self.assertEqual(keys(state(numbers={37: 3})), ([], ["katti"]))
        self.assertEqual(keys(state(numbers={37: 2})), ([], []))

    def test_steps(self):
        temple = quests.BY_KEY["temple"]
        self.assertEqual((quests.status(temple, state(616)), quests.progress(temple, state(616))), (OPEN, "1 of 3"))
        self.assertEqual(quests.progress(temple, state(616, 596)), "2 of 3")
        self.assertEqual(quests.status(temple, state(616, 595, 596, 597)), FINISHED)
        self.assertEqual(quests.progress(quests.BY_KEY["gilal"], state(527)), "")

    def test_rewards(self):
        self.assertEqual(quests.reward_of(EACH.format(3000), 8), (8, 3000, True))
        self.assertEqual(quests.reward_of(ONE.format(500), 40), (40, 500, False))
        self.assertEqual(quests.reward_of("Each party member  receives 5,000 experience points.", None), (None, 5000, True))
        self.assertIsNone(quests.reward_of("The door is locked.", 8))
        self.assertIsNone(quests.reward_of("Congratulations! The party gains 4,000 exp!", 8))  # (not the routine's)
        captives, lever = quests.BY_KEY["captives"], quests.BY_KEY["drain-lever"]
        self.assertEqual(quests.status(captives, state(), [(8, 3000, True)]), FINISHED)
        self.assertEqual(quests.status(captives, None, [(8, 3000, True)]), FINISHED)
        for other in ((9, 3000, True), (8, 3000, False), (8, 1000, True), (None, 3000, True)):
            self.assertIsNone(quests.status(captives, state(), [other]), other)
        self.assertEqual(quests.status(lever, state(), [(40, 500, False)]), FINISHED)
        self.assertIsNone(quests.status(lever, state(), [(40, 500, True)]))
        kalinin = quests.BY_KEY["kalinin"]  # (its flag is cleared at the last battle: the reward still tells)
        self.assertEqual(quests.status(kalinin, state(268)), FINISHED)
        self.assertEqual(quests.status(kalinin, state(), [(8, 1000, True)]), FINISHED)

    def test_rewards_of_entries(self):
        entries = [journal.Entry(1, 0, journal.TALK, 10, 8, text=EACH.format(3000)),
                   journal.Entry(2, 1, journal.REWARD, 20, 8, text=EACH.format(3000)),
                   journal.Entry(3, 2, journal.REWARD, 30, 40, text="Congratulations! The party gains 4,000 exp!"),
                   journal.Entry(4, 3, journal.REWARD, 40, None, text=ONE.format(50))]
        self.assertEqual(quests.rewards_of(entries), [(8, 3000, True), (None, 50, False)])

    def test_rows_keep_spoilers_out(self):
        made, open_, finished = quests.rows(state(527, 26, 616))
        text = "\n".join(line for _kind, line in made)
        self.assertEqual((open_, finished), (2, 1))
        self.assertEqual(made[0], ("day", "Open (2)"))
        self.assertIn(("day", "Finished (1)"), made)
        self.assertIn(("speaker", "Gilal's pain - The slave pens"), made)
        self.assertIn(("text", quests.BY_KEY["gilal"].told), made)
        self.assertIn(("reply", "  Done so far: 1 of 3"), made)
        self.assertIn(("reward", quests.BY_KEY["bound-prisoner"].ended), made)
        for q in quests.QUESTS:  # (nothing of how an open quest ends, nothing of a quest not met)
            if q.key != "bound-prisoner":
                self.assertNotIn(q.ended, text, q.key)
            if q.key not in ("gilal", "temple", "bound-prisoner"):
                self.assertNotIn(q.name, text)
        self.assertEqual(quests.rows(state()), ([], 0, 0))
        self.assertEqual(quests.rows(None, note="Not read.")[0], [("note", "Not read."), ("gap", "")])

    def test_words_wanted(self):
        made, open_, finished = quests.rows(state(527, 26, 616), wanted="GILAL")
        self.assertEqual((open_, finished), (1, 0))
        self.assertNotIn("Finished", "\n".join(line for _k, line in made))
        self.assertEqual(quests.rows(state(527, 26), wanted="dinos")[1:], (0, 0))  # (how it ends isn't searched while open)
        self.assertEqual(quests.rows(state(528), wanted="dinos")[1:], (0, 1))
        self.assertEqual(quests.rows(state(527, 26), wanted="arena")[1:], (0, 1))

    def test_count_text(self):
        self.assertEqual(quests.count_text(0, 0), "No quests yet")
        self.assertEqual(quests.count_text(2, 5), "2 open, 5 finished")


class Guest:
    def __init__(self):
        self.mem = bytearray(0x30000)

    def read(self, addr, size):
        return bytes(self.mem[addr:addr + size])


class ReadingTests(unittest.TestCase):
    """The flags and numbers in the game's memory, at their far pointers."""

    def game(self):
        return SimpleNamespace(guest=Guest(), ds=0x1000)

    def test_read(self):
        gd = self.game()
        self.assertIsNone(quests.read_state(gd))  # (the flags' pointer null)
        struct.pack_into("<HH", gd.guest.mem, gd.ds * 16 + game.FLAGS_PTR, 0x0010, 0x1800)
        flags = 0x1800 * 16 + 0x10
        gd.guest.mem[flags + 528 // 8] |= 1 << (528 % 8)
        gd.guest.mem[flags + 807 // 8] |= 1 << (807 % 8)
        gd.guest.mem[flags + quests.FLAG_BYTES] = 0xFF  # (past the flags: not read)
        read = quests.read_state(gd)
        self.assertTrue(read.flag(528) and read.flag(807))
        self.assertFalse(read.flag(527) or read.flag(808) or read.flag(-1))
        self.assertIsNone(read.number(96))  # (the numbers' pointer null: not read)
        self.assertFalse(read.holds(N(96, 0)))
        struct.pack_into("<HH", gd.guest.mem, gd.ds * 16 + game.NUMBERS_PTR, 0x0040, 0x2000)
        struct.pack_into("<h", gd.guest.mem, 0x2000 * 16 + 0x40 + 96 * 2, 4)
        read = quests.read_state(gd)
        self.assertEqual((read.number(96), read.number(95), read.number(200)), (4, 0, None))
        self.assertTrue(read.holds(N(96, 4)) and read.holds(F(528)) and not read.holds(N(96, 5)))

    def test_the_dice_log_keeps_its_last_reading(self):
        gd = self.game()
        log = SimpleNamespace(game=gd, quest_state=None)
        dicelog.DiceLog._quest_look(log)
        self.assertIsNone(log.quest_state)
        struct.pack_into("<HH", gd.guest.mem, gd.ds * 16 + game.FLAGS_PTR, 0x0010, 0x1800)
        gd.guest.mem[0x18010 + 26 // 8] |= 1 << (26 % 8)
        dicelog.DiceLog._quest_look(log)
        self.assertTrue(log.quest_state.flag(26))
        struct.pack_into("<HH", gd.guest.mem, gd.ds * 16 + game.FLAGS_PTR, 0, 0)  # (null again: in the arena)
        dicelog.DiceLog._quest_look(log)
        self.assertTrue(log.quest_state.flag(26))
        log.journal, log.rand_addr = None, 1  # (the game gone: the next one's flags are read afresh)
        dicelog.DiceLog.detach(log)
        self.assertIsNone(log.quest_state)

    def test_readings_compare(self):
        self.assertEqual(state(26), state(26))
        self.assertNotEqual(state(26), state(27))
        self.assertNotEqual(state(26), state(26, numbers={}))
        self.assertEqual(len({state(26), state(26)}), 1)

    def test_snapshot(self):
        with tempfile.TemporaryDirectory() as folder:
            path = quests.snapshot_path(os.path.join(folder, "Journal", "journal.jsonl"))
            self.assertEqual(path, os.path.join(folder, "Journal", "quests.json"))
            self.assertIsNone(quests.load_snapshot(path))
            reading = state(26, 528, numbers={96: 2})
            self.assertTrue(quests.save_snapshot(path, 17, reading))
            self.assertEqual(quests.load_snapshot(path), (17, reading))
            self.assertTrue(quests.save_snapshot(path, 0, state(26)))
            head, read = quests.load_snapshot(path)
            self.assertEqual((head, read.flag(26), read.number(96)), (0, True, None))
            for broken in ("", "[]", '{"head": -1, "flags": ""}', '{"head": 1, "flags": "zz"}', '{"head": true, "flags": ""}'):
                with open(path, "w") as f:
                    f.write(broken)
                self.assertIsNone(quests.load_snapshot(path), broken)
            self.assertFalse(quests.save_snapshot(os.path.join(path, "under", "a-file"), 1, reading))


class SaveTests(unittest.TestCase):
    """The test saves (playtest/saves): each gives a reading, and its quests are the pens' and the
    arena's, as far as its README tells."""

    def reading(self, name):
        with open(os.path.join(SAVES, name, "SAVE01.SAV"), "rb") as f:
            return quests.save_state(gff.read_gff(f.read()))

    def keys(self, name):
        return tuple([q.key for q in part] for part in quests.listing(self.reading(name)))

    def test_every_save_reads(self):
        names = sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(SAVES, "*", "SAVE01.SAV")))
        self.assertGreaterEqual(len(names), 15)
        for name in names:
            with self.subTest(name):
                read = self.reading(name)
                self.assertEqual((len(read.flags), len(read.numbers)), (101, 400))
                self.assertEqual(read.number(96), 0)  # (none has left Draj: Notaku not met)
                for part in quests.listing(read):
                    for q in part:
                        self.assertIn(q.area, (quests.ARENA, quests.PENS), q.key)
                self.assertNotIn("escape", self.keys(name)[1])

    def test_just_out_of_the_arena(self):
        for name in ("pens-after-arena", "pens-kurzak-door", "pens-fire-count4", "pens-new-chest"):
            self.assertEqual(self.keys(name), ([], []), name)

    def test_after_scar(self):
        read = self.reading("pens-after-scar")
        self.assertTrue(read.flag(19) and read.flag(champions.KING) and not read.flag(champions.FOUGHT))
        self.assertEqual(self.keys("pens-after-scar"), (["champions"], []))

    def test_the_shipment(self):
        self.assertEqual(self.keys("pens-thornwall-rack"), (["shipment"], []))
        open_, finished = self.keys("semyon-rack-user")
        self.assertEqual(open_, ["shipment"])
        self.assertEqual(finished, ["bound-prisoner", "arena-ring", "gilal", "pens-door-east", "pens-door-west", "water-pot"])

    def test_by_the_grate(self):
        open_, finished = self.keys("grate-user")
        self.assertEqual(open_, ["shipment"])
        self.assertTrue({"gilal", "pens-door-west", "champions", "proper-meal"} <= set(finished))

    def test_a_save_without_its_flags(self):
        self.assertIsNone(quests.save_state({}))
        self.assertIsNone(quests.save_state({quests.SAVE_FLAGS: b"\x04"}).number(1))  # (no numbers chunk)
        self.assertTrue(quests.save_state({quests.SAVE_FLAGS: b"\x04"}).flag(2))


@unittest.skipUnless(GPLDATA and os.path.isfile(GPLDATA), "needs the game's GPLDATA.GFF (DSUN_GPLDATA)")
class ScriptTests(unittest.TestCase):
    """The table against the game's scripts."""

    @classmethod
    def setUpClass(cls):
        cls.flags = questdraft.load(GPLDATA)
        cls.routine = {(s.script[1], s.at): s for s in cls.flags.sites()}
        cls.direct = {(s.script[1], s.at): s for s in cls.flags.direct_sites()}
        cls.game_quests = [q for q in quests.QUESTS if not q.ours]

    def site(self, at):
        return self.routine.get(at) or self.direct[at]

    def test_what_the_research_counted(self):
        sites = self.flags.sites()
        self.assertEqual((len(sites), len({s.script for s in sites}), sum(s.xp or 0 for s in sites)), (57, 40, 78510))
        self.assertTrue(all(s.script[0] == "GPL " for s in sites))
        self.assertEqual(len(self.direct), 34)
        self.assertEqual(self.flags.scratch(), [5, 8, 9, 11, 13, 70, 316, 317, 318, 319, 320])

    def test_every_reward_is_in_a_quest_or_left_out(self):
        used = {}
        for q in self.game_quests:
            for at in q.sites:
                self.assertTrue(at in self.routine or at in self.direct, f"{q.key}: no reward at {at}")
                self.assertNotIn(at, used, f"{q.key} and {used.get(at)}")
                used[at] = q.key
        self.assertEqual(set(self.routine) - set(used), set(quests.LEFT_OUT))
        self.assertEqual(len(set(self.routine) & set(used)), 49)

    def near(self, q, cond):
        """COND is made true within questdraft.NEAR commands of one of the quest's rewards."""
        for at in q.sites:
            site = self.site(at)
            if cond[0] == "flag" and any(u.flag == cond[1] and u.value != 0 for u in site.near):
                return True
            if cond[0] == "number" and any(n == cond[1] and value >= cond[2] for n, value, _at in site.numbers):
                return True
        return False

    def in_script(self, q, cond):
        """COND is made true somewhere in a script of one of the quest's rewards."""
        scripts = {("GPL ", at[0]) for at in q.sites}
        if cond[0] == "flag":
            return any(u.script in scripts for u in self.flags.set_in(cond[1]))
        return any(key in scripts and value is not None and value >= cond[2]
                   for key, _at, value in self.flags.number_sets(cond[1]))

    def test_done_is_set_by_the_reward(self):
        for q in self.game_quests:
            for cond in q.done:
                with self.subTest(q.key, cond=cond):
                    if q.confidence == HIGH:
                        self.assertTrue(self.near(q, cond), "not beside a reward of its script")
                    else:
                        self.assertTrue(self.in_script(q, cond), "not set in a script of its rewards")
                    if cond[0] == "flag" and not q.reward:
                        self.assertEqual(self.flags.cleared_in(cond[1]), [], "a script clears it")
            if q.confidence == MEDIUM and q.done:  # (what could be HIGH is)
                self.assertFalse(all(self.near(q, cond) for cond in q.done) and not q.reward
                                 and q.key not in ("notaku-bloom", "notaku-stinger"), q.key)

    def test_given_is_set_by_the_game(self):
        for q in self.game_quests:
            for cond in q.given + q.steps:
                with self.subTest(q.key, cond=cond):
                    if cond[0] == "flag":
                        self.assertTrue(self.flags.set_in(cond[1]))
                    else:
                        self.assertTrue(any(value is not None and value >= cond[2]
                                            for _key, _at, value in self.flags.number_sets(cond[1])))

    def test_no_scratch_flag(self):
        scratch = set(self.flags.scratch())
        for q in self.game_quests:
            self.assertFalse(scratch & {c[1] for c in conds(q) if c[0] == "flag"}, q.key)

    def test_our_flags_are_not_the_games(self):
        for q in quests.QUESTS:
            if q.ours:
                for cond in conds(q):
                    self.assertEqual(self.flags.uses.get(cond[1], []), [], f"{q.key}: the game uses flag {cond[1]}")

    def test_a_reward_told_by_its_message_is_like_no_other(self):
        self.assertEqual(set(quests.SCRIPT_REGIONS), {s.script[1] for s in self.flags.sites()})
        for q in self.game_quests:
            if q.reward is None:
                continue
            with self.subTest(q.key):
                own = [self.routine[at] for at in q.sites if at in self.routine]
                self.assertTrue(any(q.reward.xp in s.amounts and s.party == q.reward.party
                                    and set(quests.SCRIPT_REGIONS[s.script[1]]) & set(q.reward.regions) for s in own))
                for at, s in self.routine.items():
                    if at in q.sites or s.party != q.reward.party:
                        continue
                    if not set(quests.SCRIPT_REGIONS[s.script[1]]) & set(q.reward.regions):
                        continue
                    self.assertTrue(s.amounts and s.xp is not None, f"{at}: an amount not known, in its region")
                    self.assertNotIn(q.reward.xp, s.amounts, f"{at} gives the same in the same region")

    def test_the_regions_start_the_scripts(self):
        """Each script of SCRIPT_REGIONS is started by its regions' master scripts, itself or
        through one other script (a call, or a script set on an object or a place)."""
        starts = (0x14, 0x1B, 0x1C, 0x6D, 0x6E, 0x6F)

        def started(key):
            return {op.args[1][1] for op in gpl.walk(self.flags.ops.get(key, []))
                    if op.code in starts and op.args[1][0] == "n"}

        for script, regions in quests.SCRIPT_REGIONS.items():
            for region in regions:
                first = started(("MAS ", region))
                reach = first | {s for g in first for s in started(("GPL ", g))}
                self.assertIn(script, reach, f"region {region} doesn't start script {script}")

    def test_the_draft(self):
        with tempfile.TemporaryDirectory() as folder:
            out = os.path.join(folder, "draft.txt")
            self.assertEqual(questdraft.main([GPLDATA, "-o", out]), 0)
            with open(out, encoding="utf-8") as f:
                text = f.read()
        self.assertTrue(text.startswith("57 reward calls in 40 scripts, 78510 XP in all; 34 awards"))
        self.assertIn("=== GPL 139 at 331: 350 XP, each party member", text)
        self.assertIn("  beside it: flag 528 = 1 at 342", text)
        self.assertIn("=== GPL 12 at 428: 1000 or 500 XP, each party member", text)
        self.assertIn("  beside it: number 96 = 2 at 341", text)
        self.assertIn("=== GPL 62 at 5852: 20000 XP, each party member (the script itself gives it)", text)
        printed = io.StringIO()
        with redirect_stdout(printed):
            questdraft.main([GPLDATA, "--flag", "528", "--flag", "527"])
        self.assertIn("flag 528:\n  GPL 139 at 11: tested", printed.getvalue())
        self.assertIn("  GPL 140 at 2263: set to 1", printed.getvalue())
        printed = io.StringIO()
        with redirect_stdout(printed):
            questdraft.main([GPLDATA, "--script", "139"])
        self.assertEqual(printed.getvalue().count("=== "), 1)


class NoGameTextTests(unittest.TestCase):
    """The table is in the project's own words: with the game's scripts at hand, none of its
    lines is one of theirs."""

    @unittest.skipUnless(GPLDATA and os.path.isfile(GPLDATA), "needs the game's GPLDATA.GFF (DSUN_GPLDATA)")
    def test_no_line_is_the_games(self):
        with open(GPLDATA, "rb") as f:
            scripts, field_types = gpl.load_scripts(f.read())
        theirs = set()
        for data in scripts.values():
            for text in gpl.strings(gpl.decode(data, field_types)):
                said = " ".join(text.split()).casefold()
                if len(said) >= 20:
                    theirs.add(said)
        for q in quests.QUESTS:
            for ours in (q.told, q.ended):
                said = ours.casefold()
                self.assertFalse(any(line in said for line in theirs), f"{q.key}: {ours}")


try:
    import tkinter as tk
    from dsloader import launch, viewer
    from dsloader.layout import Layout
except ImportError:  # no tkinter in this Python
    viewer = None

LAYOUT = os.path.join(HERE, "layouts", "shattered_lands.json")


class Numbers:
    def __init__(self):
        self.value = 0

    def read(self):
        return self.value

    def write(self, head):
        self.value = head
        return True


@unittest.skipIf(viewer is None, "needs tkinter")
class TabTests(unittest.TestCase):
    """The quests on the Journal tab of a real Loader window (needs a display, else skipped)."""

    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("needs a display")
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        saved = launch.SETTINGS, launch.find_game_dir, journal.JOURNAL
        self.addCleanup(lambda: (setattr(launch, "SETTINGS", saved[0]), setattr(launch, "find_game_dir", saved[1]),
                                 setattr(journal, "JOURNAL", saved[2])))
        launch.SETTINGS = os.path.join(self.dir.name, "settings.json")
        launch.find_game_dir = lambda: None
        journal.JOURNAL = os.path.join(self.dir.name, "Journal", "journal.jsonl")

        def no_game():
            raise OSError("no game in a test")
        self.viewer = viewer.Viewer(self.root, Layout.load(LAYOUT), no_game)
        self.numbers = Numbers()

    def look(self, clock=0):
        for _ in range(journal.STEADY):
            self.viewer.journal.sync(self.numbers.read, self.numbers.write, clock)

    def shown(self):
        self.viewer._journal_tick()
        return self.viewer.journal_text.get("1.0", "end-1c")

    def game(self, reading):
        """A game attached, its flags read as READING."""
        self.viewer.dice = SimpleNamespace(attached=True, quest_state=reading, journal=None,
                                           speaker=lambda portrait: f"Portrait {portrait}",
                                           detach=lambda: None, close=lambda: None)

    def test_the_show_box_offers_them(self):
        v = self.viewer
        self.assertEqual(v.journal_kind.get(), "Everything")
        v.journal_kind.set(viewer.JOURNAL_QUESTS)
        self.assertEqual(self.shown(), viewer.QUESTS_UNREAD + "\n\n")
        self.assertEqual(v.journal_count.get(), "No quests yet")

    def test_open_and_finished_from_the_game(self):
        v = self.viewer
        self.look()
        v.journal.add(journal.TALK, "Follow me.", 100, 0x29, 5, "Kurzak")
        self.game(state(527, 26))
        v.journal_kind.set(viewer.JOURNAL_QUESTS)
        gilal, prisoner = quests.BY_KEY["gilal"], quests.BY_KEY["bound-prisoner"]
        self.assertEqual(self.shown(), f"Open (1)\n\nGilal's pain - The slave pens\n{gilal.told}\n\n"
                                       f"Finished (1)\n\nWater for the bound prisoner - The arena\n{prisoner.ended}\n\n")
        self.assertEqual(v.journal_count.get(), "1 open, 1 finished")
        self.assertNotIn(gilal.ended, self.shown())
        v.dice.quest_state = state(528, 26)  # (Dinos has been: the tab follows the game)
        text = self.shown()
        self.assertTrue(text.startswith("Finished (2)\n\n"), text)
        self.assertIn(gilal.ended, text)
        self.assertEqual(v.journal_count.get(), "0 open, 2 finished")
        v.journal_wanted.set("gilal")
        self.assertEqual(v.journal_count.get(), "0 open, 1 finished")
        v.journal_wanted.set("")
        v.journal_kind.set("Everything")  # (and back to the entries)
        self.assertEqual(self.shown(), "Day 1 - The slave pens\n\nKurzak\nFollow me.\n\n")
        self.assertEqual(v.journal_count.get(), "1 entry")

    def test_a_reward_in_the_journal_and_a_load(self):
        v, j, n = self.viewer, self.viewer.journal, self.numbers
        self.game(state())
        self.look()
        j.add(journal.TALK, "Hello.", 100, 8, 5, "Kalinin")
        self.look(100)
        saved = n.value
        j.add(journal.REWARD, EACH.format(3000), 160, 8)
        self.look(160)
        v.journal_kind.set(viewer.JOURNAL_QUESTS)
        captives = quests.BY_KEY["captives"]
        self.assertEqual(self.shown(), f"Finished (1)\n\nThe caravan's captives - The wagon train\n{captives.ended}\n\n")
        n.value = saved  # (the save from before the reward, loaded)
        self.look(100)
        self.assertEqual(self.shown(), "")
        self.assertEqual(v.journal_count.get(), "No quests yet")

    def test_without_the_game_the_last_reading(self):
        v, j = self.viewer, self.viewer.journal
        self.game(state(527))
        self.look()
        j.add(journal.TALK, "It hurts to think.", 100, 0x29, 7, "Gilal")
        v.journal_kind.set(viewer.JOURNAL_QUESTS)
        self.assertIn("Open (1)", self.shown())
        self.assertEqual(quests.load_snapshot(quests.snapshot_path(j.path)), (1, state(527)))
        v.dice.quest_state = state(527, 26)  # (not written again at once)
        self.shown()
        self.assertEqual(quests.load_snapshot(quests.snapshot_path(j.path))[1], state(527))
        v._quests_keep(now=True)
        self.assertEqual(quests.load_snapshot(quests.snapshot_path(j.path))[1], state(527, 26))
        v.dice = None  # (the game gone: the last reading, said to be one)
        text = self.shown()
        self.assertTrue(text.startswith(viewer.QUESTS_AS_READ + "\n\nOpen (1)\n\nGilal's pain"), text)
        self.assertEqual(v.journal_count.get(), "1 open, 1 finished")
        quests.save_snapshot(quests.snapshot_path(j.path), 99, state(527))  # (a reading from another game's journal)
        self.assertEqual(self.shown(), viewer.QUESTS_UNREAD + "\n\n")

    def test_a_game_attached_but_not_read_yet(self):
        self.game(None)
        self.viewer.journal_kind.set(viewer.JOURNAL_QUESTS)
        self.assertEqual(self.shown(), viewer.QUESTS_UNREAD + "\n\n")
        self.assertFalse(os.path.exists(quests.snapshot_path(self.viewer.journal.path)))


if __name__ == "__main__":
    unittest.main()
