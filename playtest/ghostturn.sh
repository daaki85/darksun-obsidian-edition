# ghostturn.sh: in a fight, GHOST_UNION's whole-view drawing on a GHOST_TAB change (GH_CHANGED) seen
# in the enemies' turns: in one, Cermak (thing 2) marked see-through without the changed byte (the
# control: he should stay solid), in the next with it (see-through before the party's turn). Shots
# ctrl_N.png and with_N.png in the work folder, each noting the turn; markmember.py writes the table.
. "$(dirname "$0")/env.sh"; cd "$PT"
turn() { timeout 10 python3 state.py | sed -n 's/.*turn \([0-9]*\).*/\1/p'; }
pass_party() {  # (until an enemy's turn)
  for i in $(seq 1 30); do
    t=$(turn); [ -z "$t" ] && return; [ "$t" -gt 3 ] && return
    set -- $(timeout 10 python3 memberpos.py $t | tail -1)
    if [ "${2:-0}" -gt 20 ] && [ "${2:-0}" -lt 190 ]; then
      timeout 10 python3 click.py $1 $2 >/dev/null; sleep 0.9; xdotool key e; sleep 1.2
      case "$(timeout 10 python3 state.py)" in *"camera (0, 0)"*) xdotool key Escape; sleep 1; timeout 120 python3 viewto.py 1912 872 >/dev/null;; esac
    else timeout 120 python3 viewto.py 1912 872 >/dev/null; fi
  done
}
watch_enemies() {  # NAME: shots while the enemies act, the last kept
  n=0; while [ "$(turn)" -gt 3 ] 2>/dev/null && [ $n -lt 60 ]; do n=$((n+1)); sh shot.sh $WORK/$1_$n.png; echo "$1 $n turn $(turn) pos $(timeout 10 python3 memberpos.py 2 | tail -1)"; sleep 0.25; done
}
pass_party
python3 markmember.py 2 0; watch_enemies ctrl
python3 markmember.py none 1; pass_party
python3 markmember.py 2 1; watch_enemies with
python3 markmember.py none 1
echo GT_DONE
