#!/bin/sh
# krun2.sh (the merged build's worktree; the edits kept past the click loops' set --) TAG RULES_OFF EDITS...: the ravK copy (the transferred party) with the Loader, the four ADDed, a new
# game, kits given by memory edit (EDITS: "MEMBER BYTE RACE [CLASSES]" strings for ravkits.py set), HP 250,
# the dice log (RAV_RULES_OFF), CC on, the Draxans' ambush watched 4 minutes; DSCLOG2's kit counters at the end.
PT=$(dirname "$0")/../..; cd $PT; export DISPLAY=:55 PLAYTEST_WORK=/tmp/playtest
W0=/tmp/playtest; TAG=$1; OFF=$2; shift 2
n=0; for e in "$@"; do n=$((n+1)); eval "E$n=\"\$e\""; done; NE=$n
P=$(cat $W0/rav.pid 2>/dev/null); [ -n "$P" ] && [ "$(cat /proc/$P/comm 2>/dev/null)" = dosbox ] && kill $P; sleep 2
RAV_LOADER=1 RAV_MENU=1 RAV_STDOUT=1 timeout 200 sh ravstart.sh $W0/ravK > $W0/k-$TAG.start 2>&1
W=$(xdotool search --pid "$(cat $W0/rav.pid)" | tail -1); echo $W > $W0/kgw
c(){ timeout 30 python3 ravclick.py "$@" >/dev/null; }
c 160 92; sleep 1; c 160 92; sleep 3; c 70 56 right; sleep 1.5; c 115 69; sleep 2; c 130 78; sleep 1; c 252 47; sleep 3
c 75 171; sleep 2; c 121 171; sleep 2; c 170 186; sleep 2
for s in "120 56" "70 115" "120 115"; do set -- $s; c $1 $2 right; sleep 1.5; c $(($1+45)) $(($2+13)); sleep 2; c 130 45; sleep 1; c 252 47; sleep 3; done
xdotool key --window $W Escape; sleep 3; xdotool key --window $W s; sleep 90; c 100 171; sleep 4
import -window $W $W0/k-$TAG-go.png
timeout 30 python3 ravkits.py show > $W0/k-$TAG.kits 2>&1
i=1; while [ $i -le $NE ]; do eval "e=\$E$i"; timeout 30 python3 ravkits.py match $e >> $W0/k-$TAG.kits 2>&1; i=$((i+1)); done
for m in 0 1 2 3; do timeout 30 python3 ravkits.py hp $m 250 >> $W0/k-$TAG.kits 2>&1; done
timeout 30 python3 ravkits.py show >> $W0/k-$TAG.kits 2>&1
: > $W0/k-$TAG.txt
RAV_RULES_OFF=$OFF setsid nohup timeout 330 python3 ravdice.py --numbers 330 $W0/k-$TAG.txt > $W0/k-$TAG.out 2>&1 &
sleep 8
for i in 1 2 3; do c 100 171; sleep 4; done
c 24 20; sleep 3
for p in "47 52" "100 52" "47 112" "100 112"; do c $p; sleep 1.5; done
xdotool key --window $W Escape
for i in $(seq 1 30); do sleep 10; pgrep -x dosbox >/dev/null || { echo "$TAG DEAD after ${i}0 s"; break; }
  import -window $W $W0/k-$TAG-last.png; timeout 30 python3 ravkits.py count > $W0/k-$TAG.count 2>&1; done
timeout 30 python3 ravkits.py count >> $W0/k-$TAG.kits 2>&1
cat $W0/k-$TAG.count; echo "$TAG done"
