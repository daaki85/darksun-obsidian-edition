#!/bin/sh
# shot.sh OUT.png: a screenshot of the game (DOSBox's own capture, Ctrl+F5: the 320x200 picture)
. "$(dirname "$0")/env.sh"
W=$(timeout 5 xdotool search $WINQ | head -1); [ -z "$W" ] && { echo "NO GAME WINDOW (see $WORK/dosbox.log or $WORK/dsun.log)"; exit 1; }
if [ "$TARGET" = recomp ]; then
  # (the recompiled program: a grab of its 4:3 window, scaled back to the game's 320x200 pixels)
  timeout 10 import -window $W png:- | convert - -filter point -resize '320x200!' "$1"
else
  rm -f "$GAME"/__support/app/capture/*.png; timeout 5 xdotool key --window $W ctrl+F5; sleep 2
  mv "$GAME"/__support/app/capture/*.png "$1"
fi
