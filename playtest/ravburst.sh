#!/bin/sh
# ravburst.sh NAME SECONDS [X Y W H]: a burst of window grabs of the running Wake of the Ravager
# ($WORK/rav.pid's DOSBox), as fast as `import` goes (about 15 a second), into $WORK/burst/NAME-NNN.png,
# then a sheet of up to 24 of them, evenly spaced, cropped to X Y W H in window pixels (640x480), 8 a row,
# each labelled with its number, as $WORK/burst/NAME.png: to see an animation (a walk, a swing, a fall)
# frame by frame.
. "$(dirname "$0")/env.sh"
N=$1; S=$2; D=$WORK/burst; mkdir -p "$D"; rm -f "$D/$N"-*.png
W=$(timeout 5 xdotool search --pid "$(cat "$WORK/rav.pid")" | tail -1)
[ -z "$W" ] && { echo "no window"; exit 1; }
end=$(( $(date +%s) + S )); i=0
while [ "$(date +%s)" -lt "$end" ]; do
  import -window "$W" "$D/$N-$(printf %03d $i).png"; i=$((i + 1))
done
if [ -n "$6" ]; then
  k=$(( (i + 23) / 24 )); [ "$k" -lt 1 ] && k=1
  ls "$D/$N"-*.png | awk -v k="$k" 'NR % k == 1 || k == 1' |
    while read f; do convert "$f" -crop "$5x$6+$3+$4" +repage miff:- ; done |
    montage - -tile 8x -geometry +2+2 -background gray20 "$D/$N.png"
fi
echo "$i grabs: $D/$N-*.png ${6:+strip $D/$N.png}"
