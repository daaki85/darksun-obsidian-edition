#!/bin/sh
# 2026-11-25-ravager-blast-log-tabfight.sh SECONDS (TAG in the environment): a fight by Tab and Enter, each party turn; stops when the dice log ($WORK/bl-$TAG.txt) gives back a blast
# each party turn: Tab, Enter (attack the chosen enemy); the turn ended if still ours after; until the fight flag drops or N s
cd "$(dirname "$0")/../.."; W0=1; export PLAYTEST_WORK=/tmp/playtest DISPLAY=:55
W=$(cat /tmp/playtest/blw); END=$(( $(date +%s) + ${1:-900} ))
while [ $(date +%s) -lt $END ]; do
  t=$(timeout 20 python3 ravfight.py state | awk '{print $2}')
  if [ -z "$t" ]; then sleep 2; continue; fi
  if [ "$t" -lt 4 ]; then
    xdotool key --window $W Tab; sleep 1.5; xdotool key --window $W Return; sleep 7
    t2=$(timeout 20 python3 ravfight.py state | awk '{print $2}')
    [ "$t2" = "$t" ] && { xdotool key --window $W q; sleep 1.5; xdotool key --window $W e; sleep 3; }
    echo "turn $t done"
  else sleep 2; fi
  grep -q "shakes off\|lost to Psionic" /tmp/playtest/bl-$TAG.txt && { echo given; break; }
done
