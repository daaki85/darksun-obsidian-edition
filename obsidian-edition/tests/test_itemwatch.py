"""Items that go missing (itemwatch.py): an item gone from the whole party for GONE_WAIT is
reported, with the record's fate told apart; one moved between members or back within the
wait is not."""

import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, itemwatch
from dsloader.game import ItemSeen


def item(index, member, label, slot="chest", typ=7, plus=0):
    rec = bytearray(game.ITEM_SIZE)
    struct.pack_into("<H", rec, game.ITEM_TYPE, typ)
    struct.pack_into("<H", rec, game.ITEM_NAME, 100 + typ)
    rec[game.ITEM_SLOT] = game.EQUIP_SLOTS.index(slot) if slot else 255
    struct.pack_into("b", rec, game.ITEM_PLUS, plus)
    return ItemSeen(index, member, ("Garyn", "Nira", "Dinos", "Kalzith")[member], slot, label, typ,
                    bytes(rec), bytes(game.ITEM_TYPE_SIZE))


class FakeGame:
    """Just what the watch asks of GameData."""

    def __init__(self, items):
        self.items = list(items)
        self.records = {}          # item number -> the record there now (default: as last seen)

    def party_items(self):
        return list(self.items)

    def item_record(self, index):
        if index in self.records:
            return self.records[index]
        for i in self.items:
            if i.index == index:
                return i.record
        return bytes(game.ITEM_SIZE)

    def game_time(self):
        return 600

    def region(self):
        return 0x29

    def in_combat(self):
        return False

    def whose_turn(self):
        return None

    def combatant_name(self, c):
        return "?"


class ItemWatchTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.watch = itemwatch.ItemWatch(folder=self.folder)
        self.armour = item(12, 0, "Inix Hide Chest Armor")
        self.sword = item(13, 0, "Bone Long Sword", slot="right hand", typ=9)
        self.data = FakeGame([self.armour, self.sword])

    def run_for(self, seconds, step=1.0, start=0.0):
        out = []
        t = start
        while t <= start + seconds:
            out += self.watch.check(self.data, t)
            t += step
        return out, t

    def test_an_item_gone_is_reported_once(self):
        self.run_for(2)
        self.data.items = [self.sword]            # the armour vanishes, its record freed
        self.data.records[12] = bytes(game.ITEM_SIZE)
        out, t = self.run_for(5, start=3)
        self.assertEqual(len(out), 1, out)
        self.assertIn("Inix Hide Chest Armor is gone from Garyn's chest", out[0])
        self.assertIn("freed", out[0])
        self.assertEqual(len(self.watch.reports), 1)
        with open(self.watch.reports[0], encoding="utf-8") as f:
            text = f.read()
        self.assertIn("item 12, type 7", text)
        self.assertIn("Region: 41 (RGN29.GFF)", text)
        self.assertIn("Garyn: Bone Long Sword (item 13, right hand)", text)
        self.assertTrue(os.path.basename(self.watch.reports[0]).startswith("item-"))
        out, _ = self.run_for(5, start=t)         # and not again
        self.assertEqual(out, [])

    def test_an_item_still_outside_the_party(self):
        self.run_for(2)
        self.data.items = [self.sword]            # dropped: the record is as it was
        self.data.records[12] = self.armour.record
        out, _ = self.run_for(5, start=3)
        self.assertEqual(len(out), 1)
        self.assertIn("left Garyn's chest: it is outside the party", out[0])
        self.assertEqual(self.watch.reports, [])  # (nothing wrong: no report)

    def test_ordinary_losses_get_no_report(self):
        """Used up (fruit, arrows, scrolls), a spell's weapon, sold (money up), broken: a line only."""
        apple = item(20, 1, "Apple", slot=None, typ=60)
        hammer = item(21, 2, "Spiritual Hammer", slot="right hand", typ=30)
        spear = item(22, 3, "Polearm", slot="right hand", typ=19)
        self.data.items += [apple, hammer, spear]
        self.data.money = lambda: self.money
        self.money = 100
        self.run_for(2)
        broken = item(23, 3, "Broken Weapon", slot=None, typ=93)
        self.data.items = [self.armour, self.sword, broken]
        for i in (20, 21, 22):
            self.data.records[i] = bytes(game.ITEM_SIZE)
        out, t = self.run_for(5, start=3)
        self.assertEqual(sorted(out), ["Apple left Nira's pack: used up, or taken for a quest.",
                                       "Polearm left Kalzith's right hand: it broke (a Broken Weapon in its place).",
                                       "Spiritual Hammer left Dinos's right hand: a spell made it, and the spell is over."])
        self.data.items = [self.armour, broken]
        self.data.records[13] = bytes(game.ITEM_SIZE)
        self.money = 160                           # (sold: the money went up as it went)
        out, _ = self.run_for(5, start=t)
        self.assertEqual(out, ["Bone Long Sword left Garyn's right hand: sold (the party's money went up)."])
        self.assertEqual(self.watch.reports, [])

    def test_a_game_loaded(self):
        """The game's clock gone back: a game loaded, whatever is missing is not news."""
        clock = [600]
        self.data.game_time = lambda: clock[0]
        self.run_for(2)
        clock[0] = 300
        self.data.items = []
        out, _ = self.run_for(5, start=3)
        self.assertEqual(out, [])

    def test_an_item_handed_over_or_back_soon_is_not_news(self):
        self.run_for(2)
        self.data.items = [self.sword]            # away for one look only
        self.watch.check(self.data, 3.0)
        self.data.items = [self.sword, self.armour]
        out, t = self.run_for(5, start=4)
        self.assertEqual(out, [])
        self.data.items = [self.sword, self.armour._replace(member=1, owner="Nira", slot=None)]
        out, _ = self.run_for(5, start=t)        # Nira carries it now
        self.assertEqual(out, [])

    def test_context_is_kept(self):
        self.watch.remember(["Garyn attacks: 17 vs AC 5, hit"])
        self.run_for(2)
        self.data.items = []
        out, _ = self.run_for(5, start=3)
        self.assertEqual(len(out), 2)              # both items gone
        with open(self.watch.reports[0], encoding="utf-8") as f:
            text = f.read()
        self.assertIn("Garyn attacks: 17 vs AC 5, hit", text)

    def test_reset_forgets(self):
        self.run_for(2)
        self.watch.reset()                        # a game was loaded
        self.data.items = []
        out, _ = self.run_for(5, start=3)
        self.assertEqual(out, [])                 # nothing was seen since the reset


if __name__ == "__main__":
    unittest.main()
