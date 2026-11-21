#!/bin/sh
# loadquick.sh [ROW]: start the game (start.sh) and load a save of the QUICK page (SAVQnn.SAV, the
# quick saves and autosaves: dsloader/quicksave.py) that is in the game folder already, from the
# main menu: LOAD SAVED GAME (170, 109), the QUICK button (253, 165), row ROW (default 1; the rows
# are 11 apart from y 46), LOAD (253, 46). Copies nothing: the folder's CHARSAVE.GFF and
# DARKSAVE.GFF are used as they are. Prints the state once loaded.
. "$(dirname "$0")/env.sh"
ROW=${1:-1}
sh "$PT/start.sh" | tail -1; sleep 12
W=$(timeout 10 xdotool search $WINQ | head -1)
timeout 5 xdotool windowmove $W 0 0; timeout 5 xdotool mousemove 160 120; sleep 0.3
timeout 5 xdotool click 1; sleep 1; timeout 5 xdotool click 1; sleep 12
timeout 15 python3 "$PT/click.py" 170 109 >/dev/null; sleep 4
timeout 15 python3 "$PT/click.py" 253 165 >/dev/null; sleep 1.5
timeout 15 python3 "$PT/click.py" 100 $((46 + 11 * (ROW - 1))) >/dev/null; sleep 1
timeout 15 sh "$PT/shot.sh" "$WORK/loadquick.png" >/dev/null 2>&1
timeout 15 python3 "$PT/click.py" 253 46 >/dev/null; sleep 12
timeout 10 python3 "$PT/state.py"
