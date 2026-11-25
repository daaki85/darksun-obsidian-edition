#!/bin/sh
# 2026-11-25-ravager-save-mods-tabfight.sh SECONDS: the party's turns by Tab and Enter (attack the enemy Tab chose), the
# turn ended (Q, E) if still ours after; until the dice log ($WORK/sv-$TAG.txt) says the fight is over or SECONDS pass. The window id in $WORK/svw.
cd "$(dirname "$0")/../.."; export PLAYTEST_WORK=/tmp/playtest DISPLAY=:55
W=$(cat /tmp/playtest/svw); END=$(( $(date +%s) + ${1:-600} ))
while [ $(date +%s) -lt $END ]; do
  t=$(timeout 20 python3 ravfight.py state | awk '{print $2}')
  if [ -z "$t" ]; then echo "no fight"; break; fi
  if [ "$t" -lt 4 ]; then
    xdotool key --window $W Tab; sleep 1.5; xdotool key --window $W Return; sleep 7
    t2=$(timeout 20 python3 ravfight.py state | awk '{print $2}')
    [ "$t2" = "$t" ] && { xdotool key --window $W q; sleep 1.5; xdotool key --window $W e; sleep 3; }
    echo "turn $t done"
  else sleep 2; fi
  grep -q "Fight over" /tmp/playtest/sv-${TAG:-A}.txt && { echo "fight over"; break; }
done
