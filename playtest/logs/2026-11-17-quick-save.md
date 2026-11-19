# Quick save, quick load and autosave: experiments and tests, 2026-11-17

What was under test: a save made by DSCLOG calling the game's own save routine from the map's
main loop (no window), the LOAD window opened by a key, a fifth page of the save window (QUICK,
`SAVQ01.SAV` to `SAVQ10.SAV`), and the Loader's policy for them (`dsloader/quicksave.py`). The
research behind it (`reports/modernisation-research-and-plan.md`, section 1) was static reading;
each point is checked here, in the order the plan gave. The build: DSCLOG.EXE 70,416 bytes,
signature `DSCLOGvb`; `buildcheck.py` OK at each start (134 vectors at their handlers, the tail
the EXE's; `save_tick`, `qs_key`, `our_key`, `sp_page` the same as the EXE).

DOSBox 0.74-3, 20,000 cycles, the kit's saves `pens-after-arena`, `fountain-user` and
`pens-fire-count4`. No memory edit was made in any game that was saved: the one fight was fought
as it stood (`PT_NO_EDIT=1 sh fightout.sh`).

## 1. What F5 and F9 do in the game

**Disassembled.** The map's key routine (DSUN.EXE 1B7DEh, event 6) looks its key up in a table of
26 at 1BC5Bh: 1 to 6, P, N, Space, F5 (3F00h, to 1B811h), F6 (1B81Eh), F9 (4300h, to 1BA52h),
F10, the arrows and Home/End/PgUp/PgDn, Alt+F1, Alt+F2, Alt+F4.

- **F5** (1B811h): `call 191F:00F1`, which draws the view again at the camera (DS:1178h), then
  `call 28D1:0D7E`, the screen's update. Nothing else.
- **F9** (1BA52h): the overlay entry 42E0h:0052h, 810DCh: if the current member's creature record
  has 4 at +1Dh, it sets +1Dh of all four party members to 1 and takes three kinds of object
  (-296, -171, -269) off the map. The routine just before it (80Fxxh on) is the one that puts
  those objects round the leader and sets +1Dh to 4: the game's camp. So F9 breaks camp, and does
  nothing when the party isn't camping.
- F1 to F4 are not in that table: another handler has them.

**In the game** (`pens-after-arena`, the two keys given back to the game with `qsave.py keys FFFF
FFFF`): F5 and F9 each left the screen pixel for pixel as it was (`compare -metric AE`: 0), with
no message and nothing in the dice log; the party's +1Dh bytes are 1. F1 opened the **SAVE**
window (and the game goes on after it: no quit to DOS, unlike the Escape menu's SAVE), F2 the
**LOAD** window, F4 said MUSIC OFF and MUSIC ON; F6, F7, F8, F10, F11 and F12 showed nothing (a
hundred pixels of the pointer and the torches between shots). F3 (quit, by the manual) was not
pressed. The manual's "F5 toggles sound effects" is not what this build does.

**Decided: F5 saves, F9 loads.** F5's redraw is of no use to a player in DOSBox. F9 matters only
in the game's camp, which the pens' rest is not (below, 4): there the Loader gives both keys back
to the game (the party's +1Dh 4), and with the switch off they are the game's always. The keys
are the Loader's to set (two words in DSCLOG's header), so another choice is a constant in
`quicksave.py`. Not verified: the camp itself (no place to camp was reached), so that F9 breaks
it is from the code only.

## 2. The direct save against the window's save

**Where the call is made from.** `PROBE_SCROLL`'s site (1CAACh) is in the routine at 1587h:1DF1h,
whose only caller is `main()`'s loop (1A947h; `main` at 1A521h, called once from the C startup,
5558h). So the request is served at the top of the game's one main loop, never inside a talk's
or a message box's loop. The routine does nothing (and so serves nothing) while DS:0BB6h is 0 (a
window or screen up) or on an enemy's turn in a fight.

**What the window does besides the save** (disassembled, then seen in the files):

- its open (overlay 428Ah, entries 20h LOAD and 25h SAVE; 7452Dh) calls 1587h:22BAh (lets go of
  the item boxes' pictures), 1587h:2CCBh (DS:38D2h and 3CD4h to 0: the map's drawing held while
  the window is made; 1587h:2C8Dh(1) at the end sets them again) and 191Fh:0B36h(4) (the
  pointer's shape for a window). None touches the game's state.
- its wrapper (7468Bh) makes the file name, shows SAVING GAME, calls the save (4242h:0089h,
  6912Dh), then opens **CHARSAVE.GFF** (DS:11C2h, by 4239h:57h), writes `PREF` 100 (11 bytes:
  DS:11AEh, 232Eh-2330h, 11A8h, 11AAh, 11ACh, the music and sound settings) into it, closes it,
  and shows GAME SAVED. The load's wrapper (747ABh) reads `PREF` from CHARSAVE.GFF after the load,
  if it is there. So the PREF chunk is not part of a save, and a save made without it loads with
  the settings as they stand.

**The two files.** `pens-after-arena` loaded, the look pointer up (the game's clock stands still:
1481 before and after), `qsave.py 1 "DIRECT ONE"` (done in 0.335 s; `SAVQ01.SAV`, 85,680 bytes),
then F1, row 1, "WINDOW ONE", SAVE (`SAVE01.SAV`, 85,680 bytes). `savediff.py`: 87 chunks each,
85 the same. They differ in:

- `STXT 1`, the name;
- `SAVE 1` (10,240 bytes, the map objects' 32-byte records), 12 bytes: the word at +15h of
  records 0 to 3 (the party) is 003Eh in the direct save and FF52h in the window's, and of
  records 43 and 47 003Fh and FFFEh. A picture's slot number while the map is open, the picture's
  own (negative) number once a window has closed the view.

The folder's other files: the direct save wrote `DARKRUN.GFF` and the save file; the window's
wrote those and `CHARSAVE.GFF` (its 62 chunks the same as before: the PREF chunk was there with
the same settings). `DARKSAVE.GFF` was written by neither (991 bytes, its time unchanged).

**Loaded and played on.**

- In the same session, F9 (the LOAD window on QUICK, DIRECT ONE chosen), Return: the party at
  (1672, 344), the figures drawn right, the clock running on from 1481; walked, and followed
  Kurzak (`follow.py 29`), who spoke his two lines.
- The window's save loaded (F2, PAGE 1, row 1, LOAD) and the direct one loaded again: the same
  game both times (Kurzak at square 99,31; the party's squares; hit points; the journal's id 2;
  the clock 1488 and 1489 a few seconds on).
- **From a fresh start with the install's own `CHARSAVE.GFF` and `DARKSAVE.GFF`** (copied from
  `inst/__support/save`, 2,915 and 991 bytes, in place of the save set's): `loadquick.sh 1` loaded
  DIRECT ONE to the same scene (the same squares, clock 1499 after the wait, the journal's id 2).
  A fresh folder with no `DARKSAVE.GFF` at all can't start or load any game (the kit's old
  finding), quick save or not; that was not tried again.
- A fight on a loaded quick save: in 4 below.

**Result: the direct call makes the save the window makes.** The six words are made again by a
load. Nothing of the window's own steps is needed.

## 3. Time, memory and the disk

- **Time**: 0.335, 0.339, 0.335 and 0.335 s from the request to DSCLOG's answer (`qsave.py`,
  polled every 5 ms), the game standing still meanwhile. A fight's request is answered in 6 ms
  ("refused: a fight").
- **Memory** (`heapcheck`, before and after four saves): heap 200 KB with 1 KB free in it; DOS
  memory free after the game 95 KB, the largest piece 97,984 bytes before the first save of the
  session and 95,936 after it and after each later one. No loss from save to save.
- **A nearly full disk**: the game's save (6912Dh) asks DOS for the drive's free space; under
  twice 1,330,000 bytes it shows "Disk Space Low !!!" and under 1,330,000 "Disk Space Very Low
  !!!", each in a box that waits for a click, and then saves all the same. DOSBox 0.74 answers
  for a mounted folder with fixed numbers whatever the real disk holds (`drive_local.cpp`,
  `AllocationInfo`: 512 x 127 x 4,031 free clusters, 262 MB; "always report 100 mb free" its
  comment), so in DOSBox the box cannot come up. **Not run**: a mount with `-freesize` to force
  the box (the Loader writes the mount line; no time was left for a hand-made conf). What the
  Loader does instead: it reads the real folder's free space and asks for no save under 4 MB,
  with a line in the dice log (`test_quicksave`'s `test_disk_nearly_full`). A write that fails
  anyway comes back as "the game could not write SAVQnn.SAV".

## 4. Autosave timing, with scripts running

The rule settled on: **a save is asked for only where the game's own F1 could save**: the top of
the main loop, on the map (DS:0BC9h 1), out of a fight, the loop seen running between two passes
of the dice log; an autosave 4 seconds after the area changed or a fight ended, not while a game
loads, at most one a minute after fights. A script that is running a talk or a message box holds
the main loop, so no save can fall inside it; a script that waits across passes of the loop (a
timer, an escort) is in whatever state the game's own save would save.

- **The fountain's ambush** (`fountain-user`: Pehtucl's speech up as the game loads, the fight
  the moment it is clicked away). With the speech up, F5 did nothing (not counted: DS:0BC9h 2, the
  loop's count standing at 588). The box clicked: `fight_on 1`; F5: "Quick save: not in a fight
  (the game saves none there)", no file; `qsave.py 9`: "refused: a fight". The fight fought as it
  stood (17 steps of Tab and Return). Four seconds after it: `Autosave: "Auto - after a fight -
  Day 1, 00:56" (the QUICK page, slot 6)`, `SAVQ06.SAV`, 89,621 bytes.
  **Loaded from a fresh start** (`loadquick.sh 6`): the party by the fountain at the same squares
  with the same hit points, the bodies on the floor, clock 3409, the journal's id 8; walked
  (`walkto.py 1000 1512`, ARRIVED). No autosave was made for the load.
- **Kurzak's call** (`pens-fire-count4`): two rests at the fire ring ("THE PARTY RESTS"; the
  party's +1Dh stays 1 through it and the clock jumps 8 hours in one pass: not the camp F9
  breaks), then "Gerakis! Get up here! It's your turn in the arena!". F5 with the call pending:
  `Quick save: "Quick - Day 1, 16:25" (the QUICK page, slot 1)`. Then `toarena.sh` to the gap
  ("Enter the arena?").
  **Loaded from a fresh start** (`loadquick.sh 1`, in a second game of this session's own: below):
  the party in the fire room, clock 59151; `toarena.sh` again, and the gap asked "Enter the
  arena?" (it asks nothing before the call): the call was still pending in the loaded game.
- **Into the arena** (Y): region 2Ah, the party at the gate (488, 200). Four seconds on:
  `Autosave: "Auto - The arena - Day 1, 16:28" (the QUICK page, slot 7)`, `SAVQ07.SAV`, 120,490
  bytes.
  **Loaded from a fresh start** (`loadquick.sh 7`, after the pause, with the branch rebased on the
  chance-to-hit and picture work): the party at the gate, clock 59306. Walked in through the bone
  wall's gap and onto the platform: the Announcer ("This day we have a surprise! The 'King of the
  Pens', Scar...") and the bout with Scar and his henchmen began as they should. Fought as it
  stood (`PT_NO_EDIT=1`, 8 steps; Gerakis 3 kills).
- **After the bout**: the Announcer's "Go back to the pens" box and the yes/no question held the
  main loop (DS:0BC9h 2, the loop's count standing still), and no save was made while they were
  up, 20 seconds and more after the fight's end. With them answered: four seconds on,
  `Autosave: "Auto - Day 1, 16:36 - after a fight" (the QUICK page, slot 8)`, made with the
  arena's patience running. **Loaded from a fresh start** (`loadquick.sh 8`): the party on the
  sand at the same squares and hit points, clock 59790. Walking back toward the gate, the arena's
  script took the delay as it does in any game ("Excellent! These gladiators wish to fight
  again!") and started its next bout, which the party, at a few hit points each, was losing when
  the test stopped: the story's scripts ran on from the loaded autosave.
- **Not done**: a save between the waves of the arena's first visit (several fights seconds
  apart). This trip was Scar's, one fight. What covers it: an autosave waits 4 seconds of the
  loop running out of a fight, a wave that starts sooner starts the wait again
  (`test_autosave_after_a_fight`), and a box between waves holds the loop as the Announcer's did
  here. An F5 between waves is a save the game's own F1 could make at the same moment.

## 5. The journal's id in the game's numbers 198 and 199

The journal was running (the dice log's, `Journal/journal.jsonl` emptied first).

- **In the files** (`savediff.py`, `SAVE` chunk 30, words 198 and 199): with the id 2 in memory,
  the direct save and the window's save of the same moment both hold 2. After Kurzak's two lines
  (the id 6), an **F5 quick save** (`Quick - Day 1, 00:26`, slot 5) and a window save 30 game
  seconds later both hold 6. The autosave after the fountain's fight holds 8.
- **By loading**: with the id 4 in memory (two lines said since the save), loading the direct
  save put 2 back (`journal.read_head`), and loading the window's save of that moment put 2 back
  too. The F5 save and the window's save with 6 each loaded with 6 (clock 1583 and 1608, each
  save's own). The autosave loaded from a fresh start read 8.

**Result: a save made by the feature keeps the journal's id exactly as the game's window save
does, and a load gives it back.** The save routine writes chunk 30 whoever calls it.

## Other things seen

- **The QUICK button** fits under PAGE 4 in the window (the picture in the SAVE window, with four
  quick saves' names in the rows: "Quick - Day 1, 00:25" fits a row with room to spare).
- **F9**: the LOAD window on the QUICK page, the newest save's row chosen, LOAD ready; Return
  loads it.
- **"Quick save" floats over the leader** for a moment (seen with the party in view).
- **Rotation**: the quick saves went to slots 1 to 5 as they were empty, then to the oldest (slot
  2); the autosaves to 6 and 7.
- **A window save landed on the QUICK page**: after F9's window the page stayed QUICK, and the
  next F1 save was written to `SAVQ01.SAV`, a slot the rotation writes over. Now the window never
  opens on QUICK by itself: with the window shut, the Loader makes a page left on QUICK the page
  of 1 to 4 shown last. **Seen in the game**: a game loaded from the QUICK page at the main menu,
  then F1: the SAVE window opened on PAGE 1.
- **Names in the rows**: a row shows about 32 letters. "Auto - The arena - Day 1, 16:28" just
  fitted and "Auto - after a fight - Day 1, 00:56" lost its last letters, so an autosave's name
  now has the time first ("Auto - Day 1, 16:36 - after a fight"): what a long name loses in the
  row is the end of the place.
- **No autosave for a load**: none after any of the loads above.
- **Water**: no new area was reached (the pens and the arena's gate only).

## A second game beside the shared one

The shared DOSBox's lock was held by a DOSBox another session had left running (started under
`flock`, it kept the lock's file open after its script ended; nothing was driving it, and that
session's next script was itself waiting on the lock). It was not this session's to stop. The
rest of 4 was played in a second game instead (approved by the project manager), apart from the shared one in every way: a copy
of the kit and of the game in the session's scratch folder, its own Xvfb (`:56`), DOSBox copied
under another name (`dbq`: the shared kit's tools find DOSBox by the name and `start.sh` kills
every `dosbox`), its Loader and DOSBox found by pid files, the tree's Loader and helper.
`buildcheck.py` OK there.

## What is not verified in the game

- a save between the waves of the arena's first visit (4);
- the game's camp, where F9 is the game's (1);
- "Disk Space Low !!!" forced with a small `-freesize` mount (3);
- the two switches switched in the Loader's window (unit tests and the window's tests only); the
  game started from the `.bat` without the window; GOG's DOSBox with its `cloud_saves` folder
  (the Loader looks there first for the slots' files, unit-tested; Linux's DOSBox has no overlay
  mount).
