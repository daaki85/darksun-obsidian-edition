#!/bin/sh
# arenawaves.sh: with the arena's first fight on, fight every wave (fightout.sh) and click away the
# messages between them, until the YES/NO question ("Yell something back at the Announcer?"),
# which it answers N. Then the arena says "Go back to the pens to heal your wounds" and the clock
# runs: leave at once (PLAYTESTING.md, the arena). Prints each wave's end and DONE or STUCK.
. "$(dirname "$0")/env.sh"
W=$(timeout 5 xdotool search --class dosbox | head -1)
for wave in 1 2 3 4 5 6 7 8; do
  case "$(timeout 20 python3 "$PT/state.py")" in "fight_on 1"*)
    timeout 900 sh "$PT/fightout.sh" 120 | tail -1;; esac
  for i in $(seq 1 15); do
    if [ "$(tail -1 "$WORK/dice.txt")" = "    2. No" ]; then
      timeout 5 xdotool key --window $W n; sleep 3; tail -2 "$WORK/dice.txt"
      sh "$PT/dismiss.sh" 4 >/dev/null; echo DONE; exit 0
    fi
    timeout 20 python3 "$PT/state.py" | grep -q "^fight_on 1" && break
    if sh "$PT/msgbox.sh"; then sh "$PT/boxclick.sh"; fi; sleep 2
  done
  echo "wave $wave over: $(timeout 20 python3 "$PT/state.py")"
done
echo STUCK; sh "$PT/shot.sh" "$WORK/stuck-waves.png"; exit 1
