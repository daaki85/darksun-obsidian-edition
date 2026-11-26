#!/bin/sh
# ns-run.sh TAG RULES_OFF: the ravNS copy (the fountain-user party transferred with Seneca's spec made lotulis, Ester's
# two-handed sword, Lex's gythka in the SL save) started with the Loader, the four ADDed, a new game, the opening
# talk; test edits (never saved): HP 250 for the four, the right-hand weapons made the sequel's Lotulis (61) for
# Seneca and Lex and Twohand Sword (101) for Ester, the left hands' items to the pack; the dice log (RAV_RULES_OFF);
# Seneca's inventory, View Character and Effects grabbed; Computer Control for the four; 4 minutes of the fight;
# DSCLOG2's counters. Kills only its own DOSBox (its pid in $W0/ns-$TAG.dbpid) and dice log.
PT=/tmp/claude-0/-home-claude/64ea2217-da22-5669-9254-2672bfc4a609/scratchpad/kit/playtest; S=$(dirname "$0"); cd $PT; export DISPLAY=:57 PLAYTEST_WORK=/tmp/playtest/nswork PATH=/tmp/claude-0/-home-claude/64ea2217-da22-5669-9254-2672bfc4a609/scratchpad/bin:$PATH
W0=/tmp/playtest/nswork; TAG=$1; OFF=$2
RAV_LOADER=1 RAV_MENU=1 RAV_STDOUT=1 timeout 200 sh ravstart.sh /tmp/playtest/ravNS > $W0/ns-$TAG.start 2>&1
cp $W0/rav.pid $W0/ns-$TAG.dbpid
W=$(xdotool search --pid "$(cat $W0/rav.pid)" | tail -1); echo $W > $W0/ns-gw
c(){ timeout 30 python3 ravclick.py "$@" >/dev/null; }
c 160 92; sleep 1; c 160 92; sleep 3; c 70 56 right; sleep 1.5; c 115 69; sleep 2; c 130 45; sleep 1; c 252 47; sleep 3
c 75 171; sleep 2; c 121 171; sleep 2; c 170 186; sleep 2
for s in "120 56" "70 115" "120 115"; do set -- $s; c $1 $2 right; sleep 1.5; c $(($1+45)) $(($2+13)); sleep 2; c 130 45; sleep 1; c 252 47; sleep 3; done
import -window $W $W0/ns-$TAG-party.png
xdotool key --window $W Escape; sleep 3; xdotool key --window $W s; sleep 90; c 100 171; sleep 4
import -window $W $W0/ns-$TAG-go.png
K=$W0/ns-$TAG.kits
timeout 30 python3 ravkits.py show > $K 2>&1
for m in 0 1 2 3; do timeout 30 python3 ravkits.py hp $m 250 >> $K 2>&1; done
# (each member by its classes: Seneca thief/fighter 17,9; Ester fighter/cleric 9,3; Lex fighter/preserver 9,11)
for m in 0 1 2 3; do
  cls=$(sed -n "s/^$m race [0-9]* classes \[\([0-9]*\), \([0-9]*\), 0\].*/\1,\2/p" $K)
  case $cls in 17,9) T=61;; 9,3) T=101;; 9,11) T=61;; *) T=;; esac
  timeout 30 python3 $S/nsweapon.py $m $T --pack-left >> $K 2>&1
done
: > $W0/ns-$TAG.txt
RAV_RULES_OFF=$OFF setsid nohup timeout 600 python3 ravdice.py --numbers 600 $W0/ns-$TAG.txt > $W0/ns-$TAG.out 2>&1 &
echo $! > $W0/ns-$TAG.dpid
sleep 8
for i in 1 2 3; do c 100 171; sleep 4; done
import -window $W $W0/ns-$TAG-fight.png
echo "$TAG in the fight"
