# 2026-11-27: the port audit's rest in Wake of the Ravager (dice log lines, the lock rule, GAME-BUGS' fixes)

**Under test:** branch `claude/ravager-audit-rest` (on #229, with #218-#221 merged): the dice log's effect, PSP and
ability lines in the sequel; DSCLOG2's LOCK_SITE (site 241), GL_ARMOUR (site 242), AI_WALL (243), KREEN_CLAWS (244)
and PSP_SCORES; the Loader's data fixes
(shots_left, roster_delete, Slay Living's text, CHOOSE A SPELL's grid).

**Set-up:** `ravAR`, a throwaway copy of `$WORK/rav` (game.gog hard-linked, the rest copied, the roster and
DARKSAVE from __support/save, no saves). The DOSBox lock held by this session's holder throughout.

## Steps

1. `RAV_LOADER=1 RAV_MENU=1 RAV_STDOUT=1 RAV_CORE=normal sh ravstart.sh /tmp/playtest/ravAR`, the dice log
   `RAV=/tmp/playtest/ravAR RAV_NO_SAVES=1 ravdice.py 7000 /tmp/playtest/ar-dice.txt --numbers`. The pointer did not
   move at the title menu until a click in the window (`xdotool mousemove --window W 320 400 click 1`) captured
   the mouse; after that `ravclick.py` worked.
2. CREATE CHARACTERS (160,92). The first slot's right-click (70,56), ADD (110,69): the roster holds 4 (Clk'whrr,
   Meggyn, Zontorra, Borzak) in 10 rows, so DELETE with the list scrolled can't be tried without more characters.
3. NEW (110,57): a human fighter 7; FIGHTER (250,29) off, PRESERVER (255,45) on; DONE (272,182). **CHOOSE A SPELL,
   level 1: 17 icons in rows of six, filled row by row and centred** (6, 6, 5; [the screen](img/2026-11-27-ravager-choose-a-spell-grid.png)),
   not the game's five middle columns then a seventh on the right.

**Stopped here for the user's usage limit; resumed the same day** on a new throwaway copy `ravAR` (its saves
removed); the lock holder, Xvfb restarted by hand (it was gone).

4. A new game (the title menu clicked first; S; the dragon picture: Escape, then Return; 3, Return x4): Tyr's
   ambush. Computer Control on for all four (C, `ravclick.py 200 70 none` to capture the pointer, the four lower
   icons): COMPUTER CONTROL IS ON.
5. **The gladiator's armour** (GL_ARMOUR): Gerakis armoured (legs item 11 slot 6, chest item 12 slot 9),
   attacked twice: target AC 8, `ravaudit.py` gl_bare 0. `ravitems.py 3 --bare` (a test edit, never saved):
   the party won before any foe reached him. A second run (DOSBox restarted, a new game): bare from the fight's
   start, the foes' HP 300 (scratch `foehp.py`, a test edit): attacked at **AC 9, gl_bare 1, then 3**;
   `--dress`: attacked four times at **AC 8, gl_bare held at 3**. Works.
6. **The dice log's effect lines**: "Terrannus#1 gives Controlled to Draxan#26", "Thy'rokh#2 gives Paralyzed to
   Draxan#21: loses its turns, can't move, fails every saving throw", "Paralyzed ends on ?#21" (the "?" a
   `ravdice.py --numbers` slip, fixed: a creature gone by the end keeps its name), "Controlled ends on
   Draxan#26". **PSP lines**: the level ups' "Terrannus regains 26 PSP (31 -> 57)"; a test edit of Ar'Anda's
   PSP (-5) and STR (+1), put back: "Ar'Anda spends 5 PSP (96 -> 91)", "Ar'Anda's STR 18 -> 19", "regains 5 PSP
   (91 -> 96)", "STR 19 -> 18". Works.
7. Built the rest of the shared bugs (most PSP, monster walls, thri-kreen claws: DSCLOG2 rebuilt) and a third
   run (DOSBox restarted, a new game, no memory edit): **KREEN_CLAWS** counted on Thy'rokh's bite (kreen_cuts 2,
   then 4); **PSP_SCORES** at the level ups: Terrannus 28 (31 -> 59), Thy'rokh 28 (33 -> 61), Gerakis 28 (27 ->
   55), where the first two runs gave 26, 26, 34: the creation record's WIS 18 no longer stands in for each
   member's own (19, 19, 15). No wall cast (ai_walls 0).
8. Not seen: the last foes' blows and kills in each run's log (the summary "0 kills": known, the sequel's log),
   an archer's pointer, the roster's DELETE scrolled (needs more than 10 characters), Slay Living's text, a lock
   (one open-locks check found in the sequel's scripts, GPL 9's grate; where it is not known), a computer's wall.

**Water**: no new area (Tyr's street, as before).

DOSBox, the dice log and the lock holder stopped by pid; ravAR deleted.
