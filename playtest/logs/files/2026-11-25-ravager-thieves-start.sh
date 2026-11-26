#!/bin/sh
# 2026-11-25-ravager-thieves-start.sh TAG: the ravK copy (the transferred party) with the Loader, the four ADDed, a new game, the
# opening talk up to its last Continue (the kits run's steps); the window id in $W0/kgw
PT=$(cd "$(dirname "$0")/../.." && pwd); cd $PT; export DISPLAY=:55 PLAYTEST_WORK=/tmp/playtest
W0=/tmp/playtest; TAG=$1
P=$(cat $W0/rav.pid 2>/dev/null); [ -n "$P" ] && [ "$(cat /proc/$P/comm 2>/dev/null)" = dosbox ] && kill $P; sleep 2
RAV_LOADER=1 RAV_MENU=1 RAV_STDOUT=1 timeout 200 sh ravstart.sh $W0/ravK > $W0/t-$TAG.start 2>&1
W=$(xdotool search --pid "$(cat $W0/rav.pid)" | tail -1); echo $W > $W0/kgw
c(){ timeout 30 python3 ravclick.py "$@" >/dev/null; }
c 160 92; sleep 1; c 160 92; sleep 3; c 70 56 right; sleep 1.5; c 115 69; sleep 2; c 130 78; sleep 1; c 252 47; sleep 3
c 75 171; sleep 2; c 121 171; sleep 2; c 170 186; sleep 2
for s in "120 56" "70 115" "120 115"; do set -- $s; c $1 $2 right; sleep 1.5; c $(($1+45)) $(($2+13)); sleep 2; c 130 45; sleep 1; c 252 47; sleep 3; done
xdotool key --window $W Escape; sleep 3; xdotool key --window $W s; sleep 90; c 100 171; sleep 4
import -window $W $W0/t-$TAG-go.png
timeout 30 python3 ravkits.py show > $W0/t-$TAG.kits 2>&1
echo "$TAG started"
