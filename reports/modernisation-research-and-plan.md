# Modernising the game further: research and plan

Research of 2026-11-16 into nine additions the owner chose, and the plan that follows from it.
Everything here was read from the mod's code, the two games' files and the DOSBox sources;
**nothing was run in the game**. "Verified" means read in source or disassembled; the rest is
marked inferred or unknown, and each item lists the experiment that settles it. DSUN.EXE numbers
are file offsets unless written `segment:offset`.

## What the research changed

- **No memory pass is needed.** All the helper work together is about 250-300 bytes of the
  segment's 960 spare and about 136 bytes of the tail's 1.3 KB. The far block (36 bytes) is not
  used.
- **F5 and F9 are already keys of the game** on the map (its key table at file 1BC5Bh: F5 to
  1B811h, F9 to an overlay at 810DCh). What they do is not established.
- **A save just before a story fight is risky**: it would be taken inside the script that starts
  the fight, and the script interpreter's state was not seen among the things a save writes.
  Autosave on entering an area and when a fight ends instead.
- **GOG already plays General MIDI** (SOUND.CFG: `mt32mpu.adv`, music type 4), through Windows'
  own synth. The gain is a better synth (a soundfont) or a real MT-32 score, not a new device.
- **DOSBox-X can keep the game's memory in a shared file** (`[dosbox] memory file=`), which
  DOSBox Staging can't. The Loader could map that file instead of reading another process: the
  only practical route to macOS, and a way round sandboxes on the Steam Deck.
- **Wake of the Ravager is the same engine a year on**, smaller in maps and larger in script
  than Shattered Lands; about 40% of the mod's code patch sites are recognisable in it.

## 1. Quick save, quick load, autosave

**Findings**
- More saves: the page is one letter poked into two game strings (DS:1DCFh `SAVE??.SAV`,
  DS:1DDAh `SAVE%.2d.SAV`; `sp_page`, `sp_letters db 'EBCD'`, `PAGES equ 4`). A fifth page is one
  letter in the helper, a fifth button in `savepages.py`, and `PAGES` and the copy pattern in
  `namedsaves.py`.
- The game's save is the overlay entry 560:89 (file 6912Dh), `save(far char *file, far char
  *description)`: checks disk space ("Disk Space Low !!!" under about 1.33 MB), writes the SAVE
  chunks and STXT 1 into DARKRUN.GFF and copies it to `file`. It reads nothing from the save
  window. The window's wrapper (7468Bh) adds an optional 11-byte PREF chunk.
- Load is 560:8E (69218h). The window's overlay has entries that open LOAD (590:20) and SAVE
  (590:25) with no arguments.
- The game refuses a save only in a fight (word 377E:0019h; "CAN'T SAVE DURING COMBAT", 714E5h).
- The helper's main-loop hook `PROBE_SCROLL` already serves Loader requests (`sound_req`,
  `view_redraw`, `panel_on`) and the helper already calls an overlay stub (`give_xp`).
- Keys: `our_key` in the INT 16h hook; a counted key costs 10-65 bytes.
- The Loader sees the region (DS:117Ch) and the fight flag within 50 ms, at no helper cost.

**Design** (helper: about 110-130 bytes)
- The Loader holds the policy: ten slots on a page Q (`SAVQ01.SAV`...), the name ("Quick 3 -
  Day 47, 14:20"), rotation, autosave on a new area once its item lists settle and when a fight
  ends, never with a window up; what happened goes to the dice log and a floating name.
- The helper gets two counted keys, one "save now" request in `PROBE_SCROLL` (the two strings
  written by the Loader into `pick_text`), and the fifth letter.
- Quick load opens the game's own LOAD window on page Q (590:20) rather than calling 560:8E, which
  would skip the window's steps.

**Experiments, in order**
1. What F5 and F9 do in the unmodded game. If either matters, use other keys.
2. A save by 560:89 called from `PROBE_SCROLL`, compared chunk by chunk with a window save of the
   same moment, then loaded and played on (the window runs 1587:22BA, 1587:2CCB and 191F:0B36
   first; their part is unknown).
3. How long a save takes (85,680 bytes), and memory at that moment (`heapcheck`).
4. Whether rotating slots are copied to `Named saves` at all.

**Tests like**: `test_savepages`, `test_namedsaves`, `test_dsclog` (Unicorn), `test_gamepatch`,
`test_loot`.

## 2. Showing what can be used

**Findings**
- `ring_pass` rings every thing in the draw list whose `RING_TAB` byte is set (520 entries, no
  limit on how many) and never tests the kind: items, bodies and scenery can be ringed if they
  are in the draw list.
- The ring's colour table (`RED`, 256 bytes) is written by the Loader, so another tint costs the
  helper nothing, but the Tab ring shares it. A true second colour is 256 bytes in the tail and
  about 30 of code.
- Floating names: 4 slots; each more costs 360 bytes of upper memory, so 3 more at most.
- The Loader can read the BIOS shift flags (0:0417h; Alt is bit 3) every 50 ms. Alt alone sends
  the game no key.
- The Loader can list things (table at load+3972h:0C36h), items and their types (+08h = 60h is
  scenery), bodies (objects 1101 and 2666), creatures, and doors as squares.
- Unknown: where the game keeps which objects have a script. Fallback: read the region's MAS
  script with `gpl.py`.

**Design** (helper: 0 bytes)
- While Alt is held outside a fight, the Loader rings doors, containers, bodies, ground items
  and people in a gold tint, and names the four nearest the pointer.

**Experiments**
1. Whether doors and ground items are in the draw list, and where a ring falls on them.
2. Frame time with 20-30 rings.
3. A stuck Alt flag after Alt+Tab.

**Tests like**: `test_targeting`, `test_labels`, `test_shadows`, `test_dsclog_drawing`.

## 3. The journal

**Findings**
- `textlog.py` already captures every dialogue, the reply chosen and every message box; the
  Dialogue tab shows them with a find bar, 3,000 lines at most, and nothing is kept on disk.
- Speaker names are learned, not stored by the game; the area is a number only (a table of the
  34 regions' names has to be written); the game's day and time are known.
- Quest state: 754 global flags in use (all 808 are taken) and 137 global numbers of 200. Quest
  XP goes through script 74 (57 call sites in 40 scripts, 78,510 XP: about 45-55 rewarded
  steps); 37 of the 57 set a flag within a few commands. All talk is inline in the scripts, so a
  tool can draft a table of flag, script, nearby text and XP.
- "... receives N experience points!" already passes through the text buffer.
- Loads: the Loader misses a later save of the same party loaded mid-play (DEVELOPMENT.md).

**Design** (helper: 0 bytes)
- `journal.py`: an append-only file of entries (id, parent, day and time, region, speaker,
  text, reply, XP), fed by the dialogue and message boxes.
- The newest entry's id is kept in two spare global numbers (198-199), which the game saves:
  when the id in memory differs from the last written, a save was loaded, and the journal shows
  that save's branch. Old saves fall back to cutting at the clock.
- A Journal tab: by day, person and area, with the find bar and a filter.
- Later: open and finished quests from a table of the project's own wording, drafted by a tool
  from the scripts and named by hand (a day or two).

**Experiments**
1. That numbers 137-199 survive save and load and no engine code touches them.
2. How often the numbers pointer is null (the Loader must wait and retry).

**Tests like**: `test_textlog`, `test_namedsaves`, `test_flagrange`, `test_audit_flags`,
`test_gpl`, `test_viewer_settings`.

## 4. Chance to hit before the swing

**Findings**
- `GameData.weapon_hits` already gives THAC0 for each ready weapon before a target is known
  (strength or dexterity, effects, the weapon, two weapons, kits, specialisation).
- The target's side is in `_thac0_breakdown` (Blur, a held target, "can't see"...), and AC in
  `counted_ac` or, once attacked, `last_ac`.
- The Loader knows whose turn it is and who is chosen (`targeting.py`).
- Missing: the target's facing (from behind and backstab), a not-yet-attacked monster's AC as
  the game counts it, and which weapon swings at range.

**Design** (helper: 0 bytes)
- `predict(attacker, target)`, shown on the Tab line ("needs 14+ (35%)") and in the panel's
  header. Where a term is unknown, say so ("14+, less from behind") rather than guess.

**Experiments**
1. Predictions against the log's own "needs N+" over several fights, by kit and weapon.
2. Where the facing is kept.

**Tests like**: `test_targeting`, `test_combatlog`, `test_dicelog`, `test_ledger`.

## 5. Where a figure can walk this turn

**Findings**
- Movement points are Move x 10 a turn (a word for each combatant, 37BD:022Bh). A step costs 10
  straight and 14 diagonal (table at DS:055Ch; the one `sub` at 59194h). Under 10 left is
  zeroed.
- The grid is 128 x 98 squares of 16 pixels, live at the far pointer DS:0556h; bit 80h blocks.
- Not read: the path finder's own test (22339h) for edges, doorways, corners and allies.
- No existing channel draws at arbitrary squares: rings, shadows and names all belong to
  things.
- A blow covers the 8 squares round each of the attacker's squares; with a polearm, also those
  2 away in a clear line.

**Design** (helper: about 100-150 bytes in the segment, about 136 in the tail)
- The Loader works the squares out (shortest paths at 10 and 14 on the live grid, within the
  points left) and writes a 32 x 32 bitmap; a new `tint_pass` after `ring_pass` marks each set
  square with a few tinted dots through the ring's own routines (a solid fill would be slow).
- Second step: the squares enemies' blows cover, in another pattern.

**Experiments**
1. The path finder's rules, by disassembly and then in a fight.
2. Whether attacking ends movement.
3. Drawing time.

**Tests like**: `test_dsclog_drawing`, `test_shadows`, `test_reach`, `test_stuckwalk`,
`test_fits_upper_memory`.

## 6. Music

**Findings**
- The game has three scores for each tune: General MIDI (GSEQ), MT-32 (LSEQ) and PC speaker.
  The choice is in `SOUND.CFG` (59 bytes). The mod's sounds and music buffer don't depend on it.
- GOG's DOSBox 0.74 has no built-in synth: music goes to a Windows MIDI device
  (`midiconfig=` picks which). DOSBox Staging and DOSBox-X have FluidSynth (a soundfont) and
  MT-32 emulation (the player's own ROMs) built in.
- Soundfonts: GeneralUser GS is about 30 MB under its own permissive licence; smaller and larger
  free ones exist. Licences need a second look before anything is bundled.

**Design**
- Now: a choice of Windows MIDI device on the Options tab.
- With a second engine: a soundfont picker (one named in the docs, not bundled), and MT-32 by
  writing a changed copy of SOUND.CFG.

**Experiment**: run the game's SOUND program choosing MT-32, then General MIDI, and compare the
two SOUND.CFG files.

## 7. Picture

**Findings**
- The Loader offers full screen or a window at 1x to 4x.
- 0.74 can also do scanlines (`scan2x/3x`, `tv2x/3x`) and a sharp OpenGL output (`openglnb`).
  It has no whole-number scaling in full screen, no borderless window and no shaders.
- Staging: `integer_scaling`, `shader=crt-auto` or `sharp`, `fullscreen_mode=forced-borderless`.
  DOSBox-X: `output=openglpp`, `glshader`.

**Design**: scanlines and sharp now; whole-number scaling, borderless and CRT with the second
engine. **Experiment**: one picture of each new mode at 3x, checking the pointer still tracks.

## 8. A second engine, Linux, Steam Deck, macOS

**Findings**
- The Loader finds the game's memory by the BIOS date and the interrupt table, which Staging
  and DOSBox-X write the same way (untested on either).
- Staging's upper memory and missing HMA match 0.74's, so the helper should load as now.
  DOSBox-X has a real HMA and movable upper memory: to be measured.
- The Loader insists on `DOSBOX/DOSBox.exe` in the game folder; `--recompiled` already shows the
  pattern for starting another program. For another engine the Loader should write a whole
  configuration of its own.
- Fixed cycles on another build won't give the same speed: steady pace needs measuring again.
- Linux: the Loader's memory reading, patched game and configuration already work
  (`playtest/start.sh` is in effect a Linux start). With DOSBox started as the Loader's child,
  no root should be needed (Yama allows a parent its descendants; not testable in a container).
  The distribution's 0.74-3 has no overlay mount: the starting saves must be copied.
- Steam Deck: tkinter on SteamOS and a Flatpak DOSBox are unknowns. A Steam Input layout
  (trackpad as mouse, buttons as the mod's keys) is sturdier than DOSBox's mapper. Use the
  start without the Loader's window in Gaming Mode.
- macOS: reading another process is not practical for an unsigned program. Only the
  memory-file engine gets there.

**Design**
- Engine choice on the Options tab: GOG's (default) or a DOSBox-X the player has installed, the
  Loader mapping its memory file. Staging only if DOSBox-X fails.
- `start.sh` for Linux beside the `.bat` files; a Deck layout; macOS after, if someone can test.

**Experiment**: the mod's configuration under DOSBox-X with a memory file: map it from Python,
find the BIOS date and the helper's header, read one dice-log line, and write one byte the game
then acts on (the dynamic core may cache code the Loader patches).

## DOSBox-X: what was found

The experiment of section 8, run on 2026-11-18 (Linux; DOSBox-X 2026.10.01, SDL2, built from
source in 6 minutes). Everything measured is in
[the log](../playtest/logs/2026-11-18-dosbox-x.md). The experiment's own branch was not merged;
its code was carried into the engine built from it the next day ([what was built](#dosbox-x-what-was-built),
below), and this section is kept as the experiment wrote it.

**Verdict: viable, with these changes.** The mod ran under DOSBox-X with the game's memory in
a shared file and no access to DOSBox-X's process: the helper loaded high and took the HMA, the
game had 2 KB less conventional memory than on 0.74, the dice log attached through the file,
read the party, wrote to it and printed Kurzak's speeches, a quick save asked for through the
file was made, and the playtest kit drove the game unchanged. Nothing in the helper has to
change. One risk the research named turned out to exist already on 0.74 (code patched from
outside on a dynamic core), and one was new (the file is cut and made again at each start).

**The configuration that worked** (whole, nothing of GOG's; `dosboxx.conf_lines` writes it):

```
[sdl]      fullscreen=false  output=surface  showmenu=false  autolock=true  autolock_feedback=none
           middle_unlock=none  clip_mouse_button=none  sensitivity=100  windowresolution=original
[dosbox]   machine=svga_s3  memsize=32  memory file=PATH  quit warning=false
           fastbioslogo=true  startbanner=false
[render]   aspect=true  scaler=none  doublescan=false
[cpu]      core=dynamic  cputype=auto  cycles=fixed 42000
[sblaster] sbtype=sb16  sbbase=220  irq=5  dma=1  hdma=5
[midi]     mpu401=intelligent  mididevice=none | fluidsynth (fluid.soundfont=FILE)
[dos]      xms=true  ems=false  umb=true  minimum mcb free=100  kernel allocation in umb=true
[config]   dos=umb
[autoexec] mount c GAME; mount d DOS_DIR; c:; d:\umbplus.com; lh d:\dsclog.exe; d:\dsunlog.exe;
           d:\gameend.com; exit
```

started as `dosbox-x -conf FILE -nopromptfolder -nomenu -fastlaunch`. Why each line is there:

| Setting | Without it |
|---|---|
| `memory file=PATH` | (the point) 32 MB, sparse, made at start; tmpfs and a disk folder both work |
| `irq=5` | DOSBox-X's default is 7: the game stops, "DSP Detect Fail" |
| `dos=umb` (not `high, umb`) | DOS takes the HMA; the helper's far block goes into upper memory and the game's overlay and music buffers and the see-through tables into its 640 KB |
| `minimum mcb free=100`, `kernel allocation in umb=true` | the game loads at 0824h, not 0224h: 26.7 KB less conventional memory than on 0.74 (72 KB free with the map open, not 97) |
| `ems=false` | as on 0.74 (not tried with it on) |
| `middle_unlock=none`, `clip_mouse_button=none`, `autolock=true` | the middle button unlocks the mouse: no map drag |
| `doublescan=false`, `aspect=true`, `scaler=none` | a 640x480 window for scale 1 |
| `cycles=fixed 42000` on `core=dynamic` | 35,000 walks 13% slower than 0.74's 35,000; 42,000 matches it (18.6 frames a second, 143 map units a second, the same steps run and lost) |

**What was found, experiment by experiment**

1. The unmodded game starts with a configuration of our own; the file is `memsize` bytes, is the
   guest's RAM from offset 0 (BIOS date, interrupt table), on tmpfs and on ext4.
2. `guestmem.locate` finds it unchanged through a file backend (one region, base 0); reads are
   live. No pid is needed, except to hold the game still for the item lists' gate (a signal).
3. The helper loads into upper memory at CC4Bh (DOSBox-X's block is CC00h-F000h, 144 KB: 16 KB
   more than plain 0.74's, 12 KB less than 0.74 with `UMBPLUS.COM`, which does nothing here),
   takes the HMA through XMS, and the game's buffers follow it into upper memory. With the two
   `[dos]` lines the game has 96,928 bytes free with the map open (0.74: 99,008).
4. The dice log attaches, repairs two items (writes) and prints dialogue. No fight was played.
5. Data written through the file is acted on at once on every core. **Code** written through
   the file is acted on at once on `core=normal`; on the dynamic cores, code that has already
   run can go on running as it was (the game's own code did; a tight loop did; the helper's
   did not). **DOSBox 0.74's dynamic core, the mod's engine today, does the same through
   process memory** (stale in the helper and in the game), so the mod cannot depend on it now
   and the memory file adds no risk here.
6. Speed: the table in the log. `core=normal` costs about twice the host CPU for the same pace.
7. FluidSynth loaded a soundfont and rendered the title's music (to a file: no sound device
   here); it plays through its own sound driver, not DOSBox-X's mixer. `openglpp` scales 5x6
   in a 1600x1200 window (whole pixels, 4:3) and 3x3 in 960x720 (not 4:3); a CRT shader file
   loads with `output=opengl`.

**What the Loader would need**

- **An engine choice** (`settings.json`: `engine` "gog" or "dosbox-x", `dosbox_x` its path),
  as `recompiled` is chosen today: `launch._launch` branches, `is_game_dir` accepts a game
  folder without `DOSBOX/DOSBox.exe` when DOSBox-X is the engine.
- **A memory backend**: `FileMemory` beside `ProcessMemory` (60 lines, written; `pread` and
  `pwrite`, not a mapping: DOSBox-X truncates the file at each start and a mapping read then
  would kill the Loader). `connect` takes the file when the engine is DOSBox-X; the viewer's
  status line and `reconnect` (`guest.proc.pid`) need the pid from the process the Loader
  started. The Loader names the file itself (the temp folder, or `/dev/shm`), one per game
  started, and deletes it when DOSBox-X ends (DOSBox-X leaves it).
- **Conf writing**: `dosboxx.conf_lines` as the start; the display, scale, picture, speed and
  music settings each need their DOSBox-X spelling (`display_lines`, `cpu_lines`,
  `midiout.conf_lines` are 0.74's), and the cycles a table per engine and core (42,000 and
  about 22,000 for `dynamic` on x86; `dynamic_rec` differs). `conf_encoding`'s code page rule
  and the overlay mount for `cloud_saves` were not tried.
- **Process finding**: none with the file. `find_dosbox_processes` already matches `dosbox-x`
  by name, which matters only without the file.
- **Helper layout**: nothing. Optional: teach `UMBPLUS.COM` DOSBox-X's chain (12 KB).
- **The crash and freeze reports** read DOSBox's `stdout.txt`/`stderr.txt` and exit codes as
  0.74 on Windows gives them: to be looked at for DOSBox-X (it logs to stdout; `log console`
  puts the game's last DOS text there, which `GAMEEND.COM` does today).

**Risks**

- **Windows and macOS were not run.** The memory file is mapped by different code on Windows
  (`CreateFileMapping`); whether a second program may open the file for reading and writing
  there while DOSBox-X holds it, and whether file reads see the mapping's pages at once (they
  do on Linux and should on macOS, one page cache), must be tried first. On Windows the Loader
  keeps 0.74 and process memory anyway; the file matters for macOS and sandboxed Linux.
- **The option is young** (2025.01.01) and its source comments say an interface for other
  programs is unfinished ("there needs to be an API here to flush modified pages"). Packaged
  DOSBox-X on a player's system may be older than it (Ubuntu 24.04's is): the Loader must check
  the version, and say so.
- **Code patched from outside on a dynamic core** (above). If a feature ever needs it: the
  helper makes the write, or that engine runs `core=normal`.
- **The file on a disk** is written back by the system as the game changes memory; keep it on
  tmpfs or the temp folder. It holds the whole game's memory, readable by the player's user
  only (mode 0600).
- **Speed is per engine, per core, per version**: a DOSBox-X update can move the pace.
- A long play, fights, rests and region changes under DOSBox-X were not played.

**Effort**: the engine choice, the backend wired through the viewer, the conf writer with the
Options tab's settings, tests and a play check on Linux: about a release's worth beside other
work (the experiment's code is perhaps a third of it). Soundfont choice and whole-number
scaling are then settings in that conf. macOS needs someone with a Mac. The Steam Deck needs
a DOSBox-X new enough inside or beside its sandbox, which this did not look at.

**Build first**: (1) on Windows and on a Mac, the 30-line check that a second program can read
and write the memory file while DOSBox-X runs (`playtest/codeloop.py` is nearly that); (2) then
the engine choice with `FileMemory` and the conf writer on Linux, behind a setting, 0.74 staying
the default.

## DOSBox-X: what was built

2026-11-19, from the experiment above: DOSBox-X as an optional engine, chosen on the Loader's
Options tab, GOG's DOSBox 0.74 the default and untouched. The player's page is [the
engine](../obsidian-edition/FEATURES.md#the-engine-gogs-dosbox-or-dosbox-x), how it works
[DEVELOPMENT-SCREENS](../obsidian-edition/DEVELOPMENT-SCREENS.md#the-engine-gogs-dosbox-or-dosbox-x),
the play [the log](../playtest/logs/2026-11-19-dosbox-x-engine.md).

**Against the experiment's list**

- The engine choice, the memory backend through `connect`, the window, `play` and `dicelog`,
  the conf writer for every Options setting, the version check, process finding, the crash
  report: built, with tests (`tests/test_dosboxx.py`, `tests/test_filememory.py`).
- The memory file has one name for each Loader folder (`obsidian-edition-<hash>.mem`, in
  `/dev/shm` on Linux, else the temp folder), not one per start: the Loader finds its game's file
  again after it is closed and opened, and a file left behind is the next start's to remove. The
  file and the game's pid are noted in `game.lock`.
- A file reads on after DOSBox-X has gone, so the backend watches the pid; a short read (the
  file cut at a start) is an error, not an empty answer.
- The Windows way is a mapping of the file, not file reads (see below); the experiment's "must
  be tried first" check is `playtest/dosboxx_memtest.py`, for the owner to run.

**What the play found that the experiment hadn't** (each now in the configuration)

- **`sensitivity` takes two numbers.** One alone is the pointer's speed across only: in a Triple
  window the pointer went three times too fast down the screen. The experiment played at Single
  size, where 100 is right either way.
- **`normal3x` and `normal4x` draw nothing on the surface output** (an empty grey window with
  this game; `normal2x`, `scan3x`, `tv3x` draw): Plain at Triple and Quadruple goes through
  `openglnb`.
- **"GOG's own" speed is the normal core at 8,000**, Faster the dynamic core at 22,000, Fastest
  42,000 (the experiment's guess for Faster and its number for Fastest held).
- Full screen switches only under a window manager (seen with openbox: the picture 4:3, black
  at the sides of a wide screen).
- DOSBox-X takes a second or more to close; the Loader's "the game is still running" refusal
  held until it had.

**Played** (Linux, DOSBox-X 2026.10.01, through the Loader's own start: `play`, `launch.launch`
with the `dicelog` command, and the window): the build and the memory as the experiment found
them, quick save and quick load by their keys, Alt's marks, two rests and Kurzak's call, the walk
from the pens into the arena with its autosave, loaded again, the fountain ambush with every
kind of dice-log line, Tab's and the pointer's chance to hit, squares in reach and R, F10, the
combat log's panel, the Loader's window with the Journal and the quests, twenty minutes without
a stop, the game ended and the file removed, DOSBox-X killed and the report. The log says what
was seen of each, and what wasn't.

**Windows, from DOSBox-X's source** (`src/hardware/memory.cpp`; not run). The file is opened with
`CreateFile(GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, OPEN_ALWAYS)`, cut
with `SetEndOfFile`, marked sparse, sized, and mapped with `CreateFileMapping(file, NULL,
PAGE_READWRITE, size, NULL)`: the mapping has no name. So:

- a second program can open the **file** (sharing read and write, as Python's `os.open` does),
  not the mapping object;
- it can't delete the file while DOSBox-X runs (no `FILE_SHARE_DELETE`);
- `ReadFile`/`WriteFile` on the file are not promised to agree with DOSBox-X's view (Microsoft's
  documentation promises coherence between **views** of one local file, from any mapping
  object, not between a view and file I/O), and Python has no `pread` there: the Loader maps the
  file itself (`mmap`);
- while the Loader's mapping is open the file can't be cut (`ERROR_USER_MAPPED_FILE`), and
  DOSBox-X's start would then get no memory file (`alloc_mem_file` returns false: it runs on
  with ordinary memory, and the Loader would wait for ever): the Loader closes its mapping when
  the game ends and removes the file before each start, refusing the start if it can't.

**Still untested**: Windows and macOS altogether (the script first); a packaged or sandboxed
DOSBox-X (a Flatpak's sandbox may not share `/dev/shm` or the temp folder with the Loader:
`dosbox_x_memory_dir` in `settings.json` names another folder); the Steam Deck; sound heard by
a person, and FluidSynth with a sound device; a real graphics card and vsync; MT-32;
`dynamic_rec` (ARM) speeds; DOSBox-X versions other than 2026.10.01.

**Left for later, by decision**: pixel-perfect scaling (`openglpp`) and CRT shaders (they fit
none of the four windows and four pictures as they stand: a setting of their own); MT-32;
teaching `UMBPLUS.COM` DOSBox-X's chain (10 KB of upper memory, not needed today).

## 9. Wake of the Ravager

**Measured, the two installs side by side**

| | Shattered Lands | Wake of the Ravager |
|---|---|---|
| Install | 36 MB | 287 MB (speech, CD music, films) |
| Game data | 16.2 MB | 16.4 MB |
| Regions | 33 | 20 |
| Scripts | 250 (0.89 MB) | 350 (1.48 MB) |
| Words of text | about 117,000 | about 197,000 |
| Creatures / items | 291 / 755 | 352 / 1,233 |
| Spell and power records | about 196 | 320 |
| Spell levels / level cap | 1-5 / 9 | 1-7 / 15 |

**The engine**
- The same: real mode, Borland's overlays, the same memory layer, GFF and GPL. `gpl.py` decodes
  349 of its 350 scripts once given Shattered Lands' field types.
- Changed: every address; the creature (49 bytes), sheet (66) and item (23) records; spells
  moved from the program into a data file.
- Of the mod's 426 code patch sites about 170 are recognisable (122 strictly). Carried over:
  the dice roll, message box, View Character, heap, overlay buffer, picture slots. Rewritten:
  attack and damage, saving throws, AC, level-up, spells, rest, prices.
- The mod is 457 patches, 134 hook vectors and about 84 data addresses, all to be found again.

**Carrying a party over**
- The game's own tool, CHARTRAN.EXE, reads a Shattered Lands save and writes the Ravager's
  character file, translating items through a table of 234 pairs.
- The mod's kit (sheet +43h) and specialisations (+14h..+17h) have no place in the Ravager's
  shorter sheet, and the mod's own items aren't in the table: they would be lost or turned to
  coin. The Loader must do the transfer, or finish it, and keep kit and specialisations in spare
  bytes proven unused, or in a file of its own.

**Phases, by value for effort**
1. Recognise the game; party and dice log (the roll and the message box match exactly).
2. Engine bugs whose sites match (picture slots, the overlay buffer, the record table).
3. The transfer that keeps kits and specialisations.
4. Script tools, then its script bugs.
5. Rules and kits. 6. The panel, screens and graphics.

**Effort against the Shattered Lands work**: phases 1-2 perhaps 15-25%; everything, 60-80%
(medium confidence: nothing was run, and its free memory with speech loaded is unmeasured).

**Experiments**
1. Patch only the roll (5A22h) and the message box (59A0Bh) into a copy, load the helper, and
   see the Loader find the party; measure free memory.
2. Run CHARTRAN on a mod save with a kit and specialisations and compare the records.

## Order of work

| Release | What | Helper bytes |
|---|---|---|
| A | Journal (talk, search, rolled back with saves); chance to hit; scanlines and sharp picture; MIDI device choice | 0 |
| B | Quick save, quick load, autosave; showing what can be used | about 130 |
| C | Squares in reach; quests in the journal | about 150 + 136 in the tail |
| D | DOSBox-X as an engine; soundfont and MT-32; whole-number scaling, borderless, CRT; Linux start; Deck layout | 0 |
| E | Wake of the Ravager, phases 1-3, as a build of its own | its own helper |

Each feature has a switch on the Options tab, tests, a play check with the playtest kit, and
its pages in the player's and developer's documentation.
