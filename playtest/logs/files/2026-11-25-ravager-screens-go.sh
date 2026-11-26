#!/bin/sh
# 2026-11-25-ravager-screens-go.sh: a fresh copy of ravG48 (the transferred party) started with the Loader's helper from the screens
# worktree, the four ADDed, a new game, the dice log attached; up to the opening talk's last line.
cd "$(dirname "$0")/../.."; export DISPLAY=:55 PLAYTEST_WORK=/tmp/playtest
rm -rf /tmp/playtest/ravSC; cp -r /tmp/playtest/ravG48 /tmp/playtest/ravSC
RAV_LOADER=1 RAV_MENU=1 timeout 200 sh ravstart.sh /tmp/playtest/ravSC > /tmp/playtest/ravSC.out 2>&1
W=$(xdotool search --pid "$(cat /tmp/playtest/rav.pid)" | tail -1); echo $W > /tmp/playtest/gw
c(){ timeout 30 python3 ravclick.py "$@" >/dev/null; }
c 160 92; sleep 1; c 160 92; sleep 3; c 70 56 right; sleep 1.5; c 115 69; sleep 2; c 130 78; sleep 1; c 252 47; sleep 3
c 75 171; sleep 2; c 121 171; sleep 2; c 170 186; sleep 2
for s in "120 56" "70 115" "120 115"; do set -- $s; c $1 $2 right; sleep 1.5; c $(($1+45)) $(($2+13)); sleep 2; c 130 45; sleep 1; c 252 47; sleep 3; done
xdotool key --window $W Escape; sleep 3; xdotool key --window $W s
RAV=/tmp/playtest/ravSC setsid nohup timeout 3000 python3 ravdice.py --numbers 2900 /tmp/playtest/scr-dice.txt > /tmp/playtest/scr-dice.out 2>&1 &
echo $! > /tmp/playtest/scr-dice.pid
sleep 90; c 100 171; sleep 4
import -window $W /tmp/playtest/scr-go.png; echo ready
