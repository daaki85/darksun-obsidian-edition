# 2026-11-08: the creation screen's least scores, in DOSBox

Under test: gamepatch `least_scores` (DSUN.EXE 67399h rewritten: the manual's minimums per class),
commit 87491c5 on obsidian-edition, and the dice log's creation lines that go with it.

## Steps
1. start.sh; the game runs dos/DSUNLOG.EXE, whose 104 bytes at 67399h are least_scores.asm's (checked).
2. Main menu: CREATE CHARACTERS (165,92) opens VIEW CHARACTER; right-click an empty slot (64,52):
   NEW / ADD / CANCEL; NEW (110,57) opens the creation screen (a human fighter).
3. A score's square (x 6; STR y 140, DEX 146, CON 154, INT 161, WIS 167, CHA 174): right-click
   lowers by 1, left-click raises; the game keeps it between the least (DS:4994h, which 67399h
   just wrote for that score) and the most. A class: click its name (x 250; cleric 13, druid 21,
   fighter 29, gladiator 37, preserver 45, psionicist 53, ranger 61, thief 69); a human's old class
   must be clicked off first.
4. The least for each score, read after a lowering click (DS:4994h), every class:
   - fighter STR 9 (STR lowered click by click 17 -> 9, then round: the game's own stopped at 17), the rest 3
   - gladiator STR 13, DEX 12, CON 15, WIS 3, CHA 3
   - druid WIS 12, CHA 15, the rest 3
   - psionicist CON 11, INT 12, WIS 15, the rest 3
   - ranger STR 13, DEX 13, CON 14, WIS 14, CHA 3
   - cleric WIS 9; preserver INT 9; thief DEX 9; the rest 3
   All the manual's.
5. Multiclass, set in memory (race and the creation sheet's classes): dwarf fighter/thief STR 9,
   DEX 9, the rest 3; elf ranger/cleric STR 13, DEX 13, CON 14, WIS 14; elf
   fighter/druid/psionicist STR 9, CON 11, INT 12, WIS 15, CHA 15. The highest of the classes'.
6. Found: on the creation screen the party's first slot carries the character's name and a
   placeholder sheet (XP 4000, every score 10) whose XP moves with the class, and the tracker
   logged "XP: SeanBoy +1500". The prime requisite bonus must not run there.
7. DS:119Ch is null in a game loaded first, but once the creation screen has been up it stays
   set (on the party's first sheet, DS:11A0h on the creature table), in play too: "set" can't
   tell the screen. On the screen the record is straight after the sheet (3A7A8h, 3A7EFh), and
   `game.creating()` tests that. Fixed in the tracker, with a test.
8. The prime requisite XP bonus, in a game (`pens-after-arena`), with an award of 600 written as
   the game's routine gives it (`award.py 600`: each sheet's XP + 600 / its classes):
   `XP: Gerakis +660 (+60 for Gladiator, STR 24), K'ratchek +213 (+13 for Fighter, STR 19;
   Psionicist, CON 19 WIS 19), Cermak +660 (+60 for Preserver, INT 18), Cilla +220 (+20 for
   Preserver, INT 18; Druid, WIS 18 CHA 16; Thief, DEX 21)`. K'ratchek's druid (CHA 15) has none,
   so he gets two classes' 10% of three. The sheets held the new XP and nothing was added again.
9. The same after the creation screen and a save loaded in the same run (pointers left set):
   `creating` False, the same line. A class change on the creation screen logged no XP.

Not done: the watchdog wasn't started (no fights, every step a short command with a timeout).
The XP was written in memory only; nothing was saved.

## Result
The least scores are the manual's for every class and multiclass set tried; the bonus is given
once, with the right amounts, and not on the creation screen.
