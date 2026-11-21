#!/bin/sh
# start_dosboxx.sh DOSBOX-X [name=value ...]: the mod in DOSBox-X (the Options tab's other engine:
# dsloader/dosboxx.py), a game of its own beside the shared one, for the kit's tools.
# DOSBOX-X is the path of its program (2025.01.01 or later: "memory file"). The game's memory is
# a file, which the Loader's dice log and every tool that goes through live.py read and write
# instead of DOSBox's process (process.FileMemory): the tools find it by the game's pid in
# $PLAYTEST_WORK/dsun.pid (the Loader reads the memory file's name from that DOSBox-X's own
# configuration), so each shell that uses them needs only PT_DISPLAY and PLAYTEST_WORK:
#   PT_DISPLAY=:59 PLAYTEST_WORK=/some/scratch sh start_dosboxx.sh /path/to/dosbox-x
# ($PLAYTEST_WORK/inst the game: a copy of the shared one's folder will do; never :55 or
# /tmp/playtest, the shared game's). It stops only the DOSBox-X and dice log it started before
# (their pid files in the work folder), and starts an Xvfb on PT_DISPLAY if there is none.
# The configuration is the Loader's own for the saved settings, with the window single (320x240),
# no quick saves and no autosaves (a test game: PLAYTESTING.md, rule 8); the settings after the
# program change it: cycles=N and core=normal|dynamic (a test's own speed), window_scale=3,
# fullscreen=true, picture=scanlines, soundfont=FILE, midi_device=N, dice_log=false (the game as
# it came), capture=DIR, extra=section|name=value. PT_SAVE=NAME loads saves/NAME as loadsave.sh
# does. PT_NO_DICE=1 starts no dice log. PT_SDL_AUDIO names SDL's audio driver (default dummy).
# For a game started by the Loader itself (its window, or `play`), see dbxadopt.sh.
. "$(dirname "$0")/env.sh"
DBX=$1; [ -x "$DBX" ] || { echo "usage: PT_DISPLAY=:59 PLAYTEST_WORK=DIR sh start_dosboxx.sh /path/to/dosbox-x [name=value ...]"; exit 1; }
shift
if [ "$DISPLAY" = ":55" ] || [ "$WORK" = /tmp/playtest ]; then echo "set PT_DISPLAY and PLAYTEST_WORK: not the shared game's"; exit 1; fi
MEM=${PT_MEMFILE:-/dev/shm/dsun-$(basename "$WORK")-$$.mem}
timeout 5 xdotool getdisplaygeometry >/dev/null 2>&1 || { (setsid nohup Xvfb "$DISPLAY" -screen 0 1600x1000x24 >/dev/null 2>&1 &); sleep 1; }
for f in dice.pid dbx.pid; do   # (only ours, and only if the pid is still that program)
  p=$(cat "$WORK/$f" 2>/dev/null); [ -n "$p" ] || continue
  case "$(cat /proc/$p/comm 2>/dev/null)" in dosbox-x|python3*) kill "$p";; esac
done; sleep 1
[ -f "$WORK/memfile.path" ] && rm -f "$(cat "$WORK/memfile.path")"
if [ -n "$PT_SAVE" ]; then
  [ -d "$PT/saves/$PT_SAVE" ] || { echo "no save $PT/saves/$PT_SAVE"; exit 1; }
  cp "$PT/saves/$PT_SAVE"/SAVE01.SAV "$PT/saves/$PT_SAVE"/CHARSAVE.GFF "$PT/saves/$PT_SAVE"/DARKSAVE.GFF "$GAME/"
fi
cd "$REPO/obsidian-edition" || exit 1
python3 -c "
from dsloader import launch
s = launch.load_settings(); s.update(game_dir='$GAME', window_scale=1, fullscreen=False, autosave=False, quick_save=False); launch.save_settings(s)"
ARGS=$(python3 -m dsloader.dosboxx "$GAME" "$WORK/dosboxx.conf" "$MEM" "$@") || exit 1
echo "$MEM" > "$WORK/memfile.path"
cd "$WORK" && (SDL_AUDIODRIVER=${PT_SDL_AUDIO:-dummy} SDL_DISKAUDIOFILE="${PT_AUDIO:-/dev/null}" setsid nohup "$DBX" $ARGS > "$WORK/dosbox.log" 2>&1 < /dev/null & echo $! > "$WORK/dbx.pid")
cp "$WORK/dbx.pid" "$WORK/dsun.pid"   # (live.py's)
if [ -z "$PT_NO_DICE" ]; then
  sleep 5; cd "$REPO/obsidian-edition" && (setsid nohup python3 -u -m dsloader dicelog --pid "$(cat "$WORK/dbx.pid")" > "$WORK/dice.txt" 2>&1 < /dev/null & echo $! > "$WORK/dice.pid")
fi
echo "started: DOSBox-X pid $(cat "$WORK/dbx.pid"), memory file $MEM"
[ -n "$PT_SAVE" ] || exit 0
sleep 8; W=$(timeout 10 xdotool search --class dosbox | head -1)   # (the title, the menu, LOAD: as loadsave.sh)
timeout 5 xdotool windowmove $W 0 0; timeout 5 xdotool mousemove 160 120; sleep 0.3
timeout 5 xdotool click 1; sleep 1; timeout 5 xdotool click 1; sleep 12
timeout 15 python3 "$PT/click.py" 170 109 >/dev/null; sleep 4
timeout 15 python3 "$PT/click.py" 100 46 >/dev/null; sleep 1
timeout 15 python3 "$PT/click.py" 253 46 >/dev/null; sleep 12
timeout 10 python3 "$PT/state.py"
