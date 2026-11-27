#!/bin/sh
# ravstart.sh [FOLDER]: Wake of the Ravager in DOSBox (GOG's settings, sound off), from FOLDER (default
# $WORK/rav; $WORK/ravfix for ravfixes.py's copy), to the first scene in Tyr: Shift skips the intro, S
# on the menu is START GAME, then the narrated cinematic (about 60 s, no skip). D: is the CD's data
# track alone (a cue it writes: Linux's DOSBox can't take GOG's game.ins, its music .ogg). Its pid in
# $WORK/rav.pid, its config $WORK/rav.conf. `RAV_UMB=1` runs it as the mod would (EMS off,
# UMBPLUS.COM first). `RAV_LOADER=1` starts it as the Loader does (its 48h sheets: FOLDER's roster and saves widened, NAME.42H backups; `python -m dsloader.ravager narrow FOLDER` before a plain start); `RAV_SKIP=NAME,...` with it leaves parts out for a control (patches, script fixes, object parts: every name and what it changes in RESEARCH.md, "A control run: RAV_SKIP"); the new items' pictures from $GAME's Shattered Lands, `RAV_SL=` none. `RAV_CORE=normal` runs DOSBox's normal CPU core. `RAV_NOEXIT=1` keeps DOSBox up when the game quits; `RAV_PAUSE=1` pauses before DOSBox closes; `RAV_MARK=1` writes ENDED.TXT in the game folder when the game ends; `RAV_STDOUT=1` sends the game's printing to STDOUT.TXT there (a fatal error's message: "Illegal Op (gpl=N)"); `RAV_POKE=OFF=HEX,...` puts bytes at file offsets of the patched program (with RAV_LOADER). `RAV_SOUND=1` keeps DOSBox's sound on (SDL's dummy audio device: the game finds its card, nothing heard). `RAV_MENU=1` stops at the
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
[ -n "$RAV_SOUND" ] && sed -i 's/^nosound=.*/nosound=false/' "$C"   # (sound on, to a dummy audio device: the game's sound driver found as with a card)
[ -n "$RAV_UMB" ] && sed -i 's/^ems=true/ems=false/' "$C"
if [ -n "$RAV_LOADER" ]; then   # the Loader's way: its copies (dsloader.ravager) and its autoexec
  sed -i '/^\[dos\]/,$d' "$C"
  python3 - "$F" "$REPO/obsidian-edition/dos" "${RAV_SL-$GAME}" >> "$C" <<'PY' || exit 1
import sys, os
sys.path.insert(0, os.path.join(sys.argv[2], '..'))
from dsloader import ravager
sl = sys.argv[3] if len(sys.argv) > 3 and os.path.isfile(os.path.join(sys.argv[3], 'SEGOBJEX.GFF')) else None
problem = ravager.prepare(sys.argv[1], sys.argv[2], {}, sl)   # (the new items with Shattered Lands' pictures: $GAME's, RAV_SL= none)
if problem: sys.exit('ravager.prepare: ' + problem)
ravager.widen_files(sys.argv[1])   # (the roster's and the saves' sheets the copy's 48h, as launch does; .42H backups)
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
    # (the mod's item types, its new items, or the new spells' spellbooks: OBJEX2.GFF without them, the
    # spells themselves kept; all the parts asked for in one write, since each write starts from the
    # game's own file: one at a time, the last put back what the others left out, 2026-11-27's audit)
    parts = {p for p in skip if p in ('mod_types', 'new_items', 'new_spells', 'item_shine', 'weights', 'spell_arrows', 'melee_range')}
    if parts:
        ravager.write_objects(sys.argv[1], os.path.join(sys.argv[2], ravager.OBJECTS_COPY), parts, sl)
        if 'spell_arrows' in parts:   # (the arrows' icons and names are RESOURC2.GFF's too)
            ravager.write_resources(sys.argv[1], os.path.join(sys.argv[2], ravager.RESOURCE_COPY), {'spell_arrows'}, sl)
        skip = [s for s in skip if s not in parts]
    if skip: sys.exit('RAV_SKIP: no such patch ' + ','.join(skip))
    open(exe, 'wb').write(data); print('# left out:', os.environ['RAV_SKIP'])
for poke in [p for p in os.environ.get('RAV_POKE', '').split(',') if p]:   # (FILEOFFSET=HEX: bytes put in the copy, a test's probe)
    exe = os.path.join(sys.argv[2], ravager.PATCHED_EXE); data = bytearray(open(exe, 'rb').read())
    at, new = poke.split('='); at = int(at, 16); new = bytes.fromhex(new)
    data[at:at + len(new)] = new; open(exe, 'wb').write(data); print('# poked %X: %s' % (at, new.hex()))
print('\n'.join(ravager.conf_lines(sys.argv[1], sys.argv[2], cd=os.path.join(sys.argv[1], 'data.cue'))))
PY
else
{ echo "[autoexec]"; echo "mount c $F"; echo "imgmount d $F/data.cue -t iso"
  [ -n "$RAV_UMB" ] && { echo "mount e $REPO/obsidian-edition/dos"; echo 'e:\umbplus.com'; }
  echo "c:"; echo "DSUN -W0 -L"; } >> "$C"
fi
[ -n "$RAV_CORE" ] && sed -i "s/^core=.*/core=$RAV_CORE/" "$C"   # (DOSBox's CPU core: normal for a control of the dynamic one)
[ -n "$RAV_NOEXIT" ] && sed -i '/^exit$/d' "$C"   # (the game's own exit leaves DOSBox up: its last words on screen)
[ -n "$RAV_PAUSE" ] && sed -i 's/^exit$/echo The game has ended.\npause\nexit/' "$C"   # (the game's exit then a key: its last words on screen, the autoexec unchanged before it)
[ -n "$RAV_MARK" ] && sed -i 's/^exit$/echo ended > c:\\ENDED.TXT\nexit/' "$C"   # (a file when the autoexec goes on past the game: when it ended)
[ -n "$RAV_STDOUT" ] && sed -i 's/^\(.*dsun[a-z0-9]*\.exe -W0 -L\)$/\1 > c:\\STDOUT.TXT/I' "$C"   # (the game's own printing, a fatal error's message among it, to a file)
pgrep -x Xvfb >/dev/null || { setsid nohup Xvfb :55 -screen 0 1024x768x24 >/dev/null 2>&1 & sleep 2; }
SDL_AUDIODRIVER=${RAV_SOUND:+dummy} setsid nohup dosbox -conf "$C" > "$WORK/rav-dosbox.log" 2>&1 &
echo $! > "$WORK/rav.pid"; sleep 6
W=$(timeout 5 xdotool search --pid "$(cat "$WORK/rav.pid")" | tail -1)
[ -z "$W" ] && { echo "no DOSBox window"; exit 1; }
for t in 1 2; do xdotool keydown --window "$W" Shift_L; sleep 1; xdotool keyup --window "$W" Shift_L; sleep 3; done
[ -n "$RAV_MENU" ] && { import -window "$W" "$WORK/rav-menu.png"; echo "pid $(cat "$WORK/rav.pid"), window $W: at the title menu ($WORK/rav-menu.png)"; exit 0; }
xdotool key --window "$W" s; sleep 80
import -window "$W" "$WORK/rav-tyr.png"; echo "pid $(cat "$WORK/rav.pid"), window $W: $WORK/rav-tyr.png"
