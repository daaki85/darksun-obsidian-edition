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

## The ordinary ways through the screens (a second run, the same day)

Asked for before the merge: the losses most likely to give a false report, played through the game's own
screens. Two sessions, each with its own `ravdice.py` (`RAV_NO_SAVES=1`); nothing was saved.

**`ravload.sh ravager-after-ambush`** (Tyr, the street by Uhubito's office), the inventory (USE 22,17, then
75,171). The window is 640x480 for the game's 320x200: a game x is the window's / 2, a game y the window's
/ 2.4 (Ar'Anda's left hand 173,90, her missile slot 65,50, the right hand 65,91; the portraits 30,21 / 30,71;
the backpack's first column 196,27 / 45 / 63 / 81; DROP 206,135).

4. **Handed over**: Ar'Anda's Obsidian Dagger (item 1) picked up, Terrannus's portrait, his backpack: the
   item kept its number, now his (`ravshop.py party`). Silent.
5. **Dropped**: the same dagger from his backpack onto DROP: gone from the party (on the street by the
   door). Silent.
6. **Sold**: walked to Notaku (`ravgo.py x 1176 y 1224 x 296 y 936`; the look pointer on him at game 92,3,
   its talk button 115,66; "What kind of substances do you sell?", "Yes, that was me.", "I'm not interested
   in doing that now.", "Show me your goods."). Ar'Anda's Leather Sling onto SELL (292,164): "I'll give you
   1$", TAKE IT (145,92): sold, the item gone from every list. Then her Metal Longsword +1: "I'll give you
   18000$", taken: the sword kept in Notaku's list (the buyback rule). Both silent. (Bought back by mistake
   for 3,000 from the list's first place, which the screen still drew as a scroll: the shop's list is drawn
   one change behind.)
7. **Bought**: a Spellbook (3,000), a One-use Scroll (300, MORE's page) and a Dye (5,000; type 9, a quest
   thing, nothing to use). Nothing reported as they came.
8. **Not managed: a scroll used up.** The One-use Scroll's box spell icon (288,48 for the third backpack
   cell's box) put the game in its casting pointer; Ar'Anda herself, the ground, the stall's woman and
   Notaku all gave INVALID TARGET or NO TARGET, and a right-click put the walk arrow back with the scroll
   kept. The Spellbook's icon in the shop only closed the box. The used-up types are checked by the test
   and by step 2 above (an arrow's record freed).

**`ravload.sh ravager-roost`**, then `ravjump.py 0x44 33 43` and Reyhan's talk (the look pointer at game
184,148 after walking back to 1711,1337): the region's picture, Space.

9. **Area change**: every one of the party's 15 items under a new number (the Obsidian Dagger 1 became 174, the Metal Longsword +1 2 became 173). Silent.
10. **The watch alive after it**: the dagger's new record (174) freed by a test edit: `Obsidian Dagger is
    gone from Ar'Anda's left hand: the game freed its record ...`, its report saved. So the change of area
    was matched item for item (BULK_MATCH), not taken for a load.

**Not seen in play**: a potion or scroll really used up (step 8).

**Result**: the item report works in the sequel. Handing over, dropping, selling (gone and kept), buying
and a change of area pass in silence, and the sequel's arrow type does too. Every DOSBox and dice log of
these tests was closed by pid.
