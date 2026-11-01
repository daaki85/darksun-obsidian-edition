# doors.py: the closed doors and gates on the edge of the area the party can reach now: squares the
# live grid blocks (192 and up) where the region file's grid has a doorway (below 192). Each with
# its map position, for clicking it (a door opens when used, unless locked).
import sys, os
from collections import deque
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import gff
name = f'RGN{gd.region():02X}.GFF'; path = os.path.join(REPO, 'obsidian-edition', 'dos', name)
if not os.path.exists(path): path = os.path.join(GAME, name)
base = next(v for k, v in gff.read_gff(open(path, 'rb').read()).items() if k[0] == 'GMAP')
live = live_map(); W = 128; H = len(live) // W
free = lambda c, r: 0 <= c < W and 0 <= r < H and live[r * W + c] in (0, 96)
px, py = gd.party_position(); start = (px >> 4, py >> 4)
seen = {start}; q = deque([start]); edge = set()
while q:
    c, r = q.popleft()
    for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        n = (c + dc, r + dr)
        if not (0 <= n[0] < W and 0 <= n[1] < H) or n in seen: continue
        if free(*n): seen.add(n); q.append(n)
        elif live[n[1] * W + n[0]] >= 192 and base[n[1] * W + n[0]] < 192: edge.add(n)
print('reachable squares', len(seen))
for c, r in sorted(edge):
    print(f'door square ({c}, {r}) live {live[r * W + c]} file {base[r * W + c]}  map ({c * 16 + 8}, {r * 16 + 8})')
