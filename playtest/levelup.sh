#!/bin/sh
# levelup.sh: if CHOOSE A SPELL is up (a preserver's level-up, mid-fight; a scroll whose rollers'
# pixels, in the 320x240 window grab, are 146,56,69 at 73,54 and 113,56,73 at 247,54), click the first spell (125, 90) and exit
# 0; else exit 1. It blocks the whole game until a spell is picked (2026-11-01, Cermak in the arena).
. "$(dirname "$0")/env.sh"
W=$(timeout 5 xdotool search $WINQ | head -1)
p=$(timeout 10 import -window $W png:- | convert - -format '%[pixel:p{73,54}] %[pixel:p{247,54}]' info:)
[ "$p" = "srgb(146,56,69) srgb(113,56,73)" ] || exit 1
timeout 15 python3 "$PT/click.py" 125 90 >/dev/null; sleep 2; echo "picked a spell (CHOOSE A SPELL)"; exit 0
