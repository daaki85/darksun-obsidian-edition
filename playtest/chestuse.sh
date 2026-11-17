# chestuse.sh [y|n]: uses Pehtucl's chest from a square beside it (ROUTE.md, Pehtucl's chest): the eye
# set with pointer.py look, a slow press on the chest (163,70), its look box's third button (236,101),
# then the walk arrow back. Shots cu0-cu2.png in the work folder. The use's message or question (a
# non-thief's "Bash it open?") takes the right-clicks that set the pointer, so with one up the eye
# stays: give the answer (y or n) to have it pressed, the messages after it clicked away and the walk
# arrow put back; without one the
# script leaves the question up and says so (2026-11-17: HISTORY.md, Pehtucl's chest).
. "$(dirname "$0")/env.sh"
cd "$(dirname "$0")"
timeout 20 python3 pointer.py look >/dev/null
timeout 10 python3 click.py 163 70 none >/dev/null; sleep 0.4
sh shot.sh "$WORK/cu0.png"
xdotool mousedown 1; sleep 0.15; xdotool mouseup 1; sleep 2; sh shot.sh "$WORK/cu1.png"
timeout 10 python3 click.py 236 101 none >/dev/null; sleep 0.3
xdotool mousedown 1; sleep 0.15; xdotool mouseup 1; sleep 3; sh shot.sh "$WORK/cu2.png"
W=$(xdotool search $WINQ | head -1)
if sh msgbox.sh; then
    if [ -z "$1" ]; then
        echo "a message or question is up (cu2.png): answer it, then pointer.py walk (the eye is still up)"
        exit 0
    fi
    xdotool key --window "$W" "$1"; sleep 2; sh shot.sh "$WORK/cu3.png"
    for i in 1 2 3; do sh msgbox.sh || break; sh boxclick.sh >/dev/null; sleep 1.5; done   # its answer
fi
timeout 20 python3 pointer.py walk   # (the eye pauses the game: rule 9)
