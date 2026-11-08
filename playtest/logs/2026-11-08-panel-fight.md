# The combat log panel in a fight, after the drawing savings (2026-11-08)

Under test: DSCLOG with the drawing savings (the panel put back only when the redrawn rectangle
overlaps it). Save: fountain-user (Pehtucl's ambush). Cycles: the new default, 35000.

## Steps

1. `loadsave.sh fountain-user` (DOSBox at 35000 cycles, the new default: `dosbox_dicelog.conf`
   said `cycles=fixed 35000`); clicks on the speech box (160,20) until `fight_on 1`: Round 1, ten
   combatants (Pehtucl the Templar, 4 Arena Guards, a Guard).
2. The panel: L shows it (saved as expanded, detail). The lines are in the new 7 px font.
3. The expanded panel covers the screen's right half from y 68: Ester's figure (144,148) was
   under it, so passto.sh's clicks went to the panel. `scroll.py -96 0` put the party left of it,
   the guards under and round it.
4. passto.sh then pressed E with no END menu (its "menu opened" test counts changed pixels, and
   the panel's own new lines changed enough): the Effects screen. Stopped it (kill by pid),
   Escape.
5. `fightout.sh` to the end (11 party turns, 35 attacks), a window grab every 1.2 s (80).

## Seen

- Every grab: the panel whole, its frame, header, filters and lines unbroken, nothing of the
  map drawn over it while guards walked and fought under and beside it; the 4-pixel strip at its
  right (x 316-319) showed the figures behind it, redrawn as they moved (logs/img
  2026-11-08-panel-fight.png, every fifth grab; -zoom.png, the panel at 4x). The only things over
  it were the mouse pointer and the game's own END menu and Effects screen.
- The panel's text followed the fight (each turn, attack, HP and XP line, then the clock line
  `Day 1, 00:55` after the fight).
- Dust behind running figures, shadows under them: as before.
