# 2026-11-24: the sequel's 48h sheet played

**Under test:** Wake of the Ravager run the Loader's way (RAV_LOADER=1, DSUNLOG2.EXE and DSCLOG2.EXE of
build 2d34add, branch claude/ravager-sheet-room), the character sheet 48h bytes. Copies: `rav48` (the
install, its roster and SAVE01 widened by ravstart.sh), `ravG48` (the install with fountain-user's party
transferred again by the current Loader: 48h sheets, the specs at +42h..+44h).

## Steps

Sheet bytes were read in guest memory with a scratch reader (the table at far DS:19C5h, 17 x 48h; the
creation screen's sheet at far DS:1429h). The copies' rosters and saves were read with dsloader's gff and
dataitems.

1. **ravstart.sh on rav48 (RAV_LOADER=1, RAV_MENU=1)** widened CHARSAVE.GFF and SAVE01.SAV (NAME.42H
   backups written): every CHAR sheet record 48h with +42h..+47h 0. SAVE 6 went from 462h to 4C8h.
2. **A new character (check 1).** On CREATE CHARACTERS the creation sheet pointer (DS:1429h) was table
   slot 0 (71EC4h). I wrote A1..A6 into slot 0's +42h..+47h, then right-clicked the slot and chose NEW.
   After NEW, slot 0 held the new sheet (human fighter 7) with +42h..+47h **00 00 00 00 00 00**, so
   DSCLOG2's NEW_SHEET cleared the six bytes. DS:1429h then pointed at the template (360h:29h = 3FF39h);
   its "+42h..+47h" are the creature record after it (41 00 1E ...), as the study said. DONE gave
   Deestan on View Character (65/65 HP, THAC0 14). No crash on leaving the creation screen.
3. **Editing an existing character (check 2).** I wrote 01 00 C2 (a transferred-style spec) into slot
   0's +42h..+44h, then chose EDIT, STR 17 to 18, and DONE. Slot 0 then had STR 18 (DAM 2x1D8+5) and
   +42h..+44h still **01 00 C2**. The edit's 42h copy back leaves the tail alone. The roster on disk
   kept it too: CHAR 35, Deestan, has 01 00 C2 at +42h. That was my test value, written by the roster
   save on DONE, on the scratch copy only.
4. **ADD from the roster, native characters (check 3).** Clk'whrr went into slot 1, Meggyn into slot
   2 and Zontorra into slot 3, each 48h-aligned (race, classes and levels as the roster's CHAR 36-38,
   +42h..+47h 0), with the next slot still empty. The View Character screen was right for each
   (Clk'whrr druid/psionic 6/6 54 HP, Zontorra ranger/thief 6/6).
5. **A new game with that party.** S on the title menu gave the opening talk ("Hurry! You must come with
   me to the Veiled Alliance!"). I answered 1 ("What did you see?") and got her next page, then Return,
   and the Draxans' ambush began (check 7, a talk).
6. **The ambush (check 6).** All four were under Computer Control, with `ravdice.py --numbers`
   (s48-f1.txt). The Draxans' sheets (OBJEX2 RDFF, widened by `objects_fixed`) read right: STR 20,
   "THAC0 13 base", 2d4 stone lotulis +8 STR. Seven rounds, then YOUR PARTY HAS BEEN DEFEATED (the
   made-up party is weaker than the opening one), then the title menu. No crash.
7. **An old save widened (check 4).** LOAD SAVED GAME, AFTER AMBUSH (rav48's SAVE01.SAV, 42h on disk
   before, widened). After the load, a picture (the dragon's orb) waits for a click, then Tyr's street
   with Thy'rokh. All 17 sheets were aligned (slot 9 a race-9 kind, 10-16 the street's people). The
   dice log gave the opening party their ages at once: +41h 0Ah/06h/01h/10h and the starting roll
   packed at +44h (CCh, C8h, C0h, D4h). It printed "Ar'Anda is 24 (an elf: 15 + 3d4 = [4 + 2 + 3])",
   and the roll 6 = 9 - 3, as packed. Terrannus 20 (roll 4) and Gerakis 35 (roll 10) matched too.
8. **A save written and loaded (check 4).** F1, slot 2, "SHEET 48", SAVE: SAVE02.SAV had SAVE 6 of
   **4C8h**, the four sheets with their ages and rolls. F2, slot 2, LOAD (the dragon picture, then a
   click): all 17 sheets in memory matched the file byte for byte. The arrow keys walked Thy'rokh.
   The camera scrolls while the pointer rests at the window's edge, which is why the save screen
   showed another part of Tyr behind it; H brings the view back.

## A bug: the TOC the Loader writes (found at step 8, fixed)

After the session above, rav48's **CHARSAVE.GFF no longer parsed**: "Chunk 'CHAR' 53 runs past the end of
the file". Its TOC gave CHAR 53 a length of **101E1h**, but the chunk's records end at 1E1h, and Deestan's
new CHAR 35 was appended right after them. Every other CHAR length was right.

- **The game's own TOC** (the install's roster, every SL CHARSAVE in `saves/`) is the type table, then a
  word count of free holes, then 8 bytes for each hole (offset, length). The TOC's second dword is the
  count's place (the type table's end), and the TOC's length is that place + 2 + 8 x holes. The install's
  roster has 7 holes at 4DAh.
- **`icons.with_chunks`** (the writer behind `ravager.widen_files`, `narrow`, the party transfer's roster,
  and worldgear and kalzith on SL's files) wrote the type table and set the second dword to `len(toc) -
  2` "as the game's own", but **never wrote the count**. So that dword pointed at the last two bytes of
  the type table: the high word of the last entry's length (CHAR 53's).
- The game's next write of the file (DONE on the creation screen saves the roster) appended CHAR 35,
  kept the dword and **wrote its free count (1) there**. CHAR 53's length became 1E1h + 10000h. A game
  that reads CHAR 53 with its own length (-1) would read 64K more.
- **Older than the 48h build**: ravG's and ravG48's rosters from the transfer had the same short TOC (the
  four transferred, 2026-11-22 on). The widening now runs it on every player's roster and save, and on
  DARKRUN.GFF, which the game writes as it plays (rav48's held 48h sheets by the end, and `narrow` changed
  it).
- **Fixed** (`claude/ravager-sheet-room`): `with_chunks` now ends the TOC with a count of 0 (the holes
  before aren't carried over), so the second dword is the count's place as in the game's own files.
  There is a test, `tests/test_icons.py` `test_free_list_count`: the count's place is the type table's
  end, and a game-style write of the count there leaves every length right. It fails without the fix.
  The whole suite passes (2559). The transfer into ravG48 was made again with the fix, and the narrowed
  files below have the count (TOC length = second dword + 2).
- **A file already written by the old writer and then by the game stays damaged**: the Loader doesn't
  repair it. rav48's was repaired by hand (CHAR 53's high word back to 0, the count 0 with it;
  `CHARSAVE.GFF.damaged` kept). The 42H/48H backups are the game's own or the old writer's, so a
  player's earlier transfer roster that the game has since written may hold one bad length (the last
  type's last entry).

## Steps, continued

9. **ravG48: the transferred party (checks 3 and 8).** I made a fresh copy of the install and ran the
   transfer again (`python -m dsloader.ravtransfer saves/fountain-user/SAVE01.SAV ravG48 inst dos`, with
   the fixed writer). The roster's four were 48h with the specs packed at +42h..+44h and the age at +41h:
   - Lex: 0E 00 C8 (bow, roll 4), age 07 (21)
   - Seneca: 04 00 D2 (short sword, roll 9), age 0Dh (37)
   - Ester: 01 00 C6 (long sword, roll 3), age 07 (21)
   - Jenna: 01 00 C2 (long sword, roll 1), age 03 (17)

   These are SL's own bytes (SAVE 6 of the save, +14h..+17h). The install's CHAR 36-39 were still 42h
   and were widened at the start. ADDing the four (ravGgo's clicks) put them in slots 0-3 with those
   bytes in memory, and View Character was right (Jenna ranger 3, 24/24 HP, THAC0 18).
10. **The dice log on them (check 8).** Read through `ravlog.apply_layout()` (SHEET_SIZE 48h, SPEC_SLOTS
    42h, SHEET_AGE 41h): `game.spec_kinds` gave bow / short sword / long sword / long sword,
    `game.sheet_roll` 4 / 9 / 3 / 1, and `aging.age_of` 21 / 37 / 21 / 17, the transfer's figures. **No
    attack shows a specialization bonus, and none can yet**: weapon specialization isn't a rule the
    sequel has (`game.RULE_SPECIALIZE` isn't in `ravager.RULES_PORTED`, and DSCLOG2 says "the sequel has
    no weapon specs"). Ester's and Jenna's long sword attacks showed "+1 in bonuses" (STR or the
    weapon), nothing named "specialized". The 48h build gives the specs a place and the dice log reads
    them; the rule is still to port.
11. **The ambush with them (check 6).** Under Computer Control, with the dice log (s48-f2.txt), the four
    fought the Draxans and lost, as in the earlier runs ("YOUR PARTY HAS BEEN DEFEATED"). No quit.
12. **A level up (check 5)**, on rav48's after-ambush save. Ar'anda's preserver level and best level
    (sheet +1Eh, +39h) were made 5 in memory, a test edit, never saved. I walked to Tyr's thieves (Up
    8, Right 40) and got a second talk ("Hey, sewer-scum! Give me your money, now!", four answers;
    answer 2), then fought under Computer Control. Gerakis's Computer Control click hadn't taken (his
    turn waited 2 minutes) and a second click on USE (98,113) did. In round 3 came "Ar'Anda's 6th
    Preserver level: hit points d4 = 2, +2 CON 17, into the total shared by 3 classes" and CHOOSE A
    SPELL, Ar'anda. Her sheet then had level 6 and best level 6, XP 45,082, and +41h..+47h **06 00 00 C4
    00 00 00** (the age and roll the dice log had given her at the load, kept). Then EXIT, EXIT on
    "YOU HAVEN'T CHOSEN", and the thieves won (all four dead). DOSBox was stopped without a save.
13. **narrow, then the plain game (check 9).** On a copy of rav48 (ravN), `python -m dsloader.ravager
    narrow` changed CHARSAVE.GFF, DARKRUN.GFF, SAVE01.SAV and SAVE02.SAV (NAME.48H backups): roster
    sheets 42h, SAVE 6 462h, the TOCs ending with the count. ravstart.sh without RAV_LOADER runs
    `DSUN -W0 -L`, the game itself. Its ADD list showed Deestan, Clk'whrr, Meggyn, Zontorra and Borzak.
    ADD took Deestan (65/65 HP) and Clk'whrr, at 42h in memory (slot 1 thri-kreen 7/12 6/6). LOAD SAVED
    GAME showed AFTER AMBUSH and SHEET 48. SHEET 48 loaded, its 42h sheets in place (the ages kept at
    +41h), the street's dead Draxans as saved. F2, AFTER AMBUSH loaded too, and Thy'rokh walked.

## Side notes

- The dice log's summary in the sequel says "0 kills" in every fight, and "took 0" in some (the ambush,
  where the party fell; the thieves' fight, where Ar'anda lost 2). The 42h runs of earlier days show the
  same (bs-dice.txt and others): a tally gap of the dice log in the sequel, not the sheet.
- After a load, the sequel shows a picture (the dragon's orb, a progress bar under it) that waits for a
  click.
- Water: no new area (Tyr's street and the opening only).

## Result

| Check | Result |
|---|---|
| 1. New character: +42h..+47h 0, leaving the screen | **Passed** (A1..A6 put in the slot were cleared by NEW) |
| 2. Edit | **Passed** (+42h..+44h kept, the change taken) |
| 3. ADD native and transferred | **Passed** (aligned, specs in memory) |
| 4. Save and load; an old save widened | **Passed** (SAVE 6 4C8h written and read back; the widened old save loaded) |
| 5. Level up | **Passed** (preserver 5 to 6, CHOOSE A SPELL, the tail kept) |
| 6. A fight | **Passed** (three fights, the Draxans' and thieves' sheets right, no quit) |
| 7. A talk | **Passed** (the opening talk twice, the thieves' talk) |
| 8. Dice log reads specs and age | **Passed for reading**; no spec bonus shown, because the rule isn't ported to the sequel |
| 9. narrow, plain game | **Passed** (roster ADD and both saves in the game itself) |
| Bug | `icons.with_chunks` TOC without the free count: the game then corrupted the last chunk's length; **fixed** with a test |
