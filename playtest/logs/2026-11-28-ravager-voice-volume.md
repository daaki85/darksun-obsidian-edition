# 2026-11-28: Wake of the Ravager's quiet speech (DOSBox-X and GOG's DOSBox)

**Under test:** the user heard the sequel's spoken voice barely at all in DOSBox-X (the Windows default). Where
the level goes, in both emulators, and the fix (branch `claude/ravager-voice-volume`). In short: the game menu's
SOUND EFFECT VOLUME starts at half, which the emulated card's mixer makes far quieter than a card did; the
Loader now starts the sequel at full and Shattered Lands, in DOSBox-X, a notch up.

**Set-up:** this container's DOSBox-X is Ubuntu's `apt install dosbox-x` (2024.03.01: no `memory file`, so the
Loader's dice log and the kit's tools can't attach the usual way; see below) beside DOSBox 0.74-3. Sound
recorded with SDL's disk driver (`SDL_AUDIODRIVER=disk SDL_DISKAUDIOFILE=FILE`): 16-bit stereo, 48,000 Hz in
DOSBox-X (its default rate), 44,100 Hz in 0.74 (GOG's `rate=44100`). Each run: the Loader's own configuration
for the sequel (dsloader: `dosboxx.conf_lines` with `ravager.conf_lines`' autoexec for DOSBox-X; GOG's
`dosbox_darksun2.conf` then the Loader's file for 0.74, as `_launch_wotr` starts it), Shift twice past the
intro, S (START GAME), 75 s: the narrated opening (the CD's `INTR\INTR49.VOC`, 47.9 s, 21,739 Hz 8-bit) and
Kael's "Hurry! You must come with me..." in Tyr (a `SPCH` file).

**The sounds as recorded:** speech (CD `SPEECH\`, 117 files) about -20 dB RMS with peaks at full scale;
`INTR49.VOC` -18.4 dB RMS, peak 0; the CD music (`MUSIC\TrackNN.ogg`) -18 to -22 dB mean, peaks -1 dB (track
30 -28). So the speech and the music were made about as loud.

| Run | Narration RMS | Narration peak | Kael's line peak |
|---|---|---|---|
| DOSBox-X as shipped (sb16, the card's mixer on) | -42.4 | -24.1 | -24.0 |
| DOSBox-X, `sbtype=sbpro2` | -29.6 | -11.2 | -11.3 |
| DOSBox-X, `sbmixer=false` | **-18.4** | **0.0** | 0.0 |
| GOG's DOSBox 0.74 settings (sb16, mixer on) | -34.0 | -15.6 | -15.6 |
| 0.74, `sbtype=sbpro2` | -34.0 | -15.6 | -15.6 |
| 0.74, `sbmixer=false` | **-18.4** | **0.0** | 0.0 |
| CD music at the title menu (DOSBox-X) | -18.4 to -18.7 | -2.1 to -3.7 | |

- **Cause:** the game's sound driver (SOUND.CFG: `sbpdig.adv`, the SB Pro II's) turns the card's mixer down
  by the menu's SOUND EFFECT VOLUME (below), and with `sbmixer=true` (both emulators' default, and GOG's setting) the emulator turns its Sound Blaster
  channel down with it: 16 dB in 0.74, 24 dB in DOSBox-X (its SB16 mixer takes about 8 dB more). The CD's
  audio tracks never pass the card's mixer there, so they play at full level: the speech came out 24 dB under
  the music in DOSBox-X, 16 dB under in GOG's own DOSBox. It is not the Loader's doing (GOG's settings alone
  give the 16 dB) and not the card's address, IRQ or DMA.
- Matching the narration against `INTR49.VOC` (`files/2026-11-28-voice-volume-match.py`, cross-correlation):
  0.74 r 0.70, gain -18.7 dB on the whole stretch. In DOSBox-X r only 0.24 (its resampling to 48 kHz drifts
  against a straight 21,739 Hz resample over 48 s), so its level is read from the RMS and peaks above instead.
- **First fix, dropped:** `sbmixer=false` (the card's mixer out of it) put the speech at its recorded level in
  both emulators (the table), but the game menu's SOUND EFFECT VOLUME then did nothing. The review asked to keep
  the menu, so the volume the game starts with was found instead (below). `sbtype=sbpro2` changes nothing in
  0.74 and leaves DOSBox-X 11 dB down.
- **No music under the speech here:** with the CD mounted, the title menu played track music, but the
  narration and Kael's first line played with no CD track under them (the same levels as a run with the data
  track alone).

**The game menu's SOUND EFFECT VOLUME** (the inventory's GAME MENU, game 267,187; SET PREFERENCES, 162,100;
the bar with the speaker, its right arrow at game 218,91; each press a step, 0.3 s held; Escape closes it):
- It starts at **half** (the bar about 51%). In a fight (DOSBox-X, sb16, mixer on; Q opens the END menu, E ends
  the turn) the effects' ceiling was -32.1 dB at the start; with the bar at full it was **-0.1 dB** (32,412).
- In memory it is two bytes of the data segment, DS:26B4h (100) and DS:26B5h (63), full 255 and 127 (the
  slider, then the sound driver's volume); found by three memory dumps (the start, full, and full again: the
  bytes that changed with the bar and stayed). They are initialised data in DSUN.EXE (file 4F6B4h, after
  "865\0"); Shattered Lands has the same at file 4AC8Eh (DS:232Eh, 232Fh).
- The narration in DOSBox-X with the copy's 4F6B4h poked (sbmixer on): volume 63, peak -24.1 (the first 21 s:
  -26.5); 71, -20.2; 79, -18.5 (RMS -34.9, GOG's DOSBox at 63: -34.4); 87, -14.5; 91 and 95, -10.5; 111, -2.5;
  127, **0.0**. GOG's DOSBox at 127: 0.0. So DOSBox-X at 79 plays as loud as GOG's DOSBox at 63.
- **A loaded game takes the volume from the roster**: CHARSAVE.GFF's PREF 100 (written at every save), +2 the
  slider, +3 the volume (the sequel's load at 7D97Eh, Shattered Lands' at 74821h). A new game keeps the
  program's own. The sequel's CHARSAVE.GFF as GOG installs it says 255 and 63; Shattered Lands' saves 100 and
  63. Seen: the patched start (9F 4F at the title) became 63 again when `fountain-user` was loaded, until the
  roster was set too.

**The fix** (`dsloader/sfxvolume.py`): the sequel starts at full in both emulators (ravager's
`sfx_volume_full`), its speech and effects as recorded, level with its CD music: narration -18.4 dB RMS, peak 0,
in DOSBox-X and in GOG's DOSBox with the card's mixer on, the menu still working. Shattered Lands starts at 79
in DOSBox-X alone (gamepatch's `sfx_volume_dosbox_x`, left out under GOG's DOSBox). The Loader writes the same
into the roster at each start, but only over the starting values (the game's 100/63, the sequel's stock
255/63, or Shattered Lands' 159/79 going back to 63 under GOG's DOSBox): a volume the player set stays.

**Shattered Lands** (`fountain-user`, the ambush's start: the talk clicked through, then END TURN twelve
times): GOG's DOSBox at 63, the fight's start -27.8 dB RMS (loudest 400 ms), peak -20.9 (2,964); DOSBox-X as
shipped (63) the ceiling -24.1 (2,042); DOSBox-X with the fix (79, from the roster on loading) **-27.7 dB RMS**,
peak -16.1 (5,136). Its music is MIDI, which the card's mixer never touched, so its balance stays GOG's DOSBox's.

**Tools learned:**
- **DOSBox-X from apt** (2024.03.01) runs the Loader's configuration (the `memory file` line is then unknown:
  drop it) but makes no memory file: `start_dosboxx.sh` starts it and then fails at the dice log. The kit's
  tools still work through the process's memory if `launch.game_memory_file` is made to return "" (a three-line
  wrapper that runs the tool with `runpy`): `click.py`, `state.py`, `playsound.py` all did.
- **Two configuration files, not one**: in DOSBox 0.74 a section repeated within one file doesn't override
  (`sbtype=sbpro2` after GOG's `sbtype=sb16` in one file still gave `BLASTER=... T6`); a second `-conf` file
  does (T4). The Loader passes GOG's file then its own, so its `[sblaster]` line wins.
- **playsound.py is refused while a menu or talk box is up** ("not taken"): the map's loop isn't running.
- **The sequel's menus by key**: in a talk the number keys and Space; Escape with nothing up is EXIT GAME?
  (C cancels); in a fight Q opens the END menu and E ends the turn; I the inventory. The window must show the
  whole 640x480 picture for `ravclick.py` work to be seen: DOSBox-X's `scaler=none` and
  `windowresolution=original` (the Loader's normal3x window at 960x720 showed its top-left only).
- **Shattered Lands' fight sounds for a measurement**: run `start_dosboxx.sh` with `PT_NO_DICE=1` and wait 10 s before the
  load's clicks; a run whose load put the leader elsewhere (turn 3, 888,1512) made no sound in 90 s of turns.
