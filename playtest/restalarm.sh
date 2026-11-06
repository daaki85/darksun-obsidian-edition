# restalarm.sh: in the fire room (toalarm.sh), rest at the ring (map 1931, 856) with the look
# pointer until Kurzak calls, then wait there till his patience runs out: the alarm, and a fight
# with the guards. **The pointer must be the eye before this runs**: on 2026-11-06 it was the sword,
# no rest was had ("rests: 0") and the click at the ring fell on Cilla (Gerakis slung a stone at
# her). Check a shot first, and right-click on bare floor until the eye shows.
. "$(dirname "$0")/env.sh"; cd "$PT"
start=$(wc -l < $WORK/dice.txt)
new() { tail -n +$start $WORK/dice.txt; }
cam() { timeout 20 python3 state.py | tail -1 | sed 's/.*camera (\([0-9-]*\), \([0-9-]*\)).*/\1 \2/'; }
for i in 1 2 3 4 5; do
  sh boxclick.sh >/dev/null 2>&1; sleep 1
  set -- $(cam)
  timeout 20 python3 click.py $((1931 - $1)) $((856 - $2)) none >/dev/null; sleep 0.3; xdotool mousedown 1; sleep 0.15; xdotool mouseup 1; sleep 6
done
echo "rests: $(new | grep -c 'THE PARTY RESTS')"
sh boxclick.sh >/dev/null 2>&1
timeout 20 python3 click.py 140 105 right >/dev/null; sleep 0.6; for b in 1 2 3; do xdotool mouseup $b; done
for i in $(seq 1 40); do
  new | grep -q "Time's run out" && { echo ALARM; break; }
  st=$(timeout 20 python3 state.py | tail -1); case "$st" in *"fight_on 1"*) echo FIGHT; break;; esac
  sh dismiss.sh >/dev/null 2>&1
  if [ $((i % 2)) = 0 ]; then timeout 40 python3 walkto.py 1912 872 >/dev/null; else timeout 40 python3 walkto.py 1880 880 >/dev/null; fi
  sleep 2
done
new | grep -c "Get up here" | sed 's/^/calls: /'
for i in $(seq 1 10); do sh boxclick.sh >/dev/null 2>&1; sleep 2; st=$(timeout 20 python3 state.py | tail -1); case "$st" in *"fight_on 1"*) echo FIGHT-ON; break;; esac; done
timeout 20 python3 state.py | tail -1
