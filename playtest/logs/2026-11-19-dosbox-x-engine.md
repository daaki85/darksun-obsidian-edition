# 2026-11-19: DOSBox-X as the Loader's other engine

Under test: the game started in DOSBox-X by the Loader itself (the Options tab's Engine;
`dsloader/dosboxx.py`, `process.FileMemory`), further than [the experiment](2026-11-18-dosbox-x.md)
went. The build: this branch on `obsidian-edition` after 2.19.0 (DSCLOG `DSCLOGve`, 70,304
bytes). DOSBox-X 2026.10.01, SDL2, Linux 64-bit, the experiment's own build. DOSBox 0.74 for the
comparisons is Ubuntu's 0.74-3, copied as `db74`, with GOG's configuration and the Loader's.

Everything ran in a game of its own: display `:59` (Xvfb 1600x1000; `:58` with openbox for full
screen), its own work folder and copy of the game folder, and this worktree's `obsidian-edition`
(its own `settings.json`). No memory was edited at any point (the fight was fought with
`PT_NO_EDIT=1`; `squarewalk.py` without points), so the quick saves and autosaves made are saves
of the game as played. Only processes this session started were stopped, by pid.

## How the game was started

Three ways, all through `launch.launch` with `engine` "dosbox-x" and `dosbox_x_path` in
`settings.json`:

1. **`python3.12 -m dsloader play`** (no window; the dice log inside): `play.log` says "Starting
   Shattered Lands from ... in DOSBox-X (.../dosbox-x)". `game.lock` has three lines: the
   Loader's, `game PID dosbox-x`, `memory /dev/shm/obsidian-edition-5b3e330de8.mem`; the file is
   33,554,432 bytes, mode 0600.
2. **A few lines of Python calling `launch.launch()` and then `launch.release_game()`**, and then
   `python3 -u -m dsloader dicelog > dice.txt` with no `--pid`: the command found the game by
   the lock file's memory line and said "Dice log attached." The kit's tools that read
   `dice.txt` need this way.
3. **`python3.12 -m dsloader launch`** (the Loader's window): its status line reads "Connected
   to the game (DOSBox-X, process 15494, through its memory file
   /dev/shm/obsidian-edition-5b3e330de8.mem)" and the dice pane "Dice log attached."

`dbxadopt.sh` put the game's pid in `dsun.pid` for the kit each time; every tool then read the
same file the Loader did.

## What was seen

| What | Seen |
|---|---|
| The build in place | `buildcheck.py`: OK (every routine the EXE's, the vectors at their handlers, the tail's data), at the start and after 21 minutes |
| Memory | `memaudit.py`, the slave pens, the map open: load segment 0224h, 96,928 bytes free after the game (0.74: 99,008), `far_seg` FFFFh (the HMA), DSCLOG at CC4Bh, the overlay buffer at DD84h, 16,496 bytes of upper memory free. The same after 21 minutes. "Out of memory in OEOpenGraph" never appeared |
| Quick save | F5 (the key, `xdotool key`): `SAVQ01.SAV`, 85,680 bytes; five of them after the long play |
| Quick load | the party walked to (1576, 344); F9 opened the LOAD window on the QUICK page ("Quick - Day 1, 00:22"); Return: the leader back at (1672, 344) |
| Alt's marks | Alt held: BIOS flag 08h, 2 rings, 1 name ("Legcrusher" over him, a gold ring); let go: none. 26 times in the long play, the same each time |
| A rest | `pens-after-scar`, the fire room's ring, twice: "THE PARTY RESTS", "Gerakis rests 8 hours: +3, +6 (CON 22) = +9 (+0: no more than the most), now 54/54 HP" and the other three's lines, then Kurzak's call ("Gerakis! Get up here! It's your turn in the arena!") |
| An area change | the walk to Kurzak's door and into the gap, "Enter the arena?", Y: region 2Ah, the leader at (488, 200) |
| An autosave, loaded | 4 s after arriving: "Autosave: "Auto - Day 2, 17:01 - The arena" (the QUICK page, slot 6)", `SAVQ06.SAV` 120,492 bytes. The party walked to (504, 216); F9, row 6, LOAD: back at (488, 200) |
| A whole fight | `fountain-user`: Pehtucl's speech, the ambush, eight rounds fought with no edit (`PT_NO_EDIT=1 sh fightout.sh`): 391 lines of dice log (hiding and moving silently, each attack with its THAC0 sum and "needs N+ (P%)", damage with its parts, saves against poison, XP, each round's initiative, "Templar is killed", a Guard and two Arena Guards killed). **The party lost** ("YOUR PARTY HAS BEEN DEFEATED"), the tally was printed ("Ester: 8 of 18 attacks hit, 118 dealt, 3 kills, took 26"), and the game went to its main menu. A defeat makes no autosave, so the autosave after a fight was not seen |
| The chance to hit, Tab | a red ring under the Templar and "Chosen with Tab: Templar (41 HP), Bone Hayneedle +1 needs 12+ (45%); Metal Shadowseeker +1 needs 11+ (50%); Leather Sling needs 11+ (50%) - Enter attacks it"; the swings after it in the fight carry the same form ("d20 = 14, needs 11+ (50%)") |
| The chance to hit, under the pointer | the pointer on the Templar (the panel hidden first: it covered him): "12+ (45%)" over him (`hoverlabel.py`: slot 0, thing 25) |
| The combat log's panel | L (`panel.sh show`): the panel with "Needs 12+ (45%)" in its header, the Short level, the last lines |
| Squares in reach, R | a cross on each square Seneca could reach; R: "Squares hidden" over the party and the crosses gone, "Squares in reach: hidden (R shows them)" in the log; R again: back |
| F10 | Seneca walked from square (55, 96) to (57, 93), her points 120 to 76; F10: back at (55, 96) with 120; she walked again, to (56, 93). After the **last** step (the mod's own part of F10) was not tried |
| The Loader's window | the Characters tab with the party's portraits and sheets read through the file; the Journal tab with 25 entries from the play; Show: Quests listed none while the game ran (this save has none given; not held against 0.74) |
| Twenty minutes | 21 min 37 s with the window attached: 26 passes of 45 s walking the party back and forth (18.1 to 19.0 frames a second, 142 to 146 map units a second, DOSBox-X at 20% of a core), Alt held after each, F5 every fifth. The game and the Loader ran throughout; `buildcheck.py` OK and the memory unchanged at the end |
| The game ended by its own QUIT | Escape, QUIT: `GAMEOK.TXT` written, DOSBox-X gone 4.3 s after the click, **the memory file and `game.lock` gone 0.1 s later**, the status line "Disconnected (DOSBox-X (process N) has closed). Waiting for the game...", no crash report |
| DOSBox-X killed mid-game | `kill -9`: collected within half a second; memory file and lock gone 2.5 s after the kill; status "Disconnected (DOSBox-X (process 18816) has closed)"; `crash-logs/crash-2026-11-19-233515.txt`: "DOSBox-X closed: it was ended by signal 9 (killed).", "The game didn't end on its own: ...", the game's memory, `engine: 'dosbox-x'` among the switches, "DOSBox's output (dosbox-x.log):" with DOSBox-X's own lines, the dice log's last lines |

## What the play changed in the code

- **The pointer went three times too fast down the screen in a Triple window.** With the mouse
  captured, the hand moved 60 pixels each way: 0.74 moved the game's pointer 20 across and 16
  down; DOSBox-X with `sensitivity=33` 20 across and **48** down. DOSBox-X reads a second number
  for the speed down; with `sensitivity=33,33` it was 20 and 16.
- **Plain at Triple and Quadruple drew an empty grey window** (`output=surface` with `normal3x`
  or `normal4x`; 2x, and scan3x and tv3x, draw). Through `output=openglnb` both draw, every
  pixel a block. The first grabs, at the dark SSI logo, showed nothing wrong.
- **After the game's own QUIT the Loader read on from the file for seconds.** With DOSBox-X gone
  at 4.3 s, the status line still said Connected, the memory file and the lock stayed until
  20.6 s, and at 7.3 s the Journal's kept quests reading (`Journal/quests.json`) was written
  from what the game had left in memory (a quest "finished" that wasn't). A closed process's
  memory can't be read; a file can. The window now lets go of the file as its DOSBox-X closes,
  and `FileMemory` asks after the process at every read. The same end again: file and lock gone
  at 4.4 s, the kept reading untouched.
- "GOG's own" speed is 8,000 cycles on the normal core (7,000 walked slower than 0.74's).

## The window and the pictures

Every size and picture, started with the kit's script (`window_scale=N picture=P`), two clicks
to the main menu, a grab of the display:

| | Window | Seen |
|---|---|---|
| Single | 320x240 | plain |
| Double, plain and TV | 640x480 | blocks; TV's dimmed lines |
| Triple, plain (after the change), scanlines, TV, sharp | 960x720 | blocks; a black line under each row; a dimmed one; hard-edged pixels |
| Quadruple, plain (after the change), scanlines, sharp | 1280x960 | blocks; the 2x scanlines doubled, whole dark lines; hard-edged |
| Full screen, plain, scanlines, sharp (openbox, a 1280x720 screen) | 1280x720 | the picture 942 pixels wide in each, as in the 960x720 window: 4:3, black at the sides |

On a bare Xvfb full screen does nothing to see (the window stays 640x400 while the log says
"switched to full screen mode"): SDL2 wants a window manager.

## Speed

`framerate.py 20` from `pens-after-arena`, the whole party walking, everything on, a fresh start
for every run, both engines in turn in one session. Surface output, 320x240, Xvfb, no sound
device.

| Engine, core, cycles | Frames/s | Undrawn (steady pace) | Steps run / lost | Walking, map units/s | Host CPU |
|---|---|---|---|---|---|
| 0.74, GOG's own (`core=auto`: normal, 7,000), two runs | 6.4, 6.0 | 16.5, 16.6 | 44 / 35, 46 / 33 | 97, 102 | 14%, 13% |
| 0.74, dynamic 20,000 | 15.4 | 3.6 | 68 / 26 | 113 | 20% |
| 0.74, dynamic 35,000, two runs | 18.8, 18.9 | 0.1, 0.2 | 81 / 13, 81 / 14 | 139, 142 | 28%, 26% |
| DOSBox-X normal 7,000 | 6.1 | 17.1 | 42 / 38 | 91 | 15% |
| DOSBox-X normal 8,500 | 7.1 | 15.8 | 49 / 33 | 99 | 15% |
| DOSBox-X normal 10,000 | 7.7 | 14.3 | 58 / 31 | 106 | 16% |
| DOSBox-X dynamic 20,000 | 14.2 | 4.9 | 67 / 26 | 114 | 15% |
| DOSBox-X dynamic 22,000 | 15.2 | 3.9 | 67 / 26 | 114 | 16% |
| DOSBox-X dynamic 24,000 | 15.9 | 3.1 | 68 / 26 | 113 | 17% |
| DOSBox-X dynamic 40,000 | 18.4 | 0.6 | 78 / 17 | 133 | 22% |
| DOSBox-X dynamic 42,000 | 18.8 | 0.3 | 81 / 14 | 141 | 23% |
| DOSBox-X dynamic 44,000 | 18.9 | 0.2 | 83 / 12 | 141 | 22% |

The BIOS clock and the game's clock kept real time on both engines (18.0 and 95 a second at the
faster settings; 16.8 and 89 on both at GOG's own, where the game is short of time).

**The Options tab's three speeds on DOSBox-X, through the Loader's own start** (the settings'
`cycles` "gog", 20000 and 35000; what was written and how it walked):

| Game speed | Written | Frames/s | Undrawn | Steps run / lost | Walking, map units/s | 0.74 at that setting |
|---|---|---|---|---|---|---|
| GOG's own (two runs) | `core=normal`, `cycles=fixed 8000` | 6.5, 6.8 | 16.1, 16.0 | 50 / 33, 49 / 34 | 99, 97 | 6.4, 6.0 frames; 97, 102 units |
| Faster | `core=dynamic`, `cycles=fixed 22000` | 15.2 | 3.7 | 67 / 26 | 114 | 15.4 frames; 113 units |
| Fastest | `core=dynamic`, `cycles=fixed 42000` | 18.7 | 0.3 | 81 / 14 | 142 | 18.8, 18.9 frames; 139, 142 units |

## The memory file test

`python3 dosboxx_memtest.py /path/to/dosbox-x` (no game), here on Linux:

```
its version: 2026.10.01
the memory file: /dev/shm/dosboxx-memtest-21487.mem
DOSBox-X started (process 21489), core=dynamic
1 found: yes. The file is 16777216 bytes (16 MB), the program at 0x8242.
2 read by file read/write: yes, the count is seen going up
2 read by mapping: yes, the count is seen going up
3 write by file read/write, read back by file read/write: yes
3 write by file read/write, read back by mapping: yes
3 write by mapping, read back by file read/write: yes
3 write by mapping, read back by mapping: yes
4 hold: held still, the count stands; let go, it runs again; a write made meanwhile is there
5 code: the instruction made "do nothing": the count RUNS ON (stale code: expected on a dynamic core, and the same in DOSBox 0.74); put back, it runs
6 the file, while DOSBox-X runs and this script has it open: it could be removed (its name is gone; DOSBox-X keeps its memory)
6 the file, after DOSBox-X closed: already gone
the file read/write way works: yes; the mapping way works: yes; holding DOSBox-X still works: yes
RESULT: PASSED. A second program reads and writes DOSBox-X's memory through the file here, the way the Loader does on this system.
```

With `normal` after the path (DOSBox-X's normal core), line 5 reads "the count stops (the change
is acted on at once)". It is the script for the owner to run on Windows and on macOS (its header
has the instructions): there nothing has been run.

## Water

The slave pens and the arena only: nothing new.

## Not seen

- Windows and macOS: nothing was run there.
- An autosave after a fight (the fight was lost); F10 after the last step; a won fight's XP and
  loot; spells cast in a fight; shops, the inventory, the creation screen; a talk beyond
  Kurzak's and Pehtucl's speeches.
- Sound: no sound device here (`SDL_AUDIODRIVER=dummy`), so no music, FluidSynth and the
  soundfont setting among it, was heard or rendered in this session (the experiment rendered the
  title's music to a file).
- Full screen on a real screen; a graphics card's OpenGL (Mesa's software renderer here).
- A packaged DOSBox-X (Flatpak, Snap), the Steam Deck, any version but 2026.10.01.
- The same checks side by side on 0.74 beyond speed and the pointer (the fight lost here was not
  fought on 0.74 for comparison).
