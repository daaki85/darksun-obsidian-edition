#!/bin/sh
# framegrab.sh DIR SECONDS: the game window grabbed (import -window) as fast as it goes, about 36 a
# second, into DIR/f00000.png on, for SECONDS; prints how many (run it in the background while a fight plays).
W=$(xdotool search --class dosbox | head -1); mkdir -p $1; end=$(( $(date +%s) + $2 )); n=0
while [ $(date +%s) -lt $end ]; do import -window $W $1/f$(printf %05d $n).png 2>/dev/null; n=$((n+1)); done; echo $n frames
