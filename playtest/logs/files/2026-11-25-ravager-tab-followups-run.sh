#!/bin/sh
# 2026-11-25-ravager-tab-followups-run.sh TAG [OFF] (run from playtest/): ravTF (a fresh copy of ravK), the Loader's start, the four ADDed, a new game, HP 250 (test edit, never saved), the dice log; stops at the ambush's first turn
PT=/home/claude/wt-tabfix/playtest; cd $PT; export DISPLAY=:55 PLAYTEST_WORK=/tmp/playtest
W0=/tmp/playtest; TAG=$1; OFF=$2; F=$W0/ravTF
rm -rf $F; cp -a $W0/ravK $F
RAV_LOADER=1 RAV_MENU=1 RAV_STDOUT=1 timeout 200 sh ravstart.sh $F > $W0/tf-$TAG.start 2>&1
W=$(xdotool search --pid "$(cat $W0/rav.pid)" | tail -1); echo $W > $W0/tfw
c(){ timeout 30 python3 ravclick.py "$@" >/dev/null; }
c 160 92; sleep 1; c 160 92; sleep 3; c 70 56 right; sleep 1.5; c 115 69; sleep 2; c 130 78; sleep 1; c 252 47; sleep 3
c 75 171; sleep 2; c 121 171; sleep 2; c 170 186; sleep 2
for s in "120 56" "70 115" "120 115"; do set -- $s; c $1 $2 right; sleep 1.5; c $(($1+45)) $(($2+13)); sleep 2; c 130 45; sleep 1; c 252 47; sleep 3; done
xdotool key --window $W Escape; sleep 3; xdotool key --window $W s; sleep 90; c 100 171; sleep 4
import -window $W $W0/tf-$TAG-go.png
for m in 0 1 2 3; do timeout 30 python3 ravkits.py hp $m 250 >> $W0/tf-$TAG.kits 2>&1; done
: > $W0/tf-$TAG.txt
[ -n "$OFF" ] && export RAV_TAB_OFF=1
export RAV_PREDICT=1   # (each Tab line's chance taken apart: ravdice.py)
setsid nohup timeout 1500 python3 ravdice.py --numbers 1500 $W0/tf-$TAG.txt > $W0/tf-$TAG.out 2>&1 &
echo $! > $W0/tf-$TAG.dpid
sleep 8
for i in 1 2 3; do c 100 171; sleep 4; done
import -window $W $W0/tf-$TAG-fight.png
echo "$TAG ready"
