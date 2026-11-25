#!/bin/sh
# 2026-11-25-ravager-small-ports-run.sh TAG [SKIP [CHARGES_OFF]] (run from anywhere): ravSM, a fresh copy of $WORK/ravK (the
# fountain-user party transferred), started as the Loader starts it (RAV_SKIP=SKIP for a control's copy:
# ranger_two; CHARGES_OFF 1: RAV_CHARGES_OFF for the dice log), the four ADDed, a new game, the opening talk into the Draxans' ambush (the Tab log's steps), HP 250
# for the four (a test edit, never saved), the dice log (ravdice.py --numbers) into $WORK/sm-TAG.txt; stops at
# the ambush's first turn. The rest by hand (the test log).
PT=$(cd "$(dirname "$0")/../.." && pwd); cd $PT; export DISPLAY=:55 PLAYTEST_WORK=/tmp/playtest
W0=/tmp/playtest; TAG=$1; SKIP=$2; OFF=$3; F=$W0/ravSM  # (the loop below sets $1-$3 anew)
rm -rf $F; cp -a $W0/ravK $F
RAV_SKIP=$SKIP RAV_LOADER=1 RAV_MENU=1 RAV_STDOUT=1 timeout 200 sh ravstart.sh $F > $W0/sm-$TAG.start 2>&1
W=$(xdotool search --pid "$(cat $W0/rav.pid)" | tail -1); echo $W > $W0/smw
c(){ timeout 30 python3 ravclick.py "$@" >/dev/null; }
c 160 92; sleep 1; c 160 92; sleep 3; c 70 56 right; sleep 1.5; c 115 69; sleep 2; c 130 78; sleep 1; c 252 47; sleep 3
c 75 171; sleep 2; c 121 171; sleep 2; c 170 186; sleep 2
for s in "120 56" "70 115" "120 115"; do set -- $s; c $1 $2 right; sleep 1.5; c $(($1+45)) $(($2+13)); sleep 2; c 130 45; sleep 1; c 252 47; sleep 3; done
xdotool key --window $W Escape; sleep 3; xdotool key --window $W s; sleep 90; c 100 171; sleep 4
for m in 0 1 2 3; do timeout 30 python3 ravkits.py hp $m 250 >> $W0/sm-$TAG.kits 2>&1; done
timeout 30 python3 ravkits.py show >> $W0/sm-$TAG.kits 2>&1
: > $W0/sm-$TAG.txt
RAV_CHARGES_OFF=$OFF setsid nohup timeout 1700 python3 ravdice.py --numbers 1700 $W0/sm-$TAG.txt > $W0/sm-$TAG.out 2>&1 &
echo $! > $W0/sm-$TAG.dpid
sleep 8
for i in 1 2 3; do c 100 171; sleep 4; done
import -window $W $W0/sm-$TAG-fight.png
echo "$TAG ready"
