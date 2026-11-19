# qsave.py SLOT [NAME] | load | state: ask DSCLOG for a save by the game's own routine (SAVE_REQ, the
# header's +1886: dsloader/quicksave.py), as the Loader's quick save does, and say what came of it
# and how long it took (seconds of this machine's clock, from the request to the answer, polled
# every 5 ms). SLOT 1-10 of the QUICK page (SAVQnn.SAV). `load` opens the game's LOAD window on that
# page; `state` prints the header's words and what a save would wait for. Not a memory edit of the
# game's state: the save it makes is the game's own, of the game as it stands.
import sys, os, struct, time
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT); __file__ = os.path.join(PT, 'live.py')
exec(open(__file__).read())
from dsloader import dicelog, quicksave as q
mem = g.read(0xA0000, 0x60000)
hdr = 0xA0000 + next(i for i in range(0, len(mem), 16) if mem[i:i + 8] == dicelog.HDR_SIG)
w = lambda field: struct.unpack('<H', g.read(hdr + field, 2))[0]
qs = q.QuickSave(); qs._hdr = hdr
what = sys.argv[1] if len(sys.argv) > 1 else 'state'
if what == 'state':
    print('keys %04X %04X seq %d %d save_req %d main_ticks %d screen_is %d fight_on %d region %#x clock %s path %r'
          % (w(q.TSR_QS_KEYS), w(q.TSR_QS_KEYS + 2), w(q.TSR_QS_SEQ), w(q.TSR_QS_SEQ + 2), w(q.TSR_SAVE_REQ),
             w(q.TSR_MAIN_TICKS), gd._word(q.SCREEN_IS), gd.fight_on(), gd.region(), gd.game_time(),
             g.read(ds * 16 + q.SAVE_PATH, 64).split(b'\0')[0]))
    from dsloader import heapcheck
    m = heapcheck.sample(g.read, gd.load_seg)
    print('memory:', heapcheck.describe(m) if m else '?')
    sys.exit()
if what == 'keys':  # keys SAVE LOAD (hex; FFFF none): DSCLOG's two keys by hand, to try the game's own
    g.write(hdr + q.TSR_QS_KEYS, struct.pack('<HH', int(sys.argv[2], 16), int(sys.argv[3], 16)))
    sys.exit()
start = time.time()
if what == 'load':
    line = qs._ask_load(gd, GAME, start)
else:
    name = sys.argv[2] if len(sys.argv) > 2 else q.quick_name(gd.game_time())
    line = qs._ask_save(gd, q.QUICK, int(what), name, start)
if line:
    print(line); sys.exit(1)
while time.time() - start < 20:
    got = w(q.TSR_SAVE_REQ)
    if got >= q.DONE:
        break
    time.sleep(0.005)
took = time.time() - start
g.write(hdr + q.TSR_SAVE_REQ, struct.pack('<H', 0))
print({q.DONE: 'done', q.FAILED: 'the game\'s save failed', q.IN_FIGHT: 'refused: a fight'}.get(got, 'no answer (%d)' % got),
      'in %.3f s' % took)
