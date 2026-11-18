# The chance to hit under the pointer (2026-11-18)

The owner's request: "make the chance on hit appear in game with mouse hover when the mouse is over
monster. It would be shown similar to a miss". Built in the Loader alone (`dsloader/hover.py`,
`Labels.hover`); DSCLOG unchanged. Played in the shared game on display `:55` (no other agent
running), `fountain-user`, the ambush, nobody held unless said. Quick saves and autosaves off in
`settings.json`; the fight used `healparty.py` and `foeset.py` (memory edits): nothing was saved
(the game folder's `SAVE01.SAV` is still the kit's copy, `cmp`).

## What is under test

In a fight, on a party member's turn, while the game's pointer is over an enemy, the roll needed
and the chance float over that enemy as "Miss" does (`12+ (45%)`), and go when the pointer leaves
or the turn passes.

## Read in DSUN.EXE first (file offsets)

- **The game already knows what is under the pointer.** 1E126h, called from the map's loop with
  270Fh ("the pointer's thing"), asks the finder a click uses (25B52h, DSCLOG's `PROBE_HIT`) with
  the camera (DS:1178h) and the pointer (DS:A133h) and keeps the answer in **DS:0BCBh** (FFFFh:
  none). It then lights the thing up: a creature by its side (+1Dh: 1, 4, else), of the items only
  a body (object 1101), blinking it (the thing lit in DS:0BD1h, the state in DS:0BCDh, a count in
  DS:0BD4h). When the pointer has moved on, the routine puts the thing lit before back in DS:0BCBh
  for a pass to take the light off (1E2C2h, 1E32Ah).
- **The finder** (25B52h): the draw list from its last entry (the front) down; a thing whose map
  record (DS:6694h + 32 x thing) has bit 10h in +0 and a picture (+0Fh not FFFFh), whose box holds
  the pointer (left +3 less the camera, top +5 less the camera less the signed byte +0Dh, width
  +12h, height +13h); on the map (DS:1F82h set, the pointer's mode not 3) only if the picture has
  a pixel there (147D:0166h, mirrored for the entry's +5 bit 80h). The first such thing.
- **The clicks**: the handler's table at CS:0B64h goes by the pointer's mode (DS:11B8h, 1 to 5).
  The walk arrow on a creature past the party (1B0E9h) attacks at once at a distance of 1 or less
  and walks up otherwise; the attack pointer (1B67Bh on) wants a line of sight (898:00A4h; the
  messages TOO FAR AWAY and NO LINE OF SIGHT are at DS:0BEBh and DS:0BF8h) and attacks at the
  distance between the two (1B730h), so the picker takes the missile weapon.

## In the game

`hoverlabel.py` moves the pointer (no click) and reads the label back from DSCLOG's slot, matching
its ink mask against every text the Loader can make, so the text is what the session's Loader
drew; `hoverhit.sh C [attack]` does that, clicks and prints the attack's lines.

**DS:0BCBh, all three pointer modes** (walk 1, attack 4, look 2): the Templar under the pointer at
its figure, Lex, Jenna and Ester at theirs, FFFFh on the floor.

**The label against the swing that followed:**

| Member | Enemy | The pointer, the distance | The label | The swing's line |
|---|---|---|---|---|
| Lex | Templar | attack pointer, 5 squares | `9+ (60%)` | Wooden Bow, `needs 9+ (60%)` |
| Ester | Templar | walk arrow, far | `12+ (45%), behind 9+`, then next to it `12+ (45%)` | Bone Long Sword, `needs 11+ (50%)`: 1 off, the dance (+1) rolled before the dice log was restarted with the new code, so this Loader hadn't seen it |
| Jenna | Arena Guard | attack pointer, 14 squares | `11+ (50%)` | Wooden Bow, `needs 11+ (50%)` |
| Lex | Guard | walk arrow, 6 squares | `6+ (75%)` | Bone Short Sword, `needs 6+ (75%)` |
| Ester (the next dance seen) | Guard | walk arrow, 2 squares | `5+ (80%), behind 3+`, then next to it `5+ (80%)` | Bone Long Sword, `needs 5+ (80%)` |
| Seneca, hidden | Guard | walk arrow | `Backstab 2+ (95%)` | Hayneedle BACKSTAB, `hits on anything but a 1 (95%)` |
| Jenna | Arena Guard | walk arrow, next to it | `13+ (40%)` | Obsidian Long Sword (the first swung), `needs 13+ (40%)`; then the Bone Long Sword's 12+ |
| Seneca, after her kill kept the turn | Arena Guard | walk arrow, far | `12+ (45%)` (her Hayneedle's, the first in order) | Shadowseeker, `needs 11+ (50%)`: **the Hayneedle had already swung this turn**, which the prediction doesn't know |

Jenna's walk arrow over the same guard said `13+ (40%)` where her attack pointer said `11+
(50%)`: the walk-up's first sword against the bow. The eye showed the walk arrow's number.

**Which enemy.** Four Arena Guards stood two by two: the pointer on a back one's feet point gave
the front one (the game's word and the label), its head gave the back one. Between the big
Guard's legs: nothing. An ally's figure, a body (thing 151), the floor: no label. A held guard
(`foeset.py 24 eff=34`): `Hits`.

**When it goes.** Leaving the figure: off the screen 0.2 s later (`LINGER`). The turn passing to
an enemy: gone in the same 50 ms look, nothing through the enemies' turns with the pointer at
rest on the guard, and the next member's own number as its turn began (`13+ (40%)` for Jenna's
walk arrow: the game puts the walk arrow back at each turn). The END menu up (DS:0BC9h 2): gone.
The enemy killed: gone.

**"Miss" on the hovered enemy.** Seneca's and Jenna's misses on the guard under the pointer: the
slot held "Miss" for its 1.5 s, then the chance again (for whoever's turn it was by then); with
two "Miss" labels over party members up, the chance had a third slot.

**With the rest.** Squares in reach on throughout. Tab on one guard (its red ring) and the pointer
on another: the label over the pointer's, only the `Chosen with Tab` line in the dice log, the
header Tab's. The combat log's panel over the guards with the pointer on it: the game's word still
named the guard behind it, no label (`hover.on_panel`); panel hidden with L: the label. "Names
over figures" and the Tab chance both off in settings.json (the dice log restarted): the label
showed and stayed.

## Found on the way

- **A label taken off came back.** With the scene still, the label was off the screen for one
  frame after DSCLOG erased it and then back for good, until something drew the view (window grabs
  every 30 ms: 44 pixels of ink, 0 once, 44 again for 3.5 s). The same with a "Miss" put from a
  script and taken off after 1.5 s, and with the squares in reach off. DSCLOG's state had it not
  shown and the slot empty. Asking for the view again (`shadows.redraw`) cleared it, so the
  Loader now does that whenever a label is taken off, moved or reworded (`Labels.took_off`);
  after it the label was gone 0.2 s after the pointer left and stayed gone. Why `LABEL_ERASE`
  doesn't hold in a still scene wasn't looked into (the helper wasn't to be changed).
- **A dice log killed with the label up** left it in its slot for good (a standing label, unlike a
  "Miss", is up whenever the pointer rests): a Loader now empties the slots that aren't its own
  at its first look.
- **A stumble counts.** Ester's third dance was a 20 (-1 to hit for 4 rounds): her label over the
  guard went from 12+ to `13+ (40%)`.
- **The attack pointer with no attacks left**: Ester's click after her kill ended the turn with
  nothing swung; the label still showed.
- `panel.sh` printed "panel hidden" with the panel up and empty (its pixel is the frame's while
  text is in it): L by hand, and a shot to see.

## The cost

A still scene on Jenna's turn, 10 s each (`hovercost.py`):

| | Frames shown a second | Passes of the map's loop a second |
|---|---|---|
| The pointer on a guard, the label up | 23.9, 23.9 | 933, 935 |
| The same, `hit_hover` off (the game's own blinking of the figure) | 24.1, 23.9 | 2,018, 2,054 |
| The pointer away (either way) | 0 (nothing drawn) | 3,168 |

The frames are the same; the passes are DSCLOG's upkeep of a label on a blinking figure. The
Loader's side (`hovercost.py loader`): a pass's look takes 9 microseconds with the pointer away,
16 resting on an enemy (the prediction kept), 755 when it is worked out afresh (when something
moved, else twice a second).

## Not seen

A shot with no line of sight (the label doesn't know), `Behind` next to an enemy and `Unseen`
against real swings (their numbers are `predict`'s, checked on 2026-11-17), a talk or a window
other than the END menu, any fight but the fountain's, GOG's DOSBox on Windows, the Loader's
window (the text dice log ran).

## Water

No new area.
