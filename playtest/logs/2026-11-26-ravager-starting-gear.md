# 2026-11-26: a new character's weapon in the weapon hand in Wake of the Ravager

**Under test:** branch `claude/ravager-starting-gear` (on `claude/ravager-spec-pick`, 1e13b2e): the Loader's patched
copy of the sequel (DSUNLOG2.EXE) with the patch `gear_hands` (dsloader/ravager.py: `GEAR_TABLE`, `GEAR_HANDS`), the
starting gear's table with each weapon's slot made the right hand and each shield's the left. No DSCLOG2 change (no
site, no header field): DSCLOG2.EXE 48064 bytes, as before.

**Why:** the spec-pick log's part 9 (2026-11-26-ravager-spec-pick.md) found a new fighter's +1 Longsword in the left
hand (slot 10) behind a +1 shield in the right (slot 3): one swing a round whatever the weapon specs, so a long sword
specialist showed 1 attack a round until the player swapped them.

## The game's routine

DONE (6E0B9h) calls the starting gear at 6F197h (the creation overlay, stub 46DDh) for the new member. It sorts what
the member already has, then, for a new character (creature status +14h 0), calls 6EF49h: the class flags (sheet
+12h) pick a range of a table of 3-byte entries, a word (the object, OBJEX.GFF's RDFF) and a byte (the worn slot),
tested in this order: fighter 20h (entries 16h-1Ah), druid 10h (7-8), gladiator 40h (12h-15h), ranger 200h
(0Dh-11h), cleric 0Fh (2-6), thief 400h (1Fh-22h), psionicist 100h (1Bh-1Eh), preserver 80h (9-0Ch), anyone else
7-8; a thri-kreen (race 8) 0-1. Each entry: a new item (c8:453h), made from the object (c8:0Ah), put in the slot
(c8:288Ch), else dropped back (c8:2452h): a class's item it can't use goes to the pack. Then 6F197h's loop sends any
worn item the member can't use (5E8:2Fh) to a free pack cell. The table is selector 358h's offset 0 in the overlay's
code ("mov ax,358h / mov es,ax / movsx eax,word es:[bx]", the slot at es:[bx+2]); in memory load + 3E48h (the
runtime "mov ax,..." read from the overlay once loaded: the creation screen up), in the file 43680h (5200h +
3E480h), 35 entries. By class, with the objects' types (OBJEX's item records, 17h bytes from +0Ah of the RDFF):

| Class | Entries (object: what, slot) |
|---|---|
| thri-kreen | 733 chatkcha +1, 2 (missile); 630 gythka +1, 3 |
| cleric | 842 shield +1, **3**; 609 club, **10**; 810, 815, 820 leather chest, arms, legs |
| druid | 609 club, **10**; 734 sling +1, 2 |
| preserver | 734 sling +1, 2; 632 quarterstaff +1, **10**; 1613 chest; 1628 cloak |
| ranger | 700 bow, 2; 730 arrows +1, 1; 810, 815; 603 long sword, 3 |
| gladiator | 633 long sword +1, 3; 633, 10; 811 chest, 821 legs |
| fighter | 842 shield +1, **3**; 633 long sword +1, **10**; 812, 817, 822 bone chest, arms, legs |
| psionicist | 609 club, **10**; 700 bow, 2; 730 arrows, 1; 810 |
| thief | 705 sling, 2; 633 long sword +1, 3; 810; 612 dagger, 14 (pack) |

So the left hand (10) held the weapon of every class but the gladiator (two swords), ranger, thief and
thri-kreen: the fighter's and cleric's behind a shield in the right, the druid's, preserver's and psionicist's
with the right hand empty. `gear_hands` swaps the fighter's and cleric's two and moves the other three weapons to
the right hand (seven slot bytes; `test_ravager.TableTests.test_gear_hands`).

**Shattered Lands** keeps the weapon in the right hand (its game; startgear.HANDS is the right hand), and the
Loader's SL weaponchoice.finish_new makes the game's bone long sword in the hand a plain weapon of the first pick's
kind. Nothing like it for the sequel yet (below).

**Set-up:** a throwaway copy `ravSG` of `$WORK/rav` (game.gog, the FLIs, VOCs and PDFs hard-linked, the rest copied,
the roster reset from __support/save, no saves), `RAV_LOADER=1 RAV_MENU=1 RAV_STDOUT=1 RAV_CORE=normal sh ravstart.sh
/tmp/playtest/ravSG`, the dice log `RAV_NO_SAVES=1 ravdice.py --numbers` attached at the title menu (before the picks),
the DOSBox lock held throughout. The patched copy's 105 bytes at 43680h checked (the fixed table; the control: the
game's). The watchdog not run (guard.sh watches Shattered Lands).

## Steps

**1. A fighter (Halton, slot 1, human, 7th level).** CREATE CHARACTERS, NEW, the default FIGHTER, DONE, the powers'
three picks, the weapon window: the **long sword** (75,32). `ravspecs.py`: specs `434dc7` ['long sword'].
`ravitems.py 0`: **the +1 Longsword (97) in slot 3, the right hand; the +1 shield (91) in slot 10, the left**; bone
arms, chest, legs; the Loader's sling (2). View Character: DAM 2x1D8+11.

**2. A cleric (Swat, slot 2).** FIGHTER off, CLERIC on; the sphere stayed AIR (clicks on WATER, 240,128 to 245,130,
didn't take). DONE, the powers. **The shield in slot 10**; the club (29, wood) in slot 14, the pack: the game's
placement refused it (an air cleric uses no wood: the class rules), so it went to the pack as before the change. The
Loader's gear gave a sling, but no weapon in the empty right hand (open, below).

**3. A psionicist (Deestan, slot 3).** CLERIC off, PSIONICIST (265,53), DONE, the pop-up's EXIT (202,140), "YOU HAVE
MORE" EXIT (112,92). **The club (29) in slot 3**, the bow (18) and arrows; the Loader's leather arms and legs.

**4. A ranger (Jaardoon, slot 4: right click 117,127, NEW 165,118).** RANGER (255,61), DONE, the powers, the weapon
window ("EXPERT IN"): the long sword. **The long sword (97, +0) in slot 3**, as the game had it; bow, arrows; specs
['long sword'].

**5. The Tyr ambush (run 1).** View Character's bar (270,171), S on the title menu, 90 s, the Veiled Alliance's talk
(100,171 twice): the ambush. HP 250 each (`ravkits.py hp M 250`, a test edit, never saved), C, the USE screen's
second icon of the bottom row (75,171) opened the inventory: **Halton's +1 Longsword in the right hand, the shield in
the left, "+1 Longsword 2x1D8+11"** ([the picture](img/2026-11-26-starting-gear-fighter.png)). Computer Control for
all four on that screen's lower small icons (game 6,17 / 6,65 / 6,113 / 6,161; View Character's in a fight are
47,53 / 98,53), Escape. Nothing moved by hand. Halton's Obsidian Dragonsbane +4 (member 0's, slot 14) stayed in
the pack: the left hand had the shield. Won in round 6 (10,000 XP each). Attacks by round from the dice log:

| Round | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Halton, long sword spec (mastery), Longsword +1 | 2 | 2 | 2 | 2 | 2 | 1 (the last foe killed) |
| Jaardoon, ranger, long sword spec | 2 | 2 | 2 | 2 | 2 | 2 |
| Deestan, psionicist, club | 1 | 1 | 1 | arrow | 1 | - |
| Swat, cleric, sling | - | 1 | 1 | - | 1 | 1 |

```
Halton attacks Draxan#27 with Longsword +1 (1d8+1): d20 = 10, needs 6+ (75%), hits AC -3, target AC 1 -> HIT
    THAC0 14 base, +4 in bonuses, +3 mastery = 7
  Halton hits Draxan#27 for 18: 1d8 = [7] +1 weapon +3 mastery +7 STR 19
Halton attacks Draxan#27 with Longsword +1 (1d8+1): d20 = 11, needs 6+ (75%), hits AC -4, target AC 1 -> HIT
    THAC0 14 base, +4 in bonuses, +3 mastery = 7
  Halton hits Draxan#27 for 14: 1d8 = [3] +1 weapon +3 mastery +7 STR 19
```

**6. The control: `RAV_SKIP=gear_hands`.** DOSBox and the dice log stopped by pid, started again with the skip (the
copy's 43680h the game's bytes), the dice log attached. A fighter (Cromwell, slot 1) with the long sword pick: **the
shield (91) in slot 3, the +1 Longsword (97) in slot 10**, specs ['long sword']. A psionicist (SeanBoy, slot 2): **the
game's club in slot 10**, and the Loader's gear gave a second club in the empty right hand ("SeanBoy starts with more
gear: Club (in hand), Armor, Armor"). START GAME, the ambush, HP 250, Computer Control (View Character's icons this
time: C on a member's turn opened View Character, 47,53 and 98,53). Cromwell, a long sword specialist like Halton:
**1 a round** (rounds 2-8, then down at round 8: two against four); SeanBoy 2 a round (two clubs):

```
Cromwell attacks Draxan#26 with Longsword +1 (1d8+1): d20 = 14, needs 8+ (65%), hits AC -5, target AC 1 -> HIT
    THAC0 14 base, +2 in bonuses, +3 mastery = 9
  Cromwell hits Draxan#26 for 8: 1d8 = [3] +1 weapon +3 mastery +1 STR 17
```

The control's fight was stopped (DOSBox killed by pid) at round 11, nothing saved: ravSG has no SAVE file.

**7. Memory.** No helper code: DSCLOG2.EXE 48064 bytes before and after, so the spec-pick log's figures hold
(upper memory free 108,064 bytes, the largest piece 107,920; conventional 88,816). The change is 7 bytes of the
patched program's data.

## Tests

`DSUN_WOTR=/tmp/playtest/rav python3 -m pytest -q tests`: 2758 passed, 90 skipped. `python3 -m unittest discover -s
tests`: 2566 tests OK (125 skipped).

## Open

- **The starting weapon of the first pick** (the port plan's item): not done. SL's way (weaponchoice.finish_new: the
  game's plain bone long sword made a plain weapon of the first kind, a two-handed one sending the shield to the
  pack, a bow to the missile slot with arrows) needs for the sequel a weapon of each kind from its own objects
  (ravlog's RAV_PLAIN has 13 kinds, none for the lotulis, double spear, trikal, two-handed sword, javelin, darts,
  short sword, bow or staff sling), a choice for the sequel's **+1** starting long swords (a fighter's and
  gladiator's 633, a thief's, a ranger's +0 603: a plain weapon in their place would be a step down; a +1 of the
  kind keeps the name question open), and the gladiator's two hands. The pass would run in ravlog's `_gear_pass`
  beside startgear.fill while DONE waits (GEAR_DONE), with no DSCLOG2 change.
- **An air cleric starts with no melee weapon**: the game's club goes to the pack (no wood for air), and the
  Loader's gear gives a sling but nothing in the empty right hand (an obsidian dagger is due by startgear's
  CLERIC_HAND_ORDER, as the module's notes say); not this change's (the club is refused in either hand, and
  startgear takes either free hand in the sequel), though not played in the control. Not looked into.
- The sphere's list on the creation panel didn't take a click on WATER here.

No new area: no water noted. ravSG thrown away after.
