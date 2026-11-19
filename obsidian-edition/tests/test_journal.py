"""The journal (journal.py): entries kept in a file, a game's own chain followed through the id in
the game's numbers (a save loaded, a new game, the Loader started again), the entries added
before an id could be written kept with the save that held them, and what the tab shows."""

import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import gpl, journal
from dsloader.journal import CHOSEN, MESSAGE, REWARD, TALK, Journal

GPLDATA = os.environ.get("DSUN_GPLDATA")


class Numbers:
    """The game's two numbers: None while they have no place in memory."""

    def __init__(self, value=0):
        self.value, self.there = value, True

    def read(self):
        return self.value if self.there else None

    def write(self, head):
        if self.there:
            self.value = head
        return self.there


def look(j, numbers, clock=0, times=journal.STEADY):
    for _ in range(times):
        j.sync(numbers.read, numbers.write, clock)


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.path = os.path.join(self.dir.name, "Journal", "journal.jsonl")

    def texts(self, j):
        return [e.text for e in j.shown()]

    def test_entries_kept_and_read_again(self):
        j, n = Journal(self.path), Numbers()
        look(j, n)
        j.add(TALK, "Welcome to the pens.", 100, 0x29, 5, "Kurzak", ["Yes", "No"], "Answer Yes or No")
        j.add(CHOSEN, "Yes", 100, 0x29)
        j.add(REWARD, "Cilla receives 200 experience points!", 160, 0x29)
        look(j, n, 160, 1)
        self.assertEqual(n.value, 3)
        again = Journal(self.path)
        self.assertEqual(self.texts(again), ["Welcome to the pens.", "Yes", "Cilla receives 200 experience points!"])
        first = again.shown()[0]
        self.assertEqual((first.portrait, first.speaker, first.replies, first.title, first.region, first.clock),
                         (5, "Kurzak", ["Yes", "No"], "Answer Yes or No", 0x29, 100))

    def test_a_save_loaded_shows_its_own_journal(self):
        j, n = Journal(self.path), Numbers()
        look(j, n)
        j.add(TALK, "one", 10)
        j.add(TALK, "two", 20)
        look(j, n, 20, 1)
        saved = n.value  # (a save made here holds this id)
        j.add(TALK, "three", 30)
        look(j, n, 30, 1)
        changed = j.changed
        n.value = saved  # (the save loaded)
        look(j, n, 20)
        self.assertEqual(self.texts(j), ["one", "two"])
        self.assertEqual(j.changed, changed + 1)
        j.add(TALK, "another way", 25)
        look(j, n, 25, 1)
        self.assertEqual(self.texts(j), ["one", "two", "another way"])
        self.assertGreater(n.value, 3)  # (a new id: never one a save may hold)
        n.value = 3  # (and the later save loaded: its own branch again)
        look(j, n, 30)
        self.assertEqual(self.texts(j), ["one", "two", "three"])

    def test_one_odd_read_is_not_a_load(self):
        """A game being loaded may show another id for a look: only one read twice running counts."""
        j, n = Journal(self.path), Numbers()
        look(j, n)
        j.add(TALK, "one", 10)
        look(j, n, 10, 1)
        n.value = 0
        look(j, n, 10, 1)
        self.assertEqual(self.texts(j), ["one"])
        n.value = 1
        look(j, n, 10)
        self.assertEqual((self.texts(j), j.changed), (["one"], 0))

    def test_a_new_game_begins_empty_and_the_old_one_comes_back(self):
        j, n = Journal(self.path), Numbers()
        look(j, n)
        j.add(TALK, "the first game", 500)
        look(j, n, 500, 1)
        n.value = 0  # (START GAME)
        look(j, n, 0)
        self.assertEqual(self.texts(j), [])
        j.add(TALK, "the second game", 5)
        look(j, n, 5, 1)
        self.assertEqual(self.texts(j), ["the second game"])
        n.value = 1
        look(j, n, 500)
        self.assertEqual(self.texts(j), ["the first game"])

    def test_entries_added_while_the_numbers_were_away_stay_with_the_save(self):
        """An entry added while the id couldn't be written is in a save made then all the same:
        loading that save (the old id, a clock past the entry's) keeps it; a later one is dropped."""
        j, n = Journal(self.path), Numbers()
        look(j, n)
        j.add(TALK, "written", 10)
        look(j, n, 10, 1)
        n.there = False
        j.add(TALK, "before the save", 20)
        look(j, n, 20, 1)
        n.there = True  # (the save was made at clock 25 with the old id; then, played on)
        j.add(TALK, "after the save", 30)
        look(j, n, 30, 1)
        n.value = 1
        look(j, n, 25)
        self.assertEqual(self.texts(j), ["written", "before the save"])
        self.assertEqual(n.value, 2)  # (and its id written now)

    def test_said_before_the_game_is_known_joins_it(self):
        j, n = Journal(self.path), Numbers()
        look(j, n)
        j.add(TALK, "earlier", 10)
        look(j, n, 10, 1)
        again, n.there = Journal(self.path), False
        again.add(TALK, "at once", 11)
        look(again, n, 11)
        self.assertEqual(self.texts(again), ["earlier"])  # (shown: the chain last added to)
        n.there = True
        look(again, n, 11)
        self.assertEqual(self.texts(again), ["earlier", "at once"])
        self.assertEqual(n.value, 2)

    def test_the_game_started_again_is_not_a_load(self):
        j, n = Journal(self.path), Numbers()
        look(j, n)
        j.add(TALK, "one", 10)
        look(j, n, 10, 1)
        j.reset()
        n.value = 0  # (the game at its title: nothing loaded yet)
        look(j, n, 0)
        self.assertEqual(self.texts(j), [])
        n.value = 1
        look(j, n, 10)
        self.assertEqual(self.texts(j), ["one"])

    def test_a_save_from_a_lost_journal(self):
        """The file gone, a save's id names no entry: an empty journal, and new ids past it."""
        j, n = Journal(self.path), Numbers(40)
        look(j, n)
        self.assertEqual(self.texts(j), [])
        entry = j.add(TALK, "new", 10)
        self.assertEqual((entry.id, entry.parent), (41, 40))

    def test_a_refused_file_is_tried_again(self):
        j, n = Journal(os.path.join(self.dir.name, "nowhere", "journal.jsonl")), Numbers()
        os.mkdir(os.path.join(self.dir.name, "blocked"))
        j.path = os.path.join(self.dir.name, "blocked")  # (a folder: can't be opened as a file)
        look(j, n)
        j.add(TALK, "kept", 10)
        look(j, n, 10, 1)
        self.assertTrue(j.failed)
        j.path = self.path
        look(j, n, 10, 1)
        self.assertFalse(j.failed)
        self.assertEqual(self.texts(Journal(self.path)), ["kept"])

    def test_broken_lines_are_passed_over(self):
        os.makedirs(os.path.dirname(self.path))
        with open(self.path, "w", encoding="utf-8") as f:
            f.write('{"id":1,"parent":0,"kind":"talk","text":"good"}\nnot json\n{"id":2,"parent":5,"kind":"talk"}\n'
                    '{"id":3,"parent":1,"kind":"other"}\n{"id":4,"parent":1,"kind":"message","text":"also good"}\n{"id":')
        self.assertEqual(self.texts(Journal(self.path)), ["good", "also good"])

    def test_close_keeps_what_never_had_a_game(self):
        j = Journal(self.path)
        j.add(MESSAGE, "said with no game known", 5)
        j.close()
        self.assertEqual(self.texts(Journal(self.path)), ["said with no game known"])


class ShowTests(unittest.TestCase):
    def entries(self):
        E = journal.Entry
        return [E(1, 0, TALK, 100, 0x29, 5, "Kurzak", "Follow me.", ["Yes", "No"], "Answer Yes or No"),
                E(2, 1, CHOSEN, 100, 0x29, text="Yes"),
                E(3, 2, MESSAGE, 90000, 0x29, text="The door is locked."),
                E(4, 3, REWARD, 90060, 0x2A, text="Cilla receives 200 experience points!"),
                E(5, 4, TALK, 90100, 0x1F, 0, "", "The wind howls.")]

    def test_text(self):
        self.assertEqual(journal.text_of(self.entries()), "\n".join([
            "Day 1 - The slave pens", "", "Kurzak", "Follow me.", "  (Answer Yes or No)", "  1. Yes", "  2. No",
            "  You chose: Yes", "", "Day 2 - The slave pens", "", "The door is locked.", "",
            "Day 2 - The arena", "", "Cilla receives 200 experience points!", "",
            "Day 2 - Area 1Fh", "", "Narration", "The wind howls."]) + "\n")

    def test_rows_go_on_from_a_place(self):
        entries = self.entries()
        rows = journal.rows(entries[1:3], where=journal.place(entries[0]))
        self.assertEqual([kind for kind, _ in rows], ["chosen", "gap", "day", "gap", "message", "gap"])

    def test_kinds_and_words(self):
        entries = self.entries()
        ids = lambda got: [e.id for e in got]
        self.assertEqual(ids(journal.chosen(entries)), [1, 2, 3, 4, 5])
        self.assertEqual(ids(journal.chosen(entries, (TALK,))), [1, 2, 5])  # (the answer with its talk)
        self.assertEqual(ids(journal.chosen(entries, (REWARD,))), [4])
        self.assertEqual(ids(journal.chosen(entries, None, "kurzak")), [1, 2])
        self.assertEqual(ids(journal.chosen(entries, None, "CILLA")), [4])
        self.assertEqual(ids(journal.chosen(entries, None, "yes")), [1, 2])
        self.assertEqual(ids(journal.chosen(entries, (MESSAGE,), "kurzak")), [])

    def test_message_kinds(self):
        self.assertEqual(journal.kind_of_message("Cilla receives 200 experience points!"), REWARD)
        self.assertEqual(journal.kind_of_message("Each party member receives 1 experience point!"), REWARD)
        for own in ("Congratulations! The party gains 12,000 experience!", "For destroying it, you earn 6,000 EXP!",
                    "Congratulations! The Party earns 2000 Exp!", "Each party member receives 5,000 experience points."):
            self.assertEqual(journal.kind_of_message(own), REWARD, own)  # (the awards some scripts word themselves)
        self.assertEqual(journal.kind_of_message("The door is locked."), MESSAGE)
        self.assertEqual(journal.kind_of_message("Dinos earns his keep. He has 20 years of experience."), MESSAGE)
        for notice in ("GAME SAVED", "SAVING GAME", "CAN'T SAVE DURING COMBAT", "  "):
            self.assertIsNone(journal.kind_of_message(notice))

    def test_times(self):
        self.assertEqual(journal.time_of(86400 * 46 + 14 * 3600 + 20 * 60), "Day 47, 14:20")
        self.assertEqual(journal.time_of(None), "")


class HeadTests(unittest.TestCase):
    """The id in the game's memory: two words at the numbers' far pointer."""

    class Guest:
        def __init__(self):
            self.mem = bytearray(0x20000)

        def read(self, addr, size):
            return bytes(self.mem[addr:addr + size])

        def write(self, addr, data):
            self.mem[addr:addr + len(data)] = data

    class Game:
        ds = 0x1000

    def test_read_and_write(self):
        gd = self.Game()
        gd.guest = self.Guest()
        self.assertIsNone(journal.read_head(gd))
        self.assertFalse(journal.write_head(gd, 7))
        struct.pack_into("<HH", gd.guest.mem, gd.ds * 16 + journal.game.NUMBERS_PTR, 0x0040, 0x1800)
        numbers = 0x1800 * 16 + 0x40
        self.assertEqual(journal.read_head(gd), 0)
        self.assertTrue(journal.write_head(gd, 0x00012345))
        self.assertEqual(gd.guest.mem[numbers + 198 * 2:numbers + 200 * 2], struct.pack("<HH", 0x2345, 1))
        self.assertEqual(journal.read_head(gd), 0x12345)
        self.assertEqual(sum(gd.guest.mem[numbers:numbers + 198 * 2]), 0)  # (no other number touched)

    def test_the_numbers_are_the_saves_last_two(self):
        self.assertEqual(journal.NUMBERS, (journal.NUMBER_COUNT - 2, journal.NUMBER_COUNT - 1))


@unittest.skipUnless(GPLDATA and os.path.isfile(GPLDATA), "needs the game's GPLDATA.GFF (DSUN_GPLDATA)")
class ScriptNumbersTests(unittest.TestCase):
    def test_no_script_uses_the_journals_numbers(self):
        """The game's scripts read and set global numbers (variable 87h, destination 7) well below
        the journal's two."""
        from dsloader.gff import read_gff
        with open(GPLDATA, "rb") as f:
            chunks = read_gff(f.read())
        field_types = next((v for k, v in chunks.items() if k[0] == "GPLX"), b"")[gpl.FIELD_TYPES_AT:]
        used = set()

        def walk(arg):
            if isinstance(arg, tuple):
                if len(arg) == 3 and arg[0] == "var" and arg[1] in (7, 0x87) and isinstance(arg[2], int):
                    used.add(arg[2])
                for part in arg:
                    walk(part)
            elif isinstance(arg, list):
                for part in arg:
                    walk(part)

        for (kind, _number), data in chunks.items():
            if kind in ("GPL ", "MAS "):
                for op in gpl.decode(data, field_types):
                    walk(list(op.args))
        self.assertTrue(used)
        self.assertLess(max(used), min(journal.NUMBERS), sorted(used)[-5:])


try:
    import tkinter as tk
    from dsloader import launch, viewer
    from dsloader.layout import Layout
except ImportError:  # no tkinter in this Python
    viewer = None

LAYOUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "layouts", "shattered_lands.json")


@unittest.skipIf(viewer is None, "needs tkinter")
class TabTests(unittest.TestCase):
    """The Journal tab on a real Loader window (needs a display, else skipped)."""

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

    def shown(self):
        self.viewer._journal_tick()
        return self.viewer.journal_text.get("1.0", "end-1c")

    def test_entries_shown_as_they_come_and_after_a_load(self):
        v, j, n = self.viewer, self.viewer.journal, self.numbers
        self.assertEqual((self.shown(), v.journal_count.get()), ("", "Nothing yet"))
        look(j, n)
        j.add(TALK, "Follow me.", 100, 0x29, 5, "Kurzak", ["Yes", "No"], "Answer Yes or No")
        self.assertEqual(self.shown(), "Day 1 - The slave pens\n\nKurzak\nFollow me.\n  (Answer Yes or No)\n"
                                       "  1. Yes\n  2. No\n\n")
        j.add(CHOSEN, "Yes", 100, 0x29)
        look(j, n, 100, 1)
        saved = n.value
        j.add(REWARD, "Cilla receives 200 experience points!", 160, 0x29)
        text = self.shown()
        self.assertTrue(text.endswith("  2. No\n  You chose: Yes\n\nCilla receives 200 experience points!\n\n"), text)
        self.assertEqual(text.count("Day 1"), 1)
        self.assertEqual(v.journal_count.get(), "2 entries")
        look(j, n, 160, 1)
        n.value = saved  # (the save from before the reward, loaded)
        look(j, n, 100)
        self.assertNotIn("Cilla", self.shown())
        self.assertEqual(v.journal_count.get(), "1 entry")

    def test_show_and_words(self):
        v, j = self.viewer, self.viewer.journal
        look(j, self.numbers)
        j.add(TALK, "Follow me.", 100, 0x29, 5, "Kurzak")
        j.add(REWARD, "Cilla receives 200 experience points!", 160, 0x29)
        v.journal_kind.set("Rewards")
        self.assertEqual(self.shown(), "Day 1 - The slave pens\n\nCilla receives 200 experience points!\n\n")
        self.assertEqual(v.journal_count.get(), "1 of 2")
        v.journal_kind.set("Everything")
        v.journal_wanted.set("kurz")
        self.assertEqual(self.shown(), "Day 1 - The slave pens\n\nKurzak\nFollow me.\n\n")
        j.add(TALK, "Kurzak is waiting.", 200, 0x29, 0, "")
        self.assertIn("Kurzak is waiting.", self.shown())

    def test_switched_off_and_on(self):
        v = self.viewer
        v.keep_journal.set(False)
        v._journal_switched()
        self.assertIs(launch.load_settings()["journal"], False)
        v.keep_journal.set(True)
        v._journal_switched()
        self.assertIs(launch.load_settings()["journal"], True)


if __name__ == "__main__":
    unittest.main()
