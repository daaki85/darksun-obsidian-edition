#!/bin/sh
# shot.sh OUT.png: a screenshot of the game (DOSBox's own capture, Ctrl+F5: the 320x200 picture)
. "$(dirname "$0")/env.sh"
W=$(timeout 5 xdotool search --class dosbox | head -1); [ -z "$W" ] && { echo "NO DOSBOX (see $WORK/dosbox.log)"; exit 1; }
rm -f "$GAME"/__support/app/capture/*.png; timeout 5 xdotool key --window $W ctrl+F5; sleep 2
mv "$GAME"/__support/app/capture/*.png "$1"
