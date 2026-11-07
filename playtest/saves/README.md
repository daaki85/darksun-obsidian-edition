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
- `pens-kurzak-door-recomp` (2026-11-01): `pens-kurzak-door` loaded on Dark Sun Recompiled and
  saved again there at once (slot name RECOMP1), to check a save made by the program loads in
  DOSBox and the other way round. Its `DARKSAVE.GFF` is the one the load put in the folder (the
  program did not rewrite it at the save, as DOSBox doesn't).
- `pens-thornwall-rack` (2026-11-04): a new game with the ready-made party, through the arena's
  waves and out by the gate, Kurzak followed to his stop; flag 756 (Semyon's tip) set in memory,
  the party moved in memory beside the weapon rack and back, so Thornwall is on the rack (flag
  757). Party at (1816, 1384), the east passage by the locked door (113, 90). Semyon is not in
  his pen in it. Its `DARKSAVE.GFF` is the install's own (991 bytes): the game didn't rewrite it.
- `pens-fire-count4` (2026-11-05): from `pens-after-arena`, Kurzak followed to his stop and the
  party in the east hall's fire room (map 1896, 872; its door 115, 53 opened), with the arena
  count (the game's number 12) set to 4 in memory before the save, so the next trip is Scar's.
  Not rested yet. Its `DARKSAVE.GFF` is the one in the game folder (not rewritten at this save).
- `pens-after-scar` (2026-11-05): from `pens-fire-count4`: rested, called, into the arena, Scar
  killed there by Cilla ("This makes Cilla king of the pens!"), the waves fought and out by the
  gate; in the pens at (1816, 440). The arena count 5, flags 19 and 759 set, 807 clear: the
  champions' bout is due on the next trip.
- `pens-new-chest` (2026-11-06): a new game with the ready-made party, made with the Loader of that
  day (Pehtucl's Cloak of Protection in the chest beside him, the chest's USE command in the pens'
  master script: pehtuclchest.py; the chest itself made before its shut type: `shut.py` after loading), through the arena's waves and out by the gate; in the pens at
  (1816, 440), Kurzak's greeting answered Goodbye. Nothing else done. Its `DARKSAVE.GFF` is the
  one in the game folder (not rewritten at this save).
