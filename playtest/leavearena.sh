#!/bin/sh
# leavearena.sh: right after "Go back to the pens" (arenawaves.sh), before the arena's patience runs
# out (a few actions): each step first clicks away any message (a box blocks drags as well as
# clicks), then drags the view (scroll.py, the middle button; at most 150 pixels a drag) until the
# ground inside the wall, between the bones and the gate (488, 232), is on screen, and clicks it:
# the party finds its own way in (the user's way, 2026-11-01). Then the gate strip (488, 184):
# "This corridor leads down to the slavepens. Do you wish to continue?" Y, and the region is the
# pens (29h). Prints each step; IN THE PENS or STUCK.
. "$(dirname "$0")/env.sh"
W=$(timeout 5 xdotool search $WINQ | head -1)
sh "$PT/panel.sh" hide >/dev/null
clamp() { v=$1; [ $v -gt 150 ] && v=150; [ $v -lt -150 ] && v=-150; echo $v; }
for target in "488 232" "488 232" "488 200" "488 184" "488 184" "488 176"; do
  set -- $target; tx=$1; ty=$2
  for k in 1 2 3 4 5 6 7 8; do
    s=$(timeout 20 python3 "$PT/state.py"); echo "$s"
    case "$s" in *"region 0x29"*) echo "IN THE PENS"; exit 0;; "fight_on 1"*) echo "A FIGHT: fightout.sh first"; exit 1;; esac
    if [ "$(tail -1 "$WORK/dice.txt")" = "    2. No" ]; then  # the gate's "Do you wish to continue?": Y; any other: N
      if tail -6 "$WORK/dice.txt" | grep -q "leads down to the slavepens"; then timeout 5 xdotool key --window $W y; sleep 8
      else timeout 5 xdotool key --window $W n; sleep 2; fi; continue
    fi
    if sh "$PT/msgbox.sh"; then sh "$PT/boxclick.sh"; sleep 1; continue; fi
    cx=$(echo "$s" | sed -n 's/.*camera (\([-0-9]*\), .*/\1/p'); cy=$(echo "$s" | sed -n 's/.*camera ([-0-9]*, \([-0-9]*\)).*/\1/p')
    sx=$(( tx - cx )); sy=$(( ty - cy ))
    if [ $sx -lt 20 ] || [ $sx -gt 300 ] || [ $sy -lt 40 ] || [ $sy -gt 180 ]; then
      timeout 30 python3 "$PT/scroll.py" $(clamp $(( (sx - 160) * -5 / 4 ))) $(clamp $(( (sy - 110) * -5 / 4 ))); continue
    fi
    timeout 15 python3 "$PT/click.py" $sx $sy >/dev/null; sleep 5; break
  done
done
s=$(timeout 20 python3 "$PT/state.py"); case "$s" in *"region 0x29"*) echo "IN THE PENS"; exit 0;; esac
echo "STUCK: $s"; tail -2 "$WORK/dice.txt"; sh "$PT/shot.sh" "$WORK/stuck-leave.png"; exit 1
