# Before/after frame rate runs of two DSCLOG builds, alternately (2026-11-08): OLD a folder with the old
# build's DSCLOG.EXE and dsclog.asm, NEW the new DSCLOG.EXE (a copy). Puts NEW back at the end.
: "${OLD:?}" "${NEW:?}"
cd /home/user/darksun-obsidian-edition/playtest
export PLAYTEST_WORK=/tmp/playtest DISPLAY=:55
D=../obsidian-edition/dos
setopts() { (cd ../obsidian-edition && python3 -c "
from dsloader import launch
s = launch.load_settings()
for k, v in $1.items(): s[k] = v
launch.save_settings(s)"); }
ON="'shadows': True, 'dust': True, 'see_through': True, 'rings': 'chosen', 'combat_log': True, 'floating_names': True"
run() { PT_CYCLES=$1 timeout 200 sh loadsave.sh pens-after-arena > /tmp/playtest/m_load.out 2>&1
  timeout 60 python3 pointer.py walk >/dev/null 2>&1
  echo "$3 cycles $1, $2: $(timeout 90 python3 framerate.py 20 2>&1 | tail -1)"; }
export DSCLOG_ASM
for build in before after before after; do
  if [ $build = before ]; then cp $OLD/DSCLOG.EXE $D/DSCLOG.EXE; DSCLOG_ASM=$OLD/dsclog.asm; else cp $NEW $D/DSCLOG.EXE; DSCLOG_ASM=$PWD/$D/dsclog.asm; fi
  setopts "{$ON, 'steady_pace': True}"; run 20000 "all on, steady pace" $build
  setopts "{$ON, 'steady_pace': False}"; run 20000 "all on, steady pace off" $build
  setopts "{$ON, 'steady_pace': True}"; run 35000 "all on, steady pace" $build
done
cp $NEW $D/DSCLOG.EXE
setopts "{$ON, 'steady_pace': True}"
echo RUNS-DONE
