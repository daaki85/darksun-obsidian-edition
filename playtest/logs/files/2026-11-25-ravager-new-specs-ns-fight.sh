#!/bin/sh
# ns-fight.sh TAG [SECONDS]: Computer Control for the four (C, the USE screen's lower small icons), the fight
# followed SECONDS (default 240), DSCLOG2's counters, then its own dice log and DOSBox stopped by their pids.
PT=/tmp/claude-0/-home-claude/64ea2217-da22-5669-9254-2672bfc4a609/scratchpad/kit/playtest; cd $PT; export DISPLAY=:57 PLAYTEST_WORK=/tmp/playtest/nswork PATH=/tmp/claude-0/-home-claude/64ea2217-da22-5669-9254-2672bfc4a609/scratchpad/bin:$PATH
W0=/tmp/playtest/nswork; TAG=$1; SEC=${2:-240}; W=$(cat $W0/ns-gw)
c(){ timeout 30 python3 ravclick.py "$@" >/dev/null; }
xdotool key --window $W c; sleep 3
for p in "47 53" "98 53" "47 112" "98 112"; do c $p; sleep 1.5; done
import -window $W $W0/ns-$TAG-cc.png
xdotool key --window $W Escape
P=$(cat $W0/ns-$TAG.dbpid)
for i in $(seq 1 $((SEC / 5))); do sleep 5; [ "$(cat /proc/$P/comm 2>/dev/null)" = dbns ] || { echo "$TAG DEAD"; break; }; done
import -window $W $W0/ns-$TAG-last.png 2>/dev/null
timeout 30 python3 ravkits.py count >> $W0/ns-$TAG.kits 2>&1
D=$(cat $W0/ns-$TAG.dpid); kill $D 2>/dev/null
[ "$(cat /proc/$P/comm 2>/dev/null)" = dbns ] && kill $P
echo "$TAG done"
