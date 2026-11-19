# 2026-11-19: the mod's bug fixes carried over to Wake of the Ravager, first tests

**Under test:** which of the mod's fixes to the game's own bugs apply to the sequel as they are,
and whether a copy of the sequel with them still plays. The study is in
`reports/wake-of-the-ravager.md` ("Carrying the fixes over").

1. **Twins.** Each of `gamepatch.PATCHES`' 454 sites: its 48 bytes in SL's DSUN.EXE scored
   against every place in WotR's. 223 have a clear twin (55% alike or more, 5 bytes ahead of the
   second best), 124 of them with the patch's original bytes intact; 17 of those make no call to
   the helper.
2. **Side by side** (capstone, 16-bit): `party_best`, `monster_count`, `thief_slots`, `dam_half`
   the same code; `page_free` the same test and the same target (the call before the return);
   `power_end_*` the same logic but for SL's DS:1E24h; `armor_charge` tests flag 20h, not 4, and
   pushes 5, not 2: not the same. None of the five hits a relocated word.
3. **Spells.** No spell table in WotR's program: `RESOURCE.GFF` `DATA` 0-319, 73 bytes each (SL's
   32-byte record, the name, an 8-letter short name). SL's names come from its 7-byte info records
   (spell n at info + (n-1) x 7, +5 the name's DS offset); SL's 32-byte table starts at 41F70h in
   its file. Of 23 fixes matched by name, 21 bugs still there, 2 fixed by SSI (Dispel Magic,
   Bestow Curse); Iron Skin's charges other bytes. Monsters' records (fire elementals, babau,
   slaad, styr, tari, shadows): no match.
4. **The fixed copy:** `ravfixes.py` (new) made `$WORK/ravfix` (hard links, DSUN.EXE and
   RESOURCE.GFF rewritten): 5 program fixes, 23 spell fixes. Run with GOG's settings (EMS on): the
   intro (Shift missed once: pressed again), START GAME, the cinematic, Tyr's talk ("3" picks the
   third reply, Return pages on), the map with Thy'rokh leading. Memory: `party_best`,
   `monster_count`, `thief_slots` and `dam_half` (twice) fixed, no copy of the originals;
   `page_free`'s overlay not loaded (neither version there).
5. **When the game reads a spell:** no table in memory; one record at a time. At Tyr only
   Disintegrate's (`DATA` 236, from the cinematic). The top-left icon opens USE (Thy'rokh,
   cleric level 1, the party's four in their panels); a click on his first spell put its range on
   the map, and Bless's whole record (`DATA` 115) was in memory. A right click cancelled the aim.
   None of the four knows a fixed spell: a fixed record loading, and the fixes at work, are next.

**Stalls:** Xvfb had gone between two steps (DOSBox started with no display: killed it and
started Xvfb again). The mouse was already captured on the second run, so the "capture" click
pressed START GAME itself: harmless here, but look before clicking.

**Water:** Tyr's opening room has a table with a pot and a jug on it (not tried).
