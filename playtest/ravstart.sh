#!/bin/sh
# ravstart.sh [FOLDER]: Wake of the Ravager in DOSBox (GOG's settings, sound off), from FOLDER (default
# $WORK/rav; $WORK/ravfix for ravfixes.py's copy), to the first scene in Tyr: Shift skips the intro, S
# on the menu is START GAME, then the narrated cinematic (about 60 s, no skip). D: is the CD's data
# track alone (a cue it writes: Linux's DOSBox can't take GOG's game.ins, its music .ogg). Its pid in
# $WORK/rav.pid, its config $WORK/rav.conf. `RAV_UMB=1` runs it as the mod would (EMS off,
# UMBPLUS.COM first). `RAV_LOADER=1` starts it as the Loader does (`RAV_SKIP=NAME,...` with it: those
# patches of dsloader.ravager.PATCHES or SCRIPT_FIXES left out of the copy, for a test's control). `RAV_MENU=1` stops at the
# title menu, START GAME not pressed (ravload.sh loads a save from there): dsloader.ravager's
# copies (DSUNLOG2.EXE, RESOURC2.GFF, GPLDAT2.GFF) in the mod's dos folder, run from E: with the game as C:. Kills nothing: stop an earlier one first. About 90 s.
. "$(dirname "$0")/env.sh"
F=${1:-$WORK/rav}
[ -f "$F/DSUN.EXE" ] || { echo "no $F/DSUN.EXE (setup_ravager.sh)"; exit 1; }
for f in "$F"/__support/save/*; do [ -f "$F/$(basename "$f")" ] || cp "$f" "$F/"; done
printf 'FILE "game.gog" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' > "$F/data.cue"
C=$WORK/rav.conf
grep -v "^#" "$F/__support/app/dosbox_darksun2.conf" | sed '/^\[autoexec\]/,$d' |
  sed 's/^output=.*/output=surface/; s/^fullscreen=.*/fullscreen=false/; s/^nosound=.*/nosound=true/' > "$C"
[ -n "$RAV_UMB" ] && sed -i 's/^ems=true/ems=false/' "$C"
if [ -n "$RAV_LOADER" ]; then   # the Loader's way: its copies (dsloader.ravager) and its autoexec
  sed -i '/^\[dos\]/,$d' "$C"
  python3 - "$F" "$REPO/obsidian-edition/dos" >> "$C" <<'PY' || exit 1
import sys, os
sys.path.insert(0, os.path.join(sys.argv[2], '..'))
from dsloader import ravager
problem = ravager.prepare(sys.argv[1], sys.argv[2], {})
if problem: sys.exit('ravager.prepare: ' + problem)
skip = [s for s in os.environ.get('RAV_SKIP', '').split(',') if s]   # (a control run: those fixes left out)
if skip:
    exe = os.path.join(sys.argv[2], ravager.PATCHED_EXE); data = bytearray(open(exe, 'rb').read())
    for p in ravager.PATCHES:
        if p.name in skip:
            assert data[p.offset:p.offset + len(p.replacement)] == p.replacement, p.name
            data[p.offset:p.offset + len(p.original)] = p.original; skip.remove(p.name)
    gone = [s for s in skip if s in ravager.SCRIPT_FIXES]   # (a script fix: GPLDAT2.GFF without it)
    if gone:
        ravager.write_scripts(sys.argv[1], os.path.join(sys.argv[2], ravager.SCRIPT_COPY), set(gone))
        skip = [s for s in skip if s not in gone]
    if skip: sys.exit('RAV_SKIP: no such patch ' + ','.join(skip))
    open(exe, 'wb').write(data); print('# left out:', os.environ['RAV_SKIP'])
print('\n'.join(ravager.conf_lines(sys.argv[1], sys.argv[2], cd=os.path.join(sys.argv[1], 'data.cue'))))
PY
else
{ echo "[autoexec]"; echo "mount c $F"; echo "imgmount d $F/data.cue -t iso"
  [ -n "$RAV_UMB" ] && { echo "mount e $REPO/obsidian-edition/dos"; echo 'e:\umbplus.com'; }
  echo "c:"; echo "DSUN -W0 -L"; } >> "$C"
fi
pgrep -x Xvfb >/dev/null || { setsid nohup Xvfb :55 -screen 0 1024x768x24 >/dev/null 2>&1 & sleep 2; }
setsid nohup dosbox -conf "$C" > "$WORK/rav-dosbox.log" 2>&1 &
echo $! > "$WORK/rav.pid"; sleep 6
W=$(timeout 5 xdotool search --pid "$(cat "$WORK/rav.pid")" | tail -1)
[ -z "$W" ] && { echo "no DOSBox window"; exit 1; }
for t in 1 2; do xdotool keydown --window "$W" Shift_L; sleep 1; xdotool keyup --window "$W" Shift_L; sleep 3; done
[ -n "$RAV_MENU" ] && { import -window "$W" "$WORK/rav-menu.png"; echo "pid $(cat "$WORK/rav.pid"), window $W: at the title menu ($WORK/rav-menu.png)"; exit 0; }
xdotool key --window "$W" s; sleep 80
import -window "$W" "$WORK/rav-tyr.png"; echo "pid $(cat "$WORK/rav.pid"), window $W: $WORK/rav-tyr.png"
