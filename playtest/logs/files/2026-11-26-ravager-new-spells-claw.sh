#!/bin/sh
# 2026-11-26-ravager-new-spells-claw.sh TAG [TURNS] (from playtest/, after -run.sh TAG with Ar'anda's USE screen up at
# level 1): Erdlu Claw (the list's first, 174,58) dropped on Thy'rokh's portrait (70,117); then his chatkcha and
# gythka moved from his hands to his pack in the game's own inventory (I, his portrait 25,117: hands 65,50 and
# 65,90 to the pack's 195,27 and 195,48; a slot edit in memory alone leaves him unable to attack: the game's
# barred sword), Escape; then TURNS (default 3) of his turns: ravfight.py attack (the others' turns ended).
export DISPLAY=:55 PLAYTEST_WORK=/tmp/playtest; W0=/tmp/playtest; TAG=$1
W=$(xdotool search --pid $(cat $W0/rav.pid) | tail -1)
c(){ timeout 20 python3 ravclick.py $1 $2 >/dev/null; sleep ${3:-1.5}; }
c 174 58; c 70 117 4
xdotool key --window $W i; sleep 3; c 25 117 2
c 65 50; c 195 27; c 65 90; c 195 48
import -window $W $W0/sp-$TAG-inv.png
xdotool key --window $W Escape; sleep 2
for i in $(seq 1 ${2:-3}); do timeout 200 python3 ravfight.py until 2 | tail -1; timeout 60 python3 ravfight.py attack; sleep 8; done
