# Squares in reach: where a figure can walk this turn (2026-11-17 and 18)

The game's rules of movement in a fight read from `DSUN.EXE` (capstone), then walked in the game
square by square; the marks built and held against the game; their cost. Played in a private
second game (a copy of the kit and of the game in a scratch folder, Xvfb `:58`, DOSBox copied as
`dbsq`), quick saves and autosaves off: the walks edit memory, and nothing was saved. The work
was paused twice (the owner's pause, then the branch's reorganisation): the helper's pass was
designed and assembled on the old base, taken out, and built again on the integrated one.

## What is under test

In a fight, on a party member's turn, the squares it can still reach this turn marked on the
floor. (A second step, the squares enemies' blows cover, was left out: below.)

## Read in DSUN.EXE (file offsets)

- **The points.** As a round starts (57414h, each of the 48 combatants) a creature's movement is
  its record's +1Bh x 10 (57566h), then doubled or halved by what 5B8:00D4 answers (the jump table
  at CS:09AAh: 5759Ah halves, 57580h doubles; which effects, not read), a word a creature at
  37BD:022Bh + creature x 2. Its turn's flags (37BD:01D5h + creature x 2) start at 3FFh; bit 0 is
  "can still walk".
- **A step** (the walker's step, 1BFB6h, for the thing at DS:4979h): it asks 41BE:008E (590B2h,
  the flags word) and walks only with bit 0 set; then 41BE:0093 (59106h) takes the step's cost
  from the table at DS:055Ch by direction (10 straight, 14 diagonal). With less than 10 left the
  points are zeroed and bit 0 cleared. So the test is made before the step and not against its
  cost: **a diagonal step can be taken with 10 to 13 points left** (it leaves 0). A square is in
  reach when a neighbour of it is reached with 10 or more points to spare.
- **What bars a square**: bit 40h of its byte on the live walk map (142F:00DCh, 197CCh; outside
  the 128 x 98 grid counts as barred). So 64-95 (edges with the bit), 96 (a figure: the party's
  and the others' squares get 60h, 19773h/19742h) and 192 and up (walls, shut doors) bar; 0 and
  1-31 don't; bit 80h alone (the line test's) doesn't bar walking. A figure wider than a square is
  tested over its whole footprint (1A0A:11DBh, 2067Bh: DS:1650h squares either side and DS:1652h
  up, from its sheet's +3Dh: low 3 bits and the rest / 8).
- **The path finder** is segment 8BBh (0DFB0h-0EAC1h), not 1A0A:2E99h (22339h: that one picks the
  free square nearest a target, for an approach). It draws a straight run of steps from the start
  to the goal (0DFB0h: 96C:009B gives the direction to the goal, 96C:006B takes the step), finds
  the barred stretches on it (0E069h), walks round each along its edge either way (0E185h,
  0E282h) and then straightens the result (0E8FFh). Only the square stepped into is tested
  (0E711h), so **a diagonal step between two barred squares looks allowed**. In the open its cost
  is the shortest (diagonals first, then straight); round a wall its way can be longer than the
  shortest, so a square marked by shortest paths may need two clicks.
- **F10 in a fight takes the move back** (the key table at 1BC5Bh: 4400h goes to 1B83Ah): on a
  party member's turn, if 1BF9Dh allows, the figure is put back where its turn began (DS:4966h,
  4968h) with the points it had (DS:4964h, kept at 1E59Ch). Useful for the tests; not tried.
- **The overlays**: `DSUN.EXE`'s root ends at 52EA0h (FBOV header); each overlay has a stub
  segment in the root (41A6h and up: `CD 3F`, the overlay's place and size, then 5 bytes an
  entry), so a far call to 41BE:0093 is the combat overlay's (56CC0h-5A031h) entry 59106h.

## In the game, 2026-11-18 (`fountain-user`, Pehtucl's ambush, Ester's first turn)

New kit tools: `movestate.py` (whose turn, its square, points and flags, the walk map round it with the
Loader's marks), `squarewalk.py COL ROW [POINTS]` (one click on a square, where the member
stopped) and `squaresweep.py POINTS [edge|all|out]` (the marks against the game, a walk a square,
F10 between).

- Ester (Move 12) begins with 120 points; Jenna (Move 12) has 140 (a rule of the Loader's adds
  to hers). The name box shows "Move : 12", the points / 10.
- (54,95) to (62,88), seven diagonal steps and a straight one: 12 left (108 spent). One straight
  step more: 0 left, the "can walk" bit cleared, END ESTER'S MOVE opens.
- **F10 takes the move back**: with the END menu closed (Escape), F10 put her back on (54,95)
  with her 120 points. **But the "can walk" bit stayed cleared** (flags 3EEh): the box says
  "Move : 12" and no click walks her. So F10 gives a move back only while some of it is left;
  after the last step it puts the figure back and no more (the game's own slip).
- **Walking past an enemy costs nothing and stops nothing**: (54,95) to (64,95) along the row
  under the Templar on (60,94): reached, 108 spent (the 100 of ten straight steps and 8 for the
  two diagonal ones round Jenna on (56,95)).
- **The game's route takes its diagonal steps first** (96C:009B with DS:01F8h 1: the direction is
  diagonal while both x and y differ). So the step begun with 10 to 13 points is a straight one
  and its 10 must be there, unless the whole way is diagonal: with 60 points (48,94), six west
  and one north, 64 by the shortest way, was not reached (she stopped on (49,94) with 0), though a
  click on (49,95) and then one on (48,94) would get there. **The marks therefore go by what one
  click reaches**: the shortest way's cost within the points, and a clear diagonal run's last
  step begun with 10 or more.
- **A member can be without a square**: Lex, the leader, listed on (55,94), had none on the walk
  map at the fight's start (DS:0546h, the party's squares, had 129,99 for him: "none"), and Ester
  walked onto his square. The marks follow the walk map, as the game does.
- **A test's trap**: a walk the Move ran out on stays the member's (its next step, 3972:0377h +
  thing x 1Ch); with the bit put back in memory the game goes on with it, from wherever F10 put
  the member, and the next click's walk is mixed with it (a first sweep read a square late all
  through). The tools forget it (FFh there, 0 at 3972:08AAh + thing x 13h) with the edit. In play
  the bit never comes back in a turn, so nothing of this shows.
- **Clicking the square behind a figure clicks the figure** (Ester's own square's northern
  neighbour: no walk): a tool's limit, not a rule.

### The marks against the game (`squaresweep.py`)

Each line a walk of one click with the points set in memory, F10 after it.

| Member, from | Points | Rim squares (the last 10 points' worth) | Free squares just outside the marks |
|---|---|---|---|
| Ester, (54,95) | 60 | 14 of 14 reached | 18 of 18 not reached, each stopping where the rule says |
| Jenna, (56,95) | 90 | 13 of 13 reached | 10 of 10 not reached |

The rims go round the wall's corner at (54-55,90-91) into the room to the north (56,90; 59-61,88),
round Jenna and Seneca (59,95; 56,96, a diagonal step between the two of them: corners are cut),
past the Templar (63,94; 64,93-96) and along the edge squares of row 96 (bytes 1-6: walkable). So
in this room the game's route cost what the shortest way costs every time; **no two-click square
turned up**, though the reading says one can (a route that follows an obstacle's edge the long
way round). Only squares on the view were tried, and none
behind a figure (the click is the figure's).

- **A click on an enemy's figure walks up and attacks**: Ester's blows at the Templar ended her
  turn (flags 0), Jenna's began. Whether one attack of several leaves the walk is not seen.
- Jenna's box says "Move : 14" (140 points): the marks read the points, so a Move of any size
  (Haste, Slow, the Loader's own rules) is followed.

## On the integrated base (`DSCLOGvd`), 2026-11-18

Rebased onto `claude/modernisation-integration` (dfef3d8), the pass written into `dsclog.asm`
again with the header's fields at +1880 and +1882, the signature `DSCLOGvd` in the helper, the
Loader and the kit's tools; `buildcheck.py` OK after each restart (`ring_px` and `tint_pass`
named: the same as the EXE).

### The marks on the screen

- The first pass's cross (five pixels, lightened twice) could hardly be seen. Patterns and
  strengths were tried by drawing them on a clean shot with the game's own palette and LIGHT
  table (a scratch script): **nine pixels, five each way, lightened four times** reads well on the
  pens' paving and in the walls' shadow and stays out of the way. Seen so in the game.
- With the Tab ring (red, drawn over the marks), the combat log's panel (it covers them),
  shadows and dust: nothing fights. The marks shrink as the member walks, and are the next
  member's when the turn passes.
- **The arena's sand** (a new game, `topartyfight.sh`: the first bout): white crosses on the
  pale sand, legible.
- **A floor the dust has no colours for** would have had no cross at all (LIGHT is 0 for a colour
  that isn't ground), so `RING_PX` now darkens such a pixel four times through the shadows' DARK
  instead. The arena's stone platform was to show it, but it is a thing drawn over the floor: the
  crosses under it are covered (a limit: a square under a rug or the platform shows none). Seen
  in the game with LIGHT emptied in memory for a shot: black crosses on the sand. No floor of
  the pens or the arena needs it.
- The picture, `obsidian-edition/docs/squares-in-reach.png`: the fountain's fight, Seneca with
  62 points left (two walks, no memory edit), the Templar chosen with Tab; `shot.sh` at 200%.

### The marks against the game, again (`squaresweep.py ... here`)

From where the member stood (walked back to after each try), in the ambush and the arena:

| Member, from | Points | Rim squares | Free squares just outside |
|---|---|---|---|
| Seneca, (57,80), by the two-square doorway (53-54,78) | 60 | 12 of 12 reached | 0 of 8 |
| the same | 90 | 6 of 8: (50,81) and (51,81) a step short | |
| the same | 120 | 6 of 6 | |
| Seneca, (46,80), above the one-square doorway (45,82-83) | 60 | 6 of 7: (47,84) a step short | 0 of 5 |
| Gerakis, (30,26), the arena's sand, sligs and allies round him | 60 | 22 of 25: 3 clicks walked nobody (a body or a figure under the pointer) | 0 of 26 |

With the first day's two rows: **85 rim squares, 79 reached in one click, 3 a step short, 3 not
walked; 67 squares outside, none reached.**

- **The two-click case, found.** All three short walks were to squares behind a wall, through a
  doorway off the straight line from the member: the game's route starts along the straight line
  (a diagonal step toward the square, away from the doorway), meets the wall and goes round. To
  (51,81) from (57,80) the shortest way is 86 and the game spent more than 90. The marks go by
  the shortest way, so there the last cross or two can take two clicks; the pages say so. The
  game's route finder is not played out in the Loader (1.5 KB of its code, and the Loader has no
  emulator).
- **F10 with movement left** gives all of it back, and the member walks again (Ester: 72 points
  left, F10, 120, a new walk). After the last step it gives the points and no walk (above).
- **The turns** (`onwatch`, a scratch poll of whose turn and `SQUARES_ON`): on within a quarter
  second of a party member's turn, off within a quarter second of an enemy's; K'ratchek's Move 15
  marked as 150 points.
- Not seen: whether one attack of several leaves the walk (the click on the Templar spent all of
  Ester's attacks); a hasted or slowed member; any region but the pens and the arena.

### The cost (`squarecost.py`, a member walked along row 93, 47 to 58 and back, six legs)

| Build | Marks | 250 points in memory | 120 points |
|---|---|---|---|
| first pass, the marks made again at every step | on | 131 map units/s, 62 frames/s | |
| | off | 156, 69 | |
| the pass passing over what is outside the clip, the marks waiting for the walk's end | on | 154, 155, 152 (67-68 frames/s) | 160, 158, 156 |
| | off | 157, 157 (69) | 159, 161 |

The first pass tested every pixel of every cross against the clip at each floor pass (a walker's
rectangle, each frame), and the Loader had the whole view drawn again four times a second while
the member walked. Now a row or a square outside the clip is passed over, and the marks are made
again once the member stands (two looks running the same). Standing still nothing is drawn.

### Memory

`memaudit.py` in the ambush with the first build of the day: DSCLOG's block 71,232 bytes, 29,104
free in one piece between the overlay buffer and the see-through tables (29,424 before). The
final build is 16 bytes longer (the darker fallback): 71,248 and, by the same sum, 29,088.

## What was built

- `dsloader/squares.py` (`reach`, `costs`, `bitmap`, `mover`, `Squares.update`), the dice log's
  upkeep, the Options switch (`squares`, on).
- DSCLOG: `TINT_PASS` before `RING_PASS`, `SQ_MAP` in the tail, `RING_PX` rewritten round a table
  word with the darker fallback, `FLOOR_ENTER`'s test: 208 bytes of the segment (320 spare), 128
  of the tail (27 paragraphs of upper memory spare).
- Tests: `test_squares.py` (15), `test_squares_drawing.py` (7, in the emulator).
- Kit: `movestate.py`, `squarewalk.py`, `squaresweep.py`, `squarecost.py`.
- Not built: the squares enemies' blows cover (walking past an enemy neither stops nor costs, so
  there is no "where walking ends" to show), and a mend for F10 after the last step.

## The processes

Everything this session started (Xvfb `:58`, `dbsq`, its dice log, its watchdog) was stopped by
pid at each pause and at the end. Nobody else's process was touched; none of this session's was
killed by another (the first pause's and the usage stop's took the container's processes).

