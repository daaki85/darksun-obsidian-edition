# tofight.sh N: fountain-user loaded, Ester's arrows made N, the ambush started, every foe Paralyzed,
# and on to Ester's turn (logs/2026-11-14-quiver-turn.md). Memory edits: never save after.
cd "$(dirname "$0")"
timeout 180 sh loadsave.sh fountain-user | tail -1
timeout 30 python3 setarrows.py 2 $1
timeout 60 sh dismiss.sh >/dev/null 2>&1; sleep 3
for c in $(timeout 30 python3 foeset.py 2>/dev/null | awk '$2=="creature" && $1>=4 {print $1}'); do timeout 20 python3 foeset.py $c eff=34 >/dev/null 2>&1; done
timeout 30 sh panel.sh hide | tail -1
timeout 240 sh passuntil.sh 2 2>&1 | tail -1
