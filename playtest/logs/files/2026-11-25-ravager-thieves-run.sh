#!/bin/sh
# 2026-11-25-ravager-thieves-run.sh TAG RULES_OFF [EDIT]: the start script's steps, EDIT ("MEMBER BYTE RACE [CLASSES]" for ravkits.py set, a
# test edit never saved), HP 250 for the four, the dice log (RAV_RULES_OFF, every hiding roll 1), the opening
# talk's last Continues, Seneca's inventory grabbed, Computer Control for the four (C, the USE screen's lower
# small icons), then up to 6 minutes until a backstab's damage line; DSCLOG2's counters at the end.
S=$(dirname "$0"); PT=$(cd "$(dirname "$0")/../.." && pwd); export DISPLAY=:55 PLAYTEST_WORK=/tmp/playtest
W0=/tmp/playtest; TAG=$1; OFF=$2; EDIT=$3
sh $S/2026-11-25-ravager-thieves-start.sh $TAG; cd $PT; W=$(cat $W0/kgw)
c(){ timeout 30 python3 ravclick.py "$@" >/dev/null; }
[ -n "$EDIT" ] && timeout 30 python3 ravkits.py set $EDIT >> $W0/t-$TAG.kits 2>&1
for m in 0 1 2 3; do timeout 30 python3 ravkits.py hp $m 250 >> $W0/t-$TAG.kits 2>&1; done
timeout 30 python3 ravkits.py show >> $W0/t-$TAG.kits 2>&1
: > $W0/t-$TAG.txt
RAV_STEALTH_ROLL=1 RAV_RULES_OFF=$OFF setsid nohup timeout 600 python3 ravdice.py --numbers 600 $W0/t-$TAG.txt > $W0/t-$TAG.out 2>&1 &
echo $! > $W0/t-$TAG.dpid
sleep 8
for i in 1 2 3; do c 100 171; sleep 4; done
c 22 17; sleep 2; c 74 171; sleep 3; c 25 69; sleep 3; import -window $W $W0/t-$TAG-inv.png
xdotool key --window $W Escape; sleep 3
xdotool key --window $W c; sleep 3
for p in "47 53" "98 53" "47 112" "98 112"; do c $p; sleep 1.5; done
import -window $W $W0/t-$TAG-cc.png
xdotool key --window $W Escape
for i in $(seq 1 72); do sleep 5; pgrep -x dosbox >/dev/null || { echo "$TAG DEAD"; break; }
  grep -q "backstab (the dice\|x[0-9] backstab" $W0/t-$TAG.txt && { sleep 12; break; }; done
import -window $W $W0/t-$TAG-last.png
timeout 30 python3 ravkits.py count >> $W0/t-$TAG.kits 2>&1
echo "$TAG done"
grep -q "backstab (the dice\|x[0-9] backstab" $W0/t-$TAG.txt && echo "$TAG backstab seen" || echo "$TAG no backstab"
D=$(cat $W0/t-$TAG.dpid); kill $D 2>/dev/null; pkill -P $D 2>/dev/null
P=$(cat $W0/rav.pid); [ "$(cat /proc/$P/comm 2>/dev/null)" = dosbox ] && kill $P
