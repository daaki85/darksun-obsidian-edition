#!/bin/sh
# ringrest.sh: rest at the fire room's ring in pens-fire-count4 (camera 1728,768: the ring at screen 203,88): the eye,
# a slow press on the ring, the walk arrow back (2026-11-09). Each rest there brings Kurzak nearer his call.
cd "$(dirname "$0")"
. ./env.sh
timeout 30 python3 pointer.py look >/dev/null
timeout 15 python3 click.py 203 88 none >/dev/null; sleep 0.3
xdotool mousedown 1; sleep 0.15; xdotool mouseup 1; sleep 6
timeout 30 python3 pointer.py walk
