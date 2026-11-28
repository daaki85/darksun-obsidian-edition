# Research recipes: sounds, pictures and timing

Part of the playtest guide's [research recipes](RESEARCH.md) (read the startup procedure of
[PLAYTESTING.md](PLAYTESTING.md#startup-procedure) before any in-game test). Tools: [TOOLS.md](TOOLS.md).
The game's sounds, the see-through figures, the picture store, frame rate and cycles, the picture and the
music device, and the figure prototypes in the game.

## Sounds

- **Hearing the game**: start.sh sends DOSBox's sound to a file when `PT_AUDIO` names one (`export
  PT_AUDIO=$WORK/audio.raw` before start.sh or loadsave.sh; else /dev/null): raw 16-bit stereo at
  44100 Hz, about 176 KB a second, real time. Note the file's size before and after an action, then
  `python3.13 soundmatch.py $PT_AUDIO A B clip.wav...` gives the loudest sample and how well each
  clip matches (r about 1.0 for the one played; 0.04 for another). `playsound.py N` has DSCLOG play
  sound N (its SOUND_REQ). The game plays nothing much on its own while the party stands about: a
  recording of minutes was silence but for a second at the start. The game's own 53 and 96 recorded
  at peaks near 2,800.
- **Comparing loudness** (logs/2026-11-09-sounds-louder.md): `playsound.py N` for each sound with 3 s
  between, the raw file's size noted round each, then the peak and the loudest 400 ms RMS of each
  stretch (numpy over the memmap): the game's fight sounds peak about 2,960, RMS -27 to -31 dBFS. A
  sound's descriptor +6 is its priority: the game skips one lower than the sound playing. **The
  descriptor's +0Ah (6Eh) is not a volume** (logs/2026-11-10-sounds-denser.md): set from 20 to 127
  the output peaked at 2,957 each time. DOSBox plays every clip at the same peak, so a quiet clip can
  only be made denser (make.py's soft-limiter drive): hide now -27.5, pick -30.5 dBFS.
- **Recording DOSBox-X's sound**: `SDL_AUDIODRIVER=disk SDL_DISKAUDIOFILE=FILE` works for it too (SDL2), but
  the raw file is 48,000 Hz (DOSBox-X's default `rate`), not 0.74's 44,100 (logs/2026-11-28-ravager-voice-volume.md).
  **The card's mixer sets the ceiling**: with `sbmixer=true` a full-scale clip comes out at about -21 dB in
  Shattered Lands in 0.74 (the 2,960 above), -24 dB in DOSBox-X; with `sbmixer=false` at full scale.
- **The game's table of sounds**: at load segment + 3A98h, offset 08A2h, 6 bytes each: +1 the kind
  (5 a digital clip), +2 a far pointer to a 12-byte descriptor (+7 its BVOC). 0-130 are digital,
  131-180 another kind (4), past 180 other data: a BVOC numbered past 130 isn't played by its number
  (the mod's 140 and 141 were silent until DSCLOG lent itself entries 131 and 132 for the call), and
  the game keeps the last clip loaded under a number (one lent entry for both sounds played the
  first again).

## See-through figures

- **`ghostchk.py`** shows DSCLOG's block (GHOST_SEG), GHOST_ON and the tables; `ghostchk.py 0` marks
  thing 0 (the leader) see-through and has the view drawn again, for a look without a fight or a
  spell; `ghostchk.py 0 1` marks things 0 and 1 (each call replaces the marks). Outside a fight the
  party is one figure, the leader's; walking, it spreads into four. The live table of vectors
  (segment 0, 4 bytes each) shows which handler has each; **the install's bytes turning up twice in
  the image means two probes on one vector**, not chance ([target AC
  255](HISTORY.md#two-probes-on-one-vector-target-ac-255)).
- **A big frame see-through** (logs/2026-11-06-see-through-after-fix.md): `bigthings.py` lists the
  map's things with their pictures' most runs (near the pens' gate none past 164); `setpic.py THING
  PICTURE` draws a thing with another picture in memory (picture 459, a tuft of grass of 563 runs;
  put the old number back after), and `pastblock.py save|cmp FILE` keeps and compares the 4 KB past
  GHOST's block. Past 192 runs only the frame's top is drawn see-through, by design.
- **In a fight** (logs/2026-11-05-fight-test.md): seen from a real hide and a real Invisibility. The
  pale bits behind a walking figure are the mod's dust (dust.py), not a smear: solid figures leave
  them too, and a full redraw clears them; an END menu left up keeps them on screen.
- **A hidden walk to Move 0, and the turn's end** (logs/2026-11-06-solid-frames-turn-end.md):
  `walkprobe.py N X Y DIR [SECS]` clicks, then keeps a window grab with N's position, whose turn and
  DSCLOG's STEALTH word (header +204) as often as it can (about 50 a second). **Since GHOST_UNION**
  (logs/2026-11-06-solid-at-turn-end.md) the figure is solid about 0.1 s after the hiding ends, in
  the next enemy's turn, if that enemy steps or swings; one that does nothing redraws nothing, and
  the old wait applies: the figure keeps its see-through picture through the enemies' turns and is
  drawn solid when a party member's turn begins ([the old wait](HISTORY.md#see-through-figures-at-a-turns-end)).
- **`ghostclear.py [TRIALS]`**: at each enemy turn's start, Cermak marked see-through with
  GH_CHANGED set, the byte and the turn read every 20 ms: whether GHOST_UNION cleared it within that
  turn. `markmember.py THING|none CHANGED` writes GHOST_TAB and its changed byte (GH_CHANGED) by
  hand.
- **Pointer trails**: sweeping the pointer with `xdotool mousemove_relative` (DOSBox takes only
  relative moves) while asking for view redraws (DSCLOG header +242 = 1, 30 a second) showed no
  trails, before or after the fix (interrupts off again while DSCLOG draws: DRAW_MASKED).

## Pictures, the picture store and memory

- **Memory**: `memaudit.py` lists every DOS block (the game's, DSCLOG's, the overlay buffer, the
  see-through tables, the music buffer, free) and the heap; `memsample.py LABEL` gives one line (free
  DOS memory after the game, more while the inventory or USE screen is open); `dacwatch.py SECONDS`
  shows DSCLOG's palette copy changing (every 30 s where the game cycles colours); `ghostwatch.py
  SECONDS` counts samples with GHOST_ON 0. The current figures are in [where DOSBox's memory
  is](../obsidian-edition/DEVELOPMENT-INTERNALS.md#where-dosboxs-memory-is); the history is in
  logs/2026-11-08-memory-pass.md and logs/2026-11-09-memory-pass-2.md. Comparing builds: [builds,
  the Loader and the tests](PLAYTESTING.md#builds-the-loader-and-the-tests).
- **The picture store** (logs/2026-11-09-missing-figures.md): the game's store (741,376 bytes,
  fixed, DSUN.EXE 60D9Bh) and its table of 300 picture slots (load segment + 3E60h; DS:1F84h the
  slots taken) are given back only at an area load. The pens load 203 of the 300 slots on arrival
  and walking about adds none (`slotcount.py` at each stop; logs/2026-11-09-picture-slots-explore.md);
  fights add a few (bodies, dropped items, spells). Wake of the Ravager's "graphics disappear" note
  is this same limit; leaving the region clears it. The Loader leaves a figure undressed when the
  store has no room (`_room_for`), and puts a re-dressed picture into a slot the game already has
  (`sprites.Dresser._in_store`, logs/2026-11-09-picture-store-fix.md), so `cachelist.py`'s slot count
  no longer climbs one a gear change: a toggle reuses the slot holding that outfit, the inventory
  open writes each picture's own slot, other outfits take a free STALE slot; a new slot only when
  the outfit is bigger than any free one (a few in the first dozens of changes, then none). DSCLOG's
  PIC_REUSE reuses free slots past 300. **Figures gone from the map** (the party, at times the foes,
  not drawn though their places are right; clicks on them miss) mean the store ran out: check
  `cachelist.py` (slots taken) and `cachelist.py all` (the last slot's place + length against
  741,376), and reload the save or change area to start afresh; I then Escape draws them again for a
  while. How it was found and what it did before the fix: [the picture
  store](HISTORY.md#figures-gone-from-the-map-the-picture-store).
- **Watching figures and pictures**: `figwatch.py SECONDS [EVERY] [TAG]` (passive, no writes: each
  member's screen place, its map record's +0 (80h: not drawn), its picture slot (+0Fh) with that
  slot's number and flags (2: in memory), the draw list's order and the member's place in it, and a
  strip of grabs round each figure); `drawlist.py [all]` (the draw list at DS:6690h, kept in rising
  y: the drawing finds its window DS:57CAh-57C8h by a scan that stops at the first y past the view,
  so an entry out of order would hide all after it; never seen out of order); `cachelist.py [all]`;
  `poolfree.py [SECONDS]` (the picture memory's free bytes, DS:8E94h); `figcheck.py LABEL` (a grab
  before and after DSCLOG's VIEW_REDRAW, header +242, and the pixels changed round each member: a
  figure missing then drawn shows hundreds). An inventory move in a test: `click.py` the item, then
  the place.
- **The store itself** (logs/2026-11-09-picture-store.md): an XMS block behind the game's paged
  memory manager (handle DS:4C33h, pages through the directory at DS:42D2h); in DOSBox it was guest
  RAM at 110000h, XMS pages 2-2Fh in one run. `picstore.py` finds it and checks every in-memory
  picture against its store bytes (`check`; all should match), lists the STALE cells (`stale`) or
  dumps a slot. The picture pool is 60,000 bytes; opening the inventory (I) puts every picture out
  of memory (`cachelist.py`: 0 in memory).
- **Changing outfits for a test**: `outfitcycle.py MEMBER SLOT N` changes an outfit N times
  (waiting for the Loader's copy to be written, not for the slots to grow) and prints slots, STALE,
  the store's end and whether the figure is drawn each time; `randout.py N [SEED]` puts random items
  of member 0 on and off. `fillcache.py MEMBER SLOT UNTIL` fills the slots fast by toggling a worn
  item's slot byte, the Loader dressing each time (memory edit, never save), but it waits for the
  count to grow, which the store's reuse stopped: it stalls (4 s a change) and is of no use now. A
  test that needs the store full needs a picture loaded anew some other way.
- **Lots of items on the ground** (logs/2026-11-09-picture-slot-reuse.md): `giveitems.py MEMBER N
  [FIRST]` gives items of different objects (each its own picture) into free backpack cells in
  memory (12 cells: then "no room"); `groundfill.sh CYCLES [FIRST]` gives Gerakis 12 and DROPs each
  (I, his portrait 20,20, a cell then DROP at 213,134; cells x 195/213, y 26-116), cycle after
  cycle, printing `slotcount.py` (slots, store end, in memory, STALE, and PIC_REUSE's reuse count
  `pf_count`, read through a symbol map). Dropped items pile on the party's square: walk off to see
  them. `slotcheck.py`: every map thing with a slot finds its own picture there, every wall's slot
  taken; six entries of the thing table naming slot 0 with nonsense pictures are the table's unused
  ones (the same on a fresh load). From `pens-thornwall-rack` 145 items took the table from 203 to
  300 in nine dozen (about 40 s a dozen).
- **The inventory and the picture cache**: opening it puts every picture out of memory, and its
  icons are loaded through the same cache and let go once drawn, so at 300 slots they are free for
  reuse. PIC_REUSE searches round from after the last slot it reused ([why](HISTORY.md#slot-reuse-and-the-inventorys-icons)).

## Frame rate and cycles (framerate.py)

`python3 framerate.py 20` walks the party back and forth (screen 40,104 to 280,104, a click every
3 s) for 20 s, out of a fight, and prints: the frames shown a second (DSCLOG's flip_count); those
steady pace left undrawn (pace_skipped); the steps run and lost (pace_ran, pace_lost: steady pace on
only); these found from a symbol map of the helper as built; the main loop's passes; the BIOS
clock and the game's clock (96 a second) against real time; the leader's map units a second
**while walking** (the waits at a target left out); and DOSBox's CPU. `PT_CYCLES=N sh start.sh` (or
before loadsave.sh) sets DOSBox's cycles; settings are changed with `launch.save_settings` before
loading (the log of 2026-11-08).
Its walk clicks are at y 104: from `fountain-user` after its fight they land in the fountain and
nobody walks (0 map units/s), so measure from another save.

**The rings' cost** (2026-11-16): `ringall.py [N | all | still | clear] [KIND]` puts a ring under
every thing on the screen (still: all but the party) straight in DSCLOG's table, for a framerate
run without the Loader's say; the Loader writes its own table only when it changes, so they stay
until Alt or a fight's Tab ring. DSCLOG goes round every marked thing's ring at each floor pass,
on the screen or not: 16 rings (4 under the walking party) took the walk from 155 to 122 map
units a second, 87 marked across the region with one in view from 134 to 120, and a ring's
thickness made no difference. Put the party back first (`walkto.py 1672 344`, `viewto.py 1672
344` from `pens-after-arena`): a run started from wherever the last one ended walks into a wall
or drags the view along, and its numbers aren't comparable (0 map units a second once).

How the game paces walking: its timer (DSUN.EXE seg 1DF3:29E8h) sets DS:1F7Eh at each tick of
the game's clock (DS:11D6h, 96 a second); the step (1DF3:26DCh) runs only with it set and clears
it. A tick passed while a frame draws is a step lost.

How to compare two builds fairly: run them **alternately in the same session** (before, after,
before, after) rather than against an older table: runs of one build agreed within 0.3 frames a
second, so a difference of 1 is real. A loaded game's first framerate.py run is as good as later
ones. `framerate.py` takes the symbols from `obsidian-edition/dos/dsclog.asm`; for another build's
EXE in `dos/`, set `DSCLOG_ASM` to that build's source, or it reads the wrong counters. The script
is logs/files/2026-11-08-drawing-savings-runs.sh (results in logs/2026-11-08-drawing-savings.md); put the
EXE back and `cmp` it afterwards.

The measurements (pens-after-arena, the whole party walking, 2026-11-08), the old steady pace's
and the faster drawing's: [HISTORY.md](HISTORY.md#frame-rate-measurements).

**Two engines' speeds** (2026-11-19, logs/2026-11-19-dosbox-x-engine.md): the same cycles do less
on DOSBox-X than on 0.74, and each core has its own pace, so a speed is found by walking, not by
the number. `framerate.py` reads its own game's pid (`live.py`'s: `dsun.pid`), so it measures a
DOSBox-X or a DOSBox under another name beside the shared one. A fresh start for every run, the
engines in turn in one session, `framerate.py 20` from `pens-after-arena`; match the steps run
and lost and the map units a second (within 2 between runs of one setting), then the frames.
0.74's 35,000 on its dynamic core is DOSBox-X's 42,000 on its dynamic core, 20,000 is 22,000, and
GOG's 7,000 (0.74's normal core) is about 8,000 on DOSBox-X's normal core; `dosboxx.SPEEDS` has
them. DOSBox-X's own speeds for a test: `cycles=N core=normal|dynamic` after the program on
`start_dosboxx.sh`.

## The picture and the music device (picstart.sh, picpattern.sh)

The Loader's **Picture** (plain, scanlines, tv, sharp: `launch.display_lines`) and **Music device**
(`midiout.py`) are DOSBox settings, so most of a check needs no game
(logs/2026-11-17-picture-music.md).

- **Without the game or the lock: `sh picpattern.sh win:3:scanlines win:4:sharp full:3:sharp`.** A
  DOSBox of its own shows a pattern in the game's screen mode (13h) with the Loader's display lines
  for a window (`win`) or full screen (`full`), a scale and a picture; it prints the settings, the
  window's size and any complaint of DOSBox's, and grabs the window (the whole screen for `full`)
  to `$WORK/picpattern/`. It runs on its own display (`:57`, 1920x1080, so the 1280x960 window and
  full screen fit, which `:55`'s 1024x768 can't show) and under another process name (a copy of
  the program called `dbpat`), so it never disturbs a play: `live.py` attaches to the newest process
  named dosbox, and `start.sh` kills every one. **A second DOSBox under its own name would be taken
  for the game by every tool of every agent.** Its window's class is the program's name (`xdotool
  search --class dbpat`).
- **In the game: `sh picstart.sh PICTURE [SCALE] [OUT_DIR]`**, under the lock. A start of its own
  (not the kit's 320x240): `pens-after-arena` loaded with `click.py` alone, which works at any
  scale because it moves the hand until the game's pointer reads the place; then the window's
  size, `picmove.py DX DY` (the hand moved, how far the pointer went), a grab (`import -window`)
  and DOSBox's log. It writes `window_scale` 1 and the plain picture back to settings.json as soon
  as the configuration is written, so a run cut short still leaves the kit's settings. About 75 s
  a picture.
- **The kit's own start never changes with the picture**: at `window_scale` 1 the Loader writes
  `scaler=none` whatever `picture` is stored (`tests/test_launch.py`).
- **What Linux's DOSBox 0.74-3 can and can't show.** It has no DirectDraw: GOG's `output=ddraw`
  is refused ("not a valid value... reset to surface") and the plain surface used. Windows open at
  their sizes with every picture, and OpenGL (`opengl`, `openglnb`) works under Xvfb. Full screen
  with the surface output is not stretched (the picture sits unscaled, and partly off the screen
  under Xvfb), so only Sharp's full screen can be judged here; Scanlines and TV in full screen, and
  how DirectDraw smooths a window's stretch, are for the owner's Windows.
- **Reading a grab for scanlines**: sum a column's pixels down the picture (`PIL`): at Triple a
  game row reads lit, lit, black, with the black line twice under three rows in five (the aspect
  correction's line table); TV reads full, about 5/8, about 1/3.
- **The music device can't be heard here**: the container has no ALSA sequencer ("ALSA:Can't open
  sequencer", then "MIDI:Opened device:none" in `dosbox.log`), and the Windows device list
  (`midiout.devices`, winmm) is None off Windows. The unit tests use a stand-in for winmm.

## The figure prototypes in the game (outfitgame.py)

- The figure prototypes' pictures (`prototypes/outfits.py`, `prototypes/wornlooks.py`) are not the Loader's: to see them in the game they are put
  into the Loader's copy of SEGOBJEX.GFF between the Loader writing it and DOSBox opening it, and
  the game is run with no Loader attached (it would dress the figures again):
  `PT_NO_LOADER=1 PT_AFTER_PREPARE="python3 outfitgame.py 300=Mage,305=Thief,308=Priest" sh
  loadsave.sh pens-after-arena` (`all=Warrior` for every figure). `start.sh` runs
  `PT_AFTER_PREPARE` in `playtest/` after `prepare_patched_game`, and with `PT_NO_LOADER` stops
  before the dice log (so `dice.txt` is not written and nothing of the Loader's runs).
  loadsave.sh shows only start.sh's last line: send the command's output to a file to read it.
- **With no Loader attached the game draws a party member from the game's own picture of its
  figure** (the human man's 2095/2096...), not from the object's own pair in the copy (2450 and
  on, `sprites.picture_ids`): pictures put only into the pair don't show. outfitgame.py writes
  both, so everyone of that figure wears the outfit (Kurzak, a half-giant, has a picture of his
  own and doesn't).
- `OBJECT=worn:LOOK` puts in a look by what's worn (`prototypes/wornlooks.py`: Robe, Leather, Bone
  scale, Chain, Cloak and hood). The names have spaces, so quote the list inside the double quotes:
  `PT_AFTER_PREPARE="python3 outfitgame.py '300=worn:Bone scale,308=worn:Robe'"`
  (logs/2026-11-21-worn-looks-in-game.md).
- **A fight with no Loader attached**: Tab's nearest-enemy pick is the Loader's, so Tab + Return
  opens the game's menu instead of attacking (and fightout.sh's E then the Effects screen; Escape
  closes either, a screen being up). Attack by clicking the foe. `fountain-user` starts Pehtucl's
  ambush on loading; its party is Lex (half-elf woman, object 307), Jenna (human woman, 301), Ester
  (elf woman, 305) and Seneca (halfling woman, 311), not pens-after-arena's: `python3 -m dsloader
  save SAVE01.SAV` (in obsidian-edition/) lists a save's party, race and sex, before guessing who is
  who from the screen.
- `OBJECT=preset:CLASS` puts in `prototypes/presets.py`'s picture instead: the class as a preset of
  the Loader's own gear drawing (clothes recoloured, boots, the fitted cloak), to compare.
- `pens-after-arena`'s party: a human man (object 300), an elf woman (Cilla, 305), a half-giant
  man (308) and a thri-kreen (313).
- A picture 8 pixels wider each side and taller than the game's own draws in its place without
  being cut (it stands on its bottom edge, its middle on the figure's): nothing under the feet.
- A click on a wall shows the no-walk pointer and moves nobody: click the floor.
- Grabbing a walk: `import -window $W` every quarter second from half a second after the click;
  the party crosses the hall in about two seconds, so most grabs are of it standing.
