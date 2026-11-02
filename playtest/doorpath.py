# doorpath.py TC TR: the shortest way from the leader to square (TC, TR) on the live grid, through
# closed doors too (live 192+ where the region file has a doorway); prints the doors it crosses and
# the squares where it turns. BLOCK="C,R C,R" in the environment rules squares out (a locked door).
import sys, os
from collections import deque
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import gff
name = f'RGN{gd.region():02X}.GFF'; path = os.path.join(REPO, 'obsidian-edition', 'dos', name)
if not os.path.exists(path): path = os.path.join(GAME, name)
base = next(v for k, v in gff.read_gff(open(path, 'rb').read()).items() if k[0] == 'GMAP')
live = live_map(); W = 128; H = len(live) // W
BLOCK = {tuple(map(int, s.split(','))) for s in os.environ.get('BLOCK', '').split()}
def kind(c, r):
    if (c, r) in BLOCK: return None
    if not (0 <= c < W and 0 <= r < H): return None
    v = live[r * W + c]
    if v in (0, 96): return 'floor'
    if v >= 192 and base[r * W + c] < 192: return 'door'
    return None
px, py = gd.party_position(); start = (px >> 4, py >> 4); goal = (int(sys.argv[1]), int(sys.argv[2]))
prev = {start: None}; q = deque([start])
while q:
    cur = q.popleft()
    if cur == goal: break
    for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        n = (cur[0] + d[0], cur[1] + d[1])
        if n not in prev and kind(*n): prev[n] = cur; q.append(n)
if goal not in prev: print('no path'); sys.exit(1)
p = []; c = goal
while c: p.append(c); c = prev[c]
p.reverse(); print('length', len(p))
for s in p:
    if kind(*s) == 'door': print('door', s, 'live', live[s[1] * W + s[0]], 'map', (s[0] * 16 + 8, s[1] * 16 + 8))
print('turns:', [s for i, s in enumerate(p[1:-1], 1) if (p[i+1][0]-s[0], p[i+1][1]-s[1]) != (s[0]-p[i-1][0], s[1]-p[i-1][1])])
