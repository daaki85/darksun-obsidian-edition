#!/bin/sh
# dismiss.sh [N]: click away up to N (default 6) waiting messages (msgbox.sh), then print the dice
# log's last lines. A YES/NO question stays (the log shows "(Answer Yes or No)"): answer with keys.
. "$(dirname "$0")/env.sh"
for i in $(seq 1 ${1:-6}); do
  sh "$PT/msgbox.sh" || break
  grep -q "Answer Yes or No" "$WORK/dice.txt" && tail -3 "$WORK/dice.txt" | grep -q "2. No" && { echo "YES/NO QUESTION: press N or Y"; break; }
  timeout 5 xdotool mousedown 1; sleep 0.1; timeout 5 xdotool mouseup 1; sleep 2
done; tail -3 "$WORK/dice.txt"
