#!/bin/sh
# pacerec.sh on|off OUT.mkv: a recording for docs/steady-pace.gif: pens-after-arena, steady pace on or off, the party walked east and back,
# recorded at 70 frames a second from the X display (the DOSBox window at 0,0, 320x240)
. "$(dirname "$0")/env.sh"; cd "$PT"
v=True; [ "$1" = off ] && v=False
(cd "$REPO/obsidian-edition" && python3 -c "from dsloader import launch; s=launch.load_settings(); s['steady_pace']=$v; launch.save_settings(s)")
timeout 60 sh start.sh >/dev/null 2>&1; sleep 3
W=$(xdotool search --class dosbox | head -1); xdotool windowmove $W 0 0
timeout 200 sh loadsave.sh pens-after-arena >/dev/null 2>&1; sleep 4
sh panel.sh hide >/dev/null 2>&1; sleep 1
timeout 15 python3 click.py 300 190 none >/dev/null
(ffmpeg -loglevel error -y -t 13 -f x11grab -framerate 70 -video_size 320x240 -i :55+0,0 -c:v libx264 -qp 0 -preset ultrafast "$2" &)
sleep 1
timeout 15 python3 click.py 300 125 >/dev/null; sleep 6
timeout 15 python3 click.py 40 125 >/dev/null; sleep 6
sleep 2; echo done $1
