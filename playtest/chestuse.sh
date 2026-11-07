# chestuse.sh: uses Pehtucl's chest from where the party stands (see PLAYTESTING, Pehtucl's chest):
# the eye (two right-clicks on bare floor at 200,175), a slow press on the chest (161,72), its look
# box's third button (236,101). Shots cu0-cu2.png in the work folder.
. "$(dirname "$0")/env.sh"
cd "$(dirname "$0")"
for i in 1 2; do timeout 10 python3 click.py 200 175 right >/dev/null; sleep 0.6; done
timeout 10 python3 click.py 161 72 none >/dev/null; sleep 0.4
sh shot.sh "$WORK/cu0.png"
xdotool mousedown 1; sleep 0.15; xdotool mouseup 1; sleep 2; sh shot.sh "$WORK/cu1.png"
timeout 10 python3 click.py 236 101 none >/dev/null; sleep 0.3
xdotool mousedown 1; sleep 0.15; xdotool mouseup 1; sleep 3; sh shot.sh "$WORK/cu2.png"
