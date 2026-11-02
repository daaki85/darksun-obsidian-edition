#!/bin/sh
# dismiss.sh [N]: click away up to N (default 6) waiting messages (msgbox.sh), then print the dice
# log's last lines. A YES/NO question stays (the log shows "(Answer Yes or No)"): answer with keys.
. "$(dirname "$0")/env.sh"
for i in $(seq 1 ${1:-6}); do
  sh "$PT/msgbox.sh" || break
  [ "$(tail -1 "$WORK/dice.txt")" = "    2. No" ] && { echo "YES/NO QUESTION: press N or Y"; break; }
  sh "$PT/boxclick.sh"; sleep 2
done; tail -3 "$WORK/dice.txt"
