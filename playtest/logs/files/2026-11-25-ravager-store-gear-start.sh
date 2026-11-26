#!/bin/sh
# 2026-11-25-ravager-store-gear-start.sh TAG [SKIP] (run from anywhere): ravSG, a fresh copy of $WORK/rav (thrown
# away after), started as the Loader starts it (RAV_SKIP=SKIP for a control: roll_store,gear_done), the dice log
# (ravdice.py) into $WORK/sg-TAG.txt (its pid in $WORK/sg-TAG.dpid), then CREATE CHARACTERS, a right click on the
# roster's first slot and NEW: the creation screen up, a shot in $WORK/sg-TAG-new.png.
PT=$(cd "$(dirname "$0")/../.." && pwd); cd $PT; export DISPLAY=:55 PLAYTEST_WORK=/tmp/playtest
W0=/tmp/playtest; TAG=$1; SKIP=$2; F=$W0/ravSG
rm -rf $F; cp -a $W0/rav $F
RAV_SKIP=$SKIP RAV_LOADER=1 RAV_MENU=1 RAV_STDOUT=1 timeout 200 sh ravstart.sh $F > $W0/sg-$TAG.start 2>&1
W=$(xdotool search --pid "$(cat $W0/rav.pid)" | tail -1)
xdotool mousemove --window "$W" 400 200; sleep 0.3; xdotool click --window "$W" 1; sleep 1
: > $W0/sg-$TAG.txt
RAV=$F setsid nohup timeout 3000 python3 ravdice.py 3000 $W0/sg-$TAG.txt > $W0/sg-$TAG.out 2>&1 &
echo $! > $W0/sg-$TAG.dpid
sleep 6
timeout 30 python3 ravclick.py 160 92 >/dev/null; sleep 4
timeout 30 python3 ravclick.py 70 56 right >/dev/null; sleep 2
timeout 30 python3 ravclick.py 110 57 >/dev/null; sleep 4
import -window $W $W0/sg-$TAG-new.png
echo "$TAG at the creation screen (window $W, DOSBox $(cat $W0/rav.pid))"
