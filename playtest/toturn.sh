#!/bin/sh
# toturn.sh N: the party's turns played until member N's (state.py's turn): Tab + Return for each
# member, and E when the same member's turn is still up after that (no Move left: its END menu,
# wherever the game puts it, waits; untilturn.sh keeps pressing Tab there); the foes' turns waited
# out, messages clicked away. "TURN N", "FIGHT OVER" or "NO TURN".
. "$(dirname "$0")/env.sh"; cd "$PT"
W=$(xdotool search $WINQ | head -1); last=""
for i in $(seq 1 80); do
  s=$(timeout 10 python3 state.py); f=$(echo "$s" | awk '{print $2}'); t=$(echo "$s" | awk '{print $4}')
  [ "$f" = 1 ] || { echo "FIGHT OVER"; exit 1; }
  [ "$t" = "$1" ] && { echo "TURN $1"; exit 0; }
  # (a line that comes up in a party turn, the arena's Announcer's: Tab and Return do nothing under it)
  if sh msgbox.sh; then sh boxclick.sh; sleep 2; continue; fi
  if [ "$t" -le 3 ] 2>/dev/null; then
    if [ "$t" = "$last" ]; then xdotool key --window $W e; last=""
    else xdotool key --window $W Tab; sleep 1; xdotool key --window $W Return; last=$t; fi
    sleep 5
  else last=""; sh msgbox.sh && sh boxclick.sh; sleep 2; fi
done; echo "NO TURN"; exit 1
