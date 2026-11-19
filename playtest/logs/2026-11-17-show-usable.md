# Showing what can be used while Alt is held: experiments and the check in play

2026-11-16 and 17, DOSBox 0.74-3 under Xvfb, the Loader of this branch (DSCLOG untouched: assembled
from `dos/dsclog.asm` and `cmp`'d with `dos/DSCLOG.EXE` before the first start; `buildcheck.py` OK).
Saves: `pens-after-arena` and `fountain-user`. The DOSBox was shared: every session under
`flock /tmp/playtest/dosbox.lock`. No memory edit was saved (no save was made at all).

What is under test: `dsloader/usable.py`. While Alt is held on the map, out of a fight, a gold ring
under every door, container, body, item on the ground and person in view, and the names of the four
nearest the pointer. The Loader alone does it: DSCLOG's `RING_TAB` and `RED` (rings.py) and its four
label slots (labels.py).

## What was found before building

### Where the game keeps which things have a script (found: no MAS fallback needed)

- Searched the game's memory for the words of MAS 41's triggers (script place, script number,
  object) close together: one table holds them all, 13 bytes a trigger: +0 the place in the script,
  +2 the script, +4 the object's id (negative: the object number negated, as the scripts write it),
  +6 a use-with trigger's other id, +0Bh the next trigger's index (FFFFh: the last).
- The table is at the far pointer **DS:42CCh** (DS:1372h holds the same pointer). The lists' heads
  are words in segment **377Eh** (plus the load segment): +0Fh talk, +11h attack, +13h look, +15h
  use, +17h use with (+0Dh one more, empty in the pens; +09h the tile and box triggers, whose
  records hold squares, not ids).
- DSUN.EXE confirms it: the routine at file 967Ah ("what can be done with this thing") takes a
  thing's id (1A0A:0651h: the thing's field 48h through the field reader 826:9) and walks each list
  (9720h: `imul ax, 0Dh`, `les bx, [4356:42CC]`, compares `es:[bx+4]`, for the use-with list
  `es:[bx+6]` too, next `es:[bx+0Bh]`), returning bits: 4 talk, 2 attack, 8 look, 10h use, 20h use
  with. The runner at 9520h does the same walk and starts the script.
- A thing's id: an item record's first word; a creature record's +6 (found by matching each
  creature's object number, negated, in its record: always +6).
- In `pens-after-arena` (region 29h): 15 talk ids, 3 look (the Tied-up Prisoner's bodies, 1390-1392),
  47 use (the locked doors, haystacks, buttons, junk, the grate, the wardrobes), 12 use with.

### Experiment 1: what is in the draw list, and where a ring falls

- The draw list (far pointer DS:6690h, count DS:1F72h: 415 entries in the pens, the whole region,
  not only the view) holds three sorts of entry: things 0-519 that are creatures or items (the
  things table's kind 2 or 1); things 0-519 of kind 0 (the hall's banners and braziers: objects
  10408-10415 and 9716, drawn, with no record); and entries whose number is past 519 (55135...:
  the region's own scenery, among it a haystack that can't be searched). DSCLOG rings only the
  first two (`cmp bx, MAP_COUNT - 1`), and the Loader marks only creatures and items.
- **Doors** are items of type 17h or 72h (the only two door types in SEGOBJEX: 160 "Door", 2 "Door
  of Eyes", 1 "Portculis", and 2 "Brick Wall", secret doors, which are left unmarked), each leaf a
  thing of its own. The ring falls at the leaf's base (its feet: the map record's +9, the same
  point as the draw list's), which reads well.
- **Containers** (an item whose +8 names a list: the pens' chests, leather bags, the coffin): in
  the list; the ring lies under the chest.
- **Items on the ground** (the Empty Water Pot at 1663,665; type flag +08h without 20h): in the
  list; a small thing sits inside its ring.
- **Things with a use trigger** (a haystack: type flag 60h, scenery): the ring falls at the
  haystack's base.
- **Bodies**: see the fight below.
- A thing's map record +8 is how far its picture reaches above its feet (a man 41, a door 47, a
  chest 15, a pot 10): the name goes 3 rows over that, at most a man's 34.
- Creature sides in the pens: the party 1; Kurzak, the gladiators, the Trustee 4 (neutral);
  Legcrusher, the Arena Guards, the Guards, the Templars and the Zombie 2. A side alone doesn't
  tell who can be talked to (Legcrusher and the Arena Guards have talk triggers), so: a talk
  trigger makes a person; no talk trigger and another side than the party's (not 4) a foe.

### Experiment 2: frame time and walking pace (`framerate.py 20`, the hall of `pens-after-arena`)

Runs alternated in one session, the party walking back and forth for 20 s each.

| Case | Frames a second | Walking, map units a second |
|---|---|---|
| nothing marked | 19.4 to 21.1 | 153 to 159 |
| Alt held, the switch off | 19.4 | 153, 156 (no cost: the key alone does nothing) |
| 16 rings on screen by hand (`ringall.py`), 4 of them under the walking party | 18.2 | 122 |
| the same, the Tab ring's thicker kind | 17.9 | 122 |
| first build: 87 marked across the region, 1 on screen, 1 name | 16.5 | 120 |
| 10 marked (view and 96 pixels round it), 1 on screen, no names | 19.1, 19.3 | 136, 137 |
| the same with 2 names | 17.3, 17.9 | 123, 124 |
| **as built: 3 marked (the view and 16 pixels round it), 2 names** | **18.1, 18.0** | **130, 133** |

- The cost is DSCLOG's `ring_pass`: at every floor pass of the game (one for each rectangle it
  draws again, several a frame while figures walk) it goes round every marked thing's ring, on the
  screen or not, about 150 points each. So the count of marked things matters, wherever they are:
  the Loader now marks only what is in the view or within 16 pixels of it, and looks again as soon
  as the view has moved.
- A ring's thickness costs nothing more (the points off the rectangle are what cost).
- The names cost about as much again (the labels are put again from the timer and their place
  drawn again), as the floating names always have while one shows.
- As built, holding Alt slows a walking party by about 15% and takes about 7% of the frames, while
  held. A bounds test in `ring_pass` before the points would take most of the rings' share; that
  is the helper's, not done here.

### Experiment 3: the Alt flag

- **The flag**: 0:0417h reads 08h within the same 10 ms as `xdotool keydown Alt_L` returns, and 00h
  on keyup.
- **Latency** (`altflag.py latency 6`, the windowless dice log): the rings' table and the names'
  slots written 0 to 65 ms after the flag (on the way down 0 to 5 ms). The window's pass is every
  50 ms, so there up to about 100 ms. They show at the game's next redraw of the view, which the
  Loader asks for.
- **Alt+Tab** (focus taken by another window while Alt is down, a tkinter window and `xdotool
  windowfocus`; the key let go there, focus given back): the flag cleared the moment DOSBox lost
  the focus (it lets go of every key then: its `MAPPER_LosingFocus`), the marks came down with it,
  and nothing was set on the way back. So no stuck flag in DOSBox 0.74. Kept as a backstop all the
  same: Alt read as held for 30 s on end takes the marks down until it reads clear again.
- **Walking with Alt held**: the walk clicks walk the party as ever (the framerate runs above).
- **Clicking with Alt held**: a look click on a door went to the game as a look (its "NO LINE OF
  SIGHT" from where the party stood, the same answer as without Alt).
- **DOSBox's screenshot key** (Ctrl+F5, `shot.sh`) with Alt held is Ctrl+Alt+F5, its video capture:
  no picture. For a picture with the marks up, set the flag in memory instead (below).
- **Alt+Enter** (DOSBox's full screen; `xdotool key alt+Return`, twice, `altflag.py watch`): the
  flag read 08h for about 0.15 s each time, the marks went up and came down with it, the window
  stayed 320x240 under Xvfb and DOSBox went on. Nothing stuck.
- **The flag written in memory doesn't hold**: `0:0417h` with bit 3 set by a memory write read 00h
  again within half a second, with no key pressed (DOSBox's BIOS keeps it), so the first try at
  the doc picture (`shot.sh` with the bit set by hand) showed no marks. The picture has to be a
  window grab with the key really held (`convert -sample '320x200!'` to get the game's rows back).

## The check in play so far (`pens-after-arena`)

- The hall: Legcrusher ringed in gold and named; nothing under the party, the banners or the
  braziers.
- The guard room in view (camera 1240,336): 13 marks, as `usable.py` lists and the grabs show: the
  door's two leaves (255, 288) and door 228, the Bag (229) and the Chest (259) as containers, the
  Wardrobe (216, a use trigger), the two Guards and the Templar as foes (names in red), four
  Arena Guards as people. With the pointer at (200,95) the four named were the two Guards, an
  Arena Guard and the Wardrobe; moved to (60,149), an Arena Guard, the Templar, the Chest and
  the Bag. Kurzak (47) is named when in view.
- South of Kurzak's door (camera 1464,608): the Empty Water Pot on the ground and the haystack
  that can be searched (225) ringed and named; the other haystack in view, which is the region's
  scenery, not.
- Walls hide the rings as they hide the floor (the guards' behind the room's wall).

## Experiment 4: a fight that starts while Alt is held (`fountain-user`)

`logs/files/2026-11-17-show-usable-session-b.sh`, with `altflag.py watch` following the flag, fight_on,
the rings' table and colours and the label slots every 20 ms through it all.

- Before the ambush, Alt held (the key): the Templar (thing 25, a talk trigger) and the Junk (248,
  a use trigger) ringed in gold and named; 91 usable things in the region.
- Pehtucl's speech clicked away with Alt still held: at the watch's first sample with fight_on 1
  the table was empty, the colours the red ones and the names gone (the same 20 ms sample).
- Tab with Alt still held chose nobody (with Alt down it isn't Tab to the game: Alt+Tab). With
  Alt let go, Tab ringed the Templar: one entry, kind 2 (the Tab ring), the red colours.
- The fight fought out with `fightout.sh` (12 rounds of its loop), Alt held by
  `logs/files/2026-11-17-show-usable-flagfoes.py` during every foe's turn and let go in the party's:
  through the whole fight the table held either nothing or one kind-2 entry (things 24, 25, 40,
  42, 45, 46 in turn), the colours were the red ones in every sample, never the gold, and no
  kind-1 ring was seen. "Miss" came up over the party's members with the flag at 08h (things 0,
  1 and 2: width 20, the miss's ink) and over the foes in the party's turns, 10 misses in the
  dice log.
- So marking never touches the Tab ring or the names in a fight, whether the key goes down
  before it or in it.

## Bodies, and the second save

- After that fight, Alt held: the seven bodies in view (things 145-151 and 276, object 1101) are
  in the draw list and each has its ring, round the body where it lies (a body's picture is low,
  so its name sits 12 rows up, just over it), and the four nearest the pointer read "Dead Body".
  The Fountain (41, the use-with trigger of the water pot) is ringed and named. Four bodies from
  earlier (297-302) are off the screen and get nothing. 96 usable things in the region then.
- Seven names in a heap overlap; only four show, so it reads as a cluster of "Dead Body".

## A click with Alt held (`logs/files/2026-11-17-show-usable-session-c.sh`)

- A slow press on a body with Alt held, the walk arrow up: the party walked to the body (leader
  952,1432 to 1128,1496). The same press without Alt on the next body: the party walked to it
  (to 1080,1512). No window opened either time (a walk click on a body walks; the look pointer
  opens it). So the click does with Alt what it does without.
- Not done: a door opened or a talk begun with Alt held (the look click on the door in
  `pens-after-arena` was answered "NO LINE OF SIGHT", as a look is).

## The picture

`obsidian-edition/docs/show-usable.png`: `pens-after-arena`, `viewto.py 1380 440` (camera
1240,336), the pointer at (150,100), Alt held with `xdotool keydown`, `import -window`, scaled
200% (640x480, the window's 4:3: sampling the grab back to 200 rows cut through the names).

## After the rebase (the quick save, the chance to hit, the helper rebuilt)

Rebased onto `claude/modernisation-journal` at 7a8af4f (past 44a5527: the quick save, the chance
to hit, the quests tab), conflicts in `dicelog.py`, `launch.py`, `viewer.py`, FEATURES.md and
DEVELOPMENT-SCREENS.md resolved keeping both sides, the manual rebuilt: the whole suite passes
(2052 tests, 27 skipped) and the window tests under `/usr/bin/python3.12` (46).

**The check in the game after the rebase** (`logs/files/2026-11-17-show-usable-session-d.sh`, 2026-11-18,
`autosave` off in this worktree's settings, no memory edit, `PT_KEEP_OTHERS=1` so `start.sh` killed
nobody's processes; this session's DOSBox and dice log stopped by pid at its end):

- `buildcheck.py`: OK against the rebuilt helper (`DSCLOGvb`).
- `pens-after-arena`, the guard room (camera 1240,336), Alt held: the same 13 marks as before the
  rebase, 4 names (Chest, Guard, Templar, Bag with the pointer at 150,99); let go: 0 rings, 0
  names. `altflag.py latency 3`: rings and names 2 to 15 ms after the flag, off 0 to 7 ms after.
- **A door opened with Alt held: not shown.** The party walked beside the door (`route.py 1576
  472`, to 1576,440), which is within Kurzak's range: his "All right, go through the door..."
  boxes came up, the pointer read mode 0 under them, and the press went to the box. The door
  square (95, 28) stayed shut. Not tried again.

## Kit lessons

- **Xvfb started by `start.sh` inside a `flock` session inherits the lock** and keeps it after
  the session's script ends: every other agent then waits on a lock nobody uses (found with
  `lslocks` and `/proc/PID/fd`). Start Xvfb before taking the lock, and end a session's script by
  killing the DOSBox and the dice log it started, by pid.
- **`PT_KEEP_OTHERS=1`** (start.sh): its kills left out. `start.sh` kills every `python3 -u -m
  dsloader...` and every `dosbox`: with another agent's private game running, start with this set
  and stop your own two by pid (`pgrep -n -x dosbox` just after the start).
- From `pens-after-arena`, walking to (1576,440) brings Kurzak's two speech boxes (his stop's
  lines): clear them before any click there.
- Water: nothing new (the pens' fountain at 1098,1394 and the water pots were known).
