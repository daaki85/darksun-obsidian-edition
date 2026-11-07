# arenatrip.sh: from pens-after-scar (toalarm.sh: loaded, Cilla a thief in memory, to the fire room), rest till
# Kurzak calls, answer at once (toarena.sh, Y at "Enter the arena?"), and count the game's free things
# (thingsfree.py) in the fire room and on arriving in the arena. Never save after (Cilla raised).
. "$(dirname "$0")/env.sh"; cd "$PT"
timeout 900 sh toalarm.sh | tail -3
timeout 20 python3 click.py 240 160 >/dev/null; sleep 4   # (into the fire room when the walk stops short)
timeout 20 python3 thingsfree.py "fire room" 
timeout 20 python3 pointer.py look >/dev/null
start=$(wc -l < $WORK/dice.txt)
cam() { timeout 20 python3 state.py | tail -1 | sed 's/.*camera (\([0-9-]*\), \([0-9-]*\)).*/\1 \2/'; }
for i in 1 2 3 4 5 6; do
  tail -n +$start $WORK/dice.txt | grep -q "Get up here" && break
  sh boxclick.sh >/dev/null 2>&1; sleep 1
  set -- $(cam)
  timeout 20 python3 pointer.py look >/dev/null
  timeout 20 python3 click.py $((1931 - $1)) $((856 - $2)) none >/dev/null; sleep 0.3; xdotool mousedown 1; sleep 0.15; xdotool mouseup 1; sleep 6
  timeout 20 python3 pointer.py walk >/dev/null   # (the eye pauses the game: no call while it is up)
  tail -n +$start $WORK/dice.txt | grep -q "Get up here" && break
  timeout 40 python3 walkto.py 1912 872 >/dev/null
done
echo "rests: $(tail -n +$start $WORK/dice.txt | grep -c 'THE PARTY RESTS') calls: $(tail -n +$start $WORK/dice.txt | grep -c 'Get up here')"
sh dismiss.sh >/dev/null 2>&1; sh boxclick.sh >/dev/null 2>&1
timeout 20 python3 pointer.py walk >/dev/null
timeout 600 sh toarena.sh | tail -2
for i in 1 2 3 4 5 6; do tail -3 $WORK/dice.txt | grep -q "2. No" && { xdotool key y; break; }; sleep 2; done
sleep 8; timeout 20 python3 state.py; timeout 20 python3 thingsfree.py "arena arrival"
echo TRIP_DONE
