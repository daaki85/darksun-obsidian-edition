# Saved games for tests

Each folder is one save, as the game writes it (`SAVE01.SAV`, the slot; `CHARSAVE.GFF` and
`DARKSAVE.GFF` beside it, the last written at the save and copied over `DARKRUN.GFF` by LOAD),
made with this repository's Loader build of the day. `loadsave.sh NAME` copies one into the game
folder and loads it. Take all three at the moment of the save: a set without `DARKSAVE.GFF`
cannot be loaded in a fresh install (2026-11-01).

- `pens-after-arena` (2026-11-01): a new game with the ready-made party, through the arena's
  waves and out by the gate; in the slave pens (region 29h), Kurzak just met, party at
  (1672, 344). Cermak is a 2nd-level preserver. Nothing else done in the pens. Its
  `DARKSAVE.GFF` is a stand-in (2026-11-01): the set was taken without one (with a copy of the
  slot as `DARKRUN.GFF` instead), so the file is from another game at the same point, just out of
  the arena; the entities' timers may differ from the saved game's.
- `pens-kurzak-door` (2026-11-01): from `pens-after-arena`, the party followed Kurzak (follow.py 29)
  to (1592, 520), square (99, 32), where he says "All right, go through the door. There's a place
  to rest down the east hall...". The doors bordering the party's area (doors.py) are still
  closed. Its `DARKSAVE.GFF` is the one the save left in the game folder, which the DOSBox game did
  not rewrite at this save (dated 2026-10-28, 991 bytes: the install's own).
