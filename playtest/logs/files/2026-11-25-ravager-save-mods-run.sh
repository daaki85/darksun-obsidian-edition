#!/bin/sh
# 2026-11-25-ravager-save-mods-run.sh TAG [BASE] (run from anywhere, under the DOSBox lock): ravSV, a fresh copy of
# $WORK/ravK (the fountain-user party transferred), started as the Loader starts it, the four ADDed, a new game, the
# opening talk into the Draxans' ambush (the blast log's steps), HP 250 for the four (a test edit, never saved), and
# two dice logs on the same game: this branch's (ravdice.py --numbers into $WORK/sv-TAG.txt) and, with BASE (a
# checkout of the commit before, `git worktree add --detach BASE HEAD~N`), the old one's (into $WORK/sv-TAG-old.txt):
# the same rolls, the control. Quick saves and autosave held off in both (a sitecustomize.py on PYTHONPATH,
# $NOQUICK: QuickSave.keys and .auto False). Stops at the ambush's first turn; the rest by hand (the test log).
PT=$(cd "$(dirname "$0")/../.." && pwd); cd $PT; export DISPLAY=:55 PLAYTEST_WORK=/tmp/playtest
W0=/tmp/playtest; TAG=$1; BASE=$2; F=$W0/ravSV; NQ=${NOQUICK:-/tmp/claude-0/sm/noquick}
rm -rf $F; cp -a $W0/ravK $F
RAV_LOADER=1 RAV_MENU=1 RAV_STDOUT=1 timeout 200 sh ravstart.sh $F > $W0/sv-$TAG.start 2>&1
W=$(xdotool search --pid "$(cat $W0/rav.pid)" | tail -1); echo $W > $W0/svw
c(){ timeout 30 python3 ravclick.py "$@" >/dev/null; }
c 160 92; sleep 1; c 160 92; sleep 3; c 70 56 right; sleep 1.5; c 115 69; sleep 2; c 130 78; sleep 1; c 252 47; sleep 3
c 75 171; sleep 2; c 121 171; sleep 2; c 170 186; sleep 2
for s in "120 56" "70 115" "120 115"; do set -- $s; c $1 $2 right; sleep 1.5; c $(($1+45)) $(($2+13)); sleep 2; c 130 45; sleep 1; c 252 47; sleep 3; done
xdotool key --window $W Escape; sleep 3; xdotool key --window $W s; sleep 90; c 100 171; sleep 4
for m in 0 1 2 3; do timeout 30 python3 ravkits.py hp $m 250 >> $W0/sv-$TAG.kits 2>&1; done
timeout 30 python3 ravkits.py show >> $W0/sv-$TAG.kits 2>&1
: > $W0/sv-$TAG.txt
PYTHONPATH=$NQ:$PT/../obsidian-edition setsid nohup timeout 3000 python3 ravdice.py --numbers 3000 $W0/sv-$TAG.txt > $W0/sv-$TAG.out 2>&1 &
echo $! > $W0/sv-$TAG.dpid
if [ -n "$BASE" ]; then
  cp -n $PT/../obsidian-edition/dos/* $BASE/obsidian-edition/dos/ 2>/dev/null  # (the Loader's copies: RESOURC2.GFF...)
  : > $W0/sv-$TAG-old.txt
  (cd $BASE/playtest && PYTHONPATH=$NQ:$BASE/obsidian-edition setsid nohup timeout 3000 python3 ravdice.py --numbers 3000 $W0/sv-$TAG-old.txt > $W0/sv-$TAG-old.out 2>&1 &
   echo $! > $W0/sv-$TAG-old.dpid)
fi
sleep 8
for i in 1 2 3; do c 100 171; sleep 4; done
timeout 20 import -window $W $W0/sv-$TAG-fight.png
echo "$TAG ready"
