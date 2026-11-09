# The picture-store fix in the mod: outfits put in the store's cells (2026-11-09)

Under test: the fix researched and prototyped in logs/2026-11-09-picture-store.md, now in
`obsidian-edition/dsloader/sprites.py` (the user approved it), with the repository's own Loader.

## The change (sprites.py)

- `Store`: the game's picture store where it is. The handle (DS:4C33h), the handle table
  (DS:47FAh), the page chain through the cached directory (DS:42D2h), backend 0 checked to be the
  XMS one (DS:4854h = load segment + 1187h : 04B0h); the XMS block's guest address found by an
  in-memory picture's first bytes, then **checked against up to 32 pictures in memory, both ends of
  each** (new since the prototype: an emulator whose XMS isn't one piece of guest RAM is refused,
  not written into at a wrong place), and checked again (one picture) at each use. Anything not so:
  not used.
- `Dresser._in_store` before `_unload`: (1) a STALE slot holding exactly the new chunk gets the
  number back; (2) the picture's own slot, out of memory with room, is written in place; (3) the
  smallest STALE slot out of memory with room is written and given the number; the old slot STALE.
  Never a picture in memory written, never a length (+2). DOSBox paused (itemgate's `_pause`),
  everything checked again while paused. Else the old way under `_room_for`, which now counts only
  the pictures given no cell (one not loaded yet counts: the game will take a slot for it).
- Built pictures kept per outfit (`_built`), so a dressing refused for room isn't rebuilt each pass;
  `reused` counts the pictures put in cells.

## Tests (tests/test_sprites.py: 27, 6 new; the full suite 1,555 OK, 9 skipped)

A fake store on the fake guest (`FakeGame.xms`, `slot`): `test_store_found` (found; refused for
another backend, nothing in memory, bytes not matching, a page not in the directory, the handle's id
wrong, a second picture not where the pages say; refused again once its bytes move),
`test_same_chunk_given_its_number_back` (and the old way when the old picture is in memory),
`test_own_slot_written_where_it_is` (number and length kept), `test_smallest_stale_cell_with_room`
(the best fit in memory and one too small passed over; nothing in memory written),
`test_a_cell_needs_no_room` (dressed with the table nearly full when both pictures find cells; left
when one needs a new slot), `test_no_store_the_old_way` (another backend; bytes not found, as on the
recompiled program). Each cell test fails with `_in_store` made to do nothing; the store test fails
without the new check; the smallest-cell test fails if the out-of-memory test is dropped.

## DOSBox
