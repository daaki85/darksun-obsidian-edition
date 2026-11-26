#!/bin/sh
# dbxadopt.sh: makes the kit's tools follow the game the Loader itself started (its window's Start
# the game, `launch` or `play`) rather than one of the kit's start scripts: it writes that game's
# pid, read from the Loader's lock file (obsidian-edition/game.lock), into $PLAYTEST_WORK/dsun.pid,
# which live.py reads. For a game in DOSBox-X the Loader's connect then finds the memory file by
# that process (the lock file names it), so the tools read and write the same file the Loader
# does; for a DOSBox 0.74 they read its process as ever. Run it with PT_DISPLAY and PLAYTEST_WORK
# set as for the other tools, after the game has started; it moves the game's window to 0,0 (the
# tools' clicks and grabs expect it there) and prints the pid, the program and the memory file.
. "$(dirname "$0")/env.sh"
cd "$REPO/obsidian-edition" || exit 1
python3 -c "
from dsloader import launch
pid, name = launch.lock_game()
if not pid or not launch.game_alive(pid, name):
    raise SystemExit('no game started by the Loader is running (game.lock)')
open('$WORK/dsun.pid', 'w').write(str(pid))
print('adopted: pid', pid, name, '; memory file:', launch.lock_memory() or '(none: read from the process)')" || exit 1
W=$(timeout 10 xdotool search --class dosbox | head -1)
[ -n "$W" ] && timeout 5 xdotool windowmove "$W" 0 0
exit 0
