# Audit fixes 1 in the game (2026-11-18)

Branch claude/audit-fixes-1 (DSCLOG signature DSCLOGvb; buildcheck.py: OK, 129 vectors at their
handlers). Save `selling-junk-user` (the party beside Kalzith in the pens). Window 320x240.

## 1. Selling a magic item: the buyback with the Loader, the game's sale without it

- `openshop.sh`: Kalzith's shop. Gerakis's Bone Cahulaks +1 (item 19, pack cell 211,44) on the
  pointer (thing 523 = item 19), SELL (265,63): "I'll give you 6960", TAKE IT (140,91): SOLD!,
  money 85 to 7,045. DSCLOG's queue: SOLD_SEQ 1, SOLD_Q (523, merchant 30), SOLD_ITEMS back to
  0FFFFh (the Loader saw to it); the pointer's thing all zeros; item 19 in Kalzith's pack
  (`carried.py Kalzith`, slot 14).
- Escape, 1, the box: the shop lists it at 11600. With 10,000 added in memory (the money; not
  saved), a click on it: SOLD!, money 5,445, item 19 on the pointer as the game's buy leaves it;
  put back in Gerakis's pack (211,44). **The buyback works.**
- The Loader's dice log stopped (its pid killed), 7 s waited (past LOADER_FRESH's 5 s): Gerakis's
  Leather Inixhide +1 (item 18, 211,62) sold: "I'll give you 3600", TAKE IT. SOLD_SEQ still 1
  (nothing queued), the pointer's thing emptied, item 18 first on the game's free list, not in
  Kalzith's pack: **sold as the game does, not left on the pointer and lost.**
- The dice log started again (attached).

## 2. Negative Plane Protection against an undead's touch

Not played: no save has an undead with a negative-energy attack near the party, and setting one
up in memory is long. Covered by the emulated test (`test_dsclog.NewSpellTests.test_npp_save`:
the save made through 5B8:2Fh with Vampiric Touch's own record's save byte 21h for the call only,
record 212 untouched) and the dice log's naming test (`SaveTests.test_npp_save_named`).

## 3. A pickpocket and a T loot (the gate held before the lists are read)

- Still in `selling-junk-user`: Kalzith's menu Farewell (4), `thief.py 3 12` (Cilla a 12th-level
  thief, a memory edit: not saved), `pocket.sh 112 108 Kalzith`: "d100 = 44, needs 95 or less ->
  success", "Cilla lifts Scroll from Kalzith unnoticed"; the scroll (item 210) in her backpack,
  Kalzith down to 5 scrolls. A walk of every list and the free list (a scratch script): 400
  records, none in two places.
- `fountain-user`, the ambush clicked in, `fightout.sh`: DONE after 10. `bodyitems.py`: Pehtucl's
  body, thing 151, screen (87,144). The eye, a slow press at (87,140): its window. **T**: "Lex takes
  Slavepen key, Grapes, Guava (4), Obsidian Bloodwrath +1" / "Ester takes Bone Brgnd.Chst Armor,
  Bone Brgnd. Arm Armor, Bone Brgnd.Leg Armor, Ring/Protection +1, Leather Shield". The lists
  walked again: 400 records, none twice. (T shuts the window itself: an Escape after it opened
  EXIT: SAVE GAME?, cancelled at 140,115.)

## 4. A new character's gear on the creation screen

- `start.sh`, the title clicked past, 35 s, CREATE CHARACTERS (165,92), a right-click on slot 1
  (64,52), NEW (110,57): a human fighter, Rick th'Untamed. DONE (279,183), the weapon window, the
  long sword (72,46): "Rick th'Untamed starts with more gear: Sling". `carried.py`: Leather Shield,
  Leg, Arm and Chest Armor, Leather Sling, Bone Long Sword. GEAR_DUE back to 0, GEAR_WHO 0 (the one
  worked on: cleared). The lists walked: none twice.

All four: **as they should be.** DOSBox and Xvfb stopped by pid at the end.
