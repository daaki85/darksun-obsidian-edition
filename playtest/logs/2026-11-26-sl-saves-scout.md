# Shattered Lands: saves past 9th level, the Military Scout's missile bonus (2026-11-26)

Under test (branch `claude/sl-saves-scout-fixes`):
1. DSCLOG's SAVE_BASE (site NS_IMAGE + 123 at 878F7h, RULE_HI_TABLES): a level up's saves the Player's
   Handbook's (Table 60) by class group and level, where the game held them at its table's last row.
2. KIT_TO_HIT: a Military Scout's +1 to hit with a missile under the open sky for the bow, sling and staff
   sling only, not the javelin or darts.

Build: DSCLOG.EXE rebuilt from source (nasm 2.16.01). Save: `fountain-user`. Settings: autosave and
quick_save off (memory edits below; nothing saved).

## Steps

### Saves, the fix (RULE_HI_TABLES on: rules_hi 65343)

1. `loadsave.sh fountain-user`; window 320x240; `buildcheck.py` OK (127 vectors at their handlers).
2. In memory (no save after), each member one level and a few XP short of a level up, kits cleared:
   Lex (half-elf) fighter 9, XP 499,990; Jenna (human) cleric 10, 674,990; Ester (elf) thief 12,
   659,990; Seneca (halfling, CON 19) fighter 8 / thief 11, XP 499,980 (the Loader held it at the
   share, 374,999). (The dice log's tracker took the edits for an award and added the prime
   requisites' 10%: harmless here.)
3. Pehtucl's speech clicked away, `fightout.sh`: DONE after 15 passes. The level ups came in the
   fight's turns ("Lex is now a 10th level Fighter", "Message: Jenna is 11th level Cleric", ...).
4. The sheets' saves (+37h, PPD/RSW/PP/BW/SP) after the level ups:

| Member | Class, level | Saves seen | Handbook (tables.rav_saves) | The game's own would be |
|---|---|---|---|---|
| Lex | fighter 10 | 8/10/9/9/11 | 8/10/9/9/11 | 11/11/11/13/11 |
| Jenna | cleric 11 | 6/10/9/12/11 | 6/10/9/12/11 | 8/10/9/12/11 |
| Ester | thief 13 | 10/8/9/13/9 | 10/8/9/13/9 | 10/10/9/13/10 |
| Seneca | fighter 9 / thief 11, halfling CON 19 | 3/5/4/4/6 | best of warrior 9 less the game's CON bonus 5 (3/5/4/4/6) and rogue 11 (11/10/10/14/11) | 6/6/6/8/7 |

   The inventory screen's panel for Lex: PPD 6, RSW 9, PP 8, BW 8, SP 10 (the sheet's, less his Ring of
   Protection's 1, and CON 19's 1 on PPD).

### Saves, the control (RULE_HI_TABLES off: `setmem.py ruleshi=-8`, rules_hi 65335)

5. `loadsave.sh fountain-user` again, the bit cleared, the same edits (Seneca's XP 374,990), the
   speech clicked away, `fightout.sh`: DONE after 13. The same four level ups; rules_hi still 65335
   after the fight. The saves: the game's own, as the old code works them out:

| Member | Class, level | Saves seen (rule off) | With the rule (above) |
|---|---|---|---|
| Lex | fighter 10 | 11/11/11/13/11 | 8/10/9/9/11 |
| Jenna | cleric 11 | 8/10/9/12/11 | 6/10/9/12/11 |
| Ester | thief 13 | 10/10/9/13/10 | 10/8/9/13/9 |
| Seneca | fighter 9 / thief 11 | 6/6/6/8/7 | 3/5/4/4/6 |

   Every save as predicted from the game's table (420h:6Ch) for the control and from the Player's
   Handbook's Table 60 for the fix. Levels past the XP cap's (a fighter's 10th, a cleric's 11th, a
   thief's 13th here) and every group at 1-25 are checked in the emulator (`test_slsaves`).

### The Military Scout's missile bonus

6. `loadsave.sh fountain-user` (the rules as set: kits on). Lex (a half-elf) made a fighter 5 / thief 5
   Military Scout in memory (classes 9, 17, kit byte 2). The slave pens are under a roof, so the dice
   log was run with them counted as under the open sky (a test-only wrapper: `stealth.OUTDOORS` plus
   region 29h); DSCLOG's KIT_OUTDOORS byte (header +350) then read 1111b, and Lex's initiative line
   showed "+2 Military Scout under the open sky": the kit and the sky are on.
7. Lex's bow (item 36) and short sword (43) made the Loader's javelin (`worldgear.weapon(JAVELIN)`, type
   152) in memory; on his turn the attack pointer on the Templar beside him threw it:
   `Lex attacks Templar unseen with Obsidian Javelin (1d6): d20 = 20, needs 7+ (70%), hits AC -8,
   target AC 5 -> HIT` / `THAC0 18, +2 unseen, +4 DEX = 12`. The game's THAC0 for the throw is 12
   (7 needed against AC 5) and the breakdown adds up to it with no Scout part: **no +1 for the
   javelin**. (With the old DSCLOG the throw's THAC0 is 11: its emulator test, `test_scout_and_path_finder`
   on the old DSCLOG.EXE, gives the javelin, the metal javelin and the darts +1 each.)
8. Not got in play: the darts (the record made in memory wasn't taken as a missile weapon: "NO PATH
   FROM HERE" on every try) and a bow shot (the fight's turns stalled on Ester's Effects screen, a
   turn with nothing in reach, before Lex had a clean shot). The bow, sling and staff sling keep the
   +1 and the javelin, metal javelin and darts get none in the emulator on the built DSCLOG.EXE
   (`test_scout_and_path_finder`).
9. DOSBox, the dice log and the watchdog stopped by pid; nothing saved.

## Psionicists' saves (Dark Sun's Table 8), Shattered Lands

The shared DOSBox was busy (other agents' Ravager tests in the lock's queue), so this ran in a second game
beside it: the kit copied to `/tmp/playtest/slsv` with this tree's `obsidian-edition` linked, display `:61`,
DOSBox copied as `dbsv` (`SDL_VIDEO_X11_WMCLASS=dosbox`), its own `inst` copy, dice log by pid.

10. `loadsave.sh fountain-user`, `buildcheck.py` OK. In memory: Seneca (halfling) a psionicist 10 with
    599,990 XP; Ester (elf) psionicist 8 / thief 10 with 199,990 (the share). Pehtucl's speech, `fightout.sh`;
    each PICK A PSIONIC POWER pop-up answered by a click on a red power (158,62 / 177,62; FINISHED at 112,139
    turns the discipline page). Level ups: Ester psionicist 9th, then thief 11th; Seneca psionicist 11th.
11. Control: the same with `setmem.py ruleshi=-8`.

| Member | Classes, levels | Saves, the fix | Expected (Table 8 / Table 60, the best of each) | Saves, the control (rule off) |
|---|---|---|---|---|
| Seneca | psionicist 11 | 11/11/8/13/12 | psionicist 9-12: 11/11/8/13/12 | 11/10/10/14/10 (the thief's formula) |
| Ester | psionicist 9 / thief 11 | 11/10/8/13/11 | psionicist 11/11/8/13/12, thief 11/10/10/14/11 | 11/10/10/14/10 |

    (Ester read 11/10/8/13/11 after her psionicist 9th too, the thief then at 10th: the same bands.)
12. The second game's DOSBox and dice log stopped by pid; nothing saved.

## Psionicists' saves, Wake of the Ravager (DSCLOG2's SAVE_BASE, site 116)

The same second kit (`:61`, DOSBox `dbsv`), `ravstart.sh` with `RAV_LOADER=1`, `ravdice.py` attached, the
opening talk to the Draxans' ambush (a throwaway copy of the game). DSCLOG2 in memory checked: its
`save_bands` (198 bytes, 33 bands) are the built DSCLOG2.EXE's, the last six the psionicists'.

13. In memory (never saved): Ar'Anda (member 0, race 3) psionicist 21 with 3,598,000 XP; Terrannus
    (member 1, race 3) psionicist 9 / thief 13 with 398,500; Gerakis (member 3, race 5) psionicist 12 with
    998,000 (`ravlevel.py set`); the Draxans' HP 1 (`ravlevel.py foes 1`); Computer Control for all four
    (C, the small icons at 47,53 / 98,53 / 47,113 / 98,113). The fight's 4,000 XP and the box's 10,000; the
    boxes clicked through (160,100): "Ar'Anda is 22nd level Psionic", "Terrannus gains a level" (psionicist
    10th), "Gerakis is 13th level Psionic". No PICK A POWER pop-up came in the sequel.
14. Control: DOSBox stopped by pid, the same start with `RAV_SKIP=save_table` (the copy's DSUN.EXE has the
    game's bytes, 268A876C00, at the site), the same edits and fight.

| Member | Classes, levels | Saves, the fix | Table 8 / Table 60 | Saves, the control |
|---|---|---|---|---|
| Ar'Anda | psionicist 22 | 8/5/5/9/7 | psionicist 21+: 8/5/5/9/7 | 8/10/7/11/10 |
| Gerakis | psionicist 13 | 10/9/7/12/11 | psionicist 13-16: 10/9/7/12/11 | 10/10/9/13/10 |
| Terrannus | psionicist 10 / thief 13 | 10/8/8/13/9 | psionicist 11/11/8/13/12, thief 13-16 10/8/9/13/9: the best 10/8/8/13/9 | 10/10/9/13/10 |

    DSCLOG2's save_count 25 with the fix, 0 in the control. (Thy'rokh's druid 7th: 7/11/10/13/12 with the
    fix, the priests' Table 60.)
15. Both DOSBoxes, the dice logs and the `:61` Xvfb stopped by pid; nothing saved. No new area (no water to note).
