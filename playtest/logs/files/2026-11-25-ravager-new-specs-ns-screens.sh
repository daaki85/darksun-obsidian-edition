#!/bin/sh
# ns-screens.sh TAG PORTRAIT_Y: in the fight, the inventory of the member whose portrait is at (25, Y), its View
# Character and Effects screens grabbed, then Escape.
PT=/tmp/claude-0/-home-claude/64ea2217-da22-5669-9254-2672bfc4a609/scratchpad/kit/playtest; cd $PT; export DISPLAY=:57 PLAYTEST_WORK=/tmp/playtest/nswork PATH=/tmp/claude-0/-home-claude/64ea2217-da22-5669-9254-2672bfc4a609/scratchpad/bin:$PATH
W0=/tmp/playtest/nswork; TAG=$1; Y=$2; W=$(cat $W0/ns-gw)
c(){ timeout 30 python3 ravclick.py "$@" >/dev/null; }
c 22 17; sleep 2; c 74 171; sleep 3; c 25 $Y; sleep 3; import -window $W $W0/ns-$TAG-inv$Y.png
c 170 187; sleep 3; import -window $W $W0/ns-$TAG-view$Y.png
c 122 171; sleep 3; import -window $W $W0/ns-$TAG-eff$Y.png
xdotool key --window $W Escape; sleep 3
