#!/bin/sh
# start_recomp.sh: the game on Dark Sun Recompiled ($DSUN, its build of the mod) instead of DOSBox,
# with the Loader's patched game prepared as start.sh does and the dice log attached. The window
# is made 320x240 at 0,0, the size of DOSBox's, so the kit's window grabs and pixel checks read
# the same places. Use with PT_TARGET=recomp exported for every tool afterwards. Kills any old ones.
. "$(dirname "$0")/env.sh"
[ -x "$DSUN" ] || { echo "no program at $DSUN (DSUN=... names it)"; exit 1; }
pgrep -x Xvfb >/dev/null || (Xvfb :55 -screen 0 1024x768x24 >/dev/null 2>&1 &); sleep 1
for p in $(pgrep -f "^python3 -u -m dsloade[r]"); do kill $p; done; pkill -9 -x dosbox
[ -f "$WORK/dsun.pid" ] && kill -9 $(cat "$WORK/dsun.pid") 2>/dev/null   # (only the test's own: other dsun runs may be headless tests)
sleep 1
cd "$REPO/obsidian-edition" && python3 -c "
from dsloader import launch
s = launch.load_settings(); s['game_dir'] = '$GAME'; launch.save_settings(s)
print('problem:', launch.prepare_patched_game('$GAME'))"
cd "$GAME" && (SDL_AUDIODRIVER=dummy setsid "$DSUN" --game "$GAME" --cd "$REPO/obsidian-edition/dos" > "$WORK/dsun.log" 2>&1 < /dev/null & echo $! > "$WORK/dsun.pid")
# (the pid is the test's own program: other dsun processes may run, headless tests of the
#  recompiled program, and the dice log and the tools must not pick those)
for i in $(seq 1 30); do W=$(timeout 5 xdotool search --name Recompiled | head -1); [ -n "$W" ] && break; sleep 1; done
[ -z "$W" ] && { echo "no window (see $WORK/dsun.log)"; exit 1; }
[ "$(cat /proc/$(cat "$WORK/dsun.pid")/comm 2>/dev/null)" = dsun ] || pgrep -n -x dsun > "$WORK/dsun.pid"
timeout 5 xdotool windowmove $W 0 0; timeout 5 xdotool windowsize $W 320 240; sleep 1
cd "$REPO/obsidian-edition" && (setsid nohup python3 -u -m dsloader dicelog --pid $(cat "$WORK/dsun.pid") > "$WORK/dice.txt" 2>&1 < /dev/null &)
sleep 3; grep -m1 "Dark Sun" "$WORK/dsun.log"; echo started
