#!/bin/sh
# loadsave.sh NAME: start the game (start.sh) with the save in saves/NAME copied into the game
# folder (as slot 1), and load it: the title screens clicked past, LOAD SAVED GAME (170, 109), the
# first slot (100, 46), LOAD (253, 46). Prints the state once loaded.
. "$(dirname "$0")/env.sh"
[ -d "$PT/saves/$1" ] || { echo "no save $PT/saves/$1"; exit 1; }
cp "$PT/saves/$1"/SAVE01.SAV "$PT/saves/$1"/CHARSAVE.GFF "$PT/saves/$1"/DARKRUN.GFF "$GAME/"
sh "$PT/start.sh" | tail -1; sleep 12
W=$(timeout 10 xdotool search --class dosbox | head -1)
timeout 5 xdotool windowmove $W 0 0; timeout 5 xdotool mousemove 160 120; sleep 0.3
timeout 5 xdotool click 1; sleep 1; timeout 5 xdotool click 1; sleep 12
timeout 15 python3 "$PT/click.py" 170 109 >/dev/null; sleep 4
timeout 15 python3 "$PT/click.py" 100 46 >/dev/null; sleep 1
timeout 15 python3 "$PT/click.py" 253 46 >/dev/null; sleep 12
timeout 10 python3 "$PT/state.py"
