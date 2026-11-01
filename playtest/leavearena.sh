#!/bin/sh
# leavearena.sh: right after "Go back to the pens" (arenawaves.sh), before the arena's patience runs
# out: drag the view (scroll.py, the middle button) until the ground inside the wall, between the
# bones and the gate (488, 232), is on screen, click it (the party finds its own way in), then keep
# clicking the gate strip until the region is the pens (29h). The user's way, 2026-11-01. Prints
# each step; IN THE PENS or STUCK.
. "$(dirname "$0")/env.sh"
sh "$PT/panel.sh" hide >/dev/null
cam() { timeout 20 python3 "$PT/state.py" | sed -n 's/.*camera (\([-0-9]*\), \([-0-9]*\)).*/\1 \2/p'; }
for i in 1 2 3 4 5 6; do   # the view north and over x 488
  set -- $(cam); echo "camera $1 $2"
  dx=$(( ($1 - 328) * 5 / 4 )); dy=$(( ($2 - 112) * 5 / 4 ))
  [ ${dx#-} -lt 20 ] && [ ${dy#-} -lt 20 ] && break
  timeout 30 python3 "$PT/scroll.py" $dx $dy
done
for tx_ty in "488 232" "488 200" "488 176"; do  # inside the wall, then the gate strip
  set -- $tx_ty; tx=$1; ty=$2
  for k in 1 2 3 4; do
    s=$(timeout 20 python3 "$PT/state.py"); echo "$s"
    case "$s" in *"region 0x29"*) echo "IN THE PENS"; exit 0;; esac
    if sh "$PT/msgbox.sh"; then timeout 5 xdotool mousedown 1; sleep 0.1; timeout 5 xdotool mouseup 1; sleep 2; continue; fi
    set -- $(cam); sx=$(( tx - $1 )); sy=$(( ty - $2 ))
    if [ $sy -lt 24 ]; then timeout 30 python3 "$PT/scroll.py" 0 40; continue; fi
    timeout 15 python3 "$PT/click.py" $sx $sy >/dev/null; sleep 6
  done
done
s=$(timeout 20 python3 "$PT/state.py"); case "$s" in *"region 0x29"*) echo "IN THE PENS"; exit 0;; esac
echo "STUCK: $s"; sh "$PT/shot.sh" "$WORK/stuck-leave.png"; exit 1
