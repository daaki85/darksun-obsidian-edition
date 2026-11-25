#!/bin/sh
# TAG RULES_OFF SPHERE: the ravK copy (the transferred party) with the Loader, the four ADDed, a new game, the
# opening talk; Ester (fighter/cleric) made a single-class Elementalist cleric 5 by test edits in memory
# (ravkits.py: classes, levels, kit byte 01h, second sphere SPHERE, 1-4, or auto: earth, fire for an earth cleric), HP 250 for the four, the dice log
# (RAV_RULES_OFF), then the talk on into the Draxans' ambush; the rest by hand (USE, CLERIC, the levels).
# Never saved after. As 2026-11-25-ravager-kits-run.sh, without killing any DOSBox it didn't start.
PT=$(dirname "$0")/../..; cd $PT; export DISPLAY=:55 PLAYTEST_WORK=/tmp/playtest
W0=/tmp/playtest; TAG=$1; OFF=$2; SPH=$3
RAV_LOADER=1 RAV_MENU=1 RAV_STDOUT=1 timeout 200 sh ravstart.sh $W0/ravK > $W0/s-$TAG.start 2>&1
W=$(xdotool search --pid "$(cat $W0/rav.pid)" | tail -1); echo $W > $W0/sgw
c(){ timeout 30 python3 ravclick.py "$@" >/dev/null; }
c 160 92; sleep 1; c 160 92; sleep 3; c 70 56 right; sleep 1.5; c 115 69; sleep 2; c 130 78; sleep 1; c 252 47; sleep 3
c 75 171; sleep 2; c 121 171; sleep 2; c 170 186; sleep 2
for s in "120 56" "70 115" "120 115"; do set -- $s; c $1 $2 right; sleep 1.5; c $(($1+45)) $(($2+13)); sleep 2; c 130 45; sleep 1; c 252 47; sleep 3; done
xdotool key --window $W Escape; sleep 3; xdotool key --window $W s; sleep 90; c 100 171; sleep 4
timeout 30 python3 ravkits.py show > $W0/s-$TAG.kits 2>&1
M=$(timeout 30 python3 ravkits.py match 9,c 0x01 2>/dev/null | sed -n 's/^member \([0-9]\).*/\1/p')
C=$(sed -n "$((M+1))p" $W0/s-$TAG.kits | sed 's/.*classes \[\([0-9]*\), \([0-9]*\).*/\1 \2/' | tr ' ' '\n' | awk '$1>=1&&$1<=4' | head -1)
[ "$SPH" = auto ] && { SPH=2; [ "$C" = 2 ] && SPH=3; }  # (earth, else fire: not her own)
echo "Ester member $M cleric class $C second sphere $SPH" >> $W0/s-$TAG.kits
timeout 30 python3 ravkits.py set $M 0x01 - $C >> $W0/s-$TAG.kits 2>&1
timeout 30 python3 ravkits.py levels $M 5 >> $W0/s-$TAG.kits 2>&1
timeout 30 python3 ravkits.py sphere $M $SPH >> $W0/s-$TAG.kits 2>&1
for m in 0 1 2 3; do timeout 30 python3 ravkits.py hp $m 250 >> $W0/s-$TAG.kits 2>&1; done
timeout 30 python3 ravkits.py show >> $W0/s-$TAG.kits 2>&1
: > $W0/s-$TAG.txt
RAV_RULES_OFF=$OFF setsid nohup timeout 1500 python3 ravdice.py --numbers 1500 $W0/s-$TAG.txt > $W0/s-$TAG.out 2>&1 &
sleep 8
for i in 1 2 3; do c 100 171; sleep 4; done
import -window $W $W0/s-$TAG-fight.png
timeout 30 python3 ravkits.py count >> $W0/s-$TAG.kits 2>&1
cat $W0/s-$TAG.kits; echo "$TAG ready"
