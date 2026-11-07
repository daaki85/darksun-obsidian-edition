# passmiss.sh: in a fight, the party's turns passed through each member's END menu (memberpos.py, E) until a
# foe misses (the dice log's "-> miss"), then the view dragged and shots taken (missdrag.png,
# missafter.png). E that opened the Effects screen (the camera at 0,0) is closed and the view brought back.
. /home/user/darksun-obsidian-edition/playtest/env.sh
cd /home/user/darksun-obsidian-edition/playtest
start=$(wc -l < $WORK/dice.txt)
for i in $(seq 1 80); do
  st=$(timeout 10 python3 state.py)
  case "$st" in *"fight_on 0"*) echo FIGHT_OVER; break;; esac
  if tail -n +$((start+1)) $WORK/dice.txt | grep -q -- "-> miss$"; then
    timeout 20 python3 scroll.py 0 -150 >/dev/null 2>&1; timeout 20 python3 scroll.py 0 -150 >/dev/null 2>&1; timeout 10 python3 state.py; for n in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do timeout 10 python3 memberpos.py $n 2>/dev/null; done | head -0; sh shot.sh $WORK/missdrag.png
    echo MISS_DRAGGED; sleep 2.5; sh shot.sh $WORK/missafter.png; break
  fi
  t=$(echo "$st" | sed -n 's/.*turn \([0-9]*\).*/\1/p')
  if [ -n "$t" ] && [ "$t" -le 3 ]; then
    set -- $(timeout 10 python3 memberpos.py $t | tail -1)
    if [ "${2:-0}" -gt 20 ] && [ "${2:-0}" -lt 190 ] && [ "${1:-0}" -gt 5 ] && [ "${1:-0}" -lt 315 ]; then
      timeout 10 python3 click.py $1 $2 >/dev/null; sleep 0.9; xdotool key e; sleep 1.2
      case "$(timeout 10 python3 state.py)" in *"camera (0, 0)"*)
        xdotool key Escape; sleep 1; timeout 120 python3 viewto.py 1912 872 >/dev/null; echo "effects closed";; esac
      echo "pass $t"
    else echo "member $t off screen: $*"; timeout 120 python3 viewto.py 1912 872 >/dev/null; fi
  fi
  sleep 0.3
done
echo PM_DONE
