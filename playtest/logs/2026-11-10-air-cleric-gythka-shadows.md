# 2026-11-10: air clerics' cahulaks, the gythka's large dice, the greater shadows, the Loader's Help

The build under test is commit b9b060c plus the Help status change. `buildcheck.py`: OK. Memory edits only; no game was saved.

## The Loader's window (Xvfb :57, `python3.12 -m dsloader view`)

**Help** (top right) opens `player-guide.html` with `webbrowser.open`.
- Here `gio` answered and then found no program for text/html ("Failed to find default application"), so nothing opened and the status line didn't change.
- The status line now always names the guide ("The player's guide, opening in your browser: ...").
- With no game connected, the window's retry rewrites the line a few seconds later.

**The renamed Options texts** in Graphics and Controls all read with the docs' names: "What the party wears, drawn on their figures", "See-through figures", "Choosing an enemy", "Scrolling the map", "The view in fights", "The pointer in scenes", "Where the pointer starts", "Spells on the Effects screen".

## From `pens-after-scar`

**The gythka.** I, Gerakis (20,20), and a right-click on his left hand (173,92). The box: "2 handed Bone Gythka / 2D4-1/1D10-1 / Hit -1": the large dice are now 1d10, with bone's -1 on both (`img/2026-11-10-gythka-box.png`).

**An air cleric and the cahulaks.**
- Cermak (member 2) was made a plain air cleric in memory: class 1 at sheet +21h, level 5, flags 1. The script was `/tmp/playtest/cleric.py`; the sheet comes from the far pointer DS:1661h + creature +4 x 47h.
- His staff (item 22, right hand) was made plain Cahulaks (type 21) with `setitem.py`; the panel then read "Cahulaks 2x1D6+6".
- In the inventory, a click took them out of his hand ("BONE CAHULAKS" on the pointer), and a second click put them back: accepted (`img/2026-11-10-air-cleric-cahulaks.png`).
- As a fire cleric (class 3, flags 4), the same put-back gave "CANNOT USE THIS ITEM" (`img/2026-11-10-fire-cleric-refused.png`).
- Made an air cleric again, the cahulaks went back into his hand.

## From `fountain-user` (Pehtucl's ambush)

The fight starts once Pehtucl's speech box is clicked; until then combatants 24, 40, 42, 45 and 46 don't exist and `foeset.py` stops on them.

**The greater shadows.**
- Setup:
  - Lex's item 43 made plain Cahulaks;
  - every foe held (`foeset.py C eff=34`);
  - every foe's creature name set to "Shadow King" in memory (creature record +28h, 16 bytes: `/tmp/playtest/rename.py`).
- `cahulaks.big_table` then marked combatants 17-47.
- Lex's Tab + Return: two hits on the "Shadow King" (the 41-HP Templar), and no tangle line.
- **Control:** the Templar's name put back. The next round's first hit has "Lex's cahulaks tangle Templar? Save against petrification: d20 = 8, needs 10+ -> tangled".
