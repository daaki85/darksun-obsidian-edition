#!/bin/sh
# PARTY="A|B|C|D" (the party's names, an extended regex) names whose turns are played; the others' turns are waited out
# untilturn.sh NAME: play party turns (Tab + Return) until NAME's turn comes, messages clicked away
PT0=$(cd "$(dirname "$0")" && pwd); . "$PT0/env.sh"; PT=$PT0
W=$(timeout 10 xdotool search $WINQ | head -1)
n=$(wc -l < $WORK/dice.txt); first=1
for i in $(seq 1 60); do
  last=$(grep "'s turn$" $WORK/dice.txt | tail -1)
  case "$last" in "$1's turn") [ -z "$first" ] && { echo "TURN $1"; exit 0; };; esac
  first=""
  if sh $PT/msgbox.sh; then sh $PT/boxclick.sh; sleep 2; continue; fi
  f=$(timeout 10 python3 $PT/state.py 2>/dev/null)
  case "$f" in "fight_on 0"*) echo "FIGHT OVER"; exit 1;; esac
  t=$(echo "$f" | sed 's/.*turn \([0-9]*\).*/\1/')
  if echo "$last" | grep -qE "^($PARTY)'s turn$"; then
     m=$(tail -n +$((n+1)) $WORK/dice.txt | wc -l)
     timeout 5 xdotool key --window $W Tab; sleep 1; timeout 5 xdotool key --window $W Return; sleep 5
     n2=$(tail -n +$((n+1)) $WORK/dice.txt | wc -l); [ "$n2" = "$m" ] && { timeout 5 xdotool key --window $W Tab; sleep 1; timeout 5 xdotool key --window $W Return; sleep 4; }
     continue
  fi
  case x in
  *) sleep 3;; esac
done
echo "NO TURN"; exit 1
