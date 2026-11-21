#!/bin/sh
# ravcreation.sh [ROLLS]: Wake of the Ravager started as the Loader starts it (ravstart.sh, RAV_LOADER=1,
# to the title menu), CREATE CHARACTERS (160,92), a right-click on the roster's first slot (70,56), NEW
# (110,57), then ravcreation.py ROLLS (the die pressed, each roll's hit points checked). Kills
# nothing: stop an earlier DOSBox first. About 2 minutes and 3 s a roll.
. "$(dirname "$0")/env.sh"
RAV_LOADER=1 RAV_MENU=1 sh "$PT/ravstart.sh" "$WORK/rav" | tail -1 || exit 1
W=$(xdotool search --pid "$(cat "$WORK/rav.pid")" | tail -1)
xdotool mousemove --window "$W" 400 200; sleep 0.3; xdotool click --window "$W" 1; sleep 1
cd "$PT"
python3 ravclick.py 160 92 >/dev/null; sleep 4
python3 ravclick.py 70 56 right >/dev/null; sleep 2
python3 ravclick.py 110 57 >/dev/null; sleep 4
python3 ravcreation.py "${1:-20}"
