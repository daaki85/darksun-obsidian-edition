# 2026-11-25: XP held at the cap

Under test: the branch `claude/sl-xp-freeze`: the Loader's party tracker (`tracker.py`,
`hold_at_cap`) holds a party member's XP at its share of the XP cap (`game.xp_share`, the twin of
DSCLOG's `LEVEL_ROOM`). DSCLOG unchanged; `buildcheck.py` OK in both runs.

A private game (the shared DOSBox was another agent's, its lock held and another waiting): a
scratch copy of the kit and of `inst` in `/tmp/playtest-xpcap`, its `env.sh` and `paths.py` on
`:56`, DOSBox copied as `dbxp` (`SDL_VIDEO_X11_WMCLASS=dosbox`), its own `start.sh` writing
`dsun.pid` and `dice.pid` and starting the dice log as `python3 -um dsloader dicelog --pid PID`,
with `autosave` and `quick_save` false; the kit's `obsidian-edition` a link to the tree under test
(the control: a link to a detached worktree of `origin/obsidian-edition`). Everything stopped by its
pid at the end. No save made.

## With the hold (the branch)

1. `loadsave.sh fountain-user`: the window 320x240, the ambush's speech up. The party: Lex
   (half-elf fighter/preserver, 3/2, 4,077 XP), Jenna (human water ranger, 3, 7,173), Ester (elf
   fighter/cleric), Seneca (halfling thief/fighter).
2. Memory edits for a test: `sheetedit.py 1 level0=10`, `sheetedit.py 0 level0=9 level1=10`
   (the top levels under their shares), then Jenna's XP to 749,500 and Lex's to 374,700. The dice
   log: `XP: Lex +370922 (+299 for Fighter, STR 20; Preserver, INT 20, 36,763 of it held at the
   cap), Jenna +742826 (+499 for Ranger, STR 20 DEX 20 WIS 20, 73,733 of it held at the cap)`: the
   prime requisite bonus on the edit's "gain" stopped at the shares, 374,999 and 749,999.
3. Their XP set to 749,900 and 374,900 (under the shares), the speech clicked away (160,30): the
   fight on. `fightout.sh 120`: DONE after 11 passes.
4. Each kill: the hold line, then the XP line without them. The Templar (1,400): `Lex's XP held at
   the cap: 374,999, 749,999 shared by 2 classes (76 not counted)`, `Jenna's XP held at the cap:
   749,999 (251 not counted)`, `XP: Ester +192 (...), Seneca +192 (...)`. Each Arena Guard (120):
   `(15 not counted)` and `(30 not counted)`; the Guard (1,000): 125 and 250. (Their XP line left
   them out: the edit's drop of 99 and 100, unlogged yet, and the hold back to the share net 0.)
5. After the fight, from memory: Lex 374,999 (9/10), Jenna 749,999 (10), Ester 3,723, Seneca 3,970.
6. View Character (I, then 168,187; Jenna's portrait 112,55): `EXP:374999` for Lex and
   `EXP:749999` for Jenna, no next level in brackets ([Lex](img/2026-11-25-xp-held-lex.png),
   [Jenna](img/2026-11-25-xp-held-jenna.png)).

## The control (the old Loader)

7. The same save, edits and fight with the Loader of `origin/obsidian-edition`: the edit's line
   `XP: Lex +407685 (+37062 ...), Jenna +816559 (+74232 ...)`, the kills' XP lines with Lex and
   Jenna in them (`Lex +16`, `Jenna +33`, ...). After it: Lex 375,293 and Jenna 750,690, past their
   shares, their levels still 9/10 and 10 (`LEVEL_ROOM` holding the levels alone).

## Not seen

- A human who changed class in the game (the unit tests and the emulator's `PROBE_LEVEL` check
  cover the share), a script's award (the hold is the same look whatever gave the XP).

## Learned

- `fountain-user`: a click on the speech (160,30) starts the ambush's fight.
- View Character's portraits: Lex (65,55), Jenna (112,55).
- Water: no new area (the fountain is in ROUTE.md's list).
