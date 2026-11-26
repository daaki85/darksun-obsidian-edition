#!/bin/sh
# 2026-11-25-ravager-quick-saves-fight.sh (run from playtest/): ravQS2 (a fresh copy of ravK, thrown away
# after), the Loader's start, the four ADDed, a new game, the opening talk to the Draxans' ambush, the dice
# log; stops at the ambush's first turn. HP=1: the four given HP 250 first (a test edit: the copy is thrown away
# after, its saves never kept), so they win.
# The clicks are the Tab log's (2026-11-25-ravager-tab-target-run.sh) (its HP edits only with HP=1).
PT=$(cd "$(dirname "$0")/../.." && pwd); cd "$PT"; export DISPLAY=:55 PLAYTEST_WORK=/tmp/playtest
W0=/tmp/playtest; F=$W0/ravQS2
rm -rf $F; cp -a $W0/ravK $F; rm -f $F/SAVQ*.SAV
RAV_LOADER=1 RAV_MENU=1 RAV_STDOUT=1 timeout 200 sh ravstart.sh $F > $W0/qs2.start 2>&1
W=$(xdotool search --pid "$(cat $W0/rav.pid)" | tail -1); echo $W > $W0/qsw
c(){ timeout 30 python3 ravclick.py "$@" >/dev/null; }
c 160 92; sleep 1; c 160 92; sleep 3; c 70 56 right; sleep 1.5; c 115 69; sleep 2; c 130 78; sleep 1; c 252 47; sleep 3
c 75 171; sleep 2; c 121 171; sleep 2; c 170 186; sleep 2
for s in "120 56" "70 115" "120 115"; do set -- $s; c $1 $2 right; sleep 1.5; c $(($1+45)) $(($2+13)); sleep 2; c 130 45; sleep 1; c 252 47; sleep 3; done
xdotool key --window $W Escape; sleep 3; xdotool key --window $W s; sleep 90; c 100 171; sleep 4
[ -n "$HP" ] && for m in 0 1 2 3; do timeout 30 python3 ravkits.py hp $m 250 >> $W0/qs2.kits 2>&1; done
: > $W0/qs2.txt
RAV=$F setsid nohup timeout 2400 python3 ravdice.py 2400 $W0/qs2.txt > $W0/qs2.out 2>&1 &
sleep 8
for i in 1 2 3; do c 100 171; sleep 4; done
import -window $W $W0/qs2-fight.png
echo ready
