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
  Its Scar and henchmen were made on the arena's first visit, before 2026-11-10's gear (Scar's long
  sword, no helm or leggings; henchmen with bone axes and no armour): test their gear in a new game.
  Not rested yet. Its `DARKSAVE.GFF` is the one in the game folder (not rewritten at this save).
- `pens-after-scar` (2026-11-05): from `pens-fire-count4`: rested, called, into the arena, Scar
  killed there by Cilla ("This makes Cilla king of the pens!"), the waves fought and out by the
  gate; in the pens at (1816, 440). The arena count 5, flags 19 and 759 set, 807 clear: the
  champions' bout is due on the next trip.
- `pens-new-chest` (2026-11-06): a new game with the ready-made party, made with the Loader of that
  day (Pehtucl's Cloak of Protection in the chest beside him, the chest's USE command in the pens'
  master script: pehtuclchest.py; the chest itself made before its shut type: `shut.py` after
  loading), through the arena's waves and out by the gate; in the pens at (1816, 440), Kurzak's
  greeting answered Goodbye. Nothing else done. Its `DARKSAVE.GFF` is the one in the game folder
  (not rewritten at this save).
- `fountain-user`: the user's save "templar fountain" (2026-11-08): the slave pens, Pehtucl leading the party to the fountain, the ambush a moment away (its speech comes on loading). Only the user's SAVE01.SAV: CHARSAVE.GFF and DARKSAVE.GFF are pens-after-scar's (loads and plays). The ambush's fight: Pehtucl, 4 Arena Guards and a Guard; the script also sends every guard of those kinds in the region hunting (GPL 145 at 0xE99).
- `trap-user`: the user's save "trap" (2026-11-08): the party (Lex, Jenna, Ester, Seneca) in Pehtucl's room, beside his chest (leader 136,1400; the chest about 200,1393 on the map, at screen 200,95 with the camera 0,1296). A game that came to the pens before 2.14.0: its chest was the game's plain one (type 31h), shut by the Loader since. Only the user's SAVE01.SAV: CHARSAVE.GFF and DARKSAVE.GFF are pens-after-scar's.
- `rest-no-call-user`: the user's save "rest no call" (2026-11-11): the party (Cromwell, Balthbeorn, Finster, Cenna) by the fire room's ring (leader 1960,840; the ring at screen 205,120 with the camera 1728,736). Flag 497 set (the Trustee's key used on a door): resting brings no call. Only the user's SAVE01.SAV: CHARSAVE.GFF and DARKSAVE.GFF are pens-after-scar's.
- `semyon-rack-user`: the user's second "rest no call" save (2026-11-11): Semyon saved and told of the shipment (flag 756), the pens' weapon rack (2599, at 779,550) emptied by the party before it: Thornwall had nowhere to go (`rackcheck.py`). Only the user's SAVE01.SAV.
- `grate-user`: the user's save "slave pen grate" (2026-11-11): the party (Cromwell leading) at map (56,152) beside the sewer grate; `walkto.py 60 100` brings up its menu (Y, then 1 rip, 2 hack). Only the user's SAVE01.SAV.
