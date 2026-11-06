# toalarm.sh: from pens-after-scar (loaded here, DOSBox's sound recorded to $WORK/audio.raw), Cilla's
# thief level raised to 12 in memory (she hides at 95: never save after), then through Kurzak's
# entryway and the east passage to the fire room (1896, 856). Then restalarm.sh.
. "$(dirname "$0")/env.sh"; cd "$PT"
export PT_AUDIO=$WORK/audio.raw
rm -f $PT_AUDIO
timeout 300 sh loadsave.sh pens-after-scar | tail -1
timeout 20 python3 sheetedit.py 3 level2=12 | tail -1
for p in "1816 408" "1704 408" "1592 440" "1592 600"; do timeout 90 python3 walkto.py $p | tail -1; done
for i in 1 2 3; do timeout 20 python3 click.py 200 178 left >/dev/null; sleep 2.5; done
for p in "1600 600" "1720 600" "1832 600"; do timeout 90 python3 walkto.py $p | tail -1; done
timeout 300 python3 route.py 1832 856 | tail -1
timeout 90 python3 walkto.py 1896 856 | tail -1
timeout 20 python3 state.py | tail -1
