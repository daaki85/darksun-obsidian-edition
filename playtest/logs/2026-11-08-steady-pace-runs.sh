cd /home/user/darksun-obsidian-edition/playtest
export PLAYTEST_WORK=/tmp/playtest DISPLAY=:55
setopts() { (cd ../obsidian-edition && python3 -c "
from dsloader import launch
s = launch.load_settings()
for k, v in $1.items(): s[k] = v
launch.save_settings(s)"); }
ON="'shadows': True, 'dust': True, 'see_through': True, 'rings': 'chosen', 'combat_log': True, 'floating_names': True"
OFF="'shadows': False, 'dust': False, 'see_through': False, 'rings': 'off', 'combat_log': False, 'floating_names': False"
run() { PT_CYCLES=$1 timeout 200 sh loadsave.sh pens-after-arena > /tmp/playtest/m_load.out 2>&1
  timeout 60 python3 pointer.py walk >/dev/null 2>&1
  echo "cycles $1, $2: $(timeout 90 python3 framerate.py 20 2>&1 | tail -1)"; }
setopts "{$ON, 'steady_pace': True}"; run 20000 "all on, new steady pace"
setopts "{$ON, 'steady_pace': False}"; run 20000 "all on, steady pace off"
setopts "{$ON, 'steady_pace': True}"; run 35000 "all on, new steady pace"
setopts "{$OFF, 'steady_pace': True}"; run 20000 "mod drawing off, new steady pace"
setopts "{$ON, 'steady_pace': True}"
echo MATRIX5-DONE
