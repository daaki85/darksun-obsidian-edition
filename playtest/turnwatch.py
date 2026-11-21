# turnwatch.py MEMBER SECONDS: polls whose turn it is and the member's turn bytes every 5 ms,
# printing each change with its time. +181h attacks made this round (63h = spent, the turn ends),
# +1ABh attack commands, +1D5h, +5Bh (the segment DS - (4356h - 37BDh), a byte a combatant;
# +1D5h a word). Start it in the background just before the click (logs/2026-11-14-quiver-turn.md).
import os, sys, time, struct
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
seg = (ds - (0x4356 - 0x37BD)) * 16
m = int(sys.argv[1]); end = time.time() + float(sys.argv[2]); last = None; t0 = time.time()
while time.time() < end:
    s = (struct.unpack('<h', g.read(ds*16+0x4979, 2))[0], g.read(seg+0x181+m, 1)[0], g.read(seg+0x1ab+m, 1)[0],
         struct.unpack('<H', g.read(seg+0x1d5+2*m, 2))[0], g.read(seg+0x5b+m, 1)[0])
    if s != last:
        print(f"{time.time()-t0:6.3f} turn {s[0]} +181 {s[1]} +1ab {s[2]} +1d5 {s[3]:#x} +5b {s[4]}", flush=True); last = s
    time.sleep(0.005)
