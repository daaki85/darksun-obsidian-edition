# Research recipes: the game's code and other targets

Part of the playtest guide's [research recipes](RESEARCH.md) (read the startup procedure of
[PLAYTESTING.md](PLAYTESTING.md#startup-procedure) before any in-game test). Tools: [TOOLS.md](TOOLS.md).
The game's scripts and code, the unchanged game, DOSBox-X, and the recompiled program as the target.

## Scripts and the game's code

- **What is under the pointer** (logs/2026-11-18-hit-chance-hover.md): **DS:0BCBh** is the thing
  the game last found under its pointer on the map (FFFFh: none), from the finder a click uses
  (25B52h: the front figure with a pixel there); the routine that keeps it (1E126h) lights the
  thing up, the one lit in DS:0BD1h, and puts that one back in DS:0BCBh for a pass after the
  pointer has moved on. DS:0BC9h is 1 with the map up and 2 with a menu (the END menu too), a
  window or a talk; DS:11B8h the pointer's mode (1 walk, 2 look, 4 attack; the game puts the walk
  arrow back as each member's turn begins). A map thing's picture box: left at +3, top at +5 less
  the signed byte +0Dh, width +12h, height +13h of its record (DS:6694h + 32 x thing).
- **A floating label taken off in a still scene comes back** a frame after DSCLOG erases it, until
  the view is drawn again (window grabs every 30 ms count its ink: `import -window`, the pixels
  near the label's colour). The Loader asks for the view again itself now (`Labels.took_off`); a
  test that writes a slot by hand must do the same (`shadows.redraw(gd, hdr)`).

- **The docs' code addresses (5883Ah and the like) are DSUN.EXE file offsets**, the patches'
  (`gamepatch.Patch`'s offset), not linear addresses in memory: most of the fight code is an
  overlay, so memory there reads zeros or other code. Disassemble the file (capstone, 16-bit, the
  offset as the address: near jumps and calls come out right within a routine); a near call's
  target is offset + 3 + rel16. Far calls in it carry relocations: leave their bytes where they are
  in a patch. A new hook needs no vector of its own: a site (`gamepatch._site`, DSCLOG's `site`
  table, in order) on VEC_CR_SPELLS; a site replacing a compare puts its flags into the INT's frame
  (`ammo_turn`). (logs/2026-11-14-quiver-turn.md)

- **The arena's flags and numbers can't be set from outside**: the pointers at DS:1352h and 1356h
  stay null in the arena even while a script waits on a message, so a poller never finds them. To
  test a script's branch there, build a copy of the scripts with the test forced (edit the module,
  run `start.sh`, which writes `dos/GPLDATA.GFF`, then put the module back) and say so in the log.
- **Setting the arena's visit count**: in the pens the game's numbers have a place in memory;
  number 12 is the count (4: the next trip is Scar's; 5 and up the everyday speech, or the
  champions' after Scar's death in the arena). Write it at the far pointer DS:1356h + 2 x 12:
  **`setcount.py [N]`** reads it and, with N, writes it.
- **Reading a value inside a script**: a test build whose repair PRINTs (4Fh, 98) a field prints
  nothing for a number; print a marker string under an IF per guess instead (TEST field == N, IF,
  PRINT " aN", ENDIF; the IF's address in `relocate`). Keep such a probe small: one of about 200
  tests (some 5 KB of detour) ran nothing at all, nor did 100 reading fields 72,n. Item fields seen:
  72 = the item's +00h (its kind, minus its object), 85 = its slot (+11h); no field 0-99, nor
  72,0-99, gave its type.
- **The game's command table** is words at DS:00C0h + 2 x command, the handlers in segment 5DFh
  (the dispatcher at linear 5FE9h, `call [bx+0C0h]`): dump memory with live.py (`gd.guest.read(0,
  0xA0000)`) and `ndisasm -b16 -o OFF`. 41h (5DF:1895h) stores its value, an object's number (or a
  kind, looked up), in 3923:361h (object 2Ch); 49h (5DF:140Ah), the item loop, copies each item into
  one scratch object (2Bh, 3923:35Fh).
- **The pens' master script and named routines**: `KIND='MAS ' dec.py 29 0 140` decodes the pens'
  master script; GPLI 1 is the index of named routines (id, offset, script: 2-byte words).
- **The triggers in memory** (which things have a talk, attack, look, use or use-with script: found
  2026-11-16, logs/2026-11-17-show-usable.md): one table of 13-byte records at the far pointer
  DS:42CCh (+0 the place in the script, +2 the script, +4 the object's id, the number negated as
  the scripts write it, +6 a use-with's other id, +0Bh the next record's index, FFFFh the last),
  the lists' heads words in segment 377Eh plus the load segment (+0Fh talk, +11h attack, +13h
  look, +15h use, +17h use with; +09h the tile and box triggers). DSUN.EXE 967Ah is the game's own
  "what can be done with this thing" (bits 4 talk, 2 attack, 8 look, 10h use, 20h use with). A
  thing's id: an item record's first word, a creature record's +6. `dsloader.usable.triggers(gd)`
  reads the lists; `usable.py` prints what the Loader would mark.
- **Finding a table in memory from the scripts' numbers**: search the game's memory
  (`g.read(0, 0x110000)`) for one record's words near each other (a trigger's place, script and
  object from the MAS script), print the neighbourhood in the record's size, then look for a far
  pointer to its start in the data segment and for the code that uses that pointer (capstone over
  DSUN.EXE: the image starts at file 5400h; the relocation table gives every use of a segment).
  **Never name a scratch script after a module of Python's** (`dis.py`, `types.py`: capstone and
  live.py then import the script instead, "partially initialized module").
- **The draw list's three sorts of entry** (`drawlist.py all`): things 0-519 that are creatures or
  items; things 0-519 of kind 0 (drawn, no record: the pens' banners and braziers); and numbers
  past 519 (the region's own scenery: 55135...). DSCLOG's rings and labels take the first two
  only. The list holds the whole region (415 entries in the pens), not the view.
- **The inventory's input** (for anyone trying a click there by hand): the game takes clicks from
  its queue of events, never INT 33h's position; what was tried is in [HISTORY.md](HISTORY.md#the-inventorys-input).

## The unchanged game

For a comparison with the game as it shipped (no DSCLOG, no Loader, no dice log;
logs/2026-11-16-spell-grid.md):

- **Starting it**: a DOSBox config of the Loader's settings with its own autoexec: `sed
  '/^\[autoexec\]/,$d' ../obsidian-edition/dosbox_dicelog.conf > $WORK/plain.conf`, then append
  `[autoexec]`, `mount c ".."`, `c:`, `DSUN.EXE`, `exit`. Kill any DOSBox (by pid), then from
  `$DS_GAME/DOSBOX`: `setsid dosbox -conf ../__support/app/dosbox_darksun.conf -conf $WORK/plain.conf
  &`. The game folder's files are the originals (the Loader writes its copies to
  `obsidian-edition/dos/`). **Not `start.sh` or `loadsave.sh`**: they start the Loader's game.
- **Its intro plays**: two title clicks, then Escape a few times, then the main menu.
- **A save**: copy `saves/NAME/*` into the game folder, then LOAD SAVED GAME (170,109), the slot
  (100,46), LOAD (253,46). A save made with the mod loads.
- **What works**: `click.py`, `creationscores.py`, `sheetinfo.py`, `shotinfo.py`, `hp.py` and the
  memory tools. Not: `buildcheck.py`, the dice log and its readers, and Tab's target (`fightout.sh`,
  `toturn.sh`): attack with `pointer.py attack` and a click on the foe.
- **It differs at creation**: a new preserver gets no CHOOSE A SPELL (the mod's); the window shows
  at a level-up.
- **A screen's layout**: read its WIND chunk in the game's RESOURCE.GFF against the Loader's copy
  in `obsidian-edition/dos/` (`dsloader.gff.read_gff`; a window's places are 30-byte items from
  +105h: the tag at +4, the id at +8, x and y at +0Ch).

## DOSBox-X: what the engine is like inside

For a test of the DOSBox-X engine ([a game in DOSBox-X](PLAYTESTING.md#a-game-in-dosbox-x) has the
kit's side; `dsloader/dosboxx.py` the configuration and why each line is there).

- **The memory file** is the guest's RAM, offset = guest address, 33,554,432 bytes (`memsize=32`),
  sparse, mode 0600, made again at every start (cut to nothing first: a mapping held over a
  restart would fault, so the Loader uses `pread` and `pwrite`). It stays when DOSBox-X closes;
  the Loader removes it. Read it with any tool: `python3 -c "print(open(PATH,'rb').read()[0xFFFF5:0xFFFFD])"`
  gives the BIOS date.
- **Memory layout**: the game loads at 0224h (0.74: 01A2h) and has 96,928 bytes free with the
  map open (0.74: 99,008); upper memory is CC00h-EFFFh, DSCLOG at CC4Bh with 1,168 bytes free
  below it, the overlay buffer at DD84h, 16,496 bytes free at E592h, the see-through tables at
  E99Bh and the music buffer at ED11h as on 0.74; the far block in the HMA. `memaudit.py` prints
  it all.
- **DOSBox-X's own keys**: its host key is F12 (F11 on Windows); host+F is full screen, Ctrl+F10
  lets the mouse go (as 0.74), Ctrl+F9 quits. Bare F5, F9, F10, Tab, L, R, Alt reach the game
  (all seen). Its menu bar is off (`-nomenu`, `showmenu=false`).
- **Its log** (stdout: `$WORK/dosbox.log` from the kit's script, `obsidian-edition/dosbox-x/dosbox-x.log`
  from the Loader's start) has DOS's own text ("DSCLOG loaded.") with `log console=true`, the
  window sizes it chose ("surface consider=960x720"), "Using memory file", FluidSynth's lines.
- **Pictures**: `normal3x` and `normal4x` on `output=surface` draw an empty grey window with
  this game; everything else the Loader writes draws. A picture test: start with
  `window_scale=3 picture=scanlines`, two clicks past the title, `import -window root`.
- **A write to code** made from outside may not be acted on, on a dynamic core, on either
  engine (`codepatch.py`); `core=normal` after the program on `start_dosboxx.sh` if a test needs
  it acted on.
- **Sound**: no device in the container (`SDL_AUDIODRIVER=dummy`). Since 2026-11-21 the Loader
  writes `mididevice=synth` with the soundfont in `midiconfig`: DOSBox-X's FluidSynth playing into
  its own mixer, so `PT_SDL_AUDIO=disk` records the music and the effects together. The other
  device, `mididevice=fluidsynth`, plays through FluidSynth's own driver ("Failed to create
  PulseAudio connection" here, no music; `extra='midi|fluid.driver=file'` renders it to
  `fluidsynth.wav` instead: the experiment's way).

## The recompiled program as the target

The kit drives the recompiled program (Dark Sun Recompiled) too (`PT_TARGET=recomp`, exported for
every tool; `DSUN` names the program, default `/home/user/darksun-recompiled/build/cmake/dsun`):

- `start_recomp.sh` (and `loadsave.sh` under that target) starts it with the Loader's patched
  game (`prepare_patched_game`, as start.sh) and the mod's `dos` folder, makes its window 320x240
  at 0,0 (so the window grabs and their pixel positions are DOSBox's), records its pid in
  `$WORK/dsun.pid` (the dice log and `live.py` use that pid: other dsun processes may be headless
  runs of the program's own tests, and `dsloader dicelog` refuses to guess among several) and
  attaches the dice log. **Its build must match the mod's helper**: the program lifts
  `dos/DSCLOG.EXE` into its `build/ds1o`; a branch with a newer helper needs
  `tools/build_mod.sh <this repo>/obsidian-edition` in the program's repository and its
  convergence runs first (a wrong helper shows as `no function at B....` in `$WORK/dsun.log`).
- `shot.sh` grabs its window and scales it to 320x200 (there is no Ctrl+F5 capture). Its colours
  differ from DOSBox's by one (38 of 63 is 153, DOSBox says 154) and its picture is stretched to
  240 rows a row apart, so pixel checks go through `pixmatch.py` (within 3 a channel, a row up or
  down): msgbox.sh, panel.sh and levelup.sh use it.
- **The dice log must be attached after the game is loaded**: attached at the program's start,
  or before a save is loaded, it prints nothing afterwards; `loadsave.sh` restarts it after the
  load, and after any restart of the program check that an action shows in `$WORK/dice.txt` before
  trusting its silence.
- **Saves cross over both ways**: a save made in DOSBox loads on the program (pens-kurzak-door),
  and one made on the program loads in DOSBox (pens-kurzak-door-recomp). The program's save
  leaves DARKSAVE.GFF as it was, as DOSBox's did.
- Controls behave as in DOSBox: click.py's relative moves converge on the pointer, walkto walks,
  right-click cycles arrow, red sword, red look, arrow; the arrow over a person shows the portrait
  pointer and a click opens the mod's Look box (Talk is its first button, 216,99).
- **The view does not scroll by itself** here either; the middle-button drag works (the program's
  runtime passes the middle button through). **The drag scrolls only with the Loader attached**
  (the dice log counts: it switches the helper's `scroll_on` on at attach); a program started with
  no Loader, as its own headless tests run, keeps the view still. **A kit tool that stalls on the
  program and not in DOSBox is a program fault to report**, not a tool to work around.
- **Doors at Kurzak's stop**: the look pointer on the doorway's drawing (square 95,27, above the
  door square) opens the mod's Look box "Door" (INFO only); the arrow, the look click and the sword
  on the door square do nothing and log nothing; the sword on Kurzak (object 29, then at square
  99,31) does nothing either: no fight starts from a click on a friendly figure.
