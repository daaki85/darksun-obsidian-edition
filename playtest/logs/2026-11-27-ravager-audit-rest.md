# 2026-11-27: the port audit's rest in Wake of the Ravager (dice log lines, the lock rule, GAME-BUGS' fixes)

**Under test:** branch `claude/ravager-audit-rest` (on #229, with #218-#221 merged): the dice log's effect, PSP and
ability lines in the sequel; DSCLOG2's LOCK_SITE (site 241) and GL_ARMOUR (site 242); the Loader's data fixes
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

**WIP: stopped here (the user's usage limit).** Not played yet: the effect, PSP and ability lines (the Tyr
ambush with Computer Control), the gladiator's AC with and without armour (GL_ARMOUR's `gl_bare`, header +2118),
an archer's pointer, the roster's DELETE with a scrolled list (needs more than 10 characters), Slay Living's text
(the spell's description on the USE screen), a lock (none found in the sequel yet). DOSBox, the dice log and the
lock holder stopped by pid; ravAR deleted.
