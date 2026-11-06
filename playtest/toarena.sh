# toarena.sh: after Kurzak's call, from the fire room: up to the arena (route.py through his entryway, his stop,
# the corridor at y 408), then a click into the gap south of (1816, 408): "Enter the arena?" (answer Y yourself)
. "$(dirname "$0")/env.sh"; cd "$PT"
d() { timeout 15 sh dismiss.sh >/dev/null 2>&1; }
cam() { python3 state.py | tail -1 | sed 's/.*camera (\([0-9]*\), \([0-9]*\)).*/\1 \2/'; }
d; timeout 100 python3 route.py 1592 584 | tail -1; d
timeout 60 python3 route.py 1592 584 | tail -1; d
timeout 40 python3 walkto.py 1592 520 | tail -1; d
timeout 40 python3 walkto.py 1592 440 | tail -1; d
timeout 50 python3 walkto.py 1700 408 | tail -1; d
timeout 50 python3 walkto.py 1816 408 | tail -1; d
set -- $(cam); timeout 10 python3 click.py $((1816-$1)) $((440-$2)) left; sleep 3
tail -1 $WORK/dice.txt
