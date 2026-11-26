# Audit fixes 2 in the game (2026-11-18)

Under test: `claude/audit-fixes-2` (DSCLOG `DSCLOGvc`: IF_FRAME on 22 handlers, CLD in the tick, STUB
and RECORD, INT33 forgetting a removed handler, VGA_LATCHED in the scenes' arrow, A20_CHECK each
pass; UMBPLUS at CA00h; heapcheck's pieces line). Build checked with `buildcheck.py`: OK (129
vectors at their handlers, the tail as the EXE). DOSBox 0.74-3 (Linux), window 320x240.

## Memory as loaded (memaudit.py, the title screen)

- Upper memory: system MCB 9FFFh to CA00h, a free scrap of 9 paragraphs at CA00h, DSCLOG at CA0Ah
  (71,104 bytes, as DEVELOPMENT-INTERNALS computes), the overlay buffer at DB67h (32,992), 25,136
  free, the see-through tables (14,160) and the music pool (12,016) to F000h. UMBPLUS's new start
  in place.
- Far block in the HMA (far_seg FFFFh), A20 on (FFFF:0010 differs from 0:0).
- Conventional: DOS memory after the game 185 KB free in one piece (title screen).

## The scenes

- START GAME's decree: DSCLOG's arrow drawn and following relative mouse moves over six shots, no
  arrow left behind where it had been; the scene fades out on its own. A click during the decree
  waits for the still picture's end (as FEATURES says: between a scene's steps). The arena intro's
  speech box then took a click.
- The title: the first mouse clicks went nowhere until the window had focus and a click (the
  guide's known capture step); after it, click.py read the pointer moving.

## fountain-user: the ambush, walking, the inventory, the map

- Loaded, window 320x240, `buildcheck.py` OK. The ambush's speeches clicked away; Seneca hidden
  and unheard drawn see-through (PROBE_GHOST, now with interrupts as its caller had them); the
  combat log panel (L) up.
- **Tab and Enter** (TARGET_CLICK's calls to the game's mouse handler): "Chosen with Tab:
  Templar", then Seneca's backstab and two attacks at it. `fightout.sh` finished the fight (12
  passes, 3 rounds, 6 kills); the panel's summary and the dice log's tally as usual.
- **Memory with the map open** (`memaudit.py` after the fight): the heap 201 KB with no free block
  in it, 99,008 bytes free after the game in one piece: over the 64,000 bytes of heapcheck's new
  pieces line, which said nothing (no memory line in the dice log all session). `a20_lost` 0.
- **The inventory and INFO**: Lex's Shocking Arrows' box, INFO: "SPELLARCHERS: / Lex".
- **The item box's nudge** (BOX_NUDGE, still from the timer, now after a CLD): the defilers'
  scrolls given in memory (`scrolltest.py give`; never saved), Lex read Spook from its box: "YOU
  LEARN THE SPELL" on the line under the paper doll with the pointer not moved, and in the dice
  log ("Lex reads the scroll of Spook: d100 = 76, needs 96 or less (INT 20) -> learnt"). (Two
  presses before it were lost, as the guide warns of: the box shut, nothing read.)
- **The pointer over the map**: moved across the view, walked, dragged with the middle button both
  ways (camera 936 -> 1016 and back): no pointer left behind, shadows drawn, no garbage.

## The creation screen

- CREATE CHARACTERS, NEW: the screen with its die; a roll (the dice log's best-of-four 4d4 lines,
  the hit points), a class click, EXIT. Nothing odd.

## Not seen

- A click skipping a scene before its end: the decree is a still picture, which plays to its end
  (as documented); no other scene was reached.
- A20 off, the game removing its mouse handler, a latch copy under the scenes' arrow: none of these
  happen in play; the emulated tests (`test_interrupt_hygiene`) cover them.

## Water

- The pens' fountain room (the ambush's place, about 1000,1400): the fountain; Lex carries a Pot of
  Water, the first such item noted: added to ROUTE.md's water section.

No freeze, no stuck pointer, no garbage on screen in any of it. DOSBox, the dice log and Xvfb
stopped by pid at the end; the lock released. Nothing saved.
