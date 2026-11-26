#!/bin/sh
# 2026-11-25-ravager-quick-saves-start.sh [OFF] (run from playtest/): ravQS (a fresh copy of rav, thrown away
# after), ravager-after-ambush loaded through the Loader's start, then the dice log (RAV=ravQS) in the
# background, its pid in $WORK/qs.dpid. OFF: no dice log (the control: F5 the game's own again).
PT=$(cd "$(dirname "$0")/../.." && pwd); cd "$PT"; export DISPLAY=:55 PLAYTEST_WORK=/tmp/playtest
W0=/tmp/playtest; F=$W0/ravQS
rm -rf $F; cp -a $W0/rav $F
rm -f $F/SAVQ*.SAV
RAV_STDOUT=1 timeout 300 sh ravload.sh ravager-after-ambush $F > $W0/qs.start 2>&1
xdotool search --pid "$(cat $W0/rav.pid)" | tail -1 > $W0/qsw
[ -n "$1" ] && { echo "control: no dice log"; exit 0; }
: > $W0/qs.txt
RAV=$F setsid nohup timeout 2400 python3 ravdice.py 2400 $W0/qs.txt > $W0/qs.out 2>&1 &
echo $! > $W0/qs.dpid
sleep 10; timeout 20 python3 ravquick.py
