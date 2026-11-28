# 2026-11-28-ravager-to-ptar.sh (from playtest/): Ptar's cave by its own entrance: the Roost reloaded, a jump to RGN001 square (73,86) below the cave, the camera put on the party, the thief (member 0) made leader, walk Up into the area (73,83) and Yes. Then walk west to Ptar with Space between steps (each step a Move Silently message).
cd "$(dirname "$0")/../.."
kill $(cat /tmp/playtest/rav.pid); sleep 2
timeout 150 sh ravload.sh ravager-roost | tail -1
python3 ravjump.py 1 73 86
python3 ravclick.py 150 128 right; sleep .5; python3 ravclick.py 150 128 right; sleep .5; python3 ravclick.py 150 128 left; sleep 6
W=$(xdotool search --pid $(cat /tmp/playtest/rav.pid) | tail -1); xdotool key --window $W space; sleep 6
python3 logs/files/2026-11-28-ravager-camera.py set; python3 ravclick.py 24 20 left; sleep 2; xdotool key --window $W Escape; sleep 2
python3 ravclick.py 145 117 left; sleep 2
xdotool key --window $W 1; sleep 1
timeout 60 python3 ravgo.py y 1330 | tail -1; sleep 4
xdotool key --window $W y; sleep 6
python3 logs/files/2026-11-28-ravager-camera.py
