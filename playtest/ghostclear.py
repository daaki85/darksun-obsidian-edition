# ghostclear.py [TRIALS]: in a fight, at the start of each enemy turn, Cermak marked see-through
# with GH_CHANGED set, then the byte and the turn read every 20 ms: whether DSCLOG's GHOST_UNION
# cleared it (the whole view drawn) while that enemy's turn still ran. The party's turns passed
# through the END menu (ghostturn.py's). Memory only; the table put back clear at the end.
import os, sys, struct, time; HERE = os.path.dirname(os.path.abspath(__file__))
__file__ = os.path.join(HERE, 'ghostturn.py')
src = open(__file__).read().split("phases = [")[0]
exec(src)
trials = int(sys.argv[1]) if len(sys.argv) > 1 else 6
results = []
t0 = time.time()
while len(results) < trials and time.time() - t0 < 900:
    if not gd.fight_on(): print('fight over'); break
    t = turn()
    if t is not None and t <= 3:
        pass_party(t); continue
    mark(2, 1); start = time.time(); cleared_at = None
    while turn() is not None and turn() > 3:
        if cleared_at is None and g.read(TAB + 79, 1)[0] == 0:
            cleared_at = time.time() - start
        time.sleep(0.02)
    length = time.time() - start
    after = g.read(TAB + 79, 1)[0]
    results.append((t, round(length, 2), None if cleared_at is None else round(cleared_at, 2), after))
    print('enemy turn %s: %.2f s long; byte cleared %s; after the turn %d' % (
        t, length, 'at %.2f s, within it' % cleared_at if cleared_at is not None else 'not within it', after), flush=True)
    mark(None, 1)
    while turn() is not None and turn() > 3: time.sleep(0.05)
mark(None, 1)
print('within the turn: %d of %d' % (sum(r[2] is not None for r in results), len(results)))
