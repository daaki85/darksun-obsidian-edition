# Picture slot reuse in DOSBox: lots of items on the ground (2026-11-09)

Under test: DSCLOG's PIC_REUSE (sites PIC_FULL 26009h, PIC_PLACE 260CCh, PIC_COUNT 2612Bh: 151-153).
With the game's 300 picture slots taken, a slot out of memory that no wall or map thing names is
reused for a new picture, which goes in the first gap of the store it fits. Build: `buildcheck.py
pic_full pic_place pic_count` same as the EXE, 134 vectors at their handlers; the three sites read
CD 98 97/98/99 in memory. Save: `pens-thornwall-rack` (region 29h, leader 1816,1384): 203 slots,
store end 305,305.

## Steps

1. **Items for the ground**: `giveitems.py MEMBER N FIRST` (new) gives plain items in memory, the way
   the Loader gives the arena's ring. Two lessons on the way: a record copied from the objects file
   has 0 at +08h (contents), which in memory names item 0, and the inventory then drew no icons at
   all (the old build did the same: the tool's fault); +08h must be 270Fh (none). And plain item
   *types* gave only 21 new pictures: the tool now gives by object (146 item objects).
2. **Filling** (`groundfill.sh 14 0`, new): each cycle gives Gerakis 12 items, opens the inventory,
   DROPs each (cell, then 213,134), closes it and counts. Slots: 203, 215, 227, 239, 251, 263, 273,
   283, 291, **300** at cycle 9, then cycles 10-13 at 300 with **8, 13, 17, 18 slots reused**, the
   store's end unchanged (322,726 bytes, 43%): every new picture fitted a gap.
3. **The first build churned**: its search always began at slot 0, and the inventory's icons
   (each let go once drawn, so free) took the same first free slot in turn: 3,590 reuses in one
   cycle, 35,118 by the next. The pictures still drew, but each was read from the file again. The
   search now goes round from after the last slot reused (`pf_next`; the unit test
   test_round_from_the_last_reused): 18 reuses for the whole run.
4. **Checks** after the fill: `picstore.py check` 31 of 31 pictures in memory equal to their store
   bytes; 147 things on screen, none without a slot; `slotcheck.py` (new): 165-178 things each
   find their own picture's number in their slot, every wall's slot taken. Six entries of the thing
   table name slot 0 with nonsense pictures (26, 33751, 65395...): the same six on a fresh load of
   the save, before any reuse (the table's unused entries).
5. **Playing on**: walked north off the heap (the items drawn), away up the passage to (1816,904)
   and back (no new slots needed: 18 reused still), opened the inventory (icons drawn) and closed
   it: 78 of 78 pictures in memory equal to the store, every thing with its own picture. No stall
   (the watchdog's Monitor silent).

## Not done here

A fight at 300 slots (bodies' and spells' new pictures) wasn't run.
