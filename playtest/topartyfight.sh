#!/bin/sh
# topartyfight.sh: a fresh DOSBox at its title: START GAME, through the opening show fight, the party
# gathered (6), the panel hidden (L), stepped forward until the arena fight is on; the panel shown again
. "$(dirname "$0")/env.sh"
W=$(timeout 10 xdotool search --class dosbox | head -1)
timeout 5 xdotool windowmove $W 0 0; timeout 5 xdotool mousemove 160 120; sleep 0.3
timeout 5 xdotool click 1; sleep 1; timeout 5 xdotool click 1; sleep 14
timeout 5 xdotool key --window $W s; sleep 6
for i in $(seq 1 60); do
  grep -q "Step forward" $WORK/dice.txt && break
  timeout 5 xdotool mousedown 1; sleep 0.1; timeout 5 xdotool mouseup 1; sleep 3
done
grep -q "Step forward" $WORK/dice.txt || { echo "NO STEP FORWARD"; exit 1; }
sh $PT/msgbox.sh && { timeout 5 xdotool mousedown 1; sleep 0.1; timeout 5 xdotool mouseup 1; sleep 2; }
for k in 1 2 3; do sh $PT/msgbox.sh && { timeout 5 xdotool mousedown 1; sleep 0.1; timeout 5 xdotool mouseup 1; sleep 2; }; done
timeout 5 xdotool key --window $W 6; sleep 1; timeout 5 xdotool key --window $W l; sleep 1
for i in $(seq 1 30); do
  f=$(timeout 10 python3 $PT/state.py 2>/dev/null)
  case "$f" in *"fight_on 1"*) echo "FIGHT: $f"; timeout 5 xdotool key --window $W l; exit 0;; esac
  if sh $PT/msgbox.sh; then timeout 5 xdotool mousedown 1; sleep 0.1; timeout 5 xdotool mouseup 1; sleep 2
  else timeout 15 python3 $PT/click.py 160 165 >/dev/null; sleep 5; fi
done
echo "NO FIGHT: $f"; exit 1
