#!/bin/sh
# 2026-11-26-ravager-new-spells-create.sh TAG (from playtest/): ravSP (a fresh copy of rav) started as the Loader starts
# it to the title menu (RAV_LOADER=1 RAV_MENU=1; RAV_SKIP passes on: a control), CREATE CHARACTERS (160,92), the
# roster's first slot right-clicked (70,56), NEW (110,57), the dice log attached (ravcreation.py 0: no rolls, the
# ported rules written), FIGHTER off (255,29), PRESERVER on (265,45), DONE (279,183): CHOOSE A SPELL up
# ($WORK/sp-TAG-create.png). The roster is ravSP's own; nothing saved by hand.
PT=$(cd "$(dirname "$0")/../.." && pwd); cd $PT; export DISPLAY=:55 PLAYTEST_WORK=/tmp/playtest
W0=/tmp/playtest; TAG=$1; F=$W0/ravSP
rm -rf $F; cp -a $W0/rav $F
RAV_LOADER=1 RAV_MENU=1 timeout 200 sh ravstart.sh $F > $W0/sp-$TAG.start 2>&1 || { cat $W0/sp-$TAG.start; exit 1; }
W=$(xdotool search --pid "$(cat $W0/rav.pid)" | tail -1)
xdotool mousemove --window "$W" 400 200; sleep 0.3; xdotool click --window "$W" 1; sleep 1
python3 ravclick.py 160 92 >/dev/null; sleep 4
python3 ravclick.py 70 56 right >/dev/null; sleep 2
python3 ravclick.py 110 57 >/dev/null; sleep 4
timeout 60 python3 ravcreation.py 0 | tail -1
python3 ravclick.py 255 29 >/dev/null; sleep 1.5
python3 ravclick.py 265 45 >/dev/null; sleep 1.5
import -window "$W" $W0/sp-$TAG-preserver.png
python3 ravclick.py 279 183 >/dev/null; sleep 4
import -window "$W" $W0/sp-$TAG-create.png
echo "$TAG create up"
