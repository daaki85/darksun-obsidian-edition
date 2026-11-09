# The Boots of Speed in a fight (2026-11-09)

Under test: DSCLOG's BOOTS_MOVE (in PROBE_MOVE: a turn's movement doubled) and BOOTS_AC (in PROBE_AC:
AC 2 better in a fight, not while Stuck, Paralyzed or Slowed) for a creature wearing the new type
SPEED_BOOTS (145: the 31st extra type) on the feet (slot 13). Build: `buildcheck.py boots_move
speed_worn boots_ac probe_move` all the same.

Steps: `loadsave.sh fountain-user` (the ambush a moment away). Seneca (member 3) already wears the
game's Boots (item 15, slot 13, type 68): run A as she is; run B with item 15 made the Boots of
Speed in memory (a scratch setboots.py: the worldgear.SPEED_BOOTS record, the item's own +4..+9 and
+10h kept, slot 13). Speech boxes cleared (boxclick.sh), the fight on.

- **The turn's movement** is at segment DS - (4356h - 37BDh), +22Bh + creature x 2 (Move x 10; the
  game's own store, 57566h; DSCLOG's MOVE_OFF), not at "2E0h from the load segment" (that is code).
  The END <NAME>'S MOVE menu shows what is left of it ("Move : 12").
- Run A: Seneca "Move : 12" (120). Run B: her round-2 turn's start: **240**; the others 120 (Lex,
  Ester) and 140 (Jenna: a Stalker's +20). Her round-1 showed 14 / 140: boxclick.sh's clicks at
  160,20 fell on the map while it was her turn and walked her 100 (clear boxes with care once a
  fight is on).
- `speed_worn` run in Unicorn on a snapshot of the live memory (the image's segment from the header
  DSCLOGva, CS that, DS the game's): CF clear for creature 3 only.
- **AC**: Arena Guards' bow shots at Seneca "target AC 0" (three), her counted AC 2; the others'
  attackers' target AC as before (no boots).
- Item box: "Leather Boots of Speed", the red icon; its line is the stealth rule's "Move +10" (move
  silently, every pair of boots). The price showed 24 only because the test kept the old item's
  value field (+6); Dagger's are 20,000.
- The other three fell Out Cold over the rounds passed (passn.sh): never saved.
