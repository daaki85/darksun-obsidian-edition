# Obsidian Edition for Wake of the Ravager: the port plan

The user's decision (2026-11-19): the full port, mostly the core: **the bug fixes, the rule changes and
the quality-of-life additions**. What can go into Wake of the Ravager (WotR) and what can't is sorted
below, with the reason for each; the study behind it is [wake-of-the-ravager.md](wake-of-the-ravager.md).
Work is on the branch `claude/ravager-port`.

## How it is built

The same parts as for Shattered Lands (SL), the player starting WotR from the same Loader in DOSBox:

- **A helper of its own, built from DSCLOG's routines.** (First planned as one source with an
  `%ifdef WOTR` address table; changed on reading it: DSCLOG's 29,000 lines name SL's addresses inline
  in nearly every routine, and its keyboard, mouse and DOS hooks act on every key and file open, so an
  `%ifdef` build would have touched everything and left SL's source hard to read.) `dos/dsclog2.asm`
  builds `dos/DSCLOG2.EXE`: each routine taken from `dsclog.asm` keeps its name there and says what
  differs; the header keeps DSCLOG's layout for the fields the Loader reads, under the signature
  `DSCLOGR1`. It holds only what is ported, so it never touches what it doesn't know.
- **A patch table per game.** `gamepatch.py`'s `PATCHES` stays SL's; `PATCHES_WOTR` holds WotR's
  sites (each found and read by hand, its original bytes checked, as `playtest/ravfixes.py` does
  now), written to the patched copy `DSUNLOG2.EXE`.
- **The game's data per game.** WotR's spells are `RESOURCE.GFF`'s `DATA` 0-319 (SL's record in the
  first 32 bytes): the spell fixes and rule changes in data become edits to the Loader's copy of
  WotR's `RESOURCE.GFF`, as SL's go into its copies.
- **The Loader knows which game it starts**: by `DSUN.EXE`'s size (611,408 SL, 634,416 WotR), with
  WotR's own DOSBox config (its CD as F:, found by the game through MSCDEX whatever the letter, so the
  mod's folder stays D: as for SL; EMS off and `UMBPLUS.COM` as SL's), its memory layout for
  the window and the dice log (creature records 31h bytes at DS:19C9h, sheets 42h at DS:19C5h,
  items 17h at DS:19C1h, whose turn DS:426Dh...: `playtest/RESEARCH.md`), and its patch table.
- **Memory**: measured, room enough (WotR leaves about 110 KB spare in the 640 KB, SL 57 KB; the
  same 156 KB of upper memory). The WotR helper starts small and grows feature by feature; the 64 KB
  segment is the limit to watch.

## What goes in, and what doesn't

**Goes in** (engine features, the same in both games):

| Area | Features |
|---|---|
| The game's bugs (engine) | every fix of [GAME-BUGS.md](../obsidian-edition/GAME-BUGS.md) whose bug WotR still has: found so far 6 program fixes and 21 spell records' (2 SSI fixed itself); the rest to be checked one by one |
| What the game shows | the combat log, names over figures, the Look box; THAC0, saves and thief skills on the inventory; the creation screen's additions; spell slots on USE; charges in item boxes; the Effects screen; what a scroll says; no manual check |
| Rules: characters | class restrictions, multiclass hit points, hit dice (the better of two), scores and hit points as rolled, AD&D's class tables, CON as in AD&D, ages and magical aging, dual-classing |
| Rules: weapons and armour | two weapons, half-giants' two-handed weapons, weapon traits, creature size, held targets, rings and cloaks of protection, helms AC 1, items saving against acid |
| Rules: magic | rangers' casting level, preservers' INT, the spell save, DEX against fire, cold and electricity, Enlarge, spells and psionics as the manual describes them, spells rolling to hit, resting as in AD&D |
| Customization | weapon specialization, kits, STORE and RECALL, fuller starting gear, preservers' first spells, psionic powers at creation |
| Expanded features | CHA at shops, buying back magic items, thief skills from AD&D's table, hiding in shadows to backstab, picking pockets |
| Graphics (drawing, not art) | shadows, dust, see-through figures, magic items' glow in shops, spells on the ground |
| Controls | T and Shift+T looting, S selling, Tab/Enter and the rings, scrolling the map, M/U/I, the whole party in view, the view in fights, the pointer in scenes, spells kept on the Effects screen |
| Saves and characters | more saves and saves under names, more characters in the roster; game speed |
| The Loader | the dice log, the window (Characters, Spells, Memory tabs), the crash and freeze reports, the Options tab |
| The party transfer | the Loader's own (below: every item comes across), with the kits and weapon specs kept |

**Doesn't go in:**

| Feature | Why |
|---|---|
| Kalzith, Semyon, the champions' bout, Legcrusher at the fountain, the cooked vulture, Pehtucl's chest, what Dinos and the Trustee say | Shattered Lands' story: its people, places and scripts |
| SL's script fixes (people, quests that stuck or ran twice, who is talking) | SL's own scripts; WotR's scripts are other scripts (its own bugs are a later, separate job) |
| The mod's new items placed in SL's shops, chests and people | placed in SL's regions (the items themselves do come across with the party: below) |
| Level cap by XP | WotR already takes characters past SL's caps |
| Elves' and half-elves' figures, what the party wears drawn on the figures | SL's figure art: WotR's figures are other, larger pictures; a later job if wanted |

**Also in, the user's decisions (2026-11-19):**

| What | How |
|---|---|
| **The six new wizard spells** (Cat's Grace, Erdlu Claw, Fogbolt, Reflected Image, Spook, Friends) | new spell records in RESOURCE.GFF's copy, with their icons and texts, and their effects in the helper as in SL. A character's known wizard spells are a 15-byte bitset (bit n, spell n: 0-119), so each needs a free wizard number below 120 |
| **The 6th-level priest spells** | WotR has eight of the mod's ten under its own records (Heal 210, Harm 211, Blade Barrier 208, Wall of Thorns 214, Sunstroke 213, Fire Seeds 209, Heartseeker 212, Waters of Life 215): those are WotR's, the mod's rules where they differ to be checked one by one. **Whirlwind and Restore Youth** are added (new records, the mod's icons and effects) |
| **Every item comes across with the party** | the mod's new items and **every item of Shattered Lands**: CHARTRAN gives WotR's counterpart where `ITEMS.BIN` has one and a money bag for the rest (the mod's items, and some of SL's own: 114 in the user's "rest no call" save). So: each SL item without a WotR counterpart is added to the copy of WotR's `OBJEX.GFF` (its object, record and icon, made from the player's own SL files; the two games' object records are near kin: OJFF 16 bytes in both, RDFF 61h bytes in SL and 68h in WotR), and **the transfer becomes the Loader's own** (Python, checked against CHARTRAN byte for byte on the games' own items) mapping each item to its counterpart or its added object |

**Later, if wanted:** defilers' scrolls (WotR has defilers).

## Order of work

Each step is shown working in WotR in DOSBox (the playtest kit's `rav*` tools) before the next.

1. **Scaffolding**: the Loader recognises WotR and prepares its copy (`DSUNLOG2.EXE`, the data
   files) and its DOSBox config; the helper's `%ifdef WOTR` build; the WotR layout. Done when the
   Loader starts WotR with the fixes `ravfixes.py` applies now.
2. **The helper loads under WotR**: installs high, its header found by the Loader, the game runs.
3. **The dice log**: rand (its site found: 5A22h), the saving throw (66EA6h), AC, the text window,
   message boxes; the Loader's dice log and window reading WotR's records. Done when a fight's rolls
   appear in the log.
4. **The bug fixes**: the remaining engine fixes, each found in WotR and checked.
5. **What the game shows**, then **the rules**, then **customization**, **expanded features**,
   **graphics**, **controls**, **saves**: feature by feature, the cheapest and most used first,
   each with its switch on the Options tab working for WotR.
6. **The transfer**: the Loader's own, every item and the kits and weapon specs carried; the SL
   items and spells WotR lacks added to its data copies first.

Progress is kept in the table below as features land.

## Progress

| Step | State |
|---|---|
| Study, memory, the first fixes seen working | done (wake-of-the-ravager.md) |
| 1. Scaffolding | **the Loader side done**: `dsloader/ravager.py` (the sequel recognised by its DSUN.EXE, its patch table: the data path and 6 fixes; its 23 spell records' fixes; its DOSBox config), `launch` taking a sequel folder its own way, `dsloader launch --ravager [FOLDER]`, `tests/test_ravager.py`. Played in DOSBox the Loader's way (`ravstart.sh` with `RAV_LOADER=1`): the copy runs from the mod's folder (D:) with the game as C: and its CD as F:, to Tyr. Still to do in step 1: the WotR layout for the window (with step 3). The spell records' copy (`RESOURC2.GFF`) is written but read only once the helper redirects the game's opens (step 2) |
| 2. The helper loads under WotR | **done**: `dos/dsclog2.asm` (DSCLOG2.EXE, 1,280 bytes): rand() through it (the patch at 5A22h, the seed DS:384Ah), the ring in the HMA, DOS's opens of RESOURCE.GFF redirected to the Loader's copy (the spell fixes now read in play); loaded high (C91Bh) before the game. Played: to Tyr and into the Draxans' fight, 36 rolls in the ring, the same filters matching the sequel's code. In the build audit (`test_audit_builds`) |
| 3. The dice log | next: the Loader's reader for the sequel's helper and records (its roll labels are by the calling code's address: the sequel's own table) |
