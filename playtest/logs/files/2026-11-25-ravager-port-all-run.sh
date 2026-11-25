#!/bin/sh
# 2026-11-25-ravager-port-all-run.sh TAG [MINUTES]: the integration branch's smoke run (the kits run's steps): a copy ravPA of
# ravK (the transferred party) with the Loader and every ported rule on, the four ADDed, a new game, HP 250 for
# the four (a test edit, never saved), the dice log, Computer Control for all four in the Draxans' ambush,
# watched up to MINUTES (default 10) with DSCLOG2's counters and DOS memory; STDOUT.TXT shown at the end.
PT=$(cd "$(dirname "$0")/../.." && pwd); cd $PT; export DISPLAY=:55 PLAYTEST_WORK=/tmp/playtest
W0=/tmp/playtest; TAG=$1; MIN=${2:-10}; F=$W0/ravPA
RAV_LOADER=1 RAV_MENU=1 RAV_STDOUT=1 timeout 200 sh ravstart.sh $F > $W0/pa-$TAG.start 2>&1
W=$(xdotool search --pid "$(cat $W0/rav.pid)" | tail -1); echo $W > $W0/kgw
xdotool getwindowgeometry $W > $W0/pa-$TAG.geom
c(){ timeout 30 python3 ravclick.py "$@" >/dev/null; }
c 160 92; sleep 1; c 160 92; sleep 3; c 70 56 right; sleep 1.5; c 115 69; sleep 2; c 130 78; sleep 1; c 252 47; sleep 3
c 75 171; sleep 2; c 121 171; sleep 2; c 170 186; sleep 2
for s in "120 56" "70 115" "120 115"; do set -- $s; c $1 $2 right; sleep 1.5; c $(($1+45)) $(($2+13)); sleep 2; c 130 45; sleep 1; c 252 47; sleep 3; done
xdotool key --window $W Escape; sleep 3; xdotool key --window $W s; sleep 90; c 100 171; sleep 4
import -window $W $W0/pa-$TAG-go.png
timeout 30 python3 ravkits.py show > $W0/pa-$TAG.kits 2>&1
for m in 0 1 2 3; do timeout 30 python3 ravkits.py hp $m 250 >> $W0/pa-$TAG.kits 2>&1; done
: > $W0/pa-$TAG.txt
setsid nohup timeout $((MIN*60+60)) python3 ravdice.py --numbers $((MIN*60+60)) $W0/pa-$TAG.txt > $W0/pa-$TAG.out 2>&1 &
echo $! > $W0/pa-$TAG.dpid
sleep 8
for i in 1 2 3; do c 100 171; sleep 4; done
c 24 20; sleep 3
for p in "47 52" "100 52" "47 112" "100 112"; do c $p; sleep 1.5; done
xdotool key --window $W Escape
timeout 30 python3 dosmem.py > $W0/pa-$TAG.mem 2>&1
last=0; still=0
for i in $(seq 1 $((MIN*6))); do sleep 10; pgrep -x dosbox >/dev/null || { echo "$TAG DOSBOX GONE after ${i}0 s"; break; }
  import -window $W $W0/pa-$TAG-last.png; timeout 30 python3 ravkits.py count > $W0/pa-$TAG.count 2>&1
  n=$(wc -l < $W0/pa-$TAG.txt); if [ "$n" = "$last" ]; then still=$((still+1)); else still=0; fi; last=$n
  [ $still -ge 6 ] && { echo "$TAG dice log still 60 s after ${i}0 s"; break; }; done
cat $W0/pa-$TAG.count; echo "STDOUT.TXT:"; cat $F/STDOUT.TXT 2>/dev/null; ls -l $F/STDOUT.TXT
echo "$TAG done"
