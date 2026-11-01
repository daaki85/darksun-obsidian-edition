#!/bin/sh
# fightout.sh [MAX]: finish a fight the game's own way, so its scripts see each kill: every foe to
# 1 HP (hp.py 1), then on each party turn Tab (the mod picks the nearest enemy) + Return (attacks).
# A member with no Move left gets END TURN (E). A waiting message is clicked away first (msgbox.sh: Tab/Return do nothing under one). Never
# Escape: with no menu up it opens EXIT GAME?. Enemies act alone. DONE when fight_on is 0, else
# STUCK with a screenshot. The arena sends several waves: run it again while a new fight starts.
. "$(dirname "$0")/env.sh"
W=$(timeout 5 xdotool search --class dosbox | head -1)
case "$(timeout 20 python3 "$PT/state.py")" in "fight_on 0"*) echo "NO FIGHT ON"; exit 2;; esac
timeout 20 python3 "$PT/hp.py" 1 >/dev/null
for i in $(seq 1 ${1:-40}); do
  f=$(timeout 20 python3 "$PT/state.py")
  case "$f" in "fight_on 0"*) echo "DONE after $i: $f"; exit 0;; esac
  if sh "$PT/msgbox.sh"; then sh "$PT/boxclick.sh"; sleep 2; continue; fi
  t=$(echo "$f" | sed -n 's/.*turn \([0-9-]*\).*/\1/p')
  if [ -n "$t" ] && [ "$t" -ge 0 ] 2>/dev/null && [ "$t" -le 3 ]; then
    timeout 5 xdotool key --window $W Tab; sleep 1; timeout 5 xdotool key --window $W Return; sleep 4
    # still this member's turn: no Move left, so Return opened END <NAME>'S MOVE (GUARD / WAIT /
    # END TURN), where clicks don't register but E is END TURN; if E opened the Effects screen
    # instead (no menu was up), Escape closes it (safe: a screen is open)
    if timeout 20 python3 "$PT/state.py" | grep -q " turn $t "; then
      timeout 5 xdotool key --window $W e; sleep 3
      if timeout 20 python3 "$PT/state.py" | grep -q " turn $t "; then timeout 5 xdotool key --window $W Escape; sleep 2; fi
    fi
  else sleep 3; fi
done
echo "STUCK: $f"; sh "$PT/shot.sh" "$WORK/stuck-fightout.png"; exit 1
