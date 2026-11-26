# 2026-11-25: R, F10 and Alt in Wake of the Ravager

**Under test:** branch `claude/ravager-fight-keys` (on `claude/ravager-join-gear-spells`, PR #184). Row 13 of the
port list: SL's squares in reach (R), F10 taking a whole move back (and a held member staying put) and Alt's gold
rings on what can be used, on the sequel. DSCLOG2's SQUARES pass (DSCLOG's TINT_FAR), its REDRAW_TICK (header
+1922), the rings drawn from a RING_TAB (header +246, the far block) and F10_PIN (site 100, the patch `f10_pin` at
F10's standing-still test 1EC36h); the Loader's `squares.py`, `moveback.py` and `usable.py` on the sequel through
`ravlog.RAV_FIGHT_KEYS`. Header fields taken: +1922 VIEW_REDRAW, +1924 SQUARES_ON, +1926 LIGHT's offset, +1928
squares drawn, +1930 F10's moves taken back, +1932 F10's refused, +1934 rings drawn under RING_TAB's marks.

DSCLOG2.EXE **45680 bytes**; in upper memory **45152** resident, **110448 free** after it (the largest piece
110304), `dosmem.py` during run b.

The runs: [files/2026-11-25-ravager-fight-keys-run.sh](files/2026-11-25-ravager-fight-keys-run.sh) TAG
[DICE_ENV...]: a fresh `ravFK` from `ravK` (thrown away after), the Loader's start, the four added, a new game to
the Draxans' ambush in Tyr, HP 250 a test edit (never saved: `RAV_NO_SAVES=1`). `ravkeys.py` read the state.

## Run a (the build under test)
- Lex's turn first (Move 12, 120 points). Squares on at the fight's start: 157 squares marked, dark
  crosses on Tyr's grey street (LIGHT has none for stone: DARK used), the room to the west through its door too.
- R: "Squares in reach: hidden (R shows them)", squares_on 0, the view drawn again clean; R again: shown.
- A click 7 squares up: points 46, the marks redrawn round the new square (54).
- A click past reach: points 0, flags' bit 0 clear: the sequel then opens its own menu "END Lex's MOVE: GUARD /
  WAIT / END TURN" (F10 does nothing while it is up); Escape closes it, Lex standing with Move 0.
- F10: Lex back on 74,93 with 120 points (f10_moves 1: site 100's jump), "F10: Lex's move taken back (can walk
  again)", the flags 0x3ef, 157 marked; a click: Lex walked (points 96). Before the fix the game gives the points
  but no walk (the step routine's bit 0, 5D8F1h).
- The pin (test edits, never saved: ravkeys.py effect): Lex walked 2 squares (96 left), given Cannot Move (66):
  F10 left him on 75,91 with 96 (f10_kept 1); given Paralyzed (69) too: the same (f10_kept 2); both taken out:
  F10 put him back on 74,93 with 120 (f10_moves 2), 157 marked again.
- Alt held in the fight: no marks (RING_TAB empty: the Tab ring's in a fight).
- The four put on Computer Control (USE, the small icons): the Draxans killed (Lex 4 of 5 hits); the crosses stayed
  through the level-up messages and CHOOSE A SPELL (the fight flag still up, Lex's points back to 120), gone once
  the flag dropped.
- Alt held out of the fight (the street): gold rings and names under the Scroll, the Sandals, a Pedestrian and the
  Draxan's Body (a container, object 2200, type 58: its ring at the item's feet, the corpse drawn below right of
  them); mark_draws 54, RING_TAB 5 marks; let go: the view drawn clean, RED red again.
- The sequel's things (ravkeys.py things/marks): doors are items of type 41 named "Door" (a use trigger names
  them), chests type 58, the draw list 873 entries for the whole map (SL's cap of 600 too few: the view's are past
  it), creatures off the fight side 1 (persons, by talk triggers), the Draxans in the ambush side 7.
- No water seen (Tyr's ambush street only).

## Run b, the control (RAV_SKIP=f10_pin; the dice log with RAV_NO_SQUARES, RAV_NO_MOVEBACK, RAV_NO_USABLE)
- Ester's turn: no crosses; R: nothing (squares_on 0, no line).
- Walked 6 squares, then 5, then 1: points 0, flags 0x3ee, the END MOVE menu; Escape; F10: Ester back on 73,92 with
  "Move: 12" on the panel and 120 points, but the flags still 0x3ee: a click walked nowhere (the game's bug).
- The pin without F10_PIN (test edits, never saved): the turn's start word moved to 74,90 and Cannot Move given:
  F10 moved Ester there all the same (in run a the helper kept a pinned member put).
- The control's party was defeated (the fight run on Computer Control after the test edits), so Alt's control
  had a run of its own:

## Run c, Alt's control (ravager-after-ambush in a fresh ravFK; the dice log with RAV_NO_USABLE=1)
- Alt held on the street after the ambush: no rings, no names under the scroll and the sandals (mark_draws 0,
  RING_TAB 0 marks); with the Loader's pass (run a) the same street had gold rings and names.

## Memory
`dosmem.py` during run b: DSCLOG2 45152 bytes resident in upper memory (MCB CA0Ah), 110448 free after it (the
largest piece 110304); the HMA on.

## Open
- The crosses stay up through the end-of-fight messages while the game's fight flag is up (gone once it drops).
- A body's gold ring sits at its item's feet, above left of the corpse's picture.
- Doors (item type 41) and bodies (object 2200) are known from Tyr only.
- No emulation test draws the new crosses or gold rings (the tests check the header, the site's jump and the
  Loader's side).
