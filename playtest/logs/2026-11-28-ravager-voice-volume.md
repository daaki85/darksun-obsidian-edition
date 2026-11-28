# 2026-11-28: Wake of the Ravager's quiet speech (DOSBox-X and GOG's DOSBox)

**Under test:** the user heard the sequel's spoken voice barely at all in DOSBox-X (the Windows default). Where
the level goes, in both emulators, and the fix (branch `claude/ravager-voice-volume`).

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

- **Cause:** the game's sound driver (SOUND.CFG: `sbpdig.adv`, the SB Pro II's) turns the card's mixer down,
  and with `sbmixer=true` (both emulators' default, and GOG's setting) the emulator turns its Sound Blaster
  channel down with it: 16 dB in 0.74, 24 dB in DOSBox-X (its SB16 mixer takes about 8 dB more). The CD's
  audio tracks never pass the card's mixer there, so they play at full level: the speech came out 24 dB under
  the music in DOSBox-X, 16 dB under in GOG's own DOSBox. It is not the Loader's doing (GOG's settings alone
  give the 16 dB) and not the card's address, IRQ or DMA.
- Matching the narration against `INTR49.VOC` (`files/2026-11-28-voice-volume-match.py`, cross-correlation):
  0.74 r 0.70, gain -18.7 dB on the whole stretch. In DOSBox-X r only 0.24 (its resampling to 48 kHz drifts
  against a straight 21,739 Hz resample over 48 s), so its level is read from the RMS and peaks above instead.
- **Fix:** `sbmixer=false` for the sequel in both emulators (`ravager.SOUND_LINES` in the Loader's file for
  GOG's DOSBox, after GOG's `sbmixer=true`; `dosboxx.conf_lines` for the sequel). Recorded again with the
  Loader's new configurations: DOSBox-X with the CD music, narration -18.4 dB RMS (peak 0) beside the title
  music's -18.7; 0.74 the same -18.4. The game menu's SOUND EFFECT VOLUME no longer changes anything (F5 still
  turns the effects off). `sbtype=sbpro2` was the other candidate (the game's card): it changes nothing in 0.74
  and leaves the speech 11 dB down in DOSBox-X.
- **No music under the speech here:** with the CD mounted, the title menu played track music, but the
  narration and Kael's first line played with no CD track under them (the same levels as a run with the data
  track alone). Whether area music and speech overlap later, and whether they then clip, is for the user's ear.

**Shattered Lands** (`fountain-user`, a fight with END TURN clicked twelve times, DOSBox-X 2024 sb16): the
sound effects' ceiling -24.1 dB (2,042), the same as the sequel's in DOSBox-X; in GOG's DOSBox it is about -21 dB
(2,960, logs/2026-11-09-sounds-louder.md). Its music is MIDI (the MT-32/MPU driver, `mt32mpu.adv`), which the
card's mixer never touched on real hardware either, so its balance stays as GOG's: Shattered Lands' settings are
unchanged (about 3 dB quieter effects in DOSBox-X than in GOG's DOSBox, left for the user's ear).

**Tools learned:**
- **DOSBox-X from apt** (2024.03.01) runs the Loader's configuration (the `memory file` line is then unknown:
  drop it) but makes no memory file: `start_dosboxx.sh` starts it and then fails at the dice log. The kit's
  tools still work through the process's memory if `launch.game_memory_file` is made to return "" (a three-line
  wrapper that runs the tool with `runpy`): `click.py`, `state.py`, `playsound.py` all did.
- **Two configuration files, not one**: in DOSBox 0.74 a section repeated within one file doesn't override
  (`sbtype=sbpro2` after GOG's `sbtype=sb16` in one file still gave `BLASTER=... T6`); a second `-conf` file
  does (T4). The Loader passes GOG's file then its own, so its `[sblaster]` line wins.
- **playsound.py is refused while a menu or talk box is up** ("not taken"): the map's loop isn't running.
