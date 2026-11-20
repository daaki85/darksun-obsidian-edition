# f10watch.py MEMBER SECONDS: follows a party member's turn for F10 tests, printing each change with
# its time: whose turn (DS:4979h), the member's turn flags (37BD:01D5h, bit 0 "can walk"), movement
# points (+22Bh), swings (+181h) and attack commands (+1ABh), its square, the turn's own points and
# first square (DS:4964h/4966h/4968h, what F10 gives back) and fight_on, every 5 ms. Start it in the
# background before the turn's first click (logs/2026-11-20-f10-after-spell.md).
import os, sys, time, struct
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'live.py')).read())
m = int(sys.argv[1]); end = time.time() + float(sys.argv[2]); last = None; t0 = time.time()
while time.time() < end:
    try:
        cr = gd.combatant_creature(m)
        seg = (gd.load_seg + 0x37BD) * 16
        turn = struct.unpack('<h', g.read(ds*16+0x4979, 2))[0]
        x, y = struct.unpack('<HH', g.read(ds*16 + game.POSITIONS + m*32, 4))
        st = struct.unpack('<hHH', g.read(ds*16+0x4964, 6))
        s = (turn, hex(struct.unpack('<H', g.read(seg+0x1d5+2*cr, 2))[0]), struct.unpack('<h', g.read(seg+0x22b+2*cr, 2))[0],
             g.read(seg+0x181+cr, 1)[0], g.read(seg+0x1ab+cr, 1)[0], (x >> 4, y >> 4), st, int(gd.fight_on()))
    except Exception as e:
        s = ('err', str(e))
    if s != last:
        if len(s) > 2:
            print(f'{time.time()-t0:7.2f} turn {s[0]} flags {s[1]} points {s[2]} swings {s[3]} cmds {s[4]} sq {s[5]} start {s[6]} fight {s[7]}', flush=True)
        else:
            print(s, flush=True)
        last = s
    time.sleep(0.005)
