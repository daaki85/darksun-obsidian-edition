#!/bin/sh
# msgbox.sh: exit 0 if a message waits for a click: the speech box with a portrait at the top (its
# frame's pixel at 60,3 is 154,154,178) or the grey message window (113,113,138 at 200,50). Tab,
# Return and map clicks do nothing while one is up. A YES/NO question is one too, but a click
# doesn't answer it: press N or Y (see PLAYTESTING.md).
. "$(dirname "$0")/env.sh"
# (pixmatch.py: the colours within 3 and a row either way, for the recompiled program's picture)
timeout 20 python3 "$PT/pixmatch.py" 60 3 154 154 178 && exit 0
timeout 20 python3 "$PT/pixmatch.py" 200 50 113 113 138 && exit 0
exit 1
