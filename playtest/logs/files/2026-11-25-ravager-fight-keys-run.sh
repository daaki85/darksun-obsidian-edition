#!/bin/sh
# 2026-11-25-ravager-fight-keys-run.sh TAG [DICE_ENV...] (run from playtest/): ravFK (a fresh copy of ravK), the Loader's start, the four ADDed, a new game, HP 250 (a test edit, never saved: RAV_NO_SAVES), the dice log (ravdice.py --numbers, with the env words given, as RAV_NO_SQUARES=1); stops at the Draxans' ambush's first turn. RAV_SKIP passes through to ravstart.sh (a control's copy).
PT=/home/claude/wt-ravager-fight-keys/playtest; cd $PT; export DISPLAY=:55 PLAYTEST_WORK=/tmp/playtest
W0=/tmp/playtest; TAG=$1; shift; DICE_ENV="$*"; F=$W0/ravFK
rm -rf $F; cp -a $W0/ravK $F
RAV_LOADER=1 RAV_MENU=1 RAV_STDOUT=1 timeout 200 sh ravstart.sh $F > $W0/fk-$TAG.start 2>&1
W=$(xdotool search --pid "$(cat $W0/rav.pid)" | tail -1); echo $W > $W0/fkw
c(){ timeout 30 python3 ravclick.py "$@" >/dev/null; }
c 160 92; sleep 1; c 160 92; sleep 3; c 70 56 right; sleep 1.5; c 115 69; sleep 2; c 130 78; sleep 1; c 252 47; sleep 3
c 75 171; sleep 2; c 121 171; sleep 2; c 170 186; sleep 2
for s in "120 56" "70 115" "120 115"; do set -- $s; c $1 $2 right; sleep 1.5; c $(($1+45)) $(($2+13)); sleep 2; c 130 45; sleep 1; c 252 47; sleep 3; done
xdotool key --window $W Escape; sleep 3; xdotool key --window $W s; sleep 90; c 100 171; sleep 4
import -window $W $W0/fk-$TAG-go.png
for m in 0 1 2 3; do timeout 30 python3 ravkits.py hp $m 250 >> $W0/fk-$TAG.kits 2>&1; done
: > $W0/fk-$TAG.txt
setsid nohup env RAV_NO_SAVES=1 $DICE_ENV timeout 2400 python3 ravdice.py --numbers 2400 $W0/fk-$TAG.txt > $W0/fk-$TAG.out 2>&1 &
echo $! > $W0/fk-$TAG.dpid
sleep 8
for i in 1 2 3; do c 100 171; sleep 4; done
import -window $W $W0/fk-$TAG-fight.png
echo "$TAG ready"
