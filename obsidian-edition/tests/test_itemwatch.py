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


def item(index, member, label, slot="chest", typ=7, plus=0, value=0):
    rec = bytearray(game.ITEM_SIZE)
    struct.pack_into("<H", rec, game.ITEM_TYPE, typ)
    struct.pack_into("<H", rec, game.ITEM_NAME, 100 + typ)
    rec[game.ITEM_SLOT] = game.EQUIP_SLOTS.index(slot) if slot else 255
    struct.pack_into("b", rec, game.ITEM_PLUS, plus)
    struct.pack_into("<H", rec, itemwatch.ITEM_VALUE, value)
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

    def party_position(self):
        return (1896, 856)

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
        self.sword = item(13, 0, "Bone Long Sword", slot="right hand", typ=9, value=100)
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
        self.assertEqual(out, [])                 # (nothing wrong: not a word, no report)
        self.assertEqual(self.watch.reports, [])
        self.assertIn("outside the party", itemwatch.ordinary_loss(self.armour, self.armour.record, False, False))

    def test_freed_but_unchanged_is_reported(self):
        """The game frees a destroyed item by zeroing only its +0 word: the type and name left in
        the record are not an item outside the party (a bone helm lost to Detonate was missed)."""
        helm = bytearray(item(14, 0, "Bone Helm", slot="head", typ=5).record)
        struct.pack_into("<H", helm, itemwatch.ITEM_ID, 0xFC03)
        was = ItemSeen(14, 0, "Garyn", "head", "Bone Helm", 5, bytes(helm), bytes(game.ITEM_TYPE_SIZE))
        self.data.items.append(was)
        self.run_for(2)
        self.data.items = [self.armour, self.sword]
        after = bytearray(helm)
        struct.pack_into("<H", after, itemwatch.ITEM_ID, 0)
        self.data.records[14] = bytes(after)
        out, _ = self.run_for(5, start=3)
        self.assertEqual(len(out), 1, out)
        self.assertIn("Bone Helm is gone from Garyn's head", out[0])
        self.assertIn("freed its record", out[0])
        self.assertIsNone(itemwatch.ordinary_loss(was, bytes(after), False, False))
        self.assertIn("outside the party", itemwatch.ordinary_loss(was, bytes(helm), False, False))
        # a quest item a script takes, or a wand's last charge, frees the record the same way
        for typ in (61, 71, 104):
            gone = ItemSeen(14, 0, "Garyn", "pack", "Quest", typ, bytes(helm), bytes(game.ITEM_TYPE_SIZE))
            self.assertIn("used up", itemwatch.ordinary_loss(gone, bytes(after), False, False))

    def test_ordinary_losses_get_no_report(self):
        """Used up (fruit, arrows, scrolls), a spell's weapon, sold (money up), broken: nothing said."""
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
        self.assertEqual(out, [])
        empty = bytes(game.ITEM_SIZE)
        self.assertIn("used up", itemwatch.ordinary_loss(apple, empty, False, False))
        self.assertIn("spell", itemwatch.ordinary_loss(hammer, empty, False, False))
        self.assertIn("broke", itemwatch.ordinary_loss(spear, empty, False, True))
        self.assertIsNone(itemwatch.ordinary_loss(spear, empty, False, False))
        self.data.items = [self.armour, broken]
        self.data.records[13] = bytes(game.ITEM_SIZE)
        self.money = 160                           # (sold: the money went up as it went, 60% of its 100)
        out, _ = self.run_for(5, start=t)
        self.assertEqual(out, [])
        self.assertIn("sold", itemwatch.ordinary_loss(self.sword, empty, True, False))
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

    def test_handed_over_under_a_new_number(self):
        """The game may move an item to another member as a new record, the old one freed: the
        same item turning up within the wait is a hand-over, not news."""
        self.run_for(2)
        self.data.items = [self.sword, self.armour._replace(index=40, member=1, owner="Nira", slot=None)]
        self.data.records[12] = bytes(game.ITEM_SIZE)
        out, _ = self.run_for(5, start=3)
        self.assertEqual((out, self.watch.reports), ([], []))

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


class LoadTest(ItemWatchTest):
    """A game loaded with the same party: no reports for what the save doesn't have."""

    def test_clock_on_too_far_elsewhere(self):
        """A later save with the party somewhere else in the same region: a game loaded."""
        self.run_for(2)
        self.data.game_time = lambda: 600 + itemwatch.CLOCK_JUMP + 1
        self.data.party_position = lambda: (100, 200)
        self.data.items = [self.sword]
        out, _ = self.run_for(5, start=3)
        self.assertEqual(out, [])
        self.assertEqual(self.watch.reports, [])

    def test_rest_goes_on_watching(self):
        """A rest: the clock on hours, the party where it was. An item gone as it rests is news."""
        self.run_for(2)
        self.data.game_time = lambda: 600 + 8 * 3600
        self.data.items = [self.sword]
        out, _ = self.run_for(5, start=3)
        self.assertTrue(any("Inix Hide" in line for line in out))
        self.assertEqual(len(self.watch.reports), 1)

    def test_rest_then_a_load(self):
        """After a rest the watch still starts afresh on a load (the clock gone back)."""
        clock = [600]
        self.data.game_time = lambda: clock[0]
        self.run_for(2)
        clock[0] = 600 + 8 * 3600         # (a rest: nothing gone)
        self.run_for(2, start=3)
        clock[0] = 300                    # (an earlier save)
        self.data.items = []
        out, _ = self.run_for(5, start=6)
        self.assertEqual(out, [])

    def test_most_items_gone_at_once(self):
        extra = [item(20 + n, 1, f"Thing {n}", slot=None, typ=40 + n) for n in range(3)]
        self.data.items = [self.armour, self.sword] + extra
        self.run_for(2)
        self.data.items = [self.sword]             # (four of five gone at one look)
        out, _ = self.run_for(5, start=3)
        self.assertEqual(out, [])
        self.assertEqual(self.watch.reports, [])

    def test_one_gone_still_reported(self):
        extra = [item(20 + n, 1, f"Thing {n}", slot=None, typ=40 + n) for n in range(3)]
        self.data.items = [self.armour, self.sword] + extra
        self.run_for(2)
        self.data.items = [self.sword] + extra
        out, _ = self.run_for(5, start=3)
        self.assertTrue(any("Inix Hide" in line for line in out))


class MoneyTest(ItemWatchTest):
    def test_other_money_hides_nothing(self):
        """Money that isn't the item's sale (a purse picked, a quest's reward) is no sale."""
        self.data.money = lambda: self.money
        self.money = 100
        self.run_for(2)
        self.data.items = [self.armour]
        self.data.records[13] = bytes(game.ITEM_SIZE)
        self.money = 107                           # (7 ceramic pieces from a purse)
        out, _ = self.run_for(5, start=3)
        self.assertTrue(any("Bone Long Sword" in line for line in out))

    def test_full_price_sale(self):
        """Without the CHA rule a shop pays the whole price."""
        self.assertEqual(itemwatch.sale_prices(self.sword.record), {100, 60})


class AreaChangeTest(ItemWatchTest):
    """An area change gives every item a new number: the items are matched through it, and one
    with no match is news; a game loaded (another set of items) is not."""

    def party(self, base, drop=()):
        names = [("Inix Hide Chest Armor", "chest", 7), ("Bone Long Sword", "right hand", 9),
                 ("Ring", "finger", 12), ("Boots", "foot", 13), ("Cloak", "cloak", 14)]
        return [item(base + n, n % 2, label, slot=slot, typ=typ)
                for n, (label, slot, typ) in enumerate(names) if label not in drop]

    def test_renumbered_nothing_lost(self):
        self.data.items = self.party(10)
        self.run_for(2)
        self.data.items = self.party(200)
        out, _ = self.run_for(5, start=3)
        self.assertEqual(out, [])
        self.assertEqual(self.watch.reports, [])

    def test_renumbered_one_lost(self):
        self.data.items = self.party(10)
        self.run_for(2)
        self.data.items = []                         # (the party's lists empty while the area loads)
        self.run_for(1, start=3)
        self.data.items = self.party(200, drop=("Ring",))
        out, _ = self.run_for(5, start=5)
        self.assertEqual(len(out), 1)
        self.assertIn("Ring", out[0])
        self.assertIn("change of area", out[0])
        self.assertEqual(len(self.watch.reports), 1)
        with open(self.watch.reports[0], encoding="utf-8") as f:
            text = f.read()
        self.assertIn("before the change of area", text)
        self.assertNotIn("(unreadable)", text)

    def test_watching_goes_on_after(self):
        """After an area change the new numbers are watched as before."""
        self.data.items = self.party(10)
        self.run_for(2)
        self.data.items = self.party(200)
        self.run_for(4, start=3)
        self.data.items = self.party(200, drop=("Boots",))
        out, _ = self.run_for(5, start=8)
        self.assertTrue(any("Boots" in line for line in out))

    def test_another_game_loaded(self):
        self.data.items = self.party(10)
        self.run_for(2)
        self.data.items = [item(300 + n, 2, f"Thing {n}", slot=None, typ=40 + n) for n in range(5)]
        out, _ = self.run_for(5, start=3)
        self.assertEqual(out, [])

    def test_number_reused_by_another_item(self):
        """The item's number now names another item of the party's: the item is gone all the same."""
        self.run_for(2)
        self.data.items = [self.sword, item(12, 1, "Bone Dagger", slot=None, typ=30)]
        out, _ = self.run_for(5, start=3)
        self.assertTrue(any("Inix Hide" in line for line in out))
