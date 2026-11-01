#!/bin/sh
# panel.sh hide|show: the combat log panel (bottom right) hidden or shown, by its frame's pixel at
# 140,125 (215,215,227 while it's up) and the L key, which toggles it. L blindly can leave it the
# wrong way round (topartyfight's step forward clicked the panel that way).
. "$(dirname "$0")/env.sh"
W=$(timeout 5 xdotool search --class dosbox | head -1)
up() { [ "$(timeout 10 import -window $W png:- | convert - -format '%[pixel:p{140,125}]' info:)" = "srgb(215,215,227)" ]; }
case "$1" in
  hide) up && { timeout 5 xdotool key --window $W l; sleep 1; } ;;
  show) up || { timeout 5 xdotool key --window $W l; sleep 1; } ;;
esac
up && echo "panel up" || echo "panel hidden"
