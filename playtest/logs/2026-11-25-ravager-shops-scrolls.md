# 2026-11-25: shops as in AD&D and the scroll's messages in Wake of the Ravager

**Under test** (branch `claude/ravager-shops-scrolls`, on `claude/ravager-port-all`): DSCLOG2's sites 54-59.
- **Shops as in AD&D** (SL's RULE_CHA_PRICES / RULE_BUYBACK, now `game.RULE_CHA_PRICES` in `ravager.RULES_PORTED`):
  PRICE_CX (54, the price under an item, 90E2Ah), PRICE_EAX (55, the price charged 90AA7h and the list's
  affordable test 9036Ch), SELL_PRICE (56, what the shop pays, 90F4Dh) and SELL_KEEP (57, where the shop frees
  the item sold, 91043h). Unlike SL's, the merchant's pack is filled by the helper itself in the game's own
  call (no Loader pass, so the read-only dice log view is no obstacle).
- **The game's message box** (560h:2Ah): MSG_WINDOW (59, counted) and MSG_SHOWN (58, at its wait, 59B62h).

The copy `ravSS` of `ravK` (the install with the transferred party's roster), the Loader's way
(`ravload.sh ravager-after-ambush`: the opening party in Tyr; the shop and the scroll need nothing of the
transferred party, and the after-ambush save skips the ambush), the dice log (`ravdice.py`) setting the
rules (rules_hi 0xFF3F; the controls 0xFF2F). All edits were test edits (`ravshop.py`); nothing was saved.
DOSBox's window 640x480 (the sequel's, as in the other Ravager runs: `ravclick.py`'s coordinates).

## The shop (Notaku, Shadow Square)

The route: from the save, Uhubito's caravan office (walking in by a click on its floor starts his talk;
Goodbye), out to the street (x 1176), Up to y 1224, Left along y 1224 to x 296 (the open ground south of
the square), Up to y 936: Notaku's stall (his map object 33 at world 312, 904). The look pointer (two
right-clicks from the arrow) on him opens the Look box; its first button talks. "What kind of
substances do you sell?", "Yes, that was me", "I'm not interested in doing that now", **"Show me your
goods."** opens his shop (the merchant thing DS:1A30h = 33, a creature of kind 2: Notaku, creature 19).

- **CHA 15** (Thy'rokh, the leader, DS:426Dh = 2): the game's prices, 300, 250, 175, 45000, 15000, 25000.
- **CHA 22** (a test edit: 25% off), MORE twice to draw the list again: **225, 187, 131, 33750, 11250,
  18750**; the second page 4500 (6000), 2922 (6 arrows at 650: 487 each), 225 (a one-use scroll, 300),
  3750 (5000), 6750 (9000). Bought the scroll: **"SOLD!", 5000 -> 4775** (225).
  ([picture](img/2026-11-25-ravager-shop-cha.png): CHA 15 left, 22 right.)
- **Sold it back**: **"I'll give you 180$"** (60% of 300), TAKE IT: 4775 -> 4955
  ([picture](img/2026-11-25-ravager-shop-sell.png)). DSCLOG2's sold_kept 1; `ravshop.py shop`: item 117 (the
  scroll) **first in Notaku's list again** (slot 14), the pointer's thing 523 all zeros as the game leaves
  it; MORE twice: the scroll listed again at 225, first on the first page.
- **Control** (`RAV_RULES_OFF=0x100000`, the dice log restarted: rules_hi 0xFF2F), CHA still 22: the list
  at 300, 175, 300, 45000, 250, 15000 (the game's); bought the scroll for **300** (4955 -> 4655), offered
  **300**, sold: 4955, and the scroll **gone** (not in Notaku's list; sold_kept still 1)
  ([picture](img/2026-11-25-ravager-shop-control.png)).
- The shop's slots: its own items are numbered 1, 2, 3... in its list (the shop renumbers them as it lists
  them; before it opened they were backpack cells 14-20), so the kept item's cell (14, the first free) is
  only where it waits till the shop lists it.
- The sequel's own markups (370h:36h buying, 34h selling, 914A5h and 915B8h: a shopkeeper's discount, as
  Tasarla's for Alliance members) were 0 here; they apply after the CHA's.

## The scroll's messages

Ar'Anda (INT 18, then 9: test edits), a scroll made from item 58's record (`ravshop.py scroll`) in her left
hand (slot 10; the inventory closed and opened again to show an item moved by an edit), its box's spell icon.

**Why nothing showed** (the open bug, 2026-11-21): the message box (560h:2Ah, 59A0Bh) opens its window
(5B0h:48h: DSCLOG2's msg_windows counted each), puts the text in it and calls the game's delay (0:12FAh) for
`[26B7h]` x 100 ms (the options' message time: 50, five seconds) before closing it. Two things kept it off
the screen: the game draws its windows only when it shows a new picture (3328h:0B4Ch: the windows,
309Bh:1675h, on the screen not on show, then a flip, 0BF3h:5814h), which its main loop does, never in
between; and the delay was over at once (with `[26B7h]` set to 150, 15 s, the inventory answered the
pointer 4 s after the click). A copy of the drawing screen onto the one on show (a first try) showed
nothing either: the window wasn't drawn anywhere yet. SL's routine (4D0h:2Ah) waits in the game's event
loop instead, which draws.

**The fix**, MSG_SHOWN: at the wait, the game's own "drawing on, a new picture" (0B0h:2A81h with 1, as the
routine calls before its text), then the options' time waited on the BIOS clock, the game's delay given 0.

- **YOU ALREADY KNOW THIS SPELL** (the game's own, Shield known):
  [picture](img/2026-11-25-ravager-scroll-know2.png) (the box, then the message at 1.4 s and 2.8 s).
- **YOU LEARN THE SPELL** (INT 18: "Ar'Anda reads the scroll of Shield: d100 = 78, needs 85 or less (INT 18)
  -> learnt"): [picture](img/2026-11-25-ravager-scroll-learn.png).
- **YOU FAIL TO LEARN THE SPELL** (INT 9: "Ar'Anda reads the scroll of Shocking Grasp: d100 = 81, needs 35 or
  less (INT 9) -> not learnt (the scroll is used up)"): [picture](img/2026-11-25-ravager-scroll-fail1.png).
- **TOO MANY SPELLS OF THAT LEVEL** (INT 9, six 1st-level spells known: "Ar'Anda can't learn Shocking Grasp
  from the scroll: knows 6 1st-level spells, the most for INT 9 (the scroll is kept)"; the item still a
  scroll after): [picture](img/2026-11-25-ravager-scroll-full.png).
- **Control** (`RAV_SKIP=message_shown,message_window`: the game's message box as it was): YOU ALREADY KNOW
  THIS SPELL, nothing on screen, the box simply gone ([picture](img/2026-11-25-ravager-scroll-ctlknow.png));
  as before the fix (the first runs of this session, with the build before it).

The game holds still while the message shows (its own routine's wait), five seconds at the options' first
setting; the message box's other 55 calls (I COULDN'T SELL THAT in a shop, and the rest) show the same way
now, not looked at one by one.

## Memory

DSCLOG2.EXE 39776 -> 40432 bytes (+656); not measured with `dosmem.py` this time (the port-all run had
39248 in upper memory, 116208 free after it: about 115,550 free now).

## Water

- **Uhubito's caravan office** (Tyr, the street's east side, y ~1340-1420): clay jugs by the counter and
  on the shelves at the back.
- **Shadow Square** (Tyr, the city's west): barrels, jars and sacks at the stalls south-west of Notaku's
  (world ~150-250, 1000-1100), where a merchant woman stands.
