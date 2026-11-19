# altflag.py [latency N | watch SECONDS]: the BIOS's shift flags (0:0417h; Alt is bit 3, Ctrl bit 2,
# the Shifts bits 0 and 1), which the Loader reads for "show what can be used" (dsloader/usable.py).
# No argument: the byte now, and whether the marks are up (DSCLOG's RING_TAB and label slots).
# latency N: N times, Alt pressed (xdotool keydown on DOSBox's window) and let go, timing from the
# start of the press (xdotool's own time is printed) to the flag set, to the first ring marked and
# to the first name's slot written, and the same on the way down: the Loader's latency, with the
# dice log running. watch SECONDS: every
# change of the byte, of fight_on, of the rings' table and whether its colours are the red or the
# gold ones, and of the label slots, with its time (to follow a test made by hand: focus lost,
# DOSBox's own Alt keys). (Writing the bit in memory doesn't hold: DOSBox's BIOS had cleared it again within
# half a second. Hold the key.)
import os, re, sys, struct, time, subprocess
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
args = sys.argv[1:]; sys.argv = sys.argv[:1]
exec(open(os.path.join(PT, 'live.py')).read())
from dsloader import dicelog, labels, rings, usable
mem = g.read(0, 0x110000)
hdr = next(m.start() for m in re.finditer(re.escape(dicelog.HDR_SIG), mem) if m.start() % 16 == 0)
far = struct.unpack('<H', g.read(hdr + rings.TSR_FAR_SEG, 2))[0] * 16
tab = far + struct.unpack('<H', g.read(hdr + rings.TSR_RING_TAB, 2))[0]
slots = labels.slots_at(g, hdr)
flag = lambda: g.read(usable.KEY_FLAGS, 1)[0]
ringed = lambda: sum(1 for b in g.read(tab, rings.THINGS) if b)
named = lambda: sum(1 for n in range(labels.SLOTS) if g.read(slots + n * labels.SIZE, 1)[0])
state = lambda: (flag(), ringed(), named())
def until(test, t0, most=3.0):  # ms from T0 until TEST holds
    while time.time() - t0 < most:
        if test(): return round((time.time() - t0) * 1000)
        time.sleep(0.002)
    return None
if not args:
    f, r, n = state(); print(f'flags {f:02X}h (Alt {"held" if f & usable.ALT else "up"}), rings marked {r}, names up {n}')
elif args[0] == 'latency':
    win = subprocess.run(['xdotool', 'search', '--class', 'dosbox'], capture_output=True, text=True).stdout.split()[0]
    key = lambda what: subprocess.run(['xdotool', what, '--window', win, 'Alt_L'])
    for k in range(int(args[1])):
        t = time.time(); key('keydown'); sent = round((time.time() - t) * 1000)
        a = until(lambda: flag() & usable.ALT, t); b = until(ringed, t); c = until(named, t)
        time.sleep(0.7); t = time.time(); key('keyup'); gone = round((time.time() - t) * 1000)
        d = until(lambda: not flag() & usable.ALT, t); e = until(lambda: not ringed(), t); f = until(lambda: not named(), t)
        print(f'press (xdotool took {sent} ms): flag at {a} ms, rings {b} ms, names {c} ms; release ({gone} ms): flag {d} ms, rings off {e} ms, names off {f} ms')
        time.sleep(0.7)
elif args[0] == 'watch':
    red_at = far + struct.unpack('<H', g.read(hdr + rings.TSR_RED, 2))[0]
    dac_at = far + struct.unpack('<H', g.read(hdr + 238, 2))[0]
    def full():
        table = g.read(tab, rings.THINGS); dac = g.read(dac_at, 768); red = g.read(red_at, 256)
        tint = 'red' if red == rings.red_table(dac) else 'gold' if red == rings.gold_table(dac) else 'other'
        labs = [struct.unpack_from('<BBBBBBH', g.read(slots + n * labels.SIZE, 8)) for n in range(labels.SLOTS)]
        return (flag(), gd.fight_on(), tuple((t, table[t]) for t in range(rings.THINGS) if table[t]), tint,
                tuple((l[6], l[1], l[4]) for l in labels_up(labs)), struct.unpack('<H', g.read(hdr + rings.TSR_RINGS_ON, 2))[0])
    labels_up = lambda labs: [l for l in labs if l[0]]
    t0 = time.time(); last = None
    while time.time() - t0 < float(args[1]):
        try: s = full()
        except Exception as e: s = ('?', str(e)[:40])
        if s != last and len(s) > 2:
            print(f'{time.time() - t0:7.2f} s: flags {s[0]:02X}h, fight {int(s[1])}, rings_on {s[5]}, rings (thing, kind) {list(s[2])}, colours {s[3]}, names (thing, width, ink) {list(s[4])}', flush=True)
        last = s
        time.sleep(0.02)
