#!/bin/sh
# 2026-11-26-ravager-poison-arrows-run.sh TAG RULES_OFF FINE [UNHAND [BOW15]]: the ravPZ copy (the transferred fountain-user party) with the Loader, the four
# ADDed, a new game; test edits in memory (never saved): Seneca (member 1) a halfling fighter/thief Poisoner,
# Lex (0, a Spellarcher) at preserver level 5, HP 250 for all; FINE=1 Lex's bow named the Fine Bow; the dice
# log (RAV_RULES_OFF); UNHAND=1 Lex's right hand's weapon put in the pack; BOW15=1 Lex's bow +15 so he shoots (Computer Control closes in otherwise); CC on, the Draxans' ambush watched; DSCLOG2's counters every 10 s.
PT=$(dirname "$0")/../..; cd $PT; export DISPLAY=:55 PLAYTEST_WORK=/tmp/playtest
W0=/tmp/playtest; TAG=$1; OFF=$2; FINE=$3; UNHAND=$4; BOW15=$5
pgrep -x dosbox >/dev/null && { echo "a dosbox is running: not mine, stopping"; exit 1; }
RAV_LOADER=1 RAV_MENU=1 RAV_STDOUT=1 timeout 200 sh ravstart.sh $W0/ravPZ > $W0/pz-$TAG.start 2>&1
W=$(xdotool search --pid "$(cat $W0/rav.pid)" | tail -1); echo $W > $W0/pzw
c(){ timeout 30 python3 ravclick.py "$@" >/dev/null; }
c 160 92; sleep 1; c 160 92; sleep 3; c 70 56 right; sleep 1.5; c 115 69; sleep 2; c 130 78; sleep 1; c 252 47; sleep 3
c 75 171; sleep 2; c 121 171; sleep 2; c 170 186; sleep 2
for s in "120 56" "70 115" "120 115"; do set -- $s; c $1 $2 right; sleep 1.5; c $(($1+45)) $(($2+13)); sleep 2; c 130 45; sleep 1; c 252 47; sleep 3; done
xdotool key --window $W Escape; sleep 3; xdotool key --window $W s; sleep 90; c 100 171; sleep 4
import -window $W $W0/pz-$TAG-go.png
K=$W0/pz-$TAG.kits
timeout 30 python3 ravkits.py show > $K 2>&1
timeout 30 python3 ravkits.py set 1 1 6 9 17 >> $K 2>&1
timeout 30 python3 ravkits.py levels 1 3 3 >> $K 2>&1
timeout 30 python3 ravkits.py levels 0 5 5 >> $K 2>&1
for m in 0 1 2 3; do timeout 30 python3 ravkits.py hp $m 250 >> $K 2>&1; done
timeout 30 python3 ravkits.py show >> $K 2>&1
: > $W0/pz-$TAG.txt
RAV_RULES_OFF=$OFF setsid nohup timeout 400 python3 ravdice.py --numbers 400 $W0/pz-$TAG.txt > $W0/pz-$TAG.out 2>&1 &
sleep 8
for i in 1 2 3; do c 100 171; sleep 4; done
[ "$FINE" = 1 ] && timeout 30 python3 ravitems.py 0 --fine >> $K 2>&1
[ "$UNHAND" = 1 ] && timeout 30 python3 ravitems.py 0 --unhand >> $K 2>&1
[ "$BOW15" = 1 ] && timeout 30 python3 ravitems.py 0 --bow15 >> $K 2>&1
timeout 30 python3 ravitems.py 0 1 >> $K 2>&1
c 24 20; sleep 3
for p in "47 52" "100 52" "47 112" "100 112"; do c $p; sleep 1.5; done
xdotool key --window $W Escape
for i in $(seq 1 32); do sleep 10; pgrep -x dosbox >/dev/null || { echo "$TAG DEAD after ${i}0 s"; break; }
  import -window $W $W0/pz-$TAG-last.png; timeout 30 python3 ravkits.py count > $W0/pz-$TAG.count 2>&1; done
timeout 30 python3 ravkits.py count >> $K 2>&1
cat $W0/pz-$TAG.count; echo "$TAG done"
