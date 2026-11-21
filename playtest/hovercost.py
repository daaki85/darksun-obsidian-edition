# hovercost.py SECONDS | loader: what the chance to hit under the pointer (dsloader/hover.py) costs. With SECONDS, the game's side as it stands: the map's main loop passes and the frames shown a second (DSCLOG's main_ticks, header +260, and flip_count, +1832) over SECONDS, to compare the pointer on an enemy with the pointer away, and the switch on with off; with "loader", the Loader's side: the time one pass's look takes (hover.Hover.update on the live game, its label written nowhere) with things as they are, kept and worked out afresh.
# In a fight on a party member's turn, the scene still. Read-only.
import os, re, struct, sys, time
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
args = sys.argv[1:]; sys.argv = sys.argv[:1]
exec(open(os.path.join(PT, 'live.py')).read())
from dsloader import dicelog, hitchance, hover, launch, rings
low = g.read(0, dicelog.CONVENTIONAL_AND_UPPER)
hdr = next(m.start() for m in re.finditer(re.escape(dicelog.HDR_SIG), low) if m.start() % 16 == 0)
seen = hover.look(gd)
print(f"pointer {seen.pointer} mode {seen.mode} under it {seen.under}; turn {gd.whose_turn()} fight {int(gd.in_combat())}")
if args[:1] == ['loader']:
    class Nowhere:  # (the labels' slots are the session's Loader's: nothing written)
        def hover(self, *a, **k): pass
    rules = game.rules_from_settings(launch.load_settings())
    foes = rings.enemies(gd)
    predict = lambda a, t: hitchance.predict(gd, a, t, rules)
    for name, again in (("kept", 1e9), ("worked out afresh", 0.0)):
        h, hover.AGAIN = hover.Hover(), again
        h.update(gd, hdr, True, 0.0, Nowhere(), lambda: foes, predict)
        n, start = 400, time.perf_counter()
        for i in range(n):
            h.update(gd, hdr, True, 1.0 + i * 0.05, Nowhere(), lambda: foes, predict)
        took = (time.perf_counter() - start) / n
        print(f"a pass's look, {name}: {took * 1e6:.0f} microseconds ({h.made} predictions in {n + 1} looks), label over {h.thing}")
else:
    def counts():
        return struct.unpack('<H', g.read(hdr + 260, 2))[0], struct.unpack('<H', g.read(hdr + 1832, 2))[0]
    secs = float(args[0]); last, at = counts(), time.time(); passes = flips = 0
    while time.time() - at < secs:
        time.sleep(0.05)
        now = counts()
        passes += (now[0] - last[0]) & 0xFFFF; flips += (now[1] - last[1]) & 0xFFFF; last = now
    took = time.time() - at
    print(f"{passes / took:.0f} passes of the map's loop a second, {flips / took:.1f} frames shown a second, over {took:.1f} s")
