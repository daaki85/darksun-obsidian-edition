# 2026-11-07: review fixes seen in DOSBox

Under test (obsidian-edition): Pehtucl's chest as script 223 (it had taken Alagorn's 220), with
its new distance check; the Loader's script entries numbered whatever the switches; DSCLOG with
the Spellarcher arrows wait's `sti` (loads and runs).

**Setup:** `loadsave.sh pens-new-chest` (window 320x240, dice log attached). The built
`dos/GPLDATA.GFF`: GPL 220 is Alagorn's again (10,075 bytes; his talk's call at 942 lands inside
it), the chest is GPL 223 (779 bytes), the entries end (1139, 218) (1140, 219) (1141, 223): the
chest's entry keeps the number the save holds, and MAS 41's USE command is (1, 223, -1568). DSCLOG
in memory at C91B0h has the new `call pp_restore; sti; pushad; push es` (image A974h). Then
`teleport.py 200 1432 40 1322`, walkto (216, 1440), (120, 1464), `shut.py` (the save's chest
predates the shut type).

## Seen
1. **From five squares away** (leader at 120,1464, the chest at about 201,1392): "You must be next
   to the chest in order to work on it." Nothing else; the chest stayed shut. (The last test's
   picks were made from here: the check was missing.)
2. **From beside it** (leader at 184,1400): "The chest is locked. Gerakis doesn't know how to pick
   the lock. Bash it open?" No: the chest stayed shut (type 67h).
3. **Gerakis a level-12 thief** (`thief.py 0 12`, in memory): "checks the lock for traps, and draws
   out a poisoned needle hidden in it" (find/remove traps d100 31 vs 75): **the disarm, the one
   branch the last test hadn't seen**; then "works at the lock but it holds" (85 vs 77).
4. **Again**: no trap check (the needle gone, flag 795), "works at the lock until it clicks open"
   (22 vs 77). Before the click the Loader had made it a chest (31h, flags 795 and 796 set); after
   the click the game opened it. Escape closed it; `thief.py 0 off`.

Not seen in play: Alagorn's clothes menu (he isn't in the pens; checked in the built scripts and by
`test_scriptnumbers`), and the Spellarcher arrows wait (the `sti` is in the running helper; no
Spellarcher in the save).

## Tools
- `pointer.py [walk|look|attack]`: the pointer's mode from memory (DS:11B8h: 1 walk, 2 the eye, 4
  the sword; a right-click goes 1, 4, 2), right-clicking on bare floor until it is the one wanted.
  Two right-clicks guessed from a shot left the sword up, and one landed on a party member and
  opened the USE screen.
- `teleport.py`, `shut.py`, `thief.py` (was mkthief/nothief), `orderwatch.py`, `chestuse.sh`: the
  last test's scratch tools, now in the kit.
- Walking beside the chest put Gerakis on it (his figure over it): walk a square west (184,1400)
  before the look click (163,70).

## Later the same day: the helper's label and picture fixes (DSCLOG.EXE 65,552)

**Setup:** `loadsave.sh pens-after-scar`. The new code was in memory at DSCLOG's image offsets
C6DBh (GHOST_DRAW's null-picture test), D097h (LABEL_WHERE's off-the-top test) and D0B2h
(LABEL_ERASE busy first). A spell cast out of a fight from the USE screen (Cermak's Enlarge on
Gerakis): the dice log had it, and no name floated over the map, which the screen covers.

**The alarm fight** (`toalarm.sh`, which stopped at (1832, 856) as before: a click on the room's
floor at screen 240,160 went in; then `pointer.py look` and `restalarm.sh`: 5 rests, the call, the
fight). The guards stayed out of reach at first (Tab + Return: "NO PATH FROM HERE"), so the party's
turns were passed through the END menu until a foe missed (Kurzak on Cilla, then on K'ratchek), and
the view was dragged south as the "Miss" went up. No stray pixels, the game ran on.

**Not reached:** a label whose figure is above the view's top. In a fight the drags moved the
camera only a little (from 1728,768 to 1712,832 after two drags of 150): every party figure stayed
at row 20 or more. The case needs a label over a figure off the top, which the fight's view didn't
allow; the fix is checked only by reading the code there.

**Learned:**
- `E` pressed without the END menu open (a click beside the figure) opened the Effects screen, and
  Escape left the camera at (0, 0): the loop now checks for (0, 0), presses Escape and runs
  `viewto.py` back to the party.
- A miss in the dice log ends `-> miss` (a hit `-> HIT`).
