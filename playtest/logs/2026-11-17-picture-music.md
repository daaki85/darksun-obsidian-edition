# The picture and the music device (2026-11-17)

Under test: the Loader's two new choices on the Options tab (**Picture and music**): the picture
(plain, scanlines, tv, sharp: `launch.display_lines`) and the music device (`midiout.py`). Both
are lines in the DOSBox configuration the Loader writes. DOSBox 0.74-3 on Linux throughout (GOG's
is 0.74-2.1 for Windows; its source, beside GOG's DOSBox, was read for what each setting does).

## Without the game: a pattern in the game's screen mode (`picpattern.sh`)

A DOSBox of its own (a copy named `dbpat`, display `:57` at 1920x1080, no game files, no lock)
showing a pattern in mode 13h with the Loader's display lines.

| Window | Picture | Settings written | Window | Seen |
|---|---|---|---|---|
| Triple | plain | `scaler=normal3x` | 960x720 | rows of 3 or 4 lines (the aspect correction) |
| Triple | scanlines | `scaler=scan3x` | 960x720 | lit, lit, black; the black line twice under 3 rows in 5 |
| Triple | tv | `scaler=tv3x` | 960x720 | each row full, about 5/8, about 1/3 |
| Triple | sharp | `output=openglnb`, `windowresolution=960x720`, `scaler=normal3x` | 960x720 | as plain |
| Double | scanlines | `scaler=scan2x` | 640x480 | lit, then one or two black |
| Double | sharp | `output=openglnb`, `windowresolution=640x480`, `scaler=normal2x` | 640x480 | as plain |
| Quadruple | plain | `output=opengl`, `windowresolution=1280x960`, `scaler=normal2x` | 1280x960 | smoothed (as before) |
| Quadruple | scanlines, tv | the same with `scan2x`, `tv2x` | 1280x960 | smoothed lines 4.8 apart |
| Quadruple | sharp | the same with `output=openglnb` | 1280x960 | columns of 4, rows of 4 or 5, one colour each |
| Single | tv (asked) | `scaler=none` | 320x240 | plain: the kit's window is untouched |
| Full screen | plain | nothing | 1920x1080 | **not stretched** on Linux (the surface output) |
| Full screen | sharp | `output=openglnb` | 1920x1080 | 1440x1080 in the middle, rows of 5 or 6 lines |
| Full screen | scanlines, tv | `scaler=scan3x`, `tv3x` | 1920x1080 | not stretched on Linux: for Windows to show |

DOSBox complained of nothing but GOG's `output=ddraw` ("not a valid value... reset to surface":
Linux has no DirectDraw) and the missing ALSA sequencer. OpenGL worked under Xvfb.

## In the game: each picture at Triple (`picstart.sh`)

Under the lock, a start of its own for each of plain, scanlines, tv and sharp at `window_scale` 3
(not the kit's start), `pens-after-arena` loaded by `click.py`, about 75 s each.

- The window was 960x720 each time (`xdotool getwindowgeometry`), the game loaded (region 29h,
  leader at 1672, 344) and DOSBox's log had no complaint.
- **The pointer tracked the same with every picture**: `click.py` reached every place asked
  (170,109; 100,46; 253,46; 250,150; 40,30, each within a pixel or two), and `picmove.py` read the
  same three moves with all four: 90 screen pixels across moved it 28 game pixels, 90 down 23, and
  60 up and left (18, 15). (`sensitivity=33` in each.)
- Grabs of the window (`import -window`): scanlines and tv as in the pattern. Sharp and plain
  differ only in which rows get the fourth line.
- `docs/picture-modes.png`: the party from the plain, scanlines and tv grabs, side by side at
  the window's own size.
- Afterwards `window_scale` is 1 and no picture is stored in settings.json (`picstart.sh` puts
  them back as soon as the configuration is written).

Water: no new area (the slave pens' start only).

## Not seen (for the owner's Windows)

- GOG's DirectDraw output: how it stretches Scanlines and TV in a window (600 lines to 720) and
  in full screen, and that Sharp differs from Plain there at Double and Triple.
- OpenGL (`opengl`, `openglnb`) on the owner's graphics driver, in a window and full screen, and
  Alt+Enter between them with each picture.
- The music device: the list of Windows' MIDI devices by name, a device chosen playing the music,
  and the default as before. This container has no MIDI at all ("MIDI:Opened device:none"); the
  list is tested with a stand-in for winmm.
