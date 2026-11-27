# 2026-11-27: Wake of the Ravager's mouse as Shattered Lands'

**Under test**: branch `claude/ravager-cutscene-mouse`, DSCLOG2 with five new sites (170 `mouse_init`,
171 `mouse_set`, 172 `speech_wait`, 173 `fli_key`, 174 `fli_end`), the `INT 33h` hook and drag scrolling,
and the message box closing on a click or key. The user's reports, playing in DOSBox-X: no pointer in the
cut scenes and no click to skip them; the pointer moving differently from Shattered Lands; no middle-button
scrolling; a short freeze at each small pop-up (NO LINE OF SIGHT) that a click doesn't pass.

**Setup**: plain DOSBox 0.74 on `:55`, the game from `setup_game.sh` and `setup_ravager.sh`
(`/tmp/playtest/inst`, `/tmp/playtest/rav`), the Loader's copy of the sequel, `ravstart.sh`. DOSBox-X
isn't in this container: the fixes are all in DSCLOG2, which runs the same under both engines.

## The stock sequel first

- The intro's films: Space, Esc, Enter and a click do nothing. **Shift held about a second** skips
  (the FLI player asks after each frame for the Shift bits only, `test ax,3` at 8335Ch; at once if
  [631Bh] is set, else only after frame 240).
- START GAME's narrated opening: nothing skips it. It waits in a loop at 69BDDh
  (`lcall 230:51 / or al,al / jnz`, "the speech still plays").
- No arrow in either: the films are mode 13h (chained), the narration's picture planar (mode X).
- The pointer: the driver's 8 by 16 mickeys a pixel, and the game puts it at (318,100) after each
  mode set, as Shattered Lands did before its MOUSE_START.
- The cause is the mod's Shattered Lands-only features (the pointer in scenes, its start and speed,
  scrolling, the message box's close), never ported; DOSBox-X's settings play no part.

## With the branch

| Check | Seen |
|---|---|
| Intro film | the arrow on screen, follows the mouse; one click goes on to the title menu ([picture](img/2026-11-27-ravager-fli-arrow.png)) |
| Narrated opening | the arrow on screen and moving; a click stops the speech and the game goes on to the woman's talk in Tyr ([picture](img/2026-11-27-ravager-narration-arrow.png)) |
| Pointer speed | 30 pixels across for 24 down for the same mouse moves (8:10 mickeys), as Shattered Lands |
| Pointer start | not checked on its own (the same code as Shattered Lands' MOUSE_SET) |
| Middle-button drag | the map moves with the pointer, in the Tyr street |
| NO PATH FROM HERE, click | up 0.37 s, then a click: gone 0.10 s later, and the click didn't walk (Gerakis kept Move 12) ([the box](img/2026-11-27-ravager-no-path-box.png)) |
| NO PATH FROM HERE, Space | up 0.36 s, then Space: gone 0.02 s later |
| NO PATH FROM HERE, nothing pressed | gone 4.9 s after it came up: the options' message time, as before |

The box timings came from [2026-11-27-ravager-msgwatch.py](files/2026-11-27-ravager-msgwatch.py)
(it watches DSCLOG2's `msg_waiting` in memory, grabs the box, presses, and times the close).

## Found on the way

- **The narration's loop runs hundreds of times a second** with the game's timer at about 1 kHz while
  the speech plays. The first build redrew the arrow on every pass (wipe, read the DAC, draw) and the
  arrow was never on screen. Drawn only when the pointer moves, or every 4 BIOS ticks, it shows.
- **To see where a busy loop spends its time** a small ring in DSCLOG2 that the timer filled with the
  interrupted CS:IP (taken out again) found the loop at 69BDDh at once.
- **A message box to order in the Tyr ambush**: a click (after right-clicks cycling the pointer) on a
  square inside the closed room at the street's lower left, game (14,188), gives NO PATH FROM HERE
  on a party member's turn. The Draxans in the rooms off the street are all in sight of the eye (Look
  boxes, no NO LINE OF SIGHT).
- `shot.sh` doesn't work for the sequel (its capture folder is the SL copy's); `import -window` on the
  DOSBox window does.

## Water

Nothing new: the Tyr street of the opening, as before.
