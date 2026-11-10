# The game's picture store: how it works, and outfits re-dressed without filling it (2026-11-09)

Under test: a fuller fix for logs/2026-11-09-missing-figures.md. The Loader's dressing (sprites.py)
marks a re-dressed member's old pictures STALE and the game loads the new ones into new slots, so
each outfit change costs a slot and about 7 KB of the game's fixed store; `_room_for` (in HEAD)
stops dressing near the end. Wanted: outfit changes that always show, without the store filling.

Setting: HEAD (c5c8414) exported with `git archive` to /tmp/picstore-wt (its own Loader, its own
settings), the game copied to /tmp/picstore-work/inst, `PLAYTEST_WORK=/tmp/picstore-work`. DOSBox
under `flock /tmp/playtest/dosbox.lock` (held by a background flock), the watchdog with a Monitor.
`fountain-user` loaded; the speech box clicked: Pehtucl's ambush (the fight is on).

## How the store works (DSUN.EXE; file offsets, header 5400h)

- **Loading a picture** (25FA6h, number DI, kind WALL or BMP): looks the number up in the table
  (load segment + 3E60h, 16 bytes: +0 number, +2 length (dword), +6 place in the store (dword),
  +0Ah far pointer, +0Eh flags (1 stored, 2 in memory), +0Fh age); found and in memory: that slot;
  found and not in memory: 25D6Ah reads it back. Not found: with fewer than 300 slots, a new slot
  at the end: its length from the GFF index, memory for it from the picture pool (265FDh), the
  chunk read from the file, its place the last slot's place + length, written to the store
  (1187:1FB5h, the result not read), flags 3. **The game never reuses a slot or a place**.
- **The picture pool** (in memory): 60,000 bytes (DS:1F76h; free blocks at DS:8E94h, 8 bytes each,
  DS:1F74h the last), made by 1DF3:00E3h (23413h) and freed by 234E8h, which also clears every
  slot's flag 2 (the slots and the store stay). The inventory and other screens run that pair:
  every picture out of memory. The allocator (265FDh) takes the best fit; short of room it frees
  the slots with the lowest age (2644Fh, the free 26701h gives back the slot's +2 bytes, so +2
  must stay the size the memory was taken at) and compacts (262C3h: memmove, then 26224h moves the
  slots' far pointers): **a picture's memory can move** whenever the game allocates.
- **The store is a handle of the game's paged memory manager**, not plain memory: handle DS:4C33h
  = 48EF0000h (index 0, id 48EFh), made at 60D9Bh with 0B5000h bytes (and DS:4C2Fh, 4B000h bytes,
  another). Handle table DS:47FAh (14 bytes: +0 the first page link, +2 the id, +4 the size);
  pages of 16 KB chained through a page directory cached in five 108h-byte blocks at DS:42D2h (+2
  key A+1, +4 key B, +6 age, +8 sixty-four (descriptor, next link) pairs; link = A<<12|B<<6|entry,
  17342h); descriptor = backend<<12 | page. Backend 0 (DS:4850h: read 1187:0491h, write
  1187:04B0h, +0Ch its parameter, 1) is **XMS**: 13A7:06B4h/0769h move with the XMS driver's
  function 0Bh, XMS handle 1, offset page x 4000h + offset. In DOSBox (xms=true, 32 MB) the store
  was XMS pages 2-2Fh, in one run, the XMS block at guest address **110000h**; the Loader can read
  and write it like any guest memory. `picstore.py check`: all 22 pictures in memory equal their
  store bytes.
- **The flush** (1DBD:06BEh = 2368Eh, called only from the region load at 1D4B6h): every draw-list
  thing's slot (+0Fh) to FFFFh (its +15h made a negative picture number), the 64-entry table at
  DS:6450h (9 bytes: number, far pointer) freed, the 300 slots zeroed and numbered FFFFh, the count
  0. It frees no picture memory: the region load runs the pool's shutdown (234E8h, 1D425h) and init
  (23413h, 1D4A9h) first. Slot numbers are also kept by the region's **wall pictures** (2466Ah:
  WALL chunks region x 100 + n, slots at load segment + 4356h:574Eh), set up again by the load
  after the flush, and by DSCLOG's kept shadows (keyed by a slot's place, +6).

## The prototype: outfits put in store cells the game already has (sprites.py, scratch copy)

Each picture dressed anew goes, in this order, into: a STALE slot holding exactly that chunk (its
number given back: nothing written); the picture's own slot if out of memory with room (+2); the
smallest STALE slot out of memory with room (the chunk written into the store there, the number
given). The old slot goes STALE. Only if none, the old way (a new slot, under `_room_for`). The
store is written only where no picture is in memory, so the game's moving of its pool never
meets the Loader's write; DOSBox is paused (itemgate's `_pause`) for the table and store writes,
and each is checked again while paused. Lengths (+2) are never changed. The store is found from
the handle, the page directory and an in-memory picture's bytes (`Store.locate`); anything not as
expected (another backend, a page not cached, no match) and the old way is taken.
tests/test_sprites.py: 21 OK (after counting a not-loaded picture as needing a slot, as HEAD).

## Runs (the ambush in fountain-user, Lex's shield, item 37, slot 10)

| Step | Seen |
|---|---|
| HEAD's Loader, `outfitcycle.py 0 10 8` | each change one more slot and 7,094-7,312 bytes: 204 to 212 slots, store end 296,443 to 354,067, 8 STALE |
| The prototype's Loader (dice log restarted from the scratch copy), `outfitcycle.py 0 10 40` | **40 changes: 212 slots and store end 354,067 throughout**; Lex's fighting picture alternated between slots 200 and 206 (both in memory, renumbered); drawn every time; `picstore.py check` 21 of 21 match |
| Shield off, on, off, on in memory, a shot each | the shield gone and back on the figure (img/2026-11-09-picture-store-shield.png) |
| Outfits never seen (item 36 taken off too, both, back) | each into a free STALE cell (208, 210, ...): still 212 slots, 8 STALE, store unchanged; 21 of 21 match |
| `fightout.sh` (the ambush to its end, 12 turns) | every figure drawn after it (the game's own new pictures: 217 slots); 21 of 21 match |
| 100 random changes out of a fight, four of Lex's items (36, 37, 39, 40) on and off (`randout.py`, the scratchpad's) | 78 dressings (a ring changes nothing on the figure): **217 slots, 8 STALE, store end 386,653 throughout**, Lex drawn after each; every party picture in the table equal to the Loader's copy's chunk, in the store and in memory (one cell, 6,657 bytes, first Jenna's walking picture, then another member's of 5,737) |
| The inventory open (I: every picture out of memory, `cachelist.py` 0 in memory), five changes in memory, Escape | the pictures' own cells written (217 slots); after the Escape Lex drawn in the outfit last set |

| `arenatrip.sh` with the prototype Loader from the start (`pens-after-scar`, the fire room, two rests, Kurzak's call, into the arena: an **area change**, 29h to 2Ah) | in the arena: 66 slots, 4 STALE, 14 of 14 match; the party drawn |
| 60 random changes there (member 0's six worn items) | 68 to 71 slots in the first 50 (outfits bigger than any free cell: the old way), none in the last 10; 17 of 17 match, every party picture equal to the copy's; drawn throughout |
| Walking into the bout | the bone wall stopped the party at (488, 264) (the guide's stall); the gate north asked nothing (no bout fought): no second area change |

The watchdog's one STUCK (02:14) was my clicks on a still screen at the gate, all four drawn.

HEAD stops dressing at about 59 more slots in the pens (300 - 24 spare - 217); the prototype went
past 118 dressings in that one area with no slot taken.

## The options

**(a) Calling the game's flush between frames (DSCLOG, or the Loader asking DSCLOG).** Possible but
not the flush alone: it zeroes the table without freeing the pictures' memory (the area load frees
the whole pool first: 234E8h then 23413h(60000)), so it would have to be shutdown, init, flush, and
then the region's wall pictures set up again (24643h: their slots are cached at load segment +
4356h:574Eh, and would otherwise point at slots given to other pictures), plus whatever else holds a
slot number (DSCLOG's kept shadows; any code that kept a slot from 25FA6h's return). Every picture on
screen is then read from the GFF files again (a pause like an area load's), at every flush. Risky:
the full list of slot holders isn't known; DSCLOG code ~60 bytes and a safe call site in the main
loop. Not tried.

**(b) Reusing slots and store places.** The game finds a picture by its number (25FA6h's scan) and
appends only when the number isn't in the table, so a slot can be given another picture by
writing its number, and the store's bytes at its place (+6, its room +2) can be rewritten; the
length +2 must stay (the pool frees +2 bytes, 26701h). A picture's memory copy must not be written
from outside: the game moves it while compacting (262C3h). Padding every party picture to a fixed
size (its room in the copy, about twice the chunk) would always fit, but would double the party's
use of the 60,000-byte pool (four walking pictures about 50 KB): rejected. What works without
padding is the prototype's: exact-content reuse (a toggle), the own cell out of memory (the
inventory), a free STALE cell big enough (anything else), the old way last. **Chosen.**

**(c) Compaction** (moving pictures down, dropping STALE slots): slot numbers change, so every
holder of one would need fixing (things +0Fh, the walls' table, DSCLOG's shadows, unknown others),
and pictures in memory move. Harder than (a) with the same unknowns; not needed once (b) reuses the
STALE cells.

**(d) Simpler**: only (b)'s first step (renumbering a STALE slot whose bytes equal the new chunk,
no store write at all) already covers toggles (a weapon in and out of the hand); the free-cell write
covers the rest. HEAD's `_room_for` stays as the last guard.

## Recommended (for whoever puts it in the mod: the prototype's diff is 2026-11-09-picture-store.diff)

Loader-side only, in `dsloader/sprites.py`; no DSCLOG change:
- `Store`: the handle (DS:4C33h), the handle table (DS:47FAh), the cached directory (DS:42D2h), the
  XMS backend checked (DS:4854h = load segment + 1187h : 04B0h), the block's address found by an
  in-memory picture's bytes and checked again at each use (`_still`); any doubt: not used.
- `Dresser._in_store` before `_unload`: exact-content STALE cell (renumber), own cell out of memory
  (write), smallest free STALE cell out of memory (write, renumber), else the old way. Writes only
  to cells out of memory, DOSBox paused, everything checked again while paused, lengths kept.
- `_room_for` counted only for pictures given no cell (a picture not yet loaded counts: the game
  will take a slot for it).
- Still to do: unit tests with a fake store (handle, directory, XMS block) for each of the three
  cells and the fall-backs; the built pictures kept per outfit (`_built`) so a dressing refused for
  room isn't rebuilt every pass (in the prototype); DSCLOG's kept shadows are keyed by a slot's place
  and would show the cell's last occupant's shadow for a figure whose picture is out of memory until
  it is drawn again (not seen; the figure's picture is loaded and drawn at once after a dressing);
  optionally a new slot taken by the old way given some room past its chunk (its index length
  raised, within the copy's room), so later bigger outfits find a cell (the arena's 5 new slots).
  On Dark Sun Recompiled the XMS block may not be in the guest RAM the Loader sees: `locate` then
  finds no match and the old way (HEAD's) is kept: check there.
