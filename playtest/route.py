# route.py TX TY: walk the party's leader to map position TX, TY over any distance: a path found on
# the region's walkability grid as the game has it now (live.py's live_map, DS:0556h; the region
# file's GMAP is the same at the start, without closed gates and figures: one byte a 16-unit square, 0 floor; 192 and 64 walls and things, 1-31 wall
# edges and doors), walked in short clicks near the leader (a far click says NO PATH FROM HERE, and
# the view centres on the party at each click). Prints each hop; exits 0 on arrival.
import sys, os, struct, subprocess, time
from collections import deque
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import gff
tx, ty = int(sys.argv[1]), int(sys.argv[2])
region = gd.region()
name = f'RGN{region:02X}.GFF'
path = os.path.join(REPO, 'obsidian-edition', 'dos', name)
if not os.path.exists(path): path = os.path.join(GAME, name)
chunks = gff.read_gff(open(path, 'rb').read())
gm = live_map()  # the game's own grid as it is now (DS:0556h): closed doors and gates count
W = 128; H = len(gm) // W
free = lambda c, r: 0 <= c < W and 0 <= r < H and gm[r * W + c] in (0, 96)  # (96: a figure stands there)
def cam(): return struct.unpack('<hh', g.read(ds * 16 + CAMERA, 4))
def bfs(start, goal):
    prev = {start: None}; q = deque([start])
    while q:
        cur = q.popleft()
        if cur == goal: break
        c, r = cur
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            n = (c + d[0], r + d[1])
            if n not in prev and free(*n) and (d[0] == 0 or d[1] == 0 or (free(c + d[0], r) and free(c, r + d[1]))):
                prev[n] = cur; q.append(n)
    if goal not in prev: return None
    out = [goal]
    while prev[out[-1]] is not None: out.append(prev[out[-1]])
    return out[::-1]
goal = (tx >> 4, ty >> 4)
if not free(*goal): print('target square not floor:', goal, gm[goal[1] * W + goal[0]]); sys.exit(2)
def dist_from(goal):  # steps to GOAL from every floor square reachable from it
    d = {goal: 0}; q = deque([goal])
    while q:
        c, r = q.popleft()
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            n = (c + dc, r + dr)
            if n not in d and free(*n) and (dc == 0 or dr == 0 or (free(c + dc, r) and free(c, r + dr))):
                d[n] = d[(c, r)] + 1; q.append(n)
    return d
# a square a click can take: floor all round, and two squares deep to the south (walls are drawn
# with height, so a wall's face covers the floor squares north of it, and a click there is a click
# on the wall: NO PATH FROM HERE)
clear = lambda c, r: all(free(c + i, r + j) for i in (-1, 0, 1) for j in (-1, 0, 1, 2))
dist = dist_from(goal)
tried = set()  # squares whose click didn't move the party
def ahead(sq, n):  # the square N steps further along the way to the goal
    for _ in range(n):
        c, r = sq
        nxt = [(c + i, r + j) for i in (-1, 0, 1) for j in (-1, 0, 1) if dist.get((c + i, r + j), 1e9) < dist[sq]]
        if not nxt: break
        sq = min(nxt, key=dist.get)
    return sq
for hop in range(40):
    px, py = gd.party_position()
    if abs(px - tx) <= 16 and abs(py - ty) <= 16: print('ARRIVED', px, py); sys.exit(0)
    here = (px >> 4, py >> 4)
    if here not in dist: print('NO ROUTE from', here); sys.exit(1)
    def choose(ok):
        cx, cy = cam()  # (DS:1178h is the view: checked against the drawn walls, 2026-11-01)
        best = None
        for (c, r), k in dist.items():
            sx, sy = c * 16 + 8 - cx, r * 16 + 8 - cy
            if 30 <= sx <= 290 and 40 <= sy <= 165 and k < dist[here] and (c, r) not in tried and gm[r * W + c] != 96 and (ok(c, r) or k == 0):
                if best is None or k < best[0]: best = (k, (c, r))
        return best, cx, cy
    best, cx, cy = choose(clear)
    if best is None:  # the view doesn't follow the party: bring it to the leader, then ask less
        subprocess.run(['python3', os.path.join(HERE, 'viewto.py'), str(px), str(py)], capture_output=True)
        best, cx, cy = choose(clear)
        if best is None:
            best, cx, cy = choose(lambda c, r: all(free(c + i, r + j) for i in (-1, 0, 1) for j in (0, 1)))
        if best is None:  # still none: show the way ahead (the view on the leader can hide it)
            ac, ar = ahead(here, 8)
            subprocess.run(['python3', os.path.join(HERE, 'viewto.py'), str(ac * 16 + 8), str(ar * 16 + 8)], capture_output=True)
            best, cx, cy = choose(clear)
            if best is None:
                best, cx, cy = choose(lambda c, r: all(free(c + i, r + j) for i in (-1, 0, 1) for j in (0, 1)))
    if best is None: print('NO CLEAR SQUARE ON SCREEN nearer the goal from', here); sys.exit(1)
    pick = best[1]
    sx, sy = pick[0] * 16 + 8 - cx, pick[1] * 16 + 8 - cy
    before = gd.party_position()
    subprocess.run(['python3', os.path.join(HERE, 'click.py'), str(sx), str(sy)], capture_output=True)
    time.sleep(1.5)
    for _ in range(30):
        a = gd.party_position(); time.sleep(0.5)
        if gd.party_position() == a: break
    print(f'hop {hop}: square {pick} (steps left {best[0]}) -> {gd.party_position()}', flush=True)
    if gd.party_position() == before:  # the click did nothing: not that square again, and show the way ahead
        tried.add(pick); ac, ar = ahead(here, 8)
        subprocess.run(['python3', os.path.join(HERE, 'viewto.py'), str(ac * 16 + 8), str(ar * 16 + 8)], capture_output=True)
print('NOT THERE', gd.party_position()); sys.exit(1)
