# chestuse.sh: uses Pehtucl's chest from a square beside it (ROUTE.md, Pehtucl's chest): the eye set
# with pointer.py look, a slow press on the chest (163,70), its look box's third button (236,101), then
# the walk arrow back. Shots cu0-cu2.png in the work folder.
# (The press at 161,72 after two blind right-clicks opened the USE screen, 2026-11-16: HISTORY.md.)
. "$(dirname "$0")/env.sh"
cd "$(dirname "$0")"
timeout 20 python3 pointer.py look >/dev/null
timeout 10 python3 click.py 163 70 none >/dev/null; sleep 0.4
sh shot.sh "$WORK/cu0.png"
xdotool mousedown 1; sleep 0.15; xdotool mouseup 1; sleep 2; sh shot.sh "$WORK/cu1.png"
timeout 10 python3 click.py 236 101 none >/dev/null; sleep 0.3
xdotool mousedown 1; sleep 0.15; xdotool mouseup 1; sleep 3; sh shot.sh "$WORK/cu2.png"
timeout 20 python3 pointer.py walk >/dev/null   # (the eye pauses the game: rule 9)
