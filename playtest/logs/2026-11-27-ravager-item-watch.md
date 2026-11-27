# Wake of the Ravager's dice log: the missing-item report, 2026-11-27

**Under test**: the sequel's dice log running Shattered Lands' item watch (`itemwatch.ItemWatch`, PASS's
`itemwatch` step) with the sequel's ordinary losses (`ravlog.RAV_USED_UP`, `RAV_SPELL_MADE`, `RAV_BROKEN`).
Branch `claude/sequel-item-watch`.

**Set-up**: Xvfb `:55`, the DOSBox lock held by this session. `ravload.sh ravager-roost`, then
`RAV_NO_SAVES=1 python3 ravdice.py 800 /tmp/playtest/iw-dice.txt`. The edits by
[files/2026-11-27-ravager-item-watch-edit.py](files/2026-11-27-ravager-item-watch-edit.py), test edits:
nothing was saved.

**Steps and what was seen**

1. `ravitems.py 0 1 2 3`: the party's items 0 to 14, none of an ordinary-loss type (a Longsword +1, type
   97, in Terrannus's slot 10 as item 8; Ar'Anda's Obsidian Dagger, type 72, item 1).
2. **An ordinary loss**: item 8's type made 6 (an arrow), then 5 s later its +0 word zeroed (the record
   freed, as the game frees the last arrow). The dice log said nothing: the type change is the item made
   another in place (`changed_in_place`), the freeing an arrow used up.
3. **A loss to report**: item 1's +0 word zeroed. Two seconds on: `Obsidian Dagger is gone from Ar'Anda's
   left hand: the game freed its record: destroyed (Detonate's blast, acid), or taken or dropped on the
   ground by a script (...). An item report is saved in .../crash-logs/item-2026-11-27-202006.txt.` The
   report had the item's record before and after, its type's record, the game time (2574 s), region 50,
   "In a fight: no", Ar'Anda's and the party's items, and the dice log's last lines.

**Not seen in play**: an item dropped, sold or handed over through the screens (the watch's own code, the
same as Shattered Lands', and its tests), and an area change renumbering the items (BULK_MATCH).

**Result**: the item report works in the sequel, and the sequel's arrow type passes in silence. The DOSBox
and the dice log of this test were closed by pid.
