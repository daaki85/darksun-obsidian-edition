#!/bin/sh
# stepfight.sh: from the arena gate, clicks south until the fight is on (topartyfight.sh's last loop)
PT0=$(cd "$(dirname "$0")" && pwd); . "$PT0/env.sh"; PT=$PT0
sh $PT/panel.sh hide >/dev/null
for i in $(seq 1 30); do
  f=$(timeout 10 python3 $PT/state.py 2>/dev/null)
  case "$f" in "fight_on 1"*) echo "FIGHT: $f"; sh $PT/panel.sh show >/dev/null; exit 0;; esac
  if sh $PT/msgbox.sh; then sh "$PT/boxclick.sh"; sleep 2
  else timeout 15 python3 $PT/click.py 160 165 >/dev/null; sleep 5; fi
done
echo "NO FIGHT: $f"
