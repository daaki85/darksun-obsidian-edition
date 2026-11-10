# 2026-11-10: the outstanding DOSBox checks

The build under test is commit e74d3f7. It has:
- PIC_FAIL;
- the helpless state in each ring entry (+188);
- the shortened spell texts.

`buildcheck.py`: OK after each load. Memory edits only; no game was saved.

## From `fountain-user` (Pehtucl's ambush, a fight from the start)

### KEEP's resize (memaudit)
- The helper's block is 68,080 bytes (4,255 paragraphs, C90Ah).
- The overlay buffer follows it at once (D9AAh): no gap. The 2026-11-09 pass had 288 bytes there.
- 32,256 bytes free in one piece.

### Enlarged and the cahulaks' tangle
Setup:
- Lex's right-hand item (43) was made plain Cahulaks (type 21), with a scratch script `setitem.py`:
  - the record comes from SEGOBJEX (`champions.game_item`);
  - the link, flags and slot are kept, and +08h is set to 270Fh.
- Every foe (17-47) was held (`foeset.py C eff=34`) and Enlarged (`foeset.py C eff=16:0:3`).

Results:
- **Enlarged:** Tab + Return on Lex's turn. Two hits on the Templar (combatant 25), and neither has a tangle line.
- **Control:** Enlarged taken off the Templar (`addeffect.py del 25 16`). The next round's two hits each have "Lex's cahulaks tangle Templar? Save against petrification: ..." The first failed (tangled); the second was saved.

### Spellarcher quiver
- Lex's quiver holds Wooden Shocking Arrows (item 40, name 366, a spell arrow).
- I opened the inventory, showed Ester (20,104), picked up her Wooden Arrows (66,26), showed Lex (20,20), and clicked his quiver (66,26).
- Result: "CANNOT USE THIS ITEM", and the arrows stay on the pointer (`img/2026-11-10-quiver-refused.png`). They were put back on Ester.

### Spell boxes
- Lex was taught spells 23 (Strength) and 56 (Chaos) with `spellsetup.py 0=10 23 56`.
  - `spelltexts`' tables are keyed by the SPIN chunk, which is the spell number + 1. So 24 there is Strength, and spell 24 is Web.
- Then U on his turn, LEVEL, and a right-click on the icon:
  - **Strength:** 7 lines, inside the box.
  - **Chaos:** 8 lines; "flee." ran over the box's bottom edge.
- **The fix:**
  - I measured the box: 128 pixels of the game's font (FONT 100), the first line less 19 to 28 pixels for the icon. Both boxes wrap exactly so.
  - Three texts were over 7 lines: Chaos, Charm Person (the size rule's) and Vampiric Arrows. All three were shortened, and the arrows' texts now end "casts it on a hit".
  - `tests/test_spelltexts_fit.py` checks every text.
- Before and after: `img/2026-11-10-chaos-box-before-after.png`.

## From `pens-after-scar` (out of a fight), with a test build of the scripts

The test build: `kalzith.script_chunks` had its talk's entry (1139) pointed at Alagorn's talk (script 211 at 1h). `loadsave.sh` wrote `dos/GPLDATA.GFF`, and then the module was put back with `git checkout`.

### The view drag
`scroll.py` -150 0, 150 0, 0 100 and 0 -100 moved the camera:
- (1656,336) → (1728,336)
- → (1584,336)
- → (1584,256)
- → (1584,336)

The drag works after the interrupt change.

### Chaos's new text
- Cermak (member 2, the preserver) was taught it with `spellsetup.py 2=10 56`.
- U, Cermak's portrait (66,108), LEVEL twice (to 5), then a right-click on the icon.
- Result: 7 lines, inside the box.

### The pick icons in the hand
Cermak's held item 22 was written in memory (its +0, the object, and +0Ah, the type). To change what the hand shows:
- write it with the inventory **closed**: closing the inventory writes the screen's copy back over the record;
- clear +0Ch: the game keeps the icon it drew there (2511 after the Metal Pick);
- give it the item's own type: the Loader sets +0 from the type (`icons`), so type 127 always comes back as the Metal Pick, and Deepbiter needs its type, 112.

Results:
- **Metal Pick:** a whole grey head and gold fittings.
- **Deepbiter:** the same pick, with the fire flickering along its head.
- Picture: `img/2026-11-10-picks-in-hand.png`.

### Alagorn's stories (script 224) through Kalzith
Route:
- walkto (1816,408), (1704,408), (1592,440);
- a click at screen (152,165) with the camera at (1440,416) passes the guard in the entryway;
- `route.py 1560 880`;
- `pointer.py look`, a slow press on Kalzith (the old man in green, screen 257,120), and the Look box's first button (163,150).

The talk:
1. "I'm not from the Veiled Alliance" (1)
2. "What are you doing here?" (1)
3. Y
4. "Weapons or Armor" (1)
5. "Magic melee weapons" (2): he asks to be shown the item and lists Deepbiter (Cermak's, in memory).
6. Deepbiter (1)

Result: his story ("Deepbiter! A dwarf of the Undermountain made it his focus...", three boxes), then back to "What kind of magic item...". Picture: `img/2026-11-10-alagorn-deepbiter.png`.

## Not done
**Dark Sun Recompiled:** it isn't in this container (`/home/user/darksun-recompiled` is missing). It needs `tools/build_mod.sh` for the new PIC_FAIL site.

## Ended by a worker restart
The session's worker restarted after the last check, which took DOSBox and Xvfb with it. Everything above had been seen by then.
