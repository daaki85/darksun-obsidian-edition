#!/bin/sh
# ravstart.sh [FOLDER]: Wake of the Ravager in DOSBox (GOG's settings, sound off), from FOLDER (default
# $WORK/rav; $WORK/ravfix for ravfixes.py's copy), to the first scene in Tyr: Shift skips the intro, S
# on the menu is START GAME, then the narrated cinematic (about 60 s, no skip). D: is the CD's data
# track alone (a cue it writes: Linux's DOSBox can't take GOG's game.ins, its music .ogg). Its pid in
# $WORK/rav.pid, its config $WORK/rav.conf. `RAV_UMB=1` runs it as the mod would (EMS off,
# UMBPLUS.COM first). Kills nothing: stop an earlier one first. About 90 s.
. "$(dirname "$0")/env.sh"
F=${1:-$WORK/rav}
[ -f "$F/DSUN.EXE" ] || { echo "no $F/DSUN.EXE (setup_ravager.sh)"; exit 1; }
for f in "$F"/__support/save/*; do [ -f "$F/$(basename "$f")" ] || cp "$f" "$F/"; done
printf 'FILE "game.gog" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' > "$F/data.cue"
C=$WORK/rav.conf
grep -v "^#" "$F/__support/app/dosbox_darksun2.conf" | sed '/^\[autoexec\]/,$d' |
  sed 's/^output=.*/output=surface/; s/^fullscreen=.*/fullscreen=false/; s/^nosound=.*/nosound=true/' > "$C"
[ -n "$RAV_UMB" ] && sed -i 's/^ems=true/ems=false/' "$C"
{ echo "[autoexec]"; echo "mount c $F"; echo "imgmount d $F/data.cue -t iso"
  [ -n "$RAV_UMB" ] && { echo "mount e $REPO/obsidian-edition/dos"; echo 'e:\umbplus.com'; }
  echo "c:"; echo "DSUN -W0 -L"; } >> "$C"
pgrep -x Xvfb >/dev/null || { setsid nohup Xvfb :55 -screen 0 1024x768x24 >/dev/null 2>&1 & sleep 2; }
setsid nohup dosbox -conf "$C" > "$WORK/rav-dosbox.log" 2>&1 &
echo $! > "$WORK/rav.pid"; sleep 6
W=$(timeout 5 xdotool search --pid "$(cat "$WORK/rav.pid")" | tail -1)
[ -z "$W" ] && { echo "no DOSBox window"; exit 1; }
for t in 1 2; do xdotool keydown --window "$W" Shift_L; sleep 1; xdotool keyup --window "$W" Shift_L; sleep 3; done
xdotool key --window "$W" s; sleep 80
import -window "$W" "$WORK/rav-tyr.png"; echo "pid $(cat "$WORK/rav.pid"), window $W: $WORK/rav-tyr.png"
