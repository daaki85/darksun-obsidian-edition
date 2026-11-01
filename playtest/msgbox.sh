#!/bin/sh
# msgbox.sh: exit 0 if a message waits for a click: the speech box with a portrait at the top (its
# frame's pixel at 60,3 is 154,154,178) or the grey message window (113,113,138 at 200,50). Tab,
# Return and map clicks do nothing while one is up. A YES/NO question is one too, but a click
# doesn't answer it: press N or Y (see PLAYTESTING.md).
. "$(dirname "$0")/env.sh"
W=$(timeout 5 xdotool search $WINQ | head -1)
p=$(timeout 10 import -window $W png:- | convert - -format '%[pixel:p{60,3}] %[pixel:p{200,50}]' info:)
case "$p" in "srgb(154,154,178) "*|*" srgb(113,113,138)") exit 0;; esac; exit 1
