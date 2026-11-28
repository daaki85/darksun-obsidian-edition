# scwatch.py [SECONDS]: DSCLOG's shadow cache (SHADOW CACHE, the far block's FAR_SC: SC_SLOTS slots) watched
# while the game runs, every second: the slots filled (a slot's first word not 0), the next to fill (SC_NEXT),
# and how many times the filling went round (SC_NEXT going down). Its last line: the most slots a play
# used. For the memory pass's question (2026-11-28): would fewer slots do? Read-only.
import sys, os, struct, time
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT); __file__ = os.path.join(PT, 'live.py')
exec(open(__file__).read())
import buildcheck_syms  # noqa: E402 (symbols() of dsclog.asm, image and equs)
sym, equ = buildcheck_syms.symbols()
secs = int(sys.argv[1]) if len(sys.argv) > 1 else 60
mem = g.read(0xA0000, 0x60000)
hdr = 0xA0000 + next(i for i in range(0, 0x60000, 16) if mem[i:i + 8] == b'DSCLOGvf')
w = lambda a: struct.unpack('<H', g.read(a, 2))[0]
far = w(hdr + 142) * 16
slots, size, at = equ['SC_SLOTS'], equ['SC_SLOT'], equ['FAR_SC']
last, rounds, most = None, 0, 0
for t in range(secs):
    nxt = w(hdr + sym['sc_next'])
    block = g.read(far + at, slots * size)
    used = sum(1 for i in range(slots) if block[i * size:i * size + 2] != b'\0\0')
    if last is not None and nxt < last:
        rounds += 1
    last, most = nxt, max(most, used)
    if t % 10 == 0:
        print(f'{t:4d}s  filled {used:3d} of {slots}  next {nxt:3d}  rounds {rounds}', flush=True)
    time.sleep(1)
print(f'most filled {most} of {slots}, the filling went round {rounds} times')
