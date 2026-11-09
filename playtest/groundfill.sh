# groundfill.sh CYCLES [FIRST_TYPE]: fill the ground with items (2026-11-09, the picture-cache test):
# each cycle gives Gerakis (member 0) 12 plain items of new types in memory (giveitems.py), opens
# the inventory and DROPs each, closes it, waits for the game to draw them, and prints slotcount.py.
# Starts and ends on the map with nothing open. Memory only: never save after.
cd "$(dirname "$0")"
. ./env.sh
T=${2:-40}
W=$(xdotool search --class dosbox | head -1)
for c in $(seq 1 $1); do
  out=$(timeout 60 python3 giveitems.py 0 12 $T 2>&1 | tail -1); echo "cycle $c: $out"
  T=$(echo "$out" | awk '{print $NF}')
  case "$out" in *"given 0"*) echo "nothing more to give"; break;; esac
  xdotool key --window $W i; sleep 2.5
  timeout 20 python3 click.py 20 20 >/dev/null; sleep 1
  for y in 26 44 62 80 98 116; do for x in 195 213; do
    timeout 20 python3 click.py $x $y >/dev/null; sleep 0.5
    timeout 20 python3 click.py 213 134 >/dev/null; sleep 0.7
  done; done
  xdotool key --window $W Escape; sleep 3
  timeout 60 python3 slotcount.py "cycle $c"
done
echo DONE
