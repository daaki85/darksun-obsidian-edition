#!/bin/sh
# 2026-11-25-ravager-blast-log-creation.sh TAG [SKIP] (run from anywhere): ravBLC, a fresh copy of $WORK/rav, started as the
# Loader starts it (RAV_SKIP=SKIP for a control: rl_try), CREATE CHARACTERS, NEW on the roster's first slot (ravcreation.sh's
# clicks), the dice log (ravdice.py) into $WORK/blc-TAG.txt, then the die pressed ROLLS (8) times by ravcreation.py.
PT=$(cd "$(dirname "$0")/../.." && pwd); cd $PT; export DISPLAY=:55 PLAYTEST_WORK=/tmp/playtest
W0=/tmp/playtest; TAG=$1; SKIP=$2; F=$W0/ravBLC
rm -rf $F; cp -a $W0/rav $F
RAV_SKIP=$SKIP RAV_LOADER=1 RAV_MENU=1 timeout 200 sh ravstart.sh $F > $W0/blc-$TAG.start 2>&1
W=$(xdotool search --pid "$(cat $W0/rav.pid)" | tail -1)
xdotool mousemove --window "$W" 400 200; sleep 0.3; xdotool click --window "$W" 1; sleep 1
timeout 30 python3 ravclick.py 160 92 >/dev/null; sleep 4
timeout 30 python3 ravclick.py 70 56 right >/dev/null; sleep 2
timeout 30 python3 ravclick.py 110 57 >/dev/null; sleep 4
: > $W0/blc-$TAG.txt
setsid nohup timeout 400 python3 ravdice.py 400 $W0/blc-$TAG.txt > $W0/blc-$TAG.out 2>&1 &
sleep 8
timeout 120 python3 ravcreation.py 8 > $W0/blc-$TAG.rolls 2>&1
sleep 3
import -window $W $W0/blc-$TAG.png
timeout 30 python3 ravkits.py blast > $W0/blc-$TAG.blast 2>&1
echo "$TAG done"
