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

## Step 4: the engine fixes, where each stands (2026-11-20)

`playtest/ravsites.py` looks for each of SL's 454 patch sites in WotR's program by likeness (64 bytes
round the site, the original bytes required there): 104 found, 231 with no likeness (the code
rewritten or moved into other shapes), 88 with other bytes (most of them the same code on WotR's
record offsets), 27 unclear. Each find is read by hand before it goes in.

| Fix | Where it stands |
|---|---|
| Thief skills' equipment penalty, the whole party's thief roll, random monsters' count, the slowed DAM line, the view's page freed, "can't save" signed, 23 spell records (Scare's save, Cause Serious/Critical, Brave/Fear marks...) | **in** (steps 1-2) |
| **Share Strength** (a maintained power ended on everyone) | **in**: SL's six patches at WotR's loop (61A7Dh), its effect records' fields 147h on and the live count DS:2100h |
| **Graphics disappearing** (SSI's note 2712 is WotR's) | **in**: DSCLOG's PIC_REUSE in DSCLOG2 (INT C0h-C3h at WotR's four sites: 2A5E7h, 2A6FDh, 2A75Ch, 2A58Eh) on WotR's cache (300 slots, the count DS:265Dh, the table at load + 42A2h:0CA8h, the store 123360h bytes; the map things DS:67BBh, 25h bytes, slot +10h, name slots; the walls don't use it). **253 of 300 are taken at the start of Tyr.** Seen: with the count set to 300 at the opening talk (a test edit), the ambush's new pictures drawn in 5 reused slots, no store overlaps; the control (the sites put back) leaves the fallen woman and her things undrawn |
| **Armor's charges** (one for each damaging hit, not also for every spell or blow landing) | **in**: SL's armor_charge bytes at 84B7Eh (the routine SL's 7A539h; WotR numbers Armor's effect 5). Seen: Ar'anda's Armor (14 charges) lost one a damaging hit; the control (`RAV_SKIP=armor_charge`) two |
| **Missiles from behind** (only melee is from behind by facing) | **in, the missile case not yet seen in play**: DSCLOG2's MISSILE_REAR (INT C4h) at the sequel's attack set-up (5C99Fh: "from behind" a byte at [bp-19h], THAC0 [bp-1Eh]; SL's [bp-1Ah], [bp-20h]); read side by side with SL's; 20 melee attacks logged as before with it in. A shot at a turned back still to arrange (`ravfight.py attack`) |
| **Bless and Aid's measure** (from where each stands) | **in, not yet seen in play**: the sequel's routine (86638h) pushes the map thing's fine x (DS:67C5h) twice for the place to measure from; the first made the y (67C7h), SL's bless_from_cell |
| **Absorb Disease** (no 1d6 STR) | **in, not yet seen in play**: its handler (661FFh) ran on into Strength's (6623Bh) both ways; both now jump to Strength's end (65B0Ah) |
| **Resting while poisoned** (a druid's free Neutralize Poison before the kill) | **in, played** (2026-11-20, at the inn): the rest reads each member's effects (8CD2Ah) before the free cures and kills the Poisoned from that copy (8D02Dh); DSCLOG2's REST_POISON (INT C5h) answers the test from the effects table as it is then. Seen: Gerakis Poisoned (test edit), a rest, the poison gone, Gerakis alive, REST_POISON called for all 4 |
| **The inn's room never rests** (the game's own script, not SL's: WotR's alone) | **in, played**: the Loader's first script fix (`inn_rest`, dsloader/ravager.py SCRIPT_FIXES, in the copy GPLDAT2.GFF that DSCLOG2 opens for GPLDATA.GFF). Reyhan's ring's look trigger (GPL 142 at 1478) arms a range-15 trigger that deletes the ring on the last paid night, before the program's own rest (6951Ch) can run: one night paid, no rest. A GOTO over that arming: the night rests, the spent ring goes on the next look |
| **Free Action** | **not needed**: SSI's own handler (661A0h) also takes off Petrified, No Attacks, Cannot Move (its Stuck), Cannot Use Psionics and Can't Cast |
| The fire elementals' resistances | set aside: the sequel's monster kinds aren't SL's table; its own resistance classes found since (2026-11-21, the Look box: 85052h, DS:2588h, DS:25ACh) |
| New counted as Okay | 12 of SL's 24 tests found (WotR's status at +14h); matters only between creation and the game's start: later |
| **Negative Plane Protection** (saved as against Vampiric Touch, which allows none) | **in, not yet seen in play**: the same code at 84DD2h (effect 79 "Protected vs Life Drain" taken off, the save as against spell 38, Vampiric Touch, +1Fh A0h: no save allowed, so the save routine 66D26h answers "not saved" at once). DSCLOG2's NPP_SAVE (INT C6h) at 84DDAh: the save as against POISON's record (179: 21h, paralysis, poison and death; no spare record to copy Vampiric Touch into as DSCLOG does). The helper loads with it (2026-11-20) |
| **Acid Arrow** (its acid never burned after the hit) | **in, played** (the burns): SL's five sites found by hand (the effect added 7FAA6h, the burn 82BF3h, the spell damage's effect 651FEh, the charge spender 7FD99h, the round's start 5B592h with its first-round byte DS:54Eh); DSCLOG2's ACID_* (INT C7h-CBh), the spender called through its stub 608h:57h. Seen: 3 charges on Gerakis (test edit) burnt one a round in the opening ambush, then gone. The cast's time made rounds not yet seen |
| **Mirror Image** (no blow stopped; one's own spells taken) | **in, played** (blows): the spell's d100 (84BF8h: the sequel already skipped area spells) made a foe's only, DSCLOG2's IMAGE_SPELL (INT CCh); a hit (5D09Fh, SL's ns_blow site, the same code) taken by an image 75 in 100, DSCLOG2's IMAGE_BLOW (INT CDh: the game's rand, an image spent through 608h:57h, the attack a miss). Seen: 4 images on Gerakis (test edit), two Draxan hits taken by images. Reflected Image's 50 with the new spells |
| People's armour unworn (until their first action) | **not needed**: the sequel puts it on as they come (seen 2026-11-20 in the opening ambush before any Draxan acted: Brigandine or Ring Armor in the worn list, Lotulis, bow and arrows or a mace in the held list). The mod's extra (cloaks, belts, boots, amulets, rings put on: dsloader/people.py, a dice-log pass that writes) waits for step 5, with the sequel's dice log able to write |
| A fight's music, the quiver's last arrow | **not found**: no read of a region's creature levels with a word index (SL's 14-creature loop isn't in the sequel), and the sequel's ammunition code isn't SL's (no "mov es:[6],al", no cut of the round's attacks near its attack set-up): rewritten; to look at again with the music and missiles in play |
| Psionic Blast, the shop's glow, the Effects screen's click (a switch) | the click in (2026-11-21, above); the others' sites found; their helper routines to port (step 5's with the features they belong to) |

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
| 5. What the game shows: no manual check | **in, not yet seen in play** (2026-11-20): the sequel's copy protection is GPL 331 (a presence "creates a mindlink", a word from the manual, three wrong answers and the party dies), run by GPL 137 (a look trigger on object kind -2974, set by GPL 146, region 54's) while (135,29) isn't 7. In the Loader's copy of GPLDATA.GFF (SCRIPT_FIXES `no_manual_check`) 331 does what its right answer does ((14,0) 0, (7,32) 255, (7,29) 7, as GPL 142 at 1) and returns; its first two commands made those and the filler, so the script still decodes (tests/test_ravager.py) |
| 5. What the game shows: spell slots on USE | **in, played** (2026-11-20, logs/2026-11-20-ravager-use-slots.md): SL's PROBE_USE, PROBE_WIN and USE_DRAW in DSCLOG2 (INT CEh at 79543h, after the LEVEL button's label, SL's 70FBBh; INT CFh at 303BEh, a window brought to the front, SL's 2BBA9h: the same code), the sequel's addresses: the window on show DS:1431h, the level DS:43ECh, the list DS:43E8h, the character on show (load + 3E71h):0B44h (selector 370h), the USE screen's window (load + 45C9h):0 (selector 4D8h), the text routine 301Bh:172h, its colours DS:2D16h and 2D14h, the format DS:0F6Ah. The Loader's dice log writes SL's lines into DSCLOG2's SLOTS_TEXT (header +148: the read-only view's one writable buffer). The most is the sequel's own slot routine's (626B7h: SL's but for its test switch, a byte at DS:13F8h, and which classes cast: wizard 11 and 18, priest 1-8, 13-16 and 19); none of the mod's rules or robes yet. Seen: the lines drawn and redrawn for each level and character, none on PSIONIC, after a rest at the inn every count left equal to the most shown, and Armor cast from USE taking WIZ 3/3 to 2/3 |
| 5. What the game shows: charges in item boxes | **in, played** (2026-11-20, logs/2026-11-20-ravager-item-box.md): SL's PROBE_ITEM_BOX, IB_CHARGES and IB_MATERIAL in DSCLOG2 (INT D0h at 9A4FEh, SL's 8C1A1h), on the sequel's records: the items' power (spell + 1) a word at +10h (not SL's byte at +0Fh: ravager.item_field fixed), the charges at +0Eh, the item types' SL +08h/+0Dh/+0Fh at +04h/+09h/+0Bh, fruit type 9, the box's colours C200B5h; "Charges:" with no space from 100 up (the sequel's box has an INFO button there). The material's "Hit -N" (the game's own routine, 1D401h, SL's) comes too; the mod's thief skill lines and the Fine Bow don't. Seen: an obsidian dagger's "Hit -2"; with test edits "Charges: 12", "Charges:250", and under AC BONUS on armour. A real charged item counting down not yet (none in our saves) |
| 5. What the game shows: THAC0, saves and thief skills on the inventory | **in, played** (2026-11-20, logs/2026-11-20-ravager-inventory.md): SL's PROBE_CHAR in DSCLOG2 (INT D1h at 91286h, SL's 6F6BFh), on the sequel's records (sheets 42h bytes, creatures 31h), its thief tables (load + 449Bh) and DEX tables (DS:084Ch, 0866h): THAC0 and the saves above STR, REAC and DEF, a thief's six skills beside STR..CHA. Ar'anda's match the game's own routine run in an emulator (with the thief_slots fix). Without the Loader's STATS rules, the age and a ranger's stealth (no mod rules in the sequel yet) |
| 5. What the game shows: names over figures | **in, played** (2026-11-21, logs/2026-11-21-ravager-labels.md): DSCLOG's LABELS in DSCLOG2 with PROBE_CAST (INT D2h at 80585h, SL's 772AAh: a spell cast recorded, kind 8), PROBE_SCROLL (INT D3h at 20230h, SL's 1CAACh: the main loop, the original call made by the helper) and PROBE_TICK (INT D4h at 3DA2Ch, SL's 3925Ch); the sequel's map things (DS:67BBh, 25h bytes, the feet +0Ah/+0Ch), object list (DS:67B7h, count 264Eh), view (DS:1408h) and rectangle routine (21E0:128Ch); the header's +238 (the palette DSCLOG2 reads) and +1834/+1838 (the slots, in DSCLOG2 itself); RavDiceLog writes labels.py's slots. Seen: "Miss" over the missed, "Scare" over Ar'anda casting it, both gone cleanly, a label following a scroll. Not yet: the charges' and arrows' labels (their passes aren't ported) |
| 5. Controls: spells kept on the Effects screen | **in, played** (2026-11-21, logs/2026-11-21-ravager-effects.md): SL's two jumps at 8B08Fh and 8B09Fh (the same bytes; the powers' range EBh-10Ch), with the Options switch (ravager.skipped). Seen: Protection from Evil stays on a click; without them it ends. SL's other Effects screen lines (weapon kinds, kits) wait on those features |
| 5. What the game shows: the Look box | **in, played** (2026-11-21, logs/2026-11-21-ravager-look.md): DSCLOG's PROBE_LOOK in DSCLOG2 (INT DAh at 640FBh, SL's 5FCDAh; the routine a little rewritten) and RavDiceLog's answer from the sequel's own damage resistance (85052h: a class byte at the creature's +0Fh, tables DS:2588h and DS:25ACh; ravlog.monster_lines). Seen: a Draxan's HP, AC, THAC0 and alignment. Not ported: PROBE_UNLOOK (the whole description in the dialogue window) |
| 5. What the game shows: View Character | **in, played** (2026-11-21, logs/2026-11-21-ravager-view-character.md): DSCLOG's PROBE_VIEW in DSCLOG2 (INT D9h at 987FBh, SL's 8A471h; SL's code at the same distances): the five saves under the item icons, MOVE and THAC0 right of HP and PSI, the sheet's numbers. Seen for Ar'anda (the inventory's numbers), Gerakis and Thy'rokh. Not ported: GEAR_WAIT (no Loader gear on the sequel's creation screen yet) |
| 5. What the game shows: the creation screen | **in, played** (2026-11-21, logs/2026-11-21-ravager-creation.md): THAC0 beside the hit points ("THAC0: M12 R12", SL's cr_thac0_*): DSCLOG's CR_HP and CR_THAC0_DRAW in DSCLOG2 as PROBE_CR_HP (INT DBh at 6B84Ch, 6BC62h, SL's 63AC3h, 63EDAh, and after PSP at 6D6AEh, 6B79Ch, SL's CR_AGE sites), the hit points' box widened (DS:1228h, 140 to 243). The creature's THAC0 follows the classes as they change, so no PROBE_THAC0 is needed. The labels' colour fix isn't needed: the bug was the mod's (2.3.0), and the sequel sets its white (F0h) on the way in. Not ported: kits (a Scholar's THAC0), ages |
| 5. Rules: hit dice, the better of two | **in, played** (2026-11-21, logs/2026-11-21-ravager-hit-dice.md): SL's hp_best as DSCLOG2's PROBE_HP_BEST (INT DCh at 95025h, SL's 87319h). The rules' plumbing with it: DSCLOG2's RULES (+170) and RULES_HI (+270), the Loader writing only ravager.RULES_PORTED. Not yet: the sequel's second roll, its level-up from XP (95CCEh) |
| 5. What the game shows: the combat log | **in, played** (2026-11-21, logs/2026-11-21-ravager-combat-log.md): DSCLOG's PANEL in DSCLOG2 (FLIP_SITE INT D5h at 16974h, SL's 14444h; PROBE_POINTER INT D6h at 3326Ah, SL's 2EA55h; the main loop's PROBE_SCROLL; INT 16h for L), the picture in its far block, the header's panel fields; RavDiceLog draws combatlog.py's panel; the sequel's fight flag (a byte, DS:13FAh), fight state (3C10h:19h) and clock (DS:9C0Ah/9C0Ch). Seen: the fight's lines and round header, L to show and hide, a click collapsing it, hidden under the game's windows. Then fixed: its colours (the interface's blue-greys, palette 232 to 239) and the copy of it left beside it when the view moves (the view drawn again after the centring routine, INT D7h at 21A5Ah, and after following a figure, INT D8h at 1E3ECh, 20193h, 2143Eh; a 0.1 s sliver once is left). Not yet: the wheel and the scrollbar's drag |
| 3. The dice log | started. **Found**: SL's dice log names a roll by the code right after the rand() call (and its caller's), not by address, and every roll site the sequel used in the Draxans' fight (260 rolls, 11 sites: the attack's d20, weapon damage, initiative and the rest) has **the same code as SL's**, at another offset (`playtest/ravring.py` collects them). So the dice log's logic carries over as it is; what differs is where it reads the game (names, creature and character records, items, spells: 135 addresses and sizes in `game.py`). Next: a layout profile for the sequel (its values swapped in when the attached game is the sequel), so the one dice log reads both games |
| 3. The dice log, working | **the sequel's fights read in the Loader's dice log**: `dsloader/ravlog.py` runs SL's DiceLog with the sequel's layout (game.py's constants rebound, `apply_layout`/`restore_layout`), a read-only view of the game's memory (SL's features' writes dropped until ported) that serves the item types in SL's 20-byte layout (the sequel's are 15), and the sequel's item names (RESOURCE.GFF's TEXT 1000, a name a line). DSCLOG2's header now has DSCLOG's full length (+268 the ring's segment, the rest zero) and captures the attack's target (DS:4206h). Shared fixes: an item's plus read through ITEM_PLUS; the attack's backstab and rear arguments read as bytes (the sequel's are). Played: initiative, every attack with its d20, THAC0 and the AC hit, weapon names and dice ("Stone Lotulis (2d4)", "Bone Mace (1d6+1)"), damage with STR and material; the damage matches the hit points lost (one hit by 1 HP, to check). Then: **the initiative's names** (its table, selector 308h: load + 3C4Fh at DCh); **saving throws** (DSCLOG2's PROBE_SAVE at 66EA6h, recording each save's total and number needed; seen: "Terrannus's saving throw vs Scare from Ar'Anda (spell): not needed (saves automatically) -> saved"); **spells by name and their dice** (the view serves the sequel's spell records from the Loader's RESOURCE.GFF copy as SL's table, from F0000h, and the names from the records); **the Loader's window and `dsloader log`** pick the sequel's dice log when its helper is loaded (`ravlog.make`). **The AC** each attack uses (DSCLOG2's PROBE_AC at the end of the sequel's AC function, 5D6E6h: the function rewritten, the AC after armour in `[bp-4]`; seen: "AC of Gerakis against Draxan: 5 (base 10, armour -3, DEX -1, other -1)", every "needs" adding up). **The sequel's combat sounds** (a routine of its own picking a fighter's sound by kind and sex: the "Dice: 1d5" and "1d12" lines) named, among all rolls only. **Damage checked against the hit points lost**: 21 hits, every one matching (the "1 HP off" was Gerakis gaining 1 HP between rounds on his own). **The party tabs** (Characters, All fields) on the sequel: the layout made from Shattered Lands' by the field maps (`ravlog.window_layout`), the window's reads through RavGameData on the read-only view with none of the mod's rules (the sequel's game doesn't apply them yet): spell slots left (DS:4469h/4474h, 22h a member; the slot rules DS:670h/684h), the thief skills (the table at load + 449Bh, its race rows 16 bytes longer), equipment and THAC0 by weapon, saves, AC. **The hit points after each hit** (hp_changes back on in RavDiceLog's pass: without it the round's end said "takes none of the N damage" of every hit; Gerakis's +1 is the game's regeneration at CON 20+). Still to do: the window's other tabs (Dialogue, Spells, Memory tools' party parts) and the combat log in the game (their screens' code), a save line that didn't show; the gear's slot names to check against the inventory screen out of a fight |
