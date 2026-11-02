#!/bin/sh
# boxclick.sh: click a waiting message away by clicking ON it (160, 20, the speech box at the top):
# a click wherever the pointer happens to be (after a drag, say) didn't always count (2026-11-01)
. "$(dirname "$0")/env.sh"
timeout 15 python3 "$PT/click.py" 160 20 >/dev/null; sleep 1
