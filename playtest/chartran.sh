#!/bin/sh
# chartran.sh SAVE.SAV OUTDIR [DEBUG]: runs Wake of the Ravager's own transfer utility (CHARTRAN.EXE,
# from $RAV, setup_ravager.sh) on one Shattered Lands save in a headless DOSBox of its own (not the
# game's: no Loader, no lock needed), and leaves in OUTDIR/C/RAVAGER the sequel's roster it wrote
# (CHARSAVE.GFF, started from the install's own), its screen text (OUT.TXT) and, with DEBUG, its
# DEBUG.DAT: every item's "OLD: -<Shattered Lands object>, NEW: <sequel object>" (900 a money bag)
# and each spell and psionic aptitude it couldn't carry. Takes 15 seconds. Kills no other DOSBox.
. "$(dirname "$0")/env.sh"
RAV=${RAV:-$WORK/rav}; SAV=$1; R=$2; ARGS=$3
[ -f "$SAV" ] && [ -n "$R" ] || { echo "usage: chartran.sh SAVE.SAV OUTDIR [DEBUG]"; exit 1; }
[ -f "$RAV/CHARTRAN.EXE" ] || { echo "no $RAV/CHARTRAN.EXE: run setup_ravager.sh"; exit 1; }
rm -rf "$R"; mkdir -p "$R/C/DSUN" "$R/C/RAVAGER"
cp "$SAV" "$R/C/DSUN/SAVE01.SAV"
cp "$RAV/CHARTRAN.EXE" "$RAV/ITEMS.BIN" "$RAV/OBJEX.GFF" "$RAV/__support/save/CHARSAVE.GFF" "$R/C/RAVAGER/"
cat > "$R/ct.conf" <<E2
[sdl]
output=surface
[dosbox]
memsize=16
[cpu]
cycles=max
[mixer]
nosound=true
[autoexec]
mount c $R/C
c:
cd \\RAVAGER
CHARTRAN.EXE $ARGS > OUT.TXT
exit
E2
pgrep -x Xvfb >/dev/null || { setsid nohup Xvfb :55 -screen 0 1024x768x24 >/dev/null 2>&1 & sleep 1; }
setsid dosbox -conf "$R/ct.conf" >"$R/dosbox.log" 2>&1 &
P=$!; sleep 3
W=$(timeout 5 xdotool search --pid $P 2>/dev/null | tail -1)
[ -z "$W" ] && { echo "no DOSBox window"; kill $P; exit 1; }
# the paths screen (C:\DSUN, C:\RAVAGER): Enter; the list of saves: A, the only one
xdotool key --window "$W" Return; sleep 2; xdotool key --window "$W" a; sleep 8
kill $P 2>/dev/null; wait $P 2>/dev/null
tr -d '\r' < "$R/C/RAVAGER/OUT.TXT" | grep -v '^$'
