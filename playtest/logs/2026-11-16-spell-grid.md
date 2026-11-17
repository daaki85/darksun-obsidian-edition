# 2026-11-16: CHOOSE A SPELL's grid, and no gear on the creation screen's stand-in

## The unchanged game
- DOSBox with a config whose autoexec runs the game folder's own DSUN.EXE (no DSCLOG, no Loader).
  Intro (Escape x3), CREATE CHARACTERS, NEW, a human preserver, DONE: **no CHOOSE A SPELL** (the
  picks at creation are the mod's); VIEW CHARACTER at once.
- fountain-user loaded there; Lex's XP 4,999 (preserver 3 at 5,000); the ambush; Jenna killed the
  Templar (1 HP) with the attack pointer. No level-up before the party, its turns passed, lost.
- The window read from the game's RESOURCE.GFF: WIND 17500, places APFM 2BCDh-2BE1h, the first 15
  at x 47-123 (five columns, 19 apart), y 24/44/64; 2BDCh-2BDEh at x 142; 2BDFh-2BE1h at x 28. The
  Loader's copy was the same. So past 15 spells the right-hand column fills and the left stays
  empty: the game's own 4th level has 16 wizard spells; the 1st, with the new spells, 18.

## The fix, in the game — PASS
- `spellgrid.py`: the first 18 places six to a row, 19 apart, row by row, x 38-133 (centred as the
  seven columns were). dos/RESOURCE.GFF after start.sh: (38,24), (57,24)... buildcheck OK.
- A Spellarcher "Gridcheck": the grid centred (about 22 px of parchment left, 20 right; it was 31 and
  12), row by row: Armor, Burning Hands, Charm Person, Chill Touch, Color Spray, Enlarge on the first
  row. A click at (189,91), the 11th place, took **Shocking Grasp**; then Armor, Burning Hands,
  Charm Person at (113,71).

## No gear on the stand-in — PASS
- Gridcheck renamed (typed slowly) and left 25 s on the creation screen with SPELLARCH marked: **no
  "starts with" lines** until after DONE; then once: the plain bow, armour and shield left behind,
  the Fine Bow, 24 shocking arrows in the quiver, the short sword. carried.py: Shocking Arrows 24,
  Short Sword, Fine Bow.
