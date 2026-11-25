#!/bin/sh
# 2026-11-25-ravager-loot-tabs-join-start.sh [OFF] (run from playtest/): ravJ5 (a fresh copy of rav, thrown away
# after), ravager-after-ambush loaded through the Loader's start (RAV_SKIP passes through for a control), then the
# dice log (RAV=ravJ5) in the background, its pid in $WORK/j5.dpid, its lines in $WORK/j5.txt.
# OFF: no dice log (the control: the keys the game's own).
PT=$(cd "$(dirname "$0")/../.." && pwd); cd "$PT"; export DISPLAY=:55 PLAYTEST_WORK=/tmp/playtest
W0=/tmp/playtest; F=$W0/ravJ5
rm -rf $F; cp -a $W0/rav $F
rm -f $F/SAVQ*.SAV
RAV_STDOUT=1 timeout 300 sh ravload.sh ravager-after-ambush $F > $W0/j5.start 2>&1
xdotool search --pid "$(cat $W0/rav.pid)" | tail -1 > $W0/j5w
[ -n "$1" ] && { echo "control: no dice log"; exit 0; }
: > $W0/j5.txt
RAV=$F setsid nohup timeout 3000 python3 ravdice.py 3000 $W0/j5.txt > $W0/j5.out 2>&1 &
echo $! > $W0/j5.dpid
