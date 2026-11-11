# A lock failed: another try only a level later (2026-11-11)

Build: obsidian-edition with LOCK_SITE (DSCLOG 69,136 bytes; `buildcheck.py` OK). In DOSBox.

From `pens-new-chest`: `shut.py`, `teleport.py 200 1432 40 1322`, walkto (216,1440) then (184,1400),
`thief.py 0 1` (Gerakis a 1st-level thief: open locks 25, find traps 20, in memory).

1. `chestuse.sh`: "Gerakis tries to find/remove traps: d100 = 79, needs 20 or less -> failure", the
   needle sprung (2d6 = 9), then "Gerakis tries to open locks: d100 = 27, needs 25 or less ->
   failure" and "Gerakis works at the lock but it holds."
2. The chest used again (the eye from `pointer.py look`, a slow press at 161,74, the look box's third
   button 236,101; `chestuse.sh`'s two right-clicks had cycled past the eye, left on from step 1):
   "Gerakis tries to open locks: d100 = 52 -> failure (Gerakis failed this lock at this thief level:
   another try once a level is gained)", and the chest's own "works at the lock but it holds".
3. `thief.py 0 2` ("Gerakis is now a 2nd level Thief"), the chest used again: "Gerakis tries to open
   locks: d100 = 34, needs 29 or less -> failure" (rolled again; barred again at 2nd level).

A use right after a message sometimes didn't open the look box (the eye showed red over the chest):
`pointer.py walk` then `pointer.py look` again, then the press, worked.

The pocket fumble's rule is covered by `test_fumbled_with_thieves_as_in_add` (not played).
Not saved (memory edits).
